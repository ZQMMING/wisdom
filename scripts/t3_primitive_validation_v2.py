# -*- coding: utf-8 -*-
"""T3 Primitive 小闭环验证脚本 v2（应用 Mapping 规则）

验证链路: Evidence → Primitive → Condition → Mapping → Local Judgment → Authorization
"""
import json
from dataclasses import dataclass, field, replace
from typing import Optional, List, Any, Dict
from enum import Enum


class ConditionType(str, Enum):
    NECESSARY = "necessary"
    SUFFICIENT = "sufficient"
    SUPPORTING = "supporting"
    CONSTRAINING = "constraining"
    BLOCKING = "blocking"


class Scope(str, Enum):
    PRIMITIVE = "primitive"
    COMPOSITE = "composite"
    LOCAL = "local"


class AuthorizationLevel(str, Enum):
    CLASSICAL_EXPLICIT = "CLASSICAL_EXPLICIT"
    CLASSICAL_IMPLICIT = "CLASSICAL_IMPLICIT"
    UNRESOLVED = "UNRESOLVED"


class VerificationStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    INVALID = "INVALID"
    PARTIAL = "PARTIAL"


@dataclass(frozen=True)
class Condition:
    text: str
    condition_type: ConditionType
    feature_ref: Optional[str] = None
    operator: Optional[str] = None
    value: Optional[Any] = None
    authorization: Optional[str] = None


@dataclass(frozen=True)
class Primitive:
    evidence_id: str
    source_text: str
    subject: str
    domain: str
    primitive_name: str
    conditions: List[Condition] = field(default_factory=list)
    scope: Scope = Scope.PRIMITIVE
    authorization_level: AuthorizationLevel = AuthorizationLevel.CLASSICAL_EXPLICIT
    verification_status: VerificationStatus = VerificationStatus.PENDING
    verification_result: Optional[str] = None


@dataclass
class ValidationReport:
    total_samples: int = 0
    verified: int = 0
    invalid: int = 0
    pending: int = 0
    partial: int = 0
    
    def add_result(self, primitive: Primitive):
        if primitive.verification_status == VerificationStatus.VERIFIED:
            self.verified += 1
        elif primitive.verification_status == VerificationStatus.INVALID:
            self.invalid += 1
        elif primitive.verification_status == VerificationStatus.PARTIAL:
            self.partial += 1
        else:
            self.pending += 1
    
    @property
    def pass_rate(self) -> float:
        if self.total_samples == 0:
            return 0.0
        return self.verified / self.total_samples


def load_mapping_rules() -> Dict[str, Dict]:
    """加载 Mapping 规则"""
    with open('data/t3_mapping_rules.json') as f:
        data = json.load(f)
    
    mappings = {}
    for m in data.get('mappings', []):
        mappings[m['evidence_id']] = m
    return mappings


def select_samples(evidence_data: list, target_count: int = 30) -> List[Dict]:
    """选取样本：覆盖多经典、多 domain、有条件/无条件"""
    # 优先选有条件的
    with_conditions = [e for e in evidence_data if e.get('has_conditions')]
    without_conditions = [e for e in evidence_data if not e.get('has_conditions')]
    
    selected = []
    seen_ids = set()
    
    for e in with_conditions[:target_count // 2]:
        if e['evidence_id'] not in seen_ids:
            selected.append(e)
            seen_ids.add(e['evidence_id'])
    
    for e in without_conditions:
        if e['evidence_id'] not in seen_ids and len(selected) < target_count:
            selected.append(e)
            seen_ids.add(e['evidence_id'])
    
    return selected[:target_count]


def validate_primitive_with_mapping(primitive: Primitive, mapping_rules: Dict) -> Primitive:
    """应用 Mapping 规则验证 Primitive"""
    
    # 检查是否有对应的 Mapping 规则
    mapping = mapping_rules.get(primitive.evidence_id)
    
    if mapping:
        # 有 Mapping 规则：验证为 VERIFIED
        return replace(primitive,
            verification_status=VerificationStatus.VERIFIED,
            verification_result=f"Mapping 规则已定义: {mapping['feature_ref']}"
        )
    
    # 无 Mapping 规则：按原逻辑判断
    if primitive.authorization_level == AuthorizationLevel.CLASSICAL_EXPLICIT:
        if primitive.conditions:
            # 有条件但无 Mapping：PENDING
            return replace(primitive,
                verification_status=VerificationStatus.PENDING,
                verification_result="条件无法映射到现有特征"
            )
        else:
            # 无条件：VERIFIED
            return replace(primitive,
                verification_status=VerificationStatus.VERIFIED,
                verification_result="无条件，原典授权明确"
            )
    
    return replace(primitive,
        verification_status=VerificationStatus.PENDING,
        verification_result="授权级别不足"
    )


def main():
    # 加载数据
    with open('data/p0_3_3_structured_evidence.json') as f:
        data = json.load(f)
    
    with open('data/t3_mapping_rules.json') as f:
        mapping_data = json.load(f)
    
    evidence_data = data.get('results', [])
    mapping_rules = {m['evidence_id']: m for m in mapping_data.get('mappings', [])}
    
    print(f"总证据数: {len(evidence_data)}")
    print(f"Mapping 规则数: {len(mapping_rules)}")
    
    # 选取样本
    samples = select_samples(evidence_data, target_count=30)
    print(f"选取样本: {len(samples)} 条")
    
    # 验证每条样本
    report = ValidationReport(total_samples=len(samples))
    results = []
    
    for sample in samples:
        # 构建 Primitive
        conditions = []
        for cond in sample.get('conditions', []):
            conditions.append(Condition(
                text=cond.get('text', ''),
                condition_type=ConditionType(cond.get('type', 'supporting')),
                feature_ref=cond.get('feature_ref'),
                operator=cond.get('operator'),
                value=cond.get('value'),
                authorization=cond.get('source', sample.get('source_text', ''))
            ))
        
        primitive = Primitive(
            evidence_id=sample.get('evidence_id'),
            source_text=sample.get('source_text', ''),
            subject=sample.get('subject', ''),
            domain=sample.get('domain', ''),
            primitive_name=sample.get('primitive_name', ''),
            conditions=conditions,
            scope=Scope(sample.get('scope', 'primitive')),
            authorization_level=AuthorizationLevel(sample.get('authorization_level', 'CLASSICAL_EXPLICIT')),
        )
        
        # 应用 Mapping 规则验证
        primitive = validate_primitive_with_mapping(primitive, mapping_rules)
        report.add_result(primitive)
        results.append(primitive)
    
    # 输出报告
    print(f"\n=== T3 验证报告（应用 Mapping 后）===")
    print(f"总样本: {report.total_samples}")
    print(f"通过: {report.verified}")
    print(f"失败: {report.invalid}")
    print(f"待定: {report.pending}")
    print(f"部分通过: {report.partial}")
    print(f"通过率: {report.pass_rate:.1%}")
    
    # 显示 pending 项
    if report.pending > 0:
        print(f"\n--- 待验证项目 ---")
        for r in results:
            if r.verification_status == VerificationStatus.PENDING:
                print(f"  [{r.domain}] {r.evidence_id}: {r.verification_result}")
    
    # 保存结果
    output = {
        'report': {
            'total_samples': report.total_samples,
            'verified': report.verified,
            'invalid': report.invalid,
            'pending': report.pending,
            'partial': report.partial,
            'pass_rate': report.pass_rate,
        },
        'mapping_rules_count': len(mapping_rules),
        'results': [
            {
                'evidence_id': r.evidence_id,
                'domain': r.domain,
                'scope': r.scope.value,
                'authorization_level': r.authorization_level.value,
                'verification_status': r.verification_status.value,
                'verification_result': r.verification_result,
                'condition_count': len(r.conditions),
            }
            for r in results
        ]
    }
    
    with open('data/t3_primitive_validation_result_v2.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 data/t3_primitive_validation_result_v2.json")


if __name__ == '__main__':
    main()
