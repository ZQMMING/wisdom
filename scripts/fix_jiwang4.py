# -*- coding: utf-8 -*-
import re

path=r'D:\shuntian-ziping-p0\engines\common\daymaster_power_queries.py'
content=open(path,encoding='utf-8').read()

old="    # 成势=成党或多支重根或(重根+地支有印比)\n    root_with_yinbi = heavy and (bijie_root or yin_root)\n    chengshi = bijie_party or yin_party or multi_heavy or root_with_yinbi"
new="    # 地支三会/三合局成日主同类\n    th = network['dimensions'].get('TIAN_HE', {})\n    sanhui = th.get('sanhui_ju', []) or []\n    sanhe = th.get('sanhe_ju', []) or []\n    STEM_WX2 = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}\n    f2 = network.get('facts', {}) or {}\n    dm_wx2 = STEM_WX2.get(f2.get('day_stem',''), '')\n    party_ju = False\n    for ju in sanhui + sanhe:\n        ju_wx = ju.get('wuxing', '') if isinstance(ju, dict) else ''\n        if ju_wx == dm_wx2:\n            party_ju = True\n    # 成势=成党或多支重根或(重根+地支有印比)或地支会局成日主同类\n    root_with_yinbi = heavy and (bijie_root or yin_root)\n    chengshi = bijie_party or yin_party or multi_heavy or root_with_yinbi or party_ju"

content=content.replace(old,new)

open(path,'w',encoding='utf-8',newline='').write(content)
print('done')
