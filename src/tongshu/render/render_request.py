"""Render Request builder.

Per architecture_decisions_v1.md DECISION-007, Render Request is the
SEPARATE envelope containing all rendering concerns. SIR MUST NOT carry
any of these fields.
"""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field


@dataclass
class RenderRequest:
    """Render envelope for the LLM."""

    request_id: str
    sir_ref: dict
    model_config: dict
    tone: str
    length: dict
    language: str
    safety_settings: dict
    prompt_version: str
    few_shot_set: str = "default_v1.0"
    cache_hint: dict = field(default_factory=dict)
    max_signals: int = 5  # T501: multi-signal render capacity (see renderer.py)

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "sir_ref": dict(self.sir_ref),
            "model_config": dict(self.model_config),
            "tone": self.tone,
            "length": dict(self.length),
            "language": self.language,
            "safety_settings": dict(self.safety_settings),
            "prompt_version": self.prompt_version,
            "few_shot_set": self.few_shot_set,
            "cache_hint": dict(self.cache_hint),
            "max_signals": self.max_signals,
        }


def build_render_request(
    canonical_id: str,
    canonical_schema_version: str,
    theme: str,
    request_id: str = None,
    model_id: str = "stub",
    tone: str = "warm",
    length_min: int = 80,
    length_max: int = 150,
    language: str = "zh-CN",
    prompt_version: str = "prompt.1.0.0",
    max_signals: int = 5,
) -> RenderRequest:
    """Build a default Render Request.

    Per DECISION-007: this is SEPARATE from SIR.

    V3.6 §36: an explicit `request_id` (RR-*) keeps the observability trio
    coherent — canonical.meta.request_id == render_request.request_id ==
    audit request_id. When omitted, a fresh RR-* is generated.
    """
    return RenderRequest(
        request_id=request_id or f"RR-{uuid.uuid4().hex[:8].upper()}",
        sir_ref={
            "canonical_id": canonical_id,
            "schema_version": canonical_schema_version,
        },
        model_config={
            "model_id": model_id,
            "temperature": 0.3,
        },
        tone=tone,
        length={"min": length_min, "max": length_max},
        language=language,
        safety_settings={
            "block_categories": ["PREDICTION", "MEDICAL", "INVESTMENT", "FEAR", "LEGAL", "POLITICAL"],
            "enable_layer1_deterministic": True,
            "enable_layer2_embedding": True,
            "enable_layer3_llm_judge": True,
        },
        prompt_version=prompt_version,
        max_signals=max_signals,
    )
