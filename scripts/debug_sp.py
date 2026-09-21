import sys
sys.path.insert(0, 'scripts')
from dayun_align import engine, cases, l0build, build_power_structure, build_root_classes, build_tou_cang, build_wang_xiang, build_root_relations, build_two_side, build_branch_tiers, build_tian_he, build_wuxing_power, build_power_network, build_spectrum_topology, build_spectrum_from_power, build_climate_candidates, build_climate_structure, build_special_patterns, build_yongshen_engine

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
net.setdefault('facts',{})['daymaster_element']='木'
sp = build_spectrum_topology(net,wp)
_spd = build_spectrum_from_power(wp,p)
sp['wang_shuai'] = _spd.get('wang_shuai')
sp['qiang_ruo'] = _spd.get('qiang_ruo')

print("=== L1016 直接检查sp ===")
print("spectrum (旧):", sp.get('spectrum'))
print("wang_shuai:", sp.get('wang_shuai'))
print("qiang_ruo:", sp.get('qiang_ruo'))
if sp.get('wang_shuai'):
    print("  wang_shuai.result:", sp['wang_shuai'].get('result'))
if sp.get('qiang_ruo'):
    print("  qiang_ruo.root_class:", sp['qiang_ruo'].get('root_class'))
    print("  qiang_ruo.has_root:", sp['qiang_ruo'].get('has_root'))
