"""P0-2.3 Rule Authorization Audit - 批量提取所有 Rule 的关键信息"""
import json
import os
from pathlib import Path
from collections import defaultdict

RULES_DIR = Path(r"D:\shuntian\backend\data\rules")

# Rule ID 前缀到体系的映射
PREFIX_TO_SYSTEM = {
    "ZPZ": "子平真诠",
    "DTS": "滴天髓",
    "HL": "河洛",
    "HLT": "河洛",
    "ZW": "紫微",
    "MK": "盲派",
    "SMTH": "三命通会",
    "YHZP": "渊海子平",
    "DTS": "滴天髓",
    "GW": "鬼谷子",
    "HH": "河图",
    "LM": "洛书",
    "SX": "神煞",
    "TF": "桃花",
    "WLT": "文昌",
    "TH": "桃花",
    "SUY": "岁运",
    "MAR": "婚姻",
    "CRR": "财运",
    "EDU": "学业",
    "QTB": "其他",
}

def extract_rule_info(rule_file):
    """提取单条 Rule 的关键信息"""
    with open(rule_file, 'r', encoding='utf-8') as f:
        rule = json.load(f)
    
    rule_id = rule.get("rule_id", "UNKNOWN")
    title = rule.get("title", "")
    rule_type = rule.get("rule_type", "")
    status = rule.get("status", "unknown")
    version = rule.get("version", "")
    applies_to_layers = rule.get("applies_to_layers", [])
    produces_signal_type = rule.get("produces_signal_type", "")
    
    # Source 信息
    source = rule.get("source", {})
    source_work = source.get("work", "")
    source_chapter = source.get("chapter", "")
    source_location = source.get("location", "")
    book_id = rule.get("book_id", "")
    
    # 推断体系
    prefix = rule_id.split("-")[0] if "-" in rule_id else rule_id
    source_system = PREFIX_TO_SYSTEM.get(prefix, f"未知({prefix})")
    
    # Conditions 信息
    conditions = rule.get("conditions", {})
    all_conditions = conditions.get("all", [])
    any_conditions = conditions.get("any", [])
    
    all_condition_fields = []
    has_threshold = False
    threshold_details = []
    
    for cond in all_conditions + any_conditions:
        field = cond.get("field", "")
        op = cond.get("op", "")
        value = cond.get("value", "")
        all_condition_fields.append(f"{field} {op} {value}")
        
        if op in ("gte", "lte", "gt", "lt"):
            has_threshold = True
            threshold_details.append(f"{field} {op} {value}")
    
    # Conclusion 信息
    conclusion = rule.get("conclusion", {})
    rationale_classical = conclusion.get("rationale_classical", "")
    produces_semantic_atoms = conclusion.get("produces_semantic_atoms", [])
    
    # Evidence 信息
    evidence_refs = rule.get("evidence_refs", [])
    spec_decisions_ref = rule.get("spec_decisions_ref", [])
    
    # 授权状态初步判断
    authorization_status = "UNAUTHORIZED"
    if source_work and source_work not in ("工程种子", "demo baseline", ""):
        if status == "active":
            authorization_status = "PROVISIONAL"  # 有来源但未验证原典
        elif status == "draft":
            authorization_status = "DRAFT"
    else:
        authorization_status = "ENGINEERING_SEED"  # 工程种子规则
    
    return {
        "rule_id": rule_id,
        "title": title,
        "rule_type": rule_type,
        "source_system": source_system,
        "source_work": source_work,
        "source_chapter": source_chapter,
        "source_location": source_location,
        "book_id": book_id,
        "status": status,
        "version": version,
        "applies_to_layers": applies_to_layers,
        "produces_signal_type": produces_signal_type,
        "condition_count": len(all_conditions) + len(any_conditions),
        "condition_fields": all_condition_fields,
        "has_threshold": has_threshold,
        "threshold_details": threshold_details,
        "rationale_classical": rationale_classical,
        "produces_semantic_atoms": produces_semantic_atoms,
        "evidence_refs": evidence_refs,
        "spec_decisions_ref": spec_decisions_ref,
        "authorization_status": authorization_status,
    }

def main():
    rule_files = sorted(RULES_DIR.glob("*.json"))
    print(f"找到 {len(rule_files)} 条 Rule 文件")
    
    all_rules = []
    for rule_file in rule_files:
        try:
            rule_info = extract_rule_info(rule_file)
            all_rules.append(rule_info)
        except Exception as e:
            print(f"错误: {rule_file.name}: {e}")
    
    # 统计信息
    by_system = defaultdict(int)
    by_status = defaultdict(int)
    by_authorization = defaultdict(int)
    threshold_rules = []
    engineering_seed_rules = []
    draft_rules = []
    
    for rule in all_rules:
        by_system[rule["source_system"]] += 1
        by_status[rule["status"]] += 1
        by_authorization[rule["authorization_status"]] += 1
        
        if rule["has_threshold"]:
            threshold_rules.append(rule)
        if rule["authorization_status"] == "ENGINEERING_SEED":
            engineering_seed_rules.append(rule)
        if rule["status"] == "draft":
            draft_rules.append(rule)
    
    print("\n=== 按体系统计 ===")
    for system, count in sorted(by_system.items(), key=lambda x: -x[1]):
        print(f"  {system}: {count}")
    
    print("\n=== 按状态统计 ===")
    for status, count in sorted(by_status.items(), key=lambda x: -x[1]):
        print(f"  {status}: {count}")
    
    print("\n=== 按授权状态统计 ===")
    for auth, count in sorted(by_authorization.items(), key=lambda x: -x[1]):
        print(f"  {auth}: {count}")
    
    print(f"\n=== 包含阈值的 Rule: {len(threshold_rules)} 条 ===")
    for rule in threshold_rules[:20]:
        print(f"  {rule['rule_id']}: {rule['threshold_details']}")
    
    print(f"\n=== 工程种子 Rule: {len(engineering_seed_rules)} 条 ===")
    for rule in engineering_seed_rules[:10]:
        print(f"  {rule['rule_id']}: {rule['title']}")
    
    print(f"\n=== Draft Rule: {len(draft_rules)} 条 ===")
    for rule in draft_rules[:10]:
        print(f"  {rule['rule_id']}: {rule['title']}")
    
    # 保存完整结果
    output = {
        "total_rules": len(all_rules),
        "by_system": dict(by_system),
        "by_status": dict(by_status),
        "by_authorization": dict(by_authorization),
        "threshold_rules_count": len(threshold_rules),
        "engineering_seed_rules_count": len(engineering_seed_rules),
        "draft_rules_count": len(draft_rules),
        "all_rules": all_rules,
    }
    
    output_file = Path(r"D:\shuntian\backend\docs\P0_2_3_rule_audit_raw.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n完整结果已保存到: {output_file}")

if __name__ == "__main__":
    main()
