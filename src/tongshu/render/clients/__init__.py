"""LLM renderer clients (T501).

Factory: `get_llm_client()` gates on API-key presence in the environment —
no key → None (caller defaults to the deterministic Stub); key → a real
OpenAI-compatible client (DeepSeek by default). This is the env 门控 that
lets every consumer (demo / golden / API) flip between Stub and real LLM
without code changes.
"""

from __future__ import annotations
import logging
import os
from pathlib import Path

from .openai_compat import OpenAICompatLLMClient, RenderClientError

log = logging.getLogger(__name__)

__all__ = ["OpenAICompatLLMClient", "RenderClientError", "get_llm_client"]


def _load_env_file() -> None:
    """Load backend/.env (or $TONGSHU_ENV_FILE) so the API key never has to
    live in a shell/command line. No-op if python-dotenv is missing."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    path = os.environ.get("TONGSHU_ENV_FILE") or str(
        Path(__file__).resolve().parents[4] / ".env"  # backend/.env
    )
    if Path(path).is_file():
        load_dotenv(path)


_load_env_file()


def get_llm_client() -> OpenAICompatLLMClient | None:
    """Return a real client if an API key is configured, else None.

    Callers that need a client unconditionally fall back to StubLLMClient
    when this returns None (see renderer.Renderer.__init__).
    """
    api_key = os.environ.get("TONGSHU_LLM_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        return None
    try:
        return OpenAICompatLLMClient(api_key=api_key)
    except RenderClientError:
        log.exception("Failed to build LLM client; falling back to Stub")
        return None
