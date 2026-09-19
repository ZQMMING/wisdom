# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在三合判断后增加冲月令判断
old = """        # V1.2: 三合判断 (大运地支与原局两个地支形成三合局)
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
        
        # 综合喜忌标签"""
new = """        # V1.2: 三合判断 (大运地支与原局两个地支形成三合局)
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
        
        # 综合喜忌标签"""
c = c.replace(old, new)

# 修改综合喜忌标签逻辑, 增加冲月令判断
old2 = """        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif 'GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations:
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神"""
new2 = """        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'CHONG_MONTH_AVOID' in relations:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif 'GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations or 'CHONG_MONTH_PRIMARY' in relations:
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神"""
c = c.replace(old2, new2)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V1.2'", "'module': 'DAYUN_XIJI_V1.4'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V1.4优化完成(增加冲月令判断)')
