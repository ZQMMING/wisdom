"""STR-001A Canonical Source Audit - 日主身弱 原典审计启动.

Contract/Governance Layer = FROZEN (v6-final.1, 2026-08-29 第三方审计批准)
本阶段 = STR-001A Canonical Source Audit
第一动作 = 建立 Canonical Source Registry / Scope
第二动作 = Source Claim Collection

核心原则 (来自冻结的Contract):
  - 第③步不能直接问"这句话能不能证明身弱"
  - 应该分别问: 这句话是什么性质? → DEFINITION/DESCRIPTIVE/CONDITIONAL
    → 它描述什么语义? → 它允许建立什么Mapping? → 它允许什么Evidence Role?
    → 最后才进入Proposition Evaluation
  - 必须允许最终得到REJECTED
  - 不能confirmation bias (不是"找支持身弱的句子")
  - Source Scope是"允许进入Canonical审计的资料边界", 不是说其中任何一句话天然具有同等授权等级

STR-001A 目标Proposition: 日主身弱
  - 不是: 开发"身弱算法"
  - 不是: wood_ratio → 身弱
  - 不是: 进入ContextResolver
  - 不是: 进入Assertion
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# Canonical Source Registry
# ============================================================================

class SourceStatus(str, Enum):
    """Source在Registry中的状态."""
    CANDIDATE = "CANDIDATE"          # 候选, 待审核版本/章节
    VERSION_VERIFIED = "VERSION_VERIFIED"  # 版本已确认
    SCOPE_AUTHORIZED = "SCOPE_AUTHORIZED"  # 已授权进入STR-001A审计范围
    EXCLUDED = "EXCLUDED"            # 排除


@dataclass
class SourceEdition:
    """版本信息."""
    edition_id: str
    edition_name: str = ""
    author: str = ""
    dynasty: str = ""
    version_note: str = ""
    status: SourceStatus = SourceStatus.CANDIDATE


@dataclass
class SourceChapter:
    """章节信息."""
    chapter_id: str
    chapter_name: str = ""
    chapter_number: str = ""
    content_summary: str = ""
    status: SourceStatus = SourceStatus.CANDIDATE


@dataclass
class CanonicalSource:
    """Canonical Source Registry中的一条Source."""
    source_id: str
    source_name: str = ""
    source_type: str = ""               # 经典/注本/赋论
    editions: List[SourceEdition] = field(default_factory=list)
    chapters: List[SourceChapter] = field(default_factory=list)
    scope_status: SourceStatus = SourceStatus.CANDIDATE
    scope_note: str = ""


def build_canonical_source_registry() -> List[CanonicalSource]:
    """建立Canonical Source Registry (五部核心子平经典).

    注意: 这是Registry建立, 不是自动授权. 每部经典需要版本/章节审核后才能进入STR-001A.
    """
    registry = []

    # 1. 《渊海子平》
    registry.append(CanonicalSource(
        source_id="SRC-YHZP",
        source_name="渊海子平",
        source_type="经典",
        editions=[
            SourceEdition(edition_id="ED-YHZP-001", edition_name="渊海子平",
                          author="徐子平", dynasty="宋",
                          version_note="题宋徐子平撰, 实际为后人汇编",
                          status=SourceStatus.VERSION_VERIFIED),
        ],
        chapters=[
            SourceChapter(chapter_id="CH-YHZP-XUANJIFU", chapter_name="玄机赋",
                          content_summary="赋论, 包含身旺身弱、得时失令、四柱无根等论述",
                          status=SourceStatus.SCOPE_AUTHORIZED),
            SourceChapter(chapter_id="CH-YHZP-SHENRUOLUN", chapter_name="身弱论",
                          content_summary="专论身弱, 按十干分述无根/生月/克泄等情况",
                          status=SourceStatus.SCOPE_AUTHORIZED),
            SourceChapter(chapter_id="CH-YHZP-LUOYIFU", chapter_name="络绎赋",
                          content_summary="赋论, 包含五行旺于四季、日干强弱等论述",
                          status=SourceStatus.CANDIDATE),
            SourceChapter(chapter_id="CH-YHZP-KANMINRUSHI", chapter_name="看命入式",
                          content_summary="入门式, 以日干为主, 年月日时定位, 得令不得令",
                          status=SourceStatus.CANDIDATE),
        ],
        scope_status=SourceStatus.SCOPE_AUTHORIZED,
        scope_note="子平基础经典, 玄机赋和身弱论直接涉及身弱定义和判定, 授权进入STR-001A第一轮",
    ))

    # 2. 《子平真诠》
    registry.append(CanonicalSource(
        source_id="SRC-ZPZQ",
        source_name="子平真诠",
        source_type="经典",
        editions=[
            SourceEdition(edition_id="ED-ZPZQ-001", edition_name="子平真诠",
                          author="沈孝瞻", dynasty="清",
                          version_note="清乾隆年间沈孝瞻撰, 徐乐吾评注",
                          status=SourceStatus.VERSION_VERIFIED),
        ],
        chapters=[
            SourceChapter(chapter_id="CH-ZPZQ-006", chapter_name="论十干得时不旺失时不弱",
                          chapter_number="第06章",
                          content_summary="明确区分旺衰强弱: 得时为旺失时为衰, 党众为强助寡为弱; 有虽旺而弱者, 有虽衰而强者",
                          status=SourceStatus.SCOPE_AUTHORIZED),
            SourceChapter(chapter_id="CH-ZPZQ-003", chapter_name="论阴阳生死",
                          chapter_number="第03章",
                          content_summary="日主不必生逢禄旺, 月令休囚而年日时得长禄旺便不为弱, 逢库亦为有根",
                          status=SourceStatus.SCOPE_AUTHORIZED),
        ],
        scope_status=SourceStatus.SCOPE_AUTHORIZED,
        scope_note="格局法核心经典, 第06章明确区分旺衰强弱四个概念, 第03章讨论日主强弱判定, 授权进入第一轮",
    ))

    # 3. 《滴天髓》
    registry.append(CanonicalSource(
        source_id="SRC-DTS",
        source_name="滴天髓",
        source_type="经典",
        editions=[
            SourceEdition(edition_id="ED-DTS-001", edition_name="滴天髓阐微",
                          author="京图(传) / 任铁樵注", dynasty="宋/清",
                          version_note="传为京图撰, 任铁樵清道光年间注疏",
                          status=SourceStatus.VERSION_VERIFIED),
        ],
        chapters=[
            SourceChapter(chapter_id="CH-DTS-SHUAIWANG", chapter_name="衰旺",
                          chapter_number="第十七章",
                          content_summary="能知衰旺之真机, 其于三命之奥思过半矣; 旺则宜泄宜伤, 衰则喜帮喜助; 旺中有衰, 衰中有旺",
                          status=SourceStatus.SCOPE_AUTHORIZED),
        ],
        scope_status=SourceStatus.SCOPE_AUTHORIZED,
        scope_note="命理高阶经典, 衰旺章专门讨论旺衰判定的复杂性, 授权进入第一轮",
    ))

    # 4. 《穷通宝鉴》
    registry.append(CanonicalSource(
        source_id="SRC-QTBJ",
        source_name="穷通宝鉴",
        source_type="经典",
        editions=[
            SourceEdition(edition_id="ED-QTBJ-001", edition_name="穷通宝鉴",
                          author="余春台", dynasty="清",
                          version_note="清余春台辑, 原名栏江网",
                          status=SourceStatus.VERSION_VERIFIED),
        ],
        chapters=[
            SourceChapter(chapter_id="CH-QTBJ-GENERAL", chapter_name="总论/十干月谈赋",
                          content_summary="按十干十二月论述调候用神, 涉及各干在各月的旺衰状态",
                          status=SourceStatus.CANDIDATE),
        ],
        scope_status=SourceStatus.CANDIDATE,
        scope_note="调候法核心经典, 主要论调候用神, 身弱判定非其核心主题, 暂列为候选, 第一轮不强制采集",
    ))

    # 5. 《三命通会》
    registry.append(CanonicalSource(
        source_id="SRC-SMTH",
        source_name="三命通会",
        source_type="经典",
        editions=[
            SourceEdition(edition_id="ED-SMTH-001", edition_name="三命通会",
                          author="万民英", dynasty="明",
                          version_note="明万民英撰, 万历年间",
                          status=SourceStatus.VERSION_VERIFIED),
        ],
        chapters=[
            SourceChapter(chapter_id="CH-SMTH-GENERAL", chapter_name="论日主干支/论旺衰",
                          content_summary="百科全书式命理学著作, 涉及日主旺衰的多种论述",
                          status=SourceStatus.CANDIDATE),
        ],
        scope_status=SourceStatus.CANDIDATE,
        scope_note="命理百科全书, 内容庞杂, 身弱相关论述分散, 暂列为候选, 第一轮优先采集前三部",
    ))

    return registry


# ============================================================================
# STR-001A Source Scope 入口契约
# ============================================================================

@dataclass
class STR001ASourceScope:
    """STR-001A Source Scope 入口契约.

    Source Scope是"允许进入Canonical审计的资料边界",
    不是说其中任何一句话天然具有同等授权等级.
    """
    proposition_id: str = "STR-001A"
    proposition_name: str = "日主身弱"
    authorized_source_ids: List[str] = field(default_factory=list)
    authorized_chapter_ids: List[str] = field(default_factory=list)
    collection_principles: List[str] = field(default_factory=list)
    forbidden_behaviors: List[str] = field(default_factory=list)
    audit_steps: List[str] = field(default_factory=list)


def build_str001a_source_scope() -> STR001ASourceScope:
    """建立STR-001A Source Scope入口契约."""
    return STR001ASourceScope(
        proposition_id="STR-001A",
        proposition_name="日主身弱",
        authorized_source_ids=["SRC-YHZP", "SRC-ZPZQ", "SRC-DTS"],
        authorized_chapter_ids=[
            "CH-YHZP-XUANJIFU", "CH-YHZP-SHENRUOLUN",
            "CH-ZPZQ-006", "CH-ZPZQ-003",
            "CH-DTS-SHUAIWANG",
        ],
        collection_principles=[
            "第③步不能直接问'这句话能不能证明身弱'",
            "应该分别问: 这句话是什么性质? → DEFINITION/DESCRIPTIVE/CONDITIONAL/EXAMPLE",
            "→ 它描述什么语义? → 它允许建立什么Mapping? → 它允许什么Evidence Role?",
            "→ 最后才进入Proposition Evaluation",
            "必须允许最终得到REJECTED",
            "不能confirmation bias (不是'找支持身弱的句子')",
            "Source Scope是'允许进入Canonical审计的资料边界', 不是说其中任何一句话天然具有同等授权等级",
        ],
        forbidden_behaviors=[
            "禁止: 搜到一句话就当规则",
            "禁止: 直接判断'这句话能不能证明身弱'",
            "禁止: confirmation bias (只收集支持身弱的句子)",
            "禁止: 把后世注家解释当成原典原文",
            "禁止: 把不同体系(格局法/调候法/旺衰派)的定义混为一谈",
            "禁止: 为了让Proposition成立而选择性引用",
        ],
        audit_steps=[
            "① Canonical Source Scope (已完成)",
            "② Source Claim Collection (进行中)",
            "③ Source Claim Audit: 逐条分类Claim Type, 描述语义, 允许的Mapping和Evidence Role",
            "④ Semantic Mapping: SourceClaim ↔ EngineFact",
            "⑤ Candidate Evidence",
            "⑥ Evidence Contract",
            "⑦ Authorization",
            "⑧ L3 AUTHORIZED",
            "⑨ L4 READY_FOR_EVALUATION",
            "⑩ L4 Proposition Evaluation → PROVEN / PARTIAL / REJECTED",
        ],
    )


# ============================================================================
# Source Claim Collection (第一轮)
# ============================================================================

class ClaimType(str, Enum):
    """Claim Type枚举 (来自冻结的Contract)."""
    DESCRIPTIVE = "DESCRIPTIVE"      # 描述性
    NORMATIVE = "NORMATIVE"          # 规范性
    CONDITIONAL = "CONDITIONAL"      # 条件性
    DEFINITION = "DEFINITION"        # 定义性
    EXAMPLE = "EXAMPLE"              # 示例


@dataclass
class SourceClaimCollected:
    """采集到的Source Claim (第一轮, 未审计).

    注意: 这只是采集, 不是审计结论.
    每条Claim需要经过第③步Audit才能确定其Claim Type/语义/Mapping/Evidence Role.
    """
    claim_id: str
    source_id: str
    source_name: str
    chapter_id: str
    chapter_name: str
    text_reference: str = ""         # 原文引用
    raw_text: str = ""                # 原始文本
    preliminary_claim_type: Optional[ClaimType] = None  # 初步分类(待审计确认)
    semantic_topic: str = ""          # 语义主题
    notes: str = ""
    collection_status: str = "COLLECTED"  # COLLECTED / AUDITING / AUDITED


def collect_first_round_source_claims() -> List[SourceClaimCollected]:
    """第一轮Source Claim Collection.

    基于已搜索到的原典内容, 逐条采集.
    注意: 这只是采集, 不是审计结论. 不直接判断"能否证明身弱".
    """
    claims = []

    # === 《渊海子平·玄机赋》 ===
    claims.append(SourceClaimCollected(
        claim_id="SC-YHZP-XJ-001",
        source_id="SRC-YHZP", source_name="渊海子平",
        chapter_id="CH-YHZP-XUANJIFU", chapter_name="玄机赋",
        text_reference="玄机赋",
        raw_text="身坐休囚，平生未济。身旺喜逢禄马。身弱忌见财官。",
        preliminary_claim_type=ClaimType.NORMATIVE,
        semantic_topic="身弱的忌神/身旺的喜神",
        notes="明确提到'身弱忌见财官', 但这是规范性陈述(身弱应该忌什么), 不是身弱的定义或判定标准",
    ))

    claims.append(SourceClaimCollected(
        claim_id="SC-YHZP-XJ-002",
        source_id="SRC-YHZP", source_name="渊海子平",
        chapter_id="CH-YHZP-XUANJIFU", chapter_name="玄机赋",
        text_reference="玄机赋",
        raw_text="得时俱为旺论，失令便作衰看。四柱无根，...",
        preliminary_claim_type=ClaimType.DEFINITION,
        semantic_topic="旺衰的基本判定: 得时/失令 + 有根/无根",
        notes="'得时俱为旺论, 失令便作衰看'是旺衰判定的基本原则; '四柱无根'涉及根气判定",
    ))

    # === 《渊海子平·身弱论》 ===
    claims.append(SourceClaimCollected(
        claim_id="SC-YHZP-SR-001",
        source_id="SRC-YHZP", source_name="渊海子平",
        chapter_id="CH-YHZP-SHENRUOLUN", chapter_name="身弱论",
        text_reference="身弱论",
        raw_text="阳木无根，生于丑月；水多转贵，金多则折。乙木无根，生临丑月；金多转贵，火土则折。丙火无根，子申全见；无制无生，此身贫贱。",
        preliminary_claim_type=ClaimType.CONDITIONAL,
        semantic_topic="身弱的具体条件: 无根 + 生月 + 克泄",
        notes="按十干分述身弱的具体条件: 无根 + 特定生月 + 特定克泄. 这是条件性陈述, 给出了身弱的具体判定条件之一",
    ))

    # === 《子平真诠·第06章 论十干得时不旺失时不弱》 ===
    claims.append(SourceClaimCollected(
        claim_id="SC-ZPZQ-06-001",
        source_id="SRC-ZPZQ", source_name="子平真诠",
        chapter_id="CH-ZPZQ-006", chapter_name="论十干得时不旺失时不弱",
        text_reference="第06章",
        raw_text="旺衰强弱四字，昔人论命，每笼统互用，不知须分别看也。大致得时为旺，失时为衰；党众为强，助寡为弱。故有虽旺而弱者，亦有虽衰而强者，分别观之。",
        preliminary_claim_type=ClaimType.DEFINITION,
        semantic_topic="旺衰强弱四个概念的区分: 旺/衰=得时/失时, 强/弱=党众/助寡",
        notes="非常重要的定义性陈述: 明确区分旺衰和强弱是两个不同维度. 旺衰看月令(得时/失时), 强弱看党众(生助多寡). 有虽旺而弱者, 有虽衰而强者",
    ))

    claims.append(SourceClaimCollected(
        claim_id="SC-ZPZQ-06-002",
        source_id="SRC-ZPZQ", source_name="子平真诠",
        chapter_id="CH-ZPZQ-006", chapter_name="论十干得时不旺失时不弱",
        text_reference="第06章",
        raw_text="秋木虽弱，木根深而木亦强。干甲乙而支寅卯，遇官透而能受，逢水生而太过，是失时不弱也。",
        preliminary_claim_type=ClaimType.EXAMPLE,
        semantic_topic="失时不弱的例子: 秋木虽失令但根深则强",
        notes="示例: 秋木虽弱(失时), 但木根深(通根)则木亦强. 说明失时不等于弱, 根气可以弥补月令不足",
    ))

    claims.append(SourceClaimCollected(
        claim_id="SC-ZPZQ-06-003",
        source_id="SRC-ZPZQ", source_name="子平真诠",
        chapter_id="CH-ZPZQ-006", chapter_name="论十干得时不旺失时不弱",
        text_reference="第06章",
        raw_text="书云，得时俱为旺论，失时便作衰看。虽是至理，亦死法也。然亦可活看，夫五行之气，流行四时，虽日干各有专令，而其实专令当中，亦有并存者在。",
        preliminary_claim_type=ClaimType.DESCRIPTIVE,
        semantic_topic="得时失令是基本原则但非绝对, 需活看",
        notes="描述性陈述: 得时为旺失时为衰虽是至理, 但也是死法, 需要活看. 五行之气流行四时, 专令中亦有并存者",
    ))

    # === 《子平真诠·第03章 论阴阳生死》 ===
    claims.append(SourceClaimCollected(
        claim_id="SC-ZPZQ-03-001",
        source_id="SRC-ZPZQ", source_name="子平真诠",
        chapter_id="CH-ZPZQ-003", chapter_name="论阴阳生死",
        text_reference="第03章",
        raw_text="人之日主，不必生逢禄旺，即月令休囚，而年日时中，得长禄旺，便不为弱，就使逢库，亦为有根。",
        preliminary_claim_type=ClaimType.CONDITIONAL,
        semantic_topic="日主强弱判定: 月令休囚但年日时得禄旺则不为弱, 逢库亦为有根",
        notes="条件性陈述: 日主不必生逢禄旺, 月令休囚但年日时中得长禄旺便不为弱, 就使逢库亦为有根. 给出了'不为弱'的具体条件",
    ))

    # === 《滴天髓·第十七章 衰旺》 ===
    claims.append(SourceClaimCollected(
        claim_id="SC-DTS-SW-001",
        source_id="SRC-DTS", source_name="滴天髓",
        chapter_id="CH-DTS-SHUAIWANG", chapter_name="衰旺",
        text_reference="第十七章 衰旺",
        raw_text="能知衰旺之真机，其于三命之奥，思过半矣。",
        preliminary_claim_type=ClaimType.DESCRIPTIVE,
        semantic_topic="衰旺判定的重要性",
        notes="描述性陈述: 能知衰旺之真机, 三命之奥思过半矣. 强调衰旺判定的重要性, 但未给出具体判定标准",
    ))

    claims.append(SourceClaimCollected(
        claim_id="SC-DTS-SW-002",
        source_id="SRC-DTS", source_name="滴天髓",
        chapter_id="CH-DTS-SHUAIWANG", chapter_name="衰旺",
        text_reference="第十七章 衰旺 原注",
        raw_text="旺则宜泄宜伤，衰则喜帮喜助，子平之理也。然旺中有衰者存，不可损也；衰中有旺者存，不可益也。旺之极者不可损，以损在其中矣；衰之极者不可益，以益在其中矣。",
        preliminary_claim_type=ClaimType.NORMATIVE,
        semantic_topic="旺衰的处理原则: 旺宜泄伤, 衰喜帮助; 但旺中有衰, 衰中有旺, 不可一概而论",
        notes="规范性陈述: 旺则宜泄宜伤, 衰则喜帮喜助是子平之理. 但旺中有衰不可损, 衰中有旺不可益. 旺之极者不可损, 衰之极者不可益. 这是处理原则, 不是判定标准",
    ))

    claims.append(SourceClaimCollected(
        claim_id="SC-DTS-SW-003",
        source_id="SRC-DTS", source_name="滴天髓",
        chapter_id="CH-DTS-SHUAIWANG", chapter_name="衰旺",
        text_reference="第十七章 衰旺 任氏曰",
        raw_text="得时俱为旺论，失令便作衰看，虽是至理，亦死法也。夫五行之气，流行于四时，虽日干各有专令，而其实专令之中，亦有并存者在。",
        preliminary_claim_type=ClaimType.DESCRIPTIVE,
        semantic_topic="得时失令是基本原则但非绝对, 需活看 (任铁樵注)",
        notes="任铁樵注: 与《子平真诠》第06章类似的论述. 得时为旺失时为衰虽是至理, 但也是死法, 需要活看",
    ))

    return claims


# ============================================================================
# 第一轮采集统计
# ============================================================================

def print_collection_summary(registry, scope, claims):
    """打印采集摘要."""
    print("=" * 100)
    print("STR-001A Canonical Source Audit - 日主身弱 原典审计启动")
    print("=" * 100)

    print(f"\n{'='*100}")
    print("一、Canonical Source Registry (五部核心子平经典)")
    print("=" * 100)
    for src in registry:
        print(f"\n  {src.source_id}: {src.source_name} ({src.source_type})")
        print(f"    scope_status: {src.scope_status.value}")
        print(f"    版本: {len(src.editions)}个")
        for ed in src.editions:
            print(f"      - {ed.edition_name} | {ed.author} | {ed.dynasty} | {ed.status.value}")
        print(f"    章节: {len(src.chapters)}个")
        for ch in src.chapters:
            print(f"      - {ch.chapter_id}: {ch.chapter_name} | {ch.status.value}")
        print(f"    scope_note: {src.scope_note}")

    print(f"\n{'='*100}")
    print("二、STR-001A Source Scope 入口契约")
    print("=" * 100)
    print(f"  proposition_id: {scope.proposition_id}")
    print(f"  proposition_name: {scope.proposition_name}")
    print(f"  authorized_source_ids: {scope.authorized_source_ids}")
    print(f"  authorized_chapter_ids: {len(scope.authorized_chapter_ids)}个")
    print(f"\n  采集原则:")
    for p in scope.collection_principles:
        print(f"    - {p}")
    print(f"\n  禁止行为:")
    for f in scope.forbidden_behaviors:
        print(f"    - {f}")
    print(f"\n  审计步骤:")
    for s in scope.audit_steps:
        print(f"    - {s}")

    print(f"\n{'='*100}")
    print("三、第一轮 Source Claim Collection (采集, 未审计)")
    print("=" * 100)
    print(f"  总采集数: {len(claims)}条")

    # 按来源统计
    by_source = {}
    by_type = {}
    for c in claims:
        by_source[c.source_name] = by_source.get(c.source_name, 0) + 1
        if c.preliminary_claim_type:
            by_type[c.preliminary_claim_type.value] = by_type.get(c.preliminary_claim_type.value, 0) + 1

    print(f"\n  按来源统计:")
    for src, cnt in by_source.items():
        print(f"    - {src}: {cnt}条")

    print(f"\n  按初步Claim Type统计 (待审计确认):")
    for ct, cnt in by_type.items():
        print(f"    - {ct}: {cnt}条")

    print(f"\n  逐条列出:")
    for c in claims:
        print(f"\n    {c.claim_id}:")
        print(f"      来源: {c.source_name} · {c.chapter_name}")
        print(f"      初步Claim Type: {c.preliminary_claim_type.value if c.preliminary_claim_type else '待分类'}")
        print(f"      语义主题: {c.semantic_topic}")
        print(f"      原文: {c.raw_text[:80]}{'...' if len(c.raw_text) > 80 else ''}")
        print(f"      备注: {c.notes}")

    print(f"\n{'='*100}")
    print("四、下一步")
    print("=" * 100)
    print("""
  第③步 Source Claim Audit (待执行):
    对每条采集到的Claim逐条审计:
      1. 确认Claim Type (DEFINITION/DESCRIPTIVE/NORMATIVE/CONDITIONAL/EXAMPLE)
      2. 描述语义 (它在说什么?)
      3. 允许建立什么Mapping (SourceClaim ↔ EngineFact)
      4. 允许什么Evidence Role (PRIMARY/SUPPORTING/CONTEXTUAL/EXCLUSION)
      5. 最后才进入Proposition Evaluation

  注意:
    - 不直接判断"这句话能不能证明身弱"
    - 必须允许最终得到REJECTED
    - 不能confirmation bias
    - Contract/Governance Layer保持FROZEN, 不做架构修改
""")

    print("=" * 100)
    print("STR-001A Canonical Source Audit 启动完成. 第一轮Source Claim Collection完成.")
    print("=" * 100)


# ============================================================================
# 主函数
# ============================================================================

def main():
    registry = build_canonical_source_registry()
    scope = build_str001a_source_scope()
    claims = collect_first_round_source_claims()
    print_collection_summary(registry, scope, claims)


if __name__ == "__main__":
    main()
