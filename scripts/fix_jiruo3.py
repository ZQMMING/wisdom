# -*- coding: utf-8 -*-
import re

path=r'D:\shuntian-ziping-p0\engines\common\daymaster_power_queries.py'
content=open(path,encoding='utf-8').read()

old="    root_struck_extreme = root_struck and root_heavy and op_party\n    is_extreme = bool((root_none and no_support) or (root_light and op_party) or root_struck_extreme)"
new="    root_struck_extreme = root_struck and root_heavy and op_party\n    # 根被合走: HE-HUASHEN-DESHI+HEAVY+对方成党\n    # 检查network里是否有合化成功相关信息\n    th = network['dimensions'].get('TIAN_HE', {})\n    he_huashen = bool(th.get('he_huashen_chenggong', [])) or bool(th.get('he_pairs', []))\n    root_he_extreme = he_huashen and root_heavy and op_party\n    # 无根+财多身弱\n    cai_duo = bool(network['dimensions'].get('DRAIN', {}).get('CAI', {}).get('stem_present')) and root_none\n    is_extreme = bool((root_none and no_support) or (root_light and op_party) or root_struck_extreme or root_he_extreme or cai_duo)"

content=content.replace(old,new)

open(path,'w',encoding='utf-8',newline='').write(content)
print('done')
