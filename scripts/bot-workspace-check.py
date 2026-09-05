#!/usr/bin/env python3
"""Bot工作区验证器 - 每次任务前必须执行"""

import os
import sys
from pathlib import Path

# 定义路径规则
WORKSPACE_ROOT = Path("D:/shuntian").resolve()
ALLOWED_SUBDIRS = {"src", "tests", "data", "docs", "backend", "scripts", "archive", ".tmp_cases"}
FORBIDDEN_PATHS = [
    Path("D:/today").resolve(),
    Path("D:/d/today").resolve(),
    Path("D:/shuntian-NEW").resolve(),
]

def check_workspace():
    """验证当前工作区是否合规"""
    cwd = Path.cwd().resolve()
    
    # 检查是否在允许的根目录下
    try:
        cwd.relative_to(WORKSPACE_ROOT)
    except ValueError:
        return False, f"违规: 当前路径不在 {WORKSPACE_ROOT} 下: {cwd}"
    
    # 检查是否在禁止的目录中
    for forbidden in FORBIDDEN_PATHS:
        if cwd == forbidden or forbidden in cwd.parents:
            return False, f"违规: 禁止在工作目录 {forbidden} 中执行"
    
    # 检查根目录层级
    rel = cwd.relative_to(WORKSPACE_ROOT)
    if rel.parts and rel.parts[0] not in ALLOWED_SUBDIRS:
        return False, f"警告: 非标准目录 {rel.parts[0]}/"
    
    return True, "✅ 工作区合规"

if __name__ == "__main__":
    ok, msg = check_workspace()
    print(f"[BOT-WORKSPACE] {msg}")
    sys.exit(0 if ok else 1)
