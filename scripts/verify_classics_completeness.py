#!/usr/bin/env python3
"""验证六部经典的完整性并生成报告"""

import json
from pathlib import Path
from datetime import datetime

classics_dir = Path("data/classics/original")
output_dir = Path("docs/knowledge_engine")

# 六部经典信息
classics = [
    {"name": "YHZP", "file": "YHZP_渊海子平_完整全文.md", "expected_chapters": 305, "check_pattern": r"^第 \d+ 章$"},
    {"name": "DTS", "file": "DTS_滴天髓_完整全文.md", "expected_chapters": 66, "check_pattern": r"^第 \d+ 章$"},
    {"name": "QTBJ", "file": "QTBJ_穷通宝鉴_完整全文.md", "expected_chapters": 113, "check_pattern": r"^第 \d+ 章$"},
    {"name": "SFTK", "file": "SFTK_神峰通考_完整全文.md", "expected_chapters": 12, "check_pattern": r"^## "},
    {"name": "SMTH", "file": "SMTH_三命通会_完整全文.md", "expected_chapters": 381, "check_pattern": r"^第 \d+ 章$|^卷 \d+"},
    {"name": "PZZQ", "file": "PZZQ_子平真诠_完整全文.md", "expected_chapters": 52, "check_pattern": r"^第 \d+ 章$"},
]

# 已知缺口
known_gaps = {
    "DTS": ["气血论", "根蒂论", "化元论", "流运论", "父丧论", "母丧论", "杂格局论", "音律论", "品貌论", "进程论", "关格论", "玄关论"],
    "QTBJ": ["己日调候"]
}

def verify():
    results = []
    
    for classic in classics:
        file_path = classics_dir / classic["file"]
        if not file_path.exists():
            results.append({
                **classic,
                "lines": 0,
                "chapters": 0,
                "status": "MISSING",
                "size_kb": 0
            })
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.count('\n') + 1
        size_kb = file_path.stat().st_size // 1024
        
        import re
        chapters = len(re.findall(classic["check_pattern"], content, re.MULTILINE))
        
        # 检查最后章节
        last_chapter = "N/A"
        matches = re.findall(classic["check_pattern"], content, re.MULTILINE)
        if matches:
            last_chapter = matches[-1][:30]  # 截断显示
        
        # 检查完整性
        expected = classic["expected_chapters"]
        if chapters >= expected * 0.95:  # 95%+ 算完整
            status = "COMPLETE"
        elif chapters > 0:
            status = "PARTIAL"
        else:
            status = "UNKNOWN"
        
        results.append({
            **classic,
            "lines": lines,
            "chapters": chapters,
            "expected": expected,
            "status": status,
            "last_chapter": last_chapter,
            "size_kb": size_kb
        })
    
    return results

def generate_report(results):
    output_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")
    report_path = output_dir / f"classic_completeness_report_{date_str}.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 六部经典完整性验证报告\n\n")
        f.write(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 验证结果\n\n")
        f.write("| 经典 | 行数 | 章节数 | 完整性 | 状态 | 大小 |\n")
        f.write("|------|------|--------|--------|------|------|\n")
        
        total_lines = 0
        for r in results:
            total_lines += r["lines"]
            completeness = f"{r['chapters']/r['expected']*100:.1f}%" if r.get('expected') else "N/A"
            f.write(f"| {r['name']} | {r['lines']:,} | {r['chapters']} | {completeness} | {r['status']} | {r['size_kb']}KB |\n")
        
        f.write(f"| **总计** | **{total_lines:,}** | - | - | - | - |\n\n")
        
        # 缺口说明
        f.write("## 已知缺口\n\n")
        has_gaps = False
        for classic in ["DTS", "QTBJ"]:
            if classic in known_gaps:
                has_gaps = True
                f.write(f"### {classic}\n\n")
                for gap in known_gaps[classic]:
                    f.write(f"- {gap}\n")
                f.write("\n")
        
        if not has_gaps:
            f.write("无已知缺口。\n")
        
        f.write(f"\n报告路径: `{report_path}`\n")
    
    return report_path

if __name__ == "__main__":
    print("=== 六部经典完整性验证 ===\n")
    results = verify()
    report_path = generate_report(results)
    
    print("验证结果:")
    for r in results:
        print(f"  {r['name']}: {r['lines']:,}行, {r['chapters']}章, {r['status']}")
    
    print(f"\n报告已生成: {report_path}")
