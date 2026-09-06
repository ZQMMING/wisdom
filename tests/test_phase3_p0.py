#!/usr/bin/env python3
"""Phase 3 P0 语义审计验证测试"""
import sys
sys.path.insert(0, 'src')

def test_p0_fix():
    """测试 P0 修复：day_master_strength fail-closed."""
    from tongshu.reasoning.temporal_context_contract import NatalContext
    from tongshu.reasoning.context_assembler import ContextAssembler
    from tongshu.engines.bazi_engine import BaziEngine
    
    print("\n=== Phase 3 P0 验证测试 ===")
    
    # Test 1: NatalContext 默认值应为 MISSING
    print("\n[TEST 1] NatalContext 默认 day_master_strength")
    natal = NatalContext(
        day_master="JIA",
        gender="male",
        birth_year=1983,
    )
    assert natal.day_master_strength == "MISSING", f"期望 'MISSING', 实际 '{natal.day_master_strength}'"
    print(f"✅ PASS: default = '{natal.day_master_strength}'")
    
    # Test 2: ContextAssembler 组装时应抛出 ValueError
    print("\n[TEST 2] ContextAssembler 缺少 day_master_strength 应报错")
    assembler = ContextAssembler()
    engine = BaziEngine()
    chart = engine.compute((1983, 11, 3, 12), "male")
    
    # chart 没有 day_master_strength 字段，应抛出 ValueError
    try:
        natal = assembler.assemble_natal_context(chart, 1983, "male")
        print(f"❌ FAIL: 应抛出 ValueError，但实际成功组装")
        return False
    except ValueError as e:
        error_msg = str(e)
        assert "day_master_strength" in error_msg, f"错误消息应包含字段名: {error_msg}"
        print(f"✅ PASS: 正确抛出 ValueError")
        print(f"   错误信息: {error_msg[:100]}...")
    
    # Test 3: 显式创建带 day_master_strength 的 Mock chart
    # P0-1-C: mock chart 需要包含 pillar.stem_ten_god 字段（BAZI Contract）
    print("\n[TEST 3] 显式设置 day_master_strength 应正常")
    from types import SimpleNamespace
    mock_chart = SimpleNamespace(
        day_master="JIA",
        year_pillar=SimpleNamespace(
            heavenly_stem="YI", earthly_branch="YOU",
            stem_ten_god="DIRECT_OFFICER",  # P0-1-C: BAZI 提供
        ),
        month_pillar=SimpleNamespace(
            heavenly_stem="WU", earthly_branch="CHEN",
            stem_ten_god="EATING_GOD",  # P0-1-C: BAZI 提供
        ),
        day_pillar=SimpleNamespace(
            heavenly_stem="JIA", earthly_branch="ZI",
            stem_ten_god="DAY_MASTER",  # P0-1-C: BAZI 提供
        ),
        hour_pillar=SimpleNamespace(
            heavenly_stem="REN", earthly_branch="XU",
            stem_ten_god="WEALTH",  # P0-1-C: BAZI 提供
        ),
        day_master_strength="STRONG",
        structural_features=[],
        start_age=2.5,
        luck_pillars=[],
        branch_clash_map={},
        branch_he_map={},
        branch_harm_map={},
        branch_sanhe_map={},
        birth_datetime=None,
        gender="male",
    )
    natal = assembler.assemble_natal_context(mock_chart, 1983, "male")
    assert natal.day_master_strength == "STRONG"
    print(f"✅ PASS: day_master_strength = '{natal.day_master_strength}'")
    
    # Test 4: 验证 stem_ten_god 消费链路
    print("\n[TEST 4] 验证 pillar.stem_ten_god 消费")
    assert natal.pillars[0].stem_ten_god == "DIRECT_OFFICER"
    assert natal.pillars[1].stem_ten_god == "EATING_GOD"
    assert natal.pillars[2].stem_ten_god == "DAY_MASTER"
    assert natal.pillars[3].stem_ten_god == "WEALTH"
    print(f"✅ PASS: 四柱十神消费正确")
    
    print("\n=== 所有 P0 测试通过 ===")
    return True


if __name__ == "__main__":
    try:
        success = test_p0_fix()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
