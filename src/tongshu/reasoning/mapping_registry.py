"""MappingRegistry — 词库现代化转译标签层(V3.6 §18-21)。

Mapping entries live as one JSON file per entry under
backend/data/mappings/*.json and validate against docs/mapping.schema.json
at load time — a malformed entry raises MappingLoadError, never loads
silently (mirrors RuleLoader / T203).

语义边界(DECISION 6):本层只做现代语标签。apply_to_claims 只附加
mapping_refs / modern_theme 两个可选字段,绝不改写 signal_type / USO 枚举 /
rule_refs / evidence_refs —— golden 引用的语义护栏不受影响。

解析逻辑(确定性):
  一个 atomic_claim 携带 rule_refs(产生它的规则);一个 mapping 携带
  rule_refs(它标注的规则)。claim.rule_refs ∩ mapping.rule_refs 非空 →
  该 mapping 应用。现代语 theme 取按 mapping_id 排序的第一个命中(多映射
  并存时 mapping_refs 全部附加,modern_theme 取首条),避免随机性。
"""

from __future__ import annotations
import json
import logging
from pathlib import Path

from jsonschema import Draft202012Validator

log = logging.getLogger(__name__)


class MappingLoadError(RuntimeError):
    """Raised when a mapping record fails schema validation."""


class MappingRegistry:
    def __init__(self, data_dir: Path, schema_dir: Path):
        self._dir = Path(data_dir) / "mappings"
        self._schema_dir = Path(schema_dir)
        self._schema = self._load_schema(schema_dir / "mapping.schema.json")
        self._entries: list[dict] = []
        self._load()

    @staticmethod
    def _load_schema(path: Path) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load(self) -> None:
        if not self._dir.is_dir():
            raise MappingLoadError(f"mappings dir missing: {self._dir}")
        validator = Draft202012Validator(self._schema)
        for path in sorted(self._dir.glob("*.json")):
            with open(path, "r", encoding="utf-8") as f:
                entry = json.load(f)
            errs = sorted(validator.iter_errors(entry), key=lambda e: list(e.path))
            if errs:
                raise MappingLoadError(f"{path.name}: schema invalid — {errs[0].message}")
            self._entries.append(entry)

    # ------------------------------------------------------------------ #

    @property
    def entries(self) -> list[dict]:
        return list(self._entries)

    def get(self, mapping_id: str) -> dict | None:
        for e in self._entries:
            if e.get("mapping_id") == mapping_id:
                return e
        return None

    def by_source_term(self, term: str) -> dict | None:
        for e in self._entries:
            if e.get("source_term") == term:
                return e
        return None

    def by_rule_ref(self, rule_id: str) -> list[dict]:
        return [e for e in self._entries if rule_id in e.get("rule_refs", [])]

    def apply_to_claims(self, atomic_claims: list[dict]) -> list[dict]:
        """Attach mapping_refs / modern_theme to each claim, deterministically.

        A claim is labelled by every ACTIVE mapping whose rule_refs intersect the
        claim's rule_refs. modern_theme takes the first match by mapping_id
        order (sorted); claims with no matching mapping are returned unchanged.

        Status gate: DRAFT/REVIEW/DEPRECATED mappings are excluded from
        production chain to prevent premature semantic leakage (M-LC-01).
        """
        by_rule: dict[str, list[dict]] = {}
        for e in self._entries:
            # Status gate: only ACTIVE mappings participate in production
            if e.get("status") != "ACTIVE":
                continue
            for rid in e.get("rule_refs", []):
                by_rule.setdefault(rid, []).append(e)

        out = []
        for claim in atomic_claims:
            claimed = dict(claim)
            hits: dict[str, dict] = {}
            for rid in claimed.get("rule_refs", []):
                for e in by_rule.get(rid, []):
                    hits[e["mapping_id"]] = e
            if hits:
                ordered = [hits[mid] for mid in sorted(hits)]
                claimed["mapping_refs"] = [e["mapping_id"] for e in ordered]
                claimed["modern_theme"] = ordered[0]["modern_theme"]
            out.append(claimed)
        return out
