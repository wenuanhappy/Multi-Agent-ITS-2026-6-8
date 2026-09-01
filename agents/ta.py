# -*- coding: utf-8 -*-
"""CrewAI Agent 定义 —— 数学助教（符号纠错）。

纠错 agent：仅在 SymPy 检测到数学错误时出场，提供精确的符号级纠错反馈。
反馈结构固定为三段式：身份声明 → 错误定位 → 下一步提示。
"""
from crewai import Agent
from config.settings import CREWAI_LLM


def create_ta_agent(tools=None):
    """创建助教 agent 实例。

    Parameters
    ----------
    tools : list, optional
        注入的 CrewAI Tool 列表（如 sympy_verify 等）。

    Returns
    -------
    Agent
        配置好的数学助教 agent。
    """
    return Agent(
        role="数学助教",
        goal="当SymPy检测到数学错误时，提供精确的符号级纠错反馈",
        backstory=(
            "你是一位数学助教，专门负责符号计算的校验工作。\n"
            "你平时不发言——只在 SymPy 检测到学生的数学表达有错误时才出场。\n"
            "你的反馈严格遵循三段结构：\n"
            "（1）身份声明：'我是助教，帮你检查一下计算。'\n"
            "（2）错误定位：指出具体哪一步出错，引用学生原文并给出符号级对比。\n"
            "（3）下一步提示：给一个可操作的修正方向，但绝不直接给出最终答案。\n"
            "你的语气客观专业，不做多余寒暄，也不重复老师已经给过的引导。"
        ),
        tools=tools or [],
        llm=CREWAI_LLM,
        allow_delegation=False,
        verbose=False,
        max_iter=1,  # 单轮响应，不自主循环——由 FSM 编排器控制对话推进
    )
