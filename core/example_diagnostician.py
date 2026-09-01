# -*- coding: utf-8 -*-
"""通用 SymPy 数学等价判定工具。

从 3.1.1 例题诊断器中提取的核心函数 _equivalent，
供 3.1.2 等其它课程的诊断器复用。
"""
from __future__ import annotations

from sympy import simplify, Eq


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
