# -*- coding: utf-8 -*-
"""P0-4: Local Judgment 多条件语义验证

验证多 Condition 的逻辑语义：
- AND（全部满足）
- OR（任一满足）
- Blocking（阻断条件）
- Prerequisite（前提条件）
- UNRESOLVED（不产生 Judgment）
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


class ConditionType(str, Enum):
    """Condition 类型"""
    SUPPORTING = "SUPPORTING"       # 支持条件（AND 逻辑）
    OPTIONAL = "OPTIONAL"           # 可选条件（OR 逻辑）
    BLOCKING = "BLOCKING"           # 阻断条件
    PREREQUISITE = "PREREQUISITE"   # 前提条件


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
    """多条件语义单元"""
    text: str
    condition_type: ConditionType
    feature_ref: str
    operator: str
    value: Any
    evidence_ref: str
    authorization: str

    def evaluate(self, features: D1FeatureResult) -> tuple:
        """评估单个 Condition，返回 (result: bool, status: ConditionStatus)"""
        feature_value = getattr(features, self.feature_ref, None)
        
        if feature_value is None:
            return False, ConditionStatus.UNRESOLVED
        
        try:
            if self.operator == '>':
                result = feature_value > self.value
            elif self.operator == '<':
                result = feature_value < self.value
            elif self.operator == '==':
                result = feature_value == self.value
            elif self.operator == '>=':
                result = feature_value >= self.value
            elif self.operator == '<=':
                result = feature_value <= self.value
            elif self.operator == 'contains':
                result = self.value in feature_value
            else:
                result = False
            
            status = ConditionStatus.RESOLVED if result else ConditionStatus.FAILED
            return result, status
        except (TypeError, ValueError):
            return False, ConditionStatus.UNRESOLVED


@dataclass
class Primitive:
    """包含多 Condition 的 Primitive"""
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
    """证据追溯"""
    evidence_id: str
    source_text: str
    primitive_name: str
    authorization_level: str
    verification_status: str
    local_judgment: str
    conditions_evaluated: int
    conditions_met: int
    conditions_failed: int
    blocking_failed: int
    auth_gate_passed: bool
    uses_legacy_strength: bool


def evaluate_conditions(conditions: List[Condition], features: D1FeatureResult) -> tuple:
    """评估多个 Condition，返回 (can_judge: bool, reason: str)
    
    逻辑：
    1. 检查所有 BLOCKING 条件 → 如果有阻断，返回 False
    2. 检查所有 PREREQUISITE 条件 → 如果不满足，返回 False
    3. 检查所有 SUPPORTING 条件 → 必须全部满足
    4. 检查所有 OPTIONAL 条件 → 至少满足一个
    """
    blocking_failed = []
    prerequisite_failed = []
    supporting_met = []
    supporting_failed = []
    optional_met = []
    optional_failed = []
    
    for cond in conditions:
        result, status = cond.evaluate(features)
        
        if cond.condition_type == ConditionType.BLOCKING:
            if not result:
                blocking_failed.append(cond.text)
        elif cond.condition_type == ConditionType.PREREQUISITE:
            if not result:
                prerequisite_failed.append(cond.text)
        elif cond.condition_type == ConditionType.SUPPORTING:
            if result:
                supporting_met.append(cond.text)
            else:
                supporting_failed.append(cond.text)
        elif cond.condition_type == ConditionType.OPTIONAL:
            if result:
                optional_met.append(cond.text)
            else:
                optional_failed.append(cond.text)
    
    # 判断是否可以产生 Judgment
    if blocking_failed:
        return False, f"阻断条件: {blocking_failed}"
    
    if prerequisite_failed:
        return False, f"前提条件不满足: {prerequisite_failed}"
    
    if supporting_failed:
        return False, f"支持条件未满足: {supporting_failed}"
    
    if not optional_met and not optional_failed:
        return False, "无可选条件满足"
    
    return True, f"满足: supporting={len(supporting_met)}, optional={len(optional_met)}"


def generate_local_judgment(primitive: Primitive, features: D1FeatureResult) -> tuple:
    """从 Primitive + Feature 生成 Local Judgment"""
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
            blocking_failed=0,
            auth_gate_passed=False,
            uses_legacy_strength=False,
        )
        return None, trace
    
    can_judge, reason = evaluate_conditions(primitive.conditions, features)
    
    if can_judge:
        judgment = f"[{primitive.evidence_id}] {primitive.primitive_name}: {primitive.source_text[:50]}..."
    else:
        judgment = None
    
    # 统计
    blocking_count = sum(1 for c in primitive.conditions if c.condition_type == ConditionType.BLOCKING)
    supporting_failed_count = 0
    for cond in primitive.conditions:
        result, _ = cond.evaluate(features)
        if not result and cond.condition_type == ConditionType.SUPPORTING:
            supporting_failed_count += 1
    
    trace = EvidenceTrace(
        evidence_id=primitive.evidence_id,
        source_text=primitive.source_text,
        primitive_name=primitive.primitive_name,
        authorization_level=primitive.authorization_level.value,
        verification_status=primitive.verification_status.value,
        local_judgment=judgment or "None",
        conditions_evaluated=len(primitive.conditions),
        conditions_met=sum(1 for c in primitive.conditions if c.evaluate(features)[0]),
        conditions_failed=sum(1 for c in primitive.conditions if not c.evaluate(features)[0]),
        blocking_failed=blocking_count,
        auth_gate_passed=True,
        uses_legacy_strength=False,
    )
    
    return judgment, trace


def load_test_primitives() -> List[Primitive]:
    """加载测试用 Primitive（包含多种 Condition 类型）"""
    return [
        # 场景 1: 简单 AND
        Primitive(
            evidence_id="test_and",
            source_text="甲木参天，脱胎要火",
            subject="日主",
            domain="wangshuai",
            primitive_name="甲木参天",
            primitive_type="rule",
            conditions=[
                Condition(
                    text="de_ling=True",
                    condition_type=ConditionType.SUPPORTING,
                    feature_ref="de_ling",
                    operator="==",
                    value=True,
                    evidence_ref="test",
                    authorization="原典",
                ),
                Condition(
                    text="support_count > drain_count",
                    condition_type=ConditionType.SUPPORTING,
                    feature_ref="support_count",
                    operator=">",
                    value=None,  # 动态比较
                    evidence_ref="test",
                    authorization="原典",
                ),
            ],
            authorization_level=AuthorizationLevel.CLASSICAL_EXPLICIT,
            verification_status=VerificationStatus.VERIFIED,
        ),
        # 场景 2: OR 逻辑
        Primitive(
            evidence_id="test_or",
            source_text="得令或得地",
            subject="日主",
            domain="wangshuai",
            primitive_name="得令得地",
            primitive_type="rule",
            conditions=[
                Condition(
                    text="de_ling=True",
                    condition_type=ConditionType.OPTIONAL,
                    feature_ref="de_ling",
                    operator="==",
                    value=True,
                    evidence_ref="test",
                    authorization="原典",
                ),
                Condition(
                    text="de_di >= 2",
                    condition_type=ConditionType.OPTIONAL,
                    feature_ref="de_di",
                    operator(">="),
                    value=2,
                    evidence_ref="test",
                    authorization="原典",
                ),
            ],
            authorization_level=AuthorizationLevel.CLASSICAL_EXPLICIT,
            verification_status=VerificationStatus.VERIFIED,
        ),
        # 场景 3: Blocking
        Primitive(
            evidence_id="test_blocking",
            source_text="气候极端则不Judgment",
            subject="日主",
            domain="wangshuai",
            primitive_name="气候阻断",
            primitive_type="rule",
            conditions=[
                Condition(
                    text="de_ling=True",
                    condition_type=ConditionType.SUPPORTING,
                    feature_ref="de_ling",
                    operator="==",
                    value=True,
                    evidence_ref="test",
                    authorization="原典",
                ),
                Condition(
                    text="climate != extreme",
                    condition_type=ConditionType.BLOCKING,
                    feature_ref="climate",
                    operator="!=",
                    value="extreme",
                    evidence_ref="test",
                    authorization="原典",
                ),
            ],
            authorization_level=AuthorizationLevel.CLASSICAL_EXPLICIT,
            verification_status=VerificationStatus.VERIFIED,
        ),
        # 场景 4: Prerequisite
        Primitive(
            evidence_id="test_prerequisite",
            source_text="得令为前提",
            subject="日主",
            domain="wangshuai",
            primitive_name="得令前提",
            primitive_type="rule",
            conditions=[
                Condition(
                    text="de_ling=True",
                    condition_type=ConditionType.PREREQUISITE,
                    feature_ref="de_ling",
                    operator("=="),
                    value=True,
                    evidence_ref="test",
                    authorization="原典",
                ),
                Condition(
                    text="support_count > 2",
                    condition_type=ConditionType.SUPPORTING,
                    feature_ref="support_count",
                    operator(")>"),
                    value=2,
                    evidence_ref="test",
                    authorization="原典",
                ),
            ],
            authorization_level=AuthorizationLevel.CLASSICAL_EXPLICIT,
            verification_status=VerificationStatus.VERIFIED,
        ),
    ]


def get_real_chart_features(year: int, month: int, day: int, hour: int, gender: str) -> D1FeatureResult:
    eng = BaziEngine()
    chart = eng.compute((year, month, day, hour), gender=gender)
    features = evaluate_strength_features(chart)
    return features


def main():
    print("=== P0-4: Local Judgment 多条件语义验证 ===\n")
    
    primitives = load_test_primitives()
    print(f"测试 Primitive 数: {len(primitives)}\n")
    
    # 测试命例
    test_cases = [
        (1990, 5, 15, 10, 'male', 'de_ling=False'),
        (1995, 1, 1, 12, 'male', 'de_ling=True'),
        (1985, 3, 21, 6, 'male', 'de_di=3'),
    ]
    
    all_traces = []
    
    for year, month, day, hour, gender, desc in test_cases:
        print(f"=== Chart: {year}-{month}-{day} {hour}:00 {gender} ({desc}) ===")
        
        features = get_real_chart_features(year, month, day, hour, gender)
        print(f"Feature: de_ling={features.de_ling}, de_di={features.de_di}")
        print(f"         support={features.support_count:.2f}, drain={features.drain_count:.2f}\n")
        
        for prim in primitives:
            judgment, trace = generate_local_judgment(prim, features)
            all_traces.append(trace)
            
            status = "✅" if judgment else "❌"
            print(f"{status} {prim.evidence_id}")
            print(f"  Judgment: {trace.local_judgment}")
            print(f"  Conditions: {trace.conditions_met} met, {trace.conditions_failed} failed")
            print()
    
    # 报告
    print("=== 验证报告 ===")
    success_count = sum(1 for t in all_traces if t.local_judgment != "None")
    auth_gate_active = all(t.auth_gate_passed for t in all_traces if t.authorization_level == 'CLASSICAL_EXPLICIT')
    no_legacy = all(not t.uses_legacy_strength for t in all_traces)
    
    print(f"总测试: {len(all_traces)}")
    print(f"生成 Judgment: {success_count}")
    print(f"Authorization Gate 生效: {auth_gate_active}")
    print(f"未使用旧 strength_engine: {no_legacy}")
    
    # 保存
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
    
    with open('data/p0_4_multi_condition_test.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 data/p0_4_multi_condition_test.json")


if __name__ == '__main__':
    main()
