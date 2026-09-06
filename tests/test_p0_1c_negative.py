#!/usr/bin/env python3
"""P0-1-C 负向测试 - 验证 ZIPING 不重新计算确定性事实

BOT-MASTER 要求: 增加强制负向测试，防止 Agent 重新加入计算逻辑。
"""
import sys
sys.path.insert(0, 'src')

def test_ziping_does_not_compute_year_pillar():
    """测试: ZIPING 不应该自己计算流年干支

    P0-1-C 边界: Year Pillar 由 BAZI/Temporal Engine 计算，ZIPING 只消费。
    如果 chart.year_pillar 缺失，应该抛出异常而不是 fallback 计算。
    """
    from tongshu.reasoning.context_assembler import ContextAssembler
    from types import SimpleNamespace

    assembler = ContextAssembler()

    # 完整的 mock chart (包含所有必需字段)
    mock_chart = SimpleNamespace(
        day_master="JIA",
        year_pillar=SimpleNamespace(
            heavenly_stem="BING", earthly_branch="YIN",
            stem_ten_god="DIRECT_RESOURCE"
        ),
        month_pillar=SimpleNamespace(heavenly_stem="WU", earthly_branch="CHEN", stem_ten_god="EATING_GOD"),
        day_pillar=SimpleNamespace(heavenly_stem="JIA", earthly_branch="ZI", stem_ten_god="DAY_MASTER"),
        hour_pillar=SimpleNamespace(heavenly_stem="REN", earthly_branch="XU", stem_ten_god="WEALTH"),
        day_master_strength="STRONG",
        structural_features=[],
        start_age=2.5,
        luck_pillars=[],
        branch_clash_map={"YIN": ["SHEN"], "SHEN": ["YIN"]},
        branch_he_map={"YIN": ["HEN"], "HEN": ["YIN"]},
        branch_harm_map={},
        branch_sanhe_map={},
        birth_datetime=__import__('datetime').datetime(1983, 11, 3, 12, 0),
        gender="male",
    )

    # 测试: 完整 mock chart 应该成功组装
    print("\n[子测试] 完整 mock chart 应正常组装")
    natal = assembler.assemble_natal_context(mock_chart, 1983, "male")
    from tongshu.reasoning.temporal_context_contract import DaYunContext
    dayun = DaYunContext()
    year = assembler.assemble_year_context(natal, dayun, mock_chart, 2026)

    # 验证 year context 从 chart 消费
    assert year.year_stem == "BING"
    assert year.year_branch == "YIN"
    assert year.year_stem_ten_god == "DIRECT_RESOURCE"
    print(f"✅ PASS: year context 正确消费 chart.year_pillar")

    # 测试2: year_pillar=None 应抛出异常（不允许 fallback）
    print("\n[子测试] year_pillar=None 应抛异常")
    minimal_chart = SimpleNamespace(
        day_master="JIA",
        year_pillar=None,
        month_pillar=mock_chart.month_pillar,
        day_pillar=mock_chart.day_pillar,
        hour_pillar=mock_chart.hour_pillar,
        day_master_strength="STRONG",
        structural_features=[],
        start_age=2.5,
        luck_pillars=[],
        branch_clash_map={},
        branch_he_map={},
        branch_harm_map={},
        branch_sanhe_map={},
        birth_datetime=mock_chart.birth_datetime,
        gender="male",
    )

    try:
        assembler.assemble_natal_context(minimal_chart, 1983, "male")
        print("❌ FAIL: year_pillar=None 时没有抛出异常")
        return False
    except (AttributeError, ValueError) as e:
        print(f"✅ PASS: 正确抛出 {type(e).__name__} (year_pillar 缺失)")
        return True


def test_no_local_year_cycle_formula():
    """测试: ZIPING 不应该包含 60年甲子循环公式"""
    import inspect
    from tongshu.reasoning.context_assembler import ContextAssembler
    
    source = inspect.getsource(ContextAssembler)
    
    # 禁止的模式
    forbidden_patterns = [
        "base_year = 1984",
        "% 60",
        "stem_idx = offset",
        "branch_idx = offset",
    ]
    
    violations = []
    for pattern in forbidden_patterns:
        if pattern in source:
            violations.append(pattern)
    
    if violations:
        print(f"❌ FAIL: 发现禁止的流年计算公式: {violations}")
        return False
    
    print(f"✅ PASS: 未发现禁止的流年计算公式")
    return True


def test_no_local_ten_god_for_year():
    """测试: ZIPING 不应该为 Year 重新计算十神

    注意: Natal 四柱消费 chart.*.stem_ten_god 是正确的，不算违规。
    违规的是类似 `ten_god(natal.day_master, year_stem)` 这种为 year 计算的调用。
    """
    import inspect
    from tongshu.reasoning.context_assembler import ContextAssembler

    source = inspect.getsource(ContextAssembler)

    # 查找为 year 计算 ten_god 的模式（不是 natal）
    # 违规模式: ten_god(natal.day_master, ...) 或 ten_god(day_master, ...) 在 year context 部分
    lines = source.split('\n')
    violations = []
    in_year_context = False

    for i, line in enumerate(lines):
        # 进入 assemble_year_context 方法
        if 'def assemble_year_context' in line:
            in_year_context = True
        # 退出到下一个方法
        elif in_year_context and line.startswith('    def ') and 'assemble_year_context' not in line:
            in_year_context = False

        if in_year_context:
            # 检查是否调用 ten_god() 函数（不是 getattr）
            if 'ten_god(' in line and 'getattr' not in line and not line.strip().startswith('#'):
                violations.append(f"Line {i}: {line.strip()}")

    if violations:
        print(f"❌ FAIL: 发现 Year ten_god 重新计算:")
        for v in violations[:5]:
            print(f"   {v}")
        return False

    print(f"✅ PASS: 未发现 Year ten_god 重新计算")
    return True


def test_year_context_requires_chart():
    """测试: assemble_year_context 必须接收 chart 参数"""
    import inspect
    from tongshu.reasoning.context_assembler import ContextAssembler
    
    sig = inspect.signature(ContextAssembler.assemble_year_context)
    params = list(sig.parameters.keys())
    
    if 'chart' not in params:
        print(f"❌ FAIL: assemble_year_context 缺少 chart 参数: {params}")
        return False
    
    print(f"✅ PASS: assemble_year_context 有 chart 参数")
    return True


def test_no_branh_relation_tables():
    """测试: ZIPING 不应该有本地 branch relation 表"""
    import inspect
    from tongshu.reasoning.context_assembler import ContextAssembler
    
    source = inspect.getsource(ContextAssembler)
    
    # 检查类定义内部是否有这些表
    forbidden_tables = [
        "BRANCH_CLASH =",
        "BRANCH_COMBINATION =",
        "BRANCH_HARM =",
        "BRANCH_PUNISHMENT =",
        "THREE_COMBINATION =",
    ]
    
    violations = []
    for table in forbidden_tables:
        # 检查是否在类定义中（不是注释）
        lines = source.split('\n')
        in_class = False
        for line in lines:
            if 'class ContextAssembler' in line:
                in_class = True
            if in_class and table in line and not line.strip().startswith('#'):
                violations.append(table)
                break
    
    if violations:
        print(f"❌ FAIL: 发现禁止的 branch relation 表: {violations}")
        return False
    
    print(f"✅ PASS: 未发现禁止的 branch relation 表")
    return True


if __name__ == "__main__":
    print("\n=== P0-1-C 负向测试 ===")
    print("验证 ZIPING 不重新计算确定性事实\n")
    
    tests = [
        ("Year pillar 不应 fallback 计算", test_ziping_does_not_compute_year_pillar),
        ("无本地 60年循环公式", test_no_local_year_cycle_formula),
        ("无 Year ten_god 重算", test_no_local_ten_god_for_year),
        ("Year context 需 chart 参数", test_year_context_requires_chart),
        ("无本地 branch relation 表", test_no_branh_relation_tables),
    ]
    
    results = []
    for name, test_fn in tests:
        print(f"\n[{name}]")
        try:
            result = test_fn()
            results.append((name, result))
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append((name, False))
    
    print("\n=== 测试结果汇总 ===")
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n总计: {passed}/{total} PASS")
    
    if passed < total:
        print("\n⚠️  P0-1-C 边界未完成 - 需要修复后再提交")
        sys.exit(1)
    else:
        print("\n✅ 所有负向测试通过")
        sys.exit(0)
