# -*- coding: utf-8 -*-
"""LLM 语义分类器（方案 D 的 Layer 2 兜底）。

设计原则（见 docs/scheme_D_design.md）：
  · LLM 只输出枚举 key（不生成 ack 文字）—— 由后端 deterministic 模板拼 ack
  · system prompt 强约束：必须从 options 的 key 中选 1 个返回，外加 "none"
  · 用 MultiProvider（Claude → DeepSeek-flash → DeepSeek-pro）做 provider chain
  · API 挂 / parse 失败 / LLM 返回 none → 返回 None（调用方降级到 deterministic fallback）

入口：classify(student_text, phase_id, question, options) -> Optional[str]
"""
from __future__ import annotations

import re
from typing import Dict, Optional


_CLASSIFY_SYSTEM_PROMPT_TEMPLATE = """你是教学诊断器。你的唯一任务是：把学生的回答归类到下面给定的候选 key 中。

【教师当前问题】
{question}

【候选 key（必须选其中一个，或选 none）】
{options_text}

【输出要求 —— 严格遵守】
1. 只输出一个 key（字符串），不输出任何解释、标点、空格、引号、markdown。
2. 必须从候选 key 中选一个；若学生的回答不符合任何候选含义（答非所问/不知道/明显错误），输出 `none`。
3. 不要输出多个 key。不要输出 "答案是 xxx" / "我认为 xxx" 之类。
4. 不要输出 ack 文字。后端会按你的分类结果用模板拼回复。

【示例】
学生："y 轴" → 输出：y_axis
学生："关于原点对称" → 输出：origin
学生："我不知道" → 输出：none
学生："a/c 这个比值" → 输出：c_over_a（如果候选里有）

【再次强调】只输出一个 key，单 token。"""


class LLMClassifier:
    """方案 D 的 LLM 语义分类器。"""

    def __init__(self, llm_provider):
        """llm_provider: 一个有 .complete(system, user, max_tokens, temperature) 接口的 MultiProvider。
        允许传 None —— 此时 classify 直接返回 None（系统降级为纯关键词）。
        """
        self.llm = llm_provider

    def classify(
        self,
        student_text: str,
        phase_id: str,
        question: str,
        options: Dict[str, str],
    ) -> Optional[str]:
        """LLM 分类。返回命中的 enum key（不含 "none"）或 None。

        Args:
            student_text: 学生原始输入
            phase_id: 用于日志和错误诊断
            question: 教师当前提出的问题（给 LLM 看上下文）
            options: {enum_key: 人话描述} —— 候选答案。系统会自动加 "none" 选项。
        """
        if self.llm is None:
            print(f"[LLMClassifier] ⚠️ phase={phase_id}: 无 LLM provider，降级返回 None")
            return None

        # 拼 options 描述
        opts_with_none = dict(options)
        if "none" not in opts_with_none:
            opts_with_none["none"] = "学生没回答这个问题、答非所问、表示不知道、或回答明显错误"
        options_text = "\n".join(f"  · `{k}`: {v}" for k, v in opts_with_none.items())

        system_prompt = _CLASSIFY_SYSTEM_PROMPT_TEMPLATE.format(
            question=question, options_text=options_text
        )
        user_msg = f"学生回答：{student_text}\n\n输出 key："

        try:
            raw = self.llm.complete(system_prompt, user_msg, max_tokens=20, temperature=0.0)
        except Exception as e:
            print(f"[LLMClassifier] ❌ phase={phase_id}: provider 全挂 ({type(e).__name__}: {e})")
            return None

        if not raw:
            print(f"[LLMClassifier] ⚠️ phase={phase_id}: LLM 返回空")
            return None

        # 解析：取第一个非空 token，匹配候选 key
        parsed = self._parse_key(raw, set(opts_with_none.keys()))
        if parsed is None:
            print(f"[LLMClassifier] ⚠️ phase={phase_id}: 无法解析 raw={raw!r}")
            return None

        if parsed == "none":
            print(f"[LLMClassifier] phase={phase_id}: LLM 判 none → 学生未命中")
            return None

        print(f"[LLMClassifier] ✅ phase={phase_id}: LLM 命中 {parsed}（学生原文：{student_text!r}）")
        return parsed

    @staticmethod
    def _parse_key(raw: str, valid_keys: set) -> Optional[str]:
        """从 LLM 输出里提取 key。容错策略：
        1. 直接 strip 后是 valid key → 返回
        2. 去除引号/反引号/标点 → 再试
        3. 在文本里搜 valid keys 中的第一个 → 返回
        """
        if not raw:
            return None
        s = raw.strip().strip("`'\"").strip()
        if s in valid_keys:
            return s
        # 去掉 markdown / 标点
        s_clean = re.sub(r"[`'\"\[\]\{\}\.,;:]", "", s).strip()
        if s_clean in valid_keys:
            return s_clean
        # 在文本里搜（按 key 长度降序，避免短 key 误匹配长 key 的前缀）
        for key in sorted(valid_keys, key=len, reverse=True):
            if re.search(rf"\b{re.escape(key)}\b", s):
                return key
            if key in s:
                return key
        return None
