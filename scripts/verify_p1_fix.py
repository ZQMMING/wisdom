#!/usr/bin/env python3
"""Verify P1 fix: context_assembler now imports ten_god from bazi_ten_gods."""
import sys
sys.path.insert(0, 'src')

try:
    from tongshu.reasoning.context_assembler import ContextAssembler, compute_ten_god
    from tongshu.reasoning.bazi_ten_gods import ten_god
    
    print("✅ Import OK")
    
    # Verify compute_ten_god is now the same as bazi_ten_gods.ten_god
    assert compute_ten_god is ten_god, "compute_ten_god should be imported from bazi_ten_gods"
    print("✅ compute_ten_god is now imported from bazi_ten_gods (not duplicated)")
    
    # Test basic cases
    result = compute_ten_god("JIA", "BING")
    print(f"✅ ten_god('JIA', 'BING') = {result} (expected: 食神)")
    assert result == "食神" or result == "SHISHEN", f"Unexpected result: {result}"
    
    print("\n=== P1 Fix Verification ===")
    print("Status: COMPLETED ✅")
    print("- Removed: duplicate compute_ten_god (lines 119-163)")
    print("- Added: from tongshu.reasoning.bazi_ten_gods import ten_god as compute_ten_god")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
