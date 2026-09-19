# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 增加六破表
old = """# 三刑表 (地支 -> 刑的地支列表)
SAN_XING = {
    '寅': ['巳', '申'], '巳': ['寅', '申'], '申': ['寅', '巳'],
    '丑': ['戌', '未'], '戌': ['丑', '未'], '未': ['丑', '戌'],
    '子': ['卯'], '卯': ['子'],
    '辰': ['午', '酉', '亥'], '午': ['辰', '酉', '亥'],
    '酉': ['辰', '午', '亥'], '亥': ['辰', '午', '酉'],
}"""
new = """# 三刑表 (地支 -> 刑的地支列表)
SAN_XING = {
    '寅': ['巳', '申'], '巳': ['寅', '申'], '申': ['寅', '巳'],
    '丑': ['戌', '未'], '戌': ['丑', '未'], '未': ['丑', '戌'],
    '子': ['卯'], '卯': ['子'],
    '辰': ['午', '酉', '亥'], '午': ['辰', '酉', '亥'],
    '酉': ['辰', '午', '亥'], '亥': ['辰', '午', '酉'],
}

# 六破表
LIU_PO = {
    '子': '酉', '酉': '子',
    '丑': '辰', '辰': '丑',
    '寅': '亥', '亥': '寅',
    '卯': '午', '午': '卯',
    '巳': '申', '申': '巳',
    '未': '戌', '戌': '未',
}"""
c = c.replace(old, new)

# 在三刑判断后增加六破四支判断
old = """        # V1.4: 冲月令判断"""
new = """        # V2.8: 六破四支判断 (大运地支与原局任意地支六破)
        po_target = LIU_PO.get(zhi, '')
        for pos_name, pos_branch in [('YEAR', year_branch), ('MONTH', month_branch), ('DAY', day_branch), ('HOUR', hour_branch)]:
            if po_target == pos_branch:
                relations.append(f'ZHI_PO_{pos_name}')
                pos_branch_wx = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}.get(pos_branch, '')
                if pos_branch_wx == primary:
                    relations.append(f'PO_{pos_name}_PRIMARY')  # 破该支用神根, 忌
        
        # V1.4: 冲月令判断"""
c = c.replace(old, new)

# 修改综合喜忌标签逻辑, 增加六破判断
old2 = """        xing_primary_any = any('XING_' in r and '_PRIMARY' in r for r in relations)
        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'SANHUI_PRIMARY' in relations or 'BANHE_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any:"""
new2 = """        xing_primary_any = any('XING_' in r and '_PRIMARY' in r for r in relations)
        po_primary_any = any('PO_' in r and '_PRIMARY' in r for r in relations)
        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'SANHUI_PRIMARY' in relations or 'BANHE_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any:"""
c = c.replace(old2, new2)

# 修改克泄判断, 增加六破
old3 = """        elif 'GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations or hidden_avoid_any or chong_primary_any or he_avoid_any or hai_primary_any or xing_primary_any:"""
new3 = """        elif 'GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations or hidden_avoid_any or chong_primary_any or he_avoid_any or hai_primary_any or xing_primary_any or po_primary_any:"""
c = c.replace(old3, new3)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V2.7'", "'module': 'DAYUN_XIJI_V2.8'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V2.8优化完成(增加六破四支判断)')
