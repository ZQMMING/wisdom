# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 回退合月令判断
old = """        # V1.5: 合月令判断 (大运地支与月令六合)
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
new = """        # V1.6: 冲日支判断 (日支是日主的根, 冲日支影响日主力量)
        day_branch = pillars['day'][1]
        chong_day_target = LIU_CHONG.get(zhi, '')
        if chong_day_target == day_branch:
            relations.append('ZHI_CHONG_DAY')
            day_branch_wx = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}.get(day_branch, '')
            if day_branch_wx == primary:
                relations.append('CHONG_DAY_PRIMARY')  # 冲日支用神根, 忌
            if avoid and day_branch_wx == avoid[0]:
                relations.append('CHONG_DAY_AVOID')  # 冲日支忌神根, 喜
        
        # 综合喜忌标签"""
c = c.replace(old, new)

# 修改综合喜忌标签逻辑, 增加冲日支判断
old2 = """        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'CHONG_MONTH_AVOID' in relations or 'HE_MONTH_PRIMARY' in relations:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif 'GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations or 'CHONG_MONTH_PRIMARY' in relations or 'HE_MONTH_AVOID' in relations:
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神"""
new2 = """        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'CHONG_MONTH_AVOID' in relations or 'CHONG_DAY_AVOID' in relations:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif 'GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations or 'CHONG_MONTH_PRIMARY' in relations or 'CHONG_DAY_PRIMARY' in relations:
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神"""
c = c.replace(old2, new2)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V1.5'", "'module': 'DAYUN_XIJI_V1.6'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V1.6优化完成(回退合月令,增加冲日支)')
