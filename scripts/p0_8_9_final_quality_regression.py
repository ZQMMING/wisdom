#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P0-8.9 Final Quality Regression Test

完整质量回归：
30 Assertions → Canonical Evidence → Independent Relation → Primitive → Condition → Semantic Audit → Independent Truth → Authorization

目标指标：
- unsupported_condition_rate = 0
- semantic_overreach_rate = 0
- multi_conclusion_rate = 0
- source_traceability = 100%

Commit: 4a57109 (P0-8.9 Independence Validation PASS)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from p0_8_9_canonical_production_v8 import (
    CanonicalAssertionProducer,
    EvidenceSpan
)

def load_assertions():
    """加载原始50条Assertion（从p0_8_7_expansion.json）"""
    data_path = Path(__file__).parent.parent / 'data' / 'p0_8_7_expansion.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, dict):
        assertions = data.get('assertions', data.get('verified_assertions', []))
    elif isinstance(data, list):
        assertions = data
    else:
        assertions = []
    
    return assertions[:30]  # 取前30条进行质量回归

def validate_semantic_audit(assertion, relation, condition):
    """验证Semantic Audit状态"""
    issues = []
    
    raw_text = assertion.get('raw_text', '')
    min_truth = assertion.get('min_truth', '')
    
    # 检查是否超出原文内容（semantic_overreach）
    if min_truth and raw_text not in min_truth and len(min_truth) > len(raw_text) * 1.2:
        issues.append('semantic_overreach')
    
    # 检查多个结论
    if condition and ('；' in condition or '，且' in condition or '、' in condition):
        conclusion_count = len([p for p in condition.split('；') if p.strip()]) + len([p for p in condition.split(',') if p.strip()])
        if conclusion_count > 1:
            issues.append('multi_conclusion')
    
    # 检查条件是否可追溯
    if condition and not any(e in condition for e in raw_text[:50]):
        if not any(word in condition for word in ['五行', '天干', '地支', '相生', '相克', '六合', '六冲']):
            issues.append('unsupported_condition')
    
    return issues

def validate_independent_truth(assertion):
    """验证Independent Truth状态"""
    issues = []
    
    passage_id = assertion.get('passage_id', '')
    min_truth = assertion.get('min_truth', '')
    
    # 检查最小命题是否独立
    if '仅' in min_truth or '唯一' in min_truth or '必须' in min_truth:
        issues.append('single_conclusion')
    
    # 检查是否可以追溯到原典
    if not passage_id.startswith(('YHZP-', 'QTBJ-', 'PZZQ-', 'SMTH-', 'DTS-')):
        issues.append('independent_source')
    
    return issues

def main():
    print("=" * 80)
    print("P0-8.9 Final Quality Regression Test")
    print("完整质量回归：30 Assertions")
    print("=" * 80)
    
    # 加载Assertion
    assertions = load_assertions()
    print(f"\n✅ 加载Assertion: {len(assertions)}条")
    
    # 初始化Pipeline组件
    producer = CanonicalAssertionProducer()
    
    # 运行质量审核
    results = []
    total_semantic_issues = 0
    total_condition_issues = 0
    total_multi_conclusion = 0
    total_source_issues = 0
    
    for assertion in assertions:
        passage_id = assertion.get('passage_id', '')
        raw_text = assertion.get('raw_text', '')
        
        # Step 1: Canonical Evidence（已包含在Assertion中）
        evidence = assertion.get('evidence', '')
        
        # Step 2: Evidence Span
        span = EvidenceSpan(text=evidence if evidence else raw_text, start=0, end=len(raw_text))
        
        # Step 3: Condition Production（使用内嵌producer）
        relation = span.relation
        condition = producer.producer.produce_condition(span)
        
        # Step 4: Primitive Generation（从Relation生成，不依赖旧Assertion）
        primitive = producer._generate_primitive_from_relation(relation)
        
        # Step 5: Semantic Audit
        semantic_issues = validate_semantic_audit(assertion, relation, condition)
        
        # Step 6: Independent Truth Validation
        truth_issues = validate_independent_truth(assertion)
        
        # 统计问题
        has_overreach = 'semantic_overreach' in semantic_issues
        has_multi_conclusion = 'multi_conclusion' in semantic_issues
        has_unsupported = 'unsupported_condition' in semantic_issues
        has_source_issue = 'independent_source' in truth_issues
        
        if has_overreach:
            total_semantic_issues += 1
        if has_multi_conclusion:
            total_multi_conclusion += 1
        if has_unsupported:
            total_condition_issues += 1
        if has_source_issue:
            total_source_issues += 1
        
        results.append({
            'passage_id': passage_id,
            'relation': relation,
            'primitive': primitive,
            'condition': condition,
            'semantic_issues': semantic_issues,
            'truth_issues': truth_issues,
            'passed': len(semantic_issues) == 0 and len(truth_issues) == 0
        })
    
    # 计算质量指标
    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    
    semantic_overreach_rate = (total_semantic_issues / total * 100) if total > 0 else 0
    unsupported_condition_rate = (total_condition_issues / total * 100) if total > 0 else 0
    multi_conclusion_rate = (total_multi_conclusion / total * 100) if total > 0 else 0
    source_traceability_rate = ((total - total_source_issues) / total * 100) if total > 0 else 0
    
    # 输出结果
    print("\n" + "=" * 80)
    print("质量指标汇总")
    print("=" * 80)
    print(f"\n总断言: {total}条")
    print(f"PASS: {passed}条 ({passed/total*100:.1f}%)")
    print(f"FAIL: {total-passed}条 ({(total-passed)/total*100:.1f}%)")
    
    print("\n" + "=" * 80)
    print("详细质量指标")
    print("=" * 80)
    print(f"\n  semantic_overreach_rate: {semantic_overreach_rate:.1f}%")
    print(f"  unsupported_condition_rate: {unsupported_condition_rate:.1f}%")
    print(f"  multi_conclusion_rate: {multi_conclusion_rate:.1f}%")
    print(f"  source_traceability_rate: {source_traceability_rate:.1f}%")
    
    # 找出有问题的Assertion
    failures = [r for r in results if not r['passed']]
    if failures:
        print("\n" + "=" * 80)
        print(f"FAIL详情（{len(failures)}条）")
        print("=" * 80)
        for r in failures[:10]:
            print(f"\n  {r['passage_id']}:")
            if r['semantic_issues']:
                print(f"    Semantic Issues: {', '.join(r['semantic_issues'])}")
            if r['truth_issues']:
                print(f"    Truth Issues: {', '.join(r['truth_issues'])}")
    
    # 最终判断
    print("\n" + "=" * 80)
    print("最终判断")
    print("=" * 80)
    
    all_pass = (
        semantic_overreach_rate == 0 and
        unsupported_condition_rate == 0 and
        multi_conclusion_rate == 0 and
        source_traceability_rate == 100.0
    )
    
    if all_pass:
        print("\n🎉 P0-8.9 FINAL QUALITY REGRESSION: 🟢 PASS")
        print("\n所有质量指标达到目标：")
        print("  ✅ semantic_overreach_rate = 0%")
        print("  ✅ unsupported_condition_rate = 0%")
        print("  ✅ multi_conclusion_rate = 0%")
        print("  ✅ source_traceability_rate = 100%")
    else:
        print("\n⚠️ P0-8.9 FINAL QUALITY REGRESSION: 🟡 PARTIAL")
        print(f"\n未达到全部目标：")
        if semantic_overreach_rate > 0:
            print(f"  ❌ semantic_overreach_rate: {semantic_overreach_rate:.1f}%")
        if unsupported_condition_rate > 0:
            print(f"  ❌ unsupported_condition_rate: {unsupported_condition_rate:.1f}%")
        if multi_conclusion_rate > 0:
            print(f"  ❌ multi_conclusion_rate: {multi_conclusion_rate:.1f}%")
        if source_traceability_rate < 100.0:
            print(f"  ❌ source_traceability_rate: {source_traceability_rate:.1f}%")
    
    # 保存结果
    output = {
        'timestamp': str(Path(__file__).parent),
        'total_assertions': total,
        'passed': passed,
        'failed': total - passed,
        'metrics': {
            'semantic_overreach_rate': semantic_overreach_rate,
            'unsupported_condition_rate': unsupported_condition_rate,
            'multi_conclusion_rate': multi_conclusion_rate,
            'source_traceability_rate': source_traceability_rate
        },
        'results': results
    }
    
    output_path = Path(__file__).parent.parent / 'data' / 'p0_8_9_final_quality_regression.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
    return 0 if all_pass else 1

if __name__ == '__main__':
    sys.exit(main())
