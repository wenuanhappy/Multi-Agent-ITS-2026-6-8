# -*- coding: utf-8 -*-
"""CrewAI Tool：SymPy 符号诊断——包装 example_diagnostician_312 的诊断入口。

用途：Agent 调用本工具验证学生数学答案是否匹配 canonical（支持 Eq/Expr/点集/值集/区间/关键词）。
返回格式化字符串：HIT:<goal>|FLAGS:<flags>|VIA:<method>  或  NO_MATCH。
"""
from __future__ import annotations

from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class SymPyDiagnosisInput(BaseModel):
    """SymPy 诊断工具的输入参数。"""

    student_text: str = Field(
        ..., description="学生输入的数学表达式或答案"
    )
    example_num: int = Field(
        ..., description="例题编号 (4, 5, 6)"
    )
    phase: str = Field(
        ..., description="当前阶段名称（如 ask_eq, ask_relation, ask_conclude 等）"
    )


class SymPyDiagnosisTool(BaseTool):
    """使用 SymPy 符号计算验证学生的数学答案是否正确。

    输入学生文本、例题编号和阶段，返回诊断结果。
    支持的判等类型：scalar (Eq/Expr)、point_set、value_set、interval、keyword。
    """

    name: str = "sympy_diagnosis"
    description: str = (
        "使用SymPy符号计算验证学生的数学答案是否正确。"
        "输入学生文本、例题编号和阶段，返回诊断结果。"
        "返回 HIT:<goal>|FLAGS:<flags>|VIA:<method> 或 NO_MATCH。"
    )
    args_schema: Type[BaseModel] = SymPyDiagnosisInput

    def _run(self, student_text: str, example_num: int, phase: str) -> str:
        from courses.example_diagnostician_312 import diagnose_example_312

        result = diagnose_example_312(student_text, example_num, phase)
        if result is None:
            return "NO_MATCH"
        flags = ",".join(sorted(result.implied_flags)) if result.implied_flags else ""
        return f"HIT:{result.hit_goal}|FLAGS:{flags}|VIA:{result.via}"
