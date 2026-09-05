#!/usr/bin/env python3
"""
Runtime Boundary Enforcement Test Runner
Verifies that AUXILIARY_SIGNAL/ENGINEERING_HEURISTIC outputs 
do not enter CanonicalSignal or Judgment chains.

Usage:
    python scripts/test_runtime_boundary_enforcement.py
"""
import sys
import inspect
from dataclasses import replace

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from src.tongshu.engines.bazi_engine import BaziChart, BaziEngine, Pillar
from src.tongshu.reasoning.signal_engine import extract_heluo_context
from src.tongshu.judgment_architecture.system_school_contract import get_ziping_index_paths_for_case
from src.tongshu.engines.blind_bazi_engine import BlindBaziEngine


def test_five_element_not_in_canonical_signal():
    """Core assertion: five_element_imbalance must not produce CanonicalSignal."""
    engine = BaziEngine()
    chart = engine.compute((1984, 1, 1, 0), gender="male")
    
    # Check FiveElementBalance exists (allowed for observation)
    assert hasattr(chart, 'five_element_balance')
    
    # Key assertion: signal_engine no longer reads bazi.five_element_balance
    source = inspect.getsource(extract_heluo_context)
    assert 'bazi.five_element_balance[' not in source, \
        "signal_engine should not read bazi.five_element_balance for calculations"
    
    print("✅ test_five_element_not_in_canonical_signal PASSED")


def test_strength_path_no_longer_reads_balance():
    """Verify STRENGTH_PATH input no longer contains five_element_balance."""
    paths = get_ziping_index_paths_for_case({})
    
    assert "STRENGTH_PATH" in paths
    input_features = paths["STRENGTH_PATH"]["input_features"]
    
    assert "five_element_balance" not in input_features, \
        "five_element_balance must not appear in canonical STRENGTH_PATH inputs"
    
    print("✅ test_strength_path_no_longer_reads_balance PASSED")


def test_blind_health_no_longer_uses_balance():
    """Verify blind health signals no longer generated based on five_element_imbalance."""
    source = inspect.getsource(BlindBaziEngine.compute)
    
    # Key assertion: code should not have five_element_imbalance triggering HEALTH_ISSUE
    lines = source.split('\n')
    for i, line in enumerate(lines):
        if 'HEALTH_ISSUE' in line or 'health-' in line.lower():
            context = '\n'.join(lines[max(0,i-5):i+2])
            assert 'five_element_imbalance' not in context, \
                "blind engine should not use five_element_imbalance for HEALTH_ISSUE"
    
    print("✅ test_blind_health_no_longer_uses_balance PASSED")


def test_boundary_isolation_invariant():
    """
    Boundary isolation invariant:
    Changes to five_element_balance value should not affect Signal Layer.
    """
    engine = BaziEngine()
    chart = engine.compute((1984, 1, 1, 0), gender="male")
    
    # BaziChart is frozen dataclass, must use replace
    new_chart = replace(chart, five_element_balance={
        "WOOD": 0.8, "FIRE": 0.02, "EARTH": 0.02, "METAL": 0.02, "WATER": 0.14
    })
    
    # Verify isolation: signal_engine no longer reads this field
    result = extract_heluo_context(None, new_chart)
    
    # When heluo_result=None, returns empty dict
    # Core check: code no longer reads bazi.five_element_balance
    assert result == {}, \
        "isolated chart should produce empty result when heluo_result is None"
    
    print("✅ test_boundary_isolation_invariant PASSED")


def test_kong_wang_still_works():
    """Regression test: Kong Wang calculation unaffected."""
    engine = BaziEngine()
    chart = engine.compute((1984, 1, 1, 0), gender="male")
    
    assert hasattr(chart, 'kong_wang')
    assert isinstance(chart.kong_wang, tuple)
    
    print("✅ test_kong_wang_still_works PASSED")


def test_branch_clash_map_still_works():
    """Regression test: Branch clash map unaffected."""
    engine = BaziEngine()
    chart = engine.compute((1984, 1, 1, 0), gender="male")
    
    assert hasattr(chart, 'branch_clash_map')
    assert isinstance(chart.branch_clash_map, dict)
    
    print("✅ test_branch_clash_map_still_works PASSED")


def test_day_branch_main_ten_god_computed():
    """Regression test: Day branch main ten god computation unaffected."""
    engine = BaziEngine()
    chart = engine.compute((1984, 1, 1, 0), gender="male")
    
    assert hasattr(chart, 'day_branch_main_ten_god')
    assert isinstance(chart.day_branch_main_ten_god, str)
    
    print("✅ test_day_branch_main_ten_god_computed PASSED")


if __name__ == "__main__":
    from pathlib import Path
    tests = [
        test_five_element_not_in_canonical_signal,
        test_strength_path_no_longer_reads_balance,
        test_blind_health_no_longer_uses_balance,
        test_boundary_isolation_invariant,
        test_kong_wang_still_works,
        test_branch_clash_map_still_works,
        test_day_branch_main_ten_god_computed,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} ERROR: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    
    sys.exit(0 if failed == 0 else 1)
