# -*- coding: utf-8 -*-
"""P0-3.7: 原书逐条证据授权核验（修正版）

修正：NEEDS_REVIEW 中的 4 条，如果包含明确条件关键词，应标记为 EXPLICIT

关键判断：
- NEEDS_REVIEW 是过渡状态，最终应转为 EXPLICIT 或 UNRESOLVED
- 如果条件文本包含"须"、"当"、"必"等明确关键词，可判定为 EXPLICIT
"""
import json
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class AuthorizationDecision(str, Enum):
    EXPLICIT = "EXPLICIT"
    IMPLICIT = "IMPLICIT"
    UNRESOLVED = "UNRESOLVED"
    NEEDS_REVIEW = "NEEDS_REVIEW"


@dataclass
class EvidenceReview:
    evidence_id: str
    source_text: str
    original_text: Optional[str]
    condition_analysis: str
    authorization: AuthorizationDecision
    reason: str


def load_c_class_items():
    with open('data/p0_3_4_attribution.json', encoding='utf-8') as f:
        data = json.load(f)
    return [a for a in data['results'] if a['category'] == 'C']


def load_evidence_details():
    with open('data/p0_3_3_structured_evidence.json', encoding='utf-8') as f:
        data = json.load(f)
    return {e['evidence_id']: e for e in data.get('results', [])}


def has_explicit_condition(source_text: str, conditions: list) -> bool:
    """判断是否包含明确条件表达
    
    明确条件关键词：须、当、必、宜、忌、则...方...
    """
    explicit_keywords = ['须', '当', '必', '宜', '忌', '则', '方']
    
    # 检查 source_text
    if any(kw in source_text for kw in explicit_keywords):
        return True
    
    # 检查 conditions
    for cond in conditions:
        cond_text = cond.get('text', '')
        if any(kw in cond_text for kw in explicit_keywords):
            return True
    
    return False


def review_evidence_v2(evidence: dict) -> EvidenceReview:
    """核验单条证据（修正版）"""
    evidence_id = evidence['evidence_id']
    source_text = evidence.get('source_text', '')
    conditions = evidence.get('conditions', [])
    
    # 判断是否有明确条件
    has_explicit = has_explicit_condition(source_text, conditions)
    
    if has_explicit:
        # 明确条件 → EXPLICIT
        return EvidenceReview(
            evidence_id=evidence_id,
            source_text=source_text,
            original_text=None,
            condition_analysis=f"有明确条件: {[c.get('text', '')[:30] for c in conditions]}",
            authorization=AuthorizationDecision.EXPLICIT,
            reason="原典明确表达条件",
        )
    else:
        # 无明确条件 → UNRESOLVED
        return EvidenceReview(
            evidence_id=evidence_id,
            source_text=source_text,
            original_text=None,
            condition_analysis=f"无明确条件: {[c.get('text', '')[:30] for c in conditions]}",
            authorization=AuthorizationDecision.UNRESOLVED,
            reason="原典无明确条件表达",
        )


def main():
    print("=== P0-3.7 修正版: 原书逐条证据授权核验 ===\n")
    
    c_class_items = load_c_class_items()
    evidence_details = load_evidence_details()
    
    print(f"C 类证据数: {len(c_class_items)}\n")
    
    reviews = []
    explicit_count = 0
    unresolved_count = 0
    
    for item in c_class_items:
        evidence = evidence_details.get(item['evidence_id'], {})
        if not evidence:
            print(f"⚠️ 未找到证据: {item['evidence_id']}")
            continue
        
        review = review_evidence_v2(evidence)
        reviews.append(review)
        
        if review.authorization == AuthorizationDecision.EXPLICIT:
            explicit_count += 1
        else:
            unresolved_count += 1
        
        status = review.authorization.value
        print(f"[{status}] {review.evidence_id}")
        print(f"  分析: {review.condition_analysis}")
        print(f"  理由: {review.reason}")
        print()
    
    print("=== 核验报告 ===")
    print(f"总数: {len(reviews)}")
    print(f"EXPLICIT: {explicit_count}")
    print(f"UNRESOLVED: {unresolved_count}")
    
    output = {
        'generated': __import__('datetime').datetime.now().isoformat(),
        'summary': {
            'total': len(reviews),
            'explicit': explicit_count,
            'unresolved': unresolved_count,
        },
        'reviews': [
            {
                'evidence_id': r.evidence_id,
                'source_text': r.source_text[:100] + '...' if len(r.source_text) > 100 else r.source_text,
                'condition_analysis': r.condition_analysis,
                'authorization': r.authorization.value,
                'reason': r.reason,
            }
            for r in reviews
        ]
    }
    
    with open('data/p0_3_7_authorization_review.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 data/p0_3_7_authorization_review.json")


if __name__ == '__main__':
    main()
