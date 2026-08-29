"""
P0-2.1.3 生产路径确认 — strength_engine.py 完整调用链追踪

目标：回答以下问题
1. 谁 import strength_engine？
2. 谁调用 calc_strength / wang_score / de_ling / de_di / de_shi？
3. 结果进入哪里？
4. 有没有进入 Canonical？
5. 有没有进入 Signal？
6. 有没有进入 API？
7. 还是只是 Legacy / Test？

不先入为主地判它对错，只追真实数据流。
"""

import os
import re
from pathlib import Path
from collections import defaultdict

SRC_DIR = Path(r"D:\shuntian\backend\src")

# strength_engine.py 的核心方法/属性
CORE_METHODS = [
    "calc_strength",
    "wang_score",
    "de_ling",
    "de_di",
    "de_shi",
    "support_count",
    "drain_count",
    "de_ling_weight",
    "de_di_weighted",
    "WANG_SCORE_THRESHOLD",
    "StrengthEngine",
    "strength_engine",
]


def find_imports(filepath: Path) -> list:
    """查找文件中对 strength_engine 的 import"""
    results = []
    patterns = [
        r"import.*strength_engine",
        r"from.*strength_engine.*import",
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


def find_method_calls(filepath: Path, method: str) -> list:
    """查找文件中对某方法的调用"""
    results = []
    patterns = [
        rf"{method}\s*\(",
        rf"\.{method}\s*\(",
        rf"{method}\s*=",
        rf"\.{method}\s*=",
    ]
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        # 排除定义行
                        if "def " in line and method in line:
                            continue
                        # 排除 import 行
                        if "import" in line or "from" in line:
                            continue
                        results.append({
                            "line": i,
                            "content": line.strip()[:150],
                            "pattern": pattern,
                        })
                        break  # 一个方法只记录一次
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
                    method_name = match.group(1)
                    # 只记录核心方法
                    if any(core in method_name.lower() for core in ["strength", "wang", "score", "de_", "support", "drain"]):
                        results.append({
                            "line": i,
                            "method": method_name,
                            "content": line.strip()[:150],
                        })
    except Exception:
        pass
    return results


def classify_file(filepath: Path) -> str:
    """分类文件：Canonical / Signal / API / Engine / Test / Legacy / Other"""
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
    return "OTHER"


def main():
    print("=" * 80)
    print("P0-2.1.3 生产路径确认 — strength_engine.py 完整调用链追踪")
    print("=" * 80)
    print()

    # 第一步：找到 strength_engine.py 中的类和方法定义
    print("--- 第一步：strength_engine.py 内部结构 ---")
    se_path = SRC_DIR / "tongshu/engines/strength_engine.py"
    if se_path.exists():
        classes = find_class_definitions(se_path)
        methods = find_method_definitions(se_path)
        print(f"文件: {se_path}")
        print(f"类定义: {len(classes)} 个")
        for c in classes:
            print(f"  - {c['class_name']} (行 {c['line']})")
        print(f"核心方法定义: {len(methods)} 个")
        for m in methods:
            print(f"  - {m['method']} (行 {m['line']})")
    else:
        print(f"❌ 文件不存在: {se_path}")
        classes = []
        methods = []
    print()

    # 第二步：全仓搜索谁 import 了 strength_engine
    print("--- 第二步：谁 import 了 strength_engine？ ---")
    importers = defaultdict(list)
    for root, dirs, files in os.walk(SRC_DIR):
        if "__pycache__" in root:
            continue
        for filename in files:
            if not filename.endswith(".py"):
                continue
            filepath = Path(root) / filename
            if filepath == se_path:
                continue
            imports = find_imports(filepath)
            if imports:
                file_type = classify_file(filepath)
                rel_path = filepath.relative_to(SRC_DIR)
                importers[file_type].append({
                    "file": str(rel_path),
                    "imports": imports,
                })

    total_importers = sum(len(v) for v in importers.values())
    print(f"找到 {total_importers} 个文件 import 了 strength_engine")
    for file_type, files in sorted(importers.items()):
        print(f"\n  [{file_type}] {len(files)} 个文件:")
        for f in files:
            print(f"    - {f['file']}")
            for imp in f['imports'][:3]:
                print(f"      行 {imp['line']}: {imp['content'][:80]}")
    print()

    # 第三步：全仓搜索谁调用了核心方法
    print("--- 第三步：谁调用了核心方法？ ---")
    method_callers = {}
    for method in CORE_METHODS:
        callers = defaultdict(list)
        for root, dirs, files in os.walk(SRC_DIR):
            if "__pycache__" in root:
                continue
            for filename in files:
                if not filename.endswith(".py"):
                    continue
                filepath = Path(root) / filename
                if filepath == se_path:
                    continue
                calls = find_method_calls(filepath, method)
                if calls:
                    file_type = classify_file(filepath)
                    rel_path = filepath.relative_to(SRC_DIR)
                    callers[file_type].append({
                        "file": str(rel_path),
                        "calls": calls,
                    })
        total_callers = sum(len(v) for v in callers.values())
        method_callers[method] = {
            "total": total_callers,
            "callers": dict(callers),
        }
        if total_callers > 0:
            print(f"\n  {method}: {total_callers} 个文件调用")
            for file_type, files in sorted(callers.items()):
                print(f"    [{file_type}] {len(files)} 个文件:")
                for f in files[:5]:
                    print(f"      - {f['file']} ({len(f['calls'])} 处)")
                    for call in f['calls'][:1]:
                        print(f"        行 {call['line']}: {call['content'][:60]}")
    print()

    # 第四步：结果总结
    print("=" * 80)
    print("调用链追踪总结")
    print("=" * 80)
    print(f"1. strength_engine.py 内部: {len(classes)} 个类, {len(methods)} 个核心方法")
    print(f"2. import strength_engine 的文件: {total_importers} 个")
    print(f"3. 核心方法调用情况:")
    for method, data in method_callers.items():
        if data["total"] > 0:
            print(f"   - {method}: {data['total']} 个文件调用")
    print()

    # 判断是否进入 Canonical / Signal / API
    print("--- 是否进入 Canonical / Signal / API？ ---")
    canonical_importers = importers.get("CANONICAL", [])
    signal_importers = importers.get("SIGNAL", [])
    api_importers = importers.get("API", [])
    service_importers = importers.get("SERVICE", [])
    pipeline_importers = importers.get("PIPELINE", [])

    canonical_callers = 0
    signal_callers = 0
    api_callers = 0
    for method, data in method_callers.items():
        canonical_callers += len(data["callers"].get("CANONICAL", []))
        signal_callers += len(data["callers"].get("SIGNAL", []))
        api_callers += len(data["callers"].get("API", []))

    print(f"  Canonical 层 import: {len(canonical_importers)} 个文件")
    print(f"  Signal 层 import: {len(signal_importers)} 个文件")
    print(f"  API 层 import: {len(api_importers)} 个文件")
    print(f"  Service 层 import: {len(service_importers)} 个文件")
    print(f"  Pipeline 层 import: {len(pipeline_importers)} 个文件")
    print(f"  Canonical 层调用: {canonical_callers} 处")
    print(f"  Signal 层调用: {signal_callers} 处")
    print(f"  API 层调用: {api_callers} 处")
    print()

    # 保存详细结果
    output = {
        "strength_engine_internal": {
            "classes": classes,
            "methods": methods,
        },
        "importers": {k: v for k, v in importers.items()},
        "method_callers": method_callers,
        "summary": {
            "total_importers": total_importers,
            "canonical_importers": len(canonical_importers),
            "signal_importers": len(signal_importers),
            "api_importers": len(api_importers),
            "service_importers": len(service_importers),
            "pipeline_importers": len(pipeline_importers),
            "canonical_callers": canonical_callers,
            "signal_callers": signal_callers,
            "api_callers": api_callers,
        },
    }

    output_path = Path(r"D:\shuntian\backend\docs\P0_2_1_3_strength_engine_trace.json")
    import json
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"详细结果已保存到: {output_path}")

    return output


if __name__ == "__main__":
    main()
