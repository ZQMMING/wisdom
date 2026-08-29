"""
P0-1.2.2 继续深挖原典认证 — 剩余 UNRESOLVED 细节精确搜索

重点解决：
1. 火土同生完整体系：戊随丙、己随丁的具体十二长生映射
2. 藏干中气：中气在藏干语境下的原典依据
3. 三会化气五行：寅卯辰化木、巳午未化火等的原典依据

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

# 更精确的搜索关键词
SEARCH_GROUPS = {
    "火土同生_完整体系": [
        "戊长生在寅", "己长生在酉", "戊禄在巳", "己禄在午",
        "戊帝旺在午", "己帝旺在巳", "戊墓在戌", "己墓在辰",
        "戊土长生", "己土长生", "戊随丙", "己随丁",
        "丙戊", "丁己", "火土同宫", "火土同禄",
        "戊生于寅", "己生于酉", "土寄生于",
    ],
    "藏干_中气": [
        "中气", "本气中气", "中气余气", "支中中气",
        "藏干中气", "人元中气", "地支中气",
        "辰中乙戊癸", "戌中辛丁戊", "丑中癸辛己", "未中乙己丁",
        "寅中甲丙戊", "申中庚壬戊", "巳中丙戊庚", "亥中壬甲",
        "子午藏", "卯酉藏", "藏干歌", "人元歌",
    ],
    "三会_化气": [
        "寅卯辰会", "寅卯辰方", "寅卯辰木",
        "巳午未会", "巳午未方", "巳午未火",
        "申酉戌会", "申酉戌方", "申酉戌金",
        "亥子丑会", "亥子丑方", "亥子丑水",
        "三会木", "三会火", "三会金", "三会水",
        "方局", "会方", "会局化", "三会化",
        "东方木", "南方火", "西方金", "北方水",
        "寅卯辰全", "巳午未全", "申酉戌全", "亥子丑全",
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
                idx = text.find(keyword)
                start = max(0, idx - 150)
                end = min(len(text), idx + 250)
                context = text[start:end]
                results.append({
                    "classic": classic_name,
                    "passage_id": passage_id,
                    "source": source,
                    "keyword": keyword,
                    "context": context,
                })
                break
    return results


def main():
    print("=" * 80)
    print("P0-1.2.2 继续深挖原典认证 — 剩余 UNRESOLVED 细节")
    print("=" * 80)
    print()

    classics = {}
    for name, filename in CLASSIC_FILES.items():
        filepath = CLASSICS_DIR / filename
        if filepath.exists():
            passages = load_classic(filepath)
            classics[name] = passages
            print(f"  ✅ 加载 {name}: {len(passages)} 段")
    print()

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

    output_path = Path(r"D:\shuntian\backend\docs\P0_1_2_2_deeper_evidence_raw.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"详细结果已保存到: {output_path}")
    print()

    print("=" * 80)
    print("关键原典证据预览")
    print("=" * 80)
    print()

    for group_name, results in all_results.items():
        if not results:
            print(f"【{group_name}】未找到匹配")
            print()
            continue
        print(f"【{group_name}】共 {len(results)} 段，预览前8条：")
        for r in results[:8]:
            print(f"  📖 {r['classic']} ({r['passage_id']}) 关键词: {r['keyword']}")
            print(f"     上下文: ...{r['context'][:250]}...")
            print()
        print()


if __name__ == "__main__":
    main()
