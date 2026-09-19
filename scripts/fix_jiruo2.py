# -*- coding: utf-8 -*-
import re

path=r'D:\shuntian-ziping-p0\engines\common\daymaster_power_queries.py'
content=open(path,encoding='utf-8').read()

old="    root_struck_extreme = root_struck and root_heavy and op_party and weak_support\n    is_extreme = bool((root_none and no_support) or (root_light and op_party and weak_support) or root_struck_extreme)"
new="    root_struck_extreme = root_struck and root_heavy and op_party\n    is_extreme = bool((root_none and no_support) or (root_light and op_party) or root_struck_extreme)"

content=content.replace(old,new)

open(path,'w',encoding='utf-8',newline='').write(content)
print('done')
