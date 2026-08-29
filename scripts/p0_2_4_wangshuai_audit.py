"""P0-2.4 身强身弱/旺衰辨识模型深度解剖 - 批量提取相关 Rule 关键信息"""
import json
from pathlib import Path

RULES_DIR = Path(r"D:\shuntian\backend\data\rules")

# 与身强身弱/旺衰相关的 Rule 文件
WANGSHUAI_RULES = [
    "DTS-101.json", "DTS-102.json", "DTS-103.json", "DTS-104.json",
    "DTS-105.json", "DTS-106.json", "DTS-107.json",
    "MK-101.json", "MK-102.json", "MK-103.json", "MK-104.json", "MK-105.json",
    "SMTH-101.json", "SMTH-102.json",
    "HH-101.json", "HLT-106.json", "HLT-305.json",
    "MAR-105.json", "WLT-103.json",
]

def extract_wangshuai_info(rule_file):
    """提取单条旺衰 Rule 的关键信息"""
    with open(rule_file, 'r', encoding='utf-8') as f:
        rule = json.load(f)
    
    rule_id = rule.get("rule_id", "UNKNOWN")
    title = rule.get("title", "")
    rule_type = rule.get("rule_type", "")
    status = rule.get("status", "unknown")
    
    # Source 信息
    source = rule.get("source", {})
    source_work = source.get("work", "")
    source_chapter = source.get("chapter", "")
    source_location = source.get("location", "")
    
    # Conditions 信息
    conditions = rule.get("conditions", {})
    all_conditions = conditions.get("all", [])
    
    condition_details = []
    for cond in all_conditions:
        field = cond.get("field", "")
        op = cond.get("op", "")
        value = cond.get("value", "")
        condition_details.append(f"{field} {op} {value}")
    
    # Conclusion 信息
    conclusion = rule.get("conclusion", {})
    rationale = conclusion.get("rationale_classical", "")
    produces_signal_type = rule.get("produces_signal_type", "")
    produces_semantic_atoms = conclusion.get("produces_semantic_atoms", [])
    
    # 判断是否是"单一证据 → 直接结论"
    is_single_evidence = len(all_conditions) == 1
    
    # 判断是否直接宣布身强/身弱
    is_direct_wangshuai = False
    wangshuai_keywords = ["身强", "身弱", "得令而旺", "失令而弱", "旺", "弱"]
    for kw in wangshuai_keywords:
        if kw in title or kw in rationale:
            is_direct_wangshuai = True
            break
    
    # 证据类型判断
    evidence_types = []
    for cond in all_conditions:
        field = cond.get("field", "")
        if "month_hidden_main_ten_god" in field:
            evidence_types.append("得令")
        elif "day_branch" in field or "root" in field:
            evidence_types.append("得地")
        elif "transparent" in field or "shi" in field:
            evidence_types.append("得势")
        elif "clash" in field or "harm" in field:
            evidence_types.append("受制")
        else:
            evidence_types.append(f"其他({field})")
    
    return {
        "rule_id": rule_id,
        "title": title,
        "rule_type": rule_type,
        "status": status,
        "source_work": source_work,
        "source_chapter": source_chapter,
        "source_location": source_location,
        "condition_count": len(all_conditions),
        "condition_details": condition_details,
        "evidence_types": evidence_types,
        "is_single_evidence": is_single_evidence,
        "is_direct_wangshuai": is_direct_wangshuai,
        "produces_signal_type": produces_signal_type,
        "produces_semantic_atoms": produces_semantic_atoms,
        "rationale": rationale,
    }

def main():
    all_rules = []
    for rule_name in WANGSHUAI_RULES:
        rule_file = RULES_DIR / rule_name
        if rule_file.exists():
            try:
                rule_info = extract_wangshuai_info(rule_file)
                all_rules.append(rule_info)
            except Exception as e:
                print(f"错误: {rule_name}: {e}")
        else:
            print(f"文件不存在: {rule_name}")
    
    print(f"找到 {len(all_rules)} 条旺衰相关 Rule\n")
    
    # 统计
    single_evidence_count = sum(1 for r in all_rules if r["is_single_evidence"])
    direct_wangshuai_count = sum(1 for r in all_rules if r["is_direct_wangshuai"])
    draft_count = sum(1 for r in all_rules if r["status"] == "draft")
    active_count = sum(1 for r in all_rules if r["status"] == "active")
    
    print(f"=== 统计 ===")
    print(f"  总 Rule 数: {len(all_rules)}")
    print(f"  单一证据 Rule: {single_evidence_count}")
    print(f"  直接宣布身强/身弱: {direct_wangshuai_count}")
    print(f"  Draft 状态: {draft_count}")
    print(f"  Active 状态: {active_count}")
    
    print(f"\n=== 逐条分析 ===")
    for rule in all_rules:
        print(f"\n{rule['rule_id']}: {rule['title']}")
        print(f"  状态: {rule['status']}")
        print(f"  来源: {rule['source_work']} / {rule['source_chapter']}")
        print(f"  条件数: {rule['condition_count']}")
        print(f"  证据类型: {rule['evidence_types']}")
        print(f"  单一证据: {rule['is_single_evidence']}")
        print(f"  直接宣布旺衰: {rule['is_direct_wangshuai']}")
        print(f"  条件: {rule['condition_details']}")
        print(f"  输出: {rule['produces_signal_type']}")
    
    # 保存完整结果
    output = {
        "total_rules": len(all_rules),
        "single_evidence_count": single_evidence_count,
        "direct_wangshuai_count": direct_wangshuai_count,
        "draft_count": draft_count,
        "active_count": active_count,
        "all_rules": all_rules,
    }
    
    output_file = Path(r"D:\shuntian\backend\docs\P0_2_4_wangshuai_audit_raw.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n完整结果已保存到: {output_file}")

if __name__ == "__main__":
    main()
