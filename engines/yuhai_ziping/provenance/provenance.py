"""Provenance Recorder（Phase 10 §40）。

每次运行生成 Provenance Record：engine / engine_version / contract_version /
rule_version / source_version / input_ref / rule_ids / source_ids / evidence_ids / timestamp。
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List

from engines.yuhai_ziping import ENGINE_ID, ENGINE_VERSION
from engines.yuhai_ziping.validator import CONTRACT_PATH

ROOT = __import__("pathlib").Path(__file__).resolve().parent.parent.parent.parent
RULES_PATH = ROOT / "registries" / "rule" / "rules.yhzp.jsonl"
SOURCES_PATH = ROOT / "registries" / "source" / "sources.yhzp.jsonl"


class ProvenanceRecorder:
    def __init__(self) -> None:
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        self.contract_version = contract["contract_version"]
        rules = [json.loads(l) for l in RULES_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
        srcs = [json.loads(l) for l in SOURCES_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
        self.rule_version = rules[0]["version"] if rules else "0.0.0"
        self.source_version = srcs[0]["version"] if srcs else "0.0.0"

    def record(self, result: Any, input_ref: str, rule_ids: List[str],
               source_ids: List[str], evidence_ids: List[str]) -> Dict[str, Any]:
        return {
            "engine": ENGINE_ID,
            "engine_version": ENGINE_VERSION,
            "contract_version": self.contract_version,
            "rule_version": self.rule_version,
            "source_version": self.source_version,
            "input_ref": input_ref,
            "rule_ids": sorted(set(rule_ids)),
            "source_ids": sorted(set(source_ids)),
            "evidence_ids": sorted(set(evidence_ids)),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }

    def record_from_result(self, result: Any) -> Dict[str, Any]:
        rule_ids: List[str] = []
        source_ids: List[str] = []
        evidence_ids: List[str] = []
        for items in result.facts.to_dict().values():
            for f in items:
                rule_ids.append(f["rule_id"])
                source_ids.extend(f.get("source_ids", []))
                evidence_ids.extend(f.get("evidence_ids", []))
        return self.record(result, result.canonical_input.get("ref", ""),
                           rule_ids, source_ids, evidence_ids)
