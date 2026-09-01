#!/usr/bin/env python3
"""案例验证脚本 - 验证案例格式和完整性"""

import json
import sys
from pathlib import Path
from datetime import datetime


def validate_case_file(filepath: Path) -> dict:
    """验证单个案例文件"""
    errors = []
    warnings = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return {
            "file": str(filepath),
            "valid": False,
            "errors": [f"JSON解析错误: {e}"],
            "warnings": []
        }
    except Exception as e:
        return {
            "file": str(filepath),
            "valid": False,
            "errors": [f"文件读取错误: {e}"],
            "warnings": []
        }
    
    # 必需字段检查
    required_fields = ["case_id", "type", "birth_date", "events"]
    for field in required_fields:
        if field not in data:
            errors.append(f"缺少必需字段: {field}")
    
    # 事件格式检查
    if "events" in data:
        for i, event in enumerate(data["events"]):
            if "date" not in event:
                errors.append(f"事件 {i} 缺少 date 字段")
            if "category" not in event:
                warnings.append(f"事件 {i} 缺少 category 字段")
            if "description" not in event:
                warnings.append(f"事件 {i} 缺少 description 字段")
    
    # 日期格式检查
    if "birth_date" in data:
        try:
            datetime.strptime(data["birth_date"], "%Y-%m-%d")
        except ValueError:
            errors.append(f"birth_date 格式错误: {data['birth_date']}，应为 YYYY-MM-DD")
    
    return {
        "file": str(filepath),
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def main():
    """主函数"""
    cases_dir = Path(__file__).parent.parent
    
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
        if target.is_file():
            files = [target]
        elif target.is_dir():
            files = list(target.glob("*.json"))
        else:
            print(f"错误: {target} 不存在")
            sys.exit(1)
    else:
        files = list(cases_dir.rglob("*.json"))
    
    results = []
    for f in files:
        result = validate_case_file(f)
        results.append(result)
    
    # 统计
    valid_count = sum(1 for r in results if r["valid"])
    invalid_count = len(results) - valid_count
    
    print(f"\n案例验证结果:")
    print(f"  总计: {len(results)} 个文件")
    print(f"  有效: {valid_count} 个")
    print(f"  无效: {invalid_count} 个")
    
    if invalid_count > 0:
        print("\n错误详情:")
        for r in results:
            if not r["valid"]:
                print(f"\n  {r['file']}:")
                for e in r["errors"]:
                    print(f"    - {e}")
    
    sys.exit(0 if invalid_count == 0 else 1)


if __name__ == "__main__":
    main()
