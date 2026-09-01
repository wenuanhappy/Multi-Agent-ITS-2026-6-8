"""
FastAPI 服务器 — Multi-Agent ITS (CrewAI)
基于 CrewAI 多智能体框架的苏格拉底式数学教学系统

API 兼容前端 interactive.html 的调用方式。
路由策略：
  - ellipse_312 → CrewAI TutoringFlow（真正的多智能体架构）
  - 其余5课 → legacy.LessonFlow（原系统逻辑，功能完全一致）
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
import sys
from pathlib import Path
from typing import Optional, Union

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

# 必须在任何 CrewAI 导入之前加载 config（设置 litellm.drop_params=True）
import config.settings  # noqa: F401 — 触发 anthropic SDK patch

from flow.tutoring_flow import TutoringFlow
from legacy.lesson_flow import LessonFlow as LegacyLessonFlow

# 只有 ellipse_312 走 CrewAI，其余走 legacy
CREWAI_COURSES = {"ellipse_312"}

# ============================================================
# FastAPI 应用
# ============================================================

app = FastAPI(
    title="Multi-Agent ITS (CrewAI)",
    description="基于 CrewAI 多智能体框架的苏格拉底式高中数学教学系统",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def _enlarge_thread_pool():
    """调大默认线程池，让多名学生的同步 LLM 调用并行而非排队。"""
    loop = asyncio.get_running_loop()
    loop.set_default_executor(ThreadPoolExecutor(max_workers=32, thread_name_prefix="llm"))
    print("[server] 默认线程池已调大至 32 workers")


# 前端文件
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

# 前端静态资源（头像 / icon 等）
_FRONTEND_STATIC = os.path.join(FRONTEND_DIR, "static")
if os.path.isdir(_FRONTEND_STATIC):
    app.mount("/static", StaticFiles(directory=_FRONTEND_STATIC), name="frontend_static")

# 会话存储：value 可能是 TutoringFlow (CrewAI) 或 LegacyLessonFlow
lesson_sessions: dict[str, Union[TutoringFlow, LegacyLessonFlow]] = {}


# ============================================================
# 数据模型
# ============================================================

class LessonMessageRequest(BaseModel):
    message: str


class LessonEventRequest(BaseModel):
    event: str
    payload: dict = {}


# ============================================================
# 辅助函数
# ============================================================

def _get_or_create_lesson(session_id: str) -> Union[TutoringFlow, LegacyLessonFlow]:
    if session_id not in lesson_sessions:
        # 默认创建 CrewAI flow（正常不会走到这，因为 start 总先调用）
        lesson_sessions[session_id] = TutoringFlow()
        print(f"[Lesson] 新建探索课会话(fallback): {session_id}")
    return lesson_sessions[session_id]


def _step_to_dict(step) -> dict:
    """统一序列化：CrewAI 返回 dict，legacy 返回 LessonStep dataclass。"""
    if isinstance(step, dict):
        return {
            "stage": step.get("stage", ""),
            "message": step.get("message", ""),
            "canvas_action": step.get("canvas_action", None),
            "expect_event": step.get("expect_event", None),
            "agent": step.get("agent", "teacher"),
            "event_type": step.get("event_type", "normal"),
        }
    # legacy LessonStep dataclass
    return {
        "stage": getattr(step, "stage", ""),
        "message": getattr(step, "message", ""),
        "canvas_action": getattr(step, "canvas_action", None),
        "expect_event": getattr(step, "expect_event", None),
        "agent": "teacher",
        "event_type": "normal",
    }


# ============================================================
# 前端页面
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def serve_root():
    """根路径 → 课程选择主页"""
    return await _serve_html("dispatcher.html")


@app.get("/section", response_class=HTMLResponse)
async def serve_section():
    """小节选择页（椭圆/双曲线/抛物线的子课程）"""
    return await _serve_html("section.html")


@app.get("/interactive", response_class=HTMLResponse)
async def serve_interactive():
    """交互式探索课前端页面（JSXGraph 版）"""
    return await _serve_html("interactive.html")


async def _serve_html(filename: str):
    path = os.path.join(FRONTEND_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content=f"<h1>frontend/{filename} 未找到</h1>")


# ============================================================
# REST API — 交互式探索课
# ============================================================

@app.post("/api/lesson/{session_id}/start")
async def lesson_start(session_id: str, course: str = "ellipse_312"):
    """开始课程。ellipse_312 走 CrewAI，其余走 legacy。"""
    if course in CREWAI_COURSES:
        flow = TutoringFlow()
        lesson_sessions[session_id] = flow
        print(f"[Lesson] CrewAI 会话: {session_id} (course={course})")
        result = flow.initialize()
    else:
        flow = LegacyLessonFlow(course_type=course)
        lesson_sessions[session_id] = flow
        print(f"[Lesson] Legacy 会话: {session_id} (course={course})")
        result = flow.start()
    return _step_to_dict(result)


@app.post("/api/lesson/{session_id}/message")
async def lesson_message(session_id: str, req: LessonMessageRequest):
    """处理学生消息。LLM 调用是阻塞的，放到线程池执行。"""
    flow = _get_or_create_lesson(session_id)
    try:
        if isinstance(flow, TutoringFlow):
            step = await asyncio.to_thread(flow.process_student_message, req.message)
        else:
            # legacy LessonFlow 的方法名是 on_student_message
            step = await asyncio.to_thread(flow.on_student_message, req.message)
        return _step_to_dict(step)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"[Lesson ERROR] {e}\n{tb}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/lesson/{session_id}/event")
async def lesson_event(session_id: str, req: LessonEventRequest):
    """处理画布事件（如顶点点击、线段点击等）。"""
    flow = _get_or_create_lesson(session_id)
    step = flow.on_canvas_event(req.event, req.payload)
    if step is None:
        # CrewAI flow 的 state 是 Pydantic model，legacy 的 state() 是方法返回 dict
        if isinstance(flow, TutoringFlow):
            stage = flow.state.stage
        else:
            stage = flow.stage.value if hasattr(flow.stage, 'value') else str(flow.stage)
        return {
            "stage": stage,
            "message": None,
            "canvas_action": None,
            "expect_event": None,
            "agent": "teacher",
            "event_type": "normal",
        }
    return _step_to_dict(step)


@app.get("/api/lesson/{session_id}/state")
async def lesson_state(session_id: str):
    """获取当前课程状态。"""
    flow = _get_or_create_lesson(session_id)
    if isinstance(flow, TutoringFlow):
        return {
            "stage": flow.state.stage,
            "lesson_ended": flow.state.lesson_ended,
            "feynman_active": flow.state.feynman_active,
            "history_length": len(flow.state.history),
        }
    else:
        state = flow.state()
        return {
            "stage": state.get("stage", ""),
            "lesson_ended": flow.lesson_ended,
            "feynman_active": False,
            "history_length": len(flow.history),
        }


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8300)
