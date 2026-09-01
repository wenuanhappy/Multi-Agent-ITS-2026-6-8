# -*- coding: utf-8 -*-
"""3.2.2 例题诊断器：v3.46 重构，按 311-style goal 扫描模式（仿 example_diagnostician_321.py v3.45）。

入口：
  diagnose_example_322(student_text, example_key) -> Optional[ExampleDiagnosis322]
    example_key ∈ {1, 2, 3}（内部编号，对应教材例 3/5/6）

  ※ 无 phase 参数 —— 诊断器扫描所有 canonical goal，学生跳级答最终值即可触发 all_done。
    设计文档：论文补充文献_两个技术创新点.md 2.5.5 节「311-style 跳级答题」

支持的判等类型：
  · sympy Eq/Expr（standard_eq / a / b / c / e / equation_simplified / line_eq / quadratic / ab_length）
  · named scalar lhs 白名单匹配（防 "b=4" 被误判命中 "a=4" canonical）
  · frozenset of (int, int)：focus_set（(0,±5)、(±3,0)）—— ± 自动展开
  · frozenset of int / Rational：x_set（例3，-3 与 9/5）
  · 关键词路由（form_kw, asymptote_kw, relation_kw, conclude_kw, points_kw）

3.1.1 / 3.1.2 / 3.2.1 的诊断器一行不动。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple

import sympy
from sympy import Eq, Expr, Integer, Rational

from .example_canonicals_322 import EXAMPLE_CONFIGS_322
from .example_diagnostician import _equivalent as _equivalent_scalar
from .math_normalizer import parse as parse_input


@dataclass
class ExampleDiagnosis322:
    hit_goal: Optional[str] = None
    hit_goals: List[str] = field(default_factory=list)
    implied_flags: Set[str] = field(default_factory=set)
    label: str = ""
    via: str = ""


# ───────────────────── 文本归一化（v3.48 对齐 handler 侧）─────────────────────
# 复用 math_normalizer._FULL_HALF 全局表 + 处理 KaTeX 工具栏可能产生的 LaTeX 命令
# 详见 docs/3_3_parabola_dev_guidelines.md 第一章

_NEG_SIGNS = "−–—－"
_PLUS_SIGNS = "＋"

def _normalize_text(text: str) -> str:
    """诊断器关键词路由的文本归一化（v3.52 与 handler 侧 _h322_normalize_text 完全对齐）。
    枚举所有 KaTeX 工具栏可能产生的 LaTeX 命令；顺序：长名先 → 短名后 → 反斜杠兜底。
    """
    from .math_normalizer import _FULL_HALF
    t = text
    # 1. 全局 _FULL_HALF
    t = t.translate(_FULL_HALF)
    # 2. 剥 LaTeX $ 边界
    t = t.replace("$", "")
    # 3. 处理所有 KaTeX 工具栏 LaTeX 命令（顺序：长 → 短）
    # 3a. \dfrac{X}{Y} / \frac{X}{Y} → X/Y
    t = re.sub(r"\\d?frac\s*\{\s*([^{}\s]+)\s*\}\s*\{\s*([^{}\s]+)\s*\}", r"\1/\2", t)
    # 3b. \sqrt{X} → sqrt(X)；\sqrt N → sqrt(N)
    t = re.sub(r"\\sqrt\s*\{\s*([^{}]+?)\s*\}", r"sqrt(\1)", t)
    t = re.sub(r"\\sqrt\s+(\d+(?:\.\d+)?|\w)", r"sqrt(\1)", t)
    # v3.52 用否定前瞻 (?![a-zA-Z])，兼容 `\pm\dfrac` 反斜杠紧贴位置
    # 3c. ± ∓
    t = re.sub(r"\\pm(?![a-zA-Z])", "±", t)
    t = re.sub(r"\\mp(?![a-zA-Z])", "∓", t)
    # 3d. * /
    t = re.sub(r"\\(cdot|times)(?![a-zA-Z])", "*", t)
    t = re.sub(r"\\div(?![a-zA-Z])", "/", t)
    # 3e. 比较符
    t = re.sub(r"\\(leq|le)(?![a-zA-Z])", "≤", t)
    t = re.sub(r"\\(geq|ge)(?![a-zA-Z])", "≥", t)
    t = re.sub(r"\\(neq|ne)(?![a-zA-Z])", "≠", t)
    t = re.sub(r"\\approx(?![a-zA-Z])", "≈", t)
    # 3f. 箭头 / 无穷
    t = re.sub(r"\\(to|rightarrow)(?![a-zA-Z])", "→", t)
    t = re.sub(r"\\infty(?![a-zA-Z])", "∞", t)
    # 3g. 希腊字母
    t = re.sub(r"\\pi(?![a-zA-Z])", "π", t)
    t = re.sub(r"\\alpha(?![a-zA-Z])", "α", t)
    t = re.sub(r"\\beta(?![a-zA-Z])", "β", t)
    t = re.sub(r"\\theta(?![a-zA-Z])", "θ", t)
    t = re.sub(r"\\Delta(?![a-zA-Z])", "Δ", t)
    # 4. 裸 {X}{Y}
    t = re.sub(r"\{\s*([a-zA-Z0-9]+)\s*\}\s*\{\s*([a-zA-Z0-9]+)\s*\}", r"\1/\2", t)
    # 5. 旧版兼容：负号字符表归一
    for ch in _NEG_SIGNS:
        t = t.replace(ch, "-")
    for ch in _PLUS_SIGNS:
        t = t.replace(ch, "+")
    # 6. 中文逗号 / 括号已在 _FULL_HALF 里处理，这里兜底
    t = t.replace("，", ",").replace("（", "(").replace("）", ")")
    return t


_CHUNK_SPLIT_RE = re.compile(r"[,;；、]| 且 | 和 | 与 |\s+and\s+|\n")

def _split_for_multi_assignment(text: str) -> List[str]:
    text = _normalize_text(text)
    chunks = [text]
    for piece in _CHUNK_SPLIT_RE.split(text):
        piece = piece.strip()
        if piece and piece not in chunks:
            chunks.append(piece)
    return chunks


# ───────────────────── named scalar lhs 白名单（防变量名信息丢失误判）─────────────────────

_GOAL_LHS_ALIASES = {
    "a":         ("a",),
    "b":         ("b",),
    "c":         ("c",),
    "e":         ("e",),
    "a_squared": ("a²", "a^2", "a2"),
    "b_squared": ("b²", "b^2", "b2"),
    "c_squared": ("c²", "c^2", "c2"),
    "ab_length": ("|AB|", "|ab|", "AB", "ab", "AB长度", "AB的长", "AB长"),
}


def _eq_lhs_matches_goal(parsed, goal_name) -> bool:
    """named scalar goal 必须 lhs 名字匹配；非白名单 goal 跳过此检查。"""
    accepted = _GOAL_LHS_ALIASES.get(goal_name)
    if accepted is None:
        return True
    if not isinstance(parsed, sympy.Eq):
        return False
    lhs = parsed.lhs
    if isinstance(lhs, sympy.Symbol):
        return lhs.name in accepted or lhs.name.upper() in [a.upper() for a in accepted]
    if isinstance(lhs, sympy.Pow) and lhs.exp == 2 and isinstance(lhs.base, sympy.Symbol):
        base_name = lhs.base.name
        squared_forms = {f"{base_name}²", f"{base_name}^2", f"{base_name}2"}
        return bool(squared_forms & set(accepted))
    if isinstance(lhs, sympy.Mul):
        mul_str = str(lhs).replace(" ", "")
        return mul_str in accepted
    if isinstance(lhs, sympy.Abs):
        # |AB| 形式
        inner = str(lhs.args[0]).replace(" ", "").upper()
        return inner in [a.replace("|", "").upper() for a in accepted]
    return False


# ───────────────────── 点集合（focus_set 例1: (0,±5), 例3: (±3,0)）─────────────────────

_TUPLE_RE = re.compile(r"\(\s*([+\-±]?\d+)\s*,\s*([+\-±]?\d+)\s*\)")


def _expand_pm_int(s: str) -> List[int]:
    s = s.strip()
    if s.startswith("±"):
        n = int(s[1:])
        return [n, -n]
    return [int(s)]


def _extract_point_tuples(text: str) -> Set[Tuple[int, int]]:
    text = _normalize_text(text)
    points: Set[Tuple[int, int]] = set()
    for match in _TUPLE_RE.finditer(text):
        for a in _expand_pm_int(match.group(1)):
            for b in _expand_pm_int(match.group(2)):
                points.add((a, b))
    return points


def _equivalent_point_set(text: str, canonical: frozenset) -> bool:
    student_points = _extract_point_tuples(text)
    if not student_points:
        return False
    return set(canonical).issubset(student_points)  # 学生输入包含全部 canonical 点即认


# ───────────────────── 多值集合（例3 x_set: {-3, 9/5}）─────────────────────

# 匹配 -3 或 9/5 这种分数 / 整数（不在括号内）
_X_VALUE_RE = re.compile(r"(?<![\d/\(])(-?\d+(?:/\d+)?)(?![\d/\)])")


def _extract_x_values(text: str) -> Set[Rational]:
    text = _normalize_text(text)
    values: Set[Rational] = set()
    for match in _X_VALUE_RE.finditer(text):
        try:
            tok = match.group(1)
            if "/" in tok:
                num, den = tok.split("/")
                values.add(Rational(int(num), int(den)))
            else:
                values.add(Rational(int(tok)))
        except Exception:
            continue
    return values


def _equivalent_x_set(text: str, canonical: frozenset) -> bool:
    student = _extract_x_values(text)
    return set(canonical).issubset(student)


# ───────────────────── sympy 判等 ─────────────────────

def _diagnose_scalar(parsed, canonical) -> bool:
    if parsed is None:
        return False
    if isinstance(parsed, sympy.logic.boolalg.BooleanAtom):
        return False
    try:
        return _equivalent_scalar(parsed, canonical)
    except Exception:
        return False


# ───────────────────── 关键词路由 ─────────────────────

# ─ 例 1 ─
def _looks_like_form_y_axis(text: str) -> bool:
    """例 1 form_kw：学生说"焦点在 y 轴 + y²/a²-x²/b² 形式"。"""
    t = _normalize_text(text).replace(" ", "")
    has_y_axis = any(kw in t for kw in ["y轴", "Y轴", "纵轴", "焦点在y", "y方向"])
    has_form = any(kw in t for kw in ["y²/a²", "y^2/a^2", "y2/a2", "y²/a²-x²/b²"])
    if has_y_axis and has_form:
        return True
    canonical_eqs = ["y²/16-x²/9=1", "y^2/16-x^2/9=1", "y²/a²-x²/b²=1", "y^2/a^2-x^2/b^2=1"]
    return any(c in t for c in canonical_eqs)


def _looks_like_asymptote_4_3(text: str) -> bool:
    """例 1 asymptote_kw：y = ±(4/3) x。"""
    t = _normalize_text(text).replace(" ", "")
    # 必须含 4/3 / 4:3 / 0.75 倒比 等
    has_ratio = "4/3" in t
    if not has_ratio:
        return False
    # 必须含 y= 形式
    has_eq = ("y=" in t)
    # 必须暗示双边（±/和/正负/-4/3）
    has_double = ("±" in t) or ("正负" in text) or ("-4/3" in t) or ("y=4/3" in t and "y=-4/3" in t)
    return has_eq and has_double


# ─ 例 2 ─
def _looks_like_distance_ratio_4_3(text: str) -> bool:
    """例 2 relation_kw：学生写出 |MF|/d = 4/3 关系式。"""
    t = _normalize_text(text).replace(" ", "")
    has_ratio = ("4/3" in t) or ("4:3" in t) or ("4：3" in text)
    if not has_ratio:
        return False
    relation_kws = ["距离比", "比值", "比是", "|mf|", "|MF|", "mf/d", "MF/d", "比", "ratio"]
    return any(kw.lower() in text.lower() for kw in relation_kws)


def _looks_like_hyperbola_real_6_imag_2sqrt7(text: str) -> bool:
    """例 2 conclude_kw：焦点 x 轴 + 实轴长 6 + 虚轴长 2√7。"""
    raw = text
    t = text.replace(" ", "")     # 去空格再判
    has_x_axis = any(kw in t for kw in ["x轴", "X轴", "横轴", "焦点在x"])
    has_real_6 = ("实轴" in t and "6" in t) or "实轴长6" in t or "实轴长为6" in t
    has_imag = (
        "2√7" in t or "2*sqrt(7)" in t.lower() or "2sqrt(7)" in t.lower()
        or "2根号7" in raw or "2倍根号7" in raw or "二根号7" in raw or "2sqrt7" in t.lower()
    )
    return has_x_axis and has_real_6 and has_imag


# ─ 例 3（v3.48 拆 A、B 两点为独立 sub-goal，仿 312 例 4 partial_hit 累积模式）─

def _has_sqrt3(text: str) -> bool:
    """学生写出 √3 的多种形式之一。"""
    raw = text
    t = text.lower()
    return ("√3" in raw or "sqrt(3)" in t or "sqrt3" in t
            or "根号3" in raw or "根号 3" in raw)


def _looks_like_point_A(text: str) -> bool:
    """例 3 point_A 关键词：A(-3, -2√3) 含 -3 + √3，**且不含 9/5**（否则就是综合答）。
    设计同 _looks_like_slope_am（321 探究分两次答 k_AM/k_BM 的拆分）。
    """
    t = text.replace(" ", "")
    has_x1 = ("-3" in t) or ("−3" in t)
    has_x2 = "9/5" in t
    if has_x2:
        return False  # 同时含 9/5 → 综合答，由 _looks_like_points_ab 处理
    return has_x1 and _has_sqrt3(text)


def _looks_like_point_B(text: str) -> bool:
    """例 3 point_B 关键词：B(9/5, -2√3/5) 含 9/5 + √3，**且不含 -3**。"""
    t = text.replace(" ", "")
    has_x1 = ("-3" in t) or ("−3" in t)
    has_x2 = "9/5" in t
    if has_x1:
        return False  # 同时含 -3 → 综合答
    return has_x2 and _has_sqrt3(text)


def _looks_like_points_ab(text: str) -> bool:
    """例 3 point_set 综合关键词：同一句话含 A、B 两组特征（-3 + 9/5 + √3）。"""
    t = text.replace(" ", "")
    has_x1 = ("-3" in t) or ("−3" in t)
    has_x2 = "9/5" in t
    return has_x1 and has_x2 and _has_sqrt3(text)


# 关键词路由分发表
_KW_HANDLERS = {
    (1, "form_kw"):      _looks_like_form_y_axis,
    (1, "asymptote_kw"): _looks_like_asymptote_4_3,
    (2, "relation_kw"):  _looks_like_distance_ratio_4_3,
    (2, "conclude_kw"):  _looks_like_hyperbola_real_6_imag_2sqrt7,
    # v3.48 例 3 三关键词路由（partial 累积关键）
    (3, "point_A"):      _looks_like_point_A,
    (3, "point_B"):      _looks_like_point_B,
    (3, "point_set"):    _looks_like_points_ab,
}


# ───────────────────── 优先级（多 goal 命中时选主 goal）─────────────────────

_PRIORITY_BY_EXAMPLE = {
    1: ["standard_eq", "focus_set", "e", "asymptote_kw", "asymptote_eq_pos", "asymptote_eq_neg",
        "form_kw", "a", "b", "c", "a_squared", "b_squared", "c_squared"],
    2: ["equation_simplified", "equation_raw", "conclude_kw", "relation_kw"],
    # v3.48 例 3：综合 point_set 优先于单点
    3: ["ab_length", "point_set", "point_A", "point_B", "x_set", "quadratic", "line_eq", "focus_set"],
}


# ───────────────────── 入口 ─────────────────────

def diagnose_example_322(student_text: str, example_key) -> Optional[ExampleDiagnosis322]:
    """311-style goal-scan 诊断（无 phase 参数）。

    扫描所有 canonical goal：
      · sympy goal → ratio 判等 + named scalar lhs 白名单
      · 点集合 / 多值集合 → 专用提取器
      · 关键词 goal → _KW_HANDLERS 分发

    返回 ExampleDiagnosis322（含 hit_goals + implied_flags）或 None。
    """
    if example_key not in EXAMPLE_CONFIGS_322:
        return None
    config = EXAMPLE_CONFIGS_322[example_key]
    canonical_map = config["canonical"]
    implies_map = config["implies"]

    hit_goals: List[str] = []

    # ── 1. sympy 解析（按 chunk 拆分多赋值）──
    chunks = _split_for_multi_assignment(student_text)
    parsed_chunks = []
    for chunk in chunks:
        p = parse_input(chunk)
        if p is None or isinstance(p, sympy.logic.boolalg.BooleanAtom):
            continue
        parsed_chunks.append(p)

    # ── 2. 扫描所有 sympy 类型 canonical ──
    for goal_name, canonical in canonical_map.items():
        if canonical is None:
            continue  # 关键词 goal 在下面处理
        # 点集合（frozenset of int tuple）—— v3.48 后例 3 point_set 已改 None 走关键词
        if isinstance(canonical, frozenset) and canonical:
            first = next(iter(canonical))
            if isinstance(first, tuple):
                # 兼容：万一有字符串占位的历史 frozenset → 跳给关键词
                if any(isinstance(v, str) for v in first):
                    continue
                if _equivalent_point_set(student_text, canonical):
                    if goal_name not in hit_goals:
                        hit_goals.append(goal_name)
                continue
            # 多值集合（frozenset of Rational/int）
            if _equivalent_x_set(student_text, canonical):
                if goal_name not in hit_goals:
                    hit_goals.append(goal_name)
            continue
        # sympy Eq / Expr / Rational / Integer
        for p in parsed_chunks:
            try:
                if not _eq_lhs_matches_goal(p, goal_name):
                    continue
                if _diagnose_scalar(p, canonical):
                    if goal_name not in hit_goals:
                        hit_goals.append(goal_name)
                    break
            except Exception:
                continue

    # ── 3. 扫描所有关键词 goal ──
    for goal_name, canonical in canonical_map.items():
        if canonical is not None:
            continue
        kw_fn = _KW_HANDLERS.get((example_key, goal_name))
        if kw_fn is None:
            continue
        if kw_fn(student_text):
            if goal_name not in hit_goals:
                hit_goals.append(goal_name)

    # v3.48 移除：例 3 point_set/A/B 已在上方关键词扫描里命中

    if not hit_goals:
        return None

    # ── 4. 累积 implied_flags ──
    implied_flags: Set[str] = set()
    for g in hit_goals:
        implied_flags |= implies_map.get(g, set())

    # ── 5. 选主 goal ──
    priority = _PRIORITY_BY_EXAMPLE.get(example_key, [])
    primary = next((g for g in priority if g in hit_goals), hit_goals[0])

    return ExampleDiagnosis322(
        hit_goal=primary,
        hit_goals=hit_goals,
        implied_flags=implied_flags,
        label="完全正确",
        via="goal_scan_v3.46",
    )
