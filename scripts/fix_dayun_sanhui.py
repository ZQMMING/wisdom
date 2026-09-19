# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 增加三会表
old = """# 三合表 (每个三合局: (地支1, 地支2, 地支3, 合化五行))
SAN_HE = [
    ('亥', '卯', '未', '木'),
    ('寅', '午', '戌', '火'),
    ('申', '子', '辰', '水'),
    ('巳', '酉', '丑', '金'),
]"""
new = """# 三合表 (每个三合局: (地支1, 地支2, 地支3, 合化五行))
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
]"""
c = c.replace(old, new)

# 在三合判断后增加三会判断
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
        
        # V1.4: 冲月令判断"""
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
        
        # V1.4: 冲月令判断"""
c = c.replace(old, new)

# 修改综合喜忌标签逻辑, 增加三会判断
old2 = """        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神"""
new2 = """        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'SANHUI_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神"""
c = c.replace(old2, new2)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V2.1'", "'module': 'DAYUN_XIJI_V2.2'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V2.2优化完成(增加三会判断)')
