"""
规则引擎 — 神煞 DSL 解释器 + 宜忌聚合 + 高风险过滤
基于《协纪辨方书》公有领域规则自研
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .constants import (
    TIAN_GAN, DI_ZHI, GAN_WUXING, ZHI_WUXING,
    JIANCHU_NAMES, XIUSU_NAMES, PENG_TABOO, NAYIN_TABLE,
    JIEQI_LONGITUDES, JIE_NAMES, ZHONG_QI_NAMES,
)
from .types import GanZhi, DayInfo


# ============================================================
# 风险过滤（德国合规）
# ============================================================

HIGH_RISK_KEYWORDS_DE = [
    "vorhersagen", "prophezeien", "garantieren", "versprechen",
    "reichtum", "glück", "vermögen",
    "heiratsempfehlung", "investitionsempfehlung", "medizinische Beratung",
]

HIGH_RISK_PATTERNS_ZH = [
    "发财", "横财", "破财", "血光", "灾祸", "疾病",
    "投资建议", "医疗建议", "婚姻判断",
]

DISCLAIMER_DE = "Der Inhalt dient nur der Unterhaltung und kulturellen Reflexion."
DISCLAIMER_ZH = "本内容仅供娱乐和文化参考。"


# ============================================================
# 规则 DSL
# ============================================================

@dataclass
class ShenShaRule:
    """单条神煞规则"""
    name: str                       # 神煞名
    when_field: str                 # 匹配字段（如 "jianchu", "day_branch", "day_gan"）
    when_value: str                 # 匹配值
    yi: list[str] = field(default_factory=list)     # 宜事
    ji: list[str] = field(default_factory=list)     # 忌事
    level: int = 3                  # 等第（1-5，1最高）
    source: str = ""                # 来源


# DSL 规则表（YAML 风格，直接 Python dict）
SHENSHA_RULES = [
    # === 建除十二神 ===
    {"name": "建日", "field": "jianchu", "value": "建",
     "yi": ["祭祀", "祈福", "出行", "上任"], "ji": ["动土", "开仓"], "level": 1},
    {"name": "除日", "field": "jianchu", "value": "除",
     "yi": ["治病", "除灾", "扫舍"], "ji": ["求官", "上任"], "level": 2},
    {"name": "满日", "field": "jianchu", "value": "满",
     "yi": ["祭祀", "祈福", "开市", "嫁娶"], "ji": ["动土", "安葬"], "level": 2},
    {"name": "平日", "field": "jianchu", "value": "平",
     "yi": ["平治道涂", "修墙"], "ji": ["开市", "开仓"], "level": 3},
    {"name": "定日", "field": "jianchu", "value": "定",
     "yi": ["订婚", "签约", "交易"], "ji": ["出行", "诉讼"], "level": 2},
    {"name": "执日", "field": "jianchu", "value": "执",
     "yi": ["捕获", "诉讼"], "ji": ["嫁娶", "出行", "开市"], "level": 3},
    {"name": "破日", "field": "jianchu", "value": "破",
     "yi": ["破屋", "坏垣"], "ji": ["嫁娶", "出行", "交易"], "level": 1},
    {"name": "危日", "field": "jianchu", "value": "危",
     "yi": ["安床", "伐木"], "ji": ["出行", "开市"], "level": 3},
    {"name": "成日", "field": "jianchu", "value": "成",
     "yi": ["订婚", "嫁娶", "开市", "签约", "上任"], "ji": ["诉讼", "出行"], "level": 1},
    {"name": "收日", "field": "jianchu", "value": "收",
     "yi": ["纳财", "收货", "入仓"], "ji": ["出行", "嫁娶", "开市"], "level": 2},
    {"name": "开日", "field": "jianchu", "value": "开",
     "yi": ["开市", "开张", "出行", "嫁娶"], "ji": ["安葬", "诉讼"], "level": 1},
    {"name": "闭日", "field": "jianchu", "value": "闭",
     "yi": ["祭祀", "安葬", "封仓"], "ji": ["开市", "出行", "嫁娶"], "level": 2},

    # === 彭祖百忌（自动生成，不在此重复）===

    # === 时辰吉凶 ===
    {"name": "吉时", "field": "hour_lucky", "value": "true",
     "yi": ["重要决策", "签约", "出行"], "ji": [], "level": 3},
    {"name": "凶时", "field": "hour_lucky", "value": "false",
     "yi": [], "ji": ["重要决策", "签约", "出行"], "level": 3},

    # === 冲煞 ===
    {"name": "冲煞", "field": "zodiac_clash", "value": "all",
     "yi": [], "ji": ["当日重大决策"], "level": 3},
]


# ============================================================
# 规则引擎
# ============================================================

class RuleEngine:
    """规则引擎 — 匹配 → 聚合 → 过滤"""

    def __init__(self):
        self.rules = SHENSHA_RULES

    def match(self, day_info: DayInfo) -> list[dict]:
        """匹配所有命中规则"""
        matched = []
        for rule in self.rules:
            if self._match_rule(rule, day_info):
                matched.append(rule)
        return matched

    def _match_rule(self, rule: dict, info: DayInfo) -> bool:
        field = rule["field"]
        value = rule["value"]

        if field == "jianchu":
            return info.jianchu == value
        elif field == "day_gan":
            return info.day_ganzhi.stem == value
        elif field == "day_branch":
            return info.day_ganzhi.branch == value
        elif field == "zodiac_clash":
            return info.zodiac_clash != ""
        elif field == "hour_lucky":
            # 只要有吉时/凶时就算匹配
            lucky_hours = [h for h in info.hour_lucky if h["lucky"] == (value == "true")]
            return len(lucky_hours) > 0
        return False

    def aggregate(self, matched_rules: list[dict]) -> dict:
        """聚合宜忌，按等级排序去重"""
        yi_set = {}
        ji_set = {}

        for rule in matched_rules:
            for item in rule.get("yi", []):
                if item not in yi_set or rule["level"] < yi_set[item]:
                    yi_set[item] = rule["level"]
            for item in rule.get("ji", []):
                if item not in ji_set or rule["level"] < ji_set[item]:
                    ji_set[item] = rule["level"]

        # 冲突处理：同一事项既宜又忌 → 按等级高者优先；同级 → 忌优先
        for item in list(yi_set):
            if item in ji_set:
                if yi_set[item] <= ji_set[item]:
                    del ji_set[item]
                else:
                    del yi_set[item]

        # 按等级排序
        yi_sorted = sorted(yi_set.items(), key=lambda x: x[1])
        ji_sorted = sorted(ji_set.items(), key=lambda x: x[1])

        return {
            "yi": [item for item, _ in yi_sorted],
            "ji": [item for item, _ in ji_sorted],
        }

    def filter_high_risk(self, text: str) -> str:
        """过滤高风险表达"""
        for kw in HIGH_RISK_PATTERNS_ZH:
            text = text.replace(kw, "***")
        return text

    def process(self, day_info: DayInfo) -> dict:
        """完整规则处理流程"""
        matched = self.match(day_info)
        result = self.aggregate(matched)
        result["disclaimer"] = DISCLAIMER_DE
        return result


# 单例
engine = RuleEngine()


def get_daily_advice(day_info: DayInfo) -> dict:
    """
    获取每日宜忌建议
    """
    result = engine.process(day_info)

    # 加入彭祖百忌
    peng_taboo = day_info.peng_taboo
    if peng_taboo:
        result["peng_taboo"] = peng_taboo

    return result


if __name__ == "__main__":
    from .almanac import get_day_info
    from datetime import date

    info = get_day_info(date(2026, 8, 13))
    advice = get_daily_advice(info)
    print(f"宜: {advice['yi']}")
    print(f"忌: {advice['ji']}")
    print(f"彭祖: {advice.get('peng_taboo', [])}")