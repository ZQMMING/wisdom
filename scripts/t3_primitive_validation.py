# -*- coding: utf-8 -*-
"""T3 Primitive 小闭环验证脚本

选取 30 条 Evidence 样本，验证：
Evidence → Primitive → Condition → Local Judgment → Authorization
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
    """Condition 最小验证单元"""
    text: str
    condition_type: ConditionType
    feature_ref: Optional[str] = None      # 对应 D1FeatureResult 字段
    operator: Optional[str] = None         # >/</==/contains/exists
    value: Optional[Any] = None            # 阈值或预期值
    authorization: Optional[str] = None   # 原典授权文本


@dataclass(frozen=True)
class Primitive:
    """Primitive 最小验证单元"""
    evidence_id: str
    source_text: str
    subject: str
    domain: str
    primitive_name: str
    conditions: List[Condition] = field(default_factory=list)
    scope: Scope = Scope.PRIMITIVE
    authorization_level: AuthorizationLevel = AuthorizationLevel.CLASSICAL_EXPLICIT
    verification_status: VerificationStatus = VerificationStatus.PENDING
    verification_result: Optional[str] = None  # 验证通过/失败/待定


@dataclass
class ValidationReport:
    """T3 验证报告"""
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


def select_samples(evidence_data: list, target_count: int = 30) -> List[Dict]:
    """选取样本：覆盖多经典、多 domain、有条件/无条件"""
    import random
    
    # 按条件存在分组
    with_conditions = [e for e in evidence_data if e.get('has_conditions')]
    without_conditions = [e for e in evidence_data if not e.get('has_conditions')]
    
    # 按 domain 分组
    by_domain = {}
    for e in evidence_data:
        domain = e.get('domain', 'unknown')
        by_domain.setdefault(domain, []).append(e)
    
    selected = []
    seen_ids = set()
    
    # 优先选有条件的
    for e in with_conditions[:target_count // 2]:
        if e['evidence_id'] not in seen_ids:
            selected.append(e)
            seen_ids.add(e['evidence_id'])
    
    # 补满到 target_count
    for e in without_conditions:
        if e['evidence_id'] not in seen_ids and len(selected) < target_count:
            selected.append(e)
            seen_ids.add(e['evidence_id'])
    
    # 确保覆盖各 domain
    for domain, items in by_domain.items():
        for e in items:
            if e['evidence_id'] not in seen_ids and len(selected) < target_count:
                selected.append(e)
                seen_ids.add(e['evidence_id'])
    
    return selected[:target_count]


def validate_primitive(primitive: Primitive, features: Optional[dict] = None) -> Primitive:
    """验证单个 Primitive
    
    验证链路:
    Evidence (原典原文) → Primitive → Condition → Local Judgment → Authorization
    """
    # 检查 Authorization
    if primitive.authorization_level == AuthorizationLevel.CLASSICAL_EXPLICIT:
        # 有明确原典授权，验证条件是否可映射到特征
        if primitive.conditions:
            # 有条件：检查是否能在 D1FeatureResult 中找到对应字段
            valid_conditions = []
            for cond in primitive.conditions:
                if cond.feature_ref and features:
                    # 尝试在 features 中查找对应值
                    if cond.feature_ref in features:
                        valid_conditions.append(cond)
            
            if len(valid_conditions) == len(primitive.conditions):
                primitive = replace(primitive,
                    verification_status=VerificationStatus.VERIFIED,
                    verification_result="所有条件可映射到特征"
                )
            elif valid_conditions:
                primitive = replace(primitive,
                    verification_status=VerificationStatus.PARTIAL,
                    verification_result=f"部分条件可映射 ({len(valid_conditions)}/{len(primitive.conditions)})"
                )
            else:
                primitive = replace(primitive,
                    verification_status=VerificationStatus.PENDING,
                    verification_result="条件无法映射到现有特征"
                )
        else:
            # 无条件：直接验证为 VERIFIED
            primitive = replace(primitive,
                verification_status=VerificationStatus.VERIFIED,
                verification_result="无条件，原典授权明确"
            )
    else:
        primitive = primitive._replace(
            verification_status=VerificationStatus.PENDING,
            verification_result="授权级别不足"
        )
    
    return primitive


def main():
    # 加载证据数据
    with open('data/p0_3_3_structured_evidence.json') as f:
        data = json.load(f)
    
    evidence_data = data.get('results', [])
    print(f"总证据数: {len(evidence_data)}")
    
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
        
        # 验证
        primitive = validate_primitive(primitive)
        report.add_result(primitive)
        results.append(primitive)
    
    # 输出报告
    print(f"\n=== T3 验证报告 ===")
    print(f"总样本: {report.total_samples}")
    print(f"通过: {report.verified}")
    print(f"失败: {report.invalid}")
    print(f"待定: {report.pending}")
    print(f"部分通过: {report.partial}")
    print(f"通过率: {report.pass_rate:.1%}")
    
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
    
    with open('data/t3_primitive_validation_result.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 data/t3_primitive_validation_result.json")


if __name__ == '__main__':
    main()
