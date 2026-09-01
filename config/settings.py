"""
Multi-Agent ITS Configuration
基于CrewAI框架的多智能体交互教学系统配置
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Fix: CrewAI + Anthropic strict tools 兼容性 ──
# CrewAI 给 tool schema 加了 strict=true（OpenAI 专属），Claude API 拒绝。
# 新版 CrewAI 不用 litellm，直接走 anthropic SDK。
# 方案：patch anthropic.resources.messages.Messages.create，剥掉 tools 里的 strict。
try:
    import anthropic.resources.messages as _arm

    def _strip_strict(tools):
        """递归剥掉 tool 定义里的 strict 字段。"""
        if not tools:
            return tools
        cleaned = []
        for tool in tools:
            if isinstance(tool, dict):
                t = {k: v for k, v in tool.items() if k != "strict"}
                if "input_schema" in t and isinstance(t["input_schema"], dict):
                    t["input_schema"] = {
                        k: v for k, v in t["input_schema"].items() if k != "strict"
                    }
                cleaned.append(t)
            else:
                cleaned.append(tool)
        return cleaned

    # Patch 同步 create
    _orig_create = _arm.Messages.create
    def _patched_create(self, *args, **kwargs):
        if "tools" in kwargs:
            kwargs["tools"] = _strip_strict(kwargs["tools"])
        return _orig_create(self, *args, **kwargs)
    _arm.Messages.create = _patched_create

    # Patch 异步 create（CrewAI 可能走 async）
    if hasattr(_arm, "AsyncMessages"):
        _orig_async_create = _arm.AsyncMessages.create
        async def _patched_async_create(self, *args, **kwargs):
            if "tools" in kwargs:
                kwargs["tools"] = _strip_strict(kwargs["tools"])
            return await _orig_async_create(self, *args, **kwargs)
        _arm.AsyncMessages.create = _patched_async_create

    print("[config] anthropic SDK patched: strict tools will be stripped")
except Exception as e:
    print(f"[config] anthropic SDK patch failed: {e}")

# ── LLM Configuration ──
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# ── MiniMax Configuration (阿里云 PAI-EAS 部署) ──
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = os.getenv("MINIMAX_BASE_URL", "http://1517457097276560.cn-wulanchabu.pai-eas.aliyuncs.com/api/predict/minimax_27_int8/v1")
MINIMAX_MODEL = os.getenv("MINIMAX_MODEL", "minimax_27_int8")

# CrewAI uses litellm format for model names
# 使用 MiniMax 作为主模型（所有 LLM 调用都使用 MiniMax-2.7-INT8）
CREWAI_LLM = f"openai/{MINIMAX_MODEL}"
# function_calling_llm 也使用 MiniMax
CREWAI_LLM_FALLBACK = f"openai/{MINIMAX_MODEL}"

# ── Server Configuration ──
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8300"))  # 8300 to avoid conflict with 8000/8100/8200

# ── Multi-Agent Mode ──
# CrewAI版默认运行C模式（完整多Agent：教师+反剧透+助教+同伴）
# 保留模式标识供论文消融实验描述使用
MULTI_AGENT_MODE = "c"

# ── litellm 配置：自定义 MiniMax 端点 ──
os.environ["LITELLM_CUSTOM_API_BASE"] = MINIMAX_BASE_URL
os.environ["LITELLM_API_KEY"] = MINIMAX_API_KEY
os.environ["LITELLM_SENTINEL"] = "custom-minimax"  # 标记自定义端点

# ── Knowledge Graph ──
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

# ── Logging ──
LOG_DIR = os.getenv("LOG_DIR", "logs")

# ── Temperature & Token Limits ──
LLM_TEMPERATURE = 0.4
LLM_MAX_TOKENS = 800
CLASSIFIER_MAX_TOKENS = 20
CLASSIFIER_TEMPERATURE = 0.0
