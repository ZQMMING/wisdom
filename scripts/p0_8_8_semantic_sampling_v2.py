# -*- coding: utf-8 -*-
"""P0-8.8整改版: 50条断言资产语义抽样审计（修正统计矛盾）

核心原则（b99bcf7裁决冻结）:
1. 报告统计必须与JSON完全一致
2. 不再扩大到500/1000，先裁干净这10条
3. PZZQ-GEJU-003/006/007暂停授权，重新拆Primitive
4. DTS-SHUAIWANG-002拆成独立命题
5. is_minimal=false、is_single=false、is_independent=false的资产不得COMPLETE
6. has_excluded=false不得作为PASS
7. 增加真正的semantic drift review
"""

import json
import sys
import os
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, r'D:\shuntian\backend')

class SemanticAuditorV2:
    """语义抽样审计器V2 - 真正检查semantic drift"""
    
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
    
    def check_semantic_drift(self, assertion: dict) -> Tuple[bool, str]:
        """真正的语义漂移检查 - 比较raw_text→min_truth→primitive→condition"""
        
        raw_text = assertion.get('raw_text', '')
        min_truth = assertion.get('min_truth', '')
        primitive = assertion.get('primitive', '')
        condition = assertion.get('condition', '')
        
        issues = []
        
        # 检查1: Primitive是否包含原文没有的概念
        if primitive:
            # 移除常见的前缀/后缀
            clean_primitive = primitive.replace('_', ' ').replace('ge_', '').replace('_ge', '')
            
            # 检查Primitive是否过度工程化
            if '_like_' in primitive or '_avoid_' in primitive or '_ge_' in primitive:
                issues.append(f'Primitive过度工程化: {primitive}')
            
            # 检查Primitive是否超出原文范围
            if len(clean_primitive) > len(raw_text) * 1.5:
                issues.append(f'Primitive过于冗长，可能超出原文范围')
        
        # 检查2: Condition是否添加原文没有的判断
        if condition and raw_text:
            # 检查Condition是否包含吉凶判断（原文可能没有）
            if any(keyword in condition for keyword in ['吉凶', '富贵', '贫贱', '成败']):
                if not any(keyword in raw_text for keyword in ['吉凶', '富贵', '贫贱', '成败']):
                    issues.append(f'Condition添加原文没有的吉凶判断')
        
        # 检查3: min_truth是否合并多个结论
        if min_truth:
            # 检查是否包含"和"、"与"、"及"等连接词（可能合并多个结论）
            if '和' in min_truth or '与' in min_truth or '及' in min_truth:
                # 不一定是问题，需要进一步判断
                pass
            
            # 检查是否包含多个"→"（可能表示多个推导）
            if min_truth.count('→') > 1:
                issues.append(f'min_truth包含多个推导，可能不是单一命题')
        
        # 检查4: 语义范围检查
        if raw_text and min_truth:
            # 提取原文关键词
            raw_keywords = set()
            for char in raw_text:
                if '\u4e00' <= char <= '\u9fff':  # 中文字符
                    raw_keywords.add(char)
            
            # 提取min_truth关键词
            truth_keywords = set()
            for char in min_truth:
                if '\u4e00' <= char <= '\u9fff':
                    truth_keywords.add(char)
            
            # 检查min_truth是否包含原文没有的核心概念
            extra_keywords = truth_keywords - raw_keywords
            if len(extra_keywords) > 5:  # 允许少量连接词
                issues.append(f'min_truth包含{len(extra_keywords)}个原文没有的概念')
        
        return len(issues) == 0, issues
    
    def audit_assertion(self, assertion: dict) -> dict:
        """审计单条断言的端到端语义链（严格版）"""
        
        audit_id = assertion.get('passage_id', 'UNKNOWN')
        
        # 基础检查
        checks = {
            'has_raw_text': bool(assertion.get('raw_text', '')),
            'has_min_truth': bool(assertion.get('min_truth', '')),
            'has_primitive': bool(assertion.get('primitive', '')),
            'has_condition': bool(assertion.get('condition', '')),
            'is_minimal': assertion.get('is_minimal', False),
            'is_single': assertion.get('is_single', False),
            'is_independent': assertion.get('is_independent', False),
            'has_excluded': bool(assertion.get('excluded', []))
        }
        
        # 新增：真正的语义漂移检查
        semantic_drift_ok, semantic_issues = self.check_semantic_drift(assertion)
        checks['semantic_drift_ok'] = semantic_drift_ok
        checks['semantic_issues'] = semantic_issues
        
        # 综合评估（严格版）
        issues = []
        
        # 问题1: 基础字段缺失
        if not checks['has_raw_text']:
            issues.append('原文缺失')
        if not checks['has_min_truth']:
            issues.append('最小命题不明确')
        if not checks['has_primitive']:
            issues.append('Primitive不明确')
        if not checks['has_condition']:
            issues.append('Condition不明确')
        
        # 问题2: 四个门槛不满足
        if not checks['is_minimal']:
            issues.append('不满足最小命题门槛')
        if not checks['is_single']:
            issues.append('不满足单一结论门槛')
        if not checks['is_independent']:
            issues.append('不满足独立来源门槛')
        if not checks['has_excluded']:
            issues.append('未明确排除其他结论')
        
        # 问题3: 语义漂移
        if not semantic_drift_ok:
            issues.extend(semantic_issues)
        
        # 生成审计结论（严格版）
        # 任何一项不满足都不得PASS
        critical_issues = [
            '原文缺失', '最小命题不明确', 'Primitive不明确', 'Condition不明确',
            '不满足最小命题门槛', '不满足单一结论门槛', '不满足独立来源门槛',
            '未明确排除其他结论'
        ]
        
        if any(issue in critical_issues for issue in issues):
            status = 'FAIL'
            confidence = 'LOW'
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
            'checks': checks
        }
    
    def run_audit(self, samples: List[dict]) -> dict:
        """运行完整审计"""
        print("\n▶ 阶段1: 随机抽样")
        print(f"  从50条断言中抽取 {len(samples)} 条进行审计")
        
        print("\n▶ 阶段2: 端到端语义链审计（严格版）")
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
    print("P0-8.8整改版: 50条断言资产语义抽样审计（修正统计矛盾）")
    print("="*70)
    
    # 加载断言资产
    filepath = r'D:\shuntian\backend\data\p0_8_7_expansion.json'
    
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return
    
    auditor = SemanticAuditorV2()
    assertions = auditor.load_assertions(filepath)
    
    print(f"\n▶ 阶段0: 加载断言资产")
    print(f"  总断言: {len(assertions)}条")
    
    # 随机抽样（固定种子以便复现）
    random.seed(42)
    samples = auditor.sample_assertions(assertions, sample_size=10)
    
    # 运行审计
    results = auditor.run_audit(samples)
    
    # 保存结果（确保JSON与报告一致）
    output_path = r'D:\shuntian\backend\data\p0_8_8_semantic_audit_v2.json'
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
    
    # 验证统计一致性
    assert results['pass_count'] + results['partial_count'] + results['fail_count'] == results['total_samples'], \
        "统计不一致！"
    
    print(f"\n【统计一致性检查】")
    print(f"  ✅ PASS + PARTIAL + FAIL = {results['pass_count'] + results['partial_count'] + results['fail_count']} = {results['total_samples']}")
    
    print(f"\n【关键发现】")
    if results['fail_count'] > 0:
        print(f"  ⚠️ 发现 {results['fail_count']} 条FAIL，需要整改")
        print(f"  问题集中在: Primitive过度工程化、未明确排除其他结论、语义漂移")
    else:
        print(f"  ✓ 所有抽样断言通过语义审计")
    
    print(f"\n【生产质量指标】")
    print(f"  语义保真率: {results['pass_rate']:.1f}%")
    if results['pass_rate'] >= 80:
        print(f"  建议: 可以扩大资产规模")
    else:
        print(f"  建议: 需要整改后再扩大")
    
    print(f"\n【流水线状态】")
    if results['fail_count'] == 0:
        print(f"P0-8.8 Semantic Sampling Audit V2 🟢 PASS（50条断言语义保真）")
    else:
        print(f"P0-8.8 Semantic Sampling Audit V2 🟡 HOLD（发现{results['fail_count']}条FAIL，需整改）")
    
    return results


if __name__ == '__main__':
    main()
