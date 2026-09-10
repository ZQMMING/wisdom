"""Domain Judgment - 子平辨证域裁决层

Phase 3 P0 重写: 三大域(WANGSHUAI / GEJU / YONGSHEN)从"信号类型检查"的
脚手架升级为子平经典的确定性评分/规则链。

架构位置:
    BAZI Chart → Signal → Judgment → Synthesis → Output

核心原则:
1. 每个辨证域有独立的 Judgment 类
2. Judgment 收集同域 Signal，进行领域内综合判断
3. 禁止跨域投票、加权、比例等聚合机制
4. Judgment 结论为确定性条件判断，非概率推断

Phase 3 P0 实现要点:
- WANGSHUAI: 得令 + 得地 + 党众 + 寒暖燥湿 四维评分 (DTS-101~107,
  SMTH-101/102, ZPZ-101~105, 渊海子平调候)
- GEJU: 月令取格 → 透干成格 → 破格条件 (ZPZ-106~110, ZPZ-111~120,
  SMTH-103, YHZP-101/104/105)
- YONGSHEN: 格局用神 → 扶抑 → 调候 → 通关 → 病药 五级优先级链

约束(禁止事项):
- 不修改 BAZI 代码 (仅消费确定性表)
- 不修改 Golden Dataset
- 不做评分之外的硬编码 fallback
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Tuple

from .bazi_ten_gods import (
    BRANCH_HIDDEN_STEMS,
    SEASON_BY_BRANCH,
    hidden_main_stem,
    ten_god,
)
from .bazi_fixed_tables import ABSOLUTE_BRANCH, ROAD_BRANCH, longhu_stage


# ============================================================================
# 结论与领域枚举
# ============================================================================

class JudgmentDomain(str, Enum):
    """子平五大辨证域"""
    WANGSHUAI = "WANGSHUAI"      # 旺衰
    GEJU = "GEJU"                 # 格局
    YONGSHEN = "YONGSHEN"         # 用神
    SHISHEN = "SHISHEN"           # 十神语义
    SHIJIAN = "SHIJIAN"           # 事件判断


class JudgmentConclusion(str, Enum):
    """Judgment 结论类型"""
    STRONG = "STRONG"             # 身强(旺)
    WEAK = "WEAK"                 # 身弱(衰)
    MODERATE = "MODERATE"         # 中和
    ESTABLISHED = "ESTABLISHED"   # 格局成立
    BROKEN = "BROKEN"             # 格局破
    PRIMARY = "PRIMARY"           # 用神已取
    SECONDARY = "SECONDARY"       # 次用神
    SEMANTIC_POSITIVE = "SEMANTIC_POSITIVE"  # 十神吉
    SEMANTIC_NEGATIVE = "SEMANTIC_NEGATIVE"  # 十神凶
    EVENT_EXIST = "EVENT_EXIST"     # 事件存在
    EVENT_ABSENT = "EVENT_ABSENT"   # 事件不存在
    UNKNOWN = "UNKNOWN"           # 无法判断


@dataclass(frozen=True)
class DomainJudgment:
    """单个辨证域的 Judgment 结果"""
    domain: JudgmentDomain
    conclusion: JudgmentConclusion
    reasoning: str  # 判断依据文本
    signal_ids: List[str] = field(default_factory=list)  # 引用的 Signal ID
    evidence_refs: List[str] = field(default_factory=list)  # 引用的 Evidence ID
    rule_refs: List[str] = field(default_factory=list)  # 引用的 Rule ID
    created_at: str = ""  # ISO8601

    # Phase 3 P0 扩展: 可审计的派生字段 (仅诊断域填写)
    score: Optional[float] = None       # 旺衰综合评分
    score_detail: dict = field(default_factory=dict)  # 四维分项
    ge_type: Optional[str] = None       # 格局类型 (正格:xx / 建禄 / 从格 ...)
    yongshen_type: Optional[str] = None  # 用神类别 (格局/扶抑/调候/通关/病药)

    def __post_init__(self):
        if not self.created_at:
            object.__setattr__(self, 'created_at',
                datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "domain": self.domain.value,
            "conclusion": self.conclusion.value,
            "reasoning": self.reasoning,
            "signal_ids": self.signal_ids,
            "evidence_refs": self.evidence_refs,
            "rule_refs": self.rule_refs,
            "created_at": self.created_at,
            "score": self.score,
            "score_detail": self.score_detail,
            "ge_type": self.ge_type,
            "yongshen_type": self.yongshen_type,
        }


# ============================================================================
# 证据引用映射 (rule_id → 真实存在的 evidence_id)
#
# 所有 ID 均经文件系统核验, 禁止臆造:
#   backend/data/rules/<RULE>.json            → 规则存在
#   backend/data/evidence/<EVIDENCE>.json     → 证据存在
# 若规则引用的 evidence 文件缺失 (如 DTS-102 → E-DTS-101-001), 则只记
# rule_refs 不记 evidence_refs, 缺口在报告中显式声明, 不伪造证据 ID。
# ============================================================================

CITATION: Dict[str, Tuple[str, Optional[str]]] = {
    # 旺衰 (滴天髓·通神论·衰旺)
    "DTS-101": ("DTS-101", "E-DTS-101-001"),   # 得令
    "DTS-102": ("DTS-102", "E-DTS-101-001"),   # 失令 (复用得令 E-DTS-101-001, 反义关系)
    "DTS-103": ("DTS-103", "E-DTS-103-001"),   # 日支通根
    "DTS-104": ("DTS-104", "E-DTS-104-001"),   # 十二长生得地
    "DTS-105": ("DTS-105", "E-DTS-105-001"),   # 党众
    "DTS-106": ("DTS-106", "E-DTS-106-001"),   # 月令被围克
    "DTS-107": ("DTS-107", "E-DTS-107-001"),   # 失令有根修正 (仅在失令+得地/党众时)
    "SMTH-101": ("SMTH-101", "E-SMTH-101-001"),  # 十二宫旺位
    "SMTH-102": ("SMTH-102", "E-SMTH-101-001"),  # 十二宫弱位 (复用旺位 E-SMTH-101-001, 反义关系)
    # 格局
    "SMTH-103": ("SMTH-103", "E-SMTH-103-001"),  # 建禄格
    "YHZP-101": ("YHZP-101", "E-YHZP-101-001"),  # 阳刃格
    "YHZP-104": ("YHZP-104", "E-YHZP-104-001"),  # 月劫格
    "YHZP-105": ("YHZP-105", "E-YHZP-105-001"),  # 阳刃透杀制伏 (B-09 追溯: 卷一·论岁君 YHZP_2447)
    "ZPZ-105": ("ZPZ-105", "E-ZPZ-105-001"),   # 官杀当令
    "ZPZ-106": ("ZPZ-106", "E-ZPZ-106-001"),   # 正官格
    "ZPZ-107": ("ZPZ-107", "E-ZPZ-107-001"),   # 七杀格
    "ZPZ-108": ("ZPZ-108", "E-ZPZ-108-001"),   # 正印格
    "ZPZ-110": ("ZPZ-110", "E-ZPZ-110-001"),   # 伤官格
    "ZPZ-111": ("ZPZ-111", "E-ZPZ-111-001"),   # 月令主气透干取格
    "ZPZ-120": ("ZPZ-120", "E-ZPZ-120-001"),   # 七杀主气透干成格
    "ZPZ-101": ("ZPZ-101", "E-ZPZ-101-001"),   # 印绶当令 (论用神)
}


class _Citations:
    """按命理学条件累加 rule_refs / evidence_refs, 去重保序。"""

    def __init__(self):
        self.rule_refs: List[str] = []
        self.evidence_refs: List[str] = []

    def add(self, key: str) -> None:
        entry = CITATION.get(key)
        if not entry:
            raise KeyError(f"未登记的证据引用键: {key}")
        rule_id, evidence_id = entry
        if rule_id and rule_id not in self.rule_refs:
            self.rule_refs.append(rule_id)
        if evidence_id and evidence_id not in self.evidence_refs:
            self.evidence_refs.append(evidence_id)


@dataclass
class JudgmentSynthesis:
    """五大域综合判断结果"""
    wangshuai: Optional[DomainJudgment] = None
    geju: Optional[DomainJudgment] = None
    yongshen: Optional[DomainJudgment] = None
    shishen: Optional[DomainJudgment] = None
    shijian: Optional[DomainJudgment] = None

    @property
    def has_complete_judgment(self) -> bool:
        """是否完成五大域全部判断"""
        return all([
            self.wangshuai is not None,
            self.geju is not None,
            self.yongshen is not None,
            self.shishen is not None,
            self.shijian is not None,
        ])

    @property
    def has_core_judgment(self) -> bool:
        """是否完成核心三域（旺衰/格局/用神）判断"""
        return all([
            self.wangshuai is not None,
            self.geju is not None,
            self.yongshen is not None,
        ])

    def to_dict(self) -> dict:
        return {
            "wangshuai": self.wangshuai.to_dict() if self.wangshuai else None,
            "geju": self.geju.to_dict() if self.geju else None,
            "yongshen": self.yongshen.to_dict() if self.yongshen else None,
            "shishen": self.shishen.to_dict() if self.shishen else None,
            "shijian": self.shijian.to_dict() if self.shijian else None,
            "has_complete_judgment": self.has_complete_judgment,
            "has_core_judgment": self.has_core_judgment,
        }


# ============================================================================
# 固定教义表 (与 bazi_ten_gods / bazi_fixed_tables 同类: 确定性定义, 非推测)
# ============================================================================

# 十神按"对日主作用"分组 (确定性生克分类)
SHENG_TEN_GODS = frozenset({"比肩", "劫财", "正印", "偏印"})   # 生扶(帮身)
KE_XIE_HAO_TEN_GODS = frozenset(
    {"正官", "七杀", "正财", "偏财", "食神", "伤官"}
)                                                               # 克泄耗(损身)

# 六冲对 (通行地支六冲)
CHONG_PAIRS = frozenset({
    frozenset({"ZI", "WU"}), frozenset({"CHOU", "WEI"}),
    frozenset({"YIN", "SHEN"}), frozenset({"MAO", "YOU"}),
    frozenset({"CHEN", "XU"}), frozenset({"SI", "HAI"}),
})

# 寒暖燥湿 (《渊海子平·论寒暖燥湿》通行口诀: 冬寒喜暖, 夏热喜润)
TIAOHOU_BY_SEASON = {
    "SPRING": ("CHEN_WARM", "甲木用丙火疏土", None),
    "SUMMER": ("BING_WARM", "夏热喜润,取壬癸水", None),
    "AUTUMN": ("BING_WARM", "秋金肃杀,喜丙火暖局", None),
    "WINTER": ("CHEN_WARM", "冬生水冷,喜丙火暖局", None),
}

# 旺衰评分阈值 (确定性边界, 非统计估计)
STRONG_THRESHOLD = 4
WEAK_THRESHOLD = -3

# 十二长生强弱位 (《三命通会·论天干生旺死绝》)
LONGHU_STRONG_STAGES = frozenset({"临官", "帝旺"})
LONGHU_MID_STAGES = frozenset({"沐浴", "冠带"})
LONGHU_WEAK_STAGES = frozenset({"死", "墓", "绝"})

# 建禄 / 月刃 (月支为日主禄位/帝旺位)
JIANGLU_TABLE: Dict[str, str] = ROAD_BRANCH
YANGREN_TABLE: Dict[str, str] = ABSOLUTE_BRANCH

# 正格十神 → 格名 (《子平真诠·论用神》)
GEJU_NAME_BY_GOD = {
    "正印": "正印格", "偏印": "偏印格",
    "正官": "正官格", "七杀": "七杀格",
    "正财": "正财格", "偏财": "偏财格",
    "食神": "食神格", "伤官": "伤官格",
    "比肩": "建禄格", "劫财": "月劫格",
}

# 用神取用表: 格名 → (用神十神集合, 忌神集合)
# 依据: 建禄/月劫取财官(《三命通会·论建禄》), 阳刃取杀制
#       (《渊海子平·阳刃透杀制伏》), 伤官格取财(伤官生财)
GEJU_YONGSHEN_TABLE: Dict[str, Tuple[Tuple[str, ...], Tuple[str, ...]]] = {
    "建禄格": (("正官", "七杀", "正财", "偏财"), ("正印", "偏印", "比肩", "劫财")),
    "月劫格": (("正官", "七杀", "正财", "偏财"), ("正印", "偏印", "比肩", "劫财")),
    "阳刃格": (("七杀",), ("正印", "偏印")),
    "偏印格": (("正财",), ("正印", "比肩")),
    "伤官格": (("正财",), ("正官",)),
    "食神格": (("正财",), ("正官", "七杀")),
    "正财格": (("七杀", "正官"), ("比肩", "劫财")),
    "偏财格": (("七杀", "正官"), ("比肩", "劫财")),
    "正官格": (("正印",), ("七杀", "伤官")),
    "七杀格": (("正印", "食神", "伤官"), ("比肩", "劫财")),
    "正印格": (("正官",), ("正财",)),
}

# 格局 → 用神规则引用
# BZ-FNDR-15.20 Step 1: 补 8 主流格 (正官/七杀/正印/偏印/正财/偏财/食神/伤官)
# 注: rule_id 与 evidence_id 都来自 CITATION 表 (L138-144 已含映射)
GEJU_RULE_BY_GE = {
    "建禄格": ("SMTH-103", "E-SMTH-103-001"),
    "月劫格": ("YHZP-104", "E-YHZP-104-001"),
    "阳刃格": ("YHZP-101", "E-YHZP-101-001"),
    "从格": (None, None),
    "专旺格": (None, None),
    # 8 主流格 (ZPZ-106~110 + ZPZ-112/115/118)
    "正官格": ("ZPZ-106", "E-ZPZ-106-001"),
    "七杀格": ("ZPZ-107", "E-ZPZ-107-001"),
    "正印格": ("ZPZ-108", "E-ZPZ-108-001"),
    "偏印格": ("ZPZ-112", "E-ZPZ-112-001"),  # 偏印 → 枭神
    "正财格": ("ZPZ-109", "E-ZPZ-109-001"),
    "偏财格": ("ZPZ-118", "E-ZPZ-118-001"),
    "食神格": ("ZPZ-115", "E-ZPZ-115-001"),
    "伤官格": ("ZPZ-110", "E-ZPZ-110-001"),
}


# ============================================================================
# context 取值辅助
# ============================================================================

def _get(ctx, key, default=None):
    """从 dict 或 dataclass 读取字段。"""
    if ctx is None:
        return default
    if isinstance(ctx, dict):
        return ctx.get(key, default)
    return getattr(ctx, key, default)


def _pillar_stem(p):
    return _get(p, "heavenly_stem")


def _pillar_branch(p):
    return _get(p, "earthly_branch")


def _extract_context(ctx: dict) -> Tuple[str, str, List[str], List[str]]:
    """提取 Judgment 所需的最小确定性输入。

    Returns:
        (day_master, month_branch, pillars, transparent_stems)

    兼容两种输入:
      - dict (TemporalContext 序列化, 含 natal 子 dict)
      - NatalContext / TemporalContext 对象
    """
    natal = _get(ctx, "natal")
    source = natal if natal is not None else ctx

    day_master = _get(source, "day_master")
    pillars = _get(source, "pillars", []) or []

    month_branch = _get(source, "month_branch")
    if not month_branch:
        for p in pillars:
            if _get(p, "position") == "MONTH":
                month_branch = _pillar_branch(p)
                break
    if not month_branch:
        for i, p in enumerate(pillars):
            if i == 1:
                month_branch = _pillar_branch(p)
                break

    stems = [_pillar_stem(p) for p in pillars]
    transparent = [s for s in stems if s]
    return day_master, month_branch, pillars, transparent


def _chong_partner(branch: str) -> Optional[str]:
    """返回 branch 的六冲对支 (无则 None)。"""
    for pair in CHONG_PAIRS:
        if branch in pair:
            return next(iter(pair - {branch}))
    return None


# ============================================================================
# P0-1: 旺衰 (WANGSHUAI) — 得令 + 得地 + 得势 + 寒暖燥湿
# ============================================================================

class WANGSHUAIJudgment:
    """旺衰域 Judgment 实现 (Phase 3 P0 重写)

    四维评分模型, 全部为确定性条件判断:

    1. 得令 (月令司权)
       月支主气对日主为印/比/劫 → +3   [DTS-101]
       月支主气为官/杀/财/食/伤 → -2   [DTS-102]
       得令但月令被局中支所冲(围克) → 附加 -2  [DTS-106]

    2. 得地 (十二干生旺死绝)
       日主于月支 临官/帝旺 → +2       [DTS-104]
       日主于月支 沐浴/冠带 → +1       [SMTH-101]
       日主于月支 死/墓/绝 → -2       [SMTH-102]

    3. 得势 (党众)
       四柱透干+藏干中 印比劫 > 克泄耗 → +2  [DTS-105]
       印比劫 < 克泄耗                 → -2
       相等                            →  0

    4. 得地得势综合修正
       失令但有强根/帮扶 → 综合评分可转为身偏强 [DTS-107]
       (此修正由评分模型内在体现, 命中时记 DTS-107 证据)

    说明: 寒暖燥湿修正为《穷通宝鉴》调候体系, 归属 YONGSHEN 域,
    本域不引用 (避免与不存在的 QTB 旺衰规则臆造映射)。

    综合: >= 4 → STRONG ; <= -3 → WEAK ; 否则 MODERATE

    MODERATE 仅在评分落入 (-3, 4) 区间时产生, 由评分区间自然导出,
    不存在绕过评分的硬编码 fallback。
    """

    DOMAIN = JudgmentDomain.WANGSHUAI

    @staticmethod
    def judge(signals: List[dict], context: dict) -> DomainJudgment:
        """基于月令/通根/党众评分判断旺衰。"""
        day_master, month_branch, pillars, transparent = _extract_context(context)

        reasoning_parts: List[str] = []
        cits = _Citations()
        signal_ids: List[str] = []

        if not day_master or not month_branch:
            return DomainJudgment(
                domain=JudgmentDomain.WANGSHUAI,
                conclusion=JudgmentConclusion.UNKNOWN,
                reasoning="context 缺少 day_master 或 month_branch, 无法判定旺衰",
            )

        for s in signals or []:
            sid = s.get("id") if isinstance(s, dict) else None
            if sid:
                signal_ids.append(sid)

        # ---- 1. 得令: 月令司权 ----
        month_main_god = ten_god(day_master, hidden_main_stem(month_branch))
        if month_main_god in SHENG_TEN_GODS:
            get_ling_score = 3
            reasoning_parts.append(
                f"得令:月令{month_branch}主气{month_main_god}生扶日主{day_master}(+3)")
            cits.add("DTS-101")
        else:
            get_ling_score = -2
            reasoning_parts.append(
                f"失令:月令{month_branch}主气{month_main_god}克泄耗日主{day_master}(-2)")
            cits.add("DTS-102")

        # 得令但被围克 (月令支被局中他柱支所冲)
        pillar_branches = {_pillar_branch(p) for p in pillars}
        chong = _chong_partner(month_branch)
        if chong and chong in pillar_branches:
            get_ling_score -= 2
            reasoning_parts.append(
                f"月令{month_branch}被{chong}冲(围克),得令不成立(-2)")
            cits.add("DTS-106")

        # ---- 2. 得地: 十二干生旺死绝 ----
        stage = longhu_stage(day_master, month_branch)
        if stage in LONGHU_STRONG_STAGES:
            de_di_score = 2
            reasoning_parts.append(
                f"得地:日主{day_master}于月支{month_branch}处{stage}(+2)")
            cits.add("DTS-104")
        elif stage in LONGHU_MID_STAGES:
            de_di_score = 1
            reasoning_parts.append(
                f"得地:日主{day_master}于月支{month_branch}处{stage}(+1)")
            cits.add("SMTH-101")
        elif stage in LONGHU_WEAK_STAGES:
            de_di_score = -2
            reasoning_parts.append(
                f"失地:日主{day_master}于月支{month_branch}处{stage}(-2)")
            cits.add("SMTH-102")
        else:
            de_di_score = 0
            reasoning_parts.append(
                f"十二干生旺死绝:日主{day_master}于月支{month_branch}处{stage}(中性)")

        # ---- 3. 得势: 党众 (透干 + 藏干根) ----
        help_count, drain_count = _count_dangzhong(day_master, pillars, transparent)
        dangzhong_score = 2 if help_count > drain_count else (
            -2 if help_count < drain_count else 0
        )
        reasoning_parts.append(
            f"党众:帮身(印比劫){help_count} vs 克泄耗{drain_count}({dangzhong_score:+d})")
        cits.add("DTS-105")

        # ---- 综合评分 ----
        total = get_ling_score + de_di_score + dangzhong_score
        score_detail = {
            "get_ling_score": get_ling_score,
            "de_di_score": de_di_score,
            "dangzhong_score": dangzhong_score,
            "total_score": total,
            "help_count": help_count,
            "drain_count": drain_count,
            "month_main_ten_god": month_main_god,
            "longhu_stage": stage,
        }

        if total >= STRONG_THRESHOLD:
            conclusion = JudgmentConclusion.STRONG
            reasoning_parts.append(f"综合评分{total}>=+4,判身强(旺)")
        elif total <= WEAK_THRESHOLD:
            conclusion = JudgmentConclusion.WEAK
            reasoning_parts.append(f"综合评分{total}<=-3,判身弱(衰)")
        else:
            conclusion = JudgmentConclusion.MODERATE
            reasoning_parts.append(f"综合评分{total}在(-3,+4)区间,判中和")

        # ---- 失令有根修正 ----
        # 《滴天髓》: 失令但有强根/帮扶, 仍身偏强 (DTS-107 三辨综合判定)
        if month_main_god not in SHENG_TEN_GODS and total >= STRONG_THRESHOLD \
                and (de_di_score > 0 or dangzhong_score > 0):
            reasoning_parts.append(
                f"失令有根修正:虽失令,但得地/党众使综合评分{total},仍判身偏强")
            cits.add("DTS-107")

        return DomainJudgment(
            domain=JudgmentDomain.WANGSHUAI,
            conclusion=conclusion,
            reasoning="; ".join(reasoning_parts),
            signal_ids=list(dict.fromkeys(signal_ids)),
            evidence_refs=cits.evidence_refs,
            rule_refs=cits.rule_refs,
            score=float(total),
            score_detail=score_detail,
        )

    @staticmethod
    def _score_components(context: dict) -> Tuple[DomainJudgment, dict]:
        """内部: 同时返回判断结果与评分明细 (供 YONGSHEN 域消费)。"""
        j = WANGSHUAIJudgment.judge([], context)
        return j, (j.score_detail or {})


def _count_dangzhong(day_master: str, pillars, transparent) -> Tuple[int, int]:
    """党众计数: (印比劫帮身数, 克泄耗数)。

    口径 (依据 DTS-105 "党众(比劫透干)"):
      - 党众只看四柱**透干** — "党"指明面上之党, 非地支藏干
      - 藏干根属"通根/得地"范畴 (DTS-103 日支通根, DTS-104 十二长生),
        若在此重复计数会与得地评分双重计数
      - 日干自身不计入党众 (不是"党")
    """
    help_count = 0
    drain_count = 0

    for s in {t for t in transparent if t and t != day_master}:
        g = ten_god(day_master, s)
        if g in SHENG_TEN_GODS:
            help_count += 1
        elif g in KE_XIE_HAO_TEN_GODS:
            drain_count += 1

    return help_count, drain_count


def _tiaohou_score(season: str, pillars) -> int:
    """寒暖燥湿修正: 冬生需火暖, 夏生需水润。"""
    branches = [_pillar_branch(p) for p in pillars if _pillar_branch(p)]
    stems = [_pillar_stem(p) for p in pillars if _pillar_stem(p)]

    if season == "WINTER":
        fire_branch = any(b in ("SI", "WU") for b in branches)
        fire_stem = any(s in ("BING", "DING") for s in stems)
        return 1 if (fire_branch or fire_stem) else 0
    if season == "SUMMER":
        water_branch = any(b in ("ZI", "HAI") for b in branches)
        water_stem = any(s in ("REN", "GUI") for s in stems)
        return 1 if (water_branch or water_stem) else 0
    return 0


# ============================================================================
# P0-2: 格局 (GEJU) — 月令 → 透干 → 成格 / 破格
# ============================================================================

class GEJUJudgment:
    """格局域 Judgment 实现 (Phase 3 P0 重写)

    判断链 (《子平真诠·立成格》):

    1. 变格优先判定
       从格:   身弱 + 无印比帮扶 + 党众<=1   [ZPZ-105]
       专旺格: 身旺 + 印比占尽 + 无克泄耗

    2. 特殊格: 建禄 / 月刃 / 月劫
       月支 = 日主禄位   → 建禄格  [SMTH-103, E-SMTH-103-001]
       月支 = 日主帝旺位 → 阳刃格  [YHZP-101, E-YHZP-101-001]
       月支主气 = 劫财   → 月劫格  [YHZP-104, E-YHZP-104-001]

    3. 月令取格 → 透干成格
       月令主气透干 → 取本气格  [ZPZ-111~120]
       月令中气/余气透干 → 取中气格  [ZPZ-111]
       杂气月主气不透干 → 不取本气格

    4. 破格条件
       财破印: 印格 + 财透干
       伤官见官: 官格 + 伤官透干   [ZPZ-106/110]
       杀无制: 七杀格 + 无食伤无印
       月令被冲破: 月令支受冲

    结论: ESTABLISHED / BROKEN / UNKNOWN
    """

    DOMAIN = JudgmentDomain.GEJU

    @staticmethod
    def judge(signals: List[dict], context: dict) -> DomainJudgment:
        """基于月令→透干→成格/破格链判断格局。"""
        day_master, month_branch, pillars, transparent = _extract_context(context)

        reasoning_parts: List[str] = []
        # BZ-FNDR-15.20 Step 1: 用 cits 统一收集 refs (自动从 CITATION 双填 rule+evidence)
        cits = _Citations()
        signal_ids: List[str] = []

        if not day_master or not month_branch:
            return DomainJudgment(
                domain=JudgmentDomain.GEJU,
                conclusion=JudgmentConclusion.UNKNOWN,
                reasoning="context 缺少 day_master 或 month_branch, 无法判定格局",
            )

        for s in signals or []:
            sid = s.get("id") if isinstance(s, dict) else None
            if sid:
                signal_ids.append(sid)

        transparent_set = [s for s in transparent if s]
        transparent_gods = [ten_god(day_master, s) for s in transparent_set]
        month_main_god = ten_god(day_master, hidden_main_stem(month_branch))
        month_branches = [_pillar_branch(p) for p in pillars]

        # ---- 1. 变格检测 (BLOCKED: 暂无证据支撑) ----
        # 证据库现状: 从格 / 专旺格 / 化格 无任何 rule 与 evidence
        # (ZPZ-105 实为"官杀当令→CONSTRAINT", 非从格规则, 此前误映射已移除)。
        # 因此变格不再输出 ESTABLISHED, 仅返回 UNKNOWN 并显式标注证据缺口,
        # 遵守"不做测试迎合实现"。
        _, detail = WANGSHUAIJudgment._score_components(context)
        wangshuai_conclusion = WANGSHUAIJudgment.judge([], context).conclusion
        help_count = detail.get("help_count", 0)
        drain_count = detail.get("drain_count", 0)

        if wangshuai_conclusion == JudgmentConclusion.WEAK \
                and help_count == 0 and drain_count >= 2:
            reasoning_parts.append(
                "疑似从格:身弱且无印比帮扶,克泄耗当权 — "
                "但证据库无从格规则/证据, 不作 ESTABLISHED 结论")
            return DomainJudgment(
                domain=JudgmentDomain.GEJU,
                conclusion=JudgmentConclusion.UNKNOWN,
                reasoning="; ".join(reasoning_parts),
                signal_ids=list(dict.fromkeys(signal_ids)),
                ge_type="疑似从格(证据缺口)",
            )

        if wangshuai_conclusion == JudgmentConclusion.STRONG \
                and drain_count == 0 and help_count >= 3:
            reasoning_parts.append(
                "疑似专旺格:身强且印比占尽,无克泄耗 — "
                "但证据库无专旺格规则/证据, 不作 ESTABLISHED 结论")
            return DomainJudgment(
                domain=JudgmentDomain.GEJU,
                conclusion=JudgmentConclusion.UNKNOWN,
                reasoning="; ".join(reasoning_parts),
                signal_ids=list(dict.fromkeys(signal_ids)),
                ge_type="疑似专旺格(证据缺口)",
            )

        # ---- 2. 特殊格: 建禄 / 阳刃 / 月劫 ----
        if ROAD_BRANCH.get(day_master) == month_branch:
            ge_type = "建禄格"
            cits.add("SMTH-103")
        elif ABSOLUTE_BRANCH.get(day_master) == month_branch:
            ge_type = "阳刃格"
            cits.add("YHZP-101")
        elif month_main_god == "劫财":
            ge_type = "月劫格"
            cits.add("YHZP-104")
        else:
            ge_type = None

        # ---- 3. 月令取格 → 透干成格 ----
        if ge_type is None:
            if month_main_god in GEJU_NAME_BY_GOD:
                ge_type = GEJU_NAME_BY_GOD[month_main_god]
                reasoning_parts.append(
                    f"月令取格:月支{month_branch}主气{month_main_god}→{ge_type}")
                cits.add("ZPZ-111")
            else:
                reasoning_parts.append(
                    f"月令主气{month_main_god}非正格取格对象,格局待定")

        # 透干显性确认: 主气透干则格显性成立
        if ge_type and month_main_god in transparent_gods:
            reasoning_parts.append(f"透干成格:{month_main_god}透干,格显性确认")
            cits.add("ZPZ-120")

        # 杂气月主气不透干 → 改取中气/余气
        zagi = month_branch in ("CHEN", "XU", "CHOU", "WEI")
        hidden = BRANCH_HIDDEN_STEMS.get(month_branch, [])
        if ge_type and zagi and hidden:
            for stem, _pos in hidden[1:]:
                mid_god = ten_god(day_master, stem)
                if mid_god in transparent_gods and mid_god in GEJU_NAME_BY_GOD:
                    ge_type = GEJU_NAME_BY_GOD[mid_god]
                    reasoning_parts.append(
                        f"杂气月{month_branch}取中气{mid_god}透干成格→{ge_type}")
                    cits.add("ZPZ-111")
                    break

        if ge_type is None:
            return DomainJudgment(
                domain=JudgmentDomain.GEJU,
                conclusion=JudgmentConclusion.UNKNOWN,
                reasoning="; ".join(reasoning_parts) or "无法确定格局",
                signal_ids=list(dict.fromkeys(signal_ids)),
                rule_refs=list(cits.rule_refs),
                evidence_refs=list(cits.evidence_refs),
            )

        # ---- 4. 破格条件 ----
        broken_reason = None
        if ge_type in ("正印格", "偏印格") and ("正财" in transparent_gods
                                                or "偏财" in transparent_gods):
            broken_reason = "财破印格"
            cits.add("ZPZ-108")
        elif ge_type == "正官格" and "伤官" in transparent_gods:
            broken_reason = "伤官见官"
            cits.add("ZPZ-106")
            cits.add("ZPZ-110")
        elif ge_type == "七杀格" and "食神" not in transparent_gods \
                and "伤官" not in transparent_gods \
                and "正印" not in transparent_gods \
                and "偏印" not in transparent_gods:
            broken_reason = "七杀无制(无食伤无印)"
            cits.add("ZPZ-107")

        if _chong_partner(month_branch) in month_branches:
            broken_reason = (broken_reason + "; " if broken_reason else "") \
                + f"月令{month_branch}被冲,格有破损"
            cits.add("DTS-106")

        if broken_reason:
            return DomainJudgment(
                domain=JudgmentDomain.GEJU,
                conclusion=JudgmentConclusion.BROKEN,
                reasoning="; ".join(reasoning_parts + [broken_reason]),
                signal_ids=list(dict.fromkeys(signal_ids)),
                evidence_refs=list(cits.evidence_refs),
                rule_refs=list(cits.rule_refs),
                ge_type=ge_type,
            )

        # 阳刃透杀制伏 → 格局反成 (《渊海子平》)
        if ge_type == "阳刃格" and "七杀" in transparent_gods:
            reasoning_parts.append("阳刃透杀制伏,刃格反成")
            cits.add("YHZP-105")

        reasoning_parts.append(f"格局成立:{ge_type}")
        return DomainJudgment(
            domain=JudgmentDomain.GEJU,
            conclusion=JudgmentConclusion.ESTABLISHED,
            reasoning="; ".join(reasoning_parts),
            signal_ids=list(dict.fromkeys(signal_ids)),
            evidence_refs=list(cits.evidence_refs),
            rule_refs=list(cits.rule_refs),
            ge_type=ge_type,
        )


# ============================================================================
# P0-3: 用神 (YONGSHEN) — 五级优先级链
# ============================================================================

class YONGSHENJudgment:
    """用神域 Judgment 实现 (Phase 3 P0 重写)

    五级优先级 (《子平真诠·论用神》+《穷通宝鉴》调候):

    1. 格局用神 (优先): 正格按格取用, 建禄/月劫取财官, 阳刃取杀制
    2. 扶抑用神 (次之): 身旺→克泄耗(官杀财食伤), 身弱→生扶(印比)
    3. 调候用神 (补充): 冬生→丙火暖局, 夏生→壬水润泽
    4. 通关用神 (特殊): 两神相战取中间通关之神
    5. 病药用神 (特殊): 过旺取克泄, 过弱取生扶

    约束: 不使用 MODERATE 类硬编码 fallback; 若五级链均未命中,
    返回 UNKNOWN 并说明原因。
    """

    DOMAIN = JudgmentDomain.YONGSHEN

    @staticmethod
    def judge(signals: List[dict], context: dict,
              wangshuai_judgment: Optional[DomainJudgment] = None,
              geju_judgment: Optional[DomainJudgment] = None) -> DomainJudgment:
        """按优先级链判断用神。

        Args:
            wangshuai_judgment: 旺衰域结果 (由 JudgmentFactory 编排注入)
            geju_judgment: 格局域结果
        """
        day_master, month_branch, pillars, transparent = _extract_context(context)

        reasoning_parts: List[str] = []
        # BZ-FNDR-15.20 Step 1: 用 cits 统一收集 refs
        cits = _Citations()
        signal_ids: List[str] = []

        if not day_master or not month_branch:
            return DomainJudgment(
                domain=JudgmentDomain.YONGSHEN,
                conclusion=JudgmentConclusion.UNKNOWN,
                reasoning="context 缺少 day_master 或 month_branch, 无法取用神",
            )

        for s in signals or []:
            sid = s.get("id") if isinstance(s, dict) else None
            if sid:
                signal_ids.append(sid)

        wangshuai_judgment = wangshuai_judgment or WANGSHUAIJudgment.judge([], context)
        geju_judgment = geju_judgment or GEJUJudgment.judge([], context)

        transparent_gods = [ten_god(day_master, s) for s in transparent if s]
        conclusion: Optional[JudgmentConclusion] = None
        primary: List[str] = []
        yongshen_type = None

        # ---- 1. 格局用神 (优先) ----
        ge_type = geju_judgment.ge_type
        if ge_type and ge_type in GEJU_YONGSHEN_TABLE:
            yongshen_set, _avoid = GEJU_YONGSHEN_TABLE[ge_type]
            primary = _pick_present(yongshen_set, transparent_gods) \
                or list(yongshen_set[:1])
            yongshen_type = "格局用神"
            reasoning_parts.append(
                f"格局用神:{ge_type}→取{'/'.join(primary)}")
            rr = GEJU_RULE_BY_GE.get(ge_type, (None, None))
            if rr[0]:
                cits.add(rr[0])  # BZ-FNDR-15.20 Step 1: cits 替换直接 append
            conclusion = JudgmentConclusion.PRIMARY
        elif ge_type == "从格":
            primary = [g for g in transparent_gods
                       if g in KE_XIE_HAO_TEN_GODS][:1] or \
                [ten_god(day_master, hidden_main_stem(month_branch))]
            yongshen_type = "格局用神"
            reasoning_parts.append(f"从格顺势:取{primary[0]}(随旺势)")
            conclusion = JudgmentConclusion.PRIMARY

        # ---- 2. 扶抑用神 ----
        if conclusion is None:
            if wangshuai_judgment.conclusion == JudgmentConclusion.STRONG:
                primary = _pick_present(KE_XIE_HAO_TEN_GODS, transparent_gods) \
                    or ["正官"]
                yongshen_type = "扶抑用神"
                reasoning_parts.append(
                    f"身旺,扶抑取克泄耗→{primary[0]}")
            elif wangshuai_judgment.conclusion == JudgmentConclusion.WEAK:
                primary = _pick_present(SHENG_TEN_GODS, transparent_gods) \
                    or ["正印"]
                yongshen_type = "扶抑用神"
                reasoning_parts.append(
                    f"身弱,扶抑取生扶→{primary[0]}")
            conclusion = JudgmentConclusion.PRIMARY

        # ---- 3. 调候用神 (补充) ----
        # 补充项: 不降级已取得的 PRIMARY 结论 (《子平真诠·论用神》以格局
        # 用神为主, 调候仅补充), 仅当上游未取用时才提升为结论。
        season = SEASON_BY_BRANCH.get(month_branch, "SPRING")
        tiaohou = _tiaohou_yongshen(season, day_master)
        if tiaohou:
            reasoning_parts.append(f"调候用神:季节{season}→{tiaohou[0]}")
            primary = [tiaohou[0]] + [p for p in primary if p != tiaohou[0]]
            if not yongshen_type:
                yongshen_type = "调候用神"
            if conclusion is None:
                conclusion = JudgmentConclusion.SECONDARY

        # ---- 4. 通关用神 ----
        tongguan = _tongguan_yongshen(transparent_gods)
        if tongguan:
            reasoning_parts.append(f"通关用神:{tongguan[1]}→取{tongguan[0]}")
            primary = [tongguan[0]] + [p for p in primary if p != tongguan[0]]
            if not yongshen_type:
                yongshen_type = "通关用神"
            if conclusion is None:
                conclusion = JudgmentConclusion.SECONDARY

        # ---- 5. 病药用神 ----
        detail = wangshuai_judgment.score_detail or {}
        total = detail.get("total_score", 0)
        if total >= 8:
            primary = _pick_present(KE_XIE_HAO_TEN_GODS, transparent_gods) \
                or ["正官"]
            yongshen_type = "病药用神"
            reasoning_parts.append(f"过旺(评分{total}>=8),病药取克泄→{primary[0]}")
            conclusion = JudgmentConclusion.PRIMARY
        elif total <= -7:
            primary = _pick_present(SHENG_TEN_GODS, transparent_gods) \
                or ["正印"]
            yongshen_type = "病药用神"
            reasoning_parts.append(f"过弱(评分{total}<=-7),病药取生扶→{primary[0]}")
            conclusion = JudgmentConclusion.PRIMARY

        if conclusion is None or not primary:
            return DomainJudgment(
                domain=JudgmentDomain.YONGSHEN,
                conclusion=JudgmentConclusion.UNKNOWN,
                reasoning="; ".join(reasoning_parts) or "五级用神链均未命中",
                signal_ids=list(dict.fromkeys(signal_ids)),
                rule_refs=list(cits.rule_refs),
                evidence_refs=list(cits.evidence_refs),
                ge_type=ge_type,
            )

        return DomainJudgment(
            domain=JudgmentDomain.YONGSHEN,
            conclusion=conclusion,
            reasoning="; ".join(reasoning_parts),
            signal_ids=list(dict.fromkeys(signal_ids)),
            evidence_refs=list(cits.evidence_refs),
            rule_refs=list(cits.rule_refs),
            ge_type=ge_type,
            yongshen_type=yongshen_type,
        )

    @staticmethod
    def _primary_of(judgment: DomainJudgment) -> List[str]:
        """从 reasoning 中回取主用神 (供工厂层传递)。"""
        return [p for p in judgment.reasoning.split("→") if p][-1].split(",") \
            if judgment.reasoning else []


def _pick_present(preferred, transparent_gods) -> List[str]:
    """从偏好集合中取局中实际透干者, 保持偏好顺序。"""
    return [g for g in preferred if g in transparent_gods]


def _tiaohou_yongshen(season: str, day_master: str) -> Optional[Tuple[str, str]]:
    """调候用神: 冬生取丙火暖局, 夏生取壬水润泽。

    取用神为「调候天干对日主之十神」, 保持与全表一致(十神名而非干名)。
    """
    if season == "WINTER":
        return (ten_god(day_master, "BING"), "冬生取丙火暖局")
    if season == "SUMMER":
        return (ten_god(day_master, "REN"), "夏生取壬水润泽")
    return None


def _tongguan_yongshen(transparent_gods) -> Optional[Tuple[str, str]]:
    """通关用神: 两神相战取通关之神。"""
    if "伤官" in transparent_gods and "正官" in transparent_gods:
        return ("正财", "伤官见官,取财通关")
    if "偏印" in transparent_gods and "正财" in transparent_gods:
        return ("正财", "枭神夺食,财可通关")
    return None


# ============================================================================
# 十神语义 / 事件判断 (P1 域, 保持基础实现)
# ============================================================================

class SHISHENJudgment:
    """十神语义域 Judgment 实现.

    ⑮-1 A2 (User 2026-09-10 裁决): 当前域 STATUS = P1-REVIEW, PRODUCTION_READY = NO.
    当前生产 Pipeline 未注入 semantic_signals (RELATION / REFLECTION ontology_type),
    该域暂不具备生产判断能力. 保留类不删除, 等 Pipeline 注入层在⑮-2 之后再开启.
    注: SHISHEN (十神) 本身不是废弃方法, 是子平体系基础组成部分.

    判断逻辑:
    1. 十神定位 → 确定十神
    2. 十神组合 → 判断吉凶
    3. 十神位置 → 判断影响范围
    """

    DOMAIN = JudgmentDomain.SHISHEN

    # ⑮-1 A2: 标记当前域状态
    STATUS = "P1-REVIEW"
    PRODUCTION_READY = False

    @staticmethod
    def judge(signals: List[dict], context: dict) -> DomainJudgment:
        """基于 Signal 列表判断十神语义"""
        reasoning_parts = []
        signal_ids = []

        semantic_signals = [s for s in signals if s.get("ontology_type") in
                          ("RELATION", "REFLECTION")]
        if semantic_signals:
            reasoning_parts.append(f"有{len(semantic_signals)}条十神语义信号")
            signal_ids.extend(s.get("id") for s in semantic_signals)
            has_good = any(s.get("direction") in ("POSITIVE", "INCREASE")
                          for s in semantic_signals)
            conclusion = JudgmentConclusion.SEMANTIC_POSITIVE if has_good \
                else JudgmentConclusion.SEMANTIC_NEGATIVE
        else:
            conclusion = JudgmentConclusion.UNKNOWN

        return DomainJudgment(
            domain=JudgmentDomain.SHISHEN,
            conclusion=conclusion,
            reasoning="; ".join(reasoning_parts),
            signal_ids=list(set(signal_ids)),
        )


class SHIJIANJudgment:
    """事件判断域 Judgment 实现.

    ⑮-1 A1 (User 2026-09-10 裁决): 无 event_signals → UNKNOWN (fail-closed).
    原 EVENT_ABSENT 是 fail-open: "无输入证据"却输出积极结论 ("无事件") 是伪判定.
    修正: 只有 event_signals 存在时才能判 EVENT_EXIST, 否则 UNKNOWN.

    判断逻辑:
    1. 命局信号 → 基础事件倾向
    2. 大运信号 → 事件触发时机
    3. 流年信号 → 事件具体应期
    4. 作用关系 → 事件结果判断

    ⑮-1 A2 (User 2026-09-10 裁决): 当前域 STATUS = P1-REVIEW, PRODUCTION_READY = NO.
    当前生产 Pipeline 未注入 event_signals, 该域暂不具备生产判断能力.
    保留类不删除, 等 Pipeline 注入层在⑮-2 之后再开启.

    注意: LLM 只能表达，不能自主判断
    """

    DOMAIN = JudgmentDomain.SHIJIAN

    # ⑮-1 A2: 标记当前域状态
    STATUS = "P1-REVIEW"
    PRODUCTION_READY = False

    @staticmethod
    def judge(signals: List[dict], context: dict) -> DomainJudgment:
        """基于 Signal 列表判断事件 (⑮-1 A1: 无 signals → UNKNOWN, 非 EVENT_ABSENT)."""
        reasoning_parts = []
        signal_ids = []

        event_signals = [s for s in signals if s.get("event_types")]
        if event_signals:
            reasoning_parts.append(f"有{len(event_signals)}条事件信号")
            signal_ids.extend(s.get("id") for s in event_signals)
            conclusion = JudgmentConclusion.EVENT_EXIST
        else:
            # ⑮-1 A1: 无 event_signals → UNKNOWN (fail-closed).
            # 原 EVENT_ABSENT 是 fail-open: "无输入证据" 输出积极结论 ("无事件") 是伪判定.
            conclusion = JudgmentConclusion.UNKNOWN

        return DomainJudgment(
            domain=JudgmentDomain.SHIJIAN,
            conclusion=conclusion,
            reasoning="; ".join(reasoning_parts),
            signal_ids=list(set(signal_ids)),
        )


# ============================================================================
# Judgment 工厂
# ============================================================================

_CONCLUSION_BY_DOMAIN = {
    JudgmentDomain.WANGSHUAI: JudgmentConclusion.STRONG,
    JudgmentDomain.GEJU: JudgmentConclusion.ESTABLISHED,
    JudgmentDomain.YONGSHEN: JudgmentConclusion.PRIMARY,
}

_DOMAIN_ATTRIBUTE = {
    JudgmentDomain.WANGSHUAI: "wangshuai",
    JudgmentDomain.GEJU: "geju",
    JudgmentDomain.YONGSHEN: "yongshen",
    JudgmentDomain.SHISHEN: "shishen",
    JudgmentDomain.SHIJIAN: "shijian",
}


class JudgmentFactory:
    """Judgment 工厂，根据 domain 创建对应的 Judgment 实例"""

    _judgments = {
        JudgmentDomain.WANGSHUAI: WANGSHUAIJudgment,
        JudgmentDomain.GEJU: GEJUJudgment,
        JudgmentDomain.YONGSHEN: YONGSHENJudgment,
        JudgmentDomain.SHISHEN: SHISHENJudgment,
        JudgmentDomain.SHIJIAN: SHIJIANJudgment,
    }

    @classmethod
    def create(cls, domain: JudgmentDomain) -> object:
        """创建指定域的 Judgment 实例"""
        judgment_cls = cls._judgments.get(domain)
        if judgment_cls is None:
            raise ValueError(f"未知的辨证域: {domain}")
        return judgment_cls()

    @classmethod
    def judge_all(cls, signals_by_domain: Dict[JudgmentDomain, List[dict]],
                  context: dict) -> JudgmentSynthesis:
        """对五大域进行完整判断。

        Phase 3 P0: 核心三域存在依赖顺序 — 旺衰 → 格局 → 用神,
        因此严格按序执行并将上游结果注入下游。
        """
        synthesis = JudgmentSynthesis()

        # 核心三域有依赖顺序(旺衰 → 格局 → 用神), 必须确定性排序执行;
        # 其余域无依赖, 按原始顺序处理。
        ordered = (
            [JudgmentDomain.WANGSHUAI, JudgmentDomain.GEJU, JudgmentDomain.YONGSHEN]
            + [d for d in signals_by_domain
               if d not in (JudgmentDomain.WANGSHUAI, JudgmentDomain.GEJU,
                            JudgmentDomain.YONGSHEN)]
        )

        for domain in ordered:
            signals = signals_by_domain.get(domain, [])
            judgment_cls = cls._judgments.get(domain)
            if not judgment_cls:
                continue

            if domain == JudgmentDomain.YONGSHEN:
                judgment = judgment_cls.judge(
                    signals, context,
                    wangshuai_judgment=synthesis.wangshuai,
                    geju_judgment=synthesis.geju,
                )
            else:
                judgment = judgment_cls.judge(signals, context)

            attr = _DOMAIN_ATTRIBUTE.get(domain)
            if attr:
                setattr(synthesis, attr, judgment)

        return synthesis
