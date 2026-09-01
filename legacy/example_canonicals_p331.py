# -*- coding: utf-8 -*-
"""3.3.1「抛物线及其标准方程」例题 canonical 答案配置。

参照 example_canonicals_321.py 的 311-style 模式（goal + GOAL_IMPLIES + done_fn）。
设计理念见 论文补充文献_两个技术创新点.md 2.5.5 节。

设计原则（与 311/321/322 对齐）：
  · 每例配关键里程碑（goal），不死磕教学 phase 顺序
  · 学生可以按"标准顺序"答（先 p → 方程 → 焦点），也可以**跳步直答**任一 goal
  · GOAL_IMPLIES：一个 goal 命中蕴含哪些 sub_flag 完成
    （如直答 equation_2 → 视同 form_2 / p_2 / equation_2 全部 done + all_done）
  · done_fn：检查 sub_flags 是否满足整道题完成（all_done 或具体 flag 组合）
  · 多维度答案 phase（例 1 子题 (1) 焦点+准线；例 2 综合方程+焦点）
    拆为独立 sub-flag，handler 跨 turn 累积（仿 322 例 1/2 conclude）

例 1：教材 p132 例 1
  (1) y²=6x → p=3，焦点 (3/2, 0)，准线 x=-3/2
  (2) 焦点 F(0, -2) → 标准方程 x²=-8y
例 2：教材 p132 例 2 卫星天线
  口径（直径）4.8 m，深度 1 m → 点 A(1, 2.4) 代入 y²=2px
  解得 2.4² = 2p × 1，即 p = 2.88
  标准方程 y² = 5.76x，焦点 (1.44, 0)

3.1.1 / 3.1.2 / 3.2.1 / 3.2.2 的 example_canonicals_*.py 一行不动。
"""
from __future__ import annotations

from sympy import Eq, Integer, Rational, symbols

x, y = symbols("x y")


# ────────────────────── 例 1（教材 p132 例 1）──────────────────────
# (1) y²=6x → 2p=6 → p=3
#     焦点在 x 轴正半轴 → F(p/2, 0) = (3/2, 0)
#     准线 x = -p/2 = -3/2
# (2) 焦点 F(0, -2) → 焦点在 y 轴负半轴 → 设 x² = -2py (p>0)
#     p/2 = 2 → p = 4 → 2p = 8 → 标准方程 x² = -8y

EXAMPLE_1_CANONICAL = {
    # ─── 子题 (1)：y²=6x 求焦点 + 准线 ───
    "p_1":          Integer(3),                              # p=3
    "focus_1":      frozenset({(Rational(3, 2), Integer(0))}),  # 焦点 (3/2, 0)
    "directrix_1":  Eq(x, -Rational(3, 2)),                  # 准线 x = -3/2
    "focus_1_kw":   None,    # 关键词路由备用（学生用 "1.5" 或 "(3/2, 0)" 等表达）
    # ─── 子题 (2)：F(0,-2) 求标准方程 ───
    "p_2":          Integer(4),                              # p=4
    "form_2_kw":    None,    # 关键词：开口向下 / y 轴负半轴 / x²=-2py
    "equation_2":   Eq(x**2, -8 * y),                        # x²=-8y
}

EXAMPLE_1_PHASES = ["ask_focus_1", "ask_directrix_1", "ask_form_2", "ask_eq_2"]

EXAMPLE_1_PHASE_GOAL = {
    "ask_focus_1":     None,        # 关键词路由（含 Rational 坐标）
    "ask_directrix_1": "directrix_1",
    "ask_form_2":      None,        # 关键词路由
    "ask_eq_2":        "equation_2",
}

# v3.x: GOAL_IMPLIES（仿 311 / 321）—— 跳级答某 goal 时自动标记前置完成
GOAL_IMPLIES_1 = {
    "p_1":         {"p_1_done"},
    "focus_1":     {"focus_1_done", "p_1_done"},      # 焦点暗含 p
    "focus_1_kw":  {"focus_1_done", "p_1_done"},      # 关键词命中等价
    "directrix_1": {"directrix_1_done", "p_1_done"},  # 准线暗含 p
    "p_2":         {"p_2_done"},
    "form_2_kw":   {"form_2_done"},
    # 直答 equation_2 → 子题 (2) 全部 done；子题 (1) 不蕴含（学生可能只答了 (2)）
    "equation_2":  {"equation_2_done", "form_2_done", "p_2_done"},
}


def _example_1_done(sub_flags: set) -> bool:
    """例 1 完成判定：
      · 必须 (1)(2) 两个子题都答完
      · 子题 (1) 要求：focus_1_done + directrix_1_done
      · 子题 (2) 要求：equation_2_done
    """
    return {"focus_1_done", "directrix_1_done", "equation_2_done"}.issubset(sub_flags)


# ────────────────────── 例 2（教材 p132 例 2 卫星天线）──────────────────────
# 口径 4.8 m, 深度 1 m → 顶点为原点, 焦点在 x 轴正半轴
# 设 y² = 2px (p > 0)
# 开口边缘点 A(1, 2.4) 代入: 2.4² = 2p × 1 → p = 2.88
# 标准方程 y² = 5.76x, 焦点 (1.44, 0)
#
# 注：教材 p = 2.88 用十进制；canonical 用精确 Rational(288, 100) 表示。
# sympy 比对时 2.88（Float）与 Rational(288,100) 通过 sympify+simplify 等价。

EXAMPLE_2_CANONICAL = {
    "setup_kw":    None,                                    # 关键词：A(1, 2.4) / 2.4²=2p×1
    "p_value":     Rational(288, 100),                      # p = 2.88
    "two_p":       Rational(576, 100),                      # 2p = 5.76
    "equation":    Eq(y**2, Rational(576, 100) * x),        # y² = 5.76 x
    "focus_kw":    None,                                    # 关键词：(1.44, 0) / (144/100, 0)
    "all_kw":      None,                                    # 综合：方程 + 焦点一次答全
}

EXAMPLE_2_PHASES = ["ask_setup", "ask_p", "ask_conclude"]

EXAMPLE_2_PHASE_GOAL = {
    "ask_setup":    None,           # 关键词路由
    "ask_p":        "p_value",      # sympy 严谨
    "ask_conclude": None,           # 拆为 equation + focus 两维度，partial 累积
}

GOAL_IMPLIES_2 = {
    "setup_kw":    {"setup_done"},
    "p_value":     {"p_done", "setup_done"},          # 答 p=2.88 暗含已建系
    "two_p":       {"p_done", "setup_done"},          # 答 2p=5.76 等价
    # 单维：方程 / 焦点 各自独立 done flag（支持 partial 累积）
    "equation":    {"equation_done", "p_done", "setup_done"},
    "focus_kw":    {"focus_done", "p_done", "setup_done"},
    # 综合关键词：一次答全方程 + 焦点
    "all_kw":      {"equation_done", "focus_done", "p_done", "setup_done", "all_done"},
}


def _example_2_done(sub_flags: set) -> bool:
    """例 2 完成判定：
      · all_done（学生一次答全方程 + 焦点）→ 完成
      · 或 equation_done + focus_done 累积齐全（可分多 turn 答）→ 完成
    """
    if "all_done" in sub_flags:
        return True
    return {"equation_done", "focus_done"}.issubset(sub_flags)


# ────────────────────── 配置总表 ──────────────────────
EXAMPLE_CONFIGS_P331 = {
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
}
