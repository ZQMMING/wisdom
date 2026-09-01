#!/usr/bin/env python3
"""盲派 Evidence 逐条架构重分类矩阵"""
import json
import re
from pathlib import Path
from datetime import datetime

# 使用项目根目录
project_dir = Path('C:/Users/wisdom/wisdom')
evidence_dir = project_dir / 'data/evidence/blind_seg'

print("=" * 80)
print("盲派 Evidence 逐条架构重分类矩阵")
print("=" * 80)

# 盲派原生理论结构定义
THEORY_STRUCTURE = {
    # 理法 - 结构层
    '理法-结构': {
        'GUEST_HOST': '宾主',
        'BODY_USE_RELATION': '体用',
        'POWER_PARTY': '势党',
        'EMPTY_USELESS': '虚实'
    },
    # 理法 - 机制层（做功方式）
    '理法-机制': {
        '合做功': ['合', '六合', '三合'],
        '墓做功': ['墓', '入墓', '出库'],
        '冲做功': ['冲', '六冲'],
        '穿做功': ['穿', '相穿'],
        '制做功': ['制', '官杀制劫财'],
        '化做功': ['化', '通关'],
        '生做功': ['生', '印绶生日主'],
        '泄做功': ['泄', '食伤泄秀'],
        '复合做功': ['复合', '多种']
    },
    # 理法 - 结果层
    '理法-结果': {
        '功神': ['功神', '有用'],
        '废神': ['废神', '无用'],
        '能量': ['能量', '有力', '无力'],
        '效率': ['效率', '层次']
    },
    # 理法 - 特殊角色
    '理法-特殊': {
        '贼神': ['贼神', '忌神'],
        '捕神': ['捕神', '用神']
    },
    # 理法 - 主体层
    '理法-主体': {
        '做功主体': ['做功主体', '日主', '月令'],
        '做功目标': ['做功目标', '功靶']
    },
    # 象法
    '象法': {
        '干支象': ['干支象', '象'],
        '宫位象': ['宫位象', '宫位'],
        '十神象': ['十神象', '十神'],
        '职业象': ['职业', '行业', '类象']
    },
    # 技法
    '技法': {
        '应期': ['应期', '运到'],
        '大运流年': ['大运', '流年'],
        '具体断法': ['断法', '实战']
    }
}

# 现有 Topic 到理论层的映射
TOPIC_TO_LAYER = {
    'GUEST_HOST': '理法-结构',
    'BODY_USE_RELATION': '理法-结构',
    'POWER_PARTY': '理法-结构',
    'EMPTY_USELESS': '理法-结构',
    'WORK_METHOD': '理法-机制',  # 需要拆分
    'WORK_RELATION': '理法-机制',  # 需要拆分
    'WORK_TYPE': '理法-机制',  # 需要拆分
    'COMPLEX_WORK': '理法-机制',
    'WORK_EFFICIENCY': '理法-结果',
    'WORK_ACTOR': '理法-主体',
    'WORK_TARGET': '理法-主体',
    'IMAGE': '象法',
    'YING_QI': '技法'
}

# 逐条审计结果
reclassification_matrix = []

# 读取所有 Evidence
files = [f for f in evidence_dir.glob('E-BLIND-*.json') if '-fix-record' not in f.name]
print(f"\n总证据数: {len(files)}")

for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    
    eid = data.get('evidence_id')
    topic = data.get('extraction_topic', 'Unknown')
    layer = data.get('provenance_layer', 'Unknown')
    fidelity = data.get('source_fidelity', 'UNKNOWN')
    text = data.get('original_text', '')
    
    # 判断理论层
    theory_layer = TOPIC_TO_LAYER.get(topic, '未分类')
    
    # 判断盲派概念
    blind_concept = None
    concept_layer = None
    
    # 检查是否属于做功机制
    if any(kw in text for kw in ['合', '墓', '冲', '穿', '制', '化', '生', '泄']):
        if '合' in text:
            blind_concept = '合做功'
            concept_layer = '理法-机制'
        elif '墓' in text:
            blind_concept = '墓做功'
            concept_layer = '理法-机制'
        elif '冲' in text:
            blind_concept = '冲做功'
            concept_layer = '理法-机制'
        elif '穿' in text:
            blind_concept = '穿做功'
            concept_layer = '理法-机制'
        elif '制' in text:
            blind_concept = '制做功'
            concept_layer = '理法-机制'
        elif '化' in text:
            blind_concept = '化做功'
            concept_layer = '理法-机制'
        elif '生' in text:
            blind_concept = '生做功'
            concept_layer = '理法-机制'
        elif '泄' in text:
            blind_concept = '泄做功'
            concept_layer = '理法-机制'
    
    # 检查工作主体/目标
    if topic in ['WORK_ACTOR']:
        blind_concept = '做功主体'
        concept_layer = '理法-主体'
    elif topic in ['WORK_TARGET']:
        blind_concept = '做功目标'
        concept_layer = '理法-主体'
    
    # 检查结果层
    if topic in ['WORK_EFFICIENCY']:
        blind_concept = '效率'
        concept_layer = '理法-结果'
    
    # 判断分类状态
    classification_status = 'OK'
    reclassification_required = False
    reason = ''
    
    # 检查是否需要重分类
    if topic in ['WORK_METHOD', 'WORK_RELATION', 'WORK_TYPE']:
        classification_status = 'NEEDS_SPLIT'
        reclassification_required = True
        reason = f'Topic [{topic}] 需要拆分为具体做功方式（合/墓/冲/穿/制/化/生/泄）'
    elif theory_layer != concept_layer and concept_layer:
        classification_status = 'MISMATCH'
        reclassification_required = True
        reason = f'Topic理论层({theory_layer})与实际概念层({concept_layer})不一致'
    elif fidelity == 'DIRECT' and len(text) > 150:
        classification_status = 'PENDING_VERIFICATION'
        reclassification_required = False
        reason = '文本较长，需核验是否为逐字原文'
    
    # 来源验证状态
    source_verification_status = 'UNVERIFIED'
    if fidelity == 'PENDING_VERIFICATION':
        source_verification_status = 'PENDING'
    elif fidelity == 'DIRECT':
        source_verification_status = 'CLAIMED_DIRECT'
    
    reclassification_matrix.append({
        'evidence_id': eid,
        'current_topic': topic,
        'provenance_layer': layer,
        'theory_layer': theory_layer,
        'blind_concept': blind_concept or '未识别',
        'concept_layer': concept_layer or '未识别',
        'classification_status': classification_status,
        'source_verification_status': source_verification_status,
        'reclassification_required': reclassification_required,
        'reason': reason,
        'text_length': len(text),
        'original_text_preview': text[:80] + '...' if len(text) > 80 else text
    })

# 统计结果
print("\n【统计结果】")
status_counts = {}
for item in reclassification_matrix:
    status = item['classification_status']
    status_counts[status] = status_counts.get(status, 0) + 1

for status, count in sorted(status_counts.items()):
    print(f"   {status}: {count}条")

print(f"\n需要重分类: {sum(1 for i in reclassification_matrix if i['reclassification_required'])}条")
print(f"来源待核验: {sum(1 for i in reclassification_matrix if i['source_verification_status'] == 'PENDING')}条")

# 输出需要重分类的明细
print("\n【需要重分类的证据】")
for item in reclassification_matrix:
    if item['reclassification_required']:
        print(f"   ⚠️  {item['evidence_id']}")
        print(f"      Topic: {item['current_topic']} → {item['reason']}")

# 保存矩阵
output_file = evidence_dir / 'reclassification_matrix.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'generated_at': datetime.now().isoformat(),
        'total_evidence': len(reclassification_matrix),
        'matrix': reclassification_matrix,
        'summary': {
            'needs_reclassification': sum(1 for i in reclassification_matrix if i['reclassification_required']),
            'pending_verification': sum(1 for i in reclassification_matrix if i['source_verification_status'] == 'PENDING'),
            'by_status': status_counts
        }
    }, f, ensure_ascii=False, indent=2)

print(f"\n✅ 重分类矩阵已保存: {output_file.name}")