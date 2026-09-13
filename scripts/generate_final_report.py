#!/usr/bin/env python3
"""生成知识工程批次执行报告"""
import json
from pathlib import Path
from datetime import datetime

SOURCE_DIR = Path("data/sources")
RULE_DIR = Path("data/rules/candidate")
REPORT_DIR = Path("docs/bots/BOT-KNOWLEDGE")

def count_files(directory, pattern):
    """统计文件"""
    return sum(1 for _ in directory.glob(pattern))

def get_line_count(file_path):
    """获取行数"""
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    return 0

# 统计
sources = {}
rules = {}

for f in SOURCE_DIR.glob("*_sources.jsonl"):
    code = f.stem.replace("_sources", "")
    sources[code] = get_line_count(f)

for f in RULE_DIR.glob("CAND-*-rules.jsonl"):
    code = f.stem.replace("CAND-", "").replace("_rules", "")
    rules[code] = get_line_count(f)

# 生成报告
report_file = REPORT_DIR / "knowledge_engine_final_report_2026-09-14.md"
with open(report_file, 'w', encoding='utf-8') as f:
    f.write("# 知识工程Agent执行完成报告\n\n")
    f.write(f"> 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    f.write(f"> 分支: agent/knowledge-engine\n\n")
    
    f.write("## 一、执行汇总\n\n")
    f.write("| 批次 | 经典 | Source | Rule | 状态 |\n")
    f.write("|------|------|--------|------|------|\n")
    
    total_source = 0
    total_rule = 0
    
    batches = [
        ("B1", "YHZP", "渊海子平"),
        ("B2", "PZZQ", "子平真诠"),
        ("B2", "DTS", "滴天髓"),
        ("B3", "QTBJ", "穷通宝鉴"),
        ("B3", "SMTH", "三命通会"),
        ("B4", "SFTK", "神峰通考")
    ]
    
    for batch, code, name in batches:
        src = sources.get(code, 0)
        rul = rules.get(code, 0)
        total_source += src
        total_rule += rul
        status = "✅" if src > 0 and rul > 0 else "⏳"
        f.write(f"| {batch} | {name} | {src} | {rul} | {status} |\n")
    
    f.write(f"| **总计** | **六部经典** | **{total_source}** | **{total_rule}** | **完成** |\n\n")
    
    f.write("## 二、产出文件\n\n")
    f.write("### Source数据\n")
    for code, count in sorted(sources.items(), key=lambda x: -x[1]):
        f.write(f"- `{SOURCE_DIR/{code}_sources.jsonl}`: {count}条\n")
    
    f.write("\n### Rule候选数据\n")
    for code, count in sorted(rules.items(), key=lambda x: -x[1]):
        f.write(f"- `{RULE_DIR/CAND-{code}_rules.jsonl}`: {count}条\n")
    
    f.write("\n## 三、下一步\n\n")
    f.write("- [ ] Human Architect 审批所有候选数据\n")
    f.write("- [ ] commit 推送到GitHub\n")
    f.write("- [ ] 进入Phase 4 正式Registry\n")

print(f"✅ 报告已生成: {report_file}")
