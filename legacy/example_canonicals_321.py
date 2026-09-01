# -*- coding: utf-8 -*-
"""3.2.1「双曲线及其标准方程」例题与探究 canonical 答案配置。

v3.45 重构：参照 3.1.1 example_canonicals.py 的 goal + GOAL_IMPLIES + done_fn 模式
（参见 docs/scheme_D_design.md 末段「跳级答题问题与 311-style 解决」）

设计原则（与 311 对齐）：
  · 每例配关键里程碑（goal），不死磕教学 phase 顺序
  · 学生可以按"标准顺序"答（先 form → ab → equation），也可以**跳步直答**任一 goal
  · GOAL_IMPLIES：一个 goal 命中蕴含哪些 sub_flag 完成
    （如直答 equation → 视同 a/b/c/form 都已掌握）
  · done_fn：检查 sub_flags 是否满足整道题完成（all_done 或具体 flag 组合）

3.2.1 与 3.1.1 的差异：
  · 例 2 有"分支约束"x≥340，必须方程 + 分支都答对才算完整
  · 探究有"约束"x≠±5，类似
  · 部分 goal 走关键词路由（_kw 后缀，phase_goal=None）

phases 列表保留，作为"教学提问节奏"（按顺序问 form/ab/equation），
但诊断器不再被 phases 约束——任意 goal 命中都生效。

例 1：教材 p120  焦点 F₁(-5,0) F₂(5,0)，距离差绝对值=6 → x²/9 - y²/16 = 1
例 2：教材 p120  声学应用，A 听到比 B 晚 2 s → x²/115600 - y²/44400 = 1 (x ≥ 340)
探究：教材 p121  斜率积 4/9 → x²/25 - y²/(100/9) = 1 (x ≠ ±5)
"""
from __future__ import annotations

from sympy import Eq, Integer, Rational, symbols

x, y = symbols("x y")


# ────────────────────── 例 1（教材 p120） ──────────────────────
# 焦点 F₁(-5,0), F₂(5,0), ||MF₁|-|MF₂||=6
#   2a=6 → a=3, 2c=10 → c=5, b²=c²-a²=16, b=4
# 标准方程: x²/9 - y²/16 = 1

EXAMPLE_1_CANONICAL = {
    # 关键词 goal（None 占位；诊断器走 looks_like_* 函数）
    "form_kw":   None,                          # "焦点在 x 轴 + x²/a²-y²/b²=1 形式"
    "ab_kw":     None,                          # "a=3 + (b=4 或 b²=16)"
    # sympy 严谨判等 goal（学生可单独答任一个）
    "a":         Integer(3),
    "b":         Integer(4),
    "b_squared": Integer(16),
    "c":         Integer(5),
    "c_squared": Integer(25),
    "two_a":     Integer(6),                    # 2a=6（学生可能写"2a=6"）
    "two_c":     Integer(10),                   # 2c=10
    # 最终方程（学生可以跳过中间步直接写）
    "equation":  Eq(x**2 / 9 - y**2 / 16, 1),
}

EXAMPLE_1_PHASES = ["ask_form", "ask_ab", "ask_equation"]   # 教学节奏（提问顺序），不约束诊断
EXAMPLE_1_PHASE_GOAL = {
    "ask_form":     None,
    "ask_ab":       None,
    "ask_equation": "equation",
}

# v3.45: GOAL_IMPLIES（仿 311）—— 跳级答某 goal 时自动标记前置完成
GOAL_IMPLIES_1 = {
    "form_kw":   {"form_done"},
    "ab_kw":     {"ab_done", "a_done", "b_done"},
    "a":         {"a_done"},
    "b":         {"b_done"},
    "b_squared": {"b_done"},
    "c":         {"c_done"},
    "c_squared": {"c_done"},
    "two_a":     {"a_done"},                    # 2a 暗含 a
    "two_c":     {"c_done"},                    # 2c 暗含 c
    # **跳级关键**：直答 equation → 所有前置自动 done + all_done
    "equation":  {"form_done", "ab_done", "a_done", "b_done", "c_done", "equation_done", "all_done"},
}

def _example_1_done(sub_flags: set) -> bool:
    """例 1 完成判定（仿 311 多条件）：
      · all_done（学生直接答最终方程）→ 完成
      · 或 form_done + a_done + b_done（按顺序完整答完）→ 完成
    """
    if "all_done" in sub_flags:
        return True
    if {"form_done", "a_done", "b_done"}.issubset(sub_flags):
        return True
    return False


# ────────────────────── 例 2（教材 p120） ──────────────────────
# A、B 两地相距 800m, A 听到比 B 晚 2s, 声速 340m/s
#   建系 A、B 在 x 轴, 原点为 AB 中点
#   |PA|-|PB| = 340×2 = 680  →  2a=680, a=340
#   |AB|=800  →  2c=800, c=400
#   b² = c² - a² = 400² - 340² = 44400
#   |PA|-|PB|=680>0 → 右支 x ≥ 340
# 轨迹方程: x²/115600 - y²/44400 = 1  (x ≥ 340)

EXAMPLE_2_CANONICAL = {
    "setup_kw":   None,                                # 关键词：2a=680 / 距离差=680
    "ab_kw":      None,                                # 关键词：a=340 + b²=44400
    "branch_kw":  None,                                # 关键词：右支 / x≥340
    # sympy 严谨 goal
    "a":          Integer(340),
    "c":          Integer(400),
    "b_squared":  Integer(44400),
    "two_a":      Integer(680),
    "two_c":      Integer(800),
    "a_squared":  Integer(115600),
    # 方程（不含分支约束）—— 学生只写方程没说右支，算 equation_done 但 branch 仍未答
    "equation":   Eq(x**2 / 115600 - y**2 / 44400, 1),
    # 方程 + 分支约束（综合）—— 学生写出完整答案
    "equation_with_branch_kw":   None,                 # 关键词：方程+分支组合（与诊断器 _KW_HANDLERS key 一致）
}

EXAMPLE_2_PHASES = ["ask_setup", "ask_ab", "ask_equation_with_branch"]
EXAMPLE_2_PHASE_GOAL = {
    "ask_setup":                  None,
    "ask_ab":                     None,
    "ask_equation_with_branch":   None,
}

GOAL_IMPLIES_2 = {
    "setup_kw":  {"setup_done", "two_a_done"},
    "ab_kw":     {"ab_done", "a_done", "b_done"},
    "branch_kw": {"branch_done"},
    "a":         {"a_done", "setup_done"},            # a=340 暗含已经从 2a=680 推出来
    "c":         {"c_done"},
    "b_squared": {"b_done"},
    "two_a":     {"setup_done", "a_done", "two_a_done"},
    "two_c":     {"c_done"},
    "a_squared": {"a_done"},
    # 单独写方程 → 暗含 a/b/c 都对，但不暗含 branch（学生可能漏掉右支）
    "equation":  {"setup_done", "ab_done", "a_done", "b_done", "c_done", "equation_done"},
    # 完整答（方程 + 分支）→ all_done
    "equation_with_branch_kw": {"setup_done", "ab_done", "a_done", "b_done", "c_done",
                                "equation_done", "branch_done", "all_done"},
}

def _example_2_done(sub_flags: set) -> bool:
    """例 2 完成判定：
      · all_done（学生答出完整方程+分支）→ 完成
      · 或 equation_done + branch_done（分别答完方程和分支）→ 完成
    """
    if "all_done" in sub_flags:
        return True
    if "equation_done" in sub_flags and "branch_done" in sub_flags:
        return True
    return False


# ────────────────────── 探究（教材 p121） ──────────────────────
# A(-5,0), B(5,0), k_AM·k_BM = 4/9
#   k_AM = y/(x+5),  k_BM = y/(x-5)
#   y/(x+5) · y/(x-5) = 4/9  →  9y² = 4(x²-25)
#   化简: x²/25 - y²/(100/9) = 1  (x ≠ ±5)
# ※ 结构仿 3.1.1 例 3（椭圆斜率积 -4/9），仅数值与符号替换

EXPLORATION_CANONICAL = {
    # v3.45.2: 拆 slopes 为两个独立 goal（学生分两次答 k_AM、k_BM 也能累积）
    "slope_am_kw":   None,                                                       # k_AM = y/(x+5)
    "slope_bm_kw":   None,                                                       # k_BM = y/(x-5)
    "slopes_kw":     None,                                                       # 同时含 k_AM + k_BM 一次答完
    "slope_product": Eq(y / (x + 5) * y / (x - 5), Rational(4, 9)),              # k_AM·k_BM = 4/9
    # 方程多种等价形式（sympy 通过 ratio 判等可兼容 4x²+9y²-9y²=100 等）
    "equation":      Eq(x**2 / 25 - y**2 * Rational(9, 100), 1),                 # 等价于 x²/25 - y²/(100/9) = 1
    "constraint_kw": None,                                                       # x≠±5
}

EXPLORATION_PHASES = ["ask_slopes", "ask_simplify", "ask_constraint"]
EXPLORATION_PHASE_GOAL = {
    "ask_slopes":     None,
    "ask_simplify":   "equation",
    "ask_constraint": None,
}

GOAL_IMPLIES_EXPLORATION = {
    "slope_am_kw":   {"slope_am_done"},
    "slope_bm_kw":   {"slope_bm_done"},
    "slopes_kw":     {"slopes_done", "slope_am_done", "slope_bm_done"},
    "slope_product": {"slopes_done", "slope_am_done", "slope_bm_done", "slope_product_done"},
    "equation":      {"slopes_done", "slope_am_done", "slope_bm_done",
                      "slope_product_done", "simplify_done", "equation_done"},
    "constraint_kw": {"constraint_done"},
}

def _exploration_done(sub_flags: set) -> bool:
    """探究完成判定：
      · 必须 equation_done + constraint_done（教材要求注明 x≠±5）
    """
    return "equation_done" in sub_flags and "constraint_done" in sub_flags


# ────────────────────── 配置总表 ──────────────────────
# key:
#   1 / 2 → 教材正式例题（UI 文案"例 1""例 2"）
#   "exploration" → 教材 p121 探究

EXAMPLE_CONFIGS_321 = {
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
    "exploration": {
        "canonical":  EXPLORATION_CANONICAL,
        "phases":     EXPLORATION_PHASES,
        "phase_goal": EXPLORATION_PHASE_GOAL,
        "implies":    GOAL_IMPLIES_EXPLORATION,
        "done_fn":    _exploration_done,
    },
}
