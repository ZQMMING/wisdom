# -*- coding: utf-8 -*-
"""P0-8.9 Condition层重构 - 必须有condition_evidence支持

核心原则（6286a1d裁决冻结）:
1. Condition不能再是min_truth的自然语言改写
2. Condition必须有condition_evidence，明确指出原典支持该Condition的文本片段
3. 如果原典只表达关系（如"日干克岁君→犯岁"），不要擅自改写成工程条件
4. Primitive可以是规范化计算字段，但必须标记derived_from=canonical_relation
5. Condition无直接Evidence → UNSUPPORTED_CONDITION，不得COMPLETE
"""

import json
import sys
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, r'D:\shuntian\backend')

class ConditionAuditor:
    """Condition层审计器 - 严格验证Condition的证据支持"""
    
    def __init__(self):
        self.audit_results = []
    
    def load_assertions(self, filepath: str) -> List[dict]:
        """加载断言资产"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('verified_assertions', [])
    
    def audit_assertion(self, assertion: dict) -> dict:
        """逐条审计Condition"""
        
        passage_id = assertion.get('passage_id', '')
        raw_text = assertion.get('raw_text', '')
        min_truth = assertion.get('min_truth', '')
        primitive = assertion.get('primitive', '')
        condition = assertion.get('condition', '')
        condition_evidence = assertion.get('condition_evidence', '')
        
        print(f"\n▶ 审计 {passage_id}")
        print(f"  原文: {raw_text}")
        print(f"  min_truth: {min_truth}")
        print(f"  primitive: {primitive}")
        print(f"  condition: {condition}")
        print(f"  condition_evidence: {condition_evidence}")
        
        issues = []
        
        # Check 1: SOURCE-PURE（min_truth字符来源）
        source_pure = self._check_source_pure(raw_text, min_truth)
        if not source_pure:
            issues.append(f'source_impure: min_truth包含原文没有的字')
        
        # Check 2: SEMANTIC-MINIMAL（是否最小命题）
        semantic_minimal, minimal_explanation = self._check_semantic_minimal(raw_text, min_truth)
        if not semantic_minimal:
            issues.append(f'semantic_not_minimal: {minimal_explanation}')
        
        # Check 3: SINGLE-CONCLUSION（是否单一结论）
        single_conclusion = self._check_single_conclusion(raw_text, min_truth)
        if not single_conclusion:
            issues.append(f'multi_conclusion: 包含多重结论')
        
        # Check 4: CONDITION-EVIDENCE（Condition是否有原典证据支持）← 核心！
        condition_valid, condition_explanation = self._check_condition_evidence(
            raw_text, condition, condition_evidence
        )
        if not condition_valid:
            issues.append(f'unsupported_condition: {condition_explanation}')
        
        # Check 5: PRIMITIVE-PROVENANCE（Primitive是否有原典来源标记）
        primitive_provenance = self._check_primitive_provenance(primitive, assertion)
        if not primitive_provenance:
            issues.append(f'primitive_unprovenanced: Primitive缺少derived_from标记')
        
        # 判定结果
        status = 'PASS' if len(issues) == 0 else 'FAIL'
        
        result = {
            'passage_id': passage_id,
            'raw_text': raw_text,
            'min_truth': min_truth,
            'primitive': primitive,
            'condition': condition,
            'condition_evidence': condition_evidence,
            'status': status,
            'issues': issues,
            'source_pure': source_pure,
            'semantic_minimal': semantic_minimal,
            'single_conclusion': single_conclusion,
            'condition_valid': condition_valid,
            'primitive_provenance': primitive_provenance
        }
        
        self.audit_results.append(result)
        
        # 打印结果
        if status == 'PASS':
            print(f"  ✅ 全部通过")
        else:
            print(f"  ❌ FAIL: {issues}")
        
        return result
    
    def _check_source_pure(self, raw_text: str, min_truth: str) -> bool:
        """检查min_truth是否100%由原文汉字组成"""
        raw_chars = set([c for c in raw_text if '\u4e00' <= c <= '\u9fff'])
        for char in min_truth:
            if '\u4e00' <= char <= '\u9fff' and char not in raw_chars:
                return False
        return True
    
    def _check_semantic_minimal(self, raw_text: str, min_truth: str) -> Tuple[bool, str]:
        """检查是否语义最小化"""
        # 检查复合结构
        positive_patterns = [
            (r'^(.+)(?:，|，)(.+)$', '包含逗号分隔的多个语义单元'),
            (r'^(.{2,4})(富贵|贫贱|吉凶|祸福|成败|荣枯)(.+)$', '条件+结论结构'),
        ]
        
        for pattern, explanation in positive_patterns:
            if re.match(pattern, min_truth):
                return False, explanation
        
        chinese_count = len([c for c in min_truth if '\u4e00' <= c <= '\u9fff'])
        if chinese_count > 10:
            return False, f'语义单元过多（{chinese_count}字）'
        
        common_conditions = ['中和', '平衡', '旺相', '休囚', '得令', '失令']
        common_conclusions = ['富贵', '贫贱', '吉凶', '成败', '祸福']
        
        has_condition = any(c in min_truth for c in common_conditions)
        has_conclusion = any(c in min_truth for c in common_conclusions)
        
        if has_condition and has_conclusion:
            return False, '同时包含条件词和结论词'
        
        return True, '语义最小化'
    
    def _check_single_conclusion(self, raw_text: str, min_truth: str) -> bool:
        """检查是否单一结论"""
        conclusion_markers = ['谓之', '主', '主贫', '主富', '主贵', '主贱']
        marker_count = sum(1 for m in conclusion_markers if m in min_truth)
        
        if marker_count > 1:
            return False
        
        if '富贵' in min_truth or '贫贱' in min_truth:
            return False
        
        return True
    
    def _check_condition_evidence(self, raw_text: str, condition: str, condition_evidence: str) -> Tuple[bool, str]:
        """检查Condition是否有原典证据支持（核心！）"""
        
        # 如果condition为空，可能是合理的设计选择
        if not condition:
            return True, 'Condition为空（合理设计）'
        
        # 必须有condition_evidence
        if not condition_evidence:
            return False, '缺少condition_evidence字段'
        
        # condition_evidence必须是raw_text的子串
        if condition_evidence not in raw_text:
            return False, f'condition_evidence "{condition_evidence}" 不是原文的子串'
        
        # condition必须与condition_evidence相关
        # 不能是"翻译"或"改写"，而应该是condition_evidence的直接提取
        cond_clean = condition.replace('。', '').replace('，', '')
        evid_clean = condition_evidence.replace('。', '').replace('，', '')
        
        # 如果condition完全不同于evidence，说明在"翻译"
        if cond_clean != evid_clean and not self._is_substring(evid_clean, cond_clean):
            return False, f'Condition在翻译原文而非提取证据（evidence: {evid_clean}, condition: {cond_clean}）'
        
        return True, 'Condition有原典证据支持'
    
    def _is_substring(self, substr: str, text: str) -> bool:
        """检查substr是否是text的子串（忽略空格）"""
        return substr.replace(' ', '').replace('\t', '') in text.replace(' ', '').replace('\t', '')
    
    def _check_primitive_provenance(self, primitive: str, assertion: dict) -> bool:
        """检查Primitive是否有原典来源标记"""
        # Primitive必须标记derived_from或canonical_relation
        if 'derived_from' in assertion or 'canonical_relation' in assertion:
            return True
        
        # 或者Primitive本身就是规范化的关系描述（如day_gan_克_year_gan）
        if '_' in primitive and '克' in primitive or '生' in primitive or '比' in primitive:
            return True
        
        return False
    
    def run_full_audit(self, assertions: List[dict]) -> dict:
        """运行完整审计"""
        
        print("="*70)
        print("P0-8.9 Condition层重构审计 - 必须有condition_evidence支持")
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
        
        print(f"\n▶ 阶段2: 逐条Condition层审计")
        
        for i, assertion in enumerate(sample):
            self.audit_assertion(assertion)
        
        print(f"\n▶ 阶段3: 审计统计")
        
        passed = sum(1 for r in self.audit_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.audit_results if r['status'] == 'FAIL')
        
        print(f"  总审计: {len(self.audit_results)}条")
        print(f"  PASS: {passed}条 ({passed/len(self.audit_results)*100:.1f}%)")
        print(f"  FAIL: {failed}条 ({failed/len(self.audit_results)*100:.1f}%)")
        
        # 计算质量指标
        unsupported_condition = sum(1 for r in self.audit_results if not r['condition_valid'])
        semantic_overreach = sum(1 for r in self.audit_results if not r['semantic_minimal'])
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
        
        print(f"\n【Condition层审计区分】")
        print(f"  ✓ SOURCE-PURE: {source_traceability:.1f}% - 字符是否来自原文")
        print(f"  ✓ SEMANTIC-MINIMAL: {(len(self.audit_results)-semantic_overreach)/len(self.audit_results)*100:.1f}% - 是否最小命题")
        print(f"  ✓ SINGLE-CONCLUSION: {(len(self.audit_results)-multi_conclusion)/len(self.audit_results)*100:.1f}% - 是否单一结论")
        print(f"  ✓ CONDITION-EVIDENCE: {(len(self.audit_results)-unsupported_condition)/len(self.audit_results)*100:.1f}% - Condition是否有原典证据")
        
        print(f"\n【关键发现】")
        if unsupported_condition > 0:
            print(f"  ⚠️ {unsupported_condition}条断言Condition无原典证据支持")
            for r in self.audit_results:
                if not r['condition_valid']:
                    print(f"     - {r['passage_id']}: {r['issues']}")
        
        print(f"\n【生产方法稳定性】")
        if semantic_overreach == 0 and unsupported_condition == 0 and multi_conclusion == 0:
            print(f"  ✅ 所有质量指标达标")
            print(f"  ✓ 可以安全扩展到更大规模")
        else:
            print(f"  ❌ 部分质量指标未达标")
            print(f"  ⚠️ 需要先整改再扩大规模")
        
        # 保存结果
        output_file = r'D:\shuntian\backend\data\p0_8_9_condition_audit.json'
        
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
    auditor = ConditionAuditor()
    auditor.run_full_audit([])
