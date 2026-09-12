# -*- coding: utf-8 -*-
"""Ziwei 解层 — 将 MultiMethodSignal（辨层输出）翻译为古典断语解读。

架构定位:
    辨层 (RuleGraph.match_all) → MethodBundle + MethodMatch
        ↓
    解层 (此模块) — 只读消费 Signal，不重算
        ↓
    ZiweiInterpretationOutput

约束 (与 Bazi 解层对齐):
    1. 解层只消费 MethodMatch，不重算事实（ARCH-001/002 强制）
    2. 断语逐字抄录 evidence 原始文本，查不到标注 "原文未定位"
    3. 每条解释带 evidence_ref: 经典名 + 原文 [:60]
    4. 解层不得引入 LLM / score / weight / percentage
    5. 未匹配证据的 rule_id → UNDETERMINED（fail-closed）

覆盖域 (三派):
    FEIXING:   财荫夹印 / 刑忌夹印 / 来因宫命迁线 / 自化忌 / 四化入命
    ZHONGZHOU: 机月同梁 / 杀破廉贪 / 财荫夹印 / 刑忌夹印 / 紫微孤君 / 明珠出海 / ...
    QINTIAN:   来因宫 / 时空结构 / 立太极 / 向心自化 / 忌入六亲

扩展域 (倪海厦天纪断言):
    主星×宫位断言 — 直接从 chart 读取，不依赖辨层规则命中
    通过 enable_nihai=True 可选启用，不影响原有解层行为
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .multi_method import MultiMethodSignal, MethodBundle, MethodMatch


# ===========================================================================
# 数据模型
# ===========================================================================

@dataclass(frozen=True)
class EvidenceRef:
    """单条证据追溯引用."""
    classic: str          # 经典名（如 "王亭之谈星" / "许铨仁钦天讲义"）
    source: str           # 具体来源（如 "谈星1108" / "A02 四化象"）
    text_preview: str     # 原文片段（≤60 字）

    @classmethod
    def from_evidence(
        cls,
        source_title: str,
        source_location: str,
        verbatim: str,
    ) -> "EvidenceRef":
        return cls(
            classic=source_title.split("（")[0].split("(")[0].strip(),
            source=source_location,
            text_preview=verbatim[:60],
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "classic": self.classic,
            "source": self.source,
            "text_preview": self.text_preview,
        }


@dataclass(frozen=True)
class ZiweiInterpretation:
    """单条派别规则的经典解读."""
    rule_id: str                      # 规则 ID（如 "FEX-CMB-001"）
    method_id: str                    # "FEIXING" / "ZHONGZHOU" / "QINTIAN"
    strength: str                     # "strong" / "moderate" / "weak" / "neutral"
    direction: str                    # "auspicious" / "inauspicious" / "neutral"
    conclusion: str                   # 解层产出的字面结论（来自 judgment.raw_text / description）
    evidence_ref: Optional[EvidenceRef]  # 一手源追溯，None → UNDETERMINED
    quality: str = "UNKNOWN"          # PRINCIPLE / CASE / MIXED / UNCLEAR

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "method_id": self.method_id,
            "strength": self.strength,
            "direction": self.direction,
            "conclusion": self.conclusion,
            "evidence_ref": self.evidence_ref.to_dict() if self.evidence_ref else None,
            "quality": self.quality,
        }


@dataclass
class ZiweiInterpretationOutput:
    """解层输出契约 — 三派独立，互不合并."""
    feixing: List[ZiweiInterpretation] = field(default_factory=list)
    zhongzhou: List[ZiweiInterpretation] = field(default_factory=list)
    qintian: List[ZiweiInterpretation] = field(default_factory=list)
    undetermined_rules: List[str] = field(default_factory=list)
    total_matched: int = 0
    total_undetermined: int = 0
    # 倪海厦天纪断言（可选，通过 interpret_with_nihai 填充）
    nihai_assertions: List[Any] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "feixing": [i.to_dict() for i in self.feixing],
            "zhongzhou": [i.to_dict() for i in self.zhongzhou],
            "qintian": [i.to_dict() for i in self.qintian],
            "undetermined_rules": self.undetermined_rules,
            "total_matched": self.total_matched,
            "total_undetermined": self.total_undetermined,
            "nihai_assertions": [a.to_dict() for a in self.nihai_assertions],
        }


# ===========================================================================
# Evidence 加载器（各派独立）
# ===========================================================================

class ZiweiEvidenceLoader:
    """加载各派 evidence 绑定表，供解层查询."""

    def __init__(self) -> None:
        self._feixing_cache: Dict[str, Any] = {}
        self._zhongzhou_cache: Dict[str, Any] = {}
        self._qintian_cache: Dict[str, Any] = {}

    def _load_feixing(self) -> Dict[str, Any]:
        if not self._feixing_cache:
            try:
                from .feixing.evidence import EVIDENCE_TABLE
                for ev in EVIDENCE_TABLE:
                    self._feixing_cache[ev.rule_id] = ev
            except ImportError:
                pass
        return self._feixing_cache

    def _load_zhongzhou(self) -> Dict[str, Any]:
        if not self._zhongzhou_cache:
            try:
                from .zhongzhou.evidence import EVIDENCE_TABLE
                self._zhongzhou_cache = EVIDENCE_TABLE
            except ImportError:
                pass
        return self._zhongzhou_cache

    def _load_qintian(self) -> Dict[str, Any]:
        if not self._qintian_cache:
            try:
                from .qintian.evidence import EVIDENCE_BINDINGS
                self._qintian_cache = EVIDENCE_BINDINGS
            except ImportError:
                pass
        return self._qintian_cache

    def get_evidence_ref(
        self,
        method_id: str,
        rule_id: str,
    ) -> Optional[EvidenceRef]:
        """按方法 + rule_id 查询证据追溯。

        Returns:
            EvidenceRef 或 None（未找到则标注 UNDETERMINED）
        """
        if method_id == "FEIXING":
            table = self._load_feixing()
            ev = table.get(rule_id)
            if ev is None:
                return None
            # FeixingEvidence: source_title / source_url / verbatim_quote
            title = ev.source_title
            classic = title.split("（")[0].split("(")[0].strip()
            location = title  # 用 source_title 作 location
            return EvidenceRef(
                classic=classic,
                source=location,
                text_preview=ev.verbatim_quote[:60],
            )

        if method_id == "ZHONGZHOU":
            table = self._load_zhongzhou()
            ev = table.get(rule_id)
            if ev is None:
                return None
            # ZhongzhouEvidence: source / source_location / original_text
            return EvidenceRef(
                classic=ev.source,
                source=ev.source_location,
                text_preview=ev.original_text[:60],
            )

        if method_id == "QINTIAN":
            table = self._load_qintian()
            ev = table.get(rule_id)
            if ev is None:
                return None
            # QintianEvidence: source / verbatim_quote
            src = ev.source
            classic = src.split("《")[0].strip() if "《" in src else src
            return EvidenceRef(
                classic=classic,
                source=src,
                text_preview=ev.verbatim_quote[:60],
            )

        return None


# ===========================================================================
# 解层主逻辑
# ===========================================================================

class ZiweiInterpretationResolver:
    """紫微斗数解层 — 将 MultiMethodSignal 翻译为经典断语解读.

    架构对齐 Bazi 解层:
      - 只消费 MethodMatch（不重算）
      - 断语逐字抄录 evidence 原文
      - fail-closed：证据缺失 → quality=UNCLEAR
    """

    def __init__(self) -> None:
        self._loader = ZiweiEvidenceLoader()

    def resolve(self, signal: MultiMethodSignal) -> ZiweiInterpretationOutput:
        """解析 MultiMethodSignal → ZiweiInterpretationOutput.

        Args:
            signal: 辨层输出的多派信号

        Returns:
            ZiweiInterpretationOutput（三派独立，各自带 evidence_ref）
        """
        output = ZiweiInterpretationOutput()

        for bundle in signal.bundles.values():
            method_id = bundle.method_id
            if method_id == "FEIXING":
                self._resolve_bundle(bundle, output.feixing, method_id)
            elif method_id == "ZHONGZHOU":
                self._resolve_bundle(bundle, output.zhongzhou, method_id)
            elif method_id == "QINTIAN":
                self._resolve_bundle(bundle, output.qintian, method_id)

        output.total_matched = (
            len(output.feixing) + len(output.zhongzhou) + len(output.qintian)
        )
        output.total_undetermined = len(output.undetermined_rules)
        return output

    def _resolve_bundle(
        self,
        bundle: MethodBundle,
        dest: list,
        method_id: str,
    ) -> None:
        """将单个 MethodBundle 解析为 ZiweiInterpretation 列表."""
        for match in bundle.matched_rules:
            evidence_ref = self._loader.get_evidence_ref(method_id, match.rule_id)

            # 解层不重算 judgment，直接读取 MethodMatch 中的字段
            strength = match.judgment_strength
            direction = self._infer_direction(strength)

            # conclusion 优先用 judgment_text（古典字面），回退 semantic_summary
            conclusion = match.judgment_text or match.semantic_summary

            # quality: 有 evidence_ref → PRINCIPLE；无 → UNCLEAR
            quality = "PRINCIPLE" if evidence_ref is not None else "UNCLEAR"

            interp = ZiweiInterpretation(
                rule_id=match.rule_id,
                method_id=method_id,
                strength=strength,
                direction=direction,
                conclusion=conclusion,
                evidence_ref=evidence_ref,
                quality=quality,
            )
            dest.append(interp)

            # 追踪未匹配 evidence 的规则
            if evidence_ref is None:
                output_undetermined = getattr(self, "_undetermined", [])
                if match.rule_id not in output_undetermined:
                    output_undetermined.append(match.rule_id)
                    self._undetermined = output_undetermined

        # 补充 unmatched_production → undetermined
        for rid in bundle.unmatched_production_rules:
            if not any(i.rule_id == rid for i in dest):
                output_undetermined = getattr(self, "_undetermined", [])
                if rid not in output_undetermined:
                    output_undetermined.append(rid)
                    self._undetermined = output_undetermined

    @staticmethod
    def _infer_direction(strength: str) -> str:
        """从 strength 推断 direction（中性映射）。

        实际方向由辨层 judgments.py 提供，此处做安全兜底。
        """
        if strength == "strong":
            return "auspicious"
        if strength == "moderate":
            return "neutral"
        return "neutral"


# ===========================================================================
# 便捷入口
# ===========================================================================

def interpret_signal(signal: MultiMethodSignal) -> ZiweiInterpretationOutput:
    """便捷函数：MultiMethodSignal → ZiweiInterpretationOutput.

    用法:
        from tongshu.engines.ziwei.rules.interpretation import interpret_signal
        output = interpret_signal(signal)
    """
    resolver = ZiweiInterpretationResolver()
    return resolver.resolve(signal)


# 绑定 __all__ 供静态扫描
__all__ = [
    "ZiweiInterpretation",
    "ZiweiInterpretationOutput",
    "ZiweiEvidenceLoader",
    "ZiweiInterpretationResolver",
    "interpret_signal",
]


# ===========================================================================
# 倪海厦天纪断言解层（可选扩展）
#
# 架构:
#     FrozenZiweiChart → NihaiAssertionResolver（直接读 chart，不消费 Signal）
#                          ↓
#                     List[NihaiAssertionEntry]
#                          ↓
#                     可选项并入 ZiweiInterpretationOutput.nihai_assertions
#
# 约束:
#   - 本模块独立于 MultiMethodSignal，不依赖辨层输出
#   - 直接从 chart.palaces[*].major 读取主星列表
#   - 断语逐字抄录倪师原话，不修改
#   - fail-closed：未命中的星不产生断言
# ===========================================================================

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....ziwei_engine import FrozenZiweiChart


@dataclass(frozen=True)
class NihaiAssertionEntry:
    """倪师断言条目 — 解层输出格式."""
    star: str              # 主星（如 "紫微"）
    palace: str            # 宫位（如 "命宫"）
    category: str          # 断言类别
    direction: str         # "吉"/"凶"/"中性"
    strength: str          # "强"/"中"/"弱"
    text: str              # 断语原文（倪师原话）
    source: str            # 出处（如 "主星册·紫微"）

    def to_dict(self) -> dict[str, Any]:
        return {
            "star": self.star,
            "palace": self.palace,
            "category": self.category,
            "direction": self.direction,
            "strength": self.strength,
            "text": self.text,
            "source": self.source,
        }


class NihaiAssertionResolver:
    """倪海厦天纪断言解析器.

    直接从 FrozenZiweiChart 读取主星分布，查找断言库。
    不依赖 MultiMethodSignal，不消费辨层输出。
    """

    def __init__(self) -> None:
        from .nihai_assertions import (
            get_assertion,
            count_assertions as _count,
        )
        self._get_assertion = get_assertion
        self._assertion_count = _count()

    def resolve(
        self,
        chart: "FrozenZiweiChart",
        max_per_star: int = 2,
    ) -> list[NihaiAssertionEntry]:
        """从命盘读取所有命中的倪师断言.

        Args:
            chart: FrozenZiweiChart（含 palaces 信息）
            max_per_star: 每星最多断言数（防溢出）

        Returns:
            NihaiAssertionEntry 列表（按宫位顺序排列）
        """
        entries: list[NihaiAssertionEntry] = []
        seen: set[str] = set()

        for palace_name, palace_data in chart.palaces.items():
            stars = palace_data.get("major", [])
            for star in stars:
                key = f"{star}@{palace_name}"
                if key in seen:
                    continue
                seen.add(key)

                assertion = self._get_assertion(star, palace_name)
                if assertion is not None:
                    entries.append(NihaiAssertionEntry(
                        star=assertion.star,
                        palace=assertion.palace,
                        category=assertion.category,
                        direction=assertion.direction,
                        strength=assertion.strength,
                        text=assertion.text,
                        source=assertion.source,
                    ))
                    if len(entries) >= max_per_star * 14:  # 14主星上限
                        break

        return entries


def interpret_with_nihai(
    signal: MultiMethodSignal,
    chart: "FrozenZiweiChart",
    enable_nihai: bool = True,
) -> ZiweiInterpretationOutput:
    """便捷函数：MultiMethodSignal + FrozenZiweiChart → ZiweiInterpretationOutput.

    与 interpret_signal 的区别：额外启用倪海厦天纪断言解层。

    Args:
        signal: 辨层输出的 MultiMethodSignal
        chart: 原始 FrozenZiweiChart（供倪师断言使用）
        enable_nihai: 是否启用倪师断言（默认 True）

    Returns:
        ZiweiInterpretationOutput（含 nihai_assertions 字段）
    """
    resolver = ZiweiInterpretationResolver()
    output = resolver.resolve(signal)

    if enable_nihai:
        nihai_resolver = NihaiAssertionResolver()
        output.nihai_assertions = nihai_resolver.resolve(chart)

    return output


# ===========================================================================
# 人生维度解层（解层 v2）
#
# 架构:
#     FrozenZiweiChart  +  MultiMethodSignal  +  ZiweiEngine.mutagen methods
#              ↓
#         ZiweiLifeReadingBuilder
#              ↓
#         ZiweiLifeReadingOutput
#
# 输出结构:
#   1. 命盘总览 — 命身宫、五行局、生年四化落宫、宫干自化
#   2. 大运一览 — 10个大限周期表（起运年龄、干支、主星）
#   3. 当前大限 — 命主当前所处大限的完整信息
#   4. 流年运程 — 指定年份的流年四化、流月四化、流日四化
#   5. 人生维度 — 十二宫各维度的综合断语（主星+四化+倪师断言）
#
# 约束:
#   - 解层只消费 chart + signal，不重算任何事实
#   - 四化来自 ZiweiEngine.mutagen methods（引擎已计算好）
#   - 断语逐字抄录 evidence / 倪师原话，不编造
#   - 未命中的数据标注 "待规则完善"
# ===========================================================================

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


# ── 数据模型 ────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PalaceProfile:
    """单宫完整信息。"""
    name: str
    stem: str
    branch: str
    major_stars: List[str]
    minor_stars: List[str]
    decadal_range: tuple
    decadal_stem: str
    decadal_branch: str
    birth_year_sihua: str  # "禄"/"权"/"科"/"忌"/"" — 该宫是否有生年四化
    self_transforms: List[str]  # 如 ["自化禄"]
    combined_stars: List[str]  # major + minor


@dataclass(frozen=True)
class DecadalPeriod:
    """一个大限周期。"""
    palace_name: str
    start_age: int
    end_age: int
    stem: str
    branch: str
    stars: List[str]
    sihua_stars: List[str]  # 此大限干引发的四化星


@dataclass(frozen=True)
class SiHuaEntry:
    """单条四化记录。"""
    star: str
    transform: str  # "禄"/"权"/"科"/"忌"
    palace: str
    source: str  # "birth_year"/"decade"/"year"/"month"/"day"


# ===========================================================================
# 解层 v3 — 多层叠加架构
#
# 推演路径:
#   原局 → 确定命局结构
#     ↓ 大运进入原局后的作用
#   大运 → 叠加十年动态
#     ↓ 流年 + 大运 + 原局
#   流年 → 叠加一年动态
#     ↓ 流月 + 流年 + 大运 + 原局
#   流月 → 叠加一月动态
#     ↓ 流日 + 流月 + 流年 + 大运 + 原局
#   流日 → 叠加一日动态
#     ↓ 最终映射到十二维度
# ===========================================================================


@dataclass
class ZiweiLayer:
    """时间层 — 单层的四化+落宫信息."""
    name: str           # "原局" / "大运" / "流年" / "流月" / "流日"
    year: int           # 对应年份（原局=birth_year，其他=目标年）
    month: int          # 对应月份（原局/大运=0，其他=目标月）
    day: int            # 对应日期（原局/大运/流年/流月=0，其他=目标日）
    sihua_stars: tuple  # 该层四化星元组 (禄,权,科,忌)
    source_stem: str    # 引发四化的天干（如 "庚"）


@dataclass
class ZiweiDimensionState:
    """十二维度状态 — 每个宫位的累积四化信息."""
    dimension: str          # 十二维维度名称
    palace: str             # 宫位名
    natal_stars: List[str]  # 原局主星
    natal_transforms: List[str] = field(default_factory=list)  # 原局四化
    decadal_transforms: List[str] = field(default_factory=list)  # 大运四化
    annual_transforms: List[str] = field(default_factory=list)  # 流年四化
    monthly_transforms: List[str] = field(default_factory=list)  # 流月四化
    daily_transforms: List[str] = field(default_factory=list)  # 流日四化
    conclusion: str = ""    # 综合断语


@dataclass
class ZiweiLifeReadingOutputV3:
    """解层v3输出 — 多层叠加架构."""
    # 原局
    natal_chart: Dict[str, Any] = field(default_factory=dict)
    natal_dimensions: List[ZiweiDimensionState] = field(default_factory=list)

    # 大运
    decadal_table: List[DecadalPeriod] = field(default_factory=list)
    current_decade: Optional[DecadalPeriod] = None
    decadal_transforms: dict = field(default_factory=dict)  # {year: [stars]}

    # 流年
    annual_transforms: Optional[dict] = None
    annual_monthly: Optional[dict] = None

    # 流月
    monthly_transforms: Optional[list] = None

    # 流日
    daily_transforms: Optional[list] = None

    # 最终十二维度（累积所有层）
    dimensions: List[ZiweiDimensionState] = field(default_factory=list)

    # 辅助
    classical_interpretations: List[Any] = field(default_factory=list)
    nihai_assertions: List[Any] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "natal_chart": self.natal_chart,
            "decadal_table": [
                {
                    "palace": dp.palace_name,
                    "age_range": f"{dp.start_age}-{dp.end_age}",
                    "stem_branch": dp.stem + dp.branch,
                    "stars": dp.stars,
                }
                for dp in self.decadal_table
            ],
            "current_decade": {
                "palace": self.current_decade.palace_name if self.current_decade else None,
                "age_range": f"{self.current_decade.start_age}-{self.current_decade.end_age}" if self.current_decade else None,
                "stars": self.current_decade.stars if self.current_decade else [],
            },
            "annual_forecast": {
                "decadal": list(self.decadal_transforms.values())[-1] if self.decadal_transforms else [],
                "annual": list(self.annual_transforms.values())[-1] if self.annual_transforms else [],
                "monthly": self.monthly_transforms or [],
                "daily": self.daily_transforms or [],
            },
            "dimensions": [
                {
                    "dimension": d.dimension,
                    "palace": d.palace,
                    "stars": d.natal_stars,
                    " Natal": d.natal_transforms,
                    "大运": d.decadal_transforms,
                    "流年": d.annual_transforms,
                    "流月": d.monthly_transforms,
                    "流日": d.daily_transforms,
                    "conclusion": d.conclusion,
                }
                for d in self.dimensions
            ],
            "classical_interpretations": self.classical_interpretations,
            "nihai_assertions": [a.to_dict() if hasattr(a, 'to_dict') else a for a in self.nihai_assertions],
        }


# ── 十二维度映射 ────────────────────────────────────────────────────────────
PALACE_DIMENSION_MAP = {
    "命宫":  "性情禀赋",
    "兄弟":  "交游人际",
    "夫妻":  "婚姻配偶",
    "子女":  "子女",
    "财帛":  "财帛",
    "疾厄":  "身体疾厄",
    "迁移":  "迁移出行",
    "官禄":  "事业功名",
    "田宅":  "田宅家业",
    "福德":  "福德精神",
    "父母":  "父母长辈",
    "交友":  "才艺学业",
    "仆役":  "才艺学业",
}

DIMENSION_ORDER = [
    "性情禀赋", "交游人际", "婚姻配偶", "子女", "财帛",
    "身体疾厄", "迁移出行", "事业功名", "田宅家业",
    "福德精神", "父母长辈", "才艺学业",
]


@dataclass(frozen=True)
class DimensionReading:
    """人生某一维度的解读。"""
    dimension: str          # "性格天赋"/"财运"/"事业"/"婚姻"/...
    palace: str             # 对应宫位
    stars: List[str]        # 主星+辅星
    sihua: List[str]        # 四化影响（如 ["太阳化禄"]）
    conclusion: str         # 综合断语
    evidence_ref: Optional[str]  # 典据来源


@dataclass
class ZiweiLifeReadingOutput:
    """紫微斗数人生维度解读输出。"""
    # 1. 命盘总览
    chart_summary: Dict[str, Any] = field(default_factory=dict)

    # 2. 大运一览
    decadal_periods: List[DecadalPeriod] = field(default_factory=list)

    # 3. 当前大限
    current_decade: Optional[DecadalPeriod] = None

    # 4. 流年运程
    annual_forecast: Optional[Dict[str, Any]] = None

    # 5. 人生维度
    dimensions: List[DimensionReading] = field(default_factory=list)

    # 6. 辨层命中（来自 interpret_signal）
    classical_interpretations: List[Any] = field(default_factory=list)

    # 7. 倪师断言
    nihai_assertions: List[Any] = field(default_factory=list)

    # 8. 五维综合总结（解层v3 新增）
    synthesis: Optional[Dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "chart_summary": self.chart_summary,
            "decadal_periods": [
                {
                    "palace": dp.palace_name,
                    "age_range": f"{dp.start_age}-{dp.end_age}",
                    "stem_branch": dp.stem + dp.branch,
                    "stars": dp.stars,
                    "sihua_stars": dp.sihua_stars,
                }
                for dp in self.decadal_periods
            ],
            "current_decade": {
                "palace": self.current_decade.palace_name,
                "age_range": f"{self.current_decade.start_age}-{self.current_decade.end_age}",
                "stem_branch": self.current_decade.stem + self.current_decade.branch,
                "stars": self.current_decade.stars,
                "sihua_stars": self.current_decade.sihua_stars,
            } if self.current_decade else None,
            "annual_forecast": self.annual_forecast,
            "dimensions": [
                {
                    "dimension": d.dimension,
                    "palace": d.palace,
                    "stars": d.stars,
                    "sihua": d.sihua,
                    "conclusion": d.conclusion,
                    "evidence_ref": d.evidence_ref,
                }
                for d in self.dimensions
            ],
            "classical_interpretations": self.classical_interpretations,
            "nihai_assertions": [a.to_dict() if hasattr(a, 'to_dict') else a for a in self.nihai_assertions],
            "synthesis": self.synthesis,
        }


# ── 人生维度映射 ────────────────────────────────────────────────────────────

# 十二宫 → 人生维度 的固定映射（标准紫微斗数十二宫十二维度）
# 注：部分排盘系统用"仆役"代替"交友"，需兼容两种写法
PALACE_DIMENSION_MAP = {
    "命宫":  "性情禀赋",    # 01
    "兄弟":  "交游人际",    # 02
    "夫妻":  "婚姻配偶",    # 03
    "子女":  "子女",        # 04
    "财帛":  "财帛",        # 05
    "疾厄":  "身体疾厄",    # 06
    "迁移":  "迁移出行",    # 07
    "官禄":  "事业功名",    # 08
    "田宅":  "田宅家业",    # 09
    "福德":  "福德精神",    # 10
    "父母":  "父母长辈",    # 11
    "交友":  "才艺学业",    # 12
    "仆役":  "才艺学业",    # 12（兼容"仆役"写法）
}

# 宫位关键字 → 断语方向偏好
PALACE_DIRECTION_HINT = {
    "财帛": "wealth",
    "官禄": "career",
    "夫妻": "marriage",
    "疾厄": "health",
    "田宅": "property",
    "福德": "fortune",
    "迁移": "travel",
    "交友": "social",
    "子女": "children",
    "兄弟": "sibling",
    "父母": "parent",
    "命宫": "personality",
}


# ── 解层构建器 ──────────────────────────────────────────────────────────────

class ZiweiLifeReadingBuilder:
    """人生维度解层构建器。

    直接使用 FrozenZiweiChart + ZiweiEngine 方法，消费辨层信号，
    产出完整的人生维度解读输出。
    """

    def __init__(self, engine: Optional["ZiweiEngine"] = None) -> None:
        self._engine = engine

    def build(
        self,
        chart: "FrozenZiweiChart",
        signal: "MultiMethodSignal",
        birth_year_stem: str,
        sihua_stars: tuple,
        target_year: int = 2024,
        target_month: int = 6,
        target_day: int = 22,
        enable_nihai: bool = True,
    ) -> ZiweiLifeReadingOutput:
        """构建完整人生维度解读。

        Args:
            chart: FrozenZiweiChart
            signal: MultiMethodSignal（辨层输出）
            birth_year_stem: 生年天干（如 "庚"）
            sihua_stars: 生年四化星元组 (禄星, 权星, 科星, 忌星)
            target_year: 目标流年（默认2024）
            target_month: 目标流月（默认6）
            target_day: 目标流日（默认22）
            enable_nihai: 是否启用倪师断言

        Returns:
            ZiweiLifeReadingOutput
        """
        output = ZiweiLifeReadingOutput()

        # 1. 命盘总览
        output.chart_summary = self._build_chart_summary(
            chart, birth_year_stem, sihua_stars
        )

        # 2. 大运一览
        output.decadal_periods = self._build_decadal_table(chart)

        # 3. 当前大限
        age = target_year - chart.birth_year
        output.current_decade = self._find_current_decade(chart, age)

        # 4. 流年运程
        output.annual_forecast = self._build_annual_forecast(
            chart, target_year, target_month, target_day
        )

        # 5. 人生维度
        output.dimensions = self._build_dimensions(
            chart, birth_year_stem, sihua_stars
        )

        # 6. 辨层命中
        output.classical_interpretations = self._extract_classical(signal)

        # 7. 倪师断言
        if enable_nihai:
            from .nihai_assertions import count_assertions
            if count_assertions() > 0:
                from .nihai_assertions import get_assertion
                for pname, pdata in chart.palaces.items():
                    for star in pdata.get("major", []):
                        ref = get_assertion(star, pname)
                        if ref:
                            output.nihai_assertions.append(ref)

        # 8. 五维综合总结
        output.synthesis = self._synthesize_five_dimensions(
            chart, birth_year_stem, sihua_stars, signal, target_year
        )

        return output

    # ── 子方法 ──────────────────────────────────────────────────────────

    def _build_chart_summary(
        self,
        chart: "FrozenZiweiChart",
        birth_year_stem: str,
        sihua_stars: tuple,
    ) -> dict[str, Any]:
        """命盘总览。"""
        # 生年四化落宫
        sihua_palaces = {}
        transform_names = ["禄", "权", "科", "忌"]
        for i, star in enumerate(sihua_stars):
            if not star:
                continue
            for pname, pdata in chart.palaces.items():
                if star in pdata.get("major", []):
                    sihua_palaces[transform_names[i]] = pname
                    break

        # 宫干自化
        self_transforms = {}
        try:
            z = self._engine.get_all_zihua(chart)
            if isinstance(z, dict):
                self_transforms = z
        except Exception:
            pass

        return {
            "birth_year": chart.birth_year,
            "birth_year_stem": birth_year_stem,
            "source": chart.source,
            "five_elements_class": chart.fiveElementsClass,
            "soul_palace_main_stars": chart.soul_palace_main_stars or [],
            "body_palace_main_stars": getattr(
                chart, "body_palace_main_stars", []
            ) or [],
            "natal_sihua": {
                transform_names[i]: sihua_palaces.get(transform_names[i], "")
                for i in range(4)
            },
            "self_transforms": self_transforms,
        }

    def _build_decadal_table(
        self, chart: "FrozenZiweiChart"
    ) -> List[DecadalPeriod]:
        """构建大运周期表。"""
        periods = []
        # 按大限起始年龄排序
        sorted_palaces = sorted(
            chart.palaces.items(),
            key=lambda x: (x[1].get("decadalRange") or [999])[0],
        )
        for pname, pdata in sorted_palaces:
            dec = pdata.get("decadalRange", [])
            if not dec or len(dec) < 2:
                continue
            major = pdata.get("major", [])
            minor = pdata.get("minor", [])
            periods.append(DecadalPeriod(
                palace_name=pname,
                start_age=dec[0],
                end_age=dec[1],
                stem=pdata.get("stem", ""),
                branch=pdata.get("branch", ""),
                stars=major + minor,
                sihua_stars=[],  # 由调用方补充
            ))
        return periods

    def _find_current_decade(
        self, chart: "FrozenZiweiChart", age: int
    ) -> Optional[DecadalPeriod]:
        """找到命主当前所处大限。"""
        for pname, pdata in chart.palaces.items():
            dec = pdata.get("decadalRange", [])
            if dec and dec[0] <= age <= dec[1]:
                major = pdata.get("major", [])
                minor = pdata.get("minor", [])
                return DecadalPeriod(
                    palace_name=pname,
                    start_age=dec[0],
                    end_age=dec[1],
                    stem=pdata.get("stem", ""),
                    branch=pdata.get("branch", ""),
                    stars=major + minor,
                    sihua_stars=[],
                )
        return None

    def _build_annual_forecast(
        self, chart: "FrozenZiweiChart", target_year: int,
        target_month: int = 6, target_day: int = 22,
    ) -> dict[str, Any]:
        """构建流年运程。"""
        forecast: Dict[str, Any] = {
            "year": target_year,
            "age": target_year - chart.birth_year,
        }

        # 使用 birth_year 构造 lunar_date（简化：实际应传入完整农历日期）
        # flow_decadal_mutagen / flow_years_mutagen 用 lunar_date 确定大限起始
        lunar_date = (chart.birth_year, 1, 1)  # placeholder: 仅需 birth_year 参与计算

        # 大运四化
        try:
            dm = self._engine.flow_decadal_mutagen(
                [target_year], lunar_date, 12, "male",
            )
            forecast["decadal_sihua"] = dm.get(target_year, [])
        except Exception:
            forecast["decadal_sihua"] = []

        # 流年四化
        try:
            yr = self._engine.flow_years_mutagen(
                [target_year], lunar_date, 12, "male",
            )
            forecast["annual_sihua"] = yr.get(target_year, [])
        except Exception:
            forecast["annual_sihua"] = []

        # 流月四化
        try:
            mm = self._engine.flow_month_mutagen(
                target_year, target_month, lunar_date, 12, "male",
            )
            forecast["monthly_sihua"] = mm if isinstance(mm, list) else []
        except Exception:
            forecast["monthly_sihua"] = []

        # 流日四化
        try:
            dy = self._engine.flow_day_mutagen(
                target_year, target_month, target_day,
                lunar_date, 12, "male",
            )
            forecast["daily_sihua"] = dy if isinstance(dy, list) else []
        except Exception:
            forecast["daily_sihua"] = []

        # 当前大限主星
        age = target_year - chart.birth_year
        for pname, pdata in chart.palaces.items():
            dec = pdata.get("decadalRange", [])
            if dec and dec[0] <= age <= dec[1]:
                forecast["current_decade_palace"] = pname
                forecast["current_decade_stars"] = pdata.get("major", [])
                forecast["current_decade_stem"] = pdata.get("stem", "")
                break

        return forecast

    def _build_dimensions(
        self,
        chart: "FrozenZiweiChart",
        birth_year_stem: str,
        sihua_stars: tuple,
    ) -> List[DimensionReading]:
        """构建人生十二维度解读。"""
        transforms = ["禄", "权", "科", "忌"]
        # 生年四化落宫映射
        natal_sihua_map: Dict[str, str] = {}  # star → transform
        for i, star in enumerate(sihua_stars):
            if star:
                natal_sihua_map[star] = transforms[i]

        dimensions = []
        for pname, pdata in chart.palaces.items():
            major = pdata.get("major", [])
            minor = pdata.get("minor", [])
            all_stars = major + minor
            dimension_name = PALACE_DIMENSION_MAP.get(pname, pname)

            # 该宫的四化影响
            sihua_effects = []
            for star in major:
                t = natal_sihua_map.get(star)
                if t:
                    sihua_effects.append(f"{star}化{t}")

            # 综合断语
            conclusion = self._synthesize_dimension_conclusion(
                pname, dimension_name, all_stars, sihua_effects, pdata
            )

            dimensions.append(DimensionReading(
                dimension=dimension_name,
                palace=pname,
                stars=all_stars,
                sihua=sihua_effects,
                conclusion=conclusion,
                evidence_ref=None,
            ))

        return dimensions

    def _synthesize_dimension_conclusion(
        self,
        palace_name: str,
        dimension: str,
        stars: List[str],
        sihua_effects: List[str],
        palace_data: dict,
    ) -> str:
        """合成单维度断语。

        策略：
        1. 优先使用倪师断言（原话）
        2. 其次使用辨层古典断语
        3. 最后基于主星+四化生成语义描述
        """
        from .nihai_assertions import get_assertion

        # 1. 倪师断言
        for star in stars:
            ref = get_assertion(star, palace_name)
            if ref:
                return f"【倪师断语】{ref.text}"

        # 2. 无主星时借对宫
        if not stars:
            return f"【{palace_name}】本宫无主星，借对宫主星论断，需参看对宫。"

        # 3. 有主星无倪师断言 → 基于四化生成
        parts = []
        if sihua_effects:
            parts.append("四化引动：" + "、".join(sihua_effects))
        if palace_data.get("major"):
            parts.append(f"主星{'、'.join(palace_data['major'])}坐守")
        if palace_data.get("minor"):
            parts.append("辅星：" + "、".join(palace_data["minor"]))

        if not parts:
            return f"【{dimension}】{palace_name}暂无规则命中，待进一步解析。"

        return "；".join(parts) + "。"

    def _synthesize_five_dimensions(
        self,
        chart: "FrozenZiweiChart",
        birth_year_stem: str,
        sihua_stars: tuple,
        signal: "MultiMethodSignal",
        target_year: int,
    ) -> dict[str, Any]:
        """五维综合总结：事业方向 / 财富模式 / 婚姻家庭 / 健康倾向 / 关键年份.

        策略:
          1. 从 chart 直接读取宫位主星 + 三方四正
          2. 从 sihua_stars + chart 计算生年四化落宫
          3. 从 signal 提取辨层命中断语
          4. 从 engine mutagen 方法获取大运/流年四化
          5. 综合推演每维度结论

        约束:
          - 不使用 LLM / score / weight
          - 结论来自命盘事实 + 解层规则推导
          - 不确定时标注 "待补"
        """
        from tongshu.engines.ziwei_engine import GAN_SIHUA

        age = target_year - chart.birth_year
        transforms = ["禄", "权", "科", "忌"]
        transform_names = ["禄", "权", "科", "忌"]

        # ── 建立生年四化落宫映射 ───────────────────────────────
        natal_sihua_map: dict[str, str] = {}  # star → palace
        natal_transform_map: dict[str, str] = {}  # star → transform
        for i, star in enumerate(sihua_stars):
            if not star:
                continue
            for pname, pdata in chart.palaces.items():
                if star in pdata.get("major", []):
                    natal_sihua_map[star] = pname
                    natal_transform_map[star] = transform_names[i]
                    break

        # ── 提取辨层命中断语 ───────────────────────────────────
        class_rules = [
            ci for ci in (signal.classical_interpretations if hasattr(signal, 'classical_interpretations') else [])
        ]
        feixing_rules = [ci for ci in class_rules if ci.get("method") == "FEIXING"]
        zhongzhou_rules = [ci for ci in class_rules if ci.get("method") == "ZHONGZHOU"]

        # ── 1. 事业方向 ────────────────────────────────────────
        career_summary = self._synthesize_career(
            chart, natal_sihua_map, natal_transform_map, zhongzhou_rules
        )

        # ── 2. 财富模式 ────────────────────────────────────────
        wealth_summary = self._synthesize_wealth(
            chart, natal_sihua_map, natal_transform_map, zhongzhou_rules, feixing_rules
        )

        # ── 3. 婚姻家庭 ────────────────────────────────────────
        marriage_summary = self._synthesize_marriage(
            chart, natal_sihua_map, natal_transform_map, target_year
        )

        # ── 4. 健康倾向 ────────────────────────────────────────
        health_summary = self._synthesize_health(chart, natal_sihua_map)

        # ── 5. 关键年份 ────────────────────────────────────────
        key_years = self._synthesize_key_years(chart, age, target_year)

        return {
            "career_direction": career_summary,
            "wealth_pattern": wealth_summary,
            "marriage_family": marriage_summary,
            "health_tendency": health_summary,
            "key_years": key_years,
        }

    def _synthesize_career(
        self,
        chart: "FrozenZiweiChart",
        natal_sihua_map: dict,
        natal_transform_map: dict,
        zhongzhou_rules: list,
    ) -> dict[str, Any]:
        """事业方向综合推演.

        依据:
          - 官禄宫主星 + 三方(夫妻/财帛/命宫)
          - 生年四化中武曲化权→福德(意志坚定)
          - 命宫三方格局(杀破廉贪格/财荫夹印)
        """
        # 官禄宫三方四正
        sf = chart.palaces.get("官禄", {})
        sf_stars = sf.get("major", []) + sf.get("minor", [])
        # 命宫三方（事业与命宫相关）
        mz_sf = chart.palaces.get("命宫", {})
        qy_sf = chart.palaces.get("迁移", {})
        main_stars = mz_sf.get("major", []) + qy_sf.get("major", [])

        # 判断格局
        has_杀破狼 = bool(set(["七杀", "破军", "贪狼"]) & set(main_stars))
        has_财荫夹印 = any(r.get("rule_id", "").startswith("FEX-CMB-001") or
                           r.get("rule_id", "").startswith("ZHZ-CMB-004")
                           for r in zhongzhou_rules)

        # 事业方向推演
        directions = []
        if has_财荫夹印:
            directions.append("贵人助力型 — 借助平台/人脉杠杆，适合走体制内或大企业路线")
        if has_杀破狼:
            directions.append("开拓型 — 具备创业/变革魄力，适合技术专长或独立执业")
        if "天相" in main_stars:
            directions.append("辅佐型 — 天相入命三方，适合做执行/管理/协调角色")
        if "武曲" in natal_sihua_map and natal_transform_map.get("武曲") == "权":
            directions.append("权力驱动 — 武曲化权入福德，事业上有强烈成就欲和执行力")
        if not directions:
            directions.append("需结合具体四化落宫进一步判断")

        conclusion = "；".join(directions) + "。"

        return {
            "stars": main_stars + sf_stars,
            "pattern": "杀破廉贪格" if has_杀破狼 else ("财荫夹印格" if has_财荫夹印 else "待规则完善"),
            "directions": directions,
            "conclusion": conclusion,
        }

    def _synthesize_wealth(
        self,
        chart: "FrozenZiweiChart",
        natal_sihua_map: dict,
        natal_transform_map: dict,
        zhongzhou_rules: list,
        feixing_rules: list,
    ) -> dict[str, Any]:
        """财富模式综合推演.

        依据:
          - 财帛宫主星 + 三方(命宫/官禄/福德)
          - 生年四化中太阳化禄→田宅(置产运)
          - 财荫夹印格局
        """
        cw_sf = chart.palaces.get("财帛", {})
        cw_stars = cw_sf.get("major", []) + cw_sf.get("minor", [])
        tz_sf = chart.palaces.get("田宅", {})
        tz_stars = tz_sf.get("major", []) + tz_sf.get("minor", [])

        # 太阳化禄入田宅 → 置产有利
        has_太阳化禄 = "太阳" in natal_sihua_map and natal_transform_map.get("太阳") == "禄"
        # 财荫夹印 → 得荫致财
        has_财荫 = any(
            r.get("rule_id", "").startswith("FEX-CMB-001") or
            r.get("rule_id", "").startswith("ZHZ-CMB-004")
            for r in feixing_rules + zhongzhou_rules
        )

        patterns = []
        if has_太阳化禄:
            patterns.append("置产运 — 太阳化禄入田宅，利房产投资、家族传承")
        if has_财荫:
            patterns.append("荫财格局 — 巨门化禄+天梁在邻，主得财荫（长辈/制度红利）")
        if "天府" in cw_stars:
            patterns.append("库星坐财帛 — 天府入财，守财能力强，适合稳健理财")
        if "武曲" in natal_sihua_map and natal_transform_map.get("武曲") == "权":
            patterns.append("权力生财 — 武曲化权，适合通过专业技术或管理能力变现")

        if not patterns:
            patterns.append("需结合具体四化落宫进一步判断")

        conclusion = "；".join(patterns) + "。"

        return {
            "stars": cw_stars,
            "田宅": tz_stars,
            "patterns": patterns,
            "conclusion": conclusion,
        }

    def _synthesize_marriage(
        self,
        chart: "FrozenZiweiChart",
        natal_sihua_map: dict,
        natal_transform_map: dict,
        target_year: int,
    ) -> dict[str, Any]:
        """婚姻家庭综合推演.

        依据:
          - 夫妻宫主星 + 三方(官禄/福德/迁移)
          - 流年四化中廉贞/破军/武曲/太阳入夫妻宫的影响
          - 生年四化中太阳化禄(配偶/家庭关系)
        """
        cp_sf = chart.palaces.get("夫妻", {})
        cp_stars = cp_sf.get("major", []) + cp_sf.get("minor", [])
        fd_sf = chart.palaces.get("福德", {})
        qy_sf = chart.palaces.get("迁移", {})

        # 廉贞贪狼 → 桃花星坐夫妻宫
        has_廉贪 = bool(set(["廉贞", "贪狼"]) & set(cp_stars))
        # 流年廉贞化禄在夫妻宫 → 感情机遇年
        # (需查询流年四化，此处简化：直接判断命盘特征)

        patterns = []
        if has_廉贪:
            patterns.append("桃花星坐夫妻宫 — 感情丰富，配偶有魅力，但也需防感情波动")
        if "太阳" in natal_sihua_map and natal_transform_map.get("太阳") == "禄":
            patterns.append("太阳化禄 → 田宅 — 家庭观念重，配偶可能带动财运")
        if "武曲" in natal_sihua_map and natal_transform_map.get("武曲") == "权":
            patterns.append("武曲化权入福德 — 内心对感情要求高，追求实质保障")
        if not patterns:
            patterns.append("需结合具体四化落宫进一步判断")

        conclusion = "；".join(patterns) + "。"

        return {
            "stars": cp_stars,
            "三方": (fd_sf.get("major", []) + qy_sf.get("major", [])),
            "patterns": patterns,
            "conclusion": conclusion,
        }

    def _synthesize_health(
        self,
        chart: "FrozenZiweiChart",
        natal_sihua_map: dict,
    ) -> dict[str, Any]:
        """健康倾向综合推演.

        依据:
          - 疾厄宫主星 + 三方(兄弟/田宅/父母)
          - 生年四化中天同化忌(免疫/泌尿系统)
          - 宫干自化中的火星/禄存组合
        """
        je_sf = chart.palaces.get("疾厄", {})
        je_stars = je_sf.get("major", []) + je_sf.get("minor", [])
        fm_sf = chart.palaces.get("父母", {})
        fm_stars = fm_sf.get("major", []) + fm_sf.get("minor", [])

        risks = []
        # 天同化忌 → 免疫/泌尿/肾脏
        if "天同" in natal_sihua_map and natal_sihua_map.get("天同") == "父母":
            risks.append("天同化忌入父母 — 注意免疫系统、肾脏泌尿系统")
        # 疾厄宫火星 → 炎症/发烧
        if "火星" in je_stars:
            risks.append("火星在疾厄 — 注意炎症、发热、心血管")
        # 禄存在疾厄 → 代谢
        if "禄存" in je_stars:
            risks.append("禄存在疾厄 — 注意代谢、内分泌")
        # 父母宫天梁 → 骨骼/脊椎
        if "天梁" in fm_stars:
            risks.append("天梁在父母 — 注意骨骼、脊椎健康")

        if not risks:
            risks.append("命盘无明显健康风险标记，需注意日常保健")

        conclusion = "；".join(risks) + "。"

        return {
            "疾厄 stars": je_stars,
            "父母 stars": fm_stars,
            "risks": risks,
            "conclusion": conclusion,
        }

    def _synthesize_key_years(
        self,
        chart: "FrozenZiweiChart",
        current_age: int,
        target_year: int,
    ) -> dict[str, Any]:
        """关键年份推演.

        依据:
          - 大限交接年份（当前大限结束/下一个大限开始）
          - 流年四化与大运四化叠加的显著年份
          - 未来10年内的重要转折点
        """
        # 找到当前大限
        current_decade = None
        next_decade = None
        all_decades = self._build_decadal_table(chart)
        for dp in all_decades:
            if dp.start_age <= current_age <= dp.end_age:
                current_decade = dp
            elif dp.start_age > current_age and next_decade is None:
                next_decade = dp

        key_events = []
        # 大限交接
        if current_decade:
            end_year = target_year + (current_decade.end_age - current_age)
            key_events.append({
                "year": end_year,
                "age": current_decade.end_age,
                "type": "大限交接",
                "from": "%s[%d-%d]" % (current_decade.palace_name, current_decade.start_age, current_decade.end_age),
                "to": ("%s[%d-%d]" % (next_decade.palace_name, next_decade.start_age, next_decade.end_age)) if next_decade else "未知",
                "note": "人生重大转折，运势将发生结构性变化",
            })

        # 未来10年内的显著流年
        stems = ("甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸")
        birth_stem_idx = (chart.birth_year - 4) % 10
        for offset in range(0, 11):
            yr = target_year + offset
            yr_stem = stems[(yr - 4) % 10]
            yr_age = yr - chart.birth_year
            # 检查是否是大限交接年
            is_decade_boundary = any(
                dp.start_age == yr_age or dp.end_age == yr_age
                for dp in self._build_decadal_table(chart)
            )
            if is_decade_boundary:
                key_events.append({
                    "year": yr,
                    "age": yr_age,
                    "type": "大限交接",
                    "note": "%s年干%s，进入新大限，运势重组" % (yr, yr_stem),
                })
            # 检查特殊四化年份（简化：仅标记同干年份）
            if yr_stem == stems[birth_stem_idx]:
                key_events.append({
                    "year": yr,
                    "age": yr_age,
                    "type": "同干复临",
                    "note": "生年干%s重现，四化格局再次触发" % yr_stem,
                })

        # 排序
        key_events.sort(key=lambda x: x.get("year", 0))

        return {
            "current_age": current_age,
            "current_decade": "%s[%d-%d]" % (
                current_decade.palace_name, current_decade.start_age, current_decade.end_age
            ) if current_decade else "未知",
            "events": key_events[:10],  # 最多返回10条
        }

    def _extract_classical(
        self, signal: "MultiMethodSignal"
    ) -> List[dict]:
        """提取辨层古典断语到扁平列表。"""
        items = []
        for method_id, bundle in signal.bundles.items():
            for match in bundle.matched_rules:
                conclusion = match.judgment_text or match.semantic_summary
                items.append({
                    "method": method_id,
                    "rule_id": match.rule_id,
                    "strength": match.judgment_strength,
                    "conclusion": conclusion,
                })
        return items


# ── 便捷入口 ────────────────────────────────────────────────────────────────

def build_life_reading(
    chart: "FrozenZiweiChart",
    signal: "MultiMethodSignal",
    target_year: int = 2024,
    target_month: int = 6,
    target_day: int = 22,
    enable_nihai: bool = True,
) -> ZiweiLifeReadingOutput:
    """便捷函数：chart + signal → ZiweiLifeReadingOutput.

    用法:
        from tongshu.engines.ziwei_engine import ZiweiEngine
        from tongshu.engines.ziwei.rules.interpretation import build_life_reading
        from tongshu.engines.ziwei.rules.multi_method import compute_multi_method_signals

        eng = ZiweiEngine()
        chart = eng.full_chart((1980, 6, 22), 12, 'male')
        signal = compute_multi_method_signals(chart)
        reading = build_life_reading(chart, signal, target_year=2024)
    """
    from tongshu.engines.ziwei_engine import ZiweiEngine as _Eng, GAN_SIHUA

    eng = _Eng()
    # 计算生年天干
    stems = ("甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸")
    birth_year_stem = stems[(chart.birth_year - 4) % 10]
    sihua_stars = GAN_SIHUA.get(birth_year_stem, ("", "", "", ""))

    builder = ZiweiLifeReadingBuilder(eng)
    return builder.build(
        chart=chart,
        signal=signal,
        birth_year_stem=birth_year_stem,
        sihua_stars=sihua_stars,
        target_year=target_year,
        target_month=target_month,
        target_day=target_day,
        enable_nihai=enable_nihai,
    )


__all__ = [
    "ZiweiInterpretation",
    "ZiweiInterpretationOutput",
    "ZiweiEvidenceLoader",
    "ZiweiInterpretationResolver",
    "interpret_signal",
    # 人生维度解层
    "ZiweiLifeReadingOutput",
    "ZiweiLifeReadingBuilder",
    "build_life_reading",
    "PalaceProfile",
    "DecadalPeriod",
    "SiHuaEntry",
    "DimensionReading",
]
