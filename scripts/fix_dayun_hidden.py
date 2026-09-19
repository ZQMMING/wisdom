# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 增加地支藏干表
old = """# 六合表 (地支 -> (合化五行, 合化地支对))
LIU_HE = {
    '子': ('土', '丑'), '丑': ('土', '子'),
    '寅': ('木', '亥'), '亥': ('木', '寅'),
    '卯': ('火', '戌'), '戌': ('火', '卯'),
    '辰': ('金', '酉'), '酉': ('金', '辰'),
    '巳': ('水', '申'), '申': ('水', '巳'),
    '午': ('土', '未'), '未': ('土', '午'),
}"""
new = """# 六合表 (地支 -> (合化五行, 合化地支对))
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
}"""
c = c.replace(old, new)

# 在地支五行关系后增加大运藏干判断
old = """        # 地支五行关系
        if zhi_wx == primary:
            relations.append('ZHI_PRIMARY')
        elif zhi_wx in secondary:
            relations.append('ZHI_SECONDARY')
        elif zhi_wx in avoid:
            relations.append('ZHI_AVOID')
        
        # V1.1: 五合判断"""
new = """        # 地支五行关系
        if zhi_wx == primary:
            relations.append('ZHI_PRIMARY')
        elif zhi_wx in secondary:
            relations.append('ZHI_SECONDARY')
        elif zhi_wx in avoid:
            relations.append('ZHI_AVOID')
        
        # V1.9: 大运藏干判断 (大运地支藏干中有用神/忌神)
        zhi_hidden = HIDDEN_STEMS.get(zhi, [])
        zhi_hidden_wx = [WX.get(s, '') for s in zhi_hidden]
        if primary in zhi_hidden_wx:
            relations.append('ZHI_HIDDEN_PRIMARY')  # 大运藏干中有用神, 喜
        if avoid and avoid[0] in zhi_hidden_wx:
            relations.append('ZHI_HIDDEN_AVOID')  # 大运藏干中有忌神, 忌
        
        # V1.1: 五合判断"""
c = c.replace(old, new)

# 修改综合喜忌标签逻辑, 增加大运藏干判断
old2 = """        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or chong_avoid_any:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif 'GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations or chong_primary_any:
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神"""
new2 = """        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'ZHI_HIDDEN_PRIMARY' in relations or chong_avoid_any:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif 'GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations or 'ZHI_HIDDEN_AVOID' in relations or chong_primary_any:
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神"""
c = c.replace(old2, new2)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V1.7'", "'module': 'DAYUN_XIJI_V1.9'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V1.9优化完成(增加大运藏干判断)')
