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

    接收 EngineEvidence 列表, 通过 Rule Resolver + Rule 匹配产生 SemanticSignal 列表.

    链路:
      EngineEvidence(engine, engine_rule_id, value)
        ↓ RuleResolver.resolve()
      ResolvedRule(canonical_rule_ids[], match_status)
        ↓ 对每个canonical_rule_id匹配Rule
      Rule(produces_semantic_atoms)
        ↓ 语义守恒: N atoms → N Signals
      SemanticSignal[]
    """

    def __init__(self, rules_dir: Path | str, map_path: Path | str | None = None):
        self._rules_dir = Path(rules_dir)
        self._rules: dict[str, dict] = {}
        self._load_rules()
        # P4-A: Rule Resolver
        if map_path is None:
            # 默认在rules_dir的上一级data目录下找
            map_path = self._rules_dir.parent / "rule_resolution_map.json"
        from .rule_resolver import RuleResolver
        self._resolver = RuleResolver(map_path, self._rules_dir)
        self._last_resolved: list = []  # 最近一次解析结果, 用于Observatory

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

        P4-A: 先通过RuleResolver解析engine_rule_id → canonical_rule_ids,
        再对每个canonical_rule_id匹配Rule, 产生SemanticSignal.

        Args:
            evidence_list: EngineEvidence 字典列表(每个有engine/rule_id/value/temporal_scope)
            case_id: 命例ID

        Returns:
            SemanticSignal 列表

        语义守恒:
          已迁移规则: produces_semantic_atoms有N个 → 产生N个Signal
          未迁移/未解析规则: 产生1个NOT_READY Signal
        """
        signals: list[SemanticSignal] = []
        self._last_resolved = []

        for ev in evidence_list:
            ev_rule_id = ev.get("rule_id", "")
            engine = ev.get("engine", "")
            temporal_scope = ev.get("temporal_scope", "birth")
            ev_value = ev.get("value", "")

            # P4-A: Rule Resolver 解析
            resolved = self._resolver.resolve(engine, ev_rule_id, ev_value)
            self._last_resolved.append(resolved)

            if resolved.match_status == "RESOLVED" and resolved.canonical_rule_ids:
                # 已解析: 对每个canonical_rule_id匹配Rule
                for canonical_rid in resolved.canonical_rule_ids:
                    rule = self._rules.get(canonical_rid)
                    if rule and self.is_migrated(canonical_rid):
                        atoms = rule["conclusion"]["produces_semantic_atoms"]
                        signal_type = rule.get("produces_signal_type", "")

                        for atom_id in atoms:
                            sig = SemanticSignal(
                                signal_id=make_signal_id(case_id, engine, canonical_rid, atom_id),
                                case_id=case_id,
                                engine=engine,
                                rule_id=canonical_rid,  # 使用canonical rule_id
                                atom_id=atom_id,
                                temporal_scope=temporal_scope,
                                evidence_ref=ev_rule_id,  # 保留原始engine_rule_id
                                status=SignalStatus.READY.value,
                                signal_type=signal_type,
                                context={
                                    "evidence_value": str(ev_value),
                                    "engine_rule_id": ev_rule_id,
                                    "rule_title": rule.get("title", ""),
                                    "rule_type": rule.get("rule_type", ""),
                                    "resolution_type": resolved.resolution_type,
                                },
                            )
                            signals.append(sig)
            else:
                # 未解析/未迁移: 产生NOT_READY Signal
                sig = SemanticSignal(
                    signal_id=make_signal_id(case_id, engine, ev_rule_id, "NOT_READY"),
                    case_id=case_id,
                    engine=engine,
                    rule_id=ev_rule_id,
                    atom_id="NOT_READY",
                    temporal_scope=temporal_scope,
                    evidence_ref=ev_rule_id,
                    status=SignalStatus.NOT_READY.value,
                    signal_type="",
                    context={
                        "evidence_value": str(ev_value),
                        "match_status": resolved.match_status,
                        "resolution_type": resolved.resolution_type,
                        "reason": resolved.reason,
                    },
                )
                signals.append(sig)

        # 验证契约
        errors = validate_signal_contract(signals)
        if errors:
            for e in errors:
                log.error("Signal contract violation: %s", e)

        return signals

    def get_last_resolved(self) -> list:
        """获取最近一次解析结果(用于Observatory)."""
        return self._last_resolved

    def get_stats(self, signals: list[SemanticSignal]) -> dict:
        """统计Signal信息."""
        from collections import Counter

        by_engine = Counter(s.engine for s in signals)
        by_status = Counter(s.status for s in signals)
        by_atom = Counter(s.atom_id for s in signals)
        by_rule = Counter(s.rule_id for s in signals)

        # 语义守恒检查: 按(evidence_rule_id, canonical_rule_id)对检查
        # 注意: 多条EngineEvidence可能映射到同一条canonical rule, 这是正常的一对多映射
        # 语义守恒是指: 对于每条(evidence, rule)对, rule produces N atoms → N signals
        conservation_issues = []
        ready_signals = [s for s in signals if s.status == "READY"]
        not_ready_signals = [s for s in signals if s.status == "NOT_READY"]

        # 按(evidence_ref, rule_id)分组
        from collections import defaultdict
        signals_by_pair: dict[tuple, list] = defaultdict(list)
        for s in ready_signals:
            evidence_ref = s.context.get("engine_rule_id", s.evidence_ref)
            key = (evidence_ref, s.rule_id)
            signals_by_pair[key].append(s)

        for (evidence_ref, rule_id), sigs in signals_by_pair.items():
            rule = self._rules.get(rule_id)
            if rule:
                expected = len(rule["conclusion"]["produces_semantic_atoms"])
                actual = len(sigs)
                if expected != actual:
                    conservation_issues.append({
                        "evidence_rule_id": evidence_ref,
                        "canonical_rule_id": rule_id,
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
