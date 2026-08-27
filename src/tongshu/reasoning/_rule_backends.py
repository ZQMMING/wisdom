"""RuleLoader 的双源 backend 封装。

与 _kb_backends.py 同一架构。JsonRuleBackend 为默认；
PostgresRuleBackend 为占位。实际上线时需 Claude C9 交付。

依赖：无。

Version: 1.0.0  Created: 2026-08-20 (Phase 2 / Step 2)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

log = logging.getLogger(__name__)


class _JsonRuleBackend:
    """RuleLoader 的 JSON 后端实现。

    加载 backend/data/rules/*.json + backend/data/evidence/*.json，
    按 docs/rule.schema.json (v1.1) 与 docs/evidence.schema.json 校验。
    """

    def __init__(self, data_dir: Path, schema_dir: Path) -> None:
        try:
            from jsonschema import Draft202012Validator
        except ImportError as e:
            raise RuntimeError("jsonschema is required for RuleLoader (json)") from e

        self._rules_dir = Path(data_dir) / "rules"
        self._evidence_dir = Path(data_dir) / "evidence"
        self._schema_dir = Path(schema_dir)

        self._rule_schema = self._load_schema(schema_dir / "rule.schema.json")
        self._evidence_schema = self._load_schema(schema_dir / "evidence.schema.json")

        self._rules: list[dict] = []
        self._evidence: list[dict] = []
        self._load_rules()
        self._load_evidence()

    @staticmethod
    def _load_schema(path: Path) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_rules(self) -> None:
        from .rule_loader import RuleLoadError

        if not self._rules_dir.is_dir():
            raise RuleLoadError(f"rules dir missing: {self._rules_dir}")
        from jsonschema import Draft202012Validator
        validator = Draft202012Validator(self._rule_schema)
        for path in sorted(self._rules_dir.glob("*.json")):
            with open(path, "r", encoding="utf-8") as f:
                rule = json.load(f)
            errs = sorted(validator.iter_errors(rule), key=lambda e: list(e.path))
            if errs:
                detail = errs[0].message
                raise RuleLoadError(f"{path.name}: schema invalid — {detail}")
            self._rules.append(rule)

    def _load_evidence(self) -> None:
        from .rule_loader import RuleLoadError

        if not self._evidence_dir.is_dir():
            log.warning("evidence dir missing: %s (DoD #4 追溯不闭合)", self._evidence_dir)
            return
        from jsonschema import Draft202012Validator
        validator = Draft202012Validator(self._evidence_schema)
        for path in sorted(self._evidence_dir.glob("*.json")):
            with open(path, "r", encoding="utf-8") as f:
                ev = json.load(f)
            errs = sorted(validator.iter_errors(ev), key=lambda e: list(e.path))
            if errs:
                raise RuleLoadError(f"{path.name}: evidence schema invalid — {errs[0].message}")
            self._evidence.append(ev)

    # ----- properties / methods (公共接口与原 RuleLoader 一致) -----
    @property
    def rules(self) -> list[dict]:
        return list(self._rules)

    @property
    def evidence(self) -> list[dict]:
        return list(self._evidence)

    @property
    def evidence_ids(self) -> set[str]:
        return {e.get("evidence_id") for e in self._evidence}

    def get(self, rule_id: str) -> dict | None:
        for r in self._rules:
            if r.get("rule_id") == rule_id:
                return r
        return None

    def verify_evidence_refs(self) -> list[str]:
        """Rules referencing evidence that has no record on disk."""
        missing = []
        known = self.evidence_ids
        for r in self._rules:
            for ref in r.get("evidence_refs", []):
                if ref not in known:
                    missing.append(f"{r.get('rule_id')} -> {ref}")
        return missing


class _PostgresRuleBackend:
    """RuleLoader 的 Postgres 后端占位。

    待 Claude C9 交付 RulePostgresAdapter 后启用。
    """

    def __init__(self, *_args, **_kwargs) -> None:
        self._ready = False

    @property
    def _unavailable(self) -> str:
        return (
            "PostgresRuleBackend 尚未实现：等 Claude C9 RulePostgresAdapter "
            "交付后启用。"
        )

    @property
    def rules(self):
        raise NotImplementedError(self._unavailable)

    @property
    def evidence(self):
        raise NotImplementedError(self._unavailable)

    @property
    def evidence_ids(self):
        raise NotImplementedError(self._unavailable)

    def get(self, rule_id: str):
        raise NotImplementedError(self._unavailable)

    def verify_evidence_refs(self):
        raise NotImplementedError(self._unavailable)
