"""Assertion Observatory - FastAPI路由.

API设计:
- GET  /admin/cases              - 列出cases(内存缓存)
- POST /admin/cases              - 计算新case快照
- GET  /admin/cases/{case_id}    - 获取完整case快照
- GET  /admin/cases/{case_id}/evidence   - 获取EngineEvidence列表
- GET  /admin/cases/{case_id}/atoms      - 获取Semantic Atom映射
- GET  /admin/cases/{case_id}/assertions - 获取Assertion列表
- GET  /admin/assertions/{assertion_id}/trace - 获取追溯链
- GET  /admin/semantic-atoms     - 列出所有Semantic Atom
- GET  /admin/concepts           - 列出所有Modern Concept
- POST /admin/playground/run     - 运行Playground(CURRENT vs PREVIEW)
- GET  /admin/rules/{rule_id}/impact - 规则影响反向查询
- GET  /admin/versions           - 版本信息
- GET  /admin/validate           - 运行P1 Validator
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from .service import (
    compute_case_snapshot, get_rule_impact, run_playground,
    _load_semantic_atoms, _load_modern_concepts, list_rules,
)
from .models import VersionInfo


router = APIRouter(prefix="/admin", tags=["Assertion Observatory"])

# 内存缓存: case_id -> CaseSnapshot
_case_cache: dict[str, Any] = {}


# ═══════════════════════════════════════════════════════════════════
# Request Models
# ═══════════════════════════════════════════════════════════════════

class ComputeCaseRequest(BaseModel):
    birth_year: int = Field(..., ge=1900, le=2100)
    birth_month: int = Field(..., ge=1, le=12)
    birth_day: int = Field(..., ge=1, le=31)
    birth_hour: int = Field(12, ge=0, le=23)
    gender: str = Field("male", pattern="^(male|female)$")
    analysis_date: Optional[str] = None
    theme: str = "GENERAL"
    timezone: Optional[str] = None
    location: Optional[str] = None


class PlaygroundRequest(BaseModel):
    case_id: str
    modified_mapping: Optional[dict[str, Any]] = None
    birth_year: Optional[int] = None
    birth_month: Optional[int] = None
    birth_day: Optional[int] = None
    birth_hour: int = 12
    gender: str = "male"


# ═══════════════════════════════════════════════════════════════════
# Case Routes
# ═══════════════════════════════════════════════════════════════════

@router.get("/cases")
def list_cases() -> dict:
    """列出所有已计算的cases(内存缓存)."""
    return {
        "total": len(_case_cache),
        "cases": [
            {"case_id": cid, "status": snap.status, "evidence_count": sum(snap.evidence_summary.values())}
            for cid, snap in _case_cache.items()
        ],
    }


@router.post("/cases")
def compute_case(req: ComputeCaseRequest) -> dict:
    """计算新case快照(9层完整链路)."""
    snap = compute_case_snapshot(
        birth_date=(req.birth_year, req.birth_month, req.birth_day),
        gender=req.gender,
        hour=req.birth_hour,
        analysis_date=req.analysis_date,
        theme=req.theme,
        timezone=req.timezone,
        location=req.location,
    )
    _case_cache[snap.case_id] = snap
    return snap.to_dict()


@router.get("/cases/{case_id}")
def get_case(case_id: str) -> dict:
    """获取完整case快照."""
    if case_id not in _case_cache:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found. Compute it first via POST /admin/cases")
    return _case_cache[case_id].to_dict()


@router.get("/cases/{case_id}/evidence")
def get_case_evidence(case_id: str, engine: Optional[str] = None) -> dict:
    """获取EngineEvidence列表, 可按engine过滤."""
    if case_id not in _case_cache:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    snap = _case_cache[case_id]
    evidence = snap.evidence
    if engine:
        evidence = [e for e in evidence if e["engine"] == engine]
    return {
        "case_id": case_id,
        "total": len(evidence),
        "evidence": evidence,
    }


@router.get("/cases/{case_id}/atoms")
def get_case_atoms(case_id: str) -> dict:
    """获取Semantic Atom映射(Evidence -> Atom)."""
    if case_id not in _case_cache:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    snap = _case_cache[case_id]
    return {
        "case_id": case_id,
        "total_links": len(snap.evidence_atom_links),
        "atom_summary": snap.semantic_atom_summary,
        "links": [l.to_dict() for l in snap.evidence_atom_links],
    }


@router.get("/cases/{case_id}/signals")
def get_case_signals(case_id: str, status: Optional[str] = None, engine: Optional[str] = None) -> dict:
    """获取P3 SemanticSignal列表(Evidence→Rule→produces_atoms→Signal[]).

    可按status(READY/NOT_READY)和engine过滤.
    显示语义守恒统计和每个Signal的完整信息.
    """
    if case_id not in _case_cache:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    snap = _case_cache[case_id]
    signals = snap.signals
    if status:
        signals = [s for s in signals if s.get("status") == status]
    if engine:
        signals = [s for s in signals if s.get("engine") == engine]
    return {
        "case_id": case_id,
        "total": len(signals),
        "stats": snap.signal_stats,
        "signals": signals,
    }


@router.get("/cases/{case_id}/resolved-rules")
def get_case_resolved_rules(case_id: str, status: Optional[str] = None) -> dict:
    """获取P4-A Rule Resolution结果(Evidence→Resolver→Canonical Rule).

    显示每条EngineEvidence的rule_id如何解析到canonical Rule rule_id,
    以及匹配状态(RESOLVED/PARTIAL/UNRESOLVED/RULE_NOT_FOUND).
    """
    if case_id not in _case_cache:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    snap = _case_cache[case_id]
    resolved = snap.resolved_rules
    if status:
        resolved = [r for r in resolved if r.get("match_status") == status]
    from collections import Counter
    status_counts = Counter(r.get("match_status") for r in snap.resolved_rules)
    return {
        "case_id": case_id,
        "total": len(resolved),
        "by_status": dict(status_counts),
        "resolved_rules": resolved,
    }


@router.get("/cases/{case_id}/assertions")
def get_case_assertions(case_id: str, domain: Optional[str] = None, direction: Optional[str] = None) -> dict:
    """获取P4 CanonicalAssertion列表(Context Resolver产生).

    这是direction唯一允许出现的地方: supportive/caution/neutral.
    可按domain和direction过滤.
    """
    if case_id not in _case_cache:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    snap = _case_cache[case_id]
    assertions = snap.assertions_p4
    if domain:
        assertions = [a for a in assertions if a.get("domain") == domain]
    if direction:
        assertions = [a for a in assertions if a.get("direction") == direction]
    return {
        "case_id": case_id,
        "total": len(assertions),
        "stats": snap.assertion_stats,
        "assertions": assertions,
    }


@router.get("/cases/{case_id}/clusters")
def get_case_clusters(case_id: str, domain: Optional[str] = None) -> dict:
    """获取P4 AssertionCluster列表(互补聚类, 不投票).

    source_engines表示互补覆盖面, evidence_count表示证据数量, 均非权重/概率.
    """
    if case_id not in _case_cache:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    snap = _case_cache[case_id]
    clusters = snap.assertion_clusters
    if domain:
        clusters = [c for c in clusters if c.get("domain") == domain]
    return {
        "case_id": case_id,
        "total": len(clusters),
        "stats": snap.cluster_stats,
        "clusters": clusters,
    }


@router.get("/cases/{case_id}/guidance")
def get_case_guidance(case_id: str, domain: Optional[str] = None) -> dict:
    """获取P5-A GuidanceAtom列表(Assertion→Guidance确定性映射).

    direction_label是"有利条件"/"需要注意"/"无明显方向性偏移", 不是吉凶.
    所有guidance可追溯回source_assertion_ids.
    """
    if case_id not in _case_cache:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    snap = _case_cache[case_id]
    guidance = snap.guidance_atoms
    if domain:
        guidance = [g for g in guidance if g.get("domain") == domain]
    return {
        "case_id": case_id,
        "total": len(guidance),
        "stats": snap.guidance_stats,
        "guidance": guidance,
    }


@router.get("/cases/{case_id}/guidance/composed")
def get_case_guidance_composed(case_id: str) -> dict:
    """获取P5-B ComposedGuidance(组装后的完整用户指引)."""
    if case_id not in _case_cache:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    snap = _case_cache[case_id]
    return snap.composed_guidance or {}


@router.get("/cases/{case_id}/guidance/rendered")
def get_case_guidance_rendered(case_id: str, format: str = "markdown") -> dict:
    """获取P5-C RenderedGuidance(渲染后的用户可读文本).

    format: markdown / text / structured
    """
    if case_id not in _case_cache:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    snap = _case_cache[case_id]

    if format == "markdown":
        return {"format": "markdown", "content": snap.rendered_guidance or ""}
    elif format == "text":
        # 简单去除Markdown
        text = (snap.rendered_guidance or "").replace("#", "").replace("**", "").replace("*", "")
        return {"format": "text", "content": text}
    elif format == "structured":
        return {"format": "structured", "content": snap.composed_guidance or {}}
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")


@router.get("/cases/{case_id}/assertions")
def get_case_assertions(case_id: str) -> dict:
    """获取Assertion列表."""
    if case_id not in _case_cache:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    snap = _case_cache[case_id]
    return {
        "case_id": case_id,
        "total": len(snap.assertions),
        "assertions": [a.to_dict() for a in snap.assertions],
    }


# ═══════════════════════════════════════════════════════════════════
# Assertion Trace
# ═══════════════════════════════════════════════════════════════════

@router.get("/assertions/{assertion_id}/trace")
def get_assertion_trace(assertion_id: str, case_id: Optional[str] = None) -> dict:
    """获取Assertion的完整追溯链.

    从最终断言一路追溯到:
    Guidance -> Mapping -> Assertion -> Semantic Atom -> Evidence -> Engine Raw
    """
    # 在所有cache中查找
    for cid, snap in _case_cache.items():
        if case_id and cid != case_id:
            continue
        for a in snap.assertions:
            if a.assertion_id == assertion_id:
                # 构建完整trace
                trace = a.to_dict()
                # 找到对应的evidence
                trace["evidence_details"] = [
                    e for e in snap.evidence
                    if e["rule_id"] in a.evidence_ids
                ]
                # 找到对应的atom links
                trace["atom_links"] = [
                    l.to_dict() for l in snap.evidence_atom_links
                    if l.evidence_rule_id in a.evidence_ids
                ]
                trace["engine_raw"] = {
                    k: v.to_dict() for k, v in snap.engine_raw.items()
                }
                return trace
    raise HTTPException(status_code=404, detail=f"Assertion {assertion_id} not found")


# ═══════════════════════════════════════════════════════════════════
# Semantic Atom / Concept Registry
# ═══════════════════════════════════════════════════════════════════

@router.get("/semantic-atoms")
def list_semantic_atoms(category: Optional[str] = None) -> dict:
    """列出所有Semantic Atom, 可按category过滤."""
    atoms, _ = _load_semantic_atoms()
    if category:
        atoms = {k: v for k, v in atoms.items() if v.get("category") == category}
    return {
        "total": len(atoms),
        "categories": list(set(v.get("category", "") for v in atoms.values())),
        "atoms": list(atoms.values()),
    }


@router.get("/concepts")
def list_concepts(domain: Optional[str] = None) -> dict:
    """列出所有Modern Concept, 可按domain过滤."""
    concepts = _load_modern_concepts()
    if domain:
        concepts = {k: v for k, v in concepts.items() if domain in v.get("domains", [])}
    return {
        "total": len(concepts),
        "domains": ["CAREER", "FINANCE", "RELATIONSHIP", "FAMILY", "SOCIAL", "GROWTH", "HEALTH", "DECISION"],
        "concepts": list(concepts.values()),
    }


# ═══════════════════════════════════════════════════════════════════
# Playground
# ═══════════════════════════════════════════════════════════════════

@router.post("/playground/run")
def playground_run(req: PlaygroundRequest) -> dict:
    """运行Playground - CURRENT vs PREVIEW对比, 不写生产数据库."""
    birth = None
    if req.birth_year and req.birth_month and req.birth_day:
        birth = (req.birth_year, req.birth_month, req.birth_day)
    result = run_playground(
        case_id=req.case_id,
        modified_mapping=req.modified_mapping,
        birth_date=birth,
        gender=req.gender,
        hour=req.birth_hour,
    )
    return result.to_dict()


# ═══════════════════════════════════════════════════════════════════
# Rule Explorer
# ═══════════════════════════════════════════════════════════════════

@router.get("/rules")
def list_all_rules(
    rule_type: Optional[str] = None,
    migrated: Optional[bool] = None,
) -> dict:
    """列出所有规则, 可按rule_type和迁移状态过滤.

    显示每条规则的: rule_id/title/rule_type/produces_signal_type/
    migrated/produces_semantic_atoms/version.
    """
    return list_rules(rule_type=rule_type, migrated=migrated)


# ═══════════════════════════════════════════════════════════════════
# Rule Impact
# ═══════════════════════════════════════════════════════════════════

@router.get("/rules/{rule_id}/impact")
def rule_impact(rule_id: str) -> dict:
    """规则->结果反向查询.

    查询某条规则:
    - 产生哪些Semantic Atom
    - 被哪些case使用
    - 产生哪些Assertion
    - 影响等级(low/medium/high)
    """
    snapshots = list(_case_cache.values())
    impact = get_rule_impact(rule_id, snapshots)
    return impact.to_dict()


# ═══════════════════════════════════════════════════════════════════
# Version / Validate
# ═══════════════════════════════════════════════════════════════════

@router.get("/versions")
def get_versions() -> dict:
    """获取版本信息."""
    v = VersionInfo()
    return v.to_dict()


@router.get("/validate")
def run_validation() -> dict:
    """运行P1 Validator(数据完整性检查)."""
    import subprocess
    import sys
    result = subprocess.run(
        [sys.executable, "scripts/validate_p1_semantic.py"],
        capture_output=True, text=True, cwd=str(Path(__file__).resolve().parents[3]),
    )
    return {
        "returncode": result.returncode,
        "passed": result.returncode == 0,
        "output": result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout,
        "stderr": result.stderr[-1000:] if result.stderr else "",
    }
