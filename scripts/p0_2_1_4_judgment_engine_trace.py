"""
P0-2.1.4 生产路径确认 — judgment_engine.py 完整调用链与 D1StrengthResult 数据血缘

目标：回答以下问题
1. 谁 import judgment_engine？
2. 谁调用 judgment_engine 的核心方法？
3. D1StrengthResult 到底怎么来的？在哪里创建？在哪里传递？在哪里消费？
4. 有没有 evaluate_strength() 调用（直接或间接）？
5. judgment_engine 的结果是什么？
6. 进入 Canonical？Signal？API？
7. 对象生命周期追踪：D1StrengthResult 从创建到消费的完整路径

特别关注：不能只搜索 evaluate_strength()，必须把对象生命周期追完。
"""

import os
import re
import ast
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


def find_class_instantiations(filepath: Path, class_name: str) -> list:
    """查找某类的实例化位置（对象创建点）"""
    results = []
    patterns = [
        rf"{class_name}\s*\(",
        rf"=\s*{class_name}\s*\(",
    ]
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        # 排除 import 行和定义行
                        if "import" in line or "from" in line or "class " in line:
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


def find_object_usage(filepath: Path, object_patterns: list) -> list:
    """查找对象的属性访问和方法调用（对象消费点）"""
    results = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                for pattern in object_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        results.append({
                            "line": i,
                            "content": line.strip()[:150],
                            "pattern": pattern,
                        })
                        break
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
                        # 排除定义行和 import 行
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


def find_return_types(filepath: Path) -> list:
    """查找函数的返回类型注解"""
    results = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                if "->" in line and "def " in line:
                    results.append({
                        "line": i,
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
    return "OTHER"


def main():
    print("=" * 80)
    print("P0-2.1.4 生产路径确认 — judgment_engine.py 完整调用链与 D1StrengthResult 数据血缘")
    print("=" * 80)
    print()

    # 第一步：judgment_engine.py 内部结构
    print("--- 第一步：judgment_engine.py 内部结构 ---")
    je_path = SRC_DIR / "tongshu/engines/judgment_engine.py"
    if je_path.exists():
        classes = find_class_definitions(je_path)
        methods = find_method_definitions(je_path)
        return_types = find_return_types(je_path)
        print(f"文件: {je_path}")
        print(f"类定义: {len(classes)} 个")
        for c in classes:
            print(f"  - {c['class_name']} (行 {c['line']})")
        print(f"方法定义: {len(methods)} 个")
        for m in methods[:20]:
            print(f"  - {m['method']} (行 {m['line']})")
        if len(methods) > 20:
            print(f"  ... 还有 {len(methods) - 20} 个方法")
        print(f"返回类型注解: {len(return_types)} 个")
        for rt in return_types[:10]:
            print(f"  行 {rt['line']}: {rt['content'][:100]}")
    else:
        print(f"❌ 文件不存在: {je_path}")
        classes = []
        methods = []
        return_types = []
    print()

    # 第二步：谁 import 了 judgment_engine？
    print("--- 第二步：谁 import 了 judgment_engine？ ---")
    importers = defaultdict(list)
    for root, dirs, files in os.walk(SRC_DIR):
        if "__pycache__" in root:
            continue
        for filename in files:
            if not filename.endswith(".py"):
                continue
            filepath = Path(root) / filename
            if filepath == je_path:
                continue
            imports = find_imports(filepath, "judgment_engine")
            if imports:
                file_type = classify_file(filepath)
                rel_path = filepath.relative_to(SRC_DIR)
                importers[file_type].append({
                    "file": str(rel_path),
                    "imports": imports,
                })

    total_importers = sum(len(v) for v in importers.values())
    print(f"找到 {total_importers} 个文件 import 了 judgment_engine")
    for file_type, files in sorted(importers.items()):
        print(f"\n  [{file_type}] {len(files)} 个文件:")
        for f in files:
            print(f"    - {f['file']}")
            for imp in f['imports'][:3]:
                print(f"      行 {imp['line']}: {imp['content'][:80]}")
    print()

    # 第三步：D1StrengthResult 数据血缘追踪
    print("--- 第三步：D1StrengthResult 数据血缘追踪 ---")

    # 3.1 D1StrengthResult 在哪里被 import？
    print("\n  3.1 D1StrengthResult 在哪里被 import？")
    d1_importers = defaultdict(list)
    for root, dirs, files in os.walk(SRC_DIR):
        if "__pycache__" in root:
            continue
        for filename in files:
            if not filename.endswith(".py"):
                continue
            filepath = Path(root) / filename
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f, 1):
                        if "D1StrengthResult" in line and ("import" in line or "from" in line):
                            file_type = classify_file(filepath)
                            rel_path = filepath.relative_to(SRC_DIR)
                            d1_importers[file_type].append({
                                "file": str(rel_path),
                                "line": i,
                                "content": line.strip()[:150],
                            })
                            break
            except Exception:
                pass

    total_d1_importers = sum(len(v) for v in d1_importers.items())
    print(f"    找到 {total_d1_importers} 个文件 import 了 D1StrengthResult")
    for file_type, files in sorted(d1_importers.items()):
        print(f"      [{file_type}] {len(files)} 个文件:")
        for f in files:
            print(f"        - {f['file']} (行 {f['line']})")

    # 3.2 D1StrengthResult 在哪里被实例化（创建点）？
    print("\n  3.2 D1StrengthResult 在哪里被实例化（创建点）？")
    d1_instantiations = defaultdict(list)
    for root, dirs, files in os.walk(SRC_DIR):
        if "__pycache__" in root:
            continue
        for filename in files:
            if not filename.endswith(".py"):
                continue
            filepath = Path(root) / filename
            instantiations = find_class_instantiations(filepath, "D1StrengthResult")
            if instantiations:
                file_type = classify_file(filepath)
                rel_path = filepath.relative_to(SRC_DIR)
                d1_instantiations[file_type].append({
                    "file": str(rel_path),
                    "instantiations": instantiations,
                })

    total_d1_instantiations = sum(len(v) for v in d1_instantiations.items())
    print(f"    找到 {total_d1_instantiations} 个文件实例化了 D1StrengthResult")
    for file_type, files in sorted(d1_instantiations.items()):
        print(f"      [{file_type}] {len(files)} 个文件:")
        for f in files:
            print(f"        - {f['file']} ({len(f['instantiations'])} 处)")
            for inst in f['instantiations'][:2]:
                print(f"          行 {inst['line']}: {inst['content'][:80]}")

    # 3.3 evaluate_strength 在哪里被调用？
    print("\n  3.3 evaluate_strength 在哪里被调用？")
    es_callers = defaultdict(list)
    for root, dirs, files in os.walk(SRC_DIR):
        if "__pycache__" in root:
            continue
        for filename in files:
            if not filename.endswith(".py"):
                continue
            filepath = Path(root) / filename
            calls = find_method_calls(filepath, "evaluate_strength")
            if calls:
                file_type = classify_file(filepath)
                rel_path = filepath.relative_to(SRC_DIR)
                es_callers[file_type].append({
                    "file": str(rel_path),
                    "calls": calls,
                })

    total_es_callers = sum(len(v) for v in es_callers.items())
    print(f"    找到 {total_es_callers} 个文件调用了 evaluate_strength")
    for file_type, files in sorted(es_callers.items()):
        print(f"      [{file_type}] {len(files)} 个文件:")
        for f in files:
            print(f"        - {f['file']} ({len(f['calls'])} 处)")
            for call in f['calls'][:2]:
                print(f"          行 {call['line']}: {call['content'][:80]}")

    # 第四步：judgment_engine 的核心方法调用情况
    print("\n--- 第四步：judgment_engine 核心方法调用情况 ---")
    # 从 judgment_engine 的方法定义中提取核心方法名
    core_methods = [m['method'] for m in methods if m['method'] not in ['__init__', '__str__', '__repr__']]
    # 只追踪前 10 个核心方法
    for method in core_methods[:10]:
        callers = defaultdict(list)
        for root, dirs, files in os.walk(SRC_DIR):
            if "__pycache__" in root:
                continue
            for filename in files:
                if not filename.endswith(".py"):
                    continue
                filepath = Path(root) / filename
                if filepath == je_path:
                    continue
                calls = find_method_calls(filepath, method)
                if calls:
                    file_type = classify_file(filepath)
                    rel_path = filepath.relative_to(SRC_DIR)
                    callers[file_type].append({
                        "file": str(rel_path),
                        "calls": calls,
                    })
        total = sum(len(v) for v in callers.values())
        if total > 0:
            print(f"\n  {method}: {total} 个文件调用")
            for file_type, files in sorted(callers.items()):
                print(f"    [{file_type}] {len(files)} 个文件:")
                for f in files[:3]:
                    print(f"      - {f['file']}")

    # 第五步：结果总结
    print("\n" + "=" * 80)
    print("调用链与数据血缘追踪总结")
    print("=" * 80)
    print(f"1. judgment_engine.py 内部: {len(classes)} 个类, {len(methods)} 个方法")
    print(f"2. import judgment_engine 的文件: {total_importers} 个")
    print(f"3. D1StrengthResult import 文件: {total_d1_importers} 个")
    print(f"4. D1StrengthResult 实例化文件: {total_d1_instantiations} 个")
    print(f"5. evaluate_strength 调用文件: {total_es_callers} 个")
    print()

    # 判断是否进入 Canonical / Signal / API
    print("--- 是否进入 Canonical / Signal / API？ ---")
    canonical_importers = importers.get("CANONICAL", [])
    signal_importers = importers.get("SIGNAL", [])
    api_importers = importers.get("API", [])
    service_importers = importers.get("SERVICE", [])
    pipeline_importers = importers.get("PIPELINE", [])
    reasoning_importers = importers.get("REASONING", [])

    print(f"  Canonical 层 import: {len(canonical_importers)} 个文件")
    print(f"  Signal 层 import: {len(signal_importers)} 个文件")
    print(f"  API 层 import: {len(api_importers)} 个文件")
    print(f"  Service 层 import: {len(service_importers)} 个文件")
    print(f"  Pipeline 层 import: {len(pipeline_importers)} 个文件")
    print(f"  Reasoning 层 import: {len(reasoning_importers)} 个文件")
    print()

    # 保存详细结果
    output = {
        "judgment_engine_internal": {
            "classes": classes,
            "methods": methods,
            "return_types": return_types,
        },
        "importers": {k: v for k, v in importers.items()},
        "d1_strength_result_lineage": {
            "importers": {k: v for k, v in d1_importers.items()},
            "instantiations": {k: v for k, v in d1_instantiations.items()},
        },
        "evaluate_strength_callers": {k: v for k, v in es_callers.items()},
        "summary": {
            "total_importers": total_importers,
            "total_d1_importers": total_d1_importers,
            "total_d1_instantiations": total_d1_instantiations,
            "total_es_callers": total_es_callers,
            "canonical_importers": len(canonical_importers),
            "signal_importers": len(signal_importers),
            "api_importers": len(api_importers),
            "service_importers": len(service_importers),
            "pipeline_importers": len(pipeline_importers),
            "reasoning_importers": len(reasoning_importers),
        },
    }

    output_path = Path(r"D:\shuntian\backend\docs\P0_2_1_4_judgment_engine_trace.json")
    import json
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"详细结果已保存到: {output_path}")

    return output


if __name__ == "__main__":
    main()
