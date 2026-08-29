"""
P0-1.2.1 深入原典认证 — 针对 UNRESOLVED 问题的精确搜索

重点解决：
1. 火土同生（戊随丙、己随丁）的原典依据
2. 藏干三层分层（本气/中气/余气）的原典依据
3. 空亡效力（力量减半？）的原典依据
4. 三会局的具体定义和化气五行

只搜索，不重构。
"""

import json
from pathlib import Path

CLASSICS_DIR = Path(r"D:\today\Canonical-Mining\五部经典完整数据")

CLASSIC_FILES = {
    "滴天髓": "DTS_滴天髓_段落数据.json",
    "子平真诠": "PZZQ_子平真诠_段落数据.json",
    "穷通宝鉴": "QTBJ_穷通宝鉴_段落数据.json",
    "三命通会": "SMTH_三命通会_段落数据.json",
    "渊海子平": "YHZP_渊海子平_段落数据.json",
}

# 精确搜索关键词分组
SEARCH_GROUPS = {
    "火土同生": [
        "戊长生", "己长生", "戊随丙", "己随丁", "火土同生",
        "戊禄在巳", "己禄在午", "戊帝旺", "己帝旺",
        "土寄旺", "土寄生", "戊己", "火土",
    ],
    "藏干分层": [
        "本气", "中气", "余气", "主气", "杂气",
        "支中所藏", "地支藏", "人元", "藏干",
        "辰戌丑未", "四库", "墓库",
    ],
    "空亡效力": [
        "空亡", "空亡之力", "空亡减半", "空亡无力",
        "空亡为祸", "空亡吉凶", "六甲空", "旬空",
        "孤虚", "空亡之字",
    ],
    "三会局": [
        "三会", "三方", "寅卯辰", "巳午未", "申酉戌", "亥子丑",
        "会局", "会方", "三会局", "方局",
    ],
}


def load_classic(filepath: Path) -> list:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "passages" in data:
        return data["passages"]
    return []


def search_in_classic(classic_name: str, passages: list, keywords: list) -> list:
    results = []
    for para in passages:
        text = para.get("text", "")
        passage_id = para.get("passage_id", "")
        source = para.get("source", "")
        for keyword in keywords:
            if keyword in text:
                # 找到关键词在文本中的位置，提取上下文
                idx = text.find(keyword)
                start = max(0, idx - 100)
                end = min(len(text), idx + 200)
                context = text[start:end]
                results.append({
                    "classic": classic_name,
                    "passage_id": passage_id,
                    "source": source,
                    "keyword": keyword,
                    "context": context,
                })
                break  # 一个段落只匹配一次
    return results


def main():
    print("=" * 80)
    print("P0-1.2.1 深入原典认证 — UNRESOLVED 问题精确搜索")
    print("=" * 80)
    print()

    # 加载所有经典
    classics = {}
    for name, filename in CLASSIC_FILES.items():
        filepath = CLASSICS_DIR / filename
        if filepath.exists():
            passages = load_classic(filepath)
            classics[name] = passages
            print(f"  ✅ 加载 {name}: {len(passages)} 段")
    print()

    # 按分组搜索
    all_results = {}
    for group_name, keywords in SEARCH_GROUPS.items():
        print(f"--- 搜索: {group_name} ---")
        group_results = []
        for classic_name, passages in classics.items():
            matches = search_in_classic(classic_name, passages, keywords)
            group_results.extend(matches)
            if matches:
                print(f"  {classic_name}: {len(matches)} 段匹配")
        print(f"  总计: {len(group_results)} 段")
        print()
        all_results[group_name] = group_results

    # 保存详细结果
    output_path = Path(r"D:\shuntian\backend\docs\P0_1_2_1_deep_evidence_raw.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"详细结果已保存到: {output_path}")
    print()

    # 输出每个分组的关键证据预览
    print("=" * 80)
    print("关键原典证据预览")
    print("=" * 80)
    print()

    for group_name, results in all_results.items():
        if not results:
            print(f"【{group_name}】未找到匹配")
            print()
            continue
        print(f"【{group_name}】共 {len(results)} 段，预览前5条：")
        for r in results[:5]:
            print(f"  📖 {r['classic']} ({r['passage_id']}) 关键词: {r['keyword']}")
            print(f"     上下文: ...{r['context'][:200]}...")
            print()
        print()


if __name__ == "__main__":
    main()
