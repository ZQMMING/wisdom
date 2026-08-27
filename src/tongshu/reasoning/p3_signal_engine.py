"""P3 Signal Engine - 语义信号引擎(Rule Matcher).

注意: 这是P3新的SemanticSignal引擎, 与原有的signal_engine.py(Universal Signal)不同.
原有的signal_engine.py负责从八字/紫微/黄历提取Universal Signal.
P3的p3_signal_engine.py负责将EngineEvidence通过Rule匹配为SemanticSignal(无direction).

核心逻辑:
  EngineEvidence(纯事实, 有rule_id)
    ↓ 通过rule_id查找Rule
  Rule(有produces_semantic_atoms = [atom1, atom2, ...])
    ↓ 语义守恒: 每个atom产生一个SemanticSignal
  SemanticSignal[] (无direction)

语义守恒硬契约:
  Rule.produces_semantic_atoms 有 N 个 atom
  → 必须产生 N 个 SemanticSignal
  → 不能压缩成1个, 不能合并, 不能丢弃

未迁移规则处理:
  64条非核心规则没有produces_semantic_atoms
  → 产生1个status=NOT_READY的SemanticSignal
  → 禁止走旧路径(direction/polarity)
  → P3 Validator会明确标记
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

from .semantic_signal import (
    SemanticSignal,
    SignalStatus,
    make_signal_id,
    validate_signal_contract,
)

log = logging.getLogger(__name__)


class P3SignalEngine:
    """P3 Signal Engine - Rule Matcher.

    接收 EngineEvidence 列表, 通过 Rule 匹配产生 SemanticSignal 列表.
    """

    def __init__(self, rules_dir: Path | str):
        self._rules_dir = Path(rules_dir)
        self._rules: dict[str, dict] = {}
        self._load_rules()

    def _load_rules(self) -> None:
        """加载所有规则文件."""
        if not self._rules_dir.is_dir():
            log.warning("Rules dir not found: %s", self._rules_dir)
            return
        for f in sorted(self._rules_dir.glob("*.json")):
            with open(f, encoding="utf-8") as fh:
                rule = json.load(fh)
            rid = rule.get("rule_id")
            if rid:
                self._rules[rid] = rule
        log.info("Loaded %d rules from %s", len(self._rules), self._rules_dir)

    def is_migrated(self, rule_id: str) -> bool:
        """检查规则是否已迁移(有produces_semantic_atoms)."""
        rule = self._rules.get(rule_id)
        if not rule:
            return False
        return "produces_semantic_atoms" in rule.get("conclusion", {})

    def get_rule(self, rule_id: str) -> Optional[dict]:
        """获取规则数据."""
        return self._rules.get(rule_id)

    def match_evidence(
        self,
        evidence_list: list[dict],
        case_id: str,
    ) -> list[SemanticSignal]:
        """将 EngineEvidence 列表匹配为 SemanticSignal 列表.

        Args:
            evidence_list: EngineEvidence 字典列表(每个有engine/rule_id/value/temporal_scope)
            case_id: 命例ID

        Returns:
            SemanticSignal 列表

        语义守恒:
          已迁移规则: produces_semantic_atoms有N个 → 产生N个Signal
          未迁移规则: 产生1个NOT_READY Signal
        """
        signals: list[SemanticSignal] = []

        for ev in evidence_list:
            ev_rule_id = ev.get("rule_id", "")
            engine = ev.get("engine", "")
            temporal_scope = ev.get("temporal_scope", "birth")
            ev_value = ev.get("value", "")

            rule = self._rules.get(ev_rule_id)

            if rule and self.is_migrated(ev_rule_id):
                # 已迁移规则: 语义守恒, 每个atom产生一个Signal
                atoms = rule["conclusion"]["produces_semantic_atoms"]
                signal_type = rule.get("produces_signal_type", "")

                for atom_id in atoms:
                    sig = SemanticSignal(
                        signal_id=make_signal_id(case_id, engine, ev_rule_id, atom_id),
                        case_id=case_id,
                        engine=engine,
                        rule_id=ev_rule_id,
                        atom_id=atom_id,
                        temporal_scope=temporal_scope,
                        evidence_ref=ev_rule_id,
                        status=SignalStatus.READY.value,
                        signal_type=signal_type,
                        context={
                            "evidence_value": str(ev_value),
                            "rule_title": rule.get("title", ""),
                            "rule_type": rule.get("rule_type", ""),
                        },
                    )
                    signals.append(sig)

            else:
                # 未迁移规则: 产生NOT_READY Signal, 禁止走旧路径
                sig = SemanticSignal(
                    signal_id=make_signal_id(case_id, engine, ev_rule_id, "NOT_READY"),
                    case_id=case_id,
                    engine=engine,
                    rule_id=ev_rule_id,
                    atom_id="NOT_READY",
                    temporal_scope=temporal_scope,
                    evidence_ref=ev_rule_id,
                    status=SignalStatus.NOT_READY.value,
                    signal_type=rule.get("produces_signal_type", "") if rule else "",
                    context={
                        "evidence_value": str(ev_value),
                        "reason": "Rule not migrated to P2 produces_semantic_atoms contract",
                        "rule_title": rule.get("title", "") if rule else "Rule not found",
                    },
                )
                signals.append(sig)

        # 验证契约
        errors = validate_signal_contract(signals)
        if errors:
            for e in errors:
                log.error("Signal contract violation: %s", e)

        return signals

    def get_stats(self, signals: list[SemanticSignal]) -> dict:
        """统计Signal信息."""
        from collections import Counter

        by_engine = Counter(s.engine for s in signals)
        by_status = Counter(s.status for s in signals)
        by_atom = Counter(s.atom_id for s in signals)
        by_rule = Counter(s.rule_id for s in signals)

        # 语义守恒检查: 已迁移规则的signal数量
        ready_signals = [s for s in signals if s.status == "READY"]
        not_ready_signals = [s for s in signals if s.status == "NOT_READY"]

        # 按rule分组检查语义守恒
        conservation_issues = []
        ready_by_rule: dict[str, list[SemanticSignal]] = {}
        for s in ready_signals:
            ready_by_rule.setdefault(s.rule_id, []).append(s)

        for rule_id, sigs in ready_by_rule.items():
            rule = self._rules.get(rule_id)
            if rule:
                expected = len(rule["conclusion"]["produces_semantic_atoms"])
                actual = len(sigs)
                if expected != actual:
                    conservation_issues.append({
                        "rule_id": rule_id,
                        "expected_atoms": expected,
                        "actual_signals": actual,
                    })

        return {
            "total": len(signals),
            "ready": len(ready_signals),
            "not_ready": len(not_ready_signals),
            "by_engine": dict(by_engine),
            "by_status": dict(by_status),
            "by_atom_top10": dict(by_atom.most_common(10)),
            "by_rule_count": len(by_rule),
            "conservation_issues": conservation_issues,
            "conservation_ok": len(conservation_issues) == 0,
        }
