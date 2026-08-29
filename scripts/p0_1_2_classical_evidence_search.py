"""
P0-1.2 原典认证 — 在五部经典段落数据中搜索固定数据表的原典依据

搜索范围：
  - DTS_滴天髓_段落数据.json
  - PZZQ_子平真诠_段落数据.json
  - QTBJ_穷通宝鉴_段落数据.json
  - SMTH_三命通会_段落数据.json
  - YHZP_渊海子平_段落数据.json

搜索关键词：
  - 十二长生：长生、沐浴、冠带、临官、帝旺、衰、病、死、墓、绝、胎、养
  - 藏干：本气、中气、余气、藏干、藏
  - 六冲：六冲、相冲、冲
  - 六害：六害、相害、害
  - 六合：六合、相合、合
  - 三合：三合、三合局
  - 三刑：三刑、相刑、刑
  - 空亡：空亡、空、亡
  - 天干五合：五合、天干合、甲己、乙庚、丙辛、丁壬、戊癸

只搜索，不重构。输出原典依据清单。
"""

import json
import os
from pathlib import Path

# 五部经典段落数据路径
CLASSICS_DIR = Path(r"D:\today\Canonical-Mining\五部经典完整数据")

CLASSIC_FILES = {
    "滴天髓": "DTS_滴天髓_段落数据.json",
    "子平真诠": "PZZQ_子平真诠_段落数据.json",
    "穷通宝鉴": "QTBJ_穷通宝鉴_段落数据.json",
    "三命通会": "SMTH_三命通会_段落数据.json",
    "渊海子平": "YHZP_渊海子平_段落数据.json",
}

# 搜索关键词分组
SEARCH_GROUPS = {
    "十二长生": ["长生", "沐浴", "冠带", "临官", "帝旺", "十二长生", "生旺死绝", "生旺墓绝"],
    "藏干": ["本气", "中气", "余气", "藏干", "地支藏", "人元"],
    "六冲": ["六冲", "相冲", "地支冲", "子午冲", "卯酉冲"],
    "六害": ["六害", "相害", "地支害", "子未害", "六穿"],
    "六合": ["六合", "地支合", "子丑合", "寅亥合", "六合化"],
    "三合": ["三合", "三合局", "申子辰", "亥卯未", "寅午戌", "巳酉丑"],
    "三刑": ["三刑", "相刑", "地支刑", "无恩之刑", "恃势之刑", "无礼之刑", "自刑"],
    "空亡": ["空亡", "六甲空", "旬空", "孤虚"],
    "天干五合": ["五合", "天干合", "甲己", "乙庚", "丙辛", "丁壬", "戊癸", "合化"],
}


def load_classic_json(filepath: Path) -> list:
    """加载经典段落数据 JSON"""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    # 处理不同的 JSON 结构
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        # 可能是 {"paragraphs": [...]} 或其他结构
        for key in ["passages", "paragraphs", "data", "items", "content"]:
            if key in data and isinstance(data[key], list):
                return data[key]
        # 如果没有已知的 key，返回所有 value 为 list 的第一个
        for v in data.values():
            if isinstance(v, list) and len(v) > 0:
                return v
    return []


def extract_text(paragraph) -> str:
    """从段落对象中提取文本"""
    if isinstance(paragraph, str):
        return paragraph
    elif isinstance(paragraph, dict):
        for key in ["text", "content", "paragraph", "原文", "正文"]:
            if key in paragraph and isinstance(paragraph[key], str):
                return paragraph[key]
    return str(paragraph)


def extract_location(paragraph, classic_name: str) -> str:
    """从段落对象中提取位置信息"""
    if isinstance(paragraph, dict):
        parts = []
        for key in ["chapter", "section", "title", "篇章", "章节", "卷", "篇", "节"]:
            if key in paragraph and paragraph[key]:
                parts.append(str(paragraph[key]))
        if parts:
            return f"{classic_name} · {' / '.join(parts)}"
    return classic_name


def search_in_classic(classic_name: str, paragraphs: list, keywords: list) -> list:
    """在一部经典中搜索关键词，返回匹配的段落列表"""
    results = []
    for i, para in enumerate(paragraphs):
        text = extract_text(para)
        location = extract_location(para, classic_name)
        for keyword in keywords:
            if keyword in text:
                results.append({
                    "classic": classic_name,
                    "location": location,
                    "keyword": keyword,
                    "text": text[:500],  # 限制长度
                    "paragraph_index": i,
                })
                break  # 一个段落只匹配一次
    return results


def main():
    print("=" * 80)
    print("P0-1.2 原典认证 — 五部经典固定数据表原典依据搜索")
    print("=" * 80)
    print()
    print("原则：只搜索，不重构。目标是找到固定数据表的原典依据。")
    print()

    # 加载所有经典
    classics = {}
    for name, filename in CLASSIC_FILES.items():
        filepath = CLASSICS_DIR / filename
        if filepath.exists():
            paragraphs = load_classic_json(filepath)
            classics[name] = paragraphs
            print(f"  ✅ 加载 {name}: {len(paragraphs)} 段")
        else:
            print(f"  ❌ 未找到 {name}: {filepath}")

    print()

    # 按分组搜索
    all_results = {}
    for group_name, keywords in SEARCH_GROUPS.items():
        print(f"--- 搜索: {group_name} ---")
        group_results = []
        for classic_name, paragraphs in classics.items():
            matches = search_in_classic(classic_name, paragraphs, keywords)
            group_results.extend(matches)
            if matches:
                print(f"  {classic_name}: {len(matches)} 段匹配")
        print(f"  总计: {len(group_results)} 段")
        print()
        all_results[group_name] = group_results

    # 输出摘要
    print("=" * 80)
    print("搜索结果摘要")
    print("=" * 80)
    print()
    print(f"{'数据表':<12} {'匹配段数':<10} {'涉及经典':<30}")
    print("-" * 60)
    for group_name, results in all_results.items():
        classics_involved = sorted(set(r["classic"] for r in results))
        print(f"{group_name:<12} {len(results):<10} {', '.join(classics_involved):<30}")

    print()

    # 保存详细结果到 JSON
    output_path = Path(r"D:\shuntian\backend\docs\P0_1_2_classical_evidence_raw.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"详细结果已保存到: {output_path}")
    print()

    # 输出每个分组的前几条关键证据
    print("=" * 80)
    print("关键原典证据预览（每个分组前3条）")
    print("=" * 80)
    print()
    for group_name, results in all_results.items():
        if not results:
            continue
        print(f"【{group_name}】")
        for r in results[:3]:
            print(f"  📖 {r['location']}")
            print(f"     关键词: {r['keyword']}")
            print(f"     原文: {r['text'][:150]}...")
            print()
        print()


if __name__ == "__main__":
    main()
