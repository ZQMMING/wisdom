#!/usr/bin/env python3
"""
修复 D:/shuntian 测试文件中的错误仓库路径
"""

import os
import re
from pathlib import Path

REPO_ROOT = Path("/d/shuntian").resolve()

def fix_path_in_file(file_path: Path):
    """修复单个文件中的路径引用"""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except (UnicodeDecodeError, PermissionError):
        return False, "无法读取文件或二进制文件"

    original = content

    # 替换所有 . 和 . 为相对路径
    content = re.sub(r'D:/?today', '.', content)
    content = re.sub(r'D:\\\\today', '.', content)

    # 特殊处理: sys.path.insert 需要指向 src 目录
    content = re.sub(
        r'sys\.path\.insert\(0, str\(Path\("\./backend/src"\)\)\)',
        'sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))',
        content
    )

    # 处理 _REPO_ROOT 变量
    content = content.replace('_REPO_ROOT = Path(".")',
                             '_REPO_ROOT = Path(__file__).resolve().parents[1]')

    if content == original:
        return False, "无变更"

    file_path.write_text(content, encoding='utf-8')
    return True, "已修复"

def main():
    tests_dir = REPO_ROOT / "tests"
    
    if not tests_dir.exists():
        print(f"❌ 测试目录不存在: {tests_dir}")
        return

    fixed_files = []

    for py_file in tests_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        success, msg = fix_path_in_file(py_file)
        if success:
            fixed_files.append(py_file.relative_to(REPO_ROOT))
            print(f"✅ 已修复: {py_file.relative_to(REPO_ROOT)}")

    print(f"\n{'='*60}")
    print(f"修复完成: {len(fixed_files)} 个文件")

    # 验证
    remaining = 0
    for py_file in tests_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            if '.' in content or 'D:\\today' in content:
                remaining += 1
                print(f"⚠️ 仍含 .: {py_file.relative_to(REPO_ROOT)}")
        except:
            pass

    if remaining == 0:
        print(f"✅ 所有 . 引用已修复!")
    else:
        print(f"⚠️ 仍有 {remaining} 个文件含 . 引用")

if __name__ == "__main__":
    main()
