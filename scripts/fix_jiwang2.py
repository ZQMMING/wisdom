# -*- coding: utf-8 -*-
import re

path=r'D:\shuntian-ziping-p0\engines\common\daymaster_power_queries.py'
content=open(path,encoding='utf-8').read()

old="    # 太旺须天干印比成势(透干帮扶), 不能仅凭地支重根; 成势=成党或多支重根\n    stem_aided = bijie_stem or yin_stem\n    chengshi = bijie_party or yin_party or multi_heavy"
new="    # 太旺须印比成势(透干帮扶或地支有根), 不能仅凭地支重根; 成势=成党或多支重根\n    bijie_root = bool(sup.get('BIJIE', {}).get('root_present'))\n    yin_root = bool(sup.get('YIN', {}).get('root_present'))\n    stem_aided = bijie_stem or yin_stem or bijie_root or yin_root\n    chengshi = bijie_party or yin_party or multi_heavy"

content=content.replace(old,new)

open(path,'w',encoding='utf-8',newline='').write(content)
print('done')
