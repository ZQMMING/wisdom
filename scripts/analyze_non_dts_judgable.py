#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统计非DTS案例可判率和不可判原因"""
import sys; sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('dayun_align_mod', 'scripts/dayun_align.py')
mod = importlib.util.module_from_spec(spec)
import unittest.mock
with unittest.mock.patch('sys.argv', ['dayun_align.py']):
    try: spec.loader.exec_module(mod)
    except SystemExit: pass

cases = mod.cases
luck_verdict = mod.luck_verdict

# 分离DTS和非DTS案例
dts_cases = []
non_dts_cases = []
for li, fp, dy, txt in cases:
    # DTS案例的特征：li编号或txt包含"滴天髓"
    if '滴天髓' in txt or '任铁樵' in txt or li < 1000:
        dts_cases.append((li, fp, dy, txt))
    else:
        non_dts_cases.append((li, fp, dy, txt))

print(f"DTS案例: {len(dts_cases)}")
print(f"非DTS案例: {len(non_dts_cases)}")
print()

# 统计非DTS可判率
non_dts_total = 0
non_dts_judgable = 0
non_dts_unjudgable = []

for li, fp, dy, txt in non_dts_cases:
    if len(dy) < 4: continue
    for gz in dy:
        g, z = gz[0], gz[1]
        non_dts_total += 1
        v, blob = luck_verdict(txt, g, z)
        if v and v not in ('hun', 'lao'):
            non_dts_judgable += 1
        else:
            non_dts_unjudgable.append((li, gz, v, blob[:80] if blob else '无匹配'))

print(f"非DTS大运总数: {non_dts_total}")
print(f"非DTS可判: {non_dts_judgable} ({non_dts_judgable/non_dts_total*100:.1f}%)")
print(f"非DTS不可判: {len(non_dts_unjudgable)} ({len(non_dts_unjudgable)/non_dts_total*100:.1f}%)")
print()

# 分析不可判原因
print("=== 不可判案例样本（前20）===")
for li, gz, v, blob in non_dts_unjudgable[:20]:
    print(f"  L{li} {gz}: v={v}, blob={blob}")

# 统计不可判原因
no_match = sum(1 for _, _, v, _ in non_dts_unjudgable if v is None)
hun = sum(1 for _, _, v, _ in non_dts_unjudgable if v == 'hun')
lao = sum(1 for _, _, v, _ in non_dts_unjudgable if v == 'lao')
print()
print(f"无匹配: {no_match}")
print(f"混合(吉凶共存): {hun}")
print(f"归隐安乐: {lao}")

# 看看无匹配案例的断语格式
print()
print("=== 无匹配案例断语样本（前10）===")
for li, gz, v, blob in non_dts_unjudgable[:10]:
    if v is None:
        # 找到该案例的完整断语
        for li2, fp2, dy2, txt2 in non_dts_cases:
            if li2 == li:
                # 显示包含大运干支附近的文本
                import re
                g, z = gz[0], gz[1]
                # 查找大运干支在文本中的位置
                idx = txt2.find(g+z)
                if idx == -1:
                    idx = txt2.find(g+'运')
                if idx == -1:
                    idx = txt2.find(z+'运')
                if idx >= 0:
                    start = max(0, idx-50)
                    end = min(len(txt2), idx+100)
                    print(f"  L{li} {gz}: ...{txt2[start:end]}...")
                else:
                    print(f"  L{li} {gz}: 文本中未找到{g}{z}/{g}运/{z}运")
                    print(f"    文本前200字: {txt2[:200]}")
                break
