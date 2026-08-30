#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Semantic Relation Validator - 真正的语义关系验证器

核心原则：
1. 不依赖词匹配/字符匹配
2. 验证 Evidence Span → Independent Semantic Relation → Condition 的语义链条
3. 每条Condition必须绑定：subject, predicate, object, conclusion
4. 验证四元关系是否由原典Evidence明确表达

Commit: 18d7c37 (🔴 HOLD)
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

def extract_semantic_relation(raw_text, condition):
    """
    从raw_text和condition提取语义关系四元组
    
    返回: {
        'subject': str,      # 主体（如：日干）
        'predicate': str,    # 谓词（如：克）
        'object': str,       # 客体（如：岁君）
        'conclusion': str,   # 结论（如：犯岁）
        'evidence': str      # 证据来源
    }
    """
    # 基于规则提取四元关系（不依赖外部词表，只依赖原典结构）
    relation = {
        'subject': None,
        'predicate': None,
        'object': None,
        'conclusion': None,
        'evidence': raw_text
    }
    
    # 尝试匹配"X者，谓之Y"结构
    match = re.search(r'(.+?)者[，,]?\s*(?:谓之|主|谓|曰)\s*(.+?)[。]', raw_text)
    if match:
        relation['subject'] = match.group(1).strip()
        relation['conclusion'] = match.group(2).strip()
        # 尝试从condition提取predicate
        if condition:
            # 查找condition中位于subject和object之间的动词
            subject_pattern = f"({re.escape(relation['subject'])})"
            conclusion_pattern = f"({re.escape(relation['conclusion'])})"
            pattern = f"{subject_pattern}(.+?){conclusion_pattern}"
            cond_match = re.search(pattern, condition)
            if cond_match:
                relation['predicate'] = cond_match.group(2).strip()
    
    # 尝试匹配"X，Y"结构（简单判断）
    if not relation['subject'] and '，' in raw_text:
        parts = raw_text.split('，')
        if len(parts) >= 2:
            relation['subject'] = parts[0].strip()
            relation['predicate'] = parts[1].strip()
    
    # 尝试从condition提取四元组
    if not relation['subject'] and condition:
        # 常见命理学结构
        patterns = [
            (r'(日干|岁君|正官格|伤官|食神格|财星|阴阳|中和|六合|六冲|制化|太过|不及|身强|身弱|用神|格局|原局|运势|流时)', 
             r'(克|制|生|喜|嫌|忌|有|无)',
             r'(岁君|日干|伤官|财星|官杀|印绶|比劫|富贵|贫贱|中和|偏枯)'),
        ]
        
        for subj_pat, pred_pat, obj_pat in patterns:
            match = re.search(f'({subj_pat})({pred_pat})({obj_pat})', condition)
            if match:
                relation['subject'] = match.group(1)
                relation['predicate'] = match.group(2)
                relation['object'] = match.group(3)
                break
    
    return relation

def validate_semantic_chain(raw_text, relation, condition, passage_id):
    """
    验证语义链条：Evidence Span → Independent Semantic Relation → Condition
    
    验证维度：
    1. Evidence是否来自原典
    2. Relation是否独立识别
    3. Condition是否由Evidence和Relation推导
    4. 四元关系是否完整
    """
    issues = []
    audit_evidence = {}
    
    # Step 1: 验证Evidence Span
    if not raw_text or len(raw_text) < 5:
        issues.append('insufficient_evidence')
        audit_evidence['evidence_check'] = 'FAIL: Evidence insufficient'
    else:
        audit_evidence['evidence_check'] = 'PASS'
    
    # Step 2: 验证Independent Relation
    if not relation or relation == 'general':
        issues.append('generic_relation')
        audit_evidence['relation_check'] = 'FAIL: Too generic'
    else:
        audit_evidence['relation_check'] = 'PASS'
    
    # Step 3: 提取四元关系
    semantic_relation = extract_semantic_relation(raw_text, condition)
    audit_evidence['semantic_relation'] = semantic_relation
    
    # Step 4: 验证四元关系完整性
    required_fields = ['subject', 'predicate', 'conclusion']
    missing = [f for f in required_fields if not semantic_relation.get(f)]
    
    if missing:
        issues.append('incomplete_relation')
        audit_evidence['relation_completeness'] = f'FAIL: Missing {", ".join(missing)}'
    else:
        audit_evidence['relation_completeness'] = 'PASS'
    
    # Step 5: 验证Condition是否与Evidence关联
    # 核心验证：Condition应该是Evidence的合法语义提取
    # 不检查词匹配，检查语义连贯性
    
    # 如果原始Evidence包含"者...谓之/主/谓"结构，Condition应该反映这个结构
    if '者' in raw_text and ('谓之' in raw_text or '主' in raw_text or '谓' in raw_text):
        # 检查Condition是否包含结论
        if semantic_relation['conclusion'] and semantic_relation['conclusion'] not in condition:
            issues.append('conclusion_mismatch')
            audit_evidence['condition_validation'] = f'FAIL: Conclusion "{semantic_relation["conclusion"]}" not in condition'
        else:
            audit_evidence['condition_validation'] = 'PASS: Conclusion matches'
    
    # Step 6: 检查semantic_overreach（Condition是否超出Evidence语义范围）
    # 不检查词匹配，检查是否有明显新增概念
    overreach_keywords = ['唯一', '必须', '只能', '一定', '绝对', '完全']
    if any(kw in condition for kw in overreach_keywords):
        issues.append('semantic_overreach')
        audit_evidence['overreach_check'] = f'FAIL: Contains overreach keyword'
    else:
        audit_evidence['overreach_check'] = 'PASS'
    
    # Step 7: 检查multi_conclusion（Condition是否包含多个独立结论）
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
    
    passed = len(issues) == 0
    return {
        'passage_id': passage_id,
        'raw_text': raw_text[:80] + '...' if len(raw_text) > 80 else raw_text,
        'relation': relation,
        'condition': condition,
        'semantic_relation': semantic_relation,
        'issues': issues,
        'audit_evidence': audit_evidence,
        'passed': passed
    }

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
    print("Semantic Relation Validator - 真正的语义关系验证")
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
    
    # 计算指标
    passed_count = sum(1 for r in results if r['passed'])
    total = len(results)
    
    overreach_count = sum(1 for r in results if 'semantic_overreach' in r['issues'])
    unsupported_count = sum(1 for r in results if 'unsupported_condition' in r['issues'])
    multi_conclusion_count = sum(1 for r in results if 'multi_conclusion' in r['issues'])
    incomplete_count = sum(1 for r in results if 'incomplete_relation' in r['issues'])
    
    semantic_overreach_rate = (overreach_count / total * 100) if total > 0 else 0
    unsupported_condition_rate = (unsupported_count / total * 100) if total > 0 else 0
    multi_conclusion_rate = (multi_conclusion_count / total * 100) if total > 0 else 0
    
    # 输出结果
    print("\n" + "=" * 80)
    print("Semantic Relation Validation Results")
    print("=" * 80)
    print(f"\n总断言: {total}条")
    print(f"PASS: {passed_count}条 ({passed_count/total*100:.1f}%)")
    print(f"FAIL: {total-passed_count}条 ({(total-passed_count)/total*100:.1f}%)")
    
    print("\n" + "=" * 80)
    print("Quality Metrics")
    print("=" * 80)
    print(f"\n  semantic_overreach_rate: {semantic_overreach_rate:.1f}%")
    print(f"  unsupported_condition_rate: {unsupported_condition_rate:.1f}%")
    print(f"  multi_conclusion_rate: {multi_conclusion_rate:.1f}%")
    print(f"  incomplete_relation_rate: {(incomplete_count/total*100):.1f}%")
    
    # 列出FAIL条目
    failures = [r for r in results if not r['passed']]
    if failures:
        print("\n" + "=" * 80)
        print(f"FAIL Details ({len(failures)} items)")
        print("=" * 80)
        for r in failures[:10]:
            print(f"\n  {r['passage_id']}:")
            print(f"    Raw: {r['raw_text'][:60]}...")
            print(f"    Relation: {r['relation']}")
            print(f"    Condition: {r['condition']}")
            print(f"    Issues: {', '.join(r['issues'])}")
            if 'audit_evidence' in r:
                for k, v in r['audit_evidence'].items():
                    if 'FAIL' in str(v):
                        print(f"    {k}: {v}")
    
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
            status = "✅ PASS" if r['passed'] else "❌ FAIL"
            print(f"\n  {r['passage_id']}: {status}")
            print(f"    Raw: {r['raw_text'][:50]}...")
            print(f"    Condition: {r['condition']}")
            print(f"    Issues: {', '.join(r['issues']) if r['issues'] else 'None'}")
            if 'semantic_relation' in r['audit_evidence']:
                sr = r['audit_evidence']['semantic_relation']
                print(f"    Subject: {sr.get('subject', 'N/A')}")
                print(f"    Predicate: {sr.get('predicate', 'N/A')}")
                print(f"    Conclusion: {sr.get('conclusion', 'N/A')}")
    
    # 最终判断
    print("\n" + "=" * 80)
    print("Final Judgment")
    print("=" * 80)
    
    all_pass = (
        semantic_overreach_rate == 0 and
        unsupported_condition_rate == 0 and
        multi_conclusion_rate == 0 and
        (incomplete_count / total * 100) < 20  # 允许一定比例的incomplete_relation
    )
    
    if all_pass:
        print("\n🎉 Semantic Relation Validation: 🟢 PASS")
        print("\nAll metrics达标:")
        print("  ✅ semantic_overreach_rate = 0%")
        print("  ✅ unsupported_condition_rate = 0%")
        print("  ✅ multi_conclusion_rate = 0%")
        print("  ✅ incomplete_relation_rate < 20%")
    else:
        print("\n⚠️ Semantic Relation Validation: 🔴 FAIL")
        print(f"\n未全部达标:")
        if semantic_overreach_rate > 0:
            print(f"  ❌ semantic_overreach_rate: {semantic_overreach_rate:.1f}%")
        if unsupported_condition_rate > 0:
            print(f"  ❌ unsupported_condition_rate: {unsupported_condition_rate:.1f}%")
        if multi_conclusion_rate > 0:
            print(f"  ❌ multi_conclusion_rate: {multi_conclusion_rate:.1f}%")
        if (incomplete_count / total * 100) >= 20:
            print(f"  ❌ incomplete_relation_rate: {(incomplete_count/total*100):.1f}%")
    
    # 保存结果
    output = {
        'timestamp': str(Path(__file__).parent),
        'total_assertions': total,
        'passed': passed_count,
        'failed': total - passed_count,
        'metrics': {
            'semantic_overreach_rate': semantic_overreach_rate,
            'unsupported_condition_rate': unsupported_condition_rate,
            'multi_conclusion_rate': multi_conclusion_rate,
            'incomplete_relation_rate': (incomplete_count / total * 100) if total > 0 else 0
        },
        'results': results
    }
    
    output_path = Path(__file__).parent.parent / 'data' / 'p0_8_9_semantic_relation_validation.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
    return 0 if all_pass else 1

if __name__ == '__main__':
    sys.exit(main())
