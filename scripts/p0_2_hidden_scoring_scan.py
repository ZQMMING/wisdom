"""
P0-2 全仓隐性评分扫描

目标：扫描整个 src 目录，查找 score、weight、threshold、strong、weak、strength、
balance、imbalance 等关键词，逐项判断这是：
- L1 Fact（原始事实，如十二长生状态、藏干内容）
- Relationship（关系，如五合配对、六冲配对）
- 未经授权的 Semantic Judgment（语义判断，如 strength_score、wang_score、力量减半）

严格遵守 P0 原则：
- 禁止五行计数 → score
- 禁止长生数量 → score
- 禁止藏干数量 → score
- 禁止党众 → +10、助寡 → -10
- 禁止财多 → 身弱、印多 → 身强
- 禁止合 → 强、冲 → 弱、刑 → 凶
- 禁止空亡 → 力量 × 0.5
"""

import os
import re
from pathlib import Path
from collections import defaultdict

SRC_DIR = Path(r"D:\shuntian\backend\src")

# 扫描关键词分类
SCAN_PATTERNS = {
    "score": [
        r"\bscore\b", r"_score\b", r"score_", r"得分", r"评分", r"打分",
    ],
    "weight": [
        r"\bweight\b", r"_weight\b", r"weight_", r"权重", r"加权", r"weighted",
    ],
    "threshold": [
        r"\bthreshold\b", r"_threshold\b", r"阈值", r"临界值", r">=\s*\d", r"<=\s*\d",
    ],
    "strength": [
        r"\bstrength\b", r"_strength\b", r"身强", r"身弱", r"强弱", r"wang_score",
        r"de_ling", r"de_di", r"de_shi", r"support_count", r"drain_count",
    ],
    "balance": [
        r"\bbalance\b", r"_balance\b", r"imbalance", r"五行平衡", r"五行计数",
        r"five_element", r"wuxing_count",
    ],
    "strong_weak": [
        r"\bstrong\b", r"\bweak\b", r"STRONG", r"WEAK", r"身强", r"身弱",
        r"rootless", r"spouse_star_strength",
    ],
}

# 已知的安全上下文（L1 Fact 或 Relationship，不是 Semantic Judgment）
SAFE_CONTEXTS = [
    "TIAN_GAN_TWELVE_GROWTH",  # 十二长生表
    "BRANCH_HIDDEN_STEMS",      # 藏干表
    "BRANCH_CLASH",              # 六冲表
    "BRANCH_HE",                 # 六合表
    "BRANCH_SANHE",              # 三合表
    "BRANCH_SANHUI",             # 三会表
    "BRANCH_SANXING",            # 三刑表
    "BRANCH_HARM",               # 六害表
    "STEM_HE",                   # 天干五合表
    "KONG_WANG",                 # 空亡表
    "STEM_ELEMENT",              # 天干五行表
    "STEM_POLARITY",             # 天干阴阳表
    "HEAVENLY_STEMS",            # 天干列表
    "EARTHLY_BRANCHES",          # 地支列表
    "PEACH_BLOSSOM",             # 桃花表
    "ROAD_BRANCH",               # 禄位表
    "ABSOLUTE_BRANCH",           # 帝旺位表
    "LONGHU_STAGE",              # 十二长生表（另一套）
    "TEN_GOD",                   # 十神表
    "ten_god",                   # 十神计算
    "_ten_god",                  # 十神计算
    "hidden_stem",               # 藏干计算
    "calc_hidden",               # 藏干计算
    "BRANCH_HIDDEN",             # 藏干表
    "fact_type",                 # 事实类型
    "L1_FACT",                   # L1 事实
    "Fact",                      # 事实类
    "TwelveGrowth",              # 十二长生事实
    "HiddenStem",                # 藏干事实
    "implementation_source",     # 实现来源标注
    "canonical_source_status",   # 原典来源状态
    "NOT_CANONICAL",             # 非原典来源标注
    "UNRESOLVED",                # 未解决状态
    "PARTIAL",                   # 部分授权状态
    "AUTHORIZED",                # 已授权状态
    "NOT_AUTHORIZED",            # 未授权状态
    "Relation Effect Modifier",  # 关系效应修正器
    "Strength Evidence",         # 强弱证据
]


def is_safe_context(line: str, context_lines: list) -> bool:
    """判断一行是否在安全上下文中（L1 Fact 或 Relationship 定义）"""
    full_context = "\n".join(context_lines[-5:] + [line])
    for safe in SAFE_CONTEXTS:
        if safe in full_context:
            return True
    return False


def scan_file(filepath: Path) -> dict:
    """扫描单个文件，返回发现的问题"""
    results = defaultdict(list)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        return {"error": str(e)}

    for i, line in enumerate(lines, 1):
        # 跳过注释行？不，注释也要检查，因为注释可能包含未授权的语义
        for category, patterns in SCAN_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # 检查是否在安全上下文中
                    context = lines[max(0, i-5):i]
                    if not is_safe_context(line, context):
                        results[category].append({
                            "line": i,
                            "content": line.strip()[:120],
                            "pattern": pattern,
                        })
                    break  # 一个类别只记录一次

    return dict(results)


def main():
    print("=" * 80)
    print("P0-2 全仓隐性评分扫描")
    print("=" * 80)
    print()

    all_results = {}
    total_files = 0
    files_with_issues = 0

    for root, dirs, files in os.walk(SRC_DIR):
        # 跳过 __pycache__
        if "__pycache__" in root:
            continue
        for filename in files:
            if not filename.endswith(".py"):
                continue
            filepath = Path(root) / filename
            total_files += 1
            rel_path = filepath.relative_to(SRC_DIR)

            results = scan_file(filepath)
            if results and "error" not in results:
                files_with_issues += 1
                all_results[str(rel_path)] = results
                issue_count = sum(len(v) for v in results.values())
                print(f"  ⚠️  {rel_path}: {issue_count} 个潜在问题")
                for cat, items in results.items():
                    print(f"      {cat}: {len(items)} 处")
            elif "error" in results:
                print(f"  ❌ {rel_path}: 读取错误 - {results['error']}")

    print()
    print("=" * 80)
    print(f"扫描完成：{total_files} 个 Python 文件，{files_with_issues} 个文件有潜在问题")
    print("=" * 80)

    # 保存详细结果
    output_path = Path(r"D:\shuntian\backend\docs\P0_2_hidden_scoring_scan_raw.json")
    import json
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\n详细结果已保存到: {output_path}")

    # 按类别统计
    print("\n" + "=" * 80)
    print("按问题类别统计")
    print("=" * 80)
    category_totals = defaultdict(int)
    for file_results in all_results.values():
        for cat, items in file_results.items():
            category_totals[cat] += len(items)

    for cat, count in sorted(category_totals.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count} 处")

    return all_results


if __name__ == "__main__":
    main()
