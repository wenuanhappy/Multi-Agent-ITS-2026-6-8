# -*- coding: utf-8 -*-
"""CrewAI Agent 定义 —— 诊断分类器。

内部 agent（不面向学生）：将学生回答归类到当前阶段预定义的候选类别中。
使用 temperature=0、极短 max_tokens 以保证输出确定性——只返回一个分类 key。
"""
from crewai import Agent
from config.settings import CREWAI_LLM


def create_diagnostician_agent(tools=None):
    """创建诊断分类器 agent 实例。

    Parameters
    ----------
    tools : list, optional
        注入的 CrewAI Tool 列表（如 classifier tool 等）。

    Returns
    -------
    Agent
        配置好的诊断分类器 agent。
    """
    return Agent(
        role="教学诊断分类器",
        goal="将学生的回答精确归类到当前教学阶段预定义的候选类别中，只输出分类key",
        backstory=(
            "你是教学诊断系统的核心组件，负责语义分类。\n"
            "你的唯一任务是：根据当前阶段的教师问题和候选选项，"
            "判断学生的回答属于哪个预定义类别。\n"
            "你只输出一个候选 key（如 'y_axis'、'origin'），不输出任何解释或多余文字。\n"
            "如果学生的回答不符合任何候选含义（答非所问、不知道、明显偏题），你输出 'none'。\n"
            "你是后台组件，学生看不到你的输出——你的分类结果会被 FSM 用来决定下一步路由。"
        ),
        tools=tools or [],
        llm=CREWAI_LLM,
        allow_delegation=False,
        verbose=False,
        max_iter=1,  # 单次分类，不循环
    )
