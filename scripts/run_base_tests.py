"""测试增强脚本 - 补充核心模块缺失测试"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path("D:/today/backend/src")))

# 运行现有测试，确认基准
import subprocess
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=short"],
    cwd="D:/today/backend",
    capture_output=True,
    text=True
)
print("=== 基准测试 ===")
for line in result.stdout.split('\n')[-5:]:
    print(line)
