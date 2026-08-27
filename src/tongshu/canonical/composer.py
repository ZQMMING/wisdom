"""Canonical Content Composer.

Builds a Canonical Content SIR (Semantic Intermediate Representation)
from reasoning engine outputs. Conforms to docs/canonical_content.schema.json.

Per architecture_decisions_v1.md DECISION-007, the SIR MUST NOT contain
any rendering, infrastructure, or presentation concerns.
"""

from __future__ import annotations
import uuid
from dataclasses import dataclass
from datetime import date

from ..engines.bazi_engine import BaziChart
from ..engines.ziwei_engine import ZiweiChart
from ..engines.huangli_engine import HuangliDay
from ..reasoning.signal_engine import Signal
from ..reasoning.cross_analysis import CrossResult
from ..spec.signal_layers import SIGNAL_LAYERS


@dataclass
class CanonicalContent:
    """The SIR (Semantic Intermediate Representation)."""
    schema_version: str
    canonical_id: str
    analysis_context: dict
    theme: str
    cross_analysis: dict
    signals: dict
    atomic_claims: list[dict]
    exclusions: list[dict]
    # V3.6 §6: meta 版本族 + 可观测性三件套(可选;None → 不出现在 to_dict,
    # 旧形状 SIR 保持不变)。一旦出现必须完整 —— v36 schema 对 present-but-
    # incomplete 的 meta 会拒绝,因此由 composer 一次性构建全部 11 字段。
    meta: dict | None = None

    def to_dict(self) -> dict:
        d = {
            "schema_version": self.schema_version,
            "canonical_id": self.canonical_id,
            "analysis_context": self.analysis_context,
            "theme": self.theme,
            "cross_analysis": self.cross_analysis,
            "signals": self.signals,
            "atomic_claims": list(self.atomic_claims),
            "exclusions": list(self.exclusions),
        }
        if self.meta is not None:
            d["meta"] = self.meta
        return d


class CanonicalComposer:
    """Composes Canonical Content from engine + reasoning outputs."""

    SCHEMA_VERSION = "1.0.0"

    # V3.6 §6 meta 版本族。const 值对 docs/v36/01_CANONICAL_SCHEMA.json 冻结
    # (2026-08-18);bump 走 DECISION-010/011,Spec Owner 批准后才动。
    META_SCHEMA_VERSION = "3.6.0"
    META_CALCULATION_VERSION = "1.0.0"
    META_KNOWLEDGE_VERSION = "1.0.0"
    META_MAPPING_VERSION = "0.1.0"
    META_TRANSLATION_VERSION = "0.1.0"
    META_AUDIT_VERSION = "1.0.0"

    def __init__(self, theme: str, engine_versions: dict[str, str]):
        self.theme = theme
        self._engine_versions = engine_versions

    def compose(
        self,
        analysis_date: date,
        bazi: BaziChart,
        ziwei: ZiweiChart,
        huangli: HuangliDay,
        signals: dict[str, list[Signal]],
        cross_result: CrossResult,
        atomic_claims: list[dict],
        exclusions: list[dict] = None,
        meta_observability: dict = None,
    ) -> CanonicalContent:
        canonical_id = self._make_canonical_id(analysis_date, bazi)

        signals_dict = self._format_signals(signals)

        meta = None
        if meta_observability is not None:
            meta = self._build_meta(canonical_id, meta_observability)

        return CanonicalContent(
            schema_version=self.SCHEMA_VERSION,
            canonical_id=canonical_id,
            analysis_context={
                "date": analysis_date.isoformat(),
                "calendar_system": "solar",
                "bazi_version": self._engine_versions.get("bazi", "1.0.0"),
                "ziwei_version": self._engine_versions.get("ziwei", "1.0.0"),
                "rule_set_version": self._engine_versions.get("rules", "1.0.0"),
                "engine_version": self._engine_versions.get("reasoning", "1.0.0"),
            },
            theme=self.theme,
            cross_analysis=cross_result.to_dict(),
            signals=signals_dict,
            atomic_claims=list(atomic_claims),
            exclusions=list(exclusions or []),
            meta=meta,
        )

    def _build_meta(self, canonical_id: str, obs: dict) -> dict:
        """Build the complete V3.6 §6 meta block.

        All 11 fields MUST be present at once: the v36 schema rejects a
        present-but-incomplete meta, so there is no partial state.
        `obs` carries the dynamic observability fields threaded in by the
        pipeline (request_id / trace_id / model_version / created_at).
        """
        return {
            "request_id": obs["request_id"],
            "trace_id": obs["trace_id"],
            "document_id": canonical_id,
            "schema_version": self.META_SCHEMA_VERSION,
            "calculation_version": self.META_CALCULATION_VERSION,
            "knowledge_version": self.META_KNOWLEDGE_VERSION,
            "mapping_version": self.META_MAPPING_VERSION,
            "translation_version": self.META_TRANSLATION_VERSION,
            "audit_version": self.META_AUDIT_VERSION,
            "model_version": obs.get("model_version", "stub"),
            "created_at": obs["created_at"],
        }

    def _make_canonical_id(self, analysis_date: date, bazi: BaziChart) -> str:
        dm = bazi.day_master
        return f"CC-{dm}-{analysis_date.isoformat()}-{uuid.uuid4().hex[:6].upper()}"

    def _format_signals(self, signals: dict[str, list[Signal]]) -> dict:
        """Format signals per layer for SIR serialization.

        Each layer is an array of Signal records (DECISION-002).
        """
        out: dict[str, list[dict]] = {}
        for layer in SIGNAL_LAYERS:
            out[layer] = [
                {
                    "signal_id": s.signal_id,
                    "ontology_type": s.ontology_type,
                    "direction": s.direction,
                    "polarity": s.polarity,
                    "strength": s.strength,
                    "rule_refs": list(s.rule_refs),
                    "evidence_refs": list(s.evidence_refs),
                }
                for s in signals.get(layer, [])
            ]
        return out
