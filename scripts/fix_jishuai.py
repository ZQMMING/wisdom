# -*- coding: utf-8 -*-
import re

path=r'D:\shuntian-ziping-p0\engines\common\daymaster_power_queries.py'
content=open(path,encoding='utf-8').read()

old="    match = bool(out and no_root and (ctrl_party or drain_party))"
new="    # 火旺木焚: 失令+有根+食伤成党+克泄成党\n    xie_party = drain.get('SHISHANG', {}).get('stem_present') and drain.get('SHISHANG', {}).get('root_present')\n    huo_wang_mu_fen = out and (not no_root) and xie_party and (ctrl_party or drain_party)\n    match = bool((out and no_root and (ctrl_party or drain_party)) or huo_wang_mu_fen)"

content=content.replace(old,new)

open(path,'w',encoding='utf-8',newline='').write(content)
print('done')
