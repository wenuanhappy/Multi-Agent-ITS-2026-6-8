# -*- coding: utf-8 -*-
"""anti-spoiler 硬约束：阶段黑名单 + 输出后过滤（2026-05-27 v0 起草）。

**当前状态：黑名单内容标 DRAFT，未接入 lesson_flow.py。**

设计依据：多agent_pilot_3.1.2_执行计划.md §1.4
  · 阶段黑名单：每个 stage 维护"本阶段嘴里不能说的核心剧透词"
  · 事前预防：写进 persona system prompt（agent_persona.build_system_prompt 注入）
  · 事后兜底：scan_spoiler 扫 LLM 输出，命中则由调用方决定重生 / 退兜底

工程纪律：
  · 黑名单严格收口——只列"答案级别"的核心结论；学生即将自己说出的次要表达不进黑名单
  · stage-scoped：当前 stage 黑、下一 stage 自动解禁（无需手动维护"phase 内解禁"逻辑）
  · scan_spoiler 做归一化（去空格、LaTeX 包装、全/半角、≤/<=）——避免 LLM 用变体绕过
  · 命中后由调用方决定策略；本模块只回答"命中了什么"
"""
from __future__ import annotations
import re
from typing import Iterable, Optional


# ============================================================
# DRAFT v0（2026-05-27 起草，待用户审）：3.1.2 椭圆几何性质 9 stage 黑名单
# ------------------------------------------------------------
# 收口原则：
#   1. 只禁"学生在本 stage 还没自己得出的最终结论 / 核心公式"
#   2. 学生即将自己说出的次要词（如"对称"、"顶点"、"离心率"）不进黑名单
#   3. 例题 stage 走 _llm_example_protocol JSON 协议（返回诊断 + 推进建议，
#      不自由生成对话），LLM 不会自由剧透答案 → 例题黑名单留空
#   4. INTRO / SUMMARY 阶段无剧透目标 → 留空
#
# 结构：{course_type: {stage_id: tuple[str, ...]}}
# stage_id 与 lesson_flow.LessonStage 的 .value 一致（小写带下划线）。
# ============================================================

# ============================================================
# 2026-05-28 v3 增强：跨 stage 通用的"LLM 假推进话术"黑名单
# 用户拍板（Q2）：放 B 档及以上的 anti-spoiler，让 B/C/D 都治非例题假推进话术
# → 论文 A→B 同时改进"反剧透"和"假推进话术"两个维度
#
# 这类话术让学生**视觉上**误以为 stage 推进了（"猜得不错代数方法证明！"），
# 但实际 stage 状态机没动 —— 收 LLM 在 _llm_respond fallback 路径下的假装推进
# ============================================================
GLOBAL_FAKE_ADVANCE_BLACKLIST: tuple = (
    # 假装认可学生猜想的语气词（学生没真答对时 LLM 不该这样说）
    "猜得不错", "猜对了", "你已经接近了",
    # 假冒推进的连接词
    "差不多就是这个", "你说的有道理，下面", "答得很好，那么",
    # 自由推进话术（仅 LLM 自己生成时算假推进；状态机硬编码文案不走 anti-spoiler）
    "我们来用代数方法证明", "我们一步一步推一遍", "现在让我们看看",
    # 学生说"不知道/不会"时常见的 LLM 假推进续写
    "那我们就一起", "我们就先这样吧", "那看下一",
)


STAGE_BLACKLIST: dict[str, dict[str, tuple[str, ...]]] = {
    "ellipse_312": {
        # INTRO：仅过渡问候，无剧透目标
        "e312_intro": (),

        # RANGE（范围）：predict / derive 两 phase 都不能直接给 -a≤x≤a / -b≤y≤b
        "e312_range": (
            "-a≤x≤a", "-a<=x<=a", "-a≤ x ≤a", "−a≤x≤a",
            "-b≤y≤b", "-b<=y<=b", "-b≤ y ≤b", "−b≤y≤b",
            "|x|≤a", "|x|<=a", "|y|≤b", "|y|<=b",
            "x∈[-a,a]", "y∈[-b,b]",
        ),

        # SYMMETRY（对称性）：3 phase 都不能直接说"关于 X 轴对称"的最终结论
        "e312_symmetry": (
            "关于y轴对称", "关于 y 轴对称", "关于 y轴对称", "关于y 轴对称",
            "关于x轴对称", "关于 x 轴对称", "关于 x轴对称", "关于x 轴对称",
            "关于原点对称", "关于原点中心对称",
            "三重对称", "x轴y轴原点对称",
        ),

        # VERTICES（顶点）：compute / name 两 phase
        #   - compute phase：禁直接给 4 个顶点坐标
        #   - name phase：禁直接说"长轴长 2a / 短轴长 2b"
        "e312_vertices": (
            # 顶点坐标
            "A_1(-a,0)", "A_2(a,0)", "B_1(0,-b)", "B_2(0,b)",
            "A1(-a,0)", "A2(a,0)", "B1(0,-b)", "B2(0,b)",
            "(-a,0)和(a,0)和(0,-b)和(0,b)",
            "(±a,0)", "(0,±b)",
            # 长短轴长
            "长轴长2a", "长轴长 2a", "长轴长是2a", "长轴=2a", "长轴 = 2a", "|A_1A_2|=2a",
            "短轴长2b", "短轴长 2b", "短轴长是2b", "短轴=2b", "短轴 = 2b", "|B_1B_2|=2b",
        ),

        # ECCENTRICITY（离心率）：本节重点，6 phase
        #   - explore_c / explore_a：禁"c 越大越扁 / a 越大越圆"结论
        #   - induce_ratio：禁直接给"比值 c/a"（这是要学生答的）
        #   - define：教材在此 phase 给定义，但定义之前老师不能先说
        #   - geometry / range：禁直接说"0<e<1 / e 越大越扁 / e=0 退化为圆"
        # 注意：stage 粒度无法对 define 之后解禁 e=c/a；
        #       折中：把"e=c/a"作为公式禁全 stage，让 LLM 后半段用"上面定义的 e"代替
        "e312_eccentricity": (
            # 公式
            "e=c/a", "e = c/a", "e=c÷a",
            "e=\\dfrac{c}{a}", "e=\\frac{c}{a}",
            "e = \\dfrac{c}{a}", "e = \\frac{c}{a}",
            # 探究阶段结论
            "c越大越扁", "c 越大越扁", "c越大椭圆越扁",
            "a越大越圆", "a 越大越圆", "a越大椭圆越圆",
            # 几何意义结论（含"椭圆"插入的变体）
            "e越大越扁", "e 越大越扁", "e越大椭圆越扁", "e越接近1越扁",
            "e越小越圆", "e 越小越圆", "e越小椭圆越圆", "e越接近0越圆",
            # 范围结论
            "0<e<1", "0 < e < 1", "0＜e＜1",
            "e∈(0,1)", "e属于(0,1)",
            # 极限退化
            "e=0时退化为圆", "e=0退化为圆", "a=b时e=0",
            "e=0 时椭圆变成圆", "圆是椭圆的极限",
        ),

        # 例题 1/2/3：走 _llm_example_protocol JSON 协议，不会自由剧透
        "e312_example_1": (),
        "e312_example_2": (),
        "e312_example_3": (),

        # SUMMARY：结课总结，无剧透目标
        "e312_summary": (),
    },
}


# ============================================================
# 归一化：让黑名单不被空格 / LaTeX 包装 / 全半角 / ≤<= 互换绕过
# ============================================================

# LaTeX 分数包装 → 朴素斜杠
_LATEX_FRAC_RE = re.compile(r"\\d?frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}")

# 上下标包装 → 朴素 ^ / _
_SUP_BRACE_RE = re.compile(r"\^\s*\{([^{}]+)\}")
_SUB_BRACE_RE = re.compile(r"_\s*\{([^{}]+)\}")

# 数学 dollar 围栏
_DOLLAR_RE = re.compile(r"\$+")


def _normalize(text: str) -> str:
    """把 LLM 输出 / 黑名单条目归一成同一形态以便子串匹配。

    规则：
      1. 去 markdown / LaTeX 围栏：``` $ $$
      2. \dfrac{x}{y} / \frac{x}{y} → x/y（朴素斜杠）
      3. x^{2} → x^2；y_{1} → y_1（去花括号）
      4. ≤ → <=；≥ → >=；× → *；÷ → /
      5. 全角 ＜＞≤≥ 归一为半角
      6. 去全部空格 + 制表 + 换行
      7. 全转小写（中文不受影响；英文字母统一）
    """
    if not text:
        return ""
    s = text
    # 1. 去 markdown / dollar 围栏
    s = s.replace("```", "")
    s = _DOLLAR_RE.sub("", s)
    # 2. LaTeX 分数 → /
    s = _LATEX_FRAC_RE.sub(r"\1/\2", s)
    # 3. 上下标花括号 → 直接
    s = _SUP_BRACE_RE.sub(r"^\1", s)
    s = _SUB_BRACE_RE.sub(r"_\1", s)
    # 4. & 5. 符号归一
    trans = {
        "≤": "<=", "≧": ">=", "≥": ">=", "＞": ">", "＜": "<",
        "×": "*", "÷": "/", "＝": "=",
        "（": "(", "）": ")", "，": ",", "：": ":",
    }
    for k, v in trans.items():
        s = s.replace(k, v)
    # 6. 去全部 whitespace
    s = re.sub(r"\s+", "", s)
    # 7. 小写
    return s.lower()


# ============================================================
# 对外 API
# ============================================================

def get_stage_blacklist(course_type: str, stage: str) -> tuple[str, ...]:
    """读取本 stage 的剧透黑名单。返回空 tuple = 本 stage 无约束。

    v3（2026-05-28）：自动合并 stage 黑名单 + 跨 stage 通用的假推进话术黑名单。
    B/C/D 档调本函数时同时拦剧透 + 假推进话术（论文 A→B 同时改进两指标）。
    """
    stage_bl = STAGE_BLACKLIST.get(course_type, {}).get(stage, ())
    return tuple(stage_bl) + GLOBAL_FAKE_ADVANCE_BLACKLIST


def scan_spoiler(text: str, blacklist: Iterable[str]) -> Optional[str]:
    """扫描 LLM 输出是否命中黑名单。

    Args:
        text: LLM 已生成的回复。
        blacklist: 本 stage 的禁用词序列；空序列直接返回 None。

    Returns:
        命中的第一个**原始**黑名单条目（便于日志归因）；未命中返回 None。
    """
    if not text or not blacklist:
        return None
    norm_text = _normalize(text)
    if not norm_text:
        return None
    for word in blacklist:
        if not word:
            continue
        if _normalize(word) in norm_text:
            return word
    return None


def fallback_message(course_type: str, stage: str) -> str:
    """命中黑名单且重生仍命中时的兜底文案。

    返回 stage 级中性引导话术，不揭示任何具体结论。
    """
    # 全 stage 通用兜底（保守、不剧透；具体 stage 可以在此扩展定制文案）
    return "我们再换一个角度想一想——你能从方程或图形里观察到什么？"


__all__ = [
    "STAGE_BLACKLIST",
    "get_stage_blacklist",
    "scan_spoiler",
    "fallback_message",
]
