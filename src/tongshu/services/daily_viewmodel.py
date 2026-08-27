# -*- coding: utf-8 -*-
"""
Phase 7-B: Daily Tongshu ViewModel

前端数据协议，用于今日通书展示。
"""
from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from datetime import date
from typing import Any, Dict, List, Optional


@dataclass
class HexagramData:
    """卦象数据。"""
    name: str           # 卦名，如"火山旅"
    upper: str          # 上卦，如"离"
    lower: str          # 下卦，如"艮"
    binary: str         # 二进制，如"101001"
    meaning: str        # 卦义简述


@dataclass
class StateData:
    """状态数据。"""
    title: str          # 状态标题，如"稳定期"
    description: str    # 状态描述
    energy_level: str   # 能量等级: high/middle/low


@dataclass
class GuidanceData:
    """指导数据。"""
    opportunity: str    # 宜
    attention: str      # 注意
    suggestion: str     # 建议


@dataclass
class ElementBalance:
    """五行平衡。"""
    gold: float         # 金
    wood: float         # 木
    water: float        # 水
    fire: float         # 火
    earth: float        # 土
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "金": self.gold,
            "木": self.wood,
            "水": self.water,
            "火": self.fire,
            "土": self.earth
        }


@dataclass
class DailyTongshuViewModel:
    """
    每日通书前端视图模型。
    
    接口: GET /api/v1/tongshu/daily
    """
    date: date
    solar_term: str                 # 节气，如"处暑"
    hexagram: HexagramData
    state: StateData
    guidance: GuidanceData
    element_balance: ElementBalance
    liu_nian: str                   # 流年
    liu_yue: str                    # 流月
    liu_ri: str                     # 流日
    source_reference: List[str]     # 来源引用
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，用于JSON序列化。"""
        result = {
            "date": str(self.date),
            "solar_term": self.solar_term,
            "hexagram": {
                "name": self.hexagram.name,
                "upper": self.hexagram.upper,
                "lower": self.hexagram.lower,
                "binary": self.hexagram.binary,
                "meaning": self.hexagram.meaning
            },
            "state": {
                "title": self.state.title,
                "description": self.state.description,
                "energy_level": self.state.energy_level
            },
            "guidance": {
                "opportunity": self.guidance.opportunity,
                "attention": self.guidance.attention,
                "suggestion": self.guidance.suggestion
            },
            "element_balance": self.element_balance.to_dict(),
            "liu_nian": self.liu_nian,
            "liu_yue": self.liu_yue,
            "liu_ri": self.liu_ri,
            "source_reference": self.source_reference
        }
        return result
    
    def to_json(self) -> str:
        """转换为JSON字符串。"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class DailyTongshuBuilder:
    """每日通书构建器。"""
    
    def __init__(self):
        self._date = date.today()
        self._solar_term = ""
        self._hexagram = HexagramData("", "", "", "", "")
        self._state = StateData("", "", "middle")
        self._guidance = GuidanceData("", "", "")
        self._element_balance = ElementBalance(0.2, 0.2, 0.2, 0.2, 0.2)
        self._liu_nian = ""
        self._liu_yue = ""
        self._liu_ri = ""
        self._sources = []
    
    def set_date(self, d: date) -> 'DailyTongshuBuilder':
        self._date = d
        return self
    
    def set_solar_term(self, term: str) -> 'DailyTongshuBuilder':
        self._solar_term = term
        return self
    
    def set_hexagram(self, name: str, upper: str, lower: str, 
                     binary: str, meaning: str) -> 'DailyTongshuBuilder':
        self._hexagram = HexagramData(name, upper, lower, binary, meaning)
        return self
    
    def set_state(self, title: str, description: str, 
                  energy: str = "middle") -> 'DailyTongshuBuilder':
        self._state = StateData(title, description, energy)
        return self
    
    def set_guidance(self, opportunity: str, attention: str, 
                     suggestion: str) -> 'DailyTongshuBuilder':
        self._guidance = GuidanceData(opportunity, attention, suggestion)
        return self
    
    def set_element_balance(self, gold: float, wood: float, 
                            water: float, fire: float, earth: float) -> 'DailyTongshuBuilder':
        self._element_balance = ElementBalance(gold, wood, water, fire, earth)
        return self
    
    def set_time_sequence(self, liu_nian: str, liu_yue: str, liu_ri: str) -> 'DailyTongshuBuilder':
        self._liu_nian = liu_nian
        self._liu_yue = liu_yue
        self._liu_ri = liu_ri
        return self
    
    def add_source(self, source: str) -> 'DailyTongshuBuilder':
        self._sources.append(source)
        return self
    
    def build(self) -> DailyTongshuViewModel:
        return DailyTongshuViewModel(
            date=self._date,
            solar_term=self._solar_term,
            hexagram=self._hexagram,
            state=self._state,
            guidance=self._guidance,
            element_balance=self._element_balance,
            liu_nian=self._liu_nian,
            liu_yue=self._liu_yue,
            liu_ri=self._liu_ri,
            source_reference=self._sources
        )


def create_sample_tongshu() -> DailyTongshuViewModel:
    """创建示例通书数据。"""
    builder = DailyTongshuBuilder()
    
    return (builder
        .set_date(date(2026, 8, 21))
        .set_solar_term("处暑")
        .set_hexagram(
            name="火山旅",
            upper="离",
            lower="艮",
            binary="101001",
            meaning="旅行在外，稳重前行"
        )
        .set_state(
            title="稳定期",
            description="当前处于平稳发展阶段",
            energy="middle"
        )
        .set_guidance(
            opportunity="规划、学习、沟通",
            attention="保持节奏，注意倾听",
            suggestion="稳扎稳打，不宜冒进"
        )
        .set_element_balance(0.2, 0.35, 0.15, 0.2, 0.1)
        .set_time_sequence("甲辰", "壬申", "丙午")
        .add_source("《河图》")
        .add_source("《洛书》")
        .add_source("《易经》")
        .build()
    )