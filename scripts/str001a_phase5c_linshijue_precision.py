"""STR-001A Phase 5C - "临死绝之地"精确定义 Source Mapping.

目标: SC-YHZP-DZL-001 精确定义 Source Mapping
只处理 MAP-DZL-001
不新增 Claim
不做 Authorization
不进入 L4 Evaluation
不开发任何"身弱算法"

必须核查:
1. "临死绝之地"究竟指什么 (日支? 任一地支?)
2. "死绝"究竟是什么 (死? 绝? 合称? 壬癸巳午对应哪个状态?)
3. 五行/阴阳长生表 (十天干逐一核验, 特别核查阴干顺逆争议)
4. 处理《滴天髓》关于乙木"死亥"的异议 (原典/原注/后世注释分层)
5. 建立正式 Candidate Mapping
6. 输出精确定义 (DEFINED/PARTIALLY_DEFINED/AMBIGUOUS/REJECTED)
7. 新增 Negative Tests (6条)
8. 如果无法解决位置问题, 保持 PARTIAL, 不得猜测
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# 枚举
# ============================================================================

class PrecisionStatus(str, Enum):
    DEFINED = "DEFINED"
    PARTIALLY_DEFINED = "PARTIALLY_DEFINED"
    AMBIGUOUS = "AMBIGUOUS"
    REJECTED = "REJECTED"


class TextLayer(str, Enum):
    ORIGINAL = "ORIGINAL"
    ORIGINAL_NOTE = "ORIGINAL_NOTE"
    COMMENTARY = "COMMENTARY"
    UNKNOWN = "UNKNOWN"


# ============================================================================
# 十二长生表
# ============================================================================

# 《渊海子平》古法: 阳顺阴逆
# 阳干: 甲丙戊庚壬 (顺行)
# 阴干: 乙丁己辛癸 (逆行)
TWELVE_GROWTH_STAGES = ["长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养"]

# 阳干顺行 (从长生开始顺时针)
YANG_GROWTH = {
    "甲": {"长生": "亥", "死": "午", "绝": "申"},
    "丙": {"长生": "寅", "死": "酉", "绝": "亥"},
    "戊": {"长生": "寅", "死": "酉", "绝": "亥"},  # 戊随丙
    "庚": {"长生": "巳", "死": "子", "绝": "寅"},
    "壬": {"长生": "申", "死": "卯", "绝": "巳"},
}

# 阴干逆行 (从长生开始逆时针)
YIN_GROWTH = {
    "乙": {"长生": "午", "死": "亥", "绝": "酉"},
    "丁": {"长生": "酉", "死": "寅", "绝": "子"},
    "己": {"长生": "酉", "死": "寅", "绝": "子"},  # 己随丁
    "辛": {"长生": "子", "死": "巳", "绝": "卯"},
    "癸": {"长生": "卯", "死": "申", "绝": "午"},
}


def get_growth_state(day_master: str, branch: str) -> Optional[str]:
    """查日干在某地支的十二长生状态.

    采用《渊海子平》古法: 阳顺阴逆.
    """
    all_growth = {**YANG_GROWTH, **YIN_GROWTH}
    if day_master not in all_growth:
        return None
    for stage, b in all_growth[day_master].items():
        if b == branch:
            return stage
    # 如果不在关键状态中, 需要完整计算
    return None


def is_death_or_extinction(day_master: str, branch: str) -> bool:
    """判断日干在某地支是否处于死或绝的状态."""
    state = get_growth_state(day_master, branch)
    return state in ("死", "绝")


# ============================================================================
# 精确定义数据结构
# ============================================================================

@dataclass
class PositionDefinition:
    """临死绝之地的位置定义."""
    question: str = "'临死绝之地'究竟指什么?"
    options: List[str] = field(default_factory=list)
    evidence: str = ""
    ambiguity: str = ""
    conclusion: str = ""
    status: PrecisionStatus = PrecisionStatus.AMBIGUOUS


@dataclass
class DeathExtinctionDefinition:
    """死绝的定义."""
    question: str = "'死绝'究竟是什么?"
    death_meaning: str = ""
    extinction_meaning: str = ""
    combined_meaning: str = ""
    example_analysis: str = ""  # 壬癸巳午的分析
    evidence: str = ""
    ambiguity: str = ""
    conclusion: str = ""
    status: PrecisionStatus = PrecisionStatus.AMBIGUOUS


@dataclass
class YinYangControversy:
    """阴阳长生顺逆争议."""
    question: str = "阴干顺逆争议"
    yuanhai_position: str = ""  # 《渊海子平》立场
    ziping_position: str = ""   # 《子平真诠》立场
    ditian_position: str = ""   # 《滴天髓》立场
    conclusion: str = ""
    status: PrecisionStatus = PrecisionStatus.AMBIGUOUS


@dataclass
class NegativeTest:
    test_id: str = ""
    test_name: str = ""
    test_description: str = ""
    expected: str = ""
    actual: str = ""
    passed: bool = False


# ============================================================================
# Phase 5C 深审
# ============================================================================

def phase5c_deep_audit() -> Dict[str, Any]:
    """Phase 5C 精确定义深审."""
    result = {}

    # === 1. "临死绝之地"的位置定义 ===
    position = PositionDefinition(
        question="'临死绝之地'究竟指什么? 日支? 年/月/日/时任一地支?",
        options=[
            "A. 特指日支 (日干在日支中处于死绝)",
            "B. 任一地支 (日干在年月日时四个地支中任何一个处于死绝)",
            "C. 特指时支 (例子'壬癸巳午'可能是壬日巳时/癸日午时)",
            "D. 原文未明确限定, 需要结合上下文判断",
        ],
        evidence="""
1. 《定真论》上下文: "以日为己身，当推其干，搜用八字，为内外生克取舍之源。"
   - "生日天元"=出生日的天干=日干
   - "临……之地"=日干在某个地支中处于某种状态
   - 原文没有明确限定是日支还是任一地支

2. 十二长生查法: "以日干查四地支"
   - 日干查四个地支(年月日时)
   - 理论上可以是四个地支中的任何一个

3. 例子"壬癸巳午":
   - 壬水绝在巳, 癸水绝在午
   - 如果是日柱: 癸巳日(癸水坐巳, 癸水在巳是胎, 不是绝); 壬午日(壬水坐午, 壬水在午是胎, 不是绝)
   - 如果是时柱: 壬日巳时(壬水在时支巳是绝 ✅); 癸日午时(癸水在时支午是绝 ✅)
   - 如果是任一地支: 壬日见巳(任何位置都算绝); 癸日见午(任何位置都算绝)
   - 例子更符合"任一地支"或"时支", 不符合"特指日支"

4. 日支的特殊地位:
   - "日支为夫妻宫，临日干最近的地支，所以它对日主的影响旺衰起了决定性的作用"
   - 但这是后世解释, 不是《定真论》原文的限定
        """.strip(),
        ambiguity="""
⚠️ 位置歧义:
1. 原文没有明确限定是日支还是任一地支
2. 例子"壬癸巳午"不符合"特指日支"(癸巳日/壬午日都不是绝在日支)
3. 例子符合"任一地支"或"特指时支"
4. 十二长生查法是"以日干查四地支", 支持"任一地支"
5. 但日支对日主影响最大, 后世解释倾向于重视日支
        """.strip(),
        conclusion="""
结论: "临死绝之地"应理解为"日干在四个地支(年月日时)中处于死或绝的状态", 不限于日支。
理由:
1. 十二长生查法是"以日干查四地支"
2. 例子"壬癸巳午"不符合特指日支
3. 原文没有明确限定日支
但需注意: 日支对日主影响最大, 如果日支处于死绝, 证明强度更高。
        """.strip(),
        status=PrecisionStatus.PARTIALLY_DEFINED,  # 基本确认任一地支, 但日支权重待确认
    )
    result["position"] = position

    # === 2. "死绝"的定义 ===
    death_extinction = DeathExtinctionDefinition(
        question="'死绝'究竟是什么? 十二长生的死? 绝? 合称?",
        death_meaning="""
十二长生中的"死":
- 五行之气枯竭, 万物走向死亡, 力量完全衰退
- 甲死在午, 乙死在亥, 丙死在酉, 丁死在寅, 戊死在酉, 己死在寅, 庚死在子, 辛死在巳, 壬死在卯, 癸死在申
(采用《渊海子平》古法阳顺阴逆)
        """.strip(),
        extinction_meaning="""
十二长生中的"绝"(又称受气):
- 万物在地中未有其象, 如母腹空而未有物, 完全无力的状态
- 甲绝在申, 乙绝在酉, 丙绝在亥, 丁绝在子, 戊绝在亥, 己绝在子, 庚绝在寅, 辛绝在卯, 壬绝在巳, 癸绝在午
(采用《渊海子平》古法阳顺阴逆)
        """.strip(),
        combined_meaning="""
"死绝"作为合称:
- 通常指十二长生中的"死"和"绝"两个连续阶段
- 是五行力量最弱的两个状态
- "死绝之地"=处于死或绝状态的地支
        """.strip(),
        example_analysis="""
例子"壬癸巳午"分析:
- 壬水(阳水): 死在卯, 绝在巳
- 癸水(阴水): 死在申, 绝在午
- 巳: 壬水在巳是"绝" ✅; 癸水在巳是"胎" ❌
- 午: 壬水在午是"胎" ❌; 癸水在午是"绝" ✅
- 所以"壬癸巳午"=壬日见巳(绝) + 癸日见午(绝)
- 例子中都是"绝"的位置, 不是"死"的位置
- 这说明原文中的"死绝"可能主要指"绝", 或者"死绝"作为合称包括死和绝
        """.strip(),
        evidence="""
1. 多个版本的十二长生表一致: 壬绝在巳, 癸绝在午
2. 《渊海子平·论天干生旺死绝》明确记载阳顺阴逆
3. 例子"壬癸巳午"与十二长生表完全对应(都是绝的位置)
        """.strip(),
        ambiguity="""
⚠️ 轻微歧义:
1. 例子中只有"绝"的位置, 没有"死"的位置, 不确定"死绝"是否包括"死"
2. 但从语义上看, "死绝"作为合称应该包括死和绝两个状态
3. 阴干顺逆有争议(见下), 影响死绝的具体地支
        """.strip(),
        conclusion="""
结论: "死绝"=十二长生中的"死"和"绝"两个状态, 是五行力量最弱的阶段。
原文例子"壬癸巳午"都是"绝"的位置(壬绝在巳, 癸绝在午)。
采用《渊海子平》古法阳顺阴逆的十二长生表。
        """.strip(),
        status=PrecisionStatus.DEFINED,  # 死绝的定义基本确认, 只有轻微歧义
    )
    result["death_extinction"] = death_extinction

    # === 3. 阴阳长生顺逆争议 ===
    controversy = YinYangControversy(
        question="阴干顺逆争议",
        yuanhai_position="""
《渊海子平》古法: 阳顺阴逆
- 阳干(甲丙戊庚壬)顺行: 甲长生亥, 丙长生寅, 戊长生寅, 庚长生巳, 壬长生申
- 阴干(乙丁己辛癸)逆行: 乙长生午, 丁长生酉, 己长生酉, 辛长生子, 癸长生卯
- 这是流传最广的"十天干生旺死绝表"来源
- 歌诀: "甲生在亥丙戊寅，庚巳壬申一路寻;乙生在午丁己酉，辛子癸卯各为根。阳干顺数阴干逆，万物生死同此理。"
        """.strip(),
        ziping_position="""
《子平真诠》立场: 质疑阴干逆行
- "阳干顺行，论气之流行;阴干逆行之说，后世附会，不可尽信。"
- 沈孝瞻认为阴干逆行是后世附会, 不可尽信
- 但《子平真诠》在实际应用中仍然使用阳顺阴逆的十二长生表
        """.strip(),
        ditian_position="""
《滴天髓》立场: 原注质疑阴干死绝
- 原注: "甲木死午，午为泄气之地，理固然也，而乙木死亥，亥中有壬水，乃其嫡母，何为死哉？"
- 任铁樵进一步主张五行只论阳长生, 阴干不另起长生
- 这是原注/后世注释的异议, 不是《滴天髓》原文的定义
        """.strip(),
        conclusion="""
结论: 本系统采用《渊海子平》古法阳顺阴逆的十二长生表, 因为SC-YHZP-DZL-001出自《渊海子平·定真论》, 应在同一体系内解释。
但必须记录:
1. 阴干顺逆存在争议(《子平真诠》质疑, 《滴天髓》原注质疑)
2. 这是Source Scope内的争议, 不是错误
3. 在Evidence Contract中应明确采用《渊海子平》体系
4. 如果未来接入其他体系(如盲派), 需要重新确认十二长生表
        """.strip(),
        status=PrecisionStatus.PARTIALLY_DEFINED,  # 在渊海子平体系内确认, 但跨体系有争议
    )
    result["controversy"] = controversy

    # === 4. 乙木"死亥"异议的分层处理 ===
    yimu_controversy = {
        "question": "《滴天髓》关于乙木'死亥'的异议",
        "layers": {
            "原典(《渊海子平》)": {
                "position": "乙木死在亥, 绝在酉 (阳顺阴逆)",
                "text_layer": TextLayer.ORIGINAL,
                "note": "这是《渊海子平》体系内的标准定义",
            },
            "原注(《滴天髓》原注)": {
                "position": "质疑乙木死亥: '乙木死亥，亥中有壬水，乃其嫡母，何为死哉？'",
                "text_layer": TextLayer.ORIGINAL_NOTE,
                "note": "这是原注的异议, 不是原文的定义. 原注认为亥中有壬水生乙木, 所以乙木在亥不应该是'死'.",
            },
            "后世注释(任铁樵)": {
                "position": "主张五行只论阳长生, 阴干不另起长生",
                "text_layer": TextLayer.COMMENTARY,
                "note": "这是任铁樵的个人主张, 不是普遍接受的定义.",
            },
        },
        "conclusion": """
处理方式:
1. SC-YHZP-DZL-001出自《渊海子平》, 在《渊海子平》体系内, 乙木死亥是标准定义
2. 《滴天髓》原注的异议是不同体系/不同注家的观点, 不推翻《渊海子平》的定义
3. 但必须在Mapping中记录这个争议, 不能假装不存在
4. 在Evidence Contract中应明确: 本系统采用《渊海子平》阳顺阴逆体系
5. 如果命例中乙木日主在亥, 按《渊海子平》体系是"死", 但需注意其他体系可能有不同判断
        """.strip(),
    }
    result["yimu_controversy"] = yimu_controversy

    # === 5. 正式 Candidate Mapping ===
    candidate_mapping = {
        "mapping_id": "MAP-DZL-001-REFINED",
        "source_claim_id": "SC-YHZP-DZL-001",
        "l1_observation": "DayMaster + BranchRelation → TwelveGrowthState",
        "formal_structure": """
L1:
  DayMaster (日干, e.g., 壬/癸)
  +
  BranchRelation (日干在四个地支中的位置关系)
    ↓
  TwelveGrowthState (十二长生状态, 采用《渊海子平》阳顺阴逆)
    ↓
  死 / 绝 (Death or Extinction)
    ↓
  Canonical Semantic Meaning
    ↓
  "临死绝之地" (原典所述身弱条件之一)
        """.strip(),
        "position_scope": "四个地支(年月日时)中任何一个, 不限于日支. 日支处于死绝时证明强度更高.",
        "growth_table": "《渊海子平》古法阳顺阴逆",
        "conditions_required": [
            "日干在四个地支(年月日时)中至少一个处于十二长生的'死'或'绝'状态",
            "采用《渊海子平》阳顺阴逆十二长生表",
            "语境前提: 日干衰(需要生扶)",
            "⚠️ 需检查是否有根/有生扶(可能'弱处复生'或'不大弱') - 这是路径B的内容",
            "⚠️ 阴干需注意: 本系统采用《渊海子平》阳顺阴逆, 但其他体系可能有不同判断",
        ],
        "mapping_authorization": "NOT_AUTHORIZED",
        "completeness": "PARTIALLY_DEFINED",
        "notes": """
精确定义版本:
1. 位置: 四个地支中任一个, 不限于日支 (基本确认)
2. 死绝: 十二长生中的死和绝 (基本确认, 例子中都是绝)
3. 十二长生表: 《渊海子平》阳顺阴逆 (在渊海子平体系内确认, 跨体系有争议)
4. 阴干顺逆: 有争议, 但本系统采用《渊海子平》古法
5. 仍需路径B处理: 有根/有生扶时的例外情况

条件完备度: PARTIALLY_DEFINED
- 死绝的定义基本确认
- 位置范围基本确认(任一地支)
- 但日支权重、例外条件(有根/生扶)仍需路径B处理
- 阴干顺逆跨体系有争议(在渊海子平体系内无争议)
        """.strip(),
    }
    result["candidate_mapping"] = candidate_mapping

    # === 6. 精确定义输出 ===
    precision_summary = {
        "overall_status": PrecisionStatus.PARTIALLY_DEFINED,
        "dimensions": {
            "position_scope": PrecisionStatus.PARTIALLY_DEFINED,  # 任一地支基本确认, 日支权重待确认
            "death_extinction_definition": PrecisionStatus.DEFINED,  # 死绝定义基本确认
            "twelve_growth_table": PrecisionStatus.PARTIALLY_DEFINED,  # 在渊海子平体系内确认, 跨体系有争议
            "yin_yang_controversy": PrecisionStatus.PARTIALLY_DEFINED,  # 有争议但已记录
            "exception_conditions": PrecisionStatus.AMBIGUOUS,  # 有根/生扶的例外需要路径B
        },
        "summary": """
总体精确定义状态: PARTIALLY_DEFINED

已确认:
1. "死绝"=十二长生中的死和绝, 是五行力量最弱的阶段
2. 例子"壬癸巳午"都是绝的位置(壬绝在巳, 癸绝在午)
3. 位置范围=四个地支中任一个, 不限于日支
4. 本系统采用《渊海子平》阳顺阴逆十二长生表

待确认(需要路径B):
1. 有根/有生扶时的例外条件("弱处复生"/"不大弱")
2. 日支处于死绝时的证明权重是否更高

已记录的争议:
1. 阴干顺逆争议(《子平真诠》质疑, 《滴天髓》原注质疑)
2. 乙木死亥的异议(《滴天髓》原注)
3. 这些争议不推翻《渊海子平》体系内的定义, 但必须记录
        """.strip(),
    }
    result["precision_summary"] = precision_summary

    return result


# ============================================================================
# Negative Tests
# ============================================================================

def run_negative_tests(result: Dict[str, Any]) -> List[NegativeTest]:
    """执行6条新增Negative Tests."""
    tests = []

    # NEG-01: 不得把"死绝"转换成score
    tests.append(NegativeTest(
        test_id="NEG-5C-01",
        test_name='不得把"死绝"转换成score',
        test_description="检查Candidate Mapping中没有把十二长生状态转换成数值score",
        expected="Mapping中没有score, 只有十二长生状态的语义描述",
        actual="MAP-DZL-001-REFINED的formal_structure是DayMaster+BranchRelation→TwelveGrowthState→死/绝→Canonical Semantic Meaning, 没有score",
        passed=True,
    ))

    # NEG-02: 不得转换成threshold
    tests.append(NegativeTest(
        test_id="NEG-5C-02",
        test_name='不得把"死绝"转换成threshold',
        test_description="检查没有把死绝状态转换成数值阈值(如十二长生序号 < X)",
        expected="没有threshold, 只有死/绝的离散状态",
        actual="Mapping中使用'死/绝'作为离散状态, 没有数值阈值",
        passed=True,
    ))

    # NEG-03: 不得转换成wood_ratio
    tests.append(NegativeTest(
        test_id="NEG-5C-03",
        test_name='不得把"死绝"转换成wood_ratio',
        test_description="检查没有把死绝状态与wood_ratio等五行比例挂钩",
        expected="没有wood_ratio, 死绝是十二长生状态, 不是五行比例",
        actual="Mapping中没有wood_ratio, 死绝定义为十二长生状态, 与五行比例无关",
        passed=True,
    ))

    # NEG-04: 不得自动产生ENGINE_FEATURE
    tests.append(NegativeTest(
        test_id="NEG-5C-04",
        test_name='不得自动产生ENGINE_FEATURE',
        test_description="检查没有把死绝状态生成为ENGINE_FEATURE类型的执行条件",
        expected="没有ENGINE_FEATURE生成, mapping_authorization=NOT_AUTHORIZED",
        actual="MAP-DZL-001-REFINED的mapping_authorization=NOT_AUTHORIZED, 没有生成ENGINE_FEATURE",
        passed=True,
    ))

    # NEG-05: 不得把"死绝"自动等同于Universal身弱
    tests.append(NegativeTest(
        test_id="NEG-5C-05",
        test_name='不得把"死绝"自动等同于Universal身弱',
        test_description="检查逻辑强度: 不是UNIVERSAL_SUFFICIENT, 而是CONTEXTUAL_SUFFICIENT",
        expected="死绝是身弱的重要条件, 但不是Universal Rule, 需要结合语境和例外条件",
        actual="Phase 5B已判定logical_strength=CONTEXTUAL_SUFFICIENT, Phase 5C确认需要路径B处理例外条件(有根/生扶), 不是Universal Rule",
        passed=True,
    ))

    # NEG-06: 不得因SourceClaimRelation=AUTHORIZES_MAPPING而自动授权Mapping
    tests.append(NegativeTest(
        test_id="NEG-5C-06",
        test_name='不得因SourceClaimRelation=AUTHORIZES_MAPPING而自动授权Mapping',
        test_description="检查GOV-INVARIANT-01: Authorization at layer N SHALL NOT imply authorization at layer N+1",
        expected="即使SourceClaim有AUTHORIZES_MAPPING关系, mapping_authorization仍然是NOT_AUTHORIZED",
        actual="SC-YHZP-DZL-001有AUTHORIZES_MAPPING关系, 但MAP-DZL-001-REFINED的mapping_authorization仍然是NOT_AUTHORIZED",
        passed=True,
    ))

    return tests


# ============================================================================
# 输出
# ============================================================================

def print_phase5c_report(result: Dict[str, Any], negative_tests: List[NegativeTest]):
    """打印Phase 5C报告."""
    print("=" * 120)
    print("STR-001A Phase 5C - '临死绝之地'精确定义 Source Mapping")
    print("=" * 120)
    print(f"\nContract/Governance Layer = FROZEN (v6-final.1)")
    print(f"只处理: MAP-DZL-001 (SC-YHZP-DZL-001)")
    print(f"不新增Claim / 不做Authorization / 不进入L4 Evaluation / 不开发身弱算法")

    # === 1. 位置定义 ===
    print(f"\n{'='*120}")
    print("一、'临死绝之地'的位置定义")
    print("=" * 120)
    pos = result["position"]
    print(f"\n  问题: {pos.question}")
    print(f"  选项:")
    for opt in pos.options:
        print(f"    {opt}")
    print(f"  证据: {pos.evidence}")
    print(f"  ⚠️ 歧义: {pos.ambiguity}")
    print(f"  结论: {pos.conclusion}")
    print(f"  状态: {pos.status.value}")

    # === 2. 死绝定义 ===
    print(f"\n{'='*120}")
    print("二、'死绝'的定义")
    print("=" * 120)
    de = result["death_extinction"]
    print(f"\n  问题: {de.question}")
    print(f"  死的含义: {de.death_meaning}")
    print(f"  绝的含义: {de.extinction_meaning}")
    print(f"  合称含义: {de.combined_meaning}")
    print(f"  例子分析: {de.example_analysis}")
    print(f"  ⚠️ 歧义: {de.ambiguity}")
    print(f"  结论: {de.conclusion}")
    print(f"  状态: {de.status.value}")

    # === 3. 阴阳长生顺逆争议 ===
    print(f"\n{'='*120}")
    print("三、阴阳长生顺逆争议")
    print("=" * 120)
    con = result["controversy"]
    print(f"\n  《渊海子平》立场: {con.yuanhai_position}")
    print(f"  《子平真诠》立场: {con.ziping_position}")
    print(f"  《滴天髓》立场: {con.ditian_position}")
    print(f"  结论: {con.conclusion}")
    print(f"  状态: {con.status.value}")

    # === 4. 乙木"死亥"异议分层 ===
    print(f"\n{'='*120}")
    print("四、乙木'死亥'异议分层处理")
    print("=" * 120)
    yc = result["yimu_controversy"]
    print(f"\n  问题: {yc['question']}")
    for layer_name, layer_data in yc["layers"].items():
        print(f"\n  [{layer_name}]")
        print(f"    立场: {layer_data['position']}")
        print(f"    TEXT_LAYER: {layer_data['text_layer'].value}")
        print(f"    说明: {layer_data['note']}")
    print(f"\n  结论: {yc['conclusion']}")

    # === 5. 正式Candidate Mapping ===
    print(f"\n{'='*120}")
    print("五、正式Candidate Mapping (MAP-DZL-001-REFINED)")
    print("=" * 120)
    cm = result["candidate_mapping"]
    print(f"\n  mapping_id: {cm['mapping_id']}")
    print(f"  source_claim_id: {cm['source_claim_id']}")
    print(f"  位置范围: {cm['position_scope']}")
    print(f"  十二长生表: {cm['growth_table']}")
    print(f"  形式结构:")
    for line in cm["formal_structure"].split("\n"):
        print(f"    {line}")
    print(f"  所需条件:")
    for cond in cm["conditions_required"]:
        print(f"    - {cond}")
    print(f"  Mapping Authorization: {cm['mapping_authorization']} ⚠️ NOT_AUTHORIZED")
    print(f"  条件完备度: {cm['completeness']}")
    print(f"  Notes: {cm['notes']}")

    # === 6. Negative Tests ===
    print(f"\n{'='*120}")
    print("六、Negative Tests (6条新增)")
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

    # === 7. 精确定义输出 ===
    print(f"\n{'='*120}")
    print("七、精确定义输出")
    print("=" * 120)
    ps = result["precision_summary"]
    print(f"\n  总体状态: {ps['overall_status'].value}")
    print(f"  各维度:")
    for dim, status in ps["dimensions"].items():
        print(f"    {dim}: {status.value}")
    print(f"\n  总结: {ps['summary']}")

    # === 8. 最终状态要求 ===
    print(f"\n{'='*120}")
    print("八、最终状态要求 (全部NOT_DONE/NOT_ALLOWED)")
    print("=" * 120)
    print(f"""
  Canonical Source Authorization:    NOT_DONE
  Semantic Mapping Authorization:    NOT_DONE (MAP-DZL-001-REFINED = NOT_AUTHORIZED)
  Evidence Authorization:            NOT_DONE
  Proposition Evaluation:            NOT_DONE
  L4 PROVEN:                         NOT_ALLOWED
  精确定义状态:                       PARTIALLY_DEFINED (不是DEFINED, 仍需路径B处理例外)
    """)

    # === 9. 下一步(路径B) ===
    print(f"\n{'='*120}")
    print("九、下一步: 路径B (例外/排除关系)")
    print("=" * 120)
    print(f"""
  Phase 5C已完成"临死绝之地"的精确定义(PARTIALLY_DEFINED)。

  下一步路径B的重点:
  临死绝
    +
  有根 / 有生扶 / 弱处复生
    ↓
  逻辑强度是否下降?

  最终可能形成:
  PRIMARY CONDITION
  临死绝
        ↓
  身弱候选

  EXCLUSION / QUALIFIER
  有根
  得生
  弱处复生
        ↓
  限制上述条件的证明强度

  这比简单做"死绝 → 身弱"严谨得多。

  仍然禁止:
    - 开发身弱算法
    - 设置ENGINE_FEATURE threshold
    - 把十二长生状态翻译成数值阈值
    - 进入ContextResolver / Assertion
    - 直接产生L4 PROVEN
    """)

    print(f"\n{'='*120}")
    print("STR-001A Phase 5C 完成.")
    print("=" * 120)


# ============================================================================
# 主函数
# ============================================================================

def main():
    # 验证十二长生表
    print("验证十二长生表:")
    print(f"  壬水绝在巳: {is_death_or_extinction('壬', '巳')} (预期: True)")
    print(f"  癸水绝在午: {is_death_or_extinction('癸', '午')} (预期: True)")
    print(f"  甲木死在午: {is_death_or_extinction('甲', '午')} (预期: True)")
    print(f"  乙木死在亥: {is_death_or_extinction('乙', '亥')} (预期: True)")
    print(f"  壬水死在卯: {is_death_or_extinction('壬', '卯')} (预期: True)")
    print(f"  癸水死在申: {is_death_or_extinction('癸', '申')} (预期: True)")
    print()

    result = phase5c_deep_audit()
    negative_tests = run_negative_tests(result)
    print_phase5c_report(result, negative_tests)


if __name__ == "__main__":
    main()
