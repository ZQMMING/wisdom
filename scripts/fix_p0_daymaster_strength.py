#!/usr/bin/env python3
"""
P0 修复脚本：修复 day_master_strength 字段的 fail-closed 行为。

问题：
  - temporal_context_contract.py:154 默认值为 "MODERATE"
  - context_assembler.py:203 使用 getattr(..., 'MODERATE') 静默fallback

修复：
  - 改为 "MISSING" 默认值
  - 添加 assert 检查，缺失时抛出 ValueError
"""
import sys
sys.path.insert(0, 'src')

def fix_temporal_context_contract():
    """修复 temporal_context_contract.py 的默认值."""
    file_path = 'src/tongshu/reasoning/temporal_context_contract.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修改默认值从 "MODERATE" 到 "MISSING"
    old_line = '    day_master_strength: str = "MODERATE"                         # 日主强度档位'
    new_line = '    day_master_strength: str = "MISSING"                            # 日主强度档位（MISSING表示未计算）'
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        print(f"✅ 已修改 {file_path}: 默认值改为 MISSING")
    else:
        print(f"⚠️ 未找到目标行: {old_line}")
        return False
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True


def fix_context_assembler():
    """修复 context_assembler.py 的 getattr 调用."""
    file_path = 'src/tongshu/reasoning/context_assembler.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修改 getattr 调用，改为显式检查
    old_code = """            day_master_strength=getattr(chart, 'day_master_strength', 'MODERATE'),"""
    new_code = """            # P0 修复: fail-closed，缺失时报错而非静默使用默认值
            _dm_strength = getattr(chart, 'day_master_strength', None)
            if _dm_strength is None:
                raise ValueError(
                    f"day_master_strength 未计算。"
                    f"日主强度是辨证核心，必须在 BaziEngine 中计算或明确标记为 MISSING。"
                    f"当前日主: {chart.day_master}"
                )
            day_master_strength=_dm_strength,"""
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        print(f"✅ 已修改 {file_path}: 添加 fail-closed 检查")
    else:
        print(f"⚠️ 未找到目标代码块")
        return False
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True


def verify_fix():
    """验证修复是否生效."""
    print("\n=== 验证 P0 修复 ===")
    
    try:
        from tongshu.reasoning.temporal_context_contract import NatalContext
        natal = NatalContext(
            day_master="JIA",
            gender="male",
            birth_year=1983,
        )
        print(f"✅ NatalContext 默认 day_master_strength = '{natal.day_master_strength}'")
        assert natal.day_master_strength == "MISSING", "默认值应为 MISSING"
        print("✅ 默认值验证通过")
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("P0 修复：day_master_strength fail-closed 行为")
    print("=" * 60)
    
    success = True
    success &= fix_temporal_context_contract()
    success &= fix_context_assembler()
    success &= verify_fix()
    
    if success:
        print("\n=== P0 修复完成 ===")
        print("状态: ✅ COMPLETED")
        print("请运行测试验证: pytest tests/test_phase3_p0.py")
    else:
        print("\n=== P0 修复失败 ===")
        print("状态: ❌ FAILED")
        sys.exit(1)
