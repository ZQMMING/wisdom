#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P0-8.9 Final Integration Test - 完整集成测试

测试目标：
验证整个P0-8.9 Pipeline的完整性和一致性

Pipeline流程：
raw_text → IndependentRelationRecognizer → semantic_relation
semantic_relation → EvidenceSpan (independent) → Condition
semantic_relation → Primitive (generated)
EvidenceSpan → Semantic Relation Validator → COMPLETE/PARTIAL/INSUFFICIENT

Commit: 7df2331
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from p0_8_9_canonical_production_v8 import (
    IndependentRelationRecognizer,
    EvidenceSpan,
    CanonicalAssertionProducer
)

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

def run_pipeline(assertion):
    """运行完整Pipeline"""
    passage_id = assertion.get('passage_id', '')
    raw_text = assertion.get('raw_text', '')
    
    # Step 1: 独立生成Relation
    recognizer = IndependentRelationRecognizer()
    relation = recognizer.recognize_relation(raw_text)
    
    # Step 2: 创建Evidence Span
    span = EvidenceSpan(text=raw_text, start=0, end=len(raw_text), relation=relation)
    
    # Step 3: 生成Condition（从Evidence Span，使用内嵌producer）
    condition = producer.producer.produce_condition(span)
    
    # Step 4: 生成Primitive（从Relation，不依赖旧Assertion）
    primitive = producer._generate_primitive_from_relation(relation)
    
    return {
        'passage_id': passage_id,
        'raw_text': raw_text[:100],
        'relation': relation,
        'condition': condition,
        'primitive': primitive,
        'evidence_span': span.to_dict()
    }

def main():
    print("=" * 80)
    print("P0-8.9 Final Integration Test")
    print("=" * 80)
    
    # 加载Assertion
    assertions = load_assertions()
    print(f"\n✅ 加载Assertion: {len(assertions)}条")
    
    # 运行Pipeline
    results = []
    for assertion in assertions:
        result = run_pipeline(assertion)
        results.append(result)
    
    # 输出结果
    print("\n" + "=" * 80)
    print("Pipeline Execution Results")
    print("=" * 80)
    print(f"\n成功执行: {len(results)}条")
    
    # 检查关键指标
    all_have_relation = all(r['relation'] for r in results)
    all_have_condition = all(r['condition'] for r in results)
    all_have_primitive = all(r['primitive'] for r in results)
    all_have_evidence = all(r['evidence_span']['text'] for r in results)
    
    print(f"\n关键指标检查:")
    print(f"  ✅ All have relation: {all_have_relation}")
    print(f"  ✅ All have condition: {all_have_condition}")
    print(f"  ✅ All have primitive: {all_have_primitive}")
    print(f"  ✅ All have evidence_span: {all_have_evidence}")
    
    # 检查独立性（Relation不应依赖旧Assertion）
    print(f"\n独立性检查:")
    independent_relations = sum(1 for r in results if r['relation'] not in ['general', ''])
    print(f"  独立Relation数: {independent_relations}/{len(results)}")
    
    # 保存结果
    output = {
        'timestamp': str(Path(__file__).parent),
        'total_assertions': len(results),
        'results': results
    }
    
    output_path = Path(__file__).parent.parent / 'data' / 'p0_8_9_final_integration_test.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
    
    # 最终判断
    all_pass = (
        all_have_relation and
        all_have_condition and
        all_have_primitive and
        all_have_evidence and
        independent_relations == len(results)
    )
    
    if all_pass:
        print("\n🎉 P0-8.9 Final Integration Test: 🟢 PASS")
    else:
        print("\n⚠️ P0-8.9 Final Integration Test: 🔴 FAIL")
    
    return 0 if all_pass else 1

if __name__ == '__main__':
    sys.exit(main())
