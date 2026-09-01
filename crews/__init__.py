# -*- coding: utf-8 -*-
"""Multi-Agent ITS —— CrewAI Crew 编排层。

三个 Crew 对应论文中多 agent 协作架构的三条执行路径：
  · TeachingCrew    主教学路径（苏格拉底式引导）
  · FeynmanCrew     费曼侧路（以教代学检验理解）
  · CorrectionCrew  纠错路径（SymPy 检测后结构化反馈）

FSM Flow 在不同决策点 kickoff 对应的 Crew。
"""

from crews.teaching_crew import TeachingCrew
from crews.feynman_crew import FeynmanCrew
from crews.correction_crew import CorrectionCrew

__all__ = [
    "TeachingCrew",
    "FeynmanCrew",
    "CorrectionCrew",
]
