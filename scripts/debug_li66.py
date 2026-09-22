# -*- coding: utf-8 -*-
"""调试li=66：查看中间量"""
import sys
import io
sys.path.insert(0, r'D:\shuntian-ziping-p0')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from engines.common.unified_overview import build_unified_overview

# li=66: 庚申乙酉庚戌庚辰
pillars = {
    'year': ['庚', '申'],
    'month': ['乙', '酉'],
    'day': ['庚', '戌'],
    'hour': ['庚', '辰']
}

result = build_unified_overview(pillars)

print("=== li=66 调试信息 ===\n")

# 1. 基本信息
panxi = result.get('panxi', {})
print(f"日主: {panxi.get('day_stem')}")
print(f"日主五行: {panxi.get('daymaster_element')}")
print(f"月支: {panxi.get('month_branch')}")

# 2. facts
facts = result.get('facts', {})
print(f"\n=== facts ===")
print(f"daymaster_element: {facts.get('daymaster_element')}")
print(f"hidden_stems: {facts.get('hidden_stems')}")

# 3. wuxing_power
wpo = result.get('wuxing_power', {})
print(f"\n=== wuxing_power ===")
for wx in ['金', '木', '水', '火', '土']:
    pw = wpo.get(wx, {})
    print(f"  {wx}: ben_n={pw.get('ben_n')}, stem_n={pw.get('stem_n')}, ju_n={pw.get('ju_n')}, ling_state={pw.get('ling_state')}")

# 4. tian_he
th = result.get('tian_he', {})
print(f"\n=== tian_he ===")
print(f"he_pairs: {th.get('he_pairs', [])}")

# 5. special_pattern
special = result.get('special_pattern', {})
print(f"\n=== special_pattern ===")
print(f"zhuanwang: {special.get('zhuanwang')}")
print(f"zhuanwang_state: {special.get('zhuanwang_state')}")
print(f"_gate_debug: {special.get('_gate_debug', [])}")
print(f"patterns: {[p['name'] for p in special.get('patterns', [])]}")

# 6. 看看专旺格判定的前置条件
# dm_ben_eff >= 1 and not _yin_wang_not_zw
# 让我手动计算一下
pw = wpo
dm_wx = facts.get('daymaster_element')
dm = pw.get(dm_wx, {})
print(f"\n=== 专旺格前置条件 ===")
print(f"dm_wx: {dm_wx}")
print(f"dm.ben_n: {dm.get('ben_n')}")
print(f"dm.stem_n: {dm.get('stem_n')}")
print(f"dm.ju_n: {dm.get('ju_n')}")

# 印星
yin_wx = {'木': '水', '火': '木', '土': '火', '金': '土', '水': '金'}.get(dm_wx)
yin = pw.get(yin_wx, {})
print(f"yin_wx: {yin_wx}")
print(f"yin.ben_n: {yin.get('ben_n')}")

# party = dm_ben_eff + yin_ben_eff + dm.get('banhe_n', 0)
print(f"dm.banhe_n: {dm.get('banhe_n')}")
print(f"party ≈ {dm.get('ben_n', 0) + yin.get('ben_n', 0) + dm.get('banhe_n', 0)}")
