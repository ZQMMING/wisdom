"""ZIPING V3.1 喜用神裁定 (YongShen).

基于§28辨层结果，确定性判定喜用神.
铁律: LLM不得修改此模块的计算逻辑.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# ═══════════════════════════════════════════════════════════════
# 数据结构
# ═══════════════════════════════════════════════════════════════
@dataclass
class YongShenVerdict:
    """喜用神裁定结果."""
    # 核心裁定
    primary_yong: str = "UNKNOWN"     # 用神类型: WATER/METAL/EARTH/FIRE/WOOD
    primary_help: str = "UNKNOWN"     # 喜神辅助: WATER/METAL/EARTH/FIRE/WOOD
    Ji_shen: str = "UNKNOWN"          # 忌神: WATER/METAL/EARTH/FIRE/WOOD

    # 判定依据 (可追溯)
    basis: str = ""                   # 判定路径: "QTPJ-PROSPERITY" / "DT-BINGYAO" / ...
    evidence_refs: List[str] = field(default_factory=list)

    # 命局特征
    pattern_type: str = "NORMAL"      # NORMAL / YANSHANG / CONG ...
    body_state: str = "UNKNOWN"       # STRONG / WEAK / WANG_OVER / WANG_BUT_NOT_STRONG / BALANCED
    climate_state: str = "UNKNOWN"    # HOT / COLD / HOT_WET / DRY ...
    disease_state: str = "UNKNOWN"    # defined / absent
    tangguan_state: str = "UNKNOWN"   # TONGGUAN_ABSENT / OPPOSITION_RESOLVED / ...

    # 原文引用
    classic_quote: str = ""           # 穷通宝鉴/滴天髓原文
    source: str = ""                  # 经典名+篇名


# ═══════════════════════════════════════════════════════════════
# 五行映射
# ═══════════════════════════════════════════════════════════════
_WUXING_NAMES = {
    "WATER": "水", "METAL": "金", "EARTH": "土",
    "FIRE": "火", "WOOD": "木",
}

# 十神五行映射 (日主为基准)
TEN_GOD_TO_5X = {
    "食神": "OUTPUT", "伤官": "OUTPUT",   # 泄日主
    "偏财": "WEALTH", "正财": "WEALTH",   # 被日主克
    "七杀": "OFFICER", "正官": "OFFICER", # 克日主
    "偏印": "RESOURCE", "正印": "RESOURCE", # 生日主
    "比肩": "COMpanion", "劫财": "COMpanion",  # 同日主
}

# ═══════════════════════════════════════════════════════════════
# 喜用神裁定引擎
# ═══════════════════════════════════════════════════════════════
class YongShenEngine:
    """喜用神裁定引擎 — 纯确定性布尔规则."""

    # 调候表: 月令 → 首选调候用神
    # 来源: 穷通宝鉴·各月用神 (通用版本)
    # 注意: 实际需按日主分别查表, 此处返回元数据供运行时映射
    TIAOHOU_TABLE = {
        "ZI":   {"WATER": {"yong": "WATER",  "help": "METAL",  "ji": "FIRE",
               "quote": "冬月水旺, 专用比劫", "source": "穷通宝鉴·冬月"},
                 "METAL": {"yong": "WATER",  "help": "METAL",  "ji": "WOOD",
               "quote": "十一月庚金, 专用丁火, 次取甲木", "source": "穷通宝鉴·冬月"},
                 "FIRE": {"yong": "WATER",  "help": "METAL",  "ji": "EARTH",
               "quote": "十月丙火, 阳刃当权, 专用壬水", "source": "穷通宝鉴·冬月"},
                 "EARTH": {"yong": "FIRE",  "help": "WOOD",   "ji": "WATER",
               "quote": "十二月己土, 寒气司权, 专用丙火", "source": "穷通宝鉴·腊月"},
                 "WOOD": {"yong": "FIRE",  "help": "EARTH",  "ji": "WATER",
               "quote": "十一月甲木, 水冷金寒, 专用庚丁", "source": "穷通宝鉴·冬月"},},
        "CHOU": {"WATER": {"yong": "WATER",  "help": "METAL",  "ji": "FIRE",
               "quote": "丑月水旺, 比劫帮身", "source": "穷通宝鉴·腊月"},
                 "METAL": {"yong": "FIRE",   "help": "WOOD",   "ji": "EARTH",
               "quote": "十二月辛金, 寒气凝滞, 专用丙火", "source": "穷通宝鉴·腊月"},
                 "FIRE": {"yong": "WATER",  "help": "METAL",  "ji": "EARTH",
               "quote": "十二月丙火, 寒气司权, 专用壬水", "source": "穷通宝鉴·腊月"},
                 "EARTH": {"yong": "FIRE",  "help": "WOOD",   "ji": "WATER",
               "quote": "十二月己土, 冻土不能生物, 专用丙火", "source": "穷通宝鉴·腊月"},
                 "WOOD": {"yong": "FIRE",  "help": "WOOD",   "ji": "METAL",
               "quote": "十二月甲木, 寒冷调候, 专用丙丁", "source": "穷通宝鉴·腊月"},},
        "YIN":  {"WATER": {"yong": "FIRE",   "help": "WOOD",   "ji": "EARTH",
               "quote": "正月壬水, 阳气上升, 专用丙丁", "source": "穷通宝鉴·春月"},
                 "METAL": {"yong": "FIRE",   "help": "WOOD",   "ji": "WATER",
               "quote": "正月庚金, 金寒水冷, 专用丁火", "source": "穷通宝鉴·春月"},
                 "FIRE": {"yong": "WATER",  "help": "METAL",  "ji": "WOOD",
               "quote": "正月丙火, 阳刃当权, 专取壬水", "source": "穷通宝鉴·春月"},
                 "EARTH": {"yong": "FIRE",   "help": "WOOD",   "ji": "WATER",
               "quote": "正月戊土, 寒气未除, 专用丙火", "source": "穷通宝鉴·春月"},
                 "WOOD": {"yong": "FIRE",   "help": "EARTH",  "ji": "METAL",
               "quote": "正月甲木, 孟春木旺, 专用庚金", "source": "穷通宝鉴·春月"},},
        "MAO":  {"WATER": {"yong": "FIRE",   "help": "WOOD",   "ji": "EARTH",
               "quote": "二月壬水, 旺极泛滥, 专用戊土", "source": "穷通宝鉴·春月"},
                 "METAL": {"yong": "WATER",  "help": "METAL",  "ji": "FIRE",
               "quote": "二月辛金, 金气休囚, 专用壬水", "source": "穷通宝鉴·春月"},
                 "FIRE": {"yong": "WATER",  "help": "METAL",  "ji": "WOOD",
               "quote": "二月丙火, 木火当权, 专用壬水", "source": "穷通宝鉴·春月"},
                 "EARTH": {"yong": "WATER",  "help": "METAL",  "ji": "WOOD",
               "quote": "二月己土, 湿土无气, 专用丙火", "source": "穷通宝鉴·春月"},
                 "WOOD": {"yong": "METAL",  "help": "WATER",  "ji": "FIRE",
               "quote": "二月乙木, 仲春木旺, 专用辛金", "source": "穷通宝鉴·春月"},},
        "CHEN": {"WATER": {"yong": "FIRE",   "help": "WOOD",   "ji": "EARTH",
               "quote": "三月壬水, 水库当权, 专用丙丁", "source": "穷通宝鉴·春月"},
                 "METAL": {"yong": "FIRE",   "help": "WOOD",   "ji": "EARTH",
               "quote": "三月庚金, 气渐退散, 专用丁火", "source": "穷通宝鉴·春月"},
                 "FIRE": {"yong": "WATER",  "help": "METAL",  "ji": "WOOD",
               "quote": "三月丙火, 阳气渐退, 专用壬水", "source": "穷通宝鉴·春月"},
                 "EARTH": {"yong": "WATER",  "help": "METAL",  "ji": "WOOD",
               "quote": "三月戊土, 杂气当权, 专用乙木", "source": "穷通宝鉴·春月"},
                 "WOOD": {"yong": "FIRE",   "help": "EARTH",  "ji": "METAL",
               "quote": "三月甲木, 退气无力, 专用丙火", "source": "穷通宝鉴·春月"},},
        "SI":   {"WATER": {"yong": "METAL",  "help": "WATER",  "ji": "FIRE",
               "quote": "四月壬水, 绝地逢生, 专用庚金", "source": "穷通宝鉴·夏月"},
                 "METAL": {"yong": "WATER",  "help": "METAL",  "ji": "FIRE",
               "quote": "四月辛金, 长生之地, 专用壬水", "source": "穷通宝鉴·夏月"},
                 "FIRE": {"yong": "WATER",  "help": "METAL",  "ji": "WOOD",
               "quote": "四月丙火, 特尊壬水, 辅以庚金", "source": "穷通宝鉴·夏月"},
                 "EARTH": {"yong": "WATER",  "help": "METAL",  "ji": "FIRE",
               "quote": "四月戊土, 火土焦燥, 专用壬水", "source": "穷通宝鉴·夏月"},
                 "WOOD": {"yong": "WATER",  "help": "METAL",  "ji": "FIRE",
               "quote": "四月乙木, 木火通明, 专用壬水", "source": "穷通宝鉴·夏月"},},
        "WU":   {"WATER": {"yong": "METAL",  "help": "WATER",  "ji": "FIRE",
               "quote": "五月壬水, 绝处逢生, 专用庚金", "source": "穷通宝鉴·五月"},
                 "METAL": {"yong": "WATER",  "help": "METAL",  "ji": "FIRE",
               "quote": "五月辛金, 旺极须水, 专用壬水", "source": "穷通宝鉴·五月"},
                 "FIRE": {"yong": "WATER",  "help": "METAL",  "ji": "WOOD",
               "quote": "五月丙火, 愈炎得壬庚高透方为上命", "source": "穷通宝鉴·五月"},
                 "EARTH": {"yong": "WATER",  "help": "METAL",  "ji": "FIRE",
               "quote": "五月戊土, 火旺土焦, 专用壬水", "source": "穷通宝鉴·五月"},
                 "WOOD": {"yong": "METAL",  "help": "WATER",  "ji": "FIRE",
               "quote": "五月甲木, 休囚无力, 专用癸水", "source": "穷通宝鉴·五月"},},
        "WEI":  {"WATER": {"yong": "METAL",  "help": "WATER",  "ji": "FIRE",
               "quote": "六月壬水, 进气生发, 专用庚金", "source": "穷通宝鉴·夏月"},
                 "METAL": {"yong": "FIRE",   "help": "WOOD",   "ji": "WATER",
               "quote": "六月辛金, 火旺金熔, 专用壬水", "source": "穷通宝鉴·夏月"},
                 "FIRE": {"yong": "WATER",  "help": "METAL",  "ji": "FIRE",
               "quote": "六月丙火, 湿土当权, 取壬庚为用", "source": "穷通宝鉴·夏月"},
                 "EARTH": {"yong": "WATER",  "help": "METAL",  "ji": "FIRE",
               "quote": "六月己土, 燥土无气, 专用壬水", "source": "穷通宝鉴·夏月"},
                 "WOOD": {"yong": "WATER",  "help": "METAL",  "ji": "FIRE",
               "quote": "六月乙木, 退气无力, 专用癸水", "source": "穷通宝鉴·夏月"},},
        "SHEN": {"WATER": {"yong": "FIRE",   "help": "WOOD",   "ji": "METAL",
               "quote": "七月壬水, 死气将绝, 专用丁火", "source": "穷通宝鉴·秋月"},
                 "METAL": {"yong": "FIRE",   "help": "WOOD",   "ji": "WATER",
               "quote": "七月庚金, 当令旺相, 专用丁火", "source": "穷通宝鉴·秋月"},
                 "FIRE": {"yong": "WATER",  "help": "METAL",  "ji": "METAL",
               "quote": "七月丙火, 休囚无力, 专用壬水", "source": "穷通宝鉴·秋月"},
                 "EARTH": {"yong": "WATER",  "help": "METAL",  "ji": "FIRE",
               "quote": "七月戊土, 金气旺盛, 专用甲木", "source": "穷通宝鉴·秋月"},
                 "WOOD": {"yong": "WATER",  "help": "METAL",  "ji": "FIRE",
               "quote": "七月甲木, 绝处逢生, 专用壬水", "source": "穷通宝鉴·秋月"},},
        "YOU":  {"WATER": {"yong": "METAL",  "help": "WATER",  "ji": "FIRE",
               "quote": "八月壬水, 进气旺相, 专用庚金", "source": "穷通宝鉴·秋月"},
                 "METAL": {"yong": "FIRE",   "help": "WOOD",   "ji": "EARTH",
               "quote": "八月辛金, 当令旺极, 专用壬水", "source": "穷通宝鉴·秋月"},
                 "FIRE": {"yong": "METAL",  "help": "WATER",  "ji": "FIRE",
               "quote": "八月丙火, 休囚休死, 专用金水", "source": "穷通宝鉴·秋月"},
                 "EARTH": {"yong": "FIRE",   "help": "WOOD",   "ji": "WATER",
               "quote": "八月戊土, 气渐退散, 专用丙火", "source": "穷通宝鉴·秋月"},
                 "WOOD": {"yong": "WATER",  "help": "METAL",  "ji": "FIRE",
               "quote": "八月乙木, 退气无力, 专用壬水", "source": "穷通宝鉴·秋月"},},
        "XU":   {"WATER": {"yong": "METAL",  "help": "WATER",  "ji": "FIRE",
               "quote": "九月壬水, 进气生发, 专用庚金", "source": "穷通宝鉴·秋月"},
                 "METAL": {"yong": "FIRE",   "help": "WOOD",   "ji": "EARTH",
               "quote": "九月辛金, 进气旺相, 专用壬水", "source": "穷通宝鉴·秋月"},
                 "FIRE": {"yong": "WATER",  "help": "METAL",  "ji": "WOOD",
               "quote": "九月丙火, 阳气退散, 专用壬水", "source": "穷通宝鉴·秋月"},
                 "EARTH": {"yong": "FIRE",   "help": "WOOD",   "ji": "WATER",
               "quote": "九月戊土, 燥土无气, 专用甲木", "source": "穷通宝鉴·秋月"},
                 "WOOD": {"yong": "WATER",  "help": "METAL",  "ji": "FIRE",
               "quote": "九月甲木, 退气无力, 专用癸水", "source": "穷通宝鉴·秋月"},},
        "HAI":  {"WATER": {"yong": "FIRE",   "help": "EARTH",  "ji": "WATER",
               "quote": "十月壬水, 临官旺相, 专用丙火", "source": "穷通宝鉴·冬月"},
                 "METAL": {"yong": "FIRE",   "help": "WOOD",   "ji": "WATER",
               "quote": "十月庚金, 进气旺相, 专用丁火", "source": "穷通宝鉴·冬月"},
                 "FIRE": {"yong": "WATER",  "help": "METAL",  "ji": "EARTH",
               "quote": "十月丙火, 阳刃当权, 专用壬水", "source": "穷通宝鉴·冬月"},
                 "EARTH": {"yong": "FIRE",   "help": "WOOD",   "ji": "WATER",
               "quote": "十月戊土, 寒气将至, 专用丙火", "source": "穷通宝鉴·冬月"},
                 "WOOD": {"yong": "FIRE",   "help": "EARTH",  "ji": "WATER",
               "quote": "十月甲木, 长生之地, 专用庚丁", "source": "穷通宝鉴·冬月"},},
    }

    # 身强弱 → 喜用规则
    STRENGTH_RULES = {
        "STRONG": {
            "yong": "WATER", "help": "METAL", "ji": "FIRE",
            "basis": "DT-STRENGTH-SHENG",
            "evidence": ["E-DT-STRENGTH-001", "E-QTBJ-YONG-001"],
            "quote": "火旺宜水润之，则万物发生", "source": "滴天髓·原注"},
        "WANG_OVER": {
            "yong": "WATER", "help": "METAL", "ji": "FIRE",
            "basis": "DT-STRENGTH-WANG",
            "evidence": ["E-DT-STRENGTH-011"],
            "quote": "旺极者抑之则折，惟用火土顺其势", "source": "滴天髓·旺极"},
        "WANG_BUT_NOT_STRONG": {
            "yong": "WATER", "help": "METAL", "ji": "FIRE",
            "basis": "DT-STRENGTH-WANG-NO-STRONG",
            "evidence": ["E-DT-STRENGTH-013"],
            "quote": "身旺无倚，虽聪颖而孤贫", "source": "滴天髓"},
        "BALANCED": {
            "yong": "WATER", "help": "METAL", "ji": "FIRE",
            "basis": "DT-STRENGTH-BALANCED",
            "evidence": ["E-DT-STRENGTH-014"],
            "quote": "命贵中和，偏枯终于有损", "source": "滴天髓"},
        "WEAK": {
            "yong": "FIRE", "help": "WOOD", "ji": "WATER",
            "basis": "ZQ-STRENGTH-WEAK",
            "evidence": ["E-ZQ-GEJU-001"],
            "quote": "身弱用印比帮身", "source": "子平真诠·身弱"},
        "WEAK_OVER": {
            "yong": "FIRE", "help": "WOOD", "ji": "METAL",
            "basis": "ZQ-STRENGTH-WEAK-OVER",
            "evidence": ["E-ZQ-GEJU-002"],
            "quote": "弱极从势，不可逆也", "source": "子平真诠·从格"},
    }

    # 气候 → 调候优先级
    CLIMATE_PRIORITY = {
        "HOT": {"priority": "WATER", "reason": "炎夏急需调候润局"},
        "COLD": {"priority": "FIRE", "reason": "寒冬急需调候暖局"},
        "HOT_WET": {"priority": "METAL", "reason": "湿热需金泄秀"},
        "DRY": {"priority": "WATER", "reason": "燥土需水润局"},
    }

    def __init__(self):
        pass

    def verdict(
        self,
        judgments: List[Dict[str, Any]],
        chart_info: Dict[str, Any],
    ) -> YongShenVerdict:
        """根据辨层结果裁定喜用神."""
        verdict = YongShenVerdict()

        # 1. 提取辨层状态 (兼容 dataclass 和 dict)
        states = {}
        for j in judgments:
            if isinstance(j, dict):
                dom = j.get("domain", "")
                st = j.get("state", "")
            else:
                dom = getattr(j, "domain", "")
                st = getattr(j, "state", "")
            if dom and st and st != "UNDETERMINED":
                states[dom] = st

        verdict.body_state = states.get("STRENGTH", "UNKNOWN")
        verdict.climate_state = states.get("CLIMATE", "UNKNOWN")
        verdict.tangguan_state = states.get("TONGGUAN", "UNKNOWN")
        verdict.disease_state = states.get("DISEASE", "UNKNOWN")

        # 2. 格局判定
        pattern = states.get("PATTERN", "UNKNOWN")
        special = states.get("SPECIAL", "UNKNOWN")
        if special in ("YANSHANG", "CONG_WANG", "CONG_WEAK"):
            verdict.pattern_type = special
        elif pattern in ("SUCCESS", "FAIL"):
            verdict.pattern_type = f"PATTERN_{pattern}"
        else:
            verdict.pattern_type = "NORMAL"

        # 3. 炎上格特殊处理
        if verdict.pattern_type == "YANSHANG":
            return self._yan_shang_verdict(verdict, states, chart_info)

        # 4. 调候优先 (穷通宝鉴)
        tiaohou = self._tiaohou_verdict(states, chart_info)
        if tiaohou:
            verdict.primary_yong = tiaohou["yong"]
            verdict.primary_help = tiaohou["help"]
            verdict.Ji_shen = tiaohou["ji"]
            verdict.basis = "QTPJ-TIAOHOU"
            verdict.classic_quote = tiaohou["quote"]
            verdict.source = tiaohou["source"]
            verdict.evidence_refs = tiaohou.get("evidence", [])
            return verdict

        # 5. 身强弱通用规则
        strength_rule = self.STRENGTH_RULES.get(verdict.body_state)
        if strength_rule:
            verdict.primary_yong = strength_rule["yong"]
            verdict.primary_help = strength_rule["help"]
            verdict.Ji_shen = strength_rule["ji"]
            verdict.basis = strength_rule["basis"]
            verdict.classic_quote = strength_rule["quote"]
            verdict.source = strength_rule["source"]
            verdict.evidence_refs = strength_rule["evidence"]
            return verdict

        # 6. fail-closed: 默认
        verdict.basis = "FAIL_CLOSED"
        verdict.classic_quote = "辨层不足, 喜用待察"
        verdict.source = "引擎"
        return verdict

    def _yan_shang_verdict(
        self, verdict: YongShenVerdict, states: Dict[str, str], chart_info: Dict[str, Any]
    ) -> YongShenVerdict:
        """炎上格特殊裁定."""
        verdict.Ji_shen = "WATER"
        verdict.primary_yong = "FIRE"
        verdict.primary_help = "EARTH"
        verdict.basis = "QTPJ-YANSHANG"
        verdict.classic_quote = "炎上格，不喜水破格"
        verdict.source = "穷通宝鉴·炎上格"
        verdict.evidence_refs = ["E-QTBJ-YANSHANG-001"]
        return verdict

    def _tiaohou_verdict(
        self, states: Dict[str, str], chart_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """调候裁定 (穷通宝鉴体例)."""
        month_branch = chart_info.get("month_branch", "")
        body_state = states.get("STRENGTH", "UNKNOWN")
        day_master = chart_info.get("day_master", "").upper()

        # 1. 先查调候表 (按日主)
        if month_branch in self.TIAOHOU_TABLE:
            dm_table = self.TIAOHOU_TABLE[month_branch]
            # 日主映射: REN→WATER, GENG→METAL, BING→FIRE, JI→EARTH, JIA→WOOD
            DM_MAP = {"REN": "WATER", "GUI": "WATER",
                      "GENG": "METAL", "XIN": "METAL",
                      "BING": "FIRE", "DING": "FIRE",
                      "WU": "EARTH", "JI": "EARTH",
                      "JIA": "WOOD", "YI": "WOOD"}
            dm_key = DM_MAP.get(day_master, day_master)
            if dm_key in dm_table:
                th = dm_table[dm_key]
                # 2. 但需校验: 用神是否有根 (否则无用)
                has_root = chart_info.get("has_root_for_yong", False)
                if has_root:
                    return th
                else:
                    # 用神无根 → 降级为辅助
                    return {
                        "yong": th["help"],
                        "help": th["yong"],
                        "ji": th["ji"],
                        "quote": th["quote"] + " (用神无根, 降格)",
                        "source": th["source"],
                        "evidence": th.get("evidence", []),
                        "note": "用神无根, 调候降格为辅助",
                    }

        # 3. Fallback: 身强弱规则
        if body_state in self.STRENGTH_RULES:
            return self.STRENGTH_RULES[body_state]
        return None

    @staticmethod
    def to_dict(verdict: YongShenVerdict) -> Dict[str, Any]:
        """序列化为dict."""
        return {
            "primary_yong": _WUXING_NAMES.get(verdict.primary_yong, verdict.primary_yong),
            "primary_help": _WUXING_NAMES.get(verdict.primary_help, verdict.primary_help),
            "ji_shen": _WUXING_NAMES.get(verdict.Ji_shen, verdict.Ji_shen),
            "basis": verdict.basis,
            "evidence_refs": verdict.evidence_refs,
            "pattern_type": verdict.pattern_type,
            "body_state": verdict.body_state,
            "climate_state": verdict.climate_state,
            "classic_quote": verdict.classic_quote,
            "source": verdict.source,
        }


# ═══════════════════════════════════════════════════════════════
# 流年吉凶判定
# ═══════════════════════════════════════════════════════════════
@dataclass
class LiuNianVerdict:
    """流年吉凶判定结果."""
    year: str = ""               # 干支, 如 "丙午"
    year_gan: str = ""           # 天干, 如 "丙"
    year_zhi: str = ""           # 地支, 如 "午"
    gan_ten_god: str = "UNKNOWN" # 天干十神
    zhi_ten_god: str = "UNKNOWN" # 地支十神

    # 吉凶判定
    ji_xiong: str = "UNKNOWN"   # JI / XIONG / JI_XIONG_MIXED / UNCLEAR
    reason: str = ""            # 判定理由

    # 与命局关系
    relations: List[Dict[str, str]] = field(default_factory=list)
    # [{"type": "冲/合/刑/害/伏吟", "target": "时支巳", "effect": "冲根"}]

    # 用神状态
    yong_shen_effect: str = "UNKNOWN"  # HELP / HARM / NEUTRAL / ATTACKED
    yong_shen_detail: str = ""         # 如 "壬水被丙火争合"

    # 原文支撑
    classic_quote: str = ""
    source: str = ""


class LiuNianEngine:
    """流年吉凶判定引擎 — 纯确定性规则."""

    # 天干十神 (基于丙火日主) — 使用拼音格式与BaziEngine一致
    DAY_MASTER = "BING"
    STEM_TEN_GOD = {
        "GENG": "偏财", "XIN": "正财",
        "REN": "七杀", "GUI": "正官",
        "JIA": "偏印", "YI": "正印",
        "BING": "比肩", "DING": "劫财",
        "WU": "食神", "JI": "伤官",
    }
    STEM_WUXING = {
        "JIA": "WOOD", "YI": "WOOD",
        "BING": "FIRE", "DING": "FIRE",
        "WU": "EARTH", "JI": "EARTH",
        "GENG": "METAL", "XIN": "METAL",
        "REN": "WATER", "GUI": "WATER",
    }
    STEM_HE = {
        "JIA": "JI", "JI": "JIA",
        "BING": "XIN", "XIN": "BING",
        "WU": "GUI", "GUI": "WU",
        "DING": "REN", "REN": "DING",
        "GENG": "YI", "YI": "GENG",
    }

    # 地支藏干主气 (拼音格式)
    BRANCH_MAIN_HIDDEN = {
        "ZI": "GUI", "CHOU": "JI", "YIN": "JIA", "MAO": "YI",
        "CHEN": "WU", "SI": "BING", "WU": "DING", "WEI": "JI",
        "SHEN": "GENG", "YOU": "XIN", "XU": "WU", "HAI": "REN",
    }
    BRANCH_WUXING = {
        "ZI": "WATER", "CHOU": "EARTH", "YIN": "WOOD", "MAO": "WOOD",
        "CHEN": "EARTH", "SI": "FIRE", "WU": "FIRE", "WEI": "EARTH",
        "SHEN": "METAL", "YOU": "METAL", "XU": "EARTH", "HAI": "WATER",
    }
    # 六冲
    BRANCH_CHONG = {
        "ZI": "WU", "WU": "ZI", "CHOU": "WEI", "WEI": "CHOU",
        "YIN": "SHEN", "SHEN": "YIN", "MAO": "YOU", "YOU": "MAO",
        "CHEN": "XU", "XU": "CHEN", "SI": "HAI", "HAI": "SI",
    }
    # 六合
    BRANCH_HE = {
        "ZI": "CHOU", "CHOU": "ZI", "YIN": "HEI", "HEI": "YIN",
        "MAO": "XU", "XU": "MAO", "CHEN": "YOU", "YOU": "CHEN",
        "SI": "SHEN", "SHEN": "SI", "WU": "WEI", "WEI": "WU",
    }
    # 三刑
    BRANCH_CHEN = {
        "ZI": "MAO", "MAO": "ZI", "CHEN": "CHEN",
        "YIN": "SI", "SI": "SHEN", "SHEN": "YIN",
        "CHOU": "WEI", "WEI": "CHOU",
    }

    def __init__(self):
        pass

    def verdict(
        self,
        liunian_gz: str,      # 流年干支拼音, 如 "BING wu" (空格分隔)
        chart_info: Dict[str, Any],
        yongshen: YongShenVerdict,
    ) -> LiuNianVerdict:
        """判定流年吉凶."""
        parts = liunian_gz.strip().split()
        if len(parts) == 2:
            gan, zhi = parts[0].upper(), parts[1].upper()
        else:
            # 兼容连写格式
            s = liunian_gz.upper()
            gan, zhi = s[:2], s[2:]
        lv = LiuNianVerdict(year=liunian_gz, year_gan=gan, year_zhi=zhi)

        lv.gan_ten_god = self.STEM_TEN_GOD.get(lv.year_gan, "UNKNOWN")
        lv.zhi_ten_god = self.STEM_TEN_GOD.get(
            self.BRANCH_MAIN_HIDDEN.get(lv.year_zhi, ""), "UNKNOWN"
        )

        # 提取命局信息
        four_stems = chart_info.get("four_stems", [])
        four_branches = chart_info.get("four_branches", [])
        day_master = chart_info.get("day_master", "")

        # 1. 检查冲合关系
        relations = self._check_relations(lv, four_branches, four_stems)
        lv.relations = relations

        # 2. 判定用神状态
        yong_effect = self._judge_yong_shen_effect(
            lv, yongshen, relations, chart_info
        )
        lv.yong_shen_effect = yong_effect["effect"]
        lv.yong_shen_detail = yong_effect["detail"]

        # 3. 综合吉凶
        lv.ji_xiong, lv.reason = self._synthesize_ji_xiong(lv, yong_effect)

        # 4. 原文支撑
        lv.classic_quote, lv.source = self._find_classic_support(lv, yongshen)

        return lv

    def _check_relations(
        self, lv: LiuNianVerdict, four_branches: List[str], four_stems: List[str]
    ) -> List[Dict[str, str]]:
        """检查流年与命局的干支关系."""
        relations = []

        # 地支关系
        for i, bz in enumerate(four_branches):
            if bz == lv.year_zhi:
                relations.append({
                    "type": "伏吟",
                    "target": f"第{i+1}柱地支{bz}",
                    "effect": "伏吟加重",
                })
            elif self.BRANCH_CHONG.get(bz) == lv.year_zhi:
                relations.append({
                    "type": "冲",
                    "target": f"第{i+1}柱地支{bz}",
                    "effect": f"流年{lv.year_zhi}冲命局{bz}",
                })
            elif self.BRANCH_HE.get(bz) == lv.year_zhi:
                relations.append({
                    "type": "合",
                    "target": f"第{i+1}柱地支{bz}",
                    "effect": f"流年{lv.year_zhi}合命局{bz}",
                })
            elif self.BRANCH_CHEN.get(bz) == lv.year_zhi:
                relations.append({
                    "type": "刑",
                    "target": f"第{i+1}柱地支{bz}",
                    "effect": f"流年{lv.year_zhi}刑命局{bz}",
                })

        # 天干关系
        for i, bs in enumerate(four_stems):
            if bs == lv.year_gan:
                relations.append({
                    "type": "伏吟",
                    "target": f"第{i+1}柱天干{bs}",
                    "effect": "伏吟加重",
                })
            elif self.STEM_HE.get(bs) == lv.year_gan:
                relations.append({
                    "type": "合",
                    "target": f"第{i+1}柱天干{bs}",
                    "effect": f"流年{lv.year_gan}合命局{bs}",
                })

        return relations

    def _judge_yong_shen_effect(
        self,
        lv: LiuNianVerdict,
        yongshen: YongShenVerdict,
        relations: List[Dict[str, str]],
        chart_info: Dict[str, Any],
    ) -> Dict[str, str]:
        """判定流年对喜用神的影响."""
        effect = "NEUTRAL"
        detail = ""

        yong_5x = yongshen.primary_yong  # WATER/METAL/etc
        ji_5x = yongshen.Ji_shen

        # 流年天干五行
        gan_5x = self._stem_to_wuxing(lv.year_gan)

        if gan_5x == yong_5x:
            effect = "HELP"
            detail = f"流年天干{lv.year_gan}为{yongshen.primary_yong}，助用神"
        elif gan_5x == ji_5x:
            effect = "HARM"
            detail = f"流年天干{lv.year_gan}为{yongshen.Ji_shen}，助忌神"
        elif gan_5x == yongshen.primary_help:
            effect = "HELP"
            detail = f"流年天干{lv.year_gan}为喜神{yongshen.primary_help}，辅助用神"

        # 检查合化影响
        for rel in relations:
            if rel["type"] == "合":
                # 丁壬合化木 → 如果是合走了用神 → 凶
                if lv.year_gan in ("DING", "REN") and yong_5x == "WATER":
                    effect = "ATTACKED"
                    detail += "; 丁壬合化木，用神被合"
                elif lv.year_gan in ("BING", "XIN") and yong_5x == "METAL":
                    effect = "ATTACKED"
                    detail += "; 丙辛合化水，用神被合"

        # 检查冲的影响 (冲根 → 凶)
        for rel in relations:
            if rel["type"] == "冲":
                if "时支" in rel["target"] or "第4柱" in rel["target"]:
                    effect = "ATTACKED"
                    detail += f"; {rel['effect']}，根基受损"
                elif "月支" in rel["target"] or "第2柱" in rel["target"]:
                    effect = "HARM"
                    detail += f"; {rel['effect']}，提纲受损"

        # 伏吟 → 加重
        for rel in relations:
            if rel["type"] == "伏吟":
                if effect == "HELP":
                    effect = "HELP"  # 喜神伏吟 → 更喜
                elif effect == "HARM":
                    effect = "HARM"  # 忌神伏吟 → 更凶
                detail += f"; {rel['effect']}"

        return {"effect": effect, "detail": detail}

    def _synthesize_ji_xiong(
        self, lv: LiuNianVerdict, yong_effect: Dict[str, str]
    ) -> tuple:
        """综合判定吉凶.

        规则:
        1. 天干五行决定基础吉凶 (HELP/HARM/NEUTRAL)
        2. 地支冲合修饰吉凶程度 (ATTACKED = 严重削弱)
        3. 优先级: 天干 > 地支
        """
        effect = yong_effect["effect"]
        detail = yong_effect["detail"]

        # 基础吉凶 (天干)
        if effect == "HELP":
            ji_xiong = "XIONG"
            reason = f"吉: {detail}"
        elif effect == "HARM":
            ji_xiong = "JI"
            reason = f"凶: {detail}"
        elif effect == "ATTACKED":
            # 地支冲克严重，用神受损
            ji_xiong = "JI"
            reason = f"大凶: 用神根基被冲克，{detail}"
        elif effect == "NEUTRAL":
            ji_xiong = "UNCLEAR"
            reason = f"中性: {detail}"
        else:
            ji_xiong = "UNCLEAR"
            reason = detail

        return ji_xiong, reason

    def _find_classic_support(
        self, lv: LiuNianVerdict, yongshen: YongShenVerdict
    ) -> tuple:
        """查找五经原文支撑."""
        # 简化版: 基于类型返回
        if lv.ji_xiong == "JI":
            return "一交亥运，壬水得禄，癸水临旺，火气克尽，家破身亡", "滴天髓阐微"
        elif lv.ji_xiong == "XIONG":
            return "食神生旺胜财官", "滴天髓阐微"
        return "", ""

    @staticmethod
    def _stem_to_wuxing(stem: str) -> str:
        """天干 → 五行."""
        return {
            "JIA": "WOOD", "YI": "WOOD",
            "BING": "FIRE", "DING": "FIRE",
            "WU": "EARTH", "JI": "EARTH",
            "GENG": "METAL", "XIN": "METAL",
            "REN": "WATER", "GUI": "WATER",
        }.get(stem.upper(), "UNKNOWN")

    @staticmethod
    def to_dict(lv: LiuNianVerdict) -> Dict[str, Any]:
        """序列化为dict."""
        return {
            "year": lv.year,
            "gan_ten_god": lv.gan_ten_god,
            "zhi_ten_god": lv.zhi_ten_god,
            "ji_xiong": lv.ji_xiong,
            "reason": lv.reason,
            "relations": lv.relations,
            "yong_shen_effect": lv.yong_shen_effect,
            "yong_shen_detail": lv.yong_shen_detail,
            "classic_quote": lv.classic_quote,
            "source": lv.source,
        }
