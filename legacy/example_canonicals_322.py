# -*- coding: utf-8 -*-
"""3.2.2「双曲线的简单几何性质」例题与思考 canonical 答案配置。

v3.46 重构：参照 example_canonicals_321.py 的 311-style 模式（goal + GOAL_IMPLIES + done_fn）。
设计理念见 论文补充文献_两个技术创新点.md 2.5.5 节。

设计原则（与 311/321 对齐）：
  · 每例配关键里程碑（goal），不死磕教学 phase 顺序
  · 学生可以按"标准顺序"答（先 form → ab → ...），也可以**跳步直答**任一 goal
  · GOAL_IMPLIES：一个 goal 命中蕴含哪些 sub_flag 完成
    （如直答 ab_length → 视同前置全部已掌握）
  · done_fn：检查 sub_flags 是否满足整道题完成（all_done 或具体 flag 组合）

3.2.2 例题（内部编号 1/2/3，对应教材例 3/5/6）：
  例 1：教材 p124 例 3   9y²-16x²=144 → y²/16-x²/9=1（焦点 y 轴）
                        a=4, b=3, c=5；焦点 (0,±5)；e=5/4；渐近线 y=±(4/3)x
  例 2：教材 p125 例 5   |MF|/d=4/3, F(4,0), l: x=9/4
                        7x²-9y²=63 → x²/9-y²/7=1；焦点 x 轴、实轴长 6、虚轴长 2√7
  例 3：教材 p126 例 6   焦点弦 倾斜角 30°，过 x²/3-y²/6=1 右焦点 F₂(3,0)
                        直线 y=(√3/3)(x-3)；联立 5x²+6x-27=0
                        x₁=-3, x₂=9/5；A(-3,-2√3), B(9/5,-2√3/5)
                        |AB|=16√3/5

3.1.1 / 3.1.2 / 3.2.1 的 example_canonicals_*.py 一行不动。
"""
from __future__ import annotations

from sympy import Eq, Integer, Rational, sqrt, symbols

x, y = symbols("x y")

# ────────────────────── 例 1（教材 p124 例 3） ──────────────────────
# 9y² - 16x² = 144  →  y²/16 - x²/9 = 1（焦点在 y 轴）
#   a²=16, a=4 (实半轴长)；b²=9, b=3 (虚半轴长)
#   c² = a² + b² = 25, c=5
#   焦点 (0,-5), (0,5)；离心率 e = c/a = 5/4
#   渐近线（焦点在 y 轴时）：y = ±(a/b) x = ±(4/3) x

EXAMPLE_1_CANONICAL = {
    "form_kw":        None,                       # "焦点在 y 轴 + y²/a²-x²/b²=1 形式"
    "standard_eq":    Eq(y**2 / 16 - x**2 / 9, 1),
    "a":              Integer(4),
    "b":              Integer(3),
    "c":              Integer(5),
    "a_squared":      Integer(16),
    "b_squared":      Integer(9),
    "c_squared":      Integer(25),
    "e":              Rational(5, 4),
    "focus_set":      frozenset({(0, -5), (0, 5)}),
    "asymptote_kw":   None,                       # "y = ±(4/3) x"
    "asymptote_eq_pos": Eq(y, Rational(4, 3) * x),
    "asymptote_eq_neg": Eq(y, -Rational(4, 3) * x),
}

EXAMPLE_1_PHASES = [
    "ask_form", "ask_ab", "ask_focus", "ask_eccentricity", "ask_asymptote",
]
EXAMPLE_1_PHASE_GOAL = {
    "ask_form":         "standard_eq",
    "ask_ab":           None,                     # 多 goal（a 和 b 同时答完才推进）
    "ask_focus":        "focus_set",
    "ask_eccentricity": "e",
    "ask_asymptote":    None,                     # asymptote_kw 或 双 Eq
}

GOAL_IMPLIES_1 = {
    "form_kw":           {"form_done"},
    "standard_eq":       {"form_done", "standard_eq_done"},
    "a":                 {"a_done"},
    "b":                 {"b_done"},
    "c":                 {"c_done"},
    "a_squared":         {"a_done"},
    "b_squared":         {"b_done"},
    "c_squared":         {"c_done"},
    "e":                 {"e_done", "a_done", "c_done"},
    "focus_set":         {"focus_done", "a_done", "c_done"},
    "asymptote_kw":      {"asymptote_done", "a_done", "b_done"},
    # v3.49：学生用 ±(4/3)x 形式时 sympy 通常只解析出一边（pos 或 neg）；
    # 数学上 ±(b/a)x 已完整表达两条直线，任一命中即标 asymptote_done
    "asymptote_eq_pos":  {"asymptote_pos_done", "asymptote_done"},
    "asymptote_eq_neg":  {"asymptote_neg_done", "asymptote_done"},
}


def _example_1_done(sub_flags: set) -> bool:
    """例 1 完成判定：
      · 标准方程 + a/b + 焦点 + e + 渐近线 全完成 → 完成
      · 渐近线 asymptote_done（关键词命中 / sympy 单边命中 / 双边命中，任一）
    v3.49：与 GOAL_IMPLIES 同步，sympy 单边 pos 或 neg 命中已标 asymptote_done。
    """
    has_asymptote = "asymptote_done" in sub_flags
    required = {"form_done", "a_done", "b_done", "focus_done", "e_done"}
    return required.issubset(sub_flags) and has_asymptote


# ────────────────────── 例 2（教材 p125 例 5） ──────────────────────
# |MF|/d = 4/3, F(4,0), l: x = 9/4
#   √((x-4)²+y²) / |x - 9/4| = 4/3
#   平方 + 化简 → 7x² - 9y² = 63
#   即 x²/9 - y²/7 = 1
#   a²=9, a=3, 2a=6 (实轴长)；b²=7, b=√7, 2b=2√7 (虚轴长)；c²=16, c=4
#   焦点 F(4,0) 在 x 轴上

EXAMPLE_2_CANONICAL = {
    # ask_relation 走关键词路由（学生需写出 |MF|/d = 4/3 关系式）
    "relation_kw":         None,
    # 化简中间步与最终标准方程都接受
    "equation_raw":        Eq(7 * x**2 - 9 * y**2, 63),
    "equation_simplified": Eq(x**2 / 9 - y**2 / 7, 1),
    # ask_conclude 走关键词路由（结论："焦点在 x 轴上、实轴长 6、虚轴长 2√7"）
    "conclude_kw":          None,
}

EXAMPLE_2_PHASES = ["ask_relation", "ask_simplify", "ask_conclude"]
EXAMPLE_2_PHASE_GOAL = {
    "ask_relation":  None,                        # looks_like_distance_ratio_4_3
    "ask_simplify":  "equation_simplified",        # 兼容 equation_raw（诊断器扫两个 goal）
    "ask_conclude":  None,                        # looks_like_hyperbola_real_6_imag_2sqrt7
}

GOAL_IMPLIES_2 = {
    "relation_kw":          {"relation_done"},
    "equation_raw":         {"simplify_done", "equation_done"},
    "equation_simplified":  {"simplify_done", "equation_done"},
    "conclude_kw":          {"conclude_done"},
}


def _example_2_done(sub_flags: set) -> bool:
    """例 2 完成判定：关系 + 方程 + 结论 三步全完成。"""
    return {"relation_done", "equation_done", "conclude_done"}.issubset(sub_flags)


# ────────────────────── 例 3（教材 p126 例 6） ──────────────────────
# 过双曲线 x²/3 - y²/6 = 1 的右焦点 F₂(3,0)，倾斜角 30° 的直线交曲线于 A, B
#   a²=3, b²=6, c²=9, c=3 → F₁(-3,0), F₂(3,0)
#   直线方程：y = tan(30°) · (x - 3) = (√3/3)(x - 3)
#   联立消 y → 5x² + 6x - 27 = 0
#   解得 x₁ = -3, x₂ = 9/5
#   代回直线方程：y₁ = -2√3, y₂ = -2√3/5
#   A(-3, -2√3), B(9/5, -2√3/5)
#   |AB|² = (-3 - 9/5)² + (-2√3 + 2√3/5)²
#         = (24/5)² + (8√3/5)² = 576/25 + 192/25 = 768/25
#   |AB| = √(768)/5 = 16√3/5

EXAMPLE_3_CANONICAL = {
    "focus_set":   frozenset({(-3, 0), (3, 0)}),                # 焦点
    "line_eq":     Eq(y, Rational(1, 3) * sqrt(3) * (x - 3)),   # 直线方程
    "quadratic":   Eq(5 * x**2 + 6 * x - 27, 0),                # 联立消 y 后
    "x_set":       frozenset({-3, Rational(9, 5)}),             # 两个 x 值
    # v3.48：拆 A、B 两点为独立 sub-goal（仿 312 例 4 partial_hit_point_set 累积模式）
    # 含 √3 无法用 sympy frozenset of int tuple；改关键词路由 + 各自独立 done flag
    "point_A":     None,    # 关键词路由：含 -3 + √3，不含 9/5
    "point_B":     None,    # 关键词路由：含 9/5 + √3，不含 -3
    "point_set":   None,    # 综合关键词：同一句话含 A、B 两组特征
    "ab_length":   16 * sqrt(3) / 5,                            # 最终答案
}

EXAMPLE_3_PHASES = ["ask_line", "ask_intersect", "ask_points", "ask_length"]
EXAMPLE_3_PHASE_GOAL = {
    "ask_line":      "line_eq",
    "ask_intersect": "quadratic",     # 或 x_set（诊断器扫两个）
    "ask_points":    None,            # 关键词路由（点坐标含根号，普通比对不稳）+ 累积
    "ask_length":    "ab_length",
}

GOAL_IMPLIES_3 = {
    "focus_set":  {"focus_done"},
    "line_eq":    {"line_done", "focus_done"},
    "quadratic":  {"intersect_done", "line_done", "focus_done"},
    "x_set":      {"intersect_done", "x_set_done"},
    # v3.48：A、B 拆点；独立 done flag 允许累积，两者齐才 points_done
    "point_A":    {"point_A_done"},
    "point_B":    {"point_B_done"},
    "point_set":  {"point_A_done", "point_B_done", "points_done",
                   "intersect_done", "line_done", "focus_done"},
    "ab_length":  {"length_done", "point_A_done", "point_B_done", "points_done",
                   "intersect_done", "line_done", "focus_done", "all_done"},
}


def _example_3_done(sub_flags: set) -> bool:
    """例 3 完成判定：
      · all_done（学生直答 |AB|=16√3/5，触发 ab_length 全链）→ 完成
      · 或 line + intersect + length 三步达成 → 完成
    v3.48：A、B 拆点不直接影响 done_fn（学生跳级答 |AB| 仍可触发 all_done）。
    """
    if "all_done" in sub_flags:
        return True
    return {"line_done", "intersect_done", "length_done"}.issubset(sub_flags)


# ────────────────────── 配置总表 ──────────────────────
EXAMPLE_CONFIGS_322 = {
    1: {
        "canonical":  EXAMPLE_1_CANONICAL,
        "phases":     EXAMPLE_1_PHASES,
        "phase_goal": EXAMPLE_1_PHASE_GOAL,
        "implies":    GOAL_IMPLIES_1,
        "done_fn":    _example_1_done,
    },
    2: {
        "canonical":  EXAMPLE_2_CANONICAL,
        "phases":     EXAMPLE_2_PHASES,
        "phase_goal": EXAMPLE_2_PHASE_GOAL,
        "implies":    GOAL_IMPLIES_2,
        "done_fn":    _example_2_done,
    },
    3: {
        "canonical":  EXAMPLE_3_CANONICAL,
        "phases":     EXAMPLE_3_PHASES,
        "phase_goal": EXAMPLE_3_PHASE_GOAL,
        "implies":    GOAL_IMPLIES_3,
        "done_fn":    _example_3_done,
    },
}
