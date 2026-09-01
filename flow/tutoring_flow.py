# -*- coding: utf-8 -*-
"""TutoringFlow: CrewAI Flow FSM 编排器。

将原 lesson_flow.py 12,000+ 行单体中的 E312 阶段分发逻辑，
重构为 CrewAI Flow 状态机 + 多 Crew 协作架构。

核心设计区别：
  · 原单体：_STAGE_DISPATCH → getattr(self, method_name)(text) 单一调度
  · 新架构：TutoringFlow(Flow[LessonState]) 持有结构化状态，
            按 stage 分发到对应 handler，LLM 调用委派给 Crews

状态管理：
  · self.state 是 LessonState（Pydantic 模型），所有运行时状态集中管理
  · 每个 handler 修改 self.state 的字段后返回 LessonStep dict

LLM 调用：
  · 教师回复：TeachingCrew.kickoff(...)
  · 同伴提问：FeynmanCrew.generate_peer_question(...)
  · 纠错反馈：CorrectionCrew.generate_correction(...)
  · 例题诊断：courses.example_diagnostician_312.diagnose_example_312(...)
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from crewai.flow.flow import Flow, start, listen, router

from flow.state import (
    E312Stage,
    LessonState,
    STAGE_MANDATORY_VIZ,
    next_e312_stage,
)
from crews.teaching_crew import TeachingCrew
from crews.feynman_crew import FeynmanCrew
from crews.correction_crew import CorrectionCrew


# ═══════════════════════════════════════════════════
# 确定性文案（deterministic messages）
# 从原 lesson_flow.py 提取，stage handler 直接引用
# ═══════════════════════════════════════════════════

E312_INTRO_MSG = (
    "欢迎来到 3.1.2 节 **椭圆的简单几何性质** 🌿\n\n"
    "上节课（3.1.1）我们由「**椭圆的定义**」推出了**标准方程** "
    "$\\dfrac{x^2}{a^2}+\\dfrac{y^2}{b^2}=1\\,(a>b>0)$。\n\n"
    "今天我们要做相反的事 ——\n"
    "**从已有的方程出发，反过来研究椭圆的几何性质**。\n\n"
    "先回顾一下：你还记得 $a$、$b$、$c$ 分别表示椭圆图形上的**哪条线段**吗？"
)

E312_RANGE_PREDICT_MSG = (
    "好的！我们正式开始研究椭圆的几何性质。\n\n"
    "**第一个问题：范围**\n"
    "椭圆是一条**封闭曲线**，它上面的点不可能跑得太远。\n"
    "看着方程 $\\dfrac{x^2}{a^2}+\\dfrac{y^2}{b^2}=1$，"
    "你**猜想** $x$ 和 $y$ 各自的取值范围是什么？"
)
E312_RANGE_DERIVE_MSG = (
    "猜得不错！我们来**用代数方法严格证明**。\n\n"
    "因为 $\\dfrac{x^2}{a^2}+\\dfrac{y^2}{b^2}=1$，而 $\\dfrac{y^2}{b^2}\\ge 0$，\n"
    "所以 $\\dfrac{x^2}{a^2}\\le 1$。**这个不等式告诉你 $x$ 的范围是？**"
)
E312_RANGE_DONE_MSG = (
    "完全正确 ✅：$-a\\le x\\le a$，$-b\\le y\\le b$。\n"
    "**几何意义**：椭圆完全被矩形 $[-a,a]\\times[-b,b]$ 框住。"
)

E312_SYMMETRY_Y_MSG = (
    "👀 **接下来研究对称性**。\n\n"
    "把方程 $\\dfrac{x^2}{a^2}+\\dfrac{y^2}{b^2}=1$ 中的 $x$ 换成 $-x$，方程会怎样？\n"
    "进一步：这说明椭圆关于**哪条轴**对称？"
)
E312_SYMMETRY_X_MSG = (
    "对，**关于 y 轴对称** ✅。\n\n"
    "类似地，把 $y$ 换成 $-y$，方程也不变 —— 这说明椭圆关于**哪条轴**对称？"
)
E312_SYMMETRY_O_MSG = (
    "**关于 x 轴对称** ✅。\n\n"
    "既然关于两条坐标轴都对称，把 $x$ 和 $y$ **同时**都换成相反数呢？\n"
    "这又说明椭圆关于**什么**对称？"
)
E312_SYMMETRY_DONE_MSG = (
    "完美 ✅：椭圆关于 **x 轴、y 轴、原点** 三重对称。\n"
    "数学上把 x 轴、y 轴叫**对称轴**，原点叫**对称中心**。"
)

E312_VERTICES_COMPUTE_MSG = (
    "🔍 **顶点探究**\n\n"
    "现在我们要找出椭圆上几个**特殊的点**。\n"
    "看方程 $\\dfrac{x^2}{a^2}+\\dfrac{y^2}{b^2}=1$：\n"
    "  · 令 $y=0$，得 $x=?$\n"
    "  · 令 $x=0$，得 $y=?$\n\n"
    "**右侧画布上有 8 个点**，请你点击你认为是「顶点」的点（**只点 4 个**）。"
)
E312_VERTICES_NAME_MSG = (
    "👏 全选对了！这四个点就是椭圆的 **顶点**。\n\n"
    "教材把它们规范命名为：\n"
    "  · 长轴上的两个顶点：$A_1(-a,0)$、$A_2(a,0)$\n"
    "  · 短轴上的两个顶点：$B_1(0,-b)$、$B_2(0,b)$\n\n"
    "**线段 $A_1A_2$ 叫长轴，长度 $|A_1A_2|=2a$；**\n"
    "**线段 $B_1B_2$ 叫短轴，长度 $|B_1B_2|=2b$**。\n\n"
    "记下这两个术语：**长轴 = 2a**，**短轴 = 2b**。下面我们进入今天的重点——**离心率**。"
)

E312_ECC_EXPLORE_C_MSG = (
    "⭐ **重点：离心率**\n\n"
    "我们已经知道椭圆有 $a$、$b$、$c$ 三个量。它们和椭圆的「**圆扁程度**」有什么关系？\n\n"
    "**第一组实验**（看右边沙盒）：固定 $a$ 不变，**改变 $c$**（焦距）。\n"
    "拖动滑块，观察椭圆变化。**$c$ 越大，椭圆变扁还是变圆**？"
)
E312_ECC_EXPLORE_A_MSG = (
    "很好 ✅ —— $c$ 越大椭圆**越扁**。\n\n"
    "**第二组实验**：现在反过来，固定 $c$ 不变，**改变 $a$**（长半轴）。\n"
    "**$a$ 越大，椭圆变扁还是变圆**？"
)
E312_ECC_INDUCE_MSG = (
    "✅ 你发现了：$a$ 越大椭圆**越圆**。\n\n"
    "也就是说：单看 $a$ 或单看 $c$ 都判断不了椭圆的圆扁——\n"
    "**它们要一起看**。你能想出一个**最简单的量**来同时反映 $a$ 和 $c$ 吗？\n"
    "（提示：和、差、积、商，哪一种最能反映「两者一起变化」的程度？）"
)
E312_ECC_DEFINE_MSG = (
    "完全正确 ✅ —— **比值** 才能同时反映 $a$ 和 $c$。\n\n"
    "**定义**：把比值 $\\dfrac{c}{a}$ 叫做椭圆的**离心率**，记作 $e$。\n"
    "$$e = \\dfrac{c}{a}$$\n"
    "记住这个定义。**回个「好」或「明白」**，我们就看 $e$ 是怎么反映椭圆形状的 👇"
)
E312_ECC_GEOMETRY_MSG = (
    "✅ 看右边的 **e 滑块** ——\n"
    "拖动它感受 $e$ 从小到大变化时，椭圆形状如何改变。\n\n"
    "**问题**：用一句话描述 $e$ 与椭圆形状的关系？"
)
E312_ECC_RANGE_MSG = (
    "✅ 漂亮总结：**e 越接近 1 越扁，e 越接近 0 越圆**。\n\n"
    "**最后一个问题**：椭圆里 $a>c>0$，所以 $e=\\dfrac{c}{a}$ 的**取值范围**是？\n"
    "更进一步想想：如果 **$a=b$** 时，由 $b^2=a^2-c^2$ 可知 $c=?$，那么 $e=?$\n"
    "此时椭圆会变成什么图形？"
)
E312_ECC_DONE_MSG = (
    "✅✅✅ 太棒了：**$0<e<1$**，且 $e=0$ 时椭圆变成圆 ——\n"
    "**圆是椭圆在 $e\\to 0$ 时的极限**。\n\n"
    "至此，椭圆 5 大几何性质（范围、对称性、顶点、长短轴、离心率）已全部学完。"
    "下面我们做 3 道经典例题来巩固。"
)

E312_EXAMPLE_1_INTRO = (
    "🟡 **例 1**（教材 p112）\n"
    "求椭圆 $16x^2+25y^2=400$ 的**长轴长、短轴长、离心率、焦点坐标、顶点坐标**。\n\n"
    "我们一项一项来。**先求长轴长 $2a$**：你能从方程读出 $a$，进而得到 $2a$ 吗？"
)
E312_EXAMPLE_2_INTRO = (
    "🟡 **例 2**（教材 p113 例 6）\n"
    "动点 $M(x,y)$ 与定点 $F(4,0)$ 的距离 和 $M$ 到定直线 $l:x=\\dfrac{25}{4}$ 的距离的比是常数 "
    "$\\dfrac{4}{5}$，求动点 $M$ 的轨迹。\n\n"
    "**第一步**：用集合或式子写出 $M$ 满足的**距离关系**。"
)
E312_EXAMPLE_3_INTRO = (
    "🟡 **例 3**（教材 p114 例 7）\n"
    "已知直线 $l:4x-5y+m=0$ 和椭圆 $C:\\dfrac{x^2}{25}+\\dfrac{y^2}{9}=1$。$m$ 为何值时:\n"
    "  (1) 直线与椭圆有 **两个公共点**？\n"
    "  (2) 有且**仅有 1 个公共点**？\n"
    "  (3) **没有公共点**？\n\n"
    "**先回答 (1)**：$m$ 在什么范围时，直线与椭圆有两个公共点？"
)
E312_SUMMARY_MSG = (
    "🎓 **3.1.2 总结**\n\n"
    "我们今天系统研究了椭圆的几何性质：\n"
    "  1. **范围**：$-a\\le x\\le a$，$-b\\le y\\le b$\n"
    "  2. **对称性**：关于 x 轴、y 轴、原点对称\n"
    "  3. **顶点**：4 个 $A_1A_2B_1B_2$；**长轴 $=2a$**、**短轴 $=2b$**\n"
    "  4. **离心率** $e=\\dfrac{c}{a}\\in(0,1)$：$e$ 越接近 1 越扁，越接近 0 越圆，$e=0$ 即圆\n"
    "  5. 三道例题：化方程定形状、用比例反推椭圆、直线与椭圆的位置关系\n\n"
    "**下一节（3.2.1）**：把『距离之和为常数』改成『距离之差为常数』——双曲线 🌀。"
)


# ═══════════════════════════════════════════════════
# LessonStep — handler 返回的结构化响应
# ═══════════════════════════════════════════════════

def _step(stage: str, message: str, canvas_action: Any = None,
          agent: str = "teacher", event_type: str = "normal") -> dict:
    """构建统一的 handler 返回结构。去除消息首尾空行。"""
    d = {
        "stage": stage,
        "message": message.strip() if message else "",
        "agent": agent,
        "event_type": event_type,
    }
    if canvas_action is not None:
        d["canvas_action"] = canvas_action
    return d


# ═══════════════════════════════════════════════════
# 关键词匹配函数（从原 lesson_flow.py 提取）
# ═══════════════════════════════════════════════════

# INTRO: abc recall
_ABC_KW_A = ["长半轴", "长轴的一半", "半长轴", "长轴", "a 是", "a=", "a 表示"]
_ABC_KW_B = ["短半轴", "短轴的一半", "半短轴", "短轴", "b 是", "b=", "b 表示"]
_ABC_KW_C = ["焦距的一半", "半焦距", "焦距", "c 是", "c=", "c 表示", "焦点"]


def _looks_like_abc_recall(text: str) -> bool:
    low = text.lower()
    hits = 0
    if any(kw.lower() in low for kw in _ABC_KW_A):
        hits += 1
    if any(kw.lower() in low for kw in _ABC_KW_B):
        hits += 1
    if any(kw.lower() in low for kw in _ABC_KW_C):
        hits += 1
    return hits >= 2


# RANGE: 范围识别
_RANGE_X_PAT = ["-a≤x≤a", "-a<=x<=a", "−a≤x≤a", "|x|≤a", "|x|<=a", "x∈[-a,a]"]
_RANGE_Y_PAT = ["-b≤y≤b", "-b<=y<=b", "−b≤y≤b", "|y|≤b", "|y|<=b", "y∈[-b,b]"]


def _looks_like_range_x(text: str) -> bool:
    t = text.replace(" ", "").replace("−", "-").replace("≤", "<=")
    return any(p.replace(" ", "").replace("−", "-").replace("≤", "<=") in t
               for p in _RANGE_X_PAT)


def _looks_like_range_y(text: str) -> bool:
    t = text.replace(" ", "").replace("−", "-").replace("≤", "<=")
    return any(p.replace(" ", "").replace("−", "-").replace("≤", "<=") in t
               for p in _RANGE_Y_PAT)


# SYMMETRY: 轴 / 原点
def _looks_like_y_axis_sym(t: str) -> bool:
    s = t.lower().replace(" ", "")
    return any(kw in s for kw in ["y轴对称", "关于y轴", "y-axis", "y轴", "纵轴"])


def _looks_like_x_axis_sym(t: str) -> bool:
    s = t.lower().replace(" ", "")
    return any(kw in s for kw in ["x轴对称", "关于x轴", "x-axis", "x轴", "横轴"])


def _looks_like_origin_sym(t: str) -> bool:
    s = t.replace(" ", "")
    return any(kw in s for kw in ["原点对称", "关于原点", "中心对称", "原点", "对称中心"])


# ECCENTRICITY
def _has_real_circle(t: str) -> bool:
    return "圆" in t and t.count("圆") > t.count("椭圆")


def _looks_like_flat(text: str) -> bool:
    t = text.replace(" ", "")
    has_flat = "扁" in t
    has_circ = _has_real_circle(t)
    if has_flat and not has_circ:
        return True
    if not has_flat and not has_circ:
        if "接近a" in t or "c接近a" in t or "c→a" in t:
            return True
    return False


def _looks_like_round(text: str) -> bool:
    t = text.replace(" ", "")
    return _has_real_circle(t) and "扁" not in t


def _looks_like_ratio(text: str) -> bool:
    t = text.lower().replace(" ", "")
    if any(kw in t for kw in ["比值", "c/a", "c比a", "ratio", "比例", "c÷a"]):
        return True
    if "c" in t and "a" in t and ("比" in t or "/" in t or "÷" in t or "除" in t):
        return True
    return False


def _looks_like_e_define(text: str) -> bool:
    t = text.lower().replace(" ", "")
    if "e=" in t and ("c/a" in t or "c÷a" in t):
        return True
    if "c/a" in t and ("e" in t or "离心率" in text):
        return True
    if "e" in t and "c" in t and "a" in t and any(c in t for c in "/÷比除"):
        return True
    return False


def _looks_like_e_shape_relation(text: str) -> bool:
    has_flat = "扁" in text
    has_round = "圆" in text
    if not (has_flat or has_round):
        return False
    t_ns = text.replace(" ", "")
    if "接近1" in t_ns or "e大" in t_ns or "接近0" in t_ns or "e小" in t_ns:
        return True
    if "e" in text.lower() and (has_flat or has_round):
        return True
    return False


def _looks_like_e_range_0_1(text: str) -> bool:
    t = text.replace(" ", "").replace("−", "-").replace("≤", "<=")
    if "0<e<1" in t or "0<=e<=1" in t or "(0,1)" in t:
        return True
    if "0" in t and "1" in t and "e" in t.lower() and ("<" in t or "之间" in text):
        return True
    return False


def _looks_like_e_zero_circle(text: str) -> bool:
    t = text.replace(" ", "")
    has_e0 = any(p in t for p in ["e=0", "e为0", "e等于0", "e→0", "e接近0"])
    if "圆" in t:
        only_ell = t.count("圆") == t.count("椭圆")
        has_circ = not only_ell
    else:
        has_circ = False
    return has_e0 or has_circ


# 通用：ready / understood / lesson_end / skip
def _looks_like_ready(text: str) -> bool:
    if _looks_like_understood(text):
        return True
    t_low = text.strip().lower()
    if any(kw in text for kw in [
        "准备好", "好了", "可以了", "走起", "来吧", "开始", "继续吧",
        "没问题", "没毛病", "可以的", "明白了", "懂了",
    ]):
        return True
    return t_low in (
        "好", "可以", "嗯", "行", "中", "成", "y", "yes",
        "ok", "okay", "k", "嗯嗯", "对", "对的", "搞定", "懂", "明白", "没事", "yep",
    )


def _looks_like_understood(text: str) -> bool:
    return any(kw in text for kw in [
        "懂了", "明白", "理解", "继续", "下一题", "下一个", "好的", "ok", "OK", "嗯",
    ])


def _looks_like_lesson_end(text: str) -> bool:
    return any(kw in text for kw in ["结束", "没了", "没问题", "谢谢", "再见", "下课"])


def _looks_like_skip_to_example(text: str) -> Optional[int]:
    t = text.replace(" ", "")
    if not any(kw in t for kw in ["直接", "跳到", "跳过", "看例", "进入例", "看第", "进入第"]):
        return None
    if "例1" in t or "例一" in t or "第一题" in t or "第1题" in t:
        return 1
    if "例2" in t or "例二" in t or "第二题" in t or "第2题" in t:
        return 2
    if "例3" in t or "例三" in t or "第三题" in t or "第3题" in t:
        return 3
    return None


# ── 例题 phase prompts ──
_EXAMPLE_PHASE_PROMPTS = {
    (4, "ask_minor_axis"):   "**那短轴长 $2b$ 呢？**",
    (4, "ask_eccentricity"): "**那离心率 $e$ 呢？**（提示：先求 $c$）",
    (4, "ask_focus"):        "**焦点坐标**是？（写成 $(x, y)$ 形式，两个焦点都写出来）",
    (4, "ask_vertex"):       "**4 个顶点坐标**是？（注意区分长轴和短轴上的顶点，用 $(x, y)$ 写）",
    (5, "ask_simplify"):     "**两边平方并化简**，得到的椭圆方程是？",
    (5, "ask_conclude"):     "✅ 化简正确。**结论**：$M$ 的轨迹是什么图形？**长轴、短轴**各多长？",
    (6, "ask_one_point"):    "**(2)** $m$ 为何值时直线与椭圆**有且仅有 1 个公共点**？（提示：$\\Delta=0$）",
    (6, "ask_no_point"):     "**(3)** $m$ 在什么范围时直线与椭圆**没有公共点**？（提示：$\\Delta<0$）",
}


# ═══════════════════════════════════════════════════
# Stage goal descriptions (for TeachingCrew LLM context)
# ═══════════════════════════════════════════════════

_STAGE_GOALS = {
    E312Stage.INTRO.value: "让学生回忆 a/b/c 几何含义。命中 >=2 即推进。",
    E312Stage.RANGE.value: "范围探究：predict 猜范围 → derive 严格推出 -a<=x<=a, -b<=y<=b。",
    E312Stage.SYMMETRY.value: "对称性三 phase：y_axis → x_axis → origin。",
    E312Stage.VERTICES.value: "顶点：compute 画布交互 → name 术语确认。",
    E312Stage.ECCENTRICITY.value: "离心率 6 phase 苏格拉底诱导。",
    E312Stage.EXAMPLE_1.value: "例4: 16x^2+25y^2=400 长/短/e/焦点/顶点。",
    E312Stage.EXAMPLE_2.value: "例5: |MF|/d=4/5 距离比反推椭圆。",
    E312Stage.EXAMPLE_3.value: "例6: 直线 4x-5y+m=0 与椭圆位置关系。",
    E312Stage.SUMMARY.value: "回顾 5 大几何性质 + 3 例题。",
}


# ═══════════════════════════════════════════════════
# TutoringFlow
# ═══════════════════════════════════════════════════

class TutoringFlow(Flow[LessonState]):
    """E312 椭圆几何性质 — CrewAI Flow FSM 编排器。

    9 个教学阶段，由确定性关键词 + LLM Crew 协同驱动。
    """

    def __init__(self):
        super().__init__()
        # Lazy init: Crew 在首次使用时才创建，
        # 确保 litellm.drop_params=True 在 Agent+Tool 初始化前生效
        self.__teaching_crew = None
        self.__feynman_crew = None
        self.__correction_crew = None

    @property
    def _teaching_crew(self):
        if self.__teaching_crew is None:
            self.__teaching_crew = TeachingCrew()
        return self.__teaching_crew

    @property
    def _feynman_crew(self):
        if self.__feynman_crew is None:
            self.__feynman_crew = FeynmanCrew()
        return self.__feynman_crew

    @property
    def _correction_crew(self):
        if self.__correction_crew is None:
            self.__correction_crew = CorrectionCrew()
        return self.__correction_crew

    # ─────────────────────────────────────────
    # Flow lifecycle
    # ─────────────────────────────────────────

    @start()
    def initialize(self):
        """初始化课程 — 发送 INTRO 开场白 + 画布动作。"""
        self.state.stage = E312Stage.INTRO.value
        return _step(
            stage=self.state.stage,
            message=E312_INTRO_MSG,
            canvas_action=STAGE_MANDATORY_VIZ.get(E312Stage.INTRO.value),
        )

    # ─────────────────────────────────────────
    # 主入口（非 Flow 装饰器 — 外部 server 调用）
    # ─────────────────────────────────────────

    def process_student_message(self, text: str) -> dict:
        """处理学生消息 — 由 FastAPI server 每轮调用。

        分发逻辑：
        1. 若 feynman 侧路激活 → _handle_feynman_turn
        2. 否则按 self.state.stage 分发到对应 handler
        """
        # 记录学生输入到历史
        self.state.history.append({"role": "student", "content": text})

        # Feynman side-loop 优先
        if self.state.feynman_active:
            return self._handle_feynman_turn(text)

        # 正常 stage dispatch
        handlers = {
            E312Stage.INTRO.value:        self._handle_intro,
            E312Stage.RANGE.value:        self._handle_range,
            E312Stage.SYMMETRY.value:     self._handle_symmetry,
            E312Stage.VERTICES.value:     self._handle_vertices,
            E312Stage.ECCENTRICITY.value: self._handle_eccentricity,
            E312Stage.EXAMPLE_1.value:    lambda t: self._handle_example(t, 4),
            E312Stage.EXAMPLE_2.value:    lambda t: self._handle_example(t, 5),
            E312Stage.EXAMPLE_3.value:    lambda t: self._handle_example(t, 6),
            E312Stage.SUMMARY.value:      self._handle_summary,
        }
        handler = handlers.get(self.state.stage, self._handle_fallback)
        result = handler(text)

        # 记录教师回复到历史
        if result and "message" in result:
            self.state.history.append({"role": "teacher", "content": result["message"]})
            self.state.last_agent = result.get("agent", "teacher")
            self.state.last_event_type = result.get("event_type", "normal")

        return result

    # ─────────────────────────────────────────
    # LLM Crew 调用辅助
    # ─────────────────────────────────────────

    def _llm_respond(self, text: str, fallback: str) -> str:
        """调用 TeachingCrew 生成苏格拉底式回复，失败时用 fallback。"""
        try:
            history_lines = []
            for h in self.state.history[-6:]:
                role = "学生" if h["role"] == "student" else "老师"
                history_lines.append(f"{role}: {h['content'][:80]}")
            history_summary = "\n".join(history_lines) if history_lines else "(无)"

            return self._teaching_crew.kickoff(
                student_text=text,
                stage=self.state.stage,
                system_context=f"课程: 3.1.2 椭圆几何性质",
                stage_goal=_STAGE_GOALS.get(self.state.stage, ""),
                history_summary=history_summary,
            )
        except Exception as e:
            print(f"[TutoringFlow] TeachingCrew failed: {e}")
            return fallback

    def _ta_correct(self, student_text: str, error_detail: str,
                    expected: str) -> str:
        """调用 CorrectionCrew 生成纠错反馈（传入阶段知识上下文）。"""
        from flow.state import STAGE_FEYNMAN_CONTEXT
        stage_context = STAGE_FEYNMAN_CONTEXT.get(self.state.stage, "")
        try:
            return self._correction_crew.generate_correction(
                student_text=student_text,
                error_detail=error_detail,
                stage=self.state.stage,
                expected_answer=expected,
                stage_context=stage_context,
            )
        except Exception as e:
            print(f"[TutoringFlow] CorrectionCrew failed: {e}")
            return f"助教提示：请再仔细看看你的计算。"

    # ─────────────────────────────────────────
    # Feynman side-loop
    # ─────────────────────────────────────────

    def _try_enter_feynman(self, prev_stage: str) -> Optional[dict]:
        """阶段切换瞬间：判断是否进入 Feynman 侧路。

        若进入：生成同伴提问，设置侧路状态，返回同伴气泡 step。
        若不进入：返回 None。
        """
        # 限频：同 stage 只触发 1 次
        count = self.state.feynman_triggers_in_stage.get(prev_stage, 0)
        if count >= 1:
            return None

        # 触发条件：每个知识探究阶段结束时有概率触发
        # 简化实现：RANGE/SYMMETRY/VERTICES/ECCENTRICITY 结束后触发
        triggerable = {
            E312Stage.RANGE.value,
            E312Stage.SYMMETRY.value,
            E312Stage.VERTICES.value,
            E312Stage.ECCENTRICITY.value,
        }
        if prev_stage not in triggerable:
            return None

        # 生成同伴提问 — 传入精确的"刚学完的知识点摘要"
        from flow.state import STAGE_FEYNMAN_CONTEXT
        topic_map = {
            E312Stage.RANGE.value: "椭圆的范围",
            E312Stage.SYMMETRY.value: "椭圆的对称性",
            E312Stage.VERTICES.value: "椭圆的顶点与长短轴",
            E312Stage.ECCENTRICITY.value: "离心率",
        }
        topic = topic_map.get(prev_stage, prev_stage)
        context = STAGE_FEYNMAN_CONTEXT.get(prev_stage, f"学生刚完成了{topic}的学习")

        try:
            peer_question = self._feynman_crew.generate_peer_question(
                stage=prev_stage,
                topic=topic,
                context=context,
            )
        except Exception as e:
            print(f"[TutoringFlow] FeynmanCrew failed: {e}")
            return None

        # 设置侧路状态
        self.state.feynman_active = True
        self.state.feynman_turn_count = 0
        self.state.feynman_triggers_in_stage[prev_stage] = count + 1

        return _step(
            stage=self.state.stage,
            message=peer_question,
            agent="peer",
            event_type="feynman_enter",
        )

    def _handle_feynman_turn(self, text: str) -> dict:
        """处理 Feynman 侧路中的学生回答。

        流程：Peer 判定学生解释 → 满意则退出（Teacher总结）→ 不满意则Peer追问。
        """
        self.state.feynman_turn_count += 1

        # 学生说 skip → 直接退出
        if any(kw in text for kw in ["跳过", "算了", "不想", "skip", "下一个",
                                     "不知道", "不会", "不清楚", "不懂", "不记得"]):
            return self._exit_feynman_with_summary()

        # 达到最大轮数 → 退出
        if self.state.feynman_turn_count >= self.state.feynman_max_turns:
            return self._exit_feynman_with_summary()

        # 构建对话记录（给 Peer 看的上下文）
        from flow.state import STAGE_FEYNMAN_CONTEXT
        prev_stage = self.state.pending_stage_after_feynman or self.state.stage
        # 费曼触发在 prev_stage 完成之后，context 用 prev_stage 的
        # 但 pending_stage_after_feynman 存的是 new_stage，所以需要往回看一个
        feynman_source_stage = None
        for s in [E312Stage.RANGE.value, E312Stage.SYMMETRY.value,
                  E312Stage.VERTICES.value, E312Stage.ECCENTRICITY.value,
                  E312Stage.INTRO.value]:
            if s in self.state.feynman_triggers_in_stage:
                feynman_source_stage = s
        context = STAGE_FEYNMAN_CONTEXT.get(
            feynman_source_stage or self.state.stage, "当前知识点")

        conversation = self._build_feynman_conversation()

        # Peer 判定 + 决定追问或满意
        try:
            judgment = self._feynman_crew.peer_evaluate_and_respond(
                student_text=text,
                context=context,
                conversation_so_far=conversation,
            )
        except Exception as e:
            print(f"[TutoringFlow] FeynmanCrew peer_evaluate failed: {e}")
            return self._exit_feynman_with_summary()

        if judgment.get("satisfied", False):
            # Peer 满意 → 不显示同学气泡，直接交给老师衔接
            return self._exit_feynman_with_summary()
        else:
            # Peer 追问
            peer_followup = judgment.get("response", "嗯...你能再解释清楚一点吗？")
            self.state.history.append({"role": "peer", "content": peer_followup})
            return _step(
                stage=self.state.stage,
                message=peer_followup,
                agent="peer",
                event_type="feynman_followup",
            )

    def _build_feynman_conversation(self) -> str:
        """从 history 中提取费曼侧路期间的对话记录。"""
        lines = []
        in_feynman = False
        for msg in self.state.history:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "peer":
                in_feynman = True
            if in_feynman:
                label = {"student": "学生", "peer": "同学", "teacher": "老师"}.get(role, role)
                lines.append(f"{label}：{content}")
        return "\n".join(lines[-8:])  # 最多保留最近8条

    def _exit_feynman_with_summary(self) -> dict:
        """退出 Feynman 侧路：Teacher 生成自然语言总结，恢复课程。

        同学满意时不出同学气泡，直接由老师衔接总结+过渡到下一阶段。
        """
        from flow.state import STAGE_FEYNMAN_CONTEXT

        # 找到触发费曼的源阶段
        feynman_source_stage = None
        for s in self.state.feynman_triggers_in_stage:
            feynman_source_stage = s
        context = STAGE_FEYNMAN_CONTEXT.get(
            feynman_source_stage or self.state.stage, "")
        topic_map = {
            E312Stage.RANGE.value: "椭圆的范围",
            E312Stage.SYMMETRY.value: "椭圆的对称性",
            E312Stage.VERTICES.value: "椭圆的顶点与长短轴",
            E312Stage.ECCENTRICITY.value: "离心率",
        }
        topic = topic_map.get(feynman_source_stage or "", "当前知识点")
        conversation = self._build_feynman_conversation()

        # Teacher 生成总结
        try:
            teacher_summary = self._feynman_crew.teacher_summarize(
                topic=topic, context=context, conversation=conversation)
        except Exception as e:
            print(f"[TutoringFlow] Teacher summarize failed: {e}")
            teacher_summary = "讨论得不错！我们继续。"

        # 清理侧路状态
        self.state.feynman_active = False
        self.state.feynman_turn_count = 0

        # 只有老师的总结 + 下一阶段内容（不拼同学气泡）
        parts = [teacher_summary]

        # 恢复暂存的 stage transition
        if self.state.pending_step_after_feynman:
            pending = self.state.pending_step_after_feynman
            self.state.pending_step_after_feynman = None
            if self.state.pending_stage_after_feynman:
                self.state.stage = self.state.pending_stage_after_feynman
                self.state.pending_stage_after_feynman = None
            parts.append("\n\n" + pending.get("message", ""))
            return _step(
                stage=pending.get("target_stage_value", self.state.stage),
                message="\n".join(parts),
                canvas_action=pending.get("canvas_action"),
            )

        return _step(stage=self.state.stage, message="\n".join(parts))

    # ─────────────────────────────────────────
    # Stage transition helper
    # ─────────────────────────────────────────

    def _transition_to(self, new_stage: E312Stage, message: str,
                       prev_stage: str, canvas_action: Any = None) -> dict:
        """切换到新阶段。检查 Feynman 侧路触发条件。

        若触发 Feynman：暂存 target step，返回同伴气泡。
        若不触发：直接返回 target step。
        """
        self.state.stage = new_stage.value
        viz = canvas_action or STAGE_MANDATORY_VIZ.get(new_stage.value)

        # 尝试触发 Feynman
        feynman_step = self._try_enter_feynman(prev_stage)
        if feynman_step:
            # 暂存原 target step，等侧路结束后恢复
            self.state.pending_stage_after_feynman = new_stage.value
            self.state.pending_step_after_feynman = {
                "target_stage_value": new_stage.value,
                "message": message,
                "canvas_action": viz,
            }
            # 回滚 stage 到 prev（侧路期间 FSM 视角停在切换前）
            self.state.stage = prev_stage
            return feynman_step

        return _step(stage=new_stage.value, message=message, canvas_action=viz)

    # ═══════════════════════════════════════════════════
    # STAGE HANDLERS
    # ═══════════════════════════════════════════════════

    # ──────── 1. INTRO ────────

    def _handle_intro(self, text: str) -> dict:
        """INTRO: 学生回忆 a/b/c → 推进到 RANGE。支持跳级到例题。"""
        # 跳级到例题
        skip_n = _looks_like_skip_to_example(text)
        if skip_n is not None:
            target_stage, target_intro = {
                1: (E312Stage.EXAMPLE_1, E312_EXAMPLE_1_INTRO),
                2: (E312Stage.EXAMPLE_2, E312_EXAMPLE_2_INTRO),
                3: (E312Stage.EXAMPLE_3, E312_EXAMPLE_3_INTRO),
            }[skip_n]
            self.state.stage = target_stage.value
            return _step(
                stage=self.state.stage,
                message=(f"好的，我们直接看例 {skip_n}（教材 3.1.2 节原题；"
                         f"跳过了几何性质探究，例题做完后可回到课程开头补）：\n\n"
                         + target_intro),
                canvas_action=STAGE_MANDATORY_VIZ.get(target_stage.value),
            )

        # 正常路径：abc recall → RANGE
        if _looks_like_abc_recall(text):
            ack = self._llm_respond(text, fallback="✅ 回忆得很好。")
            full = ack + "\n\n" + E312_RANGE_PREDICT_MSG
            self.state.range_phase = "predict"
            return self._transition_to(
                E312Stage.RANGE, full, prev_stage=E312Stage.INTRO.value,
            )

        # 未命中 → LLM 引导
        reply = self._llm_respond(
            text,
            fallback="提示：在椭圆图中，$a$ 是长半轴长（从中心到长轴端点），"
                     "$b$ 是短半轴长（从中心到短轴端点），$c$ 是半焦距（从中心到焦点）。"
                     "你能再说一遍它们各代表哪条线段吗？",
        )
        return _step(stage=self.state.stage, message=reply)

    # ──────── 2. RANGE ────────

    def _handle_range(self, text: str) -> dict:
        """RANGE: predict → derive（x_done + y_done）→ awaiting_next → SYMMETRY。"""
        # awaiting_next 过渡
        if self.state.range_awaiting_next:
            if _looks_like_ready(text):
                self.state.range_awaiting_next = False
                return self._transition_to(
                    E312Stage.SYMMETRY,
                    E312_SYMMETRY_Y_MSG,
                    prev_stage=E312Stage.RANGE.value,
                )
            reply = self._llm_respond(
                text,
                fallback="先看看右边的图——回个「好」/「准备好了」我们就开始下一节 🌿。",
            )
            return _step(stage=self.state.stage, message=reply)

        # phase 1: predict → derive
        if self.state.range_phase == "predict":
            self.state.range_phase = "derive"
            ack = self._llm_respond(text, fallback="✅ 收到你的猜想。")
            return _step(stage=self.state.stage,
                         message=ack + "\n\n" + E312_RANGE_DERIVE_MSG)

        # phase 2: derive — 识别 x/y 范围
        x_ok = _looks_like_range_x(text)
        y_ok = _looks_like_range_y(text)
        if x_ok:
            self.state.range_x_done = True
        if y_ok:
            self.state.range_y_done = True

        if self.state.range_x_done and self.state.range_y_done:
            self.state.range_awaiting_next = True
            return _step(
                stage=self.state.stage,
                message=E312_RANGE_DONE_MSG + "\n\n👀 接下来我们来**研究对称性**，准备好了吗？",
                canvas_action={"action": "show_e312_range_solved"},
            )

        # TA 纠错：学生写了什么但没命中
        if not x_ok and not y_ok and (self.state.range_x_done or self.state.range_y_done):
            # 可能有变量错位（如写 -b<=x<=b）
            if self.state.range_x_done and not self.state.range_y_done:
                expected = "-b<=y<=b（y 的范围用 b 不用 a）"
            else:
                expected = "-a<=x<=a（x 的范围用 a 不用 b）"
            ta_msg = self._ta_correct(text, "变量可能错位", expected)
            return _step(stage=self.state.stage, message=ta_msg, agent="ta")

        # 只答一边 → 追问另一边
        if self.state.range_x_done and not self.state.range_y_done:
            return _step(
                stage=self.state.stage,
                message="✅ $-a\\le x\\le a$ 正确！那 **$y$ 的范围**呢？"
                        "同样用 $\\dfrac{y^2}{b^2}\\le 1$ 推一下。",
            )
        if self.state.range_y_done and not self.state.range_x_done:
            return _step(
                stage=self.state.stage,
                message="✅ $-b\\le y\\le b$ 正确！那 **$x$ 的范围**呢？"
                        "同样用 $\\dfrac{x^2}{a^2}\\le 1$ 推一下。",
            )

        # 兜底 LLM
        reply = self._llm_respond(
            text,
            fallback="提示：由 $\\dfrac{x^2}{a^2}\\le 1$ 两边乘 $a^2$（$a>0$），"
                     "得 $x^2\\le a^2$，即 $|x|\\le a$。",
        )
        return _step(stage=self.state.stage, message=reply)

    # ──────── 3. SYMMETRY ────────

    def _handle_symmetry(self, text: str) -> dict:
        """SYMMETRY: y_axis → x_axis → origin → awaiting_next → VERTICES。"""
        # awaiting_next 过渡
        if self.state.sym_awaiting_next:
            if _looks_like_ready(text):
                self.state.sym_awaiting_next = False
                return self._transition_to(
                    E312Stage.VERTICES,
                    E312_VERTICES_COMPUTE_MSG,
                    prev_stage=E312Stage.SYMMETRY.value,
                )
            reply = self._llm_respond(
                text,
                fallback="先看看右边图里的 3 个对称伙伴——回个「好」/「准备好了」我们就开始顶点探究。",
            )
            return _step(stage=self.state.stage, message=reply)

        phase = self.state.sym_phase

        if phase == "y_axis":
            if _looks_like_y_axis_sym(text):
                self.state.sym_phase = "x_axis"
                return _step(stage=self.state.stage, message=E312_SYMMETRY_X_MSG)
            if _looks_like_x_axis_sym(text):
                return _step(
                    stage=self.state.stage,
                    message="嗯，x 轴对称是对的，但当前问题是 $x \\to -x$ 让方程不变，"
                            "这对应**y 轴**对称。我们按顺序来 👇",
                )
            if _looks_like_origin_sym(text):
                return _step(
                    stage=self.state.stage,
                    message="嗯，原点对称也对，但当前问题是 $x \\to -x$，先回答**y 轴**对称。",
                )
            # TA 或 LLM 兜底
            reply = self._llm_respond(
                text,
                fallback="提示：$x$ 换成 $-x$ 时 $(-x)^2=x^2$，方程不变，说明关于 **y 轴** 对称。",
            )
            return _step(stage=self.state.stage, message=reply)

        if phase == "x_axis":
            if _looks_like_x_axis_sym(text):
                self.state.sym_phase = "origin"
                return _step(stage=self.state.stage, message=E312_SYMMETRY_O_MSG)
            if _looks_like_y_axis_sym(text) or _looks_like_origin_sym(text):
                return _step(
                    stage=self.state.stage,
                    message="嗯，但当前问题是 $y \\to -y$ 方程不变 → **x 轴**对称。",
                )
            reply = self._llm_respond(
                text,
                fallback="提示：$y$ 换成 $-y$ 方程不变，关于 **x 轴** 对称。",
            )
            return _step(stage=self.state.stage, message=reply)

        # phase == "origin"
        if _looks_like_origin_sym(text):
            self.state.sym_awaiting_next = True
            return _step(
                stage=self.state.stage,
                message=E312_SYMMETRY_DONE_MSG
                        + "\n\n👀 接下来我们来**研究顶点**，准备好了吗？",
                canvas_action={"action": "show_e312_symmetry_solved"},
            )
        if _looks_like_x_axis_sym(text) or _looks_like_y_axis_sym(text):
            return _step(
                stage=self.state.stage,
                message="同时换 x 和 y → 这是**原点**对称（中心对称）。再答一次？",
            )
        reply = self._llm_respond(
            text,
            fallback="提示：$x$ 和 $y$ 同时换成相反数方程不变，关于**原点**对称。",
        )
        return _step(stage=self.state.stage, message=reply)

    # ──────── 4. VERTICES ────────

    def _handle_vertices(self, text: str) -> dict:
        """VERTICES: compute（画布交互）→ name（术语确认）→ ECCENTRICITY。"""
        phase = self.state.vertices_phase

        if phase == "compute":
            # compute phase 主要靠画布事件推进，文字输入给 LLM 提示
            reply = self._llm_respond(
                text,
                fallback="提示：先去**右边沙盒**点击 4 个你认为是顶点的点 —— "
                         "顶点是椭圆与坐标轴的交点。",
            )
            return _step(stage=self.state.stage, message=reply)

        # phase == "name"
        if _looks_like_ready(text) or _looks_like_understood(text):
            self.state.ecc_phase = "explore_c"
            return self._transition_to(
                E312Stage.ECCENTRICITY,
                E312_ECC_EXPLORE_C_MSG,
                prev_stage=E312Stage.VERTICES.value,
            )
        reply = self._llm_respond(
            text,
            fallback="如果术语都清楚了，回个「明白」我们继续到下一节——**离心率**（本课重点）。",
        )
        return _step(stage=self.state.stage, message=reply)

    def on_canvas_event(self, event_type: str, data: dict) -> Optional[dict]:
        """处理画布事件。

        支持的事件：
        - e312_abc_quiz_completed：INTRO 阶段学生点对 a/b/c 三条线段 → 推进到 RANGE
        - e312_vertex_clicked：VERTICES compute 阶段学生点击候选顶点 → 累积命中
        """
        # ── INTRO 阶段：abc 复习点线段完成 ──
        if event_type == "e312_abc_quiz_completed":
            if self.state.stage == E312Stage.INTRO.value:
                self.state.stage = E312Stage.RANGE.value
                self.state.range_phase = "predict"
                ack = "🎯 三条线段都点对了！a 是长半轴、b 是短半轴、c 是半焦距。"
                return _step(
                    stage=self.state.stage,
                    message=ack + "\n\n" + E312_RANGE_PREDICT_MSG,
                    canvas_action=STAGE_MANDATORY_VIZ.get(E312Stage.RANGE.value),
                )
            return None

        # ── VERTICES 阶段：候选顶点点击 ──
        if event_type == "e312_vertex_clicked":
            if (self.state.stage == E312Stage.VERTICES.value
                    and self.state.vertices_phase == "compute"):
                pt = (data or {}).get("point")  # 期待 [x, y]
                if pt and len(pt) == 2:
                    key = (int(pt[0]), int(pt[1]))
                    canonical_vertices = {(-2, 0), (2, 0), (0, -1), (0, 1)}
                    if key in canonical_vertices:
                        self.state.vertices_correct_hits.add(str(key))
                if len(self.state.vertices_correct_hits) >= 4:
                    self.state.vertices_phase = "name"
                    return _step(
                        stage=self.state.stage,
                        message=E312_VERTICES_NAME_MSG,
                        canvas_action={"action": "show_e312_vertices_solved"},
                    )
            return None

        return None

    # ──────── 5. ECCENTRICITY ────────

    def _handle_eccentricity(self, text: str) -> dict:
        """ECCENTRICITY: 6 phase 苏格拉底诱导。支持跳级。"""
        phase = self.state.ecc_phase

        # ── 跳级检测 ──
        # 在前面 phase 直接答出后面内容 → 快速带过
        if phase in ("explore_c", "explore_a", "induce_ratio", "define"):
            if _looks_like_e_shape_relation(text):
                self.state.ecc_phase = "geometry"
                return _step(
                    stage=self.state.stage,
                    message="✅ 你已经把后面的几何意义说出来了——我们直接看综合实验：\n\n"
                            + E312_ECC_GEOMETRY_MSG,
                    canvas_action={"action": "show_e312_eslider"},
                )
        if phase in ("explore_c", "explore_a", "induce_ratio"):
            if _looks_like_e_define(text):
                self.state.ecc_phase = "geometry"
                return _step(
                    stage=self.state.stage,
                    message="✅ 你已经写出 $e=\\dfrac{c}{a}$ 了——我们看一下它的几何意义：\n\n"
                            + E312_ECC_GEOMETRY_MSG,
                    canvas_action={"action": "show_e312_eslider"},
                )

        # ── 逐 phase 处理 ──

        if phase == "explore_c":
            if _looks_like_flat(text):
                self.state.ecc_phase = "explore_a"
                return _step(
                    stage=self.state.stage,
                    message=E312_ECC_EXPLORE_A_MSG,
                    canvas_action={"action": "show_e312_explore_a"},
                )
            reply = self._llm_respond(
                text,
                fallback="拖动 $c$ 滑块（$a$ 固定），观察椭圆变化。$c$ 越大椭圆变扁还是变圆？",
            )
            return _step(stage=self.state.stage, message=reply)

        if phase == "explore_a":
            if _looks_like_round(text):
                self.state.ecc_phase = "induce_ratio"
                return _step(stage=self.state.stage, message=E312_ECC_INDUCE_MSG)
            reply = self._llm_respond(
                text,
                fallback="拖动 $a$ 滑块（$c$ 固定），观察椭圆变化。$a$ 越大椭圆变扁还是变圆？",
            )
            return _step(stage=self.state.stage, message=reply)

        if phase == "induce_ratio":
            if _looks_like_ratio(text):
                self.state.ecc_phase = "define"
                return _step(stage=self.state.stage, message=E312_ECC_DEFINE_MSG)
            # TA 纠错：学生答了 差/和/积
            t_ns = text.replace(" ", "").lower()
            if any(kw in t_ns for kw in ["和", "差", "积", "加", "减", "乘"]):
                ta_msg = self._ta_correct(
                    text,
                    "学生选了差/和/积而非比值",
                    "比值 c/a 才能反映椭圆形状",
                )
                return _step(stage=self.state.stage, message=ta_msg, agent="ta")
            reply = self._llm_respond(
                text,
                fallback="提示：和、差、积、商哪个最能反映两个量的相对大小？",
            )
            return _step(stage=self.state.stage, message=reply)

        if phase == "define":
            # define 已剧透 e=c/a，学生只需 ack
            if _looks_like_ready(text) or _looks_like_e_define(text):
                self.state.ecc_phase = "geometry"
                return _step(
                    stage=self.state.stage,
                    message=E312_ECC_GEOMETRY_MSG,
                    canvas_action={"action": "show_e312_eslider"},
                )
            reply = self._llm_respond(
                text,
                fallback="回个「好」或「明白」，我们就看 $e$ 滑块 👇",
            )
            return _step(stage=self.state.stage, message=reply)

        if phase == "geometry":
            if _looks_like_e_shape_relation(text):
                self.state.ecc_phase = "range"
                return _step(stage=self.state.stage, message=E312_ECC_RANGE_MSG)
            reply = self._llm_respond(
                text,
                fallback="拖动沙盒的 e 滑块。用一句话描述：$e$ 越大越...，$e$ 越小越...?",
            )
            return _step(stage=self.state.stage, message=reply)

        # phase == "range"
        if not self.state.ecc_range_part1:
            if _looks_like_e_range_0_1(text):
                self.state.ecc_range_part1 = True
                return _step(
                    stage=self.state.stage,
                    message="✅ $0<e<1$。再追问一个**极限情况**：如果 $a=b$（椭圆的长短半轴相等），"
                            "由 $b^2=a^2-c^2$ 得 $c=?$，那么 $e=?$ 此时图形变成什么？",
                )
            reply = self._llm_respond(
                text,
                fallback="提示：$0<c<a$，所以 $0<e=\\dfrac{c}{a}<1$。",
            )
            return _step(stage=self.state.stage, message=reply)

        # range part 2: a=b → e=0 → 圆
        if _looks_like_e_zero_circle(text):
            return self._transition_to(
                E312Stage.EXAMPLE_1,
                E312_ECC_DONE_MSG + "\n\n" + E312_EXAMPLE_1_INTRO,
                prev_stage=E312Stage.ECCENTRICITY.value,
            )
        reply = self._llm_respond(
            text,
            fallback="提示：$a=b$ 时 $c=0$，$e=0$，椭圆退化为**圆**——圆是椭圆的极限情形。",
        )
        return _step(stage=self.state.stage, message=reply)

    # ──────── 6/7/8. EXAMPLE（统一 handler）────────

    def _handle_example(self, text: str, example_num: int) -> dict:
        """EXAMPLE 统一处理器（例4/5/6）：诊断器 + 协议 + 部分命中累积。"""
        from courses.example_canonicals_312 import EXAMPLE_CONFIGS_312
        from courses.example_diagnostician_312 import diagnose_example_312

        # awaiting_next 检查
        if self.state.example_done_awaiting_next == example_num:
            if _looks_like_ready(text):
                self.state.example_done_awaiting_next = None
                return self._continue_to_next_example(example_num)
            ui_num = example_num - 3
            return _step(
                stage=self.state.stage,
                message=f"例 {ui_num} 已经完成 看完右边的图后回个「好」/「继续」就切到下一题。",
            )

        config = EXAMPLE_CONFIGS_312[example_num]
        phases = config["phases"]
        idx = self.state.example_phase_idx.get(example_num, 0)
        if idx >= len(phases):
            return self._advance_example(example_num)
        current_phase = phases[idx]

        # 1. 确定性诊断器
        dx = diagnose_example_312(text, example_num, current_phase)

        # 2. ex5 ask_conclude 跨 turn 累积
        if dx is None and example_num == 5 and current_phase == "ask_conclude":
            cache_key = "5_ask_conclude"
            hits = self.state.example_conclude_hits.get(
                cache_key, {"ellipse": False, "axis_10": False, "axis_6": False}
            )
            if "椭圆" in text:
                hits["ellipse"] = True
            if "10" in text:
                hits["axis_10"] = True
            if "6" in text:
                hits["axis_6"] = True
            self.state.example_conclude_hits[cache_key] = hits
            if all(hits.values()):
                # 模拟完整命中
                from courses.example_diagnostician_312 import ExampleDiagnosis312
                dx = ExampleDiagnosis312(
                    hit_goal="conclude_kw",
                    implied_flags={"conclude_done"},
                    label="完全正确（累积）",
                    via="conclude_accumulated",
                )
            elif any(hits.values()):
                missing = []
                if not hits["ellipse"]:
                    missing.append("是什么图形？")
                if not hits["axis_10"]:
                    missing.append("长轴长 2a=?")
                if not hits["axis_6"]:
                    missing.append("短轴长 2b=?")
                return _step(
                    stage=self.state.stage,
                    message=f"✅ 这部分对了。还差：{'，'.join(missing)}",
                )

        # 3. point_set phase 部分累积（ask_focus / ask_vertex）
        if dx is None and current_phase in ("ask_focus", "ask_vertex"):
            from courses.example_diagnostician_312 import (
                ExampleDiagnosis312, partial_hit_point_set,
            )
            goal_key = "focus_set" if current_phase == "ask_focus" else "vertex_set"
            canonical = config["canonical"].get(goal_key)
            if canonical:
                new_hits = partial_hit_point_set(text, canonical)
                if new_hits:
                    cache_key = f"{example_num}_{current_phase}"
                    accumulated = self.state.example_partial_points.get(cache_key, set())
                    accumulated |= new_hits
                    self.state.example_partial_points[cache_key] = accumulated
                    if accumulated == set(canonical):
                        dx = ExampleDiagnosis312(
                            hit_goal=goal_key,
                            implied_flags=set(config["implies"].get(goal_key, set())),
                            label="完全正确（累积）",
                            via="point_set_accumulated",
                        )
                    else:
                        missing = set(canonical) - accumulated
                        m_str = ", ".join(f"({p[0]},{p[1]})" for p in sorted(missing))
                        return _step(
                            stage=self.state.stage,
                            message=f"✅ 对了一部分！还差 {m_str}，继续答 👇",
                        )

        # 4. LLM 协议兜底（TeachingCrew 代替原 _llm_example_protocol）
        if dx is None:
            reply = self._llm_respond(
                text,
                fallback="再想想？或者把你的答案写完整些（如焦点请写 (-3,0) 这样的坐标形式）。",
            )
            return _step(stage=self.state.stage, message=reply)

        # 5. 命中 → 推进 phase
        flags = self.state.example_subflags.get(example_num, set())
        flags |= dx.implied_flags
        self.state.example_subflags[example_num] = flags
        self.state.example_phase_idx[example_num] = idx + 1
        next_idx = idx + 1
        ack = "✅ 完全正确！"

        # 检查整道题是否做完
        done_fn = config["done_fn"]
        if done_fn(flags) or next_idx >= len(phases):
            return self._advance_example(example_num, ack=ack)

        # 进下一 phase
        next_phase = phases[next_idx]
        next_prompt = _EXAMPLE_PHASE_PROMPTS.get(
            (example_num, next_phase), "请继续。"
        )
        extra_action = None
        if example_num == 5 and current_phase == "ask_simplify":
            extra_action = {"action": "show_e312_example_2_curve_only"}
        return _step(
            stage=self.state.stage,
            message=ack + "\n\n" + next_prompt,
            canvas_action=extra_action,
        )

    def _advance_example(self, example_num: int, ack: str = "") -> dict:
        """例题通关 → 发 solved viz + 设 awaiting_next。"""
        solved_action = {"action": f"show_e312_example_{example_num - 3}_solved"}
        self.state.example_done_awaiting_next = example_num
        ui_num = example_num - 3

        head = ack + "\n\n" if ack else ""
        if example_num == 6:
            tail = (f"🎉 例 {ui_num} 完成！\n\n本节 3 道例题全部做完。"
                    "准备好了回个「好」/「继续」我们看本课总结。")
        else:
            tail = f"🎉 例 {ui_num} 完成！右边是完整答案图，回个「好」/「继续」我们看下一题。"

        return _step(
            stage=self.state.stage,
            message=head + tail,
            canvas_action=solved_action,
        )

    def _continue_to_next_example(self, completed_num: int) -> dict:
        """学生确认后切到下一例 / SUMMARY。"""
        if completed_num == 4:
            self.state.stage = E312Stage.EXAMPLE_2.value
            return _step(
                stage=self.state.stage,
                message=E312_EXAMPLE_2_INTRO,
                canvas_action=STAGE_MANDATORY_VIZ.get(E312Stage.EXAMPLE_2.value),
            )
        elif completed_num == 5:
            self.state.stage = E312Stage.EXAMPLE_3.value
            return _step(
                stage=self.state.stage,
                message=E312_EXAMPLE_3_INTRO,
                canvas_action=STAGE_MANDATORY_VIZ.get(E312Stage.EXAMPLE_3.value),
            )
        else:  # 6 → SUMMARY
            self.state.stage = E312Stage.SUMMARY.value
            return _step(
                stage=self.state.stage,
                message=E312_SUMMARY_MSG,
                canvas_action=STAGE_MANDATORY_VIZ.get(E312Stage.SUMMARY.value),
            )

    # ──────── 9. SUMMARY ────────

    def _handle_summary(self, text: str) -> dict:
        """SUMMARY: 复习总结，学生说「结束」时附 [LESSON_END]。"""
        self.state.summary_turns += 1
        if _looks_like_lesson_end(text) or self.state.summary_turns >= 6:
            self.state.lesson_ended = True
            fallback = (
                "👏 恭喜完成 3.1.2 课程！\n\n"
                "下次见 —— 我们将一起进入 3.2.1「双曲线及其标准方程」，"
                "把『距离之和』改成『距离之差』，看看会出现什么新曲线。\n\n"
                "[LESSON_END]"
            )
            reply = self._llm_respond(text, fallback=fallback)
            return _step(stage=self.state.stage, message=reply)
        reply = self._llm_respond(
            text,
            fallback="还有什么问题想问？或者输入「结束」结课。",
        )
        return _step(stage=self.state.stage, message=reply)

    # ──────── Fallback ────────

    def _handle_fallback(self, text: str) -> dict:
        """未知 stage 的兜底处理。"""
        reply = self._llm_respond(text, fallback="我没听懂，你可以再说一遍吗？")
        return _step(stage=self.state.stage, message=reply)
