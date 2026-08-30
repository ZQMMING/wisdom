# -*- coding: utf-8 -*-
"""P0-3.5: Primitive/Condition 结构化验证（9 条 C 类）

验证链路：
原典 Evidence → Primitive → Condition → Local Judgment

约束：
1. 只做 9 条 C 类，不扩展其他
2. 禁止产生 Composite Judgment
3. 禁止替古人补 AND/OR 条件
4. 允许 CONDITION_STATUS = UNRESOLVED
"""
import json
from dataclasses import dataclass, field
from typing import Optional, List, Any
from enum import Enum
from datetime import datetime


class ConditionStatus(str, Enum):
    """条件状态"""
    RESOLVED = "RESOLVED"           # 条件已解析
    UNRESOLVED = "UNRESOLVED"       # 条件未解析（原典无明确条件）
    IMPLICIT = "IMPLICIT"           # 隐含条件（需标注）
    COMPOSITE = "COMPOSITE"         # 复合条件（仅用于 C 类分析）


class PrimitiveType(str, Enum):
    """Primitive 类型"""
    PROPERTY = "property"           # 性质描述（如"甲木参天"）
    RELATION = "relation"           # 关系描述（如"生克制化"）
    RULE = "rule"                   # 规则描述（如"得令者临官帝旺"）
    PATTERN = "pattern"             # 格局描述（如"从格"）


@dataclass(frozen=True)
class Condition:
    """Condition 最小验证单元"""
    text: str                              # 条件文本
    condition_type: str                    # NECESSARY/SUFFICIENT/SUPPORTING/CONSTRAINING/BLOCKING
    status: ConditionStatus                # RESOLVED/UNRESOLVED/IMPLICIT/COMPOSITE
    evidence_ref: str                      # 支撑证据 ID
    authorization: str                     # 原典授权文本
    feature_ref: Optional[str] = None      # 对应 Feature 字段（可为 None）
    operator: Optional[str] = None         # >/</==/contains/exists（可为 None）
    value: Optional[Any] = None            # 阈值（可为 None）


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
    scope: str = "primitive"               # primitive/composite/local
    authorization_level: str = "CLASSICAL_EXPLICIT"
    verification_status: str = "PENDING"   # PENDING/VERIFIED/PARTIAL/INVALID
    local_judgment: Optional[str] = None   # 局部判断结果


@dataclass
class ValidationReport:
    """验证报告"""
    total: int = 0
    verified: int = 0
    unresolved: int = 0
    partial: int = 0
    invalid: int = 0
    
    @property
    def pass_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return self.verified / self.total


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


def analyze_primitive(evidence: dict) -> Primitive:
    """分析单条证据，构建 Primitive
    
    关键原则：
    - 不替古人补条件
    - 允许 UNRESOLVED
    - 区分性质描述 vs 条件关系
    """
    evidence_id = evidence['evidence_id']
    source_text = evidence.get('source_text', '')
    subject = evidence.get('subject', '')
    domain = evidence.get('domain', '')
    primitive_name = evidence.get('primitive_name', '')
    
    # 判断 Primitive 类型
    primitive_type = classify_primitive_type(source_text)
    
    # 分析条件
    conditions = analyze_conditions(evidence, primitive_type)
    
    # 判断验证状态
    verification_status = determine_verification_status(conditions)
    
    # 生成局部判断
    local_judgment = generate_local_judgment(evidence_id, conditions, primitive_type)
    
    return Primitive(
        evidence_id=evidence_id,
        source_text=source_text,
        subject=subject,
        domain=domain,
        primitive_name=primitive_name,
        primitive_type=primitive_type,
        conditions=conditions,
        scope=evidence.get('scope', 'primitive'),
        authorization_level=evidence.get('authorization_level', 'CLASSICAL_EXPLICIT'),
        verification_status=verification_status,
        local_judgment=local_judgment,
    )


def classify_primitive_type(source_text: str) -> PrimitiveType:
    """分类 Primitive 类型"""
    
    # 性质描述（如"甲木参天"）
    property_keywords = ['参天', '柔', '猛烈', '柔中', '刚中', '中正', '纯清', '浊乱']
    if any(kw in source_text for kw in property_keywords):
        return PrimitiveType.PROPERTY
    
    # 关系描述（如"生克制化"）
    relation_keywords = ['生', '克', '制', '化', '生扶', '泄耗']
    if any(kw in source_text for kw in relation_keywords):
        return PrimitiveType.RELATION
    
    # 规则描述（如"得令者临官帝旺"）
    rule_keywords = ['者', '当', '宜', '忌', '须', '当', '必']
    if any(kw in source_text for kw in rule_keywords):
        return PrimitiveType.RULE
    
    # 格局描述（如"从格"）
    pattern_keywords = ['从', '格', '局', '势']
    if any(kw in source_text for kw in pattern_keywords):
        return PrimitiveType.PATTERN
    
    # 默认
    return PrimitiveType.RULE


def analyze_conditions(evidence: dict, primitive_type: PrimitiveType) -> List[Condition]:
    """分析条件
    
    关键原则：
    - 不替古人补条件
    - 原典无明确条件 → UNRESOLVED
    - 明确条件 → RESOLVED
    """
    conditions = evidence.get('conditions', [])
    source_text = evidence.get('source_text', '')
    
    result = []
    
    if not conditions:
        # 原典无明确条件结构
        # 根据 Primitive 类型判断
        if primitive_type == PrimitiveType.PROPERTY:
            # 性质描述，无条件
            result.append(Condition(
                text="",
                condition_type="SUPPORTING",
                status=ConditionStatus.UNRESOLVED,
                evidence_ref=evidence.get('evidence_id', ''),
                authorization=source_text,
            ))
        else:
            # 其他类型，可能有隐含条件
            result.append(Condition(
                text="",
                condition_type="SUPPORTING",
                status=ConditionStatus.IMPLICIT,
                evidence_ref=evidence.get('evidence_id', ''),
                authorization=source_text,
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
        
        result.append(Condition(
            text=text,
            condition_type=cond_type,
            status=status,
            evidence_ref=evidence.get('evidence_id', ''),
            authorization=cond.get('source', source_text),
        ))
    
    return result


def determine_verification_status(conditions: List[Condition]) -> str:
    """判断验证状态"""
    if not conditions:
        return "INVALID"
    
    resolved = sum(1 for c in conditions if c.status == ConditionStatus.RESOLVED)
    unresolved = sum(1 for c in conditions if c.status == ConditionStatus.UNRESOLVED)
    
    if resolved > 0 and unresolved == 0:
        return "VERIFIED"
    elif resolved > 0 and unresolved > 0:
        return "PARTIAL"
    else:
        return "UNRESOLVED"


def generate_local_judgment(evidence_id: str, conditions: List[Condition], primitive_type: PrimitiveType) -> str:
    """生成局部判断（不产生全局 verdict）
    
    关键：只返回当前 Primitive 的局部信息，不推导身强身弱
    """
    if primitive_type == PrimitiveType.PROPERTY:
        return f"{evidence_id}: 性质描述，无条件结构"
    
    resolved_count = sum(1 for c in conditions if c.status == ConditionStatus.RESOLVED)
    unresolved_count = sum(1 for c in conditions if c.status == ConditionStatus.UNRESOLVED)
    
    if resolved_count > 0:
        return f"{evidence_id}: 有 {resolved_count} 条明确条件"
    elif unresolved_count > 0:
        return f"{evidence_id}: 无明确条件，性质描述"
    else:
        return f"{evidence_id}: 条件待解析"


def main():
    print("=== P0-3.5: Primitive/Condition 结构化验证 ===\n")
    
    # 加载数据
    c_class_items = load_c_class_items()
    evidence_details = load_evidence_details()
    
    print(f"C 类证据数: {len(c_class_items)}\n")
    
    # 分析每条证据
    primitives = []
    report = ValidationReport(total=len(c_class_items))
    
    for item in c_class_items:
        evidence = evidence_details.get(item['evidence_id'], {})
        if not evidence:
            print(f"⚠️ 未找到证据: {item['evidence_id']}")
            continue
        
        primitive = analyze_primitive(evidence)
        primitives.append(primitive)
        
        # 更新报告
        if primitive.verification_status == "VERIFIED":
            report.verified += 1
        elif primitive.verification_status == "UNRESOLVED":
            report.unresolved += 1
        elif primitive.verification_status == "PARTIAL":
            report.partial += 1
        else:
            report.invalid += 1
        
        # 输出
        print(f"[{primitive.verification_status}] {primitive.evidence_id}")
        print(f"  类型: {primitive.primitive_type.value}")
        print(f"  条件数: {len(primitive.conditions)}")
        print(f"  局部判断: {primitive.local_judgment}")
        print()
    
    # 输出报告
    print("=== 验证报告 ===")
    print(f"总数: {report.total}")
    print(f"通过: {report.verified}")
    print(f"未解析: {report.unresolved}")
    print(f"部分通过: {report.partial}")
    print(f"失败: {report.invalid}")
    print(f"通过率: {report.pass_rate:.1%}")
    
    # 保存结果
    output = {
        'generated': datetime.now().isoformat(),
        'report': {
            'total': report.total,
            'verified': report.verified,
            'unresolved': report.unresolved,
            'partial': report.partial,
            'invalid': report.invalid,
            'pass_rate': report.pass_rate,
        },
        'primitives': [
            {
                'evidence_id': p.evidence_id,
                'source_text': p.source_text[:100] + '...' if len(p.source_text) > 100 else p.source_text,
                'primitive_type': p.primitive_type.value,
                'conditions_count': len(p.conditions),
                'resolved_count': sum(1 for c in p.conditions if c.status == ConditionStatus.RESOLVED),
                'unresolved_count': sum(1 for c in p.conditions if c.status == ConditionStatus.UNRESOLVED),
                'verification_status': p.verification_status,
                'local_judgment': p.local_judgment,
            }
            for p in primitives
        ]
    }
    
    with open('data/p0_3_5_primitive_validation.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 data/p0_3_5_primitive_validation.json")


if __name__ == '__main__':
    main()
