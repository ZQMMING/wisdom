"""紫微斗数流派方法配置

提供四种流派的 MethodProfile，用于切换不同的计算规则。
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

# 四化表版本
SihuaVersion = Literal["classic", "zhongzhou", "ming"]

# 空宫处理策略
EmptyPalacePolicy = Literal["none", "partial", "full"]

# 小限使用模式
XiaoxianMode = Literal[True, False, "partial"]


@dataclass(frozen=True)
class MethodProfile:
    """紫微斗数流派方法配置"""
    
    # 流派标识
    school: str
    name: str
    
    # 四化表版本
    sihua_version: SihuaVersion
    
    # 运限体系
    use_xiaoxian: XiaoxianMode
    use_stream_flowers: bool
    has_liuchangliuqu: bool
    
    # 宫位处理
    empty_palace_policy: EmptyPalacePolicy
    
    # 自化系统
    enable_self_hua: bool
    enable_liji_gong: bool
    
    # 飞化优先级
    gonggan_feihua_priority: bool
    
    # 证据来源
    source: str = ""
    
    def __post_init__(self):
        """验证配置合理性"""
        if self.school not in ("sanhe", "zhongzhou", "feixing", "qintian"):
            raise ValueError(f"Unknown school: {self.school}")


# ============================================================================
# 各流派配置
# ============================================================================

# 三合派（南派）
# 依据：《紫微斗数全书》《捷览》《全集》
SANHE_PROFILE = MethodProfile(
    school="sanhe",
    name="三合派",
    sihua_version="classic",
    use_xiaoxian=True,
    use_stream_flowers=True,
    has_liuchangliuqu=False,
    empty_palace_policy="partial",
    enable_self_hua=False,
    enable_liji_gong=False,
    gonggan_feihua_priority=False,
    source="《紫微斗数全书》《全集》",
)

# 中州派
# 依据：王亭之《谈斗数》《紫微斗数讲义》《紫微星诀》
ZHONGZHOU_PROFILE = MethodProfile(
    school="zhongzhou",
    name="中州派",
    sihua_version="zhongzhou",
    use_xiaoxian=True,
    use_stream_flowers=True,
    has_liuchangliuqu=True,   # 独有流昌流曲
    empty_palace_policy="full",  # 空宫全借对宫
    enable_self_hua=False,
    enable_liji_gong=False,
    gonggan_feihua_priority=False,
    source="王亭之《谈斗数》《讲义》",
)

# 飞星派（梁若瑜系）
# 依据：梁若瑜《专论四化》《十八飞星秘仪》
FEIXING_PROFILE = MethodProfile(
    school="feixing",
    name="飞星派",
    sihua_version="classic",
    use_xiaoxian=False,        # 不用小限
    use_stream_flowers=False,  # 不用流曜
    has_liuchangliuqu=False,
    empty_palace_policy="partial",
    enable_self_hua=True,
    enable_liji_gong=False,
    gonggan_feihua_priority=True,  # 宫干飞化优先
    source="梁若瑜《专论四化》",
)

# 钦天门（北派）
# 依据：蔡明宏《华山钦天四化紫微斗数飞星秘仪》
QINTIAN_PROFILE = MethodProfile(
    school="qintian",
    name="钦天门",
    sihua_version="classic",
    use_xiaoxian="partial",
    use_stream_flowers=True,
    has_liuchangliuqu=False,
    empty_palace_policy="partial",
    enable_self_hua=True,      # 核心：向心/离心自化
    enable_liji_gong=True,     # 核心：立极宫系统
    gonggan_feihua_priority=True,
    source="蔡明宏《华山钦天四化秘仪》",
)

# ============================================================================
# 四化表
# ============================================================================

# 明代原版（《全书》）- 庚、壬干天府化科
MING_SIHUA = {
    "甲": {"禄": "廉贞", "权": "破军", "科": "武曲", "忌": "太阳"},
    "乙": {"禄": "天机", "权": "天梁", "科": "紫微", "忌": "太阴"},
    "丙": {"禄": "天同", "权": "天机", "科": "文昌", "忌": "廉贞"},
    "丁": {"禄": "太阴", "权": "天同", "科": "天机", "忌": "巨门"},
    "戊": {"禄": "贪狼", "权": "太阴", "科": "右弼", "忌": "天机"},
    "己": {"禄": "武曲", "权": "贪狼", "科": "天梁", "忌": "文曲"},
    "庚": {"禄": "太阳", "权": "武曲", "科": "天府", "忌": "天同"},  # 天府化科
    "辛": {"禄": "巨门", "权": "太阳", "科": "文曲", "忌": "文昌"},
    "壬": {"禄": "天梁", "权": "紫微", "科": "天府", "忌": "武曲"},  # 天府化科
    "癸": {"禄": "破军", "权": "巨门", "科": "太阴", "忌": "贪狼"},
}

# 通行版（《全集》）- 庚、壬干太阴/左辅化科
CLASSIC_SIHUA = {
    "甲": {"禄": "廉贞", "权": "破军", "科": "武曲", "忌": "太阳"},
    "乙": {"禄": "天机", "权": "天梁", "科": "紫微", "忌": "太阴"},
    "丙": {"禄": "天同", "权": "天机", "科": "文昌", "忌": "廉贞"},
    "丁": {"禄": "太阴", "权": "天同", "科": "天机", "忌": "巨门"},
    "戊": {"禄": "贪狼", "权": "太阴", "科": "右弼", "忌": "天机"},
    "己": {"禄": "武曲", "权": "贪狼", "科": "天梁", "忌": "文曲"},
    "庚": {"禄": "太阳", "权": "武曲", "科": "太阴", "忌": "天同"},  # 太阴化科
    "辛": {"禄": "巨门", "权": "太阳", "科": "文曲", "忌": "文昌"},
    "壬": {"禄": "天梁", "权": "紫微", "科": "左辅", "忌": "武曲"},  # 左辅化科
    "癸": {"禄": "破军", "权": "巨门", "科": "太阴", "忌": "贪狼"},
}

# 中州派 - 戊干太阳化科
ZHONGZHOU_SIHUA = {
    "甲": {"禄": "廉贞", "权": "破军", "科": "武曲", "忌": "太阳"},
    "乙": {"禄": "天机", "权": "天梁", "科": "紫微", "忌": "太阴"},
    "丙": {"禄": "天同", "权": "天机", "科": "文昌", "忌": "廉贞"},
    "丁": {"禄": "太阴", "权": "天同", "科": "天机", "忌": "巨门"},
    "戊": {"禄": "贪狼", "权": "太阴", "科": "太阳", "忌": "天机"},  # 太阳化科
    "己": {"禄": "武曲", "权": "贪狼", "科": "天梁", "忌": "文曲"},
    "庚": {"禄": "太阳", "权": "武曲", "科": "天府", "忌": "天同"},
    "辛": {"禄": "巨门", "权": "太阳", "科": "文曲", "忌": "文昌"},
    "壬": {"禄": "天梁", "权": "紫微", "科": "天府", "忌": "武曲"},
    "癸": {"禄": "破军", "权": "巨门", "科": "太阴", "忌": "贪狼"},
}

# ============================================================================
# 四化表映射
# ============================================================================

SIHUA_TABLES = {
    "ming": MING_SIHUA,
    "classic": CLASSIC_SIHUA,
    "zhongzhou": ZHONGZHOU_SIHUA,
}

# ============================================================================
# 配置加载
# ============================================================================

SCHOOL_PROFILES = {
    "sanhe": SANHE_PROFILE,
    "zhongzhou": ZHONGZHOU_PROFILE,
    "feixing": FEIXING_PROFILE,
    "qintian": QINTIAN_PROFILE,
}


def load_profile(school: str) -> MethodProfile:
    """加载指定流派的 MethodProfile
    
    Args:
        school: 流派标识 (sanhe/zhongzhou/feixing/qintian)
        
    Returns:
        MethodProfile 实例
        
    Raises:
        ValueError: 未知流派
    """
    if school not in SCHOOL_PROFILES:
        raise ValueError(
            f"Unknown school '{school}'. "
            f"Available: {list(SCHOOL_PROFILES.keys())}"
        )
    return SCHOOL_PROFILES[school]


def get_sihua_table(profile: MethodProfile) -> dict:
    """根据 MethodProfile 获取对应的四化表
    
    Args:
        profile: MethodProfile 实例
        
    Returns:
        十干四化表字典
    """
    version = profile.sihua_version
    if version not in SIHUA_TABLES:
        raise ValueError(f"Unknown sihua version: {version}")
    return SIHUA_TABLES[version]


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "MethodProfile",
    "SihuaVersion",
    "EmptyPalacePolicy",
    "XiaoxianMode",
    "SANHE_PROFILE",
    "ZHONGZHOU_PROFILE",
    "FEIXING_PROFILE",
    "QINTIAN_PROFILE",
    "MING_SIHUA",
    "CLASSIC_SIHUA",
    "ZHONGZHOU_SIHUA",
    "SIHUA_TABLES",
    "SCHOOL_PROFILES",
    "load_profile",
    "get_sihua_table",
]
