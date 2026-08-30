# -*- coding: utf-8 -*-
"""IMP-08 V2: 四体系交叉验证流年事件评估层

架构:
  ┌─ 子平/盲派 ─────┐
  │                │
命局 ──┼─ 紫微斗数 ──┼→ 独立体系信号
  │                │
  ├─ 河洛理数 ────┤
  │                │
  └─ 易经 ────────┘
          ↓
    ┌──────────────┐
    │  交叉验证层   │
    └──────────────┘
          ↓
     事件主题识别 (灾劫/财运)
    ┌─────────┴─────────┐
    风险评分            机会评分
    └─────────┬─────────┘
              ↓
         年份 Ranking
              ↓
        证据链 / 解释
"""

import sys
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

sys.path.insert(0, 'src')

from tongshu.engines.bazi_engine import BaziEngine, Pillar
from tongshu.engines.time_resolver import TimeResolver
from tongshu.engines.heluo import heluo_calculate, HeluoInput
from tongshu.engines.strength_engine import evaluate_strength  # [DEPRECATED] evaluate_strength 已退回 UNRESOLVED stub (TASK-001)
from ..signal.convergence import ConvergenceArbiter, ConvergenceOutcome
from ..signal.canonical_signal import CanonicalSignal

# === 常量定义 ===
STEM = ["JIA", "YI", "BING", "DING", "WU", "JI", "GENG", "XIN", "REN", "GUI"]
BRANCH = ["ZI", "CHOU", "YIN", "MAO", "CHEN", "SI", "WU", "WEI", "SHEN", "YOU", "XU", "HAI"]
STEM_ELEM = {"JIA": "木", "YI": "木", "BING": "火", "DING": "火", "WU": "土", "JI": "土",
             "GENG": "金", "XIN": "金", "REN": "水", "GUI": "水"}
GEN = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}  # 我生
KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}  # 我克

# 地支关系
CLASH = {"ZI": "WU", "CHOU": "WEI", "YIN": "SHEN", "MAO": "YOU", "CHEN": "XU", "SI": "HAI"}
HARM = {"ZI": "WEI", "CHOU": "WU", "YIN": "SI", "MAO": "CHEN", "SHEN": "HAI", "YOU": "XU"}
PUNISH = {("YIN", "SI"), ("SI", "SHEN"), ("SHEN", "YIN"),
          ("CHOU", "XU"), ("XU", "WEI"), ("WEI", "CHOU"),
          ("ZI", "MAO"), ("MAO", "ZI")}
XC = {"ZI": "HAI", "CHOU": "ZI", "YIN": "CHOU", "MAO": "YIN", "CHEN": "MAO", "SI": "CHEN",
      "WU": "SI", "WEI": "WU", "SHEN": "WEI", "YOU": "SHEN", "XU": "YOU", "HAI": "XU"}


# === 数据结构 ===

@dataclass
class SystemSignal:
    """单体系独立信号"""
    system: str  # 'bazi', 'heluo', 'yi'
    score: float
    evidence: str
    confidence: float  # 0-1


@dataclass
class AnnualPrediction:
    """流年预测结果"""
    year: int
    disaster_score: float  # 灾劫评分
    wealth_score: float    # 财运评分
    signals: list[SystemSignal] = field(default_factory=list)
    evidence_chain: list[str] = field(default_factory=list)


@dataclass
class EventResult:
    """事件评测结果"""
    case_id: str
    predicted: str  # 预测答案 (A/B/C/D/E)
    actual: str    # 实际答案
    correct: bool
    disaster_score: float
    wealth_score: float
    evidence: list[str]


# === 体系 1: 子平/盲派 ===

class BaziScorer:
    """子平/盲派流年评分

    V2.5 fix: 原逻辑十神吉凶固定(七杀/劫财/枭神/伤官统一+2.0灾劫), 不结合旺衰结果.
    传统命理: 十神吉凶取决于旺衰 — 身强喜官杀食伤财、忌印比; 身弱喜印比、忌官杀食伤财.
    修复后: 根据旺衰verdict动态判断忌神/喜神, 忌神加灾劫分, 喜神不加(甚至减分).
    """

    # 十神→类型映射: 比劫/食伤/财/印/官杀
    _TEN_GOD_TYPE = {
        "比肩": "COMPANION", "劫财": "COMPANION",
        "食神": "EATING", "伤官": "EATING",
        "偏财": "WEALTH", "正财": "WEALTH",
        "正印": "SEAL", "枭神": "SEAL",
        "正官": "OFFICIAL", "七杀": "OFFICIAL",
    }

    # 各旺衰类型的忌神集合
    _UNFAVORABLE_BY_VERDICT = {
        "身强": {"SEAL", "COMPANION"},           # 身强忌印比
        "身弱": {"OFFICIAL", "EATING", "WEALTH"}, # 身弱忌官杀食伤财
        "从强": {"OFFICIAL"},                      # 从强忌官杀破局
        "从弱": {"SEAL", "COMPANION"},             # 从弱忌印比破局
    }

    def __init__(self):
        self.engine = BaziEngine()
        self.resolver = TimeResolver()

    def _is_unfavorable(self, ten_god: str, verdict: str) -> bool:
        """判断十神是否为忌神(基于旺衰结果). 假从格按普通身强/身弱处理."""
        tg_type = self._TEN_GOD_TYPE.get(ten_god)
        if tg_type is None:
            return False
        # 假从格按普通身强/身弱处理
        v = verdict
        if "(假)" in v:
            v = "身强" if "从强" in v else "身弱"
        unfavorable = self._UNFAVORABLE_BY_VERDICT.get(v, set())
        return tg_type in unfavorable

    def _is_favorable_wealth(self, ten_god: str, verdict: str) -> bool:
        """判断十神是否为财运喜神(财星+食伤, 且非忌神)."""
        tg_type = self._TEN_GOD_TYPE.get(ten_god)
        if tg_type is None:
            return False
        if tg_type in ("WEALTH", "EATING"):
            return not self._is_unfavorable(ten_god, verdict)
        return False

    def ten_god(self, dm: str, st: str) -> str:
        """十神计算"""
        de, s = STEM_ELEM[dm], STEM_ELEM[st]
        dy, sy = (STEM.index(dm) % 2 == 0), (STEM.index(st) % 2 == 0)
        same = (dy == sy)
        if s == de: return "比肩" if same else "劫财"
        if GEN[de] == s: return "食神" if same else "伤官"
        if KE[de] == s: return "偏财" if same else "正财"
        if GEN[s] == de: return "枭神" if same else "正印"
        return "七杀" if same else "正官"

    def ganzhi(self, year: int) -> tuple:
        """干支计算"""
        return STEM[(year - 4) % 10], BRANCH[(year - 4) % 12]

    def score_disaster(self, dm: str, fs: str, fb: str, fourb: list, verdict: str = "身弱") -> float:
        """灾劫评分: 忌神十神 + 冲刑害. V2.5: 结合旺衰动态判断忌神."""
        s = 0.0
        g = self.ten_god(dm, fs)
        # V2.5: 忌神十神加灾劫分, 喜神不加(甚至减分表示化解)
        if self._is_unfavorable(g, verdict):
            s += 2.0
        elif g in ("正官", "正印", "食神", "正财"):
            # 喜神/中性十神, 轻微减分表示平顺
            s -= 0.3

        # 地支关系(冲刑害加灾劫分, 但如果冲的是忌神支则减分)
        for b in fourb:
            if CLASH.get(fb) == b:
                s += 1.5
            if (fb, b) in PUNISH or (b, fb) in PUNISH:
                s += 1.5
            if HARM.get(fb) == b:
                s += 1.0
        return max(s, 0.0)

    def score_wealth(self, dm: str, fs: str, fb: str, fourb: list, verdict: str = "身弱") -> float:
        """财运评分: 财星/食伤喜神 + 生扶. V2.5: 结合旺衰动态判断喜神."""
        s = 0.0
        g = self.ten_god(dm, fs)
        # V2.5: 财运喜神(财星+食伤且非忌神)加财运分
        if self._is_favorable_wealth(g, verdict):
            if g in ("正财", "偏财"):
                s += 2.5
            else:  # 食神/伤官
                s += 1.5
        elif g in ("正官", "正印"):
            s += 0.3  # 中性, 轻微加分

        # 地支生扶(我克为财, 但需非忌神)
        for b in fourb:
            if KE.get(fb) == b:  # 我克为财
                s += 1.0
        return max(s, 0.0)

    def compute(self, birth_year: int, birth_month: int, birth_day: int,
                birth_hour: int, gender: str) -> tuple:
        """【DEPRECATED】计算命局和流年信号, V2.5: 同时返回旺衰结果

        STATUS: DEPRECATED — evaluate_strength 已退回 UNRESOLVED stub (TASK-001).
        本方法保留 API, 但 verdict 始终为空字符串.
        """
        chart = self.engine.compute((birth_year, birth_month, birth_day, birth_hour), gender=gender)
        dm = chart.day_master
        fourb = [chart.year_pillar.earthly_branch, chart.month_pillar.earthly_branch,
                 chart.day_pillar.earthly_branch, chart.hour_pillar.earthly_branch]
        # [DEPRECATED] evaluate_strength 已移除生产调用链
        strength = evaluate_strength(chart)
        verdict = strength.verdict or "UNRESOLVED"
        return dm, fourb, chart, verdict


# === 体系 2: 河洛理数 ===

class HeluoScorer:
    """河洛理数流年评分.

    V3: 优先使用实际河洛流年卦吉凶方向(heluo_yi_flow.gua_direction),
    无出生信息时fallback到数理模运算.
    """

    def score_disaster(self, chart, luoshu_num: int, year: int) -> float:
        """河洛灾劫评分 (fallback: 数理模运算)."""
        s = 0.0
        tian_shu = luoshu_num
        if tian_shu % 5 == 0:  # 土数，主静，不利动
            s += 0.5
        if tian_shu % 2 == 1:  # 阳数，主动，可能有变动
            s += 0.3
        return s

    def score_wealth(self, chart, luoshu_num: int, year: int) -> float:
        """河洛财运评分 (fallback: 数理模运算)."""
        s = 0.0
        tian_shu = luoshu_num
        if tian_shu % 5 == 1 or tian_shu % 5 == 2:  # 1,2 木数，主生发
            s += 0.8
        if tian_shu % 2 == 0:  # 阴数，主聚
            s += 0.5
        return s

    def score_year_direction(
        self, birth_y: int, birth_m: int, birth_d: int,
        hour: int, gender: str, year: int,
    ) -> float:
        """V3: 使用实际河洛流年卦吉凶方向. 返回-1(凶)~+1(吉).

        无流年卦时返回0.0(中平).
        """
        try:
            from tongshu.engines.heluo_yi_flow import get_liunian_gua, gua_direction
            gua = get_liunian_gua(birth_y, birth_m, birth_d, hour, gender, year)
            if gua is None:
                return 0.0
            return gua_direction(gua["upper"], gua["lower"], gua["hexagram"])
        except Exception:
            return 0.0

    def score_disaster_from_direction(self, direction: float) -> float:
        """从方向分转换为灾劫分: 方向越凶灾劫越高."""
        if direction >= 0:
            return max(0.0, 0.3 - direction * 0.3)  # 吉年灾劫低
        return min(2.0, 0.5 + abs(direction) * 1.5)  # 凶年灾劫高

    def score_wealth_from_direction(self, direction: float) -> float:
        """从方向分转换为财运分: 方向越吉财运越高."""
        if direction <= 0:
            return max(0.0, 0.3 + direction * 0.3)  # 凶年财运低
        return min(2.5, 0.5 + direction * 2.0)  # 吉年财运高


# === 体系 3: 易经 ===

class YiScorer:
    """易经流年评分.

    V3: 优先使用实际河洛流年卦的易经卦象吉凶(卦辞+爻辞),
    无出生信息时fallback到年干五行.
    """

    def __init__(self):
        try:
            from tongshu.engines.yi.hexagram_symbol import HexagramSymbol
            self.yi_available = True
        except ImportError:
            self.yi_available = False

    def score_disaster(self, chart, year: int) -> float:
        """易经灾劫评分 (fallback: 年干五行)."""
        if not self.yi_available:
            return 0.0
        s = 0.0
        stem_idx = (year - 4) % 10
        if stem_idx in [2, 3]:  # 丙丁火，主变
            s += 0.3
        return s

    def score_wealth(self, chart, year: int) -> float:
        """易经财运评分 (fallback: 年干五行)."""
        if not self.yi_available:
            return 0.0
        s = 0.0
        stem_idx = (year - 4) % 10
        if stem_idx in [0, 1]:  # 甲乙木，主生
            s += 0.3
        return s

    def score_year_direction(
        self, birth_y: int, birth_m: int, birth_d: int,
        hour: int, gender: str, year: int,
    ) -> float:
        """V3: 使用实际易经卦象吉凶方向. 返回-1(凶)~+1(吉).

        基于河洛流年卦的卦名意象(易经卦辞吉凶), 与HeluoScorer的区别是
        只看卦名意象不看五行生克, 体现易经独立视角.
        """
        if not self.yi_available:
            return 0.0
        try:
            from tongshu.engines.heluo_yi_flow import get_liunian_gua
            from tongshu.engines.gua_jixiong import gua_name_direction
            gua = get_liunian_gua(birth_y, birth_m, birth_d, hour, gender, year)
            if gua is None:
                return 0.0
            return gua_name_direction(gua["hexagram"])
        except Exception:
            return 0.0

    def score_disaster_from_direction(self, direction: float) -> float:
        """从方向分转换为灾劫分: 卦象越凶灾劫越高."""
        if direction >= 0:
            return max(0.0, 0.2 - direction * 0.2)
        return min(2.0, 0.4 + abs(direction) * 1.6)

    def score_wealth_from_direction(self, direction: float) -> float:
        """从方向分转换为财运分: 卦象越吉财运越高."""
        if direction <= 0:
            return max(0.0, 0.2 + direction * 0.2)
        return min(2.5, 0.4 + direction * 2.1)


# === 体系 4: 盲派 ===

class BlindScorer:
    """盲派流年评分 (V4 新增).

    基于盲派应期引擎(BlindYingqiEngine)的冲穿合三刑墓库开闭分析,
    引动事件越多灾劫分越高, 应期事件越明确财运分越高.
    """

    def __init__(self):
        try:
            from tongshu.engines.blind_yingqi import BlindYingqiEngine
            self.engine = BlindYingqiEngine()
            self.available = True
        except Exception:
            self.available = False

    def score_disaster(self, birth_y: int, birth_m: int, birth_d: int,
                       hour: int, gender: str, year: int) -> float:
        """盲派灾劫评分: 引动事件(冲穿合三刑)越多灾劫越高."""
        if not self.available:
            return 0.0
        try:
            result = self.engine.analyze((birth_y, birth_m, birth_d, hour), gender, target_year=year)
            trigger_count = len(result.triggers)
            # 每个引动事件+0.5灾劫分, 上限2.0
            return min(2.0, trigger_count * 0.5)
        except Exception:
            return 0.0

    def score_wealth(self, birth_y: int, birth_m: int, birth_d: int,
                     hour: int, gender: str, year: int) -> float:
        """盲派财运评分: 应期事件(财星做功)越明确财运越高."""
        if not self.available:
            return 0.0
        try:
            result = self.engine.analyze((birth_y, birth_m, birth_d, hour), gender, target_year=year)
            yingqi_count = len(result.yingqi_events)
            # 每个应期事件+0.6财运分, 上限2.5
            return min(2.5, yingqi_count * 0.6)
        except Exception:
            return 0.0

    def score_year_direction(self, birth_y: int, birth_m: int, birth_d: int,
                             hour: int, gender: str, year: int) -> float:
        """盲派流年方向: 引动多为凶(-), 应期多为吉(+). 返回-1~+1."""
        if not self.available:
            return 0.0
        try:
            result = self.engine.analyze((birth_y, birth_m, birth_d, hour), gender, target_year=year)
            trigger_count = len(result.triggers)
            yingqi_count = len(result.yingqi_events)
            if trigger_count == 0 and yingqi_count == 0:
                return 0.0
            score = (yingqi_count - trigger_count) / max(trigger_count + yingqi_count, 1)
            return max(-1.0, min(1.0, score))
        except Exception:
            return 0.0


# === 体系 5: 紫微斗数 ===

class ZiweiScorer:
    """紫微斗数流年评分 (V4 新增).

    基于紫微大限四化(化禄/化权/化科/化忌)分析流年吉凶,
    化忌为凶, 化禄为吉. 需iztro(node.js)支持, 不可用时降级为0.
    """

    def __init__(self):
        try:
            from tongshu.engines.ziwei_engine import ZiweiEngine
            self.engine = ZiweiEngine()
            self.available = True
        except Exception:
            self.available = False

    def _get_sihua(self, birth_y: int, birth_m: int, birth_d: int,
                    hour: int, gender: str, year: int) -> dict:
        """获取流年四化分布. 返回{'禄':宫位列表, '权':..., '科':..., '忌':...}."""
        if not self.available:
            return {}
        try:
            from lunar_python import Solar as _Solar
            _lunar = _Solar.fromYmdHms(birth_y, birth_m, birth_d, hour, 0, 0).getLunar()
            chart = self.engine.compute(
                (_lunar.getYear(), _lunar.getMonth(), _lunar.getDay()),
                hour, gender=gender,
            )
            # 从palace_data中提取四化
            sihua = {"禄": [], "权": [], "科": [], "忌": []}
            for palace_name, palace_data in chart.palace_data.items():
                if isinstance(palace_data, dict):
                    stars = palace_data.get("stars", [])
                    for star in stars:
                        if isinstance(star, dict):
                            hua = star.get("hua", "")
                            if hua in sihua:
                                sihua[hua].append(palace_name)
            return sihua
        except Exception:
            return {}

    def score_disaster(self, birth_y: int, birth_m: int, birth_d: int,
                       hour: int, gender: str, year: int) -> float:
        """紫微灾劫评分: 化忌在命宫/财帛/官禄则灾劫高."""
        sihua = self._get_sihua(birth_y, birth_m, birth_d, hour, gender, year)
        if not sihua:
            return 0.0
        ji_palaces = sihua.get("忌", [])
        key_palaces = ["命宫", "财帛宫", "官禄宫", "迁移宫"]
        hit = sum(1 for p in ji_palaces if p in key_palaces)
        # 化忌在关键宫位+1.0灾劫分, 其他宫位+0.3
        return min(2.0, hit * 1.0 + max(0, len(ji_palaces) - hit) * 0.3)

    def score_wealth(self, birth_y: int, birth_m: int, birth_d: int,
                     hour: int, gender: str, year: int) -> float:
        """紫微财运评分: 化禄在财帛/福德则财运高."""
        sihua = self._get_sihua(birth_y, birth_m, birth_d, hour, gender, year)
        if not sihua:
            return 0.0
        lu_palaces = sihua.get("禄", [])
        wealth_palaces = ["财帛宫", "福德宫", "命宫"]
        hit = sum(1 for p in lu_palaces if p in wealth_palaces)
        return min(2.5, hit * 1.2 + max(0, len(lu_palaces) - hit) * 0.4)

    def score_year_direction(self, birth_y: int, birth_m: int, birth_d: int,
                             hour: int, gender: str, year: int) -> float:
        """紫微流年方向: 化禄多为吉(+), 化忌多为凶(-). 返回-1~+1."""
        sihua = self._get_sihua(birth_y, birth_m, birth_d, hour, gender, year)
        if not sihua:
            return 0.0
        lu_count = len(sihua.get("禄", []))
        ji_count = len(sihua.get("忌", []))
        total = lu_count + ji_count
        if total == 0:
            return 0.0
        return max(-1.0, min(1.0, (lu_count - ji_count) / total))


# === 交叉验证层 ===

class CrossValidationLayer:
    """五体系交叉验证层 (V4: 子平+盲派+紫微+河洛+易经)

    权重定位: 核心三体系(子平+盲派+紫微)占80%, 助力(河洛+易经)占20%.
    """

    # V4 权重: 子平40% + 盲派20% + 紫微20% + 河洛12% + 易经8%
    WEIGHTS = {
        "bazi": 0.40,
        "blind": 0.20,
        "ziwei": 0.20,
        "heluo": 0.12,
        "yi": 0.08,
    }

    def __init__(self):
        self.bazi = BaziScorer()
        self.blind = BlindScorer()
        self.ziwei = ZiweiScorer()
        self.heluo = HeluoScorer()
        self.yi = YiScorer()

    def combine_signals(self, bazi_disaster: float, blind_disaster: float,
                        ziwei_disaster: float, heluo_disaster: float,
                        yi_disaster: float, bazi_wealth: float,
                        blind_wealth: float, ziwei_wealth: float,
                        heluo_wealth: float, yi_wealth: float) -> tuple:
        """V4 综合评分: 五体系加权平均"""
        w = self.WEIGHTS
        disaster = (bazi_disaster * w["bazi"] + blind_disaster * w["blind"] +
                    ziwei_disaster * w["ziwei"] + heluo_disaster * w["heluo"] +
                    yi_disaster * w["yi"])
        wealth = (bazi_wealth * w["bazi"] + blind_wealth * w["blind"] +
                  ziwei_wealth * w["ziwei"] + heluo_wealth * w["heluo"] +
                  yi_wealth * w["yi"])
        return disaster, wealth

    def rank_years(self, predictions: list[AnnualPrediction]) -> list[int]:
        """按评分排序年份"""
        return sorted(predictions, key=lambda x: x.disaster_score, reverse=True)


# === 主评估器 ===

class AnnualEventEvaluator:
    """流年事件评估器"""

    def __init__(self):
        self.cv = CrossValidationLayer()
        self.arbiter = ConvergenceArbiter()

    def evaluate_with_signals(self, signals: list[CanonicalSignal], year_options: dict[int, str]) -> AnnualPrediction:
        """使用 signal 总线结果进行预测 (T3 新增)

        Args:
            signals: CanonicalSignal 列表，来自各体系
            year_options: {年份: 选项字母} 映射

        Returns:
            AnnualPrediction 预测结果
        """
        # 使用 ConvergenceArbiter 裁定
        result = self.arbiter.converge(signals)

        # 根据裁定结果选择年份
        if result.outcome == ConvergenceOutcome.ALIGNED and result.prediction:
            # 找到对应的年份
            for year, letter in year_options.items():
                if letter == result.prediction:
                    return AnnualPrediction(
                        year=year,
                        disaster_score=result.confidence,
                        wealth_score=result.confidence,
                        signals=[],
                        evidence_chain=[f"裁定: {result.outcome.value}"],
                    )

        # 回退到原有逻辑
        return self._fallback_evaluate(year_options)

    def _fallback_evaluate(self, year_options: dict[int, str]) -> AnnualPrediction:
        """回退到原有评分逻辑"""
        # 简化实现：返回第一个年份
        years = sorted(year_options.keys())
        if years:
            return AnnualPrediction(
                year=years[0],
                disaster_score=0.5,
                wealth_score=0.5,
            )
        return AnnualPrediction(year=0, disaster_score=0, wealth_score=0)

    def evaluate_case(self, case: dict, prediction_type: str = 'disaster') -> EventResult:
        """评估单个案例"""
        bi = case['birth_info']
        options = case['options']
        actual = case['answer']

        # 解析选项
        year_map = self._parse_options(options)
        if len(year_map) < 2:
            return EventResult(case['id'], '?', actual, False, 0, 0, [])

        # 计算命局
        h = bi.get('hour_start', 12)
        gender = 'female' if bi.get('gender') == '女' else 'male'

        try:
            dm, fourb, chart, verdict = self.cv.bazi.compute(
                bi['year'], bi['month'], bi['day'], h, gender
            )
        except Exception as e:
            return EventResult(case['id'], '?', actual, False, 0, 0, [f'计算错误: {e}'])

        # 对每个候选年份评分
        scores = {}
        evidence_list = []

        for year_str, letter in year_map.items():
            year = int(year_str)
            fs, fb = self.cv.bazi.ganzhi(year)

            # 子平评分 (V2.5: 传入旺衰verdict, 十神吉凶动态判断)
            bazi_d = self.cv.bazi.score_disaster(dm, fs, fb, fourb, verdict) if prediction_type == 'disaster' else self.cv.bazi.score_wealth(dm, fs, fb, fourb, verdict)
            bazi_w = self.cv.bazi.score_wealth(dm, fs, fb, fourb, verdict) if prediction_type == 'wealth' else self.cv.bazi.score_disaster(dm, fs, fb, fourb, verdict)

            # 河洛评分
            luoshu = (year - 4) % 60  # 简化
            heluo_d = self.cv.heluo.score_disaster(chart, luoshu, year)
            heluo_w = self.cv.heluo.score_wealth(chart, luoshu, year)

            # 易经评分
            yi_d = self.cv.yi.score_disaster(chart, year)
            yi_w = self.cv.yi.score_wealth(chart, year)

            # 盲派评分 (V4 新增)
            blind_d = self.cv.blind.score_disaster(bi['year'], bi['month'], bi['day'], h, gender, year)
            blind_w = self.cv.blind.score_wealth(bi['year'], bi['month'], bi['day'], h, gender, year)

            # 紫微评分 (V4 新增)
            ziwei_d = self.cv.ziwei.score_disaster(bi['year'], bi['month'], bi['day'], h, gender, year)
            ziwei_w = self.cv.ziwei.score_wealth(bi['year'], bi['month'], bi['day'], h, gender, year)

            # 交叉验证 (V4: 五体系加权)
            d_score, w_score = self.cv.combine_signals(
                bazi_d, blind_d, ziwei_d, heluo_d, yi_d,
                bazi_w, blind_w, ziwei_w, heluo_w, yi_w,
            )

            scores[letter] = d_score if prediction_type == 'disaster' else w_score
            evidence_list.append(
                f"{year}年: 子平{bazi_d:.1f} 盲派{blind_d:.1f} 紫微{ziwei_d:.1f} "
                f"河洛{heluo_d:.1f} 易经{yi_d:.1f}"
            )

        # 选分最高的年份
        if not scores:
            return EventResult(case['id'], '?', actual, False, 0, 0, evidence_list)

        predicted = max(scores, key=scores.get)
        correct = (predicted == actual)

        return EventResult(
            case_id=case['id'],
            predicted=predicted,
            actual=actual,
            correct=correct,
            disaster_score=scores.get(actual, 0),
            wealth_score=scores.get(actual, 0),
            evidence=evidence_list
        )

    def _parse_options(self, options: list) -> dict:
        """解析选项，提取年份-字母映射"""
        import re
        year_map = {}
        for o in options:
            mm = re.search(r'(19\d{2}|20\d{2})', o.get('text', ''))
            if mm:
                year_map[mm.group(1)] = o['letter']
        return year_map

    def run_evaluation(self, cases: list, prediction_type: str = 'disaster') -> dict:
        """运行完整评测"""
        results = []
        for case in cases:
            if case.get('category') in ('灾劫', '财运') or prediction_type == case.get('category'):
                result = self.evaluate_case(case, prediction_type)
                results.append(result)

        # 统计
        total = len(results)
        correct = sum(1 for r in results if r.correct)
        accuracy = correct / max(total, 1) * 100

        # 分主题统计
        by_cat = {}
        for r in results:
            cat = r.case_id.split('_')[1] if '_' in r.case_id else 'unknown'
            if cat not in by_cat:
                by_cat[cat] = {'total': 0, 'correct': 0}
            by_cat[cat]['total'] += 1
            if r.correct:
                by_cat[cat]['correct'] += 1

        return {
            'total': total,
            'correct': correct,
            'accuracy': accuracy,
            'by_category': by_cat,
            'results': results
        }


# === 入口 ===

def main():
    import json

    # 加载数据
    with open('.tmp_cases/fate_bench/data/hkjfma_qa.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    evaluator = AnnualEventEvaluator()

    # 灾劫主题
    print("=== 灾劫主题评估 ===")
    disaster_cases = [c for c in data if c.get('category') == '灾劫']
    disaster_result = evaluator.run_evaluation(disaster_cases, 'disaster')
    print(f"题数: {disaster_result['total']}, 命中: {disaster_result['correct']}, 命中率: {disaster_result['accuracy']:.1f}%")

    # 财运主题
    print("\n=== 财运主题评估 ===")
    wealth_cases = [c for c in data if c.get('category') == '财运']
    wealth_result = evaluator.run_evaluation(wealth_cases, 'wealth')
    print(f"题数: {wealth_result['total']}, 命中: {wealth_result['correct']}, 命中率: {wealth_result['accuracy']:.1f}%")

    # 显示详细结果
    print("\n=== 灾劫详细 ===")
    for r in disaster_result['results'][:5]:
        print(f"  {r.case_id}: 预测={r.predicted} 实际={r.actual} {'✓' if r.correct else '✗'}")

    print("\n=== 财运详细 ===")
    for r in wealth_result['results'][:5]:
        print(f"  {r.case_id}: 预测={r.predicted} 实际={r.actual} {'✓' if r.correct else '✗'}")


if __name__ == '__main__':
    main()
