# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\special_pattern.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

old = """        chengfang_gu = (dm_ju >= 1 and gs_ben_zw == 0 and gs_ju == 0 and gs_stem == 0
                        and cai_ben_zw <= 1 and cai_ju == 0 and ss_stem < 2 and cai_stem < 2)"""

new = """        chengfang_gu = (dm_ju >= 1 and gs_stem == 0 and gs_ju == 0
                        and cai_ben_zw <= 1 and cai_ju == 0 and ss_stem < 2 and cai_stem < 2)"""

c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('special_pattern.py修改完成: chengfang_gu允许官杀藏支不透干')
