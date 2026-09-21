#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""过拟合审计脚本 - 扫描所有数值参数和规则条件"""
import os
import re

ENGINE_DIR = r'D:\shuntian-ziping-p0\engines\common'
SCRIPTS_DIR = r'D:\shuntian-ziping-p0\scripts'

# 1. 参数审计：扫描所有数值常量
print("="*80)
print("层次1：参数审计 - 数值常量扫描")
print("="*80)

param_patterns = [
    (r'([A-Z_]+)\s*=\s*(\d+\.\d+)\s*(?:#\s*(.*))?', '浮点常量'),
    (r'([A-Z_]+)\s*=\s*(\d+)\s*(?:#\s*(.*))?', '整数常量'),
]

all_params = []
for root, dirs, files in os.walk(ENGINE_DIR):
    for f in files:
        if f.endswith('.py') and not f.startswith('__'):
            fpath = os.path.join(root, f)
            with open(fpath, 'r', encoding='utf-8') as fh:
                for i, line in enumerate(fh, 1):
                    for pattern, ptype in param_patterns:
                        m = re.match(r'\s*' + pattern, line)
                        if m:
                            name, val, comment = m.group(1), m.group(2), m.group(3) or ''
                            # 过滤掉明显不是参数的（如状态码、版本号）
                            if name not in ('__', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
                                all_params.append({
                                    'file': f, 'line': i, 'name': name,
                                    'value': val, 'type': ptype, 'comment': comment
                                })

# 按文件分组
from collections import defaultdict
params_by_file = defaultdict(list)
for p in all_params:
    params_by_file[p['file']].append(p)

print(f"\n数值常量总数: {len(all_params)}")
print(f"涉及文件数: {len(params_by_file)}")
print()

# 重点关注：wuxing_power.py, yongshen_engine.py, dayun_xiji.py
focus_files = ['wuxing_power.py', 'yongshen_engine.py', 'dayun_xiji.py', 'bingyao_layer.py', 'special_pattern.py']
for f in focus_files:
    if f in params_by_file:
        print(f"\n--- {f} ({len(params_by_file[f])}个数值常量) ---")
        for p in params_by_file[f][:20]:  # 只显示前20个
            print(f"  L{p['line']}: {p['name']} = {p['value']} ({p['type']}) {p['comment']}")
        if len(params_by_file[f]) > 20:
            print(f"  ... 还有{len(params_by_file[f])-20}个")

# 2. 规则审计：扫描V5.x和V6.x版本标记
print("\n" + "="*80)
print("层次2：规则审计 - V5.x/V6.x版本标记扫描")
print("="*80)

version_pattern = r'V[56]\.\d+'
all_versions = []
for root, dirs, files in os.walk(ENGINE_DIR):
    for f in files:
        if f.endswith('.py'):
            fpath = os.path.join(root, f)
            with open(fpath, 'r', encoding='utf-8') as fh:
                content = fh.read()
                versions = re.findall(version_pattern, content)
                for v in set(versions):
                    count = versions.count(v)
                    all_versions.append({'file': f, 'version': v, 'count': count})

for root, dirs, files in os.walk(SCRIPTS_DIR):
    for f in files:
        if f.endswith('.py'):
            fpath = os.path.join(root, f)
            with open(fpath, 'r', encoding='utf-8') as fh:
                content = fh.read()
                versions = re.findall(version_pattern, content)
                for v in set(versions):
                    count = versions.count(v)
                    all_versions.append({'file': f'scripts/{f}', 'version': v, 'count': count})

versions_by_name = defaultdict(list)
for v in all_versions:
    versions_by_name[v['version']].append(v)

print(f"\n版本标记总数: {len(all_versions)}")
print(f"不同版本数: {len(versions_by_name)}")
print()

for vname in sorted(versions_by_name.keys()):
    items = versions_by_name[vname]
    total_count = sum(i['count'] for i in items)
    files = ', '.join(set(i['file'] for i in items))
    print(f"  {vname}: {total_count}处, 文件: {files}")

# 3. 评分加权审计：扫描ratio/score/weight等关键词
print("\n" + "="*80)
print("层次3：评分加权审计 - ratio/score/weight关键词扫描")
print("="*80)

score_keywords = ['ratio', 'score', 'weight', '加权', '评分', '阈值', 'threshold']
score_findings = []
for root, dirs, files in os.walk(ENGINE_DIR):
    for f in files:
        if f.endswith('.py'):
            fpath = os.path.join(root, f)
            with open(fpath, 'r', encoding='utf-8') as fh:
                for i, line in enumerate(fh, 1):
                    for kw in score_keywords:
                        if kw.lower() in line.lower() and not line.strip().startswith('#'):
                            score_findings.append({'file': f, 'line': i, 'keyword': kw, 'text': line.strip()[:100]})

print(f"\n评分加权关键词命中: {len(score_findings)}处")
print()

# 重点关注：非注释的ratio/score计算
for sf in score_findings[:30]:
    print(f"  {sf['file']} L{sf['line']} [{sf['keyword']}]: {sf['text']}")
if len(score_findings) > 30:
    print(f"  ... 还有{len(score_findings)-30}处")

# 4. 案例层审计：DTS案例使用方式
print("\n" + "="*80)
print("层次4：案例层审计 - DTS案例使用方式")
print("="*80)

# 统计dayun_align.py中DTS案例数量
dts_file = os.path.join(SCRIPTS_DIR, 'dayun_align.py')
if os.path.exists(dts_file):
    with open(dts_file, 'r', encoding='utf-8') as fh:
        content = fh.read()
        # 查找案例加载逻辑
        if 'DTS' in content or '滴天髓' in content:
            print("  dayun_align.py使用DTS案例")
        # 查找案例总数
        total_matches = re.findall(r'(\d+)\s*例', content)
        if total_matches:
            print(f"  案例数量提及: {', '.join(total_matches[:10])}")

print("\n  DTS案例被用于:")
print("    - 调参（V5.1-V6.6各版本）")
print("    - 验证（每次修改后跑全量）")
print("    - 无独立验证集/测试集")

print("\n" + "="*80)
print("审计总结")
print("="*80)
print(f"  数值常量总数: {len(all_params)}")
print(f"  版本标记总数: {len(all_versions)}")
print(f"  评分加权关键词命中: {len(score_findings)}处")
print(f"  DTS案例: 被反复用于调参，无独立验证集")
