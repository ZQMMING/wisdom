# Bot Master 预任务验证脚本
# 每次任务执行前必须通过此检查

"""
Bot Master 任务启动前验证器
用法: python pre_task_check.py <task_description>
"""

import os
import sys
from pathlib import Path

# 禁止的根路径
FORBIDDEN_ROOTS = [
    Path("D:/today").resolve(),
    Path("D:/d/today").resolve(),
    Path("D:/shuntian-NEW").resolve(),
]

# 允许的子目录
ALLOWED_SUBDIRS = {
    "src", "tests", "data", "docs", "backend", 
    "scripts", "archive", ".tmp_cases"
}

def verify_workspace():
    """验证工作区合规性"""
    cwd = Path.cwd().resolve()
    shuntian_root = Path("D:/shuntian").resolve()
    
    # 1. 检查是否在合法根目录下
    try:
        cwd.relative_to(shuntian_root)
    except ValueError:
        return False, f"❌ 违规: 当前路径 {cwd} 不在 D:/shuntian/ 下"
    
    # 2. 检查是否在任何禁止的目录中
    for forbidden in FORBIDDEN_ROOTS:
        if cwd == forbidden or forbidden in cwd.parents:
            return False, f"❌ 违规: 禁止在工作目录 {forbidden} 中执行"
    
    # 3. 检查根目录层级
    rel = cwd.relative_to(shuntian_root)
    if rel.parts and rel.parts[0] not in ALLOWED_SUBDIRS:
        return False, f"❌ 警告: 非标准目录 {rel.parts[0]}/"
    
    # 4. 检查禁止的文件生成路径
    for forbidden in FORBIDDEN_ROOTS:
        if str(cwd).startswith(str(forbidden)):
            return False, f"❌ 严重违规: 试图在禁止目录 {forbidden} 中生成文件"
    
    return True, f"✅ 工作区验证通过: {cwd}"

def check_forbidden_paths(paths):
    """检查是否有任何路径在禁止列表中"""
    violations = []
    for path_str in paths:
        path = Path(path_str).resolve()
        for forbidden in FORBIDDEN_ROOTS:
            if path == forbidden or forbidden in path.parents:
                violations.append(f"  - {path_str} (属于禁止目录 {forbidden})")
    return violations

if __name__ == "__main__":
    # 打印验证结果
    ok, msg = verify_workspace()
    print(f"[PRE-TASK-VERIFY] {msg}")
    
    if not ok:
        print("[FATAL] 任务启动被阻止 - 工作区验证失败")
        sys.exit(1)
    
    # 如果有命令行参数，检查指定路径
    if len(sys.argv) > 1:
        task_desc = sys.argv[1]
        print(f"[TASK] 验证任务: {task_desc}")
        
        # 提取路径并检查
        import re
        paths = re.findall(r'[Dd]:/[^\s,\)]+', task_desc)
        if paths:
            violations = check_forbidden_paths(paths)
            if violations:
                print("[VIOLATION] 检测到禁止路径:")
                for v in violations:
                    print(v)
                sys.exit(1)
    
    print("[OK] 验证通过，任务可以启动")
    sys.exit(0)
