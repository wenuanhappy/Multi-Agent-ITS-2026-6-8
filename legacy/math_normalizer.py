# -*- coding: utf-8 -*-
"""数学输入归一化器（Unicode 工具栏 → sympy 表达式）。

学生在前端用工具栏键入的内容是 Unicode 风格（`√`、`²`、`₁`、`|MF₁|`、全角符号、隐式乘法 `2a` 等），
本模块负责把它翻译成 sympy 能 parse 的字符串，并解析为 `Eq` 或 `Expr`，供 derive_diagnostician
做"结构等价"比较。失败一律返回 `None`，由调用方降级到 LLM / fallback。

关键设计：
- 用 `implicit_multiplication`（**不带** `_application` 后缀）—— 它处理 `2a → 2*a`，但**不会**
  把 `mf1`/`xc` 这样的多字母符号拆开。这点对诊断器很关键：
  · `mf1` 保留为单符号，方便识别"|MF₁|=..."的等号左侧
  · `xc` 也保留为单符号——后续诊断器看到 free_symbols 里出现 `xc` 这种**非预期符号**，
    就能判定为「符号粘连错误」（学生想写 `x+c` 漏了运算符）
- 中文等非数学输入一律 parse 失败 → 返回 None，让上层走 LLM/fallback。
"""
from __future__ import annotations
import re
from typing import Optional, Union

import sympy
from sympy import Eq, Expr
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication, convert_xor,
)

# parse_expr 的 transformation 组合：
#  · standard：lambda_notation / auto_symbol / repeated_decimals / auto_number / factorial_notation
#  · implicit_multiplication：`2a → 2*a`（不拆多字母符号，符号粘连可被诊断器抓到）
#  · convert_xor：`x^2 → x**2`（standard 里不含！没它学生用 `^` 写平方会被当 XOR 抛错）
_TRANSFORMATIONS = standard_transformations + (implicit_multiplication, convert_xor)

# 全角 → 半角
_FULL_HALF = str.maketrans({
    "（": "(", "）": ")", "［": "[", "］": "]",
    "＝": "=", "＋": "+", "－": "-",
    "−": "-", "—": "-", "‐": "-", "‑": "-",
    # 各种 Unicode 点乘 / 乘号都映射到 ASCII *
    "×": "*", "·": "*",   # U+00D7, U+00B7
    "⋅": "*", "∙": "*",   # U+22C5（数学 dot operator）, U+2219（bullet operator）
    "．": ".",
    "÷": "/", "／": "/",
    "，": ",",
})

# Unicode 下标 → ASCII（合并到符号名）
_SUBSCRIPT_MAP = str.maketrans({
    "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
    "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9",
    "ₙ": "n", "ₘ": "m", "ₐ": "a", "ₑ": "e", "ₓ": "x",
})

# Unicode 上标 → 数字
_SUPER_DIGIT = {
    "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
    "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
}

# 任意上标紧跟在 `<character>` 或 `<)>` 之后 → `<char>**<digit>`
_SUPER_RE = re.compile(r"([\)\]a-zA-Z0-9_])([⁰¹²³⁴⁵⁶⁷⁸⁹])")

# 绝对值 |X|：在 DERIVE 阶段焦半径恒正，直接剥掉外层 |...| 不影响代数。
# 非贪婪匹配，每对独立处理。
_ABS_RE = re.compile(r"\|([^|]+)\|")

# 必须含有的"数学迹象"（任一即可），否则视为非数学输入直接拒绝
_MATH_HINT_RE = re.compile(r"[=+\-*/^()0-9a-zA-Z²³⁴⁵⁶⁷⁸⁹√_]")


def _convert_superscripts(s: str) -> str:
    """`x²` → `x**2`，`(x+c)²³` → `(x+c)**23`。"""
    prev = None
    cur = s
    # 反复用正则吸收"紧邻前缀"的上标；直到稳定
    while prev != cur:
        prev = cur
        cur = _SUPER_RE.sub(lambda m: f"{m.group(1)}**{_SUPER_DIGIT[m.group(2)]}", cur)
    # 残留的孤立上标（比如序列）一律转为 `**<digit>`
    for k, v in _SUPER_DIGIT.items():
        cur = cur.replace(k, f"**{v}")
    return cur


def normalize(raw: str) -> str:
    """把学生原始输入归一化为 sympy 友好的 ASCII 字符串。

    注意：这里不强制小写——大小写敏感度交给 parse() 后的诊断器处理（统一在那里 lower）。
    """
    if not raw:
        return ""
    s = raw.strip()
    s = s.translate(_FULL_HALF)
    s = s.translate(_SUBSCRIPT_MAP)
    s = _convert_superscripts(s)
    # √ → sqrt：前面紧邻字母/数字/) 时强制插 `*`，否则学生写 `4a√(...)` 会被
    # sympy 解析成 `4*asqrt*(...)`（asqrt 当成单符号）→ 灾难。
    s = re.sub(r"(?<=[\w\)])√", "*sqrt", s)
    s = s.replace("√", "sqrt")
    # sqrt 后**没有括号**时（学生写 `√10`、`√x` 等），自动把后面紧跟的数字/字母包起来：
    # `sqrt10` → `sqrt(10)`，`sqrtx` → `sqrt(x)`，`sqrt2x` → `sqrt(2x)`
    # 否则 sympy 把 `sqrt10` 当成 Symbol('sqrt10') 单符号 → 灾难。
    s = re.sub(r"sqrt(?!\()(\d+(?:\.\d+)?[a-zA-Z]*|[a-zA-Z]\w*)", r"sqrt(\1)", s)
    # 剥绝对值（DERIVE 阶段 |MF₁| 等恒正量）
    prev = None
    while prev != s:
        prev = s
        s = _ABS_RE.sub(r"(\1)", s)
    # v3.19：中文"等号词"翻译为 `=` —— 只在没有 ASCII = 的情况下做。
    # 学生常写"2a 是 2√10""b² 等于 6""x 就是 y"等用中文连接的等式，
    # 后续中文剥离会把这些连接词变成空格，等号语义就丢了。
    # 必须在中文剥离之前先翻译；优先长词（避免被『是』抢走『应该是』/『就是』）。
    if "=" not in s:
        for cn_eq in ["等于", "应该是", "就是", "是"]:
            if cn_eq in s:
                s = s.replace(cn_eq, " = ", 1)  # 只替换第一次出现
                break
    # 剥离自然语言前缀/后缀（中文、中文标点等非数学字符）
    # ──────────────────────────────────────────────────────────────
    # 学生常写"结果应该是 x²/10 + y²/6 = 1"、"我觉得 PF1 = 3√10/2"等，
    # 前面那段汉字会让 sympy 误把它当 Symbol 名（"结果应该是*x²..."）。
    # 此时所有合法的数学 Unicode（√、²、₁、×、·、|…| 等）都已被前面的转换
    # 步骤映射为 ASCII，剩下的非 ASCII 字符基本都是自然语言——一律变空格，
    # 让数学段独立出来。纯中文输入（"我不会"）→ 空串 → parse() 返回 None。
    s = re.sub(r"[^\x00-\x7f]+", " ", s)
    # 折叠多余空白（保留单个空格够了，sympy 不在意）
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse(raw: str) -> Optional[Union[Eq, Expr]]:
    """归一化 + sympy 解析。

    返回：
      - `Eq(lhs, rhs)`：学生写了等式
      - `Expr`：学生只写了表达式（如距离公式本体）
      - `None`：解析失败 / 非数学输入 / 多个等号（不明确）/ 空字符串

    诊断器拿到 None 应当转给 LLM，不要试图自己猜。
    """
    if raw is None:
        return None
    s = normalize(raw)
    if not s or not _MATH_HINT_RE.search(s):
        return None
    # 小写化整段（学生写 `X` 和 `x` 当作同一个；canonical 用小写）
    # 但要保留 `sqrt` —— 替换前后它都是小写，无影响
    s = s.lower()
    # 容忍 `==` 写法
    s = s.replace("==", "=")
    eq_count = s.count("=")
    try:
        if eq_count == 0:
            return parse_expr(s, transformations=_TRANSFORMATIONS, evaluate=True)
        if eq_count == 1:
            lhs_s, rhs_s = s.split("=")
            lhs_s, rhs_s = lhs_s.strip(), rhs_s.strip()
            if not lhs_s or not rhs_s:
                return None
            lhs = parse_expr(lhs_s, transformations=_TRANSFORMATIONS, evaluate=True)
            rhs = parse_expr(rhs_s, transformations=_TRANSFORMATIONS, evaluate=True)
            return Eq(lhs, rhs)
        # 多个等号 → 学生可能写了链式等式（先不处理）
        return None
    except (SyntaxError, TypeError, ValueError, sympy.SympifyError):
        return None
    except Exception:
        # 兜底：sympy 内部有时抛各种奇怪异常，一律视为 parse 失败
        return None
