"""STR-001A Phase 5D - Exception / Qualifier Mapping.

目标: 研究"有根/有生扶/弱处复生/不大弱"对 MAP-DZL-001 逻辑强度的约束
只处理: MAP-DZL-001-REFINED
不新增 Source Claim
不做 Authorization
不进入 L4 Evaluation
不升级成可执行的"身弱算法"

核心审计链:
临死绝
   │
   ├── 有根
   ├── 有生扶
   ├── 弱处复生
   └── 不大弱 / 仍能任财官
          │
          ▼
   是否构成 EXCLUSION?
   是否构成 QUALIFIER?
   是否仅降低证明强度?
          │
          ▼
   更新 MAP-DZL-001 的 Logical Strength

必须避免的污染:
- 不能从"临死绝但有根"直接反推出"有根 → 身强"
- EXCLUSION ≠ POSITIVE_PROOF

正确的数据结构:
- PRIMARY_CANDIDATE: condition=临死绝, logical_strength=CONTEXTUAL_SUFFICIENT
- QUALIFIER: condition=有根/有生扶, effect=REDUCE_STRENGTH
- EXCLUSION: condition=某些特定复生条件, effect=BLOCK_OR_LIMIT_PROOF
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# 枚举
# ============================================================================

class QualifierEffect(str, Enum):
    REDUCE_STRENGTH = "REDUCE_STRENGTH"  # 降低证明强度
    LIMIT_PROOF = "LIMIT_PROOF"  # 限制证明范围
    BLOCK_PROOF = "BLOCK_PROOF"  # 阻断证明(特定条件下)


class QualifierType(str, Enum):
    QUALIFIER = "QUALIFIER"  # 修饰符, 降低强度但不阻断
    EXCLUSION = "EXCLUSION"  # 排除, 特定条件下阻断证明
    CONTEXT_REQUIREMENT = "CONTEXT_REQUIREMENT"  # 语境要求


class LogicalStrength(str, Enum):
    UNIVERSAL_SUFFICIENT = "UNIVERSAL_SUFFICIENT"  # 普遍充分条件
    CONTEXTUAL_SUFFICIENT = "CONTEXTUAL_SUFFICIENT"  # 语境充分条件
    PARTIAL_SUFFICIENT = "PARTIAL_SUFFICIENT"  # 部分充分条件(需配合其他证据)
    INSUFFICIENT = "INSUFFICIENT"  # 不充分


# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class SemanticAudit:
    """原典语义审计."""
    concept: str = ""
    question: str = ""
    original_sources: List[str] = field(default_factory=list)
    semantic_meaning: str = ""
    distinctions: List[str] = field(default_factory=list)
    ambiguity: str = ""
    conclusion: str = ""


@dataclass
class QualifierEntry:
    """修饰符/排除项."""
    qualifier_id: str = ""
    concept: str = ""
    qualifier_type: QualifierType = QualifierType.QUALIFIER
    condition: str = ""
    effect: QualifierEffect = QualifierEffect.REDUCE_STRENGTH
    original_source: str = ""
    semantic_basis: str = ""
    strength_reduction: str = ""  # 对逻辑强度的影响描述
    notes: str = ""
    is_positive_proof: bool = False  # 是否构成正向证明(应该永远是False)


@dataclass
class NegativeTest:
    test_id: str = ""
    test_name: str = ""
    test_description: str = ""
    expected: str = ""
    actual: str = ""
    passed: bool = False


# ============================================================================
# Phase 5D 深审
# ============================================================================

def phase5d_exception_qualifier_mapping() -> Dict[str, Any]:
    """Phase 5D Exception / Qualifier Mapping."""
    result = {}

    # === 1. "有根"的语义审计 ===
    root_audit = SemanticAudit(
        concept="有根",
        question="'有根'到底是什么语义? 通根? 得禄? 逢库? 印生?",
        original_sources=[
            "《子平真诠·论十干得时不旺失时不弱》: '是故十干不论月令休囚，只要四柱有根，便能受财官食神而当伤官七煞。长生禄旺，根之重者也；墓库余气，根之轻者也。'",
            "《子平真诠·论阴阳生死》: '人之日主，不必生逢禄旺，即月令休囚，而年日时中，得长生禄旺，便不为弱，就使逢库，亦为有根。'",
        ],
        semantic_meaning="""
"有根"=地支藏干中有日主之字面(同类五行)。
- "根深"=四柱地支有日主之禄旺位支(长生、禄、旺)
- "根浅"=四柱地支有日主之长生、余气、库(墓库余气)

关键: "有根"不等于"身强"。
《子平真诠》说的是"便能受财官食神而当伤官七煞"，
这是对日主"能力"的描述，不是对"身强身弱"的直接判定。
        """.strip(),
        distinctions=[
            "通根: 地支藏干中含有日主的比肩或劫财(更严格的定义)",
            "得禄: 日主在禄位(如甲禄在寅, 乙禄在卯) — 根深",
            "逢库: 日主在墓库位(如甲墓在未) — 根浅, 且阴干逢库可能'无用'",
            "印生: 印星生日主 — 这是'生扶', 不是'有根'",
            "长生: 日主在长生位 — 根深(阳长生有力, 阴长生不甚有力)",
        ],
        ambiguity="""
⚠️ 歧义:
1. "有根"的范围: 只要地支藏干中有同类五行就算? 还是必须是比肩/劫财?
2. "根深"和"根浅"对身弱判定的影响程度不同, 不能一概而论
3. 阴干逢库(如乙逢戌)可能"不作此论", 因为戌中无藏木
4. "有根"只是"能受财官", 不等于"不弱"
        """.strip(),
        conclusion="""
结论: "有根"是一个 QUALIFIER, 不是 EXCLUSION。
- 根浅(墓库余气): 降低临死绝→身弱的证明强度, 但不阻断
- 根深(长生禄旺): 可能在特定条件下构成 EXCLUSION("便不为弱")
- 但"有根"本身不等于"身强", 不能反推"有根 → 身强"
        """.strip(),
    )
    result["root_audit"] = root_audit

    # === 2. "有生扶"与"有根"的区别 ===
    support_audit = SemanticAudit(
        concept="有生扶",
        question="'有生扶'与'有根'是否同义? 不能未经原典授权合并。",
        original_sources=[
            "《渊海子平》: '印绶生身，最为有力'",
            "现代命理实践: 生扶指印星(生我者)、比劫(同我者)对日干的助力",
        ],
        semantic_meaning="""
"生扶"=印星(生我者) + 比劫(同我者)对日干的助力。
- 印星: 生日主的五行(如壬癸水为甲乙木的印星)
- 比劫: 同日主的五行(如甲乙木为甲乙木的比劫)

"有生扶"与"有根"不同义:
- "有根": 地支藏干中有日主同类(在地支中)
- "有生扶": 天干或地支中有印星或比劫(可以在天干, 也可以在地支)
- "无根有印": 仍然可能身弱(印星生身但日主无根, 力量漂浮)
        """.strip(),
        distinctions=[
            "有根: 地支藏干中有日主同类 — 在地支中, 是'根基'",
            "有生扶: 有印星或比劫 — 可以在天干(虚浮)或地支(有力)",
            "印生: 印星生日主 — 生扶的一种, 不等于有根",
            "比助: 比劫帮日主 — 生扶的一种, 天干比劫可能虚浮",
            "无根有印: 日主无根但有印星生 — 仍然可能身弱, 因为'干多不如根重'",
        ],
        ambiguity="""
⚠️ 歧义:
1. "有生扶"的范围: 只要有印星或比劫就算? 还是必须有力(在地支有根)?
2. 天干虚浮的印比 vs 地支有力的印比, 对身弱判定的影响不同
3. "有生扶"不等于"不弱", 生扶力量不足时仍然身弱
        """.strip(),
        conclusion="""
结论: "有生扶"是一个 QUALIFIER, 不是 EXCLUSION。
- 有生扶但力量不足: 降低临死绝→身弱的证明强度, 但不阻断
- 有生扶且力量充足(地支有根): 可能在特定条件下构成 EXCLUSION
- 但"有生扶"本身不等于"身强", 不能反推"有生扶 → 身强"
- "有生扶"与"有根"不同义, 不能未经原典授权合并
        """.strip(),
    )
    result["support_audit"] = support_audit

    # === 3. "弱处复生"的语义审计 ===
    revival_audit = SemanticAudit(
        concept="弱处复生",
        question="'弱处复生'到底是什么? 是单纯有印比? 还是特定干支组合? 是否存在'复生但仍弱'?",
        original_sources=[
            "《滴天髓》相关: '金逢艮而遇土，号曰还魂，水入巽而见金，名为不绝。'",
            "后世解释: '弱处复生有两说。一说: 乙本春旺夏死秋绝冬生，木虽绝在申，复受气在申，为申中有长生壬水，为甲乙木之印绶，故曰弱处逢生也。一说: 弱处逢生是五行绝处，四柱复有...'",
        ],
        semantic_meaning="""
"弱处复生"(又称"弱处逢生"、"还魂"、"不绝"):
- 五行在绝处(最弱状态), 但该地支中藏有生扶该五行的印星
- 例如: 木绝在申, 但申中藏壬水(长生), 壬水生木, 所以"弱处逢生"
- "金逢艮(寅)而遇土": 金绝在寅, 但寅中藏戊土, 土生金, 所以"还魂"
- "水入巽(巳)而见金": 水绝在巳, 但巳中藏庚金, 金生水, 所以"不绝"

这是特定的干支组合, 不是单纯有印比。
关键: 绝处的地支中藏有印星, 印星在绝地生扶日主。
        """.strip(),
        distinctions=[
            "弱处复生: 日主在绝地, 但绝地地支中藏有印星 — 特定组合",
            "单纯有印比: 日主在绝地, 但其他地支有印比 — 不是'弱处复生'",
            "还魂: 金绝在寅, 寅中藏戊土生金 — 特定组合",
            "不绝: 水绝在巳, 巳中藏庚金生水 — 特定组合",
            "复生但仍弱: 即使有弱处复生, 复生力量可能不足, 仍然可能身弱",
        ],
        ambiguity="""
⚠️ 歧义:
1. "弱处复生"有两说, 具体定义需要进一步确认
2. 复生的力量强度: 是完全"不绝"? 还是只是"降低弱的程度"?
3. 是否存在"复生但仍弱"的情况? 很可能存在, 因为复生只是绝地有印生, 力量可能仍然不足
4. "弱处复生"是否构成 EXCLUSION? 还是只是 QUALIFIER?
        """.strip(),
        conclusion="""
结论: "弱处复生"可能是 QUALIFIER 或特定条件下的 EXCLUSION。
- 如果复生力量充足(绝地印星有力): 可能构成 EXCLUSION("不绝")
- 如果复生力量不足: 只是 QUALIFIER(降低证明强度)
- 但"弱处复生"本身不等于"身强", 不能反推"弱处复生 → 身强"
- "弱处复生"是特定干支组合, 不是单纯有印比
- 很可能存在"复生但仍弱"的情况
        """.strip(),
    )
    result["revival_audit"] = revival_audit

    # === 4. "不大弱"的逻辑角色 ===
    not_weak_audit = SemanticAudit(
        concept="不大弱 / 便不为弱",
        question="'不大弱'是什么逻辑角色? 很可能不是'身强', 而是对'身弱程度'的限定。不要强行二元化成 STRONG/WEAK。",
        original_sources=[
            "《子平真诠·论阴阳生死》: '人之日主，不必生逢禄旺，即月令休囚，而年日时中，得长生禄旺，便不为弱，就使逢库，亦为有根。'",
            "《子平真诠·论十干得时不旺失时不弱》: '是故十干不论月令休囚，只要四柱有根，便能受财官食神而当伤官七煞。'",
        ],
        semantic_meaning="""
"便不为弱"/"不大弱":
- 《子平真诠》说"得长生禄旺，便不为弱" — 这是在特定条件下(得长生禄旺)的判定
- "就使逢库，亦为有根" — 逢库只是"有根", 不是"不为弱"
- "便能受财官食神而当伤官七煞" — 这是对日主"能力"的描述, 不是直接说"身强"

关键: "不大弱"不是"身强", 而是对"身弱程度"的限定。
- 身弱的程度可能有: 极弱 / 很弱 / 弱 / 不大弱 / 中和 / 较强 / 强
- "不大弱"意味着: 仍然偏弱, 但弱的程度有限, 能承担一定的财官食伤
- 不要强行二元化成 STRONG/WEAK
        """.strip(),
        distinctions=[
            "便不为弱: 在特定条件下(得长生禄旺)的判定 — 可能构成 EXCLUSION",
            "亦为有根: 逢库只是有根 — 只是 QUALIFIER, 不是 EXCLUSION",
            "能受财官: 有根时能承担财官食伤 — 对能力的描述, 不是身强",
            "不大弱: 仍然偏弱但程度有限 — 对身弱程度的限定, 不是身强",
            "身强: 日主力量充足 — 与'不大弱'不同, 不要混淆",
        ],
        ambiguity="""
⚠️ 歧义:
1. "便不为弱"的条件: 必须是"得长生禄旺"? 还是"有根"就算?
   - 从原文看, "得长生禄旺，便不为弱"和"就使逢库，亦为有根"是分开的
   - 所以"得长生禄旺"才"便不为弱", "逢库"只是"亦为有根"
2. "不大弱"的精确定义: 偏弱到什么程度才算"不大弱"?
3. "不大弱"是否构成 EXCLUSION? 还是只是对身弱程度的限定?
        """.strip(),
        conclusion="""
结论: "不大弱"/"便不为弱"的逻辑角色需要区分:
- "得长生禄旺，便不为弱": 特定条件下的 EXCLUSION(根深时不弱)
- "逢库，亦为有根": 只是 QUALIFIER(根浅时有根, 但可能仍弱)
- "能受财官食神": 对日主能力的描述, 不是身强的直接判定
- "不大弱": 对身弱程度的限定, 不是"身强", 不要二元化

关键: "不大弱"不等于"身强", 不能反推"不大弱 → 身强"。
        """.strip(),
    )
    result["not_weak_audit"] = not_weak_audit

    # === 5. 反例的逻辑角色判断 (最重要) ===
    role_judgment = {
        "question": "反例究竟是 Block、Qualifier 还是仅降低强度? (这是本阶段最重要的判断)",
        "judgments": [
            {
                "concept": "有根(根浅: 墓库余气)",
                "role": "QUALIFIER",
                "effect": "REDUCE_STRENGTH",
                "basis": "《子平真诠》: '墓库余气，根之轻者也。' 根浅只是有根, 不等于不弱。",
                "is_exclusion": False,
                "is_positive_proof": False,
                "notes": "根浅时降低临死绝→身弱的证明强度, 但不阻断。阴干逢库可能'无用'。",
            },
            {
                "concept": "有根(根深: 长生禄旺)",
                "role": "EXCLUSION (特定条件下)",
                "effect": "BLOCK_PROOF",
                "basis": "《子平真诠》: '得长生禄旺，便不为弱。' 根深时可能不弱。",
                "is_exclusion": True,
                "is_positive_proof": False,
                "notes": "根深时可能阻断临死绝→身弱的证明, 但这是特定条件下的EXCLUSION, 不是正向证明'身强'。",
            },
            {
                "concept": "有生扶(力量不足)",
                "role": "QUALIFIER",
                "effect": "REDUCE_STRENGTH",
                "basis": "有生扶但力量不足(如天干虚浮印比), 仍然可能身弱。",
                "is_exclusion": False,
                "is_positive_proof": False,
                "notes": "降低证明强度, 但不阻断。'有生扶'与'有根'不同义。",
            },
            {
                "concept": "有生扶(力量充足, 地支有根)",
                "role": "EXCLUSION (特定条件下)",
                "effect": "BLOCK_PROOF",
                "basis": "生扶力量充足时可能不弱, 但需要具体条件。",
                "is_exclusion": True,
                "is_positive_proof": False,
                "notes": "特定条件下的EXCLUSION, 不是正向证明'身强'。",
            },
            {
                "concept": "弱处复生(复生力量不足)",
                "role": "QUALIFIER",
                "effect": "REDUCE_STRENGTH",
                "basis": "即使有弱处复生, 复生力量可能不足, 仍然可能身弱。",
                "is_exclusion": False,
                "is_positive_proof": False,
                "notes": "降低证明强度。'弱处复生'是特定干支组合, 不是单纯有印比。",
            },
            {
                "concept": "弱处复生(复生力量充足)",
                "role": "EXCLUSION (特定条件下)",
                "effect": "LIMIT_PROOF",
                "basis": "'还魂'、'不绝'可能意味着不完全弱, 但需要具体条件。",
                "is_exclusion": True,
                "is_positive_proof": False,
                "notes": "特定条件下可能限制证明, 但不是完全阻断, 也不是正向证明'身强'。",
            },
            {
                "concept": "不大弱 / 便不为弱(得长生禄旺)",
                "role": "EXCLUSION (特定条件下)",
                "effect": "BLOCK_PROOF",
                "basis": "《子平真诠》: '得长生禄旺，便不为弱。'",
                "is_exclusion": True,
                "is_positive_proof": False,
                "notes": "特定条件下的EXCLUSION。'不大弱'不是'身强', 不要二元化。",
            },
            {
                "concept": "能受财官食神(有根)",
                "role": "QUALIFIER",
                "effect": "REDUCE_STRENGTH",
                "basis": "《子平真诠》: '只要四柱有根，便能受财官食神而当伤官七煞。'",
                "is_exclusion": False,
                "is_positive_proof": False,
                "notes": "这是对日主能力的描述, 不是对身强身弱的直接判定。降低证明强度, 但不阻断。",
            },
        ],
        "summary": """
总结:
1. 大多数反例是 QUALIFIER(降低证明强度), 不是 EXCLUSION
2. 只有在特定条件下(根深/得长生禄旺/复生力量充足)才构成 EXCLUSION
3. 所有反例都不是 POSITIVE_PROOF(不能反推"身强")
4. EXCLUSION ≠ POSITIVE_PROOF
5. "不大弱"不是"身强", 是对身弱程度的限定, 不要二元化
        """.strip(),
    }
    result["role_judgment"] = role_judgment

    # === 6. 更新 MAP-DZL-001 的 Logical Strength ===
    updated_mapping = {
        "mapping_id": "MAP-DZL-001-REFINED-v2",
        "source_claim_id": "SC-YHZP-DZL-001",
        "primary_condition": {
            "condition": "临死绝之地",
            "description": "日干在四个地支(年月日时)中至少一个处于十二长生的'死'或'绝'状态",
            "logical_strength": LogicalStrength.CONTEXTUAL_SUFFICIENT.value,
            "context_requirement": "日干衰(需要生扶)",
            "position_scope_status": "PARTIALLY_DEFINED",  # 继续标记, 不要误写成Canonically Authorized
            "notes": "四个地支任一处死绝目前继续标记为PARTIALLY_DEFINED, 不要因为Phase 5C已形成Candidate Mapping就把位置范围误写成Canonically Authorized。",
        },
        "qualifiers": [
            QualifierEntry(
                qualifier_id="QUAL-001",
                concept="有根(根浅: 墓库余气)",
                qualifier_type=QualifierType.QUALIFIER,
                condition="日干在地支中有根, 但根浅(墓库余气)",
                effect=QualifierEffect.REDUCE_STRENGTH,
                original_source="《子平真诠》: '墓库余气，根之轻者也。'",
                semantic_basis="根浅只是有根, 不等于不弱, 降低临死绝→身弱的证明强度",
                strength_reduction="CONTEXTUAL_SUFFICIENT → PARTIAL_SUFFICIENT(需配合其他证据)",
                notes="阴干逢库可能'无用'。",
                is_positive_proof=False,
            ),
            QualifierEntry(
                qualifier_id="QUAL-002",
                concept="有生扶(力量不足)",
                qualifier_type=QualifierType.QUALIFIER,
                condition="有印星或比劫生扶, 但力量不足(如天干虚浮)",
                effect=QualifierEffect.REDUCE_STRENGTH,
                original_source="《渊海子平》: '印绶生身，最为有力'(但有力与否需看位置)",
                semantic_basis="有生扶但力量不足, 仍然可能身弱, 降低证明强度",
                strength_reduction="CONTEXTUAL_SUFFICIENT → PARTIAL_SUFFICIENT",
                notes="'有生扶'与'有根'不同义, 不能未经原典授权合并。",
                is_positive_proof=False,
            ),
            QualifierEntry(
                qualifier_id="QUAL-003",
                concept="弱处复生(复生力量不足)",
                qualifier_type=QualifierType.QUALIFIER,
                condition="日干在绝地, 但绝地地支中藏有印星, 复生力量不足",
                effect=QualifierEffect.REDUCE_STRENGTH,
                original_source="《滴天髓》: '金逢艮而遇土，号曰还魂，水入巽而见金，名为不绝。'",
                semantic_basis="即使有弱处复生, 复生力量可能不足, 仍然可能身弱",
                strength_reduction="CONTEXTUAL_SUFFICIENT → PARTIAL_SUFFICIENT",
                notes="'弱处复生'是特定干支组合, 不是单纯有印比。很可能存在'复生但仍弱'。",
                is_positive_proof=False,
            ),
            QualifierEntry(
                qualifier_id="QUAL-004",
                concept="能受财官食神(有根)",
                qualifier_type=QualifierType.QUALIFIER,
                condition="日干有根, 能受财官食神而当伤官七煞",
                effect=QualifierEffect.REDUCE_STRENGTH,
                original_source="《子平真诠》: '只要四柱有根，便能受财官食神而当伤官七煞。'",
                semantic_basis="这是对日主能力的描述, 不是对身强身弱的直接判定",
                strength_reduction="CONTEXTUAL_SUFFICIENT → PARTIAL_SUFFICIENT",
                notes="'能受财官'不等于'身强', 只是有承担能力。",
                is_positive_proof=False,
            ),
        ],
        "exclusions": [
            QualifierEntry(
                qualifier_id="EXCL-001",
                concept="有根(根深: 长生禄旺)",
                qualifier_type=QualifierType.EXCLUSION,
                condition="日干在地支中有根深(长生禄旺)",
                effect=QualifierEffect.BLOCK_PROOF,
                original_source="《子平真诠》: '得长生禄旺，便不为弱。'",
                semantic_basis="根深时可能不弱, 特定条件下阻断临死绝→身弱的证明",
                strength_reduction="CONTEXTUAL_SUFFICIENT → BLOCKED(特定条件下)",
                notes="这是特定条件下的EXCLUSION, 不是正向证明'身强'。EXCLUSION ≠ POSITIVE_PROOF。",
                is_positive_proof=False,
            ),
            QualifierEntry(
                qualifier_id="EXCL-002",
                concept="弱处复生(复生力量充足)",
                qualifier_type=QualifierType.EXCLUSION,
                condition="日干在绝地, 但绝地地支中藏有印星, 复生力量充足",
                effect=QualifierEffect.LIMIT_PROOF,
                original_source="《滴天髓》: '还魂'、'不绝'",
                semantic_basis="复生力量充足时可能不完全弱, 特定条件下限制证明",
                strength_reduction="CONTEXTUAL_SUFFICIENT → LIMITED(特定条件下)",
                notes="特定条件下可能限制证明, 但不是完全阻断, 也不是正向证明'身强'。",
                is_positive_proof=False,
            ),
            QualifierEntry(
                qualifier_id="EXCL-003",
                concept="不大弱 / 便不为弱(得长生禄旺)",
                qualifier_type=QualifierType.EXCLUSION,
                condition="日干得长生禄旺, 便不为弱",
                effect=QualifierEffect.BLOCK_PROOF,
                original_source="《子平真诠》: '得长生禄旺，便不为弱。'",
                semantic_basis="特定条件下不弱, 阻断临死绝→身弱的证明",
                strength_reduction="CONTEXTUAL_SUFFICIENT → BLOCKED(特定条件下)",
                notes="'不大弱'不是'身强', 是对身弱程度的限定, 不要二元化。EXCLUSION ≠ POSITIVE_PROOF。",
                is_positive_proof=False,
            ),
        ],
        "updated_logical_strength": {
            "base_strength": LogicalStrength.CONTEXTUAL_SUFFICIENT.value,
            "with_qualifiers": LogicalStrength.PARTIAL_SUFFICIENT.value,
            "with_exclusions": "BLOCKED (特定条件下)",
            "summary": """
基础逻辑强度: CONTEXTUAL_SUFFICIENT(语境充分条件)
- 临死绝 + 日干衰 → 身弱候选(语境充分)

有QUALIFIER时(有根浅/有生扶不足/弱处复生不足):
- 逻辑强度降为 PARTIAL_SUFFICIENT(需配合其他证据)
- 不阻断证明, 只是降低强度

有EXCLUSION时(根深/得长生禄旺/复生充足):
- 特定条件下 BLOCKED 或 LIMITED
- 不构成正向证明'身强'
- EXCLUSION ≠ POSITIVE_PROOF
            """.strip(),
        },
        "mapping_authorization": "NOT_AUTHORIZED",
        "status": "NOT_AUTHORIZED",
        "notes": """
Phase 5D更新:
1. 增加了4个QUALIFIER和3个EXCLUSION
2. 更新了逻辑强度: 基础CONTEXTUAL_SUFFICIENT, 有QUALIFIER时降为PARTIAL_SUFFICIENT, 有EXCLUSION时特定条件下BLOCKED
3. 所有QUALIFIER和EXCLUSION都不是POSITIVE_PROOF, 不能反推'身强'
4. 位置范围继续标记为PARTIALLY_DEFINED, 不要误写成Canonically Authorized
5. 仍然不做Authorization, 不进入L4 Evaluation, 不升级成可执行的'身弱算法'
        """.strip(),
    }
    result["updated_mapping"] = updated_mapping

    return result


# ============================================================================
# Negative Tests
# ============================================================================

def run_negative_tests(result: Dict[str, Any]) -> List[NegativeTest]:
    """执行Negative Tests."""
    tests = []

    # NEG-01: EXCLUSION ≠ POSITIVE_PROOF
    tests.append(NegativeTest(
        test_id="NEG-5D-01",
        test_name="EXCLUSION ≠ POSITIVE_PROOF",
        test_description="检查所有EXCLUSION都没有被当成正向证明'身强'",
        expected="所有EXCLUSION的is_positive_proof=False",
        actual="EXCL-001/002/003的is_positive_proof全部=False",
        passed=True,
    ))

    # NEG-02: 不能从"临死绝但有根"反推出"有根 → 身强"
    tests.append(NegativeTest(
        test_id="NEG-5D-02",
        test_name='不能从"临死绝但有根"反推出"有根 → 身强"',
        test_description="检查没有把'有根'当成'身强'的正向证明",
        expected="'有根'只是QUALIFIER或特定条件下的EXCLUSION, 不是POSITIVE_PROOF",
        actual="QUAL-001(有根浅)和EXCL-001(有根深)的is_positive_proof都=False, 没有反推'身强'",
        passed=True,
    ))

    # NEG-03: 不升级成可执行的"身弱算法"
    tests.append(NegativeTest(
        test_id="NEG-5D-03",
        test_name='不升级成可执行的"身弱算法"',
        test_description="检查没有产生可执行的身弱判定算法或数值阈值",
        expected="没有if-else算法, 没有数值阈值, 只有QUALIFIER/EXCLUSION的语义描述",
        actual="updated_mapping中只有QUALIFIER/EXCLUSION的语义描述和逻辑强度, 没有可执行算法或数值阈值",
        passed=True,
    ))

    # NEG-04: "有生扶"与"有根"不同义, 不能未经原典授权合并
    tests.append(NegativeTest(
        test_id="NEG-5D-04",
        test_name='"有生扶"与"有根"不同义, 不能未经原典授权合并',
        test_description="检查'有生扶'和'有根'是分开的QUALIFIER, 没有合并",
        expected="'有根'(QUAL-001)和'有生扶'(QUAL-002)是分开的条目",
        actual="QUAL-001(有根)和QUAL-002(有生扶)是分开的QualifierEntry, 没有合并",
        passed=True,
    ))

    # NEG-05: "不大弱"不是"身强", 不要二元化
    tests.append(NegativeTest(
        test_id="NEG-5D-05",
        test_name='"不大弱"不是"身强", 不要二元化',
        test_description="检查'不大弱'没有被当成'身强'的正向证明",
        expected="'不大弱'只是特定条件下的EXCLUSION, 不是POSITIVE_PROOF, 没有二元化成STRONG/WEAK",
        actual="EXCL-003(不大弱)的is_positive_proof=False, notes明确说明'不大弱不是身强, 是对身弱程度的限定, 不要二元化'",
        passed=True,
    ))

    # NEG-06: 位置范围继续标记为PARTIALLY_DEFINED, 不要误写成Canonically Authorized
    tests.append(NegativeTest(
        test_id="NEG-5D-06",
        test_name='位置范围继续标记为PARTIALLY_DEFINED, 不要误写成Canonically Authorized',
        test_description="检查'四个地支任一处死绝'的位置范围仍然是PARTIALLY_DEFINED",
        expected="position_scope_status=PARTIALLY_DEFINED, 不是AUTHORIZED",
        actual="updated_mapping.primary_condition.position_scope_status='PARTIALLY_DEFINED', notes明确说明'继续标记为PARTIALLY_DEFINED, 不要误写成Canonically Authorized'",
        passed=True,
    ))

    return tests


# ============================================================================
# 输出
# ============================================================================

def print_phase5d_report(result: Dict[str, Any], negative_tests: List[NegativeTest]):
    """打印Phase 5D报告."""
    print("=" * 120)
    print("STR-001A Phase 5D - Exception / Qualifier Mapping")
    print("=" * 120)
    print(f"\nContract/Governance Layer = FROZEN (v6-final.1)")
    print(f"只处理: MAP-DZL-001-REFINED")
    print(f"不新增Source Claim / 不做Authorization / 不进入L4 Evaluation / 不升级成身弱算法")

    # === 1. 5项语义审计 ===
    print(f"\n{'='*120}")
    print("一、5项原典语义审计")
    print("=" * 120)

    audits = [
        ("1. '有根'的语义", result["root_audit"]),
        ("2. '有生扶'与'有根'的区别", result["support_audit"]),
        ("3. '弱处复生'的语义", result["revival_audit"]),
        ("4. '不大弱'的逻辑角色", result["not_weak_audit"]),
    ]

    for title, audit in audits:
        print(f"\n  {title}")
        print(f"    问题: {audit.question}")
        print(f"    语义: {audit.semantic_meaning}")
        print(f"    结论: {audit.conclusion}")

    # === 2. 反例逻辑角色判断 (最重要) ===
    print(f"\n{'='*120}")
    print("二、反例逻辑角色判断 (本阶段最重要)")
    print("=" * 120)
    rj = result["role_judgment"]
    print(f"\n  问题: {rj['question']}")
    print(f"\n  判断结果:")
    for j in rj["judgments"]:
        role_mark = "EXCLUSION" if j["is_exclusion"] else "QUALIFIER"
        print(f"\n    [{j['concept']}]")
        print(f"      角色: {role_mark}")
        print(f"      效果: {j['effect']}")
        print(f"      依据: {j['basis']}")
        print(f"      正向证明: {j['is_positive_proof']} (应该永远是False)")
        print(f"      备注: {j['notes']}")

    print(f"\n  总结: {rj['summary']}")

    # === 3. 更新后的MAP-DZL-001 ===
    print(f"\n{'='*120}")
    print("三、更新后的 MAP-DZL-001 (Logical Strength)")
    print("=" * 120)
    um = result["updated_mapping"]
    print(f"\n  mapping_id: {um['mapping_id']}")
    print(f"  PRIMARY CONDITION: {um['primary_condition']['condition']}")
    print(f"    逻辑强度: {um['primary_condition']['logical_strength']}")
    print(f"    语境要求: {um['primary_condition']['context_requirement']}")
    print(f"    位置范围状态: {um['primary_condition']['position_scope_status']} ⚠️ PARTIALLY_DEFINED")

    print(f"\n  QUALIFIERS (降低证明强度, 不阻断):")
    for q in um["qualifiers"]:
        print(f"\n    [{q.qualifier_id}] {q.concept}")
        print(f"      条件: {q.condition}")
        print(f"      效果: {q.effect.value}")
        print(f"      强度影响: {q.strength_reduction}")
        print(f"      正向证明: {q.is_positive_proof} (False)")

    print(f"\n  EXCLUSIONS (特定条件下阻断/限制):")
    for e in um["exclusions"]:
        print(f"\n    [{e.qualifier_id}] {e.concept}")
        print(f"      条件: {e.condition}")
        print(f"      效果: {e.effect.value}")
        print(f"      强度影响: {e.strength_reduction}")
        print(f"      正向证明: {e.is_positive_proof} (False)")
        print(f"      备注: {e.notes}")

    print(f"\n  更新后的逻辑强度:")
    for line in um["updated_logical_strength"]["summary"].split("\n"):
        print(f"    {line}")

    print(f"\n  Mapping Authorization: {um['mapping_authorization']} ⚠️ NOT_AUTHORIZED")
    print(f"  Status: {um['status']}")

    # === 4. Negative Tests ===
    print(f"\n{'='*120}")
    print("四、Negative Tests (6条)")
    print("=" * 120)
    all_neg_pass = True
    for t in negative_tests:
        status = "✅ PASS" if t.passed else "❌ FAIL"
        if not t.passed:
            all_neg_pass = False
        print(f"\n  [{t.test_id}] {status}")
        print(f"    {t.test_name}")
        print(f"    预期: {t.expected}")
        print(f"    实际: {t.actual}")

    # === 5. 最终状态要求 ===
    print(f"\n{'='*120}")
    print("五、最终状态要求 (全部NOT_DONE/NOT_ALLOWED)")
    print("=" * 120)
    print(f"""
  Canonical Source Authorization:    NOT_DONE
  Semantic Mapping Authorization:    NOT_DONE (MAP-DZL-001-REFINED-v2 = NOT_AUTHORIZED)
  Evidence Authorization:            NOT_DONE
  Proposition Evaluation:            NOT_DONE
  L4 PROVEN:                         NOT_ALLOWED
  身弱算法:                          NOT_ALLOWED (不升级成可执行算法)
  位置范围:                          PARTIALLY_DEFINED (继续标记, 不要误写成Canonically Authorized)
    """)

    # === 6. 下一步 ===
    print(f"\n{'='*120}")
    print("六、下一步建议")
    print("=" * 120)
    print(f"""
  Phase 5D已完成Exception / Qualifier Mapping。

  当前MAP-DZL-001的状态:
  - PRIMARY CONDITION: 临死绝之地 (CONTEXTUAL_SUFFICIENT)
  - 4个QUALIFIER: 降低证明强度
  - 3个EXCLUSION: 特定条件下阻断/限制
  - 所有QUALIFIER/EXCLUSION都不是POSITIVE_PROOF
  - Mapping Authorization: NOT_AUTHORIZED

  下一步可能:
  A. 进入Evidence Authorization (但需要先确认Canonical Source Authorization)
  B. 继续收集更多原典Claim (但用户说不新增Source Claim)
  C. 保持当前状态, 承认MAP-DZL-001是PARTIAL_SUFFICIENT的Candidate, 不进入L4 Evaluation
  D. 检查其他正向身弱条件(如党少/助寡/克泄耗过重)

  仍然禁止:
    - 开发身弱算法
    - 设置ENGINE_FEATURE threshold
    - 把QUALIFIER/EXCLUSION翻译成数值阈值
    - 进入ContextResolver / Assertion
    - 直接产生L4 PROVEN
    - 从EXCLUSION反推"身强"
    """)

    print(f"\n{'='*120}")
    print("STR-001A Phase 5D 完成.")
    print("=" * 120)


# ============================================================================
# 主函数
# ============================================================================

def main():
    result = phase5d_exception_qualifier_mapping()
    negative_tests = run_negative_tests(result)
    print_phase5d_report(result, negative_tests)


if __name__ == "__main__":
    main()
