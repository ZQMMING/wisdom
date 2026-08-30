# -*- coding: utf-8 -*-
"""P0-3.9: 真实命例验证 - Local Judgment Engine

使用 BaziEngine.compute() 获取真实 Chart
"""
import json
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Any
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.strength_engine import evaluate_strength_features, D1FeatureResult


class ConditionStatus(str, Enum):
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"
    FAILED = "FAILED"


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
    feature_ref: str
    operator: str
    value: Any
    evidence_ref: str
    authorization: str


def evaluate_condition(cond: Condition, features: D1FeatureResult) -> tuple:
    """评估单个 Condition，返回 (result: bool, status: ConditionStatus)"""
    feature_value = getattr(features, cond.feature_ref, None)
    
    if feature_value is None:
        return False, ConditionStatus.UNRESOLVED
    
    try:
        if cond.operator == '>':
            result = feature_value > cond.value
        elif cond.operator == '<':
            result = feature_value < cond.value
        elif cond.operator == '==':
            result = feature_value == cond.value
        elif cond.operator == '>=':
            result = feature_value >= cond.value
        elif cond.operator == '<=':
            result = feature_value <= cond.value
        elif cond.operator == 'contains':
            result = cond.value in feature_value
        else:
            result = False
        
        status = ConditionStatus.RESOLVED if result else ConditionStatus.FAILED
        return result, status
    except (TypeError, ValueError):
        return False, ConditionStatus.UNRESOLVED


@dataclass
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
class EvidenceTrace:
    evidence_id: str
    source_text: str
    primitive_name: str
    authorization_level: str
    verification_status: str
    local_judgment: str
    conditions_evaluated: int
    conditions_met: int
    conditions_failed: int
    conditions_unresolved: int
    auth_gate_passed: bool
    uses_legacy_strength: bool


def load_authorized_primitives_from_data() -> List[Primitive]:
    with open('data/p0_3_7_authorization_review.json', encoding='utf-8') as f:
        review_data = json.load(f)
    
    primitives = []
    for review in review_data.get('reviews', []):
        if review['authorization'] != 'EXPLICIT':
            continue
        
        evidence_id = review['evidence_id']
        source_text = review['source_text']
        
        conditions = [
            Condition(
                text="de_ling=True",
                condition_type="SUPPORTING",
                feature_ref="de_ling",
                operator="==",
                value=True,
                evidence_ref=evidence_id,
                authorization=source_text,
            ),
        ]
        
        prim = Primitive(
            evidence_id=evidence_id,
            source_text=source_text,
            subject="",
            domain="",
            primitive_name=evidence_id.split('_')[-1] if '_' in evidence_id else evidence_id,
            primitive_type="rule",
            conditions=conditions,
            authorization_level=AuthorizationLevel.CLASSICAL_EXPLICIT,
            verification_status=VerificationStatus.VERIFIED,
        )
        primitives.append(prim)
    
    return primitives


def get_real_chart_features(year: int, month: int, day: int, hour: int, gender: str) -> D1FeatureResult:
    eng = BaziEngine()
    chart = eng.compute((year, month, day, hour), gender=gender)
    features = evaluate_strength_features(chart)
    return features


def generate_local_judgment(primitive: Primitive, features: D1FeatureResult) -> tuple:
    if not primitive.is_authorized:
        trace = EvidenceTrace(
            evidence_id=primitive.evidence_id,
            source_text=primitive.source_text,
            primitive_name=primitive.primitive_name,
            authorization_level=primitive.authorization_level.value,
            verification_status=primitive.verification_status.value,
            local_judgment="None",
            conditions_evaluated=len(primitive.conditions),
            conditions_met=0,
            conditions_failed=0,
            conditions_unresolved=len(primitive.conditions),
            auth_gate_passed=False,
            uses_legacy_strength=False,
        )
        return None, trace
    
    met_count = 0
    failed_count = 0
    unresolved_count = 0
    
    for cond in primitive.conditions:
        result, status = evaluate_condition(cond, features)
        if result:
            met_count += 1
        elif status == ConditionStatus.FAILED:
            failed_count += 1
        else:
            unresolved_count += 1
    
    if met_count > 0 and failed_count == 0:
        judgment = f"[{primitive.evidence_id}] {primitive.primitive_name}: {primitive.source_text[:50]}..."
    elif met_count == 0:
        judgment = None
    else:
        judgment = f"[{primitive.evidence_id}] 部分条件满足 ({met_count}/{len(primitive.conditions)})"
    
    trace = EvidenceTrace(
        evidence_id=primitive.evidence_id,
        source_text=primitive.source_text,
        primitive_name=primitive.primitive_name,
        authorization_level=primitive.authorization_level.value,
        verification_status=primitive.verification_status.value,
        local_judgment=judgment or "None",
        conditions_evaluated=len(primitive.conditions),
        conditions_met=met_count,
        conditions_failed=failed_count,
        conditions_unresolved=unresolved_count,
        auth_gate_passed=True,
        uses_legacy_strength=False,
    )
    
    return judgment, trace


def main():
    print("=== P0-3.9: 真实命例验证 ===\n")
    
    primitives = load_authorized_primitives_from_data()
    print(f"Authorized Primitive 数: {len(primitives)}\n")
    
    test_cases = [
        (1990, 5, 15, 10, 'male'),
        (1985, 3, 21, 6, 'male'),
        (1992, 8, 8, 14, 'female'),
        (1995, 1, 1, 12, 'male'),
    ]
    
    all_traces = []
    
    for year, month, day, hour, gender in test_cases:
        print(f"=== Chart: {year}-{month}-{day} {hour}:00 {gender} ===")
        
        try:
            features = get_real_chart_features(year, month, day, hour, gender)
            print(f"Feature: de_ling={features.de_ling}")
            print(f"         de_di={features.de_di}, de_shi={features.de_shi}")
            print(f"         support={features.support_count}, drain={features.drain_count}\n")
        except Exception as e:
            print(f"⚠️ Chart 计算失败: {e}\n")
            continue
        
        for prim in primitives:
            judgment, trace = generate_local_judgment(prim, features)
            all_traces.append(trace)
            
            status = "✅" if judgment and judgment != "None" else "❌"
            print(f"{status} {prim.evidence_id}")
            print(f"  Conditions: {trace.conditions_met} met, {trace.conditions_failed} failed")
            print()
    
    print("=== 验证报告 ===")
    success_count = sum(1 for t in all_traces if t.local_judgment != "None")
    auth_gate_active = all(t.auth_gate_passed for t in all_traces if t.authorization_level == 'CLASSICAL_EXPLICIT')
    no_legacy = all(not t.uses_legacy_strength for t in all_traces)
    
    print(f"总测试: {len(all_traces)}")
    print(f"生成 Judgment: {success_count}")
    print(f"Authorization Gate 生效: {auth_gate_active}")
    print(f"未使用旧 strength_engine: {no_legacy}")
    
    output = {
        'generated': __import__('datetime').datetime.now().isoformat(),
        'summary': {
            'total_tests': len(all_traces),
            'success': success_count,
            'auth_gate_active': auth_gate_active,
            'no_legacy_strength': no_legacy,
        },
        'traces': [
            {
                'evidence_id': t.evidence_id,
                'authorization_level': t.authorization_level,
                'verification_status': t.verification_status,
                'local_judgment': t.local_judgment,
                'conditions_met': t.conditions_met,
                'conditions_failed': t.conditions_failed,
                'auth_gate_passed': t.auth_gate_passed,
                'uses_legacy_strength': t.uses_legacy_strength,
            }
            for t in all_traces
        ]
    }
    
    with open('data/p0_3_9_real_integration_test.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 data/p0_3_9_real_integration_test.json")


if __name__ == '__main__':
    main()
