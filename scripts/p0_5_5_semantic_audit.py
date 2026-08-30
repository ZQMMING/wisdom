# -*- coding: utf-8 -*-
"""P0-5.5: YHZP-LF-TSJX-5 "日犯岁君" 语义取证

目标：回原典确认"岁君""犯"的精确语义
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '.')

# 搜索渊海子平原文
def search_yuanhai_ziping(keyword):
    """搜索渊海子平中关于关键词的段落"""
    classic_path = Path('/d/today/Canonical-Mining/五部经典完整数据/YHZP_渊海子平_完整全文.md')
    
    if not classic_path.exists():
        return []
    
    with open(classic_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 简单搜索（实际应该用正则或更精确的匹配）
    results = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if keyword in line:
            # 获取上下文（前后5行）
            start = max(0, i-5)
            end = min(len(lines), i+6)
            context = '\n'.join(lines[start:end])
            results.append({
                "line_number": i+1,
                "keyword": keyword,
                "context": context.strip()
            })
    
    return results


def analyze_semantic取证():
    """分析语义取证结果"""
    print("=" * 60)
    print("P0-5.5: YHZP-LF-TSJX-5 '日犯岁君' 语义取证")
    print("=" * 60)
    
    # 搜索关键词
    keywords = ['岁君', '太岁', '犯岁', '日犯']
    
    all_results = {}
    for kw in keywords:
        results = search_yuanhai_ziping(kw)
        all_results[kw] = results
        print(f"\n【{kw}】找到 {len(results)} 条相关段落")
    
    return all_results


def extract_definitions(results):
    """从搜索结果中提取定义"""
    definitions = {
        "岁君": [],
        "犯": [],
        "太岁": [],
    }
    
    for kw, hits in results.items():
        for hit in hits:
            context = hit['context']
            # 简单的上下文分析（实际需要人工审核）
            if '岁君' in context:
                definitions['岁君'].append({
                    "source": "渊海子平",
                    "line": hit['line_number'],
                    "context": context[:200]
                })
            if '犯' in context and ('岁君' in context or '太岁' in context):
                definitions['犯'].append({
                    "source": "渊海子平",
                    "line": hit['line_number'],
                    "context": context[:200]
                })
    
    return definitions


if __name__ == "__main__":
    results = analyze_semantic取证()
    definitions = extract_definitions(results)
    
    # 保存结果
    output_path = Path(__file__).parent.parent / "data" / "p0_5_5_semantic_audit.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "audit_date": datetime.now().isoformat(),
            "primitive_id": "YHZP-LF-TSJX-5",
            "source_text": "日犯岁君，灾殃必重；五行有救，其年反必招财",
            "search_results": results,
            "definitions": definitions,
            "notes": "需要人工审核上下文，确认'犯'的精确定义"
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
    
    # 关键问题
    print("\n" + "=" * 60)
    print("关键问题（待原典确认）")
    print("=" * 60)
    print("1. '岁君'是否等于'年干'？")
    print("2. '犯'是否仅指'日干克年干'？")
    print("3. 是否包含'日干冲年干'或其他关系？")
    print("4. '救'的定义是什么？")
