# -*- coding: utf-8 -*-
"""CrewAI Tool：反剧透扫描——包装 core.anti_spoiler 的阶段黑名单 + 扫描接口。

用途：Agent 生成回复后，调用本工具检查是否包含当前阶段禁止透露的关键词。
返回：SPOILER_HIT:<命中的黑名单条目>  或  CLEAN。
"""
from __future__ import annotations

from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class AntiSpoilerInput(BaseModel):
    """反剧透扫描工具的输入参数。"""

    text: str = Field(
        ..., description="要检查的LLM回复文本"
    )
    course_type: str = Field(
        default="ellipse_312",
        description="课程类型（如 ellipse_312）",
    )
    stage: str = Field(
        ..., description="当前阶段名称（如 e312_range, e312_symmetry 等）"
    )


class AntiSpoilerTool(BaseTool):
    """扫描 LLM 生成的文本中是否包含当前阶段禁止透露的关键词（反剧透）。

    自动合并阶段黑名单与跨阶段通用假推进话术黑名单。
    归一化处理 LaTeX / 全半角 / 空格变体，防止绕过。
    """

    name: str = "anti_spoiler_scan"
    description: str = (
        "扫描LLM生成的文本中是否包含当前阶段禁止透露的关键词（反剧透）。"
        "返回 SPOILER_HIT:<term> 或 CLEAN。"
    )
    args_schema: Type[BaseModel] = AntiSpoilerInput

    def _run(self, text: str, course_type: str = "ellipse_312", stage: str = "") -> str:
        from core.anti_spoiler import get_stage_blacklist, scan_spoiler

        blacklist = get_stage_blacklist(course_type, stage)
        hit = scan_spoiler(text, blacklist)
        if hit:
            return f"SPOILER_HIT:{hit}"
        return "CLEAN"
