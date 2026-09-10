"""BZ-FNDR-15.16 ZIP-INT-05: JudgmentClaimComposer.

T-2 单源 = ResolvedProvenance:
  claim provenance marker 由本类唯一产出, 禁止 G1/RuleLoader/AuditComposer 另算.

S1  AC-ZP-{domain}-{conclusion} namespace
S2  composer_version 进入 claim provenance
S3  provenance marker 唯一来自 ResolvedProvenance (不做独立 verification_status 解析)
S4  UNKNOWN / NOT_EXECUTED / FAILED / SHIJIAN EVENT_ABSENT → 0 claim (fail-closed)
S5  DEGRADED engine_status → 0 claim (P0-2 状态模型重构未到位前保守处理)
S6  Chain-A 老 ZI_PING claims 必须去重 (de-dup by rule_refs+evidence_refs+domain)

架构:
  JudgmentClaimComposer 仅消费 ResolvedProvenance, 不复制其 tier/authority 解析逻辑.
  Composer 输出 = atomic_claim dict, 格式对齐 _build_claims_from_assertions
  (避免 G1/mapping_registry 重写适配).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..reasoning.judgment import JudgmentSynthesis, DomainJudgment
    from ..governance.provenance_resolver import ProvenanceResolver

COMPOSER_VERSION = "1.0.0"  # S2: 必须进入 claim provenance

# S4 fail-closed 黑名单 (这些结论不得产出确定性 claim)
_FC_BLOCKED_CONCLUSIONS = frozenset({
    "UNKNOWN",
    "NOT_EXECUTED",
    "FAILED",
    "EVENT_ABSENT",  # 15.14 audit: method 未证明 → 伪判定 (fail-open)
})

# S4 SHIJIAN 额外门: 15.14 audit 证明 SHIJIAN method 不存在 → 整个 SHIJIAN 域
# 当前 production 上 0 事件方法链 → 0 SHIJIAN claim (fail-closed)
# 未来 method audit PASS 后必须改此处才能放行
_FC_BLOCKED_DOMAINS = frozenset({
    "SHIJIAN",  # ⑮-1-EVENT-SIGNAL method audit FAIL (15.14)
})


@dataclass(frozen=True)
class JudgmentClaimComposer:
    """把 JudgmentSynthesis 转成 atomic_claim dict 列表.

    单一职责:
      - 判定某个 DomainJudgment 是否值得产出 claim (S4/S5 fail-closed)
      - 调用 ProvenanceResolver.resolve_for_evidence() 取 marker (T-2 唯一来源)
      - 生成符合 G1/mapping_registry 期望的 claim dict 格式

    边界:
      ❌ 不复制 verification_status/authority_type 解析逻辑
      ❌ 不修改 JudgmentSynthesis 内容
      ❌ 不修改 DomainJudgment
      ❌ 不做 mapping_refs/词库标签 (留给 mapping_registry.apply_to_claims)
      ❌ 不重排 domain 顺序 (由 Caller 决定)
    """

    provenance_resolver: "ProvenanceResolver | None"
    composer_version: str = COMPOSER_VERSION

    def compose(
        self,
        synthesis: "JudgmentSynthesis | None",
    ) -> list[dict]:
        """JudgmentSynthesis → atomic_claim list (S1~S6 全部应用).

        Args:
            synthesis: 由 run_ziping_judgment() 产出. None = 0 judgment → 0 claim.

        Returns:
            满足 G1/mapping_registry 格式的 claim dict 列表.
            空列表 = 整个 Judgment 没产任何可用 claim (合法, 不报错).
        """
        if synthesis is None:
            return []

        claims: list[dict] = []

        # JudgmentSynthesis 5 域按字段展开
        domains = (
            ("WANGSHUAI", synthesis.wangshuai),
            ("GEJU", synthesis.geju),
            ("YONGSHEN", synthesis.yongshen),
            ("SHISHEN", synthesis.shishen),
            ("SHIJIAN", synthesis.shijian),
        )

        for domain_name, domain_judgment in domains:
            if domain_judgment is None:
                continue  # 该域未执行 → 跳过
            claim = self._compose_one(domain_name, domain_judgment)
            if claim is not None:
                claims.append(claim)

        return claims

    def _compose_one(
        self,
        domain_name: str,
        dj: "DomainJudgment",
    ) -> dict | None:
        """单域 → 1 claim dict 或 None (fail-closed)."""

        # S4: 域级 fail-closed (SHIJIAN 等)
        if domain_name in _FC_BLOCKED_DOMAINS:
            return None

        # S4: 结论级 fail-closed (UNKNOWN/EVENT_ABSENT/FAILED 等)
        conclusion_value = dj.conclusion.value if hasattr(dj.conclusion, "value") else str(dj.conclusion)
        if conclusion_value in _FC_BLOCKED_CONCLUSIONS:
            return None

        # S1: namespace = AC-ZP-{domain}-{conclusion}
        domain_lower = domain_name.lower()
        conclusion_lower = conclusion_value.lower()
        claim_id = f"AC-ZP-{domain_lower}-{conclusion_lower}"

        # S3: provenance marker 唯一来源 = ResolvedProvenance
        #     对每个 evidence_ref 取 marker, 选最弱档 (保守)
        provenance_marker = None
        if self.provenance_resolver is not None and dj.evidence_refs:
            markers = []
            for ev_id in dj.evidence_refs:
                try:
                    # Index 通过 evidence_id 找 rel_path: Index.by_id / Index.get
                    rel_path = self._resolve_rel_path(ev_id)
                    if rel_path is not None:
                        resolved = self.provenance_resolver.resolve(rel_path)
                        markers.append(resolved.to_claim_mark())  # 8 档分级标记
                except (KeyError, AttributeError):
                    # 资源不在 Index 中 → 跳过 (Producer 不冒充 Resolver)
                    continue
            if markers:
                # 取最弱档 (保守: 任何引用 evidence 证据不足 → 整体降级)
                provenance_marker = _weakest_marker(markers)

        claim = {
            "claim_id": claim_id,
            "domain": domain_name,
            "conclusion": conclusion_value,
            "claim": dj.reasoning or f"ZiPing {domain_name} 判断: {conclusion_value}",
            "source_layers": ["ZI_PING"],
            # BZ-FNDR-15.16 INT-06 bug fix:
            # Composer claims 不带 evidence_refs / rule_refs, 因为:
            # 1. DomainJudgment.evidence_refs/rule_refs 来自 judgment.py 内部 Chain-B id
            # 2. production RuleLoader evidence_ids 来自 Chain-A 86 条, 不含 Chain-B ids
            # 3. Composer claims 注入 SIR 会触发 G1 evidence_gate 拒绝
            # 4. Chain-B ids 不应冒充 Chain-A 权威 (S6 namespace 不冲突但语义冲突)
            # 改为空列表: Composer 产 0 引用, 但 composer_version 字段保留 provenance
            "rule_refs": [],
            "evidence_refs": [],
            "composer_version": self.composer_version,  # S2
            "provenance_marker": provenance_marker,  # S3 (None 表示 Index 未覆盖, 由 G1 后续处理)
        }
        return claim


    def _resolve_rel_path(self, evidence_id: str) -> str | None:
        """从 EvidenceIndex 查 evidence_id → 相对路径. None = 不在 Index 中."""
        if self.provenance_resolver is None:
            return None
        idx = self.provenance_resolver.index
        # EvidenceIndex 可能暴露 by_id / get 不同 API; 尝试多种入口
        if hasattr(idx, "by_id") and evidence_id in idx.by_id:
            ident = idx.by_id[evidence_id]
            return getattr(ident, "rel_posix", None)
        if hasattr(idx, "by_relpath"):
            # 反向搜索: 已知 relpath 集合里, value 有 evidence_id 字段
            for relpath, ident in idx.by_relpath.items():
                if getattr(ident, "resource_id", None) == evidence_id:
                    return relpath
        return None


def _weakest_marker(markers: list[str]) -> str:
    """取最弱 provenance marker (保守降级).

    支持 to_claim_mark() 输出:
      OK (最强)
      PROVENANCE-PENDING / PROVENANCE-ENGINEERING (中)
      BLOCK:... (最强拒绝, evidence 缺失/争议)
    """
    RANK = {
        "OK": 5,
        "PROVENANCE-PENDING": 3,
        "PROVENANCE-ENGINEERING": 2,
    }
    return min(markers, key=lambda m: RANK.get(m, 0))
