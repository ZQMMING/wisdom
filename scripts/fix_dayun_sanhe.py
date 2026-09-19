# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 增加三合表
old1 = """# 五合表 (天干 -> 合化五行)
WU_HE = {
    '甲': ('土', '己'), '己': ('土', '甲'),
    '乙': ('金', '庚'), '庚': ('金', '乙'),
    '丙': ('水', '辛'), '辛': ('水', '丙'),
    '丁': ('木', '壬'), '壬': ('木', '丁'),
    '戊': ('火', '癸'), '癸': ('火', '戊'),
}"""
new1 = """# 五合表 (天干 -> 合化五行)
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
]"""
c = c.replace(old1, new1)

# 在五合判断后增加三合判断
old2 = """        if wuhe_target and wuhe_target in original_stems:
            relations.append(f'GAN_WUHE_{wuhe_target}')
            if wuhe_huashen == primary:
                relations.append('WUHE_PRIMARY')  # 合化用神, 喜
        
        # 综合喜忌标签"""
new2 = """        if wuhe_target and wuhe_target in original_stems:
            relations.append(f'GAN_WUHE_{wuhe_target}')
            if wuhe_huashen == primary:
                relations.append('WUHE_PRIMARY')  # 合化用神, 喜
        
        # V1.2: 三合判断 (大运地支与原局两个地支形成三合局)
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
c = c.replace(old2, new2)

# 修改综合喜忌标签逻辑, 增加三合判断
old3 = """        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神"""
new3 = """        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神"""
c = c.replace(old3, new3)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V1.1'", "'module': 'DAYUN_XIJI_V1.2'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V1.2优化完成(增加三合判断)')
