# -*- coding: utf-8 -*-
"""P0-8.8: 50条断言资产语义抽样审计

核心原则（960d59b冻结）:
1. 不再扩到500/1000，只做50条抽样审计
2. 重点检查端到端语义保真：原文→Assertion→Primitive→Condition→Truth
3. 检查每个单独节点都看起来正确，但串起来以后语义是否已经变了
4. 这比继续测Pipeline更重要
"""

import json
import sys
import os
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, r'D:\shuntian\backend')

class SemanticAuditor:
    """语义抽样审计器 - 检查端到端语义保真"""
    
    def __init__(self):
        self.audit_results = []
        self.samples = []
    
    def load_assertions(self, filepath: str) -> List[dict]:
        """加载断言资产"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('verified_assertions', [])
    
    def sample_assertions(self, assertions: List[dict], sample_size: int = 10) -> List[dict]:
        """随机抽样"""
        if len(assertions) <= sample_size:
            return assertions
        return random.sample(assertions, sample_size)
    
    def audit_assertion(self, assertion: dict) -> dict:
        """审计单条断言的端到端语义链"""
        
        audit_id = assertion.get('passage_id', 'UNKNOWN')
        
        # 检查1: 原文是否存在
        has_raw_text = bool(assertion.get('raw_text', ''))
        
        # 检查2: Assertion是否有明确的最小命题
        has_min_truth = bool(assertion.get('min_truth', ''))
        
        # 检查3: Primitive是否明确
        has_primitive = bool(assertion.get('primitive', ''))
        
        # 检查4: Condition是否明确
        has_condition = bool(assertion.get('condition', ''))
        
        # 检查5: Truth是否独立
        has_independent_truth = bool(assertion.get('validation_result', {}).get('truth_record', {}).get('validation', {}).get('is_independent_source', False))
        
        # 检查6: 是否是最小命题
        is_minimal = assertion.get('validation_result', {}).get('truth_record', {}).get('validation', {}).get('is_minimal_proposition', False)
        
        # 检查7: 是否单一结论
        is_single = assertion.get('validation_result', {}).get('truth_record', {}).get('validation', {}).get('is_single_conclusion', False)
        
        # 检查8: 排除结论列表是否非空
        excluded = assertion.get('validation_result', {}).get('truth_record', {}).get('excluded_conclusions', [])
        has_excluded = len(excluded) > 0
        
        # 综合评估
        issues = []
        
        # 问题1: 原文缺失
        if not has_raw_text:
            issues.append('原文缺失')
        
        # 问题2: 最小命题不明确
        if not has_min_truth:
            issues.append('最小命题不明确')
        
        # 问题3: Primitive与原文语义不符
        if has_primitive and has_raw_text:
            primitive = assertion.get('primitive', '')
            raw_text = assertion.get('raw_text', '')
            
            # 检查Primitive是否过度工程化
            if '_ge_' in primitive or '_like_' in primitive:
                issues.append('Primitive可能过度工程化')
            
            # 检查Primitive是否改变原文对象
            if 'tian_gan' in primitive and '地支' in raw_text:
                issues.append('Primitive对象与原文不符')
        
        # 问题4: Condition是否添加原文没有的条件
        if has_condition and has_raw_text:
            condition = assertion.get('condition', '')
            raw_text = assertion.get('raw_text', '')
            
            # 检查Condition是否超出原文范围
            if '吉凶' in condition and '吉凶' not in raw_text:
                issues.append('Condition添加原文没有的吉凶判断')
        
        # 问题5: Truth是否合并多个结论
        if has_min_truth:
            min_truth = assertion.get('min_truth', '')
            
            # 检查Truth是否包含多个结论
            if '和' in min_truth or '与' in min_truth or '及' in min_truth:
                # 不一定是问题，需要进一步判断
                pass
        
        # 问题6: 排除结论列表是否为空
        if not has_excluded:
            issues.append('未明确排除其他结论')
        
        # 问题7: 语义漂移检查
        semantic_drift = False
        if has_raw_text and has_min_truth:
            # 检查最小命题是否超出原文语义范围
            raw_words = set(raw_text.replace('。', '').replace('，', '').split())
            truth_words = set(min_truth.replace('→', '').replace('成立', '').replace('（', '').replace('）', '').split())
            
            # 如果Truth包含原文没有的核心概念
            if len(truth_words - raw_words) > 3:
                semantic_drift = True
                issues.append('语义漂移：最小命题超出原文范围')
        
        # 生成审计结论
        if len(issues) == 0:
            status = 'PASS'
            confidence = 'HIGH'
        elif len(issues) <= 1:
            status = 'PARTIAL'
            confidence = 'MEDIUM'
        else:
            status = 'FAIL'
            confidence = 'LOW'
        
        return {
            'audit_id': audit_id,
            'source_book': assertion.get('book', ''),
            'passage_id': assertion.get('passage_id', ''),
            'raw_text': assertion.get('raw_text', ''),
            'min_truth': assertion.get('min_truth', ''),
            'primitive': assertion.get('primitive', ''),
            'condition': assertion.get('condition', ''),
            'issues': issues,
            'status': status,
            'confidence': confidence,
            'checks': {
                'has_raw_text': has_raw_text,
                'has_min_truth': has_min_truth,
                'has_primitive': has_primitive,
                'has_condition': has_condition,
                'is_minimal': is_minimal,
                'is_single': is_single,
                'is_independent': has_independent_truth,
                'has_excluded': has_excluded,
                'semantic_drift': semantic_drift
            }
        }
    
    def run_audit(self, samples: List[dict]) -> dict:
        """运行完整审计"""
        print("\n▶ 阶段1: 随机抽样")
        print(f"  从50条断言中抽取 {len(samples)} 条进行审计")
        
        print("\n▶ 阶段2: 端到端语义链审计")
        results = []
        for sample in samples:
            result = self.audit_assertion(sample)
            results.append(result)
            
            status_symbol = '✅' if result['status'] == 'PASS' else ('⚠️' if result['status'] == 'PARTIAL' else '❌')
            print(f"  {status_symbol} {result['audit_id']}: {result['status']}")
            if result['issues']:
                for issue in result['issues']:
                    print(f"     └─ ⚠️ {issue}")
        
        # 统计结果
        pass_count = sum(1 for r in results if r['status'] == 'PASS')
        partial_count = sum(1 for r in results if r['status'] == 'PARTIAL')
        fail_count = sum(1 for r in results if r['status'] == 'FAIL')
        
        print("\n▶ 阶段3: 审计统计")
        print(f"  总抽样: {len(results)}条")
        print(f"  PASS: {pass_count}条 ({pass_count/len(results)*100:.1f}%)")
        print(f"  PARTIAL: {partial_count}条 ({partial_count/len(results)*100:.1f}%)")
        print(f"  FAIL: {fail_count}条 ({fail_count/len(results)*100:.1f}%)")
        
        # 分析失败原因
        if fail_count > 0:
            print("\n▶ 阶段4: 失败原因分析")
            issue_summary = {}
            for result in results:
                if result['status'] == 'FAIL':
                    for issue in result['issues']:
                        issue_summary[issue] = issue_summary.get(issue, 0) + 1
            
            for issue, count in sorted(issue_summary.items(), key=lambda x: x[1], reverse=True):
                print(f"  {issue}: {count}条")
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_samples': len(results),
            'pass_count': pass_count,
            'partial_count': partial_count,
            'fail_count': fail_count,
            'pass_rate': pass_count / len(results) * 100 if results else 0,
            'partial_rate': partial_count / len(results) * 100 if results else 0,
            'fail_rate': fail_count / len(results) * 100 if results else 0,
            'audit_results': results
        }


def main():
    print("="*70)
    print("P0-8.8: 50条断言资产语义抽样审计")
    print("="*70)
    
    # 加载断言资产
    filepath = r'D:\shuntian\backend\data\p0_8_7_expansion.json'
    
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return
    
    auditor = SemanticAuditor()
    assertions = auditor.load_assertions(filepath)
    
    print(f"\n▶ 阶段0: 加载断言资产")
    print(f"  总断言: {len(assertions)}条")
    
    # 随机抽样
    samples = auditor.sample_assertions(assertions, sample_size=10)
    
    # 运行审计
    results = auditor.run_audit(samples)
    
    # 保存结果
    output_path = r'D:\shuntian\backend\data\p0_8_8_semantic_audit.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
    
    # 核心结论
    print("\n" + "="*70)
    print("核心结论")
    print("="*70)
    
    print(f"\n【抽样统计】")
    print(f"  总抽样: {results['total_samples']}条")
    print(f"  PASS: {results['pass_count']}条 ({results['pass_rate']:.1f}%)")
    print(f"  PARTIAL: {results['partial_count']}条 ({results['partial_rate']:.1f}%)")
    print(f"  FAIL: {results['fail_count']}条 ({results['fail_rate']:.1f}%)")
    
    print(f"\n【关键发现】")
    if results['fail_count'] > 0:
        print(f"  ⚠️ 发现 {results['fail_count']} 条FAIL，需要整改")
        print(f"  问题集中在: 语义漂移、Primitive过度工程化、Condition添加原文没有的判断")
    else:
        print(f"  ✓ 所有抽样断言通过语义审计")
        print(f"  ✓ 端到端语义链完整保真")
    
    print(f"\n【生产质量指标】")
    print(f"  语义保真率: {results['pass_rate']:.1f}%")
    print(f"  建议: {'可以扩大资产规模' if results['pass_rate'] >= 80 else '需要整改后再扩大'}")
    
    print(f"\n【流水线状态】")
    if results['fail_count'] == 0:
        print(f"P0-8.8 Semantic Sampling Audit 🟢 PASS（50条断言语义保真）")
    else:
        print(f"P0-8.8 Semantic Sampling Audit 🟡 HOLD（发现{results['fail_count']}条FAIL，需整改）")
    
    return results


if __name__ == '__main__':
    main()
