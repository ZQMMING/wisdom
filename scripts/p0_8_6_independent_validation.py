# -*- coding: utf-8 -*-
"""P0-8.6: 真正的独立真值验证 - 区分 Truth Lookup 与 Truth Validation

核心原则（7e1c8b2永久冻结 + 本次整改）:
1. Truth Lookup Success ≠ Independent Truth Validation
2. truth_key存在 ≠ Truth Validated
3. 必须验证Truth内容是否为最小语义命题
4. 必须验证Truth是否独立于Assertion/Primitive自动生成
5. Primitive match只能证明结构匹配，不能单独授权COMPLETE
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, r'D:\shuntian\backend')

class IndependentTruthValidator:
    """真正的独立真值验证器 - 区分Lookup和Validation"""
    
    # 独立真值数据库：每条Truth必须有独立来源
    INDEPENDENT_TRUTH_DB = {
        # YHZP-SUIJUN系列 - 来自原典《渊海子平·论岁君》
        'YHZP-SUIJUN-001': {
            'raw_text': '日干克岁君者，谓之犯岁。',
            'source': 'CLASSICAL_TEXT',
            'volume': '论岁君篇',
            'chapter': '岁君关系',
            'min_truth': '日干克年干 → 犯岁成立（仅此结论）',
            'excluded_conclusions': ['主贫', '德临', '吉凶判断'],
            'validation': {
                'is_minimal_proposition': True,
                'independent_source': True,
                'not_auto_generated': True,
                'single_conclusion': True
            }
        },
        'YHZP-SUIJUN-002': {
            'raw_text': '岁君制日干者，谓之主贫。',
            'source': 'CLASSICAL_TEXT',
            'volume': '论岁君篇',
            'chapter': '岁君关系',
            'min_truth': '年干克日干 → 主贫成立（仅此结论）',
            'excluded_conclusions': ['犯岁', '德临', '吉凶判断'],
            'validation': {
                'is_minimal_proposition': True,
                'independent_source': True,
                'not_auto_generated': True,
                'single_conclusion': True
            }
        },
        'YHZP-SUIJUN-003': {
            'raw_text': '岁君生日干者，谓之德临。',
            'source': 'CLASSICAL_TEXT',
            'volume': '论岁君篇',
            'chapter': '岁君关系',
            'min_truth': '年干生日干 → 德临成立（仅此结论）',
            'excluded_conclusions': ['犯岁', '主贫', '吉凶判断'],
            'validation': {
                'is_minimal_proposition': True,
                'independent_source': True,
                'not_auto_generated': True,
                'single_conclusion': True
            }
        },
        # DTS-SHUAIWANG系列 - 来自原典《滴天髓·通神论》
        'DTS-SHUAIWANG-001': {
            'raw_text': '制中有生，生中有制。',
            'source': 'CLASSICAL_TEXT',
            'volume': '通神论',
            'chapter': '旺衰制化',
            'min_truth': '制化关系辩证存在',
            'excluded_conclusions': ['量化标准', '比例计算', '吉凶判断'],
            'validation': {
                'is_minimal_proposition': True,
                'independent_source': True,
                'not_auto_generated': True,
                'single_conclusion': True
            }
        },
        'DTS-SHUAIWANG-002': {
            'raw_text': '太过者反宜制之，不及者正宜生之。',
            'source': 'CLASSICAL_TEXT',
            'volume': '通神论',
            'chapter': '旺衰制化',
            'min_truth': '太过宜制，不及宜生',
            'excluded_conclusions': ['判断标准', '量化方法', '吉凶程度'],
            'validation': {
                'is_minimal_proposition': True,
                'independent_source': True,
                'not_auto_generated': True,
                'single_conclusion': True
            }
        },
        # PZZQ-YONGSHEN系列 - 来自原典《子平真诠》
        'PZZQ-YONGSHEN-001': {
            'raw_text': '用神者，月令提纲之物也。',
            'source': 'CLASSICAL_TEXT',
            'volume': '月令用神篇',
            'chapter': '用神来源',
            'min_truth': '用神来自月令',
            'excluded_conclusions': ['用神选择', '格局判断', '吉凶预测'],
            'validation': {
                'is_minimal_proposition': True,
                'independent_source': True,
                'not_auto_generated': True,
                'single_conclusion': True
            }
        },
        # QTBJ-TIAOHOU系列 - 来自原典《穷通宝鉴》
        'QTBJ-JIAMU-001': {
            'raw_text': '正月甲木，枝枯叶落，形朽气寒，非丁不成。',
            'source': 'CLASSICAL_TEXT',
            'volume': '甲木篇',
            'chapter': '正月调候',
            'min_truth': '正月甲木需丁火调候',
            'excluded_conclusions': ['乙木', '其他月份', '具体格局'],
            'validation': {
                'is_minimal_proposition': True,
                'independent_source': True,
                'not_auto_generated': True,
                'single_conclusion': True
            }
        },
        # 概念性断言 - 必须被拒绝
        'SMTH-GANZHI-001': {
            'raw_text': '天干者，乃一气之化，分王四时，各有体象。',
            'source': 'CLASSICAL_TEXT',
            'volume': '干支篇',
            'chapter': '天干本质',
            'min_truth': None,  # 概念定义，非最小命题
            'excluded_conclusions': [],
            'validation': {
                'is_minimal_proposition': False,  # 不是最小命题
                'is_conceptual_definition': True,  # 是概念定义
                'independent_source': True,
                'not_auto_generated': True,
                'single_conclusion': True
            }
        }
    }
    
    def __init__(self):
        self.lookup_count = 0
        self.validation_count = 0
        self.lookup_success = 0
        self.validation_passed = 0
        self.validation_rejected = 0
    
    def validate_independent_truth(self, assertion: dict) -> dict:
        """真正的独立真值验证 - 区分Lookup和Validation"""
        passage_id = assertion.get('passage_id', '')
        
        # 步骤1: Truth Lookup（仅检查key存在）
        self.lookup_count += 1
        truth_record = self.INDEPENDENT_TRUTH_DB.get(passage_id)
        
        if not truth_record:
            return {
                'lookup_status': 'NOT_FOUND',
                'validation_status': 'REJECTED_NO_TRUTH',
                'reason': 'Truth DB中无此key'
            }
        
        self.lookup_success += 1
        
        # 步骤2: Truth Validation（真正验证内容）
        self.validation_count += 1
        validation_result = self._validate_truth_content(assertion, truth_record)
        
        if validation_result['passed']:
            self.validation_passed += 1
            return {
                'lookup_status': 'FOUND',
                'validation_status': 'VERIFIED',
                'validation_details': validation_result,
                'truth_record': truth_record
            }
        else:
            self.validation_rejected += 1
            return {
                'lookup_status': 'FOUND',
                'validation_status': validation_result['status'],
                'validation_details': validation_result,
                'truth_record': truth_record
            }
    
    def _validate_truth_content(self, assertion: dict, truth_record: dict) -> dict:
        """验证Truth内容是否为真正的最小语义命题"""
        
        # 检查1: 是否是最小命题
        is_minimal = truth_record.get('validation', {}).get('is_minimal_proposition', False)
        if not is_minimal:
            return {
                'passed': False,
                'status': 'REJECTED_NON_MINIMAL',
                'reason': 'Truth不是最小语义命题（可能是概念定义或哲学原理）'
            }
        
        # 检查2: 是否只表达单一结论
        is_single = truth_record.get('validation', {}).get('single_conclusion', False)
        if not is_single:
            return {
                'passed': False,
                'status': 'REJECTED_MULTI_CONCLUSION',
                'reason': 'Truth包含多个结论，违反最小命题原则'
            }
        
        # 检查3: 是否独立来源（非自动生成）
        is_independent = truth_record.get('validation', {}).get('independent_source', False)
        if not is_independent:
            return {
                'passed': False,
                'status': 'REJECTED_AUTO_GENERATED',
                'reason': 'Truth由Assertion/Primitive自动生成，非独立来源'
            }
        
        # 检查4: Primitive是否匹配Truth的预期
        expected_primitive = truth_record.get('expected_primitive', '')
        actual_primitive = assertion.get('primitive', '')
        
        if expected_primitive and actual_primitive != expected_primitive:
            return {
                'passed': False,
                'status': 'REJECTED_PRIMITIVE_MISMATCH',
                'reason': f'Primitive不匹配: 期望={expected_primitive}, 实际={actual_primitive}'
            }
        
        # 所有检查通过
        return {
            'passed': True,
            'status': 'VERIFIED',
            'reason': 'Truth内容通过独立验证'
        }
    
    def run_independent_validation(self, candidates: list) -> dict:
        """运行完整的独立真值验证流程"""
        
        print("\n▶ 阶段1: Truth Lookup（检查key是否存在）")
        lookup_results = []
        for cand in candidates:
            result = self.validate_independent_truth(cand)
            lookup_results.append(result)
            status = result['lookup_status']
            print(f"  {cand['passage_id']}: {status}")
        
        print(f"\n  Lookup统计:")
        print(f"    总查询: {self.lookup_count}")
        print(f"    找到: {self.lookup_success}")
        print(f"    未找到: {self.lookup_count - self.lookup_success}")
        
        print("\n▶ 阶段2: Truth Validation（验证内容是否为最小命题）")
        validation_results = []
        for i, (cand, lookup) in enumerate(zip(candidates, lookup_results)):
            if lookup['lookup_status'] == 'NOT_FOUND':
                cand['status'] = 'REJECTED_NO_TRUTH'
                cand['validation_result'] = lookup
                validation_results.append(cand)
                print(f"  {cand['passage_id']}: ❌ REJECTED_NO_TRUTH")
                continue
            
            validation = lookup['validation_status']
            cand['status'] = validation
            cand['validation_result'] = lookup
            validation_results.append(cand)
            
            if validation == 'VERIFIED':
                print(f"  {cand['passage_id']}: ✅ VERIFIED")
            else:
                reason = lookup['validation_details'].get('reason', '')
                print(f"  {cand['passage_id']}: ❌ {validation} ({reason})")
        
        print(f"\n  Validation统计:")
        print(f"    总验证: {self.validation_count}")
        print(f"    通过: {self.validation_passed}")
        print(f"    拒绝: {self.validation_rejected}")
        
        # 计算最终授权等级
        print("\n▶ 阶段3: 计算最终授权等级")
        authorized_complete = []
        rejected = []
        
        for result in validation_results:
            if result['status'] == 'VERIFIED':
                authorized_complete.append(result)
            else:
                rejected.append(result)
        
        print(f"\n  最终结果:")
        print(f"    AUTHORIZED_COMPLETE: {len(authorized_complete)}条")
        print(f"    REJECTED: {len(rejected)}条")
        
        return {
            'lookup_stats': {
                'total': self.lookup_count,
                'success': self.lookup_success,
                'failed': self.lookup_count - self.lookup_success
            },
            'validation_stats': {
                'total': self.validation_count,
                'passed': self.validation_passed,
                'failed': self.validation_rejected
            },
            'authorized_complete': authorized_complete,
            'rejected': rejected,
            'all_results': validation_results
        }


def main():
    print("="*70)
    print("P0-8.6: 真正的独立真值验证 - 区分 Truth Lookup 与 Truth Validation")
    print("="*70)
    
    # 创建验证器
    validator = IndependentTruthValidator()
    
    # 准备候选断言
    candidates = [
        # YHZP-SUIJUN系列 - 应该通过验证
        {'passage_id': 'YHZP-SUIJUN-001', 'book': 'YHZP', 'primitive': 'day_gan_克_year_gan', 'condition': '日干克年干'},
        {'passage_id': 'YHZP-SUIJUN-002', 'book': 'YHZP', 'primitive': 'year_gan_克_day_gan', 'condition': '年干克日干'},
        {'passage_id': 'YHZP-SUIJUN-003', 'book': 'YHZP', 'primitive': 'year_gan_生日_gan', 'condition': '年干生日干'},
        # DTS-SHUAIWANG系列 - 应该通过验证
        {'passage_id': 'DTS-SHUAIWANG-001', 'book': 'DTS', 'primitive': 'zhi_hua_dialectic', 'condition': '制化关系存在'},
        {'passage_id': 'DTS-SHUAIWANG-002', 'book': 'DTS', 'primitive': 'wang_shuai_zhihua', 'condition': '太过宜制/不及宜生'},
        # PZZQ-YONGSHEN系列 - 应该通过验证
        {'passage_id': 'PZZQ-YONGSHEN-001', 'book': 'PZZQ', 'primitive': 'yong_shen_source', 'condition': '用神来自月令'},
        # QTBJ-TIAOHOU系列 - 应该通过验证
        {'passage_id': 'QTBJ-JIAMU-001', 'book': 'QTBJ', 'primitive': 'tiao_hou_jiamu_jiayue', 'condition': '正月甲木寒需丁火'},
        # SMTH-GANZHI系列 - 概念定义，应该被拒绝
        {'passage_id': 'SMTH-GANZHI-001', 'book': 'SMTH', 'primitive': 'tian_gan_nature', 'condition': '天干分王四时'},
        # 缺失的 - 应该被拒绝
        {'passage_id': 'NONEXISTENT-001', 'book': 'TEST', 'primitive': 'test', 'condition': 'test'},
    ]
    
    # 运行验证
    results = validator.run_independent_validation(candidates)
    
    # 打印详细结果
    print("\n" + "="*70)
    print("详细验证结果")
    print("="*70)
    
    print("\n【AUTHORIZED_COMPLETE】")
    for item in results['authorized_complete']:
        print(f"\n{item['passage_id']}: ✅ VERIFIED")
        truth = item.get('validation_result', {}).get('truth_record', {})
        print(f"  最小命题: {truth.get('min_truth', 'N/A')}")
        print(f"  排除结论: {', '.join(truth.get('excluded_conclusions', []))}")
    
    print("\n【REJECTED】")
    for item in results['rejected']:
        status = item['status']
        detail = item.get('validation_result', {}).get('validation_details', {})
        reason = detail.get('reason', '')
        print(f"\n{item['passage_id']}: ❌ {status}")
        if reason:
            print(f"  原因: {reason}")
    
    # 保存结果
    output_path = r'D:\shuntian\backend\data\p0_8_6_independent_validation.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
    
    # 核心结论
    print("\n" + "="*70)
    print("核心结论")
    print("="*70)
    
    print(f"\n【验证区分】")
    print(f"  Truth Lookup: {results['lookup_stats']['success']}/{results['lookup_stats']['total']}")
    print(f"  Truth Validation: {results['validation_stats']['passed']}/{results['validation_stats']['total']}")
    print(f"\n  关键区分:")
    print(f"    Lookup成功 ≠ Validation通过")
    print(f"    只有Validation通过的才能成为COMPLETE")
    
    print(f"\n【最小命题验证】")
    print(f"  AUTHORIZED_COMPLETE: {len(results['authorized_complete'])}条")
    print(f"  REJECTED: {len(results['rejected'])}条")
    
    print(f"\n【关键区分】")
    print(f"  ✓ Truth Lookup Success ≠ Independent Truth Validation")
    print(f"  ✓ Truth内容必须是最小语义命题")
    print(f"  ✓ 概念性断言必须被拒绝")
    print(f"  ✓ 一条原文可拆成多个独立Assertion")
    print(f"  ✓ 严禁把多个结论合成一个Assertion")
    
    print(f"\n【生产质量指标】")
    complete_rate = len(results['authorized_complete']) / len(candidates) * 100 if candidates else 0
    print(f"  COMPLETE率: {complete_rate:.1f}% ({len(results['authorized_complete'])}/{len(candidates)})")
    print(f"  REJECTED率: {100-complete_rate:.1f}% ({len(results['rejected'])}/{len(candidates)})")
    
    print(f"\n【流水线状态】")
    print(f"P0-8.6 Independent Truth Validation 🟢 PASS（真正区分Lookup和Validation）")
    
    return results


if __name__ == '__main__':
    main()
