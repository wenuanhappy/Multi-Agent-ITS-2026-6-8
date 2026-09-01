# -*- coding: utf-8 -*-
"""CorrectionCrew: 纠错Crew

当 FSM 检测到学生数学错误时触发。
助教 Agent 基于 FSM 传入的诊断结果 + 阶段知识上下文，生成三段式纠错反馈。

数据流：
  FSM 调用 SymPyDiagnosisTool → 获取 error_detail
  FSM 查 STAGE_FEYNMAN_CONTEXT → 获取 stage_context（当前阶段的知识摘要）
  FSM 传给 CorrectionCrew → TA Agent 生成自然语言纠错
"""
from crewai import Crew, Task, Process
from agents.ta import create_ta_agent
from tools.sympy_diagnosis import SymPyDiagnosisTool
from tools.kg_retrieval import KGRetrievalTool
from config.settings import CREWAI_LLM_FALLBACK


class CorrectionCrew:
    """纠错Crew：TA Agent 持有 SymPy + KG Tool。"""

    def __init__(self):
        self.sympy_tool = SymPyDiagnosisTool()
        self.kg_retrieval = KGRetrievalTool()
        self.ta = create_ta_agent(tools=[self.sympy_tool, self.kg_retrieval])

    def generate_correction(self, student_text: str, error_detail: str,
                            stage: str, expected_answer: str,
                            stage_context: str = "") -> str:
        """助教生成结构化纠错反馈。

        Args:
            student_text: 学生的原始输入
            error_detail: 错误类型描述（如"变量可能错位"）
            stage: 当前阶段名
            expected_answer: 期望答案方向（不直接给学生看，供助教参考）
            stage_context: 当前阶段正在教的知识内容（防止助教举无关例子）
        Returns:
            三段式纠错反馈文本
        """
        task = Task(
            description=f"""你是高中数学助教。学生在学习椭圆几何性质（3.1.2节）时犯了错。

【当前正在教的内容】
{stage_context if stage_context else f"椭圆几何性质，阶段：{stage}"}

【学生写了什么】
"{student_text}"

【FSM 诊断结果】
错误类型：{error_detail}
期望方向：{expected_answer}

请严格使用三段式结构回复：
1. **身份声明**（一句话，如"我是助教，让我帮你看看这一步。"）
2. **错点定位**（用 $LaTeX$ 引用学生原文，指出具体哪里错了，对比正确方向。**必须围绕椭圆方程 $x^2/a^2+y^2/b^2=1$ 来解释**，不要举其他函数的例子）
3. **可操作建议**（提示学生检查某个具体步骤，不直接给答案。引导回到椭圆方程推导）

要求：
- 所有举例和解释都必须与椭圆有关，不要提三角函数、圆、双曲线等无关内容
- 数学公式用 $LaTeX$ 格式
- 简洁专业，3段总共不超过5句话""",
            expected_output="三段式纠错反馈（身份声明→椭圆相关的错点定位→可操作建议）",
            agent=self.ta,
        )
        crew = Crew(
            agents=[self.ta],
            tasks=[task],
            process=Process.sequential,
            verbose=False,
            function_calling_llm=CREWAI_LLM_FALLBACK,  # DeepSeek 做 tool 路由
        )
        result = crew.kickoff()
        return result.raw if hasattr(result, 'raw') else str(result)
