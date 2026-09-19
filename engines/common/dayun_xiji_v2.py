# -*- coding: utf-8 -*-
"""160-E 大运应期喜忌结构层 V2.0
基于原局用神/喜神/忌神与大运干支的关系, 输出结构判断(非吉凶裁决)。
V2.0: 增加六冲/六合判断, 综合天干地支作用。
边界: 只输出结构关系标签, 不输出吉凶/成败/贵贱; 喜忌前端拦截。
"""
from typing import Dict, List, Any

WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
SHENG = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
KE = {'木':'土','土':'水','水':'火','火':'金','金':'木'}
SHENG_ME = {v:k for k,v in SHENG.items()}
KE_ME = {v:k for k,v in KE.items()}

# 六冲表
LIU_CHONG = {
    '子':'午', '午':'子',
    '丑':'未', '未':'丑',
    '寅':'申', '申':'寅',
    '卯':'酉', '酉':'卯',
    '辰':'戌', '戌':'辰',
    '巳':'亥', '亥':'巳',
}

# 六合表 (地支 -> (合化五行, 合化地支对))
LIU_HE = {
    '子': ('土', '丑'), '丑': ('土', '子'),
    '寅': ('木', '亥'), '亥': ('木', '寅'),
    '卯': ('火', '戌'), '戌': ('火', '卯'),
    '辰': ('金', '酉'), '酉': ('金', '辰'),
    '巳': ('水', '申'), '申': ('水', '巳'),
    '午': ('土', '未'), '未': ('土', '午'),
}

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


def _get_branch_hidden_wuxing(branch: str, hidden_stems: Dict) -> List[str]:
    """获取地支藏干的五行列表."""
    stems = hidden_stems.get(branch, [])
    return [WX.get(s, '') for s in stems if s in WX]


def build_dayun_xiji(
    pillars: Dict[str, list],
    yongshen_result: Dict[str, Any],
    dayun_list: List[str],
    facts: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """大运应期喜忌结构层 V2.0.
    
    输入:
        pillars: 原局四柱
        yongshen_result: 用神引擎输出 (含primary/secondary/avoid)
        dayun_list: 大运列表 ['丙申','乙未',...]
        facts: L0 facts (含hidden_stems/combination_facts), 可选
    
    输出:
        per_step: 每个大运的喜忌结构
        boundary_note: 边界说明
    """
    dm = pillars['day'][0]
    dmw = WX[dm]
    
    primary = yongshen_result.get('yongshen_primary') or ''
    secondary = yongshen_result.get('yongshen_secondary') or []
    avoid = yongshen_result.get('yongshen_avoid') or []
    
    # 原局地支列表和藏干
    original_branches = [pillars[k][1] for k in ['year', 'month', 'day', 'hour']]
    hidden_stems = {}
    if facts and 'hidden_stems' in facts:
        for k in ['year', 'month', 'day', 'hour']:
            branch = pillars[k][1]
            hidden_stems[branch] = facts['hidden_stems'].get(k, [])
    
    per_step = []
    for gz in dayun_list:
        gan = gz[0]
        zhi = gz[1]
        gan_wx = WX[gan]
        zhi_wx = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}.get(zhi, '')
        
        ten_god = get_ten_god(dm, gz)
        
        # 与用神/喜神/忌神的关系
        relations = []
        chong_xiji = 0  # 六冲喜忌分数: 正=喜, 负=忌
        he_xiji = 0     # 六合喜忌分数
        
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
        
        # V2.0: 六冲判断
        chong_target = LIU_CHONG.get(zhi, '')
        if chong_target and chong_target in original_branches:
            relations.append(f'ZHI_CHONG_{chong_target}')
            # 被冲地支的藏干五行
            chong_hidden = _get_branch_hidden_wuxing(chong_target, hidden_stems)
            if primary in chong_hidden:
                chong_xiji -= 1  # 冲用神根, 忌(权重减半)
                relations.append('CHONG_PRIMARY_ROOT')
            if avoid and avoid[0] in chong_hidden:
                chong_xiji += 0.5  # 冲忌神根, 喜(权重减半)
                relations.append('CHONG_AVOID_ROOT')
        
        # V2.0: 六合判断
        he_info = LIU_HE.get(zhi, ('', ''))
        he_huashen = he_info[0]
        he_target = he_info[1]
        if he_target and he_target in original_branches:
            relations.append(f'ZHI_HE_{he_target}')
            if he_huashen == primary:
                he_xiji += 1  # 合化用神, 喜(权重减半)
                relations.append('HE_PRIMARY')
            if avoid and he_huashen == avoid[0]:
                he_xiji -= 0.5  # 合化忌神, 忌(权重减半)
                relations.append('HE_AVOID')
        
        # 综合喜忌标签 (结构判断, 非吉凶)
        # V2.0: 综合五行生克 + 六冲 + 六合
        xi_score = 0
        ji_score = 0
        
        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations:
            xi_score += 2
        if 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            xi_score += 1
        if 'GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations:
            ji_score += 2
        
        xi_score += max(0, chong_xiji) + max(0, he_xiji)
        ji_score += max(0, -chong_xiji) + max(0, -he_xiji)
        
        if xi_score > ji_score:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif ji_score > xi_score:
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
            'xi_score': xi_score,
            'ji_score': ji_score,
        })
    
    return {
        'module': 'DAYUN_XIJI_V2',
        'namespace': 'dayun_xiji_structure',
        'day_master': dm,
        'daymaster_wuxing': dmw,
        'yongshen_primary': primary,
        'yongshen_secondary': secondary,
        'yongshen_avoid': avoid,
        'per_step': per_step,
        'judgment_status': 'DAYUN_XIJI_STRUCTURE_ONLY',
        'boundary_note': '大运喜忌结构层V2: 基于用神/喜神/忌神与大运干支的五行生克+六冲+六合关系输出结构标签; 非吉凶裁决; 吉凶前端拦截',
    }
