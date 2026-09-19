# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在冲日支判断后增加冲年支/时支判断
old = """        if chong_day_target == day_branch:
            relations.append('ZHI_CHONG_DAY')
            day_branch_wx = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}.get(day_branch, '')
            if day_branch_wx == primary:
                relations.append('CHONG_DAY_PRIMARY')  # 冲日支用神根, 忌
            if avoid and day_branch_wx == avoid[0]:
                relations.append('CHONG_DAY_AVOID')  # 冲日支忌神根, 喜
        
        # 综合喜忌标签"""
new = """        if chong_day_target == day_branch:
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
        
        # 综合喜忌标签"""
c = c.replace(old, new)

# 修改综合喜忌标签逻辑, 增加冲年支/时支判断
old2 = """        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'CHONG_MONTH_AVOID' in relations or 'CHONG_DAY_AVOID' in relations:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif 'GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations or 'CHONG_MONTH_PRIMARY' in relations or 'CHONG_DAY_PRIMARY' in relations:
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神"""
new2 = """        chong_primary_any = any('CHONG_' in r and '_PRIMARY' in r for r in relations)
        chong_avoid_any = any('CHONG_' in r and '_AVOID' in r for r in relations)
        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or chong_avoid_any:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif 'GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations or chong_primary_any:
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神"""
c = c.replace(old2, new2)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V1.6'", "'module': 'DAYUN_XIJI_V1.7'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V1.7优化完成(增加冲年支/时支,四支全冲)')
