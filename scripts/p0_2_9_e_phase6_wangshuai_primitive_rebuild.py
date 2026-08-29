"""
P0-2.9-E Phase 6: 基于滴天髓阐微衰旺章原典的旺衰Primitive体系重建

基于 2026-08-30 对《滴天髓阐微·十七、衰旺》完整原文的审计结果：

核心发现：
1. "得令得地有根有气"四元组不是滴天髓原典的表述（原典中完全不存在）
2. 任铁樵用"得时"，不用"得令"（衰旺章中"得令"一次都没出现）
3. "有气"作为旺衰判据在衰旺章中完全不存在
4. 任铁樵真实的旺衰框架是：得时 + 有根/通根（根的轻重）+ 比肩（党众）+ 年日时损益

原典来源：
- 文件：D:/today/Canonical-Mining/完整原典补充/滴天髓阐微_garychowcmu.txt
- 章节：十七、衰旺（3773字符，任氏曰部分627字符）
- 版本：任铁樵《滴天髓阐微》通行本

核心原则：
- 算出来的是事实；关系是结构；证是经典从事实/关系中取出来的局部信息；辨才是经典把多个证组织起来后的状态
- 推理强度 ≤ 原典授权强度
- 合理 ≠ 原典证明
- 局部 Evidence ≠ 整体 Judgment
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
import json


# ============================================================================
# 证据等级（沿用 Phase 5 定义）
# ============================================================================

class EvidenceLevel(Enum):
    """证据等级 — 严格区分原典核验状态"""
    SOURCE_UNVERIFIED = "SOURCE_UNVERIFIED"
    CLASSICAL_EXPLICIT = "CLASSICAL_EXPLICIT"
    CLASSICAL_IMPLICIT = "CLASSICAL_IMPLICIT"
    REASONABLE_HYPOTHESIS = "REASONABLE_HYPOTHESIS"
    ENGINEERING_DERIVED = "ENGINEERING_DERIVED"
    NOT_SUPPORTED = "NOT_SUPPORTED"


class EvidenceStatus(Enum):
    """证据状态"""
    CANDIDATE = "CANDIDATE"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"


class PrimitiveLayer(Enum):
    """Primitive 层级"""
    L1_FACT = "L1_FACT"              # 事实层（Canonical Fact）
    L2_STATE = "L2_STATE"            # 状态层（Primitive State）
    L3_STRUCTURE = "L3_STRUCTURE"    # 结构层（Structural State）
    L4_DOMAIN = "L4_DOMAIN"          # 领域辨证层（Classical Domain Judgment）


class QITarget(Enum):
    """气的作用对象 — 多对象语义载体"""
    DAY_MASTER = "DAY_MASTER"            # 日主
    USEFUL_SPIRIT = "USEFUL_SPIRIT"      # 用神
    FIVE_ELEMENT = "FIVE_ELEMENT"        # 五行（金木水火土）
    WEALTH = "WEALTH"                    # 财星
    OFFICER = "OFFICER"                  # 官星
    OUTPUT = "OUTPUT"                    # 食伤
    RESOURCE = "RESOURCE"                # 印星
    PEER = "PEER"                        # 比劫
    WHOLE_CHART = "WHOLE_CHART"          # 全局
    CLIMATE_FACTOR = "CLIMATE_FACTOR"    # 调候因素（寒/暖/燥/湿）
    UNCLEAR = "UNCLEAR"                  # 不明确


# ============================================================================
# 原典溯源
# ============================================================================

@dataclass(frozen=True)
class ClassicalProvenance:
    """原典溯源 — 四层结构"""
    classic: str                          # 经典名称
    edition: str                          # 版本
    chapter: str                          # 章节
    section: Optional[str]                # 小节/段落
    source_span: str                      # 原文定位（如"任氏曰，十七、衰旺"）
    source_text_exact: str                # 原典逐字文本
    text_type: str = "COMMENTARY"        # ORIGINAL（原文）/ COMMENTARY（注疏）
    author: Optional[str] = None          # 作者（如"任铁樵"）
    verification_status: str = "verified"  # 核验状态
    notes: str = ""


# ============================================================================
# 基于原典的滴天髓旺衰Primitive
# ============================================================================

@dataclass(frozen=True)
class DTSWangshuaiPrimitive:
    """滴天髓旺衰Primitive — 基于衰旺章原典"""
    primitive_id: str                     # Primitive ID（如 DTS-WS-001）
    name: str                             # 名称（如"得时"）
    layer: PrimitiveLayer                 # 层级
    primitive_type: str                   # 类型（核心判据/辅助判据/限定条件/优先级规则/结构影响）
    description: str                      # 描述

    # 原典溯源
    provenance: ClassicalProvenance       # 原典溯源

    # 证据等级和状态
    evidence_level: EvidenceLevel          # 证据等级
    evidence_status: EvidenceStatus        # 证据状态

    # 工程语义
    canonical_fact_dependencies: List[str]  # 依赖的Canonical Fact
    relation_dependencies: List[str]         # 依赖的Relation
    output_type: str                         # 输出类型（Boolean/Enum/Struct/Qualifier）
    output_values: Optional[List[str]]       # 可能的输出值

    # 与其他Primitive的关系
    related_primitives: List[str]            # 相关Primitive ID
    relation_type: str                        # 关系类型（DEPENDS_ON/QUALIFIES/PRIORITY_OVER等）

    # 禁止的推导
    forbidden_inferences: List[str]

    notes: str = ""


# ============================================================================
# 任铁樵真实的旺衰Primitive体系（10个，基于衰旺章原典）
# ============================================================================

class DTSWangshuaiPrimitiveSystem:
    """滴天髓旺衰Primitive体系 — 基于《滴天髓阐微·十七、衰旺》原典"""

    @staticmethod
    def get_all_primitives() -> List[DTSWangshuaiPrimitive]:
        return [
            # ================================================================
            # DTS-WS-001: 得时（月令）
            # ================================================================
            DTSWangshuaiPrimitive(
                primitive_id="DTS-WS-001",
                name="得时",
                layer=PrimitiveLayer.L2_STATE,
                primitive_type="月令状态",
                description=(
                    "日主是否得月令（得时）。任铁樵用'得时'，不用'得令'。"
                    "原典：'得时俱为旺论，失令便作衰看，虽是至理，亦死法也。'"
                    "注意：得时 ≠ 旺，因为存在'得时不旺'的情况。"
                ),
                provenance=ClassicalProvenance(
                    classic="滴天髓阐微",
                    edition="任铁樵《滴天髓阐微》通行本",
                    chapter="十七、衰旺",
                    section="任氏曰",
                    source_span="任氏曰，十七、衰旺，开篇",
                    source_text_exact="得时俱为旺论，失令便作衰看，虽是至理，亦死法也。",
                    text_type="COMMENTARY",
                    author="任铁樵",
                ),
                evidence_level=EvidenceLevel.CLASSICAL_EXPLICIT,
                evidence_status=EvidenceStatus.VERIFIED,
                canonical_fact_dependencies=["day_master", "month_branch", "month_hidden_stems", "ten_gods"],
                relation_dependencies=["SEASONAL_ALIGNMENT"],
                output_type="Enum",
                output_values=["DE_SHI（得时）", "SHI_LING（失令）", "NEUTRAL（中性）"],
                related_primitives=["DTS-WS-002", "DTS-WS-003", "DTS-WS-004"],
                relation_type="QUALIFIES（得时状态需要被得时不旺/失时不弱限定）",
                forbidden_inferences=[
                    "❌ 禁止：得时 → 身强（得时不旺的情况存在）",
                    "❌ 禁止：失令 → 身弱（失时不弱的情况存在）",
                    "❌ 禁止：得时 = 得令（任铁樵用'得时'，不用'得令'，术语需精确）",
                ],
            ),

            # ================================================================
            # DTS-WS-002: 得时不旺
            # ================================================================
            DTSWangshuaiPrimitive(
                primitive_id="DTS-WS-002",
                name="得时不旺",
                layer=PrimitiveLayer.L2_STATE,
                primitive_type="限定条件",
                description=(
                    "虽然得时（月令生扶），但因克泄耗过重，实际不旺。"
                    "原典：'有如春木虽强，金太重而木亦危；干庚辛而支申酉，无火制而不富，逢土生而必夭，是得时不旺也。'"
                ),
                provenance=ClassicalProvenance(
                    classic="滴天髓阐微",
                    edition="任铁樵《滴天髓阐微》通行本",
                    chapter="十七、衰旺",
                    section="任氏曰",
                    source_span="任氏曰，十七、衰旺，得时不旺例",
                    source_text_exact="有如春木虽强，金太重而木亦危；干庚辛而支申酉，无火制而不富，逢土生而必夭，是得时不旺也。",
                    text_type="COMMENTARY",
                    author="任铁樵",
                ),
                evidence_level=EvidenceLevel.CLASSICAL_EXPLICIT,
                evidence_status=EvidenceStatus.VERIFIED,
                canonical_fact_dependencies=["day_master", "month_branch", "officer_count", "output_count", "wealth_count"],
                relation_dependencies=["OFFICER_CONTROL", "OUTPUT_DRAIN", "WEALTH_DRAIN"],
                output_type="Boolean",
                output_values=["TRUE（得时不旺）", "FALSE（不适用）"],
                related_primitives=["DTS-WS-001", "DTS-WS-005"],
                relation_type="QUALIFIES（限定得时状态，使其不能直接推出旺）",
                forbidden_inferences=[
                    "❌ 禁止：得时 + 官杀多 → 直接判身弱（需要辨证）",
                    "❌ 禁止：得时不旺 = 身弱（得时不旺只是限定条件，不是最终判断）",
                ],
            ),

            # ================================================================
            # DTS-WS-003: 失时不弱
            # ================================================================
            DTSWangshuaiPrimitive(
                primitive_id="DTS-WS-003",
                name="失时不弱",
                layer=PrimitiveLayer.L2_STATE,
                primitive_type="限定条件",
                description=(
                    "虽然失时（月令不生扶），但因根固党众，实际不弱。"
                    "原典：'秋木虽弱，木根深而木亦强，干甲乙而支寅卯，遇官透而能受，逢水生而太过，是失时不弱也。'"
                ),
                provenance=ClassicalProvenance(
                    classic="滴天髓阐微",
                    edition="任铁樵《滴天髓阐微》通行本",
                    chapter="十七、衰旺",
                    section="任氏曰",
                    source_span="任氏曰，十七、衰旺，失时不弱例",
                    source_text_exact="秋木虽弱，木根深而木亦强，干甲乙而支寅卯，遇官透而能受，逢水生而太过，是失时不弱也。",
                    text_type="COMMENTARY",
                    author="任铁樵",
                ),
                evidence_level=EvidenceLevel.CLASSICAL_EXPLICIT,
                evidence_status=EvidenceStatus.VERIFIED,
                canonical_fact_dependencies=["day_master", "month_branch", "root_details", "peer_count", "resource_count"],
                relation_dependencies=["ROOT_PRESENT", "STEM_ROOT_PRESENT", "PEER_SUPPORT", "RESOURCE_SUPPORT"],
                output_type="Boolean",
                output_values=["TRUE（失时不弱）", "FALSE（不适用）"],
                related_primitives=["DTS-WS-001", "DTS-WS-005", "DTS-WS-008"],
                relation_type="QUALIFIES（限定失时状态，使其不能直接推出弱）",
                forbidden_inferences=[
                    "❌ 禁止：失令 + 有根 → 直接判身强（需要辨证）",
                    "❌ 禁止：失时不弱 = 身强（失时不弱只是限定条件，不是最终判断）",
                ],
            ),

            # ================================================================
            # DTS-WS-004: 年日时损益
            # ================================================================
            DTSWangshuaiPrimitive(
                primitive_id="DTS-WS-004",
                name="年日时损益",
                layer=PrimitiveLayer.L2_STATE,
                primitive_type="补充判据",
                description=(
                    "月令虽重，但年日时也有损益之权。"
                    "原典：'况八字虽以月令为重，而旺相休囚，年日时中，亦有损益之权，故生月即不值令，亦能值年值日值时，岂可执一而论？'"
                ),
                provenance=ClassicalProvenance(
                    classic="滴天髓阐微",
                    edition="任铁樵《滴天髓阐微》通行本",
                    chapter="十七、衰旺",
                    section="任氏曰",
                    source_span="任氏曰，十七、衰旺，年日时损益",
                    source_text_exact="况八字虽以月令为重，而旺相休囚，年日时中，亦有损益之权，故生月即不值令，亦能值年值日值时，岂可执一而论？",
                    text_type="COMMENTARY",
                    author="任铁樵",
                ),
                evidence_level=EvidenceLevel.CLASSICAL_EXPLICIT,
                evidence_status=EvidenceStatus.VERIFIED,
                canonical_fact_dependencies=["year_pillar", "day_pillar", "hour_pillar", "month_pillar"],
                relation_dependencies=["SEASONAL_ALIGNMENT", "POSITION_ROLE"],
                output_type="Struct",
                output_values=["YEAR_EFFECT", "DAY_EFFECT", "HOUR_EFFECT", "NET_BALANCE"],
                related_primitives=["DTS-WS-001"],
                relation_type="SUPPLEMENTS（补充月令判据，不能执一而论）",
                forbidden_inferences=[
                    "❌ 禁止：只看月令，不看年日时（执一而论）",
                    "❌ 禁止：年日时损益 = 简单加减分（需要辨证）",
                ],
            ),

            # ================================================================
            # DTS-WS-005: 有根（通根）— 核心判据
            # ================================================================
            DTSWangshuaiPrimitive(
                primitive_id="DTS-WS-005",
                name="有根（通根）",
                layer=PrimitiveLayer.L2_STATE,
                primitive_type="核心判据",
                description=(
                    "日主在地支藏干中有同干之根。这是任铁樵旺衰判断的核心判据。"
                    "原典：'是故日干不论月令休囚，只要四柱有根，便能受财官食神而当伤官七杀。'"
                    "注意：有根是核心判据，但有根 ≠ 身强，还需要看根的轻重、数量、是否受伤。"
                ),
                provenance=ClassicalProvenance(
                    classic="滴天髓阐微",
                    edition="任铁樵《滴天髓阐微》通行本",
                    chapter="十七、衰旺",
                    section="任氏曰",
                    source_span="任氏曰，十七、衰旺，核心论断",
                    source_text_exact="是故日干不论月令休囚，只要四柱有根，便能受财官食神而当伤官七杀。",
                    text_type="COMMENTARY",
                    author="任铁樵",
                ),
                evidence_level=EvidenceLevel.CLASSICAL_EXPLICIT,
                evidence_status=EvidenceStatus.VERIFIED,
                canonical_fact_dependencies=["day_master", "hidden_stems", "root_details"],
                relation_dependencies=["ROOT_PRESENT", "STEM_ROOT_PRESENT"],
                output_type="Struct",
                output_values=["HAS_ROOT（有根）", "NO_ROOT（无根）", "ROOT_COUNT", "ROOT_TYPES"],
                related_primitives=["DTS-WS-006", "DTS-WS-007", "DTS-WS-010"],
                relation_type="CORE（核心判据，其他判据围绕它组织）",
                forbidden_inferences=[
                    "❌ 禁止：有根 → 身强（有根只是核心判据，不是最终判断）",
                    "❌ 禁止：无根 → 身弱（无根也可能失时不弱）",
                    "❌ 禁止：ROOT_PRESENT = 日主有根（需区分日主根和十神根，使用STEM_ROOT_PRESENT）",
                ],
            ),

            # ================================================================
            # DTS-WS-006: 根之重者（长生禄旺）
            # ================================================================
            DTSWangshuaiPrimitive(
                primitive_id="DTS-WS-006",
                name="根之重者（长生禄旺）",
                layer=PrimitiveLayer.L3_STRUCTURE,
                primitive_type="根的分类",
                description=(
                    "根的类型：长生禄旺是根之重者。"
                    "原典：'长生禄旺，根之重者也。'"
                    "原典例：'得二比肩，不如支中得一长生禄旺，如甲乙逢亥寅卯之类是也。'"
                ),
                provenance=ClassicalProvenance(
                    classic="滴天髓阐微",
                    edition="任铁樵《滴天髓阐微》通行本",
                    chapter="十七、衰旺",
                    section="任氏曰",
                    source_span="任氏曰，十七、衰旺，根的分类",
                    source_text_exact="长生禄旺，根之重者也。",
                    text_type="COMMENTARY",
                    author="任铁樵",
                ),
                evidence_level=EvidenceLevel.CLASSICAL_EXPLICIT,
                evidence_status=EvidenceStatus.VERIFIED,
                canonical_fact_dependencies=["day_master", "hidden_stems", "growth_stage", "root_details"],
                relation_dependencies=["ROOT_PRESENT", "GROWTH_STAGE"],
                output_type="Enum",
                output_values=["HEAVY_ROOT（重根：长生禄旺）", "LIGHT_ROOT（轻根：墓库余气）", "MIXED（混合）"],
                related_primitives=["DTS-WS-005", "DTS-WS-007", "DTS-WS-009"],
                relation_type="CLASSIFIES（对有根进行分类，重根 > 轻根 > 比肩）",
                forbidden_inferences=[
                    "❌ 禁止：长生禄旺 = 身强（根重只是根的分类，不是最终判断）",
                    "❌ 禁止：十二长生 = 通根（十二长生不能制造藏干根）",
                ],
            ),

            # ================================================================
            # DTS-WS-007: 根之轻者（墓库余气）
            # ================================================================
            DTSWangshuaiPrimitive(
                primitive_id="DTS-WS-007",
                name="根之轻者（墓库余气）",
                layer=PrimitiveLayer.L3_STRUCTURE,
                primitive_type="根的分类",
                description=(
                    "根的类型：墓库余气是根之轻者。"
                    "原典：'墓库余气，根之轻者也。'"
                    "原典例：'天干得一比肩，不如地支得一余气墓库。'"
                    "墓者：甲乙逢未，丙丁逢戌，庚辛逢丑，壬癸逢辰。"
                    "余气者：丙丁逢未，甲乙逢辰，庚辛逢戌，壬癸逢丑。"
                ),
                provenance=ClassicalProvenance(
                    classic="滴天髓阐微",
                    edition="任铁樵《滴天髓阐微》通行本",
                    chapter="十七、衰旺",
                    section="任氏曰",
                    source_span="任氏曰，十七、衰旺，根的分类",
                    source_text_exact="墓库余气，根之轻者也。",
                    text_type="COMMENTARY",
                    author="任铁樵",
                ),
                evidence_level=EvidenceLevel.CLASSICAL_EXPLICIT,
                evidence_status=EvidenceStatus.VERIFIED,
                canonical_fact_dependencies=["day_master", "hidden_stems", "root_details"],
                relation_dependencies=["ROOT_PRESENT", "HIDDEN_STEM_RELATION"],
                output_type="Enum",
                output_values=["HEAVY_ROOT（重根：长生禄旺）", "LIGHT_ROOT（轻根：墓库余气）", "MIXED（混合）"],
                related_primitives=["DTS-WS-005", "DTS-WS-006", "DTS-WS-009"],
                relation_type="CLASSIFIES（对有根进行分类，轻根 < 重根，但 > 比肩）",
                forbidden_inferences=[
                    "❌ 禁止：墓库余气 = 无根（墓库余气仍是根，只是轻根）",
                    "❌ 禁止：逢库 = 有根（需要藏干中有同干，不是见库就有根）",
                ],
            ),

            # ================================================================
            # DTS-WS-008: 比肩（党众）
            # ================================================================
            DTSWangshuaiPrimitive(
                primitive_id="DTS-WS-008",
                name="比肩（党众）",
                layer=PrimitiveLayer.L2_STATE,
                primitive_type="辅助判据",
                description=(
                    "天干有比肩（同类五行）帮身。"
                    "原典：'天干得一比肩，不如地支得一余气墓库。'、'得二比肩，不如支中得一长生禄旺。'"
                    "注意：比肩是辅助判据，其重要性低于通根（干多不如根重）。"
                ),
                provenance=ClassicalProvenance(
                    classic="滴天髓阐微",
                    edition="任铁樵《滴天髓阐微》通行本",
                    chapter="十七、衰旺",
                    section="任氏曰",
                    source_span="任氏曰，十七、衰旺，比肩与通根比较",
                    source_text_exact="天干得一比肩，不如地支得一余气墓库。",
                    text_type="COMMENTARY",
                    author="任铁樵",
                ),
                evidence_level=EvidenceLevel.CLASSICAL_EXPLICIT,
                evidence_status=EvidenceStatus.VERIFIED,
                canonical_fact_dependencies=["day_master", "heavenly_stems", "ten_gods", "peer_count"],
                relation_dependencies=["PEER_SUPPORT", "TEN_GOD_RELATION"],
                output_type="Struct",
                output_values=["PEER_COUNT", "PEER_POSITIONS", "PEER_ROOTED"],
                related_primitives=["DTS-WS-005", "DTS-WS-006", "DTS-WS-007", "DTS-WS-009"],
                relation_type="SUPPLEMENTS（辅助判据，重要性低于通根）",
                forbidden_inferences=[
                    "❌ 禁止：比肩多 → 身强（干多不如根重）",
                    "❌ 禁止：比肩 = 得势（任铁樵用'比肩'，不用'得势'作为旺衰判据术语）",
                    "❌ 禁止：比肩数量 = 分数（禁止评分模型）",
                ],
            ),

            # ================================================================
            # DTS-WS-009: 干多不如根重（优先级规则）
            # ================================================================
            DTSWangshuaiPrimitive(
                primitive_id="DTS-WS-009",
                name="干多不如根重",
                layer=PrimitiveLayer.L3_STRUCTURE,
                primitive_type="优先级规则",
                description=(
                    "天干比肩再多，也不如地支通根重要。"
                    "原典：'盖比肩如朋友之相扶，通根如家室之可托，干多不如根重，理固然也。'"
                    "这是任铁樵明确的优先级规则：通根 > 比肩。"
                    "更精确的优先级：长生禄旺（重根）> 二比肩 > 墓库余气（轻根）> 一比肩。"
                ),
                provenance=ClassicalProvenance(
                    classic="滴天髓阐微",
                    edition="任铁樵《滴天髓阐微》通行本",
                    chapter="十七、衰旺",
                    section="任氏曰",
                    source_span="任氏曰，十七、衰旺，干多不如根重",
                    source_text_exact="盖比肩如朋友之相扶，通根如家室之可托，干多不如根重，理固然也。",
                    text_type="COMMENTARY",
                    author="任铁樵",
                ),
                evidence_level=EvidenceLevel.CLASSICAL_EXPLICIT,
                evidence_status=EvidenceStatus.VERIFIED,
                canonical_fact_dependencies=["day_master", "root_details", "peer_count"],
                relation_dependencies=["ROOT_PRESENT", "PEER_SUPPORT"],
                output_type="PriorityRule",
                output_values=["HEAVY_ROOT > 2_PEERS > LIGHT_ROOT > 1_PEER"],
                related_primitives=["DTS-WS-005", "DTS-WS-006", "DTS-WS-007", "DTS-WS-008"],
                relation_type="PRIORITY_OVER（通根优先级高于比肩）",
                forbidden_inferences=[
                    "❌ 禁止：用评分模型表达优先级（禁止 strength_score / root_score）",
                    "❌ 禁止：比肩数量 > 根数量 → 身强（干多不如根重）",
                ],
            ),

            # ================================================================
            # DTS-WS-010: 本根之气（结构影响）
            # ================================================================
            DTSWangshuaiPrimitive(
                primitive_id="DTS-WS-010",
                name="本根之气",
                layer=PrimitiveLayer.L3_STRUCTURE,
                primitive_type="结构影响",
                description=(
                    "刑冲可以伤害本根之气。"
                    "原典：'更有壬癸逢辰，丙丁逢戌，甲乙逢未，庚辛逢丑之类，不以为通根峰库，甚至求刑冲以开之，竟不思刑冲伤吾本根之气。'"
                    "注意：这是结构影响，不是独立的旺衰判据。刑冲对根的影响需要单独授权。"
                ),
                provenance=ClassicalProvenance(
                    classic="滴天髓阐微",
                    edition="任铁樵《滴天髓阐微》通行本",
                    chapter="十七、衰旺",
                    section="任氏曰",
                    source_span="任氏曰，十七、衰旺，批判时弊",
                    source_text_exact="竟不思刑冲伤吾本根之气。",
                    text_type="COMMENTARY",
                    author="任铁樵",
                ),
                evidence_level=EvidenceLevel.CLASSICAL_EXPLICIT,
                evidence_status=EvidenceStatus.VERIFIED,
                canonical_fact_dependencies=["day_master", "root_details", "clash_relations", "punishment_relations"],
                relation_dependencies=["ROOT_PRESENT", "CLASH", "PUNISHMENT", "STRUCTURAL_CHANGE"],
                output_type="Qualifier",
                output_values=["ROOT_INTACT（根完整）", "ROOT_DAMAGED（根受损）", "ROOT_DESTROYED（根被破坏）"],
                related_primitives=["DTS-WS-005", "DTS-WS-006", "DTS-WS-007"],
                relation_type="QUALIFIES（限定有根状态，刑冲可能伤根）",
                forbidden_inferences=[
                    "❌ 禁止：子午冲 → 根受损（需要原典授权的结构变化规则）",
                    "❌ 禁止：刑冲 → 身弱（结构影响需要辨证，不能直接推导）",
                    "❌ 禁止：求刑冲以开库（任铁樵明确批判这种做法）",
                ],
            ),
        ]

    @staticmethod
    def get_primitive_summary() -> Dict[str, Any]:
        """Primitive体系摘要"""
        primitives = DTSWangshuaiPrimitiveSystem.get_all_primitives()
        return {
            "total_primitives": len(primitives),
            "all_classical_explicit": all(p.evidence_level == EvidenceLevel.CLASSICAL_EXPLICIT for p in primitives),
            "all_verified": all(p.evidence_status == EvidenceStatus.VERIFIED for p in primitives),
            "core_primitives": [p.primitive_id for p in primitives if p.primitive_type == "核心判据"],
            "auxiliary_primitives": [p.primitive_id for p in primitives if p.primitive_type == "辅助判据"],
            "qualifier_primitives": [p.primitive_id for p in primitives if p.primitive_type == "限定条件"],
            "classification_primitives": [p.primitive_id for p in primitives if p.primitive_type == "根的分类"],
            "priority_rules": [p.primitive_id for p in primitives if p.primitive_type == "优先级规则"],
            "structural_effects": [p.primitive_id for p in primitives if p.primitive_type == "结构影响"],
            "key_principles": [
                "得时 ≠ 旺（得时不旺的情况存在）",
                "失时 ≠ 弱（失时不弱的情况存在）",
                "有根是核心判据：'只要四柱有根，便能受财官食神而当伤官七杀'",
                "干多不如根重：通根 > 比肩",
                "根分轻重：长生禄旺（重）> 墓库余气（轻）",
                "年日时也有损益之权，不能执一而论",
                "刑冲可以伤本根之气",
                "任铁樵用'得时'，不用'得令'",
                "'有气'不是旺衰四元组之一",
            ],
            "forbidden_inferences_total": sum(len(p.forbidden_inferences) for p in primitives),
        }


# ============================================================================
# "有气"的重新定义（E001-V2）
# ============================================================================

@dataclass(frozen=True)
class YouQIRedefined:
    """'有气'的重新定义 — 多对象语义载体，不是旺衰四元组之一"""
    entry_id: str = "DTS-QI-E001-V2"
    name: str = "有气（多对象语义载体）"

    # 原典依据（多章，不是单一衰旺章）
    classical_evidence: List[ClassicalProvenance] = field(default_factory=lambda: [
        ClassicalProvenance(
            classic="滴天髓阐微",
            edition="任铁樵《滴天髓阐微》通行本",
            chapter="清气/浊气（相关章节）",
            section="清枯论",
            source_span="清枯者，不特日主无根之谓也",
            source_text_exact="清枯者，不特日主无根之谓也，即日主有气，而用神无气者，亦是也。",
            text_type="COMMENTARY",
            author="任铁樵",
        ),
        ClassicalProvenance(
            classic="滴天髓阐微",
            edition="任铁樵《滴天髓阐微》通行本",
            chapter="何知章",
            section="贫富判断",
            source_span="何知其人富，财气通门户",
            source_text_exact="何知其人富，财气通门户。",
            text_type="ORIGINAL",
            author="京图（传）",
        ),
    ])

    # 重新定义
    redefinition: str = (
        "'有气'不是与得令、得地、有根并列的旺衰四元组之一。"
        "'有气'是一个语义载体/状态描述机制，描述某对象（日主/用神/十神/五行/调候因素）"
        "是否具有基本力量、有源、有支撑。其具体含义取决于对象和语境，不能统一映射为旺衰判据。"
    )

    # 可作用对象
    targets: List[QITarget] = field(default_factory=lambda: [
        QITarget.DAY_MASTER,       # 日主有气
        QITarget.USEFUL_SPIRIT,    # 用神有气/无气
        QITarget.FIVE_ELEMENT,      # 某五行有气（如"秋金有气"）
        QITarget.WEALTH,            # 财星有气（如"财气通门户"）
        QITarget.OFFICER,           # 官星有气
        QITarget.OUTPUT,            # 食伤有气
        QITarget.RESOURCE,          # 印星有气
        QITarget.PEER,              # 比劫有气
        QITarget.CLIMATE_FACTOR,    # 调候因素有气（如"要暖有气"）
    ])

    # 与旺衰判断的关系
    relation_to_wangshuai: str = (
        "'有气'可以作为旺衰判断的Qualifier（限定条件），但不是核心判据。"
        "任铁樵的核心旺衰判据是：得时（月令）+ 有根/通根（根的轻重）+ 比肩（党众）+ 年日时损益。"
        "'有气'更多是对这些判据结果的综合描述，而不是独立判据。"
    )

    # 证据等级和状态
    evidence_level: EvidenceLevel = EvidenceLevel.CLASSICAL_IMPLICIT
    evidence_status: EvidenceStatus = EvidenceStatus.PARTIALLY_VERIFIED

    # 禁止的推导
    forbidden_inferences: List[str] = field(default_factory=lambda: [
        "❌ 禁止：'得令得地有根有气'作为原典表述（原典中不存在）",
        "❌ 禁止：'有气'与得令、得地、有根并列（PARALLEL关系，原典不支持）",
        "❌ 禁止：'有气' = 日主力量状态（单一对象，气可作用于多对象）",
        "❌ 禁止：'有气' → 身强（直接推导）",
        "❌ 禁止：得令+得地+有根+有气 → 真旺（AND关系，原典不支持）",
        "❌ 禁止：'有气' = 得令",
        "❌ 禁止：'有气' = 得地",
        "❌ 禁止：'有气' = 有根",
    ])

    notes: str = (
        "E001原假设（'有气'作为旺衰四元组之一）被滴天髓阐微衰旺章原典证伪。"
        "'有气'的概念本身在滴天髓多章中确实存在（如'日主有气，用神无气'、'财气通门户'、'秋金有气'、'要暖有气'），"
        "但它是一个可作用于多对象的语义载体，不是旺衰核心判据，更不是与得令得地有根并列的四元组之一。"
    )


# ============================================================================
# 旺衰判断的真实组合逻辑框架（基于原典，非形式化）
# ============================================================================

@dataclass(frozen=True)
class DTSWangshuaiCombinationFramework:
    """滴天髓旺衰判断组合逻辑框架 — 基于原典，非形式化"""

    framework_id: str = "DTS-WS-COMB-001"
    name: str = "滴天髓旺衰判断组合逻辑框架"

    # 输入层
    input_primitives: List[str] = field(default_factory=lambda: [
        "DTS-WS-001（得时）",
        "DTS-WS-002（得时不旺限定）",
        "DTS-WS-003（失时不弱限定）",
        "DTS-WS-004（年日时损益）",
        "DTS-WS-005（有根/通根，核心判据）",
        "DTS-WS-006（根之重者：长生禄旺）",
        "DTS-WS-007（根之轻者：墓库余气）",
        "DTS-WS-008（比肩/党众，辅助判据）",
        "DTS-WS-009（干多不如根重，优先级规则）",
        "DTS-WS-010（本根之气，结构影响）",
    ])

    # 判断逻辑（非形式化，需要辨证）
    judgment_logic: str = (
        "任铁樵没有给出形式化的旺衰算法（如'得令+得地+有根+有气=真旺'）。"
        "他的旺衰判断是辨证式的，核心原则如下：\n"
        "\n"
        "1. 得时是重要参考，但不是决定性的：\n"
        "   - 得时可能不旺（克泄耗过重）\n"
        "   - 失时可能不弱（根固党众）\n"
        "\n"
        "2. 有根/通根是核心判据：\n"
        "   - '只要四柱有根，便能受财官食神而当伤官七杀'\n"
        "   - 根分轻重：长生禄旺（重）> 墓库余气（轻）\n"
        "   - 干多不如根重：通根 > 比肩\n"
        "\n"
        "3. 年日时也有损益之权：\n"
        "   - 不能只看月令，执一而论\n"
        "   - 生月即不值令，亦能值年值日值时\n"
        "\n"
        "4. 结构变化可以影响根的状态：\n"
        "   - 刑冲可以伤本根之气\n"
        "   - 不能求刑冲以开库\n"
        "\n"
        "5. 最终旺衰判断需要综合以上所有因素，不能简单加权。"
    )

    # 输出层
    output_layer: str = (
        "局部状态（Structured States）：\n"
        "  - 得时状态：DE_SHI / SHI_LING / NEUTRAL\n"
        "  - 得时不旺限定：TRUE / FALSE\n"
        "  - 失时不弱限定：TRUE / FALSE\n"
        "  - 年日时损益：NET_BALANCE\n"
        "  - 有根状态：HAS_ROOT / NO_ROOT + ROOT_COUNT + ROOT_TYPES\n"
        "  - 根的分类：HEAVY_ROOT / LIGHT_ROOT / MIXED\n"
        "  - 比肩状态：PEER_COUNT + PEER_POSITIONS\n"
        "  - 优先级规则：HEAVY_ROOT > 2_PEERS > LIGHT_ROOT > 1_PEER\n"
        "  - 本根之气状态：ROOT_INTACT / ROOT_DAMAGED / ROOT_DESTROYED\n"
        "\n"
        "整体旺衰（Overall State）：\n"
        "  - 当前状态：UNRESOLVED / NOT_DEFINED\n"
        "  - 原因：任铁樵没有给出形式化的综合旺衰算法\n"
        "  - 禁止：未经原典授权的组合规则直接推出最终强弱\n"
    )

    # 禁止的推导
    forbidden_inferences: List[str] = field(default_factory=lambda: [
        "❌ 禁止：得令+得地+有根+有气 → 真旺（原典不支持此表述）",
        "❌ 禁止：support_score > constraint_score → 身强（禁止评分模型）",
        "❌ 禁止：strength_score / root_score（禁止评分）",
        "❌ 禁止：五行数量 → 强弱（势大于数）",
        "❌ 禁止：长生 → 通根（十二长生不能制造藏干根）",
        "❌ 禁止：调候 → 强弱（调候是独立维度）",
        "❌ 禁止：未经授权的组合规则 → 最终强弱",
        "❌ 禁止：局部状态 → 整体强弱（需要明确授权的综合规则）",
    ])

    notes: str = (
        "本框架基于《滴天髓阐微·十七、衰旺》原典重建。"
        "任铁樵的旺衰判断是辨证式的，不是形式化算法。"
        "当前只建立了局部状态的提取框架，整体旺衰判断仍为UNRESOLVED，"
        "需要进一步研究五部经典中是否存在明确授权的综合辨证规则。"
    )


# ============================================================================
# 输出报告
# ============================================================================

def print_phase6_report():
    """输出 Phase 6 报告"""
    print("=" * 80)
    print("P0-2.9-E Phase 6: 基于滴天髓阐微衰旺章原典的旺衰Primitive体系重建")
    print("=" * 80)

    print("\n【审计背景】")
    print("  基于 2026-08-30 对《滴天髓阐微·十七、衰旺》完整原文的审计结果：")
    print("  1. '得令得地有根有气'四元组不是滴天髓原典的表述（原典中完全不存在）")
    print("  2. 任铁樵用'得时'，不用'得令'（衰旺章中'得令'一次都没出现）")
    print("  3. '有气'作为旺衰判据在衰旺章中完全不存在")
    print("  4. 任铁樵真实的旺衰框架是：得时 + 有根/通根（根的轻重）+ 比肩（党众）+ 年日时损益")

    # Primitive体系摘要
    print("\n" + "=" * 80)
    print("【滴天髓旺衰Primitive体系摘要】")
    print("=" * 80)

    summary = DTSWangshuaiPrimitiveSystem.get_primitive_summary()
    print(f"\n  总Primitive数: {summary['total_primitives']}")
    print(f"  全部 CLASSICAL_EXPLICIT: {summary['all_classical_explicit']}")
    print(f"  全部 VERIFIED: {summary['all_verified']}")
    print(f"  核心判据: {summary['core_primitives']}")
    print(f"  辅助判据: {summary['auxiliary_primitives']}")
    print(f"  限定条件: {summary['qualifier_primitives']}")
    print(f"  根的分类: {summary['classification_primitives']}")
    print(f"  优先级规则: {summary['priority_rules']}")
    print(f"  结构影响: {summary['structural_effects']}")
    print(f"  禁止推导总数: {summary['forbidden_inferences_total']}")

    print(f"\n  【核心原则】")
    for i, p in enumerate(summary['key_principles'], 1):
        print(f"    {i}. {p}")

    # Primitive详情
    print("\n" + "=" * 80)
    print("【10个旺衰Primitive详情】")
    print("=" * 80)

    primitives = DTSWangshuaiPrimitiveSystem.get_all_primitives()
    for p in primitives:
        print(f"\n{'='*60}")
        print(f"  {p.primitive_id}: {p.name}")
        print(f"  层级: {p.layer.value}")
        print(f"  类型: {p.primitive_type}")
        print(f"  证据等级: {p.evidence_level.value}")
        print(f"  证据状态: {p.evidence_status.value}")
        print(f"  原典: {p.provenance.classic} · {p.provenance.chapter} · {p.provenance.source_span}")
        print(f"  原文: {p.provenance.source_text_exact[:80]}...")
        print(f"  输出类型: {p.output_type}")
        print(f"  关系: {p.relation_type}")
        print(f"{'='*60}")

        print(f"\n  【描述】")
        print(f"    {p.description[:150]}...")

        print(f"\n  【禁止的推导】({len(p.forbidden_inferences)} 条)")
        for f in p.forbidden_inferences:
            print(f"    {f}")

    # "有气"重新定义
    print("\n" + "=" * 80)
    print("【'有气'的重新定义（E001-V2）】")
    print("=" * 80)

    youqi = YouQIRedefined()
    print(f"\n  entry_id: {youqi.entry_id}")
    print(f"  证据等级: {youqi.evidence_level.value}")
    print(f"  证据状态: {youqi.evidence_status.value}")
    print(f"  可作用对象: {[t.value for t in youqi.targets]}")

    print(f"\n  【重新定义】")
    print(f"    {youqi.redefinition}")

    print(f"\n  【与旺衰判断的关系】")
    print(f"    {youqi.relation_to_wangshuai}")

    print(f"\n  【禁止的推导】({len(youqi.forbidden_inferences)} 条)")
    for f in youqi.forbidden_inferences:
        print(f"    {f}")

    print(f"\n  【备注】")
    print(f"    {youqi.notes}")

    # 组合逻辑框架
    print("\n" + "=" * 80)
    print("【旺衰判断组合逻辑框架】")
    print("=" * 80)

    comb = DTSWangshuaiCombinationFramework()
    print(f"\n  framework_id: {comb.framework_id}")

    print(f"\n  【输入Primitive】({len(comb.input_primitives)} 个)")
    for i, inp in enumerate(comb.input_primitives, 1):
        print(f"    {i}. {inp}")

    print(f"\n  【判断逻辑（非形式化，需要辨证）】")
    print(f"    {comb.judgment_logic[:300]}...")

    print(f"\n  【输出层】")
    print(f"    {comb.output_layer[:300]}...")

    print(f"\n  【禁止的推导】({len(comb.forbidden_inferences)} 条)")
    for f in comb.forbidden_inferences:
        print(f"    {f}")

    # 核心结论
    print("\n" + "=" * 80)
    print("【核心结论】")
    print("=" * 80)

    print("""
  1. E001原假设（"有气"作为旺衰四元组之一）被滴天髓阐微衰旺章原典证伪。

  2. 任铁樵真实的旺衰框架是：
     得时（月令）+ 有根/通根（根的轻重）+ 比肩（党众）+ 年日时损益
     而不是"得令得地有根有气"。

  3. "有气"是一个可作用于多对象的语义载体（日主/用神/十神/五行/调候因素），
     不是旺衰核心判据，更不是与得令得地有根并列的四元组之一。

  4. 已重建10个基于原典的旺衰Primitive（DTS-WS-001 ~ 010），
     全部为 CLASSICAL_EXPLICIT + VERIFIED。

  5. 整体旺衰判断仍为 UNRESOLVED，因为任铁樵没有给出形式化的综合算法，
     需要进一步研究五部经典中是否存在明确授权的综合辨证规则。

  项目总纪律不变：算准 → 辨准 → 解准；FROZEN ≠ PROVEN CORRECT。
  P6-CALC Calculation Integrity 仍是施工区和最高优先级。
""")


if __name__ == "__main__":
    print_phase6_report()
