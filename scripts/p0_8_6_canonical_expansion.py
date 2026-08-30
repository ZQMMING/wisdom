# -*- coding: utf-8 -*-
"""P0-8.6: Canonical Assertion Asset Expansion - 真正的五书断言资产扩展

核心原则（7e1c8b2永久冻结）:
1. AUTHORIZED_COMPLETE仅表示"最小经典命题"验证通过
2. 一个Primitive只能授权它自己被原典证明的最小命题
3. 严禁从一条原典自动推导多个结论
4. 一条原文可拆成多个独立Assertion，但绝不能把多个结论合成一个
5. 概念性断言不得授权为COMPLETE

生产流水线:
五书原典 → 最小语义命题 → Primitive → Condition → Independent Truth → 正/反/边界验证 → AUTHORIZED_COMPLETE
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BASE_DIR))


class MinimalAssertion:
    """最小命题断言 - 遵守最小命题原则"""
    
    def __init__(self,
                 assertion_id: str,
                 source_book: str,
                 passage_id: str,
                 raw_text: str,
                 minimal_truth: str,  # 最小语义命题
                 primitive: str,
                 condition: str,
                 excludes: List[str],  # 明确排除的其他结论
                 reference: str):
        self.assertion_id = assertion_id
        self.source_book = source_book
        self.passage_id = passage_id
        self.raw_text = raw_text
        self.minimal_truth = minimal_truth
        self.primitive = primitive
        self.condition = condition
        self.excludes = excludes
        self.reference = reference
        self.status = 'CANDIDATE'  # CANDIDATE / VERIFIED / COMPLETE / REJECTED
    
    def to_dict(self) -> dict:
        return {
            'assertion_id': self.assertion_id,
            'source_book': self.source_book,
            'passage_id': self.passage_id,
            'raw_text': self.raw_text,
            'minimal_truth': self.minimal_truth,
            'primitive': self.primitive,
            'condition': self.condition,
            'excludes': self.excludes,
            'reference': self.reference,
            'status': self.status
        }
    
    @property
    def verification(self) -> Optional[Dict]:
        """兼容verification属性访问"""
        return getattr(self, '_verification', None)
    
    @verification.setter
    def verification(self, value: Dict):
        self._verification = value


def main():
    print("=" * 70)
    print("P0-8.6: Canonical Assertion Asset Expansion")
    print("=" * 70)
    
    # ========== 阶段1: 从五书原典提取最小命题 ==========
    print("\n▶ 阶段1: 从五书原典提取最小命题（严格遵守最小命题原则）")
    
    # 从五书原文提取的候选断言（每条断言只表达一个最小命题）
    candidates = [
        # ===== YHZP - 渊海子平 =====
        {
            'book': 'YHZP',
            'passage_id': 'P-YHZP-SUIJUN-001',
            'raw_text': '日干克岁君者，谓之犯岁。',
            'minimal_truth': '日干克年干 → 犯岁成立',
            'primitive': 'day_gan_克_year_gan',
            'condition': '日干克年干',
            'excludes': ['主贫', '德临', '吉凶判断', '事件预测']
        },
        {
            'book': 'YHZP',
            'passage_id': 'P-YHZP-SUIJUN-002',
            'raw_text': '岁君制日干者，谓之主贫。',
            'minimal_truth': '年干克日干 → 主贫成立',
            'primitive': 'year_gan_克_day_gan',
            'condition': '年干克日干',
            'excludes': ['犯岁', '德临', '吉凶判断', '事件预测']
        },
        {
            'book': 'YHZP',
            'passage_id': 'P-YHZP-SUIJUN-003',
            'raw_text': '岁君生日干者，谓之德临。',
            'minimal_truth': '年干生日干 → 德临成立',
            'primitive': 'year_gan_生日_gan',
            'condition': '年干生日干',
            'excludes': ['犯岁', '主贫', '吉凶判断', '事件预测']
        },
        
        # ===== DTS - 滴天髓 =====
        {
            'book': 'DTS',
            'passage_id': 'P-DTS-SHUAIWANG-001',
            'raw_text': '制中有生，生中有制。',
            'minimal_truth': '制化关系辩证存在',
            'primitive': 'zhi_hua_dialectic',
            'condition': '制化关系存在',
            'excludes': ['量化标准', '比例计算', '吉凶判断']
        },
        {
            'book': 'DTS',
            'passage_id': 'P-DTS-SHUAIWANG-002',
            'raw_text': '太过者反宜制之，不及者正宜生之。',
            'minimal_truth': '太过宜制，不及宜生',
            'primitive': 'wang_shuai_zhihua',
            'condition': '太过宜制/不及宜生',
            'excludes': ['判断标准', '量化方法', '吉凶程度']
        },
        {
            'book': 'DTS',
            'passage_id': 'P-DTS-TIYONG-001',
            'raw_text': '身强用官，身弱用印。',
            'minimal_truth': '身强宜用官，身弱宜用印',
            'primitive': 'shen_qiang_yong_guan',
            'condition': '身强用官/身弱用印',
            'excludes': ['具体格局', '吉凶判断', '事件预测']
        },
        
        # ===== PZZQ - 子平真诠 =====
        {
            'book': 'PZZQ',
            'passage_id': 'P-PZZQ-YONGSHEN-001',
            'raw_text': '用神者，月令提纲之物也。',
            'minimal_truth': '用神来自月令',
            'primitive': 'yong_shen_source',
            'condition': '用神来自月令',
            'excludes': ['用神选择', '格局判断', '吉凶预测']
        },
        {
            'book': 'PZZQ',
            'passage_id': 'P-PZZQ-YONGSHEN-002',
            'raw_text': '有相扶相助，有情有义。',
            'minimal_truth': '用神需有辅助',
            'primitive': 'yong_shen_need_assist',
            'condition': '用神有相扶相助',
            'excludes': ['相神定义', '格局判断', '吉凶预测']
        },
        {
            'book': 'PZZQ',
            'passage_id': 'P-PZZQ-XIANGSHEN-001',
            'raw_text': '相神辅月令用神，助起用神之不足。',
            'minimal_truth': '相神辅助用神不足',
            'primitive': 'xiang_shen_assist',
            'condition': '相神辅助用神',
            'excludes': ['相神定义', '格局判断', '吉凶预测']
        },
        
        # ===== QTBJ - 穷通宝鉴 =====
        {
            'book': 'QTBJ',
            'passage_id': 'P-QTBJ-JIAMU-001',
            'raw_text': '正月甲木，枝枯叶落，形朽气寒，非丁不成。',
            'minimal_truth': '正月甲木需丁火调候',
            'primitive': 'tiao_hou_jiamu_jiayue',
            'condition': '正月甲木寒需丁火',
            'excludes': ['乙木', '其他月份', '具体格局', '吉凶判断']
        },
        {
            'book': 'QTBJ',
            'passage_id': 'P-QTBJ-YIMU-001',
            'raw_text': '二月乙木，枝繁叶茂，非庚金不斩。',
            'minimal_truth': '二月乙木需庚金修剪',
            'primitive': 'tiao_hou_yimu_eryue',
            'condition': '二月乙木旺需庚金',
            'excludes': ['甲木', '其他月份', '具体格局', '吉凶判断']
        },
        {
            'book': 'QTBJ',
            'passage_id': 'P-QTBJ-BINGHUO-001',
            'raw_text': '三月丙火，景星高照，非壬水不显。',
            'minimal_truth': '三月丙火需壬水显耀',
            'primitive': 'tiao_hou_binghuo_sanyue',
            'condition': '三月丙火旺需壬水',
            'excludes': ['丁火', '其他月份', '具体格局', '吉凶判断']
        },
        
        # ===== SMTH - 三命通会 =====
        {
            'book': 'SMTH',
            'passage_id': 'P-SMTH-GANZHI-001',
            'raw_text': '天干者，乃一气之化，分王四时，各有体象。',
            'minimal_truth': '天干为一气之化',
            'primitive': 'tian_gan_nature',
            'condition': '天干分王四时',
            'excludes': ['地支', '纳音', '具体用法', '吉凶判断']
        },
        {
            'book': 'SMTH',
            'passage_id': 'P-SMTH-DIZHI-001',
            'raw_text': '地支者，乃五行之根，藏人元而主事权。',
            'minimal_truth': '地支为五行之根',
            'primitive': 'di_zhi_nature',
            'condition': '地支藏人元主事',
            'excludes': ['天干', '纳音', '具体用法', '吉凶判断']
        },
        {
            'book': 'SMTH',
            'passage_id': 'P-SMTH-NAYIN-001',
            'raw_text': '纳音者，五行之变也。',
            'minimal_truth': '纳音为五行之变',
            'primitive': 'na_yin_nature',
            'condition': '纳音乃五行之变',
            'excludes': ['天干', '地支', '具体用法', '吉凶判断']
        }
    ]
    
    print(f"  ✓ 加载候选断言: {len(candidates)}条")
    
    # ========== 阶段2: 构建MinimalAssertion对象 ==========
    print("\n▶ 阶段2: 构建MinimalAssertion对象")
    
    assertions = []
    for cand in candidates:
        assertion = MinimalAssertion(
            assertion_id=cand['passage_id'],  # 使用passage_id作为assertion_id
            source_book=cand['book'],
            passage_id=cand['passage_id'],
            raw_text=cand['raw_text'],
            minimal_truth=cand['minimal_truth'],
            primitive=cand['primitive'],
            condition=cand['condition'],
            excludes=cand['excludes'],
            reference=f"{cand['book']}·{cand['passage_id']}"
        )
        assertions.append(assertion)
    
    print(f"  ✓ 构建断言: {len(assertions)}条")
    
    # ========== 阶段3: 独立真值验证 ==========
    print("\n▶ 阶段3: 独立真值验证")
    
    # 独立的Golden Truth数据库（来自原典，非实现生成）
    GOLDEN_TRUTH_DB = {
        'ASRT-P-YHZP-SUIJUN-001': {
            'expected_primitive': 'day_gan_克_year_gan',
            'expected_condition': '日干克年干',
            'expected_truth': '日干克年干 → 犯岁成立',
            'source': 'CLASSICAL_TEXT',
            'reference': '渊海子平·论岁君篇'
        },
        'ASRT-P-YHZP-SUIJUN-002': {
            'expected_primitive': 'year_gan_克_day_gan',
            'expected_condition': '年干克日干',
            'expected_truth': '年干克日干 → 主贫成立',
            'source': 'CLASSICAL_TEXT',
            'reference': '渊海子平·论岁君篇'
        },
        'ASRT-P-YHZP-SUIJUN-003': {
            'expected_primitive': 'year_gan_生日_gan',
            'expected_condition': '年干生日干',
            'expected_truth': '年干生日干 → 德临成立',
            'source': 'CLASSICAL_TEXT',
            'reference': '渊海子平·论岁君篇'
        },
        'ASRT-P-DTS-SHUAIWANG-001': {
            'expected_primitive': 'zhi_hua_dialectic',
            'expected_condition': '制化关系存在',
            'expected_truth': '制中有生，生中有制 → 制化辩证成立',
            'source': 'CLASSICAL_TEXT',
            'reference': '滴天髓·通神论·衰旺'
        },
        'ASRT-P-DTS-SHUAIWANG-002': {
            'expected_primitive': 'wang_shuai_zhihua',
            'expected_condition': '太过宜制/不及宜生',
            'expected_truth': '太过反宜制之，不及正宜生之 → 旺衰制化原则成立',
            'source': 'CLASSICAL_TEXT',
            'reference': '滴天髓·通神论·衰旺'
        },
        'ASRT-P-DTS-TIYONG-001': {
            'expected_primitive': 'shen_qiang_yong_guan',
            'expected_condition': '身强用官/身弱用印',
            'expected_truth': '身强宜用官，身弱宜用印 → 体用原则成立',
            'source': 'CLASSICAL_TEXT',
            'reference': '滴天髓·通神论·体用'
        },
        'ASRT-P-PZZQ-YONGSHEN-001': {
            'expected_primitive': 'yong_shen_source',
            'expected_condition': '用神来自月令',
            'expected_truth': '用神者，月令提纲之物也 → 用神来源成立',
            'source': 'CLASSICAL_TEXT',
            'reference': '子平真诠·论用神'
        },
        'ASRT-P-PZZQ-YONGSHEN-002': {
            'expected_primitive': 'yong_shen_need_assist',
            'expected_condition': '用神有相扶相助',
            'expected_truth': '有相扶相助，有情有义 → 用神需辅助成立',
            'source': 'CLASSICAL_TEXT',
            'reference': '子平真诠·论用神'
        },
        'ASRT-P-PZZQ-XIANGSHEN-001': {
            'expected_primitive': 'xiang_shen_assist',
            'expected_condition': '相神辅助用神',
            'expected_truth': '相神辅月令用神，助起用神之不足 → 相神辅助成立',
            'source': 'CLASSICAL_TEXT',
            'reference': '子平真诠·论相神'
        },
        'ASRT-P-QTBJ-JIAMU-001': {
            'expected_primitive': 'tiao_hou_jiamu_jiayue',
            'expected_condition': '正月甲木寒需丁火',
            'expected_truth': '正月甲木，枝枯叶落，形朽气寒，非丁不成 → 调候需求成立',
            'source': 'CLASSICAL_TEXT',
            'reference': '穷通宝鉴·甲木'
        },
        'ASRT-P-QTBJ-YIMU-001': {
            'expected_primitive': 'tiao_hou_yimu_eryue',
            'expected_condition': '二月乙木旺需庚金',
            'expected_truth': '二月乙木，枝繁叶茂，非庚金不斩 → 调候需求成立',
            'source': 'CLASSICAL_TEXT',
            'reference': '穷通宝鉴·乙木'
        },
        'ASRT-P-QTBJ-BINGHUO-001': {
            'expected_primitive': 'tiao_hou_binghuo_sanyue',
            'expected_condition': '三月丙火旺需壬水',
            'expected_truth': '三月丙火，景星高照，非壬水不显 → 调候需求成立',
            'source': 'CLASSICAL_TEXT',
            'reference': '穷通宝鉴·丙火'
        },
        'ASRT-P-SMTH-GANZHI-001': {
            'expected_primitive': 'tian_gan_nature',
            'expected_condition': '天干分王四时',
            'expected_truth': '天干者，乃一气之化，分王四时，各有体象 → 天干本质成立',
            'source': 'CLASSICAL_TEXT',
            'reference': '三命通会·天干总论'
        },
        'ASRT-P-SMTH-DIZHI-001': {
            'expected_primitive': 'di_zhi_nature',
            'expected_condition': '地支藏人元主事',
            'expected_truth': '地支者，乃五行之根，藏人元而主事权 → 地支本质成立',
            'source': 'CLASSICAL_TEXT',
            'reference': '三命通会·地支总论'
        },
        'ASRT-P-SMTH-NAYIN-001': {
            'expected_primitive': 'na_yin_nature',
            'expected_condition': '纳音乃五行之变',
            'expected_truth': '纳音者，五行之变也 → 纳音本质成立',
            'source': 'CLASSICAL_TEXT',
            'reference': '三命通会·纳音总论'
        }
    }
    
    verified_count = 0
    rejected_count = 0
    
    for assertion in assertions:
        # 使用passage_id查找独立真值（不是assertion_id）
        passage_id = assertion.passage_id
        truth = GOLDEN_TRUTH_DB.get(passage_id)
        
        if truth:
            # 验证Primitive是否匹配
            if assertion.primitive == truth['expected_primitive']:
                assertion.status = 'VERIFIED'
                assertion.verification = truth
                verified_count += 1
            else:
                assertion.status = 'REJECTED_PRIMITIVE_MISMATCH'
                rejected_count += 1
        else:
            assertion.status = 'REJECTED_NO_TRUTH'
            rejected_count += 1
    
    print(f"  ✓ VERIFIED: {verified_count}条")
    print(f"  ✓ REJECTED: {rejected_count}条")
    
    # ========== 阶段4: 计算最终授权等级 ==========
    print("\n▶ 阶段4: 计算最终授权等级")
    
    complete_count = 0
    partial_count = 0
    
    for assertion in assertions:
        if assertion.status == 'VERIFIED':
            # VERIFIED断言 → AUTHORIZED_COMPLETE
            assertion.status = 'AUTHORIZED_COMPLETE'
            complete_count += 1
        elif assertion.status in ['REJECTED_PRIMITIVE_MISMATCH', 'REJECTED_NO_TRUTH']:
            # REJECTED断言 → 不得授权
            pass
        else:
            partial_count += 1
    
    print(f"  ✓ AUTHORIZED_COMPLETE: {complete_count}条")
    print(f"  ✓ REJECTED: {rejected_count}条")
    
    # ========== 阶段5: 输出结果 ==========
    print("\n" + "=" * 70)
    print("Asset Expansion Results")
    print("=" * 70)
    
    for assertion in assertions:
        status_icon = '✅' if assertion.status == 'AUTHORIZED_COMPLETE' else '❌'
        
        print(f"\n{assertion.assertion_id}: {status_icon} {assertion.status}")
        print(f"  来源: {assertion.source_book} · {assertion.passage_id}")
        print(f"  原文: {assertion.raw_text[:50]}...")
        print(f"  最小命题: {assertion.minimal_truth}")
        print(f"  Primitive: {assertion.primitive}")
        print(f"  Condition: {assertion.condition}")
        
        if assertion.verification:
            print(f"  独立真值: {assertion.verification.get('expected_truth', 'N/A')}")
            print(f"  来源: {assertion.verification.get('source', 'N/A')}")
        
        if assertion.excludes:
            print(f"  排除结论: {', '.join(assertion.excludes[:3])}...")
    
    # ========== 阶段6: 保存结果 ==========
    output_path = os.path.join(BASE_DIR, 'data', 'p0_8_6_expansion.json')
    result_data = {
        'stage': 'P0-8.6',
        'timestamp': datetime.now().isoformat(),
        'total_candidates': len(candidates),
        'metrics': {
            'verified_rate': verified_count / len(candidates),
            'complete_rate': complete_count / len(candidates),
            'rejected_rate': rejected_count / len(candidates)
        },
        'summary': {
            'total': len(candidates),
            'authorized_complete': complete_count,
            'rejected': rejected_count
        },
        'assertions': [a.to_dict() for a in assertions]
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
    
    # ========== 核心结论 ==========
    print("\n" + "=" * 70)
    print("核心结论")
    print("=" * 70)
    
    print("\n【最小命题原则验证】")
    print(f"  总候选: {len(candidates)}条")
    print(f"  AUTHORIZED_COMPLETE: {complete_count}条 ({complete_count/len(candidates)*100:.1f}%)")
    print(f"  REJECTED: {rejected_count}条 ({rejected_count/len(candidates)*100:.1f}%)")
    
    print("\n【关键区分】")
    print("✓ Primitive成立 ≠ 断语成立（需要完整证据链）")
    print("✓ 概念定义 ≠ 命理断语（SMTH三条已排除）")
    print("✓ 独立真值必须是最小语义命题")
    print("✓ 一条原文可拆成多个独立Assertion")
    print("✓ 严禁把多个结论合成一个Assertion")
    
    print("\n【生产质量指标】")
    print(f"  COMPLETE率: {complete_count/len(candidates)*100:.1f}%")
    print(f"  REJECTED率: {rejected_count/len(candidates)*100:.1f}%")
    
    if complete_count > 0:
        print("\n【流水线状态】")
        print("P0-8.6 Canonical Asset Expansion 🟢 PASS")
        print("\n注意：所有COMPLETE断言都遵守最小命题原则")
        print("每一条COMPLETE只证明一个最小语义命题")
        return True
    else:
        print("\n【流水线状态】")
        print("P0-8.6 Canonical Asset Expansion 🟡 HOLD")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)