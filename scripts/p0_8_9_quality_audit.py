# -*- coding: utf-8 -*-
"""P0-8.9: 30条五书断言扩展验证 - 验证生产方法稳定性

核心原则（418f270裁决冻结）:
1. 从10→30，不要直接30→500
2. 验证生产方法是否稳定
3. 关注质量指标：
   - semantic_overreach_rate = 0
   - unsupported_condition_rate = 0
   - multi_conclusion_rate = 0
   - source_traceability_rate = 100%
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, r'D:\shuntian\backend')

class AssertionQualityAuditor:
    """断言质量审计器 - 验证生产方法稳定性"""
    
    def __init__(self):
        self.quality_metrics = {
            'semantic_overreach_rate': 0.0,
            'unsupported_condition_rate': 0.0,
            'multi_conclusion_rate': 0.0,
            'source_traceability_rate': 100.0
        }
        self.audit_results = []
    
    def load_candidates(self, filepath: str, limit: int = 30) -> List[dict]:
        """从现有50条中加载30条候选"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        candidates = data.get('verified_assertions', [])
        
        # 选择前30条（或全部如果不足30条）
        selected = candidates[:limit]
        
        return selected
    
    def audit_quality(self, assertion: dict) -> dict:
        """审计单条断言的质量指标"""
        
        passage_id = assertion.get('passage_id', '')
        raw_text = assertion.get('raw_text', '')
        primitive = assertion.get('primitive', '')
        condition = assertion.get('condition', '')
        min_truth = assertion.get('min_truth', '')
        excluded = assertion.get('excluded', [])
        
        issues = []
        
        # 指标1: semantic_overreach（语义超出原文）
        semantic_overreach = False
        if raw_text and min_truth:
            raw_chars = set(raw_text.replace('。', '').replace('，', ''))
            truth_chars = set(min_truth)
            extra_chars = truth_chars - raw_chars
            
            # 检查是否包含原文没有的核心汉字
            core_extra = [c for c in extra_chars if '\u4e00' <= c <= '\u9fff']
            if len(core_extra) > 0:
                semantic_overreach = True
                issues.append(f'semantic_overreach: 包含{len(core_extra)}个原文没有的汉字')
        
        # 指标2: unsupported_condition（Condition添加原文没有的判断）
        unsupported_condition = False
        jixiong_keywords = ['吉凶', '富贵', '贫贱', '成败', '祸福', '荣枯']
        if condition:
            for kw in jixiong_keywords:
                if kw in condition and kw not in raw_text:
                    unsupported_condition = True
                    issues.append(f'unsupported_condition: 添加原文没有的{kw}判断')
                    break
        
        # 指标3: multi_conclusion（min_truth合并多个结论）
        multi_conclusion = False
        if min_truth:
            # 检查是否包含多个"→"或"和/与/及"
            if min_truth.count('→') > 1:
                multi_conclusion = True
                issues.append(f'multi_conclusion: 包含多个推导')
            elif '和' in min_truth or '与' in min_truth or '及' in min_truth:
                # 不一定是问题，需要进一步判断
                pass
        
        # 指标4: source_traceability（来源可追溯）
        source_traced = bool(raw_text and assertion.get('volume', '') and assertion.get('chapter', ''))
        if not source_traced:
            issues.append('source_traceability: 缺少volume/chapter信息')
        
        # 综合评估
        all_pass = not semantic_overreach and not unsupported_condition and not multi_conclusion and source_traced
        
        return {
            'passage_id': passage_id,
            'semantic_overreach': semantic_overreach,
            'unsupported_condition': unsupported_condition,
            'multi_conclusion': multi_conclusion,
            'source_traced': source_traced,
            'issues': issues,
            'status': 'PASS' if all_pass else 'FAIL'
        }
    
    def run_audit(self, candidates: List[dict]) -> dict:
        """运行完整的质量审计"""
        
        print("\n▶ 阶段1: 加载30条候选断言")
        print(f"  总候选: {len(candidates)}条")
        
        print("\n▶ 阶段2: 逐条质量审计")
        results = []
        for cand in candidates:
            result = self.audit_quality(cand)
            results.append(result)
            
            status_symbol = '✅' if result['status'] == 'PASS' else '❌'
            print(f"  {status_symbol} {result['passage_id']}: {result['status']}")
            if result['issues']:
                for issue in result['issues']:
                    print(f"     └─ ⚠️ {issue}")
        
        # 统计结果
        pass_count = sum(1 for r in results if r['status'] == 'PASS')
        fail_count = sum(1 for r in results if r['status'] == 'FAIL')
        
        # 计算质量指标
        semantic_overreach_count = sum(1 for r in results if r['semantic_overreach'])
        unsupported_condition_count = sum(1 for r in results if r['unsupported_condition'])
        multi_conclusion_count = sum(1 for r in results if r['multi_conclusion'])
        source_traced_count = sum(1 for r in results if r['source_traced'])
        
        total = len(results)
        
        self.quality_metrics = {
            'semantic_overreach_rate': semantic_overreach_count / total * 100 if total > 0 else 0,
            'unsupported_condition_rate': unsupported_condition_count / total * 100 if total > 0 else 0,
            'multi_conclusion_rate': multi_conclusion_count / total * 100 if total > 0 else 0,
            'source_traceability_rate': source_traced_count / total * 100 if total > 0 else 100
        }
        
        print("\n▶ 阶段3: 质量指标统计")
        print(f"  总候选: {total}条")
        print(f"  PASS: {pass_count}条 ({pass_count/total*100:.1f}%)")
        print(f"  FAIL: {fail_count}条 ({fail_count/total*100:.1f}%)")
        
        print(f"\n  【质量指标】")
        print(f"    semantic_overreach_rate: {self.quality_metrics['semantic_overreach_rate']:.1f}%")
        print(f"    unsupported_condition_rate: {self.quality_metrics['unsupported_condition_rate']:.1f}%")
        print(f"    multi_conclusion_rate: {self.quality_metrics['multi_conclusion_rate']:.1f}%")
        print(f"    source_traceability_rate: {self.quality_metrics['source_traceability_rate']:.1f}%")
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_candidates': total,
            'pass_count': pass_count,
            'fail_count': fail_count,
            'pass_rate': pass_count / total * 100 if total > 0 else 0,
            'fail_rate': fail_count / total * 100 if total > 0 else 0,
            'quality_metrics': self.quality_metrics,
            'audit_results': results
        }


def main():
    print("="*70)
    print("P0-8.9: 30条五书断言扩展验证 - 验证生产方法稳定性")
    print("="*70)
    
    # 加载候选断言
    filepath = r'D:\shuntian\backend\data\p0_8_7_expansion.json'
    
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return
    
    auditor = AssertionQualityAuditor()
    candidates = auditor.load_candidates(filepath, limit=30)
    
    # 运行质量审计
    results = auditor.run_audit(candidates)
    
    # 保存结果
    output_path = r'D:\shuntian\backend\data\p0_8_9_quality_audit.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
    
    # 核心结论
    print("\n" + "="*70)
    print("核心结论")
    print("="*70)
    
    print(f"\n【质量指标验证】")
    metrics = results['quality_metrics']
    
    # 检查是否达到目标
    targets = {
        'semantic_overreach_rate': 0.0,
        'unsupported_condition_rate': 0.0,
        'multi_conclusion_rate': 0.0,
        'source_traceability_rate': 100.0
    }
    
    all_targets_met = True
    for metric, target in targets.items():
        actual = metrics[metric]
        met = (actual == target) if metric != 'source_traceability_rate' else (actual >= target)
        status = '✅' if met else '❌'
        print(f"  {status} {metric}: {actual:.1f}% (目标: {target:.1f}%)")
        if not met:
            all_targets_met = False
    
    print(f"\n【生产方法稳定性】")
    if all_targets_met:
        print(f"  ✅ 所有质量指标达标")
        print(f"  ✅ 生产方法稳定，可以继续扩大资产规模")
    else:
        print(f"  ❌ 部分质量指标未达标")
        print(f"  ⚠️ 需要先整改再扩大规模")
    
    print(f"\n【流水线状态】")
    if all_targets_met:
        print(f"P0-8.9 30-Asset Quality Audit 🟢 PASS（生产方法稳定）")
    else:
        print(f"P0-8.9 30-Asset Quality Audit 🟡 HOLD（需整改）")
    
    return results


if __name__ == '__main__':
    main()
