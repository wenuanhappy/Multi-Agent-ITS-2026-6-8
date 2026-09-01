# -*- coding: utf-8 -*-
"""费曼侧路：milestone 完成 / stage 切换时触发的「以教代学」轮次（2026-05-27 v0）。

**当前状态：v0 实现，未接入 lesson_flow.py（明日接入）。**

设计依据：多agent_pilot_3.1.2_执行计划.md §1.3
  · 触发：FSM 检测到 milestone 完全正确 / stage 即将切换
  · 侧路内：纯 LLM 自由对话（同学发起追问 → 学生答 → 老师/同学衔接 1–3 轮）
  · 退出：LLM-judge 判讲解完整度 / 超过 3 轮 / 学生主动 skip
  · **关键不变量：侧路不动 FSM 状态**（保护 §6.6.2 假推进 5.0% 不被搅乱）

模块设计：
  · 本模块**无状态**——FeynmanLoopState 由 lesson_flow 实例持有。
  · LLM 调用通过 callable 注入（FeynmanCallbacks），避免本模块耦合 llm_providers。
  · 任何回调失败 → exit_reason="llm_error"，回主线 FSM。
  · v0 简化：只做 1 轮"同学追问 + 学生答 + LLM-judge"；
    multi-turn 衔接（同学再追、老师补救）待 v1 扩展。

日志约定（lesson_flow 接入时落实到 interaction_logger）：
  · 侧路里每一轮的 event_type="feynman_loop"
  · agent="peer"（同学发问）/"teacher"（衔接）
  · 退出时记一条 exit_reason
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


# ---------------- 触发条件 ----------------

TRIGGER_MILESTONE_COMPLETED = "milestone_completed"
TRIGGER_STAGE_TRANSITION = "stage_transition"
VALID_TRIGGERS = (TRIGGER_MILESTONE_COMPLETED, TRIGGER_STAGE_TRANSITION)

# 退出原因
EXIT_JUDGE_PASS = "judge_pass"          # LLM-judge 判讲解完整
EXIT_JUDGE_FAIL = "judge_fail"          # 超 3 轮仍讲不清
EXIT_TURN_LIMIT = "turn_limit"          # 强制上限
EXIT_STUDENT_SKIP = "student_skip"      # 学生主动 skip
EXIT_LLM_ERROR = "llm_error"            # LLM 失败降级


# 学生 skip 的关键词（保守列表，命中其一即退出侧路）
_STUDENT_SKIP_KEYS = (
    "跳过", "下一题", "下一步", "skip", "next",
    "不想讲", "不想答", "继续上课", "继续主线",
)


@dataclass
class FeynmanLoopState:
    """一次费曼侧路的运行状态（lesson_flow 实例持有）。"""
    session_id: str
    course_type: str
    stage: str                              # 进入侧路时所处的 stage
    trigger: str                            # 见 VALID_TRIGGERS
    turn_count: int = 0
    max_turns: int = 3
    # history: [(agent_id, text), ...] —— 包含 peer/teacher/student 三类
    history: list = field(default_factory=list)
    exit_reason: Optional[str] = None       # 退出后填


@dataclass
class FeynmanCallbacks:
    """侧路调用所需的回调（由 lesson_flow 注入）。

    设计原则：本模块不直接调 llm_providers，让 lesson_flow 注入实际调用——
    便于单测 mock，便于 lesson_flow 复用现有 _llm_respond 通道。
    """
    # (system_prompt, user_text) -> str（失败应抛异常或返回空字符串）
    llm_call: Callable[[str, str], str]

    # (student_text, expected_topic) -> dict:
    #   {"complete": bool, "missing": list[str], "raw": str}
    llm_judge: Callable[[str, str], dict]

    # 黑名单后过滤：(text, course_type, stage) -> Optional[hit_word]
    spoiler_scan: Callable[[str, str, str], Optional[str]]

    # 兜底文案：(course_type, stage) -> str
    spoiler_fallback: Callable[[str, str], str]


# ---------------- 工具 ----------------

def _student_wants_skip(text: str) -> bool:
    """学生输入是否含主动 skip 关键词。"""
    if not text:
        return False
    low = text.strip().lower().replace(" ", "")
    return any(k in low for k in _STUDENT_SKIP_KEYS)


def _safe_llm_call_with_filter(
    cb: FeynmanCallbacks,
    *,
    system_prompt: str,
    user_text: str,
    course_type: str,
    stage: str,
    max_retry: int = 1,
) -> tuple[Optional[str], Optional[str]]:
    """调 LLM + 黑名单后过滤 + 命中重生（最多 max_retry 次）。

    Returns:
        (reply or None, hit_word or None)
        · reply 为 None = LLM 失败；调用方退出侧路
        · hit_word is not None 且 reply 已经是兜底文案 = 命中且重生仍命中
    """
    try:
        reply = cb.llm_call(system_prompt, user_text)
    except Exception as e:  # noqa: BLE001
        print(f"[feynman_loop] LLM 调用失败：{type(e).__name__}: {e}")
        return None, None
    if not reply:
        return None, None
    hit = cb.spoiler_scan(reply, course_type, stage)
    if hit is None:
        return reply, None
    # 命中：重生 1 次
    for _ in range(max_retry):
        try:
            reply = cb.llm_call(
                system_prompt + "\n\n[强制]你上次的回复触犯了黑名单，请彻底换一种说法。",
                user_text,
            )
        except Exception:
            return cb.spoiler_fallback(course_type, stage), hit
        hit2 = cb.spoiler_scan(reply, course_type, stage)
        if hit2 is None:
            return reply, None
        hit = hit2
    # 重生仍命中：退兜底
    return cb.spoiler_fallback(course_type, stage), hit


# ---------------- 对外 API ----------------

def should_enter(
    *,
    course_type: str,
    stage: str,
    milestone_just_completed: bool,
    stage_about_to_transition: bool,
    mode: str,
    recent_triggers_in_stage: int = 0,
    same_stage_throttle: int = 1,
) -> Optional[str]:
    """判断是否进入费曼侧路。

    Args:
        mode: settings.MULTI_AGENT_MODE，"off" 直接返回 None。
        milestone_just_completed: 主线刚判定 milestone（如 phase 完整答完）正确。
        stage_about_to_transition: 主线即将切换 stage（赋值新 stage 之前）。
        recent_triggers_in_stage: 本 stage 已经触发过的侧路次数（限频用）。
        same_stage_throttle: 同 stage 内最多触发次数（默认 1，避免连发）。

    Returns:
        触发原因（VALID_TRIGGERS 之一）或 None。
    """
    # 费曼侧路只在 C/D 档触发（有"同学"agent）；A/B/off 都不进
    # 渐进式消融（v2，2026-05-28）：
    #   A = 原系统（仅 UI）；B = A + anti-spoiler；C = B + 多 agent（同学+TA）；D = C + LLM 提议
    if mode not in ("c", "d"):
        return None
    # 限频：同 stage 已触发达上限
    if recent_triggers_in_stage >= same_stage_throttle:
        return None
    # 优先级：stage_transition 高于 milestone（避免 milestone + 紧接 transition 双触发）
    if stage_about_to_transition:
        return TRIGGER_STAGE_TRANSITION
    if milestone_just_completed:
        return TRIGGER_MILESTONE_COMPLETED
    return None


def enter_loop(
    state: FeynmanLoopState,
    cb: FeynmanCallbacks,
    *,
    peer_system_prompt: str,
    seed_text: str = "",
) -> tuple[Optional[str], str]:
    """侧路开场：同学发起一个追问。

    Args:
        state: 已构造好的 FeynmanLoopState（lesson_flow 创建并持有）。
        cb: 调用回调。
        peer_system_prompt: 由 agent_persona.build_system_prompt(PEER_PERSONA, ...) 生成。
        seed_text: 可选，给 peer LLM 的「上下文种子」，如"学生刚把椭圆范围推完，
            得到 -a≤x≤a"。peer 据此生成针对该内容的追问。

    Returns:
        (peer_question or None, agent_id="peer")
        · peer_question is None 表示 LLM 失败，调用方应直接结束侧路。
    """
    user_text = seed_text or "请你针对学生刚完成的这一步，提一个具体的、不剧透的追问。"
    reply, _hit = _safe_llm_call_with_filter(
        cb,
        system_prompt=peer_system_prompt,
        user_text=user_text,
        course_type=state.course_type,
        stage=state.stage,
    )
    if reply is None:
        state.exit_reason = EXIT_LLM_ERROR
        return None, "peer"
    state.history.append(("peer", reply))
    return reply, "peer"


def step_loop(
    state: FeynmanLoopState,
    student_text: str,
    cb: FeynmanCallbacks,
    *,
    peer_system_prompt: str,
    teacher_system_prompt: str,
    judge_topic: str,
) -> tuple[Optional[str], str, Optional[str]]:
    """侧路一轮：学生答 → LLM-judge → 老师/同学衔接 / 退出。

    v0 简化：
      · judge.complete=True → 老师一句肯定 + 退出（EXIT_JUDGE_PASS）
      · judge.complete=False 且 turn < max_turns → 同学再追一问，继续
      · turn >= max_turns → 老师兜底 + 退出（EXIT_TURN_LIMIT）
      · student 含 skip 关键词 → 立即退出（EXIT_STUDENT_SKIP）

    Args:
        state: FeynmanLoopState；本函数会原地更新 turn_count / history / exit_reason。
        student_text: 学生本轮输入。
        peer_system_prompt / teacher_system_prompt: 由 agent_persona 生成的对应 prompt。
        judge_topic: LLM-judge 的目标主题，如"椭圆离心率 e 的定义来源"。

    Returns:
        (reply_text or None, agent_id, exit_reason or None)
        · exit_reason is None 表示侧路继续；调用方保留 state
        · exit_reason 非 None 表示侧路结束；调用方应清掉 state，回主线
        · reply_text is None 仅在 EXIT_LLM_ERROR 时出现
    """
    state.turn_count += 1
    state.history.append(("student", student_text))

    # 1. 学生 skip？
    if _student_wants_skip(student_text):
        state.exit_reason = EXIT_STUDENT_SKIP
        return "好的，我们继续。", "teacher", EXIT_STUDENT_SKIP

    # 2. LLM-judge 判讲解完整度
    try:
        verdict = cb.llm_judge(student_text, judge_topic)
    except Exception as e:  # noqa: BLE001
        print(f"[feynman_loop] judge 失败：{type(e).__name__}: {e}")
        verdict = {"complete": False, "missing": [], "raw": ""}
    complete = bool(verdict.get("complete", False))

    # 3a. 完整 → 老师肯定 + 退出
    if complete:
        teacher_reply, _ = _safe_llm_call_with_filter(
            cb,
            system_prompt=teacher_system_prompt,
            user_text=f"学生刚刚把「{judge_topic}」讲清楚了，请用一句话肯定并衔接回主线。",
            course_type=state.course_type,
            stage=state.stage,
        )
        teacher_reply = teacher_reply or "讲得不错，我们继续。"
        state.exit_reason = EXIT_JUDGE_PASS
        state.history.append(("teacher", teacher_reply))
        return teacher_reply, "teacher", EXIT_JUDGE_PASS

    # 3b. 不完整 + 还有轮数 → 同学再追一问
    if state.turn_count < state.max_turns:
        missing = ", ".join(verdict.get("missing", [])[:3])
        followup_seed = (
            f"学生刚才的解释还差点意思（缺失要点：{missing or '关键依据'}）——"
            f"请你再追一个**具体而不剧透**的问题，引学生补足。"
        )
        peer_reply, _ = _safe_llm_call_with_filter(
            cb,
            system_prompt=peer_system_prompt,
            user_text=followup_seed,
            course_type=state.course_type,
            stage=state.stage,
        )
        if peer_reply is None:
            state.exit_reason = EXIT_LLM_ERROR
            return None, "peer", EXIT_LLM_ERROR
        state.history.append(("peer", peer_reply))
        return peer_reply, "peer", None  # 继续

    # 3c. 超轮数 → 老师兜底 + 退出（不剧透）
    state.exit_reason = EXIT_TURN_LIMIT
    teacher_reply = (
        "没关系，这点稍微绕一些。我们先继续主线，"
        "等会例题里你会再遇到这个概念，到时候再多体会一下。"
    )
    state.history.append(("teacher", teacher_reply))
    return teacher_reply, "teacher", EXIT_TURN_LIMIT


__all__ = [
    "TRIGGER_MILESTONE_COMPLETED", "TRIGGER_STAGE_TRANSITION", "VALID_TRIGGERS",
    "EXIT_JUDGE_PASS", "EXIT_JUDGE_FAIL", "EXIT_TURN_LIMIT",
    "EXIT_STUDENT_SKIP", "EXIT_LLM_ERROR",
    "FeynmanLoopState", "FeynmanCallbacks",
    "should_enter", "enter_loop", "step_loop",
]
