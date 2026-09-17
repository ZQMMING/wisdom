# -*- coding: utf-8 -*-
"""DTS 7个真命例 认真对照."""
import sys
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build
from engines.common.daymaster_power_structure import build_power_structure
from engines.common.daymaster_root_class import build_root_classes
from engines.common.daymaster_tou_cang import build_tou_cang
from engines.common.daymaster_wang_xiang import build_wang_xiang
from engines.common.daymaster_root_relations import build_root_relations
from engines.common.daymaster_two_side import build_two_side
from engines.common.daymaster_branch_tier import build_branch_tiers
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.daymaster_power_network import build_power_network
from engines.common.daymaster_power_queries import run_queries

cases = [
    ("DTS-01 辛卯丁酉庚午丙子(金水四正,任氏:不作旺论)", {'year':['辛','卯'],'month':['丁','酉'],'day':['庚','午'],'hour':['丙','子']},
     "任氏: 五行无土虽诞秋令不作旺论; 子午卯酉四正"),
    ("DTS-02 庚申庚辰戊辰戊午(董中堂,任氏:似乎旺相日主过泄)", {'year':['庚','申'],'month':['庚','辰'],'day':['戊','辰'],'hour':['戊','午']},
     "任氏: 春时虚土非六九月实; 两辰泄火生金; 日主过泄; 午火印"),
    ("DTS-03 辛酉辛丑己酉丙寅(任氏:日主过泄用神丙火)", {'year':['辛','酉'],'month':['辛','丑'],'day':['己','酉'],'hour':['丙','寅']},
     "任氏: 冬土寒湿; 干透两辛支会丑酉; 日主过泄; 丙火有根寅"),
    ("DTS-04 壬辰壬寅甲寅庚午(王姓,任氏:身强杀浅旺极宜泄)", {'year':['壬','辰'],'month':['壬','寅'],'day':['甲','寅'],'hour':['庚','午']},
     "任氏: 支坐两寅乘权当令; 干透两壬生助; 庚金休囚; 旺极宜泄"),
    ("DTS-05 癸酉甲子癸亥辛酉(任氏:金水旺极顺其流)", {'year':['癸','酉'],'month':['甲','子'],'day':['癸','亥'],'hour':['辛','酉']},
     "任氏: 满局金水; 水旺逢金; 旺则宜泄宜伤"),
    ("DTS-06 丁亥庚戌甲辰壬申(任氏:似乎杀重身轻实壬水贴身)", {'year':['丁','亥'],'month':['庚','戌'],'day':['甲','辰'],'hour':['壬','申']},
     "任氏: 甲木休囚庚金禄旺克之; 杀重身轻; 壬水贴身生; 丁火通根身库戌"),
    ("DTS-07 乙亥庚辰甲戌壬申(任氏:乙庚合化金反助其暴)", {'year':['乙','亥'],'month':['庚','辰'],'day':['甲','戌'],'hour':['壬','申']},
     "任氏: 乙庚合化金反助其暴; 戌燥土不能生木"),
]
for name, p, note in cases:
    f = build(p); pa = build_power_structure(p)
    hst = {p[k][1]: f['hidden_stems'][k] for k in ('year','month','day','hour')}
    rc = build_root_classes(p, hst); tc = build_tou_cang(f); wx = build_wang_xiang(f, f['day_stem'])
    rr = build_root_relations(rc, f['combination_facts']); ts = build_two_side(rc, tc, rr)
    bt = build_branch_tiers(p, f); th = build_tian_he(p, f)
    net = build_power_network(pa, rc, tc, wx, rr, ts, branch_tier=bt, tian_he=th)
    print(f"\n=== {name}")
    print(f"  任氏: {note}")
    print(f"  root={net['dimensions']['ROOT']['root_weight_class']}  seasonal={net['dimensions']['SEASONAL'].get('state')}")
    for q in run_queries(net):
        if q['state'] != 'NOT_SUPPORTED':
            print(f"  {q['query_id'].split('QUERY-')[-1]:22s} {q['state']:10s} {q['match_type']}")
