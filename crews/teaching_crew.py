# -*- coding: utf-8 -*-
"""TeachingCrew: 主教学Crew

当FSM需要LLM生成苏格拉底式回复时触发。
Sequential流程：教师Agent生成回复 → 反剧透Tool后过滤。
"""
from crewai import Crew, Task, Process
from agents.teacher import create_teacher_agent
from tools.anti_spoiler_scan import AntiSpoilerTool
from tools.kg_retrieval import KGRetrievalTool
from config.settings import CREWAI_LLM_FALLBACK


class TeachingCrew:
    """主教学Crew：Teacher Agent 持有 AntiSpoiler + KG Tool，DeepSeek 做 tool 路由。"""

    def __init__(self):
        self.anti_spoiler = AntiSpoilerTool()
        self.kg_retrieval = KGRetrievalTool()
        self.teacher = create_teacher_agent(tools=[self.anti_spoiler, self.kg_retrieval])

    def kickoff(self, student_text: str, stage: str, system_context: str,
                stage_goal: str, history_summary: str) -> str:
        """生成一条苏格拉底式教师回复。

        Args:
            student_text: 学生输入
            stage: 当前阶段名
            system_context: 系统提示（含阶段约束、KG上下文等）
            stage_goal: 当前阶段教学目标
            history_summary: 最近对话摘要
        Returns:
            教师回复文本
        """
        task = Task(
            description=f"""你是苏格拉底式数学教师，正在教授椭圆几何性质（3.1.2节）。

当前阶段：{stage}
阶段目标：{stage_goal}

教学上下文：
{system_context}

最近对话：
{history_summary}

学生刚才说："{student_text}"

请用苏格拉底式提问回应这位学生。要求：
1. 不要直接告诉答案
2. 用引导性问题帮助学生思考
3. 如果学生方向正确，给予肯定并深入追问
4. 如果学生有误，温和地用反问引导纠正
5. 回复控制在2-3句话
6. 数学公式用 $LaTeX$ 格式""",
            expected_output="一条简洁的苏格拉底式引导回复（2-3句话，含LaTeX数学公式）",
            agent=self.teacher,
        )

        crew = Crew(
            agents=[self.teacher],
            tasks=[task],
            process=Process.sequential,
            verbose=False,
            function_calling_llm=CREWAI_LLM_FALLBACK,  # DeepSeek 做 tool 路由
        )
        result = crew.kickoff()
        return result.raw if hasattr(result, 'raw') else str(result)
