"""P0-2.5 JUDGMENT MODEL AUDIT - 批量提取所有 Rule 的辨识模型信息"""
import json
from pathlib import Path
from collections import defaultdict

RULES_DIR = Path(r"D:\shuntian\backend\data\rules")

# 辨识类型分类
JUDGMENT_TYPES = {
    "旺衰": ["旺衰", "身强", "身弱", "得令", "得地", "得势", "strength", "wang", "shuai", "qiang", "ruo", "SUPPORT", "CONSTRAINT"],
    "格局": ["格局", "格", "成格", "破格", "pattern", "GE"],
    "调候": ["调候", "寒暖", "燥湿", "候", "tiao hou", "climate"],
    "用神": ["用神", "喜神", "忌神", "yong shen", "xi shen", "ji shen"],
    "制化": ["制化", "制", "化", "zhi hua", "control", "transform"],
    "合化": ["合化", "合", "化气", "he hua", "combination", "transform"],
    "刑冲合害": ["刑", "冲", "合", "害", "破", "clash", "harm", "combination", "punish", "break"],
    "清浊": ["清浊", "清", "浊", "qing zhuo", "pure", "turbid"],
    "体用": ["体用", "体", "用", "ti yong", "body", "function"],
    "顺逆": ["顺逆", "顺", "逆", "shun ni", "direct", "reverse"],
    "气势": ["气势", "气", "势", "qi shi", "momentum"],
    "盲派结构": ["盲派", "结构", "象", "blind", "structure", "image"],
    "紫微宫星关系": ["紫微", "宫", "星", "ziwei", "palace", "star"],
    "紫微四化": ["四化", "化禄", "化权", "化科", "化忌", "sihua", "four transformations"],
    "河洛卦象": ["河洛", "河图", "洛书", "卦", "heluo", "hetu", "luoshu", "hexagram"],
    "易经卦爻": ["易经", "周易", "爻", "yi jing", "zhou yi", "yao", "line"],
    "健康": ["健康", "病", "医", "health", "disease", "medical", "HLT"],
    "婚姻": ["婚姻", "妻", "夫", "marriage", "spouse", "MAR"],
    "财运": ["财", "富", "wealth", "money", "CRR"],
    "学业": ["学业", "文", "文昌", "education", "study", "EDU", "WLT"],
    "官运": ["官", "贵", "career", "official", "GW"],
    "岁运": ["岁运", "大运", "流年", "流月", "流日", "dayun", "liunian", "SUY"],
    "神煞": ["神煞", "贵人", "桃花", "shen sha", "noble", "peach blossom", "SX", "TF", "TH"],
}

def classify_judgment_type(rule):
    """分类 Rule 的辨识类型"""
    title = rule.get("title", "")
    rule_type = rule.get("rule_type", "")
    produces_signal_type = rule.get("produces_signal_type", "")
    rationale = rule.get("conclusion", {}).get("rationale_classical", "")
    
    combined_text = f"{title} {rule_type} {produces_signal_type} {rationale}"
    
    matched_types = []
    for jtype, keywords in JUDGMENT_TYPES.items():
        for kw in keywords:
            if kw.lower() in combined_text.lower():
                matched_types.append(jtype)
                break
    
    if not matched_types:
        matched_types = ["其他/未分类"]
    
    return matched_types

def extract_judgment_info(rule_file):
    """提取单条 Rule 的辨识模型信息"""
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
    any_conditions = conditions.get("any", [])
    
    condition_fields = []
    for cond in all_conditions + any_conditions:
        field = cond.get("field", "")
        op = cond.get("op", "")
        value = cond.get("value", "")
        if field:
            condition_fields.append(field)
    
    # Conclusion 信息
    conclusion = rule.get("conclusion", {})
    rationale = conclusion.get("rationale_classical", "")
    produces_signal_type = rule.get("produces_signal_type", "")
    produces_semantic_atoms = conclusion.get("produces_semantic_atoms", [])
    
    # 辨识类型
    judgment_types = classify_judgment_type(rule)
    
    # 判断推理类型
    condition_count = len(all_conditions) + len(any_conditions)
    if condition_count == 0:
        inference_type = "无条件/永远匹配"
    elif condition_count == 1:
        inference_type = "单一条件型"
    elif any_conditions:
        inference_type = "多条件择一型(OR)"
    else:
        inference_type = "多条件组合型(AND)"
    
    # 是否直接宣布结论
    is_direct_judgment = False
    direct_keywords = ["→", "主", "断", "判", "为", "则", "故", "因此", "所以"]
    for kw in direct_keywords:
        if kw in title or kw in rationale:
            is_direct_judgment = True
            break
    
    return {
        "rule_id": rule_id,
        "title": title,
        "rule_type": rule_type,
        "status": status,
        "source_work": source_work,
        "source_chapter": source_chapter,
        "source_location": source_location,
        "judgment_types": judgment_types,
        "inference_type": inference_type,
        "condition_count": condition_count,
        "condition_fields": condition_fields,
        "is_direct_judgment": is_direct_judgment,
        "produces_signal_type": produces_signal_type,
        "produces_semantic_atoms": produces_semantic_atoms,
        "rationale": rationale,
    }

def main():
    rule_files = sorted(RULES_DIR.glob("*.json"))
    print(f"找到 {len(rule_files)} 条 Rule 文件\n")
    
    all_rules = []
    for rule_file in rule_files:
        try:
            rule_info = extract_judgment_info(rule_file)
            all_rules.append(rule_info)
        except Exception as e:
            print(f"错误: {rule_file.name}: {e}")
    
    # 按辨识类型统计
    by_judgment_type = defaultdict(int)
    for rule in all_rules:
        for jtype in rule["judgment_types"]:
            by_judgment_type[jtype] += 1
    
    # 按推理类型统计
    by_inference_type = defaultdict(int)
    for rule in all_rules:
        by_inference_type[rule["inference_type"]] += 1
    
    # 按状态统计
    by_status = defaultdict(int)
    for rule in all_rules:
        by_status[rule["status"]] += 1
    
    print(f"=== 按辨识类型统计 ===")
    for jtype, count in sorted(by_judgment_type.items(), key=lambda x: -x[1]):
        print(f"  {jtype}: {count}")
    
    print(f"\n=== 按推理类型统计 ===")
    for itype, count in sorted(by_inference_type.items(), key=lambda x: -x[1]):
        print(f"  {itype}: {count}")
    
    print(f"\n=== 按状态统计 ===")
    for status, count in sorted(by_status.items(), key=lambda x: -x[1]):
        print(f"  {status}: {count}")
    
    # 直接宣布结论的 Rule
    direct_judgment_count = sum(1 for r in all_rules if r["is_direct_judgment"])
    print(f"\n=== 直接宣布结论的 Rule: {direct_judgment_count} 条 ===")
    
    # 保存完整结果
    output = {
        "total_rules": len(all_rules),
        "by_judgment_type": dict(by_judgment_type),
        "by_inference_type": dict(by_inference_type),
        "by_status": dict(by_status),
        "direct_judgment_count": direct_judgment_count,
        "all_rules": all_rules,
    }
    
    output_file = Path(r"D:\shuntian\backend\docs\P0_2_5_judgment_model_audit_raw.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n完整结果已保存到: {output_file}")

if __name__ == "__main__":
    main()
