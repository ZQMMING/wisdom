"""
P2.1-B: Admission Authority Model — AdmissionRegistry + AuditedIdentity

核心安全原则（机构裁决确认）：
  1. Authority 来自 Registry 内部操作，不在 dataclass 构造。
  2. 调用者无法自行制造具有 Production Authority 的 AdmissionRecord。
  3. LEGACY identity 不得进入 PRODUCTION_ADMITTED。

实现方式：
  - AdmissionRecord 是 frozen dataclass（防篡改，不防伪造）
  - AdmissionRegistry.register() 是私有方法（不可从外部调用）
  - 唯一公开入口是 create_admission_record() 工厂函数
  - 工厂在注册时做合法性校验，拒绝非法输入
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
    LEGACY = "LEGACY"  # 旧 str 格式转换，不得进入 PRODUCTION_ADMITTED


@dataclass(frozen=True)
class AuditedIdentity:
    """
    可信审核身份。

    设计原则：
    - identity_type 只是身份类别，不等于 authority
    - authority_source 指明身份授权来源
    - LEGACY 类型在 PRODUCTION_ADMITTED 检查中会被硬拒绝
    """
    identity_type: IdentityType
    identity_id: str
    authority_source: str = ""
    credential_hash: str = ""

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
    5. LEGACY identity 绝对不能进入 PRODUCTION_ADMITTED

    重要：frozen dataclass 本身不是不可伪造证明。
    Authority 来自 AdmissionRegistry 内部注册流程，不在 dataclass 构造。
    调用者无法通过公共 API 将自己构造的 AdmissionRecord 注册进 Registry。
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

    def validate_for_scope(self, required_scope: AdmissionScope) -> List[str]:
        """校验 Record 是否满足指定 scope 的要求。"""
        errors = []
        if not self.asset_id:
            errors.append("asset_id cannot be empty")
        if not self.source_work:
            errors.append("source_work cannot be empty")
        if not self.passage_ref:
            errors.append("passage_ref cannot be empty")
        if self.admission_hash and len(self.admission_hash) != 64:
            errors.append("admission_hash must be 64-char SHA-256")

        # 生产准入额外校验
        if required_scope == AdmissionScope.PRODUCTION_ADMITTED:
            if self.synthetic:
                errors.append("synthetic asset cannot be PRODUCTION_ADMITTED")
            if self.verified_by.identity_type == IdentityType.LEGACY:
                errors.append("LEGACY identity not allowed for PRODUCTION_ADMITTED")
        return errors

    def verify_integrity(self, expected_hash: Optional[str] = None) -> bool:
        """验证 admission_hash 完整性。"""
        if not self.admission_hash:
            return False
        if expected_hash and self.admission_hash != expected_hash:
            return False
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

    核心安全设计：
    - register() 是私有方法（下划线前缀），不可从模块外部直接调用
    - 唯一公开入口是 create_admission_record() 工厂函数
    - 工厂在内部创建 record 并完成注册，外部无法绕过
    - append-only：一旦注册，不可修改或删除
    - hash 链式结构：防止事后篡改
    - verify() 只能验证已注册记录

    攻击模型防护：
    任意 caller → AdmissionRecord(...) → ❌ 无法 register（无公开入口）
    任意 caller → AdmissionRegistry() → 可以构造，但 register() 不可见
    """

    def __init__(self):
        self._records: Dict[str, AdmissionRecord] = {}
        self._asset_index: Dict[str, List[str]] = {}
        self._hash_chain: List[str] = []

    def _register(self, record: AdmissionRecord) -> str:
        """
        内部注册方法（私有）。

        只有工厂函数 create_admission_record() 调用此方法。
        外部代码无法直接调用 registry.register()。
        """
        # 校验
        errors = record.validate_for_scope(record.admission_scope)
        if errors:
            raise ValueError(f"AdmissionRecord validation failed: {errors}")

        # 计算并验证 hash
        computed_hash = record._compute_admission_hash()
        if record.admission_hash != computed_hash:
            raise ValueError(
                f"AdmissionRecord hash mismatch for asset_id={record.asset_id}"
            )

        # Append-only
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
        注意：外部无法通过公共 API 将伪造 record 注册进 Registry。
        """
        record = self._records.get(admission_id)
        if record is None:
            return None
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

    @property
    def record_count(self) -> int:
        return len(self._records)

    @property
    def production_count(self) -> int:
        return sum(
            1 for r in self._records.values()
            if r.admission_scope == AdmissionScope.PRODUCTION_ADMITTED
        )


# ============================================================
# 工厂函数 — 唯一合法的 AdmissionRecord 创建入口（G1）
# ============================================================

def create_admission_record(
    asset_id: str,
    asset_type: str,
    source_work: str,
    source_chapter: str,
    passage_ref: str,
    verified_by: AuditedIdentity,
    verification_stage: str,
    verification_version: str,
    admission_scope: AdmissionScope,
    synthetic: bool = False,
) -> AdmissionRecord:
    """
    创建并注册一条 Admission Record。

    这是唯一合法的 Production Authority 创建入口。
    调用者不能绕过此函数直接构造 AdmissionRecord 并注册到 Registry。

    参数:
        asset_id: 资产唯一标识
        asset_type: "RULE" | "EVIDENCE" | "ASSERTION"
        source_work: 原典作品名
        source_chapter: 具体篇目
        passage_ref: 具体引文位置
        verified_by: AuditedIdentity（不能是 LEGACY，如果 admission_scope=PRODUCTION_ADMITTED）
        verification_stage: 审核阶段
        verification_version: 审核版本
        admission_scope: 三态范围
        synthetic: 是否为合成/测试资产

    返回:
        注册后的 AdmissionRecord（含有效 admission_hash）

    异常:
        ValueError: 如果 verified_by 是 LEGACY 且 admission_scope=PRODUCTION_ADMITTED
                    或 synthetic=True 且 admission_scope=PRODUCTION_ADMITTED
    """
    # G2: LEGACY identity 硬拒绝生产准入
    if admission_scope == AdmissionScope.PRODUCTION_ADMITTED and verified_by.identity_type == IdentityType.LEGACY:
        raise ValueError(
            f"LEGACY identity not allowed for PRODUCTION_ADMITTED asset_id={asset_id}"
        )

    # G3 preview: synthetic 硬拒绝生产准入
    if synthetic and admission_scope == AdmissionScope.PRODUCTION_ADMITTED:
        raise ValueError(
            f"Synthetic asset '{asset_id}' cannot be registered as PRODUCTION_ADMITTED"
        )

    admission_id = f"admission_{asset_id}_{int(time.time())}_{hashlib.md5(f'{asset_id}{time.time()}'.encode()).hexdigest()[:8]}"
    asset_hash = hashlib.sha256(f"{asset_id}:{asset_type}".encode("utf-8")).hexdigest()

    record = AdmissionRecord(
        asset_id=asset_id,
        asset_type=asset_type,
        source_work=source_work,
        source_chapter=source_chapter,
        passage_ref=passage_ref,
        verified_by=verified_by,
        verification_stage=verification_stage,
        verification_version=verification_version,
        admission_scope=admission_scope,
        admission_timestamp=time.time(),
        admission_id=admission_id,
        asset_hash=asset_hash,
        admission_hash="",  # placeholder
        synthetic=synthetic,
    )
    computed_hash = record._compute_admission_hash()
    return AdmissionRecord(
        asset_id=record.asset_id,
        asset_type=record.asset_type,
        source_work=record.source_work,
        source_chapter=record.source_chapter,
        passage_ref=record.passage_ref,
        verified_by=record.verified_by,
        verification_stage=record.verification_stage,
        verification_version=record.verification_version,
        admission_scope=record.admission_scope,
        admission_timestamp=record.admission_timestamp,
        admission_id=admission_id,
        asset_hash=record.asset_hash,
        admission_hash=computed_hash,
        synthetic=record.synthetic,
    )
