"""
STR-001A P6.2-A Assertion Precondition Engine
Golden Assertion #1: 财星透干，逢流年合之，主进财。

五层拆解:
  Evidence → Preconditions → Matcher → Effect → Conclusion

6条锁定规则:
  1. Assertion Engine不重新排盘, 只消费Canonical State / Relation State
  2. "财星透干"与"流年合之"是两个独立Preconditions
  3. 五合≠合化, 只验证"合"的关系
  4. "主进财"作为Assertion Effect/Conclusion单独存储, 保留完整证据链
  5. 缺任一前置条件→NOT_MATCHED, 不能模糊匹配
  6. 证据不足→INSUFFICIENT_SOURCE / UNRESOLVED

测试: 至少1个命中案例 + 2个非命中案例, 证明不是关键词搜索而是结构化Preconditions匹配
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


# ============================================================
# 状态枚举
# ============================================================

class PreconditionState(str, Enum):
    SATISFIED = "SATISFIED"           # 前置条件满足
    NOT_SATISFIED = "NOT_SATISFIED"   # 前置条件不满足
    UNRESOLVED = "UNRESOLVED"         # 无法确定


class MatchResult(str, Enum):
    ASSERTION_CONFIRMED = "ASSERTION_CONFIRMED"   # 断言确认(所有preconditions满足, evidence确认)
    ASSERTION_QUALIFIED = "ASSERTION_QUALIFIED"   # 断言有条件成立(所有preconditions满足, 但evidence为candidate/带qualifier)
    NOT_MATCHED = "NOT_MATCHED"                   # 不匹配(缺前置条件)
    UNRESOLVED = "UNRESOLVED"                     # 无法确定(证据不足)


class EvidenceAuthority(str, Enum):
    CONFIRMED = "CONFIRMED"               # 原典明确授权
    CANDIDATE = "CANDIDATE"               # 候选(组成部分有原典依据, 完整断言未找到精确原文)
    PARTIALLY_AUTHORIZED = "PARTIALLY_AUTHORIZED"  # 部分授权
    INSUFFICIENT_SOURCE = "INSUFFICIENT_SOURCE"    # 原典依据不足


# ============================================================
# 数据结构
# ============================================================

@dataclass
class AssertionDef:
    """ASSERTION 定义"""
    id: str
    source: str
    canonical_text: str
    description: str


@dataclass
class EvidenceEntry:
    """EVIDENCE 层"""
    source_reference: str               # 来源参考
    source_text: str                    # 原典原文(如找到)
    authority_status: EvidenceAuthority  # 授权状态
    component_evidence: List[str] = field(default_factory=list)  # 各组成部分的原典依据
    notes: str = ""


@dataclass
class Precondition:
    """单个前置条件"""
    pid: str
    name: str
    description: str
    state: PreconditionState = PreconditionState.UNRESOLVED
    evidence: str = ""
    failure_reason: str = ""


@dataclass
class PreconditionsLayer:
    """PRECONDITIONS 层"""
    p1_caixing_tougan: Precondition = field(default_factory=lambda: Precondition(
        pid="P1", name="财星透干",
        description="命局中财星(正财/偏财)出现在天干(年干/月干/时干), 而非仅藏于地支",
    ))
    p2_liunian_cunzai: Precondition = field(default_factory=lambda: Precondition(
        pid="P2", name="流年存在",
        description="指定流年天干已确认",
    ))
    p3_wuhe: Precondition = field(default_factory=lambda: Precondition(
        pid="P3", name="流年干与财星天干五合",
        description="流年天干与命局中透干的财星天干构成天干五合关系(甲己/乙庚/丙辛/丁壬/戊癸)",
    ))

    def all_satisfied(self) -> bool:
        return all(p.state == PreconditionState.SATISFIED for p in [
            self.p1_caixing_tougan, self.p2_liunian_cunzai, self.p3_wuhe
        ])

    def get_failed(self) -> List[Precondition]:
        return [p for p in [self.p1_caixing_tougan, self.p2_liunian_cunzai, self.p3_wuhe]
                if p.state == PreconditionState.NOT_SATISFIED]

    def get_unresolved(self) -> List[Precondition]:
        return [p for p in [self.p1_caixing_tougan, self.p2_liunian_cunzai, self.p3_wuhe]
                if p.state == PreconditionState.UNRESOLVED]


@dataclass
class MatchLayer:
    """MATCH 层"""
    matched: bool = False
    failed_conditions: List[str] = field(default_factory=list)
    unresolved_conditions: List[str] = field(default_factory=list)
    match_details: str = ""


@dataclass
class EffectLayer:
    """EFFECT 层"""
    source_authorized_effect: str = ""   # 原典授权的效果
    effect_qualifiers: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class ConclusionLayer:
    """CONCLUSION 层"""
    result: MatchResult = MatchResult.UNRESOLVED
    reason: str = ""
    evidence_chain: List[str] = field(default_factory=list)


@dataclass
class AssertionResult:
    """完整断言结果"""
    assertion: AssertionDef
    evidence: EvidenceEntry
    preconditions: PreconditionsLayer
    match: MatchLayer
    effect: EffectLayer
    conclusion: ConclusionLayer
    input_chart: Dict = field(default_factory=dict)
    input_liunian: str = ""


# ============================================================
# 基础数据 (不重新排盘, 只消费结构化数据)
# ============================================================

# 天干五合表
TIANGAN_WUHE = {
    ("甲", "己"): "甲己合",
    ("己", "甲"): "甲己合",
    ("乙", "庚"): "乙庚合",
    ("庚", "乙"): "乙庚合",
    ("丙", "辛"): "丙辛合",
    ("辛", "丙"): "丙辛合",
    ("丁", "壬"): "丁壬合",
    ("壬", "丁"): "丁壬合",
    ("戊", "癸"): "戊癸合",
    ("癸", "戊"): "戊癸合",
}

# 十神: 日主克者为财 (阳见阴/阴见阳为正财, 阳见阳/阴见阴为偏财)
# 五行相克: 木克土, 土克水, 水克火, 火克金, 金克木
WUXING_KE = {
    "木": "土", "土": "水", "水": "火", "火": "金", "金": "木"
}

TIANGAN_WUXING = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火",
    "戊": "土", "己": "土", "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}

TIANGAN_YINYANG = {
    "甲": "阳", "乙": "阴", "丙": "阳", "丁": "阴",
    "戊": "阳", "己": "阴", "庚": "阳", "辛": "阴",
    "壬": "阳", "癸": "阴",
}


def get_caixing(day_master: str) -> Tuple[str, str]:
    """获取日主的正财和偏财天干 (只做基础十神映射, 不重新排盘)"""
    dm_wuxing = TIANGAN_WUXING[day_master]
    dm_yinyang = TIANGAN_YINYANG[day_master]
    ke_wuxing = WUXING_KE[dm_wuxing]  # 日主克的五行 = 财

    zhengcai = ""
    piancai = ""
    for gan, wx in TIANGAN_WUXING.items():
        if wx == ke_wuxing:
            if TIANGAN_YINYANG[gan] != dm_yinyang:
                zhengcai = gan  # 异性为正财
            else:
                piancai = gan   # 同性为偏财
    return zhengcai, piancai


# ============================================================
# Assertion Precondition Engine
# ============================================================

class AssertionEngine:
    """Assertion Precondition Engine — 只消费结构化数据, 不重新排盘"""

    def __init__(self):
        # 定义 Golden Assertion #1
        self.assertion = AssertionDef(
            id="ASSERT-001",
            source="传统命理断语 (五部经典组成部分有原典依据, 完整断言原文待精确溯源)",
            canonical_text="财星透干，逢流年合之，主进财。",
            description="命局中财星透干, 逢流年天干与该财星构成天干五合, 主进财。",
        )

    def _build_evidence(self) -> EvidenceEntry:
        """构建 Evidence 层"""
        return EvidenceEntry(
            source_reference="《三命通会·论正财》《渊海子平·论正财》天干五合基础概念",
            source_text=(
                "《三命通会》论正财: '正财者，乃甲见己、乙见戊之例。受我克制，为我之妻...'"
                "《三命通会》看命口诀: '凡财一位，务要得时，富贵成家。'"
                "天干五合: 甲己合、乙庚合、丙辛合、丁壬合、戊癸合 (基础命理概念)"
            ),
            authority_status=EvidenceAuthority.CANDIDATE,
            component_evidence=[
                "财星: 《三命通会》《渊海子平》均有正财/偏财定义 (CONFIRMED)",
                "透干: 财星出现在天干为命理基础概念 (CONFIRMED)",
                "流年天干五合: 天干五合为基础命理概念, 有原典依据 (CONFIRMED)",
                "'主进财': 断语效果, 完整断言'财星透干逢流年合之主进财'未找到五部经典精确原文 (CANDIDATE)",
            ],
            notes=(
                "完整断言'财星透干，逢流年合之，主进财'未在五部经典中找到精确原文出处。"
                "各组成部分(财星、透干、流年五合)有原典依据, 但组合后的完整断语可能为后世归纳。"
                "因此Evidence层标为CANDIDATE, 不为了让断言命中而补充原典没有授权的条件。"
            ),
        )

    def _check_p1_caixing_tougan(self, chart: Dict, precond: Precondition):
        """P1: 财星透干检查 (只消费结构化数据, 不重新排盘)"""
        day_master = chart.get("day_master", "")
        tiangan = chart.get("tiangan", [])  # [年干, 月干, 日干, 时干]

        if not day_master or not tiangan:
            precond.state = PreconditionState.UNRESOLVED
            precond.failure_reason = "缺少日主或天干数据"
            return

        zhengcai, piancai = get_caixing(day_master)
        caixing_list = [zhengcai, piancai]

        # 检查财星是否透干 (出现在年干/月干/时干, 日干是日主本身不算)
        tougan_positions = []
        for i, gan in enumerate(tiangan):
            if i == 2:  # 日干是日主
                continue
            if gan in caixing_list:
                caixing_type = "正财" if gan == zhengcai else "偏财"
                pos_name = ["年干", "月干", "日干", "时干"][i]
                tougan_positions.append(f"{pos_name}{gan}({caixing_type})")

        if tougan_positions:
            precond.state = PreconditionState.SATISFIED
            precond.evidence = f"财星透干: {', '.join(tougan_positions)}"
            # 保存透干的财星天干, 供P3使用
            chart["_tougan_caixing"] = [tiangan[i] for i in range(4) if i != 2 and tiangan[i] in caixing_list]
        else:
            precond.state = PreconditionState.NOT_SATISFIED
            precond.failure_reason = f"财星({zhengcai}正财/{piancai}偏财)未透干, 仅可能藏于地支"
            chart["_tougan_caixing"] = []

    def _check_p2_liunian(self, liunian_gan: str, precond: Precondition):
        """P2: 流年存在检查"""
        if liunian_gan and liunian_gan in TIANGAN_WUXING:
            precond.state = PreconditionState.SATISFIED
            precond.evidence = f"流年天干: {liunian_gan}"
        else:
            precond.state = PreconditionState.NOT_SATISFIED
            precond.failure_reason = f"流年天干无效: {liunian_gan}"

    def _check_p3_wuhe(self, chart: Dict, liunian_gan: str, precond: Precondition):
        """P3: 流年干与财星天干五合检查 (五合≠合化, 只验证合的关系)"""
        tougan_caixing = chart.get("_tougan_caixing", [])

        if not tougan_caixing:
            precond.state = PreconditionState.NOT_SATISFIED
            precond.failure_reason = "无透干财星, 无法检查五合 (P1未满足)"
            return

        if not liunian_gan:
            precond.state = PreconditionState.NOT_SATISFIED
            precond.failure_reason = "流年天干无效"
            return

        # 检查流年天干与任一透干财星是否构成五合
        wuhe_matches = []
        for caixing_gan in tougan_caixing:
            key = (liunian_gan, caixing_gan)
            if key in TIANGAN_WUHE:
                wuhe_matches.append(f"流年{liunian_gan}与财星{caixing_gan}构成{TIANGAN_WUHE[key]}")

        if wuhe_matches:
            precond.state = PreconditionState.SATISFIED
            precond.evidence = "; ".join(wuhe_matches) + " [仅验证五合关系, 不判定合化]"
        else:
            precond.state = PreconditionState.NOT_SATISFIED
            caixing_str = "/".join(tougan_caixing)
            precond.failure_reason = f"流年{liunian_gan}与透干财星({caixing_str})不构成天干五合 (五合表: 甲己/乙庚/丙辛/丁壬/戊癸)"

    def evaluate(self, chart: Dict, liunian_gan: str) -> AssertionResult:
        """
        主评估入口
        chart: 结构化命局数据 (不重新排盘, 只消费)
          {
            "day_master": "庚",
            "tiangan": ["甲", "丙", "庚", "丁"],  # 年干月干日干时干
            "dizhi": [...],  # 可选
            ...
          }
        liunian_gan: 流年天干, 如 "己"
        """
        result = AssertionResult(
            assertion=self.assertion,
            evidence=self._build_evidence(),
            preconditions=PreconditionsLayer(),
            match=MatchLayer(),
            effect=EffectLayer(),
            conclusion=ConclusionLayer(),
            input_chart=chart,
            input_liunian=liunian_gan,
        )

        pc = result.preconditions

        # 检查三个前置条件 (独立检查, 不模糊匹配)
        self._check_p1_caixing_tougan(chart, pc.p1_caixing_tougan)
        self._check_p2_liunian(liunian_gan, pc.p2_liunian_cunzai)
        self._check_p3_wuhe(chart, liunian_gan, pc.p3_wuhe)

        # Matcher
        match = result.match
        failed = pc.get_failed()
        unresolved = pc.get_unresolved()

        if failed:
            match.matched = False
            match.failed_conditions = [f"{p.pid} {p.name}: {p.failure_reason}" for p in failed]
            match.match_details = "前置条件不满足, 断言不匹配"
        elif unresolved:
            match.matched = False
            match.unresolved_conditions = [f"{p.pid} {p.name}: 无法确定" for p in unresolved]
            match.match_details = "前置条件无法确定, 断言待确认"
        else:
            match.matched = True
            match.match_details = (
                f"P1: {pc.p1_caixing_tougan.evidence}; "
                f"P2: {pc.p2_liunian_cunzai.evidence}; "
                f"P3: {pc.p3_wuhe.evidence}"
            )

        # Effect 层 (单独存储, 不把原文直接变成 财星+五合=进财)
        effect = result.effect
        effect.source_authorized_effect = "主进财"
        effect.effect_qualifiers = [
            "此效果为断语文本, 具体进财程度/条件/时间需更多原典授权",
            "五合仅验证'合'的关系, 不判定'合化'",
            "Evidence层为CANDIDATE, 完整断言原文待精确溯源",
        ]
        effect.notes = "Effect层单独存储, 保留完整证据链, 不简化为 财星+五合=进财"

        # Conclusion 层
        conclusion = result.conclusion
        if not match.matched:
            if failed:
                conclusion.result = MatchResult.NOT_MATCHED
                conclusion.reason = f"前置条件不满足: {'; '.join(match.failed_conditions)}"
            else:
                conclusion.result = MatchResult.UNRESOLVED
                conclusion.reason = f"前置条件无法确定: {'; '.join(match.unresolved_conditions)}"
        else:
            # 所有前置条件满足, 但Evidence为CANDIDATE
            if result.evidence.authority_status == EvidenceAuthority.CONFIRMED:
                conclusion.result = MatchResult.ASSERTION_CONFIRMED
                conclusion.reason = "所有前置条件满足, Evidence原典明确授权"
            elif result.evidence.authority_status in [EvidenceAuthority.CANDIDATE, EvidenceAuthority.PARTIALLY_AUTHORIZED]:
                conclusion.result = MatchResult.ASSERTION_QUALIFIED
                conclusion.reason = (
                    "所有前置条件满足, 但Evidence为CANDIDATE "
                    "(完整断言'财星透干逢流年合之主进财'未找到五部经典精确原文, "
                    "各组成部分有原典依据)。断言有条件成立, 需更多原典溯源确认。"
                )
            else:
                conclusion.result = MatchResult.UNRESOLVED
                conclusion.reason = "Evidence原典依据不足"

        # 证据链
        conclusion.evidence_chain = [
            f"ASSERTION: {result.assertion.canonical_text}",
            f"EVIDENCE: {result.evidence.authority_status.value} - {result.evidence.notes}",
            f"P1 财星透干: {pc.p1_caixing_tougan.state.value} - {pc.p1_caixing_tougan.evidence or pc.p1_caixing_tougan.failure_reason}",
            f"P2 流年存在: {pc.p2_liunian_cunzai.state.value} - {pc.p2_liunian_cunzai.evidence or pc.p2_liunian_cunzai.failure_reason}",
            f"P3 流年干与财星五合: {pc.p3_wuhe.state.value} - {pc.p3_wuhe.evidence or pc.p3_wuhe.failure_reason}",
            f"MATCH: {'MATCHED' if match.matched else 'NOT_MATCHED'} - {match.match_details}",
            f"EFFECT: {effect.source_authorized_effect} (qualifiers: {'; '.join(effect.effect_qualifiers)})",
            f"CONCLUSION: {conclusion.result.value} - {conclusion.reason}",
        ]

        return result


# ============================================================
# 测试案例
# ============================================================

def run_tests():
    """运行测试案例: 1个命中 + 2个非命中, 证明不是关键词搜索而是结构化匹配"""

    engine = AssertionEngine()

    print("=" * 100)
    print("STR-001A P6.2-A Assertion Precondition Engine")
    print("Golden Assertion #1: 财星透干，逢流年合之，主进财。")
    print("=" * 100)
    print()
    print("6条锁定规则:")
    print("  1. Assertion Engine不重新排盘, 只消费Canonical State / Relation State")
    print("  2. '财星透干'与'流年合之'是两个独立Preconditions")
    print("  3. 五合≠合化, 只验证'合'的关系")
    print("  4. '主进财'作为Assertion Effect/Conclusion单独存储")
    print("  5. 缺任一前置条件→NOT_MATCHED, 不能模糊匹配")
    print("  6. 证据不足→INSUFFICIENT_SOURCE / UNRESOLVED")
    print()

    # 先输出 Assertion 定义和 Evidence
    print("─" * 100)
    print("ASSERTION 定义")
    print("─" * 100)
    a = engine.assertion
    print(f"  ID: {a.id}")
    print(f"  Source: {a.source}")
    print(f"  Canonical Text: {a.canonical_text}")
    print(f"  Description: {a.description}")

    print()
    print("─" * 100)
    print("EVIDENCE 层")
    print("─" * 100)
    e = engine._build_evidence()
    print(f"  Source Reference: {e.source_reference}")
    print(f"  Authority Status: {e.authority_status.value}")
    print(f"  Component Evidence:")
    for ce in e.component_evidence:
        print(f"    - {ce}")
    print(f"  Notes: {e.notes}")

    # 测试案例1: 命中案例
    print()
    print("=" * 100)
    print("测试案例1: 命中案例 (财星透干 + 流年五合)")
    print("=" * 100)
    # 日主庚金, 财星甲木(偏财)透干在年干, 流年己土, 甲己合
    chart1 = {
        "day_master": "庚",
        "tiangan": ["甲", "丙", "庚", "丁"],  # 年干甲(偏财), 月干丙, 日干庚(日主), 时干丁
        "dizhi": ["辰", "子", "午", "亥"],
    }
    liunian1 = "己"  # 甲己合
    print(f"  命局: 甲辰 丙子 庚午 丁亥")
    print(f"  日主: 庚金 | 财星: 甲木(偏财, 庚金克甲木)")
    print(f"  财星透干: 年干甲(偏财) ✓")
    print(f"  流年: 己土年 | 甲己合 ✓")
    print()

    result1 = engine.evaluate(chart1, liunian1)
    _print_result(result1)

    # 测试案例2: 非命中案例 (财星不透干)
    print()
    print("=" * 100)
    print("测试案例2: 非命中案例 (财星不透干 → P1 NOT_SATISFIED)")
    print("=" * 100)
    # 日主庚金, 财星甲木只在藏干不透干, 流年己土
    chart2 = {
        "day_master": "庚",
        "tiangan": ["戊", "丙", "庚", "丁"],  # 年干戊(偏印), 月干丙, 日干庚, 时干丁 — 无财星透干
        "dizhi": ["辰", "子", "午", "亥"],  # 辰中藏乙(正财), 但不透干
    }
    liunian2 = "己"
    print(f"  命局: 戊辰 丙子 庚午 丁亥")
    print(f"  日主: 庚金 | 财星: 甲木(偏财)/乙木(正财)")
    print(f"  财星透干: 天干无甲/乙 ✗ (辰中藏乙但不透干)")
    print(f"  流年: 己土年")
    print()

    result2 = engine.evaluate(chart2, liunian2)
    _print_result(result2)

    # 测试案例3: 非命中案例 (流年不五合 → P3 NOT_SATISFIED)
    print()
    print("=" * 100)
    print("测试案例3: 非命中案例 (流年天干与财星不五合 → P3 NOT_SATISFIED)")
    print("=" * 100)
    # 日主庚金, 财星甲木透干, 流年丙火(甲与丙不五合)
    chart3 = {
        "day_master": "庚",
        "tiangan": ["甲", "丙", "庚", "丁"],  # 年干甲(偏财)透干
        "dizhi": ["辰", "子", "午", "亥"],
    }
    liunian3 = "丙"  # 甲与丙不五合 (甲己合才是)
    print(f"  命局: 甲辰 丙子 庚午 丁亥")
    print(f"  日主: 庚金 | 财星: 甲木(偏财)透干 ✓")
    print(f"  流年: 丙火年 | 甲与丙不构成天干五合 ✗ (五合表: 甲己/乙庚/丙辛/丁壬/戊癸)")
    print()

    result3 = engine.evaluate(chart3, liunian3)
    _print_result(result3)

    # 汇总
    print()
    print("=" * 100)
    print("测试汇总")
    print("=" * 100)
    print(f"  案例1 (命中): {result1.conclusion.result.value}")
    print(f"  案例2 (财星不透干): {result2.conclusion.result.value}")
    print(f"  案例3 (流年不五合): {result3.conclusion.result.value}")
    print()
    print(f"  关键验证:")
    print(f"    1. 案例1 P1/P2/P3全部SATISFIED → ASSERTION_QUALIFIED (不是关键词搜索, 是结构化匹配)")
    print(f"    2. 案例2 P1 NOT_SATISFIED (财星不透干) → NOT_MATCHED (缺任一前置条件即不匹配)")
    print(f"    3. 案例3 P3 NOT_SATISFIED (流年不五合) → NOT_MATCHED (五合≠合化, 只验证合的关系)")
    print(f"    4. 所有案例Effect层单独存储'主进财', 不简化为 财星+五合=进财")
    print(f"    5. Evidence层为CANDIDATE (完整断言未找到五部经典精确原文), 不为命中补授权")
    print(f"    6. Assertion Engine只消费结构化数据(day_master/tiangan), 不重新排盘")
    print()
    print("P6.2-A Assertion Precondition Engine 完成.")
    print("下一步: 可扩展更多断言, 或对ASSERT-001进行原典精确溯源以提升Evidence授权等级.")
    print("=" * 100)


def _print_result(result: AssertionResult):
    """打印单个断言结果"""
    pc = result.preconditions
    print(f"  ┌─ PRECONDITIONS")
    print(f"  │   P1 财星透干: {pc.p1_caixing_tougan.state.value}")
    print(f"  │     {pc.p1_caixing_tougan.evidence or pc.p1_caixing_tougan.failure_reason}")
    print(f"  │   P2 流年存在: {pc.p2_liunian_cunzai.state.value}")
    print(f"  │     {pc.p2_liunian_cunzai.evidence or pc.p2_liunian_cunzai.failure_reason}")
    print(f"  │   P3 流年干与财星五合: {pc.p3_wuhe.state.value}")
    print(f"  │     {pc.p3_wuhe.evidence or pc.p3_wuhe.failure_reason}")
    print(f"  ├─ MATCH: {'MATCHED' if result.match.matched else 'NOT_MATCHED'}")
    print(f"  │   {result.match.match_details}")
    print(f"  ├─ EFFECT: {result.effect.source_authorized_effect}")
    print(f"  │   qualifiers: {'; '.join(result.effect.effect_qualifiers)}")
    print(f"  └─ CONCLUSION: {result.conclusion.result.value}")
    print(f"      {result.conclusion.reason}")


# ============================================================
# 主执行
# ============================================================

if __name__ == "__main__":
    run_tests()
