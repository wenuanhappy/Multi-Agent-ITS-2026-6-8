# -*- coding: utf-8 -*-
"""CrewAI Tool：LLM 语义分类器——包装 core.llm_classifier 的方案 D Layer 2 兜底。

用途：当关键词匹配失败时，Agent 调用本工具让 LLM 对学生回答进行语义分类。
LLM 只输出枚举 key（不生成 ack 文字），由后端 deterministic 模板拼回复。
返回：命中的 enum key 字符串，或 NONE（无匹配）。
"""
from __future__ import annotations

import json
from typing import Dict, Type, Union

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class ClassifierInput(BaseModel):
    """LLM 分类器工具的输入参数。"""

    student_text: str = Field(
        ..., description="学生的原始输入文本"
    )
    phase_id: str = Field(
        ..., description="当前阶段标识（用于日志和错误诊断）"
    )
    question: str = Field(
        ..., description="教师当前提出的问题（给 LLM 看上下文）"
    )
    options: str = Field(
        ...,
        description=(
            '候选答案的 JSON 字符串，格式为 {"key": "描述"}'
            "，如 {\"y_axis\": \"关于y轴对称\", \"x_axis\": \"关于x轴对称\"}"
        ),
    )


class LLMClassifierTool(BaseTool):
    """当关键词匹配失败时，使用 LLM 对学生回答进行语义分类。

    走 MultiProvider（Claude -> DeepSeek-flash -> DeepSeek-pro）provider chain。
    LLM 只输出枚举 key，不生成 ack 文字。
    """

    name: str = "llm_classifier"
    description: str = (
        "当关键词匹配失败时，使用LLM对学生回答进行语义分类。"
        "输入学生文本、阶段ID、教师问题和候选选项(JSON)，返回命中的 key 或 NONE。"
    )
    args_schema: Type[BaseModel] = ClassifierInput

    def _run(
        self,
        student_text: str,
        phase_id: str,
        question: str,
        options: str,
    ) -> str:
        from core.llm_classifier import LLMClassifier
        from core.llm_providers import build_default_multi_provider

        # options 可能是 JSON 字符串或已解析的 dict
        opts: Dict[str, str]
        if isinstance(options, str):
            try:
                opts = json.loads(options)
            except (json.JSONDecodeError, TypeError):
                return f"ERROR:invalid_options_json:{options[:100]}"
        else:
            opts = options

        provider = build_default_multi_provider(verbose=False)
        classifier = LLMClassifier(provider)
        result = classifier.classify(student_text, phase_id, question, opts)
        return result if result is not None else "NONE"
