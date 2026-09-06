"""Domain Judgment - 子平辨证域裁决层

架构位置:
    BAZI Chart → Signal → Judgment → Synthesis → Output

核心原则:
1. 每个辨证域有独立的 Judgment 类
2. Judgment 收集同域 Signal，进行领域内综合判断
3. 禁止跨域投票、加权、比例等聚合机制
4. Judgment 结论为确定性条件判断，非概率推断

五 domain:
- WANGSHUAI: 旺衰判断
- GEJU: 格局判断
- YONGSHEN: 用神判断
- SHISHEN: 十神语义判断
- SHIJIAN: 事件判断
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Set


class JudgmentDomain(str, Enum):
    """子平五大辨证域"""
    WANGSHUAI = "WANGSHUAI"      # 旺衰
    GEJU = "GEJU"                 # 格局
    YONGSHEN = "YONGSHEN"         # 用神
    SHISHEN = "SHISHEN"           # 十神语义
    SHIJIAN = "SHIJIAN"           # 事件判断


class JudgmentConclusion(str, Enum):
    """Judgment 结论类型"""
    STRONG = "STRONG"             # 强（旺）
    WEAK = "WEAK"                 # 弱（衰）
    MODERATE = "MODERATE"         # 中和
    ESTABLISHED = "ESTABLISHED"   # 格局成立
    BROKEN = "BROKEN"             # 格局破
    PRIMARY = "PRIMARY"           # 主用神
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
        }


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


class WANGSHUAIJudgment:
    """旺衰域 Judgment 实现

    判断逻辑:
    1. 月令得令 → 偏旺
    2. 通根有力 → 偏旺
    3. 比劫帮身 → 偏旺
    4. 印星生身 → 偏旺
    5. 克泄耗多 → 偏弱
    6. 综合判断 → 强/弱/中和
    """

    DOMAIN = JudgmentDomain.WANGSHUAI

    @staticmethod
    def judge(signals: List[dict], context: dict) -> DomainJudgment:
        """基于 Signal 列表判断旺衰

        Args:
            signals: 旺衰域相关 Signal 列表
            context: TemporalContext（包含日主、月令等信息）

        Returns:
            DomainJudgment
        """
        reasoning_parts = []
        signal_ids = []
        evidence_refs = []
        rule_refs = []

        # 检查关键信号
        has_sheng = any(s.get("type") == "SUPPORT" for s in signals)
        has_ke = any(s.get("type") == "CONSTRAINT" for s in signals)

        if has_sheng:
            reasoning_parts.append("有生扶信号")
            signal_ids.extend(s.get("id") for s in signals if s.get("type") == "SUPPORT")
        if has_ke:
            reasoning_parts.append("有克泄信号")
            signal_ids.extend(s.get("id") for s in signals if s.get("type") == "CONSTRAINT")

        # 简单规则：有生扶无克泄 → 偏旺
        if has_sheng and not has_ke:
            conclusion = JudgmentConclusion.STRONG
            reasoning_parts.append("生扶多克泄少")
        elif has_ke and not has_sheng:
            conclusion = JudgmentConclusion.WEAK
            reasoning_parts.append("克泄多生扶少")
        else:
            conclusion = JudgmentConclusion.MODERATE
            reasoning_parts.append("生扶克泄均衡")

        return DomainJudgment(
            domain=JudgmentDomain.WANGSHUAI,
            conclusion=conclusion,
            reasoning="; ".join(reasoning_parts),
            signal_ids=list(set(signal_ids)),
            evidence_refs=evidence_refs,
            rule_refs=rule_refs,
        )


class GEJUJudgment:
    """格局域 Judgment 实现

    判断逻辑:
    1. 月令透干 → 取格
    2. 成格条件 → 格局成立
    3. 破格条件 → 格局破
    4. 特殊格局 → 优先级最高
    """

    DOMAIN = JudgmentDomain.GEJU

    @staticmethod
    def judge(signals: List[dict], context: dict) -> DomainJudgment:
        """基于 Signal 列表判断格局"""
        reasoning_parts = []
        signal_ids = []

        # 检查格局信号
        has_geju_signal = any(s.get("type") in ("ACTION", "OUTPUT") for s in signals)

        if has_geju_signal:
            reasoning_parts.append("有格局信号")
            signal_ids.extend(s.get("id") for s in signals)
            conclusion = JudgmentConclusion.ESTABLISHED
        else:
            reasoning_parts.append("无明确格局信号")
            conclusion = JudgmentConclusion.UNKNOWN

        return DomainJudgment(
            domain=JudgmentDomain.GEJU,
            conclusion=conclusion,
            reasoning="; ".join(reasoning_parts),
            signal_ids=list(set(signal_ids)),
        )


class YONGSHENJudgment:
    """用神域 Judgment 实现

    判断逻辑:
    1. 格局用神 → 优先
    2. 扶抑用神 → 次之
    3. 调候用神 → 补充
    4. 制化用神 → 特殊

    注意: 目前此域规则尚未完整授权，返回 UNKNOWN
    """

    DOMAIN = JudgmentDomain.YONGSHEN

    @staticmethod
    def judge(signals: List[dict], context: dict) -> DomainJudgment:
        """基于 Signal 列表判断用神"""
        # TODO: 实现完整的用神判断逻辑
        # 当前返回 UNKNOWN，等待 YG 规则授权
        return DomainJudgment(
            domain=JudgmentDomain.YONGSHEN,
            conclusion=JudgmentConclusion.UNKNOWN,
            reasoning="用神规则尚未完整授权",
            signal_ids=[],
        )


class SHISHENJudgment:
    """十神语义域 Judgment 实现

    判断逻辑:
    1. 十神定位 → 确定十神
    2. 十神组合 → 判断吉凶
    3. 十神位置 → 判断影响范围
    """

    DOMAIN = JudgmentDomain.SHISHEN

    @staticmethod
    def judge(signals: List[dict], context: dict) -> DomainJudgment:
        """基于 Signal 列表判断十神语义"""
        reasoning_parts = []
        signal_ids = []

        # 检查十神信号
        semantic_signals = [s for s in signals if s.get("ontology_type") in
                          ("RELATION", "REFLECTION")]
        if semantic_signals:
            reasoning_parts.append(f"有{len(semantic_signals)}条十神语义信号")
            signal_ids.extend(s.get("id") for s in semantic_signals)
            # 简单判断：有吉神信号 → 偏吉
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
    """事件判断域 Judgment 实现

    判断逻辑:
    1. 命局信号 → 基础事件倾向
    2. 大运信号 → 事件触发时机
    3. 流年信号 → 事件具体应期
    4. 作用关系 → 事件结果判断

    注意: LLM 只能表达，不能自主判断
    """

    DOMAIN = JudgmentDomain.SHIJIAN

    @staticmethod
    def judge(signals: List[dict], context: dict) -> DomainJudgment:
        """基于 Signal 列表判断事件"""
        reasoning_parts = []
        signal_ids = []

        # 检查事件信号
        event_signals = [s for s in signals if s.get("event_types")]
        if event_signals:
            reasoning_parts.append(f"有{len(event_signals)}条事件信号")
            signal_ids.extend(s.get("id") for s in event_signals)
            # 事件存在
            conclusion = JudgmentConclusion.EVENT_EXIST
        else:
            conclusion = JudgmentConclusion.EVENT_ABSENT

        return DomainJudgment(
            domain=JudgmentDomain.SHIJIAN,
            conclusion=conclusion,
            reasoning="; ".join(reasoning_parts),
            signal_ids=list(set(signal_ids)),
        )


# Judgment 工厂
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
        """对五大域进行完整判断

        Args:
            signals_by_domain: 按域分组的 Signal 列表
            context: TemporalContext

        Returns:
            JudgmentSynthesis
        """
        synthesis = JudgmentSynthesis()

        for domain, signals in signals_by_domain.items():
            judgment_cls = cls._judgments.get(domain)
            if judgment_cls:
                judgment = judgment_cls.judge(signals, context)
                # 使用 setattr 因为 dataclass 是 frozen=True
                if domain == JudgmentDomain.WANGSHUAI:
                    synthesis.wangshuai = judgment
                elif domain == JudgmentDomain.GEJU:
                    synthesis.geju = judgment
                elif domain == JudgmentDomain.YONGSHEN:
                    synthesis.yongshen = judgment
                elif domain == JudgmentDomain.SHISHEN:
                    synthesis.shishen = judgment
                elif domain == JudgmentDomain.SHIJIAN:
                    synthesis.shijian = judgment

        return synthesis
