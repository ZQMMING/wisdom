# -*- coding: utf-8 -*-
"""P0-3.6: Primitive/Condition 正式 Schema + Authorization 边界

核心约束：
1. 只有 CLASSICAL_EXPLICIT + VERIFIED 才能授权
2. generate_judgment() 必须审计，不能沿用旧逻辑
3. Condition 的 operator/value 必须有明确来源

执行顺序：
Schema → Authorization Gate → Resolver → 9 条重新验证 → 测试 → 审计
"""
import json
from dataclasses import dataclass, field
from typing import Optional, List, Any
from enum import Enum
from datetime import datetime
import inspect


class ConditionStatus(str, Enum):
    """条件状态"""
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"
    IMPLICIT = "IMPLICIT"
    COMPOSITE = "COMPOSITE"


class VerificationStatus(str, Enum):
    """验证状态"""
    STRUCTURED = "STRUCTURED"
    VERIFIED = "VERIFIED"
    UNRESOLVED = "UNRESOLVED"
    INVALID = "INVALID"

    @property
    def is_executable(self) -> bool:
        return self == VerificationStatus.VERIFIED

    @property
    def can_authorize_judgment(self) -> bool:
        return self == VerificationStatus.VERIFIED


class AuthorizationLevel(str, Enum):
    """授权级别

    关键约束：
    - CLASSICAL_EXPLICIT: 原典明确授权
    - CLASSICAL_IMPLICIT: 原典隐含授权（当前阶段不自动授权）
    - UNRESOLVED: 未解析，禁止授权
    """
    CLASSICAL_EXPLICIT = "CLASSICAL_EXPLICIT"
    CLASSICAL_IMPLICIT = "CLASSICAL_IMPLICIT"
    UNRESOLVED = "UNRESOLVED"


class PrimitiveType(str, Enum):
    """Primitive 类型"""
    PROPERTY = "property"
    RELATION = "relation"
    RULE = "rule"
    PATTERN = "pattern"


@dataclass(frozen=True)
class Condition:
    """Condition 最小验证单元

    关键约束：
    - operator/value 必须有明确来源（原典或 Canonical Calculation）
    - 不能由工程师自行决定阈值
    """
    text: str                              # 条件文本
    condition_type: str                    # NECESSARY/SUFFICIENT/SUPPORTING/CONSTRAINING/BLOCKING
    status: ConditionStatus                # RESOLVED/UNRESOLVED/IMPLICIT/COMPOSITE
    evidence_ref: str                      # 支撑证据 ID
    authorization: str                     # 原典授权文本
    feature_ref: Optional[str] = None      # 对应 Feature 字段（可为 None）
    operator: Optional[str] = None         # >/</==/contains/exists（可为 None）
    value: Optional[Any] = None            # 阈值（可为 None）
    source_documented: bool = True         # 是否已文档化来源

    def __post_init__(self):
        """验证约束"""
        # operator/value 必须有明确来源
        if self.operator is not None and self.value is not None:
            if not self.source_documented:
                raise ValueError(
                    f"Condition operator/value must be documented: {self.evidence_ref}"
                )


@dataclass(frozen=True)
class Primitive:
    """Primitive 最小验证单元"""
    evidence_id: str
    source_text: str
    subject: str
    domain: str
    primitive_name: str
    primitive_type: PrimitiveType
    conditions: List[Condition] = field(default_factory=list)
    scope: str = "primitive"
    authorization_level: AuthorizationLevel = AuthorizationLevel.CLASSICAL_EXPLICIT
    verification_status: VerificationStatus = VerificationStatus.STRUCTURED
    local_judgment: Optional[str] = None

    @property
    def is_authorized(self) -> bool:
        """检查是否获得授权
        
        关键约束：
        - 只有 CLASSICAL_EXPLICIT + VERIFIED 才能授权
        - CLASSICAL_IMPLICIT 不自动授权
        """
        if self.authorization_level != AuthorizationLevel.CLASSICAL_EXPLICIT:
            return False
        if self.verification_status != VerificationStatus.VERIFIED:
            return False
        return True


def check_authorization(primitive: Primitive) -> bool:
    """检查 Primitive 是否获得授权

    关键约束：
    - 只有 CLASSICAL_EXPLICIT + VERIFIED 才能授权
    - CLASSICAL_IMPLICIT 即使 VERIFIED 也不自动授权
    """
    return primitive.is_authorized


def audit_generate_judgment():
    """审计 generate_judgment() 函数

    目的：确保不使用旧评分/旧假设
    
    当前实现：返回 None（未实现），避免旧逻辑污染
    """
    # 临时方案：返回 None，避免旧逻辑污染
    # 后续需要实现新的 Judgment Generator
    return None


def resolve_local_judgment(primitive: Primitive) -> Optional[str]:
    """从 Primitive 推导 Local Judgment

    关键约束：
    - 仅当 VERIFIED 且授权时才产生 Judgment
    - 使用审计后的 generate_judgment()
    - 不使用旧评分逻辑
    """
    # 检查授权
    if not check_authorization(primitive):
        return None

    # 使用审计后的 Judgment Generator
    result = audit_generate_judgment()

    # 如果未实现，返回结构化说明
    if result is None:
        return f"[{primitive.evidence_id}] VERIFIED，待实现 Judgment Generator"

    return result


def analyze_primitive_v2(evidence: dict) -> Primitive:
    """分析单条证据（v2，符合新约束）"""
    evidence_id = evidence['evidence_id']
    source_text = evidence.get('source_text', '')
    subject = evidence.get('subject', '')
    domain = evidence.get('domain', '')
    primitive_name = evidence.get('primitive_name', '')

    # 判断 Primitive 类型
    primitive_type = classify_primitive_type(source_text)

    # 判断授权级别（保守策略）
    authorization_level = determine_authorization_level(evidence, primitive_type)

    # 分析条件
    conditions = analyze_conditions_v2(evidence, primitive_type)

    # 判断验证状态（保守策略）
    verification_status = determine_verification_status_v2(conditions, authorization_level)

    # 生成局部判断（需授权）
    local_judgment = resolve_local_judgment(Primitive(
        evidence_id=evidence_id,
        source_text=source_text,
        subject=subject,
        domain=domain,
        primitive_name=primitive_name,
        primitive_type=primitive_type,
        conditions=conditions,
        scope=evidence.get('scope', 'primitive'),
        authorization_level=authorization_level,
        verification_status=verification_status,
    ))

    return Primitive(
        evidence_id=evidence_id,
        source_text=source_text,
        subject=subject,
        domain=domain,
        primitive_name=primitive_name,
        primitive_type=primitive_type,
        conditions=conditions,
        scope=evidence.get('scope', 'primitive'),
        authorization_level=authorization_level,
        verification_status=verification_status,
        local_judgment=local_judgment,
    )


def determine_authorization_level(evidence: dict, primitive_type: PrimitiveType) -> AuthorizationLevel:
    """确定授权级别（保守策略）

    关键约束：
    - 只有 CLASSICAL_EXPLICIT 才可能授权
    - CLASSICAL_IMPLICIT 不自动授权
    """
    source_text = evidence.get('source_text', '')

    # 检查是否有明确原典引用
    explicit_indicators = ['明言', '明示', '直言', '原文', '原典']
    has_explicit = any(ind in source_text for ind in explicit_indicators)

    if has_explicit:
        return AuthorizationLevel.CLASSICAL_EXPLICIT
    else:
        # 保守：不轻易授权 IMPLICIT
        return AuthorizationLevel.UNRESOLVED


def classify_primitive_type(source_text: str) -> PrimitiveType:
    """分类 Primitive 类型"""
    property_keywords = ['参天', '柔', '猛烈', '柔中', '刚中', '中正', '纯清', '浊乱']
    if any(kw in source_text for kw in property_keywords):
        return PrimitiveType.PROPERTY

    relation_keywords = ['生', '克', '制', '化', '生扶', '泄耗']
    if any(kw in source_text for kw in relation_keywords):
        return PrimitiveType.RELATION

    rule_keywords = ['者', '当', '宜', '忌', '须', '必']
    if any(kw in source_text for kw in rule_keywords):
        return PrimitiveType.RULE

    pattern_keywords = ['从', '格', '局', '势']
    if any(kw in source_text for kw in pattern_keywords):
        return PrimitiveType.PATTERN

    return PrimitiveType.RULE


def analyze_conditions_v2(evidence: dict, primitive_type: PrimitiveType) -> List[Condition]:
    """分析条件（v2，符合新约束）

    关键约束：
    - operator/value 必须有明确来源
    - 原典无明确条件 → UNRESOLVED
    """
    conditions = evidence.get('conditions', [])
    source_text = evidence.get('source_text', '')

    result = []

    if not conditions:
        # 原典无明确条件结构
        if primitive_type == PrimitiveType.PROPERTY:
            # 性质描述，无条件
            result.append(Condition(
                text="",
                condition_type="SUPPORTING",
                status=ConditionStatus.UNRESOLVED,
                evidence_ref=evidence.get('evidence_id', ''),
                authorization=source_text,
                source_documented=True,
            ))
        else:
            result.append(Condition(
                text="",
                condition_type="SUPPORTING",
                status=ConditionStatus.IMPLICIT,
                evidence_ref=evidence.get('evidence_id', ''),
                authorization=source_text,
                source_documented=True,
            ))
        return result

    # 有明确条件
    for cond in conditions:
        text = cond.get('text', '')
        cond_type = cond.get('type', 'supporting')

        # 判断条件状态
        if not text or text.strip() == '':
            status = ConditionStatus.UNRESOLVED
        elif '须' in text or '当' in text or '必' in text:
            status = ConditionStatus.RESOLVED
        else:
            status = ConditionStatus.IMPLICIT

        # 检查 operator/value 来源
        feature_ref = cond.get('feature_ref')
        operator = cond.get('operator')
        value = cond.get('value')
        source_documented = cond.get('source_documented', True)

        result.append(Condition(
            text=text,
            condition_type=cond_type,
            status=status,
            evidence_ref=evidence.get('evidence_id', ''),
            authorization=cond.get('source', source_text),
            feature_ref=feature_ref,
            operator=operator,
            value=value,
            source_documented=source_documented,
        ))

    return result


def determine_verification_status_v2(conditions: List[Condition], authorization_level: AuthorizationLevel) -> VerificationStatus:
    """判断验证状态（v2，保守策略）

    关键约束：
    - 只有 RESOLVED + CLASSICAL_EXPLICIT 才可能 VERIFIED
    - 其他情况保持 UNRESOLVED 或 STRUCTURED
    """
    if authorization_level != AuthorizationLevel.CLASSICAL_EXPLICIT:
        return VerificationStatus.UNRESOLVED

    resolved = sum(1 for c in conditions if c.status == ConditionStatus.RESOLVED)
    unresolved = sum(1 for c in conditions if c.status == ConditionStatus.UNRESOLVED)

    if resolved > 0 and unresolved == 0:
        return VerificationStatus.VERIFIED
    elif resolved > 0 and unresolved > 0:
        return VerificationStatus.STRUCTURED
    else:
        return VerificationStatus.UNRESOLVED


def load_c_class_items():
    """加载 9 条 C 类证据"""
    with open('data/p0_3_4_attribution.json') as f:
        data = json.load(f)
    c_class = [a for a in data['results'] if a['category'] == 'C']
    return c_class


def load_evidence_details():
    """加载原始证据详情"""
    with open('data/p0_3_3_structured_evidence.json') as f:
        data = json.load(f)
    return {e['evidence_id']: e for e in data.get('results', [])}


def main():
    print("=== P0-3.6: Primitive/Condition 正式 Schema + Authorization 边界 ===\n")

    # 加载数据
    c_class_items = load_c_class_items()
    evidence_details = load_evidence_details()

    print(f"C 类证据数: {len(c_class_items)}\n")

    # 分析每条证据
    primitives = []
    status_counts = {s: 0 for s in VerificationStatus}
    auth_counts = {a: 0 for a in AuthorizationLevel}

    for item in c_class_items:
        evidence = evidence_details.get(item['evidence_id'], {})
        if not evidence:
            print(f"⚠️ 未找到证据: {item['evidence_id']}")
            continue

        primitive = analyze_primitive_v2(evidence)
        primitives.append(primitive)

        # 更新统计
        status_counts[primitive.verification_status] += 1
        auth_counts[primitive.authorization_level] += 1

        # 输出
        authorized = "✅ 授权" if primitive.is_authorized else "❌ 未授权"
        print(f"[{primitive.verification_status.value}] {primitive.evidence_id}")
        print(f"  授权级别: {primitive.authorization_level.value} {authorized}")
        print(f"  条件数: {len(primitive.conditions)}")
        print(f"  局部判断: {primitive.local_judgment}")
        print()

    # 输出报告
    print("=== 验证报告 ===")
    for status, count in status_counts.items():
        print(f"{status.value}: {count}")
    print()
    for auth, count in auth_counts.items():
        print(f"{auth.value}: {count}")

    # 保存结果
    output = {
        'generated': datetime.now().isoformat(),
        'summary': {
            'total': len(primitives),
            'by_status': {s.value: c for s, c in status_counts.items()},
            'by_authorization': {a.value: c for a, c in auth_counts.items()},
            'authorized_count': sum(1 for p in primitives if p.is_authorized),
        },
        'primitives': [
            {
                'evidence_id': p.evidence_id,
                'source_text': p.source_text[:100] + '...' if len(p.source_text) > 100 else p.source_text,
                'primitive_type': p.primitive_type.value,
                'authorization_level': p.authorization_level.value,
                'verification_status': p.verification_status.value,
                'is_authorized': p.is_authorized,
                'conditions_count': len(p.conditions),
                'resolved_count': sum(1 for c in p.conditions if c.status == ConditionStatus.RESOLVED),
                'local_judgment': p.local_judgment,
            }
            for p in primitives
        ]
    }

    with open('data/p0_3_6_primitive_schema.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到 data/p0_3_6_primitive_schema.json")


if __name__ == '__main__':
    main()
