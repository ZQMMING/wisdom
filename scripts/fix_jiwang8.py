# -*- coding: utf-8 -*-
import re

path=r'D:\shuntian-ziping-p0\engines\common\daymaster_power_queries.py'
content=open(path,encoding='utf-8').read()

old="    # 成势=成党或多支重根或(重根+地支有印比)或地支会局成日主同类\n    root_with_yinbi = heavy and (bijie_root or yin_root)\n    chengshi = bijie_party or yin_party or multi_heavy or root_with_yinbi or party_ju"
new="    # 成势=成党或多支重根或(重根+地支有印比)或(重根+印比透干)或地支会局成日主同类\n    root_with_yinbi = heavy and (bijie_root or yin_root)\n    root_with_stem = heavy and (bijie_stem or yin_stem)\n    chengshi = bijie_party or yin_party or multi_heavy or root_with_yinbi or root_with_stem or party_ju"

content=content.replace(old,new)

open(path,'w',encoding='utf-8',newline='').write(content)
print('done')
