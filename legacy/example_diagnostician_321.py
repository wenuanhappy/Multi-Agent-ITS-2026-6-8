# -*- coding: utf-8 -*-
"""3.2.1 例题与探究诊断器：v3.45 重构，参照 3.1.1 example_diagnostician.py 的 goal 扫描模式。

入口：
  diagnose_example_321(student_text, example_key) -> Optional[ExampleDiagnosis321]
    example_key ∈ {1, 2, "exploration"}

  ※ 移除 current_phase 参数 —— 诊断器不再被 phase 顺序约束（仿 311）。
    任意 goal 命中都生效，handler 用 implied_flags 累积 + done_fn 判定收尾。
    保留 legacy 4 参数签名作为兼容入口（忽略 phase 参数）。

设计原则：
  · 遍历所有 canonical goal，sympy ratio 判等 + 关键词路由各自试一遍
  · 命中多个 goal → 累积所有 implied_flags
  · 解决"学生跳级答最终方程"问题（详见 docs/scheme_D_design.md）

3.1.1 / 3.1.2 的 example_diagnostician_*.py / example_canonicals_*.py 一行不动。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional, Set, List

import sympy
from sympy import Eq, Expr

from .example_canonicals_321 import EXAMPLE_CONFIGS_321
from .example_diagnostician import _equivalent as _equivalent_scalar
from .math_normalizer import parse as parse_input


@dataclass
class ExampleDiagnosis321:
    hit_goal: Optional[str] = None              # 主要命中 goal（优先级最高的）
    hit_goals: List[str] = field(default_factory=list)  # v3.45: 所有命中 goal
    implied_flags: Set[str] = field(default_factory=set)
    label: str = ""
    via: str = ""


# ───────────────────── 文本归一化 ─────────────────────

_NEG_SIGNS = "−–—－"
_PLUS_SIGNS = "＋"

def _normalize_text(text: str) -> str:
    t = text
    for ch in _NEG_SIGNS:
        t = t.replace(ch, "-")
    for ch in _PLUS_SIGNS:
        t = t.replace(ch, "+")
    t = t.replace("，", ",").replace("（", "(").replace("）", ")")
    return t


# v3.45 增强：把"c=5, a=3" / "a=3 且 b=4" 这种多赋值拆成 chunk 分别 try
_CHUNK_SPLIT_RE = re.compile(r"[,;；、]| 且 | 和 | 与 |\s+and\s+|\n")

def _split_for_multi_assignment(text: str) -> List[str]:
    """把含多个赋值的输入拆分（学生可能一句话写多个 a=3, b=4, c=5）。
    返回 [原文, chunk1, chunk2, ...]（原文也保留，便于整体 Eq 判等如 ratio 方程）。
    """
    text = _normalize_text(text)
    chunks = [text]                                # 原文整体也试一遍
    for piece in _CHUNK_SPLIT_RE.split(text):
        piece = piece.strip()
        if piece and piece not in chunks:
            chunks.append(piece)
    return chunks


# ───────────────────── sympy 判等 ─────────────────────

def _diagnose_scalar(student_text: str, canonical) -> bool:
    """学生输入 → sympy 解析 → 与 canonical ratio 判等。"""
    parsed = parse_input(student_text)
    if parsed is None:
        return False
    if isinstance(parsed, sympy.logic.boolalg.BooleanAtom):
        return False
    return _equivalent_scalar(parsed, canonical)


# v3.45 修 ratio_equivalent 变量名信息丢失 bug：
# 学生写"b=3"，sympy._equivalent 把 Eq(b,3) rhs 提取为 3，跟 canonical a=Integer(3) 误判等价。
# 解决：对 Eq 输入，检查 lhs Symbol.name 是否与 goal_name 匹配（白名单内的 named scalar goal）。
_GOAL_LHS_ALIASES = {
    "a":         ("a",),
    "b":         ("b",),
    "c":         ("c",),
    "a_squared": ("a²", "a^2", "a2"),
    "b_squared": ("b²", "b^2", "b2"),
    "c_squared": ("c²", "c^2", "c2"),
    "two_a":     ("2a", "2*a"),
    "two_c":     ("2c", "2*c"),
}

def _eq_lhs_matches_goal(parsed, goal_name) -> bool:
    """对 Eq(Symbol, ...) 输入检查 lhs 是否匹配 goal。
    非 Eq 或非 named scalar goal → True（不做 lhs 检查，避免误拒）。
    """
    accepted = _GOAL_LHS_ALIASES.get(goal_name)
    if accepted is None:
        return True  # 不在白名单的 goal（如 "equation" / "slope_product"）跳过 lhs 检查
    if not isinstance(parsed, sympy.Eq):
        return False  # named scalar goal 必须是 "a=3" 这种 Eq 形式
    lhs = parsed.lhs
    if isinstance(lhs, sympy.Symbol):
        return lhs.name in accepted
    # 处理 "b²=16" → sympy 可能解析为 Pow(Symbol("b"), 2)
    if isinstance(lhs, sympy.Pow) and lhs.exp == 2 and isinstance(lhs.base, sympy.Symbol):
        base_name = lhs.base.name
        squared_forms = {f"{base_name}²", f"{base_name}^2", f"{base_name}2"}
        return bool(squared_forms & set(accepted))
    # 处理 "2a" → sympy 可能解析为 Mul(2, Symbol("a"))
    if isinstance(lhs, sympy.Mul):
        mul_str = str(lhs).replace(" ", "")
        return mul_str in accepted
    return False


# ───────────────────── 关键词路由：例 1 ─────────────────────

def _looks_like_form_x_axis(text: str) -> bool:
    """例 1 form_kw：学生说出"焦点在 x 轴 + x²/a² - y²/b² = 1"形式。"""
    t = _normalize_text(text).replace(" ", "")
    has_x_axis = any(kw in t for kw in ["x轴", "x-axis", "焦点在x", "x方向"])
    has_form = any(kw in t for kw in ["x²/a²", "x^2/a^2", "x2/a2", "x²/a²-y²/b²"])
    if has_x_axis and has_form:
        return True
    canonical_eqs = ["x²/a²-y²/b²=1", "x^2/a^2-y^2/b^2=1"]
    return any(c in t for c in canonical_eqs)


def _looks_like_ab_3_4(text: str) -> bool:
    """例 1 ab_kw：a=3 + (b=4 或 b²=16)。"""
    t = _normalize_text(text).replace(" ", "")
    has_a3 = ("a=3" in t) or ("a²=9" in t) or ("a^2=9" in t)
    has_b4 = (
        ("b=4" in t) or ("b²=16" in t) or ("b^2=16" in t) or ("b2=16" in t)
    )
    return has_a3 and has_b4


# ───────────────────── 关键词路由：例 2 ─────────────────────

def _looks_like_setup_680(text: str) -> bool:
    """例 2 setup_kw：2a=680 或 |PA|-|PB|=680。"""
    t = _normalize_text(text).replace(" ", "")
    if "680" not in t:
        return False
    setup_kws = [
        "2a=680", "a=340",
        "|pa|-|pb|=680", "|pb|-|pa|=680",
        "距离差=680", "差=680", "差为680", "差是680",
        "pa-pb=680", "pb-pa=680",
    ]
    return any(kw in t.lower() for kw in setup_kws)


def _looks_like_ab_340_44400(text: str) -> bool:
    """例 2 ab_kw：a=340 + b²=44400 (or c=400 + b²=44400)。"""
    t = _normalize_text(text).replace(" ", "")
    has_a340 = ("a=340" in t) or ("a²=115600" in t) or ("a^2=115600" in t)
    has_b2 = ("b²=44400" in t) or ("b^2=44400" in t) or ("b2=44400" in t)
    has_c400 = ("c=400" in t) or ("c²=160000" in t) or ("c^2=160000" in t)
    if has_a340 and has_b2:
        return True
    if has_c400 and has_b2:
        return True
    return False


def _looks_like_right_branch(text: str) -> bool:
    """例 2 branch_kw：x≥340 / 右支。"""
    t = _normalize_text(text).replace(" ", "")
    if "右支" in text:
        return True
    if "x≥340" in t or "x>=340" in t or "x≧340" in t:
        return True
    if "x大于等于340" in t or "x不小于340" in t:
        return True
    return False


def _looks_like_eq_115600_44400(text: str) -> bool:
    """例 2 方程部分（关键词）：x²/115600 - y²/44400 = 1。"""
    t = _normalize_text(text).replace(" ", "")
    if "115600" not in t or "44400" not in t:
        return False
    has_minus = "-y²" in t or "-y^2" in t or "-y2" in t
    has_x_squared = "x²" in t or "x^2" in t or "x2" in t
    return has_minus and has_x_squared


def _looks_like_equation_with_branch_2(text: str) -> bool:
    """例 2 equation_with_branch_kw：方程对 + 分支对（综合）。"""
    return _looks_like_eq_115600_44400(text) and _looks_like_right_branch(text)


# ───────────────────── 关键词路由：探究 ─────────────────────

def _looks_like_slope_am(text: str) -> bool:
    """探究 slope_am_kw：学生写出 k_AM 表达式（含 y 和 x+5）。"""
    t = _normalize_text(text).replace(" ", "")
    has_x_plus_5 = ("x+5" in t) or ("(x+5)" in t)
    has_y = "y" in t
    # 命中 am 但**不能**同时含 x-5（避免和 slopes_kw 重复命中）
    has_x_minus_5 = ("x-5" in t) or ("(x-5)" in t)
    if has_x_minus_5:
        return False
    return has_x_plus_5 and has_y


def _looks_like_slope_bm(text: str) -> bool:
    """探究 slope_bm_kw：学生写出 k_BM 表达式（含 y 和 x-5）。"""
    t = _normalize_text(text).replace(" ", "")
    has_x_minus_5 = ("x-5" in t) or ("(x-5)" in t)
    has_y = "y" in t
    has_x_plus_5 = ("x+5" in t) or ("(x+5)" in t)
    if has_x_plus_5:
        return False  # 一次输入含两者算 slopes_kw
    return has_x_minus_5 and has_y


def _looks_like_slopes_5(text: str) -> bool:
    """探究 slopes_kw：一次输入同时含 k_AM 和 k_BM（含 x+5 和 x-5 和 y）。"""
    t = _normalize_text(text).replace(" ", "")
    has_x_plus_5 = ("x+5" in t) or ("(x+5)" in t)
    has_x_minus_5 = ("x-5" in t) or ("(x-5)" in t)
    has_y = "y" in t
    return has_x_plus_5 and has_x_minus_5 and has_y


def _looks_like_constraint_ne_5(text: str) -> bool:
    """探究 constraint_kw：x≠±5。"""
    t = _normalize_text(text).replace(" ", "")
    has_ne = "≠" in t or "!=" in t or "不等" in text or "排除" in text or "除去" in text
    if not has_ne and not ("不等于" in text or "排除" in text or "除去" in text):
        return False
    has_5 = "5" in t
    return has_5 and has_ne


# ───────────────────── 关键词路由分发表（按 example_key + goal）─────────────────────

_KW_HANDLERS = {
    (1, "form_kw"):                _looks_like_form_x_axis,
    (1, "ab_kw"):                  _looks_like_ab_3_4,
    (2, "setup_kw"):               _looks_like_setup_680,
    (2, "ab_kw"):                  _looks_like_ab_340_44400,
    (2, "branch_kw"):              _looks_like_right_branch,
    (2, "equation_with_branch_kw"):_looks_like_equation_with_branch_2,
    # v3.45.2 探究 slopes 拆双 goal（修分两次答 k_AM/k_BM 死循环）
    ("exploration", "slope_am_kw"):_looks_like_slope_am,
    ("exploration", "slope_bm_kw"):_looks_like_slope_bm,
    ("exploration", "slopes_kw"):  _looks_like_slopes_5,
    ("exploration", "constraint_kw"):_looks_like_constraint_ne_5,
}


# ───────────────────── 优先级（多 goal 命中时选主 goal）─────────────────────

# 优先级：最终方程 / 综合答案 > 关键参数 > 中间值
_PRIORITY_BY_EXAMPLE = {
    1: ["equation", "ab_kw", "form_kw", "b_squared", "b", "a_squared", "a",
        "c_squared", "c", "two_a", "two_c"],
    2: ["equation_with_branch_kw", "equation", "ab_kw", "setup_kw", "branch_kw",
        "a_squared", "b_squared", "a", "c", "two_a", "two_c"],
    "exploration": ["equation", "slope_product", "constraint_kw",
                    "slopes_kw", "slope_am_kw", "slope_bm_kw"],
}


# ───────────────────── 入口 ─────────────────────

def diagnose_example_321(student_text: str, example_key, phase=None) -> Optional[ExampleDiagnosis321]:
    """v3.45 重构入口：扫描所有 canonical goal（不限 phase）。

    Args:
        student_text:  学生本轮输入
        example_key:   1 / 2 / "exploration"
        phase:         **保留参数兼容旧调用，但 v3.45 起忽略**（参见 docs/scheme_D_design.md）

    Returns:
        ExampleDiagnosis321（含 hit_goal / hit_goals / implied_flags）或 None。
    """
    if example_key not in EXAMPLE_CONFIGS_321:
        return None
    config = EXAMPLE_CONFIGS_321[example_key]
    canonical_map = config["canonical"]
    implies_map = config["implies"]

    hit_goals = []

    # ── 1. 扫描所有 sympy goal ──
    # v3.45 增强：学生可能一句话写多个赋值 "c=5, a=3"，按逗号/分号/和/与拆分多次 try
    chunks = _split_for_multi_assignment(student_text)
    parsed_chunks = []
    for chunk in chunks:
        p = parse_input(chunk)
        if p is None or isinstance(p, sympy.logic.boolalg.BooleanAtom):
            continue
        parsed_chunks.append(p)

    if parsed_chunks:
        for goal_name, canonical in canonical_map.items():
            if canonical is None:
                continue  # 关键词 goal 下面处理
            for p in parsed_chunks:
                try:
                    # v3.45 修变量名信息丢失 bug：named scalar goal 必须 lhs 匹配
                    if not _eq_lhs_matches_goal(p, goal_name):
                        continue
                    if _equivalent_scalar(p, canonical):
                        if goal_name not in hit_goals:
                            hit_goals.append(goal_name)
                        break  # 此 goal 已命中，不用 try 其他 chunk
                except Exception:
                    continue

    # ── 2. 扫描所有关键词 goal ──
    for goal_name, canonical in canonical_map.items():
        if canonical is not None:
            continue
        kw_fn = _KW_HANDLERS.get((example_key, goal_name))
        if kw_fn is None:
            continue
        if kw_fn(student_text):
            hit_goals.append(goal_name)

    # 命中 form_kw + ab_kw 这种关键词，且学生还附加了 equation kw（综合输入）
    # 例如学生答 "x²/9 - y²/16 = 1" + "焦点在 x 轴" 一句话里，多 goal 命中
    if not hit_goals:
        return None

    # ── 3. 累积 implied_flags ──
    implied_flags: Set[str] = set()
    for g in hit_goals:
        implied_flags |= implies_map.get(g, set())

    # ── 4. 选主 goal（优先级最高的）──
    priority = _PRIORITY_BY_EXAMPLE.get(example_key, [])
    primary = next((g for g in priority if g in hit_goals), hit_goals[0])

    return ExampleDiagnosis321(
        hit_goal=primary,
        hit_goals=hit_goals,
        implied_flags=implied_flags,
        label="完全正确",
        via="goal_scan_v3.45",
    )
