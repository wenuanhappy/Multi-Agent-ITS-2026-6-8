# -*- coding: utf-8 -*-
"""3.1.2「椭圆的简单几何性质」例题 canonical 答案配置。

设计原则（与 3.1.1 区分）：
  · 老师每 phase 单 goal 逐项问 → phase 内不存在多命中冲突 → **无 priority 数组**
  · 点集合用 frozenset of (int, int)；诊断器从学生输入抽取所有 (n, n) 后做集合比对
  · ± 简写在诊断器层展开（如 "(±5,0)" → {(5,0), (-5,0)}）
  · 区间不等式用 sympy.Interval / Union；多值用 frozenset
  · 部分 phase 走"关键词路由"（如"椭圆+长10+短6"），phase_goal 填 None，
    由 example_diagnostician_312.py 内的 looks_like_* 函数额外识别

例 4：教材 p112  16x²+25y²=400  → 长轴/短轴/e/焦点/顶点（5 phase）
例 5：教材 p113  |MF|/d = 4/5  → 准线比例反推椭圆（3 phase）
例 6：教材 p114  直线 4x-5y+m=0 与椭圆  → m 三类讨论（3 phase）

3.1.1 的 example_canonicals.py / example_diagnostician.py 一行不动。
"""
from __future__ import annotations

from sympy import Eq, Integer, Interval, Rational, Union, oo, symbols

x, y = symbols("x y")
m = symbols("m")


# ────────────────────── 例 4 ──────────────────────
# 16x² + 25y² = 400  →  x²/25 + y²/16 = 1
# a=5, b=4, c=3 → 长轴=10、短轴=8、e=3/5、焦点(±3,0)、顶点(±5,0)(0,±4)

EXAMPLE_4_CANONICAL = {
    "major_axis":  Integer(10),     # 2a
    "minor_axis":  Integer(8),      # 2b
    "e":           Rational(3, 5),  # 离心率
    "focus_set":   frozenset({(-3, 0), (3, 0)}),
    "vertex_set":  frozenset({(-5, 0), (5, 0), (0, -4), (0, 4)}),
}

EXAMPLE_4_PHASES = [
    "ask_major_axis", "ask_minor_axis", "ask_eccentricity", "ask_focus", "ask_vertex",
]

EXAMPLE_4_PHASE_GOAL = {
    "ask_major_axis":   "major_axis",
    "ask_minor_axis":   "minor_axis",
    "ask_eccentricity": "e",
    "ask_focus":        "focus_set",
    "ask_vertex":       "vertex_set",
}

GOAL_IMPLIES_4 = {
    "major_axis":  {"major_axis_done"},
    "minor_axis":  {"minor_axis_done"},
    "e":           {"e_done"},
    "focus_set":   {"focus_done"},
    "vertex_set":  {"vertex_done"},
}

def _example_4_done(sub_flags: set) -> bool:
    return {"major_axis_done", "minor_axis_done", "e_done", "focus_done", "vertex_done"}.issubset(sub_flags)


# ────────────────────── 例 5 ──────────────────────
# 教材 p113 例 6 ：|MF|/d = 4/5，F(4,0)，l: x=25/4
#   √((x-4)²+y²) / |25/4 - x| = 4/5
#   平方化简 → 9x²+25y²=225 → x²/25 + y²/9 = 1（长轴 10、短轴 6）
#
# 学生第一步要写出"距离比 = 4/5"的关系（关键词识别，写法多变），
# 第二步给出化简后的椭圆方程（sympy ratio 判等 9x²+25y²=225 / x²/25+y²/9=1 均认），
# 第三步说出"椭圆 + 长 10 + 短 6"结论（关键词识别）。

EXAMPLE_5_CANONICAL = {
    # ask_relation 走关键词，不进此表
    "equation_simplified": Eq(x**2 / 25 + y**2 / 9, 1),
    # ask_conclude 走关键词，不进此表
}

EXAMPLE_5_PHASES = ["ask_relation", "ask_simplify", "ask_conclude"]
EXAMPLE_5_PHASE_GOAL = {
    "ask_relation": None,                   # looks_like_distance_ratio_4_5
    "ask_simplify": "equation_simplified",
    "ask_conclude": None,                   # looks_like_ellipse_with_axes_10_6
}

GOAL_IMPLIES_5 = {
    "equation_simplified": {"simplify_done"},
}

def _example_5_done(sub_flags: set) -> bool:
    return {"relation_done", "simplify_done", "conclude_done"}.issubset(sub_flags)


# ────────────────────── 例 6 ──────────────────────
# 教材 p114 例 7：直线 l: 4x-5y+m=0 与椭圆 C: x²/25+y²/9=1
# 联立消 y → 25x² + 8mx + m² - 225 = 0
# Δ = 36(625-m²)
# (1) Δ>0 → -25<m<25：直线与 C 有 2 个公共点
# (2) Δ=0 → m=±25：直线与 C 有且仅有 1 个公共点
# (3) Δ<0 → m<-25 或 m>25：直线与 C 没有公共点
#
# user #2 明确：m=±25 等价于 -25 或 25，宽松判等（不要求集合表示）

EXAMPLE_6_CANONICAL = {
    "range_two_points":  Interval.open(-25, 25),
    "value_one_point":   frozenset({-25, 25}),
    "range_no_point":    Union(Interval.open(-oo, -25), Interval.open(25, oo)),
}

EXAMPLE_6_PHASES = ["ask_two_points", "ask_one_point", "ask_no_point"]
EXAMPLE_6_PHASE_GOAL = {
    "ask_two_points": "range_two_points",
    "ask_one_point":  "value_one_point",
    "ask_no_point":   "range_no_point",
}

GOAL_IMPLIES_6 = {
    "range_two_points": {"two_points_done"},
    "value_one_point":  {"one_point_done"},
    "range_no_point":   {"no_point_done"},
}

def _example_6_done(sub_flags: set) -> bool:
    return {"two_points_done", "one_point_done", "no_point_done"}.issubset(sub_flags)


# ────────────────────── 总表 ──────────────────────
EXAMPLE_CONFIGS_312 = {
    4: {
        "canonical":  EXAMPLE_4_CANONICAL,
        "phases":     EXAMPLE_4_PHASES,
        "phase_goal": EXAMPLE_4_PHASE_GOAL,
        "implies":    GOAL_IMPLIES_4,
        "done_fn":    _example_4_done,
    },
    5: {
        "canonical":  EXAMPLE_5_CANONICAL,
        "phases":     EXAMPLE_5_PHASES,
        "phase_goal": EXAMPLE_5_PHASE_GOAL,
        "implies":    GOAL_IMPLIES_5,
        "done_fn":    _example_5_done,
    },
    6: {
        "canonical":  EXAMPLE_6_CANONICAL,
        "phases":     EXAMPLE_6_PHASES,
        "phase_goal": EXAMPLE_6_PHASE_GOAL,
        "implies":    GOAL_IMPLIES_6,
        "done_fn":    _example_6_done,
    },
}
