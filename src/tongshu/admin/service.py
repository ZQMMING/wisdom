"""Assertion Observatory - Service层.

核心功能:
1. compute_case_snapshot - 计算完整Case快照(9层)
2. build_evidence_atom_links - Evidence -> Semantic Atom映射
3. build_assertion_traces - 从现有断言构建追溯链
4. get_rule_impact - 规则影响反向查询
5. run_playground - Playground运行(CURRENT vs PREVIEW, 不写库)
"""

from __future__ import annotations
import json
import hashlib
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .models import (
    VersionInfo, InputSnapshot, EngineRawResult,
    EvidenceAtomLink, AssertionTrace, CaseSnapshot,
    PlaygroundResult, RuleImpact,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_semantic_atoms() -> tuple[dict[str, dict], dict[str, str]]:
    """加载所有Semantic Atom, 返回(atom_id->atom, label_zh->atom_id)."""
    atom_dir = _repo_root() / "data" / "semantic_atoms"
    atoms: dict[str, dict] = {}
    label_to_id: dict[str, str] = {}
    for f in sorted(atom_dir.glob("*.json")):
        data = json.load(open(f, encoding="utf-8"))
        for atom in data.get("atoms", []):
            atoms[atom["atom_id"]] = atom
            label_to_id[atom["label_zh"]] = atom["atom_id"]
    return atoms, label_to_id


def _load_modern_concepts() -> dict[str, dict]:
    """加载Modern Concept Registry."""
    path = _repo_root() / "data" / "mapping" / "modern_concepts.json"
    data = json.load(open(path, encoding="utf-8"))
    return {c["concept_id"]: c for c in data.get("concepts", [])}


def _make_case_id(birth: tuple, gender: str, hour: int) -> str:
    """生成稳定的case_id."""
    raw = f"{birth[0]}{birth[1]:02d}{birth[2]:02d}{hour:02d}{gender}"
    return f"case_{hashlib.md5(raw.encode()).hexdigest()[:12]}"


def compute_case_snapshot(
    birth_date: tuple,
    gender: str,
    hour: int = 12,
    analysis_date: Optional[str] = None,
    theme: str = "GENERAL",
    timezone: Optional[str] = None,
    location: Optional[str] = None,
) -> CaseSnapshot:
    """计算完整Case快照(9层链路).

    Layer 1: Input Snapshot
    Layer 2: Engine Raw Result (子平/盲派/紫微/河洛/易经)
    Layer 3: EngineEvidence (P0统一证据)
    Layer 4: Semantic Atom映射
    Layer 5-9: 从现有架构桥接(Assertion/Cluster/Mapping/Guidance/Render)
    """
    from tongshu.assertion.engine_adapters import produce_all_evidence
    from tongshu.assertion.engine_evidence import EngineName

    case_id = _make_case_id(birth_date, gender, hour)
    version = VersionInfo()

    # Layer 1: Input
    input_snap = InputSnapshot(
        case_id=case_id,
        birth_date=birth_date,
        gender=gender,
        analysis_date=analysis_date,
        theme=theme,
        timezone=timezone,
        location=location,
    )

    # 构建context
    context = {
        "birth": (birth_date[0], birth_date[1], birth_date[2], hour, gender),
        "gender": gender,
        "birth_hour": _hour_to_branch(hour),
        "birth_year": birth_date[0],
    }

    # Layer 2: Engine Raw Result (简化, 实际应调用各引擎)
    engine_raw: dict[str, EngineRawResult] = {}
    for name in EngineName:
        engine_raw[name.value] = EngineRawResult(
            engine=name.value,
            status="OK",
            data={"note": "raw result placeholder - full engine integration in P2"},
        )

    # Layer 3: EngineEvidence
    evidence_dict = produce_all_evidence(None, None, context)
    evidence_list = []
    evidence_summary: dict[str, int] = {}
    for name, evs in evidence_dict.items():
        evidence_summary[name.value] = len(evs)
        for ev in evs:
            evidence_list.append(ev.to_dict())

    # Layer 4: Evidence -> Semantic Atom映射
    atoms, label_to_id = _load_semantic_atoms()
    concepts = _load_modern_concepts()
    atom_links: list[EvidenceAtomLink] = []
    atom_summary: dict[str, int] = {}

    for name, evs in evidence_dict.items():
        for ev in evs:
            mapped_atoms = _map_evidence_to_atoms(ev, atoms, label_to_id, concepts)
            link = EvidenceAtomLink(
                evidence_rule_id=ev.rule_id,
                evidence_value=ev.value,
                engine=ev.engine.value,
                temporal_scope=ev.temporal_scope.value,
                mapped_atoms=mapped_atoms,
                mapping_method="static",
            )
            atom_links.append(link)
            for aid in mapped_atoms:
                atom_summary[aid] = atom_summary.get(aid, 0) + 1

    # Layer 5-9: 从现有架构桥接(简化)
    assertion_traces = _build_assertion_traces(evidence_list, atom_links)

    return CaseSnapshot(
        case_id=case_id,
        version=version,
        input=input_snap,
        engine_raw=engine_raw,
        evidence=evidence_list,
        evidence_summary=evidence_summary,
        evidence_atom_links=atom_links,
        semantic_atom_summary=dict(sorted(atom_summary.items(), key=lambda x: -x[1])),
        assertions=assertion_traces,
        guidance=None,
        final_render=None,
        status="CALCULATED",
    )


def _hour_to_branch(hour: int) -> str:
    """小时->地支."""
    branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    return branches[(hour + 1) // 2 % 12]


def _map_evidence_to_atoms(
    ev: Any,
    atoms: dict[str, dict],
    label_to_id: dict[str, str],
    concepts: dict[str, dict],
) -> list[str]:
    """将一条EngineEvidence映射到Semantic Atom列表."""
    mapped: list[str] = []
    val = str(ev.value)

    # 1. 直接匹配label_zh
    if val in label_to_id:
        mapped.append(label_to_id[val])

    # 2. 检查attributes中的element/ten_god/star
    for attr_key, attr_val in ev.attributes.items():
        if isinstance(attr_val, str) and attr_val in label_to_id:
            mapped.append(label_to_id[attr_val])
        elif isinstance(attr_val, list):
            for item in attr_val:
                if isinstance(item, str) and item in label_to_id:
                    mapped.append(label_to_id[item])

    # 3. 通过rule_id前缀推断Atom类别
    rule_prefix = ev.rule_id.split("_")[0] if "_" in ev.rule_id else ev.rule_id
    category_map = {
        "ZP": "TEN_GOD", "BS": "TEN_GOD",
        "ZW": "ZIWEI_MAJOR", "HL": "HEXAGRAM", "YJ": "HEXAGRAM",
    }
    if rule_prefix in category_map:
        # 找到该类别下的所有atom
        for aid, atom in atoms.items():
            if atom.get("category") == category_map[rule_prefix]:
                # 检查value是否匹配atom的label
                if val == atom.get("label_zh"):
                    if aid not in mapped:
                        mapped.append(aid)

    return list(dict.fromkeys(mapped))  # 去重保序


def _build_assertion_traces(
    evidence_list: list[dict],
    atom_links: list[EvidenceAtomLink],
) -> list[AssertionTrace]:
    """从现有证据构建Assertion Trace(简化版, P2-P5完善)."""
    traces: list[AssertionTrace] = []
    # 按engine分组, 每个engine生成一个trace
    by_engine: dict[str, list[dict]] = {}
    for ev in evidence_list:
        eng = ev["engine"]
        by_engine.setdefault(eng, []).append(ev)

    for i, (engine, evs) in enumerate(by_engine.items()):
        # 收集这个engine的所有mapped atoms
        atoms_for_engine = []
        for link in atom_links:
            if link.engine == engine:
                atoms_for_engine.extend(link.mapped_atoms)

        trace = AssertionTrace(
            assertion_id=f"AST_{engine}_{i:03d}",
            domain="GENERAL",
            semantic=f"{engine}_STRUCTURAL",
            direction="neutral",
            intensity=50,
            temporal_scope="birth",
            source_engine=engine,
            source_rule=evs[0]["rule_id"] if evs else "",
            semantic_atoms=list(dict.fromkeys(atoms_for_engine)),
            evidence_ids=[ev["rule_id"] for ev in evs],
        )
        traces.append(trace)

    return traces


def get_rule_impact(rule_id: str, case_snapshots: Optional[list[CaseSnapshot]] = None) -> RuleImpact:
    """规则->结果反向查询.

    查询某条规则:
    - 产生哪些Semantic Atom (produces_semantic_atoms)
    - 每个Atom对应的Modern Concept和Domain候选
    - 被哪些case使用
    - 产生哪些Assertion
    - 影响等级(low/medium/high)
    """
    atoms, label_to_id = _load_semantic_atoms()
    concepts = _load_modern_concepts()

    # 加载规则文件
    rule_path = _repo_root() / "data" / "rules" / f"{rule_id}.json"
    rule_data = None
    produces_atoms = []
    if rule_path.exists():
        with open(rule_path, encoding="utf-8") as f:
            rule_data = json.load(f)
        produces_atoms = rule_data.get("conclusion", {}).get("produces_semantic_atoms", [])

    # 构建Atom -> Concept -> Domain链
    atom_concept_chain = []
    for atom_id in produces_atoms:
        concept = concepts.get(atom_id, {})
        atom_concept_chain.append({
            "atom_id": atom_id,
            "concept_label": concept.get("label_zh", atom_id),
            "domains": concept.get("domains", []),
        })

    # 使用的cases(如果提供了snapshots)
    used_in_cases = []
    if case_snapshots:
        for snap in case_snapshots:
            for ev in snap.evidence:
                if ev.get("rule_id") == rule_id:
                    used_in_cases.append(snap.case_id)
                    break

    # 产生的assertions(简化)
    produces_assertions = [
        {"domain": ac["domains"][0] if ac["domains"] else "GENERAL",
         "semantic": ac["atom_id"], "direction": "neutral"}
        for ac in atom_concept_chain
    ]

    # 影响等级
    impact_level = "medium" if len(produces_atoms) > 3 else "low"
    if used_in_cases:
        impact_level = "high"

    return RuleImpact(
        rule_id=rule_id,
        produces_atoms=produces_atoms,
        used_in_cases=used_in_cases,
        produces_assertions=produces_assertions,
        impact_level=impact_level,
        rule_data=rule_data,
        atom_concept_chain=atom_concept_chain,
    )


def list_rules(rule_type: Optional[str] = None, migrated: Optional[bool] = None) -> dict:
    """列出所有规则, 可按rule_type和迁移状态过滤."""
    rules_dir = _repo_root() / "data" / "rules"
    rules = []
    for f in sorted(rules_dir.glob("*.json")):
        with open(f, encoding="utf-8") as fh:
            r = json.load(fh)
        has_new = "produces_semantic_atoms" in r.get("conclusion", {})
        if rule_type and r.get("rule_type") != rule_type:
            continue
        if migrated is not None and has_new != migrated:
            continue
        rules.append({
            "rule_id": r["rule_id"],
            "title": r.get("title", ""),
            "rule_type": r.get("rule_type", ""),
            "produces_signal_type": r.get("produces_signal_type", ""),
            "migrated": has_new,
            "produces_semantic_atoms": r.get("conclusion", {}).get("produces_semantic_atoms", []),
            "version": r.get("version", ""),
        })
    return {
        "total": len(rules),
        "by_type": dict(Counter(r["rule_type"] for r in rules)),
        "migrated_count": sum(1 for r in rules if r["migrated"]),
        "rules": rules,
    }


def run_playground(
    case_id: str,
    modified_mapping: Optional[dict] = None,
    birth_date: Optional[tuple] = None,
    gender: str = "male",
    hour: int = 12,
) -> PlaygroundResult:
    """Playground运行 - CURRENT vs PREVIEW对比, 不写生产数据库.

    修改Mapping后立即预览结果, 不持久化.
    """
    # CURRENT: 用现有映射计算
    if birth_date:
        current_snap = compute_case_snapshot(birth_date, gender, hour)
    else:
        # 从已有的case加载(简化)
        current_snap = None

    # PREVIEW: 用修改后的映射计算(简化, 实际应重新跑Mapping Layer)
    preview = {
        "modified_mapping": modified_mapping,
        "note": "Preview uses modified mapping - full re-computation in P5",
    }

    # DIFF
    diff = {
        "changed_atoms": list(modified_mapping.keys()) if modified_mapping else [],
        "note": "Diff computed against current mapping",
    }

    return PlaygroundResult(
        case_id=case_id,
        current=current_snap.to_dict() if current_snap else {},
        preview=preview,
        diff=diff,
        modified_mapping=modified_mapping,
    )
