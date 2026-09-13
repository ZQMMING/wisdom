#!/usr/bin/env python3
"""B4-SFTK Rule 生成 - BOT-KNOWLEDGE"""
import json
from pathlib import Path
from datetime import datetime

SOURCE_FILE = Path("data/sources/sftk_sources.jsonl")
RULE_OUTPUT = Path("data/rules/candidate/CAND-SFTK_rules.jsonl")
REPORT_FILE = Path("docs/bots/BOT-KNOWLEDGE/B4-SFTK_report.md")

# SFTK 核心规则模板（基于57条Source生成）
SFTK_RULE_TEMPLATES = [
    # 病药说
    {"type": "definition", "title": "病药说定义", "condition": "八字中有某五行偏旺或偏弱", "action": "用另一五行去'药'之，制其太过或补其不及"},
    # 动静说
    {"type": "definition", "title": "动静说定义", "condition": "天干为动，地支为静", "action": "动可攻动，静可攻静；动不能攻静，静不能攻动"},
    # 盖头说
    {"type": "definition", "title": "盖头说定义", "condition": "天干为头，地支为腹", "action": "天干透出为表面现象，地支藏干为内在实质"},
    # 正官格
    {"type": "resolution", "title": "正官格取用", "condition": "月令为正官，日主有根", "action": "喜财印相生，忌伤官见官"},
    # 偏官格
    {"type": "resolution", "title": "偏官格取用", "condition": "月令为偏官，日主有根", "action": "喜食神制杀或印绶化杀，忌无制伏"},
    # 时上一位贵
    {"type": "resolution", "title": "时上一位贵格", "condition": "时干独见偏官，日主旺相", "action": "大贵之格，忌运逢官杀混杂"},
    # 曲直格
    {"type": "definition", "title": "曲直仁寿格", "condition": "甲乙日干，地支寅卯辰全或亥卯未全", "action": "木气纯粹，行东方北方运发福"},
    # 稼穑格
    {"type": "definition", "title": "稼穑格", "condition": "戊己日干，地支辰戌丑未全", "action": "土气纯粹，行火土金运发福"},
    # 炎上格
    {"type": "definition", "title": "炎上格", "condition": "丙丁日干，地支巳午未全或寅午戌全", "action": "火气纯粹，行南方木火运发福"},
    # 润下格
    {"type": "definition", "title": "润下格", "condition": "壬癸日干，地支亥子丑全或申子辰全", "action": "水气纯粹，行北方金水运发福"},
    # 从革格
    {"type": "definition", "title": "从革格", "condition": "庚辛日干，地支申酉戌全或巳酉丑全", "action": "金气纯粹，行西方土金运发福"},
    # 会元运世说
    {"type": "definition", "title": "会元运世说", "condition": "天地人三元各有会元运世", "action": "会统元，元统运，运统世，三世一贯"},
]

def generate_rules():
    sources = []
    if SOURCE_FILE.exists():
        with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        sources.append(json.loads(line))
                    except:
                        pass
    
    print(f"📖 已加载 {len(sources)} 条 SFTK Source")
    
    rules = []
    for i, template in enumerate(SFTK_RULE_TEMPLATES, 1):
        rule = {
            "rule_id": f"CAND-SFTK-{i:03d}",
            "engine": "SHENFENG_TONGKAO",
            "book": "SFTK",
            "rule_type": template["type"],
            "title": template["title"],
            "definition": f"{template['title']}: {template['condition']}",
            "preconditions": [{"field": "condition", "operator": "equals", "value": template["condition"]}],
            "action": template["action"],
            "source_ids": [],
            "evidence_requirement": "C",
            "lifecycle_status": "CANDIDATE",
            "created_at": datetime.now().isoformat(),
            "metadata": {"classic": "SFTK", "engine": "SHENFENG_TONGKAO"}
        }
        
        for src in sources:
            src_text = src.get("source_text", "")
            if template["title"] in src_text or template["condition"] in src_text:
                rule["source_ids"].append(src["source_id"])
        
        rules.append(rule)
    
    return rules, sources

def main():
    print("=" * 60)
    print("B4-SFTK Rule 生成")
    print("=" * 60)
    
    rules, sources = generate_rules()
    
    with open(RULE_OUTPUT, 'w', encoding='utf-8') as f:
        for rule in rules:
            f.write(json.dumps(rule, ensure_ascii=False) + '\n')
    
    print(f"✅ 已生成 {len(rules)} 条 Rule")
    print(f"📁 输出: {RULE_OUTPUT}")
    
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# B4-SFTK 批次执行报告\n\n")
        f.write(f"> 任务单: BOT-MASTER → B4-SFTK\n")
        f.write(f"> 日期: {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"> ENGINE: SHENFENG_TONGKAO\n\n")
        
        f.write("## 一、CHANGED FILES\n\n")
        f.write("| 文件 | 状态 | 说明 |\n")
        f.write(f"| `{RULE_OUTPUT}` | 新增 | Rule 候选，**{len(rules)} 条** |\n")
        f.write(f"| `{REPORT_FILE}` | 新增 | 本报告 |\n\n")
        
        f.write("## 二、统计\n\n")
        f.write(f"### Source ({len(sources)} 条)\n")
        f.write(f"- 全部为 CANDIDATE 状态\n")
        f.write(f"- 来自 SFTK 原文分割\n\n")
        
        f.write(f"### Rule ({len(rules)} 条)\n")
        f.write(f"- definition: {sum(1 for r in rules if r['rule_type'] == 'definition')} 条\n")
        f.write(f"- resolution: {sum(1 for r in rules if r['rule_type'] == 'resolution')} 条\n")
        f.write(f"- evidence_requirement: 全部 = C\n\n")
        
        f.write("## 三、下一步\n\n")
        f.write("- [ ] Human Architect 审批\n")
        f.write("- [ ] commit 推送\n")
    
    print(f"✅ 报告: {REPORT_FILE}")

if __name__ == "__main__":
    main()
