# -*- coding: utf-8 -*-
"""FeynmanCrew: 费曼侧路Crew

阶段切换时触发，测试学生理解深度。

流程：
  1. Peer 提出第一个问题（约束当前阶段知识点）
  2. 学生回答 → Peer 判定是否理解到位
     · 理解到位 → Peer 说"懂了" → Teacher 总结 → 退出
     · 没到位 → Peer 追问（内容由 Peer 自主决定）→ 回到步骤2
  3. 最多3轮，超出后 Teacher 总结退出

角色分工：
  · Peer：提问 + 判定 + 追问（全程主导）
  · Teacher：仅在退出时做自然语言总结
"""
from __future__ import annotations

import json
import re

from crewai import Crew, Task, Process
from agents.peer import create_peer_agent
from agents.teacher import create_teacher_agent
from config.settings import CREWAI_LLM_FALLBACK


class FeynmanCrew:
    """费曼侧路Crew：Peer主导提问/判定，Teacher仅做退出总结。"""

    def __init__(self):
        from tools.anti_spoiler_scan import AntiSpoilerTool
        from tools.kg_retrieval import KGRetrievalTool
        self.anti_spoiler = AntiSpoilerTool()
        self.kg_retrieval = KGRetrievalTool()
        self.peer = create_peer_agent(tools=[self.anti_spoiler, self.kg_retrieval])
        self.teacher = create_teacher_agent(tools=[])

    # ─────────────────────────────────────
    # 1. Peer 首次提问（约束当前阶段）
    # ─────────────────────────────────────

    def generate_peer_question(self, stage: str, topic: str, context: str) -> str:
        """Peer 基于当前阶段知识点生成第一个问题。"""
        task = Task(
            description=f"""你是一个好奇的高中同学。老师刚讲完「{topic}」这个知识点。

【刚才学到的具体内容】
{context}

你想让旁边的同学（就是用户）用自己的话给你讲一遍，帮你确认理解。

要求：
1. **只能围绕上面「刚才学到的具体内容」提问**，不要问之前的课或其他知识点
2. 挑其中一个你"没太想通"的点来问（比如某一步推导的原因、某个结论的几何意义）
3. 用高中生同学的口吻，自然随意
4. 只问一个问题，1-2句话
5. 不要透露答案""",
            expected_output="一个针对刚学内容的具体费曼式反问（1-2句话，同学口吻）",
            agent=self.peer,
        )
        crew = Crew(agents=[self.peer], tasks=[task],
                    process=Process.sequential, verbose=False,
                    function_calling_llm=CREWAI_LLM_FALLBACK)
        result = crew.kickoff()
        return result.raw if hasattr(result, 'raw') else str(result)

    # ─────────────────────────────────────
    # 2. Peer 判定 + 追问/满意
    # ─────────────────────────────────────

    def peer_evaluate_and_respond(self, student_text: str, context: str,
                                  conversation_so_far: str) -> dict:
        """Peer 评估学生的解释，决定追问还是满意。

        Args:
            student_text: 学生本轮的回答
            context: 当前阶段的知识点摘要（STAGE_FEYNMAN_CONTEXT）
            conversation_so_far: 侧路中此前的对话记录

        Returns:
            {
                "satisfied": bool,      # true=理解到位，false=需要追问
                "response": str,        # Peer 的回复文本
                "missing": list[str],   # 缺失的要点（仅 satisfied=false 时有意义）
            }
        """
        task = Task(
            description=f"""你是一个友善好奇的高中同学，正在请旁边的同学帮你讲解一个知识点。

【这个知识点的完整内容】
{context}

【你们之前的对话】
{conversation_so_far}

【同学最新的回答】
"{student_text}"

请判断同学的解释是否让你听懂了，然后 **只输出 JSON**（不要加任何其他文字）：

听懂了：{{"satisfied": true, "response": "你的友善回复（如：哦我明白了！...谢谢你！）"}}
没听懂：{{"satisfied": false, "response": "你的温和追问（如：嗯...我还是有点不太明白，...能再说说吗？）"}}

语气要求：
- 友善、温和、不带任何攻击性或讽刺
- 即使同学说得不好，也要先肯定再温和追问（"嗯你说的有道理，不过我还想问..."）
- 如果同学说"不知道"或"不会"，直接 satisfied=true，response 说"没关系，我们一起听老师讲吧！"
- 数学公式用 $LaTeX$ 格式（如 $x^2/a^2$）
- 1-2句话，不要长篇大论""",
            expected_output='仅JSON: {"satisfied": bool, "response": "..."}',
            agent=self.peer,
        )
        crew = Crew(agents=[self.peer], tasks=[task],
                    process=Process.sequential, verbose=False,
                    function_calling_llm=CREWAI_LLM_FALLBACK)
        result = crew.kickoff()
        raw = result.raw if hasattr(result, 'raw') else str(result)
        return self._parse_peer_judgment(raw)

    # ─────────────────────────────────────
    # 3. Teacher 退出总结
    # ─────────────────────────────────────

    def teacher_summarize(self, topic: str, context: str,
                          conversation: str) -> str:
        """Teacher 根据 Peer-学生对话生成自然语言总结。

        Args:
            topic: 知识点主题
            context: 知识点完整内容
            conversation: 完整的侧路对话记录

        Returns:
            教师的总结文本（1-2句，过渡到下一阶段）
        """
        task = Task(
            description=f"""你是苏格拉底式数学教师。刚才有一位同学向你的学生提了关于「{topic}」的问题。

【知识点内容】
{context}

【同学和学生的对话】
{conversation}

请简短总结一下这段对话：
1. 肯定学生解释得好的部分
2. 如果有遗漏或不准确的地方，补充一句点拨
3. 自然过渡到"好，我们继续下一个内容"

要求：2-3句话，温和鼓励，用 $LaTeX$ 格式写数学公式。""",
            expected_output="教师的简短总结（2-3句话，含过渡语）",
            agent=self.teacher,
        )
        crew = Crew(agents=[self.teacher], tasks=[task],
                    process=Process.sequential, verbose=False,
                    function_calling_llm=CREWAI_LLM_FALLBACK)
        result = crew.kickoff()
        return result.raw if hasattr(result, 'raw') else str(result)

    # ─────────────────────────────────────
    # 内部工具
    # ─────────────────────────────────────

    @staticmethod
    def _parse_peer_judgment(raw: str) -> dict:
        """从 LLM 输出中解析 Peer 判定 JSON。只返回 response 文本，不泄漏 JSON 结构。"""
        # 尝试直接解析
        try:
            obj = json.loads(raw)
            if "satisfied" in obj and "response" in obj:
                return {"satisfied": bool(obj["satisfied"]),
                        "response": str(obj["response"])}
        except (json.JSONDecodeError, TypeError):
            pass

        # 尝试提取 JSON 子串（支持嵌套引号和中文）
        match = re.search(r'\{[^{}]*"satisfied"\s*:\s*(true|false)[^{}]*\}',
                          raw, re.DOTALL | re.IGNORECASE)
        if match:
            try:
                obj = json.loads(match.group())
                return {"satisfied": bool(obj.get("satisfied", False)),
                        "response": str(obj.get("response", ""))}
            except (json.JSONDecodeError, TypeError):
                pass

        # 兜底：从 raw 中提取纯文本（去掉 JSON 残留）
        # 去掉 JSON 关键字残留
        cleaned = re.sub(r'\{[^{}]*\}', '', raw).strip()
        cleaned = re.sub(r'"(satisfied|response|missing)"\s*:', '', cleaned).strip()
        cleaned = cleaned.strip('"').strip()

        if "true" in raw.lower() and ("懂了" in raw or "明白" in raw or "谢谢" in raw):
            return {"satisfied": True, "response": cleaned or "嗯我懂了，谢谢！"}

        # 如果解析完全失败，返回一个安全的追问
        return {"satisfied": False,
                "response": cleaned or "嗯...你能再说得具体一点吗？"}
