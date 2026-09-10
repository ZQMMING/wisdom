"""Resolved Provenance — G0-2 基础设施（BZ-FNDR-15.11 §2 / 15.12 ① 语义衔接）。

将 evidence 资源的两层原始 status（顶层 verification_status 与
citation.verification_status, 15.9 §④ 已证二者互补而非互斥）+ authority_type +
source_layer 解析为"生产可用"的 Resolved Provenance。

已锁定规则（15.11 §2, User V3+V4 裁决）:
    verified / cross_verified / pending / UNVERIFIED / missing /
    not_applicable / disputed / unknown-invalid  八档分级放行表。

红线（User 2026-09-10 正式施工授权 + 三条施工红线）:
    🔒 G1 不修改 —— 本模块【不调用、不改写、不覆盖】 g1_evidence.py 任何逻辑；
       它只【产出】 ResolvedProvenance（含放行判定 + claim 标记 + BLOCK 理由），
       由未来的 JudgmentClaimComposer 消费（15.11 §3.1 分工: ② 可见性 / ③ 权威 / G1 终 Gate）。
    ❌ 不覆盖原始字段 —— Raw Top-level / Raw Nested Citation 原样保留在
       ResolvedProvenance.raw_* 中（"原始状态保留, 解析态另行计算", 15.11 §2.3）。
    ❌ G1 PASS 永不把 pending 升级 verified —— 本模块无此路径; disputed/unknown
       一律 BLOCK（15.11 §2.1 表）。
    ❌ 本模块不修改任何 evidence 资源文件（Infrastructure Change ≠ Evidence Change）。

大小写/命名归一（15.9 §⑦, 在 Resolved 层做, 不动原始资源）:
    PENDING_VERIFICATION / SOURCE_VERIFICATION_REQUIRED /
    CASE_SOURCE_VERIFICATION_REQUIRED  → 归入 G-PENDING 档
    UNVERIFIED → G-UNVERIFIED 档;  缺失 → G-MISSING 档
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Set

from .evidence_index import EvidenceIndex, ResourceIdentity


class ProvenanceTier(str, Enum):
    """③ 分级档（V3）: 决定 claim 的放行与标记; BLOCK 档禁止产生生产 claim。"""

    VERIFIED = "VERIFIED"                      # verified
    CROSS_VERIFIED = "CROSS_VERIFIED"          # cross_verified (保留交叉核验标识)
    PENDING = "PENDING"                        # pending_verification 系 (含大小写归一)
    UNVERIFIED = "UNVERIFIED"                  # 抽取批占位
    MISSING = "MISSING"                        # 字段缺失 (不得伪装已核验)
    NOT_APPLICABLE = "NOT_APPLICABLE"          # 工程种子
    DISPUTED = "DISPUTED"                      # BLOCK
    UNKNOWN = "UNKNOWN"                        # 未知/非法值 → BLOCK


# --- 取值归一表（15.9 §①④⑦ 全仓实测取值 → 档） ---
# 顶层抽取批体系（非 schema enum, 历史批次）
_TOP_TIER_MAP: Dict[str, ProvenanceTier] = {
    "unverified": ProvenanceTier.UNVERIFIED,
    "source_verification_required": ProvenanceTier.PENDING,
    "case_source_verification_required": ProvenanceTier.PENDING,
    "pending_verification": ProvenanceTier.PENDING,   # 大小写归一: 15.9 §⑦ PENDING_VERIFICATION
    "verified": ProvenanceTier.VERIFIED,
    "cross_verified": ProvenanceTier.CROSS_VERIFIED,
    "not_applicable": ProvenanceTier.NOT_APPLICABLE,
    "disputed": ProvenanceTier.DISPUTED,
}

# 嵌套 citation.verification_status（schema v1.1 enum, M2-A/B）
_CIT_TIER_MAP: Dict[str, ProvenanceTier] = dict(_TOP_TIER_MAP)

_MISSING = "<MISSING>"


def _norm(value: str) -> str:
    """归一: 去首尾空白 + 全小写（PENDING_VERIFICATION ≡ pending_verification）。"""
    return (value or "").strip().lower()


@dataclass
class ResolvedProvenance:
    """单个资源的解析态 provenance。原始字段只读保留, 解析结果另行计算。"""

    identity: ResourceIdentity
    tier: ProvenanceTier
    authority_type: str            # 原样（<MISSING> 容许, 不做权威判定）
    source_layer: str              # 原样
    # --- raw 保留（15.11 §2.3 硬边界: 不覆盖） ---
    raw_top_verification_status: str
    raw_citation_verification_status: str
    # --- 生产行为 ---
    admitted: bool                 # False = BLOCK（不得产生生产 claim）
    claim_markers: Set[str] = field(default_factory=set)
    block_reason: Optional[str] = None

    def to_claim_mark(self) -> str:
        """供 JudgmentClaimComposer 消费的单标记字符串（③ claim 行为列, 15.11 §2.1）。"""
        if not self.admitted:
            return f"BLOCK:{self.block_reason or self.tier.value}"
        if self.tier in (ProvenanceTier.VERIFIED, ProvenanceTier.CROSS_VERIFIED):
            return "OK"
        if self.tier == ProvenanceTier.NOT_APPLICABLE:
            return "PROVENANCE-ENGINEERING"
        # PENDING / UNVERIFIED / MISSING 均放行但显式标记（"可放行 ≠ 证据已证明"）
        return "PROVENANCE-PENDING"


class ProvenanceResolver:
    """③ V3+V4 分级放行计算器（消费 G0-1 Index, 不触碰 G1）。"""

    def __init__(self, index: EvidenceIndex) -> None:
        self.index = index

    # --- 单资源解析 ---
    def resolve(self, relative_path: str) -> ResolvedProvenance:
        identity = self.index.get(relative_path)
        if identity is None:
            raise KeyError(f"resource not in index: {relative_path}")
        raw_top = self.index.raw_top_status.get(relative_path, _MISSING)
        raw_cit = self.index.raw_cit_status.get(relative_path, _MISSING)
        authority = self.index.raw_authority.get(relative_path, _MISSING)
        source_layer = self.index.raw_source_layer.get(relative_path, _MISSING)
        tier = self._resolve_tier(raw_top, raw_cit)
        return self._build(identity, tier, raw_top, raw_cit, authority, source_layer)

    def _resolve_tier(self, raw_top: str, raw_cit: str) -> ProvenanceTier:
        """两层 status 合并为一个档。

        规则（③ 裁决 + 15.9 §④ 分层事实 + 15.11 §2.3）:
          - 任一层 DISPUTED / UNKNOWN → 一票否决（BLOCK）
          - 两层【均】缺失            → MISSING（显式标记, 不伪装）
          - 缺失层【不参与合并】: 只在有值的层里取更弱者。
            （缺失 ≠ 否定核验; 不得因顶层缺字段就抹掉嵌套的 verified）
        """
        t_top = self._tier_of(raw_top, _TOP_TIER_MAP, allow_missing=True)
        t_cit = self._tier_of(raw_cit, _CIT_TIER_MAP, allow_missing=True)

        for t in (t_top, t_cit):
            if t is ProvenanceTier.DISPUTED:
                return ProvenanceTier.DISPUTED
            if t is ProvenanceTier.UNKNOWN:
                return ProvenanceTier.UNKNOWN
        if t_top is ProvenanceTier.MISSING and t_cit is ProvenanceTier.MISSING:
            return ProvenanceTier.MISSING

        # 仅取有值层, 缺失层不降级。档内"更弱"排序: 数值越大越弱。
        order = [
            ProvenanceTier.VERIFIED,
            ProvenanceTier.CROSS_VERIFIED,
            ProvenanceTier.NOT_APPLICABLE,
            ProvenanceTier.PENDING,
            ProvenanceTier.UNVERIFIED,
        ]

        def rank(t: ProvenanceTier) -> int:
            try:
                return order.index(t)
            except ValueError:
                return 99

        candidates = [t for t in (t_top, t_cit) if t is not ProvenanceTier.MISSING]
        return max(candidates, key=rank)

    @staticmethod
    def _tier_of(value: str, table: Dict[str, ProvenanceTier], allow_missing: bool) -> ProvenanceTier:
        if value == _MISSING:
            return ProvenanceTier.MISSING
        key = _norm(value)
        tier = table.get(key)
        if tier is None:
            return ProvenanceTier.UNKNOWN
        return tier

    def _build(
        self,
        identity: ResourceIdentity,
        tier: ProvenanceTier,
        raw_top: str,
        raw_cit: str,
        authority: str = "",
        source_layer: str = "",
    ) -> ResolvedProvenance:
        admitted = tier not in (ProvenanceTier.DISPUTED, ProvenanceTier.UNKNOWN)
        markers: Set[str] = set()
        block_reason = None
        if not admitted:
            block_reason = "DISPUTED" if tier is ProvenanceTier.DISPUTED else "UNKNOWN_OR_INVALID_STATUS"
        else:
            if tier in (ProvenanceTier.PENDING, ProvenanceTier.UNVERIFIED, ProvenanceTier.MISSING):
                markers.add("PROVENANCE-PENDING")
            if tier is ProvenanceTier.NOT_APPLICABLE:
                markers.add("PROVENANCE-ENGINEERING")
            if tier is ProvenanceTier.CROSS_VERIFIED:
                markers.add("CROSS-VERIFIED")
        return ResolvedProvenance(
            identity=identity,
            tier=tier,
            authority_type=authority,
            source_layer=source_layer,
            raw_top_verification_status=raw_top,
            raw_citation_verification_status=raw_cit,
            admitted=admitted,
            claim_markers=markers,
            block_reason=block_reason,
        )

    # --- 批量（V4: 只作用于 Index 可见资源） ---
    def resolve_all(self) -> Dict[str, ResolvedProvenance]:
        return {rel: self.resolve(rel) for rel in self.index.by_relpath}

    def tier_summary(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for rel in self.index.by_relpath:
            t = self._resolve_tier(
                self.index.raw_top_status.get(rel, _MISSING),
                self.index.raw_cit_status.get(rel, _MISSING),
            )
            out[t.value] = out.get(t.value, 0) + 1
        return out
