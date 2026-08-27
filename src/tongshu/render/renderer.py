"""Renderer — invokes LLM with Render Request + SIR.

This module is the actual integration point with the external LLM API.
Per architecture_decisions_v1.md §0.2, the Renderer MUST NOT modify
SIR content; it only translates.

T501 (2026-08-17): multi-signal capacity + graded degradation.
The renderer selects a composition mode from the claim count vs the
Render Request capacity (max_signals):
    - full  (N <= 2)            : echo each claim verbatim (unchanged behavior).
    - multi (3 <= N <= max)     : condensed per-claim segments, ALL claims
                                  covered, length guaranteed within bounds.
    - top_k (N > max)           : graded degradation — keep the top `max`
                                  claims (BASELINE-first ordering), drop the
                                  tail, and DECLARE the drop via a
                                  `degradation` block in the raw output so
                                  Layer 1 can validate coverage accordingly.
    - template fallback         : only on hard failure (no claims, unparseable
                                  payload) — NOT on capacity overflow.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol

# T501: render composition modes.
RENDER_MODE_FULL = "full"
RENDER_MODE_MULTI = "multi"
RENDER_MODE_TOP_K = "top_k"

# Default capacity for "stable multi-signal" rendering (Render Request may override).
MAX_SIGNALS_DEFAULT = 5

# Claims up to this count are echoed verbatim (N<=2 keeps golden cases unchanged).
FULL_ECHO_LIMIT = 2

_DEFAULT_LENGTH = {"min": 80, "max": 150}
_SEP = " · "


def _select_render_mode(claim_ids: list[str], max_signals: int) -> tuple[str, list[str]]:
    """Pick the composition mode + dropped claim ids for a claim set.

    Returns (mode, dropped_claim_ids). Order of atomic_claims is layer-major
    (BASELINE first, then CYCLE_CONTEXT, then DAILY_ACTIVATION — see
    pipeline._build_atomic_claims), so top_k keeps the earliest claims and
    drops from the tail, preserving the most fundamental signals.
    """
    n = len(claim_ids)
    if n <= FULL_ECHO_LIMIT:
        return RENDER_MODE_FULL, []
    if n <= max_signals:
        return RENDER_MODE_MULTI, []
    return RENDER_MODE_TOP_K, claim_ids[max_signals:]


@dataclass
class RenderResult:
    """Output of a render invocation."""
    text: str
    covered_claim_ids: list[str]
    honored_exclusion_ids: list[str]
    self_check: dict
    raw_output: dict

    @property
    def passed(self) -> bool:
        return all(self.self_check.values())

    @property
    def degradation(self) -> dict | None:
        """Declared degradation block from the raw output, if any (T501)."""
        return self.raw_output.get("degradation") or None

    @property
    def token_usage(self) -> dict:
        """Provider token usage (prompt/completion/total), if reported."""
        return self.raw_output.get("usage") or {}


class LLMClient(Protocol):
    """Protocol for LLM client implementations."""

    def call(
        self,
        system_prompt: str,
        user_payload: str,
        render_mode: dict | None = None,
    ) -> dict:
        """Make an LLM API call. Returns parsed JSON response.

        render_mode carries capacity decisions made by the Renderer
        (mode / capacity / dropped_claim_ids / length). Real clients may
        ignore it; the Stub uses it to compose deterministic text.
        """


class StubLLMClient:
    """Stub LLM client that returns deterministic content.

    For v1.0 demo: echoes the Atomic Claims in Chinese.
    Real implementation will use OpenAI / Claude / Qwen etc.

    T501: composes text per the renderer's `render_mode` so any claim count
    up to `capacity` is rendered within the length bounds, and counts beyond
    capacity degrade to top_k (declaring the drop) instead of overflowing.
    """

    # Mirrors OpenAICompatLLMClient.model_id so Renderer.model_id resolves
    # uniformly (audit receipt truth) regardless of which client is live.
    model_id = "stub"

    SUFFIXES = [
        "请结合实际情境，把握当下节奏。",
        "保持觉察，跟随内在节拍。",
        "在日常中细味今日的方向。",
        "留意当下的细节与感受。",
        "稳步行来，自有印证。",
    ]

    def call(
        self,
        system_prompt: str,
        user_payload: str,
        render_mode: dict | None = None,
    ) -> dict:
        """Compose deterministic Chinese text for the claims in the SIR payload."""
        import json

        try:
            payload = json.loads(user_payload)
            claims = payload.get("atomic_claims", [])
            theme = payload.get("theme", "")
            exclusions = payload.get("exclusions", [])
        except Exception:
            return {"text": "", "covered_claim_ids": [], "honored_exclusion_ids": [], "self_check": {"forbidden_content_absent": True, "all_claims_covered": False, "length_within_bounds": True}}

        rm = render_mode or {}
        mode = rm.get("mode", RENDER_MODE_FULL)
        length_cfg = rm.get("length") or _DEFAULT_LENGTH
        dropped_ids = set(rm.get("dropped_claim_ids", []))
        kept = [c for c in claims if c.get("claim_id") not in dropped_ids]

        text = self._compose(theme, kept, mode, length_cfg)
        length_ok = length_cfg["min"] <= len(text) <= length_cfg["max"]

        degradation = None
        if mode == RENDER_MODE_TOP_K and dropped_ids:
            degradation = {
                "mode": RENDER_MODE_TOP_K,
                "capacity": rm.get("capacity"),
                "total_claims": len(claims),
                "dropped_claim_ids": sorted(dropped_ids),
            }

        return {
            "text": text,
            "covered_claim_ids": [c.get("claim_id", "") for c in kept],
            "honored_exclusion_ids": [e.get("exclusion_id", "") for e in exclusions],
            "self_check": {
                "forbidden_content_absent": True,
                "all_claims_covered": True,  # within renderer scope; drops declared via degradation
                "length_within_bounds": length_ok,
            },
            "degradation": degradation,
        }

    def _compose(self, theme: str, claims: list, mode: str, length_cfg: dict) -> str:
        """Build the rendered text within [min, max], never truncating past max."""
        prefix = f"今日【{theme}】主题方向： "
        if not claims:
            text = prefix + "本日平稳，顺其自然，自有印证。"
        elif mode == RENDER_MODE_MULTI or mode == RENDER_MODE_TOP_K:
            text = self._compose_multi(theme, claims, length_cfg)
        else:  # RENDER_MODE_FULL — echo each claim verbatim
            base = " ".join(c.get("claim", "") for c in claims if c.get("claim"))
            text = prefix + base

        # Length floor: pad with safe suffixes, never overshooting max.
        si = 0
        while len(text) < length_cfg["min"] and si < len(self.SUFFIXES):
            text = text + " " + self.SUFFIXES[si]
            si += 1
        if len(text) < length_cfg["min"]:
            text = text + ("。本日节拍平稳。" * 3)

        # Hard cap: never exceed max. (T501: the old `text[:148] + "..."` was
        # exactly 151 chars and always tripped the [80, 150] validator.)
        if len(text) > length_cfg["max"]:
            text = text[: length_cfg["max"] - 3] + "..."
        return text

    @staticmethod
    def _compose_multi(theme: str, claims: list, length_cfg: dict) -> str:
        """Condensed per-claim segments; every claim represented within bounds.

        Segment budget is derived from the max length so N<=capacity claims
        always fit:  budget = (max - prefix - separators) / N.
        Each segment is "【TYPE】<excerpt>" where the excerpt reuses the claim's
        own first characters, keeping Layer 2 char-overlap high.
        """
        prefix = f"今日【{theme}】主题方向： "
        n = len(claims)
        avail = length_cfg["max"] - len(prefix) - len(_SEP) * (n - 1)
        per = max(12, avail // n)
        segments = []
        for c in claims:
            signal_type = c.get("signal_type", "")
            claim = c.get("claim", "")
            marker = f"【{signal_type}】" if signal_type else ""
            room = max(1, per - len(marker))
            excerpt = claim if len(claim) <= room else claim[:room]
            segments.append(marker + excerpt)
        return prefix + _SEP.join(segments)


class Renderer:
    """High-level Renderer using any LLMClient implementation."""

    PROMPT_VERSION = "prompt.1.0.0"

    def __init__(self, llm_client: LLMClient = None):
        if llm_client is not None:
            self._client = llm_client
            return
        # T501: env-gated real client — DEEPSEEK_API_KEY present → OpenAI-
        # compatible client (DeepSeek); absent → deterministic Stub.
        from .clients import get_llm_client  # lazy: keep Stub-only imports cheap

        self._client = get_llm_client() or StubLLMClient()

    @property
    def is_stub(self) -> bool:
        """True when the deterministic Stub is in use (no API key configured)."""
        return isinstance(self._client, StubLLMClient)

    @property
    def model_id(self) -> str:
        """Model actually used for rendering — receipt truth.

        The Render Request defaults its own model_config.model_id to "stub"
        by construction (DECISION-007 envelope), so the audit receipt must
        read the live client, not the request. "stub" for the deterministic
        Stub, else the resolved provider model (e.g. sensenova-6.8-flash-lite).
        """
        return getattr(self._client, "model_id", "stub")

    def render(
        self,
        sir: dict,
        render_request: dict,
        system_prompt: str | None = None,
    ) -> RenderResult:
        """Render SIR through LLM.

        Args:
            sir: Canonical Content dict.
            render_request: Render Request dict.
            system_prompt: Optional pre-composed prompt (else default).

        Returns:
            RenderResult with text + metadata.

        T501: selects the composition mode from claim count vs
        `render_request.max_signals` and passes capacity decisions to the
        client via `render_mode`.
        """
        if system_prompt is None:
            system_prompt = _default_system_prompt(
                tone=render_request.get("tone", "warm"),
                length=render_request.get("length", _DEFAULT_LENGTH),
                language=render_request.get("language", "zh-CN"),
                theme=sir.get("theme", ""),
            )

        claim_ids = [c.get("claim_id", "") for c in sir.get("atomic_claims", [])]
        max_signals = render_request.get("max_signals", MAX_SIGNALS_DEFAULT)
        mode, dropped = _select_render_mode(claim_ids, max_signals)
        render_mode = {
            "mode": mode,
            "capacity": max_signals,
            "dropped_claim_ids": dropped,
            "length": render_request.get("length", _DEFAULT_LENGTH),
        }

        user_payload = _sir_to_user_payload(sir)
        raw = self._client.call(system_prompt, user_payload, render_mode=render_mode)

        return RenderResult(
            text=raw.get("text", ""),
            covered_claim_ids=raw.get("covered_claim_ids", []),
            honored_exclusion_ids=raw.get("honored_exclusion_ids", []),
            self_check=raw.get("self_check", {}),
            raw_output=raw,
        )


def _default_system_prompt(tone: str, length: dict, language: str, theme: str) -> str:
    return f"""你是 TONGSHU Renderer。唯一职责：把 Canonical Content (SIR)
翻译成自然语言。

约束：
- 只翻译 SIR 内容，不添加任何额外语义
- 不修改 atomic_claims / signals / exclusions
- 不添加：医疗、投资金额、具体预测、恐吓内容
- 不引用 Rule DB ID / Evidence ID

Tone: {tone}
Length: {length['min']}-{length['max']} 字符
Language: {language}
Theme: {theme}

输出 JSON：{{"text": "...", "covered_claim_ids": [...], "honored_exclusion_ids": [...], "self_check": {{...}}}}
"""


def _sir_to_user_payload(sir: dict) -> str:
    import json
    return json.dumps(sir, ensure_ascii=False)
