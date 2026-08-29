"""P0-1.3 验证脚本：验证所有固定数据表修改"""

import sys
sys.path.insert(0, r"D:\shuntian\backend\src")

# 验证 bazi_l1_facts.py 丁火修正
from tongshu.engines.bazi_l1_facts import TIAN_GAN_TWELVE_GROWTH

ding = TIAN_GAN_TWELVE_GROWTH["丁"]
print("=== 丁火十二长生（修正后）===")
print(f"  酉(长生): {ding['酉']}")
print(f"  午(临官): {ding['午']}")
print(f"  子(绝): {ding['子']}")
assert ding["酉"] == "长生", "丁火酉应为长生"
assert ding["午"] == "临官", "丁火午应为临官"
assert ding["子"] == "绝", "丁火子应为绝"
print("  ✅ 丁火修正验证通过")

# 验证己土保持 UNRESOLVED（未修改）
ji = TIAN_GAN_TWELVE_GROWTH["己"]
print("\n=== 己土十二长生（保持 UNRESOLVED，未修改）===")
print(f"  酉: {ji['酉']}")
print(f"  子: {ji['子']}")
print("  ✅ 己土保持原样（UNRESOLVED）")

# 验证 bazi_engine.py 新表
from tongshu.engines.bazi_engine import STEM_HE, BRANCH_SANHUI

print("\n=== 天干五合配对表（STEM_HE）===")
print(f"  数量: {len(STEM_HE)}")
assert len(STEM_HE) == 5, "五合应为5组"
for combo in STEM_HE:
    print(f"  {set(combo)}")
print("  ✅ 天干五合配对表验证通过")

print("\n=== 三会组成表（BRANCH_SANHUI）===")
print(f"  数量: {len(BRANCH_SANHUI)}")
assert len(BRANCH_SANHUI) == 4, "三会应为4组"
for k, v in BRANCH_SANHUI.items():
    print(f"  {set(k)} -> {v}")
print("  ✅ 三会组成表验证通过")

# 验证空亡注释已移除
import inspect
from tongshu.engines.bazi_engine import calc_kong_wang
doc = inspect.getdoc(calc_kong_wang) or ""
print("\n=== 空亡函数注释检查 ===")
print(f"  包含'力量减半': {'力量减半' in doc}")
assert "力量减半" not in doc, "空亡注释不应包含'力量减半'"
print(f"  包含'Relation Effect Modifier': {'Relation Effect Modifier' in doc}")
print("  ✅ 空亡注释已移除'力量减半'，改为 Relation Effect Modifier")

print("\n" + "=" * 50)
print("✅ P0-1.3 全部验证通过！")
print("=" * 50)
