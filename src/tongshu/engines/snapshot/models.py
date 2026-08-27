"""Calculation Snapshot - 计算快照模型

依据：Architecture Freeze V1.0 §4.2
核心原则：历史结果不因算法升级而变更
"""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import Any


@dataclass(frozen=True)
class ProfileSnapshot:
    """计算时的 Profile 快照"""
    birth_date: date
    birth_time: time
    gender: str
    calendar_system: str
    location: dict[str, Any]  # {latitude, longitude, country, city}
    timezone: str


@dataclass(frozen=True)
class TimeSnapshot:
    """时间解析快照"""
    timezone: str
    utc_datetime: datetime
    local_datetime: datetime
    true_solar_datetime: datetime
    dst: bool
    day_boundary: str
    canonical_date: date


@dataclass(frozen=True)
class CalculationContextSnapshot:
    """计算上下文快照"""
    subject: dict[str, Any]
    time: TimeSnapshot
    policy: dict[str, str]


@dataclass(frozen=True)
class HeluoResultSnapshot:
    """河洛计算结果快照"""
    tian_shu: int
    di_shu: int
    tian_reduced: int
    di_reduced: int
    prenatal_hexagram: str
    yuantang: str
    yuantang_index: int
    postnatal_hexagram: str
    daily_hexagram: str | None


@dataclass(frozen=True)
class StructuralResultSnapshot:
    """卦象结构分析结果快照"""
    hexagram_symbol: dict[str, Any] | None = None
    line_symbol: dict[str, Any] | None = None
    ti_yong: str | None = None
    sheng_ke: str | None = None


@dataclass(frozen=True)
class YiResultSnapshot:
    """易经解释层结果快照"""
    classical_text: dict[str, Any] | None = None
    image_expansion: dict[str, Any] | None = None


@dataclass(frozen=True)
class InterpretationResultSnapshot:
    """最终解释输出快照"""
    state: str
    opportunity: str
    attention: str
    suggestion: str
    source_references: list[str]


@dataclass(frozen=True)
class CalculationSnapshot:
    """
    完整计算快照
    
    不可变，只追加。禁止 UPDATE。
    """
    snapshot_id: uuid.UUID = field(default_factory=uuid.uuid4)
    user_id: uuid.UUID | None = None
    calculation_timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # 版本号
    algorithm_version: str = "heluo-v2.0"
    knowledge_version: str = "knowledge-v1.0"
    rule_set_version: str = "rules-v1.0"
    
    # 快照数据
    profile_snapshot: ProfileSnapshot | None = None
    calculation_context: CalculationContextSnapshot | None = None
    
    # 各层结果
    heluo_result: HeluoResultSnapshot | None = None
    structural_result: StructuralResultSnapshot | None = None
    yi_result: YiResultSnapshot | None = None
    interpretation_result: InterpretationResultSnapshot | None = None
    
    def validate(self) -> list[str]:
        """验证快照完整性，返回错误列表"""
        errors = []
        if not self.profile_snapshot:
            errors.append("profile_snapshot 不能为空")
        if not self.heluo_result:
            errors.append("heluo_result 不能为空")
        if not self.calculation_timestamp:
            errors.append("calculation_timestamp 不能为空")
        return errors
