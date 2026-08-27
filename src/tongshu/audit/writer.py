"""Audit Log writer.

Per architecture_decisions_v1.md §0.2, Audit Log is cross-cutting infrastructure.
Sensitive PII MUST live only in PII Vault; Analysis Log holds semantic trace.
"""

from __future__ import annotations
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


class AuditWriter:
    """Writes audit log entries to JSONL file."""

    def __init__(self, log_dir: Path):
        self._dir = Path(log_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._path = self._dir / "audit_log.jsonl"

    def write(
        self,
        request_id: str,
        pii_vault_ref: dict,
        sir_summary: dict,
        render_receipt: dict,
        validation_results: dict,
        final_output: dict,
        spec_version: str,
        unresolved_refs: list[str] = None,
        client_metadata: dict = None,
        trace_id: str = None,
        document_id: str = None,
    ) -> str:
        """Write one audit log entry. Returns entry_id.

        V3.6 §36: trace_id / document_id are the observability trio companions
        to request_id. The frozen docs/audit_log.schema.json (1.0.0) does not
        declare them — runtime writes are not schema-validated, and the
        supersession is documented in docs/v36/10_AUDIT_POLICY (pending a
        MINOR bump per DECISION-010/011).
        """
        entry_id = f"AL-{uuid.uuid4().hex[:8].upper()}"
        entry = {
            "entry_id": entry_id,
            "request_id": request_id,
            "trace_id": trace_id,
            "document_id": document_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis_id": f"AN-{uuid.uuid4().hex[:8].upper()}",
            "pii_vault_ref": dict(pii_vault_ref),
            "sir_summary": dict(sir_summary),
            "render_receipt": dict(render_receipt),
            "validation_results": dict(validation_results),
            "final_output": dict(final_output),
            "spec_version": spec_version,
            "unresolved_refs": list(unresolved_refs or []),
            "client_metadata": dict(client_metadata or {}),
        }

        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return entry_id

    @property
    def log_path(self) -> Path:
        return self._path
