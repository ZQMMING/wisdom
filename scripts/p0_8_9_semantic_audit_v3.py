# -*- coding: utf-8 -*-
"""P0-8.9真正的语义整改 - 区分SOURCE-PURE与SEMANTIC-MINIMAL

核心原则（3f88d9e + 68d01ba裁决冻结）:
1. SOURCE-PURE ≠ SEMANTIC-MINIMAL ≠ TRUTH-VALIDATED ≠ AUTHORIZED
2. min_truth字符来自原文 ≠ 语义最小化
3. 禁止通过字符串清洗制造PASS
4. 必须重新运行原P0-8.9 Semantic Audit V2
5. 多语义层必须拆分Assertion，不能压成一句
"""

import json
import sys
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, r'D:\shuntian\backend')

class SemanticAuditorV3:
    """真正的语义审计器 - 区分纯净性与最小性"""
    
    def __init__(self):
        self.audit_results = []
    
    def audit_assertion(self, assertion: dict) -> dict:
        """逐条语义审计"""
        
        passage_id = assertion.get('passage_id', '')
        raw_text = assertion.get('raw_text', '')
        min_truth = assertion.get('min_truth', '')
        primitive = assertion.get('primitive', '')
        condition = assertion.get('condition', '')
        
        print(f"\n▶ 审计 {passage_id}")
        print(f"  原文: {raw_text}")
        print(f"  min_truth: {min_truth}")
        print(f"  primitive: {primitive}")
        print(f"  condition: {condition}")
        
        issues = []
        
        # Check 1: SOURCE-PURE（字符是否来自原文）
        source_pure = self._check_source_pure(raw_text, min_truth)
        if not source_pure:
            issues.append(f'source_impure: min_truth包含原文没有的字')
        
        # Check 2: SEMANTIC-MINIMAL（是否最小命题）
        semantic_minimal, minimal_explanation = self._check_semantic_minimal(raw_text, min_truth)
        if not semantic_minimal:
            issues.append(f'semantic_not_minimal: {minimal_explanation}')
        
        # Check 3: SINGLE-CONCLUSION（是否单一结论）
        single_conclusion, conclusion_explanation = self._check_single_conclusion(raw_text, min_truth)
        if not single_conclusion:
            issues.append(f'multi_conclusion: {conclusion_explanation}')
        
        # Check 4: CONDITION_VALID（Condition是否合理）
        condition_valid = self._check_condition_valid(condition, raw_text)
        if not condition_valid:
            issues.append('invalid_condition: Condition添加原文没有的判断')
        
        # 判定结果
        status = 'PASS' if len(issues) == 0 else 'FAIL'
        
        result = {
            'passage_id': passage_id,
            'raw_text': raw_text,
            'min_truth': min_truth,
            'primitive': primitive,
            'condition': condition,
            'status': status,
            'issues': issues,
            'source_pure': source_pure,
            'semantic_minimal': semantic_minimal,
            'single_conclusion': single_conclusion,
            'condition_valid': condition_valid
        }
        
        self.audit_results.append(result)
        
        # 打印结果
        if status == 'PASS':
            print(f"  ✅ 语义纯粹且最小")
        else:
            print(f"  ❌ FAIL: {issues}")
        
        return result
    
    def _check_source_pure(self, raw_text: str, min_truth: str) -> bool:
        """检查min_truth是否100%由原文汉字组成"""
        
        # 提取原文所有汉字
        raw_chars = set([c for c in raw_text if '\u4e00' <= c <= '\u9fff'])
        
        # 检查min_truth的每个汉字
        for char in min_truth:
            if '\u4e00' <= char <= '\u9fff' and char not in raw_chars:
                return False
        
        return True
    
    def _check_semantic_minimal(self, raw_text: str, min_truth: str) -> Tuple[bool, str]:
        """检查是否语义最小化（核心！）"""
        
        # 策略：检查min_truth是否包含多个独立语义单元
        
        # 常见模式1：A + B 结构（如"阴阳中和富贵双全"）
        positive_patterns = [
            (r'^(.+)(?:，|，)(.+)$', '包含逗号分隔的多个语义单元'),
            (r'^(.{2,4})(富贵|贫贱|吉凶|祸福|成败|荣枯)(.+)$', '条件+结论结构'),
            (r'^(.+)(?:宜|须|需|当)(.+)$', '条件性判断结构'),
        ]
        
        for pattern, explanation in positive_patterns:
            if re.match(pattern, min_truth):
                return False, explanation
        
        # 策略：检查是否包含多个核心概念
        # 如果min_truth超过10字，可能需要拆分
        chinese_count = len([c for c in min_truth if '\u4e00' <= c <= '\u9fff'])
        if chinese_count > 10:
            return False, f'语义单元过多（{chinese_count}字），可能包含多层语义'
        
        # 检查是否包含常见"条件+结论"组合
        common_conditions = ['中和', '平衡', '旺相', '休囚', '得令', '失令']
        common_conclusions = ['富贵', '贫贱', '吉凶', '成败', '祸福']
        
        has_condition = any(c in min_truth for c in common_conditions)
        has_conclusion = any(c in min_truth for c in common_conclusions)
        
        if has_condition and has_conclusion:
            return False, '同时包含条件词和结论词，不符合最小命题'
        
        return True, '语义最小化'
    
    def _check_single_conclusion(self, raw_text: str, min_truth: str) -> Tuple[bool, str]:
        """检查是否单一结论"""
        
        # 检查是否包含多个结论词
        conclusion_markers = ['谓之', '主', '主贫', '主富', '主贵', '主贱']
        marker_count = sum(1 for m in conclusion_markers if m in min_truth)
        
        if marker_count > 1:
            return False, f'包含{marker_count}个结论标记'
        
        # 检查是否同时包含条件和结论
        if '富贵' in min_truth or '贫贱' in min_truth:
            # 这本身就是一个复合结论
            return False, '同时断言富贵或贫贱，是复合结论'
        
        return True, '单一结论'
    
    def _check_condition_valid(self, condition: str, raw_text: str) -> bool:
        """检查Condition是否有效"""
        
        # 如果condition为空，不判定为FAIL（可能是合理的设计选择）
        if not condition:
            return True
        
        # 提取原文关键词
        raw_keywords = set([c for c in raw_text if '\u4e00' <= c <= '\u9fff'])
        
        # 检查condition是否包含原文没有的判断
        cond_keywords = set([c for c in condition if '\u4e00' <= c <= '\u9fff'])
        extra = cond_keywords - raw_keywords
        
        if extra:
            return False
        
        return True
    
    def run_full_audit(self, assertions: List[dict]) -> dict:
        """运行完整审计"""
        
        print("="*70)
        print("P0-8.9: 真正的语义审计 - SOURCE-PURE vs SEMANTIC-MINIMAL")
        print("="*70)
        
        # 加载原始数据
        filepath = r'D:\shuntian\backend\data\p0_8_7_expansion.json'
        
        if not os.path.exists(filepath):
            print(f"❌ 文件不存在: {filepath}")
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assertions = data.get('verified_assertions', [])
        
        # 取前30条
        sample = assertions[:30]
        
        print(f"\n▶ 阶段1: 加载{len(sample)}条候选断言")
        
        print(f"\n▶ 阶段2: 逐条语义审计")
        
        for i, assertion in enumerate(sample):
            self.audit_assertion(assertion)
        
        print(f"\n▶ 阶段3: 审计统计")
        
        passed = sum(1 for r in self.audit_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.audit_results if r['status'] == 'FAIL')
        
        print(f"  总审计: {len(self.audit_results)}条")
        print(f"  PASS: {passed}条 ({passed/len(self.audit_results)*100:.1f}%)")
        print(f"  FAIL: {failed}条 ({failed/len(self.audit_results)*100:.1f}%)")
        
        # 计算质量指标
        semantic_overreach = sum(1 for r in self.audit_results if not r['semantic_minimal'])
        unsupported_condition = sum(1 for r in self.audit_results if not r['condition_valid'])
        multi_conclusion = sum(1 for r in self.audit_results if not r['single_conclusion'])
        source_traceability = sum(1 for r in self.audit_results if r['source_pure']) / len(self.audit_results) * 100
        
        print(f"\n▶ 阶段4: 质量指标统计")
        print(f"  semantic_overreach_rate: {semantic_overreach/len(self.audit_results)*100:.1f}%")
        print(f"  unsupported_condition_rate: {unsupported_condition/len(self.audit_results)*100:.1f}%")
        print(f"  multi_conclusion_rate: {multi_conclusion/len(self.audit_results)*100:.1f}%")
        print(f"  source_traceability_rate: {source_traceability:.1f}%")
        
        # 核心结论
        print("\n" + "="*70)
        print("核心结论")
        print("="*70)
        
        print(f"\n【语义审计区分】")
        print(f"  ✓ SOURCE-PURE: {source_traceability:.1f}% - 字符是否来自原文")
        print(f"  ✓ SEMANTIC-MINIMAL: {(len(self.audit_results)-semantic_overreach)/len(self.audit_results)*100:.1f}% - 是否最小命题")
        print(f"  ✓ SINGLE-CONCLUSION: {(len(self.audit_results)-multi_conclusion)/len(self.audit_results)*100:.1f}% - 是否单一结论")
        
        print(f"\n【关键发现】")
        if semantic_overreach > 0:
            print(f"  ⚠️ {semantic_overreach}条断言语义不最小化")
            for r in self.audit_results:
                if not r['semantic_minimal']:
                    print(f"     - {r['passage_id']}: {r['issues']}")
        
        if multi_conclusion > 0:
            print(f"  ⚠️ {multi_conclusion}条断言包含多重结论")
            for r in self.audit_results:
                if not r['single_conclusion']:
                    print(f"     - {r['passage_id']}: {r['issues']}")
        
        print(f"\n【生产方法稳定性】")
        if semantic_overreach == 0 and unsupported_condition == 0 and multi_conclusion == 0:
            print(f"  ✅ 所有质量指标达标")
            print(f"  ✓ 可以安全扩展到更大规模")
        else:
            print(f"  ❌ 部分质量指标未达标")
            print(f"  ⚠️ 需要先整改再扩大规模")
        
        # 保存结果
        output_file = r'D:\shuntian\backend\data\p0_8_9_quality_audit_v3.json'
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'total_candidates': len(sample),
            'passed': passed,
            'failed': failed,
            'pass_rate': passed / len(sample) * 100,
            'quality_metrics': {
                'semantic_overreach_rate': semantic_overreach / len(sample) * 100,
                'unsupported_condition_rate': unsupported_condition / len(sample) * 100,
                'multi_conclusion_rate': multi_conclusion / len(sample) * 100,
                'source_traceability_rate': source_traceability
            },
            'audit_details': self.audit_results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n结果已保存到 {output_file}")
        
        return result


if __name__ == '__main__':
    auditor = SemanticAuditorV3()
    auditor.run_full_audit([])
