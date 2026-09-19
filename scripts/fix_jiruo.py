# -*- coding: utf-8 -*-
import re

path=r'D:\shuntian-ziping-p0\engines\common\daymaster_power_queries.py'
content=open(path,encoding='utf-8').read()

old="""    # 假从: 轻根(余气墓库)+对方成党(财官食伤透干成势)
    root_light = root.get('root_weight_class') == 'LIGHT'
    op_members = [m for m, v in (op.get('members_present', {}) or {}).items() if v]
    op_party = len(op_members) >= 2
    dm_members = [m for m, v in (dm.get('members_present', {}) or {}).items() if v]
    weak_support = len(dm_members) < 2  # 印比不成党(0或1个)
    is_extreme = bool((root_none and no_support) or (root_light and op_party and weak_support))
    mode = '真从' if (root_none and no_support) else '假从'"""

new="""    # 假从: 轻根(余气墓库)+对方成党(财官食伤透干成势)
    root_light = root.get('root_weight_class') == 'LIGHT'
    op_members = [m for m, v in (op.get('members_present', {}) or {}).items() if v]
    op_party = len(op_members) >= 2
    dm_members = [m for m, v in (dm.get('members_present', {}) or {}).items() if v]
    weak_support = len(dm_members) < 2  # 印比不成党(0或1个)
    # 根被冲拔: ROOT-STRUCK+HEAVY+对方成党+印比不成党
    rr = network['dimensions'].get('ROOT_RELATION', {})
    root_struck = bool(rr.get('struck_root_pillars', []))
    root_heavy = root.get('root_weight_class') == 'HEAVY'
    root_struck_extreme = root_struck and root_heavy and op_party and weak_support
    is_extreme = bool((root_none and no_support) or (root_light and op_party and weak_support) or root_struck_extreme)
    mode = '真从' if (root_none and no_support) else ('根被冲拔' if root_struck_extreme else '假从')"""

content=content.replace(old,new)

open(path,'w',encoding='utf-8',newline='').write(content)
print('done')
