"""
STR-001A Phase 6.1 — 全局 Authority Matrix

把 Layer 1-4 所有已审关系统一登记，明确：
- EXIS 哪些东西可以计算 (COMPUTABLE)
- 哪些只能作为关系事实 (RELATION_FACT)
- 哪些只能作为候选 (CANDIDATE)
- 哪些必须输出 UNRESOLVED

字段: ID, LAYER, RELATION, SOURCE_STATUS, ALLOWED, FORBIDDEN, UNRESOLVED_TRIGGER
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class Layer(str, Enum):
    FACT = "FACT"                    # L1 原始事实
    RELATION = "RELATION"            # Layer 2 关系
    COMBINATION = "COMBINATION"      # Layer 3 组合
    MODIFIER = "MODIFIER"            # Layer 4 修正/覆盖


class SourceStatus(str, Enum):
    SOURCE_SUPPORTED = "SOURCE_SUPPORTED"
    SOURCE_SUPPORTED_WITH_QUALIFIER = "SOURCE_SUPPORTED_WITH_QUALIFIER"
    SOURCE_MAPPED_NON_PROOF = "SOURCE_MAPPED_NON_PROOF"
    INSUFFICIENT_SOURCE = "INSUFFICIENT_SOURCE"
    SOURCE_CONTESTED = "SOURCE_CONTESTED"


class Computability(str, Enum):
    COMPUTABLE = "COMPUTABLE"                    # 可以直接计算
    COMPUTABLE_WITH_QUALIFIER = "COMPUTABLE_WITH_QUALIFIER"  # 可以计算但带限定
    RELATION_FACT_ONLY = "RELATION_FACT_ONLY"    # 只能作为关系事实
    CANDIDATE_ONLY = "CANDIDATE_ONLY"            # 只能作为候选
    MUST_BE_UNRESOLVED = "MUST_BE_UNRESOLVED"    # 必须输出 UNRESOLVED


@dataclass
class AuthorityEntry:
    entry_id: str
    layer: Layer
    relation: str
    source_status: SourceStatus
    computability: Computability
    allowed: str
    forbidden: str
    unresolved_trigger: str
    source_book: str = ""
    notes: str = ""

    def to_dict(self):
        return {
            "ID": self.entry_id,
            "LAYER": self.layer.value,
            "RELATION": self.relation,
            "SOURCE_STATUS": self.source_status.value,
            "COMPUTABILITY": self.computability.value,
            "ALLOWED": self.allowed,
            "FORBIDDEN": self.forbidden,
            "UNRESOLVED_TRIGGER": self.unresolved_trigger,
            "SOURCE_BOOK": self.source_book,
            "NOTES": self.notes,
        }


entries: List[AuthorityEntry] = []


# ============================================================
# Layer FACT — L1 原始事实
# ============================================================

entries.append(AuthorityEntry(
    entry_id="F-001",
    layer=Layer.FACT,
    relation="八字四柱 (年月日时天干地支)",
    source_status=SourceStatus.SOURCE_SUPPORTED,
    computability=Computability.COMPUTABLE,
    allowed="直接计算四柱干支",
    forbidden="—",
    unresolved_trigger="—",
    source_book="通用",
    notes="基础输入事实",
))

entries.append(AuthorityEntry(
    entry_id="F-002",
    layer=Layer.FACT,
    relation="日主 (day_master)",
    source_status=SourceStatus.SOURCE_SUPPORTED,
    computability=Computability.COMPUTABLE,
    allowed="直接确定日主天干五行",
    forbidden="—",
    unresolved_trigger="—",
    source_book="通用",
    notes="日柱天干",
))

entries.append(AuthorityEntry(
    entry_id="F-003",
    layer=Layer.FACT,
    relation="月令 (month_branch)",
    source_status=SourceStatus.SOURCE_SUPPORTED,
    computability=Computability.COMPUTABLE,
    allowed="直接确定月令地支",
    forbidden="—",
    unresolved_trigger="—",
    source_book="通用",
    notes="月柱地支",
))

entries.append(AuthorityEntry(
    entry_id="F-004",
    layer=Layer.FACT,
    relation="十神 (ten_gods)",
    source_status=SourceStatus.SOURCE_SUPPORTED,
    computability=Computability.COMPUTABLE,
    allowed="直接计算每个天干/地支相对于日主的十神",
    forbidden="十神数量→强弱结论",
    unresolved_trigger="—",
    source_book="渊海子平",
    notes="正官/七杀/正印/偏印/比肩/劫财/食神/伤官/正财/偏财",
))

entries.append(AuthorityEntry(
    entry_id="F-005",
    layer=Layer.FACT,
    relation="十二长生 (twelve_growth_stages)",
    source_status=SourceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
    computability=Computability.COMPUTABLE_WITH_QUALIFIER,
    allowed="日主×四支计算十二长生状态(阳干顺行阴干逆行戊己与丙丁同论)",
    forbidden="十二长生状态→直接强弱结论; 所有十二长生状态→自动算根",
    unresolved_trigger="阴干长生存在体系争议时",
    source_book="三命通会/渊海子平",
    notes="作为L1原始事实, 不直接推出强弱",
))

entries.append(AuthorityEntry(
    entry_id="F-006",
    layer=Layer.FACT,
    relation="地支藏干 (hidden_stems)",
    source_status=SourceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
    computability=Computability.COMPUTABLE_WITH_QUALIFIER,
    allowed="完整藏干(本气/中气/余气作为工程结构)",
    forbidden="藏干数量→强弱; 有藏干→自动有根; 声称'三层命名是原典原词'",
    unresolved_trigger="—",
    source_book="渊海子平",
    notes="三层命名是工程归纳, 不是原典原词",
))

entries.append(AuthorityEntry(
    entry_id="F-007",
    layer=Layer.FACT,
    relation="五行分布 (five_element_distribution)",
    source_status=SourceStatus.SOURCE_SUPPORTED,
    computability=Computability.COMPUTABLE,
    allowed="统计天干地支藏干的五行数量分布",
    forbidden="五行数量→score→强弱; 五行占比→直接结论",
    unresolved_trigger="—",
    source_book="通用",
    notes="只能作为事实展示, 不能用于评分",
))

entries.append(AuthorityEntry(
    entry_id="F-008",
    layer=Layer.FACT,
    relation="空亡 (kong_wang)",
    source_status=SourceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
    computability=Computability.COMPUTABLE_WITH_QUALIFIER,
    allowed="计算旬空, 标记哪些地支逢空亡",
    forbidden="空亡=力量×0.5; 空亡→根自动失效; 空亡→身弱",
    unresolved_trigger="空亡对具体关系的影响需要单独判断",
    source_book="渊海子平",
    notes="金空则鸣/火空则发/水空则流(上吉), 木空则朽/土空则崩(下凶)",
))


# ============================================================
# Layer RELATION — Layer 2 关系
# ============================================================

# R1 根关系
entries.append(AuthorityEntry(
    entry_id="R-001",
    layer=Layer.RELATION,
    relation="藏干对应日主 → 通根",
    source_status=SourceStatus.SOURCE_SUPPORTED,
    computability=Computability.COMPUTABLE,
    allowed="地支藏干中存在日主同类五行→通根=TRUE",
    forbidden="有藏干→自动通根(必须是日主同类); 名义通根(乙逢戌无藏木不算)",
    unresolved_trigger="—",
    source_book="子平真诠",
    notes="乙逢戌不作通根论(戌中无藏木)",
))

entries.append(AuthorityEntry(
    entry_id="R-002",
    layer=Layer.RELATION,
    relation="十二长生部分状态 → 根",
    source_status=SourceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
    computability=Computability.COMPUTABLE_WITH_QUALIFIER,
    allowed="长生/禄/旺→根之重候选; 墓库/余气→根之轻候选(需结合实际藏干)",
    forbidden="所有十二长生状态→自动算根; 十二长生标签→直接根重; 阴干长生=阳干长生",
    unresolved_trigger="阴干长生(乙午/丁酉)需特殊处理",
    source_book="子平真诠",
    notes="长生禄旺根之重者, 墓库余气根之轻者; 阴长生不作此论然亦为有根比得一余气",
))

entries.append(AuthorityEntry(
    entry_id="R-003",
    layer=Layer.RELATION,
    relation="根 → 根之重/根之轻",
    source_status=SourceStatus.SOURCE_SUPPORTED,
    computability=Computability.COMPUTABLE,
    allowed="长生/禄/旺→ROOT_HEAVY; 墓库/余气→ROOT_LIGHT; 实际通根→ROOT_PRESENT; 无通根→ROOT_NONE",
    forbidden="根数量→score; root_count>1→身强",
    unresolved_trigger="—",
    source_book="子平真诠",
    notes="工程状态ROOT_HEAVY/ROOT_LIGHT/ROOT_PRESENT/ROOT_NONE, 不要声称原典说根深/根浅",
))

entries.append(AuthorityEntry(
    entry_id="R-004",
    layer=Layer.RELATION,
    relation="比劫 → 扶助",
    source_status=SourceStatus.SOURCE_SUPPORTED,
    computability=Computability.COMPUTABLE,
    allowed="比肩/劫财存在→扶助关系标记",
    forbidden="比劫数量→score; 比劫扶助=通根; 比劫count>=N→党众",
    unresolved_trigger="—",
    source_book="子平真诠",
    notes="比劫如朋友之相扶, 通根如室家之可住; 干多不如根重",
))

entries.append(AuthorityEntry(
    entry_id="R-005",
    layer=Layer.RELATION,
    relation="印 → 生扶",
    source_status=SourceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
    computability=Computability.COMPUTABLE_WITH_QUALIFIER,
    allowed="正印/偏印存在→生扶关系标记",
    forbidden="印越多越好; 印数量→score; 印过旺不检查反作用",
    unresolved_trigger="印过旺时(水多木漂等)",
    source_book="渊海子平/子平真诠",
    notes="水多木漂有原典依据(论五行生克制化); 印绶不宜身太旺",
))

# R3 克泄耗
entries.append(AuthorityEntry(
    entry_id="R-006",
    layer=Layer.RELATION,
    relation="官杀 → 克/制",
    source_status=SourceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
    computability=Computability.COMPUTABLE_WITH_QUALIFIER,
    allowed="正官/七杀存在→克/制关系标记",
    forbidden="官杀旺→身弱; 官杀数量→score; 官杀→直接强弱结论",
    unresolved_trigger="官杀过重且无制化时",
    source_book="渊海子平",
    notes="身强杀浅假杀为权 vs 杀重身轻终身有损; 官杀作用关系≠身弱结果",
))

entries.append(AuthorityEntry(
    entry_id="R-007",
    layer=Layer.RELATION,
    relation="食伤 → 泄/盗气",
    source_status=SourceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
    computability=Computability.COMPUTABLE_WITH_QUALIFIER,
    allowed="食神/伤官存在→泄/盗气关系标记",
    forbidden="有食伤→身弱; 食伤数量→score; 食伤→直接强弱结论",
    unresolved_trigger="食伤过重时",
    source_book="渊海子平",
    notes="原典明确称食伤为盗气; 但泄身需要过重条件, 身弱食多反为害",
))

entries.append(AuthorityEntry(
    entry_id="R-008",
    layer=Layer.RELATION,
    relation="财 → 耗/我克",
    source_status=SourceStatus.SOURCE_MAPPED_NON_PROOF,
    computability=Computability.RELATION_FACT_ONLY,
    allowed="正财/偏财存在→耗/我克关系标记",
    forbidden="财多→身弱; 财数量→score; 财→直接强弱结论",
    unresolved_trigger="—",
    source_book="渊海子平",
    notes="财多身弱与财多身健方为贵同时存在; 财是承载能力变量不是身弱指标",
))

# R4 合冲刑会
entries.append(AuthorityEntry(
    entry_id="R-009",
    layer=Layer.RELATION,
    relation="合 (六合/三合/半合/天干五合)",
    source_status=SourceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
    computability=Computability.COMPUTABLE_WITH_QUALIFIER,
    allowed="检测合的关系, 标记合的对象和类型",
    forbidden="合→强; 合→直接强弱; 五合=合化",
    unresolved_trigger="合而不化/争合时",
    source_book="渊海子平/子平真诠",
    notes="必须区分合/合住/合化/争合; 贪合忘官",
))

entries.append(AuthorityEntry(
    entry_id="R-010",
    layer=Layer.RELATION,
    relation="冲 (六冲)",
    source_status=SourceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
    computability=Computability.COMPUTABLE_WITH_QUALIFIER,
    allowed="检测六冲关系, 标记冲的对象",
    forbidden="冲→弱; 冲→根自动失效; 冲→直接强弱",
    unresolved_trigger="冲动根的位置时",
    source_book="滴天髓/渊海子平",
    notes="生方怕动, 库宜开, 败地逢冲子细裁; 冲≠弱",
))

entries.append(AuthorityEntry(
    entry_id="R-011",
    layer=Layer.RELATION,
    relation="刑 (三刑/自刑)",
    source_status=SourceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
    computability=Computability.COMPUTABLE_WITH_QUALIFIER,
    allowed="检测刑的关系, 标记刑的对象",
    forbidden="刑→凶; 刑→根自动伤; 刑→直接强弱",
    unresolved_trigger="刑被引动时",
    source_book="滴天髓",
    notes="刑与害兮动不动; 纵遇卯刑还有情; 刑≠凶",
))

entries.append(AuthorityEntry(
    entry_id="R-012",
    layer=Layer.RELATION,
    relation="会 (三会方)",
    source_status=SourceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
    computability=Computability.COMPUTABLE_WITH_QUALIFIER,
    allowed="检测三会方(三支齐全), 标记会的五行",
    forbidden="会→日主强; 会→直接强弱",
    unresolved_trigger="缺一支不成会时",
    source_book="渊海子平/三命通会",
    notes="三会方需要三支齐全; 会≠强",
))

entries.append(AuthorityEntry(
    entry_id="R-013",
    layer=Layer.RELATION,
    relation="破/害",
    source_status=SourceStatus.INSUFFICIENT_SOURCE,
    computability=Computability.MUST_BE_UNRESOLVED,
    allowed="仅检测标记, 不计算效果",
    forbidden="破/害→任何效果计算; 破/害→强弱",
    unresolved_trigger="所有涉及破/害的效果判断",
    source_book="—",
    notes="五部经典内对破/害的具体作用效果论述不足",
))

# R5 有效性修正
entries.append(AuthorityEntry(
    entry_id="R-014",
    layer=Layer.RELATION,
    relation="空亡 → 关系有效性修正",
    source_status=SourceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
    computability=Computability.COMPUTABLE_WITH_QUALIFIER,
    allowed="空亡作为Relation Effect Modifier, 按五行区分(金火水空反吉, 木土空为凶)",
    forbidden="空亡=力量减半; 空亡→根自动失效; 空亡→身弱; 空亡=Strength Evidence",
    unresolved_trigger="空亡对具体十神/根的影响",
    source_book="渊海子平",
    notes="金空则鸣火空则发水空则流(上吉), 木空则朽土空则崩(下凶)",
))

entries.append(AuthorityEntry(
    entry_id="R-015",
    layer=Layer.RELATION,
    relation="合解冲/刑, 冲破合",
    source_status=SourceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
    computability=Computability.COMPUTABLE_WITH_QUALIFIER,
    allowed="检测合冲刑的相互作用, 标记可能的解/破",
    forbidden="简单叠加效果; 有合就一定解冲",
    unresolved_trigger="多重合冲刑同时存在时",
    source_book="子平真诠",
    notes="因解而反得刑冲; 具体解析规则需逐条细化",
))

# R6 天干五合
entries.append(AuthorityEntry(
    entry_id="R-016",
    layer=Layer.RELATION,
    relation="天干五合 (合/合住/合化/争合)",
    source_status=SourceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
    computability=Computability.COMPUTABLE_WITH_QUALIFIER,
    allowed="检测天干五合, 区分合/合住/合化/争合",
    forbidden="五合=合化; 合→直接强弱; 争合不检查",
    unresolved_trigger="合化条件验证/争合时",
    source_book="渊海子平",
    notes="合化条件严格(化神得令得地无克制); 贪合忘官; 丁壬妒合",
))


# ============================================================
# Layer COMBINATION — Layer 3 组合
# ============================================================

entries.append(AuthorityEntry(
    entry_id="C-001",
    layer=Layer.COMBINATION,
    relation="比劫+印绶+通根 → 党众",
    source_status=SourceStatus.SOURCE_SUPPORTED,
    computability=Computability.COMPUTABLE_WITH_QUALIFIER,
    allowed="比劫扶助+印绶生扶+实际通根→党众状态标记(质性判断)",
    forbidden="比劫count>=2 AND 印count>=1 AND 通根count>=1→党众(数值公式); 党众→+score",
    unresolved_trigger="要素不完整或质量不足时",
    source_book="子平真诠",
    notes="比劫印绶通根扶助为党众; 通根必须实际有效(乙逢戌不算)",
))

entries.append(AuthorityEntry(
    entry_id="C-002",
    layer=Layer.COMBINATION,
    relation="比劫/印绶/通根不足 → 助寡",
    source_status=SourceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
    computability=Computability.COMPUTABLE_WITH_QUALIFIER,
    allowed="生扶/根基整体不足→助寡状态标记(质性判断)",
    forbidden="比劫<2 OR 印<1 OR 无通根→助寡(简单数值); 助寡→-score",
    unresolved_trigger="部分缺失时(如只有比劫无印绶)",
    source_book="子平真诠",
    notes="助寡从党众反面推导, 不足标准未数值化",
))

entries.append(AuthorityEntry(
    entry_id="C-003",
    layer=Layer.COMBINATION,
    relation="党众/助寡 → 强/弱",
    source_status=SourceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
    computability=Computability.COMPUTABLE_WITH_QUALIFIER,
    allowed="党众→一般强; 助寡→一般弱(带'大致'qualifier)",
    forbidden="党众=绝对强(无条件); 助寡=绝对弱; 党众→+score; 助寡→-score",
    unresolved_trigger="克泄耗过重/特殊格局/印过旺反作用时",
    source_book="子平真诠",
    notes="★最高风险项; 大致党众为强助寡为弱; 虽衰而强证明党众→强; 但大致意味着可能有例外",
))

entries.append(AuthorityEntry(
    entry_id="C-004",
    layer=Layer.COMBINATION,
    relation="生扶组合+克泄耗组合 → 最终强弱",
    source_status=SourceStatus.INSUFFICIENT_SOURCE,
    computability=Computability.MUST_BE_UNRESOLVED,
    allowed="克泄耗作为QUALIFIER/COUNTER_RELATION标记, 不直接计算最终强弱",
    forbidden="support_score - opposition_score = final_strength; 加权评分; 克泄耗数量→强弱",
    unresolved_trigger="所有涉及生扶+克泄耗组合的最终强弱判断",
    source_book="—",
    notes="原典没有系统的组合规则只有个案描述; 宁愿UNRESOLVED也不制造不存在的因果规则",
))


# ============================================================
# Layer MODIFIER — Layer 4 修正/覆盖
# ============================================================

entries.append(AuthorityEntry(
    entry_id="M-001",
    layer=Layer.MODIFIER,
    relation="月令+全局 → 旺衰修正",
    source_status=SourceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
    computability=Computability.COMPUTABLE_WITH_QUALIFIER,
    allowed="月令建立旺衰基线; 全局结构(党众/助寡)修正强弱维度; 输出二维状态(wangshuai+qiangruo)",
    forbidden="全局气势→推翻月令; 修正=月令被覆盖; 自行补数值公式",
    unresolved_trigger="全局结构与月令明显冲突时",
    source_book="子平真诠/滴天髓",
    notes="修正的是强弱维度不是旺衰维度; 虽旺而弱虽衰而强是二维分离",
))

entries.append(AuthorityEntry(
    entry_id="M-002",
    layer=Layer.MODIFIER,
    relation="全局气势 → 月令覆盖",
    source_status=SourceStatus.SOURCE_MAPPED_NON_PROOF,
    computability=Computability.RELATION_FACT_ONLY,
    allowed="全局气势作为QUALIFIER标记(如'全局金太重'/'木根深')",
    forbidden="global_qi_score > X → 月令覆盖; 五行计分→气势分数; 全局气势→直接推翻月令",
    unresolved_trigger="全局气势与月令明显冲突时qiangruo标UNRESOLVED",
    source_book="滴天髓",
    notes="滴天髓言其理不言其用; 月令是第一观察入口不是绝对否决权但也不能被简单覆盖",
))

entries.append(AuthorityEntry(
    entry_id="M-003",
    layer=Layer.MODIFIER,
    relation="调候 → 强弱",
    source_status=SourceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
    computability=Computability.COMPUTABLE_WITH_QUALIFIER,
    allowed="调候作为独立字段seasonal_remedy(primary/assistant), 与wangshuai/qiangruo并行",
    forbidden="调候→强弱推导; 乙木戌月丙火为主→所以身弱; 调候混入旺衰强弱",
    unresolved_trigger="—",
    source_book="穷通宝鉴",
    notes="调候是独立维度; 穷通宝鉴言其用不言其理; 120条调候候选需原典核验",
))

entries.append(AuthorityEntry(
    entry_id="M-004",
    layer=Layer.MODIFIER,
    relation="特殊格局 → 普通模型覆盖",
    source_status=SourceStatus.SOURCE_SUPPORTED_WITH_QUALIFIER,
    computability=Computability.CANDIDATE_ONLY,
    allowed="检测特殊格局候选; 按原典条件严格验证成格/破格; 成格标记special_pattern=CONFIRMED并覆盖普通路径",
    forbidden="关键词→强制成格; 官杀count>=3→从杀格; 特殊格局作为万能例外; 条件不明确时强行成格",
    unresolved_trigger="成格条件不完整/破格条件存疑时",
    source_book="子平真诠/滴天髓",
    notes="★★★最高危险项; 从杀格四柱皆煞而日主无根舍而从之; 弱极宜克是原则不是算法; 破格退回普通路径",
))


# ============================================================
# 主执行：输出 Authority Matrix
# ============================================================

def main():
    print("=" * 120)
    print("STR-001A Phase 6.1 — 全局 Authority Matrix")
    print("=" * 120)
    print()
    print("目的: 把 Layer 1-4 所有已审关系统一登记, 明确:")
    print("  - COMPUTABLE: 可以直接计算")
    print("  - COMPUTABLE_WITH_QUALIFIER: 可以计算但带限定")
    print("  - RELATION_FACT_ONLY: 只能作为关系事实")
    print("  - CANDIDATE_ONLY: 只能作为候选")
    print("  - MUST_BE_UNRESOLVED: 必须输出 UNRESOLVED")
    print()

    # 按层级分组
    layers = [
        ("FACT (L1 原始事实)", Layer.FACT),
        ("RELATION (Layer 2 关系)", Layer.RELATION),
        ("COMBINATION (Layer 3 组合)", Layer.COMBINATION),
        ("MODIFIER (Layer 4 修正/覆盖)", Layer.MODIFIER),
    ]

    for layer_name, layer_enum in layers:
        layer_entries = [e for e in entries if e.layer == layer_enum]
        print(f"\n{'='*120}")
        print(f"【{layer_name}】({len(layer_entries)}条)")
        print(f"{'='*120}")
        print(f"  {'ID':<8} {'关系':<30} {'原典状态':<35} {'可计算性':<25}")
        print(f"  {'─'*8} {'─'*30} {'─'*35} {'─'*25}")
        for e in layer_entries:
            print(f"  {e.entry_id:<8} {e.relation[:28]:<30} {e.source_status.value:<35} {e.computability.value:<25}")

    # 可计算性统计
    print(f"\n{'='*120}")
    print("可计算性统计")
    print(f"{'='*120}")
    for c in Computability:
        count = sum(1 for e in entries if e.computability == c)
        print(f"  {c.value}: {count}条")
    print(f"  总计: {len(entries)}条")

    # 详细清单
    print(f"\n{'='*120}")
    print("详细清单 (ALLOWED / FORBIDDEN / UNRESOLVED_TRIGGER)")
    print(f"{'='*120}")
    for e in entries:
        print(f"\n  【{e.entry_id}】{e.relation}")
        print(f"    原典: {e.source_book} | 状态: {e.source_status.value} | 可计算: {e.computability.value}")
        print(f"    ALLOWED: {e.allowed}")
        print(f"    FORBIDDEN: {e.forbidden}")
        print(f"    UNRESOLVED_TRIGGER: {e.unresolved_trigger}")
        if e.notes:
            print(f"    NOTES: {e.notes}")

    # 对 Canonical State Resolver 的工程指令
    print(f"\n{'='*120}")
    print("对 Canonical State Resolver 的工程指令")
    print(f"{'='*120}")
    print(f"""
  输入: 八字四柱
    ↓
  Step 1: FACT 层 (全部 COMPUTABLE)
    - 计算四柱干支、日主、月令、十神、十二长生、藏干、五行分布、空亡
    - 注意: 十二长生和藏干只作为事实, 不直接推出强弱

  Step 2: RELATION 层 (大部分 COMPUTABLE_WITH_QUALIFIER)
    - 通根判断 (R-001): 藏干中日主同类五行→通根
    - 根质量判断 (R-003): 长生禄旺→ROOT_HEAVY, 墓库余气→ROOT_LIGHT
    - 十神关系标记 (R-004~R-008): 比劫扶助、印生扶、官杀克制、食伤泄、财耗
    - 结构关系标记 (R-009~R-013): 合冲刑会破害
    - 有效性修正 (R-014~R-016): 空亡、合解冲、天干五合
    - 注意: 所有关系只标记, 不直接推出强弱; 破/害(R-013)必须UNRESOLVED

  Step 3: COMBINATION 层
    - 党众判断 (C-001): 比劫+印绶+通根→党众 (质性判断, 非数值)
    - 助寡判断 (C-002): 生扶不足→助寡 (质性判断)
    - 强弱基线 (C-003): 党众→一般强, 助寡→一般弱 (带'大致'qualifier)
    - 克泄耗组合 (C-004): 必须UNRESOLVED, 只作QUALIFIER标记

  Step 4: MODIFIER 层
    - 旺衰修正 (M-001): 月令旺衰基线 + 全局强弱修正 → 二维输出
    - 全局气势 (M-002): 作为QUALIFIER, 不覆盖月令
    - 调候 (M-003): 独立字段seasonal_remedy, 不参与强弱
    - 特殊格局 (M-004): 候选检测, 严格成格/破格验证, 成格覆盖普通路径

  输出: Canonical State
    wangshuai: 旺 / 衰 / UNRESOLVED
    qiangruo: 强 / 弱 / UNRESOLVED
    root_state: ROOT_HEAVY / ROOT_LIGHT / ROOT_PRESENT / ROOT_NONE
    dangzhong: TRUE / FALSE / UNRESOLVED
    seasonal_remedy: {{ primary: ..., assistant: [...] }}
    special_pattern: candidate / confirmed / rejected / unresolved
    qualifiers: [水多木漂, 官杀过重, 食伤过重, ...]
    unresolved_reasons: [克泄耗组合无法计算, 破害效果未知, ...]

  ★ 核心原则: 宁愿输出 UNRESOLVED, 也不制造不存在于原典的因果规则。
""")

    print("=" * 120)
    print("全局 Authority Matrix 生成完成。")
    print("下一步: 用 1983 癸亥 壬戌 乙未 壬午 跑 Canonical State Resolver 验证。")
    print("=" * 120)


if __name__ == "__main__":
    main()
