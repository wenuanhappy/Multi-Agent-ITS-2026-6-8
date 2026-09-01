# -*- coding: utf-8 -*-
"""3.3.2「抛物线的简单几何性质」例题 / 思考 canonical 答案配置。

参照 example_canonicals_p331.py 的模式（goal + GOAL_IMPLIES + done_fn + phases + phase_goal）。
设计见 docs/3.3.2_design_phase1.md。

3 道题（按 stage 顺序编号 key=1..3）：
  key=1 例题 1（教材原编号 例 3，p134）：
        已知抛物线关于 x 轴对称、顶点在原点、过点 M(2, −2√2)，求标准方程。
        设 y²=2px → (−2√2)²=2p·2 → 8=4p → p=2 → 标准方程 y²=4x。
  key=2 思考（教材 p135 思考栏，例 3 与例 4 之间）：
        顶点在原点、对称轴是坐标轴（x 轴或 y 轴）、过 M(2,−2√2) 的抛物线有几条？求标准方程。
        共 2 条：① 轴=x 轴、开口向右 y²=4x；② 轴=y 轴、开口向下 x²=−√2 y（p=√2/2）。
  key=3 例题 2（教材原编号 例 4，p135）：
        斜率为 1 的直线 l 经过抛物线 y²=4x 的焦点 F，与抛物线交于 A、B，求 |AB|。
        p=2，焦点 F(1,0)，准线 x=−1；y=x−1 代入得 x²−6x+1=0 → x₁+x₂=6 → |AB|=x₁+x₂+2=8。

3.1.1 / 3.1.2 / 3.2.1 / 3.2.2 / 3.3.1 的 example_canonicals_*.py 一行不动。
"""
from __future__ import annotations

from sympy import Eq, Integer, sqrt, symbols

x, y = symbols("x y")


# ────────────────────── 例题 1（教材 例 3）求标准方程 ──────────────────────
# 关于 x 轴对称 + 顶点原点 → 设 y²=2px；过 M(2,−2√2) → 8=4p → p=2 → y²=4x

EXAMPLE_1_CANONICAL = {
    "form_kw":     None,                  # 关键词：设 y²=2px / 开口向右 / 关于 x 轴对称
    "p_1":         Integer(2),            # p=2
    "equation_1":  Eq(y**2, 4 * x),       # y²=4x
}

EXAMPLE_1_PHASES = ["ask_form", "ask_eq"]

EXAMPLE_1_PHASE_GOAL = {
    "ask_form": None,            # 关键词路由
    "ask_eq":   "equation_1",
}

GOAL_IMPLIES_1 = {
    "form_kw":     {"form_1_done"},
    "p_1":         {"p_1_done", "form_1_done"},                 # 求出 p 暗含已定形式
    "equation_1":  {"equation_1_done", "p_1_done", "form_1_done"},  # 直答方程 → 全 done
}


def _example_1_done(sub_flags: set) -> bool:
    """例题 1 完成判定：写出标准方程 y²=4x。"""
    return "equation_1_done" in sub_flags


# ────────────────────── 思考（教材 p135 思考栏）2 条抛物线 ──────────────────────
# 对称轴放宽为坐标轴（x 轴或 y 轴）：
#   ① 轴=x 轴、开口向右：y²=4x
#   ② 轴=y 轴、开口向下：x²=−√2 y（2p=√2 → p=√2/2）

EXAMPLE_2_CANONICAL = {
    "count_2":     None,                       # 关键词：2 条 / 两条
    "eq_xaxis":    Eq(y**2, 4 * x),            # 轴=x 轴
    "eq_yaxis":    Eq(x**2, -sqrt(2) * y),     # 轴=y 轴（sympy 严谨）
    "eq_yaxis_kw": None,                       # 关键词兜底（防 "x²=-√2y" 无空格误解析为 √(y)）
}

EXAMPLE_2_PHASES = ["ask_count", "ask_eqs"]

EXAMPLE_2_PHASE_GOAL = {
    "ask_count": None,           # 关键词路由（几条）
    "ask_eqs":   None,           # 两方程拆维度 partial 累积
}

GOAL_IMPLIES_2 = {
    "count_2":     {"count_done"},
    "eq_xaxis":    {"eq_xaxis_done"},
    "eq_yaxis":    {"eq_yaxis_done"},
    "eq_yaxis_kw": {"eq_yaxis_done"},
}


def _example_2_done(sub_flags: set) -> bool:
    """思考完成判定：两条标准方程都答出（count 仅引导，不强制）。"""
    return {"eq_xaxis_done", "eq_yaxis_done"}.issubset(sub_flags)


# ────────────────────── 例题 2（教材 例 4）焦点弦 |AB| ──────────────────────
# y²=4x → p=2，焦点 F(1,0)，准线 x=−1；y=x−1 代入 → x²−6x+1=0 → x₁+x₂=6 → |AB|=8

EXAMPLE_3_CANONICAL = {
    "focus_kw":  None,             # 关键词：焦点 (1, 0)
    "directrix": Eq(x, -1),        # 准线 x=−1（sympy）
    "sum_x":     Integer(6),       # x₁+x₂=6（"x1+x2=6" 取 rhs / "6" 直接命中）
    "ab":        Integer(8),       # |AB|=8（"|AB|=8" 取 rhs / "8" 直接命中）
}

EXAMPLE_3_PHASES = ["ask_setup", "ask_intersect", "ask_ab"]

EXAMPLE_3_PHASE_GOAL = {
    "ask_setup":     None,         # 焦点 + 准线两要素累积（关键词 + sympy）
    "ask_intersect": "sum_x",
    "ask_ab":        "ab",
}

GOAL_IMPLIES_3 = {
    "focus_kw":  {"focus_done"},
    "directrix": {"directrix_done"},
    "sum_x":     {"intersect_done", "focus_done", "directrix_done"},   # 求出和暗含已建系
    "ab":        {"ab_done", "intersect_done", "focus_done", "directrix_done"},  # 直答 |AB| → 全 done
}


def _example_3_done(sub_flags: set) -> bool:
    """例题 2 完成判定：求出 |AB|=8。"""
    return "ab_done" in sub_flags


# ────────────────────── 配置总表 ──────────────────────
EXAMPLE_CONFIGS_332 = {
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
