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

# 三会表 (每个三会局: (地支1, 地支2, 地支3, 合化五行))
SAN_HUI = [
    ('寅', '卯', '辰', '木'),
    ('巳', '午', '未', '火'),
    ('申', '酉', '戌', '金'),
    ('亥', '子', '丑', '水'),
]

# 半合表 (每个半合局: (地支1, 地支2, 合化五行))
BAN_HE = [
    ('申', '子', '水'), ('子', '辰', '水'),
    ('寅', '午', '火'), ('午', '戌', '火'),
    ('亥', '卯', '木'), ('卯', '未', '木'),
    ('巳', '酉', '金'), ('酉', '丑', '金'),
]

# 六害表
LIU_HAI = {
    '子': '未', '未': '子',
    '丑': '午', '午': '丑',
    '寅': '巳', '巳': '寅',
    '卯': '辰', '辰': '卯',
    '申': '亥', '亥': '申',
    '酉': '戌', '戌': '酉',
}

# 三刑表 (地支 -> 刑的地支列表)
SAN_XING = {
    '寅': ['巳', '申'], '巳': ['寅', '申'], '申': ['寅', '巳'],
    '丑': ['戌', '未'], '戌': ['丑', '未'], '未': ['丑', '戌'],
    '子': ['卯'], '卯': ['子'],
    '辰': ['午', '酉', '亥'], '午': ['辰', '酉', '亥'],
    '酉': ['辰', '午', '亥'], '亥': ['辰', '午', '酉'],
}

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

# 地支藏干表 (地支 -> 藏干列表, 按本气/中气/余气顺序)
HIDDEN_STEMS = {
    '子': ['癸'],
    '丑': ['己', '癸', '辛'],
    '寅': ['甲', '丙', '戊'],
    '卯': ['乙'],
    '辰': ['戊', '乙', '癸'],
    '巳': ['丙', '庚', '戊'],
    '午': ['丁', '己'],
    '未': ['己', '丁', '乙'],
    '申': ['庚', '壬', '戊'],
    '酉': ['辛'],
    '戌': ['戊', '辛', '丁'],
    '亥': ['壬', '甲'],
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


def build_dayun_xiji(
    pillars: Dict[str, list],
    yongshen_result: Dict[str, Any],
    dayun_list: List[str],
    wpo: Dict[str, Any] = None,
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
    
    # V3.3: 计算用神的十神类型(通过日主天干和用神五行)
    primary_ten_god_type = ''
    if primary and dm:
        dmw = WX.get(dm, '')
        primary_wx = primary
        dm_yang = dm in '甲丙戊庚壬'
        if primary_wx == dmw:
            primary_ten_god_type = '比劫'
        elif SHENG.get(primary_wx) == dmw:
            primary_ten_god_type = '印'
        elif SHENG.get(dmw) == primary_wx:
            primary_ten_god_type = '食伤'
        elif KE.get(dmw) == primary_wx:
            primary_ten_god_type = '财'
        elif KE_ME.get(dmw) == primary_wx:
            primary_ten_god_type = '官杀'
    
    # V2.7: 计算用神在原局中的力量占比 # PCT-MARK: 用神力量占比, 用于判断用神强弱
    primary_power_ratio = 0.0
    # V2.9: 计算原局缺少的五行(力量为0或极低)
    missing_wuxing = []
    # V3.0: 计算原局五行平衡度(标准差) # PCT-MARK: 五行力量占比标准差, 用于判断五行平衡度
    original_balance = 0.0
    if wpo and 'wuxing_power' in wpo:
        wp = wpo['wuxing_power']
        total_all = sum(v.get('total', 0) for v in wp.values())
        if total_all > 0:
            primary_power_ratio = wp.get(primary, {}).get('total', 0) / total_all
            ratios = [v.get('total', 0) / total_all for v in wp.values()]
            mean_ratio = sum(ratios) / len(ratios)
            original_balance = (sum((r - mean_ratio) ** 2 for r in ratios) / len(ratios)) ** 0.5
            for wx, v in wp.items():
                if v.get('total', 0) < 0.5:  # 力量极低, 视为缺少
                    missing_wuxing.append(wx)
    
    # V3.8: 格局层面喜忌判断 (基于子平真诠各格局取运规则)
    # 判断伤官佩印格: 月令伤官 + 印星透干有根
    month_branch_main = pillars['month'][1]
    month_hidden = HIDDEN_STEMS.get(month_branch_main, [])
    # 月令本气对应的十神
    dm_wx_local = WX.get(dm, '')
    month_benqi = month_hidden[0] if month_hidden else ''
    month_benqi_wx = WX.get(month_benqi, '')
    # 判断月令是否是伤官(日主生的异性五行)
    is_shangguan_month = False
    if month_benqi_wx and dm_wx_local:
        # 伤官: 日主生的异性五行 (如甲木生丁火=伤官, 甲木生丙火=食神)
        if SHENG.get(dm_wx_local) == month_benqi_wx:
            dm_yang = dm in '甲丙戊庚壬'
            mb_yang = month_benqi in '甲丙戊庚壬'
            if dm_yang != mb_yang:  # 异性=伤官
                is_shangguan_month = True
    # 判断印星是否透干有根
    yin_stems = []
    yin_wx = SHENG_ME.get(dm_wx_local, '')  # 生日主的五行=印
    for pos in ['year', 'month', 'day', 'hour']:
        stem = pillars[pos][0]
        if WX.get(stem, '') == yin_wx:
            yin_stems.append(stem)
    # 印星有根: 地支中有印星五行的藏干
    yin_has_root = False
    for pos in ['year', 'month', 'day', 'hour']:
        branch = pillars[pos][1]
        hidden = HIDDEN_STEMS.get(branch, [])
        for h in hidden:
            if WX.get(h, '') == yin_wx:
                yin_has_root = True
                break
        if yin_has_root:
            break
    is_shangguan_peiyin = is_shangguan_month and len(yin_stems) > 0 and yin_has_root
    
    per_step = []
    for gz in dayun_list:
        gan = gz[0]
        zhi = gz[1]
        gan_wx = WX[gan]
        zhi_wx = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}.get(zhi, '')
        
        ten_god = get_ten_god(dm, gz)
        
        # 与用神/喜神/忌神的关系
        relations = []
        
        # 天干五行关系 (V3.6修复: 改为多个独立if判断, 允许同时具有多种关系属性)
        if gan_wx == primary:
            relations.append('GAN_PRIMARY')
        if gan_wx in secondary:
            relations.append('GAN_SECONDARY')
        if gan_wx in avoid:
            relations.append('GAN_AVOID')
        if SHENG.get(gan_wx) == primary:
            relations.append('GAN_SHENG_PRIMARY')  # 大运生用神
        if SHENG_ME.get(gan_wx) == primary:
            relations.append('GAN_PRIMARY_SHENG')  # 用神生大运(泄用神)
        if KE.get(gan_wx) == primary:
            relations.append('GAN_KE_PRIMARY')  # 大运克用神
        
        # 地支五行关系 (V3.6修复: 改为多个独立if判断)
        if zhi_wx == primary:
            relations.append('ZHI_PRIMARY')
        if zhi_wx in secondary:
            relations.append('ZHI_SECONDARY')
        if zhi_wx in avoid:
            relations.append('ZHI_AVOID')
        
        # V2.0: 大运藏干判断 (区分本气/中气/余气权重)
        zhi_hidden = HIDDEN_STEMS.get(zhi, [])
        zhi_hidden_wx = [WX.get(s, '') for s in zhi_hidden]
        # 本气(第1个)权重最高, 中气(第2个)次之, 余气(第3个)最小
        if len(zhi_hidden_wx) >= 1 and zhi_hidden_wx[0] == primary:
            relations.append('ZHI_HIDDEN_BENQI_PRIMARY')  # 大运藏干本气是用神, 喜(强)
        elif len(zhi_hidden_wx) >= 2 and zhi_hidden_wx[1] == primary:
            relations.append('ZHI_HIDDEN_ZHONGQI_PRIMARY')  # 大运藏干中气是用神, 喜(中)
        elif len(zhi_hidden_wx) >= 3 and zhi_hidden_wx[2] == primary:
            relations.append('ZHI_HIDDEN_YUQI_PRIMARY')  # 大运藏干余气是用神, 喜(弱)
        if avoid:
            if len(zhi_hidden_wx) >= 1 and zhi_hidden_wx[0] == avoid[0]:
                relations.append('ZHI_HIDDEN_BENQI_AVOID')  # 大运藏干本气是忌神, 忌(强)
            elif len(zhi_hidden_wx) >= 2 and zhi_hidden_wx[1] == avoid[0]:
                relations.append('ZHI_HIDDEN_ZHONGQI_AVOID')  # 大运藏干中气是忌神, 忌(中)
            elif len(zhi_hidden_wx) >= 3 and zhi_hidden_wx[2] == avoid[0]:
                relations.append('ZHI_HIDDEN_YUQI_AVOID')  # 大运藏干余气是忌神, 忌(弱)
        
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
        
        # V2.2: 三会判断 (大运地支与原局两个地支形成三会局)
        for sanhui in SAN_HUI:
            b1, b2, b3, huashen = sanhui
            sanhui_branches = {b1, b2, b3}
            if zhi in sanhui_branches:
                other_two = sanhui_branches - {zhi}
                if other_two.issubset(set(original_branches)):
                    relations.append(f'ZHI_SANHUI_{b1}{b2}{b3}')
                    if huashen == primary:
                        relations.append('SANHUI_PRIMARY')  # 三会化用神, 喜
        
        # V2.3: 半合判断 (大运地支与原局一个地支形成半合)
        for banhe in BAN_HE:
            b1, b2, huashen = banhe
            banhe_branches = {b1, b2}
            if zhi in banhe_branches:
                other_one = banhe_branches - {zhi}
                if other_one.issubset(set(original_branches)):
                    relations.append(f'ZHI_BANHE_{b1}{b2}')
                    if huashen == primary:
                        relations.append('BANHE_PRIMARY')  # 半合化用神, 喜
        
        # V2.4: 六害四支判断 (大运地支与原局任意地支六害)
        year_branch = pillars['year'][1]
        month_branch = pillars['month'][1]
        day_branch = pillars['day'][1]
        hour_branch = pillars['hour'][1]
        hai_target = LIU_HAI.get(zhi, '')
        for pos_name, pos_branch in [('YEAR', year_branch), ('MONTH', month_branch), ('DAY', day_branch), ('HOUR', hour_branch)]:
            if hai_target == pos_branch:
                relations.append(f'ZHI_HAI_{pos_name}')
                pos_branch_wx = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}.get(pos_branch, '')
                if pos_branch_wx == primary:
                    relations.append(f'HAI_{pos_name}_PRIMARY')  # 害该支用神根, 忌
        
        # V2.6: 三刑四支判断 (大运地支与原局任意地支三刑)
        xing_targets = SAN_XING.get(zhi, [])
        for pos_name, pos_branch in [('YEAR', year_branch), ('MONTH', month_branch), ('DAY', day_branch), ('HOUR', hour_branch)]:
            if pos_branch in xing_targets:
                relations.append(f'ZHI_XING_{pos_name}')
                pos_branch_wx = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}.get(pos_branch, '')
                if pos_branch_wx == primary:
                    relations.append(f'XING_{pos_name}_PRIMARY')  # 刑该支用神根, 忌
        
        # V1.4: 冲月令判断 (月令是最重要的地支, 冲月令影响大)
        month_branch = pillars['month'][1]
        chong_month_target = LIU_CHONG.get(zhi, '')
        if chong_month_target == month_branch:
            relations.append('ZHI_CHONG_MONTH')
            # 月令五行如果是用神, 冲月令则忌; 如果是忌神, 冲月令则喜
            month_branch_wx = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}.get(month_branch, '')
            if month_branch_wx == primary:
                relations.append('CHONG_MONTH_PRIMARY')  # 冲月令用神, 忌
            if avoid and month_branch_wx == avoid[0]:
                relations.append('CHONG_MONTH_AVOID')  # 冲月令忌神, 喜
        
        # V1.6: 冲日支判断 (日支是日主的根, 冲日支影响日主力量)
        day_branch = pillars['day'][1]
        chong_day_target = LIU_CHONG.get(zhi, '')
        if chong_day_target == day_branch:
            relations.append('ZHI_CHONG_DAY')
            day_branch_wx = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}.get(day_branch, '')
            if day_branch_wx == primary:
                relations.append('CHONG_DAY_PRIMARY')  # 冲日支用神根, 忌
            if avoid and day_branch_wx == avoid[0]:
                relations.append('CHONG_DAY_AVOID')  # 冲日支忌神根, 喜
        
        # V1.7: 冲年支/时支判断
        year_branch = pillars['year'][1]
        hour_branch = pillars['hour'][1]
        for pos_name, pos_branch in [('YEAR', year_branch), ('HOUR', hour_branch)]:
            chong_target = LIU_CHONG.get(zhi, '')
            if chong_target == pos_branch:
                relations.append(f'ZHI_CHONG_{pos_name}')
                pos_branch_wx = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}.get(pos_branch, '')
                if pos_branch_wx == primary:
                    relations.append(f'CHONG_{pos_name}_PRIMARY')  # 冲该支用神根, 忌
                if avoid and pos_branch_wx == avoid[0]:
                    relations.append(f'CHONG_{pos_name}_AVOID')  # 冲该支忌神根, 喜
        
        # V2.1: 六合四支判断 (大运地支与原局任意地支六合)
        he_info = LIU_HE.get(zhi, ('', ''))
        he_huashen = he_info[0]
        he_target = he_info[1]
        for pos_name, pos_branch in [('YEAR', year_branch), ('MONTH', month_branch), ('DAY', day_branch), ('HOUR', hour_branch)]:
            if he_target == pos_branch:
                relations.append(f'ZHI_HE_{pos_name}')
                if he_huashen == primary:
                    relations.append(f'HE_{pos_name}_PRIMARY')  # 合该支化用神, 喜
                if avoid and he_huashen == avoid[0]:
                    relations.append(f'HE_{pos_name}_AVOID')  # 合该支化忌神, 忌
        
        # 综合喜忌标签 (结构判断, 非吉凶)
        chong_primary_any = any('CHONG_' in r and '_PRIMARY' in r for r in relations)
        chong_avoid_any = any('CHONG_' in r and '_AVOID' in r for r in relations)
        hidden_primary_any = any('ZHI_HIDDEN_' in r and '_PRIMARY' in r for r in relations)
        hidden_avoid_any = any('ZHI_HIDDEN_' in r and '_AVOID' in r for r in relations)
        he_primary_any = any('HE_' in r and '_PRIMARY' in r for r in relations)
        he_avoid_any = any('HE_' in r and '_AVOID' in r for r in relations)
        hai_primary_any = any('HAI_' in r and '_PRIMARY' in r for r in relations)
        xing_primary_any = any('XING_' in r and '_PRIMARY' in r for r in relations)
        
        # V3.3: 十神关系判断 - 大运十神与用神十神的生克关系
        ten_god_xi = False
        ten_god_ji = False
        if primary_ten_god_type and ten_god != '未知':
            # 十神生克关系: 比劫生食伤, 食伤生财, 财生官杀, 官杀生印, 印生比劫
            sheng_chain = {'比劫': '食伤', '食伤': '财', '财': '官杀', '官杀': '印', '印': '比劫'}
            ke_chain = {'比劫': '财', '财': '印', '印': '食伤', '食伤': '官杀', '官杀': '比劫'}
            # 大运十神生用神十神 -> 喜
            if sheng_chain.get(ten_god) == primary_ten_god_type:
                ten_god_xi = True
            # 大运十神克用神十神 -> 忌
            if ke_chain.get(ten_god) == primary_ten_god_type:
                ten_god_ji = True
        
        # V3.2: 多标签输出 - 一个大运可能同时具有多种喜忌属性
        # V3.8: 伤官佩印格中官星为喜 (官杀生印→印生身, 流通有情)
        shangguan_peiyin_guanxi = False
        if is_shangguan_peiyin:
            # 官星五行: 克日主的五行
            guan_wx = KE_ME.get(dm_wx_local, '')
            if gan_wx == guan_wx or zhi_wx == guan_wx:
                shangguan_peiyin_guanxi = True
        
        has_xi = ('GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations 
                  or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'SANHUI_PRIMARY' in relations 
                  or 'BANHE_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any
                  or ten_god_xi or 'MONTH_ROOT_SHENG' in relations or shangguan_peiyin_guanxi)
        has_ji = ('GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations 
                  or 'GAN_PRIMARY_SHENG' in relations or hidden_avoid_any or chong_primary_any or he_avoid_any or hai_primary_any or xing_primary_any
                  or ten_god_ji or 'MONTH_ROOT_KE' in relations)
        xiji_labels = []
        if has_xi:
            xiji_labels.append('SUPPORT_USE_GOD')
        if has_ji:
            xiji_labels.append('SUPPRESS_USE_GOD')
        if 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            xiji_labels.append('SUPPORT_XI_SHEN')
        if not xiji_labels:
            xiji_labels.append('NEUTRAL')
        
        # V2.7: 用神力量修正 # PCT-MARK: 用神弱(<15%)时生扶更喜, 用神强(>30%)时克泄可能为喜
        primary_weak = primary_power_ratio < 0.15 if primary_power_ratio > 0 else False
        primary_strong = primary_power_ratio > 0.30 if primary_power_ratio > 0 else False
        
        if has_xi and has_ji:
            # 生扶和克泄同时存在: 用神弱则生扶, 用神强则克泄, 否则生扶优先
            if primary_weak:
                xiji_label = 'SUPPORT_USE_GOD'
            elif primary_strong:
                xiji_label = 'SUPPRESS_USE_GOD'
            else:
                xiji_label = 'SUPPORT_USE_GOD'
        elif has_xi:
            xiji_label = 'SUPPORT_USE_GOD'
        elif has_ji:
            # 只有克泄: 用神强时可能是抑制过强(为喜)
            if primary_strong:
                xiji_label = 'SUPPORT_USE_GOD'
            else:
                xiji_label = 'SUPPRESS_USE_GOD'
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
            'xiji_labels': xiji_labels,
            'xiji_labels': xiji_labels,
        })
    
    return {
        'module': 'DAYUN_XIJI_V3.8',
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
