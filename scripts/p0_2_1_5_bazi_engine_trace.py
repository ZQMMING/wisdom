"""
P0-2.1.5 生产路径确认 — bazi_engine.py 完整调用链与 Calculation Facts 数据血缘审计

目标：
1. 谁 import bazi_engine？
2. 谁调用了 calc_spouse_star_strength？
3. 谁调用了 calc_five_element_balance？
4. bazi_engine 到底产生哪些 Facts？
5. 这些 Facts 如何进入 Canonical State？
6. 哪些模块消费这些 Facts？
7. 给每个输出做分类：Calculation Fact vs Semantic State / 辨

审计尺度：
不是"有没有算法"，而是"这个算法究竟在生产什么数据、这个数据属于算还是辨、它有没有越过层级边界"。
"""

import os
import re
from pathlib import Path
from collections import defaultdict

SRC_DIR = Path(r"D:\shuntian\backend\src")


def find_imports(filepath: Path, module_name: str) -> list:
    """查找文件中对某模块的 import"""
    results = []
    patterns = [
        rf"import.*{module_name}",
        rf"from.*{module_name}.*import",
    ]
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        results.append({
                            "line": i,
                            "content": line.strip()[:150],
                            "pattern": pattern,
                        })
    except Exception:
        pass
    return results


def find_method_calls(filepath: Path, method_name: str) -> list:
    """查找某方法的调用"""
    results = []
    patterns = [
        rf"{method_name}\s*\(",
        rf"\.{method_name}\s*\(",
    ]
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        if "def " in line and method_name in line:
                            continue
                        if "import" in line or "from" in line:
                            continue
                        results.append({
                            "line": i,
                            "content": line.strip()[:150],
                            "pattern": pattern,
                        })
                        break
    except Exception:
        pass
    return results


def find_class_definitions(filepath: Path) -> list:
    """查找文件中的类定义"""
    results = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                match = re.search(r"class\s+(\w+)", line)
                if match:
                    results.append({
                        "line": i,
                        "class_name": match.group(1),
                        "content": line.strip()[:150],
                    })
    except Exception:
        pass
    return results


def find_method_definitions(filepath: Path) -> list:
    """查找文件中的方法定义"""
    results = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                match = re.search(r"def\s+(\w+)\s*\(", line)
                if match:
                    results.append({
                        "line": i,
                        "method": match.group(1),
                        "content": line.strip()[:150],
                    })
    except Exception:
        pass
    return results


def classify_file(filepath: Path) -> str:
    """分类文件"""
    path_str = str(filepath).lower()
    filename = filepath.name.lower()

    if "test" in path_str or "test" in filename:
        return "TEST"
    if "canonical" in path_str:
        return "CANONICAL"
    if "signal" in path_str:
        return "SIGNAL"
    if "router" in filename or "api" in path_str or "endpoint" in filename:
        return "API"
    if "engine" in path_str:
        return "ENGINE"
    if "legacy" in path_str:
        return "LEGACY"
    if "validation" in path_str or "audit" in path_str:
        return "VALIDATION"
    if "service" in path_str:
        return "SERVICE"
    if "pipeline" in path_str:
        return "PIPELINE"
    if "reasoning" in path_str:
        return "REASONING"
    if "admin" in path_str:
        return "ADMIN"
    if "judgment_architecture" in path_str:
        return "JUDGMENT_ARCH"
    return "OTHER"


def classify_method_output(method_name: str, method_content: str) -> dict:
    """
    给方法输出做分类：Calculation Fact vs Semantic State / 辨

    返回：
    - category: CALCULATION_FACT / SEMANTIC_STATE / MIXED / UNKNOWN
    - description: 分类说明
    - concerns: 需要关注的问题
    """
    name_lower = method_name.lower()
    content_lower = method_content.lower()

    # 明确的 Calculation Fact（纯事实计算）
    calculation_fact_keywords = [
        "pillar", "stem", "branch", "hidden", "ten_god", "wuxing", "element",
        "clash", "harm", "he", "sanhe", "sanhui", "sanxing", "kong_wang",
        "twelve", "growth", "longhu", "dayun", "liunian", "liuyue", "liuri",
        "ganzhi", "solar", "lunar", "calendar", "boundary",
        "四柱", "天干", "地支", "藏干", "十神", "五行",
        "冲", "害", "合", "三合", "三会", "三刑", "空亡",
        "十二长生", "大运", "流年", "流月", "流日",
    ]

    # 明确的 Semantic State / 辨（语义判断）
    semantic_state_keywords = [
        "strength", "weak", "strong", "wang", "shuai", "qiang", "ruo",
        "balance", "imbalance", "score", "weight", "threshold",
        "身强", "身弱", "旺衰", "强弱", "平衡", "失衡",
        "评分", "权重", "阈值",
        "spouse_star_strength", "five_element_balance",
    ]

    # 检查是否包含语义判断关键词
    has_semantic = any(kw in name_lower or kw in content_lower for kw in semantic_state_keywords)
    has_calculation = any(kw in name_lower or kw in content_lower for kw in calculation_fact_keywords)

    if has_semantic and has_calculation:
        return {
            "category": "MIXED",
            "description": "混合了 Calculation Fact 和 Semantic State，需要进一步审计是否越界",
            "concerns": ["可能存在 Fact → Judgment 的越界", "需要确认数值计算是否只是客观统计", "需要确认是否有人为权重/阈值"],
        }
    elif has_semantic:
        return {
            "category": "SEMANTIC_STATE",
            "description": "明确的 Semantic State / 辨，需要确认是否经过原典授权",
            "concerns": ["需要确认是否经过原典授权", "需要确认是否消费正确的 Calculation Facts", "需要确认是否越过层级边界"],
        }
    elif has_calculation:
        return {
            "category": "CALCULATION_FACT",
            "description": "明确的 Calculation Fact / 算，纯事实计算",
            "concerns": ["需要确认计算规则是否经过原典授权", "需要确认计算结果是否正确"],
        }
    else:
        return {
            "category": "UNKNOWN",
            "description": "无法自动分类，需要人工审计",
            "concerns": ["需要人工审计方法的输入、输出和语义"],
        }


def main():
    print("=" * 80)
    print("P0-2.1.5 生产路径确认 — bazi_engine.py 完整调用链与 Calculation Facts 数据血缘审计")
    print("=" * 80)
    print()

    # 第一步：bazi_engine.py 内部结构
    print("--- 第一步：bazi_engine.py 内部结构 ---")
    be_path = SRC_DIR / "tongshu/engines/bazi_engine.py"
    if be_path.exists():
        classes = find_class_definitions(be_path)
        methods = find_method_definitions(be_path)
        print(f"文件: {be_path}")
        print(f"类定义: {len(classes)} 个")
        for c in classes:
            print(f"  - {c['class_name']} (行 {c['line']})")
        print(f"\n方法定义: {len(methods)} 个")
        for m in methods:
            classification = classify_method_output(m['method'], m['content'])
            print(f"  - {m['method']} (行 {m['line']}) [{classification['category']}]")
            if classification['category'] in ['SEMANTIC_STATE', 'MIXED']:
                print(f"      ⚠️  {classification['description']}")
    else:
        print(f"❌ 文件不存在: {be_path}")
        classes = []
        methods = []
    print()

    # 第二步：谁 import 了 bazi_engine？
    print("--- 第二步：谁 import 了 bazi_engine？ ---")
    importers = defaultdict(list)
    for root, dirs, files in os.walk(SRC_DIR):
        if "__pycache__" in root:
            continue
        for filename in files:
            if not filename.endswith(".py"):
                continue
            filepath = Path(root) / filename
            if filepath == be_path:
                continue
            imports = find_imports(filepath, "bazi_engine")
            if imports:
                file_type = classify_file(filepath)
                rel_path = filepath.relative_to(SRC_DIR)
                importers[file_type].append({
                    "file": str(rel_path),
                    "imports": imports,
                })

    total_importers = sum(len(v) for v in importers.values())
    print(f"找到 {total_importers} 个文件 import 了 bazi_engine")
    for file_type, files in sorted(importers.items()):
        print(f"\n  [{file_type}] {len(files)} 个文件:")
        for f in files[:10]:
            print(f"    - {f['file']}")
            for imp in f['imports'][:2]:
                print(f"      行 {imp['line']}: {imp['content'][:80]}")
        if len(files) > 10:
            print(f"    ... 还有 {len(files) - 10} 个文件")
    print()

    # 第三步：calc_spouse_star_strength 调用链
    print("--- 第三步：calc_spouse_star_strength 调用链 ---")
    spouse_callers = defaultdict(list)
    for root, dirs, files in os.walk(SRC_DIR):
        if "__pycache__" in root:
            continue
        for filename in files:
            if not filename.endswith(".py"):
                continue
            filepath = Path(root) / filename
            calls = find_method_calls(filepath, "calc_spouse_star_strength")
            if calls:
                file_type = classify_file(filepath)
                rel_path = filepath.relative_to(SRC_DIR)
                spouse_callers[file_type].append({
                    "file": str(rel_path),
                    "calls": calls,
                })

    total_spouse = sum(len(v) for v in spouse_callers.items())
    print(f"找到 {total_spouse} 个文件调用了 calc_spouse_star_strength")
    for file_type, files in sorted(spouse_callers.items()):
        print(f"\n  [{file_type}] {len(files)} 个文件:")
        for f in files:
            print(f"    - {f['file']} ({len(f['calls'])} 处)")
            for call in f['calls'][:2]:
                print(f"      行 {call['line']}: {call['content'][:80]}")
    print()

    # 第四步：calc_five_element_balance 调用链
    print("--- 第四步：calc_five_element_balance 调用链 ---")
    balance_callers = defaultdict(list)
    for root, dirs, files in os.walk(SRC_DIR):
        if "__pycache__" in root:
            continue
        for filename in files:
            if not filename.endswith(".py"):
                continue
            filepath = Path(root) / filename
            calls = find_method_calls(filepath, "calc_five_element_balance")
            if calls:
                file_type = classify_file(filepath)
                rel_path = filepath.relative_to(SRC_DIR)
                balance_callers[file_type].append({
                    "file": str(rel_path),
                    "calls": calls,
                })

    total_balance = sum(len(v) for v in balance_callers.items())
    print(f"找到 {total_balance} 个文件调用了 calc_five_element_balance")
    for file_type, files in sorted(balance_callers.items()):
        print(f"\n  [{file_type}] {len(files)} 个文件:")
        for f in files:
            print(f"    - {f['file']} ({len(f['calls'])} 处)")
            for call in f['calls'][:2]:
                print(f"      行 {call['line']}: {call['content'][:80]}")
    print()

    # 第五步：BaziChart 类的使用情况（生产入口）
    print("--- 第五步：BaziChart 类的使用情况 ---")
    chart_callers = defaultdict(list)
    for root, dirs, files in os.walk(SRC_DIR):
        if "__pycache__" in root:
            continue
        for filename in files:
            if not filename.endswith(".py"):
                continue
            filepath = Path(root) / filename
            calls = find_method_calls(filepath, "BaziChart")
            if calls:
                file_type = classify_file(filepath)
                rel_path = filepath.relative_to(SRC_DIR)
                chart_callers[file_type].append({
                    "file": str(rel_path),
                    "calls": calls,
                })

    total_chart = sum(len(v) for v in chart_callers.items())
    print(f"找到 {total_chart} 个文件使用了 BaziChart")
    for file_type, files in sorted(chart_callers.items()):
        print(f"\n  [{file_type}] {len(files)} 个文件:")
        for f in files[:10]:
            print(f"    - {f['file']}")
        if len(files) > 10:
            print(f"    ... 还有 {len(files) - 10} 个文件")
    print()

    # 第六步：结果总结
    print("=" * 80)
    print("调用链与数据血缘追踪总结")
    print("=" * 80)
    print(f"1. bazi_engine.py 内部: {len(classes)} 个类, {len(methods)} 个方法")
    print(f"2. import bazi_engine 的文件: {total_importers} 个")
    print(f"3. calc_spouse_star_strength 调用文件: {total_spouse} 个")
    print(f"4. calc_five_element_balance 调用文件: {total_balance} 个")
    print(f"5. BaziChart 使用文件: {total_chart} 个")
    print()

    # 方法分类统计
    print("--- 方法输出分类统计 ---")
    category_counts = defaultdict(int)
    for m in methods:
        classification = classify_method_output(m['method'], m['content'])
        category_counts[classification['category']] += 1
    for cat, count in sorted(category_counts.items()):
        print(f"  {cat}: {count} 个方法")
    print()

    # 判断是否进入 Canonical / Signal / API
    print("--- 是否进入 Canonical / Signal / API？ ---")
    canonical_importers = importers.get("CANONICAL", [])
    signal_importers = importers.get("SIGNAL", [])
    api_importers = importers.get("API", [])
    service_importers = importers.get("SERVICE", [])
    pipeline_importers = importers.get("PIPELINE", [])
    reasoning_importers = importers.get("REASONING", [])
    admin_importers = importers.get("ADMIN", [])

    print(f"  Canonical 层 import: {len(canonical_importers)} 个文件")
    print(f"  Signal 层 import: {len(signal_importers)} 个文件")
    print(f"  API 层 import: {len(api_importers)} 个文件")
    print(f"  Service 层 import: {len(service_importers)} 个文件")
    print(f"  Pipeline 层 import: {len(pipeline_importers)} 个文件")
    print(f"  Reasoning 层 import: {len(reasoning_importers)} 个文件")
    print(f"  Admin 层 import: {len(admin_importers)} 个文件")
    print()

    # 保存详细结果
    output = {
        "bazi_engine_internal": {
            "classes": classes,
            "methods": methods,
            "method_classifications": [
                {**m, **classify_method_output(m['method'], m['content'])}
                for m in methods
            ],
        },
        "importers": {k: v for k, v in importers.items()},
        "spouse_star_strength_callers": {k: v for k, v in spouse_callers.items()},
        "five_element_balance_callers": {k: v for k, v in balance_callers.items()},
        "bazichart_usage": {k: v for k, v in chart_callers.items()},
        "summary": {
            "total_importers": total_importers,
            "total_spouse_callers": total_spouse,
            "total_balance_callers": total_balance,
            "total_chart_usage": total_chart,
            "canonical_importers": len(canonical_importers),
            "signal_importers": len(signal_importers),
            "api_importers": len(api_importers),
            "service_importers": len(service_importers),
            "pipeline_importers": len(pipeline_importers),
            "reasoning_importers": len(reasoning_importers),
            "admin_importers": len(admin_importers),
            "method_category_counts": dict(category_counts),
        },
    }

    output_path = Path(r"D:\shuntian\backend\docs\P0_2_1_5_bazi_engine_trace.json")
    import json
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"详细结果已保存到: {output_path}")

    return output


if __name__ == "__main__":
    main()
