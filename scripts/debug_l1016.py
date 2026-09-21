import sys
sys.path.insert(0, 'scripts')
from dayun_align import engine, cases

for li, fp, dy, txt in cases:
    if li+1 == 1016:
        p, f, ye, tp0 = engine(fp)
        sp = tp0.get('spectrum_topology', {})
        print("=== L1016 ===")
        print("fp type:", type(fp))
        print("fp:", fp)
        print("tier:", ye.get('spectrum_tier'))
        print("wang_shuai:", sp.get('wang_shuai'))
        print("qiang_ruo:", sp.get('qiang_ruo'))
        print("spectrum:", sp.get('spectrum'))
        break
