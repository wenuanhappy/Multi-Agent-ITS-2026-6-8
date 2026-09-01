# -*- coding: utf-8 -*-
"""CrewAI Agent 定义 —— 苏格拉底式数学教师。

主线教学 agent：通过精心设计的问题链引导学生自主发现椭圆的几何性质。
FSM 编排器控制调度，agent 本身不做 delegation 也不自主循环。
"""
from crewai import Agent
from config.settings import CREWAI_LLM


def create_teacher_agent(tools=None):
    """创建教师 agent 实例。

    Parameters
    ----------
    tools : list, optional
        注入的 CrewAI Tool 列表（如 anti_spoiler、knowledge_graph 等）。

    Returns
    -------
    Agent
        配置好的苏格拉底教师 agent。
    """
    return Agent(
        role="苏格拉底式数学教师",
        goal="通过提问引导学生自主发现椭圆的几何性质，绝不直接告诉答案",
        backstory=(
            "你是一位经验丰富的高中数学教师，专精圆锥曲线教学。\n"
            "你的教学理念是苏格拉底式提问——通过精心设计的问题链，"
            "让学生自己推导出结论。\n"
            "你深知每个知识点的常见误区，能在学生犯错时给出恰到好处的引导提示。\n"
            "你说话温和鼓励，但绝不会因为学生催促就直接给出答案。"
        ),
        tools=tools or [],
        llm=CREWAI_LLM,
        allow_delegation=False,
        verbose=False,
        max_iter=1,  # 单轮响应，不自主循环——由 FSM 编排器控制对话推进
    )
