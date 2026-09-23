import sys
sys.path.insert(0, '.')
from engines.cong_ge_gates import _tou_gan, SHISHEN_CLASSES

stems = ["庚", "辛", "壬", "辛"]
day_wx = "木"  # 甲日主

print("天干:", stems)
print("印类:", SHISHEN_CLASSES[day_wx]["印"])
print("印透干?", _tou_gan(stems, day_wx, "印"))
print("比劫类:", SHISHEN_CLASSES[day_wx]["比"])
print("比劫透干?", _tou_gan(stems, day_wx, "比"))
print("食伤类:", SHISHEN_CLASSES[day_wx]["食伤"])
print("食伤透干?", _tou_gan(stems, day_wx, "食伤"))
