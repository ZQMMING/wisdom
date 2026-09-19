# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\wuxing_power.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 修复第499行: 三合局(self_ju)旺极应受月令限制, 只有三会方才不受月令失令限制
# 案例4庚申戊寅壬子甲辰: 申子辰三合水局但寅月失令(L=0), 被误判旺极导致用神走食伤木而非印金
old = """    elif S==3 and self_ju and dm_ben>=3 and fin_rooted_eff<=1:
        spec='旺极'"""
new = """    elif S==3 and self_ju and dm_ben>=3 and fin_rooted_eff<=1 and L>=1:
        spec='旺极'   # 三合局旺极须得令/相令(失令三合局不判旺极, 如庚申戊寅壬子甲辰寅月食神当令); 三会方才不受月令限制"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('三合局旺极判断修复完成')
