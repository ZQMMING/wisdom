# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 增加半合表
old = """# 三会表 (每个三会局: (地支1, 地支2, 地支3, 合化五行))
SAN_HUI = [
    ('寅', '卯', '辰', '木'),
    ('巳', '午', '未', '火'),
    ('申', '酉', '戌', '金'),
    ('亥', '子', '丑', '水'),
]"""
new = """# 三会表 (每个三会局: (地支1, 地支2, 地支3, 合化五行))
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
]"""
c = c.replace(old, new)

# 在三会判断后增加半合判断
old = """        # V2.2: 三会判断 (大运地支与原局两个地支形成三会局)
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
new = """        # V2.2: 三会判断 (大运地支与原局两个地支形成三会局)
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
        
        # V1.4: 冲月令判断"""
c = c.replace(old, new)

# 修改综合喜忌标签逻辑, 增加半合判断
old2 = """        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'SANHUI_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神"""
new2 = """        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'SANHUI_PRIMARY' in relations or 'BANHE_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神"""
c = c.replace(old2, new2)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V2.2'", "'module': 'DAYUN_XIJI_V2.3'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V2.3优化完成(增加半合判断)')
