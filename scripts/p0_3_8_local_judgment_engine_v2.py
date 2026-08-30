# -*- coding: utf-8 -*-
"""P0-3.8: Local Judgment Engine 最小闭环验证

直接使用修正后的授权数据
"""
import json
from dataclasses import dataclass, field
from typing import Optional, List, Any
from enum import Enum


class ConditionStatus(str, Enum):
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    UNRESOLVED = "UNRESOLVED"


class AuthorizationLevel(str, Enum):
    CLASSICAL_EXPLICIT = "CLASSICAL_EXPLICIT"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class Condition:
    text: str
    condition_type: str
    status: ConditionStatus
    evidence_ref: str
    authorization: str
    source_documented: bool = True


@dataclass(frozen=True)
class Primitive:
    evidence_id: str
    source_text: str
    subject: str
    domain: str
    primitive_name: str
    primitive_type: str
    conditions: List[Condition] = field(default_factory=list)
    scope: str = "primitive"
    authorization_level: AuthorizationLevel = AuthorizationLevel.UNRESOLVED
    verification_status: VerificationStatus = VerificationStatus.UNRESOLVED
    local_judgment: Optional[str] = None

    @property
    def is_authorized(self) -> bool:
        return (
            self.authorization_level == AuthorizationLevel.CLASSICAL_EXPLICIT
            and self.verification_status == VerificationStatus.VERIFIED
        )


@dataclass
class D1FeatureResult:
    de_ling: bool = False
    de_di: int = 0
    de_shi: int = 0
    support_count: float = 0.0
    drain_count: float = 0.0
    climate: str = "neutral"
    evidence: List[str] = field(default_factory=list)


def generate_local_judgment(primitive: Primitive, features: D1FeatureResult) -> Optional[str]:
    if not primitive.is_authorized:
        return None
    return f"[{primitive.evidence_id}] {primitive.primitive_name}: {primitive.source_text[:50]}..."


def get_evidence_trace(primitive: Primitive, judgment: str) -> dict:
    return {
        'evidence_id': primitive.evidence_id,
        'source_text': primitive.source_text,
        'conditions_evaluated': len(primitive.conditions),
        'authorization_level': primitive.authorization_level.value,
        'judgment': judgment,
    }


def main():
    print("=== P0-3.8: Local Judgment Engine 最小闭环验证 ===\n")
    
    # 加载修正后的授权数据
    with open('data/p0_3_7_authorization_review.json', encoding='utf-8') as f:
        review_data = json.load(f)
    
    reviews = review_data.get('reviews', [])
    
    # 分离 Authorized 和 UNRESOLVED
    authorized_primitives = []
    unresolved_primitives = []
    
    for review in reviews:
        auth = review['authorization']
        evidence_id = review['evidence_id']
        source_text = review['source_text']
        
        prim = Primitive(
            evidence_id=evidence_id,
            source_text=source_text,
            subject="",
            domain="",
            primitive_name=evidence_id.split('_')[-1] if '_' in evidence_id else evidence_id,
            primitive_type="rule",
            conditions=[
                Condition(
                    text="test",
                    condition_type="SUPPORTING",
                    status=ConditionStatus.RESOLVED if auth == 'EXPLICIT' else ConditionStatus.UNRESOLVED,
                    evidence_ref=evidence_id,
                    authorization=source_text,
                )
            ],
            authorization_level=AuthorizationLevel.CLASSICAL_EXPLICIT if auth == 'EXPLICIT' else AuthorizationLevel.UNRESOLVED,
            verification_status=VerificationStatus.VERIFIED if auth == 'EXPLICIT' else VerificationStatus.UNRESOLVED,
        )
        
        if auth == 'EXPLICIT':
            authorized_primitives.append(prim)
        else:
            unresolved_primitives.append(prim)
    
    print(f"Authorized: {len(authorized_primitives)} 条")
    print(f"UNRESOLVED: {len(unresolved_primitives)} 条\n")
    
    test_features = D1FeatureResult()
    
    # 测试 Authorized
    print("=== 测试 Authorized Primitive ===")
    authorized_results = []
    for prim in authorized_primitives:
        judgment = generate_local_judgment(prim, test_features)
        trace = get_evidence_trace(prim, judgment or "")
        authorized_results.append({
            'evidence_id': prim.evidence_id,
            'judgment': judgment,
            'success': judgment is not None,
        })
        status = "✅" if judgment else "❌"
        print(f"{status} {prim.evidence_id}")
    print()
    
    # 测试 UNRESOLVED
    print("=== 测试 UNRESOLVED Primitive ===")
    unresolved_results = []
    for prim in unresolved_primitives:
        judgment = generate_local_judgment(prim, test_features)
        trace = get_evidence_trace(prim, judgment or "")
        unresolved_results.append({
            'evidence_id': prim.evidence_id,
            'judgment': judgment,
            'success': judgment is None,
        })
        status = "✅" if judgment is None else "❌"
        print(f"{status} {prim.evidence_id}")
    print()
    
    # 报告
    print("=== 验证报告 ===")
    auth_success = sum(1 for r in authorized_results if r['success'])
    unresolved_success = sum(1 for r in unresolved_results if r['success'])
    
    print(f"Authorized 通过: {auth_success}/{len(authorized_primitives)}")
    print(f"UNRESOLVED 正确拒绝: {unresolved_success}/{len(unresolved_primitives)}")
    
    # 保存
    output = {
        'generated': __import__('datetime').datetime.now().isoformat(),
        'summary': {
            'authorized_total': len(authorized_primitives),
            'authorized_success': auth_success,
            'unresolved_total': len(unresolved_primitives),
            'unresolved_correctly_rejected': unresolved_success,
        },
        'authorized_results': authorized_results,
        'unresolved_results': unresolved_results,
    }
    
    with open('data/p0_3_8_local_judgment_test.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    if auth_success == len(authorized_primitives) and unresolved_success == len(unresolved_primitives):
        print("\n🟢 PASS: Local Judgment Engine 验证通过")
    else:
        print("\n🔴 FAIL")


if __name__ == '__main__':
    main()
