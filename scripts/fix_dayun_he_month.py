# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在六冲表后增加六合表
old = """# 六冲表
LIU_CHONG = {
    '子':'午', '午':'子',
    '丑':'未', '未':'丑',
    '寅':'申', '申':'寅',
    '卯':'酉', '酉':'卯',
    '辰':'戌', '戌':'辰',
    '巳':'亥', '亥':'巳',
}"""
new = """# 六冲表
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
}"""
c = c.replace(old, new)

# 在冲月令判断后增加合月令判断
old = """        if chong_month_target == month_branch:
            relations.append('ZHI_CHONG_MONTH')
            # 月令五行如果是用神, 冲月令则忌; 如果是忌神, 冲月令则喜
            month_branch_wx = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}.get(month_branch, '')
            if month_branch_wx == primary:
                relations.append('CHONG_MONTH_PRIMARY')  # 冲月令用神, 忌
            if avoid and month_branch_wx == avoid[0]:
                relations.append('CHONG_MONTH_AVOID')  # 冲月令忌神, 喜
        
        # 综合喜忌标签"""
new = """        if chong_month_target == month_branch:
            relations.append('ZHI_CHONG_MONTH')
            # 月令五行如果是用神, 冲月令则忌; 如果是忌神, 冲月令则喜
            month_branch_wx = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}.get(month_branch, '')
            if month_branch_wx == primary:
                relations.append('CHONG_MONTH_PRIMARY')  # 冲月令用神, 忌
            if avoid and month_branch_wx == avoid[0]:
                relations.append('CHONG_MONTH_AVOID')  # 冲月令忌神, 喜
        
        # V1.5: 合月令判断 (大运地支与月令六合)
        he_month_info = LIU_HE.get(zhi, ('', ''))
        he_month_huashen = he_month_info[0]
        he_month_target = he_month_info[1]
        if he_month_target == month_branch:
            relations.append('ZHI_HE_MONTH')
            if he_month_huashen == primary:
                relations.append('HE_MONTH_PRIMARY')  # 合月令化用神, 喜
            if avoid and he_month_huashen == avoid[0]:
                relations.append('HE_MONTH_AVOID')  # 合月令化忌神, 忌
        
        # 综合喜忌标签"""
c = c.replace(old, new)

# 修改综合喜忌标签逻辑, 增加合月令判断
old2 = """        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'CHONG_MONTH_AVOID' in relations:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif 'GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations or 'CHONG_MONTH_PRIMARY' in relations:
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神"""
new2 = """        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'CHONG_MONTH_AVOID' in relations or 'HE_MONTH_PRIMARY' in relations:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif 'GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations or 'CHONG_MONTH_PRIMARY' in relations or 'HE_MONTH_AVOID' in relations:
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神"""
c = c.replace(old2, new2)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V1.4'", "'module': 'DAYUN_XIJI_V1.5'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V1.5优化完成(增加合月令判断)')
