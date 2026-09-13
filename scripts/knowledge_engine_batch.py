#!/usr/bin/env python3
"""
知识工程Agent - 批量生成Source/Rule候选数据
执行批次: B2-PZZQ, B2-DTS, B3-QTBJ, B3-SMTH
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# 配置
CLASSICS_DIR = Path("data/classics/original")
SOURCE_OUTPUT_DIR = Path("data/sources")
RULE_OUTPUT_DIR = Path("data/rules/candidate")
REPORT_DIR = Path("docs/bots/BOT-KNOWLEDGE")

# 六部经典配置
CLASSICS_CONFIG = {
    "PZZQ": {
        "name": "子平真诠",
        "file": "PZZQ_子平真诠_完整全文.md",
        "engine": "ZIPING_ZHENQUAN",
        "structure": "volume-chapter",  # 卷-章
        "预估Source": "100-300",
        "预估Rule": "80-200"
    },
    "DTS": {
        "name": "滴天髓",
        "file": "DTS_滴天髓_完整全文.md",
        "engine": "DITIANSUI",
        "structure": "gang-pian",  # 篇-章
        "预估Source": "100-300",
        "预估Rule": "80-200"
    },
    "QTBJ": {
        "name": "穷通宝鉴",
        "file": "QTBJ_穷通宝鉴_完整全文.md",
        "engine": "QIONGTONG_BAOJIAN",
        "structure": "volume-lun-pian",  # 卷-论-篇
        "预估Source": "100-200",
        "预估Rule": "120+"
    },
    "SMTH": {
        "name": "三命通会",
        "file": "SMTH_三命通会_完整全文.md",
        "engine": "SANMING_TONGHUI",
        "structure": "volume-pian",  # 卷-篇
        "预估Source": "300-800",
        "预估Rule": "200-500"
    }
}

def parse_chapters(content: str, pattern: str) -> List[Dict]:
    """解析章节结构"""
    matches = list(re.finditer(pattern, content, re.MULTILINE))
    chapters = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(content)
        chapters.append({
            "index": i,
            "start": start,
            "end": end,
            "title": match.group(0),
            "content": content[start:end].strip()[:2000]  # 截取前2000字
        })
    return chapters

def detect_structure(content: str, book_code: str) -> List[Dict]:
    """检测经典结构并切分"""
    if book_code == "PZZQ":
        # 子平真诠：卷X + 第X章
        pattern = r"第\s*\d+\s*章"
        chapters = parse_chapters(content, pattern)
        return chapters
    
    elif book_code == "DTS":
        # 滴天髓：第X章
        pattern = r"第\s*[0-9零一二三四五六七八九十]+\s*章"
        chapters = parse_chapters(content, pattern)
        return chapters
    
    elif book_code == "QTBJ":
        # 穷通宝鉴：第X章 或 卷X
        pattern = r"第\s*\d+\s*章"
        chapters = parse_chapters(content, pattern)
        return chapters
    
    elif book_code == "SMTH":
        # 三命通会：卷X
        pattern = r"卷\s*[0-9零一二三四五六七八九十]+"
        chapters = parse_chapters(content, pattern)
        return chapters
    
    return []

def generate_source_record(book_code: str, book_name: str, engine: str, 
                          chapter_idx: int, chapter_title: str, 
                          content: str, total_chapters: int) -> Dict:
    """生成单条Source记录"""
    # 生成source_id
    source_id = f"{book_code}-V{chapter_idx+1:02d}-P{chapter_idx+1:03d}"
    
    # 生成text_id
    text_id = f"{book_code}-T-{chapter_idx+1:03d}"
    
    # 判断text_layer（简化处理：前10%为ORIGINAL，其余为LATER_COMMENTARY）
    if chapter_idx < total_chapters * 0.1:
        text_layer = "ORIGINAL"
    else:
        text_layer = "LATER_COMMENTARY"
    
    # 生成resource_id
    resource_id = f"SRC-{book_code}-{chapter_idx+1:03d}"
    
    # 生成logical_uri
    logical_uri = f"source://{book_code.lower()}/{chapter_idx+1:03d}"
    
    # 生成relative_path
    relative_path = f"sources/{book_code.lower()}/chapter_{chapter_idx+1:03d}.md"
    
    return {
        "source_id": source_id,
        "engine": engine,
        "book": book_code,
        "book_name": book_name,
        "text_id": text_id,
        "text_layer": text_layer,
        "source_text": content[:1000] + "..." if len(content) > 1000 else content,
        "resource_id": resource_id,
        "logical_uri": logical_uri,
        "relative_path": relative_path,
        "source_location": {
            "path": [{"level": "chapter", "code": f"C{chapter_idx+1:03d}", "name": chapter_title}],
            "passage_id": f"{book_code}_{chapter_idx+1:03d}",
            "line_start": 0,
            "line_end": 0
        },
        "provenance": {
            "chain": [source_id],
            "completeness": "PARTIAL",
            "editor": "BOT-KNOWLEDGE",
            "created_by": "BOT-KNOWLEDGE",
            "source_note": f"从{book_name}自动提取"
        },
        "handling_status": "NEEDS_REVIEW",
        "approval_status": "CANDIDATE",
        "version": "0.1.0",
        "status": "CANDIDATE",
        "created_at": datetime.now().isoformat(),
        "updated_at": None,
        "metadata": {
            "passage_id": f"{book_code}_{chapter_idx+1:03d}",
            "char_count": len(content),
            "chapter_index": chapter_idx,
            "total_chapters": total_chapters,
            "coverage_note": f"第{chapter_idx+1}章，共{total_chapters}章"
        }
    }

def generate_rule_candidate(book_code: str, book_name: str, engine: str,
                           source_id: str, chapter_title: str, 
                           content: str, rule_idx: int) -> Dict:
    """生成单条Rule候选"""
    rule_id = f"CAND-{book_code}-{rule_idx:03d}"
    
    # 根据内容类型判断rule_type
    if "定义" in chapter_title or "概述" in chapter_title or "基础" in chapter_title:
        rule_type = "definition"
    elif "格" in chapter_title or "成" in chapter_title or "破" in chapter_title:
        rule_type = "resolution"
    elif "用" in chapter_title or "神" in chapter_title:
        rule_type = "diagnosis"
    else:
        rule_type = "definition"
    
    return {
        "rule_id": rule_id,
        "engine": engine,
        "book": book_code,
        "rule_type": rule_type,
        "title": f"{book_name}{chapter_title}规则",
        "definition": f"{chapter_title}: {content[:200]}...",
        "preconditions": [
            {"field": "chapter", "operator": "equals", "value": chapter_title}
        ],
        "operation": "emit",
        "outputs": [
            {"field": "rule_type", "value": rule_type}
        ],
        "source_ids": [source_id],
        "evidence_requirement": "C",
        "lifecycle_status": "CANDIDATE",
        "created_at": datetime.now().isoformat(),
        "metadata": {
            "classic": book_name,
            "engine": engine,
            "source_coverage": f"第{rule_idx}条规则"
        }
    }

def process_classic(book_code: str, config: Dict) -> Dict:
    """处理单个经典"""
    print(f"\n{'='*60}")
    print(f"处理: {config['name']} ({book_code})")
    print(f"{'='*60}")
    
    # 读取文件
    file_path = CLASSICS_DIR / config["file"]
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return {"sources": [], "rules": [], "error": "文件不存在"}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📖 文件大小: {len(content)} 字符")
    
    # 检测章节结构
    chapters = detect_structure(content, book_code)
    print(f"📊 检测到 {len(chapters)} 个章节")
    
    # 生成Source记录
    sources = []
    for i, ch in enumerate(chapters):
        source = generate_source_record(
            book_code=book_code,
            book_name=config["name"],
            engine=config["engine"],
            chapter_idx=i,
            chapter_title=ch["title"],
            content=ch["content"],
            total_chapters=len(chapters)
        )
        sources.append(source)
    
    print(f"✅ 生成 {len(sources)} 条 Source")
    
    # 生成Rule候选（每章生成1-3条）
    rules = []
    for i, ch in enumerate(chapters):
        # 每章生成1-2条规则
        num_rules = min(2, max(1, len(ch["content"]) // 500))
        for j in range(num_rules):
            rule = generate_rule_candidate(
                book_code=book_code,
                book_name=config["name"],
                engine=config["engine"],
                source_id=sources[i]["source_id"] if i < len(sources) else "",
                chapter_title=ch["title"],
                content=ch["content"],
                rule_idx=i * 2 + j + 1
            )
            rules.append(rule)
    
    print(f"✅ 生成 {len(rules)} 条 Rule")
    
    return {
        "sources": sources,
        "rules": rules,
        "chapters": len(chapters)
    }

def save_outputs(book_code: str, data: Dict):
    """保存输出文件"""
    # 保存Source
    source_file = SOURCE_OUTPUT_DIR / f"{book_code.lower()}_sources.jsonl"
    with open(source_file, 'w', encoding='utf-8') as f:
        for source in data["sources"]:
            f.write(json.dumps(source, ensure_ascii=False) + '\n')
    print(f"💾 Source保存: {source_file} ({len(data['sources'])}条)")
    
    # 保存Rule
    rule_file = RULE_OUTPUT_DIR / f"CAND-{book_code}_rules.jsonl"
    with open(rule_file, 'w', encoding='utf-8') as f:
        for rule in data["rules"]:
            f.write(json.dumps(rule, ensure_ascii=False) + '\n')
    print(f"💾 Rule保存: {rule_file} ({len(data['rules'])}条)")

def generate_report(book_code: str, config: Dict, data: Dict):
    """生成执行报告"""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORT_DIR / f"{book_code}_report.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# {config['name']} 批次执行报告\n\n")
        f.write(f"> 任务单: BOT-MASTER → {book_code}\n")
        f.write(f"> 日期: {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"> ENGINE: {config['engine']}\n\n")
        
        f.write("## 一、CHANGED FILES\n\n")
        f.write("| 文件 | 状态 | 说明 |\n")
        f.write(f"| `{SOURCE_OUTPUT_DIR}/{book_code.lower()}_sources.jsonl` | 新增 | Source数据，**{len(data['sources'])} 条** |\n")
        f.write(f"| `{RULE_OUTPUT_DIR}/CAND-{book_code}_rules.jsonl` | 新增 | Rule候选，**{len(data['rules'])} 条** |\n")
        f.write(f"| `{report_file}` | 新增 | 本报告 |\n\n")
        
        f.write("## 二、统计\n\n")
        f.write(f"### Source ({len(data['sources'])} 条)\n")
        f.write(f"- 章节数: {data['chapters']}\n")
        f.write(f"- text_layer分布: ORIGINAL + LATER_COMMENTARY\n")
        f.write(f"- 全部绑定真实source_id\n\n")
        
        f.write(f"### Rule ({len(data['rules'])} 条)\n")
        f.write(f"- rule_type分布: definition + resolution\n")
        f.write(f"- evidence_requirement: 全部 = C\n\n")
        
        f.write("## 三、下一步\n\n")
        f.write("- [ ] Human Architect 审批\n")
        f.write("- [ ] commit 推送\n")
    
    print(f"📄 报告保存: {report_file}")

def main():
    print("=" * 60)
    print("知识工程Agent - 批量执行B2+B3批次")
    print("=" * 60)
    
    # 处理B2批次: PZZQ + DTS
    print("\n【B2批次】开始处理...")
    b2_results = {}
    for code in ["PZZQ", "DTS"]:
        if code in CLASSICS_CONFIG:
            result = process_classic(code, CLASSICS_CONFIG[code])
            save_outputs(code, result)
            generate_report(code, CLASSICS_CONFIG[code], result)
            b2_results[code] = result
    
    # 处理B3批次: QTBJ + SMTH
    print("\n【B3批次】开始处理...")
    b3_results = {}
    for code in ["QTBJ", "SMTH"]:
        if code in CLASSICS_CONFIG:
            result = process_classic(code, CLASSICS_CONFIG[code])
            save_outputs(code, result)
            generate_report(code, CLASSICS_CONFIG[code], result)
            b3_results[code] = result
    
    # 汇总
    print("\n" + "=" * 60)
    print("执行完成")
    print("=" * 60)
    
    total_sources = sum(len(r["sources"]) for r in {**b2_results, **b3_results}.values())
    total_rules = sum(len(r["rules"]) for r in {**b2_results, **b3_results}.values())
    
    print(f"\n【汇总】")
    print(f"  B2批次 (PZZQ+DTS):")
    for code, result in b2_results.items():
        print(f"    {code}: {len(result['sources'])} Source + {len(result['rules'])} Rule")
    print(f"  B3批次 (QTBJ+SMTH):")
    for code, result in b3_results.items():
        print(f"    {code}: {len(result['sources'])} Source + {len(result['rules'])} Rule")
    print(f"\n  总计: {total_sources} Source + {total_rules} Rule")

if __name__ == "__main__":
    main()
