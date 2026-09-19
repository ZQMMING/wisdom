# -*- coding: utf-8 -*-
"""160-E 大运应期喜忌结构层 V1.0
基于原局用神/喜神/忌神与大运干支的关系, 输出结构判断(非吉凶裁决)。
边界: 只输出结构关系标签, 不输出吉凶/成败/贵贱; 喜忌前端拦截。
"""
from typing import Dict, List, Any

WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
SHENG = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
KE = {'木':'土','土':'水','水':'火','火':'金','金':'木'}
SHENG_ME = {v:k for k,v in SHENG.items()}
KE_ME = {v:k for k,v in KE.items()}

# 五合表 (天干 -> 合化五行)
WU_HE = {
    '甲': ('土', '己'), '己': ('土', '甲'),
    '乙': ('金', '庚'), '庚': ('金', '乙'),
    '丙': ('水', '辛'), '辛': ('水', '丙'),
    '丁': ('木', '壬'), '壬': ('木', '丁'),
    '戊': ('火', '癸'), '癸': ('火', '戊'),
}

# 三合表 (每个三合局: (地支1, 地支2, 地支3, 合化五行))
SAN_HE = [
    ('亥', '卯', '未', '木'),
    ('寅', '午', '戌', '火'),
    ('申', '子', '辰', '水'),
    ('巳', '酉', '丑', '金'),
]

# 十神映射 (日主五行 -> 十神)
def get_ten_god(dm_gan: str, gz: str) -> str:
    """根据日主天干和大运干支, 返回十神(中文)."""
    dmw = WX[dm_gan]
    gan = gz[0]
    gan_wx = WX[gan]
    dm_yang = dm_gan in '甲丙戊庚壬'
    gan_yang = gan in '甲丙戊庚壬'
    if gan_wx == dmw:
        return '比肩' if (dm_yang == gan_yang) else '劫财'
    elif SHENG.get(gan_wx) == dmw:
        return '正印' if (dm_yang != gan_yang) else '偏印'
    elif SHENG.get(dmw) == gan_wx:
        return '伤官' if (dm_yang != gan_yang) else '食神'
    elif KE.get(dmw) == gan_wx:
        return '正财' if (dm_yang != gan_yang) else '偏财'
    elif KE_ME.get(dmw) == gan_wx:
        return '正官' if (dm_yang != gan_yang) else '七杀'
    return '未知'


def build_dayun_xiji(
    pillars: Dict[str, list],
    yongshen_result: Dict[str, Any],
    dayun_list: List[str],
) -> Dict[str, Any]:
    """大运应期喜忌结构层.
    
    输入:
        pillars: 原局四柱
        yongshen_result: 用神引擎输出 (含primary/secondary/avoid)
        dayun_list: 大运列表 ['丙申','乙未',...]
    
    输出:
        per_step: 每个大运的喜忌结构
        boundary_note: 边界说明
    """
    dm = pillars['day'][0]
    dmw = WX[dm]
    
    primary = yongshen_result.get('yongshen_primary') or ''
    secondary = yongshen_result.get('yongshen_secondary') or []
    avoid = yongshen_result.get('yongshen_avoid') or []
    
    per_step = []
    for gz in dayun_list:
        gan = gz[0]
        zhi = gz[1]
        gan_wx = WX[gan]
        zhi_wx = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}.get(zhi, '')
        
        ten_god = get_ten_god(dm, gz)
        
        # 与用神/喜神/忌神的关系
        relations = []
        
        # 天干五行关系
        if gan_wx == primary:
            relations.append('GAN_PRIMARY')
        elif gan_wx in secondary:
            relations.append('GAN_SECONDARY')
        elif gan_wx in avoid:
            relations.append('GAN_AVOID')
        elif SHENG.get(gan_wx) == primary:
            relations.append('GAN_SHENG_PRIMARY')  # 大运生用神
        elif SHENG_ME.get(gan_wx) == primary:
            relations.append('GAN_PRIMARY_SHENG')  # 用神生大运(泄用神)
        elif KE.get(gan_wx) == primary:
            relations.append('GAN_KE_PRIMARY')  # 大运克用神
        
        # 地支五行关系
        if zhi_wx == primary:
            relations.append('ZHI_PRIMARY')
        elif zhi_wx in secondary:
            relations.append('ZHI_SECONDARY')
        elif zhi_wx in avoid:
            relations.append('ZHI_AVOID')
        
        # V1.1: 五合判断 (大运天干与原局天干五合)
        wuhe_info = WU_HE.get(gan, ('', ''))
        wuhe_huashen = wuhe_info[0]
        wuhe_target = wuhe_info[1]
        original_stems = [pillars[k][0] for k in ['year', 'month', 'day', 'hour']]
        if wuhe_target and wuhe_target in original_stems:
            relations.append(f'GAN_WUHE_{wuhe_target}')
            if wuhe_huashen == primary:
                relations.append('WUHE_PRIMARY')  # 合化用神, 喜
        
        # V1.2: 三合判断 (大运地支与原局两个地支形成三合局)
        original_branches = [pillars[k][1] for k in ['year', 'month', 'day', 'hour']]
        for sanhe in SAN_HE:
            b1, b2, b3, huashen = sanhe
            sanhe_branches = {b1, b2, b3}
            # 大运地支是否在三合局中
            if zhi in sanhe_branches:
                # 原局地支是否包含另外两个
                other_two = sanhe_branches - {zhi}
                if other_two.issubset(set(original_branches)):
                    relations.append(f'ZHI_SANHE_{b1}{b2}{b3}')
                    if huashen == primary:
                        relations.append('SANHE_PRIMARY')  # 三合化用神, 喜
        
        # 综合喜忌标签 (结构判断, 非吉凶)
        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif 'GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations:
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神
        elif 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            xiji_label = 'SUPPORT_XI_SHEN'  # 生扶喜神
        else:
            xiji_label = 'NEUTRAL'  # 中性
        
        per_step.append({
            'ganzhi': gz,
            'gan': gan,
            'zhi': zhi,
            'gan_wuxing': gan_wx,
            'zhi_wuxing': zhi_wx,
            'ten_god': ten_god,
            'relations': relations,
            'xiji_label': xiji_label,
        })
    
    return {
        'module': 'DAYUN_XIJI_V1.2',
        'namespace': 'dayun_xiji_structure',
        'day_master': dm,
        'daymaster_wuxing': dmw,
        'yongshen_primary': primary,
        'yongshen_secondary': secondary,
        'yongshen_avoid': avoid,
        'per_step': per_step,
        'judgment_status': 'DAYUN_XIJI_STRUCTURE_ONLY',
        'boundary_note': '大运喜忌结构层: 基于用神/喜神/忌神与大运干支的关系输出结构标签; 非吉凶裁决; 吉凶前端拦截; 冲合/调候/通关等深层作用待后续扩展',
    }
