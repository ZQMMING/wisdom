#!/usr/bin/env python3
"""检查 BOT-KNOWLEDGE 任务进展"""

from pathlib import Path
from datetime import datetime

log_file = Path("logs/cron_check.log")
log_file.parent.mkdir(parents=True, exist_ok=True)

def check():
    print(f"=== 检查进度 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===", flush=True)
    
    # YHZP
    yhzp_src = Path("data/sources/yhzp_sources.jsonl")
    yhzp_rule = Path("data/rules/candidate/CAND-YHZP_rules.jsonl")
    if yhzp_src.exists():
        count = sum(1 for _ in open(yhzp_src, encoding='utf-8'))
        print(f"✅ YHZP Source: {count} 条", flush=True)
    if yhzp_rule.exists():
        count = sum(1 for _ in open(yhzp_rule, encoding='utf-8'))
        print(f"✅ YHZP Rule: {count} 条", flush=True)
    
    # SFTK
    sftk_src = Path("data/sources/sftk_sources.jsonl")
    sftk_rule = Path("data/rules/candidate/CAND-SFTK_rules.jsonl")
    if sftk_src.exists():
        count = sum(1 for _ in open(sftk_src, encoding='utf-8'))
        print(f"✅ SFTK Source: {count} 条", flush=True)
    if sftk_rule.exists():
        count = sum(1 for _ in open(sftk_rule, encoding='utf-8'))
        print(f"✅ SFTK Rule: {count} 条", flush=True)
    else:
        print("⏳ SFTK Rule: 等待生成", flush=True)
    
    # 报告
    report = Path("docs/bots/BOT-KNOWLEDGE/B4-SFTK_report.md")
    if report.exists():
        print("✅ B4-SFTK 报告已生成", flush=True)
    else:
        print("⏳ B4-SFTK 报告: 等待生成", flush=True)
    
    print("", flush=True)

if __name__ == "__main__":
    check()
