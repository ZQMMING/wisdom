# -*- coding: utf-8 -*-
"""全量baseline专旺格/从格新旧数量对比"""
import sys
import io
import json
sys.path.insert(0, r'D:\shuntian-ziping-p0')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from engines.common.unified_overview import build_unified_overview

# 读取baseline
with open(r'D:\shuntian-ziping-p0\baseline_special_20260922.json', 'r', encoding='utf-8') as f:
    baseline = json.load(f)

print(f"=== baseline总数: {len(baseline)}条 ===\n")

# 统计旧格局分布
old_pattern_count = {}
for case in baseline:
    special = case.get('special', '未知')
    old_pattern_count[special] = old_pattern_count.get(special, 0) + 1

print("=== 旧格局分布（baseline快照） ===")
for pat, cnt in sorted(old_pattern_count.items(), key=lambda x: -x[1]):
    print(f"  {pat}: {cnt}条")

# 跑新引擎，统计新格局分布
new_pattern_count = {}
new_zhuanwang_count = 0
new_cong_count = 0
errors = 0

def parse_key(key):
    gz_list = [key[i:i+2] for i in range(0, len(key), 2)]
    return {
        'year': list(gz_list[0]),
        'month': list(gz_list[1]),
        'day': list(gz_list[2]),
        'hour': list(gz_list[3])
    }

print(f"\n=== 跑新引擎（{len(baseline)}条） ===")

for i, case in enumerate(baseline):
    if i % 100 == 0:
        print(f"  进度: {i}/{len(baseline)}")
    
    try:
        pillars = parse_key(case['key'])
        result = build_unified_overview(pillars)
        special = result.get('special_pattern', {})
        
        zw = special.get('zhuanwang')
        patterns = [p['name'] for p in special.get('patterns', [])]
        
        # 统计专旺格
        if zw:
            new_zhuanwang_count += 1
            new_pattern_count[zw] = new_pattern_count.get(zw, 0) + 1
        else:
            # 统计从格
            for p in patterns:
                if '从' in p:
                    new_cong_count += 1
                    new_pattern_count[p] = new_pattern_count.get(p, 0) + 1
                    break
            else:
                # 其他格局
                for p in patterns:
                    new_pattern_count[p] = new_pattern_count.get(p, 0) + 1
                    break
                else:
                    new_pattern_count['正格'] = new_pattern_count.get('正格', 0) + 1
    except Exception as e:
        errors += 1
        new_pattern_count['ERROR'] = new_pattern_count.get('ERROR', 0) + 1

print(f"  完成: {len(baseline)}/{len(baseline)}")
print(f"  错误: {errors}条\n")

print("=== 新格局分布（新引擎） ===")
for pat, cnt in sorted(new_pattern_count.items(), key=lambda x: -x[1]):
    print(f"  {pat}: {cnt}条")

# 对比
print("\n=== 新旧对比（专旺格） ===")
old_zw_total = sum(cnt for pat, cnt in old_pattern_count.items() if any(x in pat for x in ['曲直', '炎上', '稼穑', '润下', '从革', '化']))
new_zw_total = new_zhuanwang_count
print(f"  旧专旺格总数（含化气格）: {old_zw_total}条")
print(f"  新专旺格总数: {new_zw_total}条")
print(f"  变化: {new_zw_total - old_zw_total:+d}条")

print("\n=== 新旧对比（从格） ===")
old_cong_total = sum(cnt for pat, cnt in old_pattern_count.items() if '从' in pat)
new_cong_total = new_cong_count
print(f"  旧从格总数: {old_cong_total}条")
print(f"  新从格总数: {new_cong_total}条")
print(f"  变化: {new_cong_total - old_cong_total:+d}条")

print("\n=== 假设校验 ===")
print(f"  假设1: 专旺格数量上升 → {'✅ 通过' if new_zw_total >= old_zw_total else '❌ 未通过'}")
print(f"  假设2: 从格数量下降 → {'✅ 通过' if new_cong_total <= old_cong_total else '❌ 未通过'}")
