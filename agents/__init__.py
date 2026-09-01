# -*- coding: utf-8 -*-
"""Multi-Agent ITS —— CrewAI Agent 工厂函数。

四个 agent 对应论文中多 agent 架构的四个角色：
  · Teacher       苏格拉底教师（主线教学）
  · Peer          好奇同学（费曼检验）
  · TA            数学助教（符号纠错）
  · Diagnostician 诊断分类器（语义归类）
"""

from agents.teacher import create_teacher_agent
from agents.peer import create_peer_agent
from agents.ta import create_ta_agent
from agents.diagnostician import create_diagnostician_agent

__all__ = [
    "create_teacher_agent",
    "create_peer_agent",
    "create_ta_agent",
    "create_diagnostician_agent",
]
