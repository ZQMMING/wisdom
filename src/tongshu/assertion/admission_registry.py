"""
P2.1-B: Admission Authority Model — AdmissionRegistry + AuditedIdentity (v5)

核心安全原则（机构裁决确认）：
  1. AdmissionRegistry 不可被外部代码实例化。
  2. 唯一合法路径：ProductionRuleLoader → AdmissionCapability → AdmissionRegistry
  3. AdmissionCapability 是 module-internal class，外部无法构造。
  4. identity 从 validated provenance 推导，不暴露给 caller。

实现方式（v5）：
  - AdmissionCapability 是内部类，无公开构造入口
  - AdmissionRegistry.__init__ 要求 AdmissionCapability 实例（不是 bool）
  - ProductionRuleLoader 是唯一能构造 AdmissionCapability 的 caller
  - _create_production_admission 接受 AuditedIdentity（从 provenance 推导）
"""
from __future__ import annotations

import enum
import hashlib
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ============================================================
# AdmissionCapability — 唯一合法的 Admission Authority（G1 核心）
# ============================================================

class AdmissionCapability:
    """
    生产准入 Authority Capability。

    核心安全设计：
    - 无公开构造方法（__new__ 私有）
    - 只有同模块内的 AdmissionRegistry 可以持有此对象
    - 外部代码无法 import 或直接构造此对象
    - 持有此对象 = 拥有注册 Production Admission 的权限

    攻击模型防护：
    任意 caller → AdmissionCapability()   ← ❌ TypeError（无法从外部实例化）
    任意 caller → AdmissionRegistry(cap) ← ❌ TypeError（无 cap 对象）
    """

    __slots__ = ()  # 禁止添加属性

    def __new__(cls):
        # 只在模块内部通过 object.__new__ 构造
        raise TypeError("AdmissionCapability cannot be instantiated externally.")

    @classmethod
    def _create(cls) -> "AdmissionCapability":
        """内部工厂：只有模块内代码可调用。"""
        obj = object.__new__(cls)
        return obj


# ============================================================
# AuditedIdentity — 可信审核身份（G2）
# ============================================================

class IdentityType(str, enum.Enum):
    """审核身份类型。"""
    HUMAN = "HUMAN"
    AGENT = "AGENT"
    SYSTEM = "SYSTEM"
    GPT = "GPT"
    LEGACY = "LEGACY"


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
    """严格分离测试/审核/生产三态。"""
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

    重要：Authority 来自 AdmissionCapability（不可伪造的 capability 对象），
    不在 dataclass 构造。外部代码无法获得 AdmissionCapability 实例。
    """
    asset_id: str
    asset_type: str  # "RULE" | "EVIDENCE" | "ASSERTION"

    source_work: str
    source_chapter: str
    passage_ref: str

    verified_by: AuditedIdentity
    verification_stage: str
    verification_version: str

    admission_scope: AdmissionScope
    admission_timestamp: float
    admission_id: str

    asset_hash: str
    admission_hash: str

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
# AdmissionRegistry — 生产准入注册表（G1，v5）
# ============================================================

class AdmissionRegistry:
    """
    生产准入注册表。

    核心安全设计（v5）：
    - __init__ 要求 AdmissionCapability 实例（不是 bool）
    - AdmissionCapability 无法从外部实例化
    - 因此外部代码无法获得 AdmissionRegistry 实例
    - ProductionRuleLoader 是唯一可传入 AdmissionCapability 的 caller

    攻击模型防护（v5）：
    任意 caller → AdmissionRegistry(cap)  ← ❌ TypeError（无 cap 对象）
    任意 caller → AdmissionCapability()  ← ❌ TypeError（无法实例化）
    唯一合法路径：
      ProductionRuleLoader → _create_capability() → AdmissionRegistry(cap)
                            → _create_production_admission(provenance)
    """

    def __init__(self, capability: "AdmissionCapability"):
        """
        内部构造函数。

        要求传入 AdmissionCapability 实例。
        外部代码无法获得 AdmissionCapability 实例。
        """
        if not isinstance(capability, AdmissionCapability):
            raise TypeError(
                "AdmissionRegistry requires an AdmissionCapability instance. "
                "Use ProductionRuleLoader.load() for Production Admission."
            )
        self._records: Dict[str, AdmissionRecord] = {}
        self._asset_index: Dict[str, List[str]] = {}
        self._hash_chain: List[str] = []

    def _register(self, record: AdmissionRecord) -> str:
        """内部注册方法。"""
        errors = record.validate_for_scope(record.admission_scope)
        if errors:
            raise ValueError(f"AdmissionRecord validation failed: {errors}")

        computed_hash = record._compute_admission_hash()
        if record.admission_hash != computed_hash:
            raise ValueError(
                f"AdmissionRecord hash mismatch for asset_id={record.asset_id}"
            )

        if record.admission_id in self._records:
            raise ValueError(
                f"AdmissionRecord with admission_id={record.admission_id} already exists"
            )

        self._records[record.admission_id] = record
        if record.asset_id not in self._asset_index:
            self._asset_index[record.asset_id] = []
        self._asset_index[record.asset_id].append(record.admission_id)

        prev_hash = self._hash_chain[-1] if self._hash_chain else "GENESIS"
        chain_hash = hashlib.sha256(
            f"{prev_hash}:{record.admission_id}:{record.admission_hash}".encode("utf-8")
        ).hexdigest()
        self._hash_chain.append(chain_hash)

        return record.admission_id

    def _create_production_admission(
        self,
        asset_id: str,
        asset_type: str,
        source_work: str,
        source_chapter: str,
        passage_ref: str,
        verified_by: AuditedIdentity,
        verification_stage: str,
        verification_version: str,
        synthetic: bool = False,
    ) -> AdmissionRecord:
        """
        在 Registry 内部创建并注册一条 PRODUCTION_ADMITTED AdmissionRecord。

        参数:
            asset_id: 资产唯一标识
            asset_type: "RULE" | "EVIDENCE" | "ASSERTION"
            source_work: 原典作品名
            source_chapter: 具体篇目
            passage_ref: 具体引文位置
            verified_by: 已从 provenance 验证的 AuditedIdentity（非 caller 注入）
            verification_stage: 审核阶段
            verification_version: 审核版本
            synthetic: 是否为合成/测试资产（PRODUCTION_ADMITTED 时硬拒绝）

        返回:
            注册后的 AdmissionRecord（含有效 admission_hash）

        异常:
            ValueError: synthetic=True 且 PRODUCTION_ADMITTED
        """
        if synthetic:
            raise ValueError(
                f"Synthetic asset '{asset_id}' cannot be admitted to PRODUCTION"
            )

        admission_id = (
            f"admission_{asset_id}_{int(time.time())}_"
            f"{hashlib.md5(f'{asset_id}{time.time()}'.encode()).hexdigest()[:8]}"
        )
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
            admission_scope=AdmissionScope.PRODUCTION_ADMITTED,
            admission_timestamp=time.time(),
            admission_id=admission_id,
            asset_hash=asset_hash,
            admission_hash="",
            synthetic=False,
        )
        computed_hash = record._compute_admission_hash()
        final_record = AdmissionRecord(
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
        self._register(final_record)
        return final_record

    def verify(self, admission_id: str) -> Optional[AdmissionRecord]:
        """验证并返回 Admission Record。None = 不存在或已失效。"""
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

    @staticmethod
    def _create_capability() -> AdmissionCapability:
        """
        内部工厂方法，创建 AdmissionCapability。

        此方法是 AdmissionCapability 的唯一构造入口。
        只有同模块代码（ProductionRuleLoader）可以调用此方法。
        外部代码无法获得 AdmissionCapability 实例。
        """
        return AdmissionCapability._create()
