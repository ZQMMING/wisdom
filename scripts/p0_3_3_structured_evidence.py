#!/usr/bin/env python3
"""
P0-3.3: 结构化 Evidence → Primitive/Condition 提取

核心原则:
1. 原典说了什么？ → source_text + subject + domain
2. 在什么条件下说？ → conditions (如果存在)
3. 判断的对象是什么？ → target (primitive/status/state)
4. 是局部规则还是综合规则？ → scope (LOCAL/COMPOSITE)

禁止:
- 不要直接转成"身强/身弱规则"
- 不要合并多条证据成单一结论
- 不要假设条件成立

治理:
- 原典授权 ≠ 条件成立 ≠ 断事结论授权
- 整体旺衰保持 UNRESOLVED
"""
import json
import os
import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum

# ============================================================
# 数据结构定义
# ============================================================

class Scope(str, Enum):
    """规则作用域"""
    LOCAL = "local"              # 局部规则: 单一条件判断
    COMPOSITE = "composite"      # 综合规则: 多条件组合
    PRIMITIVE = "primitive"      # 基本Primitive: 不可再分的事实

class ConditionType(str, Enum):
    """条件类型"""
    NECESSARY = "necessary"      # 必要条件
    SUFFICIENT = "sufficient"    # 充分条件
    SUPPORTING = "supporting"    # 支持条件
    CONSTRAINING = "constraining" # 制约条件
    BLOCKING = "blocking"        # 阻断条件
    QUALIFYING = "qualifying"    # 限定条件

@dataclass(frozen=True)
class StructuredEvidence:
    """结构化证据 — 从EXACT_PRIMARY提取的结构化单元"""
    
    # === 来源 ===
    evidence_id: str                          # 唯一ID
    classic: str                              # 经典名称
    category: str                             # 分类
    original_key: str                         # 原文key
    source_text: str                          # 原文
    
    # === 结构化提取 ===
    subject: str                              # 判断主体（如"甲木"、"日主"、"月令"）
    domain: str                               # 辨证域（wangshuai/pattern/climate/ten_god）
    primitive_name: str                       # Primitive名称（如"得令"、"有根"）
    primitive_type: Scope                     # Primitive类型
    
    # === 条件分析 ===
    conditions: List[Dict[str, Any]] = field(default_factory=list)  # 条件列表
    has_conditions: bool = False              # 是否含条件
    
    # === 范围判定 ===
    scope: Scope = Scope.LOCAL                # 局部/综合/Primitive
    scope_reason: str = ""                    # 范围判定理由
    
    # === 治理字段 ===
    authorization_level: str = "CLASSICAL_EXPLICIT"  # 授权等级
    verification_status: str = "UNVERIFIED"      # 核验状态
    unresolved_reasons: List[str] = field(default_factory=list)  # 未解决原因
    
    def to_dict(self) -> dict:
        return {
            "evidence_id": self.evidence_id,
            "classic": self.classic,
            "category": self.category,
            "original_key": self.original_key,
            "source_text": self.source_text,
            "subject": self.subject,
            "domain": self.domain,
            "primitive_name": self.primitive_name,
            "primitive_type": self.primitive_type.value,
            "conditions": self.conditions,
            "has_conditions": self.has_conditions,
            "scope": self.scope.value,
            "scope_reason": self.scope_reason,
            "authorization_level": self.authorization_level,
            "verification_status": self.verification_status,
            "unresolved_reasons": self.unresolved_reasons,
        }


# ============================================================
# 提取规则库
# ============================================================

# 条件关键词识别
CONDITION_PATTERNS = [
    (r"若.*?(?:则|就|便|当)", ConditionType.NECESSARY),
    (r"须.*?(?:得|有|见)", ConditionType.NECESSARY),
    (r"唯.*?(?:宜|可|当)", ConditionType.CONSTRAINING),
    (r"不宜.*?(?:见|逢|遇)", ConditionType.BLOCKING),
    (r"忌.*?(?:见|逢|遇)", ConditionType.BLOCKING),
    (r"喜.*?(?:见|逢|遇)", ConditionType.SUPPORTING),
    (r"得.*?(?:时|令|地|势)", ConditionType.SUFFICIENT),
    (r"无.*?(?:根|气|助)", ConditionType.BLOCKING),
]

# 判断对象识别
TARGET_PATTERNS = [
    (r"日主.{0,10}(?:旺|强|弱|衰|虚|实)", "日主旺衰"),
    (r"(?:日主|身){0,5}(?:旺|强|弱|衰)", "身之旺衰"),
    (r"(?:格局|格){0,5}(?:成|败|清|浊)", "格局成败"),
    (r"(?:用神|神){0,5}(?:得|失|清|浊)", "用神得失"),
    (r"(?:气势|气){0,5}(?:聚|散|纯|杂)", "气势聚散"),
]

# 领域识别
DOMAIN_KEYWORDS = {
    "wangshuai": ["旺", "强", "弱", "衰", "虚", "实", "气", "势"],
    "pattern": ["格", "局", "成", "败", "清", "浊"],
    "climate": ["寒", "暖", "燥", "湿", "调候"],
    "ten_god": ["官", "杀", "印", "比", "劫", "食", "伤", "财"],
}


def extract_conditions(text: str) -> tuple[List[Dict[str, Any]], bool]:
    """从原文提取条件"""
    conditions = []
    for pattern, ctype in CONDITION_PATTERNS:
        matches = re.findall(pattern, text)
        for match in matches:
            conditions.append({
                "text": match,
                "type": ctype.value,
                "source": text
            })
    return conditions, len(conditions) > 0


def extract_subject_and_domain(text: str) -> tuple[str, str]:
    """提取判断主体和领域"""
    subject = "日主"  # 默认
    domain = "wangshuai"  # 默认
    
    for pattern, target in TARGET_PATTERNS:
        if re.search(pattern, text):
            subject = target
            break
    
    for dom, keywords in DOMAIN_KEYWORDS.items():
        if any(k in text for k in keywords):
            domain = dom
            break
    
    return subject, domain


def extract_primitive_name(key: str, text: str) -> tuple[str, Scope]:
    """提取Primitive名称和类型"""
    key_lower = key.lower()
    
    # 判断是否为Primitive（不可再分的基本概念）
    primitives = ["得令", "得时", "得地", "得势", "有根", "通根", "有气", 
                  "气势", "党众", "成群", "从旺", "从弱", "身强", "身弱",
                  "调候", "用神", "格局", "成败", "救应"]
    
    for p in primitives:
        if p in key or p in text:
            # 判断是否为综合规则（含多个条件）
            condition_count = text.count("若") + text.count("须") + text.count("唯")
            if condition_count >= 2:
                return p, Scope.COMPOSITE
            elif "和" in text or "与" in text:
                return p, Scope.COMPOSITE
            else:
                return p, Scope.PRIMITIVE
    
    # 默认按key判断
    if "论" in key or "总" in key:
        return key, Scope.PRIMITIVE
    return key, Scope.LOCAL


def classify_scope(text: str, conditions: List[Dict]) -> tuple[Scope, str]:
    """判定规则范围"""
    # 检查是否包含多条件组合
    has_multiple_conditions = len(conditions) >= 2
    has_combination_words = any(w in text for w in ["和", "与", "且", "又", "兼"])
    has_composite_keywords = any(k in text for k in ["皆", "俱", "并", "总", "全"])
    
    if has_multiple_conditions and has_combination_words:
        return Scope.COMPOSITE, "多条件组合规则"
    elif has_composite_keywords:
        return Scope.COMPOSITE, "综合性描述"
    elif len(conditions) == 1:
        return Scope.LOCAL, "单条件局部规则"
    else:
        return Scope.PRIMITIVE, "基本Primitive定义"


def process_entry(entry: Dict, classic_name: str, entry_id: str) -> StructuredEvidence:
    """处理单个证据条目，提取结构化信息"""
    key = entry.get("key", "")
    original_text = entry.get("原文", "")
    category = entry.get("category", "")
    tags = entry.get("tags", [])
    
    # 生成证据ID
    evidence_id = f"{classic_name}_{entry_id}"
    
    # 提取条件
    conditions, has_conditions = extract_conditions(original_text)
    
    # 提取主体和领域
    subject, domain = extract_subject_and_domain(original_text)
    
    # 提取Primitive名称
    primitive_name, primitive_type = extract_primitive_name(key, original_text)
    
    # 判定范围
    scope, scope_reason = classify_scope(original_text, conditions)
    
    # 确定授权等级（EXACT_PRIMARY默认CLASSICAL_EXPLICIT）
    auth_level = "CLASSICAL_EXPLICIT"
    
    # 识别未解决原因
    unresolved = []
    if not conditions:
        unresolved.append("原文未明确标注条件")
    if scope == Scope.COMPOSITE and not conditions:
        unresolved.append("综合规则但条件不明确")
    
    return StructuredEvidence(
        evidence_id=evidence_id,
        classic=classic_name,
        category=category,
        original_key=key,
        source_text=original_text,
        subject=subject,
        domain=domain,
        primitive_name=primitive_name,
        primitive_type=primitive_type,
        conditions=conditions,
        has_conditions=has_conditions,
        scope=scope,
        scope_reason=scope_reason,
        authorization_level=auth_level,
        verification_status="UNVERIFIED",
        unresolved_reasons=unresolved,
    )


def main():
    """主处理流程"""
    base = r'D:\today\Canonical-Mining\FOR-DAZI'
    results = []
    
    classics = {
        'di_tian_sui.json': '滴天髓',
        'qiongtong_baojian.json': '穷通宝鉴',
        'sanming_tonghui.json': '三命通会',
        'yuanhai_ziping.json': '渊海子平',
        'ziping_zhenquan.json': '子平真诠',
    }
    
    for filename, classic_name in classics.items():
        filepath = os.path.join(base, filename)
        with open(filepath, encoding='utf-8') as fp:
            data = json.load(fp)
        
        for entry_id, entry in data['entries'].items():
            structured = process_entry(entry, classic_name, entry_id)
            results.append(structured)
    
    # 统计
    stats = {
        "total": len(results),
        "by_scope": {},
        "by_domain": {},
        "by_classic": {},
        "with_conditions": 0,
        "unresolved_count": 0,
    }
    
    for r in results:
        stats["by_scope"][r.scope.value] = stats["by_scope"].get(r.scope.value, 0) + 1
        stats["by_domain"][r.domain] = stats["by_domain"].get(r.domain, 0) + 1
        stats["by_classic"][r.classic] = stats["by_classic"].get(r.classic, 0) + 1
        if r.has_conditions:
            stats["with_conditions"] += 1
        if r.unresolved_reasons:
            stats["unresolved_count"] += 1
    
    # 输出
    output = {
        "generated": "2026-08-30",
        "method": "P0-3.3 结构化Evidence→Primitive/Condition提取",
        "stats": stats,
        "results": [r.to_dict() for r in results],
    }
    
    # 保存
    output_path = r'D:\shuntian\backend\data\p0_3_3_structured_evidence.json'
    with open(output_path, 'w', encoding='utf-8') as fp:
        json.dump(output, fp, ensure_ascii=False, indent=2)
    
    print(f"✅ 处理完成: {len(results)} 条证据已结构化")
    print(f"   按范围: {stats['by_scope']}")
    print(f"   按领域: {stats['by_domain']}")
    print(f"   含条件: {stats['with_conditions']}")
    print(f"   未解决: {stats['unresolved_count']}")
    print(f"   输出: {output_path}")


if __name__ == '__main__':
    main()
