# -*- coding: utf-8 -*-
"""LessonState: CrewAI Flow 的结构化状态模型。

对应原 lesson_flow.py 中分散在 self._e312_* 属性上的所有运行时状态，
统一到一个 Pydantic BaseModel 中，供 TutoringFlow(Flow[LessonState]) 使用。

关键设计区别：
  · 原单体把状态散落在 self._e312_range_phase / self._e312_sym_phase 等属性上
  · 新架构把全部状态收敛到 LessonState，CrewAI Flow 通过 self.state 访问
  · Pydantic 保证类型安全 + 可序列化（便于持久化 / 日志）
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────
# Stage 枚举
# ─────────────────────────────────────────────

class E312Stage(str, Enum):
    """3.1.2 椭圆几何性质 — 9 个教学阶段

    严格对齐教材 p110-p114 栏目。
    阶段顺序：开场 → 范围 → 对称性 → 顶点 → 离心率 → 例4 → 例5 → 例6 → 总结
    """
    INTRO        = "e312_intro"          # 1. 开场：回顾 3.1.1 + 引入"由方程研究图形"
    RANGE        = "e312_range"          # 2. 范围（2 phase: predict → derive）
    SYMMETRY     = "e312_symmetry"       # 3. 对称性（3 phase: y_axis → x_axis → origin）
    VERTICES     = "e312_vertices"       # 4. 顶点（2 phase: compute → name）
    ECCENTRICITY = "e312_eccentricity"   # 5. 离心率（6 phase: explore_c/a → induce → define → geometry → range）
    EXAMPLE_1    = "e312_example_1"      # 6. 例4 (教材 p112) 16x²+25y²=400
    EXAMPLE_2    = "e312_example_2"      # 7. 例5 (教材 p113) |MF|/d = 4/5
    EXAMPLE_3    = "e312_example_3"      # 8. 例6 (教材 p114) 直线椭圆位置
    SUMMARY      = "e312_summary"        # 9. 总结（衔接 3.2.1 双曲线）


# 阶段顺序表（用于 next_stage 推进）
E312_STAGE_ORDER: List[E312Stage] = [
    E312Stage.INTRO,
    E312Stage.RANGE,
    E312Stage.SYMMETRY,
    E312Stage.VERTICES,
    E312Stage.ECCENTRICITY,
    E312Stage.EXAMPLE_1,
    E312Stage.EXAMPLE_2,
    E312Stage.EXAMPLE_3,
    E312Stage.SUMMARY,
]


def next_e312_stage(current: E312Stage) -> Optional[E312Stage]:
    """返回下一个阶段，若已是最后阶段则返回 None。"""
    try:
        idx = E312_STAGE_ORDER.index(current)
        if idx + 1 < len(E312_STAGE_ORDER):
            return E312_STAGE_ORDER[idx + 1]
    except ValueError:
        pass
    return None


# ─────────────────────────────────────────────
# 每阶段入口 Canvas 动作
# ─────────────────────────────────────────────

STAGE_MANDATORY_VIZ: Dict[str, Dict[str, Any]] = {
    E312Stage.INTRO.value:        {"action": "show_e312_abc_quiz"},
    E312Stage.RANGE.value:        {"action": "show_e312_range_setup"},
    E312Stage.SYMMETRY.value:     {"action": "show_e312_symmetry_setup"},
    E312Stage.VERTICES.value:     {"action": "show_e312_vertices_setup"},
    E312Stage.ECCENTRICITY.value: {"action": "show_e312_explore_c"},
    E312Stage.EXAMPLE_1.value:    {"action": "show_e312_example_1_setup"},
    E312Stage.EXAMPLE_2.value:    {"action": "show_e312_example_2_setup"},
    E312Stage.EXAMPLE_3.value:    {"action": "show_e312_example_3_setup"},
    E312Stage.SUMMARY.value:      {"action": "show_e312_summary"},
}


# ─────────────────────────────────────────────
# LessonState
# ─────────────────────────────────────────────

class LessonState(BaseModel):
    """教学会话状态 — CrewAI Flow 的结构化状态。

    设计目标：把原 lesson_flow.py 散落在 self._e312_* 属性上的全部运行时状态
    收敛到一个类型安全、可序列化的 Pydantic 模型中。
    """

    # ── 课程元信息 ──
    course_type: str = "ellipse_312"
    stage: str = E312Stage.INTRO.value

    # ── 对话历史 ──
    history: List[Dict[str, str]] = Field(default_factory=list)
    summary_turns: int = 0          # SUMMARY 阶段累计轮数

    # ── RANGE 阶段 phase tracking ──
    # 2 phase: predict → derive; derive 内需 x_done + y_done 才推进
    range_phase: str = "predict"    # "predict" | "derive"
    range_x_done: bool = False
    range_y_done: bool = False
    range_awaiting_next: bool = False

    # ── SYMMETRY 阶段 phase tracking ──
    # 3 phase: y_axis → x_axis → origin
    sym_phase: str = "y_axis"       # "y_axis" | "x_axis" | "origin"
    sym_awaiting_next: bool = False

    # ── VERTICES 阶段 phase tracking ──
    # 2 phase: compute（画布交互）→ name（术语确认）
    vertices_phase: str = "compute"  # "compute" | "name"
    vertices_correct_hits: Set[str] = Field(default_factory=set)

    # ── ECCENTRICITY 阶段 phase tracking ──
    # 6 phase: explore_c → explore_a → induce_ratio → define → geometry → range
    ecc_phase: str = "explore_c"
    ecc_range_part1: bool = False    # range phase 两步：part1 = 0<e<1, part2 = a=b→e=0→圆

    # ── EXAMPLE 阶段 tracking ──
    # 例题编号映射：example_1→4, example_2→5, example_3→6（教材全局编号延续 3.1.1）
    example_phase_idx: Dict[int, int] = Field(
        default_factory=lambda: {4: 0, 5: 0, 6: 0}
    )
    example_subflags: Dict[int, Set[str]] = Field(
        default_factory=lambda: {4: set(), 5: set(), 6: set()}
    )
    example_partial_points: Dict[str, Set[Tuple[int, int]]] = Field(
        default_factory=dict
    )
    example_conclude_hits: Dict[str, Dict[str, bool]] = Field(
        default_factory=dict
    )
    example_done_awaiting_next: Optional[int] = None  # 例题通关后等学生确认

    # ── Feynman 侧路 ──
    feynman_active: bool = False
    feynman_turn_count: int = 0
    feynman_max_turns: int = 3
    feynman_triggers_in_stage: Dict[str, int] = Field(default_factory=dict)
    pending_stage_after_feynman: Optional[str] = None
    pending_step_after_feynman: Optional[Dict[str, Any]] = None

    # ── Agent tracking ──
    last_agent: str = "teacher"         # "teacher" | "peer" | "ta"
    last_event_type: str = "normal"     # "normal" | "llm_propose_advance" | "fsm_reject"

    # ── 课程终结标记 ──
    lesson_ended: bool = False


# ═══════════════════════════════════════════════════
# 费曼侧路：每个阶段切换点的"刚学完的知识点摘要"
# Peer 必须围绕这些内容提问，不得扩展到其他知识点
# ═══════════════════════════════════════════════════

STAGE_FEYNMAN_CONTEXT: Dict[str, str] = {
    E312Stage.INTRO.value: (
        "学生刚回顾了椭圆标准方程 x²/a²+y²/b²=1 中三个参数的几何含义："
        "a 是长半轴长（中心到长轴端点），b 是短半轴长（中心到短轴端点），"
        "c 是半焦距（中心到焦点），且 a>b>0，c²=a²-b²。"
    ),
    E312Stage.RANGE.value: (
        "学生刚用代数方法严格证明了椭圆的范围：\n"
        "由 x²/a²+y²/b²=1 且 y²/b²≥0，推出 x²/a²≤1，即 -a≤x≤a；\n"
        "同理由 x²/a²≥0，推出 y²/b²≤1，即 -b≤y≤b。\n"
        "几何意义：椭圆完全被矩形 [-a,a]×[-b,b] 框住。"
    ),
    E312Stage.SYMMETRY.value: (
        "学生刚证明了椭圆的三种对称性：\n"
        "1. 把 x 换成 -x，方程不变 → 关于 y 轴对称\n"
        "2. 把 y 换成 -y，方程不变 → 关于 x 轴对称\n"
        "3. 把 (x,y) 换成 (-x,-y)，方程不变 → 关于原点对称\n"
        "原点是椭圆的中心（对称中心）。"
    ),
    E312Stage.VERTICES.value: (
        "学生刚确定了椭圆的四个顶点坐标：\n"
        "长轴端点 A₁(-a,0)、A₂(a,0)，长轴长=2a；\n"
        "短轴端点 B₁(0,-b)、B₂(0,b)，短轴长=2b。\n"
        "长轴是最长的弦（沿 x 轴），短轴沿 y 轴。"
    ),
    E312Stage.ECCENTRICITY.value: (
        "学生刚探索并定义了离心率：\n"
        "e = c/a（半焦距与长半轴之比），0<e<1。\n"
        "几何意义：e 越接近 1，椭圆越扁（越像线段）；"
        "e 越接近 0，椭圆越圆（越像正圆）。\n"
        "因为 c<a（焦点在长轴端点之内），所以 e 一定小于 1。"
    ),
}
