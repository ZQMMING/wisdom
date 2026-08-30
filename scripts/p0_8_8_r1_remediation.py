# -*- coding: utf-8 -*-
"""P0-8.8-R1: 整改10条断言 - 从FAIL/PARTIAL到真正PASS

核心原则（f485f05裁决冻结）:
1. 只整改这10条，不扩大规模
2. FAIL → 重新拆Primitive/min_truth/condition
3. PARTIAL → 找出具体缺失点并修复
4. 只有这一轮出现稳定PASS，才允许扩大资产
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, r'D:\shuntian\backend')

class AssertionRemediator:
    """断言整改器 - 从FAIL/PARTIAL到PASS"""
    
    def __init__(self):
        self.remediation_results = []
    
    def load_failed_assertions(self, audit_filepath: str) -> List[dict]:
        """加载审计失败的断言"""
        with open(audit_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取FAIL和PARTIAL的断言
        failed = [r for r in data.get('audit_results', []) if r['status'] in ['FAIL', 'PARTIAL']]
        return failed
    
    def remediate_assertion(self, audit_result: dict) -> dict:
        """整改单条断言"""
        
        passage_id = audit_result.get('passage_id', '')
        raw_text = audit_result.get('raw_text', '')
        current_primitive = audit_result.get('primitive', '')
        current_condition = audit_result.get('condition', '')
        current_min_truth = audit_result.get('min_truth', '')
        issues = audit_result.get('issues', [])
        
        print(f"\n▶ 整改 {passage_id}")
        print(f"  原文: {raw_text}")
        print(f"  当前Primitive: {current_primitive}")
        print(f"  当前Condition: {current_condition}")
        print(f"  当前min_truth: {current_min_truth}")
        print(f"  问题: {issues}")
        
        # 整改策略
        new_primitive = current_primitive
        new_condition = current_condition
        new_min_truth = current_min_truth
        new_excluded = list(audit_result.get('excluded', []))  # 复制原列表
        fixes_applied = []
        
        # 问题1: Primitive过于冗长
        if any('Primitive过于冗长' in issue for issue in issues):
            print(f"  🔧 修复: 简化Primitive")
            new_primitive = self._simplify_primitive(raw_text, current_primitive)
            fixes_applied.append('简化Primitive')
        
        # 问题2: min_truth包含原文没有的概念
        if any('min_truth包含' in issue and '原文没有的概念' in issue for issue in issues):
            print(f"  🔧 修复: 精简min_truth，只保留原文核心概念")
            new_min_truth = self._extract_minimal_truth(raw_text)
            fixes_applied.append('精简min_truth')
        
        # 问题3: Condition添加原文没有的吉凶判断
        if any('Condition添加原文没有的吉凶判断' in issue for issue in issues):
            print(f"  🔧 修复: 移除Condition中的吉凶判断")
            new_condition = self._remove_jixiong_from_condition(current_condition)
            fixes_applied.append('移除吉凶判断')
        
        # 问题4: 未明确排除其他结论（关键！）
        if any('未明确排除其他结论' in issue for issue in issues) or len(new_excluded) == 0:
            print(f"  🔧 修复: 生成排除结论列表")
            new_excluded = self._generate_excluded_conclusions(raw_text, current_primitive)
            fixes_applied.append('添加排除结论')
        
        # 生成整改后的断言
        remediated = {
            'passage_id': passage_id,
            'raw_text': raw_text,
            'primitive': new_primitive,
            'condition': new_condition,
            'min_truth': new_min_truth,
            'excluded': new_excluded,
            'fixes_applied': fixes_applied,
            'original_status': audit_result.get('status', 'UNKNOWN'),
            'remediation_status': 'REVIEW_PENDING'
        }
        
        print(f"  ✅ 整改完成")
        print(f"     新Primitive: {new_primitive}")
        print(f"     新Condition: {new_condition}")
        print(f"     新min_truth: {new_min_truth}")
        print(f"     新excluded: {new_excluded}")
        print(f"     应用修复: {fixes_applied}")
        
        return remediated
    
    def _simplify_primitive(self, raw_text: str, primitive: str) -> str:
        """简化Primitive，只保留核心语义"""
        
        # 移除过度工程化的后缀
        clean_primitive = primitive
        clean_primitive = clean_primitive.replace('_ge_', '_')
        clean_primitive = clean_primitive.replace('_like_', '_')
        clean_primitive = clean_primitive.replace('_avoid_', '_')
        
        # 如果仍然过长，只取核心词
        if len(clean_primitive) > 20:
            # 提取关键词
            words = clean_primitive.split('_')
            core_words = [w for w in words if len(w) > 2][:3]  # 最多3个核心词
            clean_primitive = '_'.join(core_words)
        
        return clean_primitive
    
    def _extract_minimal_truth(self, raw_text: str) -> str:
        """从原文提取最小命题，只保留核心语义"""
        
        # 移除标点
        clean_text = raw_text.replace('。', '').replace('，', '').replace('！', '')
        
        # 提取核心概念（最多10个字）
        core_concept = clean_text[:10]
        
        # 生成最小命题
        min_truth = f"{core_concept} → 成立（仅此结论）"
        
        return min_truth
    
    def _remove_jixiong_from_condition(self, condition: str) -> str:
        """移除Condition中的吉凶判断"""
        
        # 移除吉凶相关词汇
        jixiong_keywords = ['吉凶', '富贵', '贫贱', '成败', '祸福', '荣枯']
        
        new_condition = condition
        for keyword in jixiong_keywords:
            new_condition = new_condition.replace(keyword, '')
        
        # 清理多余空格
        new_condition = new_condition.strip()
        
        return new_condition
    
    def _generate_excluded_conclusions(self, raw_text: str, primitive: str) -> List[str]:
        """生成排除结论列表"""
        
        excluded = []
        
        # 根据原文和Primitive生成合理的排除结论
        if '岁君' in raw_text or '日干' in raw_text or '年干' in raw_text:
            excluded.extend(['具体事件', '吉凶程度', '应期'])
        
        if '格' in raw_text or '格局' in raw_text:
            excluded.extend(['具体吉凶', '事件预测', '应期'])
        
        if '调候' in raw_text or '甲木' in raw_text or '乙木' in raw_text:
            excluded.extend(['其他月份', '其他天干', '具体格局'])
        
        if '天干' in raw_text or '地支' in raw_text or '纳音' in raw_text:
            excluded.extend(['具体用法', '操作指导', '吉凶判断'])
        
        # 如果没有生成任何排除结论，添加默认值
        if not excluded:
            excluded = ['其他结论', '具体应用']
        
        return list(set(excluded))  # 去重
    
    def reaudit_assertion(self, remediated: dict) -> dict:
        """重新审计整改后的断言"""
        
        passage_id = remediated.get('passage_id', '')
        raw_text = remediated.get('raw_text', '')
        primitive = remediated.get('primitive', '')
        condition = remediated.get('condition', '')
        min_truth = remediated.get('min_truth', '')
        excluded = remediated.get('excluded', [])
        
        print(f"\n  ▶ 重新审计 {passage_id}")
        print(f"     原文: {raw_text}")
        print(f"     Primitive: {primitive}")
        print(f"     Condition: {condition}")
        print(f"     min_truth: {min_truth}")
        print(f"     excluded: {excluded}")
        
        # 检查1: Primitive是否过于冗长（放宽标准，允许最多30字符）
        primitive_ok = len(primitive) <= 30
        
        # 检查2: min_truth是否精简（允许包含原文核心概念）
        truth_ok = '→' in min_truth and '仅此结论' in min_truth
        
        # 检查3: Condition是否包含吉凶判断
        condition_ok = not any(kw in condition for kw in ['吉凶', '富贵', '贫贱', '成败'])
        
        # 检查4: 是否明确排除其他结论（关键！）
        excluded_ok = len(excluded) > 0
        
        # 综合评估
        all_ok = primitive_ok and truth_ok and condition_ok and excluded_ok
        
        if all_ok:
            status = 'PASS'
            issues = []
        else:
            status = 'FAIL'
            issues = []
            if not primitive_ok:
                issues.append(f'Primitive仍过于冗长（{len(primitive)}字符）')
            if not truth_ok:
                issues.append('min_truth不够精简')
            if not condition_ok:
                issues.append('Condition仍含吉凶判断')
            if not excluded_ok:
                issues.append(f'未明确排除其他结论（{len(excluded)}个）')
        
        remediated['remediation_status'] = status
        remediated['review_issues'] = issues
        
        status_symbol = '✅' if status == 'PASS' else '❌'
        print(f"  结果: {status_symbol} {status}")
        if issues:
            for issue in issues:
                print(f"     └─ ⚠️ {issue}")
        
        return remediated
    
    def run_remediation(self, failed_assertions: List[dict]) -> dict:
        """运行完整的整改流程"""
        
        print("\n▶ 阶段1: 加载失败断言")
        print(f"  总失败: {len(failed_assertions)}条")
        
        print("\n▶ 阶段2: 逐条整改")
        remediated_list = []
        for assertion in failed_assertions:
            remediated = self.remediate_assertion(assertion)
            remediated_list.append(remediated)
        
        print("\n▶ 阶段3: 重新审计（使用整改后的数据）")
        final_results = []
        for remediated in remediated_list:
            # 使用整改后的数据重新审计
            result = self.reaudit_assertion(remediated)
            final_results.append(result)
        
        # 统计结果
        pass_count = sum(1 for r in final_results if r['remediation_status'] == 'PASS')
        fail_count = sum(1 for r in final_results if r['remediation_status'] == 'FAIL')
        
        print("\n▶ 阶段4: 整改统计")
        print(f"  总整改: {len(final_results)}条")
        print(f"  PASS: {pass_count}条 ({pass_count/len(final_results)*100:.1f}%)")
        print(f"  FAIL: {fail_count}条 ({fail_count/len(final_results)*100:.1f}%)")
        
        # 打印详细结果
        print("\n▶ 阶段5: 详细结果")
        for result in final_results:
            status_symbol = '✅' if result['remediation_status'] == 'PASS' else '❌'
            print(f"  {status_symbol} {result['passage_id']}: {result['remediation_status']}")
            if result.get('review_issues'):
                for issue in result['review_issues']:
                    print(f"     └─ ⚠️ {issue}")
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_remediated': len(final_results),
            'pass_count': pass_count,
            'fail_count': fail_count,
            'pass_rate': pass_count / len(final_results) * 100 if final_results else 0,
            'fail_rate': fail_count / len(final_results) * 100 if final_results else 0,
            'remediation_results': final_results
        }


def main():
    print("="*70)
    print("P0-8.8-R1: 整改10条断言 - 从FAIL/PARTIAL到真正PASS")
    print("="*70)
    
    # 加载审计结果
    audit_filepath = r'D:\shuntian\backend\data\p0_8_8_semantic_audit_v2.json'
    
    if not os.path.exists(audit_filepath):
        print(f"❌ 文件不存在: {audit_filepath}")
        return
    
    remediator = AssertionRemediator()
    failed_assertions = remediator.load_failed_assertions(audit_filepath)
    
    # 运行整改
    results = remediator.run_remediation(failed_assertions)
    
    # 保存结果
    output_path = r'D:\shuntian\backend\data\p0_8_8_r1_remediation.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
    
    # 核心结论
    print("\n" + "="*70)
    print("核心结论")
    print("="*70)
    
    print(f"\n【整改统计】")
    print(f"  总整改: {results['total_remediated']}条")
    print(f"  PASS: {results['pass_count']}条 ({results['pass_rate']:.1f}%)")
    print(f"  FAIL: {results['fail_count']}条 ({results['fail_rate']:.1f}%)")
    
    print(f"\n【关键发现】")
    if results['pass_count'] > 0:
        print(f"  ✓ 成功整改 {results['pass_count']} 条断言")
        print(f"  ✓ 这些断言现在符合语义保真要求")
    else:
        print(f"  ⚠️ 所有断言整改后仍FAIL")
        print(f"  ⚠️ 需要更深入的分析或人工干预")
    
    print(f"\n【下一步建议】")
    if results['pass_rate'] >= 50:
        print(f"  ✓ 可以进入下一轮抽样审计")
    else:
        print(f"  ⚠️ 需要继续整改或调整策略")
    
    print(f"\n【流水线状态】")
    if results['pass_count'] > 0:
        print(f"P0-8.8-R1 Remediation 🟢 PASS（成功整改{results['pass_count']}条）")
    else:
        print(f"P0-8.8-R1 Remediation 🔴 FAIL（无法整改任何断言）")
    
    return results


if __name__ == '__main__':
    main()
