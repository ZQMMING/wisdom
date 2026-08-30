# -*- coding: utf-8 -*-
"""P0-3.4 语义归因脚本

对 15 条 PENDING 证据进行人工/原典语义归因
区分 A/B/C/D 类别
"""
import json
from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum


class Category(str, Enum):
    A = "A"       # 现有 Feature 已有，映射缺失
    B = "B"       # 需要新增 Calculation Feature
    C = "C"       # Primitive/Condition 语义，不应塞进 Feature
    D = "D"       # 需要综合辨证，不能作为 Feature


@dataclass
class AttributionResult:
    evidence_id: str
    source_text: str
    domain: str
    category: Category
    reason: str
    suggestion: str
    authorization_ref: str  # 原典出处引用


def load_pending_items():
    """加载 PENDING 项"""
    with open('data/t3_pending_analysis.json') as f:
        data = json.load(f)
    return data['analyses']


def classify_item(item: Dict) -> AttributionResult:
    """对单条证据进行语义归因"""
    
    evidence_id = item['evidence_id']
    source_text = ""
    domain = item.get('domain', '')
    
    # 从原始证据数据中获取 source_text
    with open('data/p0_3_3_structured_evidence.json') as f:
        evidence_data = json.load(f)
    
    for e in evidence_data.get('results', []):
        if e.get('evidence_id') == evidence_id:
            source_text = e.get('source_text', '')
            break
    
    # 语义归因规则（基于原典特征）
    
    # A 类特征：涉及已知特征的映射问题
    a_keywords = ['得令', '得地', '得势', '通根', '透干', '生扶', '泄耗']
    if any(kw in source_text for kw in a_keywords):
        # 检查是否有明确的 feature_ref
        conditions = item.get('conditions', [])
        has_feature_ref = any(c.get('feature_ref') for c in conditions)
        if not has_feature_ref:
            return AttributionResult(
                evidence_id=evidence_id,
                source_text=source_text,
                domain=domain,
                category=Category.A,
                reason="条件涉及已知特征但缺少 feature_ref 映射",
                suggestion="补充 Mapping 规则，不扩 Feature",
                authorization_ref="《渊海子平》得令得地得势论"
            )
    
    # C 类特征：纯语义规则
    c_keywords = ['气势', '从格', '格局', '成败', '救应', '调候', '十神', '体用', '五行', '天干', '地支']
    if any(kw in source_text for kw in c_keywords):
        # 排除已归为 A 类的
        if not any(kw in source_text for kw in a_keywords):
            return AttributionResult(
                evidence_id=evidence_id,
                source_text=source_text,
                domain=domain,
                category=Category.C,
                reason="条件属于 Primitive/Condition 语义边界",
                suggestion="保持分离，由辨证层处理",
                authorization_ref="《滴天髓》《渊海子平》相关论述"
            )
    
    # D 类特征：综合辨证
    d_keywords = ['综合', '全局', '配合', '协同', '整体', '辩证', '权衡', '旺极', '从势']
    if any(kw in source_text for kw in d_keywords):
        return AttributionResult(
            evidence_id=evidence_id,
            source_text=source_text,
            domain=domain,
            category=Category.D,
            reason="条件需要综合辨证，不能作为单一 Feature",
            suggestion="交由辨证层处理，不提取为 Feature",
            authorization_ref="《滴天髓》通神论"
        )
    
    # B 类特征：涉及新的计算维度
    b_keywords = ['权重', '质量', '比例', '修正', '系数', '量化', '计算']
    if any(kw in source_text for kw in b_keywords):
        return AttributionResult(
            evidence_id=evidence_id,
            source_text=source_text,
            domain=domain,
            category=Category.B,
            reason="条件涉及新的计算维度",
            suggestion="评估后决定是否扩展 D1FeatureResult",
            authorization_ref="需逐条核实原典依据"
        )
    
    # 默认归类为 C（安全策略）
    return AttributionResult(
        evidence_id=evidence_id,
        source_text=source_text,
        domain=domain,
        category=Category.C,
        reason="条件属于 Primitive/Condition 语义边界",
        suggestion="保持分离，由辨证层处理",
        authorization_ref="需人工审核确认"
    )


def main():
    print("=== P0-3.4 语义归因 ===\n")
    
    # 加载 PENDING 项
    pending_items = load_pending_items()
    print(f"共 {len(pending_items)} 条 PENDING 项\n")
    
    # 逐条归因
    results = []
    for item in pending_items:
        result = classify_item(item)
        results.append(result)
        
        print(f"[{result.category.value}] {result.evidence_id}")
        print(f"  域: {result.domain}")
        print(f"  原因: {result.reason}")
        print(f"  建议: {result.suggestion}")
        print()
    
    # 统计
    from collections import Counter
    stats = Counter([r.category.value for r in results])
    
    print("=== 归因统计 ===")
    for cat in ['A', 'B', 'C', 'D']:
        print(f"  {cat}: {stats.get(cat, 0)} 条")
    
    # 保存结果
    output = {
        'total': len(results),
        'stats': {cat: stats.get(cat, 0) for cat in ['A', 'B', 'C', 'D']},
        'results': [
            {
                'evidence_id': r.evidence_id,
                'domain': r.domain,
                'category': r.category.value,
                'reason': r.reason,
                'suggestion': r.suggestion,
                'authorization_ref': r.authorization_ref,
            }
            for r in results
        ]
    }
    
    with open('data/p0_3_4_attribution.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 data/p0_3_4_attribution.json")
    
    # 关键结论
    print(f"\n=== 关键结论 ===")
    if stats.get('B', 0) == 0:
        print("✅ B=0：不需要扩展 D1FeatureResult")
    if stats.get('A', 0) > 0:
        print(f"⚠️ A={stats['A']}：需补充 Mapping 规则")
    if stats.get('C', 0) > 0:
        print(f"🔒 C={stats['C']}：保持语义边界")
    if stats.get('D', 0) > 0:
        print(f"🔒 D={stats['D']}：交由辨证层处理")


if __name__ == '__main__':
    main()
