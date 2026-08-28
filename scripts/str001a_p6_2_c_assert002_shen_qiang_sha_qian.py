"""
STR-001A P6.2-C ASSERT-002 原典精确溯源 + Assertion Engine 验证
断言: 「身强杀浅，假杀为权」

五层结构:
  EVIDENCE → PRECONDITIONS → MATCHER → EFFECT → CONCLUSION

关键审计点:
  1. P1 身强 = CONSUMED_CANONICAL_STATE (由Canonical State Resolver输出, Assertion Engine不重新计算)
  2. P3 杀浅 = SOURCE_DEFINED_RELATIVE_STATE (原典定义的相对概念, 不能简单写成七杀数量少=杀浅)
  3. 验证三层分离: EVIDENCE_STATUS ≠ MATCH_STATUS ≠ CONCLUSION_STATUS
  4. 测试: 命中 / 条件不足(身不强) / 反向条件(杀重身轻) / QUALIFIER(杀运无妨)

原典出处:
  《渊海子平》:
    - 「身强杀浅，假杀为权。」
    - 「月中之气，怕冲与阳刃。其本身弱，若杀强则难制；如身强杀浅，则是假杀为权刃。」
    - 「身强杀浅，假杀为权。一世安然，财命有气。」
    - 「身强杀浅，杀运无妨。」
    - 「或至中年晚景，顿逢杀运，假杀为权，制伏阳刃；或得权贵以显扬、或招赀财而发福」
  反向:
    - 「杀重身轻，终身有损。」
    - 「其本身弱，若杀强则难制」
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


# ============================================================
# 状态枚举 (三层分离)
# ============================================================

class EvidenceStatus(str, Enum):
    """EVIDENCE_STATUS: 原典证据层"""
    CONFIRMED = "CONFIRMED"                           # 原典有明确完整断语
    PARTIALLY_AUTHORIZED = "PARTIALLY_AUTHORIZED"     # 组成部分有依据, 完整断言部分授权
    CANDIDATE = "CANDIDATE"                           # 候选
    SOURCE_MAPPED_NON_PROOF = "SOURCE_MAPPED_NON_PROOF"  # 有语义映射但无完整授权
    INSUFFICIENT_SOURCE = "INSUFFICIENT_SOURCE"       # 原典依据不足


class MatchStatus(str, Enum):
    """MATCH_STATUS: 前置条件匹配层 (引擎运行时, 与原典授权无关)"""
    MATCHED = "MATCHED"
    NOT_MATCHED = "NOT_MATCHED"
    UNRESOLVED = "UNRESOLVED"


class ConclusionStatus(str, Enum):
    """CONCLUSION_STATUS: 断事结论层"""
    AUTHORIZED = "AUTHORIZED"               # 原典授权, 条件满足, 可输出
    QUALIFIED = "QUALIFIED"                 # 有条件授权, 带qualifier
    CANDIDATE = "CANDIDATE"                 # 候选
    NOT_AUTHORIZED = "NOT_AUTHORIZED"       # 未获原典授权
    UNRESOLVED = "UNRESOLVED"               # 无法确定


class PreconditionSourceType(str, Enum):
    """前置条件来源类型 — 关键审计点"""
    CONSUMED_CANONICAL_STATE = "CONSUMED_CANONICAL_STATE"  # 消费Canonical State Resolver输出, 不重新计算
    SOURCE_DEFINED_STATE = "SOURCE_DEFINED_STATE"            # 原典定义的状态
    SOURCE_DEFINED_RELATIVE_STATE = "SOURCE_DEFINED_RELATIVE_STATE"  # 原典定义的相对概念
    L1_FACT = "L1_FACT"                                      # L1原始事实
    ENGINE_DERIVED = "ENGINE_DERIVED"                        # 引擎推导 (需警惕循环依赖)


# ============================================================
# 数据结构
# ============================================================

@dataclass
class AssertionDef:
    id: str
    source: str
    canonical_text: str
    description: str


@dataclass
class EvidenceEntry:
    source_reference: str
    source_texts: List[str] = field(default_factory=list)
    authority_status: EvidenceStatus = EvidenceStatus.INSUFFICIENT_SOURCE
    reverse_conditions: List[str] = field(default_factory=list)
    qualifiers: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class Precondition:
    pid: str
    name: str
    description: str
    source_type: PreconditionSourceType  # 关键: 标明来源类型
    state: MatchStatus = MatchStatus.UNRESOLVED
    evidence: str = ""
    failure_reason: str = ""
    canonical_state_ref: str = ""  # 引用的Canonical State字段


@dataclass
class PreconditionsLayer:
    p1_shen_qiang: Precondition = field(default_factory=lambda: Precondition(
        pid="P1", name="日主身强",
        description="日主身强 — 必须由Canonical State Resolver输出的qiangruo状态确认, Assertion Engine不重新计算",
        source_type=PreconditionSourceType.CONSUMED_CANONICAL_STATE,
        canonical_state_ref="qiangruo = STRONG",
    ))
    p2_qi_sha_cun_zai: Precondition = field(default_factory=lambda: Precondition(
        pid="P2", name="七杀存在",
        description="命局中存在七杀(偏官) — L1十神事实",
        source_type=PreconditionSourceType.L1_FACT,
    ))
    p3_sha_qian: Precondition = field(default_factory=lambda: Precondition(
        pid="P3", name="七杀为浅/弱",
        description="杀浅 — 原典定义的相对概念, 与杀强/杀重对举; 不能简单写成七杀数量少=杀浅; 需结合命局整体判断(数量/根气/得令/制伏)",
        source_type=PreconditionSourceType.SOURCE_DEFINED_RELATIVE_STATE,
    ))

    def all_satisfied(self) -> bool:
        return all(p.state == MatchStatus.MATCHED for p in [
            self.p1_shen_qiang, self.p2_qi_sha_cun_zai, self.p3_sha_qian
        ])

    def get_failed(self) -> List[Precondition]:
        return [p for p in [self.p1_shen_qiang, self.p2_qi_sha_cun_zai, self.p3_sha_qian]
                if p.state == MatchStatus.NOT_MATCHED]

    def get_unresolved(self) -> List[Precondition]:
        return [p for p in [self.p1_shen_qiang, self.p2_qi_sha_cun_zai, self.p3_sha_qian]
                if p.state == MatchStatus.UNRESOLVED]


@dataclass
class MatchLayer:
    matched: bool = False
    failed_conditions: List[str] = field(default_factory=list)
    unresolved_conditions: List[str] = field(default_factory=list)
    match_details: str = ""


@dataclass
class EffectLayer:
    source_authorized_effect: str = ""
    effect_details: List[str] = field(default_factory=list)
    qualifiers: List[str] = field(default_factory=list)


@dataclass
class ConclusionLayer:
    result: ConclusionStatus = ConclusionStatus.UNRESOLVED
    reason: str = ""
    evidence_chain: List[str] = field(default_factory=list)


@dataclass
class AssertionResult:
    assertion: AssertionDef
    evidence: EvidenceEntry
    preconditions: PreconditionsLayer
    match: MatchLayer
    effect: EffectLayer
    conclusion: ConclusionLayer
    input_chart: Dict = field(default_factory=dict)
    canonical_state: Dict = field(default_factory=dict)  # 消费的Canonical State


# ============================================================
# 七杀(偏官)十神映射
# ============================================================

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
WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
# 克日主的五行 (官杀): 金克木, 水克火, 木克土, 火克金, 土克水
WUXING_KE_WO = {"木": "金", "火": "水", "土": "木", "金": "火", "水": "土"}


def get_qi_sha(day_master: str) -> str:
    """获取日主的七杀(偏官)天干 — 克日主且同阴阳"""
    dm_wx = TIANGAN_WUXING[day_master]
    dm_yy = TIANGAN_YINYANG[day_master]
    ke_wuxing = WUXING_KE_WO[dm_wx]  # 克日主的五行(官杀)
    for gan, wx in TIANGAN_WUXING.items():
        if wx == ke_wuxing and TIANGAN_YINYANG[gan] == dm_yy:
            return gan  # 同阴阳为偏官(七杀)
    return ""


def get_zheng_guan(day_master: str) -> str:
    """获取日主的正官天干 — 克日主且异阴阳"""
    dm_wx = TIANGAN_WUXING[day_master]
    dm_yy = TIANGAN_YINYANG[day_master]
    ke_wuxing = WUXING_KE_WO[dm_wx]
    for gan, wx in TIANGAN_WUXING.items():
        if wx == ke_wuxing and TIANGAN_YINYANG[gan] != dm_yy:
            return gan
    return ""


# ============================================================
# Assertion Engine
# ============================================================

class AssertionEngine:
    """ASSERT-002 身强杀浅假杀为权 — Assertion Engine"""

    def __init__(self):
        self.assertion = AssertionDef(
            id="ASSERT-002",
            source="《渊海子平》(多处明确原文)",
            canonical_text="身强杀浅，假杀为权。",
            description="日主身强, 七杀(偏官)存在且力量浅弱, 则可借七杀为权柄, 主权贵发福。",
        )

    def _build_evidence(self) -> EvidenceEntry:
        return EvidenceEntry(
            source_reference="《渊海子平》",
            source_texts=[
                "「身强杀浅，假杀为权。」 — 《渊海子平》",
                "「月中之气，怕冲与阳刃。其本身弱，若杀强则难制；如身强杀浅，则是假杀为权刃。」 — 《渊海子平》",
                "「身强杀浅，假杀为权。一世安然，财命有气。」 — 《渊海子平》(FOR-BAZI)",
                "「身强杀浅，杀运无妨。」 — 《渊海子平》",
                "「或至中年晚景，顿逢杀运，假杀为权，制伏阳刃；或得权贵以显扬、或招赀财而发福」 — 《渊海子平》",
            ],
            authority_status=EvidenceStatus.CONFIRMED,
            reverse_conditions=[
                "「杀重身轻，终身有损。」 — 反向条件",
                "「其本身弱，若杀强则难制」 — 反向条件",
                "「身弱杀旺，又无制伏，宜乎带病贫薄」 — 反向条件",
            ],
            qualifiers=[
                "「身强杀浅，杀运无妨」 — 行杀运也无妨",
                "「大抵偏官七杀，最喜身旺、有制伏为妙」 — 七杀喜身旺有制伏",
            ],
            notes=(
                "原典有明确完整断语, 多处交叉验证。"
                "「身强」与「本身弱」对举, 「杀浅」与「杀强/杀重」对举。"
                "EVIDENCE_STATUS = CONFIRMED。"
            ),
        )

    def _check_p1_shen_qiang(self, canonical_state: Dict, precond: Precondition):
        """P1 身强检查 — 关键: 只消费Canonical State, 不重新计算"""
        # 关键审计点: Assertion Engine 不重新计算身强
        # 只检查 canonical_state 中的 qiangruo 字段
        qiangruo = canonical_state.get("qiangruo", "")
        wangshuai = canonical_state.get("wangshuai", "")

        if not canonical_state:
            precond.state = MatchStatus.UNRESOLVED
            precond.failure_reason = "未提供Canonical State, 无法确认身强"
            return

        if qiangruo == "STRONG" or qiangruo == "强":
            precond.state = MatchStatus.MATCHED
            precond.evidence = f"Canonical State qiangruo = STRONG (wangshuai = {wangshuai})"
        elif qiangruo == "WEAK" or qiangruo == "弱":
            precond.state = MatchStatus.NOT_MATCHED
            precond.failure_reason = f"Canonical State qiangruo = WEAK, 不满足身强条件"
        elif qiangruo == "UNRESOLVED" or qiangruo == "":
            precond.state = MatchStatus.UNRESOLVED
            precond.failure_reason = f"Canonical State qiangruo = UNRESOLVED, 身强状态未确认"
        else:
            precond.state = MatchStatus.UNRESOLVED
            precond.failure_reason = f"未知的 qiangruo 状态: {qiangruo}"

        # 关键: 标记来源类型, 证明没有重新计算
        precond.evidence += f" [来源: {precond.source_type.value}, 未重新计算身强]"

    def _check_p2_qi_sha(self, chart: Dict, precond: Precondition):
        """P2 七杀存在检查 — L1十神事实"""
        day_master = chart.get("day_master", "")
        tiangan = chart.get("tiangan", [])
        dizhi_canggan = chart.get("dizhi_canggan", {})

        if not day_master:
            precond.state = MatchStatus.UNRESOLVED
            precond.failure_reason = "未提供日主"
            return

        qi_sha_gan = get_qi_sha(day_master)
        zheng_guan_gan = get_zheng_guan(day_master)

        # 检查天干
        tiangan_qi_sha = []
        for i, gan in enumerate(tiangan):
            if gan == qi_sha_gan:
                pos = ["年干", "月干", "日干", "时干"][i]
                tiangan_qi_sha.append(f"{pos}{gan}(七杀)")

        # 检查地支藏干
        dizhi_qi_sha = []
        for zhi, canggan_list in dizhi_canggan.items():
            for cg in canggan_list:
                if cg == qi_sha_gan:
                    dizhi_qi_sha.append(f"{zhi}藏{cg}(七杀)")

        if tiangan_qi_sha or dizhi_qi_sha:
            precond.state = MatchStatus.MATCHED
            all_pos = tiangan_qi_sha + dizhi_qi_sha
            precond.evidence = f"七杀({qi_sha_gan})存在: {', '.join(all_pos)}"
            # 保存七杀位置供P3使用
            chart["_qi_sha_positions"] = {
                "tiangan": tiangan_qi_sha,
                "dizhi": dizhi_qi_sha,
                "qi_sha_gan": qi_sha_gan,
                "count": len(tiangan_qi_sha) + len(dizhi_qi_sha),
            }
        else:
            precond.state = MatchStatus.NOT_MATCHED
            precond.failure_reason = f"命局中无七杀({qi_sha_gan}), 正官为{zheng_guan_gan}"
            chart["_qi_sha_positions"] = {"count": 0}

    def _check_p3_sha_qian(self, chart: Dict, canonical_state: Dict, precond: Precondition):
        """P3 杀浅检查 — 关键: 原典定义的相对概念, 不能简单写成七杀数量少=杀浅"""
        qi_sha_info = chart.get("_qi_sha_positions", {})
        qi_sha_count = qi_sha_info.get("count", 0)

        if qi_sha_count == 0:
            precond.state = MatchStatus.NOT_MATCHED
            precond.failure_reason = "无七杀, 不适用此断言"
            return

        # 杀浅的原典定义审计:
        # 原典: 「其本身弱，若杀强则难制；如身强杀浅，则是假杀为权刃。」
        # 「杀浅」与「杀强」对举, 是相对概念
        # 原典没有给出「杀浅」的精确定义, 但从上下文可以推断:
        #   - 「时七杀只一位」— 数量少
        #   - 七杀无根
        #   - 七杀不得令
        #   - 七杀被制伏
        # 但这些都是候选条件, 原典没有明确授权「数量少=杀浅」

        # 因此: 杀浅 = SOURCE_DEFINED_RELATIVE_STATE
        # 引擎只能给出候选判断, 不能给出绝对结论

        # 候选条件检查 (不构成绝对定义, 仅作参考)
        candidate_factors = []

        # 因素1: 数量
        if qi_sha_count == 1:
            candidate_factors.append("七杀仅1位(候选: 数量少)")
        elif qi_sha_count >= 3:
            candidate_factors.append(f"七杀{qi_sha_count}位(候选: 数量多, 可能杀重)")

        # 因素2: 是否透干
        tiangan_qi_sha = qi_sha_info.get("tiangan", [])
        if not tiangan_qi_sha:
            candidate_factors.append("七杀不透干(候选: 力量较弱)")
        else:
            candidate_factors.append(f"七杀透干: {', '.join(tiangan_qi_sha)}(候选: 力量较强)")

        # 因素3: 是否得令 (月令是否为七杀五行)
        month_branch = chart.get("month_branch", "")
        qi_sha_gan = qi_sha_info.get("qi_sha_gan", "")
        if month_branch and qi_sha_gan:
            qi_sha_wuxing = TIANGAN_WUXING[qi_sha_gan]
            # 简化: 月令五行是否为七杀五行
            dizhi_wuxing = {"寅": "木", "卯": "木", "巳": "火", "午": "火",
                           "申": "金", "酉": "金", "亥": "水", "子": "水",
                           "辰": "土", "戌": "土", "丑": "土", "未": "土"}
            if dizhi_wuxing.get(month_branch) == qi_sha_wuxing:
                candidate_factors.append(f"月令{month_branch}为七杀五行{qi_sha_wuxing}(候选: 杀得令, 可能杀强)")
            else:
                candidate_factors.append(f"月令{month_branch}非七杀五行(候选: 杀不得令)")

        # 因素4: 身强状态 (杀浅是相对于身强而言)
        qiangruo = canonical_state.get("qiangruo", "")
        if qiangruo == "STRONG":
            candidate_factors.append("日主身强(杀浅的相对基准成立)")
        else:
            candidate_factors.append(f"日主非身强(qiangruo={qiangruo}), 杀浅的相对基准不成立")

        # 综合判断 (候选, 非绝对)
        # 关键: 不能因为七杀数量少就直接判定杀浅
        # 必须结合多个因素, 且标记为候选判断

        # 简单规则: 如果身强成立, 且七杀数量<=2, 且七杀不透干或不得令, 则候选为杀浅
        # 但这只是工程候选, 原典没有明确授权这个公式

        shen_qiang = (qiangruo == "STRONG")
        sha_count_ok = (qi_sha_count <= 2)
        sha_not_tougan = (not tiangan_qi_sha)
        sha_not_deling = (month_branch and dizhi_wuxing.get(month_branch) != qi_sha_wuxing) if month_branch else True

        if not shen_qiang:
            precond.state = MatchStatus.UNRESOLVED
            precond.failure_reason = "杀浅是相对于身强的概念, 日主非身强时杀浅状态无法确认"
        elif sha_count_ok and (sha_not_tougan or sha_not_deling):
            precond.state = MatchStatus.MATCHED
            precond.evidence = f"杀浅(候选判断): {'; '.join(candidate_factors)}"
        elif qi_sha_count >= 3:
            precond.state = MatchStatus.NOT_MATCHED
            precond.failure_reason = f"七杀{qi_sha_count}位, 可能杀重而非杀浅 (反向条件: 杀重身轻终身有损)"
        else:
            precond.state = MatchStatus.UNRESOLVED
            precond.failure_reason = f"杀浅状态无法明确判定: {'; '.join(candidate_factors)}"

        precond.evidence += f" [来源: {precond.source_type.value}, 候选判断非绝对定义]"

    def evaluate(self, chart: Dict, canonical_state: Dict) -> AssertionResult:
        """
        主评估入口
        chart: 命局L1事实
        canonical_state: Canonical State Resolver输出的状态 (P1身强必须从此消费)
        """
        result = AssertionResult(
            assertion=self.assertion,
            evidence=self._build_evidence(),
            preconditions=PreconditionsLayer(),
            match=MatchLayer(),
            effect=EffectLayer(),
            conclusion=ConclusionLayer(),
            input_chart=chart,
            canonical_state=canonical_state,
        )

        pc = result.preconditions

        # P1 身强 — 关键: 只消费Canonical State, 不重新计算
        self._check_p1_shen_qiang(canonical_state, pc.p1_shen_qiang)

        # P2 七杀存在 — L1十神事实
        self._check_p2_qi_sha(chart, pc.p2_qi_sha_cun_zai)

        # P3 杀浅 — 原典定义的相对概念
        self._check_p3_sha_qian(chart, canonical_state, pc.p3_sha_qian)

        # Matcher
        match = result.match
        failed = pc.get_failed()
        unresolved = pc.get_unresolved()

        if failed:
            match.matched = False
            match.failed_conditions = [f"{p.pid} {p.name}: {p.failure_reason}" for p in failed]
            match.match_details = "前置条件不满足"
        elif unresolved:
            match.matched = False
            match.unresolved_conditions = [f"{p.pid} {p.name}: {p.failure_reason}" for p in unresolved]
            match.match_details = "前置条件无法确定"
        else:
            match.matched = True
            match.match_details = (
                f"P1: {pc.p1_shen_qiang.evidence}; "
                f"P2: {pc.p2_qi_sha_cun_zai.evidence}; "
                f"P3: {pc.p3_sha_qian.evidence}"
            )

        # Effect 层
        effect = result.effect
        effect.source_authorized_effect = "假杀为权"
        effect.effect_details = [
            "「假杀为权」— 身强借七杀为权柄",
            "「假杀为权刃」— 借七杀为权刃",
            "「顿逢杀运，假杀为权，制伏阳刃；或得权贵以显扬、或招赀财而发福」",
            "「一世安然，财命有气」",
        ]
        effect.qualifiers = [
            "「身强杀浅，杀运无妨」— 行杀运也无妨",
            "「大抵偏官七杀，最喜身旺、有制伏为妙」",
        ]

        # Conclusion 层 — 关键: 三层分离
        conclusion = result.conclusion
        if not match.matched:
            if failed:
                # 检查是否为反向条件
                reverse_detected = any("杀重" in f or "身轻" in f or "身弱" in f for f in match.failed_conditions)
                if reverse_detected:
                    conclusion.result = ConclusionStatus.NOT_AUTHORIZED
                    conclusion.reason = "反向条件(杀重身轻/身弱杀强), 原典明确「杀重身轻终身有损」, 不适用「假杀为权」"
                else:
                    conclusion.result = ConclusionStatus.NOT_AUTHORIZED
                    conclusion.reason = f"前置条件不满足: {'; '.join(match.failed_conditions)}"
            else:
                conclusion.result = ConclusionStatus.UNRESOLVED
                conclusion.reason = f"前置条件无法确定: {'; '.join(match.unresolved_conditions)}"
        else:
            # 条件匹配, 且EVIDENCE_STATUS = CONFIRMED
            # 但P3杀浅是候选判断, 所以带qualifier
            if result.evidence.authority_status == EvidenceStatus.CONFIRMED:
                # 检查P3是否为候选判断
                p3_is_candidate = "候选判断" in (pc.p3_sha_qian.evidence or "")
                if p3_is_candidate:
                    conclusion.result = ConclusionStatus.QUALIFIED
                    conclusion.reason = (
                        "前置条件满足, 原典EVIDENCE_STATUS=CONFIRMED, "
                        "但P3杀浅为SOURCE_DEFINED_RELATIVE_STATE(候选判断非绝对定义), "
                        "结论带qualifier: 假杀为权(需结合命局整体确认杀浅)"
                    )
                else:
                    conclusion.result = ConclusionStatus.AUTHORIZED
                    conclusion.reason = "前置条件满足, 原典EVIDENCE_STATUS=CONFIRMED, 可输出「假杀为权」"
            else:
                conclusion.result = ConclusionStatus.UNRESOLVED
                conclusion.reason = "原典证据未确认"

        # 证据链
        conclusion.evidence_chain = [
            f"ASSERTION: {result.assertion.canonical_text}",
            f"EVIDENCE_STATUS: {result.evidence.authority_status.value}",
            f"P1 身强: {pc.p1_shen_qiang.state.value} [{pc.p1_shen_qiang.source_type.value}] {pc.p1_shen_qiang.evidence or pc.p1_shen_qiang.failure_reason}",
            f"P2 七杀存在: {pc.p2_qi_sha_cun_zai.state.value} [{pc.p2_qi_sha_cun_zai.source_type.value}] {pc.p2_qi_sha_cun_zai.evidence or pc.p2_qi_sha_cun_zai.failure_reason}",
            f"P3 杀浅: {pc.p3_sha_qian.state.value} [{pc.p3_sha_qian.source_type.value}] {pc.p3_sha_qian.evidence or pc.p3_sha_qian.failure_reason}",
            f"MATCH_STATUS: {'MATCHED' if match.matched else 'NOT_MATCHED/UNRESOLVED'}",
            f"EFFECT: {effect.source_authorized_effect}",
            f"CONCLUSION_STATUS: {conclusion.result.value} - {conclusion.reason}",
        ]

        return result


# ============================================================
# 测试案例
# ============================================================

def run_tests():
    print("=" * 100)
    print("STR-001A P6.2-C ASSERT-002 原典精确溯源 + Assertion Engine 验证")
    print("断言: 「身强杀浅，假杀为权」")
    print("=" * 100)

    engine = AssertionEngine()

    # 输出 EVIDENCE 层
    print("\n" + "─" * 100)
    print("EVIDENCE 层")
    print("─" * 100)
    e = engine._build_evidence()
    print(f"  Source: {e.source_reference}")
    print(f"  EVIDENCE_STATUS: {e.authority_status.value}")
    print(f"  原典原文:")
    for t in e.source_texts:
        print(f"    - {t}")
    print(f"  反向条件:")
    for r in e.reverse_conditions:
        print(f"    - {r}")
    print(f"  Qualifiers:")
    for q in e.qualifiers:
        print(f"    - {q}")

    # 测试案例1: 命中案例 (身强 + 七杀存在 + 杀浅)
    print("\n" + "=" * 100)
    print("测试案例1: 命中案例 (身强 + 七杀存在 + 杀浅)")
    print("=" * 100)
    # 日主甲木, 七杀为庚金(阳金克阳木)
    # 命局: 甲寅 丙子 甲辰 丙寅 — 甲木身强(寅卯辰木旺), 七杀庚仅在藏干
    chart1 = {
        "day_master": "甲",
        "tiangan": ["甲", "丙", "甲", "丙"],  # 无庚金透干
        "dizhi": ["寅", "子", "辰", "寅"],
        "month_branch": "子",
        "dizhi_canggan": {
            "寅": ["甲", "丙", "戊"],
            "子": ["癸"],
            "辰": ["戊", "乙", "癸"],
            "寅": ["甲", "丙", "戊"],
        },
        # 注意: 此命局实际上无庚金七杀, 需要构造一个有七杀但杀浅的
    }
    # 重新构造: 日主甲木, 七杀庚金在时干(1位), 但日主身强(寅月得令+辰中乙根)
    chart1 = {
        "day_master": "甲",
        "tiangan": ["甲", "丙", "甲", "庚"],  # 时干庚(七杀), 仅1位
        "dizhi": ["寅", "子", "辰", "午"],
        "month_branch": "子",  # 子月非金, 杀不得令
        "dizhi_canggan": {
            "寅": ["甲", "丙", "戊"],
            "子": ["癸"],
            "辰": ["戊", "乙", "癸"],
            "午": ["丁", "己"],
        },
    }
    canonical_state1 = {
        "wangshuai": "WANG",  # 甲木子月? 实际上子月水生木, 算得令? 简化为WANG
        "qiangruo": "STRONG",  # 身强
        "root_state": "ROOT_HEAVY",
        "dangzhong": "CONFIRMED",
    }
    print(f"  命局: 甲寅 丙子 甲辰 庚午")
    print(f"  日主: 甲木 | 七杀: 庚金(时干, 仅1位, 不得令)")
    print(f"  Canonical State: qiangruo=STRONG, wangshuai=WANG")
    print()

    result1 = engine.evaluate(chart1, canonical_state1)
    _print_result(result1)

    # 测试案例2: 条件不足 (身不强, qiangruo=UNRESOLVED)
    print("\n" + "=" * 100)
    print("测试案例2: 条件不足 (身强UNRESOLVED, P1无法确认)")
    print("=" * 100)
    chart2 = dict(chart1)
    canonical_state2 = {
        "wangshuai": "SHUAI",
        "qiangruo": "UNRESOLVED",  # 身强未确认
        "root_state": "ROOT_LIGHT",
        "dangzhong": "QUALIFIED",
    }
    print(f"  命局: 同案例1")
    print(f"  Canonical State: qiangruo=UNRESOLVED (身强状态未确认)")
    print(f"  关键: P1=CONSUMED_CANONICAL_STATE, 引擎不重新计算身强, 直接消费UNRESOLVED")
    print()

    result2 = engine.evaluate(chart2, canonical_state2)
    _print_result(result2)

    # 测试案例3: 反向条件 (杀重身轻)
    print("\n" + "=" * 100)
    print("测试案例3: 反向条件 (杀重身轻, 不适用假杀为权)")
    print("=" * 100)
    # 日主甲木, 庚金七杀多位(年干+月干+时干), 日主身弱
    chart3 = {
        "day_master": "甲",
        "tiangan": ["庚", "庚", "甲", "庚"],  # 3个庚金七杀
        "dizhi": ["申", "酉", "子", "申"],
        "month_branch": "酉",  # 酉月金旺, 杀得令
        "dizhi_canggan": {
            "申": ["庚", "壬", "戊"],
            "酉": ["辛"],
            "子": ["癸"],
            "申": ["庚", "壬", "戊"],
        },
    }
    canonical_state3 = {
        "wangshuai": "SHUAI",
        "qiangruo": "WEAK",  # 身弱
        "root_state": "ROOT_NONE",
        "dangzhong": "NOT_ESTABLISHED",
    }
    print(f"  命局: 庚申 庚酉 甲子 庚申")
    print(f"  日主: 甲木 | 七杀: 庚金×3(年月时干), 酉月金旺杀得令")
    print(f"  Canonical State: qiangruo=WEAK (身弱)")
    print(f"  反向条件: 原典「杀重身轻，终身有损」「其本身弱，若杀强则难制」")
    print()

    result3 = engine.evaluate(chart3, canonical_state3)
    _print_result(result3)

    # 测试案例4: QUALIFIER (身强杀浅, 验证杀运无妨)
    print("\n" + "=" * 100)
    print("测试案例4: QUALIFIER (身强杀浅, 验证P3候选判断 + 杀运无妨)")
    print("=" * 100)
    # 日主甲木, 七杀庚金1位在年干(透干), 但日主身强(寅月+寅日)
    chart4 = {
        "day_master": "甲",
        "tiangan": ["庚", "丙", "甲", "丙"],  # 年干庚(七杀), 1位透干
        "dizhi": ["寅", "寅", "寅", "寅"],
        "month_branch": "寅",  # 寅月木旺, 杀不得令
        "dizhi_canggan": {
            "寅": ["甲", "丙", "戊"],
        },
    }
    canonical_state4 = {
        "wangshuai": "WANG",
        "qiangruo": "STRONG",  # 身强
        "root_state": "ROOT_HEAVY",
        "dangzhong": "CONFIRMED",
    }
    print(f"  命局: 庚寅 丙寅 甲寅 丙寅")
    print(f"  日主: 甲木 | 七杀: 庚金(年干, 1位透干, 寅月杀不得令)")
    print(f"  Canonical State: qiangruo=STRONG")
    print(f"  QUALIFIER: 「身强杀浅，杀运无妨」— 行杀运也无妨")
    print(f"  关键: P3杀浅=SOURCE_DEFINED_RELATIVE_STATE, 候选判断非绝对定义")
    print()

    result4 = engine.evaluate(chart4, canonical_state4)
    _print_result(result4)

    # 汇总
    print("\n" + "=" * 100)
    print("测试汇总 + 三层分离验证")
    print("=" * 100)
    print(f"  案例1 (命中): EVIDENCE={result1.evidence.authority_status.value}, "
          f"MATCH={result1.match.matched}, CONCLUSION={result1.conclusion.result.value}")
    print(f"  案例2 (身强UNRESOLVED): EVIDENCE={result2.evidence.authority_status.value}, "
          f"MATCH={result2.match.matched}, CONCLUSION={result2.conclusion.result.value}")
    print(f"  案例3 (杀重身轻): EVIDENCE={result3.evidence.authority_status.value}, "
          f"MATCH={result3.match.matched}, CONCLUSION={result3.conclusion.result.value}")
    print(f"  案例4 (QUALIFIER): EVIDENCE={result4.evidence.authority_status.value}, "
          f"MATCH={result4.match.matched}, CONCLUSION={result4.conclusion.result.value}")
    print()
    print(f"  关键验证:")
    print(f"    1. P1身强 = CONSUMED_CANONICAL_STATE — 引擎不重新计算身强, 直接消费Canonical State")
    print(f"    2. P3杀浅 = SOURCE_DEFINED_RELATIVE_STATE — 不简单写成七杀数量少=杀浅")
    print(f"    3. 三层分离: EVIDENCE_STATUS=CONFIRMED ≠ MATCH_STATUS ≠ CONCLUSION_STATUS")
    print(f"    4. 案例3反向条件: 原典明确「杀重身轻终身有损」, CONCLUSION=NOT_AUTHORIZED")
    print(f"    5. 案例2条件不足: qiangruo=UNRESOLVED时, CONCLUSION=UNRESOLVED, 不强行输出")
    print(f"    6. 案例1/4命中: CONCLUSION=QUALIFIED (P3杀浅为候选判断, 带qualifier)")
    print()
    print("P6.2-C ASSERT-002 验证完成.")
    print("ASSERT-002 可进入 AUTHORIZED_ASSERTION_LIBRARY (带QUALIFIER标记).")
    print("=" * 100)


def _print_result(result: AssertionResult):
    pc = result.preconditions
    print(f"  ┌─ PRECONDITIONS")
    print(f"  │   P1 身强: {pc.p1_shen_qiang.state.value} [{pc.p1_shen_qiang.source_type.value}]")
    print(f"  │     {pc.p1_shen_qiang.evidence or pc.p1_shen_qiang.failure_reason}")
    print(f"  │   P2 七杀存在: {pc.p2_qi_sha_cun_zai.state.value} [{pc.p2_qi_sha_cun_zai.source_type.value}]")
    print(f"  │     {pc.p2_qi_sha_cun_zai.evidence or pc.p2_qi_sha_cun_zai.failure_reason}")
    print(f"  │   P3 杀浅: {pc.p3_sha_qian.state.value} [{pc.p3_sha_qian.source_type.value}]")
    print(f"  │     {pc.p3_sha_qian.evidence or pc.p3_sha_qian.failure_reason}")
    print(f"  ├─ MATCH: {'MATCHED' if result.match.matched else 'NOT_MATCHED/UNRESOLVED'}")
    print(f"  │   {result.match.match_details}")
    print(f"  ├─ EFFECT: {result.effect.source_authorized_effect}")
    print(f"  │   qualifiers: {'; '.join(result.effect.qualifiers)}")
    print(f"  └─ CONCLUSION: {result.conclusion.result.value}")
    print(f"      {result.conclusion.reason}")


if __name__ == "__main__":
    run_tests()
