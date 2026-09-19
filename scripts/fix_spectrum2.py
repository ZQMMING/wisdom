# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\wuxing_power.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 修复拱局旺极: 半合本方局+印重但日主失令(L=0)时不应判旺极
old = """    elif S==3 and fin_rooted_eff==0 and dm_banhe>=1 and dm_heavy>=1 and (yin_ben>=2 or yin_ju) and ratio>=0.40:
        spec='旺极'   # 印成方/三根生身(水旺木坚)"""

new = """    elif S==3 and fin_rooted_eff==0 and dm_banhe>=1 and dm_heavy>=1 and (yin_ben>=2 or yin_ju) and ratio>=0.40 and L>=1:
        spec='旺极'   # 得令/相令+半合本方局+印重(失令印重不判旺极, 如己丑丙子辛酉壬辰子月伤官当令+丙火官杀)"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('拱局旺极判断修复完成')
