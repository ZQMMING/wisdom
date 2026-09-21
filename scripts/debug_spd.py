import sys
sys.path.insert(0, 'scripts')
from engines.common.wuxing_power import build_wuxing_power, build_spectrum_from_power, build_spectrum_topology
from dayun_align import l0build, build_power_structure, build_root_classes, build_tou_cang, build_wang_xiang, build_root_relations, build_two_side, build_branch_tiers, build_tian_he, build_power_network

fp = [('壬','子'),('辛','亥'),('乙','亥'),('丙','子')]
p = {'year':list(fp[0]),'month':list(fp[1]),'day':list(fp[2]),'hour':list(fp[3])}
f = l0build(p)
ds = f['day_stem']
hst = {p[k][1]:f['hidden_stems'][k] for k in ('year','month','day','hour')}
pa = build_power_structure(p); rc = build_root_classes(p,hst); tc = build_tou_cang(f)
wxo = build_wang_xiang(f,ds); rr = build_root_relations(rc,f['combination_facts'])
ts = build_two_side(rc,tc,rr); bt = build_branch_tiers(p,f); th = build_tian_he(p,f)
wp = build_wuxing_power(p,f,th)
net = build_power_network(pa,rc,tc,wxo,rr,ts,branch_tier=bt,tian_he=th,facts=f)

spd = build_spectrum_from_power(wp, p)
print("spd keys:", list(spd.keys()))
print("wang_shuai:", spd.get('wang_shuai'))
print("qiang_ruo:", spd.get('qiang_ruo'))
print("spectrum:", spd.get('spectrum'))
