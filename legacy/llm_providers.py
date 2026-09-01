# -*- coding: utf-8 -*-
"""LLM Provider 抽象层：Claude 主 + DeepSeek 兜底（V4-flash → V4-pro）。

设计原则（与 lesson_flow 架构对齐）：
  · 每个 provider 把第三方异常映射成本模块的统一类别（BillingError 等）
  · MultiProvider 按错误类别决定"重试 / 切下一个 / 直接报错"
  · 完全不依赖新包：anthropic + httpx（项目已装）

错误分类约定（从用户给的策略）：
  BillingError   → 立刻切下一个 provider，不重试
  AuthError      → 配置错误，不要静默吞掉 → raise
  RateLimitError → 短重试 1 次后切
  ServerError    → 重试 1-2 次后切
  TimeoutError   → 同 ServerError（网络抖动）
  BadRequestError→ 400 内容问题，切下一个（同一 provider 重试无意义）
  ValidationError→ 输出不符合 validator（如 JSON 解析失败），切下一个
"""
from __future__ import annotations
import contextvars
import os
import time
from typing import Any, Callable, List, Optional

import httpx

# 记录每轮实际成功的 provider（contextvars 并发安全；供实验数据甄别 claude / deepseek-*）
last_provider: "contextvars.ContextVar" = contextvars.ContextVar("last_provider", default=None)

# ────────────────────── 统一异常类别 ──────────────────────

class LLMProviderError(Exception):
    """所有 provider 异常的基类。"""

class BillingError(LLMProviderError):
    """余额不足 / 欠费 / 套餐用尽 —— 切下一个 provider，不要重试。"""

class AuthError(LLMProviderError):
    """API key 无效 / 401 / 403 —— **配置错误**，不要静默吞掉，直接 raise。"""

class RateLimitError(LLMProviderError):
    """429 —— 短重试后切。"""

class ServerError(LLMProviderError):
    """5xx —— 后端暂时故障，重试后切。"""

class TimeoutError(LLMProviderError):  # noqa: A001 — 故意 shadow，本模块内只用本类
    """网络超时（多见于跨境访问 api.anthropic.com）。"""

class BadRequestError(LLMProviderError):
    """400 —— 请求格式 / 模型 ID / 参数有问题。重试无意义，切下一个。"""

class ValidationError(LLMProviderError):
    """输出通过了 API 但不满足 validator（如 JSON 解析失败、空内容）。"""


# ────────────────────── 抽象基类 ──────────────────────

class LLMProvider:
    """每个 provider 实现 complete()，失败抛上面定义的统一异常。

    2026-05-28 新增 system_blocks 可选参数（prompt caching 支持）：
      · None（默认）：用 system 字符串发 API，无缓存
      · List[dict]：用 anthropic list 形式发 API，可在 block 上挂 cache_control
        每个 dict 形如 {"type": "text", "text": "...", "cache_control": {"type": "ephemeral"}?}
      · 提供 system_blocks 时 system 参数应为空字符串（被忽略）
      · 非 Anthropic provider（DeepSeek）会合并 blocks 文本为字符串，忽略 cache_control
    """
    name: str = "abstract"

    def complete(self, system: str, user: str, *,
                 max_tokens: int = 800, temperature: float = 0.4,
                 json_mode: bool = False,
                 system_blocks: Optional[List[dict]] = None) -> str:
        raise NotImplementedError


# ────────────────────── Claude（anthropic SDK） ──────────────────────

class ClaudeProvider(LLMProvider):
    name = "claude"

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        import anthropic  # 延迟 import，未安装也不影响 DeepSeekProvider
        self._anthropic = anthropic
        self.client = anthropic.Anthropic(api_key=api_key, timeout=httpx.Timeout(45.0))
        self.model = model

    def complete(self, system, user, *, max_tokens=800, temperature=0.4, json_mode=False,
                 system_blocks: Optional[List[dict]] = None):
        # anthropic SDK 没有 native json_mode；JSON 控制在 system prompt 里做
        # 2026-05-28：支持 system_blocks（list 形式带 cache_control）
        if system_blocks is not None and len(system_blocks) > 0:
            system_payload = system_blocks  # SDK 接受 List[{"type": "text", ...}]
        else:
            system_payload = system
        try:
            resp = self.client.messages.create(
                model=self.model, max_tokens=max_tokens, temperature=temperature,
                system=system_payload,
                messages=[{"role": "user", "content": user}],
            )
            text = resp.content[0].text.strip() if resp.content else ""
            if not text:
                raise ValidationError("claude returned empty text")
            # 调试：如果有 cache 命中/写入，打印（usage 字段含 cache_read_input_tokens / cache_creation_input_tokens）
            try:
                usage = getattr(resp, "usage", None)
                cr = getattr(usage, "cache_read_input_tokens", 0) if usage else 0
                cc = getattr(usage, "cache_creation_input_tokens", 0) if usage else 0
                if cr or cc:
                    print(f"[LLM.cache] claude cache: read={cr}, write={cc}")
            except Exception:
                pass
            return text
        except self._anthropic.AuthenticationError as e:
            raise AuthError(f"claude auth failed: {e}") from e
        except self._anthropic.PermissionDeniedError as e:
            # 403 多见于 "your credit balance is too low" → 当作 billing
            msg = str(e).lower()
            if "credit" in msg or "balance" in msg or "billing" in msg:
                raise BillingError(f"claude billing: {e}") from e
            raise AuthError(f"claude permission denied: {e}") from e
        except self._anthropic.RateLimitError as e:
            raise RateLimitError(f"claude rate limit: {e}") from e
        except self._anthropic.BadRequestError as e:
            # 400 也可能是 "credit balance is too low"
            msg = str(e).lower()
            body = getattr(e, "body", "") or ""
            full = msg + " " + str(body).lower()
            if "credit" in full or "balance" in full or "insufficient" in full:
                raise BillingError(f"claude billing (in 400): {e}") from e
            raise BadRequestError(f"claude bad request: {e}") from e
        except self._anthropic.APITimeoutError as e:
            raise TimeoutError(f"claude timeout: {e}") from e
        except self._anthropic.APIConnectionError as e:
            raise TimeoutError(f"claude connection: {e}") from e
        except self._anthropic.InternalServerError as e:
            raise ServerError(f"claude 5xx: {e}") from e
        except Exception as e:
            # 其他未分类异常归到 ServerError（保守，让 MultiProvider 还能切）
            raise ServerError(f"claude unknown: {type(e).__name__}: {e}") from e


# ────────────────────── DeepSeek（httpx 直连，OpenAI 兼容） ──────────────────────

class DeepSeekProvider(LLMProvider):
    """DeepSeek OpenAI-compatible endpoint。
    支持 thinking_disabled（V4 系列默认 thinking on，稳定 JSON 必须关）。"""

    BASE_URL = "https://api.deepseek.com/v1/chat/completions"

    def __init__(self, api_key: str, model: str = "deepseek-v4-flash",
                 thinking_enabled: bool = False, name_suffix: str = ""):
        self.api_key = api_key
        self.model = model
        self.thinking_enabled = thinking_enabled
        self.name = f"deepseek-{model.replace('deepseek-', '')}{name_suffix}"

    def complete(self, system, user, *, max_tokens=800, temperature=0.4, json_mode=False,
                 system_blocks: Optional[List[dict]] = None):
        # DeepSeek 不支持 cache_control —— 把 blocks 合并成字符串
        if system_blocks is not None and len(system_blocks) > 0:
            system = "\n\n".join(
                (b.get("text") or "") for b in system_blocks if isinstance(b, dict)
            )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            # thinking 跟 json_mode 完全解耦——按 init 时的配置发
            "thinking": {"type": "enabled" if self.thinking_enabled else "disabled"},
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            r = httpx.post(self.BASE_URL, json=payload, headers=headers, timeout=60.0)
        except httpx.TimeoutException as e:
            raise TimeoutError(f"deepseek timeout: {e}") from e
        except httpx.HTTPError as e:
            raise TimeoutError(f"deepseek network: {e}") from e

        if r.status_code == 200:
            data = r.json()
            choices = data.get("choices") or []
            if not choices:
                raise ValidationError(f"deepseek empty choices: {data}")
            text = (choices[0].get("message") or {}).get("content", "").strip()
            if not text:
                raise ValidationError("deepseek returned empty text")
            return text

        # 错误状态码 → 映射类别
        body = r.text[:500]
        if r.status_code == 401:
            raise AuthError(f"deepseek 401: {body}")
        if r.status_code == 402:
            raise BillingError(f"deepseek 402 billing: {body}")
        if r.status_code == 403:
            raise AuthError(f"deepseek 403: {body}")
        if r.status_code == 429:
            raise RateLimitError(f"deepseek 429: {body}")
        if 500 <= r.status_code < 600:
            raise ServerError(f"deepseek {r.status_code}: {body}")
        if r.status_code == 400:
            raise BadRequestError(f"deepseek 400: {body}")
        raise ServerError(f"deepseek {r.status_code} (unmapped): {body}")


# ────────────────────── MiniMax（阿里云 PAI-EAS 部署） ──────────────────────

class MiniMaxProvider(LLMProvider):
    """MiniMax OpenAI-compatible endpoint on 阿里云 PAI-EAS.

    部署信息:
    - 端点: http://1517457097276560.cn-wulanchabu.pai-eas.aliyuncs.com/api/predict/minimax_27_int8/v1
    - 模型: minimax_27_int8
    """
    BASE_URL = "http://1517457097276560.cn-wulanchabu.pai-eas.aliyuncs.com/api/predict/minimax_27_int8/v1"

    def __init__(self, api_key: str, model: str = "minimax_27_int8"):
        self.api_key = api_key
        self.model = model
        self.name = "minimax"

    def complete(self, system, user, *, max_tokens=800, temperature=0.4, json_mode=False,
                 system_blocks: Optional[List[dict]] = None):
        if system_blocks is not None and len(system_blocks) > 0:
            system = "\n\n".join(
                (b.get("text") or "") for b in system_blocks if isinstance(b, dict)
            )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            r = httpx.post(self.BASE_URL, json=payload, headers=headers, timeout=120.0)
        except httpx.TimeoutException as e:
            raise TimeoutError(f"minimax timeout: {e}") from e
        except httpx.HTTPError as e:
            raise TimeoutError(f"minimax network: {e}") from e

        if r.status_code == 200:
            data = r.json()
            choices = data.get("choices") or []
            if not choices:
                raise ValidationError(f"minimax empty choices: {data}")
            text = (choices[0].get("message") or {}).get("content", "").strip()
            if not text:
                raise ValidationError("minimax returned empty text")
            return text

        body = r.text[:500]
        if r.status_code == 401:
            raise AuthError(f"minimax 401: {body}")
        if r.status_code == 402:
            raise BillingError(f"minimax 402 billing: {body}")
        if r.status_code == 403:
            raise AuthError(f"minimax 403: {body}")
        if r.status_code == 429:
            raise RateLimitError(f"minimax 429: {body}")
        if 500 <= r.status_code < 600:
            raise ServerError(f"minimax {r.status_code}: {body}")
        if r.status_code == 400:
            raise BadRequestError(f"minimax 400: {body}")
        raise ServerError(f"minimax {r.status_code} (unmapped): {body}")


# ────────────────────── 多 Provider 编排 ──────────────────────

# 单个 provider 在不同错误类别下的最大尝试次数（含首次）
_MAX_ATTEMPTS = {
    RateLimitError: 2,    # 1 次重试
    ServerError:    3,    # 2 次重试
    TimeoutError:   3,    # 2 次重试
}
_DEFAULT_MAX_ATTEMPTS = 1   # 其余类别只试 1 次

# 重试间隔（秒），指数退避
def _backoff(attempt: int) -> float:
    return min(2 ** attempt, 4.0)


class MultiProvider(LLMProvider):
    """按顺序尝试若干 provider，按错误类别决定"重试 / 切 / 抛"。"""
    name = "multi"

    def __init__(self, providers: List[LLMProvider]):
        if not providers:
            raise ValueError("MultiProvider needs at least 1 provider")
        self.providers = providers

    def complete(self, system, user, *, max_tokens=800, temperature=0.4,
                 json_mode=False,
                 system_blocks: Optional[List[dict]] = None,
                 validator: Optional[Callable[[str], bool]] = None) -> str:
        last_exc: Optional[Exception] = None
        for p in self.providers:
            max_attempts = _DEFAULT_MAX_ATTEMPTS
            for attempt in range(1, 10):  # 实际上限由 break 控制
                try:
                    text = p.complete(system, user, max_tokens=max_tokens,
                                      temperature=temperature, json_mode=json_mode,
                                      system_blocks=system_blocks)
                    if validator and not validator(text):
                        # 通过了 API 但内容不符合（如 JSON 解析失败）→ 当 ValidationError 处理
                        raise ValidationError(f"validator rejected: {text[:120]!r}")
                    print(f"[LLM] ✅ {p.name} 成功（attempt {attempt}）")
                    last_provider.set(p.name)
                    return text
                except AuthError as e:
                    # **配置错误**——立刻 raise，不要静默吞，不要切下一个
                    print(f"[LLM] 🔑 {p.name} AUTH 错误：{e}")
                    raise
                except BillingError as e:
                    print(f"[LLM] 💳 {p.name} 余额不足，立刻切下一个：{e}")
                    last_exc = e
                    break
                except RateLimitError as e:
                    last_exc = e
                    max_attempts = _MAX_ATTEMPTS[RateLimitError]
                    if attempt < max_attempts:
                        wait = _backoff(attempt)
                        print(f"[LLM] 🛑 {p.name} 限流（{attempt}/{max_attempts}），{wait}s 后重试")
                        time.sleep(wait)
                        continue
                    print(f"[LLM] 🛑 {p.name} 限流次数耗尽，切下一个")
                    break
                except (ServerError, TimeoutError) as e:
                    last_exc = e
                    max_attempts = _MAX_ATTEMPTS[ServerError]
                    if attempt < max_attempts:
                        wait = _backoff(attempt)
                        print(f"[LLM] ⚠️ {p.name} 暂时故障（{attempt}/{max_attempts}）：{e}；{wait}s 后重试")
                        time.sleep(wait)
                        continue
                    print(f"[LLM] ⚠️ {p.name} 多次故障，切下一个：{e}")
                    break
                except (BadRequestError, ValidationError) as e:
                    print(f"[LLM] 🚫 {p.name} 内容/校验失败，切下一个：{e}")
                    last_exc = e
                    break
                except Exception as e:
                    # 未分类异常 —— 保守当成可切（防止整个流程挂死）
                    print(f"[LLM] ❓ {p.name} 未分类异常：{type(e).__name__}: {e}")
                    last_exc = e
                    break
        # 所有 provider 跑完都没成功
        raise LLMProviderError(
            f"all {len(self.providers)} providers exhausted; last: {last_exc!r}"
        ) from last_exc


# ────────────────────── 工厂：按环境变量装配默认 chain ──────────────────────

# 默认使用 MiniMax 作为主模型
# 任一缺 key 自动跳过；全缺返回 None（调用方走纯 deterministic fallback）

def build_default_multi_provider(verbose: bool = True) -> Optional[MultiProvider]:
    """按 .env 装配 provider 链：
        1) MiniMax（主力，阿里云 PAI-EAS 部署）
        2) DeepSeek flash（兜底）

    任一层 key 缺失自动跳过；全无返回 None。
    """
    providers: List[LLMProvider] = []

    # 1) MiniMax（主力）
    from config.settings import MINIMAX_API_KEY, MINIMAX_MODEL
    if MINIMAX_API_KEY:
        try:
            providers.append(MiniMaxProvider(MINIMAX_API_KEY, model=MINIMAX_MODEL))
            if verbose: print(f"[LLM] 装配 MiniMaxProvider（model={MINIMAX_MODEL}）")
        except Exception as e:
            if verbose: print(f"[LLM] ⚠️ MiniMax 装配失败：{e}")

    # 2) DeepSeek flash（兜底）
    dk = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if dk:
        flash_model = os.environ.get("DEEPSEEK_MODEL_FLASH", "deepseek-v4-flash")
        try:
            providers.append(DeepSeekProvider(dk, model=flash_model,
                                              thinking_enabled=False, name_suffix=""))
            if verbose: print(f"[LLM] 装配 DeepSeekProvider flash（model={flash_model}, thinking=disabled）")
        except Exception as e:
            if verbose: print(f"[LLM] ⚠️ DeepSeek 装配失败：{e}")

    if not providers:
        if verbose: print("[LLM] ⚠️ 无可用 provider（未配置 MINIMAX_API_KEY 也未配置 DEEPSEEK_API_KEY）")
        return None
    if verbose:
        print(f"[LLM] 链路总长 {len(providers)} 层：{' → '.join(p.name for p in providers)}")
    return MultiProvider(providers)
