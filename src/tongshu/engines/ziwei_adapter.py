"""紫微斗数适配器 — bySolar 模式

关键修改：使用 iztro 的 bySolar 函数（阳历输入），而非 byLunar。

依据：倪海厦《天纪》体系 + 官方数据集验证
- 数据集使用 bySolar(solarDate, hour, gender, isLeapMonth, locale)
- 我们的引擎必须对齐此行为
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from typing import Optional

from .ziwei_engine import ZiweiEngine, ZiweiChart


@dataclass(frozen=True)
class ZiweiCalculationPolicy:
    """紫微斗数计算政策 — P0-14 已冻结。"""
    date_source: str = "lunar"
    late_zi_handling: str = "same_day"
    ratified_policy_version: str = "P0-14-v1"

    @property
    def is_pending(self) -> bool:
        return False

    @property
    def is_ratified(self) -> bool:
        return True

    def to_dict(self) -> dict:
        return {
            "status": "RATIFIED",
            "date_source": self.date_source,
            "late_zi_handling": self.late_zi_handling,
            "ratified_policy_version": self.ratified_policy_version,
        }


@dataclass(frozen=True)
class SolarInput:
    """阳历输入"""
    year: int
    month: int
    day: int
    hour: int
    gender: str = "male"
    longitude: Optional[float] = None  # 经度（用于真太阳时校正）


def compute_via_solar(year: int, month: int, day: int, hour: int, 
                       gender: str = "male") -> dict:
    """使用 bySolar 计算命盘（与数据集一致）
    
    Args:
        year: 阳历年
        month: 阳历月
        day: 阳历日
        hour: 出生时辰（24小时制，0-23）
        gender: 性别
    
    Returns:
        dict: 包含命盘关键信息的字典
    """
    gender_js = "男" if gender == "male" else "女"
    
    script = f'''
    const {{ bySolar }} = require('iztro').astro;
    const a = bySolar('{year}-{month}-{day}', {hour}, '{gender_js}', true, 'zh-CN');
    console.log(JSON.stringify({{
        soul: a.earthlyBranchOfSoulPalace,
        body: a.earthlyBranchOfBodyPalace,
        wuxing: a.fiveElementsClass,
        palaces: a.palaces.map(p => ({{
            name: p.name,
            branch: p.earthlyBranch,
            major: (p.majorStars||[]).map(s=>s.name),
            minor: (p.minorStars||[]).map(s=>s.name),
            stem: p.heavenlyStem,
            decadalRange: p.decadal?.range || [],
            decadalStem: p.decadal?.heavenlyStem || '',
        }}))
    }}));
    '''
    
    proc = subprocess.run(
        ["node", "-e", script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
    )
    
    if proc.returncode != 0:
        raise RuntimeError(f"iztro bySolar failed: {proc.stderr}")
    
    return json.loads(proc.stdout)


def solar_to_chart(solar_input: SolarInput, raw_result: dict) -> ZiweiChart:
    """将 bySolar 结果转换为 ZiweiChart
    
    Args:
        solar_input: 阳历输入
        raw_result: bySolar 返回的原始结果
    
    Returns:
        ZiweiChart 实例
    """
    from .ziwei_engine import CHINESE_STAR_TO_KEY, SIHUA_NAMES
    
    # 地支映射
    BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
    # 五行局名称映射
    WUXING_NAMES = {
        '水二局': '水二局',
        '木三局': '木三局',
        '金四局': '金四局',
        '土五局': '土五局',
        '火六局': '火六局',
    }
    
    soul_branch = raw_result.get('soul', '')
    body_branch = raw_result.get('body', '')
    wuxing = raw_result.get('wuxing', '')
    
    # 构建宫位数据
    palace_data = {}
    for p in raw_result.get('palaces', []):
        name = p.get('name', '')
        branch = p.get('branch', '')
        major = p.get('major', [])
        minor = p.get('minor', [])
        
        # 转换为主星 pinyin key
        major_keys = [CHINESE_STAR_TO_KEY.get(s, s) for s in major if CHINESE_STAR_TO_KEY.get(s)]
        minor_keys = [CHINESE_STAR_TO_KEY.get(s, s) for s in minor if CHINESE_STAR_TO_KEY.get(s)]
        
        palace_data[name] = {
            'branch': branch,
            'major': major_keys,
            'minor': minor_keys,
            'decadal_range': p.get('decadalRange', []),
        }
    
    # 命宫主星
    soul_palace = palace_data.get('命宫', {})
    main_stars = soul_palace.get('major', [])
    main_star = main_stars[0] if main_stars else ''
    
    # 构建 ZiweiChart
    return ZiweiChart(
        soul_palace_main_star=main_star,
        soul_palace_main_stars=main_stars,
        soul_palace_sihua=[],
        palace_data={
            'five_elements_class': wuxing,
            'soul_earthly_branch': soul_branch,
            'body_earthly_branch': body_branch,
            'palaces': palace_data,
        },
        source='iztro-bySolar',
    )


class ZiweiSolarAdapter:
    """阳历输入的紫微斗数适配器

    使用 bySolar 函数，与倪海厦数据集保持一致。
    """

    def __init__(self, engine: Optional[ZiweiEngine] = None, policy: Optional[ZiweiCalculationPolicy] = None):
        self._engine = engine
        self.policy = policy if policy is not None else ZiweiCalculationPolicy()
    
    def compute(self, year: int, month: int, day: int, 
                hour: int, gender: str = "male") -> ZiweiChart:
        """计算命盘
        
        Args:
            year: 阳历年
            month: 阳历月
            day: 阳历日
            hour: 出生时辰（24小时制）
            gender: 性别 ("male"/"female")
        
        Returns:
            ZiweiChart 实例
        """
        raw = compute_via_solar(year, month, day, hour, gender)
        return solar_to_chart(SolarInput(year, month, day, hour, gender), raw)
    
    @property
    def engine(self):
        if self._engine is None:
            from .ziwei_engine import ZiweiEngine
            self._engine = ZiweiEngine()
        return self._engine


__all__ = [
    'SolarInput',
    'compute_via_solar',
    'solar_to_chart',
    'ZiweiSolarAdapter',
    'ZiweiCalculationPolicy',
]
