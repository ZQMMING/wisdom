import sys
sys.path.insert(0, 'scripts')
from dayun_align import l0build, build_power_structure, build_root_classes, build_tou_cang, build_wang_xiang, build_root_relations, build_two_side, build_branch_tiers, build_tian_he, build_wuxing_power, build_power_network, build_climate_structure, build_special_patterns

fp = [('丙','寅'),('辛','卯'),('癸','酉'),('戊','午')]
p = {'year':list(fp[0]),'month':list(fp[1]),'day':list(fp[2]),'hour':list(fp[3])}
f = l0build(p)
ds = f['day_stem']
hst = {p[k][1]:f['hidden_stems'][k] for k in ('year','month','day','hour')}
pa = build_power_structure(p); rc = build_root_classes(p,hst); tc = build_tou_cang(f)
wxo = build_wang_xiang(f,ds); rr = build_root_relations(rc,f['combination_facts'])
ts = build_two_side(rc,tc,rr); bt = build_branch_tiers(p,f); th = build_tian_he(p,f)
wp = build_wuxing_power(p,f,th)
cls = build_climate_structure(p,f,th)
spp = build_special_patterns(p,f,wp,th,cls)

print("=== L1430 special ===")
print("cong_type:", spp.get('cong_type'))
print("hua_qi:", spp.get('hua_qi'))
print("hua_qi_state:", spp.get('hua_qi_state'))
print("zhuanwang:", spp.get('zhuanwang'))
print("patterns:")
for pat in spp.get('patterns', []):
    print(f"  name={pat.get('name')}, state={pat.get('state')}, side={pat.get('side')}")
print("tian_he:", th)
if th:
    print("  he_pairs:")
    for hp in th.get('he_pairs', []):
        print(f"    stems={hp.get('stems')}, pillars={hp.get('pillars')}")
