#!/usr/bin/env python3
"""Blind Evidence Architecture Audit - 盲派证据架构审计"""
import json
from pathlib import Path
from collections import defaultdict

evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence/blind_seg')
files = [f for f in evidence_dir.glob('E-BLIND-*.json') if '-fix-record' not in f.name]

print("=" * 80)
print("盲派 Evidence 架构审计 (Architecture Audit)")
print("=" * 80)

# 盲派原生理论结构
THEORY_STRUCTURE = {
    '理法': {
        '宾主': ['GUEST_HOST'],
        '体用': ['BODY_USE_RELATION'],
        '做功': {
            '结构': ['制用', '化用', '生用', '泄用', '合用', '墓用', '复合做功'],
            '机制': ['合', '冲', '刑', '克', '穿', '墓'],
            '结果': ['功神', '废神', '能量', '效率'],
            '特殊': ['贼神', '捕神']
        },
        '势党': ['POWER_PARTY'],
        '虚实': ['EMPTY_USELESS']
    },
    '象法': {
        '干支象': [],
        '宫位象': [],
        '十神象': [],
        '职业象': ['IMAGE']
    },
    '技法': {
        '应期': ['YING_QI'],
        '大运流年': [],
        '具体断法': []
    }
}

# 当前 Topic 映射
CURRENT_TOPICS = {
    'GUEST_HOST': '宾主',
    'BODY_USE_RELATION': '体用',
    'WORK_RELATION': '做功关系',
    'WORK_TYPE': '做功类型',
    'WORK_ACTOR': '做功主体',
    'WORK_TARGET': '做功目标',
    'WORK_EFFICIENCY': '做功效率',
    'POWER_PARTY': '势党',
    'EMPTY_USELESS': '虚实',
    'IMAGE': '象法',
    'YING_QI': '应期',
    'COMPLEX_WORK': '复合做功',
    'WORK_METHOD': '做功方式'
}

# 审计结果
audit_results = {
    'total': len(files),
    'by_topic': defaultdict(list),
    'issues': [],
    'misclassified': [],
    'doubtful_original': [],
    'layer_distribution': {'A': 0, 'B': 0, 'C': 0, 'D': 0},
    'theory_layer_distribution': defaultdict(lambda: defaultdict(int))
}

print(f"\n总证据数: {len(files)}")

# 逐条审计
for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    
    eid = data.get('evidence_id')
    topic = data.get('extraction_topic')
    layer = data.get('provenance_layer')
    fidelity = data.get('source_fidelity')
    text = data.get('original_text', '')
    
    audit_results['layer_distribution'][layer] += 1
    audit_results['by_topic'][topic].append(eid)
    
    # 理论层归属分析
    theory_layer = None
    if topic in ['GUEST_HOST', 'BODY_USE_RELATION', 'POWER_PARTY', 'EMPTY_USELESS']:
        theory_layer = '理法-结构'
    elif topic in ['WORK_RELATION', 'WORK_TYPE', 'WORK_METHOD', 'COMPLEX_WORK']:
        theory_layer = '理法-机制'
    elif topic in ['WORK_ACTOR', 'WORK_TARGET']:
        theory_layer = '理法-主体'
    elif topic in ['WORK_EFFICIENCY']:
        theory_layer = '理法-结果'
    elif topic in ['IMAGE']:
        theory_layer = '象法'
    elif topic in ['YING_QI']:
        theory_layer = '技法'
    else:
        theory_layer = '未分类'
    
    audit_results['theory_layer_distribution'][theory_layer][layer] += 1
    
    # 问题检测
    # 1. 疑似二次整理文本
    if len(text) > 100 and any(kw in text for kw in ['主要包括', '主要分为', '分别是', '第一种', '第二种']):
        audit_results['doubtful_original'].append({
            'id': eid,
            'topic': topic,
            'reason': '疑似二次整理文本（包含分类列举式表达）',
            'text_preview': text[:80] + '...'
        })
    
    # 2. DIRECT/HIGH 但长度异常
    if fidelity == 'DIRECT' and len(text) > 200:
        audit_results['issues'].append({
            'id': eid,
            'type': 'LENGTH_WARNING',
            'message': f'DIRECT/HIGH 但文本较长 ({len(text)}字)，需核验是否为逐字原文'
        })
    
    # 3. Topic 分类可疑
    if topic in ['WORK_METHOD', 'WORK_RELATION', 'WORK_TYPE']:
        # 这些 Topic 可能压扁了盲派的做功分层
        audit_results['issues'].append({
            'id': eid,
            'type': 'TOPIC_FLAT',
            'message': f'Topic [{topic}] 可能压扁了盲派做功理论的分层结构'
        })

# 输出审计结果
print("\n" + "=" * 80)
print("一、Layer 分布")
print("=" * 80)
for layer, count in sorted(audit_results['layer_distribution'].items()):
    print(f"   {layer}: {count}条 ({count*100//len(files)}%)")

print("\n" + "=" * 80)
print("二、理论层分布")
print("=" * 80)
for theory_layer, layers in sorted(audit_results['theory_layer_distribution'].items()):
    total = sum(layers.values())
    print(f"\n   {theory_layer}: {total}条")
    for layer, count in sorted(layers.items()):
        print(f"      {layer}: {count}")

print("\n" + "=" * 80)
print("三、Topic 分布")
print("=" * 80)
for topic, ids in sorted(audit_results['by_topic'].items()):
    print(f"   {topic}: {len(ids)}条")

print("\n" + "=" * 80)
print("四、问题检测")
print("=" * 80)

# 疑似二次整理文本
if audit_results['doubtful_original']:
    print(f"\n【疑似二次整理文本】({len(audit_results['doubtful_original'])}条):")
    for item in audit_results['doubtful_original'][:10]:  # 只显示前10条
        print(f"   ⚠️  {item['id']}")
        print(f"      原因: {item['reason']}")
        print(f"      预览: {item['text_preview'][:60]}...")

# TOPIC_FLAT 问题
flat_topics = [i for i in audit_results['issues'] if i['type'] == 'TOPIC_FLAT']
if flat_topics:
    print(f"\n【Topic 压扁问题】({len(flat_topics)}条):")
    print("   以下 Topic 可能将盲派做功理论的不同层次压平:")
    topics_found = set(i['message'].split('[')[1].split(']')[0] for i in flat_topics)
    for t in sorted(topics_found):
        print(f"      - {t}")

# LENGTH_WARNING
length_warnings = [i for i in audit_results['issues'] if i['type'] == 'LENGTH_WARNING']
print(f"\n【文本长度警告】({len(length_warnings)}条):")
print("   DIRECT/HIGH 但文本较长，需核验是否为逐字原文")

print("\n" + "=" * 80)
print("五、修正建议")
print("=" * 80)
print("""
1. WORK_METHOD / WORK_RELATION / WORK_TYPE 需要拆分:
   - WORK_METHOD → 拆分为 制用/化用/生用/泄用/合用/墓用 等
   - WORK_RELATION → 拆分为 合/冲/刑/克/穿/墓 等具体作用方式
   - WORK_TYPE → 可能需要重新定义或合并

2. 新增 Topic 建议:
   - GONG_SHEN (功神)
   - FEI_SHEN (废神)
   - ZEI_SHEN (贼神)
   - BU_SHEN (捕神)
   - ENERGY (能量)

3. 所有新扩充 Evidence:
   - 必须先确定理论层归属（理法/象法/技法）
   - 再确定具体层次（结构/机制/结果/特殊角色）
   - 确认原文为真实出处
   - 不得标 DIRECT/HIGH 除非完成文献核验
""")

print("=" * 80)
print("审计完成")
print("=" * 80)
