# -*- coding: utf-8 -*-
"""交互日志采集器（实验数据用）。

设计原则：
  · 纯旁路：只读取 server 已生成的 step / state，不参与教学逻辑、不改任何返回值。
  · 静默容错：任何写盘异常都被吞掉并打印告警，绝不影响正在进行的课程。
  · 行级安全：JSONL append，每行一条；多 session 并发按 session_id 分文件 + 全局锁。
  · 零依赖 lesson_flow：只接收 server 层能拿到的字段；不碰教学核心。

用途：
  1. 教学效果实验——对话轮数 / viz 频率 / phase 停留时长（由相邻 turn 时间戳算）。
  2. 消融 benchmark 的输入来源——学生输入序列 + 可重建的多轮上下文。
诊断标签不在此采集（实时用完即丢）；消融实验在脚手架层用 monkey-patch 获取。

适配说明（Multi-Agent-ITS / CrewAI 版）：
  · 交互日志落盘模块
  · 日志目录计算调整为 Multi-Agent-ITS 的项目根
  · _PROJECT_ROOT: __file__ = <PROJECT_ROOT>/core/interaction_logger.py → dirname x2
"""
from __future__ import annotations
import json
import os
import threading
from datetime import datetime, timezone
from typing import Any, Optional

# 日志目录：<PROJECT_ROOT>/logs/raw_logs/
#   __file__ = <PROJECT_ROOT>/core/interaction_logger.py
#   dirname×2 = PROJECT_ROOT
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEFAULT_LOG_DIR = os.path.join(_PROJECT_ROOT, "logs", "raw_logs")

_lock = threading.Lock()


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="milliseconds")


class InteractionLogger:
    """按 session_id 分文件、append JSONL 的旁路采集器。"""

    def __init__(self, log_dir: Optional[str] = None) -> None:
        self.log_dir = log_dir or os.environ.get("EXP_LOG_DIR", _DEFAULT_LOG_DIR)
        self._turn_idx: dict[str, int] = {}
        try:
            os.makedirs(self.log_dir, exist_ok=True)
        except Exception as e:  # noqa: BLE001
            print(f"[ExpLogger] cannot create log dir {self.log_dir}: {e}")

    def _path(self, session_id: str) -> str:
        safe = "".join(c for c in session_id if c.isalnum() or c in "-_") or "unknown"
        return os.path.join(self.log_dir, f"{safe}.jsonl")

    def _write(self, session_id: str, record: dict) -> None:
        """append 一条记录；任何异常静默（绝不影响上课）。"""
        try:
            line = json.dumps(record, ensure_ascii=False)
            with _lock:
                with open(self._path(session_id), "a", encoding="utf-8") as f:
                    f.write(line + "\n")
                    f.flush()
        except Exception as e:  # noqa: BLE001
            print(f"[ExpLogger] write failed (ignored): {e}")

    def _next_turn(self, session_id: str) -> int:
        n = self._turn_idx.get(session_id, 0) + 1
        self._turn_idx[session_id] = n
        return n

    # ---- 三个采集入口（对应 server 三个路由）----

    def log_start(self, session_id: str, course_type: str) -> None:
        self._turn_idx[session_id] = 0
        self._write(session_id, {
            "type": "start", "ts": _now_iso(),
            "session_id": session_id, "course_type": course_type,
        })

    def log_turn(self, session_id: str, *, student_input: str, step: Any,
                 state: dict, latency_ms: int, provider: Optional[str] = None,
                 agent: str = "teacher", event_type: str = "normal",
                 internal_actions: Optional[dict] = None) -> None:
        """记录一轮交互。

        字段说明：
          · agent: "teacher" / "peer" / "ta"——本轮回复来自哪个 agent
          · event_type: 本轮事件类型，可能值：
            - normal              : 主线常规一轮
            - feynman_loop        : 学生在费曼侧路里的一轮
            - fallback            : anti-spoiler 命中且重生仍命中，退回 stage 兜底文案
            - probe               : 标准化对抗探针注入（事后重放）
            - llm_propose_advance : LLM 协议提议 advance 且 FSM 复核通过
            - llm_propose_peer    : LLM 启发式提议同学出场且 FSM 软门控通过
            - fsm_reject          : 提议被 FSM 否决

          · internal_actions：本轮内部决策埋点（anti-spoiler/TA/peer 触发等）
        """
        ca = getattr(step, "canvas_action", None)
        rec = {
            "type": "turn", "ts": _now_iso(),
            "session_id": session_id,
            "turn_idx": self._next_turn(session_id),
            "course_type": state.get("course_type"),
            "stage": state.get("stage"),
            "student_input": student_input,
            "tutor_reply": getattr(step, "message", None),
            "provider": provider,  # 本轮实际成功的 LLM（None=走了预设兜底文本）
            "has_viz": self._detect_viz(ca),
            "canvas_action_type": self._action_types(ca),  # 原始 action 名全记
            "slider_changes": state.get("slider_changes"),
            "history_len": state.get("history_len"),
            "latency_ms": latency_ms,
            "agent": agent,
            "event_type": event_type,
        }
        if internal_actions:
            rec["internal_actions"] = internal_actions
        self._write(session_id, rec)

    def log_event(self, session_id: str, *, event: str, payload: dict,
                  state: dict) -> None:
        self._write(session_id, {
            "type": "event", "ts": _now_iso(),
            "session_id": session_id,
            "event": event, "payload": payload,
            "stage": state.get("stage"),
        })

    # ---- 工具：从 canvas_action 提取信息（容错，未知结构返回保守值）----

    @staticmethod
    def _action_types(canvas_action: Any) -> list:
        if not canvas_action:
            return []
        items = canvas_action if isinstance(canvas_action, list) else [canvas_action]
        return [a.get("action") for a in items if isinstance(a, dict) and a.get("action")]

    @classmethod
    def _detect_viz(cls, canvas_action: Any) -> bool:
        if not canvas_action:
            return False
        items = canvas_action if isinstance(canvas_action, list) else [canvas_action]
        for a in items:
            if isinstance(a, dict):
                act = str(a.get("action", "")).lower()
                if "viz" in act or "generated" in act or a.get("code"):
                    return True
        return False
