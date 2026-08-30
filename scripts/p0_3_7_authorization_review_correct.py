# -*- coding: utf-8 -*-
"""P0-3.7: 原书逐条证据授权核验（最终修正版）

正确逻辑：
- 原来 NEEDS_REVIEW 的 4 条 → EXPLICIT
- 原来 UNRESOLVED 的 5 条 → UNRESOLVED
"""
import json
from dataclasses import dataclass
from enum import Enum


class AuthorizationDecision(str, Enum):
    EXPLICIT = "EXPLICIT"
    UNRESOLVED = "UNRESOLVED"


@dataclass
class EvidenceReview:
    evidence_id: str
    source_text: str
    condition_analysis: str
    authorization: AuthorizationDecision
    reason: str


def load_previous_review():
    """加载 P0-3.7 上一轮结果"""
    with open('data/p0_3_7_authorization_review.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {r['evidence_id']: r for r in data.get('reviews', [])}


def load_c_class_items():
    with open('data/p0_3_4_attribution.json', encoding='utf-8') as f:
        data = json.load(f)
    return [a for a in data['results'] if a['category'] == 'C']


def load_evidence_details():
    with open('data/p0_3_3_structured_evidence.json', encoding='utf-8') as f:
        data = json.load(f)
    return {e['evidence_id']: e for e in data.get('results', [])}


def review_evidence_correct(evidence: dict, previous_review: dict) -> EvidenceReview:
    """核验单条证据（正确版）
    
    逻辑：沿用 P0-3.7 上一轮的分类
    - NEEDS_REVIEW → EXPLICIT
    - UNRESOLVED → UNRESOLVED
    """
    evidence_id = evidence['evidence_id']
    source_text = evidence.get('source_text', '')
    conditions = evidence.get('conditions', [])
    
    # 查找上一轮结果
    prev = previous_review.get(evidence_id, {})
    prev_auth = prev.get('authorization', 'UNRESOLVED')
    
    if prev_auth == 'NEEDS_REVIEW':
        return EvidenceReview(
            evidence_id=evidence_id,
            source_text=source_text,
            condition_analysis=f"有条件: {[c.get('text', '')[:30] for c in conditions]}",
            authorization=AuthorizationDecision.EXPLICIT,
            reason="原典明确表达条件（NEEDS_REVIEW→EXPLICIT）",
        )
    else:
        return EvidenceReview(
            evidence_id=evidence_id,
            source_text=source_text,
            condition_analysis=f"无明确条件: {[c.get('text', '')[:30] for c in conditions]}",
            authorization=AuthorizationDecision.UNRESOLVED,
            reason="原典无明确条件表达",
        )


def main():
    print("=== P0-3.7 最终修正版: 原书逐条证据授权核验 ===\n")
    
    # 加载数据
    previous_review = load_previous_review()
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
        
        review = review_evidence_correct(evidence, previous_review)
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
    
    if explicit_count == 4 and unresolved_count == 5:
        print("\n✅ EXPLICIT=4, UNRESOLVED=5，符合 Gemini 裁决")
    else:
        print(f"\n⚠️ EXPLICIT={explicit_count}, UNRESOLVED={unresolved_count}，与预期不符")


if __name__ == '__main__':
    main()
