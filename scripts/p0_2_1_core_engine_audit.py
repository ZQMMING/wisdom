"""
P0-2.1 核心引擎深度审计

针对四个核心文件，提取所有 score/strength/threshold/weight 的具体代码行和上下文，
用于人工逐项归因：
- FALSE POSITIVE（误报：字段定义、测试、注释、数据结构）
- LEGACY（旧代码，已标记 Legacy）
- REAL POSITIVE（真正的未经授权评分路径）

核心目标：不是消灭 score，而是证明生产 Calculation Path 中不存在
未经授权的"评分 → 阈值 → 语义状态"链。
"""

import re
import json
from pathlib import Path
from collections import defaultdict

SRC_DIR = Path(r"D:\shuntian\backend\src")

# 四个核心文件
CORE_FILES = [
    "tongshu/engines/strength_engine.py",
    "tongshu/engines/bazi_engine.py",
    "tongshu/engines/annual_event_evaluator.py",
    "tongshu/engines/judgment_engine.py",
]

# 扫描模式（更精确）
SCAN_PATTERNS = {
    "score": [
        (r"\.score\b", "属性访问"),
        (r"score\s*=", "赋值"),
        (r"score\s*\+", "累加"),
        (r"score\s*-", "累减"),
        (r"def.*score", "函数定义"),
        (r"score_\w+", "变量名"),
        (r"\w+_score", "变量名"),
        (r"得分", "中文"),
        (r"评分", "中文"),
    ],
    "strength": [
        (r"\.strength\b", "属性访问"),
        (r"strength\s*=", "赋值"),
        (r"def.*strength", "函数定义"),
        (r"strength_\w+", "变量名"),
        (r"\w+_strength", "变量名"),
        (r"身强", "中文"),
        (r"身弱", "中文"),
        (r"强弱", "中文"),
    ],
    "threshold": [
        (r">=\s*\d", "大于等于阈值"),
        (r"<=\s*\d", "小于等于阈值"),
        (r">\s*\d", "大于阈值"),
        (r"<\s*\d", "小于阈值"),
        (r"threshold\s*=", "阈值赋值"),
        (r"THRESHOLD\s*=", "常量阈值"),
        (r"阈值", "中文"),
    ],
    "weight": [
        (r"\.weight\b", "属性访问"),
        (r"weight\s*=", "赋值"),
        (r"weighted", "加权"),
        (r"weight_\w+", "变量名"),
        (r"\w+_weight", "变量名"),
        (r"权重", "中文"),
        (r"加权", "中文"),
    ],
    "balance": [
        (r"\.balance\b", "属性访问"),
        (r"balance\s*=", "赋值"),
        (r"imbalance", "失衡"),
        (r"五行平衡", "中文"),
        (r"五行计数", "中文"),
    ],
}


def extract_context(lines: list, line_idx: int, context_size: int = 5) -> dict:
    """提取某一行的上下文"""
    start = max(0, line_idx - context_size)
    end = min(len(lines), line_idx + context_size + 1)
    return {
        "line_number": line_idx + 1,
        "content": lines[line_idx].strip()[:150],
        "before": [l.strip()[:100] for l in lines[start:line_idx]],
        "after": [l.strip()[:100] for l in lines[line_idx+1:end]],
    }


def classify_finding(filepath: str, finding: dict) -> str:
    """初步分类（人工审核前的自动初判）"""
    content = finding["content"].lower()
    before = " ".join(finding.get("before", [])).lower()
    after = " ".join(finding.get("after", [])).lower()
    full_context = before + " " + content + " " + after

    # Legacy 标记
    if "legacy" in full_context or "deprecated" in full_context or "old" in full_context:
        return "LIKELY_LEGACY"

    # 注释/文档
    if content.strip().startswith("#") or content.strip().startswith('"""') or content.strip().startswith("'''"):
        return "LIKELY_COMMENT"

    # 数据结构/字段定义
    if "dataclass" in before or "class " in before or "typing" in before or "optional" in content.lower():
        return "LIKELY_FIELD_DEFINITION"

    # 测试/验证
    if "test" in filepath.lower() or "assert" in full_context or "expected" in full_context:
        return "LIKELY_TEST"

    # 排序/优先级（可能是合法的）
    if "sort" in full_context or "rank" in full_context or "priority" in full_context:
        return "LIKELY_SORTING"

    # 默认：需要人工审核
    return "NEEDS_MANUAL_REVIEW"


def scan_file(filepath: Path) -> dict:
    """扫描单个核心文件"""
    results = defaultdict(list)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        return {"error": str(e)}

    for i, line in enumerate(lines):
        for category, patterns in SCAN_PATTERNS.items():
            for pattern, pattern_type in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    finding = extract_context(lines, i)
                    finding["pattern"] = pattern
                    finding["pattern_type"] = pattern_type
                    finding["initial_classification"] = classify_finding(str(filepath), finding)
                    results[category].append(finding)
                    break  # 一个类别只记录一次

    return dict(results)


def main():
    print("=" * 80)
    print("P0-2.1 核心引擎深度审计")
    print("=" * 80)
    print()

    all_results = {}
    total_findings = 0

    for rel_path in CORE_FILES:
        filepath = SRC_DIR / rel_path
        if not filepath.exists():
            print(f"  ❌ 文件不存在: {rel_path}")
            continue

        print(f"--- 扫描: {rel_path} ---")
        results = scan_file(filepath)
        if "error" in results:
            print(f"  ❌ 错误: {results['error']}")
            continue

        file_total = sum(len(v) for v in results.values())
        total_findings += file_total
        all_results[rel_path] = results

        print(f"  总计: {file_total} 处")
        for cat, items in results.items():
            # 按初步分类统计
            classifications = defaultdict(int)
            for item in items:
                classifications[item["initial_classification"]] += 1
            class_str = ", ".join(f"{k}:{v}" for k, v in classifications.items())
            print(f"    {cat}: {len(items)} 处 ({class_str})")
        print()

    print("=" * 80)
    print(f"四个核心文件总计: {total_findings} 处")
    print("=" * 80)

    # 保存详细结果
    output_path = Path(r"D:\shuntian\backend\docs\P0_2_1_core_engine_audit_raw.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\n详细结果已保存到: {output_path}")

    # 按初步分类汇总
    print("\n" + "=" * 80)
    print("按初步分类汇总（自动初判，需人工复核）")
    print("=" * 80)
    classification_totals = defaultdict(int)
    for file_results in all_results.values():
        for cat, items in file_results.items():
            for item in items:
                classification_totals[item["initial_classification"]] += 1

    for cls, count in sorted(classification_totals.items(), key=lambda x: -x[1]):
        print(f"  {cls}: {count} 处")

    return all_results


if __name__ == "__main__":
    main()
