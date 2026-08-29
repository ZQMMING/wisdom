"""
STR-001A P6.4-G-R ASSERT-006 Cross-Classical Effect Provenance Audit

目标: 在五部经典及其他本地Canonical Corpus中搜索「富贵自天来」及相关组合,
      建立Effect Provenance Matrix, 彻底查清「富贵自天来」到底有没有原典依据。

搜索范围:
  1. 「富贵自天来」精确匹配
  2. 「食神生财」+「富贵」
  3. 「食神」+「富贵」
  4. 「食神」+「财」+「贵」

最终只允许三种结果:
  - 找到精确原文, 且明确把食神生财与富贵结果连接 → 继续审计
  - 找到相近语义, 但条件不同 → SOURCE_SUPPORTED_WITH_QUALIFIER
  - 完全找不到直接授权 → EFFECT_NOT_AUTHORIZED

尤其不能因为「食神干旺，胜似财官」就自动推导成「食神生财→富贵自天来」。
"""

import sys
sys.path.insert(0, r"D:\shuntian\backend\scripts")

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


# ============================================================
# Effect Provenance Matrix
# ============================================================

@dataclass
class ProvenanceRecord:
    """Effect溯源记录"""
    record_id: str
    search_term: str
    found: bool
    book: str = ""
    location: str = ""
    exact_quote: str = ""
    context_before: str = ""
    context_after: str = ""
    full_context: str = ""
    relation_to_assert006: str = ""  # DIRECT / RELATED / UNRELATED
    analysis: str = ""
    authorization_level: str = ""  # DIRECT_AUTHORIZED / QUALIFIED / NOT_AUTHORIZED / UNRESOLVED


# ============================================================
# 搜索结果1: 「富贵自天来」精确匹配
# ============================================================

PROVENANCE_FUGUI_ZI_TIAN_LAI = [
    ProvenanceRecord(
        record_id="P-FGTL-001",
        search_term="富贵自天来",
        found=True,
        book="《三命通会》",
        location="第1161段 (行4661)",
        exact_quote="(早年且掩埋/富贵自天来)",
        context_before="丁亥日乙巳时时日并冲忧伤妻子巳酉丑申子辰金水二局财官得用以富贵论(壬辰王爌侍郎/甲辰)(丁亥乞丐/甲辰)(偏印破财局/运行官禄地)",
        context_after="丁日巳时怕虎刑财官运歩始能通好意人情反恶意先难后易乐从容丁日时临乙巳破财倒食难通双亲雁侣且和平妻子无嗔无闷君子文学秀",
        full_context="""丁亥日乙巳时时日并冲忧伤妻子巳酉丑申子辰金水二局财官得用以富贵论
(壬辰王爌侍郎/甲辰)(丁亥乞丐/甲辰)(偏印破财局/运行官禄地)(早年且掩埋/富贵自天来)
丁日巳时怕虎刑财官运歩始能通好意人情反恶意先难后易乐从容""",
        relation_to_assert006="UNRELATED",
        analysis="""「富贵自天来」出现在括号注释中, 是对「丁亥日乙巳时」这个特定日柱时柱组合的补充说明。
上下文是: 丁亥日乙巳时 + 时日并冲 + 巳酉丑申子辰金水二局 + 财官得用以富贵论 + 偏印破财局 + 运行官禄地 + 早年且掩埋 → 富贵自天来。
这与「食神生财」完全无关。这里的富贵来自「金水二局+财官得用+运行官禄地」, 不是食神生财。""",
        authorization_level="NOT_AUTHORIZED",
    ),
    ProvenanceRecord(
        record_id="P-FGTL-002",
        search_term="富贵自天来",
        found=True,
        book="《三命通会》",
        location="第1345段 (行5399)",
        exact_quote="(无官亦有财/富贵自天来)",
        context_before="壬戌日壬寅时巳月偏官格名标金榜身坐玉堂纯子三品寅卯行北运风宪又六壬日见壬寅时名白太虚贵不久盛而祸生(癸亥闵如霖侍郎/辛酉)(甲子京卿/丙子)(壬寅大参/戊申)(壬戌同知/壬子)(壬申宪副/壬子)(戊寅易应昌掌院/壬戌)(庚戌御史/乙酉)(壬日壬时局/寅辰重叠见)",
        context_after="六壬逢虎是浮沤富贵功名莫强求有印有官为上格骤然财禄免忧愁壬日壬寅时遇比肩相遇食神弟兄雁侣少同群此是生时定分坐局运行官地身强禄位超伦身衰刑害祸相侵衣禄平常之命",
        full_context="""壬戌日壬寅时巳月偏官格名标金榜身坐玉堂纯子三品寅卯行北运风宪
又六壬日见壬寅时名白太虚贵不久盛而祸生
(癸亥闵如霖侍郎/辛酉)(甲子京卿/丙子)(壬寅大参/戊申)(壬戌同知/壬子)(壬申宪副/壬子)(戊寅易应昌掌院/壬戌)(庚戌御史/乙酉)
(壬日壬时局/寅辰重叠见)(无官亦有财/富贵自天来)
六壬逢虎是浮沤富贵功名莫强求有印有官为上格骤然财禄免忧愁""",
        relation_to_assert006="UNRELATED",
        analysis="""「富贵自天来」出现在括号注释中, 是对「六壬日壬寅时」这个特定日柱时柱组合的补充说明。
上下文是: 壬日壬时局 + 寅辰重叠见 + 无官亦有财 → 富贵自天来。
这与「食神生财」完全无关。这里的富贵来自「壬日壬时局+寅辰重叠见+无官亦有财」, 不是食神生财。
注意后面紧接着说「六壬逢虎是浮沤富贵功名莫强求」, 说明这种富贵是不稳定的。""",
        authorization_level="NOT_AUTHORIZED",
    ),
]

# ============================================================
# 搜索结果2: 「食神生财」在五部经典中的出处
# ============================================================

PROVENANCE_SHISHENG_SHENGCAI = [
    ProvenanceRecord(
        record_id="P-SSSC-001",
        search_term="食神生财",
        found=True,
        book="《渊海子平》",
        location="第2430段 (格局列表)",
        exact_quote="食神生财。",
        context_before="食神生旺。",
        context_after="杀化印綬。",
        full_context="""正气官星。
财官两旺。
印綬天德。
独杀有制。
伤官生财。
坐禄逢财。
官星带合。
日贵逢财。
官贵逢官。
官星坐禄。
官星桃花。
食神生旺。
食神生财。
杀化印綬。
二德扶身。
三奇合局。
阳刃有制。
拱禄拱贵。
归禄逢财。""",
        relation_to_assert006="RELATED",
        analysis="""「食神生财」出现在格局列表中, 与「正气官星」「财官两旺」「印绶天德」「独杀有制」「伤官生财」「坐禄逢财」等并列。
这说明「食神生财」首先是一个格局名称, 不是一个简单的断语。
原典没有在这个格局列表中直接说明「食神生财→富贵自天来」。""",
        authorization_level="QUALIFIED",
    ),
    ProvenanceRecord(
        record_id="P-SSSC-002",
        search_term="食神生财",
        found=True,
        book="《子平真诠》",
        location="第113段 (论用神成败救应)",
        exact_quote="食神生财，或食带煞而无财，弃食就煞而透印，食格成也。",
        context_before="何谓成?如官逢财印,又无刑冲破害,官格成也。财生官旺,或财逢食生而身强带比,或财格透印而位置妥贴,两不相克,财格成也。印轻逢煞,或官印双全,或身印两旺而用食伤泄气,或印多逢财而财透根轻,印格成也。",
        context_after="身强七煞逢制,煞格成也。伤官生财,或伤官佩印而伤官旺,印有根,或伤官旺、身主弱而透煞印,或伤官带煞而无财,伤官格成也。",
        full_context="""何谓成?如官逢财印,又无刑冲破害,官格成也。
财生官旺,或财逢食生而身强带比,或财格透印而位置妥贴,两不相克,财格成也。
印轻逢煞,或官印双全,或身印两旺而用食伤泄气,或印多逢财而财透根轻,印格成也。
食神生财，或食带煞而无财，弃食就煞而透印，食格成也。
身强七煞逢制,煞格成也。
伤官生财,或伤官佩印而伤官旺,印有根,或伤官旺、身主弱而透煞印,或伤官带煞而无财,伤官格成也。""",
        relation_to_assert006="RELATED",
        analysis="""「食神生财」在这里是作为「食格成」的条件之一。
原文说: 食神生财, 或食带煞而无财, 弃食就煞而透印, 食格成也。
这说明「食神生财」是食神格成格的条件之一, 不是直接说「食神生财→富贵自天来」。
原典在这里讨论的是格局成败, 不是断语效果。""",
        authorization_level="QUALIFIED",
    ),
    ProvenanceRecord(
        record_id="P-SSSC-003",
        search_term="食神生财",
        found=True,
        book="《子平真诠》",
        location="第109段 (论用神)",
        exact_quote="见财透食神，不以为财逢食生，而以为食神生财，与食神生财同论",
        context_before="今人不知专主提纲,然后将四柱干支,字字统归月令,以观喜忌,甚至见正官佩印,则以为官印双全,与印绶用官者同论",
        context_after="见偏印透食,不以为泄身之秀,而以为枭神夺食,宜用财制,与食神逢枭同论",
        full_context="""今人不知专主提纲,然后将四柱干支,字字统归月令,以观喜忌,
甚至见正官佩印,则以为官印双全,与印绶用官者同论;
见财透食神,不以为财逢食生,而以为食神生财,与食神生财同论;
见偏印透食,不以为泄身之秀,而以为枭神夺食,宜用财制,与食神逢枭同论;
见煞逢食制而露印者,不为去食护煞,而以为煞印相生,与印绶逢煞者同论;
更有煞格逢刃,不以为刃可帮身制煞,而以为七煞制刃,与阳刃露煞者同论。
此皆由不知月令而妄论之故也。""",
        relation_to_assert006="RELATED",
        analysis="""这里是在批评后人把「财逢食生」和「食神生财」混为一谈。
原文说: 见财透食神, 不以为财逢食生, 而以为食神生财, 与食神生财同论。
这说明「财逢食生」和「食神生财」是两个不同的格局, 不能混淆。
「财逢食生」是财格用食神生财, 「食神生财」是食神格用财。
这进一步证明「食神生财」是格局名称, 不是简单的断语。""",
        authorization_level="QUALIFIED",
    ),
]

# ============================================================
# 搜索结果3: 「食神」+「富贵」的组合
# ============================================================

PROVENANCE_SHISHEN_FUGUI = [
    ProvenanceRecord(
        record_id="P-SF-001",
        search_term="食神+富贵",
        found=True,
        book="《渊海子平》",
        location="第2335段",
        exact_quote="食神居先杀居后，衣禄无亏富贵厚；食神近杀却为殃，终日尘寰慢奔走。",
        context_before="寿元合起最为奇，七杀何忧在岁时；禁凶制杀干头旺，此是人间富贵儿。",
        context_after="何谓之正财？犹如正官之意",
        full_context="""寿元合起最为奇，七杀何忧在岁时；禁凶制杀干头旺，此是人间富贵儿。
食神居先杀居后，衣禄无亏富贵厚；食神近杀却为殃，终日尘寰慢奔走。""",
        relation_to_assert006="RELATED",
        analysis="""这里把食神与富贵联系起来了, 但组合是「食神居先杀居后→衣禄无亏富贵厚」。
这是「食神+杀」的组合, 不是「食神生财→富贵自天来」。
而且还有反向条件: 「食神近杀却为殃」。
所以这里的富贵需要「食神居先杀居后」的特定排列, 不是简单的食神生财。""",
        authorization_level="QUALIFIED",
    ),
    ProvenanceRecord(
        record_id="P-SF-002",
        search_term="食神+富贵",
        found=True,
        book="《渊海子平》",
        location="第2438段",
        exact_quote="盖四柱中身主专旺；而其所用吉神，或为财、或为官、或为印綬、或为食神，俱各带禄权得令，不偏不杂；又无刑冲伤损剋害，方为富贵本源之不杂也。",
        context_before="夫人生有秉富贵之荣，而当兴富贵，而且能享福，而保其终身。其何故也？",
        context_after="他日能成才，振耀前人之基业，成当代之功名；不招谗谤，不致伤害。又在运上步步皆吉，四柱益加吉利，是谓源清流洁；故能享福以过人，保其中而无悔也。皆由命运一路滔滔，生旺而然。非幸也，乃命也，可不辩乎！",
        full_context="""夫人生有秉富贵之荣，而当兴富贵，而且能享福，而保其终身。其何故也？
盖四柱中身主专旺；而其所用吉神，或为财、或为官、或为印綬、或为食神，俱各带禄权得令，不偏不杂；又无刑冲伤损剋害，方为富贵本源之不杂也。
他日能成才，振耀前人之基业，成当代之功名；不招谗谤，不致伤害。又在运上步步皆吉，四柱益加吉利，是谓源清流洁；故能享福以过人，保其中而无悔也。皆由命运一路滔滔，生旺而然。非幸也，乃命也，可不辩乎！""",
        relation_to_assert006="RELATED",
        analysis="""这是非常重要的一段。原典说: 身主专旺 + 所用吉神(财/官/印/食神)带禄权得令 + 不偏不杂 + 无刑冲伤损 → 富贵本源之不杂。
这里食神是作为「所用吉神」之一, 与财、官、印绶并列。
但注意: 富贵的条件是「身主专旺+吉神带禄权得令+不偏不杂+无刑冲伤损」, 不是简单的「食神生财」。
而且这里说的是「富贵本源之不杂」, 不是「富贵自天来」。
这说明食神可以参与富贵的形成, 但需要更多条件, 不能直接说「食神生财→富贵自天来」。""",
        authorization_level="QUALIFIED",
    ),
]

# ============================================================
# 搜索结果4: 财运类断语中的「食神+财」
# ============================================================

PROVENANCE_CAIYUN = [
    ProvenanceRecord(
        record_id="P-CY-001",
        search_term="食神+财 (财运类断语)",
        found=True,
        book="《滴天髓阐微》断语库",
        location="财运类_断语.md 第23条",
        exact_quote="癸巳壬戌此造旺财当令，加以年上食神生助，日逢时禄，不为无根，所以身出富家",
        context_before="必以丑中辛金为用，得丑土包藏，泄劫生财，为辅用之喜神也",
        context_after="癸卯癸未此财官虚露无根，枭比当权得势，以四柱观之，贫夭之命",
        full_context="""必以丑中辛金为用，得丑土包藏，泄劫生财，为辅用之喜神也
癸巳壬戌此造旺财当令，加以年上食神生助，日逢时禄，不为无根，所以身出富家
癸卯癸未此财官虚露无根，枭比当权得势，以四柱观之，贫夭之命""",
        relation_to_assert006="RELATED",
        analysis="""这里说的是「旺财当令+年上食神生助+日逢时禄+不为无根→身出富家」。
这是食神生助旺财, 不是「食神生财→富贵自天来」。
而且条件是「旺财当令+食神生助+日逢时禄+不为无根」, 需要多个条件同时满足。
这说明食神可以生财, 但需要财星当令、日主有根等条件, 不是简单的食神生财就富贵。""",
        authorization_level="QUALIFIED",
    ),
]


# ============================================================
# Effect Provenance Matrix 汇总
# ============================================================

def build_provenance_matrix() -> Dict:
    """构建Effect Provenance Matrix"""

    all_records = (
        PROVENANCE_FUGUI_ZI_TIAN_LAI +
        PROVENANCE_SHISHENG_SHENGCAI +
        PROVENANCE_SHISHEN_FUGUI +
        PROVENANCE_CAIYUN
    )

    matrix = {
        "search_terms": {
            "富贵自天来": {
                "total_found": len(PROVENANCE_FUGUI_ZI_TIAN_LAI),
                "direct_relation_to_assert006": 0,
                "related": 0,
                "unrelated": len(PROVENANCE_FUGUI_ZI_TIAN_LAI),
                "books": ["《三命通会》"],
                "conclusion": "「富贵自天来」在《三命通会》中出现2次, 但都出现在括号注释中, 且都与「食神生财」无关。第一次上下文是「丁亥日乙巳时+金水二局+财官得用」, 第二次是「壬日壬时局+寅辰重叠见+无官亦有财」。",
            },
            "食神生财": {
                "total_found": len(PROVENANCE_SHISHENG_SHENGCAI),
                "direct_relation_to_assert006": 0,
                "related": len(PROVENANCE_SHISHENG_SHENGCAI),
                "unrelated": 0,
                "books": ["《渊海子平》", "《子平真诠》"],
                "conclusion": "「食神生财」在《渊海子平》和《子平真诠》中都有出现, 但主要是作为格局名称/成格条件。《渊海子平》第2430段是格局列表, 《子平真诠》第113段是食格成格条件, 第109段是批评后人混淆「财逢食生」和「食神生财」。没有一处直接说「食神生财→富贵自天来」。",
            },
            "食神+富贵": {
                "total_found": len(PROVENANCE_SHISHEN_FUGUI),
                "direct_relation_to_assert006": 0,
                "related": len(PROVENANCE_SHISHEN_FUGUI),
                "unrelated": 0,
                "books": ["《渊海子平》"],
                "conclusion": "食神与富贵确实有关系, 但需要更多条件。《渊海子平》第2335段是「食神居先杀居后→衣禄无亏富贵厚」(食神+杀的组合), 第2438段是「身主专旺+所用吉神(财/官/印/食神)带禄权得令+不偏不杂+无刑冲伤损→富贵本源之不杂」(食神作为吉神之一)。都不是「食神生财→富贵自天来」。",
            },
            "食神+财 (财运类)": {
                "total_found": len(PROVENANCE_CAIYUN),
                "direct_relation_to_assert006": 0,
                "related": len(PROVENANCE_CAIYUN),
                "unrelated": 0,
                "books": ["《滴天髓阐微》断语库"],
                "conclusion": "财运类断语中有「旺财当令+年上食神生助+日逢时禄+不为无根→身出富家」。这是食神生助旺财, 需要财星当令、日主有根等条件, 不是简单的食神生财就富贵。",
            },
        },
        "direct_authorization_found": False,
        "direct_authorization_evidence": [],
        "qualified_authorization_found": True,
        "qualified_authorization_evidence": [
            "「食神生财」作为格局名称有原典依据(《渊海子平》第2430段)",
            "「食神生财」作为食格成格条件有原典依据(《子平真诠》第113段)",
            "食神与富贵有关系, 但需要更多条件(《渊海子平》第2335段、第2438段)",
            "食神可以生财, 但需要财星当令、日主有根等条件(财运类断语第23条)",
        ],
        "not_authorized_evidence": [
            "「富贵自天来」在《三命通会》中出现2次, 但都与「食神生财」无关",
            "没有找到「食神生财→富贵自天来」的直接原典链条",
            "「食神干旺，胜似财官」不能自动推导成「食神生财→富贵自天来」",
        ],
        "final_conclusion": "EFFECT_NOT_AUTHORIZED",
        "final_conclusion_reason": """跨五部经典及断语库搜索后, 没有找到「食神生财→富贵自天来」的直接原典授权链条。

1. 「富贵自天来」有原典出处(《三命通会》2次), 但上下文完全不同:
   - 第一次: 丁亥日乙巳时+金水二局+财官得用→富贵自天来
   - 第二次: 壬日壬时局+寅辰重叠见+无官亦有财→富贵自天来
   都与「食神生财」无关。

2. 「食神生财」有原典出处, 但主要是作为格局名称/成格条件:
   - 《渊海子平》第2430段: 格局列表中的「食神生财」
   - 《子平真诠》第113段: 「食神生财...食格成也」
   - 《子平真诠》第109段: 批评后人混淆「财逢食生」和「食神生财」

3. 食神与富贵确实有关系, 但需要更多条件:
   - 《渊海子平》第2335段: 「食神居先杀居后→衣禄无亏富贵厚」(食神+杀的组合)
   - 《渊海子平》第2438段: 「身主专旺+所用吉神(财/官/印/食神)带禄权得令+不偏不杂+无刑冲伤损→富贵本源之不杂」
   - 财运类断语第23条: 「旺财当令+食神生助+日逢时禄+不为无根→身出富家」

4. 因此, 「食神生财」作为格局/结构语义可以确认存在, 但「富贵自天来」作为Effect没有获得直接原典授权。
   结构成立 ≠ Effect获得授权。

ASSERT-006应该保持CANDIDATE状态, 不能进入Authorized Assertion Library。
「食神生财」可以作为关系进入关系矩阵, 但「富贵自天来」不能作为Effect授权。""",
    }

    return matrix


# ============================================================
# 主流程
# ============================================================

def main():
    print("=" * 110)
    print("STR-001A P6.4-G-R ASSERT-006 Cross-Classical Effect Provenance Audit")
    print("=" * 110)

    print(f"""
  目标: 在五部经典及其他本地Canonical Corpus中搜索「富贵自天来」及相关组合,
        建立Effect Provenance Matrix, 彻底查清「富贵自天来」到底有没有原典依据。

  搜索范围:
    1. 「富贵自天来」精确匹配
    2. 「食神生财」+「富贵」
    3. 「食神」+「富贵」
    4. 「食神」+「财」+「贵」

  搜索语料:
    - D:\\today\\Canonical-Mining\\五部经典完整数据\\ (五部经典完整全文+段落JSON)
    - D:\\today\\五部经典断语库\\ (按经典分+按类别分+综合索引)
    - D:\\today\\Canonical-Mining\\FOR-BAZI五书JSON\\ (五书JSON候选索引)
""")

    # 搜索结果1: 「富贵自天来」
    print(f"\n  {'='*100}")
    print(f"  搜索结果1: 「富贵自天来」精确匹配")
    print(f"  {'='*100}")
    print(f"""
    找到: {len(PROVENANCE_FUGUI_ZI_TIAN_LAI)}处
    典籍: 《三命通会》
    与ASSERT-006直接相关: 0处
    与ASSERT-006无关: {len(PROVENANCE_FUGUI_ZI_TIAN_LAI)}处
""")

    for rec in PROVENANCE_FUGUI_ZI_TIAN_LAI:
        print(f"""
    [{rec.record_id}] {rec.book} {rec.location}
      原文: 「{rec.exact_quote}」
      与ASSERT-006关系: {rec.relation_to_assert006}
      授权级别: {rec.authorization_level}
      分析: {rec.analysis[:100]}...
""")

    # 搜索结果2: 「食神生财」
    print(f"\n  {'='*100}")
    print(f"  搜索结果2: 「食神生财」在五部经典中的出处")
    print(f"  {'='*100}")
    print(f"""
    找到: {len(PROVENANCE_SHISHENG_SHENGCAI)}处
    典籍: 《渊海子平》、《子平真诠》
    与ASSERT-006直接相关: 0处
    与ASSERT-006相关(格局/结构): {len(PROVENANCE_SHISHENG_SHENGCAI)}处
""")

    for rec in PROVENANCE_SHISHENG_SHENGCAI:
        print(f"""
    [{rec.record_id}] {rec.book} {rec.location}
      原文: 「{rec.exact_quote[:80]}...」
      与ASSERT-006关系: {rec.relation_to_assert006}
      授权级别: {rec.authorization_level}
      分析: {rec.analysis[:100]}...
""")

    # 搜索结果3: 「食神」+「富贵」
    print(f"\n  {'='*100}")
    print(f"  搜索结果3: 「食神」+「富贵」的组合")
    print(f"  {'='*100}")
    print(f"""
    找到: {len(PROVENANCE_SHISHEN_FUGUI)}处
    典籍: 《渊海子平》
    与ASSERT-006直接相关: 0处
    与ASSERT-006相关(需要更多条件): {len(PROVENANCE_SHISHEN_FUGUI)}处
""")

    for rec in PROVENANCE_SHISHEN_FUGUI:
        print(f"""
    [{rec.record_id}] {rec.book} {rec.location}
      原文: 「{rec.exact_quote[:80]}...」
      与ASSERT-006关系: {rec.relation_to_assert006}
      授权级别: {rec.authorization_level}
      分析: {rec.analysis[:100]}...
""")

    # 搜索结果4: 财运类断语
    print(f"\n  {'='*100}")
    print(f"  搜索结果4: 财运类断语中的「食神+财」")
    print(f"  {'='*100}")
    print(f"""
    找到: {len(PROVENANCE_CAIYUN)}处
    典籍: 《滴天髓阐微》断语库
    与ASSERT-006直接相关: 0处
    与ASSERT-006相关(需要更多条件): {len(PROVENANCE_CAIYUN)}处
""")

    for rec in PROVENANCE_CAIYUN:
        print(f"""
    [{rec.record_id}] {rec.book} {rec.location}
      原文: 「{rec.exact_quote[:80]}...」
      与ASSERT-006关系: {rec.relation_to_assert006}
      授权级别: {rec.authorization_level}
      分析: {rec.analysis[:100]}...
""")

    # Effect Provenance Matrix 汇总
    print(f"\n  {'='*100}")
    print(f"  Effect Provenance Matrix 汇总")
    print(f"  {'='*100}")

    matrix = build_provenance_matrix()

    print(f"""
    搜索词汇总:
""")
    for term, data in matrix["search_terms"].items():
        print(f"""
      「{term}」:
        找到: {data['total_found']}处
        直接相关: {data['direct_relation_to_assert006']}处
        相关(需更多条件): {data['related']}处
        无关: {data['unrelated']}处
        典籍: {', '.join(data['books'])}
        结论: {data['conclusion'][:80]}...
""")

    print(f"""
    直接授权找到: {'✓ 是' if matrix['direct_authorization_found'] else '✗ 否'}
    限定授权找到: {'✓ 是' if matrix['qualified_authorization_found'] else '✗ 否'}

    限定授权证据:
""")
    for ev in matrix["qualified_authorization_evidence"]:
        print(f"      • {ev}")

    print(f"""
    未授权证据:
""")
    for ev in matrix["not_authorized_evidence"]:
        print(f"      • {ev}")

    # 最终结论
    print(f"\n  {'='*100}")
    print(f"  P6.4-G-R 最终结论")
    print(f"  {'='*100}")

    print(f"""
    最终结论: {matrix['final_conclusion']}

    {matrix['final_conclusion_reason']}

    ASSERT-006当前状态: CANDIDATE (不进入Authorized Assertion Library)
      - 「食神生财」作为格局/结构语义可以确认存在, 可以进入关系矩阵
      - 「富贵自天来」作为Effect没有获得直接原典授权
      - 结构成立 ≠ Effect获得授权

    这正是P6.4最重要的原则:
      结构成立 ≠ Effect获得授权 ✓

    P6.4-G-R验证通过。P6.4 Assertion Asset Production Protocol完整验证通过。

    即使ASSERT-006永远进不了Authorized Library, 也属于成功。
    这才是断言资产治理真正建立起来的标志。

    当前Library状态:
      AUTHORIZED_WITH_QUALIFIER = 4
        ASSERT-002 身强杀浅假杀为权
        ASSERT-003 杀重身轻终身有损
        ASSERT-004 财多身弱富屋贫人
        ASSERT-005 伤官见官为祸百端
      CANDIDATE = 1
        ASSERT-006 食神生财富贵自天来 (Effect未授权)
      POSTERIOR = 1
        ASSERT-001 财星透干逢流年合之主进财

    P6.1～P6.4全部冻结。可以进入P6.5批量断言资产生产。
    {'='*100}
""")


if __name__ == "__main__":
    main()
