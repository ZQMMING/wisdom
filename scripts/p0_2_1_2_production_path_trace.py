"""
P0-2.1.2 生产路径确认 — annual_event_evaluator.py 完整调用链追踪

目标：回答以下问题
1. 谁 import annual_event_evaluator？
2. 谁调用 evaluate_case？
3. 谁调用 combine_signals？
4. score_disaster / score_wealth 从哪里来？
5. 结果进入哪里？
6. 有没有进入 Canonical？
7. 有没有进入 Signal？
8. 有没有进入 API？

只有把这个链追完，才能裁决它是 Legacy、测试代码，还是生产污染源。
"""

import os
import re
from pathlib import Path
from collections import defaultdict

SRC_DIR = Path(r"D:\shuntian\backend\src")

# 追踪目标
TARGETS = {
    "annual_event_evaluator": {
        "import_patterns": [
            r"import.*annual_event_evaluator",
            r"from.*annual_event_evaluator.*import",
        ],
        "class_patterns": [
            r"class\s+(\w*AnnualEvent\w*)",
            r"class\s+(\w*EventEvaluator\w*)",
        ],
        "method_patterns": [
            r"def\s+(evaluate_case)\s*\(",
            r"def\s+(combine_signals)\s*\(",
            r"def\s+(score_disaster)\s*\(",
            r"def\s+(score_wealth)\s*\(",
        ],
    },
    "combine_signals": {
        "call_patterns": [
            r"combine_signals\s*\(",
            r"\.combine_signals\s*\(",
        ],
    },
    "evaluate_case": {
        "call_patterns": [
            r"evaluate_case\s*\(",
            r"\.evaluate_case\s*\(",
        ],
    },
    "score_disaster": {
        "call_patterns": [
            r"score_disaster\s*\(",
            r"\.score_disaster\s*\(",
        ],
    },
    "score_wealth": {
        "call_patterns": [
            r"score_wealth\s*\(",
            r"\.score_wealth\s*\(",
        ],
    },
}

# Canonical / Signal / API 相关文件
CANONICAL_PATTERNS = [
    r"canonical",
    r"CanonicalState",
    r"canonical_state",
]

SIGNAL_PATTERNS = [
    r"signal",
    r"SemanticSignal",
    r"semantic_signal",
]

API_PATTERNS = [
    r"router",
    r"api",
    r"endpoint",
    r"@app\.",
    r"@router\.",
]


def find_imports(filepath: Path, target: str) -> list:
    """查找文件中对目标的 import"""
    results = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                for pattern in TARGETS[target].get("import_patterns", []):
                    if re.search(pattern, line, re.IGNORECASE):
                        results.append({
                            "line": i,
                            "content": line.strip()[:150],
                            "pattern": pattern,
                        })
    except Exception:
        pass
    return results


def find_calls(filepath: Path, target: str) -> list:
    """查找文件中对目标方法的调用"""
    results = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                for pattern in TARGETS[target].get("call_patterns", []):
                    if re.search(pattern, line, re.IGNORECASE):
                        # 排除定义行
                        if "def " in line and target in line:
                            continue
                        results.append({
                            "line": i,
                            "content": line.strip()[:150],
                            "pattern": pattern,
                        })
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
    """查找文件中的方法定义（特别是 score_disaster, score_wealth, combine_signals）"""
    results = []
    target_methods = ["score_disaster", "score_wealth", "combine_signals", "evaluate_case"]
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                for method in target_methods:
                    if re.search(rf"def\s+{method}\s*\(", line):
                        results.append({
                            "line": i,
                            "method": method,
                            "content": line.strip()[:150],
                        })
    except Exception:
        pass
    return results


def classify_file(filepath: Path) -> str:
    """分类文件：Canonical / Signal / API / Engine / Test / Other"""
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
    return "OTHER"


def main():
    print("=" * 80)
    print("P0-2.1.2 生产路径确认 — annual_event_evaluator.py 完整调用链追踪")
    print("=" * 80)
    print()

    # 第一步：找到 annual_event_evaluator.py 中的类和方法定义
    print("--- 第一步：annual_event_evaluator.py 内部结构 ---")
    aee_path = SRC_DIR / "tongshu/engines/annual_event_evaluator.py"
    if aee_path.exists():
        classes = find_class_definitions(aee_path)
        methods = find_method_definitions(aee_path)
        print(f"文件: {aee_path}")
        print(f"类定义: {len(classes)} 个")
        for c in classes:
            print(f"  - {c['class_name']} (行 {c['line']})")
        print(f"目标方法定义: {len(methods)} 个")
        for m in methods:
            print(f"  - {m['method']} (行 {m['line']})")
    else:
        print(f"❌ 文件不存在: {aee_path}")
    print()

    # 第二步：全仓搜索谁 import 了 annual_event_evaluator
    print("--- 第二步：谁 import 了 annual_event_evaluator？ ---")
    importers = defaultdict(list)
    for root, dirs, files in os.walk(SRC_DIR):
        if "__pycache__" in root:
            continue
        for filename in files:
            if not filename.endswith(".py"):
                continue
            filepath = Path(root) / filename
            if filepath == aee_path:
                continue
            imports = find_imports(filepath, "annual_event_evaluator")
            if imports:
                file_type = classify_file(filepath)
                rel_path = filepath.relative_to(SRC_DIR)
                importers[file_type].append({
                    "file": str(rel_path),
                    "imports": imports,
                })

    total_importers = sum(len(v) for v in importers.values())
    print(f"找到 {total_importers} 个文件 import 了 annual_event_evaluator")
    for file_type, files in sorted(importers.items()):
        print(f"\n  [{file_type}] {len(files)} 个文件:")
        for f in files:
            print(f"    - {f['file']}")
            for imp in f['imports'][:2]:
                print(f"      行 {imp['line']}: {imp['content'][:80]}")
    print()

    # 第三步：全仓搜索谁调用了 evaluate_case
    print("--- 第三步：谁调用了 evaluate_case？ ---")
    evaluate_callers = defaultdict(list)
    for root, dirs, files in os.walk(SRC_DIR):
        if "__pycache__" in root:
            continue
        for filename in files:
            if not filename.endswith(".py"):
                continue
            filepath = Path(root) / filename
            calls = find_calls(filepath, "evaluate_case")
            if calls:
                file_type = classify_file(filepath)
                rel_path = filepath.relative_to(SRC_DIR)
                evaluate_callers[file_type].append({
                    "file": str(rel_path),
                    "calls": calls,
                })

    total_callers = sum(len(v) for v in evaluate_callers.values())
    print(f"找到 {total_callers} 个文件调用了 evaluate_case")
    for file_type, files in sorted(evaluate_callers.items()):
        print(f"\n  [{file_type}] {len(files)} 个文件:")
        for f in files:
            print(f"    - {f['file']} ({len(f['calls'])} 处调用)")
            for call in f['calls'][:2]:
                print(f"      行 {call['line']}: {call['content'][:80]}")
    print()

    # 第四步：全仓搜索谁调用了 combine_signals
    print("--- 第四步：谁调用了 combine_signals？ ---")
    combine_callers = defaultdict(list)
    for root, dirs, files in os.walk(SRC_DIR):
        if "__pycache__" in root:
            continue
        for filename in files:
            if not filename.endswith(".py"):
                continue
            filepath = Path(root) / filename
            calls = find_calls(filepath, "combine_signals")
            if calls:
                file_type = classify_file(filepath)
                rel_path = filepath.relative_to(SRC_DIR)
                combine_callers[file_type].append({
                    "file": str(rel_path),
                    "calls": calls,
                })

    total_combine = sum(len(v) for v in combine_callers.values())
    print(f"找到 {total_combine} 个文件调用了 combine_signals")
    for file_type, files in sorted(combine_callers.items()):
        print(f"\n  [{file_type}] {len(files)} 个文件:")
        for f in files:
            print(f"    - {f['file']} ({len(f['calls'])} 处调用)")
            for call in f['calls'][:2]:
                print(f"      行 {call['line']}: {call['content'][:80]}")
    print()

    # 第五步：score_disaster / score_wealth 定义在哪里？
    print("--- 第五步：score_disaster / score_wealth 定义在哪里？ ---")
    score_definitions = defaultdict(list)
    for root, dirs, files in os.walk(SRC_DIR):
        if "__pycache__" in root:
            continue
        for filename in files:
            if not filename.endswith(".py"):
                continue
            filepath = Path(root) / filename
            methods = find_method_definitions(filepath)
            if methods:
                file_type = classify_file(filepath)
                rel_path = filepath.relative_to(SRC_DIR)
                score_definitions[file_type].append({
                    "file": str(rel_path),
                    "methods": methods,
                })

    total_score_defs = sum(len(v) for v in score_definitions.values())
    print(f"找到 {total_score_defs} 个文件定义了 score_disaster/score_wealth/combine_signals/evaluate_case")
    for file_type, files in sorted(score_definitions.items()):
        print(f"\n  [{file_type}] {len(files)} 个文件:")
        for f in files:
            print(f"    - {f['file']}")
            for m in f['methods']:
                print(f"      行 {m['line']}: def {m['method']}")
    print()

    # 第六步：结果总结
    print("=" * 80)
    print("调用链追踪总结")
    print("=" * 80)
    print(f"1. annual_event_evaluator.py 内部: {len(classes)} 个类, {len(methods)} 个目标方法")
    print(f"2. import annual_event_evaluator 的文件: {total_importers} 个")
    print(f"3. 调用 evaluate_case 的文件: {total_callers} 个")
    print(f"4. 调用 combine_signals 的文件: {total_combine} 个")
    print(f"5. 定义 score_disaster/score_wealth 的文件: {total_score_defs} 个")
    print()

    # 判断是否进入 Canonical / Signal / API
    print("--- 是否进入 Canonical / Signal / API？ ---")
    canonical_importers = importers.get("CANONICAL", [])
    signal_importers = importers.get("SIGNAL", [])
    api_importers = importers.get("API", [])
    canonical_callers = evaluate_callers.get("CANONICAL", []) + combine_callers.get("CANONICAL", [])
    signal_callers = evaluate_callers.get("SIGNAL", []) + combine_callers.get("SIGNAL", [])
    api_callers = evaluate_callers.get("API", []) + combine_callers.get("API", [])

    print(f"  Canonical 层 import: {len(canonical_importers)} 个文件")
    print(f"  Signal 层 import: {len(signal_importers)} 个文件")
    print(f"  API 层 import: {len(api_importers)} 个文件")
    print(f"  Canonical 层调用: {len(canonical_callers)} 个文件")
    print(f"  Signal 层调用: {len(signal_callers)} 个文件")
    print(f"  API 层调用: {len(api_callers)} 个文件")
    print()

    # 保存详细结果
    output = {
        "annual_event_evaluator_internal": {
            "classes": classes,
            "methods": methods,
        },
        "importers": {k: v for k, v in importers.items()},
        "evaluate_case_callers": {k: v for k, v in evaluate_callers.items()},
        "combine_signals_callers": {k: v for k, v in combine_callers.items()},
        "score_definitions": {k: v for k, v in score_definitions.items()},
        "summary": {
            "total_importers": total_importers,
            "total_evaluate_case_callers": total_callers,
            "total_combine_signals_callers": total_combine,
            "total_score_definition_files": total_score_defs,
            "canonical_importers": len(canonical_importers),
            "signal_importers": len(signal_importers),
            "api_importers": len(api_importers),
            "canonical_callers": len(canonical_callers),
            "signal_callers": len(signal_callers),
            "api_callers": len(api_callers),
        },
    }

    output_path = Path(r"D:\shuntian\backend\docs\P0_2_1_2_production_path_trace.json")
    import json
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"详细结果已保存到: {output_path}")

    return output


if __name__ == "__main__":
    main()
