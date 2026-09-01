# -*- coding: utf-8 -*-
"""3.1.2 例题诊断器：phase 驱动，独立于 3.1.1 的 example_diagnostician。

3.1.1 共用 priority 数组排序（一句话多命中时挑主要 goal）。3.1.2 老师每 phase 单 goal
逐项问，**不存在多命中冲突**，因此不需要 priority。

入口：
  diagnose_example_312(student_text, example_num, phase) -> Optional[ExampleDiagnosis312]

支持的 canonical 类型（每 phase 单 type，由 example_canonicals_312.EXAMPLE_*_PHASE_GOAL 决定）：
  · sympy Expr / Eq （数、方程）—— 用 ratio 判等（复用 3.1.1 的 _equivalent）
  · frozenset of (int, int) （点集合：顶点、焦点）—— 用 regex 抽点 + ± 展开 + 集合比对
  · frozenset of int （多值：例 6 的 m=±25）—— 用 regex 抽数 + ± 展开 + 集合比对
  · sympy.Interval / Union （区间不等式）—— 用关键词 + 数字模式启发式判断
  · phase_goal=None → 走 looks_like_* 关键词路由（例 5 的 ask_relation / ask_conclude）

3.1.1 的 example_diagnostician.py / example_canonicals.py 一行不动。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple

import sympy
from sympy import Eq, Expr, Interval, Union

from .example_canonicals_312 import EXAMPLE_CONFIGS_312
from core.example_diagnostician import _equivalent as _equivalent_scalar  # 复用 3.1.1 的 Eq/Expr ratio 判等
from core.math_normalizer import parse as parse_input


@dataclass
class ExampleDiagnosis312:
    hit_goal: Optional[str] = None           # 命中的 canonical goal 名（关键词路由时为字符串如 "relation_kw"）
    implied_flags: Set[str] = field(default_factory=set)
    label: str = ""                           # "完全正确" or ""
    via: str = ""                             # "scalar" / "point_set" / "value_set" / "interval" / "keyword"


# ───────────────────── 文本归一化工具 ─────────────────────

_NEG_SIGNS = "−–—－"   # 各种 Unicode 负号
_PLUS_SIGNS = "＋"

def _normalize_text(text: str) -> str:
    """归一化全角/Unicode 符号到 ASCII，但**保留**逗号/或字/绝对值竖线，供后续解析。"""
    t = text
    for ch in _NEG_SIGNS:
        t = t.replace(ch, "-")
    for ch in _PLUS_SIGNS:
        t = t.replace(ch, "+")
    t = t.replace("，", ",").replace("（", "(").replace("）", ")")
    return t


# ───────────────────── 点集合判等（顶点、焦点）─────────────────────

_TUPLE_RE = re.compile(r"\(\s*([+\-±]?\d+)\s*,\s*([+\-±]?\d+)\s*\)")

def _expand_pm_int(s: str) -> List[int]:
    """'±5' → [5, -5]；'5' → [5]；'-3' → [-3]；'+4' → [4]"""
    s = s.strip()
    if s.startswith("±"):
        n = int(s[1:])
        return [n, -n]
    return [int(s)]


def _extract_point_tuples(text: str) -> Set[Tuple[int, int]]:
    """提取学生输入里所有 (a, b) 形式的点，自动展开 ± 简写。"""
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
    return student_points == set(canonical)


def partial_hit_point_set(text: str, canonical: frozenset) -> set:
    """v3.30: 提取学生输入中属于 canonical 的点（部分命中支持累积）。
    返回学生答的点 ∩ canonical。非空 → 部分对；等于 canonical → 完整对。
    """
    student_points = _extract_point_tuples(text)
    return student_points & set(canonical)


# ───────────────────── 多值枚举判等（例 6 ask_one_point）─────────────────────

# 单个数字模式（带可选 ± / 负号），不在括号内（避免抓到点坐标里的）
_SOLO_NUM_RE = re.compile(r"(?<![\d\(])([+\-±]?\d+)(?![\d\)])")

def _extract_value_set(text: str) -> Set[int]:
    """从文本中提取所有数字（展开 ±），用于多值答案识别。"""
    text = _normalize_text(text)
    values: Set[int] = set()
    for match in _SOLO_NUM_RE.finditer(text):
        for n in _expand_pm_int(match.group(1)):
            values.add(n)
    return values


def _equivalent_value_set(text: str, canonical: frozenset) -> bool:
    """学生写 '±25' / '-25 或 25' / '{-25, 25}' / 'm=25 或 m=-25' 都算对。"""
    student_values = _extract_value_set(text)
    return student_values == set(canonical)


# ───────────────────── 区间不等式判等（例 6 ask_two_points / ask_no_point）─────────────────────

def _equivalent_interval(text: str, canonical) -> bool:
    """启发式判断学生输入是否匹配 canonical 区间（Interval 或 Interval 的 Union）。

    支持写法（针对例 6 的 ±25 边界）：
      · two_points (-25<m<25): "-25<m<25" / "|m|<25" / "m ∈ (-25, 25)" / "m 属于 (-25,25)"
      · no_point (m<-25 或 m>25): "m<-25 或 m>25" / "|m|>25" / "m∉[-25,25]"
    """
    t_raw = text
    t = _normalize_text(text).replace(" ", "")
    values = _extract_value_set(text)

    # 期待答案的边界值（绝对值集合）
    if isinstance(canonical, Interval):
        # 单 Interval：开区间 (-25, 25) 这种
        a, b = canonical.start, canonical.end
        bounds = {abs(int(a)), abs(int(b))} if a.is_finite and b.is_finite else None
    elif isinstance(canonical, Union):
        # Union of two open intervals: (-oo, -25) ∪ (25, oo)
        bound_set: Set[int] = set()
        for sub in canonical.args:
            if isinstance(sub, Interval):
                if sub.start.is_finite:
                    bound_set.add(abs(int(sub.start)))
                if sub.end.is_finite:
                    bound_set.add(abs(int(sub.end)))
        bounds = bound_set
    else:
        return False

    # 学生输入提到的所有数字的绝对值
    student_abs = {abs(v) for v in values}

    # 边界数字必须匹配（如答案 ±25，学生写的数字也必须是 25 这一个绝对值，可正可负）
    if bounds is None or student_abs != bounds:
        return False

    has_lt = "<" in t
    has_gt = ">" in t
    has_or = any(kw in t_raw for kw in ["或", " or ", " OR "])
    has_abs_m = "|m|" in t
    has_in_set = ("∈" in t_raw) or ("属于" in t_raw)

    if isinstance(canonical, Interval):
        # 双侧夹击形式：包含 -25 和 25 且使用 < 双向夹（如 "-25<m<25"）
        if has_lt and not has_or and ("-25" in t and "25" in t):
            # 排除 "m<-25 或 m>25" 形式（带或）
            return True
        # 绝对值形式：|m|<25
        if has_abs_m and has_lt and not has_gt:
            return True
        # m ∈ (-25, 25) 或 "m 属于 (-25, 25)"
        if has_in_set and "-25" in t and "25" in t:
            return True
        return False

    if isinstance(canonical, Union):
        # m<-25 或 m>25
        if has_or and has_lt and has_gt:
            return True
        # |m|>25
        if has_abs_m and has_gt and not has_lt:
            return True
        return False

    return False


# ───────────────────── scalar (Eq/Expr) 判等：复用 3.1.1 引擎 ─────────────────────

def _diagnose_scalar(student_text: str, canonical) -> bool:
    parsed = parse_input(student_text)
    if parsed is None:
        return False
    if isinstance(parsed, sympy.logic.boolalg.BooleanAtom):
        return False
    return _equivalent_scalar(parsed, canonical)


# ───────────────────── 关键词路由（例 5 ask_relation / ask_conclude）─────────────────────

def _looks_like_distance_ratio_4_5(text: str) -> bool:
    """例 5 ask_relation：学生说出"距离比 4/5"或"|MF|/d = 4/5"。"""
    t = _normalize_text(text).replace(" ", "")
    # 必须出现 4/5 或 0.8 这个常数
    has_ratio = ("4/5" in t) or ("0.8" in t) or ("4：5" in text) or ("4:5" in t)
    if not has_ratio:
        return False
    # 必须有"距离比 / |MF|/d / |MF|:d / 比值" 之类的提示
    relation_kws = ["距离比", "比值", "比是", "|mf|", "|MF|", "mf/d", "MF/d", "比", "ratio"]
    return any(kw.lower() in text.lower() for kw in relation_kws)


def _looks_like_ellipse_with_axes_10_6(text: str) -> bool:
    """例 5 ask_conclude：学生说"椭圆 + 长轴 10 + 短轴 6"。"""
    has_ellipse = "椭圆" in text
    has_10 = "10" in text
    has_6 = "6" in text
    # 长 / 短 关键词（允许"长轴""长""主轴"）
    has_major = any(kw in text for kw in ["长轴", "长 轴", "主轴", "长 ", "长"])
    has_minor = any(kw in text for kw in ["短轴", "短 轴", "次轴", "短 ", "短"])
    return has_ellipse and has_10 and has_6 and has_major and has_minor


# ───────────────────── 入口 ─────────────────────

def diagnose_example_312(student_text: str, example_num: int, phase: str) -> Optional[ExampleDiagnosis312]:
    """phase 驱动诊断。

    无命中返回 None；命中返回 ExampleDiagnosis312。
    """
    if example_num not in EXAMPLE_CONFIGS_312:
        return None
    config = EXAMPLE_CONFIGS_312[example_num]
    phase_goal_map = config["phase_goal"]
    implies_map = config["implies"]

    if phase not in phase_goal_map:
        return None
    goal_name = phase_goal_map[phase]

    # ── 关键词路由（phase_goal=None）──
    if goal_name is None:
        # 例 5 的两个 phase
        if example_num == 5 and phase == "ask_relation":
            if _looks_like_distance_ratio_4_5(student_text):
                return ExampleDiagnosis312(
                    hit_goal="relation_kw",
                    implied_flags={"relation_done"},
                    label="完全正确",
                    via="keyword",
                )
            return None
        if example_num == 5 and phase == "ask_conclude":
            if _looks_like_ellipse_with_axes_10_6(student_text):
                return ExampleDiagnosis312(
                    hit_goal="conclude_kw",
                    implied_flags={"conclude_done"},
                    label="完全正确",
                    via="keyword",
                )
            return None
        return None

    # ── 取 canonical，分类型判等 ──
    canonical = config["canonical"][goal_name]

    # 点集合
    if isinstance(canonical, frozenset) and canonical and isinstance(next(iter(canonical)), tuple):
        if _equivalent_point_set(student_text, canonical):
            return ExampleDiagnosis312(
                hit_goal=goal_name,
                implied_flags=set(implies_map.get(goal_name, set())),
                label="完全正确",
                via="point_set",
            )
        return None

    # 多值集合（int）
    if isinstance(canonical, frozenset):
        if _equivalent_value_set(student_text, canonical):
            return ExampleDiagnosis312(
                hit_goal=goal_name,
                implied_flags=set(implies_map.get(goal_name, set())),
                label="完全正确",
                via="value_set",
            )
        return None

    # 区间 / Union
    if isinstance(canonical, (Interval, Union)):
        if _equivalent_interval(student_text, canonical):
            return ExampleDiagnosis312(
                hit_goal=goal_name,
                implied_flags=set(implies_map.get(goal_name, set())),
                label="完全正确",
                via="interval",
            )
        return None

    # scalar (Eq / Expr / Integer / Rational)
    if isinstance(canonical, (Eq, Expr)) or hasattr(canonical, "is_number"):
        if _diagnose_scalar(student_text, canonical):
            return ExampleDiagnosis312(
                hit_goal=goal_name,
                implied_flags=set(implies_map.get(goal_name, set())),
                label="完全正确",
                via="scalar",
            )
        return None

    return None
