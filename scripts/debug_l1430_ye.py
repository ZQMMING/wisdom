import sys
sys.path.insert(0, 'scripts')
from dayun_align import engine

fp = [('丙','寅'),('辛','卯'),('癸','酉'),('戊','午')]
p, f, ye, tp0 = engine(fp)

print("=== L1430 yongshen_engine ===")
print("primary:", ye.get('primary'))
print("secondary:", ye.get('secondary'))
print("avoid:", ye.get('avoid'))
print("paths:", ye.get('paths'))
print("spectrum_tier:", ye.get('spectrum_tier'))
print("spectrum_tier2:", ye.get('spectrum_tier2'))
print("special:", ye.get('special'))
if ye.get('notes'):
    for k, v in ye['notes'].items():
        print(f"  notes[{k}]: {v}")
