# -*- coding: utf-8 -*-
"""CrewAI Tool：知识图谱检索 —— 从圆锥曲线知识图谱中检索阶段相关知识。

基于阶段的上下文知识描述，为 Agent 提供精确的教学内容约束。
"""
from __future__ import annotations

from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# ────────────────────── 阶段→知识节点的静态映射 ──────────────────────

_STAGE_KNOWLEDGE: dict[str, str] = {
    "e312_intro": "椭圆定义：平面上到两定点距离之和等于常数(大于两定点间距离)的点的轨迹。标准方程 x²/a² + y²/b² = 1 (a>b>0)。",
    "e312_range": "椭圆的范围：由标准方程可得 -a≤x≤a, -b≤y≤b，即椭圆被限制在以原点为中心、边长为2a和2b的矩形内。",
    "e312_symmetry": "椭圆的对称性：椭圆关于x轴、y轴和原点都对称。x轴和y轴是椭圆的对称轴，原点是椭圆的对称中心（中心）。",
    "e312_vertices": "椭圆的顶点：椭圆与对称轴的四个交点 A₁(-a,0), A₂(a,0), B₁(0,-b), B₂(0,b)。A₁A₂为长轴(长2a)，B₁B₂为短轴(长2b)。",
    "e312_eccentricity": "椭圆的离心率：e = c/a (0<e<1)。e越接近1椭圆越扁，e越接近0椭圆越接近圆。a=b时e=0退化为圆。",
    "e312_example_1": "例题4（椭圆标准方程求解）：已知椭圆条件求标准方程，涉及 a²=b²+c² 关系。",
    "e312_example_2": "例题5（椭圆轨迹判定）：根据距离比值条件判断轨迹类型，涉及椭圆定义的等价形式。",
    "e312_example_3": "例题6（椭圆与直线位置关系）：联立方程判断交点个数，涉及判别式分析。",
    "e312_summary": "本节总结：椭圆几何性质包括范围、对称性、顶点、离心率四个方面，是解析几何的基础。",
}


class KGRetrievalInput(BaseModel):
    """知识图谱检索工具的输入参数。"""

    query: str = Field(
        ..., description="检索查询（自然语言描述需要的知识）"
    )
    stage: str = Field(
        ..., description="当前教学阶段名称（如 e312_range, e312_eccentricity 等）"
    )


class KGRetrievalTool(BaseTool):
    """从圆锥曲线知识图谱中检索与当前教学阶段相关的知识节点。

    基于阶段静态映射返回教学上下文，确保 Agent 回复限定在当前知识范围内。
    """

    name: str = "knowledge_graph_retrieval"
    description: str = (
        "从圆锥曲线知识图谱中检索与当前教学阶段相关的知识节点。"
        "输入查询文本和阶段名称，返回该阶段的核心知识描述。"
    )
    args_schema: Type[BaseModel] = KGRetrievalInput

    def _run(self, query: str, stage: str) -> str:
        # 基于 stage 返回该阶段的知识上下文
        context = _STAGE_KNOWLEDGE.get(stage)
        if context:
            return f"[KG:{stage}] {context}"
        return f"[KG:{stage}] 未找到该阶段的知识节点。查询：{query}"
