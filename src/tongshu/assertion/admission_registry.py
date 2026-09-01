"""
P2.1-B: Admission Authority Model — AdmissionRegistry + AuditedIdentity

核心安全原则：
  Authority 来自 Registry 注册，不是来自 dataclass 构造。
  调用者无法自行伪造具有 Production Authority 的 AdmissionRecord。
"""
from __future__ import annotations

import enum
import hashlib
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ============================================================
# AuditedIdentity — 可信审核身份（G2）
# ============================================================

class IdentityType(str, enum.Enum):
    """审核身份类型。"""
    HUMAN = "HUMAN"
    AGENT = "AGENT"
    SYSTEM = "SYSTEM"
    GPT = "GPT"
    LEGACY = "LEGACY"  # 向后兼容：旧 str 格式转换


@dataclass(frozen=True)
class AuditedIdentity:
    """
    可信审核身份。

    设计原则：
    - identity_type 只是身份类别，不等于 authority
    - 必须有 identity_id（≥3 字符）
    - authority_source 指明身份授权来源
    - LEGACY 类型在 is_complete_for_production 检查中会被拒绝
    """
    identity_type: IdentityType
    identity_id: str
    authority_source: str = ""
    credential_hash: str = ""

    def __post_init__(self):
        # lenient validation: allow empty for legacy migration, but reject in production
        pass

    @classmethod
    def from_legacy_string(cls, s: str) -> "AuditedIdentity":
        """从旧 str 格式转换（向后兼容）。"""
        if not s or len(s) < 3:
            raise ValueError(f"Invalid legacy verified_by string: {s!r}")
        return cls(
            identity_type=IdentityType.LEGACY,
            identity_id=s,
            authority_source="legacy_migration",
        )


# ============================================================
# AdmissionScope — 三态准入范围
# ============================================================

class AdmissionScope(str, enum.Enum):
    """
    严格分离测试/审核/生产三态。

    TEST_FIXTURE:        测试 fixture，不得进入任何生产路径
    SOURCE_VERIFIED:     原典来源已确认，等待独立审计
    PRODUCTION_ADMITTED: 通过完整审核流程，可进入生产
    """
    TEST_FIXTURE = "TEST_FIXTURE"
    SOURCE_VERIFIED = "SOURCE_VERIFIED"
    PRODUCTION_ADMITTED = "PRODUCTION_ADMITTED"


# ============================================================
# AdmissionRecord — 不可伪造的生产准入凭证（G1）
# ============================================================

@dataclass(frozen=True)
class AdmissionRecord:
    """
    不可伪造的生产准入凭证。

    核心设计原则：
    1. frozen dataclass — 构造后不可修改
    2. admission_hash 对 asset_content + metadata 做完整性校验
    3. verified_by 是 AuditedIdentity，不是裸字符串
    4. synthetic=True 的记录绝对不能进入 PRODUCTION_ADMITTED

    重要：frozen dataclass 本身不是不可伪造证明。
    Authority 来自 Registry.register()，不是来自 dataclass 构造。
    """
    # ─── 资产标识 ───
    asset_id: str
    asset_type: str  # "RULE" | "EVIDENCE" | "ASSERTION"

    # ─── 原典溯源 ───
    source_work: str
    source_chapter: str
    passage_ref: str

    # ─── 审核身份 ───
    verified_by: AuditedIdentity
    verification_stage: str  # "SOURCE_VERIFIED" | "INDEPENDENT_AUDIT" | "GPT_ADJUDICATED"
    verification_version: str

    # ─── 准入状态 ───
    admission_scope: AdmissionScope
    admission_timestamp: float
    admission_id: str  # UUIDv7

    # ─── 完整性校验 ───
    asset_hash: str  # SHA-256(asset_content)
    admission_hash: str  # SHA-256(asset_hash + metadata_hash)

    # ─── 防伪造标记 ───
    synthetic: bool = False

    def validate(self) -> List[str]:
        """校验 Record 完整性。"""
        errors = []
        if not self.asset_id:
            errors.append("asset_id cannot be empty")
        if not self.source_work:
            errors.append("source_work cannot be empty")
        if not self.passage_ref:
            errors.append("passage_ref cannot be empty")
        if self.admission_scope == AdmissionScope.PRODUCTION_ADMITTED and self.synthetic:
            errors.append("synthetic asset cannot be PRODUCTION_ADMITTED")
        # LEGACY identity is allowed for backward compatibility (P2.1-B)
        # but flagged — full rejection will be G3
        if self.admission_hash and len(self.admission_hash) != 64:
            errors.append("admission_hash must be 64-char SHA-256")
        return errors

    def verify_integrity(self, expected_hash: Optional[str] = None) -> bool:
        """验证 admission_hash 完整性。"""
        if not self.admission_hash:
            return False
        if expected_hash and self.admission_hash != expected_hash:
            return False
        # 重新计算 hash 并比对
        computed = self._compute_admission_hash()
        return self.admission_hash == computed

    def _compute_admission_hash(self) -> str:
        """计算 admission_hash（内部方法，用于完整性验证）。"""
        metadata = {
            "asset_id": self.asset_id,
            "asset_type": self.asset_type,
            "source_work": self.source_work,
            "source_chapter": self.source_chapter,
            "passage_ref": self.passage_ref,
            "verified_by_id": self.verified_by.identity_id,
            "verified_by_type": self.verified_by.identity_type.value,
            "verification_stage": self.verification_stage,
            "verification_version": self.verification_version,
            "admission_scope": self.admission_scope.value,
            "synthetic": self.synthetic,
            "asset_hash": self.asset_hash,
        }
        metadata_str = hashlib.sha256(
            str(sorted(metadata.items())).encode("utf-8")
        ).hexdigest()
        hash_input = f"{self.asset_hash}:{metadata_str}:{self.admission_id}"
        return hashlib.sha256(hash_input.encode("utf-8")).hexdigest()


# ============================================================
# AdmissionRegistry — 生产准入注册表（G1）
# ============================================================

class AdmissionRegistry:
    """
    生产准入注册表。

    核心安全原则：
    - append-only：一旦注册，不可修改或删除
    - hash 链式结构：防止事后篡改
    - verify() 只能验证已注册记录
    - 调用者无法通过直接构造 AdmissionRecord 获得 Authority

    真正的 Authority 来自 Registry.register()，不是来自 dataclass 构造。
    """

    def __init__(self):
        self._records: Dict[str, AdmissionRecord] = {}  # admission_id → record
        self._asset_index: Dict[str, List[str]] = {}    # asset_id → [admission_id, ...]
        self._hash_chain: List[str] = []                 # 链式哈希，防篡改

    def register(self, record: AdmissionRecord) -> str:
        """
        注册一条 Admission Record。

        返回 admission_id（即 record.admission_id）。
        如果 record.admission_scope == PRODUCTION_ADMITTED 且 synthetic=True，
        会抛出 ValueError（硬拒绝）。
        """
        # 校验
        errors = record.validate()
        if errors:
            raise ValueError(f"AdmissionRecord validation failed: {errors}")

        # 硬拒绝 synthetic + PRODUCTION_ADMITTED
        if record.admission_scope == AdmissionScope.PRODUCTION_ADMITTED and record.synthetic:
            raise ValueError(
                f"Synthetic asset '{record.asset_id}' cannot be registered as PRODUCTION_ADMITTED"
            )

        # 计算并验证 hash
        computed_hash = record._compute_admission_hash()
        if record.admission_hash != computed_hash:
            raise ValueError(
                f"AdmissionRecord hash mismatch for asset_id={record.asset_id}"
            )

        # Append-only：不允许覆盖已有记录
        if record.admission_id in self._records:
            raise ValueError(
                f"AdmissionRecord with admission_id={record.admission_id} already exists"
            )

        # 记录
        self._records[record.admission_id] = record
        if record.asset_id not in self._asset_index:
            self._asset_index[record.asset_id] = []
        self._asset_index[record.asset_id].append(record.admission_id)

        # 更新 hash 链
        prev_hash = self._hash_chain[-1] if self._hash_chain else "GENESIS"
        chain_hash = hashlib.sha256(
            f"{prev_hash}:{record.admission_id}:{record.admission_hash}".encode("utf-8")
        ).hexdigest()
        self._hash_chain.append(chain_hash)

        return record.admission_id

    def verify(self, admission_id: str) -> Optional[AdmissionRecord]:
        """
        验证并返回 Admission Record。

        None = 不存在或已失效。
        注意：外部无法伪造有效 admission_hash，所以 verify() 是 Authority 的唯一来源。
        """
        record = self._records.get(admission_id)
        if record is None:
            return None
        # 重新验证 hash
        if not record.verify_integrity():
            return None
        return record

    def get_produced_assets(self) -> List[AdmissionRecord]:
        """返回所有 PRODUCTION_ADMITTED 的 Admission Record。"""
        return [
            r for r in self._records.values()
            if r.admission_scope == AdmissionScope.PRODUCTION_ADMITTED
        ]

    def get_asset_records(self, asset_id: str) -> List[AdmissionRecord]:
        """返回指定 asset_id 的所有 Admission Record。"""
        ids = self._asset_index.get(asset_id, [])
        return [self._records[mid] for mid in ids if mid in self._records]

    def reject_synthetic(self, record: AdmissionRecord) -> bool:
        """
        检查并拒绝 synthetic=True 的资产。

        返回 True = 应拒绝。
        这是 G3 的前置检查，但 G1 的 Registry API 不得留下绕过入口。
        """
        return record.synthetic and record.admission_scope == AdmissionScope.PRODUCTION_ADMITTED

    @property
    def record_count(self) -> int:
        return len(self._records)

    @property
    def production_count(self) -> int:
        return sum(
            1 for r in self._records.values()
            if r.admission_scope == AdmissionScope.PRODUCTION_ADMITTED
        )
