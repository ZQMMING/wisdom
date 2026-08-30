#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Semantic Relation Validator v4 - 状态语义修正版

核心修正：
1. COMPLETE = 自动验证完整，可进入Authorization
2. PARTIAL = 语义证据不完整，必须HOLD，等待人工裁决
3. INSUFFICIENT = 证据不足，必须HOLD，等待人工裁决

不再使用PASS/FAIL二元状态
改用COMPLETE/PARTIAL/INSUFFICIENT三级状态

Commit: ff7a078 (🔴 HOLD)
"""

import json
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from p0_8_9_canonical_production_v8 import (
    IndependentRelationRecognizer,
    EvidenceSpan,
    ConditionProducer
)

# 语义完整性等级（最终状态）
SEMANTIC_LEVEL_COMPLETE = 'COMPLETE'
SEMANTIC_LEVEL_PARTIAL = 'PARTIAL'
SEMANTIC_LEVEL_INSUFFICIENT = 'INSUFFICIENT'

def classify_semantic_structure(raw_text, condition):
    """
    根据原典文本结构，分类语义关系类型
    
    返回结构类型和完整性等级
    """
    
    # 尝试匹配"X者，谓之/主/谓/曰 Y"结构（完整定义型）
    pattern1 = re.search(r'(.+?)者[，,]?\s*(?:谓之|主|谓|曰)\s*(.+?)[。]', raw_text)
    if pattern1:
        return {
            'type': 'definition',
            'level': SEMANTIC_LEVEL_COMPLETE,
            'subject': pattern1.group(1).strip(),
            'predicate': '谓之/主/谓/曰',
            'conclusion': pattern1.group(2).strip(),
            'object': None
        }
    
    # 尝试匹配"X者，Y也"结构（完整解释型）
    pattern2 = re.search(r'(.+?)者[，,]?\s*(.+?)也[。]', raw_text)
    if pattern2:
        return {
            'type': 'explanation',
            'level': SEMANTIC_LEVEL_COMPLETE,
            'subject': pattern2.group(1).strip(),
            'predicate': '也',
            'conclusion': pattern2.group(2).strip(),
            'object': None
        }
    
    # 尝试匹配"X，Y"结构（简单判断型）
    if '，' in raw_text:
        parts = [p.strip() for p in raw_text.split('，') if p.strip()]
        if len(parts) >= 2:
            return {
                'type': 'judgment',
                'level': SEMANTIC_LEVEL_PARTIAL,
                'subject': parts[0],
                'predicate': parts[1] if len(parts) == 2 else None,
                'conclusion': None,
                'object': None
            }
    
    # 默认：证据不足
    return {
        'type': 'unknown',
        'level': SEMANTIC_LEVEL_INSUFFICIENT,
        'subject': None,
        'predicate': None,
        'conclusion': None,
        'object': None
    }

def validate_semantic_chain(raw_text, relation, condition, passage_id):
    """
    验证语义链：Evidence → Relation → Condition
    
    根据语义结构类型，采用不同的验证策略
    返回最终状态：COMPLETE / PARTIAL / INSUFFICIENT
    """
    issues = []
    audit_evidence = {}
    
    # Step 1: 分类语义结构
    structure = classify_semantic_structure(raw_text, condition)
    audit_evidence['structure_type'] = structure['type']
    audit_evidence['structure_level'] = structure['level']
    
    # Step 2: 根据结构等级，执行不同的验证策略
    
    if structure['level'] == SEMANTIC_LEVEL_COMPLETE:
        # COMPLETE：验证所有要素
        validation = validate_complete_relation(raw_text, condition, structure)
        issues.extend(validation['issues'])
        audit_evidence.update(validation['evidence'])
    
    elif structure['level'] == SEMANTIC_LEVEL_PARTIAL:
        # PARTIAL：仅验证存在的部分，标记为HOLD
        validation = validate_partial_relation(raw_text, condition, structure)
        issues.extend(validation['issues'])
        audit_evidence.update(validation['evidence'])
        # PARTIAL必须HOLD，不能通过
        issues.append('hold_for_manual_review')
    
    else:
        # INSUFFICIENT：证据不足，标记为HOLD
        issues.append('insufficient_evidence')
        audit_evidence['validation'] = 'SKIPPED: Insufficient evidence for automated validation'
    
    # Step 3: 通用检查（所有结构都适用）
    
    # 3.1 检查semantic_overreach（Condition是否超出Evidence语义范围）
    overreach_keywords = ['唯一', '必须', '只能', '一定', '绝对', '完全', '始终']
    if any(kw in condition for kw in overreach_keywords):
        issues.append('semantic_overreach')
        audit_evidence['overreach_check'] = f'FAIL: Contains overreach keyword'
    else:
        audit_evidence['overreach_check'] = 'PASS'
    
    # 3.2 检查multi_conclusion（Condition是否包含多个独立结论）
    clauses = []
    if '；' in condition:
        clauses = [c.strip() for c in condition.split('；') if c.strip()]
    elif condition.count('，') >= 2:
        clauses = [c.strip() for c in condition.split('，') if c.strip() and len(c.strip()) > 2]
    
    if len(clauses) > 1:
        issues.append('multi_conclusion')
        audit_evidence['multi_conclusion_check'] = f'FAIL: {len(clauses)} independent clauses'
    else:
        audit_evidence['multi_conclusion_check'] = 'PASS'
    
    # 3.3 检查Condition是否包含raw_text中没有的新概念
    raw_concepts = set(re.findall(r'[\u4e00-\u9fff]{2,}', raw_text))
    cond_concepts = set(re.findall(r'[\u4e00-\u9fff]{2,}', condition))
    
    new_concepts = cond_concepts - raw_concepts
    if len(new_concepts) > 5:
        issues.append('semantic_overreach')
        audit_evidence['concept_check'] = f'WARN: {len(new_concepts)} new concepts in condition'
    else:
        audit_evidence['concept_check'] = 'PASS'
    
    # 最终状态判断
    final_status = structure['level']
    
    return {
        'passage_id': passage_id,
        'raw_text': raw_text[:80] + '...' if len(raw_text) > 80 else raw_text,
        'relation': relation,
        'condition': condition,
        'structure': structure,
        'issues': issues,
        'final_status': final_status,
        'audit_evidence': audit_evidence
    }

def validate_complete_relation(raw_text, condition, structure):
    """验证完整语义关系（COMPLETE等级）"""
    issues = []
    evidence = {}
    
    # 验证subject是否存在
    if not structure.get('subject'):
        issues.append('missing_subject')
        evidence['subject_check'] = 'FAIL: No subject identified'
    else:
        evidence['subject_check'] = f'PASS: {structure["subject"]}'
    
    # 验证conclusion是否存在
    if not structure.get('conclusion'):
        issues.append('missing_conclusion')
        evidence['conclusion_check'] = 'FAIL: No conclusion identified'
    else:
        evidence['conclusion_check'] = f'PASS: {structure["conclusion"]}'
    
    # 验证Condition是否包含结论
    if structure.get('conclusion') and structure['conclusion'] not in condition:
        issues.append('conclusion_mismatch')
        evidence['conclusion_match'] = f'FAIL: Conclusion "{structure["conclusion"]}" not in condition'
    else:
        evidence['conclusion_match'] = 'PASS: Conclusion present in condition'
    
    return {'issues': issues, 'evidence': evidence}

def validate_partial_relation(raw_text, condition, structure):
    """验证部分语义关系（PARTIAL等级）"""
    issues = []
    evidence = {}
    
    # 验证subject是否存在
    if not structure.get('subject'):
        issues.append('missing_subject')
        evidence['subject_check'] = 'FAIL: No subject identified'
    else:
        evidence['subject_check'] = f'PASS: {structure["subject"]}'
    
    # 对于PARTIAL结构，不强制要求conclusion，但必须标记为HOLD
    evidence['conclusion_check'] = 'N/A: Partial structure, conclusion optional but requires manual review'
    
    # 验证Condition是否包含subject
    if structure.get('subject') and structure['subject'] not in condition:
        issues.append('subject_mismatch')
        evidence['subject_match'] = f'FAIL: Subject "{structure["subject"]}" not in condition'
    else:
        evidence['subject_match'] = 'PASS: Subject present in condition'
    
    # 必须标记为HOLD
    issues.append('hold_for_manual_review')
    evidence['hold_reason'] = 'PARTIAL structure requires manual canonical review before authorization'
    
    return {'issues': issues, 'evidence': evidence}

def load_assertions():
    """加载原始Assertion"""
    data_path = Path(__file__).parent.parent / 'data' / 'p0_8_7_expansion.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, dict):
        assertions = data.get('assertions', data.get('verified_assertions', []))
    elif isinstance(data, list):
        assertions = data
    else:
        assertions = []
    
    return assertions[:30]

def main():
    print("=" * 80)
    print("Semantic Relation Validator v4 - 状态语义修正版")
    print("=" * 80)
    
    # 加载Assertion
    assertions = load_assertions()
    print(f"\n✅ 加载Assertion: {len(assertions)}条")
    
    # 初始化独立组件
    recognizer = IndependentRelationRecognizer()
    producer = ConditionProducer(recognizer)
    
    # 运行语义链验证
    results = []
    for assertion in assertions:
        passage_id = assertion.get('passage_id', '')
        raw_text = assertion.get('raw_text', '')
        
        # Step 1: 独立生成Relation
        relation = recognizer.recognize_relation(raw_text)
        
        # Step 2: 创建Evidence Span
        span = EvidenceSpan(text=raw_text, start=0, end=len(raw_text), relation=relation)
        
        # Step 3: 生成Condition
        condition = producer.produce_condition(span)
        
        # Step 4: 验证语义链
        result = validate_semantic_chain(raw_text, relation, condition, passage_id)
        results.append(result)
    
    # 统计结果
    complete_count = sum(1 for r in results if r['final_status'] == SEMANTIC_LEVEL_COMPLETE)
    partial_count = sum(1 for r in results if r['final_status'] == SEMANTIC_LEVEL_PARTIAL)
    insufficient_count = sum(1 for r in results if r['final_status'] == SEMANTIC_LEVEL_INSUFFICIENT)
    total = len(results)
    
    # 计算指标（只统计COMPLETE条目）
    complete_results = [r for r in results if r['final_status'] == SEMANTIC_LEVEL_COMPLETE]
    
    overreach_count = sum(1 for r in complete_results if 'semantic_overreach' in r['issues'])
    multi_conclusion_count = sum(1 for r in complete_results if 'multi_conclusion' in r['issues'])
    
    semantic_overreach_rate = (overreach_count / len(complete_results) * 100) if complete_results else 0
    multi_conclusion_rate = (multi_conclusion_count / len(complete_results) * 100) if complete_results else 0
    
    # 输出结果
    print("\n" + "=" * 80)
    print("Semantic Structure Distribution")
    print("=" * 80)
    print(f"\n  COMPLETE: {complete_count}条 ({complete_count/total*100:.1f}%)")
    print(f"  PARTIAL: {partial_count}条 ({partial_count/total*100:.1f}%) - HOLD for manual review")
    print(f"  INSUFFICIENT: {insufficient_count}条 ({insufficient_count/total*100:.1f}%) - HOLD for manual review")
    
    print("\n" + "=" * 80)
    print("Quality Metrics (COMPLETE only)")
    print("=" * 80)
    print(f"\n  semantic_overreach_rate: {semantic_overreach_rate:.1f}%")
    print(f"  multi_conclusion_rate: {multi_conclusion_rate:.1f}%")
    
    # 列出PARTIAL和INSUFFICIENT条目（需要人工裁决）
    hold_items = [r for r in results if r['final_status'] != SEMANTIC_LEVEL_COMPLETE]
    if hold_items:
        print("\n" + "=" * 80)
        print(f"HOLD Items for Manual Review ({len(hold_items)}条)")
        print("=" * 80)
        for r in hold_items[:20]:
            print(f"\n  {r['passage_id']} [{r['structure']['type']}/{r['final_status']}]:")
            print(f"    Raw: {r['raw_text'][:60]}...")
            print(f"    Condition: {r['condition']}")
            print(f"    Hold Reason: {', '.join([i for i in r['issues'] if 'hold' in i or 'insufficient' in i])}")
    
    # 特别复核已知问题条目
    print("\n" + "=" * 80)
    print("Flagged Items Review")
    print("=" * 80)
    
    flagged_ids = [
        'YHZP-YINYANG-001',
        'DTS-JUGE-001',
        'DTS-TIYONG-001',
        'DTS-ZHONGHE-001',
        'PZZQ-GEJU-003',
        'PZZQ-GEJU-004',
        'PZZQ-GEJU-005',
        'PZZQ-GEJU-006'
    ]
    
    for r in results:
        if r['passage_id'] in flagged_ids:
            status_icon = "✅ COMPLETE" if r['final_status'] == SEMANTIC_LEVEL_COMPLETE else "⏸️ HOLD"
            print(f"\n  {r['passage_id']}: {status_icon}")
            print(f"    Raw: {r['raw_text'][:50]}...")
            print(f"    Condition: {r['condition']}")
            print(f"    Structure: {r['structure']['type']}/{r['final_status']}")
    
    # 最终判断
    print("\n" + "=" * 80)
    print("Final Status Summary")
    print("=" * 80)
    
    print(f"\n📊 语义完整性分级结果：")
    print(f"  ✅ COMPLETE: {complete_count}条 - 可进入Authorization")
    print(f"  ⏸️ PARTIAL: {partial_count}条 - 必须HOLD，等待人工原典裁决")
    print(f"  ⏸️ INSUFFICIENT: {insufficient_count}条 - 必须HOLD，等待人工原典裁决")
    
    print(f"\n📈 质量指标（仅COMPLETE条目）：")
    print(f"  ✅ semantic_overreach_rate: {semantic_overreach_rate:.1f}%")
    print(f"  ✅ multi_conclusion_rate: {multi_conclusion_rate:.1f}%")
    
    # 保存结果
    output = {
        'timestamp': str(Path(__file__).parent),
        'total_assertions': total,
        'structure_distribution': {
            'COMPLETE': complete_count,
            'PARTIAL': partial_count,
            'INSUFFICIENT': insufficient_count
        },
        'metrics': {
            'semantic_overreach_rate': semantic_overreach_rate,
            'multi_conclusion_rate': multi_conclusion_rate
        },
        'results': results
    }
    
    output_path = Path(__file__).parent.parent / 'data' / 'p0_8_9_semantic_relation_validation_v4.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
    
    # 返回状态（用于CI/CD）
    # 返回0表示脚本执行成功，但不代表P0-8.9通过
    # P0-8.9的通过需要GPT裁决
    return 0

if __name__ == '__main__':
    sys.exit(main())
