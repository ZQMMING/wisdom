"""
STR-001A Phase 6.1 Layer 4 — 修正覆盖层审计

执行边界:
- 决定普通强弱基线什么时候可以被覆盖、修正或判定为无法解析
- 每条关系按12字段模板输出
- 5个硬约束严格执行:
  ① 不允许把"气势"变成五行计分
  ② M1必须寻找"失令而强/得令而弱"的具体原典条件，不能自行补公式
  ③ M2必须区分"月令重要"与"月令可以被全局推翻"
  ④ M3调候必须保持独立维度
  ⑤ M4是最高危险项，必须审成格/破格条件

4个关系:
M1: 月令 + 全局 → 旺衰修正
M2: 全局气势 → 月令修正
M3: 调候 → 强弱
M4: 特殊格局 → 普通模型覆盖 (最高危险项)

12字段模板:
RELATION_ID, SOURCE_CLAIM, L1_FACTS, PRECONDITIONS, RELATION,
EFFECT, CONCLUSION, QUALIFIERS, COUNTER_EXAMPLES, SOURCE_STATUS,
CANONICAL_AUTHORITY, IMPLEMENTATION_PERMISSION
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class SourceStatus(str, Enum):
    SOURCE_SUPPORTED = "SOURCE_SUPPORTED"
    SOURCE_SUPPORTED_WITH_QUALIFIER = "SOURCE_SUPPORTED_WITH_QUALIFIER"
    SOURCE_MAPPED_NON_PROOF = "SOURCE_MAPPED_NON_PROOF"
    INSUFFICIENT_SOURCE = "INSUFFICIENT_SOURCE"
    SOURCE_CONTESTED = "SOURCE_CONTESTED"


@dataclass
class OverrideAudit:
    """修正覆盖层审计模板 (12字段)"""
    relation_id: str
    source_claim: str             # 原典说了什么
    l1_facts: List[str]           # L1事实
    preconditions: str            # 前置条件
    relation: str                 # 关系描述
    effect: str                   # 作用效果
    conclusion: str               # 结论
    qualifiers: str               # 限定/修饰
    counter_examples: str         # 反例
    source_status: SourceStatus   # 原典状态
    canonical_authority: str      # Canonical授权 (原典说了什么)
    implementation_permission: str # 引擎因此允许做什么
    risk_level: str = ""
    key_finding: str = ""

    def to_dict(self):
        return {
            "RELATION_ID": self.relation_id,
            "SOURCE_CLAIM": self.source_claim,
            "L1_FACTS": self.l1_facts,
            "PRECONDITIONS": self.preconditions,
            "RELATION": self.relation,
            "EFFECT": self.effect,
            "CONCLUSION": self.conclusion,
            "QUALIFIERS": self.qualifiers,
            "COUNTER_EXAMPLES": self.counter_examples,
            "SOURCE_STATUS": self.source_status.value,
            "CANONICAL_AUTHORITY": self.canonical_authority,
            "IMPLEMENTATION_PERMISSION": self.implementation_permission,
            "RISK_LEVEL": self.risk_level,
            "KEY_FINDING": self.key_finding,
        }


audits: List[OverrideAudit] = []


# ============================================================
# M1: 月令 + 全局 → 旺衰修正
# ============================================================

audits.append(OverrideAudit(
    relation_id="M1",
    source_claim=(
        "《子平真诠》：'大致得时为旺，失时为衰；党众为强，助寡为弱。故有虽旺而弱者，亦有虽衰而强者。' "
        "《子平真诠》：'甲乙木生申酉月...比印重叠...通根比印，即为党众，虽失时而不弱。' "
        "《子平真诠》：'甲乙木生寅卯月...火党众...木泄气太重...虽秉令而不强。' "
        "《滴天髓》：'得时俱为旺论，失令便作衰看，虽是至理，亦死法也。' "
        "《滴天髓》：'春木虽强...金太重而木亦危；秋木虽弱...木根深而木亦强。'"
    ),
    l1_facts=[
        "month_branch (月令)",
        "day_master (日主)",
        "de_shi_status (得时/失时)",
        "tonggen_status (通根状态)",
        "companion_stems (比劫)",
        "resource_stems (印绶)",
        "opposition_stems (官杀/食伤/财)",
        "dangzhong_status (党众状态, 来自C1)",
    ],
    preconditions=(
        "(1)月令旺衰基线已确定(得时=旺, 失时=衰); "
        "(2)全局结构已评估(通根、比劫、印绶、官杀、食伤、财); "
        "(3)需要判断全局结构是否修正月令旺衰基线。"
    ),
    relation=(
        "月令建立旺衰基线(得时→旺, 失时→衰)，全局结构(党众/助寡、通根、克泄耗)可以修正这个基线。 "
        "具体表现为：失时+党众+通根→虽衰而强(失时而不弱)；得时+泄气太重/克泄耗过重→虽旺而弱(得时而不强)。"
    ),
    effect=(
        "全局结构可以修正月令旺衰基线，产生'虽旺而弱'和'虽衰而强'的组合状态。 "
        "但这是旺衰维度和强弱维度的分离，不是月令基线被'推翻'——月令仍然是旺/衰，只是强弱维度独立判断。"
    ),
    conclusion=(
        "原典明确授权了'月令+全局→旺衰修正'的关系，但修正的具体条件是质性的，不是可计算的公式。 "
        "原典给出了两个典型案例：(1)失时+比印重叠+通根→党众→虽失时而不弱；(2)得时+火党众+木泄气太重→虽秉令而不强。 "
        "但原典没有给出'什么程度的比印重叠才算党众'、'什么程度的泄气才算太重'的可计算标准。 "
        "这些标准需要依赖C1(党众定义)和C3(党众→强)的质性判断，不能自行补数值公式。"
    ),
    qualifiers=(
        "(1)【硬约束②】必须寻找具体原典条件，不能自行补公式。原典给出的条件是质性的(比印重叠、通根、泄气太重)，不是数值阈值； "
        "(2)修正的是强弱维度，不是旺衰维度——月令仍然是旺/衰，强弱独立判断； "
        "(3)'虽旺而弱'=得时(旺)+助寡(弱)，不是月令被推翻； "
        "(4)'虽衰而强'=失时(衰)+党众(强)，不是月令被推翻； "
        "(5)原典用了'大致'，意味着这是一般规律，可能存在例外； "
        "(6)禁止：把'比印重叠'数值化为count>=2，把'泄气太重'数值化为output_ratio>X。"
    ),
    counter_examples=(
        "(1)得时但助寡→虽旺而弱(月令旺但强弱弱)； "
        "(2)失时但党众→虽衰而强(月令衰但强弱强)； "
        "(3)原典未给出'党众但仍弱'的直接反例(党众→强是C3的一般规律)； "
        "(4)特殊格局可能完全不适用普通旺衰→强弱路径(见M4)。"
    ),
    source_status=SourceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
    canonical_authority=(
        "原典明确授权：月令建立旺衰基线，全局结构(党众/助寡、通根、克泄耗)可以修正强弱维度， "
        "产生'虽旺而弱、虽衰而强'的组合状态。原典给出了两个典型案例的质性条件。 "
        "但原典没有给出可计算的数值公式，修正条件是质性的。"
    ),
    implementation_permission=(
        "引擎允许：(1)月令建立旺衰基线(得时→旺, 失时→衰)； "
        "(2)全局结构按C1/C2/C3的质性标准判断党众/助寡→强/弱； "
        "(3)输出二维状态：wangshuai(旺/衰) + qiangruo(强/弱/UNRESOLVED)，二者独立； "
        "(4)当克泄耗过重或条件不明确时，qiangruo标UNRESOLVED，不强行计算。 "
        "引擎不允许：(1)自行补数值公式(如比劫count>=2=党众)； "
        "(2)把旺衰和强弱混为一谈；(3)把'修正'理解为'月令被推翻'。"
    ),
    risk_level="MEDIUM",
    key_finding=(
        "M1的关键发现：月令+全局修正的是强弱维度，不是旺衰维度。 "
        "'虽旺而弱、虽衰而强'是二维分离，不是月令被推翻。 "
        "修正条件是质性的(比印重叠、通根、泄气太重)，原典未给数值公式，不能自行补。"
    ),
))


# ============================================================
# M2: 全局气势 → 月令修正
# ============================================================

audits.append(OverrideAudit(
    relation_id="M2",
    source_claim=(
        "《滴天髓》：'得时俱为旺论，失令便作衰看，虽是至理，亦死法也。' "
        "《滴天髓》：'旺中有衰者存，不可损也；衰中有旺者存，不可益也。' "
        "《滴天髓》：'不可以一端论也，要在扶之抑之得其宜。' "
        "《子平真诠》：月令虽然重要，但年月日时都有损益之权。 "
        "《穷通宝鉴》评：'滴天髓言其理而不言其用，穷通宝监言其用而不言其理。'"
    ),
    l1_facts=[
        "month_branch (月令)",
        "all_branches (四支)",
        "all_stems (四天干)",
        "hidden_stems (藏干)",
        "five_element_distribution (五行分布)",
        "global_structure (全局结构)",
    ],
    preconditions=(
        "(1)月令旺衰基线已确定；(2)全局五行分布和结构已评估； "
        "(3)需要判断全局气势是否修正月令基线，以及修正到什么程度。"
    ),
    relation=(
        "月令是第一观察入口(提纲)，但不是绝对否决权。全局气势(年月日时的整体五行分布和结构) "
        "可以修正月令基线。但滴天髓'言其理而不言其用'——它告诉我们不能执一而论，但没有给出 "
        "可计算的修正规则。"
    ),
    effect=(
        "全局气势可以修正月令基线，但修正的程度和条件原典未给出可计算的规则。 "
        "滴天髓提供的是原则性指导('不可以一端论'、'扶之抑之得其宜')，不是具体算法。"
    ),
    conclusion=(
        "原典明确授权了'月令重要但不是绝对'的原则，滴天髓明确批评了'得时俱为旺论，失令便作衰看'的死法。 "
        "但原典没有给出'全局气势在什么条件下可以覆盖月令'的可计算规则。 "
        "滴天髓'言其理而不言其用'——它告诉我们不能执一而论，但没有告诉我们具体怎么计算修正。 "
        "因此，全局气势对月令的修正只能作为原则性指导，不能作为可计算的覆盖规则。 "
        "在引擎中，月令仍然是第一观察入口，全局气势作为QUALIFIER标记，不直接覆盖月令基线。"
    ),
    qualifiers=(
        "(1)【硬约束①】不允许把'气势'变成五行计分。禁止：木3水4火1金0→总体气势分数→修正月令； "
        "(2)【硬约束③】必须区分'月令重要'与'月令可以被全局推翻'。原典支持的是'月令作为第一观察入口，全局结构作为修正'， "
        "不是'某条件下月令失效/被覆盖'； "
        "(3)滴天髓'言其理而不言其用'——原则性指导，不是具体算法； "
        "(4)'旺中有衰者存，不可损也；衰中有旺者存，不可益也'——这是说旺衰中存在反向力量时不能简单损益， "
        "不是说全局气势可以覆盖月令； "
        "(5)禁止：global_qi_score > X → 月令基线被覆盖。"
    ),
    counter_examples=(
        "(1)'得时俱为旺论，失令便作衰看，虽是至理，亦死法也'——滴天髓批评了简单的月令决定论， "
        "但没有给出替代算法； "
        "(2)原典未给出'全局气势在X条件下月令失效'的明确规则； "
        "(3)特殊格局(从格/专旺)可能不适用普通月令逻辑，但这是M4的范围，不是M2。"
    ),
    source_status=SourceStatus.SOURCE_MAPPED_NON_PROOF,
    canonical_authority=(
        "原典明确授权了'月令重要但不是绝对'的原则，滴天髓批评了月令决定论的死法。 "
        "但原典没有给出'全局气势在什么条件下可以覆盖月令'的可计算规则。 "
        "滴天髓提供的是原则性指导，不是具体算法。"
    ),
    implementation_permission=(
        "引擎允许：(1)月令作为第一观察入口建立旺衰基线； "
        "(2)全局气势作为QUALIFIER标记(如'全局金太重'、'木根深')，提示可能存在修正； "
        "(3)当全局气势与月令明显冲突时，qiangruo标UNRESOLVED或需要人工判断。 "
        "引擎不允许：(1)把全局气势数值化为分数； "
        "(2)global_qi_score > X → 月令基线被覆盖； "
        "(3)把'修正'理解为'月令被推翻'。"
    ),
    risk_level="HIGH",
    key_finding=(
        "M2的关键发现：滴天髓'言其理而不言其用'——它告诉我们不能执一而论，但没有给出可计算的修正规则。 "
        "全局气势对月令的修正只能作为原则性指导和QUALIFIER标记，不能作为可计算的覆盖规则。 "
        "月令仍然是第一观察入口，不是绝对否决权，但也不能被全局气势简单覆盖。"
    ),
))


# ============================================================
# M3: 调候 → 强弱
# ============================================================

audits.append(OverrideAudit(
    relation_id="M3",
    source_claim=(
        "《穷通宝鉴》120条调候用神表：如乙木戌月'丙火为主，癸辛为佐'。 "
        "《穷通宝鉴》评：'滴天髓言其理而不言其用，穷通宝监言其用而不言其理。' "
        "穷通宝鉴主要提供月令+五行季节环境+寒暖燥湿+具体干支条件。"
    ),
    l1_facts=[
        "day_master (日主)",
        "month_branch (月令)",
        "seasonal_context (季节环境: 寒暖燥湿)",
        "tiaohou_primary (调候主用神)",
        "tiaohou_assistant (调候佐用神)",
    ],
    preconditions=(
        "(1)日主和月令已确定；(2)查穷通宝鉴调候用神表确定调候主/佐用神； "
        "(3)需要判断调候是否影响强弱判断。"
    ),
    relation=(
        "调候是独立维度，根据日主+月令确定调候用神(寒暖燥湿)。调候≠旺衰，调候≠强弱。 "
        "调候不直接改变强弱状态，它是与强弱并行的独立维度。"
    ),
    effect=(
        "调候提供季节环境的用神建议，指导用神选取和后续解释。调候不直接改变旺衰/强弱状态。 "
        "Strength State(强/弱/UNRESOLVED)和Seasonal Condition(primary=丙, assistant=癸辛)可以同时存在，但不能互相偷渡。"
    ),
    conclusion=(
        "原典(穷通宝鉴)明确授权了调候作为独立维度的存在，但原典没有授权'调候→强弱'的因果链。 "
        "穷通宝鉴'言其用而不言其理'——它提供具体的调候用神建议，但没有讨论调候如何影响强弱。 "
        "调候和强弱是两个独立维度：Strength State和Seasonal Condition可以同时存在，但不能互相推导。 "
        "特别是，不能出现'乙木戌月→穷通宝鉴丙火为主→所以乙木身弱'的非法推导。"
    ),
    qualifiers=(
        "(1)【硬约束④】调候必须保持独立维度。禁止：乙木戌月→穷通宝鉴丙火为主→所以乙木身弱； "
        "(2)调候≠旺衰，调候≠强弱，是独立维度； "
        "(3)穷通宝鉴120条调候用神表是候选知识/索引，不是直接授权，需要回到原典验证上下文和条件； "
        "(4)调候影响后续解释和用神选取，但不直接改变旺衰/强弱状态； "
        "(5)Strength State和Seasonal Condition并行存在，不能互相偷渡； "
        "(6)禁止：tiaohou_primary=X → day_master_strength=WEAK。"
    ),
    counter_examples=(
        "(1)同一调候条件下，日主可能强也可能弱——调候不决定强弱； "
        "(2)穷通宝鉴的调候用神建议是针对季节环境的，不是针对日主强弱的； "
        "(3)原典未给出'调候条件X→强弱Y'的明确规则。"
    ),
    source_status=SourceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
    canonical_authority=(
        "原典(穷通宝鉴)明确授权了调候作为独立维度的存在，提供120条调候用神表。 "
        "但原典没有授权'调候→强弱'的因果链。调候和强弱是两个独立维度。"
    ),
    implementation_permission=(
        "引擎允许：(1)根据日主+月令查穷通宝鉴调候用神表，确定tiaohou_primary和tiaohou_assistant； "
        "(2)调候作为独立字段seasonal_remedy，与wangshuai/qiangruo并行； "
        "(3)调候影响后续用神选取和解释，但不参与强弱计算。 "
        "引擎不允许：(1)调候→强弱的因果推导； "
        "(2)tiaohou_primary=X → day_master_strength=WEAK； "
        "(3)把调候混入旺衰/强弱判断。"
    ),
    risk_level="MEDIUM",
    key_finding=(
        "M3的关键发现：调候是独立维度，与强弱并行存在，不能互相推导。 "
        "穷通宝鉴'言其用而不言其理'——提供调候用神建议，但不讨论调候如何影响强弱。 "
        "Strength State和Seasonal Condition是两个独立字段，禁止互相偷渡。"
    ),
))


# ============================================================
# M4: 特殊格局 → 普通模型覆盖 (最高危险项)
# ============================================================

audits.append(OverrideAudit(
    relation_id="M4",
    source_claim=(
        "《子平真诠》：'有弃命从煞者，四柱皆煞，而日主无根，舍而从之，格成大贵。若有伤食...' "
        "《滴天髓》：'旺者宜克，旺极宣泄，弱者宜生，弱极宜克。' "
        "从财/从杀/从儿/专旺(曲直/炎上/稼穑/从革/润下)/化气(甲己化土等)。"
    ),
    l1_facts=[
        "day_master (日主)",
        "month_branch (月令)",
        "all_stems (四天干)",
        "all_branches (四支)",
        "hidden_stems (藏干)",
        "tonggen_status (通根状态)",
        "ten_god_distribution (十神分布)",
        "wangshuai_baseline (旺衰基线)",
        "qiangruo_baseline (强弱基线, 来自C3)",
    ],
    preconditions=(
        "(1)普通旺衰→强弱路径已评估(C3基线)； "
        "(2)检测到特殊格局候选(从财/从杀/从儿/专旺/化气)； "
        "(3)需要判断特殊格局是否满足成格条件，以及是否覆盖普通强弱路径。"
    ),
    relation=(
        "特殊格局(从格/专旺/化气)在满足严格成格条件时，可以退出普通'旺衰→强弱'路径， "
        "采用特殊格局的判断逻辑。但成格条件非常严格，且存在破格条件。 "
        "不能因为发现从格关键词就强制改成从弱。"
    ),
    effect=(
        "特殊格局成格时，普通强弱路径被覆盖，采用特殊格局逻辑。 "
        "如从杀格：日主无根，四柱皆煞，舍命从煞——此时'身弱'的普通判断不适用， "
        "因为日主已经'舍命从煞'，强弱概念被格局概念替代。 "
        "但破格时，退回普通强弱路径。"
    ),
    conclusion=(
        "原典明确授权了特殊格局的存在，并给出了部分成格条件(如从杀格'四柱皆煞而日主无根，舍而从之')。 "
        "滴天髓'弱极宜克'也暗示了极弱时普通生扶逻辑不适用。 "
        "但原典对各类特殊格局的成格/破格条件论述不统一，且很多条件是质性的，不是可计算的。 "
        "特别是：(1)从财/从杀/从儿的'成势'标准原典未数值化； "
        "(2)专旺格的'成方'条件需要三会方或三合局； "
        "(3)化气格的化神条件非常严格(化神得令得地，无克制)； "
        "(4)破格条件(如从杀格见伤食)原典有提及但不完整。 "
        "因此，特殊格局的成格判断需要严格的条件验证，不能简单检测关键词就判定成格。 "
        "在条件不明确时，应标UNRESOLVED，退回普通路径或需要人工判断。"
    ),
    qualifiers=(
        "(1)【硬约束⑤】M4是最高危险项。特殊格局不是'发现关键词→强制改成从弱'，必须审成格/破格条件； "
        "(2)成格条件非常严格，且存在破格条件。不能因为发现从格关键词就判定成格； "
        "(3)从杀格条件：'四柱皆煞而日主无根，舍而从之'——需要日主无根+四柱皆煞，不是简单的官杀多； "
        "(4)从财/从儿的成格条件原典论述不完整，需要更多原典证据； "
        "(5)专旺格需要成方(三会方)或成局(三合局)，且日主专旺无克泄； "
        "(6)化气格需要化神得令得地，无克制，条件极严； "
        "(7)破格条件：从杀格见伤食破格，从财格见比劫破格等——原典有提及但不完整； "
        "(8)'弱极宜克'是滴天髓原则，不是具体算法——极弱的标准原典未数值化； "
        "(9)禁止：detect_cong_keyword() → force_cong_weak()； "
        "(10)禁止：officer_killer_count >= 3 → 从杀格成格。"
    ),
    counter_examples=(
        "(1)从杀格见伤食→破格，退回普通路径； "
        "(2)从财格见比劫→破格，退回普通路径； "
        "(3)日主有微根→不能从(从格需要日主无根)； "
        "(4)官杀多但日主有根有印→不是从杀格，仍按普通路径； "
        "(5)原典未给出各类从格的完整成格/破格条件，很多需要人工判断。"
    ),
    source_status=SourceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
    canonical_authority=(
        "原典明确授权了特殊格局的存在，并给出了部分成格条件(如从杀格'四柱皆煞而日主无根，舍而从之')。 "
        "滴天髓'弱极宜克'也暗示了极弱时普通生扶逻辑不适用。 "
        "但原典对各类特殊格局的成格/破格条件论述不统一，且很多条件是质性的，不是可计算的。 "
        "特殊格局成格时可以覆盖普通强弱路径，但成格判断需要严格条件验证。"
    ),
    implementation_permission=(
        "引擎允许：(1)检测特殊格局候选(从财/从杀/从儿/专旺/化气)； "
        "(2)按原典条件严格验证成格/破格； "
        "(3)成格时，标记special_pattern=CONG_SHA/CONG_CAI等，普通强弱路径被覆盖，采用特殊格局逻辑； "
        "(4)破格或条件不明确时，退回普通路径或标UNRESOLVED； "
        "(5)从杀格的基础条件可实现：日主无根 AND 官杀成势(质性判断)。 "
        "引擎不允许：(1)检测关键词就强制判定成格； "
        "(2)officer_killer_count >= 3 → 从杀格； "
        "(3)把特殊格局作为'万能例外'逃避普通路径的判断； "
        "(4)在成格条件不明确时强行判定成格。"
    ),
    risk_level="CRITICAL (最高危险项)",
    key_finding=(
        "M4的关键发现：特殊格局成格时可以覆盖普通强弱路径，但成格条件非常严格。 "
        "从杀格'四柱皆煞而日主无根，舍而从之'——需要日主无根+四柱皆煞，不是简单的官杀多。 "
        "滴天髓'弱极宜克'是原则不是算法。各类从格的成格/破格条件原典论述不完整， "
        "很多需要人工判断。在条件不明确时标UNRESOLVED，不能强行判定成格。 "
        "特殊格局不能成为系统的'万能例外'。"
    ),
))


# ============================================================
# 主执行
# ============================================================

def main():
    print("=" * 100)
    print("STR-001A Phase 6.1 Layer 4 — 修正覆盖层审计")
    print("=" * 100)
    print()
    print("执行边界:")
    print("  - 决定普通强弱基线什么时候可以被覆盖、修正或判定为无法解析")
    print("  - 每条关系按12字段模板输出")
    print("  - 5个硬约束严格执行")
    print("  - M4是最高危险项")
    print()

    for audit in audits:
        print(f"\n{'='*100}")
        print(f"【{audit.relation_id}】{audit.relation[:50]}...")
        print(f"风险级别: {audit.risk_level}")
        print(f"{'='*100}")
        print(f"  SOURCE_CLAIM: {audit.source_claim[:300]}{'...' if len(audit.source_claim) > 300 else ''}")
        print(f"  L1_FACTS: {', '.join(audit.l1_facts)}")
        print(f"  PRECONDITIONS: {audit.preconditions}")
        print(f"  RELATION: {audit.relation}")
        print(f"  EFFECT: {audit.effect}")
        print(f"  CONCLUSION: {audit.conclusion}")
        print(f"  QUALIFIERS: {audit.qualifiers}")
        print(f"  COUNTER_EXAMPLES: {audit.counter_examples}")
        print(f"  SOURCE_STATUS: {audit.source_status.value}")
        print(f"  CANONICAL_AUTHORITY: {audit.canonical_authority}")
        print(f"  IMPLEMENTATION_PERMISSION: {audit.implementation_permission}")
        print(f"  KEY_FINDING: {audit.key_finding}")

    # 汇总
    print("\n" + "=" * 100)
    print("Layer 4 审计汇总")
    print("=" * 100)
    print(f"\n  {'关系ID':<8} {'修正关系':<30} {'原典状态':<35} {'风险':<15}")
    print(f"  {'─'*8} {'─'*30} {'─'*35} {'─'*15}")
    for audit in audits:
        print(f"  {audit.relation_id:<8} {audit.relation[:28]:<30} {audit.source_status.value:<35} {audit.risk_level[:13]:<15}")

    print(f"\n  统计:")
    for ss in SourceStatus:
        count = sum(1 for a in audits if a.source_status == ss)
        print(f"    {ss.value}: {count}")
    print(f"    总计: {len(audits)}个")

    print(f"\n  5个硬约束执行确认:")
    print(f"    ① 不允许把'气势'变成五行计分: M2已确认禁止global_qi_score")
    print(f"    ② M1必须寻找具体原典条件: M1已确认原典条件是质性的, 未自行补公式")
    print(f"    ③ M2区分'月令重要'与'月令可以被全局推翻': M2已确认原典支持'第一观察入口+修正', 不支持'覆盖'")
    print(f"    ④ M3调候保持独立维度: M3已确认调候≠强弱, 禁止互相偷渡")
    print(f"    ⑤ M4最高危险项: M4已确认必须审成格/破格条件, 禁止关键词→强制成格")

    print(f"\n  关键结论:")
    print(f"    M1 月令+全局→旺衰修正: SOURCE_SUPPORTED_WITH_QUALIFIER")
    print(f"       - 修正的是强弱维度, 不是旺衰维度")
    print(f"       - '虽旺而弱、虽衰而强'是二维分离, 不是月令被推翻")
    print(f"       - 修正条件是质性的, 原典未给数值公式")
    print(f"    M2 全局气势→月令修正: SOURCE_MAPPED_NON_PROOF")
    print(f"       - 滴天髓'言其理而不言其用'——原则性指导, 不是具体算法")
    print(f"       - 全局气势作为QUALIFIER标记, 不直接覆盖月令基线")
    print(f"       - 月令是第一观察入口, 不是绝对否决权, 但也不能被简单覆盖")
    print(f"    M3 调候→强弱: SOURCE_SUPPORTED_WITH_QUALIFIER")
    print(f"       - 调候是独立维度, 与强弱并行存在, 不能互相推导")
    print(f"       - 穷通宝鉴'言其用而不言其理'")
    print(f"       - Strength State和Seasonal Condition是两个独立字段")
    print(f"    M4 特殊格局→普通模型覆盖: SOURCE_SUPPORTED_WITH_QUALIFIER (最高危险项)")
    print(f"       - 成格时可以覆盖普通强弱路径, 但成格条件非常严格")
    print(f"       - 从杀格'四柱皆煞而日主无根, 舍而从之'")
    print(f"       - 滴天髓'弱极宜克'是原则不是算法")
    print(f"       - 各类从格的成格/破格条件原典论述不完整")
    print(f"       - 条件不明确时标UNRESOLVED, 不能强行判定成格")
    print(f"       - 特殊格局不能成为系统的'万能例外'")

    print(f"\n  对Canonical State Resolver的最终影响:")
    print(f"    1. 二维输出: wangshuai(旺/衰) + qiangruo(强/弱/UNRESOLVED), 二者独立")
    print(f"    2. 月令是第一观察入口, 全局气势作为QUALIFIER, 不直接覆盖")
    print(f"    3. 调候作为独立字段seasonal_remedy, 与强弱并行")
    print(f"    4. 特殊格局候选检测, 严格成格/破格验证, 成格覆盖普通路径, 破格退回")
    print(f"    5. 克泄耗过重、条件不明确、特殊格局存疑时, qiangruo标UNRESOLVED")
    print(f"    6. 禁止: 数值评分、五行计分、关键词→强制成格、调候→强弱推导")

    print("\n" + "=" * 100)
    print("Layer 4 修正覆盖层审计完成。")
    print("Phase 6.1 Relationship Audit (Layer 1-4) 全部完成。")
    print("下一步: Phase 6.1 全局 Authority Matrix 汇总, 然后拿1983命例跑Canonical State Resolver。")
    print("=" * 100)


if __name__ == "__main__":
    main()
