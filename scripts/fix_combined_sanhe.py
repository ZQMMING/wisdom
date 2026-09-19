# -*- coding: utf-8 -*-
import re

path=r'D:\shuntian-ziping-p0\engines\common\daymaster_power_queries.py'
content=open(path,encoding='utf-8').read()

# 在_root_combined_away函数里加三合局处理
old="    for pillar in comb_root:\n        info = root_detail.get(pillar, {})\n        for rel in (info.get('relations') or []):\n            if rel.get('relation') == 'SIX_COMBINE':\n                huashen = rel.get('huashen', '')\n                if huashen and month_wx == huashen and huashen != dm_wx:\n                    return True\n    return False"
new="    # 三合局化神表\n    SANHE_HUASHEN = {'亥卯未':'木','寅午戌':'火','申子辰':'水','巳酉丑':'金'}\n    for pillar in comb_root:\n        info = root_detail.get(pillar, {})\n        for rel in (info.get('relations') or []):\n            if rel.get('relation') == 'SIX_COMBINE':\n                huashen = rel.get('huashen', '')\n                if huashen and month_wx == huashen and huashen != dm_wx:\n                    return True\n            # 三合局: 根支参与三合局且化神得令且化神≠日主五行\n            elif rel.get('relation') == 'SANHE':\n                branches = rel.get('branches', [])\n                if len(branches) == 3:\n                    key = ''.join(sorted(branches))\n                    # 尝试所有排列\n                    for k, v in SANHE_HUASHEN.items():\n                        if set(k) == set(branches):\n                            huashen = v\n                            if huashen and month_wx == huashen and huashen != dm_wx:\n                                return True\n                            break\n    return False"

content=content.replace(old,new)

open(path,'w',encoding='utf-8',newline='').write(content)
print('done')
