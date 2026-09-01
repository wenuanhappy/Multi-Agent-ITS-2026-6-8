# -*- coding: utf-8 -*-
"""3.3.2 例题 / 思考诊断器：参照 example_diagnostician_p331.py。

入口：
  diagnose_example_332(student_text, example_key) -> Optional[ExampleDiagnosis332]
    example_key ∈ {1, 2, 3}  （1=例3 求方程 / 2=思考 2条 / 3=例4 焦点弦）

设计原则（与 p331 对齐）：
  · 遍历所有 canonical goal，sympy ratio 判等 + 关键词路由各自试一遍
  · 命中多个 goal → 累积所有 implied_flags
  · sympy 入口统一走 math_normalizer.parse()（坑 2：全角→半角/上下标/√/中文等号）
  · 多要素 phase（例 4 ask_setup 焦点+准线；思考两方程）拆 sub-flag，handler 跨 turn 累积

3.1.1 / 3.1.2 / 3.2.1 / 3.2.2 / 3.3.1 的 example_diagnostician_*.py 一行不动。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Set

import sympy
from sympy import Rational

from .example_canonicals_332 import EXAMPLE_CONFIGS_332
from .example_diagnostician import _equivalent as _equivalent_scalar
from .math_normalizer import parse as parse_input


@dataclass
class ExampleDiagnosis332:
    hit_goal: Optional[str] = None
    hit_goals: List[str] = field(default_factory=list)
    implied_flags: Set[str] = field(default_factory=set)
    label: str = ""
    via: str = ""


# ───────────────────── 文本归一化（轻量版，用于关键词路由）─────────────────────
# sympy 入口走 math_normalizer.parse()，此处仅为关键词比对补充。

_NEG_SIGNS = "−–—－"
_PLUS_SIGNS = "＋"


def _normalize_text(text: str) -> str:
    t = text
    for ch in _NEG_SIGNS:
        t = t.replace(ch, "-")
    for ch in _PLUS_SIGNS:
        t = t.replace(ch, "+")
    t = t.replace("，", ",").replace("（", "(").replace("）", ")")
    t = t.replace("＝", "=").replace("．", ".").replace("／", "/")
    return t


_CHUNK_SPLIT_RE = re.compile(r"[,;；、]| 且 | 和 | 与 |\s+and\s+|\n")


def _split_for_multi_assignment(text: str) -> List[str]:
    """把含多个赋值的输入拆分（学生可能一句写多项：焦点(1,0), 准线x=-1）。"""
    text = _normalize_text(text)
    chunks = [text]
    for piece in _CHUNK_SPLIT_RE.split(text):
        piece = piece.strip()
        if piece and piece not in chunks:
            chunks.append(piece)
    return chunks


# ───────────────────── sympy 判等：named scalar lhs 检查 ─────────────────────
# 仅 p_1 需要 lhs=p；sum_x / ab 故意不约束 lhs，让 "6" / "8" 裸数也能命中。
_GOAL_LHS_ALIASES = {
    "p_1": ("p",),
}


def _eq_lhs_matches_goal(parsed, goal_name) -> bool:
    accepted = _GOAL_LHS_ALIASES.get(goal_name)
    if accepted is None:
        return True
    if not isinstance(parsed, sympy.Eq):
        return False
    lhs = parsed.lhs
    if isinstance(lhs, sympy.Symbol):
        return lhs.name in accepted
    if isinstance(lhs, sympy.Mul):
        return str(lhs).replace(" ", "") in accepted
    return False


# ───────────────────── (a, b) 对提取 ─────────────────────
_PAIR_RE = re.compile(r"\(\s*([^,\s\)]+)\s*,\s*([^,\s\)]+)\s*\)")


def _extract_pairs_with_sympy(text: str):
    pairs = []
    text = _normalize_text(text)
    for m in _PAIR_RE.finditer(text):
        try:
            sx = sympy.sympify(m.group(1).strip())
            sy = sympy.sympify(m.group(2).strip())
            pairs.append((sx, sy))
        except Exception:
            continue
    return pairs


# ───────────────────── 关键词路由 ─────────────────────

def _looks_like_p332_ex3_form(text: str) -> bool:
    """例题 1（例 3）form_kw：学生说出"设 y²=2px / 开口向右"等形式判断。"""
    t = _normalize_text(text).replace(" ", "").lower()
    return any(kw in t for kw in [
        "y²=2px", "y^2=2px", "y2=2px",
        "开口向右", "向右开口", "向右的",
        "设y²=2px", "设y^2=2px",
    ])


def _looks_like_p332_count2(text: str) -> bool:
    """思考 count_2：抛物线有 2 条 / 两条。"""
    t = _normalize_text(text).replace(" ", "")
    if t in {"2", "两", "二", "2条", "两条", "二条"}:
        return True
    return any(kw in t for kw in [
        "2条", "两条", "二条", "2个", "两个", "两条抛物线", "有2", "有两",
    ])


def _looks_like_p332_eq_yaxis(text: str) -> bool:
    """思考 eq_yaxis_kw：x²=−√2 y 的关键词兜底。

    防 "x²=-√2y"（无空格无括号）被 normalize 误解析为 −√(2y)。
    命中条件：含 x² + y + 负号 + √2 / 根号2 / sqrt2 / 1.41 任一。
    """
    t = _normalize_text(text).replace(" ", "").lower()
    has_x2 = ("x²" in t) or ("x^2" in t) or ("x2=" in t) or t.startswith("x2")
    has_y = "y" in t
    has_neg = ("-" in t) or ("负" in t)
    has_root2 = any(k in t for k in ["√2", "根号2", "sqrt2", "sqrt(2)", "1.41"])
    return has_x2 and has_y and has_neg and has_root2


def _looks_like_p332_ex4_focus(text: str) -> bool:
    """例题 2（例 4）focus_kw：焦点 (1, 0)。"""
    for sx, sy in _extract_pairs_with_sympy(text):
        try:
            if sympy.simplify(sx - 1) == 0 and sympy.simplify(sy - 0) == 0:
                return True
        except Exception:
            continue
    return False


_KW_HANDLERS = {
    (1, "form_kw"):     _looks_like_p332_ex3_form,
    (2, "count_2"):     _looks_like_p332_count2,
    (2, "eq_yaxis_kw"): _looks_like_p332_eq_yaxis,
    (3, "focus_kw"):    _looks_like_p332_ex4_focus,
}


# ───────────────────── 优先级（最终答案 > 中间步骤）─────────────────────
_PRIORITY_BY_EXAMPLE = {
    1: ["equation_1", "p_1", "form_kw"],
    2: ["eq_xaxis", "eq_yaxis", "eq_yaxis_kw", "count_2"],
    3: ["ab", "sum_x", "directrix", "focus_kw"],
}


# ───────────────────── 入口 ─────────────────────

def diagnose_example_332(student_text: str, example_key, phase=None) -> Optional[ExampleDiagnosis332]:
    """扫描所有 canonical goal（不限 phase），返回命中诊断或 None。"""
    if example_key not in EXAMPLE_CONFIGS_332:
        return None
    config = EXAMPLE_CONFIGS_332[example_key]
    canonical_map = config["canonical"]
    implies_map = config["implies"]

    hit_goals: List[str] = []

    # ── 1. 扫描所有 sympy goal（多赋值拆分多次 try）──
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
                continue
            for p in parsed_chunks:
                try:
                    if not _eq_lhs_matches_goal(p, goal_name):
                        continue
                    if _equivalent_scalar(p, canonical):
                        if goal_name not in hit_goals:
                            hit_goals.append(goal_name)
                        break
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

    if not hit_goals:
        return None

    # ── 3. 累积 implied_flags ──
    implied_flags: Set[str] = set()
    for g in hit_goals:
        implied_flags |= implies_map.get(g, set())

    # ── 4. 选主 goal ──
    priority = _PRIORITY_BY_EXAMPLE.get(example_key, [])
    primary = next((g for g in priority if g in hit_goals), hit_goals[0])

    return ExampleDiagnosis332(
        hit_goal=primary,
        hit_goals=hit_goals,
        implied_flags=implied_flags,
        label="完全正确",
        via="goal_scan_332",
    )
