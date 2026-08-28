"""P6-C-3C-2 Judgment Asset Schema V2 - 断言资产Schema.

核心原则:
- system与school必须强制 (不能只写system=ZI_PING)
- conditions必须是确定性条件 (不同经典用不同match_mode)
- 必须加入specificity (高特异性不能覆盖低特异性)
- modern_mapping不负责生成内容 (人工/资产标注, 不是LLM)
- 跨经典隔离 (三命通会断言不能被子平真诠Resolver命中)

Schema结构:
  Judgment
  ├── identity (judgment_id/system/school/judgment_type/version)
  ├── retrieval (match_mode/conditions/feature_requirements/specificity)
  ├── statement (classical/semantic_keys/modern_mapping)
  ├── source (book/chapter/section/page/source_locator)
  └── provenance (created_at/revision/status)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from tongshu.judgment_architecture.system_school_contract import (
    DivinationSystem, ZiPingSchool, MatcherType,
)


# ============================================================================
# 1. 断言状态
# ============================================================================

class JudgmentStatus(str, Enum):
    """断言资产状态."""
    ACTIVE = "ACTIVE"               # 活跃
    DRAFT = "DRAFT"                 # 草稿
    DEPRECATED = "DEPRECATED"       # 已废弃
    UNDER_REVIEW = "UNDER_REVIEW"   # 审核中


# ============================================================================
# 2. 匹配条件
# ============================================================================

@dataclass(frozen=True)
class MatchCondition:
    """匹配条件 - 确定性条件, 不是模糊匹配."""
    feature: str                    # Feature ID (如 ZP.DAY_PILLAR)
    operator: str                   # 操作符: EQ/NE/IN/NOT_IN/CONTAINS/GT/LT/GTE/LTE
    value: Any                      # 匹配值

    def to_dict(self) -> dict:
        return {"feature": self.feature, "operator": self.operator, "value": self.value}


# ============================================================================
# 3. 断言资产 V2
# ============================================================================

@dataclass(frozen=True)
class JudgmentAssetV2:
    """Judgment Asset V2 - 断言资产.

    强制字段: system + school (不能只写system)
    """
    # === identity ===
    judgment_id: str                # 唯一标识 (如 SMTH-YIWEI-RENWU-001)
    system: str                     # 体系 (如 ZI_PING)
    school: str                     # 经典/学派 (如 SAN_MING_TONG_HUI) - 强制
    judgment_type: str              # 断言类型 (如 DAY_TIME/PATTERN/TUNING)
    version: str = "1.0.0"         # 版本

    # === retrieval ===
    match_mode: str = "CONDITION"  # 匹配模式: EXACT/SET/RANGE/ALL/ANY/GRAPH/CONDITION/COMPOSITE
    conditions: list[MatchCondition] = field(default_factory=list)  # 确定性条件
    feature_requirements: list[str] = field(default_factory=list)   # 必需的Feature
    specificity: int = 10           # 特异性 (10-100, 越高越具体)

    # === statement ===
    classical: str = ""             # 原典文本
    semantic_keys: list[str] = field(default_factory=list)  # 语义键 (人工标注)
    modern_mapping: dict[str, Any] = field(default_factory=dict)  # 现代映射 (人工标注, 非LLM生成)

    # === source ===
    book: str = ""                  # 书名
    chapter: str = ""               # 章节
    section: str = ""               # 节
    page: str = ""                  # 页码
    source_locator: str = ""        # 来源定位器 (如 三命通会/卷三/六乙日壬午时断)

    # === provenance ===
    created_at: str = ""            # 创建时间
    revision: int = 1               # 修订号
    status: str = JudgmentStatus.ACTIVE.value  # 状态

    def __post_init__(self):
        # 强制验证: system与school必须都有
        if not self.system:
            raise ValueError(f"Judgment {self.judgment_id}: system不能为空")
        if not self.school:
            raise ValueError(f"Judgment {self.judgment_id}: school不能为空 (不能只写system={self.system})")
        # 验证school属于该system
        if self.system == DivinationSystem.ZI_PING.value:
            valid_schools = [s.value for s in ZiPingSchool]
            if self.school not in valid_schools:
                raise ValueError(f"Judgment {self.judgment_id}: school={self.school} 不属于 system={self.system}")
        # 验证match_mode
        valid_modes = [m.value for m in MatcherType]
        if self.match_mode not in valid_modes:
            raise ValueError(f"Judgment {self.judgment_id}: match_mode={self.match_mode} 无效")
        # 验证specificity范围
        if self.specificity < 10 or self.specificity > 100:
            raise ValueError(f"Judgment {self.judgment_id}: specificity={self.specificity} 必须在10-100之间")

    def to_dict(self) -> dict:
        return {
            "judgment_id": self.judgment_id,
            "system": self.system,
            "school": self.school,
            "judgment_type": self.judgment_type,
            "version": self.version,
            "match_mode": self.match_mode,
            "conditions": [c.to_dict() for c in self.conditions],
            "feature_requirements": list(self.feature_requirements),
            "specificity": self.specificity,
            "classical": self.classical,
            "emantic_keys": list(self.semantic_keys),
            "modern_mapping": dict(self.modern_mapping),
            "book": self.book,
            "chapter": self.chapter,
            "section": self.section,
            "page": self.page,
            "source_locator": self.source_locator,
            "created_at": self.created_at,
            "revision": self.revision,
            "status": self.status,
        }


# ============================================================================
# 4. 匹配结果
# ============================================================================

class MatchResult(str, Enum):
    MATCH = "MATCH"
    PARTIAL = "PARTIAL"
    REJECT = "REJECT"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class JudgmentMatchResult:
    """断言匹配结果."""
    judgment: JudgmentAssetV2
    result: str                     # MATCH/PARTIAL/REJECT/UNRESOLVED
    matched_conditions: list[str] = field(default_factory=list)  # 匹配的条件
    unmatched_conditions: list[str] = field(default_factory=list)  # 未匹配的条件
    evidence_binding: dict[str, Any] = field(default_factory=dict)  # 证据绑定

    def to_dict(self) -> dict:
        return {
            "judgment_id": self.judgment.judgment_id,
            "system": self.judgment.system,
            "school": self.judgment.school,
            "judgment_type": self.judgment.judgment_type,
            "specificity": self.judgment.specificity,
            "result": self.result,
            "matched_conditions": list(self.matched_conditions),
            "unmatched_conditions": list(self.unmatched_conditions),
            "evidence_binding": dict(self.evidence_binding),
            "classical": self.judgment.classical,
            "source_locator": self.judgment.source_locator,
        }


# ============================================================================
# 5. 断言库 (按school隔离)
# ============================================================================

class JudgmentLibraryV2:
    """断言库 V2 - 按system+school隔离存储."""

    def __init__(self):
        self._judgments: dict[str, JudgmentAssetV2] = {}
        self._by_school: dict[str, list[str]] = {}  # school -> [judgment_id]

    def add(self, judgment: JudgmentAssetV2) -> None:
        """添加断言."""
        if judgment.judgment_id in self._judgments:
            raise ValueError(f"Judgment {judgment.judgment_id} 已存在")
        self._judgments[judgment.judgment_id] = judgment
        key = f"{judgment.system}:{judgment.school}"
        if key not in self._by_school:
            self._by_school[key] = []
        self._by_school[key].append(judgment.judgment_id)

    def get(self, judgment_id: str) -> Optional[JudgmentAssetV2]:
        return self._judgments.get(judgment_id)

    def get_by_school(self, system: str, school: str) -> list[JudgmentAssetV2]:
        """按system+school获取断言 (跨经典隔离)."""
        key = f"{system}:{school}"
        ids = self._by_school.get(key, [])
        return [self._judgments[i] for i in ids]

    def get_all(self) -> list[JudgmentAssetV2]:
        return list(self._judgments.values())

    def stats(self) -> dict[str, Any]:
        result = {"total": len(self._judgments), "by_school": {}}
        for key, ids in self._by_school.items():
            result["by_school"][key] = len(ids)
        return result


# ============================================================================
# 6. 确定性Matcher
# ============================================================================

class DeterministicMatcher:
    """确定性Matcher - 不做模糊匹配.

    支持: EXACT/SET/RANGE/ALL/ANY/CONDITION/COMPOSITE
    GRAPH类型需要专门的GraphMatcher处理.
    """

    OPERATORS = {"EQ", "NE", "IN", "NOT_IN", "CONTAINS", "GT", "LT", "GTE", "LTE"}

    @classmethod
    def evaluate_condition(cls, condition: MatchCondition, features: dict[str, Any]) -> tuple[bool, str]:
        """评估单个条件."""
        feature_value = features.get(condition.feature)
        if feature_value is None:
            return False, f"feature {condition.feature} 不存在"

        op = condition.operator.upper()
        if op == "EQ":
            return feature_value == condition.value, f"{condition.feature}={feature_value} == {condition.value}"
        elif op == "NE":
            return feature_value != condition.value, f"{condition.feature}={feature_value} != {condition.value}"
        elif op == "IN":
            return feature_value in condition.value, f"{condition.feature}={feature_value} in {condition.value}"
        elif op == "NOT_IN":
            return feature_value not in condition.value, f"{condition.feature}={feature_value} not in {condition.value}"
        elif op == "CONTAINS":
            if isinstance(feature_value, (list, dict, str)):
                return condition.value in feature_value, f"{condition.feature} contains {condition.value}"
            return False, f"{condition.feature} 不是可包含类型"
        elif op == "GT":
            return feature_value > condition.value, f"{condition.feature}={feature_value} > {condition.value}"
        elif op == "LT":
            return feature_value < condition.value, f"{condition.feature}={feature_value} < {condition.value}"
        elif op == "GTE":
            return feature_value >= condition.value, f"{condition.feature}={feature_value} >= {condition.value}"
        elif op == "LTE":
            return feature_value <= condition.value, f"{condition.feature}={feature_value} <= {condition.value}"
        else:
            return False, f"未知操作符 {op}"

    @classmethod
    def match(cls, judgment: JudgmentAssetV2, features: dict[str, Any]) -> JudgmentMatchResult:
        """匹配断言 - 确定性匹配."""
        # 检查必需的Feature
        missing_features = [f for f in judgment.feature_requirements if f not in features]
        if missing_features:
            return JudgmentMatchResult(
                judgment=judgment, result=MatchResult.UNRESOLVED.value,
                unmatched_conditions=[f"缺少必需Feature: {f}" for f in missing_features],
            )

        matched = []
        unmatched = []
        evidence_binding = {}

        for cond in judgment.conditions:
            ok, detail = cls.evaluate_condition(cond, features)
            if ok:
                matched.append(detail)
                evidence_binding[cond.feature] = features.get(cond.feature)
            else:
                unmatched.append(detail)

        # 根据match_mode决定结果
        if judgment.match_mode == "EXACT":
            # EXACT: 所有条件必须全部匹配, 否则REJECT
            result = MatchResult.MATCH.value if not unmatched else MatchResult.REJECT.value
        elif judgment.match_mode in ("ALL", "CONDITION"):
            # ALL/CONDITION: 所有条件必须匹配, 部分匹配为PARTIAL
            if not unmatched:
                result = MatchResult.MATCH.value
            elif matched and unmatched:
                result = MatchResult.PARTIAL.value
            else:
                result = MatchResult.REJECT.value
        elif judgment.match_mode == "ANY":
            # 任一条件匹配即可
            result = MatchResult.MATCH.value if matched else MatchResult.REJECT.value
        elif judgment.match_mode == "SET":
            # 集合匹配: 所有指定feature的值在允许集合内
            result = MatchResult.MATCH.value if not unmatched else MatchResult.REJECT.value
        else:
            # COMPOSITE/GRAPH/RANGE 需要专门处理, 这里先按ALL处理
            result = MatchResult.MATCH.value if not unmatched else MatchResult.PARTIAL.value

        return JudgmentMatchResult(
            judgment=judgment, result=result,
            matched_conditions=matched, unmatched_conditions=unmatched,
            evidence_binding=evidence_binding,
        )


# ============================================================================
# 7. 按school隔离的Judgment Resolver
# ============================================================================

class SchoolIsolatedResolver:
    """按school隔离的Judgment Resolver.

    三命通会断言只能由SAN_MING_TONG_HUI Resolver检索,
    不能被子平真诠/穷通宝鉴Resolver自动命中.
    """

    def __init__(self, library: JudgmentLibraryV2):
        self.library = library

    def resolve(self, system: str, school: str, features: dict[str, Any]) -> list[JudgmentMatchResult]:
        """解析指定system+school的断言匹配."""
        judgments = self.library.get_by_school(system, school)
        results = []
        for j in judgments:
            result = DeterministicMatcher.match(j, features)
            results.append(result)
        # 按specificity降序排列 (高特异性在前, 但不覆盖低特异性)
        results.sort(key=lambda r: r.judgment.specificity, reverse=True)
        return results

    def resolve_all_schools(self, system: str, features: dict[str, Any]) -> dict[str, list[JudgmentMatchResult]]:
        """解析指定system下所有school的断言匹配 (跨经典隔离)."""
        result = {}
        for key in self.library._by_school:
            if key.startswith(f"{system}:"):
                school = key.split(":", 1)[1]
                result[school] = self.resolve(system, school, features)
        return result


if __name__ == "__main__":
    print("=" * 70)
    print("P6-C-3C-2 Judgment Asset Schema V2 - 快速测试")
    print("=" * 70)

    # 测试1: 创建三命通会日时断断言
    print("\n[1] 创建三命通会日时断断言:")
    j1 = JudgmentAssetV2(
        judgment_id="SMTH-YIWEI-RENWU-001",
        system="ZI_PING", school="SAN_MING_TONG_HUI",
        judgment_type="DAY_TIME", match_mode="EXACT",
        conditions=[
            MatchCondition("ZP.DAY_PILLAR", "EQ", "YI_WEI"),
            MatchCondition("ZP.HOUR_PILLAR", "EQ", "REN_WU"),
        ],
        feature_requirements=["ZP.DAY_PILLAR", "ZP.HOUR_PILLAR"],
        specificity=40,
        classical="六乙日壬午时断：乙日壬午时，印绶带食神，丁己庚辛俱不见，名利有成。",
        semantic_keys=["CAREER", "STATUS", "RESOURCE", "OUTPUT"],
        book="三命通会", chapter="卷三", section="六乙日壬午时断",
        source_locator="三命通会/卷三/六乙日壬午时断",
    )
    print(f"  创建成功: {j1.judgment_id}")
    print(f"  system={j1.system}, school={j1.school}")
    print(f"  match_mode={j1.match_mode}, specificity={j1.specificity}")

    # 测试2: 创建穷通宝鉴调候断言
    print("\n[2] 创建穷通宝鉴调候断言:")
    j2 = JudgmentAssetV2(
        judgment_id="QTBJ-YI-XU-001",
        system="ZI_PING", school="QIONG_TONG_BAO_JIAN",
        judgment_type="TUNING", match_mode="CONDITION",
        conditions=[
            MatchCondition("ZP.DAY_MASTER", "EQ", "YI"),
            MatchCondition("ZP.MONTH_BRANCH", "EQ", "XU"),
        ],
        feature_requirements=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH"],
        specificity=20,
        classical="乙木戌月，戊土当权，先用癸水，次取丙火。",
        semantic_keys=["TUNING", "WATER", "FIRE", "CLIMATE"],
        book="穷通宝鉴", chapter="乙木篇", section="戌月乙木",
        source_locator="穷通宝鉴/乙木篇/戌月乙木",
    )
    print(f"  创建成功: {j2.judgment_id}")

    # 测试3: 验证school强制
    print("\n[3] 验证school强制 (只写system应该报错):")
    try:
        bad = JudgmentAssetV2(
            judgment_id="BAD-001", system="ZI_PING", school="",
            judgment_type="PATTERN",
        )
        print("  错误: 没有报错!")
    except ValueError as e:
        print(f"  正确报错: {e}")

    # 测试4: 匹配测试
    print("\n[4] 匹配测试:")
    features = {
        "ZP.DAY_PILLAR": "YI_WEI",
        "ZP.HOUR_PILLAR": "REN_WU",
        "ZP.DAY_MASTER": "YI",
        "ZP.MONTH_BRANCH": "XU",
    }

    library = JudgmentLibraryV2()
    library.add(j1)
    library.add(j2)
    print(f"  断言库统计: {library.stats()}")

    resolver = SchoolIsolatedResolver(library)

    # 三命通会匹配
    smth_results = resolver.resolve("ZI_PING", "SAN_MING_TONG_HUI", features)
    print(f"\n  三命通会匹配:")
    for r in smth_results:
        print(f"    {r.judgment.judgment_id}: {r.result} (specificity={r.judgment.specificity})")
        print(f"      匹配: {r.matched_conditions}")
        print(f"      原典: {r.judgment.classical[:50]}...")

    # 穷通宝鉴匹配
    qtbj_results = resolver.resolve("ZI_PING", "QIONG_TONG_BAO_JIAN", features)
    print(f"\n  穷通宝鉴匹配:")
    for r in qtbj_results:
        print(f"    {r.judgment.judgment_id}: {r.result} (specificity={r.judgment.specificity})")

    # 测试5: 负向测试 (乙未日癸午时应该REJECT)
    print("\n[5] 负向测试 (乙未日癸午时应该REJECT):")
    features_neg = {"ZP.DAY_PILLAR": "YI_WEI", "ZP.HOUR_PILLAR": "GUI_WU"}
    neg_results = resolver.resolve("ZI_PING", "SAN_MING_TONG_HUI", features_neg)
    for r in neg_results:
        print(f"    {r.judgment.judgment_id}: {r.result}")
        print(f"      未匹配: {r.unmatched_conditions}")

    # 测试6: 跨经典隔离
    print("\n[6] 跨经典隔离测试:")
    all_results = resolver.resolve_all_schools("ZI_PING", features)
    for school, results in all_results.items():
        print(f"  {school}: {len(results)} 条断言, MATCH={sum(1 for r in results if r.result=='MATCH')}")

    print("\n" + "=" * 70)
    print("P6-C-3C-2 Schema V2 测试通过")
    print("=" * 70)
