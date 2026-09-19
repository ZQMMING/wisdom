# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\wuxing_power.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 修复"旺极"判断: 印重成势生身但日主失令(L=0)时不应判旺极
# 案例5己丑丙子辛酉壬辰: 印ben=3但子月伤官当令+丙火官杀, 误判旺极导致用神走调候火而非食伤水
old = """    elif S==3 and fin_rooted_eff==0 and (yin_ju or yin_ben>=3) and ratio>=0.85 and dm_heavy>=1:
        spec='旺极'   # 得令两本气根 + 印多根(两长生逢禄旺, 木火/水木成势)"""

new = """    elif S==3 and fin_rooted_eff==0 and (yin_ju or yin_ben>=3) and ratio>=0.85 and dm_heavy>=1 and L>=1:
        spec='旺极'   # 得令/相令 + 印多根成势生身(失令印重不判旺极, 如己丑丙子辛酉壬辰子月伤官当令)"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('spectrum旺极判断修复完成')
