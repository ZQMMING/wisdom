# -*- coding: utf-8 -*-
"""T3 PENDING 归因分类脚本

对 15 条 PENDING 证据进行分类：
A. 现有 Canonical State 已有，只是映射缺失
B. 需要新增确定性的 Calculation Feature
C. 属于 Primitive/Condition 语义，不应塞进 Feature
D. 本身需要综合辨证，不能作为 Feature

只有 B 才允许扩展 D1FeatureResult。
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
class PendingAnalysis:
    evidence_id: str
    source_text: str
    conditions: List[Dict]
    category: Category
    reason: str
    suggestion: str  # 如何处理


def analyze_pending_items():
    """分析 15 条 PENDING 项，进行 A/B/C/D 分类"""
    
    # 加载验证结果
    with open('data/t3_primitive_validation_result.json') as f:
        result = json.load(f)
    
    # 加载原始证据
    with open('data/p0_3_3_structured_evidence.json') as f:
        evidence_data = json.load(f)
    
    # 构建 evidence_id -> evidence 映射
    evidence_map = {e['evidence_id']: e for e in evidence_data.get('results', [])}
    
    # 分析 PENDING 项
    pending_results = [r for r in result['results'] if r['verification_status'] == 'PENDING']
    
    print(f"共 {len(pending_results)} 条 PENDING 项\n")
    
    analyses = []
    for r in pending_results:
        evidence = evidence_map.get(r['evidence_id'], {})
        source_text = evidence.get('source_text', '')
        conditions = evidence.get('conditions', [])
        
        # 分类逻辑
        analysis = classify_evidence(r['evidence_id'], source_text, conditions, r['domain'])
        analyses.append(analysis)
        
        print(f"[{analysis.category.value}] {r['evidence_id']}")
        print(f"  原因: {analysis.reason}")
        print(f"  建议: {analysis.suggestion}")
        print()
    
    # 统计
    stats = {cat: len([a for a in analyses if a.category == cat]) for cat in Category}
    
    print("=== 分类统计 ===")
    for cat, count in stats.items():
        print(f"  {cat.value}: {count} 条")
    
    # 保存结果
    output = {
        'total_pending': len(analyses),
        'stats': {cat.value: count for cat, count in stats.items()},
        'analyses': [
            {
                'evidence_id': a.evidence_id,
                'domain': r['domain'],
                'category': a.category.value,
                'reason': a.reason,
                'suggestion': a.suggestion,
            }
            for a, r in zip(analyses, pending_results)
        ]
    }
    
    with open('data/t3_pending_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 data/t3_pending_analysis.json")
    
    return stats


def classify_evidence(evidence_id: str, source_text: str, conditions: List[Dict], domain: str) -> PendingAnalysis:
    """根据证据内容判断类别"""
    
    # A类特征：条件只是命名/映射问题
    a_keywords = ['得令', '得地', '得势', '通根', '透干', '气候', '生扶', '泄耗']
    if any(kw in source_text for kw in a_keywords):
        # 检查是否有明确的 feature_ref
        has_feature_ref = any(c.get('feature_ref') for c in conditions)
        if not has_feature_ref:
            return PendingAnalysis(
                evidence_id=evidence_id,
                source_text=source_text,
                conditions=conditions,
                category=Category.A,
                reason="条件涉及现有特征但缺少 feature_ref 映射",
                suggestion="补充 Mapping 规则，不扩 Feature"
            )
    
    # C类特征：纯语义规则，不是计算特征
    c_keywords = ['气势', '从格', '格局', '成败', '救应', '调候', '十神', '体用']
    if any(kw in source_text for kw in c_keywords):
        return PendingAnalysis(
            evidence_id=evidence_id,
            source_text=source_text,
            conditions=conditions,
            category=Category.C,
            reason="条件属于 Primitive/Condition 语义，不应塞入 Feature",
            suggestion="保持分离，由辨证层处理"
        )
    
    # D类特征：需要综合辨证
    d_keywords = ['综合', '全局', '配合', '协同', '整体', '辩证', '权衡']
    if any(kw in source_text for kw in d_keywords):
        return PendingAnalysis(
            evidence_id=evidence_id,
            source_text=source_text,
            conditions=conditions,
            category=Category.D,
            reason="条件需要综合辨证，不能作为单一 Feature",
            suggestion="交由辨证层处理，不提取为 Feature"
        )
    
    # B类特征：需要新的计算特征
    # 检查是否涉及新的计算维度
    new_calc_keywords = ['得令权重', '通根质量', '生扶比例', '泄耗比例', '气候修正']
    if any(kw in source_text for kw in new_calc_keywords):
        return PendingAnalysis(
            evidence_id=evidence_id,
            source_text=source_text,
            conditions=conditions,
            category=Category.B,
            reason="条件涉及新的计算维度，需要新增 Calculation Feature",
            suggestion="评估后决定是否扩展 D1FeatureResult"
        )
    
    # 默认归类为 C（安全策略）
    return PendingAnalysis(
        evidence_id=evidence_id,
        source_text=source_text,
        conditions=conditions,
        category=Category.C,
        reason="条件属于 Primitive/Condition 语义边界",
        suggestion="保持分离，由辨证层处理"
    )


if __name__ == '__main__':
    analyze_pending_items()
