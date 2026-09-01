# -*- coding: utf-8 -*-
"""3.3.1 例题诊断器：v3.x 重构，参照 example_diagnostician_321.py 的 311-style goal 扫描模式。

入口：
  diagnose_example_p331(student_text, example_key) -> Optional[ExampleDiagnosisP331]
    example_key ∈ {1, 2}

设计原则：
  · 遍历所有 canonical goal，sympy ratio 判等 + 关键词路由各自试一遍
  · 命中多个 goal → 累积所有 implied_flags
  · 解决"学生跳级答最终方程"问题（详见 docs/scheme_D_design.md）
  · 例 2 ask_conclude 拆为 equation_done + focus_done 两维度（partial 累积仿 322 例 2）

支持的 canonical 类型：
  · sympy Expr / Eq （p_1 / p_2 / p_value / two_p / directrix_1 / equation_2 / equation）
    走 _equivalent_scalar 的 ratio 判等
  · keyword goal（focus_1_kw / form_2_kw / setup_kw / focus_kw / all_kw）
    走对应的 _looks_like_* 函数

3.1.1 / 3.1.2 / 3.2.1 / 3.2.2 的 example_diagnostician_*.py 一行不动。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Set

import sympy
from sympy import Eq, Expr, Rational

from .example_canonicals_p331 import EXAMPLE_CONFIGS_P331
from .example_diagnostician import _equivalent as _equivalent_scalar
from .math_normalizer import parse as parse_input


@dataclass
class ExampleDiagnosisP331:
    hit_goal: Optional[str] = None
    hit_goals: List[str] = field(default_factory=list)
    implied_flags: Set[str] = field(default_factory=set)
    label: str = ""
    via: str = ""


# ───────────────────── 文本归一化（轻量版，用于关键词路由）─────────────────────
# 注意：sympy 入口走 math_normalizer.parse()，那里已含全角→半角等完整归一。
# 本节的 _normalize_text 只为关键词比对补充，不替代 normalize()。

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


# v3.45 增强：把 "a=3, b=4" 这种多赋值拆成 chunk
_CHUNK_SPLIT_RE = re.compile(r"[,;；、]| 且 | 和 | 与 |\s+and\s+|\n")

def _split_for_multi_assignment(text: str) -> List[str]:
    """把含多个赋值的输入拆分（学生可能一句话写多个 a=3, b=4, c=5）。
    返回 [原文, chunk1, chunk2, ...]（原文也保留，便于整体 Eq 判等如 ratio 方程）。
    """
    text = _normalize_text(text)
    chunks = [text]
    for piece in _CHUNK_SPLIT_RE.split(text):
        piece = piece.strip()
        if piece and piece not in chunks:
            chunks.append(piece)
    return chunks


# ───────────────────── sympy 判等 ─────────────────────

# v3.45 修变量名信息丢失：named scalar goal 必须 lhs 匹配（不要把 "y=3" 当成 a=3）
_GOAL_LHS_ALIASES = {
    "p_1":      ("p",),
    "p_2":      ("p",),
    "p_value":  ("p",),
    "two_p":    ("2p", "2*p"),
}


def _eq_lhs_matches_goal(parsed, goal_name) -> bool:
    """对 Eq(Symbol, ...) 输入检查 lhs 是否匹配 goal。
    非 Eq 或非 named scalar goal → True（不做 lhs 检查，避免误拒）。
    """
    accepted = _GOAL_LHS_ALIASES.get(goal_name)
    if accepted is None:
        return True  # 非 named scalar goal（如 directrix_1 / equation_2 / equation）跳过 lhs 检查
    if not isinstance(parsed, sympy.Eq):
        return False
    lhs = parsed.lhs
    if isinstance(lhs, sympy.Symbol):
        return lhs.name in accepted
    # 处理 "2p" → sympy 可能解析为 Mul(2, Symbol("p"))
    if isinstance(lhs, sympy.Mul):
        mul_str = str(lhs).replace(" ", "")
        return mul_str in accepted
    return False


# ───────────────────── 关键词路由：例 1 ─────────────────────

# 通用 (a, b) 对提取（含 Rational / 小数 / 表达式，分子分母不含逗号空格右括号）
_PAIR_RE = re.compile(r"\(\s*([^,\s\)]+)\s*,\s*([^,\s\)]+)\s*\)")


def _extract_pairs_with_sympy(text: str):
    """提取 (a, b) 对并 sympify。返回 [(sx, sy), ...]。失败的对跳过。"""
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


def _looks_like_focus_1(text: str) -> bool:
    """例 1 focus_1_kw：焦点 (3/2, 0) 或 (1.5, 0)。
    支持 sympify 等价：(3/2, 0) ≡ (1.5, 0) ≡ (1.50, 0)。
    """
    target_x, target_y = Rational(3, 2), 0
    for sx, sy in _extract_pairs_with_sympy(text):
        try:
            if sympy.simplify(sx - target_x) == 0 and sympy.simplify(sy - target_y) == 0:
                return True
        except Exception:
            continue
    return False


def _looks_like_form_2(text: str) -> bool:
    """例 1 子题 (2) form_2_kw：学生说出"开口向下 / y 轴负半轴 / x²=-2py"形式。
    （已经直接写 x²=-8y 的会被 equation_2 sympy 命中，本函数只处理"形式判断"中间步。）
    """
    t = _normalize_text(text).replace(" ", "")
    has_form_kw = any(kw in t for kw in [
        "开口向下", "向下开口", "向下的", "y轴负", "y的负半轴", "焦点在y轴负", "y负半轴",
        "x²=-2py", "x^2=-2py", "x2=-2py",
        "x²=-2p", "x^2=-2p",
    ])
    # 或者识别"焦点在 y 轴上 + 标准方程是 x²=-2py 类形式" 的组合：
    has_yaxis = ("y轴" in t) or ("y-axis" in t.lower())
    has_neg = ("负" in t) or ("-" in t)
    has_x2_form = ("x²" in t) or ("x^2" in t) or ("x2=" in t)
    if has_form_kw:
        return True
    if has_yaxis and has_neg and has_x2_form:
        return True
    return False


# ───────────────────── 关键词路由：例 2（卫星天线） ─────────────────────


def _looks_like_setup_satellite(text: str) -> bool:
    """例 2 setup_kw：学生说出建系或点 A(1, 2.4) 代入。
    命中条件（任一）：
      · 含 "(1, 2.4)" 或 "A(1, 2.4)" 或 "点 (1,2.4)"
      · 含 "2.4²=2p" / "2.4^2=2p" / "5.76=2p"（代入式）
      · 含 "顶点为原点" + "焦点在 x 轴"
    """
    t = _normalize_text(text).replace(" ", "")
    # 含 (1, 2.4) 形式（sympify 等价）
    for sx, sy in _extract_pairs_with_sympy(text):
        try:
            if (sympy.simplify(sx - 1) == 0
                    and sympy.simplify(sy - Rational(24, 10)) == 0):
                return True
        except Exception:
            continue
    # 代入式
    sub_kws = ["2.4²=2p", "2.4^2=2p", "2.4*2=2p", "5.76=2p", "2.4²=2p×1", "2.4^2=2p*1"]
    if any(kw in t for kw in sub_kws):
        return True
    # 建系描述：顶点 + 原点 任意搭配（如『原点建在顶点』『顶点为原点』『顶点放原点』）
    if ("顶点" in t) and ("原点" in t):
        return True
    # 对称轴 / 焦点连线 作 x 轴（建系的另一种正确表达）
    if ("对称轴" in t or "焦点" in t) and ("x轴" in t or "横轴" in t):
        return True
    return False


def _looks_like_focus_satellite(text: str) -> bool:
    """例 2 focus_kw：焦点 (1.44, 0) 或 (144/100, 0)。"""
    target_x, target_y = Rational(144, 100), 0
    for sx, sy in _extract_pairs_with_sympy(text):
        try:
            if sympy.simplify(sx - target_x) == 0 and sympy.simplify(sy - target_y) == 0:
                return True
        except Exception:
            continue
    return False


def _looks_like_equation_satellite(text: str) -> bool:
    """例 2 学生写出方程 y²=5.76x 的关键词识别（备用，主路径由 equation sympy 命中）。"""
    t = _normalize_text(text).replace(" ", "").lower()
    if "5.76" not in t and "576/100" not in t and "144/25" not in t:
        return False
    has_y2 = ("y²" in t) or ("y^2" in t) or ("y2=" in t)
    has_x = "x" in t
    return has_y2 and has_x


def _looks_like_all_satellite(text: str) -> bool:
    """例 2 all_kw：一次输入同时含 方程 y²=5.76x 和 焦点 (1.44, 0)。"""
    return _looks_like_equation_satellite(text) and _looks_like_focus_satellite(text)


# ───────────────────── 关键词路由分发表 ─────────────────────

_KW_HANDLERS = {
    (1, "focus_1_kw"):  _looks_like_focus_1,
    (1, "form_2_kw"):   _looks_like_form_2,
    (2, "setup_kw"):    _looks_like_setup_satellite,
    (2, "focus_kw"):    _looks_like_focus_satellite,
    (2, "all_kw"):      _looks_like_all_satellite,
}


# ───────────────────── 优先级 ─────────────────────

# 优先级：综合答案 > 最终方程 > 关键参数
_PRIORITY_BY_EXAMPLE = {
    1: ["equation_2", "directrix_1", "focus_1_kw", "form_2_kw", "p_1", "p_2"],
    2: ["all_kw", "equation", "focus_kw", "p_value", "two_p", "setup_kw"],
}


# ───────────────────── 入口 ─────────────────────


def diagnose_example_p331(student_text: str, example_key, phase=None) -> Optional[ExampleDiagnosisP331]:
    """v3.x 入口：扫描所有 canonical goal（不限 phase）。

    Args:
        student_text:  学生本轮输入
        example_key:   1 / 2
        phase:         保留参数兼容旧调用，v3.x 起忽略

    Returns:
        ExampleDiagnosisP331（含 hit_goal / hit_goals / implied_flags）或 None。
    """
    if example_key not in EXAMPLE_CONFIGS_P331:
        return None
    config = EXAMPLE_CONFIGS_P331[example_key]
    canonical_map = config["canonical"]
    implies_map = config["implies"]

    hit_goals: List[str] = []

    # ── 1. 扫描所有 sympy goal ──
    # v3.45 增强：学生可能一句话写多个赋值 "p=4, x²=-8y"，按逗号/分号/和/与拆分多次 try
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

    # ── 4. 选主 goal（优先级最高的）──
    priority = _PRIORITY_BY_EXAMPLE.get(example_key, [])
    primary = next((g for g in priority if g in hit_goals), hit_goals[0])

    return ExampleDiagnosisP331(
        hit_goal=primary,
        hit_goals=hit_goals,
        implied_flags=implied_flags,
        label="完全正确",
        via="goal_scan_p331",
    )
