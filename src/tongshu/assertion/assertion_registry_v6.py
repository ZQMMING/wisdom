"""
P2.1-B: Admission Authority Model — AdmissionRegistry + AuditedIdentity (v6)

核心安全原则（机构裁决确认）：
  1. AdmissionRegistry 不可被外部代码实例化。
  2. 唯一合法路径：ProductionRuleLoader → object.__new__(AdmissionCapability) → Registry
  3. AdmissionCapability 定义在 assertion_rule_library 模块内部，无公开发放方法。
  4. identity 从 validated provenance 推导，不暴露给 caller。

实现方式（v6）：
  - AdmissionCapability, IdentityType, AuditedIdentity, AdmissionScope,
    AdmissionRecord, AdmissionRegistry 全部定义在此模块
  - 无 _create_capability() 或 _create() 公开方法
  - ProductionRuleLoader.load() 内部直接用 object.__new__(AdmissionCapability)
"""
from __future__ import annotations

import enum
import hashlib
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..spec.canonical import SemanticAtom, AssertionDirection

logger = logging.getLogger(__name__)


# ============================================================
# AdmissionCapability — 唯一合法的 Admission Authority（G1 核心）
# ============================================================

class AdmissionCapability:
    """
    生产准入 Authority Capability。

    核心安全设计（v6）：
    - 无公开构造方法（__new__ 抛 TypeError）
    - 无公开 _create() 或 _create_capability() 方法
    - 唯一合法创建路径：ProductionRuleLoader.load() 内部用 object.__new__()
    """
    __slots__ = ()

    def __new__(cls):
        raise TypeError("AdmissionCapability cannot be instantiated externally.")


# ============================================================
# IdentityType / AuditedIdentity / AdmissionScope
# ============================================================

class IdentityType(str, enum.Enum):
    HUMAN = "HUMAN"
    AGENT = "AGENT"
    SYSTEM = "SYSTEM"
    GPT = "GPT"
    LEGACY = "LEGACY"


@dataclass(frozen=True)
class AuditedIdentity:
    identity_type: IdentityType
    identity_id: str
    authority_source: str = ""
    credential_hash: str = ""

    @classmethod
    def from_legacy_string(cls, s: str) -> "AuditedIdentity":
        if not s or len(s) < 3:
            raise ValueError(f"Invalid legacy verified_by string: {s!r}")
        return cls(
            identity_type=IdentityType.LEGACY,
            identity_id=s,
            authority_source="legacy_migration",
        )


class AdmissionScope(str, enum.Enum):
    TEST_FIXTURE = "TEST_FIXTURE"
    SOURCE_VERIFIED = "SOURCE_VERIFIED"
    PRODUCTION_ADMITTED = "PRODUCTION_ADMITTED"


# ============================================================
# AdmissionRecord
# ============================================================

@dataclass(frozen=True)
class AdmissionRecord:
    asset_id: str
    asset_type: str
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
        if not self.admission_hash:
            return False
        if expected_hash and self.admission_hash != expected_hash:
            return False
        return self.admission_hash == self._compute_admission_hash()

    def _compute_admission_hash(self) -> str:
        metadata = {
            "asset_id": self.asset_id, "asset_type": self.asset_type,
            "source_work": self.source_work, "source_chapter": self.source_chapter,
            "passage_ref": self.passage_ref,
            "verified_by_id": self.verified_by.identity_id,
            "verified_by_type": self.verified_by.identity_type.value,
            "verification_stage": self.verification_stage,
            "verification_version": self.verification_version,
            "admission_scope": self.admission_scope.value,
            "synthetic": self.synthetic, "asset_hash": self.asset_hash,
        }
        metadata_str = hashlib.sha256(
            str(sorted(metadata.items())).encode("utf-8")
        ).hexdigest()
        return hashlib.sha256(
            f"{self.asset_hash}:{metadata_str}:{self.admission_id}".encode("utf-8")
        ).hexdigest()


# ============================================================
# AdmissionRegistry — v6: 无公开 Capability 发放方法
# ============================================================

class AdmissionRegistry:
    """
    生产准入注册表。

    核心安全设计（v6）：
    - __init__ 要求 AdmissionCapability 实例
    - 无任何公开方法可创建或获取 AdmissionCapability
    - _create_production_admission 接受 AuditedIdentity（从 provenance 推导）

    攻击模型防护（v6）：
    任意 caller → AdmissionRegistry()                ← ❌ TypeError（缺少 capability）
    任意 caller → AdmissionCapability()              ← ❌ TypeError（无法实例化）
    任意 caller → AdmissionRegistry._create_capability()  ← ❌ 方法不存在
    任意 caller → AdmissionCapability._create()      ← ❌ 方法不存在
    """

    def __init__(self, capability: AdmissionCapability):
        if not isinstance(capability, AdmissionCapability):
            raise TypeError(
                "AdmissionRegistry requires an AdmissionCapability instance. "
                "Use ProductionRuleLoader.load() for Production Admission."
            )
        self._records: Dict[str, AdmissionRecord] = {}
        self._asset_index: Dict[str, List[str]] = {}
        self._hash_chain: List[str] = []

    def _register(self, record: AdmissionRecord) -> str:
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
        self, asset_id: str, asset_type: str,
        source_work: str, source_chapter: str, passage_ref: str,
        verified_by: AuditedIdentity, verification_stage: str,
        verification_version: str, synthetic: bool = False,
    ) -> AdmissionRecord:
        if synthetic:
            raise ValueError(
                f"Synthetic asset '{asset_id}' cannot be admitted to PRODUCTION"
            )
        admission_id = (
            f"admission_{asset_id}_{int(time.time())}_"
            f"{hashlib.md5(f'{asset_id}{time.time()}'.encode()).hexdigest()[:8]}"
        )
        asset_hash = hashlib.sha256(
            f"{asset_id}:{asset_type}".encode("utf-8")
        ).hexdigest()
        record = AdmissionRecord(
            asset_id=asset_id, asset_type=asset_type,
            source_work=source_work, source_chapter=source_chapter,
            passage_ref=passage_ref, verified_by=verified_by,
            verification_stage=verification_stage,
            verification_version=verification_version,
            admission_scope=AdmissionScope.PRODUCTION_ADMITTED,
            admission_timestamp=time.time(), admission_id=admission_id,
            asset_hash=asset_hash, admission_hash="", synthetic=False,
        )
        final = AdmissionRecord(
            asset_id=record.asset_id, asset_type=record.asset_type,
            source_work=record.source_work, source_chapter=record.source_chapter,
            passage_ref=record.passage_ref, verified_by=record.verified_by,
            verification_stage=record.verification_stage,
            verification_version=record.verification_version,
            admission_scope=record.admission_scope,
            admission_timestamp=record.admission_timestamp,
            admission_id=admission_id, asset_hash=record.asset_hash,
            admission_hash=record._compute_admission_hash(),
            synthetic=record.synthetic,
        )
        self._register(final)
        return final

    def verify(self, admission_id: str) -> Optional[AdmissionRecord]:
        record = self._records.get(admission_id)
        if record is None:
            return None
        if not record.verify_integrity():
            return None
        return record

    def get_produced_assets(self) -> List[AdmissionRecord]:
        return [
            r for r in self._records.values()
            if r.admission_scope == AdmissionScope.PRODUCTION_ADMITTED
        ]

    def get_asset_records(self, asset_id: str) -> List[AdmissionRecord]:
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
