"""双曲线 3.2.2 双曲线的简单几何性质 —— stage handlers + 静态数据"""
import re
from legacy.lesson_flow import LessonStage, LessonStep

# ---- 静态文本 ----
H322_INTRO_MSG = (
    "你好！上节课（3.2.1）我们由「双曲线的定义」推出了**标准方程** "
    "$\\dfrac{x^2}{a^2}-\\dfrac{y^2}{b^2}=1\\,(a>0, b>0)$，其中 $c^2=a^2+b^2$。\n\n"
    "本节我们要做与 3.1.2 相同的事 ——\n"
    "**从已有的方程出发，反过来研究双曲线的几何性质**。\n\n"
    "回顾一下椭圆几何性质（3.1.2）研究过哪些方面？\n"
    "（提示：范围、对称性、顶点、离心率……）"
)

# ── H322_EXAMPLE 题目 hard-coded（教材原题，禁止改任何数值）──
H322_EXAMPLE_1_INTRO = (
    "🟡 **例 1**\n\n"
    "求双曲线 $9y^2-16x^2=144$ 的**实半轴长**和**虚半轴长**、**焦点坐标**、"
    "**离心率**、**渐近线方程**。\n\n"
    "**第一步**：把方程化为**标准方程**，并判断焦点在 x 轴还是 y 轴？"
)

H322_EXAMPLE_2_INTRO = (
    "🟡 **例 2**\n\n"
    "动点 $M(x, y)$ 与定点 $F(4, 0)$ 的距离和它到定直线 $l: x=\\dfrac{9}{4}$ 的距离的比是常数 "
    "$\\dfrac{4}{3}$，求动点 $M$ 的轨迹。\n\n"
    "**第一步**：根据题意，把"
    "「$M$ 到 $F$ 的距离」与「$M$ 到直线 $l$ 的距离」的比值关系写成等式。"
)

H322_EXAMPLE_3_INTRO = (
    "🟡 **例 3**\n\n"
    "如图 3.2-12，过双曲线 $\\dfrac{x^2}{3}-\\dfrac{y^2}{6}=1$ 的**右焦点** $F_2$，"
    "**倾斜角为 30°** 的直线交双曲线于 $A, B$ 两点，求 $|AB|$。\n\n"
    "**第一步**：先求双曲线的**焦点坐标**，再写出直线 $AB$ 的方程。"
)

H322_SUMMARY_MSG = (
    "🎓 **3.2.2 总结**：椭圆 vs 双曲线 几何性质五维对照\n\n"
    "| 性质 | 椭圆 (3.1.2) | 双曲线 (3.2.2) |\n"
    "|---|---|---|\n"
    "| 范围 | $\\|x\\|\\le a, \\|y\\|\\le b$（封闭） | $\\|x\\|\\ge a, y\\in\\mathbb{R}$（向外延展） |\n"
    "| 对称性 | x 轴 / y 轴 / 原点 | **同上**（结构一致） |\n"
    "| 顶点 | **4 个**：$(\\pm a, 0), (0, \\pm b)$ | **只 2 个**：$A_1(-a,0), A_2(a,0)$ |\n"
    "| 轴术语 | 长轴 2a / 短轴 2b | **实轴 2a / 虚轴 2b**（$B_1,B_2$ 不在曲线上）|\n"
    "| **渐近线** | 无 | $y=\\pm\\dfrac{b}{a}x$（**独有**） |\n"
    "| 离心率 | $0<e<1$（越大越扁）| $e>1$（越大开口越张）|\n"
    "| 离心率与形状 | e→0 接近圆 | e 与 $b/a$ 关系 $b/a=\\sqrt{e^2-1}$ |\n\n"
    "**等轴双曲线**：$a=b$，渐近线 $y=\\pm x$（互相垂直），双曲线开口最对称。\n\n"
    "如果都明白了，回个『没问题』/『结束』我们就到这里。"
)


# ============================================================
# ---- 抛物线 3.3.1 课预置文本 (v3.x) ----
# 教材精确对齐铁律：所有数值、坐标、公式与教材 p130-p132 一字不差
# 苏格拉底铁律：题目原文之外的引导文案不得含答案数值
# ============================================================

# 关键词集合
PARABOLA_NAME_KEYWORDS_P331 = ["抛物线", "parabola"]
PARABOLA_DEFINITION_KEYWORDS_P331 = [
    # 距离相等核心词
    "距离相等", "距离一样", "距离等于", "距离=", "距离 =", "等距", "相等",
    "|mf|=|m", "|MF|=|M",
    # 定直线 / 准线相关
    "定直线", "准线", "直线不过",
]
PARABOLA_COORD_KEYWORDS_P331 = [
    # 建系关键意思
    "过f", "过焦点", "焦点", "垂直", "垂线", "中点",
    "x轴", "y轴", "原点", "对称",
    "kf中点", "顶点",
]
# 推导 4 子阶段关键词（备用，主路径由协议判断）
PARABOLA_DERIVE_KEYWORDS_P331 = [
    "|MF|", "(x-p/2)", "(x+p/2)", "d=", "平方", "化简", "y²=2px", "y^2=2px",
]


# ---- Stage Goals ----
H322_STAGE_GOALS = {
    LessonStage.H322_INTRO: (
        "📒 3.2.2 开场。让学生回忆 3.1.2 椭圆几何性质研究的方面（范围、对称性、顶点、离心率）。\n"
        "学生答出 ≥2 个对应方面即推进到 RANGE。\n\n"
        "可用动画：`show_h322_recall`（沙盒，椭圆 vs 双曲线 5 性质并排回忆）。"
    ) + _H322_VIZ_SUPPRESSION + _EXAMPLE_NO_FABRICATE_RULE,
    LessonStage.H322_RANGE: (
        "📒 范围阶段（教材 p122 §1）。2 phase：predict（猜 x、y 范围）→ derive（由 x²/a²≥1 严格推）。\n"
        "学生答出 **|x|≥a 且 y∈ℝ**（或 x≤-a 或 x≥a）即推进 SYMMETRY。\n"
        "**与椭圆对比**：椭圆是 |x|≤a 且 |y|≤b（封闭）；双曲线是 |x|≥a 且 y 无界（向外延展）。\n\n"
        "可用动画：`show_h322_range_setup`（双曲线 + x²/a²≥1 项标注）、`show_h322_range_solved`（含 ±a 虚线带 + 双曲线两支阴影区域）。"
    ) + _H322_VIZ_SUPPRESSION + _EXAMPLE_NO_FABRICATE_RULE,
    LessonStage.H322_SYMMETRY: (
        "📒 对称性阶段（教材 p122 §2）。3 phase 递进：y 轴 → x 轴 → 原点。每 phase 检测对应关键词推进。\n"
        "结构与 e312 SYMMETRY 完全一致（双曲线对称性与椭圆同模式）。\n\n"
        "可用动画：`show_h322_symmetry_setup`（双曲线 + 可拖点）、`show_h322_symmetry_solved`（4 镜像伙伴）。"
    ) + _H322_VIZ_SUPPRESSION + _EXAMPLE_NO_FABRICATE_RULE,
    LessonStage.H322_VERTICES_AXES: (
        "📒 顶点+实/虚轴阶段（教材 p122 §3，**与椭圆术语差异最大**）。3 phase：\n"
        "  · vertex_compute：沙盒 `show_h322_vertices_clickable` 8 候选点，学生只点 A₁(-a,0)、A₂(a,0) 两点"
        "（**反直觉**：椭圆 4 顶点，双曲线只 2 个；B₁B₂ 不在双曲线上）。前端 h322_vertex_clicked 事件累积。\n"
        "  · axes_name：答出『实轴 2a / 虚轴 2b』术语。\n"
        "  · imaginary_clarify：澄清 B₁(0,-b), B₂(0,b) 是虚轴端点但**不在双曲线上**。\n"
        "全部完成后推进 ASYMPTOTE。viz 完成时**保留虚线矩形框 x=±a, y=±b** 供下一 stage 复用。\n\n"
        "可用动画：`show_h322_vertices_clickable`、`show_h322_vertices_solved_with_rect`。"
    ) + _H322_VIZ_SUPPRESSION + _EXAMPLE_NO_FABRICATE_RULE,
    LessonStage.H322_ASYMPTOTE: (
        "⭐ 渐近线阶段（教材 p122 §4 + p123 顶段，**本课重点 + 双曲线独有**，无椭圆对照）。\n"
        "本 stage 3 phase 由 _H322_ASYMPTOTE_PHASE_GOALS 替换：rectangle → equation → behavior。\n"
        "视觉延续：复用上一 stage 的虚线矩形 → 矩形对角线动画 → 双曲线两支接近渐近线。\n\n"
        "可用动画：`show_h322_asymptote_from_rect`（矩形+对角线生长动画）、`show_h322_asymptote_final`（双曲线+渐近线，演示接近不相交）。"
    ) + _H322_VIZ_SUPPRESSION + _EXAMPLE_NO_FABRICATE_RULE,
    LessonStage.H322_EQUILATERAL: (
        "📒 等轴双曲线阶段（教材 p123 中段）。让学生回答：若 $a=b$，方程变为？渐近线变为？\n"
        "学生答出『$x^2-y^2=a^2$』或『$y=\\pm x$』即推进 ECCENTRICITY。\n"
        "**教材关键词**：等轴双曲线、渐近线互相垂直、正方形（四线 x=±a, y=±a 围成）。\n\n"
        "可用动画：`show_h322_equilateral`（a=b 滑块：双曲线 → 正方形 → 渐近线垂直 y=±x）。"
    ) + _H322_VIZ_SUPPRESSION + _EXAMPLE_NO_FABRICATE_RULE,
    LessonStage.H322_ECCENTRICITY: (
        "⭐ 离心率阶段（教材 p123 §5 + p124 顶段）：5 个 phase 苏格拉底诱导。\n"
        "_build_system_prompt 会按 phase 替换为 _H322_ECC_PHASE_GOALS 里的细分目标。\n"
        "**与椭圆对照**：椭圆 0<e<1（越大越扁），双曲线 e>1（越大开口越张）；新增 e 与 b/a 关系 $b/a=\\sqrt{e^2-1}$。"
    ) + _H322_VIZ_SUPPRESSION + _EXAMPLE_NO_FABRICATE_RULE,
    LessonStage.H322_EXAMPLE_1: (
        "🟡 例 1（教材 p124 例 3，$9y^2-16x^2=144$）。5 phase 苏格拉底逐项问：标准方程形式 → a/b → 焦点 → e → 渐近线。\n"
        "诊断器对答案严谨判等。phase_goal 由 example_canonicals_322.EXAMPLE_1_PHASE_GOAL 控制。\n"
        "**题目原文（铁律：不得修改任何数值）**：求双曲线 $9y^2-16x^2=144$ 的实半轴长和虚半轴长、焦点坐标、离心率、渐近线方程。\n"
        "**标准答案**：标准方程 $y^2/16-x^2/9=1$（焦点在 y 轴），a=4, b=3, c=5；焦点 (0, ±5)；e=5/4；渐近线 $y=\\pm\\dfrac{4}{3}x$。\n\n"
        "可用动画：`show_h322_example_1_setup`、`show_h322_example_1_solved`。"
    ) + _H322_VIZ_SUPPRESSION + _EXAMPLE_NO_FABRICATE_RULE,
    LessonStage.H322_EXAMPLE_2: (
        "🟡 例 2（教材 p125 例 5，$|MF|/d=4/3$）。3 phase：写关系 → 化简方程 → 结论（焦点 x 轴、实轴长 6、虚轴长 2√7）。\n"
        "完成后发 explore 动画让学生拖 M 感受比值恒为 4/3。\n"
        "**题目原文（铁律：不得修改）**：动点 M(x,y) 与定点 F(4,0) 的距离和它到定直线 l: x=9/4 的距离的比是常数 4/3，求动点 M 的轨迹。\n"
        "**标准答案**：化简 $7x^2-9y^2=63$，即 $x^2/9-y^2/7=1$；焦点在 x 轴、**实轴长 6**、**虚轴长 $2\\sqrt 7$**。\n\n"
        "可用动画：`show_h322_example_2_setup`、`show_h322_example_2_solved`、`show_h322_example_2_explore`（拖 M 感受 4/3）。"
    ) + _H322_VIZ_SUPPRESSION + _EXAMPLE_NO_FABRICATE_RULE,
    LessonStage.H322_EXAMPLE_3: (
        "🟡 例 3（教材 p126 例 6，焦点弦倾斜角 30°）。4 phase：直线方程 → 联立求 x₁,x₂ → A,B 坐标 → |AB|。\n"
        "**题目原文（铁律：不得修改）**：过双曲线 $x^2/3-y^2/6=1$ 的右焦点 F₂，倾斜角为 30° 的直线交双曲线于 A, B 两点，求 |AB|。\n"
        "**标准答案**：a²=3,b²=6,c=3，F₂(3,0)；直线 $y=\\dfrac{\\sqrt 3}{3}(x-3)$；联立消 y 得 $5x^2+6x-27=0$；"
        "$x_1=-3, x_2=9/5$；$A(-3,-2\\sqrt 3), B(9/5,-2\\sqrt 3/5)$；**$|AB|=\\dfrac{16\\sqrt 3}{5}$**。\n\n"
        "可用动画：`show_h322_example_3_setup`、`show_h322_example_3_solved`、`show_h322_example_3_explore`（倾斜角滑块 + |AB| 动态计算）。"
    ) + _H322_VIZ_SUPPRESSION + _EXAMPLE_NO_FABRICATE_RULE,
    LessonStage.H322_SUMMARY: (
        "📒 3.2.2 总结阶段。回顾 5 大几何性质 + 3 道例题。展示椭圆 vs 双曲线五维对照表。\n"
        "学生说『没问题』/『结束』时附加 [LESSON_END] 标记。\n\n"
        "可用动画：`show_h322_summary`（椭圆 vs 双曲线对照图，渐近线特征独立标记）。"
    ) + _H322_VIZ_SUPPRESSION + _EXAMPLE_NO_FABRICATE_RULE,
}

_STAGE_GOALS.update(_STAGE_GOALS_H322)


# ===============================================================
# ---- 抛物线 3.3.1 课（v3.x 新增）—— 教材 p130-p132，12 stage 教学目标 ----
# 5 LLM 角色谱见论文素材 2.5.9 节；例题三层防御见 2.5.5 节
# 苏格拉底铁律：所有 stage_goal 描述不得含答案数值（6 / -2 / 1.44 / 2.88 / 5.76 / 8）
# ===============================================================

_P331_VIZ_SUPPRESSION = (
    "\n\n**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
    "学生明确要求看动画时温和回应「好的，我们看一个动画」，由系统自动配图。"
    "**严禁承诺画不出的图**：本章可用动画清单见各 phase。"
)

# ---- Course Config ----
H322_COURSE_CONFIG = {
    "hyperbola_322": {
        "name_cn": "3.2.2 双曲线的简单几何性质",
        "scope": "hyperbola",
        "first_stage": LessonStage.H322_INTRO,
        "start_stage": LessonStage.H322_INTRO,  # 学生回答后由 INTRO handler 推进到 RANGE
        "kg_nodes_basic": [
            "hyperbola_definition", "hyperbola_standard_equation_x",
            "hyperbola_parameter_triangle",
        ],
        "kg_nodes_equation": [
            "hyperbola_range", "hyperbola_symmetry", "hyperbola_vertices",
            "hyperbola_real_axis", "hyperbola_imaginary_axis",
            "hyperbola_asymptote",  # 双曲线特有
            "hyperbola_equilateral",
        ],
        "kg_nodes_eccentricity": [
            "hyperbola_eccentricity", "concept_eccentricity_unified",
        ],
        "kg_nodes_examples": {
            LessonStage.H322_EXAMPLE_1: ["hyperbola_322_example_1"],
            LessonStage.H322_EXAMPLE_2: ["hyperbola_322_example_2"],
            LessonStage.H322_EXAMPLE_3: ["hyperbola_322_example_3"],
        },
        "eccentricity_stages": {LessonStage.H322_ECCENTRICITY, LessonStage.H322_SUMMARY},
        "summary_kg_nodes": [
            "hyperbola_range", "hyperbola_symmetry", "hyperbola_vertices",
            "hyperbola_asymptote", "hyperbola_eccentricity",
        ],
    },
}

# ---- Mandatory VIZ ----
H322_MANDATORY_VIZ = {
    # INTRO 不出画布（让学生先回忆 e312 性质）
    LessonStage.H322_RANGE:           {"action": "show_h322_range_setup"},
    LessonStage.H322_SYMMETRY:        {"action": "show_h322_symmetry_setup"},
    # VERTICES_AXES 入口：8 候选点的点击交互沙盒
    LessonStage.H322_VERTICES_AXES:   {"action": "show_h322_vertices_clickable"},
    # ASYMPTOTE 入口：教材 p122-123 探究 —— 具体双曲线 x²/9-y²/4=1 + 两条直线，
    # 学生拖点 M 在右支上感知 x_M↑ → d↓（但永远不为 0）。**不剧透 b/a 公式**。
    # 完成 explore_concrete phase 后由 handler 主动切到 show_h322_asymptote_generalize
    LessonStage.H322_ASYMPTOTE:       {"action": "show_h322_asymptote_explore"},
    LessonStage.H322_EQUILATERAL:     {"action": "show_h322_equilateral"},
    # ECCENTRICITY 入口：**不剧透**——前 3 phase（recall_e/range_e/geometry）是文字 + 概念探究，
    #   slider 互动留到 phase 4 (slider_experience) 由 handler 主动发；
    #   因此 ECCENTRICITY stage 入口不发任何 mandatory viz（画布保留上一 stage 的内容或空）。
    # 3 道例题入口：setup 版（题目方程，不剧透答案）
    LessonStage.H322_EXAMPLE_1:       {"action": "show_h322_example_1_setup"},
    LessonStage.H322_EXAMPLE_2:       {"action": "show_h322_example_2_setup"},
    LessonStage.H322_EXAMPLE_3:       {"action": "show_h322_example_3_setup"},
}

# ---- Skip function ----
def _looks_like_skip_to_example_322(text: str):
    """识别学生「直接跳到例 N」意图。内部编号 1/2/3 对应教材例 3/5/6。
    返回 1 / 2 / 3 / None。"""
    t = text.replace(" ", "")
    has_skip_intent = any(kw in t for kw in [
        "直接", "跳到", "跳过", "看例", "进入例", "看第", "进入第", "看练习", "进入练习",
    ])
    if not has_skip_intent:
        return None
    if "例1" in t or "例一" in t or "第一题" in t or "第1题" in t:
        return 1
    if "例2" in t or "例二" in t or "第二题" in t or "第2题" in t:
        return 2
    if "例3" in t or "例三" in t or "第三题" in t or "第3题" in t:
        return 3
    return None



# ---- Stage Dispatch Registry ----
H322_STAGE_DISPATCH = {
    LessonStage.H322_INTRO: ("_handle_h322_intro", {}),
    LessonStage.H322_RANGE: ("_handle_h322_range", {}),
    LessonStage.H322_SYMMETRY: ("_handle_h322_symmetry", {}),
    LessonStage.H322_VERTICES_AXES: ("_handle_h322_vertices_axes", {}),
    LessonStage.H322_ASYMPTOTE: ("_handle_h322_asymptote", {}),
    LessonStage.H322_EQUILATERAL: ("_handle_h322_equilateral", {}),
    LessonStage.H322_ECCENTRICITY: ("_handle_h322_eccentricity", {}),
    LessonStage.H322_EXAMPLE_1: ("_handle_h322_example", {"example_num": 1}),
    LessonStage.H322_EXAMPLE_2: ("_handle_h322_example", {"example_num": 2}),
    LessonStage.H322_EXAMPLE_3: ("_handle_h322_example", {"example_num": 3}),
    LessonStage.H322_SUMMARY: ("_handle_h322_summary", {}),
}


class Hyperbola322Mixin:
    """双曲线 3.2.2 课 stage handlers（作为 LessonFlow 的 mixin 使用）"""

    def _handle_h322_example_generic(self, text: str, example_key) -> LessonStep:
        """v3.46 311-style 例题 generic handler（仿 _handle_h321_example_generic）。

        三层防御：
          Layer 1: example_diagnostician_322（全 goal 扫描，无 phase 参数）
          Layer 2: 路径 2 协议 LLM 兜底（角色 2）
          Layer 3: deterministic phase prompt

        架构：
          · 诊断器命中 → 累积 implied_flags 到 subflags
          · done_fn(subflags) 满足 → _h322_advance_example 收尾（awaiting_next）
          · 部分命中 → 按 _H322_PHASE_REQUIRED_FLAGS 找下一未完成 phase + 精准追问
        """
        from .example_canonicals_322 import EXAMPLE_CONFIGS_322
        from .example_diagnostician_322 import diagnose_example_322

        # 0. awaiting_next 状态检查（前次例题完成等学生确认）
        if getattr(self, "_h322_example_done_awaiting_next", None) is not None:
            t = text.replace(" ", "")
            if any(kw in t for kw in ["继续", "没问题", "好的", "好", "可以", "下一题", "下一", "ok", "OK"]):
                return self._continue_to_next_h322_example()
            # 学生没确认 → 提示
            return LessonStep(
                stage=self.stage.value,
                message="如果都明白了，回复「**继续**」进入下一题；或者你可以问我刚才哪一步还想再讲。",
            )

        # 1. 跨例跳级（学生说"看例 N"）
        skip_n = _looks_like_skip_to_example_322(text)
        if skip_n is not None and skip_n != example_key:
            target_stage, target_intro = {
                1: (LessonStage.H322_EXAMPLE_1, H322_EXAMPLE_1_INTRO),
                2: (LessonStage.H322_EXAMPLE_2, H322_EXAMPLE_2_INTRO),
                3: (LessonStage.H322_EXAMPLE_3, H322_EXAMPLE_3_INTRO),
            }[skip_n]
            self.stage = target_stage
            self._h322_example_subflags = set()  # 新题独立 subflags
            # v3.50.2：跨例跳级时清理跨轮累积字典（防止上一题状态污染）
            self._h322_example_conclude_hits = {}
            self._h322_example_partial_pts = {}
            viz = H322_MANDATORY_VIZ.get(target_stage)
            return LessonStep(
                stage=self.stage.value,
                message=f"好的，跳到例 {skip_n}：\n\n" + target_intro,
                canvas_action=viz,
            )

        # 2. 初始化 subflags（每题独立）
        if not hasattr(self, "_h322_example_subflags") or getattr(self, "_h322_example_active", None) != example_key:
            self._h322_example_subflags = set()
            self._h322_example_active = example_key
        subflags: set = self._h322_example_subflags

        config = EXAMPLE_CONFIGS_322[example_key]
        done_fn = config["done_fn"]

        # v3.52 调试日志：每条输入打印 raw + 归一后 + 当前 subflags，便于用户截图排错
        try:
            _normed_dbg = self._h322_normalize_text(text)
        except Exception:
            _normed_dbg = "<norm-fail>"
        print(f"[H322 EX{example_key}] raw={text!r} normed={_normed_dbg!r} "
              f"subflags={sorted(subflags)}")

        # 3. Layer 1: 诊断器全 goal 扫描
        dx = diagnose_example_322(text, example_key)

        # v3.50.2 例 1 ask_focus 焦点点跨轮累积（仿 312 例 4 partial_hit_point_set）
        # 学生分两次答 (0, 5) → (0, -5) 时也要累积，不能只接受一次性答全
        if example_key == 1 and "focus_done" not in subflags:
            from .example_diagnostician_322 import _extract_point_tuples
            canonical_pts = set(config["canonical"]["focus_set"])
            student_pts = _extract_point_tuples(text)
            if not hasattr(self, "_h322_example_partial_pts"):
                self._h322_example_partial_pts = {}
            cache_key = (1, "ask_focus")
            accumulated = self._h322_example_partial_pts.get(cache_key, set())
            new_hits = student_pts & canonical_pts
            if new_hits:
                accumulated |= new_hits
                self._h322_example_partial_pts[cache_key] = accumulated
                if accumulated == canonical_pts:
                    # 累积满 → 命中 focus_set
                    implies = config["implies"].get("focus_set", set())
                    subflags |= implies
                    self._h322_example_subflags = subflags
                    if done_fn(subflags):
                        return self._h322_advance_example(example_key)
                    # 推进到下一 phase 由后续流程处理
                else:
                    # 苏格拉底引导：不直接给坐标，提示"对称性"——双曲线焦点关于原点对称
                    got_str = "、".join(f"$({p[0]}, {p[1]})$" for p in sorted(new_hits))
                    return LessonStep(
                        stage=self.stage.value,
                        message=(
                            f"✅ 答出 {got_str}。\n\n"
                            "**双曲线焦点关于原点对称**——已经答出一个，**对称那个**是？"
                        ),
                    )

        # v3.50.2 例 3 ask_intersect x_set 跨轮累积（同模式）
        # 学生分两次答 x₁=-3 → x₂=9/5 时也要累积
        if example_key == 3 and "intersect_done" not in subflags:
            from .example_diagnostician_322 import _extract_x_values
            canonical_x = set(config["canonical"]["x_set"])
            student_x = _extract_x_values(text)
            if not hasattr(self, "_h322_example_partial_pts"):
                self._h322_example_partial_pts = {}
            cache_key = (3, "ask_intersect")
            accumulated = self._h322_example_partial_pts.get(cache_key, set())
            new_hits = student_x & canonical_x
            if new_hits:
                accumulated |= new_hits
                self._h322_example_partial_pts[cache_key] = accumulated
                if accumulated == canonical_x:
                    implies = config["implies"].get("x_set", set())
                    subflags |= implies
                    self._h322_example_subflags = subflags
                    if done_fn(subflags):
                        return self._h322_advance_example(example_key)
                else:
                    # 苏格拉底引导：不直接给另一个根，提示"二次方程两根"
                    got_str = "、".join(f"$x={v}$" for v in sorted(new_hits, key=lambda r: float(r)))
                    return LessonStep(
                        stage=self.stage.value,
                        message=(
                            f"✅ 答出 {got_str}。\n\n"
                            "**二次方程 $5x^2+6x-27=0$ 有两个根** —— 用求根公式 / 因式分解再求一个？"
                        ),
                    )

        # v3.50 例 2 ask_conclude 跨轮关键词维度累积（仿 312 例 5 _e312_example_conclude_hits）
        # 学生可能分多轮答："焦点在 x 轴" + "2a=6, 2b=2√7" + "实轴长 6, 虚轴长 2√7"
        # 三维度（x_axis / real_axis_6 / imag_axis_2sqrt7）各自累积，齐了才标 conclude_done
        if example_key == 2 and "conclude_done" not in subflags:
            if not hasattr(self, "_h322_example_conclude_hits"):
                self._h322_example_conclude_hits = {}
            raw = text
            t_norm = self._h322_normalize_text(text)  # 已去空格 + × → * + ÷ → / 等
            t_lower = t_norm.lower()
            hits = self._h322_example_conclude_hits.get(2,
                       {"x_axis": False, "real_6": False, "imag_2sqrt7": False})
            # 维度 1：焦点在 x 轴
            if any(kw in t_norm for kw in ["焦点在x轴", "焦点在x", "x轴上", "焦点x轴"]) \
               or ("x轴" in t_norm and "焦点" in t_norm) \
               or ("轨迹是双曲线" in t_norm and "x" in t_norm and "轴" in t_norm):
                hits["x_axis"] = True
            # 维度 2：实轴长 6 / 2a=6
            if "2a=6" in t_norm or ("实轴" in t_norm and "6" in t_norm) \
               or "实轴长6" in t_norm or "实轴长为6" in t_norm:
                hits["real_6"] = True
            # 维度 3：虚轴长 2√7 / 2b=2√7（v3.51 修：用 t_norm 兜空格，加 × → * 变体）
            #   t_norm 已经把 × 归一为 *，所以 "2 × √7" → "2*√7"
            has_imag = (
                "2√7" in t_norm                       # 2√7（学生紧凑写）
                or "2*√7" in t_norm                  # 2 × √7（× 已归一 *）
                or "2sqrt(7)" in t_lower             # 2sqrt(7)
                or "2sqrt7" in t_lower               # 2sqrt7
                or "2*sqrt(7)" in t_lower            # 2 × sqrt(7)
                or "2*sqrt7" in t_lower              # 2 × sqrt7
                # v3.51 同源修复：中文写法也用 t_norm 兜空格
                or "2根号7" in t_norm or "二根号7" in t_norm or "2倍根号7" in t_norm
                or "2b=2√7" in t_norm or "2b=2*√7" in t_norm
                or "2b=2sqrt(7)" in t_lower or "2b=2*sqrt(7)" in t_lower
            )
            if has_imag:
                hits["imag_2sqrt7"] = True
            self._h322_example_conclude_hits[2] = hits

            if all(hits.values()):
                # 三维度齐 → 标 conclude_done（即使 LLM/诊断器都没命中）
                subflags |= {"conclude_done"}
                self._h322_example_subflags = subflags
                # 整道题完成 → advance
                if done_fn(subflags):
                    return self._h322_advance_example(example_key)

        if dx is not None:
            subflags |= dx.implied_flags
            self._h322_example_subflags = subflags
            # 整道题完成 → advance
            if done_fn(subflags):
                return self._h322_advance_example(example_key)
            # 部分命中 → 找下一未答完 phase
            next_phase = self._h322_find_next_unanswered_phase(example_key, subflags)
            if next_phase is None:
                # 边界：所有 phase required 都满足但 done_fn 还未触发（不太可能，但保险）
                return self._h322_advance_example(example_key)
            ack = "✅ " + "、".join(dx.hit_goals) + " 收到。"
            # 精准追问（missing-aware）
            required = _H322_PHASE_REQUIRED_FLAGS.get((example_key, next_phase), set())
            missing = required - subflags
            specific_prompt = None
            if len(missing) == 1:
                missing_flag = next(iter(missing))
                specific_prompt = _H322_PHASE_PROMPT_BY_MISSING.get((example_key, next_phase, missing_flag))
            phase_prompt = specific_prompt or self._h322_example_phase_prompt(example_key, next_phase)
            return LessonStep(
                stage=self.stage.value,
                message=ack + "\n\n" + phase_prompt,
            )

        # v3.50：例 2 ask_conclude 跨轮累积部分命中 → 苏格拉底式追问（不剧透数值）
        if example_key == 2 and "conclude_done" not in subflags:
            hits = getattr(self, "_h322_example_conclude_hits", {}).get(2, {})
            if any(hits.values()) and not all(hits.values()):
                # 已答的维度（不剧透答案，只点名）
                got_label = {"x_axis": "焦点在 x 轴", "real_6": "实轴长", "imag_2sqrt7": "虚轴长"}
                # 还差维度的"苏格拉底提示"（**不给数值**，只引导从方程读出）
                hint_label = {
                    "x_axis":      "**焦点在哪个轴**？（看你刚化简的方程 $\\dfrac{x^2}{?}-\\dfrac{y^2}{?}=1$ 哪一项符号是正的，焦点就在那个轴上）",
                    "real_6":      "**实轴长 $2a$**？（从方程读出 $a^2$ 再开方，乘 2）",
                    "imag_2sqrt7": "**虚轴长 $2b$**？（从方程读出 $b^2$ 再开方，乘 2）",
                }
                got_parts = [got_label[k] for k, v in hits.items() if v]
                miss_hints = [hint_label[k] for k, v in hits.items() if not v]
                got_txt = "、".join(got_parts) if got_parts else ""
                return LessonStep(
                    stage=self.stage.value,
                    message=(
                        (f"✅ 已答出：**{got_txt}**。\n\n" if got_txt else "")
                        + "还差：\n" + "\n".join(f"  · {h}" for h in miss_hints)
                    ),
                )

        # 4. Layer 2: 路径 2 协议（LLM 兜底）
        next_phase = self._h322_find_next_unanswered_phase(example_key, subflags) or config["phases"][0]
        protocol = self._llm_h322_example_protocol(text, example_key, next_phase)
        if protocol is not None:
            # skip_request 处理
            skip_to = protocol.get("skip_to_example")
            if skip_to in (1, 2, 3) and skip_to != example_key:
                target_stage = {1: LessonStage.H322_EXAMPLE_1, 2: LessonStage.H322_EXAMPLE_2, 3: LessonStage.H322_EXAMPLE_3}[skip_to]
                target_intro = {1: H322_EXAMPLE_1_INTRO, 2: H322_EXAMPLE_2_INTRO, 3: H322_EXAMPLE_3_INTRO}[skip_to]
                self.stage = target_stage
                self._h322_example_subflags = set()
                viz = H322_MANDATORY_VIZ.get(target_stage)
                return LessonStep(stage=self.stage.value,
                                  message=f"好的，跳到例 {skip_to}：\n\n" + target_intro,
                                  canvas_action=viz)
            ack = (protocol.get("ack_text") or "")[:200]
            if not ack:
                ack = "（继续作答）"
            if protocol.get("diagnosis") == "correct" and protocol.get("advance"):
                # 协议判 advance 但诊断器没命中 → 标 phase required flag 防卡循环
                hit = protocol.get("hit_goal")
                if hit:
                    implies = config["implies"].get(hit, set())
                    subflags |= implies
                    self._h322_example_subflags = subflags
                    if done_fn(subflags):
                        return self._h322_advance_example(example_key)
                    # v3.49：subflags 更新后**必须重算 next_phase**，否则 ack 后又问已答的 phase
                    new_next = self._h322_find_next_unanswered_phase(example_key, subflags)
                    if new_next is not None:
                        next_phase = new_next
            # 用协议 ack + 下一 phase 提问（next_phase 已是更新后的值）
            phase_prompt = self._h322_example_phase_prompt(example_key, next_phase)
            return LessonStep(stage=self.stage.value, message=ack + "\n\n" + phase_prompt)

        # 5. Layer 3: deterministic
        return LessonStep(
            stage=self.stage.value,
            message=self._h322_example_phase_prompt(example_key, next_phase),
        )



    def _h322_find_next_unanswered_phase(self, example_key, subflags: set) -> Optional[str]:
        """按 phase 顺序找第一个未答完的 phase。返回 phase 名或 None（全答完）。"""
        from .example_canonicals_322 import EXAMPLE_CONFIGS_322
        if example_key not in EXAMPLE_CONFIGS_322:
            return None
        phases = EXAMPLE_CONFIGS_322[example_key]["phases"]
        for phase in phases:
            required = _H322_PHASE_REQUIRED_FLAGS.get((example_key, phase), set())
            if not required.issubset(subflags):
                return phase
        return None


    def _h322_advance_example(self, example_key) -> LessonStep:
        """例题完整通关，切下一题或 SUMMARY；写 awaiting_next 标志位等学生确认。

        v3.48：仿 _advance_e312_example / _advance_h321_example，例 2 / 例 3 完成后
        追加 explore viz（拖 M 看比值 / 拖倾斜角看 |AB|）。前端 applyCanvasAction 已支持 list 链式。
        """
        # 标 awaiting_next，等学生确认后再切
        self._h322_example_done_awaiting_next = example_key
        next_label = {1: "例 2", 2: "例 3", 3: "总结"}.get(example_key, "下一节")
        # 起手 solved
        actions = [{"action": f"show_h322_example_{example_key}_solved"}]
        # 例 2 |MF|/d 拖 M 互动；例 3 倾斜角滑块互动（例 1 没有 explore viz）
        explore_hint = ""
        if example_key in (2, 3):
            actions.append({"action": f"show_h322_example_{example_key}_explore"})
            if example_key == 2:
                explore_hint = "右图切到了**拖 $M$ 感受 $|MF|/d=4/3$** 互动 —— 拖动看看比值是不是恒等于 $4/3$。\n\n"
            elif example_key == 3:
                explore_hint = "右图切到了**拖倾斜角滑块**互动 —— 看不同角度下 $|AB|$ 怎么变。\n\n"
        return LessonStep(
            stage=self.stage.value,
            message=(
                f"🎉 例 {example_key} 完成！整道题已通关。\n\n"
                + explore_hint
                + f"如果都明白了，回复「**继续**」/「**没问题**」进入 **{next_label}**；"
                f"如果还想看下哪一步的解析，可以再问我。"
            ),
            canvas_action=actions if len(actions) > 1 else actions[0],
        )


    def _continue_to_next_h322_example(self) -> LessonStep:
        """学生确认 awaiting_next 后，切到下一例题或 SUMMARY。"""
        prev = getattr(self, "_h322_example_done_awaiting_next", None)
        self._h322_example_done_awaiting_next = None
        # 重置 subflags（下一题独立）
        if hasattr(self, "_h322_example_subflags"):
            self._h322_example_subflags = set()
        # v3.50.2：跨例切换时清理累积字典
        self._h322_example_conclude_hits = {}
        self._h322_example_partial_pts = {}
        if prev == 1:
            self.stage = LessonStage.H322_EXAMPLE_2
            viz = H322_MANDATORY_VIZ.get(LessonStage.H322_EXAMPLE_2)
            return LessonStep(stage=self.stage.value, message=H322_EXAMPLE_2_INTRO, canvas_action=viz)
        if prev == 2:
            self.stage = LessonStage.H322_EXAMPLE_3
            viz = H322_MANDATORY_VIZ.get(LessonStage.H322_EXAMPLE_3)
            return LessonStep(stage=self.stage.value, message=H322_EXAMPLE_3_INTRO, canvas_action=viz)
        if prev == 3:
            self.stage = LessonStage.H322_SUMMARY
            return LessonStep(stage=self.stage.value, message=H322_SUMMARY_MSG)
        # fallback
        return LessonStep(stage=self.stage.value, message="（系统提示）已是最后一题，输入「结束」结课。")


    def _handle_h322_example_generic(self, text: str, example_key) -> LessonStep:
        """v3.46 311-style 例题 generic handler（仿 _handle_h321_example_generic）。

        三层防御：
          Layer 1: example_diagnostician_322（全 goal 扫描，无 phase 参数）
          Layer 2: 路径 2 协议 LLM 兜底（角色 2）
          Layer 3: deterministic phase prompt

        架构：
          · 诊断器命中 → 累积 implied_flags 到 subflags
          · done_fn(subflags) 满足 → _h322_advance_example 收尾（awaiting_next）
          · 部分命中 → 按 _H322_PHASE_REQUIRED_FLAGS 找下一未完成 phase + 精准追问
        """
        from .example_canonicals_322 import EXAMPLE_CONFIGS_322
        from .example_diagnostician_322 import diagnose_example_322

        # 0. awaiting_next 状态检查（前次例题完成等学生确认）
        if getattr(self, "_h322_example_done_awaiting_next", None) is not None:
            t = text.replace(" ", "")
            if any(kw in t for kw in ["继续", "没问题", "好的", "好", "可以", "下一题", "下一", "ok", "OK"]):
                return self._continue_to_next_h322_example()
            # 学生没确认 → 提示
            return LessonStep(
                stage=self.stage.value,
                message="如果都明白了，回复「**继续**」进入下一题；或者你可以问我刚才哪一步还想再讲。",
            )

        # 1. 跨例跳级（学生说"看例 N"）
        skip_n = _looks_like_skip_to_example_322(text)
        if skip_n is not None and skip_n != example_key:
            target_stage, target_intro = {
                1: (LessonStage.H322_EXAMPLE_1, H322_EXAMPLE_1_INTRO),
                2: (LessonStage.H322_EXAMPLE_2, H322_EXAMPLE_2_INTRO),
                3: (LessonStage.H322_EXAMPLE_3, H322_EXAMPLE_3_INTRO),
            }[skip_n]
            self.stage = target_stage
            self._h322_example_subflags = set()  # 新题独立 subflags
            # v3.50.2：跨例跳级时清理跨轮累积字典（防止上一题状态污染）
            self._h322_example_conclude_hits = {}
            self._h322_example_partial_pts = {}
            viz = H322_MANDATORY_VIZ.get(target_stage)
            return LessonStep(
                stage=self.stage.value,
                message=f"好的，跳到例 {skip_n}：\n\n" + target_intro,
                canvas_action=viz,
            )

        # 2. 初始化 subflags（每题独立）
        if not hasattr(self, "_h322_example_subflags") or getattr(self, "_h322_example_active", None) != example_key:
            self._h322_example_subflags = set()
            self._h322_example_active = example_key
        subflags: set = self._h322_example_subflags

        config = EXAMPLE_CONFIGS_322[example_key]
        done_fn = config["done_fn"]

        # v3.52 调试日志：每条输入打印 raw + 归一后 + 当前 subflags，便于用户截图排错
        try:
            _normed_dbg = self._h322_normalize_text(text)
        except Exception:
            _normed_dbg = "<norm-fail>"
        print(f"[H322 EX{example_key}] raw={text!r} normed={_normed_dbg!r} "
              f"subflags={sorted(subflags)}")

        # 3. Layer 1: 诊断器全 goal 扫描
        dx = diagnose_example_322(text, example_key)

        # v3.50.2 例 1 ask_focus 焦点点跨轮累积（仿 312 例 4 partial_hit_point_set）
        # 学生分两次答 (0, 5) → (0, -5) 时也要累积，不能只接受一次性答全
        if example_key == 1 and "focus_done" not in subflags:
            from .example_diagnostician_322 import _extract_point_tuples
            canonical_pts = set(config["canonical"]["focus_set"])
            student_pts = _extract_point_tuples(text)
            if not hasattr(self, "_h322_example_partial_pts"):
                self._h322_example_partial_pts = {}
            cache_key = (1, "ask_focus")
            accumulated = self._h322_example_partial_pts.get(cache_key, set())
            new_hits = student_pts & canonical_pts
            if new_hits:
                accumulated |= new_hits
                self._h322_example_partial_pts[cache_key] = accumulated
                if accumulated == canonical_pts:
                    # 累积满 → 命中 focus_set
                    implies = config["implies"].get("focus_set", set())
                    subflags |= implies
                    self._h322_example_subflags = subflags
                    if done_fn(subflags):
                        return self._h322_advance_example(example_key)
                    # 推进到下一 phase 由后续流程处理
                else:
                    # 苏格拉底引导：不直接给坐标，提示"对称性"——双曲线焦点关于原点对称
                    got_str = "、".join(f"$({p[0]}, {p[1]})$" for p in sorted(new_hits))
                    return LessonStep(
                        stage=self.stage.value,
                        message=(
                            f"✅ 答出 {got_str}。\n\n"
                            "**双曲线焦点关于原点对称**——已经答出一个，**对称那个**是？"
                        ),
                    )

        # v3.50.2 例 3 ask_intersect x_set 跨轮累积（同模式）
        # 学生分两次答 x₁=-3 → x₂=9/5 时也要累积
        if example_key == 3 and "intersect_done" not in subflags:
            from .example_diagnostician_322 import _extract_x_values
            canonical_x = set(config["canonical"]["x_set"])
            student_x = _extract_x_values(text)
            if not hasattr(self, "_h322_example_partial_pts"):
                self._h322_example_partial_pts = {}
            cache_key = (3, "ask_intersect")
            accumulated = self._h322_example_partial_pts.get(cache_key, set())
            new_hits = student_x & canonical_x
            if new_hits:
                accumulated |= new_hits
                self._h322_example_partial_pts[cache_key] = accumulated
                if accumulated == canonical_x:
                    implies = config["implies"].get("x_set", set())
                    subflags |= implies
                    self._h322_example_subflags = subflags
                    if done_fn(subflags):
                        return self._h322_advance_example(example_key)
                else:
                    # 苏格拉底引导：不直接给另一个根，提示"二次方程两根"
                    got_str = "、".join(f"$x={v}$" for v in sorted(new_hits, key=lambda r: float(r)))
                    return LessonStep(
                        stage=self.stage.value,
                        message=(
                            f"✅ 答出 {got_str}。\n\n"
                            "**二次方程 $5x^2+6x-27=0$ 有两个根** —— 用求根公式 / 因式分解再求一个？"
                        ),
                    )

        # v3.50 例 2 ask_conclude 跨轮关键词维度累积（仿 312 例 5 _e312_example_conclude_hits）
        # 学生可能分多轮答："焦点在 x 轴" + "2a=6, 2b=2√7" + "实轴长 6, 虚轴长 2√7"
        # 三维度（x_axis / real_axis_6 / imag_axis_2sqrt7）各自累积，齐了才标 conclude_done
        if example_key == 2 and "conclude_done" not in subflags:
            if not hasattr(self, "_h322_example_conclude_hits"):
                self._h322_example_conclude_hits = {}
            raw = text
            t_norm = self._h322_normalize_text(text)  # 已去空格 + × → * + ÷ → / 等
            t_lower = t_norm.lower()
            hits = self._h322_example_conclude_hits.get(2,
                       {"x_axis": False, "real_6": False, "imag_2sqrt7": False})
            # 维度 1：焦点在 x 轴
            if any(kw in t_norm for kw in ["焦点在x轴", "焦点在x", "x轴上", "焦点x轴"]) \
               or ("x轴" in t_norm and "焦点" in t_norm) \
               or ("轨迹是双曲线" in t_norm and "x" in t_norm and "轴" in t_norm):
                hits["x_axis"] = True
            # 维度 2：实轴长 6 / 2a=6
            if "2a=6" in t_norm or ("实轴" in t_norm and "6" in t_norm) \
               or "实轴长6" in t_norm or "实轴长为6" in t_norm:
                hits["real_6"] = True
            # 维度 3：虚轴长 2√7 / 2b=2√7（v3.51 修：用 t_norm 兜空格，加 × → * 变体）
            #   t_norm 已经把 × 归一为 *，所以 "2 × √7" → "2*√7"
            has_imag = (
                "2√7" in t_norm                       # 2√7（学生紧凑写）
                or "2*√7" in t_norm                  # 2 × √7（× 已归一 *）
                or "2sqrt(7)" in t_lower             # 2sqrt(7)
                or "2sqrt7" in t_lower               # 2sqrt7
                or "2*sqrt(7)" in t_lower            # 2 × sqrt(7)
                or "2*sqrt7" in t_lower              # 2 × sqrt7
                # v3.51 同源修复：中文写法也用 t_norm 兜空格
                or "2根号7" in t_norm or "二根号7" in t_norm or "2倍根号7" in t_norm
                or "2b=2√7" in t_norm or "2b=2*√7" in t_norm
                or "2b=2sqrt(7)" in t_lower or "2b=2*sqrt(7)" in t_lower
            )
            if has_imag:
                hits["imag_2sqrt7"] = True
            self._h322_example_conclude_hits[2] = hits

            if all(hits.values()):
                # 三维度齐 → 标 conclude_done（即使 LLM/诊断器都没命中）
                subflags |= {"conclude_done"}
                self._h322_example_subflags = subflags
                # 整道题完成 → advance
                if done_fn(subflags):
                    return self._h322_advance_example(example_key)

        if dx is not None:
            subflags |= dx.implied_flags
            self._h322_example_subflags = subflags
            # 整道题完成 → advance
            if done_fn(subflags):
                return self._h322_advance_example(example_key)
            # 部分命中 → 找下一未答完 phase
            next_phase = self._h322_find_next_unanswered_phase(example_key, subflags)
            if next_phase is None:
                # 边界：所有 phase required 都满足但 done_fn 还未触发（不太可能，但保险）
                return self._h322_advance_example(example_key)
            ack = "✅ " + "、".join(dx.hit_goals) + " 收到。"
            # 精准追问（missing-aware）
            required = _H322_PHASE_REQUIRED_FLAGS.get((example_key, next_phase), set())
            missing = required - subflags
            specific_prompt = None
            if len(missing) == 1:
                missing_flag = next(iter(missing))
                specific_prompt = _H322_PHASE_PROMPT_BY_MISSING.get((example_key, next_phase, missing_flag))
            phase_prompt = specific_prompt or self._h322_example_phase_prompt(example_key, next_phase)
            return LessonStep(
                stage=self.stage.value,
                message=ack + "\n\n" + phase_prompt,
            )

        # v3.50：例 2 ask_conclude 跨轮累积部分命中 → 苏格拉底式追问（不剧透数值）
        if example_key == 2 and "conclude_done" not in subflags:
            hits = getattr(self, "_h322_example_conclude_hits", {}).get(2, {})
            if any(hits.values()) and not all(hits.values()):
                # 已答的维度（不剧透答案，只点名）
                got_label = {"x_axis": "焦点在 x 轴", "real_6": "实轴长", "imag_2sqrt7": "虚轴长"}
                # 还差维度的"苏格拉底提示"（**不给数值**，只引导从方程读出）
                hint_label = {
                    "x_axis":      "**焦点在哪个轴**？（看你刚化简的方程 $\\dfrac{x^2}{?}-\\dfrac{y^2}{?}=1$ 哪一项符号是正的，焦点就在那个轴上）",
                    "real_6":      "**实轴长 $2a$**？（从方程读出 $a^2$ 再开方，乘 2）",
                    "imag_2sqrt7": "**虚轴长 $2b$**？（从方程读出 $b^2$ 再开方，乘 2）",
                }
                got_parts = [got_label[k] for k, v in hits.items() if v]
                miss_hints = [hint_label[k] for k, v in hits.items() if not v]
                got_txt = "、".join(got_parts) if got_parts else ""
                return LessonStep(
                    stage=self.stage.value,
                    message=(
                        (f"✅ 已答出：**{got_txt}**。\n\n" if got_txt else "")
                        + "还差：\n" + "\n".join(f"  · {h}" for h in miss_hints)
                    ),
                )

        # 4. Layer 2: 路径 2 协议（LLM 兜底）
        next_phase = self._h322_find_next_unanswered_phase(example_key, subflags) or config["phases"][0]
        protocol = self._llm_h322_example_protocol(text, example_key, next_phase)
        if protocol is not None:
            # skip_request 处理
            skip_to = protocol.get("skip_to_example")
            if skip_to in (1, 2, 3) and skip_to != example_key:
                target_stage = {1: LessonStage.H322_EXAMPLE_1, 2: LessonStage.H322_EXAMPLE_2, 3: LessonStage.H322_EXAMPLE_3}[skip_to]
                target_intro = {1: H322_EXAMPLE_1_INTRO, 2: H322_EXAMPLE_2_INTRO, 3: H322_EXAMPLE_3_INTRO}[skip_to]
                self.stage = target_stage
                self._h322_example_subflags = set()
                viz = H322_MANDATORY_VIZ.get(target_stage)
                return LessonStep(stage=self.stage.value,
                                  message=f"好的，跳到例 {skip_to}：\n\n" + target_intro,
                                  canvas_action=viz)
            ack = (protocol.get("ack_text") or "")[:200]
            if not ack:
                ack = "（继续作答）"
            if protocol.get("diagnosis") == "correct" and protocol.get("advance"):
                # 协议判 advance 但诊断器没命中 → 标 phase required flag 防卡循环
                hit = protocol.get("hit_goal")
                if hit:
                    implies = config["implies"].get(hit, set())
                    subflags |= implies
                    self._h322_example_subflags = subflags
                    if done_fn(subflags):
                        return self._h322_advance_example(example_key)
                    # v3.49：subflags 更新后**必须重算 next_phase**，否则 ack 后又问已答的 phase
                    new_next = self._h322_find_next_unanswered_phase(example_key, subflags)
                    if new_next is not None:
                        next_phase = new_next
            # 用协议 ack + 下一 phase 提问（next_phase 已是更新后的值）
            phase_prompt = self._h322_example_phase_prompt(example_key, next_phase)
            return LessonStep(stage=self.stage.value, message=ack + "\n\n" + phase_prompt)

        # 5. Layer 3: deterministic
        return LessonStep(
            stage=self.stage.value,
            message=self._h322_example_phase_prompt(example_key, next_phase),
        )


    def _h322_example_phase_prompt(self, example_key, phase: str) -> str:
        """例题每 phase 的 hard-coded 提问文案。"""
        prompts = {
            (1, "ask_form"):        "**第 1 步**：把方程 $9y^2-16x^2=144$ 化为标准方程，判断焦点在哪个轴？",
            (1, "ask_ab"):          "**第 2 步**：从标准方程读出**实半轴长 $a$** 和**虚半轴长 $b$**。",
            (1, "ask_focus"):       "**第 3 步**：由 $c^2=a^2+b^2$ 求 $c$，写出**焦点坐标**。",
            (1, "ask_eccentricity"):"**第 4 步**：写出**离心率** $e=\\dfrac{c}{a}=?$",
            (1, "ask_asymptote"):   "**第 5 步**：写出**渐近线方程**。注意焦点在 y 轴时，渐近线是 $y=\\pm\\dfrac{a}{b}x$（不是 b/a！）",
            (2, "ask_relation"):    "**第 1 步**：根据题意，把「$M$ 到 $F$ 的距离」与「$M$ 到直线 $l$ 的距离」的**比值**写成等式。",
            (2, "ask_simplify"):    "**第 2 步**：把比值等式**两边平方并化简**，得到关于 $x, y$ 的方程。",
            (2, "ask_conclude"):    "**第 3 步**：把方程写成标准型，**结论**：M 的轨迹是什么图形？焦点在哪个轴？实轴长 / 虚轴长 是多少？",
            (3, "ask_line"):        "**第 1 步**：先求双曲线的**焦点坐标**（$c^2=a^2+b^2$），再用倾斜角 30° 和 $F_2$ 写出**直线方程**。",
            (3, "ask_intersect"):   "**第 2 步**：把直线方程代入双曲线方程，**消去 y**，得到 x 的二次方程；再解出 $x_1, x_2$。",
            (3, "ask_points"):      "**第 3 步**：把 $x_1, x_2$ 代回直线方程，求出 $A, B$ 两点的坐标。",
            (3, "ask_length"):      "**第 4 步**：用距离公式 $|AB|=\\sqrt{(x_1-x_2)^2+(y_1-y_2)^2}$ 算出 $|AB|$。",
        }
        return prompts.get((example_key, phase), "请继续。")

    # ---- 跨 stage 跳级 ----


    def _handle_h322_intro(self, text: str) -> LessonStep:
        """1. 开场。学生回忆 3.1.2 椭圆几何性质 5 维（范围/对称/顶点/轴/离心率）任意 ≥2 个即推进 RANGE。"""
        # v3.51 同源修复：用 _h322_normalize_text 兜空格/全角/LaTeX
        t = self._h322_normalize_text(text)
        kws = ["范围", "对称", "顶点", "长轴", "短轴", "离心率", "e=c/a", "焦点", "性质"]
        hits = sum(1 for kw in kws if kw in t)
        if hits >= 2:
            self.stage = LessonStage.H322_RANGE
            viz = H322_MANDATORY_VIZ.get(LessonStage.H322_RANGE)
            return LessonStep(
                stage=self.stage.value,
                message=(
                    "✅ 没错！3.1.2 我们研究了**范围、对称性、顶点、离心率**这些方面。\n\n"
                    "现在我们用**同样的方法**来研究双曲线 $\\dfrac{x^2}{a^2}-\\dfrac{y^2}{b^2}=1\\,(a>0, b>0)$。\n\n"
                    "**第一步 · 范围**：你能从方程出发，推一下 $x$ 和 $y$ 的取值范围吗？"
                ),
                canvas_action=viz,
            )
        # 不命中 → 提示
        return LessonStep(
            stage=self.stage.value,
            message=(
                "提示一下：3.1.2 椭圆几何性质我们研究了几个方面 —— 比如**范围**（x、y 的取值）、"
                "**对称性**、**顶点**、**离心率** 等。你还记得吗？"
            ),
        )


    def _handle_h322_range(self, text: str) -> LessonStep:
        """2. 范围阶段：v3.46 partial-aware 累积式推进。

        学生可分两次答（先 x 再 y / 先 y 再 x），任一命中累积对应 sub_flag，
        两个都齐才推进到 SYMMETRY。
        """
        t = self._h322_normalize_text(text)
        # 初始化 subflags
        if not hasattr(self, "_h322_range_subflags"):
            self._h322_range_subflags = set()
        subflags = self._h322_range_subflags

        has_x = any(kw in t for kw in [
            "|x|≥a", "|x|>=a", "x≥a", "x>=a", "x≤-a", "x<=-a", "x>a", "x<-a",
            "x大于等于a", "x大于等于α", "x小于等于-a", "x>=a或", "x≥a或", "x≥a或x≤-a", "x≤-a或x≥a",
        ])
        has_y = any(kw in t for kw in [
            "y∈R", "y∈ℝ", "y任意", "y所有", "y为任意", "y的范围是R",
            "y∈实数", "y属于R", "y属于实数", "无界", "无穷", "yR",
            "yIS R", "yisR", "y可以取任意", "y可以是任意",
            "y是任意", "y为实数", "y是实数", "y是任意实数", "y为任意实数",
        ])
        # 宽松回退：含 y + (任意/实数/全部/无限制) 任一搭配
        # v3.51 同源修复：用 t（已归一去空格）兜"任意 实数"等带空格写法
        if not has_y and ("y" in t.lower()):
            if any(kw in t for kw in ["任意实数", "全体实数", "所有实数", "任意的实数",
                                       "任意值", "没限制", "没有限制", "不受限", "无限制"]):
                has_y = True

        if has_x:
            subflags.add("x_done")
        if has_y:
            subflags.add("y_done")
        self._h322_range_subflags = subflags

        # 两个都齐 → 推进
        if "x_done" in subflags and "y_done" in subflags:
            # 重置，避免污染下一课
            self._h322_range_subflags = set()
            self.stage = LessonStage.H322_SYMMETRY
            viz = H322_MANDATORY_VIZ.get(LessonStage.H322_SYMMETRY)
            return LessonStep(
                stage=self.stage.value,
                message=(
                    "✅ 完全正确！双曲线上 $|x|\\ge a$、$y\\in\\mathbb{R}$，所以双曲线**位于两条直线 $x=\\pm a$ 外侧**，向 y 方向无限延展。\n\n"
                    "**下一步 · 对称性**：把方程里的 $x$ 换成 $-x$，方程变不变？这说明双曲线关于什么对称？"
                ),
                canvas_action=viz,
            )

        # 只命中 x → 追问 y
        if "x_done" in subflags and "y_done" not in subflags:
            return LessonStep(
                stage=self.stage.value,
                message=(
                    "✅ $x$ 的范围对了：$x\\ge a$ 或 $x\\le -a$（即 $|x|\\ge a$）。\n\n"
                    "**还差 $y$ 的范围**：方程里 $y$ 有没有受限制？$y$ 的取值范围是？"
                ),
            )

        # 只命中 y → 追问 x
        if "y_done" in subflags and "x_done" not in subflags:
            return LessonStep(
                stage=self.stage.value,
                message=(
                    "✅ $y\\in\\mathbb{R}$ 对了。\n\n"
                    "**还差 $x$ 的范围**：由 $\\dfrac{x^2}{a^2}=1+\\dfrac{y^2}{b^2}\\ge 1$，可以推出 $x$ 的范围是什么？"
                ),
            )

        # 都没命中 → 通用提示
        return LessonStep(
            stage=self.stage.value,
            message=(
                "由方程 $\\dfrac{x^2}{a^2}-\\dfrac{y^2}{b^2}=1$ 移项：$\\dfrac{x^2}{a^2}=1+\\dfrac{y^2}{b^2}\\ge 1$，"
                "所以 $x^2\\ge a^2$，即 $|x|\\ge a$。你能从这个不等式说出 $x$ **和** $y$ 的范围吗？（两个都要说）"
            ),
        )


    def _handle_h322_symmetry(self, text: str) -> LessonStep:
        """3. 对称性阶段：v3.46 partial-aware 累积式 + v3.47 加 solved viz 过渡确认。

        学生分次答 y轴/x轴/原点，累积 ≥2 种 → 切 solved viz（4 镜像伙伴动画）+
        标记 awaiting_next 等学生说"好的"再进 VERTICES_AXES（与 e312 同模式）。
        """
        t = self._h322_normalize_text(text)
        if not hasattr(self, "_h322_sym_subflags"):
            self._h322_sym_subflags = set()
        subflags = self._h322_sym_subflags

        # awaiting_next 状态：已发 solved viz，等学生确认进 VERTICES_AXES
        if getattr(self, "_h322_sym_awaiting_next", False):
            t_ready = t
            is_ready = any(kw in t_ready for kw in [
                "好", "好的", "ok", "OK", "可以", "继续", "下一", "准备", "明白了", "懂了",
            ])
            if is_ready:
                self._h322_sym_awaiting_next = False
                self.stage = LessonStage.H322_VERTICES_AXES
                viz = H322_MANDATORY_VIZ.get(LessonStage.H322_VERTICES_AXES)
                return LessonStep(
                    stage=self.stage.value,
                    message=(
                        "👀 **下一步 · 顶点**：右边沙盒里画了 8 个候选点，你**点出**所有在双曲线上的"
                        "「类似椭圆顶点」的特殊点。（提示：可能没你想的那么多！）"
                    ),
                    canvas_action=viz,
                )
            # 学生没说继续 → 让他先看 solved viz 中的 3 个对称伙伴
            return LessonStep(
                stage=self.stage.value,
                message=(
                    "👀 右边图里你可以**拖动点 P**，看 3 个对称伙伴（$P'_x$ 蓝、$P'_y$ 绿、$P'_O$ 紫）"
                    "同步联动 —— 这就是双曲线 3 重对称的可视化。\n\n"
                    "玩够了回个「**好的**」/「**继续**」，进入下一步 · 顶点探究 📍。"
                ),
            )

        if any(kw in t for kw in ["y轴", "Y轴", "纵轴"]):
            subflags.add("y_axis")
        if any(kw in t for kw in ["x轴", "X轴", "横轴"]):
            subflags.add("x_axis")
        if "原点" in t or "中心对称" in t:
            subflags.add("origin")
        self._h322_sym_subflags = subflags

        # 至少 2 种对称答出 → 先发 solved viz（4 镜像伙伴），等学生确认
        if len(subflags) >= 2:
            self._h322_sym_subflags = set()      # 重置 subflags
            self._h322_sym_awaiting_next = True  # 进入 awaiting_next 状态
            return LessonStep(
                stage=self.stage.value,         # 不切 stage，留在 SYMMETRY
                message=(
                    "✅ 没错。双曲线关于 **x 轴、y 轴、原点**都对称。\n"
                    "x 轴和 y 轴是**对称轴**，原点是**对称中心**（即双曲线的**中心**）。\n\n"
                    "👀 右边图切到了**对称伙伴**视图：拖动点 P，看 3 个伙伴（$P'_x, P'_y, P'_O$）同步联动。\n\n"
                    "玩够了回个「**好的**」/「**继续**」，进入下一步 · 顶点探究 📍。"
                ),
                canvas_action={"action": "show_h322_symmetry_solved"},
            )

        # 命中 1 个 → 追问其他
        if len(subflags) == 1:
            answered = next(iter(subflags))
            ack_map = {"y_axis": "y 轴", "x_axis": "x 轴", "origin": "原点"}
            remain = [n for k, n in ack_map.items() if k not in subflags]
            return LessonStep(
                stage=self.stage.value,
                message=(
                    f"✅ 双曲线关于 **{ack_map[answered]}** 对称（确实是这样）。\n\n"
                    f"**还能想到吗**？把 $x$ 换成 $-x$、把 $x, y$ 同时换成 $-x, -y$ 等，"
                    f"双曲线还可能关于 **{remain[0]}** 或 **{remain[1] if len(remain)>1 else ''}** 对称吗？"
                ),
            )

        # 都没命中
        return LessonStep(
            stage=self.stage.value,
            message=(
                "把 $x$ 换成 $-x$、$y$ 换成 $-y$、再两个都换，看看方程是否不变。"
                "由此说说双曲线关于哪些线 / 点对称？（提示：至少有 x 轴、y 轴、原点三个对称对象）"
            ),
        )


    def _handle_h322_vertices_axes(self, text: str) -> LessonStep:
        """4. 顶点+实/虚轴阶段：v3.46 phase 拆分 + 前端点击事件累积。

        phase: vertex_compute（前端 h322_vertex_clicked 事件累积驱动）→ axes_name（术语文本）
        """
        phase = getattr(self, "_h322_vertices_phase", "vertex_compute")
        t = text
        t_clean = t.replace(" ", "")

        # phase 1: vertex_compute —— 学生未点击/未答清
        if phase == "vertex_compute":
            # 文字答出关键内容 → 直接跳过点击进 axes_name
            said_two = any(kw in t_clean for kw in [
                "只有2个", "只有两个", "2个顶点", "两个顶点",
                "顶点只有2", "顶点只有两", "只2个", "仅2个"])
            said_coords = any(kw in t_clean for kw in [
                "A1(-a,0)", "A2(a,0)", "(-a,0)", "(a,0)", "(±a,0)", "A1A2"])
            if said_two or said_coords:
                self._h322_vertices_phase = "axes_name"
                return LessonStep(
                    stage=self.stage.value,
                    message=(
                        "✅ 没错！双曲线顶点**只有 2 个**：$A_1(-a, 0), A_2(a, 0)$"
                        "（令 $x=0$ 方程无实数解 → 与 y 轴无交点）。\n\n"
                        "**下一步 · 术语**：教材把线段 $A_1A_2$ 叫做**实轴**（长 $=2a$），"
                        "$B_1(0,-b), B_2(0,b)$ 连成的线段叫**虚轴**（长 $=2b$）。\n\n"
                        "请你**复述**一下：线段 $A_1A_2$ 叫什么？$B_1B_2$ 叫什么？"
                    ),
                    canvas_action={"action": "show_h322_vertices_solved"},
                )
            # 否则提示去右边沙盒点击
            hits = len(getattr(self, "_h322_vertices_correct_hits", set()))
            if hits == 0:
                return LessonStep(
                    stage=self.stage.value,
                    message=(
                        "👉 请到**右边沙盒**点击你认为是双曲线顶点的点（候选 8 个）。\n\n"
                        "提示：让 $y=0$ 代入方程，$x$ 取哪些值？再让 $x=0$，$y$ 有没有实数解？"
                    ),
                )
            if hits == 1:
                return LessonStep(
                    stage=self.stage.value,
                    message="你已经点中 **1 个**真顶点（绿色）。再找找看，**还有一个**真顶点在哪里？",
                )
            # hits 已 ≥2 但 phase 还没切（理论上不会发生，但保险）
            self._h322_vertices_phase = "axes_name"
            return LessonStep(
                stage=self.stage.value,
                message="✅ 你已经点中了两个真顶点。线段 $A_1A_2$ 叫什么？$B_1B_2$ 叫什么？",
                canvas_action={"action": "show_h322_vertices_solved_with_rect"},
            )

        # phase 2: axes_name —— 检查实/虚轴术语
        if phase == "axes_name":
            has_real = "实轴" in t
            has_imag = "虚轴" in t
            if has_real and has_imag:
                self._h322_vertices_phase = "vertex_compute"  # 重置
                self.stage = LessonStage.H322_ASYMPTOTE
                viz = H322_MANDATORY_VIZ.get(LessonStage.H322_ASYMPTOTE)
                return LessonStep(
                    stage=self.stage.value,
                    message=(
                        "✅ 完全正确！\n\n"
                        "- 线段 $A_1A_2$ 叫**实轴**，长 $=2a$；$a$ 是**实半轴长**\n"
                        "- 线段 $B_1B_2$ 叫**虚轴**，长 $=2b$；$b$ 是**虚半轴长**\n"
                        "- 注意：$B_1, B_2$ **不在双曲线上**，但它们决定了虚轴\n\n"
                        "**下一步 · 渐近线 探究**（教材 p122 图 3.2-9）：\n\n"
                        "利用信息技术画出双曲线 $\\dfrac{x^2}{9}-\\dfrac{y^2}{4}=1$ 和两条直线 "
                        "$\\dfrac{x}{3}\\pm\\dfrac{y}{2}=0$。"
                        "在双曲线的**右支**上取一点 $M$，**测量** $M$ 的横坐标 $x_M$ 以及它到直线 "
                        "$\\dfrac{x}{3}-\\dfrac{y}{2}=0$ 的距离 $d$。\n\n"
                        "👉 **沿曲线向右上方拖动点 $M$**，观察 $x_M$ 与 $d$ 的大小关系，**你发现了什么？**"
                    ),
                    canvas_action=viz,
                )
            if has_real and not has_imag:
                return LessonStep(
                    stage=self.stage.value,
                    message="✅ $A_1A_2$ 叫**实轴**对了。还差 $B_1B_2$ 叫什么？（提示：与实相对的概念）",
                )
            if has_imag and not has_real:
                return LessonStep(
                    stage=self.stage.value,
                    message="✅ $B_1B_2$ 叫**虚轴**对了。还差 $A_1A_2$ 叫什么？（提示：与虚相对的概念）",
                )
            return LessonStep(
                stage=self.stage.value,
                message="教材里把 $A_1A_2$ 和 $B_1B_2$ 各起了一个名字 —— 一个叫**实**轴，一个叫**虚**轴。你能对应一下吗？",
            )

        return LessonStep(stage=self.stage.value, message="请继续。")


    def _handle_h322_asymptote(self, text: str) -> LessonStep:
        """5. 渐近线阶段：v3.47 按教材 p122-123 探究路径设计（2 phase）。

        教材路径：
          phase 1: explore_concrete —— 具体双曲线 x²/9-y²/4=1 拖点 M 感知 x_M↑→d↓ 但 d≠0
          phase 2: generalize_equation —— 推广 y=±(2/3)x 到一般 y=±(b/a)x + 命名渐近线

        架构：deterministic 关键词命中优先；不命中时尝试角色 3 方案 B 协议兜底（无 LLM 时降级）。
        """
        t = self._h322_normalize_text(text)
        if not hasattr(self, "_h322_asymptote_phase"):
            self._h322_asymptote_phase = "explore_concrete"
        phase = self._h322_asymptote_phase

        # ── phase 1: explore_concrete 拖点感知"接近不相交"（partial-aware 累积）──
        if phase == "explore_concrete":
            # 初始化 sub-flag 累积器
            if not hasattr(self, "_h322_asymptote_explore_subflags"):
                self._h322_asymptote_explore_subflags = set()
            sub = self._h322_asymptote_explore_subflags

            close_kw_hit = any(kw in t for kw in [
                "接近", "无限接近", "趋近", "越来越近", "越来越小", "d越来越小",
                "趋于0", "趋向0", "趋于零", "靠近", "贴近", "d越小",
            ])
            not_zero_kw_hit = any(kw in t for kw in [
                "不为0", "不等于0", "不会等于0", "不会为0", "不能等于0", "不到0",
                "永远不", "始终不", "不为零", "不等于零",
                "不相交", "不交", "不会碰", "碰不到", "不会相交", "d≠0",
            ])
            if close_kw_hit:
                sub.add("close_done")
            if not_zero_kw_hit:
                sub.add("not_zero_done")
            self._h322_asymptote_explore_subflags = sub

            has_close = "close_done" in sub
            has_not_zero = "not_zero_done" in sub
            if has_close and has_not_zero:
                # 重置 sub-flags
                self._h322_asymptote_explore_subflags = set()
                self._h322_asymptote_phase = "generalize_equation"
                return LessonStep(
                    stage=self.stage.value,
                    message=(
                        "✅ **完全正确**！这正是教材的发现 ——\n"
                        "「**$x_M$ 越大 → $d$ 越小，但 $d$ 始终 $\\ne 0$**」\n"
                        "也就是：双曲线**无限接近**两条直线，**但永远不相交**。\n\n"
                        "**phase 2 · 推广**：刚才的具体例子里两条直线是 $\\dfrac{x}{3}\\pm\\dfrac{y}{2}=0$，"
                        "也就是 $y=\\pm\\dfrac{2}{3}x$。\n"
                        "注意到 $a=3, b=2$，所以 $\\dfrac{2}{3}=\\dfrac{b}{a}$。\n\n"
                        "那对一般的双曲线 $\\dfrac{x^2}{a^2}-\\dfrac{y^2}{b^2}=1$，这两条「无限接近不相交」的直线方程是？"
                    ),
                    canvas_action={"action": "show_h322_asymptote_generalize"},
                )
            # 只命中 close 没 not_zero（学生只发现一半）
            if has_close and not has_not_zero:
                return LessonStep(
                    stage=self.stage.value,
                    message=(
                        "✅ 没错，$x_M$ 越大时 $d$ 越来越小。\n\n"
                        "**关键问题**：继续拖 M 往右上方，$d$ 会**等于 0** 吗？换句话说，双曲线和直线会**相交**吗？"
                    ),
                )
            if has_not_zero and not has_close:
                return LessonStep(
                    stage=self.stage.value,
                    message=(
                        "✅ 对，双曲线不会和直线相交。\n\n"
                        "**还有另一半**：$x_M$ 越大时，$d$ 是变大还是变小？继续拖 M 观察。"
                    ),
                )
            # 协议兜底（LLM 没 key 时返回 None）
            protocol = self._llm_h322_asymptote_action_protocol(text, "explore_concrete")
            if self._h322_proto_b_advance(protocol):
                self._h322_asymptote_phase = "generalize_equation"
                soc = (protocol.get("socratic_text") or "")[:400]
                return LessonStep(
                    stage=self.stage.value,
                    message=(soc + "\n\n" if soc else "") +
                            "**phase 2 · 推广**：具体的 $y=\\pm\\dfrac{2}{3}x$ 对一般 $a, b$ 该写成什么？",
                    canvas_action={"action": "show_h322_asymptote_generalize"},
                )
            soc = (protocol.get("socratic_text") or "")[:400] if protocol else ""
            return LessonStep(
                stage=self.stage.value,
                message=soc or (
                    "👉 请到**右边沙盒**拖动点 M（在双曲线右支上），看着上方实时显示的 $x_M$ 和 $d$：\n\n"
                    "  · $x_M$ 越来越大时，$d$ 是变大还是变小？\n"
                    "  · $d$ 最后会**等于 0** 吗？\n\n"
                    "用自己的话总结一下你的观察。"
                ),
            )

        # ── phase 2: generalize_equation 推广到一般式 ──
        if phase == "generalize_equation":
            has_general = (("b/a" in t and "y=" in t) or "y=bx/a" in t or "y=b/a*x" in t
                          or "(b/a)x" in t)
            has_double = ("±" in t) or ("正负" in t) or ("-b/a" in t and "b/a" in t)
            if has_general and has_double:
                # 完成 → 推进 EQUILATERAL
                self._h322_asymptote_phase = "explore_concrete"  # 重置
                self.stage = LessonStage.H322_EQUILATERAL
                viz = H322_MANDATORY_VIZ.get(LessonStage.H322_EQUILATERAL)
                return LessonStep(
                    stage=self.stage.value,
                    message=(
                        "✅ **完全正确**！一般情形下，双曲线 $\\dfrac{x^2}{a^2}-\\dfrac{y^2}{b^2}=1$ 的两条「无限接近不相交」直线方程是\n\n"
                        "$$y=\\pm\\dfrac{b}{a}x$$\n\n"
                        "教材把这两条直线叫做双曲线的**渐近线**（asymptote）。\n\n"
                        "（推广路径：过 $A_1, A_2$ 作 $x=\\pm a$、过 $B_1, B_2$ 作 $y=\\pm b$，四线围成矩形，两条对角线方程正是 $y=\\pm\\dfrac{b}{a}x$。）\n\n"
                        "**下一步 · 等轴双曲线**：如果 $a=b$，方程变成什么？渐近线又变成什么？"
                    ),
                    canvas_action=viz,
                )
            # 学生答了具体 y=±(2/3)x 但没推广到一般式
            if "2/3" in t and "y=" in t:
                return LessonStep(
                    stage=self.stage.value,
                    message=(
                        "✅ 具体例子里确实是 $y=\\pm\\dfrac{2}{3}x$。\n\n"
                        "**再往前一步**：注意到 $a=3, b=2$，所以 $\\dfrac{2}{3}=\\dfrac{b}{a}$。\n"
                        "把这个比值换成一般的 $\\dfrac{b}{a}$，对任意双曲线，渐近线方程是？"
                    ),
                )
            # 协议兜底
            protocol = self._llm_h322_asymptote_action_protocol(text, "generalize_equation")
            if self._h322_proto_b_advance(protocol):
                self._h322_asymptote_phase = "explore_concrete"
                self.stage = LessonStage.H322_EQUILATERAL
                viz = H322_MANDATORY_VIZ.get(LessonStage.H322_EQUILATERAL)
                soc = (protocol.get("socratic_text") or "")[:400]
                return LessonStep(
                    stage=self.stage.value,
                    message=(soc + "\n\n" if soc else "") +
                            "**下一步 · 等轴双曲线**：如果 $a=b$，方程变成什么？渐近线又变成什么？",
                    canvas_action=viz,
                )
            soc = (protocol.get("socratic_text") or "")[:400] if protocol else ""
            return LessonStep(
                stage=self.stage.value,
                message=soc or (
                    "刚才的具体例子里两条直线是 $y=\\pm\\dfrac{2}{3}x$（因为 $a=3, b=2$，$\\dfrac{2}{3}=\\dfrac{b}{a}$）。\n\n"
                    "**推广到一般情形**：对双曲线 $\\dfrac{x^2}{a^2}-\\dfrac{y^2}{b^2}=1$，这两条渐近线方程写成 $y=\\pm\\dfrac{?}{?}x$ ？"
                ),
            )

        return LessonStep(stage=self.stage.value, message="请继续。")


    def _handle_h322_equilateral(self, text: str) -> LessonStep:
        """6. 等轴双曲线阶段 stub。"""
        t = self._h322_normalize_text(text)
        has_eq = any(kw in t for kw in ["x²-y²=a²", "x^2-y^2=a^2", "x2-y2=a2"])
        has_asy = ("y=±x" in t or "y=x" in t or "y=-x" in t or "y=x和y=-x" in t)
        if has_eq or has_asy:
            self.stage = LessonStage.H322_ECCENTRICITY
            viz = H322_MANDATORY_VIZ.get(LessonStage.H322_ECCENTRICITY)
            return LessonStep(
                stage=self.stage.value,
                message=(
                    "✅ 完全正确！$a=b$ 时方程变为 $x^2-y^2=a^2$，渐近线 $y=\\pm x$（**互相垂直**），"
                    "我们把它叫做**等轴双曲线**。\n\n"
                    "**下一步 · 离心率**：先回忆一下，**椭圆的离心率怎么定义**的？"
                ),
                canvas_action=viz,
            )
        return LessonStep(
            stage=self.stage.value,
            message=(
                "把 $b=a$ 代入双曲线方程 $\\dfrac{x^2}{a^2}-\\dfrac{y^2}{b^2}=1$ 试试 —— 方程化简成什么？"
                "再把 $b=a$ 代入渐近线 $y=\\pm\\dfrac{b}{a}x$，得到什么？"
            ),
        )

    @staticmethod

    def _handle_h322_eccentricity(self, text: str) -> LessonStep:
        """7. 离心率阶段：v3.46 5 phase + 协议兜底 + slider 体验。

        phases: recall_e → range_e → geometry → slider_experience → link_asymptote
        """
        t = self._h322_norm_ecc(text)
        if not hasattr(self, "_h322_ecc_phase"):
            self._h322_ecc_phase = "recall_e"
        if not hasattr(self, "_h322_ecc_geometry_misses"):
            self._h322_ecc_geometry_misses = 0
        phase = self._h322_ecc_phase

        # ── phase 1: recall_e ──
        if phase == "recall_e":
            # 兼容多种写法：e=c/a / c/a / \dfrac{c}{a} / \frac{c}{a} / 全角等号 / 中文斜杠
            if any(kw in t for kw in ["e=c/a", "c/a", "离心率=c/a", "离心率是c/a", "比值c/a"]):
                self._h322_ecc_phase = "range_e"
                return LessonStep(
                    stage=self.stage.value,
                    message=(
                        "✅ 椭圆离心率 $e=\\dfrac{c}{a}$。\n\n"
                        "**phase 2**：双曲线沿用同样的定义 $e=\\dfrac{c}{a}$。"
                        "在双曲线中 $c$ 和 $a$ 谁大？所以 $e$ 的**范围**是？"
                    ),
                )
            return LessonStep(
                stage=self.stage.value,
                message="先回忆一下：3.1.2 节我们把**椭圆的离心率**定义为什么？写出公式。",
            )

        # ── phase 2: range_e ──
        if phase == "range_e":
            if any(kw in t for kw in ["e>1", "e大于1", "大于1", "c>a"]):
                self._h322_ecc_phase = "geometry"
                return LessonStep(
                    stage=self.stage.value,
                    message=(
                        "✅ 因为 $c>a>0$，所以 $e=\\dfrac{c}{a}>1$（与椭圆 $0<e<1$ **互补**）。\n\n"
                        "**phase 3**：e 越大，双曲线的**形状**会怎样变？（用你自己的话描述）"
                    ),
                )
            return LessonStep(
                stage=self.stage.value,
                message="双曲线里 $c$ 和 $a$ 比较谁大？由此推出 $e=\\dfrac{c}{a}$ 的**范围**。",
            )

        # ── phase 3: geometry（口述张口大小）──
        if phase == "geometry":
            # v3.51 同源修复：用 t（_h322_normalize_text 后）兜空格
            has_open_word = any(kw in t for kw in ["越大", "越张", "张口", "开口", "越宽", "越张开"])
            if has_open_word:
                # 推进到 slider 体验 phase —— **此时才显式发 slider viz**（不再依赖入口 mandatory）
                self._h322_ecc_phase = "slider_experience"
                return LessonStep(
                    stage=self.stage.value,
                    message=(
                        "✅ 没错，e 越大开口越张。\n\n"
                        "**phase 4**：右边主板上有 e 的**滑块**（e 从 1 → ∞）。"
                        "拖一拖**亲自感受**：e=1.1 / 1.5 / 2 / 5 时形状的变化。\n\n"
                        "（拖完后，告诉我一句话感受。）"
                    ),
                    canvas_action={"action": "show_h322_e_slider"},
                )
            # 卡 ≥2 turn → 主动 fallback 到 slider 让学生体验
            self._h322_ecc_geometry_misses += 1
            if self._h322_ecc_geometry_misses >= 2:
                self._h322_ecc_phase = "slider_experience"
                return LessonStep(
                    stage=self.stage.value,
                    message=(
                        "没关系，我们换个方式看一看 🎚️\n\n"
                        "右边主板上有 e 的**滑块**。拖一拖，看 e=1.1 → 1.5 → 2 → 5 时双曲线开口的变化。"
                        "拖完后，**用你自己的话**告诉我观察到了什么。"
                    ),
                    canvas_action={"action": "show_h322_e_slider"},
                )
            return LessonStep(
                stage=self.stage.value,
                message="提示：固定 $a$，让 $c$ 变大（$e=\\dfrac{c}{a}$ 也变大），双曲线开口会越来越…？",
            )

        # ── phase 4: slider_experience（拖滑块 + 口头总结）──
        if phase == "slider_experience":
            # v3.51 同源修复：用 t（_h322_normalize_text 后）兜空格
            has_summary = any(kw in t for kw in ["越大", "越张", "越宽", "越接近1", "越窄", "开口"])
            if has_summary:
                self._h322_ecc_phase = "link_asymptote"
                return LessonStep(
                    stage=self.stage.value,
                    message=(
                        "✅ 总结到位。e 越大开口越张，e 越接近 1 双曲线越"
                        "「窄」（两支几乎贴着实轴方向）。\n\n"
                        "**phase 5**（教材思考栏）：由 $c^2=a^2+b^2$，"
                        "试着推一下 $\\dfrac{b}{a}$ 和 $e$ 的**关系**。"
                    ),
                )
            return LessonStep(
                stage=self.stage.value,
                message="**先拖一拖** e 的滑块（试 1.1 / 1.5 / 2 / 5），然后用一句话总结 e 与开口的关系。",
            )

        # ── phase 5: link_asymptote ──
        if phase == "link_asymptote":
            # t 已被 _h322_norm_ecc 归一化（去空格 / 全角等号 / LaTeX 分数）
            has_link = (
                "√(e²-1)" in t or "sqrt(e^2-1)" in t or "sqrt(e²-1)" in t
                or "b/a=" in t or "e^2-1" in t or "e²-1" in t
                or "\\sqrt{e^2-1}" in t or "\\sqrt(e^2-1)" in t
                or ("b/a" in t and ("sqrt" in t or "√" in t or "^2" in t))
            )
            if has_link:
                # 完成全 stage → 推进 EXAMPLE_1
                self._h322_ecc_phase = "recall_e"  # 重置
                self.stage = LessonStage.H322_EXAMPLE_1
                viz = H322_MANDATORY_VIZ.get(LessonStage.H322_EXAMPLE_1)
                return LessonStep(
                    stage=self.stage.value,
                    message=(
                        "✅ 完美！由 $e^2=\\dfrac{c^2}{a^2}=\\dfrac{a^2+b^2}{a^2}=1+\\dfrac{b^2}{a^2}$，"
                        "推出 $\\dfrac{b}{a}=\\sqrt{e^2-1}$。\n\n"
                        "→ e 越大 → 渐近线斜率 $b/a$ 越大 → 开口越张。\n\n"
                        "现在我们做 3 道例题巩固一下。\n\n" + H322_EXAMPLE_1_INTRO
                    ),
                    canvas_action=viz,
                )
            return LessonStep(
                stage=self.stage.value,
                message=(
                    "提示：在双曲线中 $c^2=a^2+b^2$，两边都除以 $a^2$ → "
                    "$\\dfrac{c^2}{a^2}=1+\\dfrac{b^2}{a^2}$，左边是 $e^2$，所以 $\\dfrac{b^2}{a^2}=?$"
                ),
            )

        return LessonStep(stage=self.stage.value, message="请继续。")


    def _handle_h322_example(self, text: str, example_num: int) -> LessonStep:
        """8/9/10. 例题阶段：v3.46 311-style 三层防御。委托给 generic handler。"""
        return self._handle_h322_example_generic(text, example_key=example_num)


    def _handle_h322_summary(self, text: str) -> LessonStep:
        """11. 总结。deterministic 结课逻辑。"""
        self.summary_turns += 1
        if _looks_like_lesson_end(text) or self.summary_turns >= 6:
            self.lesson_ended = True
            return LessonStep(
                stage=self.stage.value,
                message=(
                    "👏 恭喜完成 3.2.2 课程！\n\n"
                    "椭圆与双曲线两章已学完。下一节（3.3）我们将进入**抛物线**——"
                    "圆锥曲线第三种、也是离心率 $e=1$ 的临界情形。\n\n"
                    "[LESSON_END]"
                ),
            )
        return LessonStep(
            stage=self.stage.value,
            message="还有什么问题想问？或者输入「结束」结课。",
        )

    # ================================================================
    # ---- 抛物线 3.3.1 课（v3.x 新增 12 stage）handler 集 ----
    # 仿 H321 (3.2.1) 模板：12 stage + 例题三层防御 + awaiting_next + partial 累积 + 跨 stage 跳级
    # 例题内部编号 1/2 对应教材 p132 例 1/2（双向题 + 卫星天线）
    # ================================================================

    # ---- 短答阶段苏格拉底提示协议（角色 3 风格，只给提示不改状态）----

