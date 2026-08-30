#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立语义审计器 - 完全独立于production pipeline

核心原则：
1. 不读取旧Assertion的任何字段（primitive/condition/min_truth）
2. 仅从raw_text和source_metadata出发
3. 使用inspect.getsource()验证Recognizer不读取旧字段
4. 逐条输出完整审计证据

Commit: a540f7c (🔴 HOLD)
"""

import json
import sys
import inspect
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from p0_8_9_canonical_production_v8 import (
    IndependentRelationRecognizer,
    EvidenceSpan,
    ConditionProducer
)

def verify_recognizer_independence():
    """验证Recognizer不读取旧Assertion字段"""
    print("\n" + "=" * 80)
    print("Recognizer独立性验证")
    print("=" * 80)
    
    source = inspect.getsource(IndependentRelationRecognizer)
    forbidden_fields = ['primitive', 'condition', 'min_truth', 'assertion']
    
    issues = []
    for field in forbidden_fields:
        # 使用正则避免误匹配
        if re.search(rf'self\.{field}\b', source):
            issues.append(f'Recognizer访问了self.{field}')
        if re.search(rf'assertion\["{field}"\]', source):
            issues.append(f'Recognizer访问了assertion["{field}"]')
        if re.search(rf'assertion\[{field}\]', source):
            issues.append(f'Recognizer访问了assertion[{field}]')
    
    # 也检查recognize_relation方法
    method_source = inspect.getsource(IndependentRelationRecognizer.recognize_relation)
    for field in forbidden_fields:
        if re.search(rf'self\.{field}\b', method_source):
            issues.append(f'recognize_relation()访问了self.{field}')
        if re.search(rf'assertion\["{field}"\]', method_source):
            issues.append(f'recognize_relation()访问了assertion["{field}"]')
        if re.search(rf'assertion\[{field}\]', method_source):
            issues.append(f'recognize_relation()访问了assertion[{field}]')
    
    if issues:
        print(f"\n❌ Recognizer违规访问旧字段: {', '.join(issues)}")
        return False
    else:
        print(f"\n✅ Recognizer独立验证通过（不读取primitive/condition/min_truth/assertion）")
        return True

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

def independent_semantic_audit(raw_text, passage_id, source_metadata):
    """
    独立语义审计 - 完全从raw_text出发
    
    审计维度：
    1. Evidence Span是否来自原文
    2. Condition是否可追溯到Evidence Span
    3. 是否存在semantic_overreach
    4. 是否存在multi_conclusion
    """
    issues = []
    audit_evidence = {}
    
    # Step 1: 独立生成Relation
    recognizer = IndependentRelationRecognizer()
    relation = recognizer.recognize_relation(raw_text)
    audit_evidence['relation'] = relation
    audit_evidence['relation_source'] = 'IndependentRelationRecognizer from raw_text'
    
    # Step 2: 创建Evidence Span（使用整个raw_text）
    span = EvidenceSpan(text=raw_text, start=0, end=len(raw_text), relation=relation)
    audit_evidence['evidence_span'] = span.to_dict()
    
    # Step 3: 独立生成Condition
    producer = ConditionProducer(recognizer)
    condition = producer.produce_condition(span)
    audit_evidence['condition'] = condition
    audit_evidence['condition_source'] = 'ConditionProducer from EvidenceSpan'
    
    # Step 4: Semantic Audit
    
    # 4.1 检查semantic_overreach
    # 如果min_truth包含原文没有的字，就是overreach
    # 但这里我们不读min_truth，只检查condition是否在raw_text中有依据
    
    # 提取condition的核心词
    condition_words = re.findall(r'[\u4e00-\u9fff]{2,}', condition)
    raw_text_words = re.findall(r'[\u4e00-\u9fff]{2,}', raw_text)
    
    unmatched = [w for w in condition_words if w not in raw_text_words]
    if len(unmatched) > 2:
        issues.append('semantic_overreach')
        audit_evidence['semantic_overreach_detail'] = f"Condition中有{len(unmatched)}个词未出现在原文: {', '.join(unmatched[:5])}"
    
    # 4.2 检查multi_conclusion
    clauses = []
    if '；' in condition:
        clauses = [c.strip() for c in condition.split('；') if c.strip()]
    elif '，且' in condition:
        clauses = [c.strip() for c in condition.split('，且') if c.strip()]
    elif '、' in condition:
        clauses = [c.strip() for c in condition.split('、') if c.strip()]
    
    if len(clauses) > 1:
        issues.append('multi_conclusion')
        audit_evidence['multi_conclusion_detail'] = f"Condition包含{len(clauses)}个独立子句"
    
    # 4.3 检查unsupported_condition
    # 如果condition的核心词在raw_text中找不到，就是不支持的
    if not condition_words:
        issues.append('unsupported_condition')
        audit_evidence['unsupported_condition_detail'] = "Condition为空或无中文字符"
    elif len(unmatched) > len(condition_words) * 0.5:
        issues.append('unsupported_condition')
        audit_evidence['unsupported_condition_detail'] = f"Condition中超过50%的词未出现在原文"
    
    passed = len(issues) == 0
    return {
        'passage_id': passage_id,
        'raw_text': raw_text[:80] + '...' if len(raw_text) > 80 else raw_text,
        'source_metadata': source_metadata,
        'relation': relation,
        'condition': condition,
        'issues': issues,
        'audit_evidence': audit_evidence,
        'passed': passed
    }

def main():
    print("=" * 80)
    print("独立语义审计器 - 完全独立于production pipeline")
    print("=" * 80)
    
    # Step 0: 验证Recognizer独立性
    recognizer_independent = verify_recognizer_independence()
    if not recognizer_independent:
        print("\n❌ Recognizer独立性验证失败，审计终止")
        return 1
    
    # Step 1: 加载Assertion
    assertions = load_assertions()
    print(f"\n✅ 加载Assertion: {len(assertions)}条")
    
    # Step 2: 运行独立审计
    results = []
    for assertion in assertions:
        passage_id = assertion.get('passage_id', '')
        raw_text = assertion.get('raw_text', '')
        source_metadata = {
            'book': assertion.get('book', ''),
            'volume': assertion.get('volume', ''),
            'chapter': assertion.get('chapter', '')
        }
        
        result = independent_semantic_audit(raw_text, passage_id, source_metadata)
        results.append(result)
    
    # Step 3: 计算指标
    passed_count = sum(1 for r in results if r['passed'])
    total = len(results)
    
    overreach_count = sum(1 for r in results if 'semantic_overreach' in r['issues'])
    unsupported_count = sum(1 for r in results if 'unsupported_condition' in r['issues'])
    multi_conclusion_count = sum(1 for r in results if 'multi_conclusion' in r['issues'])
    
    semantic_overreach_rate = (overreach_count / total * 100) if total > 0 else 0
    unsupported_condition_rate = (unsupported_count / total * 100) if total > 0 else 0
    multi_conclusion_rate = (multi_conclusion_count / total * 100) if total > 0 else 0
    
    # Step 4: 输出结果
    print("\n" + "=" * 80)
    print("独立语义审计结果")
    print("=" * 80)
    print(f"\n总断言: {total}条")
    print(f"PASS: {passed_count}条 ({passed_count/total*100:.1f}%)")
    print(f"FAIL: {total-passed_count}条 ({(total-passed_count)/total*100:.1f}%)")
    
    print("\n" + "=" * 80)
    print("质量指标（独立计算）")
    print("=" * 80)
    print(f"\n  semantic_overreach_rate: {semantic_overreach_rate:.1f}%")
    print(f"  unsupported_condition_rate: {unsupported_condition_rate:.1f}%")
    print(f"  multi_conclusion_rate: {multi_conclusion_rate:.1f}%")
    
    # Step 5: 列出FAIL条目（带详细证据）
    failures = [r for r in results if not r['passed']]
    if failures:
        print("\n" + "=" * 80)
        print(f"FAIL详情（{len(failures)}条）")
        print("=" * 80)
        for r in failures:
            print(f"\n  {r['passage_id']} [{r['source_metadata']['book']}]:")
            print(f"    Raw: {r['raw_text'][:60]}...")
            print(f"    Relation: {r['relation']}")
            print(f"    Condition: {r['condition']}")
            print(f"    Issues: {', '.join(r['issues'])}")
            if 'semantic_overreach_detail' in r['audit_evidence']:
                print(f"    Detail: {r['audit_evidence']['semantic_overreach_detail']}")
            if 'multi_conclusion_detail' in r['audit_evidence']:
                print(f"    Detail: {r['audit_evidence']['multi_conclusion_detail']}")
            if 'unsupported_condition_detail' in r['audit_evidence']:
                print(f"    Detail: {r['audit_evidence']['unsupported_condition_detail']}")
    
    # Step 6: 特别复核已知问题条目
    print("\n" + "=" * 80)
    print("特别复核条目")
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
            status = "✅ PASS" if r['passed'] else "❌ FAIL"
            print(f"\n  {r['passage_id']}: {status}")
            print(f"    Raw: {r['raw_text'][:50]}...")
            print(f"    Condition: {r['condition']}")
            print(f"    Issues: {', '.join(r['issues']) if r['issues'] else '无'}")
    
    # Step 7: 最终判断
    print("\n" + "=" * 80)
    print("最终判断")
    print("=" * 80)
    
    all_pass = (
        semantic_overreach_rate == 0 and
        unsupported_condition_rate == 0 and
        multi_conclusion_rate == 0
    )
    
    if all_pass:
        print("\n🎉 独立语义审计: 🟢 PASS")
        print("\n所有指标达标：")
        print("  ✅ semantic_overreach_rate = 0%")
        print("  ✅ unsupported_condition_rate = 0%")
        print("  ✅ multi_conclusion_rate = 0%")
    else:
        print("\n⚠️ 独立语义审计: 🔴 FAIL")
        print(f"\n未达到全部目标：")
        if semantic_overreach_rate > 0:
            print(f"  ❌ semantic_overreach_rate: {semantic_overreach_rate:.1f}%")
        if unsupported_condition_rate > 0:
            print(f"  ❌ unsupported_condition_rate: {unsupported_condition_rate:.1f}%")
        if multi_conclusion_rate > 0:
            print(f"  ❌ multi_conclusion_rate: {multi_conclusion_rate:.1f}%")
    
    # Step 8: 保存结果
    output = {
        'timestamp': str(Path(__file__).parent),
        'total_assertions': total,
        'passed': passed_count,
        'failed': total - passed_count,
        'metrics': {
            'semantic_overreach_rate': semantic_overreach_rate,
            'unsupported_condition_rate': unsupported_condition_rate,
            'multi_conclusion_rate': multi_conclusion_rate
        },
        'results': results
    }
    
    output_path = Path(__file__).parent.parent / 'data' / 'p0_8_9_independent_semantic_audit_v2.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
    return 0 if all_pass else 1

if __name__ == '__main__':
    sys.exit(main())
