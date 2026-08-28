"""
P6.2-B ASSERT-001 原典精确溯源搜索脚本
从五部经典完整数据(JSON)和断语库中搜索与"财星透干逢流年合之主进财"相关的原文

三个独立搜索目标:
1. 财星透干 (财透/透财/财星透出)
2. 流年合财星 (流年合/岁君合/合财)
3. 主进财 (进财/得财/发财/主财)
"""

import json
import os
import re
from pathlib import Path


# 五部经典完整数据目录
CLASSICS_DIR = r"D:\today\Canonical-Mining\五部经典完整数据"
# 断语库目录
DUANYU_DIR = r"D:\today\五部经典断语库"

# 经典缩写映射
CLASSICS_MAP = {
    "DTS": "滴天髓",
    "PZZQ": "子平真诠",
    "QTBJ": "穷通宝鉴",
    "SMTH": "三命通会",
    "YHZP": "渊海子平",
}

# 搜索关键词组
KEYWORDS = {
    "P1_财星透干": [
        "财星透干", "财透干", "财透出", "透干财", "财星透出",
        "财透", "透财", "财星露", "露财", "财星明透",
    ],
    "P2_流年合财": [
        "流年合", "岁君合", "太岁合", "合财星", "合财",
        "财星合", "流年干合", "岁运合", "合去财", "合来财",
    ],
    "P3_主进财": [
        "进财", "得财", "发财", "主进", "主得财",
        "主发财", "招财", "进横财", "得横财", "发财致富",
    ],
    "组合_财透干+流年+合+进财": [
        "财星透干.*流年", "流年.*财星透干", "透干.*合.*财",
        "合.*财.*进", "财.*合.*流年",
    ],
}


def search_json_file(filepath, classic_name):
    """搜索JSON段落数据文件"""
    results = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 处理不同的JSON结构
        paragraphs = []
        if isinstance(data, list):
            paragraphs = data
        elif isinstance(data, dict):
            # 可能是 {"paragraphs": [...]} 或其他结构
            for key in ["paragraphs", "data", "passages", "items"]:
                if key in data and isinstance(data[key], list):
                    paragraphs = data[key]
                    break
            if not paragraphs:
                # 可能是 {id: {text: ...}} 结构
                for v in data.values():
                    if isinstance(v, dict) and "text" in v:
                        paragraphs.append(v)
                    elif isinstance(v, str):
                        paragraphs.append({"text": v})

        for i, para in enumerate(paragraphs):
            if isinstance(para, dict):
                text = para.get("text", "") or para.get("content", "") or para.get("paragraph", "")
                chapter = para.get("chapter", "") or para.get("section", "") or para.get("title", "")
                source = para.get("source", "")
            elif isinstance(para, str):
                text = para
                chapter = ""
                source = ""
            else:
                continue

            if not text:
                continue

            # 搜索每个关键词组
            for group_name, keywords in KEYWORDS.items():
                for kw in keywords:
                    if "*" in kw or "." in kw:
                        # 正则表达式
                        try:
                            if re.search(kw, text):
                                results.append({
                                    "classic": classic_name,
                                    "group": group_name,
                                    "keyword": kw,
                                    "chapter": chapter,
                                    "source": source,
                                    "text": text[:500],  # 截断
                                    "para_index": i,
                                })
                        except re.error:
                            pass
                    else:
                        if kw in text:
                            results.append({
                                "classic": classic_name,
                                "group": group_name,
                                "keyword": kw,
                                "chapter": chapter,
                                "source": source,
                                "text": text[:500],
                                "para_index": i,
                            })
    except Exception as e:
        print(f"  错误读取 {filepath}: {e}")
    return results


def search_md_file(filepath, source_name):
    """搜索Markdown断语文件"""
    results = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        current_classic = source_name
        for i, line in enumerate(lines):
            line = line.strip()
            # 检测经典标题
            if line.startswith("## 《"):
                current_classic = line.strip("# 《》")
                continue
            if not line.startswith("**"):
                continue

            # 提取断语文本
            text = re.sub(r"^\*\*\d+\.\*\*\s*", "", line)

            for group_name, keywords in KEYWORDS.items():
                for kw in keywords:
                    if "*" in kw or "." in kw:
                        try:
                            if re.search(kw, text):
                                results.append({
                                    "classic": current_classic,
                                    "group": group_name,
                                    "keyword": kw,
                                    "chapter": "",
                                    "source": source_name,
                                    "text": text[:500],
                                    "line": i + 1,
                                })
                        except re.error:
                            pass
                    else:
                        if kw in text:
                            results.append({
                                "classic": current_classic,
                                "group": group_name,
                                "keyword": kw,
                                "chapter": "",
                                "source": source_name,
                                "text": text[:500],
                                "line": i + 1,
                            })
    except Exception as e:
        print(f"  错误读取 {filepath}: {e}")
    return results


def main():
    print("=" * 100)
    print("P6.2-B ASSERT-001 原典精确溯源搜索")
    print("目标: 财星透干逢流年合之主进财")
    print("=" * 100)

    all_results = []

    # 1. 搜索五部经典完整数据 JSON
    print("\n[1/2] 搜索五部经典完整数据 (JSON段落数据)...")
    for abbrev, name in CLASSICS_MAP.items():
        json_file = os.path.join(CLASSICS_DIR, f"{abbrev}_{name}_段落数据.json")
        if os.path.exists(json_file):
            print(f"  搜索 {name}...")
            results = search_json_file(json_file, name)
            all_results.extend(results)
            print(f"    找到 {len(results)} 条匹配")
        else:
            print(f"  文件不存在: {json_file}")

    # 2. 搜索断语库
    print("\n[2/2] 搜索断语库...")
    # 按经典分
    classics_dir = os.path.join(DUANYU_DIR, "01_按经典分")
    if os.path.exists(classics_dir):
        for fname in os.listdir(classics_dir):
            if fname.endswith("_断语.md"):
                filepath = os.path.join(classics_dir, fname)
                source_name = fname.replace("_断语.md", "")
                print(f"  搜索 {source_name}...")
                results = search_md_file(filepath, source_name)
                all_results.extend(results)
                print(f"    找到 {len(results)} 条匹配")

    # 按类别分 - 财运类
    caiyun_file = os.path.join(DUANYU_DIR, "02_按类别分", "财运类_断语.md")
    if os.path.exists(caiyun_file):
        print(f"  搜索 财运类断语...")
        results = search_md_file(caiyun_file, "财运类")
        all_results.extend(results)
        print(f"    找到 {len(results)} 条匹配")

    # 流年大运类
    liunian_file = os.path.join(DUANYU_DIR, "02_按类别分", "流年大运类_断语.md")
    if os.path.exists(liunian_file):
        print(f"  搜索 流年大运类断语...")
        results = search_md_file(liunian_file, "流年大运类")
        all_results.extend(results)
        print(f"    找到 {len(results)} 条匹配")

    # 刑冲合害类
    hehai_file = os.path.join(DUANYU_DIR, "02_按类别分", "刑冲合害类_断语.md")
    if os.path.exists(hehai_file):
        print(f"  搜索 刑冲合害类断语...")
        results = search_md_file(hehai_file, "刑冲合害类")
        all_results.extend(results)
        print(f"    找到 {len(results)} 条匹配")

    # 去重
    print(f"\n总计找到 {len(all_results)} 条匹配 (去重前)")
    seen = set()
    unique_results = []
    for r in all_results:
        key = (r["classic"], r["group"], r["keyword"], r["text"][:100])
        if key not in seen:
            seen.add(key)
            unique_results.append(r)
    print(f"去重后 {len(unique_results)} 条")

    # 按组统计
    print("\n" + "=" * 100)
    print("按搜索目标分组统计")
    print("=" * 100)
    for group_name in KEYWORDS.keys():
        group_results = [r for r in unique_results if r["group"] == group_name]
        print(f"\n【{group_name}】共 {len(group_results)} 条")
        # 按经典统计
        from collections import Counter
        classic_counts = Counter(r["classic"] for r in group_results)
        for classic, count in classic_counts.most_common():
            print(f"  {classic}: {count}条")

    # 输出详细结果 - 重点输出组合匹配和P1/P2/P3的关键条目
    print("\n" + "=" * 100)
    print("详细匹配结果 (重点条目)")
    print("=" * 100)

    for group_name in ["组合_财透干+流年+合+进财", "P1_财星透干", "P2_流年合财", "P3_主进财"]:
        group_results = [r for r in unique_results if r["group"] == group_name]
        if not group_results:
            print(f"\n【{group_name}】无匹配")
            continue

        print(f"\n{'='*80}")
        print(f"【{group_name}】共 {len(group_results)} 条 (显示前20条)")
        print(f"{'='*80}")
        for i, r in enumerate(group_results[:20]):
            print(f"\n  [{i+1}] {r['classic']} | 关键词: {r['keyword']}")
            if r.get("chapter"):
                print(f"      章节: {r['chapter']}")
            if r.get("source"):
                print(f"      来源: {r['source']}")
            print(f"      原文: {r['text'][:200]}")

    # 保存完整结果到JSON
    output_file = r"D:\shuntian\backend\docs\assert001_source_search_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(unique_results, f, ensure_ascii=False, indent=2)
    print(f"\n完整结果已保存到: {output_file}")
    print(f"共 {len(unique_results)} 条匹配")


if __name__ == "__main__":
    main()
