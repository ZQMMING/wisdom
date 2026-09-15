"""Evidence Registry（Phase 5 §39/§64）。

- 每条 (rule_id, source_id) 绑定生成一条 Evidence Record（§39 结构）
- Fact → Rule → Source → Evidence 链完整性检查；链断 → Gap Report（不得强行通过）
- UNVERIFIED（evidence_grade=D）不视为断链，但列入 Gap Report 待 Human 裁定
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from shared_types.fail_closed import FailClosedReason, FailClosedError

ROOT = Path(__file__).resolve().parent.parent.parent.parent
RULES_PATH = ROOT / "registries" / "rule" / "rules.yhzp.jsonl"
SOURCES_PATH = ROOT / "registries" / "source" / "sources.yhzp.jsonl"
EVD_OUT = ROOT / "registries" / "evidence" / "evidence.yhzp.jsonl"
GAP_OUT = ROOT / "registries" / "evidence" / "gap_report.yhzp.jsonl"


class EvidenceRegistry:
    """从正式 Source/Rule Registry 派生 Evidence；运行时为 Fact 补 evidence_ids。"""

    def __init__(self, rules_path: Path = RULES_PATH, sources_path: Path = SOURCES_PATH) -> None:
        self.sources: Dict[str, Dict[str, Any]] = {
            json.loads(l)["source_id"]: json.loads(l)
            for l in sources_path.read_text(encoding="utf-8").splitlines() if l.strip()
        }
        self.rules: List[Dict[str, Any]] = [
            json.loads(l) for l in rules_path.read_text(encoding="utf-8").splitlines() if l.strip()
        ]
        self._records: Dict[str, List[str]] = {}  # rule_id -> [evidence_id, ...]
        self._by_id: Dict[str, Dict[str, Any]] = {}
        self.gaps: List[Dict[str, Any]] = []
        self._build()

    def _build(self) -> None:
        seq = 0
        seen_src: Dict[str, str] = {}
        for r in self.rules:
            evds = []
            for sid in r["source_ids"]:
                src = self.sources.get(sid)
                if src is None:
                    self.gaps.append({"type": "BROKEN_CHAIN", "rule_id": r["rule_id"], "source_id": sid,
                                      "detail": "Rule 引用了不存在的 Source"})
                    raise FailClosedError(FailClosedReason.CONTRACT_INVALID,
                                          f"链断: {r['rule_id']} -> {sid}")
                # 同一 source 被多 rule 引用时复用 evidence（同一文本证据）
                if sid in seen_src:
                    evd_id = seen_src[sid]
                else:
                    seq += 1
                    evd_id = f"EVD-YHZP-{seq:03d}"
                    seen_src[sid] = evd_id
                    self._by_id[evd_id] = {
                        "evidence_id": evd_id,
                        "source_id": sid,
                        "source_location": src.get("logical_uri", ""),
                        "text_layer": src.get("text_layer", "UNVERIFIED"),
                        "evidence_grade": src.get("evidence_grade", "D"),
                        "rule_id": r["rule_id"],
                        "fact_ids": [],
                    }
                evds.append(evd_id)
            self._records[r["rule_id"]] = evds
            # 附加到该 evidence 的 rule 列表（一个 evidence 可服务多 rule）
        # 反查：record 里 rule_id 存第一条，补充 rule_ids
        self._reindex_rules()

    def _reindex_rules(self) -> None:
        rule_by_evd: Dict[str, List[str]] = {}
        for rid, evds in self._records.items():
            for e in evds:
                rule_by_evd.setdefault(e, []).append(rid)
        for eid, rec in self._by_id.items():
            rec["rule_ids"] = sorted(set(rule_by_evd.get(eid, [])))

    # ---- 运行时 ----

    def evidence_ids_for(self, rule_id: str) -> List[str]:
        return list(self._records.get(rule_id, []))

    def attach(self, fact: Dict[str, Any]) -> Dict[str, Any]:
        """给 Rule Engine 产出的 fact 补 evidence_ids。"""
        evds = self.evidence_ids_for(fact["rule_id"])
        if not evds:
            raise FailClosedError(FailClosedReason.CONTRACT_INVALID, f"Fact 无证据链: {fact['rule_id']}")
        fact["evidence_ids"] = evds
        return fact

    # ---- 导出 ----

    def export(self, evd_out: Path = EVD_OUT, gap_out: Path = GAP_OUT) -> None:
        evd_out.parent.mkdir(parents=True, exist_ok=True)
        evd_out.write_text("".join(json.dumps(self._by_id[k], ensure_ascii=False) + "\n"
                                  for k in sorted(self._by_id)), encoding="utf-8")
        gap_out.parent.mkdir(parents=True, exist_ok=True)
        gaps = self.gaps + [{"type": "UNVERIFIED_SOURCE", "source_id": sid, "evidence_grade": "D",
                             "detail": "UNVERIFIED 待 Human 裁定（不影响链完整性）"}
                            for sid, s in self.sources.items() if s.get("evidence_grade") == "D"]
        gap_out.write_text("".join(json.dumps(g, ensure_ascii=False) + "\n" for g in gaps), encoding="utf-8")

    @property
    def record_count(self) -> int:
        return len(self._by_id)
