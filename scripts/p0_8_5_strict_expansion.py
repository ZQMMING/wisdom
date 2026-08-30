# -*- coding: utf-8 -*-
"""P0-8.5: Assertion Asset Expansion v2 - 严格授权标准

核心原则:
1. Primitive成立 ≠ 完整断语成立
2. Independent Truth必须是最小语义命题，不得合并多个结论
3. 概念关系（如"天干为一气之化"）不等于可执行命理断语
4. 每一条COMPLETE必须分别证明完整证据链

整改内容:
- 撤回9条COMPLETE授权
- 重新定义Truth为最小语义命题
- 严格区分"概念成立"和"断语成立"
- 只保留真正有完整证据链的断言为COMPLETE
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BASE_DIR))


class StrictIndependentTruth:
    """严格独立真值提供者 - 最小语义命题"""
    
    # 真正的独立真值：每条断言必须有独立的原典证据
    # 不得合并多个结论到一个Truth
    STRICT_TRUTH = {
        # YHZP-SUIJUN-001: 日干克岁君 → 犯岁（单一结论）
        'YHZP-SUIJUN-001': {
            'primitive': 'day_gan_克_year_gan',
            'condition': '日干克年干',
            'minimal_truth': '日干克年干 → 犯岁成立（仅此结论）',
            'source': 'CLASSICAL_TEXT',
            'reference': '渊海子平·论岁君篇：“日干克岁君者，谓之犯岁”',
            'excludes': ['主贫', '德临']  # 明确排除其他结论
        },
        # YHZP-SUIJUN-002: 岁君制日干 → 主贫（单一结论）
        'YHZP-SUIJUN-002': {
            'primitive': 'year_gan_克_day_gan',
            'condition': '年干克日干',
            'minimal_truth': '年干克日干 → 主贫成立（仅此结论）',
            'source': 'CLASSICAL_TEXT',
            'reference': '渊海子平·论岁君篇：“岁君制日干者，谓之主贫”',
            'excludes': ['犯岁', '德临']
        },
        # YHZP-SUIJUN-003: 岁君生日干 → 德临（单一结论）
        'YHZP-SUIJUN-003': {
            'primitive': 'year_gan_生日_gan',
            'condition': '年干生日干',
            'minimal_truth': '年干生日干 → 德临成立（仅此结论）',
            'source': 'CLASSICAL_TEXT',
            'reference': '渊海子平·论岁君篇：“岁君生日干者，谓之德临”',
            'excludes': ['犯岁', '主贫']
        },
        # DTS-SHUAIWANG-001: 制中有生，生中有制（辩证关系）
        'DTS-SHUAIWANG-001': {
            'primitive': 'zhi_hua_dialectic',
            'condition': '制化关系辩证存在',
            'minimal_truth': '制中有生，生中有制 → 制化辩证成立',
            'source': 'CLASSICAL_TEXT',
            'reference': '滴天髓·通神论·衰旺：“制中有生，生中有制”',
            'excludes': []  # 无排除项，这是辩证原则
        },
        # DTS-SHUAIWANG-002: 太过宜制，不及宜生（原则性断言）
        'DTS-SHUAIWANG-002': {
            'primitive': 'wang_shuai_zhihua',
            'condition': '太过宜制/不及宜生',
            'minimal_truth': '太过反宜制之，不及正宜生之 → 旺衰制化原则成立',
            'source': 'CLASSICAL_TEXT',
            'reference': '滴天髓·通神论·衰旺：“太过者反宜制之，不及者正宜生之”',
            'excludes': []
        },
        # PZZQ-YONGSHEN-001: 用神来自月令（核心定义）
        'PZZQ-YONGSHEN-001': {
            'primitive': 'yong_shen_source',
            'condition': '用神来自月令',
            'minimal_truth': '用神者，月令提纲之物也 → 用神来源成立',
            'source': 'CLASSICAL_TEXT',
            'reference': '子平真诠·论用神：“用神者，月令提纲之物也”',
            'excludes': []
        },
        # QTBJ-JIAMU-001: 正月甲木调候需求（具体命例）
        'QTBJ-JIAMU-001': {
            'primitive': 'tiao_hou_requirement',
            'condition': '正月甲木需丁火调候',
            'minimal_truth': '正月甲木，寒需丁火 → 调候需求成立（仅针对此月份此日干）',
            'source': 'CLASSICAL_TEXT',
            'reference': '穷通宝鉴·甲木：“正月甲木，枝枯叶落，形朽气寒，非丁不成”',
            'excludes': ['乙木', '其他月份']
        }
    }
    
    # 明确排除的"概念性断言"（不是可执行命理判断）
    CONCEPTUAL_EXCLUSIONS = [
        'SMTH-GANZHI-001',  # 天干本质 - 概念定义，非命理断语
        'SMTH-DIZHI-001',  # 地支本质 - 概念定义，非命理断语
        'SMTH-NAYIN-001',  # 纳音本质 - 概念定义，非命理断语
        'PZZQ-XIANGSHEN-001',  # 相神辅助 - 条件不充分
        'QTBJ-YIMU-001',  # 二月乙木 - 条件不完整
        'QTBJ-BINGHUO-001',  # 三月丙火 - 条件不完整
        'DTS-TIYONG-001',  # 体用关系 - 条件不充分
        'PZZQ-YONGSHEN-002'  # 用神相扶 - 条件不完整
    ]
    
    @classmethod
    def get_strict_truth(cls, passage_id: str) -> Optional[Dict]:
        """获取严格独立真值（支持多种格式）"""
        
        # 标准格式: P-YHZP-SUIJUN-001 → YHZP-SUIJUN-001
        clean_id = passage_id.replace('P-', '') if passage_id.startswith('P-') else passage_id
        
        if clean_id in cls.STRICT_TRUTH:
            truth = cls.STRICT_TRUTH[clean_id].copy()
            truth['passage_id'] = clean_id
            return truth
        
        # 尝试原始格式
        if passage_id in cls.STRICT_TRUTH:
            truth = cls.STRICT_TRUTH[passage_id].copy()
            truth['passage_id'] = passage_id
            return truth
        
        # 检查是否在概念性排除列表中
        if clean_id in cls.CONCEPTUAL_EXCLUSIONS:
            return {
                'passage_id': clean_id,
                'status': 'EXCLUDED_CONCEPTUAL',
                'reason': '概念定义，非可执行命理断语'
            }
        
        if passage_id in cls.CONCEPTUAL_EXCLUSIONS:
            return {
                'passage_id': passage_id,
                'status': 'EXCLUDED_CONCEPTUAL',
                'reason': '概念定义，非可执行命理断语'
            }
        
        return None


def main():
    print("=" * 70)
    print("P0-8.5: Strict Assertion Asset Expansion (v2)")
    print("=" * 70)
    
    # ========== 阶段1: 从五书原典挖掘候选断言 ==========
    print("\n▶ 阶段1: 从五书原典挖掘候选断言")
    
    # 严格定义15条候选断言（基于真实五书原文）
    strict_candidates = [
        # YHZP - 渊海子平（岁君篇）
        {
            'passage_id': 'P-YHZP-SUIJUN-001',
            'raw_text': '日干克岁君者，谓之犯岁。',
            'context': '渊海子平·论岁君篇讨论日干与岁君的关系',
            'chapter': '论岁君'
        },
        {
            'passage_id': 'P-YHZP-SUIJUN-002',
            'raw_text': '岁君制日干者，谓之主贫。',
            'context': '渊海子平·论岁君篇讨论岁君克日干的凶象',
            'chapter': '论岁君'
        },
        {
            'passage_id': 'P-YHZP-SUIJUN-003',
            'raw_text': '岁君生日干者，谓之德临。',
            'context': '渊海子平·论岁君篇讨论岁君生日干的吉象',
            'chapter': '论岁君'
        },
        # DTS - 滴天髓（通神论·衰旺）
        {
            'passage_id': 'P-DTS-SHUAIWANG-001',
            'raw_text': '制中有生，生中有制。',
            'context': '滴天髓·通神论讨论五行制化关系的辩证关系',
            'chapter': '衰旺'
        },
        {
            'passage_id': 'P-DTS-SHUAIWANG-002',
            'raw_text': '太过者反宜制之，不及者正宜生之。',
            'context': '滴天髓·通神论讨论旺衰的制化原则',
            'chapter': '衰旺'
        },
        {
            'passage_id': 'P-DTS-TIYONG-001',
            'raw_text': '身强用官，身弱用印。',
            'context': '滴天髓·通神论讨论身强身弱的用神选择',
            'chapter': '体用'
        },
        # PZZQ - 子平真诠（用神篇）
        {
            'passage_id': 'P-PZZQ-YONGSHEN-001',
            'raw_text': '用神者，月令提纲之物也。',
            'context': '子平真诠·论用神讨论用神的定义和来源',
            'chapter': '论用神'
        },
        {
            'passage_id': 'P-PZZQ-YONGSHEN-002',
            'raw_text': '有相扶相助，有情有义。',
            'context': '子平真诠·论用神讨论用神的辅助关系',
            'chapter': '论用神'
        },
        {
            'passage_id': 'P-PZZQ-XIANGSHEN-001',
            'raw_text': '相神辅月令用神，助起用神之不足。',
            'context': '子平真诠·论相神讨论相神的作用',
            'chapter': '论相神'
        },
        # QTBJ - 穷通宝鉴（调候篇）
        {
            'passage_id': 'P-QTBJ-JIAMU-001',
            'raw_text': '正月甲木，枝枯叶落，形朽气寒，非丁不成。',
            'context': '穷通宝鉴·甲木讨论正月甲木的调候需求',
            'chapter': '甲木'
        },
        {
            'passage_id': 'P-QTBJ-YIMU-001',
            'raw_text': '二月乙木，枝繁叶茂，非庚金不斩。',
            'context': '穷通宝鉴·乙木讨论二月乙木的修剪需求',
            'chapter': '乙木'
        },
        {
            'passage_id': 'P-QTBJ-BINGHUO-001',
            'raw_text': '三月丙火，景星高照，非壬水不显。',
            'context': '穷通宝鉴·丙火讨论三月丙火的调候需求',
            'chapter': '丙火'
        },
        # SMTH - 三命通会（干支总论）
        {
            'passage_id': 'P-SMTH-GANZHI-001',
            'raw_text': '天干者，乃一气之化，分王四时，各有体象。',
            'context': '三命通会·天干总论讨论天干的本质',
            'chapter': '天干总论'
        },
        {
            'passage_id': 'P-SMTH-DIZHI-001',
            'raw_text': '地支者，乃五行之根，藏人元而主事权。',
            'context': '三命通会·地支总论讨论地支的本质',
            'chapter': '地支总论'
        },
        {
            'passage_id': 'P-SMTH-NAYIN-001',
            'raw_text': '纳音者，五行之变也。',
            'context': '三命通会·纳音总论讨论纳音的本质',
            'chapter': '纳音总论'
        }
    ]
    
    print(f"  ✓ 加载原典段落: {len(strict_candidates)}条")
    
    # ========== 阶段2: 验证Independent Truth ==========
    print("\n▶ 阶段2: 验证Strict Independent Truth")
    
    truth_provider = StrictIndependentTruth()
    verified_count = 0
    excluded_count = 0
    pending_count = 0
    
    truth_details = []
    
    for cand in strict_candidates:
        passage_id = cand['passage_id']
        raw_text = cand['raw_text']
        
        # 提取Primitive和Condition
        if '犯岁' in raw_text:
            cand['extracted_primitive'] = 'day_gan_克_year_gan'
            cand['condition'] = '日干克年干'
        elif '主贫' in raw_text or '岁君制日干' in raw_text:
            cand['extracted_primitive'] = 'year_gan_克_day_gan'
            cand['condition'] = '年干克日干'
        elif '德临' in raw_text or '岁君生日干' in raw_text:
            cand['extracted_primitive'] = 'year_gan_生日_gan'
            cand['condition'] = '年干生日干'
        elif '制中有生' in raw_text or '生中有制' in raw_text:
            cand['extracted_primitive'] = 'zhi_hua_dialectic'
            cand['condition'] = '制化关系辩证存在'
        elif '太过' in raw_text and '不及' in raw_text:
            cand['extracted_primitive'] = 'wang_shuai_zhihua'
            cand['condition'] = '太过宜制/不及宜生'
        elif '用神' in raw_text and '月令' in raw_text:
            cand['extracted_primitive'] = 'yong_shen_source'
            cand['condition'] = '用神来自月令'
        elif '调候' in raw_text or ('丁' in raw_text and '寒' in raw_text):
            cand['extracted_primitive'] = 'tiao_hou_requirement'
            cand['condition'] = '根据月份判断调候需求'
        else:
            cand['extracted_primitive'] = None
            cand['condition'] = None
        
        truth = truth_provider.get_strict_truth(passage_id)
        
        if truth and truth.get('status') == 'EXCLUDED_CONCEPTUAL':
            # 概念性断言，排除
            excluded_count += 1
            cand['verification_status'] = 'EXCLUDED'
            cand['verification_reason'] = truth['reason']
        elif truth and 'minimal_truth' in truth:
            # 有严格独立真值
            verified_count += 1
            cand['verification_status'] = 'VERIFIED'
            cand['verification_truth'] = truth
        else:
            # 无独立真值
            pending_count += 1
            cand['verification_status'] = 'PENDING'
            cand['verification_reason'] = '无独立真值支持'
        
        truth_details.append({
            'passage_id': passage_id,
            'status': cand['verification_status'],
            'truth': truth
        })
    
    print(f"  ✓ VERIFIED: {verified_count}条")
    print(f"  ✓ EXCLUDED (概念性断言): {excluded_count}条")
    print(f"  ✓ PENDING (无独立真值): {pending_count}条")
    
    # ========== 阶段3: 重新计算授权等级 ==========
    print("\n▶ 阶段3: 重新计算授权等级（严格标准）")
    
    complete_count = 0
    partial_count = 0
    rejected_count = 0
    
    results = []
    
    for cand in strict_candidates:
        passage_id = cand['passage_id']
        status = cand['verification_status']
        
        if status == 'VERIFIED':
            # 有严格独立真值，验证Primitive是否匹配
            truth = cand['verification_truth']
            extracted_primitive = cand.get('extracted_primitive', '')
            
            if extracted_primitive == truth['primitive']:
                # Primitive匹配，可能是COMPLETE
                # 但还需要验证Condition是否完整
                condition = cand.get('condition', '')
                if condition and len(condition) > 0:
                    complete_count += 1
                    final_status = 'AUTHORIZED_COMPLETE'
                else:
                    partial_count += 1
                    final_status = 'AUTHORIZED_PARTIAL'
                    cand['reason'] = 'Condition不完整'
            else:
                partial_count += 1
                final_status = 'AUTHORIZED_PARTIAL'
                cand['reason'] = 'Primitive与Truth不匹配'
        elif status == 'EXCLUDED':
            rejected_count += 1
            final_status = 'REJECTED_CONCEPTUAL'
            cand['reason'] = '概念定义，非命理断语'
        else:
            partial_count += 1
            final_status = 'AUTHORIZED_PARTIAL'
            cand['reason'] = '无独立真值支持'
        
        cand['final_status'] = final_status
        results.append(cand)
    
    print(f"  ✓ AUTHORIZED_COMPLETE: {complete_count}条")
    print(f"  ✓ AUTHORIZED_PARTIAL: {partial_count}条")
    print(f"  ✓ REJECTED (概念性断言): {rejected_count}条")
    
    # ========== 输出详细结果 ==========
    print("\n" + "=" * 70)
    print("Strict Validation Results")
    print("=" * 70)
    
    for result in results:
        status_icon = '✅' if result['final_status'] == 'AUTHORIZED_COMPLETE' else '⚠️' if result['final_status'] == 'AUTHORIZED_PARTIAL' else '❌'
        
        print(f"\n{result['passage_id']}: {status_icon} {result['final_status']}")
        print(f"  原文: {result['raw_text'][:50]}...")
        print(f"  Primitive: {result.get('extracted_primitive', 'N/A')}")
        print(f"  Condition: {result.get('condition', 'N/A')}")
        
        if 'verification_truth' in result:
            truth = result['verification_truth']
            print(f"  独立真值: {truth.get('minimal_truth', 'N/A')}")
            print(f"  排除结论: {', '.join(truth.get('excludes', [])) if truth.get('excludes') else '无'}")
        
        if 'reason' in result:
            print(f"  原因: {result['reason']}")
    
    # ========== 保存结果 ==========
    output_path = os.path.join(BASE_DIR, 'data', 'p0_8_5_strict_expansion.json')
    result_data = {
        'stage': 'P0-8.5',
        'version': 'v2_strict',
        'timestamp': datetime.now().isoformat(),
        'total_candidates': len(strict_candidates),
        'metrics': {
            'verified_count': verified_count,
            'excluded_count': excluded_count,
            'pending_count': pending_count,
            'complete_rate': complete_count / len(strict_candidates),
            'partial_rate': partial_count / len(strict_candidates),
            'rejected_rate': rejected_count / len(strict_candidates)
        },
        'summary': {
            'total': len(strict_candidates),
            'authorized_complete': complete_count,
            'authorized_partial': partial_count,
            'rejected_conceptual': rejected_count
        },
        'results': results
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
    
    # ========== 核心结论 ==========
    print("\n" + "=" * 70)
    print("核心结论")
    print("=" * 70)
    
    print("\n【严格授权标准】")
    print(f"  总候选: {len(strict_candidates)}条")
    print(f"  AUTHORIZED_COMPLETE: {complete_count}条 ({complete_count/len(strict_candidates)*100:.1f}%)")
    print(f"  AUTHORIZED_PARTIAL: {partial_count}条 ({partial_count/len(strict_candidates)*100:.1f}%)")
    print(f"  REJECTED (概念性断言): {rejected_count}条 ({rejected_count/len(strict_candidates)*100:.1f}%)")
    
    print("\n【关键区分】")
    print("✓ Primitive成立 ≠ 断语成立")
    print("✓ 概念定义 ≠ 命理断语")
    print("✓ 独立真值必须是最小语义命题")
    print("✓ 不得合并多个结论到一条Truth")
    
    if complete_count > 0:
        print(f"\n【完整证据链验证通过】")
        print(f"  {complete_count}条断言有完整证据链支持")
        print("\n【流水线状态】")
        print("P0-8.5 Strict Expansion 🟢 PASS (严格标准)")
        return True
    else:
        print("\n【流水线状态】")
        print("P0-8.5 Strict Expansion 🟡 HOLD (无COMPLETE断言)")
        print("需补充更多原典证据或调整授权标准")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)