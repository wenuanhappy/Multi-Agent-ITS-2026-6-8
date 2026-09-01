# -*- coding: utf-8 -*-
"""DERIVE 阶段符号诊断器：canonical 答案 + diff 结构分类。

设计原则（与 lesson_flow 一致）：
  · 能被符号代数高置信判断的错误 → 这里出最终诊断，调用方据此短路 LLM
  · 解析失败 / 结构不在已知错误模式中 → 返回 None，让 LLM 接手
  · 调用方 fallback 在 LLM 也挂时仍负责给一个保底回复

本模块的 canonical 表只覆盖 DERIVE 阶段的几个关键步骤（距离公式、原方程、
移项后、最终方程）。例题阶段在下一轮加 canonical 即可复用同一套引擎，
不需要改本文件的代码逻辑。

返回的 Diagnosis.confidence 含义：
  · 1.0：完全正确 / 完全等价（包括正确移项）
  · 0.9：结构清晰的高频错误（移项变号 / 距离公式内号错 / 符号粘连）
  · None：本引擎给不出结论 → 转 LLM
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any

import sympy
from sympy import Eq, Expr, sqrt, simplify, expand, symbols, Symbol, Mul, Add

from .math_normalizer import parse as parse_input


# ───────────────────── 共享 sympy 符号 ─────────────────────
# 重要：不加 assumptions（如 real=True）—— 因为 sympy 里 Symbol('mf1') 与
# Symbol('mf1', real=True) 不被视为相等。学生输入经 parse_expr 得到的是无 assumptions
# 的 Symbol，必须用同样的"裸 Symbol"做 canonical 才能做相等性比较和 simplify 差值。
x, y, a, c = symbols("x y a c")
mf1, mf2 = symbols("mf1 mf2")

# ───────────────────── DERIVE 阶段 canonical 表 ─────────────────────

def _sqrt_terms(expr):
    """提取 expr 中所有 sqrt(...) 节点（公用工具）。"""
    if not hasattr(expr, "atoms"):
        return []
    return [t for t in expr.atoms(sympy.Pow) if t.exp == sympy.Rational(1, 2)]


def _radical_isolated_form(eq) -> bool:
    """检查方程是否把含 √ 项孤立到等号一边（教材 4.6 形态）。
    判据：equation 一边是 `coefficient · √(...)` 形态（系数不含 √），
         另一边完全不含 √。
    用"含任意 sqrt 节点"判断，避免 sympy 内部展开形式（如
    `sqrt(y**2 + (-c+x)**2)` vs `sqrt(c**2 - 2*c*x + x**2 + y**2)`）的字面字串差异。

    例：
      `a√((x-c)²+y²) = a² - cx` → True
      `-a√((x-c)²+y²) = -a² + cx` → True
      `4cx = 4a² - 4a√((x-c)²+y²)` → False（一边没 √、另一边混合多项式+√）
      `cx = a² - a√((x-c)²+y²)` → False（同上）
    """
    if not isinstance(eq, Eq):
        return False

    for side, other in [(eq.lhs, eq.rhs), (eq.rhs, eq.lhs)]:
        try:
            # 关键判定：side **不能是 Add**（即 side 不是"多项相加"形态）。
            # `a√r₂` 是 Mul(a, sqrt(...))；`-a√r₂` 是 Mul(-1, a, sqrt(...))；
            # 单独 `√r₂` 是 Pow(..., 1/2)。这三类都不是 Add。
            # 而 `a² - a√r₂` 是 Add(a², Mul(-a, sqrt(...)))，被排除。
            if isinstance(side, sympy.Add):
                continue
            side_sqrts = _sqrt_terms(side)
            other_sqrts = _sqrt_terms(other)
            if not side_sqrts:
                continue       # side 不含 √
            if other_sqrts:
                continue       # other 也含 √ → 不是孤立形态
            return True
        except Exception:
            continue
    return False


def _radical_simplified_not_isolated_form(eq) -> bool:
    """检查方程是否处于"已化简未孤立"形态——
    教材 4.5 → 4.6 之间的过渡形态，特征：
      · 一边是**单项**（不含 √、不是 Add，如 `cx`、`4cx`）
      · 另一边是 **Add**（多项相加），其中**恰好含 1 个** √ 项 + 若干不含 √ 项
        （如 `a² - a√r₂` = Add(a², -a√r₂)）

    例：
      `cx = a² - a√((x-c)²+y²)`            → True
      `4cx = 4a² - 4a√((x-c)²+y²)`         → True
      `a² - cx = a√((x-c)²+y²)`            → False（这是已孤立形态，由 _radical_isolated_form 抓）
      `(x+c)²+y² = 4a²+(x-c)²+y²-4a√...`   → False（两边都是 Add，是 raw 展开形态）
      `cx + a√((x-c)²+y²) = a²`            → False（左边是 Add）

    此形态学生离"根号已孤立"只差一步（把 -a√r₂ 移到等号另一边）。
    """
    if not isinstance(eq, Eq):
        return False
    for side, other in [(eq.lhs, eq.rhs), (eq.rhs, eq.lhs)]:
        try:
            # side 必须是**单项**：不是 Add 且不含 √
            if isinstance(side, sympy.Add):
                continue
            if _sqrt_terms(side):
                continue
            # other 必须是 Add，且**恰好** 1 个 √ 项
            if not isinstance(other, sympy.Add):
                continue
            other_sqrts = _sqrt_terms(other)
            if len(other_sqrts) != 1:
                continue
            return True
        except Exception:
            continue
    return False


class DeriveStep(str, Enum):
    COLLECT_MF1   = "collect_mf1"      # 距离公式 |MF₁|
    COLLECT_MF2   = "collect_mf2"      # 距离公式 |MF₂|
    ORIGINAL_EQ   = "original_eq"      # √r1 + √r2 = 2a
    AFTER_TRANSPOSE = "after_transpose"  # √r1 = 2a - √r2（与原方程代数等价）
    AFTER_SQUARE1 = "after_square1"    # 第①次平方区间：(x+c)²+y² = (2a-√r₂)² 及其代数等价形式
    AFTER_SQUARE2 = "after_square2"    # 第②次平方区间：(a²-cx)² = a²((x-c)²+y²) 及其代数等价形式
    FINAL_EQ      = "final_eq"         # x²/a² + y²/(a²-c²) = 1

# canonical sympy 对象
_R1 = sqrt((x + c) ** 2 + y ** 2)       # |MF₁| 内部
_R2 = sqrt((x - c) ** 2 + y ** 2)       # |MF₂| 内部

CANONICAL: dict = {
    DeriveStep.COLLECT_MF1:   _R1,                                   # Expr
    DeriveStep.COLLECT_MF2:   _R2,                                   # Expr
    DeriveStep.ORIGINAL_EQ:   Eq(_R1 + _R2, 2 * a),                  # Eq
    DeriveStep.AFTER_TRANSPOSE: Eq(_R1, 2 * a - _R2),                # 代数等价于 ORIGINAL
    # 第①次平方区间（教材 P107 ②）—— 教材步骤 4.5/4.6 互相等价，sympy 会自动识别
    DeriveStep.AFTER_SQUARE1: Eq((x + c) ** 2 + y ** 2, (2 * a - _R2) ** 2),
    # 第②次平方区间（教材 P107 ③）—— 与 SQUARE1 不等价（经过一次平方变形）
    DeriveStep.AFTER_SQUARE2: Eq((a ** 2 - c * x) ** 2, a ** 2 * ((x - c) ** 2 + y ** 2)),
    DeriveStep.FINAL_EQ:      Eq(x ** 2 / a ** 2 + y ** 2 / (a ** 2 - c ** 2), 1),
}


# ───────────────────── 诊断结果 ─────────────────────

@dataclass
class Diagnosis:
    label: str                                  # 8+2 错误类型之一
    locus: str                                  # 错误定位（短句）
    message: str                                # 给学生的苏格拉底回复
    canvas_action: Optional[dict] = None        # viz 动作（可空）
    matched_step: Optional[DeriveStep] = None   # 匹配/对齐到的步骤
    confidence: float = 0.9                     # 高置信短路阈值约定 ≥ 0.8


# ───────────────────── 工具：从 sympy 结构里挖信息 ─────────────────────

# 已知合法的单字母 / 多字母符号（DERIVE 阶段的"白名单"）。
# 出现这之外的多字母符号（如 `xc`、`xy`、`ay`）就是符号粘连。
_KNOWN_SYMBOLS = {"x", "y", "a", "b", "c", "e", "p", "mf1", "mf2"}

# 字母粘连"简写"展开表——平方阶段 cx/xc 通常意思是 c·x（学生省略乘号），不是错误。
# 在 dispatcher 比对 canonical 前用这张表 substitute；粘连检测仍用**原始** parsed，
# 保证原方程阶段的 `(xc)²` 等真错误仍被抓住。
def _build_concat_subs():
    pairs = [("xc", x*c), ("cx", c*x), ("yc", y*c), ("cy", c*y),
             ("ax", a*x), ("xa", x*a), ("ay", a*y), ("ya", y*a),
             ("ac", a*c), ("ca", c*a), ("xy", x*y), ("yx", y*x)]
    return {Symbol(name): val for name, val in pairs}
_CONCAT_SHORTCUTS = _build_concat_subs()


def _resolve_concat_shortcuts(expr):
    """把 expr 中粘连符号（Symbol('cx') 等）替换为对应乘积（c*x 等）。
    Eq 对象会按 lhs/rhs 各自替换重组。None 透传。"""
    if expr is None:
        return None
    if isinstance(expr, Eq):
        return Eq(expr.lhs.subs(_CONCAT_SHORTCUTS),
                  expr.rhs.subs(_CONCAT_SHORTCUTS))
    return expr.subs(_CONCAT_SHORTCUTS)


def _suspicious_concat_symbols(expr: Any) -> list:
    """返回表达式里疑似"符号粘连"的多字母符号名（如 'xc'、'ya'）。
    判据：长度 > 1 且不在白名单，且由白名单字母拼接而成（避免误报罕见变量）。"""
    if not hasattr(expr, "free_symbols"):
        return []
    bad = []
    for s in expr.free_symbols:
        name = s.name
        if name in _KNOWN_SYMBOLS:
            continue
        if len(name) >= 2 and all(ch in _KNOWN_SYMBOLS for ch in name):
            bad.append(name)
    return bad


def _radical_terms(expr: Any) -> list:
    """从表达式里把所有 sqrt(...) 子项捞出来（递归）。"""
    out = []
    if expr is None or not hasattr(expr, "args"):
        return out
    if isinstance(expr, sympy.Pow) and expr.args[1] == sympy.Rational(1, 2):
        out.append(expr)
        return out
    if getattr(expr, "func", None) is sqrt:
        out.append(expr)
        return out
    for a_ in getattr(expr, "args", ()):
        out.extend(_radical_terms(a_))
    # 去重（按 srepr）
    seen, uniq = set(), []
    for r in out:
        k = sympy.srepr(r)
        if k not in seen:
            seen.add(k); uniq.append(r)
    return uniq


def _eq_normal(e: Any) -> Optional[Expr]:
    """把 Eq(lhs, rhs) 标准化为 (lhs - rhs)。Expr 原样返回。None → None。"""
    if e is None:
        return None
    if isinstance(e, Eq):
        return simplify(e.lhs - e.rhs)
    if isinstance(e, Expr):
        return e
    return None


# ───────────────────── 各 canonical 的比较器 ─────────────────────

def _compare_distance_formula(rhs_expr: Expr, canonical: Expr,
                              which: str) -> Optional[Diagnosis]:
    """比较学生写的距离公式 sqrt(...) 与 canonical。
    `which` 取 'MF1' 或 'MF2'。"""
    # 完全相等。只给简短 ack；"下一步说什么"由 lesson_flow 根据状态合成
    if simplify(rhs_expr - canonical) == 0:
        sub = "1" if which == "MF1" else "2"
        return Diagnosis(
            label="完全正确", locus="",
            message=f"距离公式 $|MF_{sub}|$ 写对了 ✅",
            confidence=1.0,
            matched_step=(DeriveStep.COLLECT_MF1 if which == "MF1"
                          else DeriveStep.COLLECT_MF2),
        )

    # 1) 符号粘连：学生侧含 xc/yc 之类（在 RHS 本体或根号内）
    suspicious = _suspicious_concat_symbols(rhs_expr)
    if suspicious:
        return Diagnosis(
            label="符号表达错误·符号粘连", locus=f"出现了未定义符号 {suspicious[0]}",
            message=(
                "思路是对的！不过看一下根号里面：$xc$ 在数学里表示「$x$ **乘以** $c$」，"
                "和你想写的不是一回事。\n\n"
                "$M(x,y)$ 到焦点的**横坐标之差**，应该是 $x$ 和 $c$ 相加或相减——"
                "你想想 $M$ 到 $F_1(-c,0)$ 的横坐标差是 $x-(-c)$，那写出来是什么？"
                "把这里改对再继续。"
            ),
            confidence=0.9,
            matched_step=(DeriveStep.COLLECT_MF1 if which == "MF1"
                          else DeriveStep.COLLECT_MF2),
        )

    # 2) 根号内号错：取出学生和 canonical 各自的 sqrt 内部
    s_rads = _radical_terms(rhs_expr)
    c_rads = _radical_terms(canonical)
    if len(s_rads) == 1 and len(c_rads) == 1:
        s_inner = s_rads[0].args[0]
        c_inner = c_rads[0].args[0]
        inner_diff = simplify(s_inner - c_inner)
        # diff == -2*y² → 学生把 +y² 写成了 -y²（截图 bug）
        if simplify(inner_diff - (-2 * y ** 2)) == 0:
            return Diagnosis(
                label="代数运算错误·距离公式内号错",
                locus="根号内 $y^2$ 前的符号写反了",
                message=(
                    "看一下根号里**第二项**的符号 🔍 距离公式 "
                    "$d=\\sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}$ 两项之间是**加号**——"
                    "把横坐标差的平方和纵坐标差的平方**加起来**再开根号。\n\n"
                    f"你现在写的是 $\\sqrt{{(x+c)^2 - y^2}}$，$y^2$ 前应该是什么号？"
                    "改一下再发给我。"
                ),
                confidence=0.9,
                matched_step=(DeriveStep.COLLECT_MF1 if which == "MF1"
                              else DeriveStep.COLLECT_MF2),
            )
        # 对称情况：student 把 +x² 类项写错（理论上）—— 略，先不命中
    # 结构匹配不上 → 让 LLM 接手
    return None


def _check_target_mismatch(expr: Expr, claimed: str) -> Optional[Diagnosis]:
    """检测【基本正确·目标不匹配】：学生声称写的是 |MF₁|（或 MF₂），
    但 expr 在数学上等于另一个的 canonical。
    `claimed` ∈ {"MF1","MF2"}——学生通过等式左侧声明在写哪个。
    命中返回 0.9 confidence 的 Diagnosis；不命中返回 None（继续走常规诊断路径）。

    设计要点：
      · 这是"公式对、对象错"，**不算 MF₁ 写对**——matched_step 填 claimed 那个，
        lesson_flow 据此决定是否置 strict 标志（不会置）。
      · 短路掉，不调 LLM。"""
    other_step = (DeriveStep.COLLECT_MF2 if claimed == "MF1"
                  else DeriveStep.COLLECT_MF1)
    other_canonical = CANONICAL[other_step]
    # 用 simplify 做符号等价判定（处理 (x+c)² 与 (c+x)² 等表面差异）
    if simplify(expr - other_canonical) != 0:
        return None
    # 命中：构造定向引导话术
    if claimed == "MF1":
        msg = (
            "这个距离公式**本身是对的** 👍 不过它对应的是 $|MF_2|$，**不是** $|MF_1|$。\n\n"
            "因为 $F_2(c,0)$ 的横坐标是 $c$，所以横坐标差是 $(x-c)$。\n"
            "现在请你写 $|MF_1|$：点 $F_1(-c,0)$ 对应的横坐标差应该是多少？"
        )
        claimed_step = DeriveStep.COLLECT_MF1
    else:  # claimed == "MF2"
        msg = (
            "这个距离公式**本身是对的** 👍 不过它对应的是 $|MF_1|$，**不是** $|MF_2|$。\n\n"
            "因为 $F_1(-c,0)$ 的横坐标是 $-c$，所以横坐标差是 $x-(-c)=(x+c)$。\n"
            "现在请你写 $|MF_2|$：点 $F_2(c,0)$ 对应的横坐标差应该是多少？"
        )
        claimed_step = DeriveStep.COLLECT_MF2
    return Diagnosis(
        label="基本正确·目标不匹配",
        locus=f"公式正确但对应的是 |MF_{'2' if claimed == 'MF1' else '1'}| 而非 |{claimed[:2]}_{claimed[-1]}|",
        message=msg,
        confidence=0.9,
        matched_step=claimed_step,
    )


def _check_cross_term_missed(student_eq) -> Optional[Diagnosis]:
    """【代数运算错误·交叉项漏乘】检测 (A−B)² 展开时把 −2AB 写成 −2A + B 的错误。
    截图四就是这个：student 把 `-4a·√r₂` 写成了 `-4a + √r₂`（两个独立加减项）。

    思路：枚举 4 种学生可能的"独立加减项"组合 ±4a ± √r₂，分别尝试"修复"——
    如果用 ±4a·√r₂ 替换 ±4a + √r₂ 后整个等式等价于 AFTER_SQUARE1 canonical，
    就判定为交叉项漏乘。仅短路 LLM，不污染 _e311_wrote_square1 标志。"""
    if not isinstance(student_eq, Eq):
        return None
    rad_r2 = sqrt((x - c) ** 2 + y ** 2)
    try:
        s_norm = simplify(student_eq.lhs - student_eq.rhs)
        c_norm = simplify(CANONICAL[DeriveStep.AFTER_SQUARE1].lhs
                          - CANONICAL[DeriveStep.AFTER_SQUARE1].rhs)
        diff = simplify(s_norm - c_norm)
    except Exception:
        return None
    if diff == 0:
        return None  # 学生其实写对了，让 _compare_equation 走正常 ack
    # canonical 的交叉项是 −4a·√r₂；学生可能写成 ±4a ± √r₂ 的独立加减
    cross_correct = -4 * a * rad_r2
    for s1 in (-1, 1):
        for s2 in (-1, 1):
            cross_wrong = s1 * 4 * a + s2 * rad_r2
            # student 把 cross_correct 错写成 cross_wrong → s_rhs - c_rhs = cross_wrong - cross_correct
            # 而 diff = s_norm - c_norm = -(s_rhs - c_rhs)（设 LHS 相等）
            #         = cross_correct - cross_wrong
            expected_diff = simplify(cross_correct - cross_wrong)
            if simplify(diff - expected_diff) == 0:
                return Diagnosis(
                    label="代数运算错误·交叉项漏乘",
                    locus="(A-B)² 展开时把交叉项 -2AB 写成了独立的加减两项",
                    message=(
                        "看一下右边——把 $(2a - |MF_2|)^2$ 展开，**中间这项是个乘积**：\n\n"
                        "$$(2a - |MF_2|)^2 = 4a^2 - 2 \\cdot 2a \\cdot |MF_2| + |MF_2|^2 "
                        "= 4a^2 - 4a \\cdot |MF_2| + |MF_2|^2$$\n\n"
                        "你现在把它写成了 $-4a + |MF_2|$（两个**独立**的加减项），"
                        "但其实应该是 $-4a \\cdot |MF_2|$（即 $-4a \\cdot \\sqrt{(x-c)^2 + y^2}$，**一个乘积**）。\n"
                        "把这里的加号改成乘号再发给我看～"
                    ),
                    confidence=0.9,
                    matched_step=DeriveStep.AFTER_SQUARE1,
                )
    return None


def _check_square1_expansion_errors(student_eq) -> Optional[Diagnosis]:
    """SQUARE1 阶段 `(2a − √r₂)²` 展开的高频"系数错误"检测（B 类有限版）。

    严格 signature：拿 diff = student_norm − canonical_SQUARE1_norm 做正交分解
    `diff = A + B·√r₂`，其中：
      · A = diff.subs(√r₂, 0)（不含 √r₂ 的部分）
      · B = (diff − A) / √r₂（√r₂ 的系数）
    只有 A 和 B 都是**仅含 a 的多项式**（不能含 x/y/c/√r₁）且形态干净时才命中：

      · Pattern 1: A = k·a²，B = 0 → `(2a)²` 系数算错（如写成 2a²）
      · Pattern 2: A = 0，B = k·a → 交叉项系数错（如 -2a·√r₂ 漏 2 倍）

    其它任何 signature 不清洁、含杂项 → 返 None，让 LLM 接手。

    matched_step=AFTER_SQUARE1 但 label 不以"完全正确"开头，
    所以 lesson_flow **不会**把 _e311_wrote_square1 置位。"""
    if not isinstance(student_eq, Eq):
        return None
    # 用 sympy 解析时自动展开后的形式构造 rad_r2，确保 subs 字面命中
    rad_r2 = sqrt(c ** 2 - 2 * c * x + x ** 2 + y ** 2)
    try:
        s_norm = simplify(student_eq.lhs - student_eq.rhs)
        c_norm = simplify(CANONICAL[DeriveStep.AFTER_SQUARE1].lhs
                          - CANONICAL[DeriveStep.AFTER_SQUARE1].rhs)
        diff = simplify(s_norm - c_norm)
    except Exception:
        return None
    if diff == 0:
        return None  # 完全正确，让常规分支接管

    # 分解 diff = A + B·√r₂
    try:
        A = simplify(diff.subs(rad_r2, 0))
        residual = simplify(diff - A)
        # residual 必须能整除 √r₂，否则 signature 不清洁
        B = simplify(residual / rad_r2)
        # 验证 A + B·√r₂ == diff（防 sympy 解构污染）
        if simplify(A + B * rad_r2 - diff) != 0:
            return None
        # A、B 都必须**仅是 a 的多项式**（不含 x/y/c/√r₁）
        free_AB = (A.free_symbols if hasattr(A, "free_symbols") else set()) | \
                  (B.free_symbols if hasattr(B, "free_symbols") else set())
        if any(s in free_AB for s in (x, y, c)):
            return None
        # 还要排除 A/B 里残留 √r₁ 这种根号
        if any(arg.is_Pow and arg.exp == sympy.Rational(1, 2)
               for expr in (A, B) for arg in sympy.preorder_traversal(expr)):
            return None
    except Exception:
        return None

    # 工具：检查 P 是否是 k·a^deg（k≠0），返回 True/False。其它情形（含常数项 / 高次）一律 False。
    def _is_clean_monomial(P, deg):
        if P == 0:
            return False
        try:
            coefs = sympy.Poly(P, a).all_coeffs()  # 从最高次到 0 次
            # 期望长度 = deg + 1，最高位 ≠ 0，其余位全 0
            if len(coefs) != deg + 1:
                return False
            return coefs[0] != 0 and all(c == 0 for c in coefs[1:])
        except Exception:
            return False

    A_is_ka2 = _is_clean_monomial(A, 2)   # A = k·a²
    B_is_ka  = _is_clean_monomial(B, 1)   # B = m·a

    # 三种情形：单独 Pattern 1 / 单独 Pattern 2 / 复合（A & B 都干净）
    if A_is_ka2 and B == 0:
        # —— Pattern 1：(2a)² 系数错 ——
        return Diagnosis(
            label="代数运算错误·(2a)² 系数错",
            locus="(2a)² 应等于 4a²",
            message=(
                "看一下右边 $a^2$ 的系数——\n"
                "$(2a)^2$ 是 $2a$ **整体**的平方，应该是 $2^2 \\cdot a^2 = \\mathbf{4}a^2$，"
                "**系数 2 也要平方**。\n\n"
                "把 $a^2$ 前面的系数改对再发给我～"
            ),
            confidence=0.9,
            matched_step=DeriveStep.AFTER_SQUARE1,
        )
    if A == 0 and B_is_ka:
        # —— Pattern 2：交叉项系数 / 符号错 ——
        return Diagnosis(
            label="代数运算错误·交叉项系数错",
            locus="交叉项 $-2 \\cdot 2a \\cdot |MF_2|$ 的系数算错了",
            message=(
                "$(2a − |MF_2|)^2$ 展开公式：$(A−B)^2 = A^2 − 2AB + B^2$\n\n"
                "这里 $A = 2a$，$B = |MF_2|$。"
                "**中间这项**是 $-2AB = -2 \\cdot 2a \\cdot |MF_2|$，"
                "系数等于多少？你算一下，看右边交叉项的系数对不对～"
            ),
            confidence=0.9,
            matched_step=DeriveStep.AFTER_SQUARE1,
        )
    if A_is_ka2 and B_is_ka:
        # —— 复合错误：两个都中（截图六）——
        return Diagnosis(
            label="代数运算错误·(2a)² 系数错+交叉项系数错",
            locus="(2a)² 系数错 + 交叉项系数错（同时出现）",
            message=(
                "平方的方向是对的 👍 但这里**两处都要修**——回到展开公式：\n"
                "$(A−B)^2 = A^2 \\mathbf{- 2AB} + B^2$，这里 $A = 2a$，$B = |MF_2|$。\n\n"
                "① $A^2 = (2a)^2 = 2^2 \\cdot a^2 = \\mathbf{4}a^2$，**系数 2 也要平方**——"
                "你写的 $a^2$ 前面系数对吗？\n"
                "② **交叉项** $-2AB = -2 \\cdot 2a \\cdot |MF_2|$，注意是**减号**，系数等于多少？"
                "你看下右边那项前面是 $+$ 还是 $-$，系数又是多少。\n\n"
                "两处都改一下再发给我～"
            ),
            confidence=0.9,
            matched_step=DeriveStep.AFTER_SQUARE1,
        )

    # signature 不清洁 / 不匹配任何已知 pattern → 让 LLM 接手
    return None


def _compare_equation(student_eq: Eq, canonical_eq: Eq,
                      step: DeriveStep) -> Optional[Diagnosis]:
    """比较学生等式与 canonical 等式。"""
    s_norm = _eq_normal(student_eq)
    c_norm = _eq_normal(canonical_eq)
    if s_norm is None or c_norm is None:
        return None

    # 完全等价判定：用 ratio 而不是 diff。
    # 原理：两个方程 lhs−rhs=0 同解 ⟺ s_norm 是 c_norm 的**非零常数倍**
    # （`simplify(s_norm / c_norm)` 是常数且不为 0）。
    # 这覆盖了：①完全一致写法 ②两边除以公因子（如 4cx=4a²-4a√r₂ vs cx=a²-a√r₂）
    # ③两边乘任意非零常数 ④移项重排（lhs/rhs 交换符号自动处理）。
    # 单纯用 simplify(diff)==0 会把这些等价形式判错，造成"反复粘连误诊"。
    is_equivalent = False
    if s_norm == 0 and c_norm == 0:
        is_equivalent = True   # 恒等式，少见
    elif s_norm == 0 or c_norm == 0:
        is_equivalent = False  # 一边是 0 一边不是 → 不等价
    else:
        try:
            ratio = simplify(s_norm / c_norm)
            is_equivalent = bool(ratio.is_constant()) and ratio != 0
        except Exception:
            is_equivalent = False
    if is_equivalent:
        # 区分：是原方程本体，还是已经把一个根号移到了另一边？
        # 严格判据：student LHS 本身是 **纯 sqrt 表达式**（Pow with exp=1/2），
        # 而不是 Add/Mul 中嵌了 sqrt 项。这样能避免把 SQUARE1 等价形式
        # `4cx − 4a² + 4a·√r₂ = 0` 误判为"移项后"——它 LHS 是 Add，不是 Pow。
        # 同时只在比对 ORIGINAL_EQ / TRANSPOSE step 时考虑"正确移项"。
        student_lhs = student_eq.lhs
        is_pure_radical = (isinstance(student_lhs, sympy.Pow)
                           and student_lhs.exp == sympy.Rational(1, 2))
        if (step in (DeriveStep.ORIGINAL_EQ, DeriveStep.AFTER_TRANSPOSE)
                and is_pure_radical):
            return Diagnosis(
                label="完全正确·正确移项", locus="",
                message="漂亮，移项做对了 ✅ 一个根号已经「落单」在等号一边了。",
                confidence=1.0,
                matched_step=DeriveStep.AFTER_TRANSPOSE,
            )
        # 按 step 给简短 ack（不含下一步引导，引导由 lesson_flow 合成）
        if step == DeriveStep.ORIGINAL_EQ:
            msg = "对了 ✅ 这就是椭圆定义的代数表达：$|MF_1|+|MF_2|=2a$。"
        elif step == DeriveStep.AFTER_SQUARE1:
            # AFTER_SQUARE1 内三档形态识别（教学层面的"半进度"区分）：
            #   1) 根号已孤立（教材 4.6 形态）→ 引导第④步第二次平方
            #   2) 已化简未孤立（教材 4.5→4.6 之间）→ 鼓励"再把 √ 移过去"
            #   3) raw 展开形态（如 (x+c)²+y² = 4a²+(x-c)²+y²-4a√...）→ 引导整理
            if _radical_isolated_form(student_eq):
                return Diagnosis(
                    label="完全正确·根号已孤立", locus="",
                    message="漂亮 ✨ 含根号的项已经孤立到等号一边了，整理得很到位！",
                    confidence=1.0,
                    matched_step=DeriveStep.AFTER_SQUARE1,
                )
            if _radical_simplified_not_isolated_form(student_eq):
                return Diagnosis(
                    label="完全正确·已化简未孤立", locus="",
                    message="化简得很到位 ✅ 一边是单项、另一边只剩 1 个 √ 项了。",
                    confidence=1.0,
                    matched_step=DeriveStep.AFTER_SQUARE1,
                )
            msg = "第①次平方做对了 ✅ 左边的根号消掉了。"
        elif step == DeriveStep.AFTER_SQUARE2:
            msg = "第②次平方做对了 ✅ 剩下的根号也消掉了。"
        elif step == DeriveStep.FINAL_EQ:
            msg = "漂亮 🎉 这就是椭圆的标准方程 $\\dfrac{x^2}{a^2}+\\dfrac{y^2}{a^2-c^2}=1$！"
        else:
            msg = "这一步写得对 ✅"
        return Diagnosis(
            label="完全正确", locus="",
            message=msg,
            confidence=1.0,
            matched_step=step,
        )

    # 移项变号：diff = ±2 * <某个根号项>
    diff = simplify(s_norm - c_norm)
    s_rads = _radical_terms(student_eq.lhs) + _radical_terms(student_eq.rhs)
    c_rads = _radical_terms(canonical_eq.lhs) + _radical_terms(canonical_eq.rhs)
    rads = s_rads + c_rads
    for r in rads:
        if simplify(diff - 2 * r) == 0 or simplify(diff + 2 * r) == 0:
            return Diagnosis(
                label="代数运算错误·移项变号",
                locus="移项时忘了变号",
                message=(
                    "移项的**方向**对了 👍 但有个关键细节要提醒你：把一个量从等号"
                    "**一边移到另一边**，符号必须**变号**。\n\n"
                    "原式是 $|MF_1| + |MF_2| = 2a$，$|MF_2|$ 在左边是「**加**」。"
                    "那它移到右边以后，前面应该是「加」还是「减」呢？\n\n"
                    "把这个符号改一下，再发给我看看～"
                ),
                confidence=0.9,
                matched_step=DeriveStep.AFTER_TRANSPOSE,
            )

    # 注：粘连检测**不在这里**做——会让 SQUARE2 等阶段的正确输入（含 cx 简写）被
    # 误判。粘连检测移到 dispatcher 顶层，**所有 canonical 都不命中**之后才执行，
    # 这样合法的 SQUARE 阶段输入先被 simplify(diff)==0 命中"完全正确"分支。
    return None


def _check_concat_in_equation(student_eq) -> Optional[Diagnosis]:
    """【符号粘连·等式版】整个 dispatcher 跑完所有 canonical 都没命中后才调。
    用于抓"原方程阶段把 (x+c) 写成 (xc)"这类输入——此时它一定不能 simplify 到任何
    canonical，且未定义符号能指向粘连。"""
    if not isinstance(student_eq, Eq):
        return None
    suspicious = (_suspicious_concat_symbols(student_eq.lhs)
                  + _suspicious_concat_symbols(student_eq.rhs))
    if not suspicious:
        return None
    return Diagnosis(
        label="符号表达错误·符号粘连",
        locus=f"出现了未定义符号 {suspicious[0]}",
        message=(
            "思路是对的！不过看一下根号里面：$xc$ 在数学里表示「$x$ **乘以** $c$」，"
            "和你想写的不是一回事。\n\n"
            "$M(x,y)$ 到焦点的**横坐标之差**，应该是 $x$ 和 $c$ 相加或相减——"
            "你想想 $M$ 到 $F_1(-c,0)$ 的横坐标差是 $x-(-c)$，那写出来是什么？"
            "把这里改对再继续。"
        ),
        confidence=0.9,
        matched_step=DeriveStep.ORIGINAL_EQ,
    )


# ───────────────────── 公共入口 ─────────────────────

def diagnose(student_text: str) -> Optional[Diagnosis]:
    """统一入口：归一化 → parse → 按结构尝试各 canonical 比较 → 返回 Diagnosis 或 None。

    返回 None 的情形（调用方应转给 LLM）：
      · 输入解析失败（非数学输入 / 学生写半句话）
      · 解析成功但与所有 canonical 都对不上 / diff 不属于已知错误模式
    """
    parsed = parse_input(student_text)
    if parsed is None:
        return None
    # 学生写出了恒等式（如 "1+1=2"）→ sympy 会折叠成布尔 True/False，与教学无关，转 LLM
    if isinstance(parsed, sympy.logic.boolalg.BooleanAtom):
        return None

    # ── 情形 A：学生写了等式 ─────────────────────────
    if isinstance(parsed, Eq):
        # 用解开了字母粘连简写的版本去 canonical 比对（SQUARE 阶段 cx 是 c·x 简写）；
        # 原始 parsed 留给粘连检测和"目标不匹配"检测（那里需要看到 Symbol('cx')）。
        parsed_resolved = _resolve_concat_shortcuts(parsed)
        lhs, rhs = parsed.lhs, parsed.rhs

        # A.1 形如 "|MF₁| = X" → 比较 X 和 COLLECT_MF1 / MF2
        # 注意：先做"目标不匹配"检测（学生说他写的是 MF₁，但 X 其实是 MF₂ 的公式）。
        # 这是一类"基本正确但偏题"的诊断——公式对、对象错——状态机不应把它当成
        # MF₁ 写对，所以 matched_step 填学生**声称要写**的那个（COLLECT_MF1）。
        if lhs == mf1:
            d_mis = _check_target_mismatch(rhs, claimed="MF1")
            if d_mis is not None:
                return d_mis
            return _compare_distance_formula(rhs, CANONICAL[DeriveStep.COLLECT_MF1], "MF1")
        if lhs == mf2:
            d_mis = _check_target_mismatch(rhs, claimed="MF2")
            if d_mis is not None:
                return d_mis
            return _compare_distance_formula(rhs, CANONICAL[DeriveStep.COLLECT_MF2], "MF2")
        # 反过来：学生把表达式写左边（少见但合法）
        if rhs == mf1:
            d_mis = _check_target_mismatch(lhs, claimed="MF1")
            if d_mis is not None:
                return d_mis
            return _compare_distance_formula(lhs, CANONICAL[DeriveStep.COLLECT_MF1], "MF1")
        if rhs == mf2:
            d_mis = _check_target_mismatch(lhs, claimed="MF2")
            if d_mis is not None:
                return d_mis
            return _compare_distance_formula(lhs, CANONICAL[DeriveStep.COLLECT_MF2], "MF2")

        # A.2 等式 canonical 依次比较——按推导顺序：原方程 → 移项 → 第①次平方 → 第②次平方 → 最终
        # 用 parsed_resolved（cx→c*x 简写已解开）跑 canonical 比对，
        # 让"含 cx 简写但实质正确"的输入能命中"完全正确"。
        d_cross = _check_cross_term_missed(parsed_resolved)
        if d_cross is not None:
            return d_cross
        # 在 canonical 循环之前再尝试"SQUARE1 系数错"——严格 signature 命中才短路，
        # 否则返 None 让后面的 canonical 循环和 LLM 各自接手。
        d_coef = _check_square1_expansion_errors(parsed_resolved)
        if d_coef is not None:
            return d_coef
        for step in (DeriveStep.ORIGINAL_EQ, DeriveStep.AFTER_TRANSPOSE,
                     DeriveStep.AFTER_SQUARE1, DeriveStep.AFTER_SQUARE2,
                     DeriveStep.FINAL_EQ):
            d = _compare_equation(parsed_resolved, CANONICAL[step], step)
            if d is not None:
                return d
        # v3.8：**不再**在等式分支兜底报粘连。
        # 历史 bug：`_check_concat_in_equation` 在所有 canonical 失败后，
        # 看到 Symbol('cx') 就报粘连——但 cx 在 SQUARE 阶段是合法简写。
        # 这导致只要学生方程稍微出错（不命中任何 canonical），就被误诊为粘连。
        # 距离公式阶段的真粘连（√((xc)²+y²) 这种）仍由 _compare_distance_formula
        # 抓到；等式阶段的不匹配输入一律转给 LLM 接手——LLM 比规则层更适合处理
        # 这种"哪里不对但说不清"的情况。
        return None

    # ── 情形 B：学生只写了表达式（无等号） ─────────────────
    # 优先匹配为某个距离公式
    for step, which in [(DeriveStep.COLLECT_MF1, "MF1"), (DeriveStep.COLLECT_MF2, "MF2")]:
        d = _compare_distance_formula(parsed, CANONICAL[step], which)
        if d is not None:
            return d
    return None
