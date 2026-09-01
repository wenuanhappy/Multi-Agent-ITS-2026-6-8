# -*- coding: utf-8 -*-
"""3.1.1 例题诊断器：通用引擎，配置驱动。

核心逻辑：
  1. normalize 学生输入（复用 math_normalizer）
  2. 解开字母粘连简写（复用 derive_diagnostician._resolve_concat_shortcuts）
  3. 对每个 goal 用 simplify(student/canonical).is_constant() 判等价
  4. 命中即返回 hit_goals 集合（可能命中多个：写 equation 同时蕴含其它）

设计原则：
  · 引擎不绑死具体例题——只读 canonical 配置
  · 不做小错诊断（user 决定）：对的能识别+推进；错的让 LLM 接手
  · 数值精度只认符号等价（√10、a=√10 等 sympy 等价表达式都行）
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Set, List

import sympy
from sympy import simplify, Eq, Expr

from .math_normalizer import parse as parse_input
from .derive_diagnostician import _resolve_concat_shortcuts
from .example_canonicals import EXAMPLE_CONFIGS


@dataclass
class ExampleDiagnosis:
    hit_goals: List[str] = field(default_factory=list)   # 学生输入数学等价于哪些 canonical goal
    implied_flags: Set[str] = field(default_factory=set) # 这些 goal 蕴含的 sub_flag 完成
    label: str = ""                                       # "完全正确" 或 ""（未命中）
    matched_canonical: Optional[str] = None               # 主要命中的 goal 名


def _equivalent(student_expr, canonical) -> bool:
    """检查 student_expr 是否与 canonical 数学等价。
    对方程：normalize 到 lhs-rhs=0 后用 ratio 判等（非零常数倍即等价）。
    对表达式：student - canonical == 0（符号严格等价）或 ratio.is_constant 非零。
    """
    try:
        # Eq vs Eq
        if isinstance(canonical, Eq):
            if not isinstance(student_expr, Eq):
                return False
            s_norm = simplify(student_expr.lhs - student_expr.rhs)
            c_norm = simplify(canonical.lhs - canonical.rhs)
            if s_norm == 0 and c_norm == 0:
                return True
            if s_norm == 0 or c_norm == 0:
                return False
            ratio = simplify(s_norm / c_norm)
            return bool(ratio.is_constant()) and ratio != 0
        # 表达式 vs 表达式：student 必须不是 Eq，且数学等价
        if isinstance(student_expr, Eq):
            # 学生写了 `X = canonical` 形式（X 是变量名，如 `PF1 = 3√10/2`）
            # 取 rhs 跟 canonical 比对（lhs 是变量名标签，忽略）
            student_expr = student_expr.rhs
        diff = simplify(student_expr - canonical)
        return diff == 0
    except Exception:
        return False


def diagnose_example(student_text: str, example_num: int) -> Optional[ExampleDiagnosis]:
    """学生输入 → 命中哪些 example_num 的 canonical goal。

    无命中返回 None；命中返回 ExampleDiagnosis（hit_goals 可能为多个）。
    """
    if example_num not in EXAMPLE_CONFIGS:
        return None
    config = EXAMPLE_CONFIGS[example_num]
    canonical_map = config["canonical"]
    implies_map = config["implies"]
    if not canonical_map:   # 例 2/3 还没配置
        return None

    parsed = parse_input(student_text)
    if parsed is None:
        return None
    # sympy 折叠成 BooleanAtom 的恒等式（如 "1+1=2"）跳过
    if isinstance(parsed, sympy.logic.boolalg.BooleanAtom):
        return None
    # 解开字母粘连简写（c*x、a*x 等）让数学等价比对生效
    parsed_resolved = _resolve_concat_shortcuts(parsed)

    hit_goals = []
    for goal_name, canonical in canonical_map.items():
        if _equivalent(parsed_resolved, canonical):
            hit_goals.append(goal_name)

    if not hit_goals:
        return None

    # 优先级：equation > a > 2a > PF1/PF2/c/b 等（推进力强的 goal 优先）
    priority = ["equation", "a_squared", "a", "2a", "b_squared", "b",
                "c_squared", "c", "PF1", "PF2"]
    primary = next((g for g in priority if g in hit_goals), hit_goals[0])

    implied_flags = set()
    for g in hit_goals:
        implied_flags |= implies_map.get(g, set())

    return ExampleDiagnosis(
        hit_goals=hit_goals,
        implied_flags=implied_flags,
        label="完全正确",
        matched_canonical=primary,
    )
