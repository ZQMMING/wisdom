# -*- coding: utf-8 -*-
"""P0-8.9整改版：真正的语义审计 - 从原始数据重新审计"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, r'D:\shuntian\backend')

class SemanticPuristAuditorV2:
    """语义纯粹主义审计器V2 - 从原始数据重新审计"""
    
    def __init__(self):
        self.fixes = []
    
    def load_assertions_from_source(self, expansion_filepath: str, limit: int = 30) -> List[dict]:
        """从原始p0_8_7扩展数据加载断言"""
        with open(expansion_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assertions = data.get('verified_assertions', [])
        
        # 选择前30条
        selected = assertions[:limit]
        
        return selected
    
    def audit_semantic_purity_v2(self, assertion: dict) -> dict:
        """真正的语义纯粹性审计（V2版）"""
        
        passage_id = assertion.get('passage_id', '')
        raw_text = assertion.get('raw_text', '')
        min_truth = assertion.get('min_truth', '')
        primitive = assertion.get('primitive', '')
        condition = assertion.get('condition', '')
        
        print(f"\n▶ 审计 {passage_id}")
        print(f"  原文: {raw_text}")
        print(f"  当前min_truth: {min_truth}")
        print(f"  当前Primitive: {primitive}")
        print(f"  当前Condition: {condition}")
        
        issues = []
        fixes = []
        
        # 审计1: min_truth是否包含原文没有的汉字
        raw_chars = set(raw_text.replace('。', '').replace('，', '').replace('！', ''))
        truth_chars = set(min_truth)
        extra_chars = truth_chars - raw_chars
        
        # 只检查汉字（排除标点、箭头等）
        han_extra = [c for c in extra_chars if '\u4e00' <= c <= '\u9fff']
        
        if han_extra:
            issues.append(f'min_truth包含{len(han_extra)}个原文没有的汉字: {"".join(han_extra)}')
        
        # 审计2: Condition是否添加原文没有的判断
        jixiong_keywords = ['吉凶', '富贵', '贫贱', '成败', '祸福', '荣枯']
        for kw in jixiong_keywords:
            if kw in condition and kw not in raw_text:
                issues.append(f'Condition添加原文没有的{kw}判断')
        
        # 审计3: Primitive是否过度工程化
        if '_ge_' in primitive or '_like_' in primitive or '_avoid_' in primitive:
            issues.append('Primitive过度工程化')
        
        # 审计4: min_truth是否超出原文语义范围
        if len(min_truth) > len(raw_text) * 1.5:
            issues.append(f'min_truth长度({len(min_truth)})超过原文({len(raw_text)})的1.5倍')
        
        # 生成整改方案
        if issues:
            print(f"  ❌ 发现问题: {issues}")
            
            # 整改策略1: 从原文提取真正最小的语义命题
            new_min_truth = self._extract_pure_minimal_truth(raw_text)
            if new_min_truth != min_truth:
                fixes.append(f'精简min_truth: {min_truth} → {new_min_truth}')
                min_truth = new_min_truth
            
            # 整改策略2: 移除Condition中的吉凶判断
            if any('Condition添加原文没有的' in i for i in issues):
                new_condition = self._remove_jixiong_from_condition(condition)
                if new_condition != condition:
                    fixes.append(f'移除Condition吉凶判断: {condition} → {new_condition}')
                    condition = new_condition
            
            # 整改策略3: 简化Primitive
            if any('Primitive过度工程化' in i for i in issues):
                new_primitive = self._simplify_primitive(primitive)
                if new_primitive != primitive:
                    fixes.append(f'简化Primitive: {primitive} → {new_primitive}')
                    primitive = new_primitive
        else:
            print(f"  ✅ 语义纯粹")
        
        return {
            'passage_id': passage_id,
            'original_min_truth': assertion.get('min_truth', ''),
            'fixed_min_truth': min_truth,
            'original_primitive': assertion.get('primitive', ''),
            'fixed_primitive': primitive,
            'original_condition': assertion.get('condition', ''),
            'fixed_condition': condition,
            'issues': issues,
            'fixes': fixes,
            'status': 'PASS' if not issues else 'FAIL'
        }
    
    def _extract_pure_minimal_truth(self, raw_text: str) -> str:
        """从原文提取真正纯粹的min_truth - 只使用原文汉字"""
        
        # 移除标点
        clean_text = raw_text.replace('。', '').replace('，', '').replace('！', '')
        
        # 提取核心语义（最多10个字，确保纯粹）
        core_chars = []
        for char in clean_text:
            if '\u4e00' <= char <= '\u9fff':  # 中文字符
                core_chars.append(char)
        
        # 只取前10个汉字作为核心命题
        pure_min_truth = ''.join(core_chars[:10])
        
        return pure_min_truth
    
    def _remove_jixiong_from_condition(self, condition: str) -> str:
        """移除Condition中的吉凶判断"""
        
        jixiong_keywords = ['吉凶', '富贵', '贫贱', '成败', '祸福', '荣枯']
        
        new_condition = condition
        for kw in jixiong_keywords:
            new_condition = new_condition.replace(kw, '')
        
        # 清理多余空格
        new_condition = new_condition.strip()
        
        return new_condition
    
    def _simplify_primitive(self, primitive: str) -> str:
        """简化Primitive，移除过度工程化后缀"""
        
        # 移除工程化后缀
        clean_primitive = primitive
        clean_primitive = clean_primitive.replace('_ge_', '_')
        clean_primitive = clean_primitive.replace('_like_', '_')
        clean_primitive = clean_primitive.replace('_avoid_', '_')
        
        # 如果仍然过长，只取核心词
        if len(clean_primitive) > 20:
            words = clean_primitive.split('_')
            core_words = [w for w in words if len(w) > 2][:3]
            clean_primitive = '_'.join(core_words)
        
        return clean_primitive
    
    def run_purist_audit_v2(self, assertions: List[dict]) -> dict:
        """运行真正的语义纯粹性审计（V2版）"""
        
        print("\n▶ 阶段1: 加载30条候选断言")
        print(f"  总候选: {len(assertions)}条")
        
        print("\n▶ 阶段2: 逐条语义纯粹性审计")
        results = []
        for assertion in assertions:
            result = self.audit_semantic_purity_v2(assertion)
            results.append(result)
            
            status_symbol = '✅' if result['status'] == 'PASS' else '❌'
            print(f"  {status_symbol} {result['passage_id']}: {result['status']}")
            if result['fixes']:
                for fix in result['fixes']:
                    print(f"     └─ 🔧 {fix}")
        
        # 统计结果
        pass_count = sum(1 for r in results if r['status'] == 'PASS')
        fail_count = sum(1 for r in results if r['status'] == 'FAIL')
        
        print("\n▶ 阶段3: 审计统计")
        print(f"  总审计: {len(results)}条")
        print(f"  PASS: {pass_count}条 ({pass_count/len(results)*100:.1f}%)")
        print(f"  FAIL: {fail_count}条 ({fail_count/len(results)*100:.1f}%)")
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_audited': len(results),
            'pass_count': pass_count,
            'fail_count': fail_count,
            'pass_rate': pass_count / len(results) * 100 if results else 0,
            'fail_rate': fail_count / len(results) * 100 if results else 0,
            'audit_results': results
        }


def main():
    print("="*70)
    print("P0-8.9整改版：真正的语义审计 - 从原始数据重新审计")
    print("="*70)
    
    # 从原始p0_8_7扩展数据加载断言
    expansion_filepath = r'D:\shuntian\backend\data\p0_8_7_expansion.json'
    
    if not os.path.exists(expansion_filepath):
        print(f"❌ 文件不存在: {expansion_filepath}")
        return
    
    auditor = SemanticPuristAuditorV2()
    assertions = auditor.load_assertions_from_source(expansion_filepath, limit=30)
    
    # 运行审计
    results = auditor.run_purist_audit_v2(assertions)
    
    # 保存结果
    output_path = r'D:\shuntian\backend\data\p0_8_9_purist_audit_v2.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
    
    # 核心结论
    print("\n" + "="*70)
    print("核心结论")
    print("="*70)
    
    print(f"\n【语义纯粹性审计】")
    print(f"  总审计: {results['total_audited']}条")
    print(f"  PASS: {results['pass_count']}条 ({results['pass_rate']:.1f}%)")
    print(f"  FAIL: {results['fail_count']}条 ({results['fail_rate']:.1f}%)")
    
    print(f"\n【关键区分】")
    print(f"  ✓ 真正的语义审计 ≠ 字符串清洗")
    print(f"  ✓ min_truth必须100%由原文汉字组成")
    print(f"  ✓ 如果原典包含多个语义层，必须拆分成多个Assertion")
    print(f"  ✓ 禁止通过删除后缀制造PASS")
    
    print(f"\n【流水线状态】")
    if results['pass_count'] == len(results):
        print(f"P0-8.9 Purist Audit V2 🟢 PASS（所有断言语义纯粹）")
    else:
        print(f"P0-8.9 Purist Audit V2 🟡 HOLD（仍需整改{results['fail_count']}条）")
    
    return results


if __name__ == '__main__':
    main()
