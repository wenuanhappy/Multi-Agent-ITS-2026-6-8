# -*- coding: utf-8 -*-
"""3.1.1 例题的 canonical 答案配置（数值 / 符号 / 方程）。

设计原则（与 GPT 校准 + user 确认）：
  · 每个例题配关键里程碑（约 6-8 个 goal），不死磕中间化简过程
  · 学生可以按"标准顺序"做，也可以跳步直答任一 goal
  · GOAL_IMPLIES：一个 goal 命中蕴含哪些 sub_flag 完成
    （如直答 2a → 视同 PF1/PF2 都完成）
  · 命中 equation goal 或 (a AND b) → 视为整道题做完，handler 推进到下一阶段

新增例题只需在本文件加一份 EXAMPLE_N_CANONICAL + GOAL_IMPLIES_N 配置即可，
diagnostician 和 handler 不动。
"""
from __future__ import annotations
import sympy
from sympy import sqrt, Rational, Eq, symbols

x, y = symbols("x y")
# 例 2/3 用到的辅助符号（学生写 P(x₀,y₀)、k_AM 等会归一化成这些 Symbol）
x0, y0 = symbols("x0 y0")
# k_AM、k_BM —— normalize 后被小写为 k_am、k_bm（Symbol 名）
k_am, k_bm = symbols("k_am k_bm")

# ────────────────────── 例 1 ──────────────────────
# F₁(-2,0), F₂(2,0)，椭圆经过 P(5/2, -3/2)，求椭圆标准方程。
#   |PF₁| = √((5/2+2)² + (3/2)²) = 3√10/2
#   |PF₂| = √((5/2-2)² + (3/2)²) = √10/2
#   2a = |PF₁| + |PF₂| = 2√10
#   a = √10,  a² = 10
#   c = 2,    c² = 4
#   b² = a² - c² = 6,  b = √6
#   方程：x²/10 + y²/6 = 1

EXAMPLE_1_CANONICAL = {
    "PF1":        3 * sqrt(10) / 2,
    "PF2":        sqrt(10) / 2,
    "2a":         2 * sqrt(10),
    "a":          sqrt(10),
    "a_squared":  10,
    "c":          2,                      # c 一般在题目给出，但学生答这个也行
    "c_squared":  4,
    "b":          sqrt(6),
    "b_squared":  6,
    "equation":   Eq(x ** 2 / 10 + y ** 2 / 6, 1),
}

# 一个 goal 命中蕴含哪些 sub_flag 完成（按教学因果顺序）
# 如直答 2a → 视同 PF1/PF2 都完成（学生已经算到 2a，前置都默认知道）
GOAL_IMPLIES_1 = {
    "PF1":        {"pf1_done"},
    "PF2":        {"pf2_done"},
    "2a":         {"pf1_done", "pf2_done", "two_a_done"},
    "a":          {"pf1_done", "pf2_done", "two_a_done", "a_done"},
    "a_squared":  {"pf1_done", "pf2_done", "two_a_done", "a_done"},
    "c":          {"c_done"},
    "c_squared":  {"c_done"},
    "b":          {"b_done"},
    "b_squared":  {"b_done"},
    "equation":   {"pf1_done", "pf2_done", "two_a_done", "a_done", "c_done", "b_done", "all_done"},
}

# 例题完成判定：哪些 sub_flag 组合代表整道题做完
# 命中 equation 直接 all_done；或者 a+b 都做完也算（学生通常先求 a、b 再写方程）
def _example_1_done(sub_flags: set) -> bool:
    if "all_done" in sub_flags:
        return True
    if "a_done" in sub_flags and "b_done" in sub_flags:
        return True
    return False


# ────────────────────── 例 2 ──────────────────────
# 圆 x²+y²=4 上动点 P(x₀, y₀)；PD ⊥ x 轴（D 为垂足），M 是 PD 中点。求 M 轨迹方程。
# 关键关系：
#   M 是中点 → x = x₀，y = y₀/2（等价 y₀ = 2y）
#   代入圆 x₀² + y₀² = 4 → x² + (2y)² = 4 → x²/4 + y² = 1
#
# canonical 等式都用 ratio 判等，所以学生写 x = x₀ / x₀ = x 都能命中；
# 写 x² + 4y² = 4 / x²/4 + y² = 1 都能命中 equation。

EXAMPLE_2_CANONICAL = {
    # 中点的横坐标关系：x = x₀（或 x₀ = x）
    "mid_x":     Eq(x0, x),
    # 中点的纵坐标关系：y = y₀/2 ↔ y₀ = 2y（关键洞察，决定压缩比）
    "mid_y":     Eq(y0, 2 * y),
    # M 的轨迹方程
    "equation":  Eq(x ** 2 / 4 + y ** 2, 1),
}

GOAL_IMPLIES_2 = {
    "mid_x":     {"mid_x_done"},
    "mid_y":     {"mid_y_done"},
    # 直接答最终方程视同所有中间步都已知
    "equation":  {"mid_x_done", "mid_y_done", "all_done"},
}

def _example_2_done(sub_flags: set) -> bool:
    # 例 2 与例 1 不同：只建立 x、y 与 x₀、y₀ 关系还没"完成"；
    # 必须代入圆方程化出最终轨迹方程才算 done。
    if "all_done" in sub_flags:
        return True
    return False


# ────────────────────── 例 3 ──────────────────────
# A(-5,0)、B(5,0)，M(x, y) 动点，k_AM · k_BM = -4/9。求 M 轨迹方程。
# 关键关系：
#   k_AM = y/(x+5)，k_BM = y/(x-5)
#   k_AM · k_BM = y²/((x+5)(x-5)) = y²/(x²-25) = -4/9
#   ⇒ 9y² = -4(x²-25) ⇒ 4x² + 9y² = 100 ⇒ x²/25 + y²/(100/9) = 1
#
# 教材会标注「除去 (±5, 0)」——属于范围说明，不在数学等价匹配范围内，由 LLM/话术处理。

EXAMPLE_3_CANONICAL = {
    # 斜率公式（Expr 形式；学生写 "k_AM = y/(x+5)" 时取 rhs 比对）
    "k_AM":           y / (x + 5),
    "k_BM":           y / (x - 5),
    # 斜率乘积代入：Eq(y/(x+5) * y/(x-5), -4/9)
    "slope_product":  Eq(y / (x + 5) * y / (x - 5), -Rational(4, 9)),
    # M 的轨迹方程（标准形式；ratio 判等可兼容 4x²+9y²=100 等任意非零倍数形式）
    "equation":       Eq(x ** 2 / 25 + 9 * y ** 2 / 100, 1),
}

GOAL_IMPLIES_3 = {
    "k_AM":          {"k_am_done"},
    "k_BM":          {"k_bm_done"},
    # 写出斜率乘积式 → 视同两个斜率都已写出
    "slope_product": {"k_am_done", "k_bm_done", "slope_product_done"},
    # 直接答最终方程视同所有中间步都已知
    "equation":      {"k_am_done", "k_bm_done", "slope_product_done", "all_done"},
}

def _example_3_done(sub_flags: set) -> bool:
    if "all_done" in sub_flags:
        return True
    return False


# ────────────────────── 总表 ──────────────────────
EXAMPLE_CONFIGS = {
    1: {"canonical": EXAMPLE_1_CANONICAL, "implies": GOAL_IMPLIES_1, "done_fn": _example_1_done},
    2: {"canonical": EXAMPLE_2_CANONICAL, "implies": GOAL_IMPLIES_2, "done_fn": _example_2_done},
    3: {"canonical": EXAMPLE_3_CANONICAL, "implies": GOAL_IMPLIES_3, "done_fn": _example_3_done},
}
