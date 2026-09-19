# -*- coding: utf-8 -*-
import re

path = r'D:\shuntian-ziping-p0\engines\common\daymaster_power_queries.py'
content = open(path, encoding='utf-8').read()

# 在query_jiruo_wugen里加从杀格条件
old = """    # 无根+财多身弱
    cai_duo = bool(network['dimensions'].get('DRAIN', {}).get('CAI', {}).get('stem_present')) and root_none
    is_extreme = bool((root_none and no_support) or (root_light and op_party) or root_struck_extreme or root_he_extreme or cai_duo)
    mode = '真从' if (root_none and no_support) else ('根被冲拔' if root_struck_extreme else '假从')"""

new = """    # 从杀格: HEAVY根+七杀三重以上(天干+地支)+印比不成党
    facts = network.get('facts', {})
    tgm = facts.get('ten_god_members', []) if isinstance(facts, dict) else []
    qisha_count = sum(1 for m in tgm if m.get('ten_god') == '七杀')
    dm_members_list = [m for m, v in (dm.get('members_present', {}) or {}).items() if v]
    weak_support_dm = len(dm_members_list) < 2
    cong_sha = bool(root_heavy and qisha_count >= 3 and weak_support_dm)
    # 三合局克身: HEAVY根+三合局(亥卯未/寅午戌/申子辰/巳酉丑)化神克日主+印比不成党
    comb_facts = facts.get('combination_facts', []) if isinstance(facts, dict) else []
    sanhe_ju = any(c.get('type') == 'SANHE' for c in comb_facts) if isinstance(comb_facts, list) else False
    sanhe_ke_shen = bool(root_heavy and sanhe_ju and weak_support_dm)
    # 无根+财多身弱
    cai_duo = bool(network['dimensions'].get('DRAIN', {}).get('CAI', {}).get('stem_present')) and root_none
    is_extreme = bool((root_none and no_support) or (root_light and op_party) or root_struck_extreme or root_he_extreme or cai_duo or cong_sha or sanhe_ke_shen)
    mode = '真从' if (root_none and no_support) else ('根被冲拔' if root_struck_extreme else ('从杀' if cong_sha else ('三合克身' if sanhe_ke_shen else '假从')))"""

content = content.replace(old, new)

open(path, 'w', encoding='utf-8', newline='\n').write(content)
print('done')
