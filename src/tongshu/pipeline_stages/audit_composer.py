"""AuditComposer — 阶段 10（审计日志组装）。

职责：
    - 构造 render_receipt（model_id / prompt_version / token_usage / degradation）
    - 构造 validation_results（layer1/2/3 + gates + final_decision）
    - 调用 AuditWriter.write()
    - 返回 entry_id

compute_only 模式：render_receipt / validation_results 用占位符。

Version: 1.0.0
Created: 2026-08-20 (Phase 2 / Step 3 C5)
Migrated from: pipeline.py:271-322（run() 阶段 10）
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from ..audit.writer import AuditWriter

if TYPE_CHECKING:
    from .compute_stage import ComputeResult
    from .render_stage import RenderStageResult
    from .validation_stage import ValidationStageResult


class AuditComposer:
    """阶段 10: 审计日志组装。"""

    def __init__(self, audit_writer: AuditWriter) -> None:
        self.audit_writer = audit_writer

    def compose_and_write(
        self,
        request_id: str,
        trace_id: str,
        spec_version: str,
        document_id: str,
        compute: "ComputeResult",
        render: "RenderStageResult",
        validation: "ValidationStageResult",
        theme: str,
        model_id: str,
        final_text: str,
        final_source: str,
    ) -> str:
        """组装审计日志并写入；返回 entry_id。

        final_text / final_source 必须是**最终交付**的文本与来源
        （可能已由模板回退降级），而非 RenderStageResult 的快照——
        C9P2A 审计 P1 修复：渲染成功但校验失败时，RenderStageResult
        记录的是降级前的 LLM 文本，而实际交付的是模板回退文本；
        audit final_output 必须与交付一致（AUDIT == DELIVERED）。
        """
        canonical = compute.canonical
        signals = compute.signals
        cross_result = compute.cross_result

        # 构造 render_receipt + validation_results
        if compute_only:
            render_receipt: dict = {}
            validation_results: dict = {
                "final_decision": None,
                "note": "compute_only — no renderer invoked",
            }
        else:
            rendered_obj = render.rendered
            render_receipt = {
                "model_id": model_id,
                "prompt_version": render.render_request_dict.get("prompt_version", "unknown"),
                "render_timestamp": datetime.now(timezone.utc).isoformat(),
                "token_usage": rendered_obj.token_usage if rendered_obj else {},
                "raw_output_hash": "",
                "degradation": rendered_obj.degradation if rendered_obj else None,
            }
            l1 = validation.layer1
            l2 = validation.layer2
            l3 = validation.layer3
            validation_results = {
                "layer1": {
                    "passed": l1.passed if l1 else False,
                    "errors": list(l1.errors) if l1 else ["renderer_hard_failure"],
                },
                "layer2": {
                    "passed": l2.passed if l2 else False,
                    "min_similarity": l2.min_similarity if l2 else None,
                    "threshold": l2.threshold if l2 else None,
                },
                "layer3": {
                    "passed": l3.passed if l3 else False,
                    "entailment_verdict": l3.entailment_verdict if l3 else None,
                    "judge_model_id": l3.judge_model_id if l3 else None,
                },
                "gates": [g.to_dict() for g in validation.gates],
                "final_decision": "PASS" if validation.passed else "FAIL",
            }

        # 写入审计日志
        return self.audit_writer.write(
            request_id=request_id,
            pii_vault_ref={"user_id_hash": "PII-VAULT", "birth_data_ref": "PII-VAULT"},
            sir_summary={
                "canonical_id": canonical.canonical_id,
                "schema_version": canonical.schema_version,
                "analysis_context": canonical.analysis_context,
                "theme": canonical.theme,
                "cross_status": cross_result.status if cross_result else None,
                "claim_count": len(canonical.atomic_claims),
                "exclusion_count": len(canonical.exclusions),
                "rule_refs": [],
                "signal_layer_summary": {
                    "BASELINE_count": len(signals.get("BASELINE", [])),
                    "CYCLE_CONTEXT_count": len(signals.get("CYCLE_CONTEXT", [])),
                    "DAILY_ACTIVATION_count": len(signals.get("DAILY_ACTIVATION", [])),
                },
            },
            render_receipt=render_receipt,
            validation_results=validation_results,
            final_output={
                "text": final_text,
                "source": final_source,
                "template_id": None,
            },
            spec_version=spec_version,
            trace_id=trace_id,
            document_id=document_id,
        )
