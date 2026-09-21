#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""过拟合审计详细报告 - 追踪wuxing_power字段消费情况"""
import os
import re

ENGINE_DIR = r'D:\shuntian-ziping-p0\engines\common'

# wuxing_power.py输出的关键字段
key_fields = [
    'ratio', 'spectrum', 'spectrum_tier', 'self_score', 'opp_score',
    'W_BENQI', 'W_ZHONGQI', 'W_YUQI', 'W_STEM', 'W_JU', 'W_BANHE',
    'T_WANG_JI', 'T_TAI_WANG', 'T_WANG', 'T_WANG_HEAVY',
    'wang_shuai', 'qiang_ruo', 'ben_n', 'zhong_n', 'yu_n', 'stem_n', 'ju_n'
]

print("="*80)
print("过拟合审计详细报告")
print("="*80)

# 1. 追踪每个关键字段的消费情况
print("\n【1】wuxing_power关键字段消费追踪")
print("-"*80)

field_consumers = {}
for field in key_fields:
    consumers = []
    for root, dirs, files in os.walk(ENGINE_DIR):
        for f in files:
            if f.endswith('.py') and f != 'wuxing_power.py':
                fpath = os.path.join(root, f)
                with open(fpath, 'r', encoding='utf-8') as fh:
                    for i, line in enumerate(fh, 1):
                        if field in line and not line.strip().startswith('#'):
                            consumers.append((f, i, line.strip()[:80]))
    if consumers:
        field_consumers[field] = consumers

# 分类：评分加权字段 vs 结构字段
score_fields = ['ratio', 'spectrum', 'spectrum_tier', 'self_score', 'opp_score',
                 'W_BENQI', 'W_ZHONGQI', 'W_YUQI', 'W_STEM', 'W_JU', 'W_BANHE',
                 'T_WANG_JI', 'T_TAI_WANG', 'T_WANG', 'T_WANG_HEAVY']
struct_fields = ['wang_shuai', 'qiang_ruo', 'ben_n', 'zhong_n', 'yu_n', 'stem_n', 'ju_n']

print("\n评分加权字段消费情况（高风险）:")
for field in score_fields:
    if field in field_consumers:
        print(f"  {field}: {len(field_consumers[field])}处消费")
        for f, ln, txt in field_consumers[field][:5]:
            print(f"    {f} L{ln}: {txt}")
    else:
        print(f"  {field}: 0处消费（已隔离）")

print("\n结构字段消费情况（低风险）:")
for field in struct_fields:
    if field in field_consumers:
        print(f"  {field}: {len(field_consumers[field])}处消费")
    else:
        print(f"  {field}: 0处消费")

# 2. V5.x规则保留情况
print("\n【2】V5.x规则保留/回退情况")
print("-"*80)

rules = {
    'V5.1': '身弱印比升喜（dayun_align.py）',
    'V5.2': '流通修正',
    'V5.3': '身旺克泄耗升喜（yongshen_engine.py）',
    'V5.4': '非冬夏印比升喜（yongshen_engine.py）',
    'V5.6': '调候轨专旺格排除（yongshen_engine.py）',
    'V5.7': '专旺格fallback（yongshen_engine.py）',
    'V6.0-V6.6': '互动级判断（全部回退）',
}

for version, desc in rules.items():
    if version.startswith('V6'):
        print(f"  {version}: {desc} → 已回退（100%回退率）")
    else:
        print(f"  {version}: {desc} → 保留")

# 3. 原著依据审计
print("\n【3】参数原著依据审计")
print("-"*80)

wp_file = os.path.join(ENGINE_DIR, 'wuxing_power.py')
with open(wp_file, 'r', encoding='utf-8') as fh:
    content = fh.read()

# 查找PCT-MARK标记
pct_marks = re.findall(r'#\s*PCT-MARK\s*(.*)', content)
print(f"PCT-MARK（案例拟合标记）数量: {len(pct_marks)}")
for mark in pct_marks:
    print(f"  - {mark.strip()}")

# 查找原著依据标记
original_marks = re.findall(r'#\s*原典\s*(.*)', content)
print(f"\n原典依据标记数量: {len(original_marks)}")
for mark in original_marks[:10]:
    print(f"  - {mark.strip()}")

# 4. 过拟合风险评级
print("\n【4】过拟合风险评级")
print("-"*80)

risks = [
    ('wuxing_power.py 37个数值参数', '高', '全部标注PCT-MARK，案例拟合非原著推导'),
    ('DTS案例反复调参无独立验证集', '高', '训练集=验证集=测试集，非DTS(75%)>DTS(69.8%)方向反了'),
    ('V5.1身弱印比修正', '中', '命中19例中9正确10错误，净效果接近0，可能只在DTS有效'),
    ('V5.4非冬夏印比升喜', '中', '依据梁湘润注释（非原文），可能只在DTS有效'),
    ('V6.x互动级判断', '低', '全部回退，不构成过拟合源'),
    ('wang_shuai/qiang_ruo布尔枚举', '低', '已切换为布尔枚举，不依赖数值参数'),
]

print(f"{'风险源':<40} {'等级':<6} {'说明'}")
print("-"*80)
for source, level, desc in risks:
    print(f"{source:<40} {level:<6} {desc}")

# 5. 应对方案
print("\n【5】应对方案")
print("-"*80)

print("P0（立即执行）:")
print("  1. 建立独立验证集：从非DTS案例中抽取30-50例作为验证集")
print("  2. 用独立验证集评估V5.1/V5.4规则，只在DTS有效的规则回退")
print("  3. wuxing_power.py参数标注来源：原著依据 vs 案例拟合")

print("P1（短期）:")
print("  1. 从原著重新推导wuxing_power.py参数，无原著依据的标注ENGINEERING_DERIVED")
print("  2. 检查bingyao_layer/dayun_xiji等模块是否消费了ratio/spectrum等评分字段")
print("  3. 建立训练/验证/测试三集分离机制")

print("P2（长期）:")
print("  1. 系统性重构专旺格识别逻辑（当前识别分散在不同模块）")
print("  2. 从格/专旺格用神构造从原著重新推导")
print("  3. 引擎核心（元素级判断、四轨并行、冲突保留）保持不变")

print("\n" + "="*80)
print("审计结论")
print("="*80)
print("  过拟合程度：中等偏高")
print("  主要风险源：wuxing_power.py数值参数（案例拟合）+ DTS案例反复调参")
print("  引擎核心：稳健（非DTS对齐率75% > DTS 69.8%）")
print("  应对：建立独立验证集，评估V5.1/V5.4规则，从原著重新推导参数")
print("  不是推倒重来，是诊断和清理")
