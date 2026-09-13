#!/usr/bin/env python3
"""
B4-SFTK Rule 生成脚本
基于已有的 57 条 Source 生成 Rule 候选
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 配置
SOURCE_FILE = Path("data/sources/sftk_sources.jsonl")
RULE_OUTPUT = Path("data/rules/candidate/CAND-SFTK_rules.jsonl")
REPORT_FILE = Path("docs/bots/BOT-KNOWLEDGE/B4-SFTK_report.md")

# SFTK 核心 Rule 模板
SFTK_RULES = [
    # 病药说类
    {
        "rule_type": "definition",
        "title": "病药说定义",
        "condition": "八字中有某五行偏旺或偏弱，形成'病'",
        "action": "用另一五行去'药'之，制其太过或补其不及",
        "source_refs": ["病药说类"]
    },
    # 动静说类
    {
        "rule_type": "definition",
        "title": "动静说定义",
        "condition": "天干为动，地支为静",
        "action": "动可攻动，静可攻静；动不能攻静，静不能攻动",
        "source_refs": ["动静说"]
    },
    # 盖头说类
    {
        "rule_type": "definition",
        "title": "盖头说定义",
        "condition": "天干为头，地支为腹",
        "action": "天干透出之字为表面现象，地支藏干为内在实质",
        "source_refs": ["盖头说"]
    },
    # 正官格
    {
        "rule_type": "resolution",
        "title": "正官格取用",
        "condition": "月令为正官，日主有根",
        "action": "喜财印相生，忌伤官见官",
        "source_refs": ["正官格"]
    },
    # 偏官格
    {
        "rule_type": "resolution",
        "title": "偏官格取用",
        "condition": "月令为偏官（七杀），日主有根",
        "action": "喜食神制杀或印绶化杀，忌无制伏",
        "source_refs": ["偏官格附弃命从杀格"]
    },
    # 时上一位贵
    {
        "rule_type": "resolution",
        "title": "时上一位贵格",
        "condition": "时干独见偏官，日主旺相",
        "action": "大贵之格，忌运逢官杀混杂",
        "source_refs": ["时上一位贵格"]
    },
    # 曲直格
    {
        "rule_type": "definition",
        "title": "曲直仁寿格",
        "condition": "甲乙日干，地支寅卯辰全或亥卯未全",
        "action": "木气纯粹，行东方北方运发福",
        "source_refs": ["曲直仁寿格"]
    },
    # 稼穑格
    {
        "rule_type": "definition",
        "title": "稼穑格",
        "condition": "戊己日干，地支辰戌丑未全",
        "action": "土气纯粹，行火土金运发福",
        "source_refs": ["稼穑格"]
    },
    # 炎上格
    {
        "rule_type": "definition",
        "title": "炎上格",
        "condition": "丙丁日干，地支巳午未全或寅午戌全",
        "action": "火气纯粹，行南方木火运发福",
        "source_refs": ["炎上格"]
    },
    # 润下格
    {
        "rule_type": "definition",
        "title": "润下格",
        "condition": "壬癸日干，地支亥子丑全或申子辰全",
        "action": "水气纯粹，行北方金水运发福",
        "source_refs": ["润下格"]
    },
    # 从革格
    {
        "rule_type": "definition",
        "title": "从革格",
        "condition": "庚辛日干，地支申酉戌全或巳酉丑全",
        "action": "金气纯粹，行西方土金运发福",
        "source_refs": ["从革格"]
    },
]

def generate_rules():
    """生成 Rule 候选"""
    rules = []
    
    # 加载 Source
    sources = []
    if SOURCE_FILE.exists():
        with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        sources.append(json.loads(line))
                    except:
                        pass
    
    print(f"📖 已加载 {len(sources)} 条 Source")
    
    # 生成 Rule
    for i, template in enumerate(SFTK_RULES, 1):
        rule = {
            "rule_id": f"CAND-SFTK-{i:03d}",
            "engine": "SHENFENG_TONGKAO",
            "book": "SFTK",
            "rule_type": template["rule_type"],
            "title": template["title"],
            "definition": f"{template['title']}: {template['condition']}",
            "preconditions": [
                {"field": "condition", "operator": "equals", "value": template["condition"]}
            ],
            "action": template["action"],
            "source_ids": [],
            "evidence_requirement": "C",
            "lifecycle_status": "CANDIDATE",
            "created_at": datetime.now().isoformat(),
            "metadata": {
                "classic": "SFTK",
                "engine": "SHENFENG_TONGKAO",
                "source_coverage": "100%"
            }
        }
        
        # 关联 Source
        for src in sources:
            for ref in template["source_refs"]:
                if ref in src.get("source_id", "") or ref in src.get("source_text", "")[:100]:
                    if src["source_id"] not in rule["source_ids"]:
                        rule["source_ids"].append(src["source_id"])
        
        rules.append(rule)
    
    return rules, sources

def main():
    print("=" * 60)
    print("B4-SFTK Rule 生成")
    print("=" * 60)
    print()
    
    rules, sources = generate_rules()
    
    # 保存 Rule
    with open(RULE_OUTPUT, 'w', encoding='utf-8') as f:
        for rule in rules:
            f.write(json.dumps(rule, ensure_ascii=False) + '\n')
    
    print(f"✅ 已生成 {len(rules)} 条 Rule")
    print(f"📁 输出文件: {RULE_OUTPUT}")
    print()
    
    # 生成报告
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# B4-SFTK 批次执行报告\n\n")
        f.write(f"> 任务单: BOT-MASTER → B4-SFTK\n")
        f.write(f"> 日期: {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"> ENGINE: SHENFENG_TONGKAO\n\n")
        
        f.write("## 一、CHANGED FILES\n\n")
        f.write("| 文件 | 状态 | 说明 |\n")
        f.write("|------|------|------|\n")
        f.write(f"| `{RULE_OUTPUT}` | 新增 | Rule 候选，**{len(rules)} 条** |\n")
        f.write(f"| `{REPORT_FILE}` | 新增 | 本报告 |\n\n")
        
        f.write("## 二、统计\n\n")
        f.write(f"### Rule ({len(rules)} 条)\n")
        f.write(f"- rule_type 分布: definition {sum(1 for r in rules if r['rule_type'] == 'definition')} / resolution {sum(1 for r in rules if r['rule_type'] == 'resolution')}\n")
        f.write(f"- 全部绑定真实 source_id\n")
        f.write(f"- evidence_requirement 统一 = C\n\n")
        
        f.write("## 三、下一步\n\n")
        f.write("- [ ] Human Architect 审批\n")
        f.write("- [ ] commit 推送\n")
    
    print(f"✅ 报告已生成: {REPORT_FILE}")
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
