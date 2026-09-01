#!/usr/bin/env python3
"""盲派 Evidence 架构修正 - 按仲裁裁决执行"""
import json
from pathlib import Path
from datetime import datetime

evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence/blind_seg')

print("=" * 80)
print("盲派 Evidence 架构修正")
print("=" * 80)

# 1. 读取 manifest 获取当前状态
manifest = json.load(open(evidence_dir / 'manifest.json'))
print(f"\n当前 manifest total: {manifest['total_evidence']}")

# 2. 找出 WORK_METHOD/WORK_RELATION/WORK_TYPE 的证据
files = [f for f in evidence_dir.glob('E-BLIND-*.json') if '-fix-record' not in f.name]

issues = {
    'WORK_METHOD': [],
    'WORK_RELATION': [],
    'WORK_TYPE': []
}

for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    topic = data.get('extraction_topic')
    if topic in issues:
        issues[topic].append({
            'id': data.get('evidence_id'),
            'text': data.get('original_text', '')[:100],
            'layer': data.get('provenance_layer')
        })

print("\n【问题 Topic 分布】")
for topic, items in issues.items():
    print(f"  {topic}: {len(items)}条")
    for item in items[:3]:  # 显示前3条
        print(f"    - {item['id']}: {item['text'][:50]}...")

# 3. 建立新的 Topic taxonomy
NEW_TOPIC_TAXONOMY = {
    # 理法 - 结构层
    'GUEST_HOST': '宾主（理法-结构）',
    'BODY_USE_RELATION': '体用（理法-结构）',
    'POWER_PARTY': '势党（理法-结构）',
    'EMPTY_USELESS': '虚实（理法-结构）',
    
    # 理法 - 机制层（做功方式）
    'WORK_MERGE': '合做功（理法-机制）',
    'WORK grave': '墓做功（理法-机制）',
    'WORK_PUSH': '冲做功（理法-机制）',
    'WORK_PENETRATE': '穿做功（理法-机制）',
    'WORK_RESTRAINT': '制做功（理法-机制）',
    'WORK_TRANSFORM': '化做功（理法-机制）',
    'WORK_NOURISH': '生做功（理法-机制）',
    'WORK_DRAIN': '泄做功（理法-机制）',
    
    # 理法 - 结果层
    'WORK_EFFICIENCY': '做功效率（理法-结果）',
    'GONG_SHEN': '功神（理法-结果）',
    'FEI_SHEN': '废神（理法-结果）',
    'ENERGY': '能量（理法-结果）',
    
    # 理法 - 特殊角色
    'ZEI_SHEN': '贼神（理法-特殊）',
    'BU_SHEN': '捕神（理法-特殊）',
    
    # 理法 - 主体层
    'WORK_ACTOR': '做功主体（理法-主体）',
    'WORK_TARGET': '做功目标（理法-主体）',
    
    # 象法
    'IMAGE': '象法（象法）',
    
    # 技法
    'YING_QI': '应期（技法）',
    'COMPLEX_WORK': '复合做功（理法-机制）'
}

# 4. 创建修正记录
correction_log = {
    "correction_date": datetime.now().isoformat(),
    "reason": "盲派理论结构分层修正",
    "old_topics": ['WORK_METHOD', 'WORK_RELATION', 'WORK_TYPE'],
    "new_topics": list(NEW_TOPIC_TAXONOMY.keys()),
    "mapping": {
        "WORK_METHOD": "拆分为合/墓/冲/穿/制/化/生/泄做功",
        "WORK_RELATION": "拆分为合/墓/冲/穿等具体作用方式",
        "WORK_TYPE": "重新归类到做功机制或合并"
    },
    "status": "IN_PROGRESS"
}

with open(evidence_dir / 'topic_correction_log.json', 'w', encoding='utf-8') as f:
    json.dump(correction_log, f, ensure_ascii=False, indent=2)

print("\n✅ 主题修正日志已创建: topic_correction_log.json")
print("\n【新的 Topic Taxonomy】")
for topic, description in sorted(NEW_TOPIC_TAXONOMY.items()):
    print(f"   {topic}: {description}")

print("\n" + "=" * 80)
print("修正完成 - 等待进一步裁决")
print("=" * 80)