# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'.')
from engines.common.l0_fact_builder import build
from engines.common.daymaster_root_class import build_root_classes
from engines.common.daymaster_power_network import build_power_network

pillars = {
    'year': ('甲', '寅'),
    'month': ('癸', '酉'),
    'day': ('乙', '酉'),
    'hour': ('乙', '酉'),
}
facts = build(pillars)
tgm = facts.get('ten_god_members', [])
print('ten_god_members:')
for m in tgm:
    print(f"  {m}")
print(f"\n七杀数量: {sum(1 for m in tgm if m.get('ten_god') == '七杀')}")
print(f"所有ten_god值: {set(m.get('ten_god') for m in tgm)}")
