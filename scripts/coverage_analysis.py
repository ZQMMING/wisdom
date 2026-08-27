"""测试覆盖率分析脚本"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path("D:/today/backend/src")))

# 扫描所有测试文件
tests_dir = Path("D:/today/backend/tests")
test_files = list(tests_dir.glob("**/test_*.py")) + list(tests_dir.glob("test_*.py"))

module_tests = {}
for tf in test_files:
    content = tf.read_text(encoding='utf-8')
    test_count = content.count('def test_')
    if test_count > 0:
        # 推断被测模块
        module = tf.stem.replace('test_', '')
        module_tests[module] = test_count

print("=" * 60)
print("测试覆盖度分析")
print("=" * 60)
print(f"测试文件数: {len(test_files)}")
print(f"总测试用例: {sum(module_tests.values())}")
print()
print("--- 按模块统计 ---")
for k, v in sorted(module_tests.items(), key=lambda x: -x[1])[:30]:
    bar = "█" * (v // 2)
    print(f"  {k:30s} {v:3d} tests {bar}")

# 检查未被覆盖的源码模块
src_dir = Path("D:/today/backend/src/tongshu/engines")
print()
print("--- 源码模块覆盖检查 ---")
src_files = list(src_dir.rglob("*.py"))
for sf in src_files:
    if sf.name in ('__init__.py', 'exceptions.py'):
        continue
    rel = sf.relative_to(src_dir)
    covered = any(m in str(rel) for m in module_tests.keys())
    status = "✅" if covered else "❌"
    print(f"  {status} {rel}")
