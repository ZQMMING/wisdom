# -*- coding: utf-8 -*-
"""P0-4.2: 原书上下文取证

目标：对 4 条 Authorized Primitive 做原书上下文取证
"""
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional


# 4 条需要取证的 Primitive
TARGET_PRIMITIVES = [
    {
        "id": "滴天髓_生克制化_总论",
        "source_text": "生克制化，须制中有生，生中有制。太过者宜损之，不及者宜益之。",
        "classic": "滴天髓",
        "chapter": "生克制化",
    },
    {
        "id": "滴天髓_理法_气势",
        "source_text": "一行得二三人之气，则党众而专，须从其势",
        "classic": "滴天髓",
        "chapter": "理法·气势",
    },
    {
        "id": "滴天髓_理法_生扶克泄耗",
        "source_text": "生克制化，须制中有生，生中有制",
        "classic": "滴天髓",
        "chapter": "理法·生扶克泄耗",
    },
    {
        "id": "渊海子平_论法_论太岁吉凶",
        "source_text": "太岁乃年中天子，故不可犯，犯之则凶。经云：『日犯岁君，灾殃必重；五行有救，其年反必招财。』且如甲日见戊年，太岁是也，剋重者死。甲乙若寅卯亥未日时者，犯剋岁君，决死无疑；有救则吉，乃八字庚辛巳酉丑金局...",
        "classic": "渊海子平",
        "chapter": "论法·论太岁吉凶",
    },
]


def load_classic_corpus() -> Dict[str, str]:
    """加载五部经典完整数据
    
    从资料库加载
    """
    corpus_path = Path("D:/today/Canonical-Mining/五部经典完整数据")
    
    corpus = {}
    
    # 尝试加载各经典
    classic_files = {
        "滴天髓": ["DTS_滴天髓_完整全文.md", "DTS_滴天髓_段落数据.json"],
        "渊海子平": ["YHZP_渊海子平_完整全文.md", "YHZP_渊海子平_段落数据.json"],
        "三命通会": ["SMTH_三命通会_完整全文.md", "SMTH_三命通会_段落数据.json"],
        "穷通宝鉴": ["QTBJ_穷通宝鉴_完整全文.md", "QTBJ_穷通宝鉴_段落数据.json"],
        "子平真诠": ["PZZQ_子平真诠_完整全文.md", "PZZQ_子平真诠_段落数据.json"],
    }
    
    for classic, files in classic_files.items():
        for f in files:
            path = corpus_path / f
            if path.exists():
                with open(path, 'r', encoding='utf-8') as fp:
                    corpus[classic] = fp.read()
                break
    
    return corpus


def find_context(text: str, keyword: str, context_size: int = 500) -> Optional[str]:
    """在文本中查找关键词并返回上下文"""
    if keyword not in text:
        return None
    
    idx = text.find(keyword)
    start = max(0, idx - context_size)
    end = min(len(text), idx + len(keyword) + context_size)
    
    return text[start:end]


def analyze_primitive_context(primitive: dict, corpus: Dict[str, str]) -> dict:
    """分析单条 Primitive 的上下文"""
    classic = primitive["classic"]
    source_text = primitive["source_text"]
    
    result = {
        "id": primitive["id"],
        "classic": classic,
        "source_text": source_text,
        "context_found": False,
        "full_context": "",
        "related_passages": [],
        "semantic_analysis": "",
        "feature_mapping": {},
        "questions": [],
    }
    
    if classic not in corpus:
        result["questions"].append(f"未找到 {classic} 原文数据")
        return result
    
    text = corpus[classic]
    
    # 查找完整上下文
    context = find_context(text, source_text[:20], context_size=1000)
    if context:
        result["context_found"] = True
        result["full_context"] = context
    
    # 查找同篇相关论述
    chapter = primitive.get("chapter", "")
    if chapter:
        # 简化：查找包含关键词的段落
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if source_text[:10] in line:
                # 获取前后 10 行
                start = max(0, i - 5)
                end = min(len(lines), i + 16)
                related = '\n'.join(lines[start:end])
                result["related_passages"].append(related)
                break
    
    # 语义分析（保守）
    result["semantic_analysis"] = analyze_semantics_conservative(source_text)
    
    return result


def analyze_semantics_conservative(source_text: str) -> str:
    """保守语义分析：不假设 AND/OR 关系"""
    analysis = []
    
    # 检查明确关键词
    if "须" in source_text:
        analysis.append("- '须' 表示必要条件，但未必是逻辑 AND")
    if "则" in source_text:
        analysis.append("- '则' 表示条件结果关系，但条件组合方式未明确")
    if "或" in source_text:
        analysis.append("- '或' 表示选择关系（OR）")
    if "若" in source_text:
        analysis.append("- '若' 表示假设条件")
    
    if not analysis:
        analysis.append("- 原典未使用明确逻辑连接词")
        analysis.append("- 无法确定 Condition 之间的逻辑关系")
    
    return "\n".join(analysis)


def main():
    print("=== P0-4.2: 原书上下文取证 ===\n")
    
    # 加载 Corpus
    print("加载五部经典 Corpus...")
    corpus = load_classic_corpus()
    
    if not corpus:
        print("⚠️ 未找到原书数据，请检查路径: D:/today/Canonical-Mining/五部经典完整数据/")
        return
    
    print(f"已加载 {len(corpus)} 部经典\n")
    
    # 对每条 Primitive 进行取证
    results = []
    for prim in TARGET_PRIMITIVES:
        print(f"取证: {prim['id']}")
        result = analyze_primitive_context(prim, corpus)
        results.append(result)
        
        print(f"  上下文: {'找到' if result['context_found'] else '未找到'}")
        print(f"  相关段落: {len(result['related_passages'])} 条")
        print(f"  语义分析: {result['semantic_analysis'][:50]}...")
        print()
    
    # 输出报告
    output = {
        "generated": __import__('datetime').datetime.now().isoformat(),
        "summary": {
            "total": len(results),
            "context_found": sum(1 for r in results if r["context_found"]),
            "total_related": sum(len(r["related_passages"]) for r in results),
            "total_questions": sum(len(r["questions"]) for r in results),
        },
        "results": results,
    }
    
    with open('data/p0_4_2_context_research.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("=== 取证报告 ===")
    print(f"总数: {output['summary']['total']}")
    print(f"找到上下文: {output['summary']['context_found']}")
    print(f"相关段落: {output['summary']['total_related']}")
    print(f"待确认问题: {output['summary']['total_questions']}")
    print(f"\n结果已保存到 data/p0_4_2_context_research.json")


if __name__ == '__main__':
    main()
