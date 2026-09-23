import sys
sys.path.insert(0, '.')
from spec.root_qi import STEM_WUXING
from engines.cong_ge_gates import _tou_gan, SHISHEN_CLASSES

stems = ["戊", "壬", "甲", "己"]
day_wx = "木"

print("天干:", stems)
print("比劫类:", SHISHEN_CLASSES[day_wx]["比"])
print("比劫透干?", _tou_gan(stems, day_wx, "比"))
print("印类:", SHISHEN_CLASSES[day_wx]["印"])
print("印透干?", _tou_gan(stems, day_wx, "印"))

# 天干五行
for s in stems:
    print(f"  {s} -> {STEM_WUXING[s]}")
