# -*- coding: utf-8 -*-
import re

path=r'D:\shuntian-ziping-p0\engines\common\daymaster_power_queries.py'
content=open(path,encoding='utf-8').read()

# 把bijie_stem/yin_stem定义移到heavy之前
old="    heavy = root.get('root_weight_class') == 'HEAVY'\n    # 月令是日主墓库/余气+重根+印比透干也算旺令(如腊月壬水旺)"
new="    bijie_stem = bool(sup.get('BIJIE', {}).get('stem_present'))\n    yin_stem = bool(sup.get('YIN', {}).get('stem_present'))\n    heavy = root.get('root_weight_class') == 'HEAVY'\n    # 月令是日主墓库/余气+重根+印比透干也算旺令(如腊月壬水旺)"

content=content.replace(old,new)

# 删除后面重复的bijie_stem/yin_stem定义
old2="    bijie_stem = bool(sup.get('BIJIE', {}).get('stem_present'))\n    yin_stem = bool(sup.get('YIN', {}).get('stem_present'))\n    bijie_party = bool(bijie_stem and sup.get('BIJIE', {}).get('root_present'))"
new2="    bijie_party = bool(bijie_stem and sup.get('BIJIE', {}).get('root_present'))"

content=content.replace(old2,new2)

open(path,'w',encoding='utf-8',newline='').write(content)
print('done')
