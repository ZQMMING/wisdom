# -*- coding: utf-8 -*-
"""P0-3.7: 原书逐条证据授权核验

核心任务：
对 9 条 C 类证据逐条回到原书核验授权级别

约束：
- 不要实现 Judgment Generator
- 不要强行提高授权数
- 只有原典明确表达的才授权
"""
import json
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class AuthorizationDecision(str, Enum):
    """授权决策"""
    EXPLICIT = "EXPLICIT"           # 原典明确表达
    IMPLICIT = "IMPLICIT"           # 原典隐含（不自动授权）
    UNRESOLVED = "UNRESOLVED"       # 未解析
    NEEDS_REVIEW = "NEEDS_REVIEW"   # 需要人工复核


@dataclass
class EvidenceReview:
    """单条证据核验结果"""
    evidence_id: str
    source_text: str
    original_text: Optional[str]  # 原书原文
    condition_analysis: str       # 条件分析
    authorization: AuthorizationDecision
    reason: str                   # 授权理由


def load_c_class_items():
    """加载 9 条 C 类证据"""
    with open('data/p0_3_4_attribution.json') as f:
        data = json.load(f)
    return [a for a in data['results'] if a['category'] == 'C']


def load_evidence_details():
    """加载原始证据详情"""
    with open('data/p0_3_3_structured_evidence.json') as f:
        data = json.load(f)
    return {e['evidence_id']: e for e in data.get('results', [])}


def load_original_texts():
    """加载原书原文数据
    
    注意：需要从资料库 D:/today/Canonical-Mining/ 加载
    这里先返回空 dict，后续补充
    """
    # TODO: 从原书加载原文
    return {}


def review_evidence(evidence: dict, original_text: str) -> EvidenceReview:
    """核验单条证据
    
    核验流程：
    1. 检查原书原文
    2. 判断原典是否明确表达该条件
    3. 检查 Condition 是否忠实于原文
    4. 决定授权级别
    """
    evidence_id = evidence['evidence_id']
    source_text = evidence.get('source_text', '')
    
    # 分析条件
    conditions = evidence.get('conditions', [])
    
    # 判断授权级别
    if not conditions:
        # 无条件结构
        return EvidenceReview(
            evidence_id=evidence_id,
            source_text=source_text,
            original_text=original_text,
            condition_analysis="无条件结构",
            authorization=AuthorizationDecision.UNRESOLVED,
            reason="原典无明确条件结构",
        )
    
    # 检查是否有明确条件表达
    has_explicit_condition = False
    explicit_keywords = ['当', '须', '必', '宜', '忌']
    
    for cond in conditions:
        cond_text = cond.get('text', '')
        if any(kw in cond_text for kw in explicit_keywords):
            has_explicit_condition = True
            break
    
    # 检查是否忠实于原文
    faithful_to_original = original_text and source_text in original_text
    
    if has_explicit_condition and faithful_to_original:
        return EvidenceReview(
            evidence_id=evidence_id,
            source_text=source_text,
            original_text=original_text,
            condition_analysis=f"有明确条件: {[c.get('text', '')[:50] for c in conditions]}",
            authorization=AuthorizationDecision.EXPLICIT,
            reason="原典明确表达且忠实于原文",
        )
    elif has_explicit_condition:
        return EvidenceReview(
            evidence_id=evidence_id,
            source_text=source_text,
            original_text=original_text,
            condition_analysis=f"有条件但需复核: {[c.get('text', '')[:50] for c in conditions]}",
            authorization=AuthorizationDecision.NEEDS_REVIEW,
            reason="有条件但需回到原书复核",
        )
    else:
        return EvidenceReview(
            evidence_id=evidence_id,
            source_text=source_text,
            original_text=original_text,
            condition_analysis=f"条件不明确: {[c.get('text', '')[:50] for c in conditions]}",
            authorization=AuthorizationDecision.UNRESOLVED,
            reason="原典无明确条件表达",
        )


def main():
    print("=== P0-3.7: 原书逐条证据授权核验 ===\n")
    
    # 加载数据
    c_class_items = load_c_class_items()
    evidence_details = load_evidence_details()
    original_texts = load_original_texts()
    
    print(f"C 类证据数: {len(c_class_items)}\n")
    
    # 核验每条证据
    reviews = []
    explicit_count = 0
    unresolved_count = 0
    needs_review_count = 0
    
    for item in c_class_items:
        evidence = evidence_details.get(item['evidence_id'], {})
        if not evidence:
            print(f"⚠️ 未找到证据: {item['evidence_id']}")
            continue
        
        original_text = original_texts.get(item['evidence_id'], '')
        review = review_evidence(evidence, original_text)
        reviews.append(review)
        
        # 统计
        if review.authorization == AuthorizationDecision.EXPLICIT:
            explicit_count += 1
        elif review.authorization == AuthorizationDecision.UNRESOLVED:
            unresolved_count += 1
        else:
            needs_review_count += 1
        
        # 输出
        status = review.authorization.value
        print(f"[{status}] {review.evidence_id}")
        print(f"  分析: {review.condition_analysis}")
        print(f"  理由: {review.reason}")
        print()
    
    # 输出报告
    print("=== 核验报告 ===")
    print(f"总数: {len(reviews)}")
    print(f"EXPLICIT: {explicit_count}")
    print(f"UNRESOLVED: {unresolved_count}")
    print(f"NEEDS_REVIEW: {needs_review_count}")
    
    # 保存结果
    output = {
        'generated': __import__('datetime').datetime.now().isoformat(),
        'summary': {
            'total': len(reviews),
            'explicit': explicit_count,
            'unresolved': unresolved_count,
            'needs_review': needs_review_count,
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
    
    # 警告
    if explicit_count == 0:
        print("\n⚠️ 当前没有 EXPLICIT 授权，generate_judgment() 保持返回 None")
    else:
        print(f"\n✅ 已有 {explicit_count} 条 EXPLICIT 授权，可以设计 Judgment Generator")


if __name__ == '__main__':
    main()
