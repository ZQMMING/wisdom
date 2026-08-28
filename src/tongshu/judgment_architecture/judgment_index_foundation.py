"""P6-C-3C-3 Judgment Index Foundation - 断言索引基础层.

核心原则:
- 5个独立Index (不是一个大子平Index)
- 资产质量状态机: RAW → NORMALIZED → MACHINE_VALIDATED → SOURCE_VERIFIED → MATCH_VERIFIED → GOLDEN → ACTIVE
- CoverageMatrix: 计算引擎产生的Feature, 有多少已经存在可检索的原典Judgment
- 覆盖率≠命理准确率, 只回答"有多少Feature有对应的原典Judgment"

资产质量状态机:
  RAW              原始导入, 未处理
  NORMALIZED       已标准化格式
  MACHINE_VALIDATED Schema验证通过 (字段完整, 类型正确)
  SOURCE_VERIFIED  原典来源验证通过 (书名/章节/页码可追溯)
  MATCH_VERIFIED   匹配验证通过 (正向案例MATCH, 负向案例REJECT)
  GOLDEN           黄金资产 (通过全部验证, 可用于Golden Dataset)
  ACTIVE           活跃资产 (可用于生产环境检索)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from tongshu.judgment_architecture.judgment_asset_v2 import (
    JudgmentAssetV2, JudgmentLibraryV2, SchoolIsolatedResolver,
    MatchStatus, ConditionStatus,
)
from tongshu.judgment_architecture.system_school_contract import (
    DivinationSystem, ZiPingSchool,
)


# ============================================================================
# 1. 资产质量状态机
# ============================================================================

class AssetQualityStatus(str, Enum):
    """资产质量状态 - 每条断言不是一导入就ACTIVE."""
    RAW = "RAW"                           # 原始导入, 未处理
    NORMALIZED = "NORMALIZED"             # 已标准化格式
    MACHINE_VALIDATED = "MACHINE_VALIDATED"  # Schema验证通过
    SOURCE_VERIFIED = "SOURCE_VERIFIED"  # 原典来源验证通过
    MATCH_VERIFIED = "MATCH_VERIFIED"    # 匹配验证通过 (正向+负向)
    GOLDEN = "GOLDEN"                     # 黄金资产 (通过全部验证)
    ACTIVE = "ACTIVE"                     # 活跃资产 (可用于生产)


class ValidationResult(str, Enum):
    """验证结果."""
    PASS = "PASS"
    FAIL = "FAIL"
    PENDING = "PENDING"
    SKIP = "SKIP"


@dataclass(frozen=True)
class AssetValidationRecord:
    """资产验证记录 - 每条断言的验证历史."""
    judgment_id: str
    validation_type: str               # SCHEMA/SOURCE/MATCH_POSITIVE/MATCH_NEGATIVE/EVIDENCE
    result: str                        # PASS/FAIL/PENDING/SKIP
    detail: str = ""                   # 验证详情
    validator: str = ""                # 验证者 (自动/人工)
    validated_at: str = ""             # 验证时间

    def to_dict(self) -> dict:
        return {
            "judgment_id": self.judgment_id,
            "validation_type": self.validation_type,
            "result": self.result,
            "detail": self.detail,
            "validator": self.validator,
            "validated_at": self.validated_at,
        }


# ============================================================================
# 2. 独立 Judgment Index (按school隔离)
# ============================================================================

@dataclass
class JudgmentIndex:
    """独立 Judgment Index - 每个school一个独立Index.

    不能因为同属八字, 就共用一个Judgment Pool.
    """
    system: str                        # 体系 (如 ZI_PING)
    school: str                        # 经典 (如 SAN_MING_TONG_HUI)
    library: JudgmentLibraryV2 = field(default_factory=JudgmentLibraryV2)
    resolver: Optional[SchoolIsolatedResolver] = None
    validation_records: list[AssetValidationRecord] = field(default_factory=list)
    coverage_stats: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.resolver is None:
            self.resolver = SchoolIsolatedResolver(self.library)

    def add_judgment(self, judgment: JudgmentAssetV2, initial_status: str = AssetQualityStatus.RAW.value) -> None:
        """添加断言到Index."""
        # 验证school匹配
        if judgment.school != self.school:
            raise ValueError(f"Judgment {judgment.judgment_id} school={judgment.school} 与 Index school={self.school} 不匹配")
        self.library.add(judgment)

    def get_judgment(self, judgment_id: str) -> Optional[JudgmentAssetV2]:
        return self.library.get(judgment_id)

    def get_all_judgments(self) -> list[JudgmentAssetV2]:
        return self.library.get_all()

    def resolve(self, features: dict[str, Any]) -> list:
        """检索匹配的断言."""
        return self.resolver.resolve(self.system, self.school, features)

    def resolve_grouped(self, features: dict[str, Any]) -> dict[str, list]:
        """按RetrievalPartition分组检索."""
        return self.resolver.resolve_grouped(self.system, self.school, features)

    def stats(self) -> dict[str, Any]:
        """Index统计."""
        base_stats = self.library.stats()
        return {
            "system": self.system,
            "school": self.school,
            "total": base_stats["total"],
            "validation_records": len(self.validation_records),
        }

    def add_validation_record(self, record: AssetValidationRecord) -> None:
        """添加验证记录."""
        self.validation_records.append(record)


# ============================================================================
# 3. Judgment Index Foundation (5个独立Index管理)
# ============================================================================

class JudgmentIndexFoundation:
    """Judgment Index Foundation - 5个独立Index管理.

    ZI_PING
    ├── DI_TIAN_SUI_INDEX
    ├── ZI_PING_ZHEN_QUAN_INDEX
    ├── QIONG_TONG_BAO_JIAN_INDEX
    ├── YUAN_HAI_ZI_PING_INDEX
    └── SAN_MING_TONG_HUI_INDEX
    """

    def __init__(self, system: str = DivinationSystem.ZI_PING.value):
        self.system = system
        self.indices: dict[str, JudgmentIndex] = {}
        # 初始化5个独立Index
        for school in ZiPingSchool:
            self.indices[school.value] = JudgmentIndex(
                system=system, school=school.value
            )

    def get_index(self, school: str) -> JudgmentIndex:
        """获取指定school的Index."""
        if school not in self.indices:
            raise ValueError(f"School {school} 不存在, 可用: {list(self.indices.keys())}")
        return self.indices[school]

    def add_judgment(self, judgment: JudgmentAssetV2) -> None:
        """添加断言到对应的Index."""
        index = self.get_index(judgment.school)
        index.add_judgment(judgment)

    def resolve_all(self, features: dict[str, Any]) -> dict[str, list]:
        """在所有Index中检索, 返回按school分组的结果."""
        result = {}
        for school, index in self.indices.items():
            result[school] = index.resolve(features)
        return result

    def resolve_all_grouped(self, features: dict[str, Any]) -> dict[str, dict[str, list]]:
        """在所有Index中检索, 返回按school+partition分组的结果."""
        result = {}
        for school, index in self.indices.items():
            result[school] = index.resolve_grouped(features)
        return result

    def stats(self) -> dict[str, Any]:
        """全部Index统计."""
        result = {
            "system": self.system,
            "total_indices": len(self.indices),
            "total_judgments": 0,
            "by_school": {},
        }
        for school, index in self.indices.items():
            index_stats = index.stats()
            result["by_school"][school] = index_stats
            result["total_judgments"] += index_stats["total"]
        return result


# ============================================================================
# 4. Coverage Matrix (覆盖率矩阵)
# ============================================================================

@dataclass
class CoverageEntry:
    """覆盖率条目 - 某个Feature Pattern的覆盖情况."""
    feature_pattern: str              # Feature模式 (如 ZP.DAY_PILLAR+ZP.HOUR_PILLAR)
    school: str                       # 经典
    judgment_type: str                # 断言类型
    total_features: int               # 该模式下的Feature总数
    covered_features: int             # 已有Judgment覆盖的Feature数
    coverage_rate: float              # 覆盖率

    def to_dict(self) -> dict:
        return {
            "feature_pattern": self.feature_pattern,
            "school": self.school,
            "judgment_type": self.judgment_type,
            "total_features": self.total_features,
            "covered_features": self.covered_features,
            "coverage_rate": f"{self.coverage_rate:.1%}",
        }


class CoverageMatrix:
    """覆盖率矩阵 - Observatory展示用.

    覆盖率≠命理准确率, 只回答:
    计算引擎产生的Feature, 有多少已经存在可检索的原典Judgment.
    """

    def __init__(self, foundation: JudgmentIndexFoundation):
        self.foundation = foundation
        self.entries: list[CoverageEntry] = []

    def calculate_coverage(self, features: dict[str, Any]) -> dict[str, Any]:
        """计算给定Feature集的覆盖率."""
        result = {
            "total_features": len(features),
            "by_school": {},
            "overall_coverage": 0.0,
        }

        total_covered = 0
        for school, index in self.foundation.indices.items():
            # 检索该school的匹配结果
            matches = index.resolve(features)
            matched_count = sum(1 for m in matches if m.match_status == MatchStatus.MATCH.value)

            # 计算该school覆盖的Feature数 (匹配的Judgment涉及的Feature)
            covered_features = set()
            for m in matches:
                if m.match_status == MatchStatus.MATCH.value:
                    for ce in m.condition_evaluations:
                        if ce.status == ConditionStatus.SATISFIED.value:
                            covered_features.add(ce.feature)

            school_coverage = len(covered_features) / len(features) if features else 0
            result["by_school"][school] = {
                "matched_judgments": matched_count,
                "covered_features": len(covered_features),
                "coverage_rate": f"{school_coverage:.1%}",
            }
            total_covered = max(total_covered, len(covered_features))

        result["overall_coverage"] = f"{total_covered / len(features):.1%}" if features else "0%"
        return result

    def generate_observatory_report(self, features: dict[str, Any]) -> str:
        """生成Observatory覆盖率报告."""
        coverage = self.calculate_coverage(features)
        lines = [
            "=" * 70,
            "Coverage Matrix - 覆盖率报告",
            "=" * 70,
            f"总Feature数: {coverage['total_features']}",
            f"整体覆盖率: {coverage['overall_coverage']}",
            "",
            f"{'经典':<25} {'匹配断言':<10} {'覆盖Feature':<12} {'覆盖率':<10}",
            "-" * 70,
        ]
        for school, data in coverage["by_school"].items():
            lines.append(
                f"{school:<25} {data['matched_judgments']:<10} "
                f"{data['covered_features']:<12} {data['coverage_rate']:<10}"
            )
        lines.append("=" * 70)
        lines.append("注意: 覆盖率≠命理准确率, 只回答'有多少Feature有对应的原典Judgment'")
        return "\n".join(lines)


if __name__ == "__main__":
    print("=" * 70)
    print("P6-C-3C-3 Judgment Index Foundation - 快速测试")
    print("=" * 70)

    # 1. 创建Foundation
    print("\n[1] 创建Judgment Index Foundation (5个独立Index):")
    foundation = JudgmentIndexFoundation()
    stats = foundation.stats()
    print(f"  System: {stats['system']}")
    print(f"  Index数量: {stats['total_indices']}")
    print(f"  School列表: {list(stats['by_school'].keys())}")

    # 2. 加载50条Vertical Slice
    print("\n[2] 加载50条Vertical Slice断言:")
    from tongshu.judgment_architecture.vertical_slice_50 import build_vertical_slice_library
    slice_library = build_vertical_slice_library()
    for j in slice_library.get_all():
        foundation.add_judgment(j)
    stats = foundation.stats()
    print(f"  总断言数: {stats['total_judgments']}")
    for school, data in stats["by_school"].items():
        print(f"    {school}: {data['total']}")

    # 3. 资产质量状态机
    print("\n[3] 资产质量状态机:")
    print(f"  状态: {[s.value for s in AssetQualityStatus]}")
    print("  RAW → NORMALIZED → MACHINE_VALIDATED → SOURCE_VERIFIED → MATCH_VERIFIED → GOLDEN → ACTIVE")

    # 4. Coverage Matrix
    print("\n[4] Coverage Matrix - 1983案例覆盖率:")
    from tongshu.engines.bazi_engine import BaziEngine
    from tongshu.feature_registry import FeatureRegistry, ZiPingFeatureAdapter

    engine = BaziEngine()
    chart = engine.compute((1983, 11, 3, 12), "male")
    registry = FeatureRegistry()
    adapter = ZiPingFeatureAdapter(registry)
    feature_result = adapter.adapt(chart)
    features = {f.feature_id: f.value for f in feature_result.resolved_features}

    coverage_matrix = CoverageMatrix(foundation)
    report = coverage_matrix.generate_observatory_report(features)
    print(report)

    # 5. 检索验证
    print("\n[5] 检索验证 - 三命通会乙未日壬午时:")
    smth_index = foundation.get_index("SAN_MING_TONG_HUI")
    results = smth_index.resolve(features)
    matches = [r for r in results if r.match_status == MatchStatus.MATCH.value]
    print(f"  MATCH数量: {len(matches)}")
    for m in matches:
        print(f"    - {m.judgment.judgment_id} (specificity={m.judgment.specificity.level})")
        print(f"      原典: {m.judgment.classical[:50]}...")
        print(f"      来源: {m.judgment.source_locator}")

    print("\n" + "=" * 70)
    print("P6-C-3C-3 Judgment Index Foundation 测试通过")
    print("=" * 70)
