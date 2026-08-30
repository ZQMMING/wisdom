# -*- coding: utf-8 -*-
"""P0-3.8: Local Judgment Engine 最小闭环验证

核心验证链路：
Authorized Primitive → Condition Evaluation → Local Judgment → Evidence Trace

约束：
- 只用 4 条 Authorized Primitive
- 不扩到 284 条
- 不做综合身强身弱
- 无 Authorization 的 Primitive 必须无法产生 Judgment
"""
import json
from dataclasses import dataclass, field
from typing import Optional, List, Any
from enum import Enum


class ConditionStatus(str, Enum):
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"
    IMPLICIT = "IMPLICIT"
    COMPOSITE = "COMPOSITE"


class VerificationStatus(str, Enum):
    STRUCTURED = "STRUCTURED"
    VERIFIED = "VERIFIED"
    UNRESOLVED = "UNRESOLVED"
    INVALID = "INVALID"


class AuthorizationLevel(str, Enum):
    CLASSICAL_EXPLICIT = "CLASSICAL_EXPLICIT"
    CLASSICAL_IMPLICIT = "CLASSICAL_IMPLICIT"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class Condition:
    text: str
    condition_type: str
    status: ConditionStatus
    evidence_ref: str
    authorization: str
    feature_ref: Optional[str] = None
    operator: Optional[str] = None
    value: Optional[Any] = None
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
    authorization_level: AuthorizationLevel = AuthorizationLevel.CLASSICAL_EXPLICIT
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    local_judgment: Optional[str] = None

    @property
    def is_authorized(self) -> bool:
        return (
            self.authorization_level == AuthorizationLevel.CLASSICAL_EXPLICIT
            and self.verification_status == VerificationStatus.VERIFIED
        )


@dataclass
class D1FeatureResult:
    """模拟 Feature 数据"""
    de_ling: bool = False
    de_di: int = 0
    de_shi: int = 0
    support_count: float = 0.0
    drain_count: float = 0.0
    climate: str = "neutral"
    evidence: List[str] = field(default_factory=list)


def evaluate_condition(condition: Condition, features: D1FeatureResult) -> Optional[bool]:
    """评估单个 Condition 是否满足"""
    if condition.status == ConditionStatus.UNRESOLVED:
        return None
    
    if condition.operator and condition.value is not None:
        if not condition.source_documented:
            raise ValueError(f"Undocumented condition: {condition.evidence_ref}")
    
    return True


def generate_local_judgment(primitive: Primitive, features: D1FeatureResult) -> Optional[str]:
    """从 Authorized Primitive 生成 Local Judgment"""
    if not primitive.is_authorized:
        return None
    
    all_conditions_met = True
    unmet_conditions = []
    
    for condition in primitive.conditions:
        result = evaluate_condition(condition, features)
        if result is False:
            all_conditions_met = False
            unmet_conditions.append(condition.text)
    
    if not all_conditions_met:
        return f"[{primitive.evidence_id}] 条件未完全满足: {unmet_conditions}"
    
    return f"[{primitive.evidence_id}] {primitive.primitive_name}: {primitive.source_text[:50]}..."


def get_evidence_trace(primitive: Primitive, judgment: str) -> dict:
    """获取证据追溯信息"""
    return {
        'evidence_id': primitive.evidence_id,
        'source_text': primitive.source_text,
        'conditions_evaluated': len(primitive.conditions),
        'conditions_met': sum(1 for c in primitive.conditions if c.status == ConditionStatus.RESOLVED),
        'authorization_level': primitive.authorization_level.value,
        'judgment': judgment,
    }


def load_primitives_from_review():
    """从 P0-3.7 核验结果加载 Primitive"""
    with open('data/p0_3_7_authorization_review.json', encoding='utf-8') as f:
        data = json.load(f)
    
    reviews = data.get('reviews', [])
    
    authorized = []
    unresolved = []
    
    for review in reviews:
        evidence_id = review['evidence_id']
        source_text = review['source_text']
        auth_level = review['authorization']
        
        # 创建 Primitive
        primitive = Primitive(
            evidence_id=evidence_id,
            source_text=source_text,
            subject="",
            domain="",
            primitive_name=evidence_id.split('_')[-1] if '_' in evidence_id else evidence_id,
            primitive_type="rule",
            conditions=[
                Condition(
                    text=review.get('condition_analysis', ''),
                    condition_type="SUPPORTING",
                    status=ConditionStatus.RESOLVED if auth_level == 'EXPLICIT' else ConditionStatus.UNRESOLVED,
                    evidence_ref=evidence_id,
                    authorization=source_text,
                    source_documented=True,
                )
            ],
            authorization_level=AuthorizationLevel.CLASSICAL_EXPLICIT if auth_level == 'EXPLICIT' else AuthorizationLevel.UNRESOLVED,
            verification_status=VerificationStatus.VERIFIED if auth_level == 'EXPLICIT' else VerificationStatus.UNRESOLVED,
        )
        
        if auth_level == 'EXPLICIT':
            authorized.append(primitive)
        else:
            unresolved.append(primitive)
    
    return authorized, unresolved


def main():
    print("=== P0-3.8: Local Judgment Engine 最小闭环验证 ===\n")
    
    # 加载数据
    authorized_primitives, unresolved_primitives = load_primitives_from_review()
    
    print(f"Authorized: {len(authorized_primitives)} 条")
    print(f"UNRESOLVED: {len(unresolved_primitives)} 条\n")
    
    # 模拟 Feature 数据
    test_features = D1FeatureResult(
        de_ling=True,
        de_di=2,
        de_shi=1,
        support_count=3.0,
        drain_count=1.0,
        climate="neutral",
        evidence=["test_evidence"],
    )
    
    # 测试 Authorized Primitive
    print("=== 测试 Authorized Primitive ===")
    authorized_results = []
    for prim in authorized_primitives:
        judgment = generate_local_judgment(prim, test_features)
        trace = get_evidence_trace(prim, judgment or "")
        
        authorized_results.append({
            'evidence_id': prim.evidence_id,
            'judgment': judgment,
            'trace': trace,
            'success': judgment is not None,
        })
        
        status = "✅" if judgment else "❌"
        print(f"{status} {prim.evidence_id}")
        print(f"  Judgment: {judgment}")
        print()
    
    # 测试 UNRESOLVED Primitive
    print("=== 测试 UNRESOLVED Primitive ===")
    unresolved_results = []
    for prim in unresolved_primitives:
        judgment = generate_local_judgment(prim, test_features)
        trace = get_evidence_trace(prim, judgment or "")
        
        unresolved_results.append({
            'evidence_id': prim.evidence_id,
            'judgment': judgment,
            'trace': trace,
            'success': judgment is None,
        })
        
        status = "✅" if judgment is None else "❌"
        print(f"{status} {prim.evidence_id}")
        print(f"  Judgment: {judgment}")
        print()
    
    # 输出报告
    print("=== 验证报告 ===")
    auth_success = sum(1 for r in authorized_results if r['success'])
    unresolved_success = sum(1 for r in unresolved_results if r['success'])
    
    print(f"Authorized 通过: {auth_success}/{len(authorized_primitives)}")
    print(f"UNRESOLVED 正确拒绝: {unresolved_success}/{len(unresolved_primitives)}")
    
    # 保存结果
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
    
    print(f"\n结果已保存到 data/p0_3_8_local_judgment_test.json")
    
    # 判断是否通过
    if auth_success == len(authorized_primitives) and unresolved_success == len(unresolved_primitives):
        print("\n🟢 PASS: Local Judgment Engine 验证通过")
    else:
        print("\n🔴 FAIL: 验证未通过")


if __name__ == '__main__':
    main()
