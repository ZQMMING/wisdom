import sys
sys.path.insert(0, '.')
from spec.root_qi import calc_root_qi, shi

# F4+: 戊寅 戊午 庚辰 己未
# 庚日主，地支寅午辰未
root_qi = calc_root_qi("庚", ["寅", "午", "辰", "未"], ["戊", "戊", "庚", "己"])
print(f"F4+ root_qi(庚): {root_qi}")

# 印比势（土）
tu_shi = shi(["寅", "午", "辰", "未"], ["戊", "戊", "庚", "己"], "土", "午")
print(f"F4+ 土势: {tu_shi:.2f}")

# 比劫势（金）
jin_shi = shi(["寅", "午", "辰", "未"], ["戊", "戊", "庚", "己"], "金", "午")
print(f"F4+ 金势: {jin_shi:.2f}")
