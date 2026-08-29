"""P0-2.6 RULE LAYER MAPPING AUDIT - 将136条Rule映射到Fact/Relation/Evidence/Judgment四层"""
import json
from pathlib import Path
from collections import defaultdict

RULES_DIR = Path(r"D:\shuntian\backend\data\rules")

# 层级分类规则
LAYER_RULES = {
    "FACT": {
        "description": "纯事实计算规则 - 直接描述Calculation Fact，不涉及推理",
        "keywords": ["计算", "生成", "属性", "定义", "是什么", "等于", "属于"],
        "condition_patterns": ["eq", "in", "contains"],
        "examples": ["日主=甲", "月令=寅", "日支=子"]
    },
    "RELATION": {
        "description": "关系计算规则 - 描述两个或多个Fact之间的关系（生克、合冲刑害、十神等）",
        "keywords": ["生", "克", "合", "冲", "刑", "害", "破", "会", "十神", "关系", "作用"],
        "condition_patterns": ["eq", "in", "contains"],
        "examples": ["甲生丙", "庚克甲", "甲己合", "子午冲"]
    },
    "EVIDENCE": {
        "description": "证据生成规则 - 从Fact和Relation中提取证据（得令、得地、得势、受制等）",
        "keywords": ["得令", "得地", "得势", "受制", "有根", "无根", "透干", "通根", "证据", "支持", "制约"],
        "condition_patterns": ["eq", "in", "contains", "gte", "lte"],
        "examples": ["月令主气为印比劫→得令证据", "日支主气为比劫→得地证据"]
    },
    "JUDGMENT": {
        "description": "辨证判断规则 - 基于Evidence进行综合判断（旺衰、格局、调候、用神等）",
        "keywords": ["旺", "衰", "强", "弱", "格局", "调候", "用神", "喜神", "忌神", "体用", "清浊", "顺逆", "气势", "判断", "主", "断", "为", "则", "故"],
        "condition_patterns": ["eq", "in", "contains", "gte", "lte", "gt", "lt"],
        "examples": ["得令+得地+得势→身强", "月令为官+财生官→官格成立"]
    }
}

def classify_layer(rule):
    """分类 Rule 所属层级"""
    title = rule.get("title", "")
    rule_type = rule.get("rule_type", "")
    produces_signal_type = rule.get("produces_signal_type", "")
    rationale = rule.get("conclusion", {}).get("rationale_classical", "")
    
    combined_text = f"{title} {rule_type} {produces_signal_type} {rationale}"
    
    # 计算各层级的匹配分数
    scores = {}
    for layer, config in LAYER_RULES.items():
        score = 0
        for kw in config["keywords"]:
            if kw.lower() in combined_text.lower():
                score += 1
        scores[layer] = score
    
    # 找到最高分的层级
    max_score = max(scores.values())
    if max_score == 0:
        return "UNCERTAIN", scores
    
    # 如果有多个层级分数相同，需要进一步判断
    top_layers = [layer for layer, score in scores.items() if score == max_score]
    
    if len(top_layers) == 1:
        return top_layers[0], scores
    
    # 多层级匹配时，根据条件复杂度和输出类型进一步判断
    conditions = rule.get("conditions", {})
    all_conditions = conditions.get("all", [])
    condition_count = len(all_conditions)
    
    # 如果条件数 <= 1 且输出是简单状态，更可能是 EVIDENCE 或 RELATION
    if condition_count <= 1:
        if "得令" in combined_text or "得地" in combined_text or "得势" in combined_text or "受制" in combined_text:
            return "EVIDENCE", scores
        if "生" in combined_text or "克" in combined_text or "合" in combined_text or "冲" in combined_text:
            return "RELATION", scores
    
    # 如果条件数 >= 2 且输出是综合判断，更可能是 JUDGMENT
    if condition_count >= 2:
        if "旺" in combined_text or "衰" in combined_text or "强" in combined_text or "弱" in combined_text or "格局" in combined_text:
            return "JUDGMENT", scores
    
    return top_layers[0], scores

def extract_mapping_info(rule_file):
    """提取单条 Rule 的层级映射信息"""
    with open(rule_file, 'r', encoding='utf-8') as f:
        rule = json.load(f)
    
    rule_id = rule.get("rule_id", "UNKNOWN")
    title = rule.get("title", "")
    rule_type = rule.get("rule_type", "")
    status = rule.get("status", "unknown")
    
    # Source 信息
    source = rule.get("source", {})
    source_work = source.get("work", "")
    
    # Conditions 信息
    conditions = rule.get("conditions", {})
    all_conditions = conditions.get("all", [])
    condition_count = len(all_conditions)
    
    condition_fields = []
    for cond in all_conditions:
        field = cond.get("field", "")
        if field:
            condition_fields.append(field)
    
    # Conclusion 信息
    conclusion = rule.get("conclusion", {})
    rationale = conclusion.get("rationale_classical", "")
    produces_signal_type = rule.get("produces_signal_type", "")
    
    # 层级分类
    layer, scores = classify_layer(rule)
    
    # 判断是否应该迁移
    should_migrate = False
    migration_target = ""
    migration_reason = ""
    
    if layer == "FACT":
        should_migrate = True
        migration_target = "calculation/ 或 ontology/"
        migration_reason = "纯事实计算规则，不应该在Rule层"
    elif layer == "RELATION":
        should_migrate = True
        migration_target = "relations/"
        migration_reason = "关系计算规则，应该在Relation Engine层"
    elif layer == "EVIDENCE":
        should_migrate = True
        migration_target = "evidence/"
        migration_reason = "证据生成规则，应该在Evidence Derivation层"
    elif layer == "JUDGMENT":
        should_migrate = False
        migration_target = "judgment/ 或 classics/"
        migration_reason = "辨证判断规则，属于Judgment层，但需要按体系分类"
    
    return {
        "rule_id": rule_id,
        "title": title,
        "rule_type": rule_type,
        "status": status,
        "source_work": source_work,
        "condition_count": condition_count,
        "condition_fields": condition_fields,
        "produces_signal_type": produces_signal_type,
        "rationale": rationale,
        "layer": layer,
        "layer_scores": scores,
        "should_migrate": should_migrate,
        "migration_target": migration_target,
        "migration_reason": migration_reason,
    }

def main():
    rule_files = sorted(RULES_DIR.glob("*.json"))
    print(f"找到 {len(rule_files)} 条 Rule 文件\n")
    
    all_rules = []
    for rule_file in rule_files:
        try:
            rule_info = extract_mapping_info(rule_file)
            all_rules.append(rule_info)
        except Exception as e:
            print(f"错误: {rule_file.name}: {e}")
    
    # 按层级统计
    by_layer = defaultdict(int)
    for rule in all_rules:
        by_layer[rule["layer"]] += 1
    
    # 按状态统计
    by_status = defaultdict(int)
    for rule in all_rules:
        by_status[rule["status"]] += 1
    
    # 按层级+状态交叉统计
    by_layer_status = defaultdict(lambda: defaultdict(int))
    for rule in all_rules:
        by_layer_status[rule["layer"]][rule["status"]] += 1
    
    print(f"=== 按层级统计 ===")
    for layer, count in sorted(by_layer.items(), key=lambda x: -x[1]):
        print(f"  {layer}: {count} ({count/len(all_rules)*100:.1f}%)")
    
    print(f"\n=== 按状态统计 ===")
    for status, count in sorted(by_status.items(), key=lambda x: -x[1]):
        print(f"  {status}: {count}")
    
    print(f"\n=== 按层级+状态交叉统计 ===")
    for layer in ["FACT", "RELATION", "EVIDENCE", "JUDGMENT", "UNCERTAIN"]:
        if layer in by_layer_status:
            status_str = ", ".join([f"{s}: {c}" for s, c in by_layer_status[layer].items()])
            print(f"  {layer}: {status_str}")
    
    # 需要迁移的 Rule
    migrate_count = sum(1 for r in all_rules if r["should_migrate"])
    print(f"\n=== 需要迁移的 Rule: {migrate_count} 条 ({migrate_count/len(all_rules)*100:.1f}%) ===")
    
    # 各层级的代表性 Rule
    print(f"\n=== 各层级代表性 Rule ===")
    for layer in ["FACT", "RELATION", "EVIDENCE", "JUDGMENT", "UNCERTAIN"]:
        layer_rules = [r for r in all_rules if r["layer"] == layer]
        if layer_rules:
            print(f"\n  {layer} ({len(layer_rules)} 条):")
            for r in layer_rules[:5]:
                print(f"    - {r['rule_id']}: {r['title']}")
            if len(layer_rules) > 5:
                print(f"    ... 还有 {len(layer_rules)-5} 条")
    
    # 保存完整结果
    output = {
        "total_rules": len(all_rules),
        "by_layer": dict(by_layer),
        "by_status": dict(by_status),
        "by_layer_status": {k: dict(v) for k, v in by_layer_status.items()},
        "migrate_count": migrate_count,
        "all_rules": all_rules,
    }
    
    output_file = Path(r"D:\shuntian\backend\docs\P0_2_6_rule_layer_mapping_raw.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n完整结果已保存到: {output_file}")

if __name__ == "__main__":
    main()
