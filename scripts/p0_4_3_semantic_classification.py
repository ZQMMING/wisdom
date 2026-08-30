# -*- coding: utf-8 -*-
"""P0-4.3: 五经规则语义类型研究

目标：
1. 建立语义类型体系
2. 从五经中抽取样本并分类
3. 统计分布，验证分类标准

语义类型定义：
① 事实/状态 - 描述客观状态
② 条件 - 明确条件关系
③ 充分条件 - 满足即成立
④ 必要条件 - 必须满足
⑤ 倾向/宜忌 - 推荐或忌讳
⑥ 制约/阻断 - 阻止或限制
⑦ 推论 - 从前提推出的结论
⑧ 复合论断 - 多个条件组合
⑨ 未确定 - 无法判断语义
"""
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple


# 语义类型定义
SEMANTIC_TYPES = {
    "FACT": "① 事实/状态 - 描述客观状态",
    "CONDITION": "② 条件 - 明确条件关系",
    "SUFFICIENT": "③ 充分条件 - 满足即成立",
    "NECESSARY": "④ 必要条件 - 必须满足",
    "PREFERENCE": "⑤ 倾向/宜忌 - 推荐或忌讳",
    "BLOCKING": "⑥ 制约/阻断 - 阻止或限制",
    "INFERENCE": "⑦ 推论 - 从前提推出的结论",
    "COMPOUND": "⑧ 复合论断 - 多个条件组合",
    "UNKNOWN": "⑨ 未确定 - 无法判断语义",
}


# 分类规则（基于关键词）
classifiers = {
    "FACT": [
        r"[甲乙丙丁戊己庚辛壬癸][木火土金水].*生|克|旺|相|休|囚|死",
        r"日主.*强|弱|旺|相|休|囚|死",
        r"月令.*当权|得令|失令",
    ],
    "SUFFICIENT": [
        r"若.*则.*",
        r"见.*必.*",
        r"逢.*主.*",
        r"得.*即.*",
    ],
    "NECESSARY": [
        r"须.*",
        r"必.*",
        r"当.*",
        r"宜.*",
    ],
    "PREFERENCE": [
        r"宜.*",
        r"喜.*",
        r"忌.*",
        r"畏.*",
        r"好.*",
    ],
    "BLOCKING": [
        r"不可.*",
        r"忌.*",
        r"畏.*",
        r"犯.*凶",
        r"破.*",
    ],
    "INFERENCE": [
        r"故.*",
        r"是.*",
        r"乃.*",
        r"此.*也",
    ],
    "COMPOUND": [
        r".*且.*",
        r".*而.*",
        r".*与.*",
        r".*并.*",
    ],
}


def load_classic_text(classic_name: str) -> Optional[str]:
    """加载经典文本"""
    corpus_path = Path("D:/today/Canonical-Mining/五部经典完整数据")
    
    file_map = {
        "滴天髓": "DTS_滴天髓_完整全文.md",
        "渊海子平": "YHZP_渊海子平_完整全文.md",
        "三命通会": "SMTH_三命通会_完整全文.md",
        "穷通宝鉴": "QTBJ_穷通宝鉴_完整全文.md",
        "子平真诠": "PZZQ_子平真诠_完整全文.md",
    }
    
    if classic_name not in file_map:
        return None
    
    file_path = corpus_path / file_map[classic_name]
    if not file_path.exists():
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def classify_sentence(text: str) -> Tuple[str, str]:
    """分类单句"""
    # 优先检查 BLOCKING
    for pattern in classifiers["BLOCKING"]:
        if re.search(pattern, text):
            return "BLOCKING", "制约/阻断"
    
    # 检查 COMPOUND
    for pattern in classifiers["COMPOUND"]:
        if re.search(pattern, text):
            return "COMPOUND", "复合论断"
    
    # 检查 INFERENCE
    for pattern in classifiers["INFERENCE"]:
        if re.search(pattern, text):
            return "INFERENCE", "推论"
    
    # 检查 SUFFICIENT
    for pattern in classifiers["SUFFICIENT"]:
        if re.search(pattern, text):
            return "SUFFICIENT", "充分条件"
    
    # 检查 NECESSARY
    for pattern in classifiers["NECESSARY"]:
        if re.search(pattern, text):
            return "NECESSARY", "必要条件"
    
    # 检查 PREFERENCE
    for pattern in classifiers["PREFERENCE"]:
        if re.search(pattern, text):
            return "PREFERENCE", "倾向/宜忌"
    
    # 检查 FACT
    for pattern in classifiers["FACT"]:
        if re.search(pattern, text):
            return "FACT", "事实/状态"
    
    return "UNKNOWN", "未确定"


def extract_sentences(text: str, max_count: int = 100) -> List[str]:
    """从文本中提取句子（改进版）"""
    # 按段落分割
    paragraphs = text.split('\n\n')

    sentences = []
    seen = set()

    for para in paragraphs:
        lines = para.split('\n')

        # 查找【原文】标记
        for i, line in enumerate(lines):
            if '【原文】' in line:
                # 提取原文内容
                match = re.search(r'【原文】\s*(.+)', line)
                if match:
                    sentence = match.group(1).strip()
                    # 过滤掉元数据行
                    if (len(sentence) > 10 and len(sentence) < 150
                            and '来源' not in sentence
                            and '共' not in sentence
                            and '整合' not in sentence
                            and sentence not in seen):
                        seen.add(sentence)
                        sentences.append(sentence)
                        break

            # 也检查 markdown 引用格式
            elif line.startswith('> ') and len(line) > 15:
                content = line.lstrip('> ').strip()
                if ('【原文】' in content or '**《' in content) and '来源' not in content:
                    # 提取实际内容
                    match = re.search(r'\*\*《(.+?)》\*\*\s*(.+)', content)
                    if match:
                        sentence = match.group(2).strip()
                    else:
                        sentence = re.sub(r'【原文】\s*', '', content).strip()

                    if (len(sentence) > 10 and len(sentence) < 150
                            and sentence not in seen):
                        seen.add(sentence)
                        sentences.append(sentence)

        if len(sentences) >= max_count:
            break

    return sentences


def main():
    print("=== P0-4.3: 五经规则语义类型研究 ===\n")
    
    # 经典列表
    classics = ["滴天髓", "渊海子平", "三命通会", "穷通宝鉴", "子平真诠"]
    
    all_samples = []
    type_counts = {t: 0 for t in SEMANTIC_TYPES.keys()}
    
    for classic in classics:
        print(f"处理: {classic}")
        text = load_classic_text(classic)
        
        if not text:
            print(f"  ⚠️ 未找到原文")
            continue
        
        # 提取句子
        sentences = extract_sentences(text, max_count=50)
        print(f"  提取句子: {len(sentences)} 条")
        
        # 分类
        for sentence in sentences:
            type_key, type_desc = classify_sentence(sentence)
            type_counts[type_key] += 1
            
            all_samples.append({
                "classic": classic,
                "type": type_key,
                "type_desc": type_desc,
                "sentence": sentence[:100],  # 截断
            })
        
        print(f"  分类完成: {type_counts[type_key]} 条\n")
    
    # 统计
    print("=== 语义类型分布 ===")
    for type_key, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {SEMANTIC_TYPES[type_key]}: {count}")
    
    # 输出报告
    report = {
        "generated": __import__('datetime').datetime.now().isoformat(),
        "summary": {
            "total_sentences": sum(type_counts.values()),
            "type_distribution": {k: v for k, v in type_counts.items()},
        },
        "samples": all_samples[:50],  # 只保存前 50 条样本
    }
    
    with open('data/p0_4_3_classification_result.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 data/p0_4_3_classification_result.json")


if __name__ == '__main__':
    main()
