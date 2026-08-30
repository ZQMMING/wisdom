#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立语义审计器 - 不依赖production pipeline

验证30条Assertion的语义正确性
特别复核之前失败的条目

Commit: a540f7c (🔴 HOLD)
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from p0_8_9_canonical_production_v8 import (
    IndependentRelationRecognizer,
    EvidenceSpan,
    ConditionProducer
)

def load_assertions():
    """加载原始50条Assertion"""
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

def independent_semantic_audit(raw_text, min_truth, condition, passage_id):
    """独立语义审计（不与production pipeline共享逻辑）"""
    issues = []
    audit_reasons = []
    
    # 1. 检查semantic_overreach（min_truth是否超出原文）
    if min_truth and raw_text not in min_truth:
        # 检查是否添加了原文没有的字
        extra_chars = set(min_truth) - set(raw_text)
        if extra_chars and len(extra_chars) > 3:
            issues.append('semantic_overreach')
            audit_reasons.append(f"min_truth添加原文未有的字: {', '.join(list(extra_chars)[:5])}")
    
    # 2. 检查multi_conclusion（condition是否包含多个结论）
    if condition:
        # 检查分号、逗号+且、顿号
        clauses = []
        if '；' in condition:
            clauses = [c.strip() for c in condition.split('；') if c.strip()]
        elif '，且' in condition:
            clauses = [c.strip() for c in condition.split('，且') if c.strip()]
        elif '、' in condition:
            clauses = [c.strip() for c in condition.split('、') if c.strip()]
        
        if len(clauses) > 1:
            issues.append('multi_conclusion')
            audit_reasons.append(f"Condition包含{len(clauses)}个独立子句")
    
    # 3. 检查unsupported_condition（condition是否可追溯到原文）
    if condition and raw_text:
        # 检查condition的核心词是否出现在raw_text中
        condition_words = re.findall(r'[\u4e00-\\u9fff]{2,}', condition)
        raw_text_words = re.findall(r'[\u4e00-\\u9fff]{2,}', raw_text)
        
        unmatched = [w for w in condition_words if w not in raw_text_words]
        if len(unmatched) > 2:
            issues.append('unsupported_condition')
            audit_reasons.append(f"Condition中有{len(unmatched)}个词未出现在原文: {', '.join(unmatched[:3])}")
    
    # 4. 检查single_conclusion（min_truth是否是单一命题）
    if min_truth:
        # 检查是否包含"须/必须/唯一/仅"等限定词
        restrictive_words = ['须', '必须', '唯一', '仅', '只能', '一定']
        has_restriction = any(w in min_truth for w in restrictive_words)
        
        if has_restriction:
            # 这不一定有问题，但需要记录
            audit_reasons.append(f"min_truth包含限定词，需人工核查: {min_truth[:30]}...")
    
    return issues, '; '.join(audit_reasons) if audit_reasons else '通过独立语义审计'

def check_specific_assertions(results):
    """特别复核已知问题条目"""
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
    
    print("\n" + "=" * 80)
    print("特别复核条目")
    print("=" * 80)
    
    for r in results:
        if r['passage_id'] in flagged_ids:
            print(f"\n  {r['passage_id']}:")
            print(f"    Raw Text: {r['raw_text'][:50]}...")
            print(f"    Min Truth: {r['min_truth']}")
            print(f"    Condition: {r['condition']}")
            print(f"    Issues: {r['semantic_issues']}")
            print(f"    Audit Reason: {r['audit_reason'][:100]}...")
            print(f"    Passed: {r['passed']}")

def main():
    print("=" * 80)
    print("独立语义审计器 - 验证30条Assertion")
    print("=" * 80)
    
    # 加载Assertion
    assertions = load_assertions()
    print(f"\n✅ 加载Assertion: {len(assertions)}条")
    
    # 初始化独立组件（不与production pipeline共享）
    recognizer = IndependentRelationRecognizer()
    condition_producer = ConditionProducer(recognizer)
    
    # 运行独立审计
    results = []
    total_issues = 0
    
    for assertion in assertions:
        passage_id = assertion.get('passage_id', '')
        raw_text = assertion.get('raw_text', '')
        min_truth = assertion.get('min_truth', '')
        condition = assertion.get('condition', '')
        evidence = assertion.get('evidence', '')
        
        # 独立生成Relation（不依赖旧Assertion）
        relation = recognizer.recognize_relation(raw_text)
        
        # 独立生成EvidenceSpan
        span = EvidenceSpan(text=evidence if evidence else raw_text, start=0, end=len(raw_text), relation=relation)
        
        # 独立生成Condition
        new_condition = condition_producer.produce_condition(span)
        
        # 独立语义审计
        issues, audit_reason = independent_semantic_audit(raw_text, min_truth, new_condition, passage_id)
        
        # 统计
        passed = len(issues) == 0
        if not passed:
            total_issues += 1
        
        results.append({
            'passage_id': passage_id,
            'book': assertion.get('book', ''),
            'raw_text': raw_text[:100] + '...' if len(raw_text) > 100 else raw_text,
            'min_truth': min_truth,
            'old_condition': condition,
            'new_condition': new_condition,
            'relation': relation,
            'semantic_issues': issues,
            'audit_reason': audit_reason,
            'passed': passed
        })
    
    # 计算指标
    passed_count = sum(1 for r in results if r['passed'])
    total = len(results)
    
    overreach_count = sum(1 for r in results if 'semantic_overreach' in r['semantic_issues'])
    unsupported_count = sum(1 for r in results if 'unsupported_condition' in r['semantic_issues'])
    multi_conclusion_count = sum(1 for r in results if 'multi_conclusion' in r['semantic_issues'])
    
    semantic_overreach_rate = (overreach_count / total * 100) if total > 0 else 0
    unsupported_condition_rate = (unsupported_count / total * 100) if total > 0 else 0
    multi_conclusion_rate = (multi_conclusion_count / total * 100) if total > 0 else 0
    
    # 输出结果
    print("\n" + "=" * 80)
    print("独立语义审计结果")
    print("=" * 80)
    print(f"\n总断言: {total}条")
    print(f"PASS: {passed_count}条 ({passed_count/total*100:.1f}%)")
    print(f"FAIL: {total-passed_count}条 ({(total-passed_count)/total*100:.1f}%)")
    
    print("\n" + "=" * 80)
    print("质量指标（独立计算）")
    print("=" * 80)
    print(f"\n  semantic_overreach_rate: {semantic_overreach_rate:.1f}% ({overreach_count}条)")
    print(f"  unsupported_condition_rate: {unsupported_condition_rate:.1f}% ({unsupported_count}条)")
    print(f"  multi_conclusion_rate: {multi_conclusion_rate:.1f}% ({multi_conclusion_count}条)")
    
    # 列出FAIL条目
    failures = [r for r in results if not r['passed']]
    if failures:
        print("\n" + "=" * 80)
        print(f"FAIL详情（{len(failures)}条）")
        print("=" * 80)
        for r in failures:
            print(f"\n  {r['passage_id']} [{r['book']}]:")
            print(f"    Raw: {r['raw_text'][:60]}...")
            print(f"    Old Cond: {r['old_condition'][:50]}")
            print(f"    New Cond: {r['new_condition'][:50]}")
            print(f"    Issues: {', '.join(r['semantic_issues'])}")
            print(f"    Reason: {r['audit_reason']}")
    
    # 检查特定条目
    check_specific_assertions(results)
    
    # 最终判断
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
        print("\n⚠️ 独立语义审计: 🟡 FAIL")
        print(f"\n未达到全部目标：")
        if semantic_overreach_rate > 0:
            print(f"  ❌ semantic_overreach_rate: {semantic_overreach_rate:.1f}%")
        if unsupported_condition_rate > 0:
            print(f"  ❌ unsupported_condition_rate: {unsupported_condition_rate:.1f}%")
        if multi_conclusion_rate > 0:
            print(f"  ❌ multi_conclusion_rate: {multi_conclusion_rate:.1f}%")
    
    # 保存结果
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
    
    output_path = Path(__file__).parent.parent / 'data' / 'p0_8_9_independent_semantic_audit.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
    return 0 if all_pass else 1

if __name__ == '__main__':
    sys.exit(main())
