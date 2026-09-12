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
    brightness: Dict[str, str] = field(default_factory=dict)  # {star: "庙"/"旺"/"得"/"利"/"平"/"弱"/"陷"}
    branch: str = ""  # 地支（丑/寅/...）用于查亮度
    borrowed_from: Optional[str] = None  # 对宫来源（空宫借对宫主星时用）
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
    """紫微斗数人生维度解读输出（v2 兼容占位，新代码用 ZiweiLifeReadingOutputV3）。"""
    pass


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


# ── 对宫映射（空宫借对宫主星）──────────────────────────────────────────────
OPPOSITE_PALACE: Dict[str, str] = {
    "命宫":  "迁移",
    "迁移":  "命宫",
    "兄弟":  "仆役",
    "仆役":  "兄弟",
    "夫妻":  "官禄",
    "官禄":  "夫妻",
    "子女":  "田宅",
    "田宅":  "子女",
    "财帛":  "福德",
    "福德":  "财帛",
    "疾厄":  "父母",
    "父母":  "疾厄",
}


# ── 庙旺利陷亮度表 ───────────────────────────────────────────────────────
_BRANCH_IDX = {"子":1,"丑":2,"寅":3,"卯":4,"辰":5,"巳":6,
               "午":7,"未":8,"申":9,"酉":10,"戌":11,"亥":12}

STAR_BRIGHTNESS: Dict[str, Dict[str, str]] = {
    "紫微": {
        "子":"旺","丑":"庙","寅":"平","卯":"弱","辰":"庙","巳":"旺",
        "午":"庙","未":"旺","申":"得","酉":"弱","戌":"庙","亥":"旺",
    },
    "天机": {
        "子":"庙","丑":"旺","寅":"庙","卯":"旺","辰":"平","巳":"陷",
        "午":"平","未":"旺","申":"庙","酉":"旺","戌":"平","亥":"陷",
    },
    "太阳": {
        "子":"陷","丑":"陷","寅":"旺","卯":"旺","辰":"旺","巳":"旺",
        "午":"庙","未":"旺","申":"旺","酉":"陷","戌":"陷","亥":"陷",
    },
    "武曲": {
        "子":"庙","丑":"旺","寅":"平","卯":"陷","辰":"庙","巳":"旺",
        "午":"得","未":"平","申":"庙","酉":"旺","戌":"平","亥":"陷",
    },
    "天同": {
        "子":"旺","丑":"庙","寅":"平","卯":"陷","辰":"庙","巳":"旺",
        "午":"庙","未":"平","申":"旺","酉":"陷","戌":"庙","亥":"旺",
    },
    "廉贞": {
        "子":"庙","丑":"平","寅":"平","卯":"庙","辰":"旺","巳":"陷",
        "午":"庙","未":"平","申":"平","酉":"庙","戌":"旺","亥":"陷",
    },
    "天府": {
        "子":"旺","丑":"庙","寅":"旺","卯":"庙","辰":"庙","巳":"旺",
        "午":"庙","未":"旺","申":"庙","酉":"庙","戌":"庙","亥":"旺",
    },
    "太阴": {
        "子":"旺","丑":"旺","寅":"陷","卯":"庙","辰":"旺","巳":"庙",
        "午":"陷","未":"陷","申":"旺","酉":"庙","戌":"旺","亥":"庙",
    },
    "贪狼": {
        "子":"庙","丑":"旺","寅":"庙","卯":"旺","辰":"旺","巳":"庙",
        "午":"陷","未":"旺","申":"庙","酉":"旺","戌":"旺","亥":"庙",
    },
    "巨门": {
        "子":"陷","丑":"庙","寅":"旺","卯":"旺","辰":"庙","巳":"陷",
        "午":"旺","未":"陷","申":"旺","酉":"旺","戌":"庙","亥":"陷",
    },
    "天相": {
        "子":"旺","丑":"庙","寅":"陷","卯":"庙","辰":"旺","巳":"庙",
        "午":"陷","未":"旺","申":"庙","酉":"旺","戌":"庙","亥":"陷",
    },
    "天梁": {
        "子":"旺","丑":"庙","寅":"陷","卯":"庙","辰":"旺","巳":"庙",
        "午":"陷","未":"旺","申":"庙","酉":"旺","戌":"庙","亥":"陷",
    },
    "七杀": {
        "子":"旺","丑":"庙","寅":"庙","卯":"旺","辰":"庙","巳":"旺",
        "午":"庙","未":"旺","申":"庙","酉":"旺","戌":"庙","亥":"旺",
    },
    "破军": {
        "子":"庙","丑":"陷","寅":"庙","卯":"旺","辰":"陷","巳":"庙",
        "午":"旺","未":"陷","申":"庙","酉":"旺","戌":"陷","亥":"庙",
    },
}

# 各宫位主星断语模板库
PALACE_STAR_RULES: Dict[str, Dict[str, List[Dict[str, str]]]] = {
    # ── 性情禀赋（命宫）──
    "性情禀赋": {
        "紫微": [
            {"brightness":["庙","旺","得"],"text":"领袖气质强，有统御之才，但需防孤高自赏"},
            {"brightness":["平","弱","陷"],"text":"志大才疏，领导力受阻，宜借势而行"},
        ],
        "天机": [
            {"brightness":["庙","旺"],"text":"聪明机智，思维敏捷，善谋略策划"},
            {"brightness":["平","弱","陷"],"text":"思虑过多，优柔寡断，神经质倾向"},
        ],
        "太阳": [
            {"brightness":["庙","旺"],"text":"光明磊落，热心公益，有博爱之心"},
            {"brightness":["平","弱","陷"],"text":"心力交瘁，付出多收获少，宜低调隐忍"},
        ],
        "武曲": [
            {"brightness":["庙","旺","得"],"text":"刚毅果断，理财能力强，实干型人格"},
            {"brightness":["平","弱","陷"],"text":"刚愎自用，财运起伏大，宜修柔和之德"},
        ],
        "天同": [
            {"brightness":["庙","旺"],"text":"福厚安乐，性格温和，不喜竞争，随缘自在"},
            {"brightness":["平","弱","陷"],"text":"懒散依赖，缺乏进取心，需自立自强"},
        ],
        "廉贞": [
            {"brightness":["庙","旺"],"text":"精明干练，社交能力强，有艺术气质"},
            {"brightness":["平","弱","陷"],"text":"感情用事，易陷桃色纠纷，需修身养性"},
        ],
        "天府": [
            {"brightness":["庙","旺","得"],"text":"稳重包容，善于守成，有库星之能，理财有方"},
            {"brightness":["平","弱","陷"],"text":"保守过头，优柔寡断，错失良机"},
        ],
        "太阴": [
            {"brightness":["庙","旺"],"text":"温柔细腻，心思缜密，女命尤佳，男命亦主内敛沉稳"},
            {"brightness":["平","弱","陷"],"text":"情绪波动大，内心敏感脆弱，需心理调适"},
        ],
        "贪狼": [
            {"brightness":["庙","旺"],"text":"多才多艺，善交际，有野心也有执行力"},
            {"brightness":["平","弱","陷"],"text":"欲望过度，易沉迷声色，需节制收敛"},
        ],
        "巨门": [
            {"brightness":["庙","旺"],"text":"口才出众，善辩论，研究能力极强"},
            {"brightness":["平","弱","陷"],"text":"口舌是非多，宜谨言慎行，以技术立身"},
        ],
        "天相": [
            {"brightness":["庙","旺","得"],"text":"辅佐之才，做事周到，重信誉，位高无权"},
            {"brightness":["平","弱","陷"],"text":"优柔寡断，缺乏主见，易受他人左右"},
        ],
        "天梁": [
            {"brightness":["庙","旺"],"text":"长者风范，乐于助人，有监察之才，逢凶化吉"},
            {"brightness":["平","弱","陷"],"text":"孤克之象，助人反被累，宜专注自身"},
        ],
        "七杀": [
            {"brightness":["庙","旺","得"],"text":"魄力十足，敢闯敢拼，适合开拓型事业"},
            {"brightness":["平","弱","陷"],"text":"冲动冒进，易招意外，宜三思而后行"},
        ],
        "破军": [
            {"brightness":["庙","旺"],"text":"破旧立新，敢于变革，具开创精神"},
            {"brightness":["平","弱","陷"],"text":"破坏力有余建设力不足，需稳中求进"},
        ],
    },
    # ── 婚姻配偶（夫妻）──
    "婚姻配偶": {
        "紫微": [
            {"brightness":["庙","旺"],"text":"配偶尊贵或有社会地位，但需防对方强势"},
            {"brightness":["平","弱","陷"],"text":"感情波折多，配偶关系复杂，需包容沟通"},
        ],
        "天机": [
            {"brightness":["庙","旺"],"text":"配偶聪明灵巧，感情丰富多变，宜晚婚"},
            {"brightness":["平","弱","陷"],"text":"感情不稳定，易有第三者介入，需防信任危机"},
        ],
        "太阳": [
            {"brightness":["庙","旺"],"text":"配偶光明磊落，事业有成，男命得助力"},
            {"brightness":["平","弱","陷"],"text":"配偶关系疏离，付出多回报少，宜聚少离多"},
        ],
        "武曲": [
            {"brightness":["庙","旺"],"text":"配偶刚毅务实，理财能手，但缺少浪漫情趣"},
            {"brightness":["平","弱","陷"],"text":"感情冷漠，易因财生变，需增进情感交流"},
        ],
        "天同": [
            {"brightness":["庙","旺"],"text":"配偶温和体贴，感情和谐，但需防对方依赖性强"},
            {"brightness":["平","弱","陷"],"text":"感情平淡如水，缺乏激情，宜培养共同兴趣"},
        ],
        "廉贞": [
            {"brightness":["庙","旺"],"text":"配偶魅力四射，感情丰富，但需防桃花纠纷"},
            {"brightness":["平","弱","陷"],"text":"感情波折大，易有第三者，需修身养性防烂桃花"},
        ],
        "天府": [
            {"brightness":["庙","旺"],"text":"配偶稳重可靠，持家有道，感情稳定"},
            {"brightness":["平","弱","陷"],"text":"配偶过于保守，缺乏情趣，需主动经营关系"},
        ],
        "太阴": [
            {"brightness":["庙","旺"],"text":"配偶温柔贤淑，感情细腻，女命尤佳"},
            {"brightness":["平","弱","陷"],"text":"感情多变，配偶情绪不稳，需耐心呵护"},
        ],
        "贪狼": [
            {"brightness":["庙","旺"],"text":"配偶魅力出众，感情丰富，但需防外遇风险"},
            {"brightness":["平","弱","陷"],"text":"感情混乱，烂桃花多，宜晚婚或聚少离多"},
        ],
        "巨门": [
            {"brightness":["庙","旺"],"text":"配偶口才好，但易有口舌之争，需谨言慎行"},
            {"brightness":["平","弱","陷"],"text":"感情多口舌是非，沟通障碍大，宜找年龄差距大的对象"},
        ],
        "天相": [
            {"brightness":["庙","旺"],"text":"配偶外貌端正，为人正直，感情稳定"},
            {"brightness":["平","弱","陷"],"text":"感情平淡，配偶易受外界影响，需加强信任"},
        ],
        "天梁": [
            {"brightness":["庙","旺"],"text":"配偶成熟稳重，有长者风范，宜找年长或成熟的对象"},
            {"brightness":["平","弱","陷"],"text":"感情孤独，配偶关系冷淡，宜聚少离多以保和谐"},
        ],
        "七杀": [
            {"brightness":["庙","旺"],"text":"配偶刚强独立，事业心强，但需防争执"},
            {"brightness":["平","弱","陷"],"text":"感情波动大，配偶性格急躁，宜晚婚"},
        ],
        "破军": [
            {"brightness":["庙","旺"],"text":"感情有大变化，配偶个性强烈，宜晚婚或聚少离多"},
            {"brightness":["平","弱","陷"],"text":"感情多变不稳定，易有分离之象，需经营维护"},
        ],
    },
    # ── 财帛 ──
    "财帛": {
        "紫微": [{"text":"财来财去，宜置产守财，不宜投机"}],
        "天机": [{"text":"动脑赚钱，灵活求财，宜技术或咨询行业"}],
        "太阳": [{"text":"花钱大方，宜公益投资，男命财来财去"}],
        "武曲": [
            {"brightness":["庙","旺"],"text":"财星入庙，理财能力强，宜金融或实业"},
            {"brightness":["平","弱","陷"],"text":"财运起伏大，宜稳健理财，不宜高风险投机"},
        ],
        "天同": [{"text":"福气生财，宜安稳行业，不宜投机取巧"}],
        "廉贞": [{"text":"偏财运佳，但需防桃花破财"}],
        "天府": [{"text":"库星坐财，守财能力强，适合稳健投资和置产"}],
        "太阴": [
            {"brightness":["庙","旺"],"text":"财星入庙，善于积累，宜房地产或长期投资"},
            {"brightness":["平","弱","陷"],"text":"财运不稳，宜储蓄为主，不宜大额投资"},
        ],
        "贪狼": [{"text":"偏财运强，但需防因贪破财，宜正当途径求财"}],
        "巨门": [{"text":"口才生财，宜律师、讲师、销售等行业"}],
        "天相": [{"text":"正财运稳，宜辅佐他人得财，不宜独立创业"}],
        "天梁": [{"text":"荫财格局，得长辈或制度红利，宜稳健理财"}],
        "七杀": [{"text":"财运波动大，宜技术专长变现，不宜投机"}],
        "破军": [{"text":"先破后立，财运有大起大落，宜置产保值"}],
    },
    # ── 事业功名（官禄）──
    "事业功名": {
        "紫微": [
            {"brightness":["庙","旺"],"text":"领导型人才，宜管理或创业，有大发展"},
            {"brightness":["平","弱","陷"],"text":"志向远大但执行力不足，宜借平台发展"},
        ],
        "天机": [{"text":"谋略型人才，宜策划、咨询、技术类工作"}],
        "太阳": [
            {"brightness":["庙","旺"],"text":"公众人物，宜公益、教育、媒体等发挥影响力"},
            {"brightness":["平","弱","陷"],"text":"劳心劳力，宜低调行事，以专业立身"},
        ],
        "武曲": [
            {"brightness":["庙","旺"],"text":"实干型人才，宜金融、工程、技术类职业"},
            {"brightness":["平","弱","陷"],"text":"财运与事业并重，需防冲动决策"},
        ],
        "天同": [{"text":"福荫之业，宜稳定工作，不宜冒险创业"}],
        "廉贞": [
            {"brightness":["庙","旺"],"text":"多才多艺，宜创意、演艺、公关类工作"},
            {"brightness":["平","弱","陷"],"text":"感情影响事业，需专注专业发展"},
        ],
        "天府": [{"text":"守成之才，适合大企业稳定发展，不宜频繁跳槽"}],
        "太阴": [
            {"brightness":["庙","旺"],"text":"细腻专业型人才，宜设计、财务、内务类工作"},
            {"brightness":["平","弱","陷"],"text":"事业上易受情绪影响，需培养稳定性"},
        ],
        "贪狼": [{"text":"多才多艺，适合销售、公关、娱乐等需要人缘的行业"}],
        "巨门": [{"text":"口舌生财，宜律师、讲师、谈判等以口才为业的职业"}],
        "天相": [{"text":"辅佐之才，适合执行、管理、协调类岗位，位高无权"}],
        "天梁": [
            {"brightness":["庙","旺"],"text":"监察型人才，宜监督、审计、医疗、法律等需要原则性的职业"},
            {"brightness":["平","弱","陷"],"text":"助人反被累，宜专注专业技术，减少人际关系消耗"},
        ],
        "七杀": [{"text":"开拓型人才，适合创业、军警、工程等需要魄力的行业"}],
        "破军": [{"text":"变革型人才，适合创新、转型行业，不宜守成"}],
    },
    # ── 迁移出行 ──
    "迁移出行": {
        "紫微": [
            {"brightness":["庙","旺"],"text":"出外遇贵人，在外发展优于在家"},
            {"brightness":["平","弱","陷"],"text":"外出多波折，宜谨慎选择发展方向"},
        ],
        "天机": [{"text":"动中求财，适合奔波型工作，不宜久居一地"}],
        "太阳": [
            {"brightness":["庙","旺"],"text":"出外得志，宜离家发展，远行有利"},
            {"brightness":["平","弱","陷"],"text":"外出劳心劳力，宜就近发展"},
        ],
        "武曲": [{"text":"出外求财辛苦，宜技术谋生，不宜投机"}],
        "天同": [{"text":"出外有福，宜去宜居之地发展，不宜高压环境"}],
        "廉贞": [
            {"brightness":["庙","旺"],"text":"出外有人缘，适合社交型发展"},
            {"brightness":["平","弱","陷"],"text":"外出易陷是非，宜低调行事"},
        ],
        "天府": [{"text":"出外安稳，宜去稳定环境发展"}],
        "太阴": [
            {"brightness":["庙","旺"],"text":"出外得财，女命尤佳，男命亦利"},
            {"brightness":["平","弱","陷"],"text":"外出多忧，不宜远行"},
        ],
        "贪狼": [{"text":"出外有人缘桃花，适合社交型工作"}],
        "巨门": [{"text":"出外多口舌是非，宜低调，以技术立身"}],
        "天相": [{"text":"出外有贵人，宜去有人脉基础的地区"}],
        "天梁": [
            {"brightness":["庙","旺"],"text":"出外逢凶化吉，适合去有长者贵人之地"},
            {"brightness":["平","弱","陷"],"text":"出外孤立无援，宜就近发展"},
        ],
        "七杀": [{"text":"出外动荡多变化，宜去有挑战性的环境"}],
        "破军": [{"text":"出外变化大，先破后立，适合开创新局"}],
    },
    # ── 福德精神 ──
    "福德精神": {
        "紫微": [
            {"brightness":["庙","旺"],"text":"精神世界丰富，有追求和理想"},
            {"brightness":["平","弱","陷"],"text":"精神压力较大，内心孤独"},
        ],
        "天机": [{"text":"思虑多，精神易紧张，宜修身养性减压"}],
        "太阳": [
            {"brightness":["庙","旺"],"text":"心胸开阔，精神明朗乐观"},
            {"brightness":["平","弱","陷"],"text":"操心劳神，精神疲惫，宜学会放下"},
        ],
        "武曲": [
            {"brightness":["庙","旺"],"text":"意志坚定，精神刚毅，有执行力"},
            {"brightness":["平","弱","陷"],"text":"内心刚硬，缺乏柔情，需修柔和"},
        ],
        "天同": [
            {"brightness":["庙","旺"],"text":"福气深厚，精神安乐，心态平和"},
            {"brightness":["平","弱","陷"],"text":"精神懈怠，缺乏进取动力"},
        ],
        "廉贞": [
            {"brightness":["庙","旺"],"text":"精神丰富，有艺术感知力"},
            {"brightness":["平","弱","陷"],"text":"精神波动大，易陷入情感困扰"},
        ],
        "天府": [{"text":"精神稳重，心态平和，善于自我调节"}],
        "太阴": [
            {"brightness":["庙","旺"],"text":"内心细腻温柔，有艺术天赋"},
            {"brightness":["平","弱","陷"],"text":"内心敏感脆弱，易受情绪影响"},
        ],
        "贪狼": [{"text":"精神世界丰富，欲望多，需节制修心"}],
        "巨门": [{"text":"思虑深沉，精神内耗大，宜专注一门深入"}],
        "天相": [{"text":"心地善良，精神平和，乐于助人"}],
        "天梁": [
            {"brightness":["庙","旺"],"text":"精神境界高，有超脱之象"},
            {"brightness":["平","弱","陷"],"text":"精神孤高，易感孤独"},
        ],
        "七杀": [{"text":"内心刚强，精神上有压力和斗志"}],
        "破军": [{"text":"精神世界变化大，有革新和突破的冲动"}],
    },
    # ── 田宅家业 ──
    "田宅家业": {
        "紫微": [{"text":"家运平稳，有置业机会，宜置产"}],
        "天机": [{"text":"家宅有变动，宜灵活安排"}],
        "太阳": [
            {"brightness":["庙","旺"],"text":"置产运佳，利房产投资和家庭传承"},
            {"brightness":["平","弱","陷"],"text":"家运一般，宜保守理财"},
        ],
        "武曲": [{"text":"家运稳健，宜踏实守成"}],
        "天同": [{"text":"家运安乐，有福气，适合居家生活"}],
        "廉贞": [{"text":"家宅有桃花之象，宜注意家庭和谐"}],
        "天府": [{"text":"库星入宅，置产运佳，守财能力强"}],
        "太阴": [
            {"brightness":["庙","旺"],"text":"置产运佳，适合房地产投资"},
            {"brightness":["平","弱","陷"],"text":"家运波动，宜储蓄为主"},
        ],
        "贪狼": [{"text":"家宅有变动，宜稳定为主"}],
        "巨门": [{"text":"家宅多口舌，宜注意家庭沟通"}],
        "天相": [{"text":"家运平稳，宜稳中求进"}],
        "天梁": [{"text":"家运有荫庇，可得长辈助力置业"}],
        "七杀": [{"text":"家宅有变动，不宜大额投资"}],
        "破军": [{"text":"家宅有破耗，宜置产保值，不宜投机"}],
    },
    # ── 身体疾厄 ──
    "身体疾厄": {
        "紫微": [{"text":"体质强健，但需注意脾胃和消化系统"}],
        "天机": [{"text":"注意神经系统、肝胆，需防失眠焦虑"}],
        "太阳": [
            {"brightness":["庙","旺"],"text":"体质良好，注意心血管和眼睛"},
            {"brightness":["平","弱","陷"],"text":"体虚易疲劳，注意心脑血管保健"},
        ],
        "武曲": [{"text":"注意呼吸系统、肺部，戒烟养生"}],
        "天同": [
            {"brightness":["庙","旺"],"text":"福气之体，体质较好"},
            {"brightness":["平","弱","陷"],"text":"注意泌尿系统、肾脏，天同化忌尤需注意"},
        ],
        "廉贞": [{"text":"注意心血管、炎症，需防情绪影响健康"}],
        "天府": [{"text":"体质稳定，注意消化系统保健"}],
        "太阴": [
            {"brightness":["庙","旺"],"text":"体质良好，女性需注意妇科"},
            {"brightness":["平","弱","陷"],"text":"体质偏弱，需注意内分泌和妇科"},
        ],
        "贪狼": [{"text":"注意肝肾、生殖系统，需节制欲望"}],
        "巨门": [{"text":"注意呼吸系统、咽喉，需防呼吸道疾病"}],
        "天相": [{"text":"体质稳定，注意皮肤和泌尿系统"}],
        "天梁": [
            {"brightness":["庙","旺"],"text":"逢凶化吉，体质较好"},
            {"brightness":["平","弱","陷"],"text":"注意骨骼、脊椎，需防慢性病"},
        ],
        "七杀": [{"text":"注意外伤、意外，需防手术，注意肺部"}],
        "破军": [{"text":"注意肾水系统、泌尿系统，身体易有突发变化"}],
    },
    # ── 子女 ──
    "子女": {
        "紫微": [{"text":"子女有出息，但管教需得当"}],
        "天机": [{"text":"子女聪明伶俐，但多思多虑"}],
        "太阳": [
            {"brightness":["庙","旺"],"text":"子女光明磊落，有成就"},
            {"brightness":["平","弱","陷"],"text":"子女缘分较浅，需多关心"},
        ],
        "武曲": [{"text":"子女独立坚强，宜培养独立性"}],
        "天同": [
            {"brightness":["庙","旺"],"text":"子女福气厚，性格温和"},
            {"brightness":["平","弱","陷"],"text":"子女依赖性强，需培养自立"},
        ],
        "廉贞": [{"text":"子女有艺术天赋，但需引导正道"}],
        "天府": [{"text":"子女稳重可靠，家业可托"}],
        "太阴": [
            {"brightness":["庙","旺"],"text":"子女温柔贤淑，缘分深"},
            {"brightness":["平","弱","陷"],"text":"子女缘分较淡，需用心培养"},
        ],
        "贪狼": [{"text":"子女多才多艺，但需防欲望过度"}],
        "巨门": [{"text":"子女口才好，但需防口舌是非"}],
        "天相": [{"text":"子女正直善良，缘分和睦"}],
        "天梁": [{"text":"子女成熟稳重，可得助力"}],
        "七杀": [{"text":"子女个性强，需耐心引导"}],
        "破军": [{"text":"子女变化多，宜培养独立能力"}],
    },
    # ── 交游人际（兄弟）──
    "交游人际": {
        "紫微": [{"text":"人脉广博，但需防小人"}],
        "天机": [{"text":"朋友多但关系不稳，宜慎选朋友圈"}],
        "太阳": [
            {"brightness":["庙","旺"],"text":"朋友众多，贵人多助"},
            {"brightness":["平","弱","陷"],"text":"付出多回报少，宜选择真朋友"},
        ],
        "武曲": [{"text":"朋友务实，宜志同道合者"}],
        "天同": [{"text":"朋友和气，宜交温和之友"}],
        "廉贞": [{"text":"朋友多桃花，宜防烂桃花"}],
        "天府": [{"text":"朋友稳定可靠，贵人运佳"}],
        "太阴": [
            {"brightness":["庙","旺"],"text":"朋友细腻真诚，缘分深"},
            {"brightness":["平","弱","陷"],"text":"朋友关系多变，需用心经营"},
        ],
        "贪狼": [{"text":"朋友多但关系复杂，宜精简朋友圈"}],
        "巨门": [{"text":"朋友间易有口舌，宜谨言慎行"}],
        "天相": [{"text":"朋友正直可靠，宜交益友"}],
        "天梁": [{"text":"朋友中有长者贵人，可得助力"}],
        "七杀": [{"text":"朋友关系动荡，宜少交游多专注"}],
        "破军": [{"text":"朋友聚散无常，宜珍惜真心朋友"}],
    },
    # ── 父母长辈 ──
    "父母长辈": {
        "紫微": [{"text":"长辈有威严，关系和睦"}],
        "天机": [{"text":"与长辈沟通需耐心，思虑多"}],
        "太阳": [
            {"brightness":["庙","旺"],"text":"长辈缘分深，可得助力"},
            {"brightness":["平","弱","陷"],"text":"与长辈缘分浅，需主动维系"},
        ],
        "武曲": [{"text":"长辈务实严厉，关系较疏"}],
        "天同": [
            {"brightness":["庙","旺"],"text":"长辈慈爱，缘分深"},
            {"brightness":["平","弱","陷"],"text":"天同化忌，注意长辈健康，免疫/肾脏"},
        ],
        "廉贞": [{"text":"与长辈关系复杂，需耐心沟通"}],
        "天府": [{"text":"长辈稳重可靠，可得庇护"}],
        "太阴": [
            {"brightness":["庙","旺"],"text":"母亲缘分深，可得母爱"},
            {"brightness":["平","弱","陷"],"text":"母亲身体较弱，需多关心"},
        ],
        "贪狼": [{"text":"长辈人缘好，但关系复杂"}],
        "巨门": [{"text":"与长辈易有隔阂，需主动沟通"}],
        "天相": [{"text":"长辈正直，关系和睦"}],
        "天梁": [
            {"brightness":["庙","旺"],"text":"长辈有德行，可得长者指导"},
            {"brightness":["平","弱","陷"],"text":"注意长辈骨骼健康，天梁落陷宜多检查"},
        ],
        "七杀": [{"text":"与长辈关系紧张，需主动改善"}],
        "破军": [{"text":"与长辈缘分波动大，宜保持距离"}],
    },
    # ── 才艺学业（交友/仆役）──
    "才艺学业": {
        "紫微": [{"text":"学习能力强，有领导才华"}],
        "天机": [
            {"brightness":["庙","旺"],"text":"聪明好学，适合学术研究"},
            {"brightness":["平","弱","陷"],"text":"思虑过多，宜专注一门深入"},
        ],
        "太阳": [
            {"brightness":["庙","旺"],"text":"学识广博，适合公开表达和学习"},
            {"brightness":["平","弱","陷"],"text":"学习吃力，需更努力"},
        ],
        "武曲": [{"text":"适合技术型学习，动手能力强"}],
        "天同": [
            {"brightness":["庙","旺"],"text":"学习轻松，有福气学业运"},
            {"brightness":["平","弱","陷"],"text":"学习懈怠，需培养自律"},
        ],
        "廉贞": [{"text":"有艺术天赋，适合创意类学习"}],
        "天府": [{"text":"学习稳重，适合系统性学习"}],
        "太阴": [
            {"brightness":["庙","旺"],"text":"心思细腻，适合艺术和设计类学习"},
            {"brightness":["平","弱","陷"],"text":"学习易受情绪影响"},
        ],
        "贪狼": [{"text":"多才多艺，兴趣广泛，适合艺术娱乐类学习"}],
        "巨门": [{"text":"口才出众，适合法律、外语等以口为业的学习"}],
        "天相": [{"text":"学习能力强，适合管理协调类学习"}],
        "天梁": [
            {"brightness":["庙","旺"],"text":"好学深思，适合研究类学习"},
            {"brightness":["平","弱","陷"],"text":"学习孤独，需独自用功"},
        ],
        "七杀": [{"text":"行动力强，适合实践型学习"}],
        "破军": [{"text":"学习变化多，适合创新探索型学习"}],
    },
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
    ) -> ZiweiLifeReadingOutputV3:
        """构建完整人生维度解读 — 多层叠加 pipeline.

        推演路径:
          原局 → 大运 → 流年 → 流月 → 流日 → 十二维度

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
            ZiweiLifeReadingOutputV3
        """
        output = ZiweiLifeReadingOutputV3()
        age = target_year - chart.birth_year
        lunar_date = (chart.birth_year, target_month, target_day)

        # ── Layer 0: 原局 ───────────────────────────────────────────────────
        output.natal_chart = self._build_chart_summary(
            chart, birth_year_stem, sihua_stars
        )
        output.natal_dimensions = self._init_natal_dimensions(chart, sihua_stars)

        # ── Layer 1: 大运 ───────────────────────────────────────────────────
        output.decadal_table = self._build_decadal_table(chart)
        output.current_decade = self._find_current_decade(chart, age)
        dm_result = self._call_mutagen(
            lambda eng: eng.flow_decadal_mutagen([target_year], lunar_date, 12, "male")
        )
        output.decadal_transforms = dm_result or {}

        # ── Layer 2: 流年 ───────────────────────────────────────────────────
        yr_result = self._call_mutagen(
            lambda eng: eng.flow_years_mutagen([target_year], lunar_date, 12, "male")
        )
        output.annual_transforms = yr_result or {}
        mm_result = self._call_mutagen(
            lambda eng: eng.flow_month_mutagen(target_year, target_month, lunar_date, 12, "male")
        )
        output.annual_monthly = mm_result if isinstance(mm_result, list) else {}

        # ── Layer 3: 流月 ───────────────────────────────────────────────────
        output.monthly_transforms = mm_result if isinstance(mm_result, list) else []

        # ── Layer 4: 流日 ───────────────────────────────────────────────────
        dy_result = self._call_mutagen(
            lambda eng: eng.flow_day_mutagen(target_year, target_month, target_day, lunar_date, 12, "male")
        )
        output.daily_transforms = dy_result if isinstance(dy_result, list) else []

        # ── 最终映射到十二维度 ───────────────────────────────────────────────
        output.dimensions = self._map_to_dimensions(
            chart, output.natal_dimensions,
            output.decadal_transforms, output.annual_transforms,
            output.monthly_transforms, output.daily_transforms,
            sihua_stars, birth_year_stem,
        )

        # ── 辅助数据 ────────────────────────────────────────────────────────
        output.classical_interpretations = self._extract_classical(signal)

        if enable_nihai:
            from .nihai_assertions import count_assertions
            if count_assertions() > 0:
                from .nihai_assertions import get_assertion
                for pname, pdata in chart.palaces.items():
                    for star in pdata.get("major", []):
                        ref = get_assertion(star, pname)
                        if ref:
                            output.nihai_assertions.append(ref)

        return output

    def _call_mutagen(self, fn):
        """安全调用 mutagen 方法，失败返回 None."""
        if self._engine is None:
            return None
        try:
            return fn(self._engine)
        except Exception:
            return None

    # ── Layer 0: 原局 ─────────────────────────────────────────────────────

    def _init_natal_dimensions(
        self,
        chart: "FrozenZiweiChart",
        sihua_stars: tuple,
    ) -> List[ZiweiDimensionState]:
        """原局维度初始化 — 各宫主星 + 生年四化."""
        transforms = ["禄", "权", "科", "忌"]
        natal_map: dict[str, str] = {}  # star → palace
        natal_transform_map: dict[str, str] = {}  # star → transform
        for i, star in enumerate(sihua_stars):
            if not star:
                continue
            for pname, pdata in chart.palaces.items():
                if star in pdata.get("major", []):
                    natal_map[star] = pname
                    natal_transform_map[star] = transforms[i]
                    break

        dimensions = []
        for pname, pdata in chart.palaces.items():
            dim_name = PALACE_DIMENSION_MAP.get(pname, pname)
            major = pdata.get("major", [])
            minor = pdata.get("minor", [])
            sihua_effects = []
            # branch may be wrapped in quotes by iztro stub
            raw_branch = str(pdata.get("branch", "")).strip("'\"")
            branch = raw_branch if raw_branch else ""
            # 空宫借对宫主星
            borrowed_from = None
            borrowed_stars = []
            if not major:
                opp = OPPOSITE_PALACE.get(pname)
                if opp:
                    opp_data = chart.palaces.get(opp, {})
                    opp_major = opp_data.get("major", [])
                    if opp_major:
                        borrowed_from = opp
                        borrowed_stars = opp_major
            # 查亮度（含借来的主星，用本宫地支查亮度）
            brightness: dict[str, str] = {}
            all_major = major + borrowed_stars
            for star in all_major:
                if star in STAR_BRIGHTNESS and branch in STAR_BRIGHTNESS[star]:
                    brightness[star] = STAR_BRIGHTNESS[star][branch]
            for star in major:
                t = natal_transform_map.get(star)
                if t:
                    sihua_effects.append(f"{star}化{t}")
            dimensions.append(ZiweiDimensionState(
                dimension=dim_name,
                palace=pname,
                natal_stars=major + minor + borrowed_stars,
                natal_transforms=sihua_effects,
                brightness=brightness,
                branch=branch,
                borrowed_from=borrowed_from,
            ))
        return dimensions

    # ── 最终映射 ──────────────────────────────────────────────────────────

    def _map_to_dimensions(
        self,
        chart: "FrozenZiweiChart",
        natal_dims: List[ZiweiDimensionState],
        decadal_transforms: dict,
        annual_transforms: dict,
        monthly_transforms: list,
        daily_transforms: list,
        birth_sihua_stars: tuple,
        birth_year_stem: str,
    ) -> List[ZiweiDimensionState]:
        """将多层四化叠加到十二维度，生成最终断语."""
        transforms = ["禄", "权", "科", "忌"]
        # 建立各层 star→transform 映射
        natal_tm: dict[str, str] = {}
        for i, star in enumerate(birth_sihua_stars):
            if star:
                natal_tm[star] = transforms[i]

        # 大运四化映射（取目标年的大运四化）
        decade_tm: dict[str, str] = {}
        decade_list = decadal_transforms.get(list(decadal_transforms.keys())[-1], []) if decadal_transforms else []
        for i, star in enumerate(decade_list):
            if star and i < 4:
                decade_tm[star] = transforms[i]

        # 流年四化映射
        annual_tm: dict[str, str] = {}
        annual_list = annual_transforms.get(list(annual_transforms.keys())[-1], []) if annual_transforms else []
        for i, star in enumerate(annual_list):
            if star and i < 4:
                annual_tm[star] = transforms[i]

        # 流月/流日四化映射
        monthly_tm: dict[str, str] = {}
        for i, star in enumerate(monthly_transforms[:4] if monthly_transforms else []):
            if star:
                monthly_tm[star] = transforms[i]
        daily_tm: dict[str, str] = {}
        for i, star in enumerate(daily_transforms[:4] if daily_transforms else []):
            if star:
                daily_tm[star] = transforms[i]

        # 合并到每个维度
        result = []
        for dim in natal_dims:
            state = ZiweiDimensionState(
                dimension=dim.dimension,
                palace=dim.palace,
                natal_stars=dim.natal_stars,
                natal_transforms=list(dim.natal_transforms),
                decadal_transforms=[],
                annual_transforms=[],
                monthly_transforms=[],
                daily_transforms=[],
                brightness=dict(dim.brightness),
                branch=dim.branch,
                borrowed_from=dim.borrowed_from,
            )
            # 检查该宫位的星曜在各层的四化
            for star in dim.natal_stars:
                if star in decade_tm:
                    state.decadal_transforms.append(f"{star}化{decade_tm[star]}")
                if star in annual_tm:
                    state.annual_transforms.append(f"{star}化{annual_tm[star]}")
                if star in monthly_tm:
                    state.monthly_transforms.append(f"{star}化{monthly_tm[star]}")
                if star in daily_tm:
                    state.daily_transforms.append(f"{star}化{daily_tm[star]}")
            # 生成综合断语
            state.conclusion = self._synthesize_dimension_conclusion(dim.palace, dim.dimension, dim.natal_stars, state)
            result.append(state)
        return result

    def _synthesize_dimension_conclusion(
        self,
        palace_name: str,
        dimension: str,
        stars: List[str],
        state: ZiweiDimensionState,
    ) -> str:
        """合成单维度断语 — 基于多层四化叠加 + 庙旺利陷 + 维度专属规则."""
        from .nihai_assertions import get_assertion as _get_assertion

        parts = []

        # 1. 倪师断言（命宫优先）
        if palace_name == "命宫":
            main = [s for s in stars if s in STAR_BRIGHTNESS]
            for star in main:
                try:
                    ref = _get_assertion(star, palace_name)
                    if ref:
                        parts.append(f"【倪师断语】{ref.text}")
                        break
                except Exception:
                    pass

        # 2. 维度专属断语（主星 + 庙旺利陷 → 对应维度规则）
        main_stars = [s for s in stars if s in STAR_BRIGHTNESS]
        if main_stars and dimension in PALACE_STAR_RULES:
            dim_rules = PALACE_STAR_RULES[dimension]
            rule_parts = []
            for star in main_stars:
                rules = dim_rules.get(star, [])
                if not rules:
                    continue
                brightness_val = state.brightness.get(star, "")
                # 匹配亮度
                matched = None
                for r in rules:
                    bw = r.get("brightness")
                    if bw and brightness_val in bw:
                        matched = r
                        break
                if matched is None:
                    matched = rules[0]  # fallback to first rule
                rule_parts.append(matched.get("text", ""))
            if rule_parts:
                parts.append("；".join(rule_parts))

        # 3. 各层四化叠加
        all_transforms = (state.natal_transforms + state.decadal_transforms +
                         state.annual_transforms + state.monthly_transforms +
                         state.daily_transforms)
        if all_transforms:
            parts.append("四化引动：" + "、".join(all_transforms))

        # 4. 辅星
        non_main = [s for s in stars if s not in STAR_BRIGHTNESS]
        if non_main:
            parts.append("辅星：" + "、".join(non_main))

        if not parts:
            return "【%s】%s暂无主星，借对宫论断。" % (dimension, palace_name)

        return "；".join(parts) + "。"

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
) -> ZiweiLifeReadingOutputV3:
    """便捷函数：chart + signal → ZiweiLifeReadingOutputV3.

    推演路径: 原局 → 大运 → 流年 → 流月 → 流日 → 十二维度

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
    # 人生维度解层 v3
    "ZiweiLifeReadingOutputV3",
    "ZiweiLifeReadingOutput",
    "ZiweiLifeReadingBuilder",
    "build_life_reading",
    "PalaceProfile",
    "DecadalPeriod",
    "SiHuaEntry",
    "DimensionReading",
    "ZiweiLayer",
    "ZiweiDimensionState",
    "PALACE_DIMENSION_MAP",
    "DIMENSION_ORDER",
]
