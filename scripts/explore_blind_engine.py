#!/usr/bin/env python3
"""Quick exploration of BlindBaziEngine output structure"""
import sys
from pathlib import Path

# ─── 路径独立定位 ──────────────────────────────────────────────────────────────
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / 'src'))

from tongshu.engines.blind_bazi_engine import compute_blind_bazi

# Standard test case
result = compute_blind_bazi((1990, 5, 15, 10), 'male')

print("=" * 60)
print("BlindBaziEngine Output Structure")
print("=" * 60)

# Check result attributes
print("\n--- Result Attributes ---")
for attr in dir(result):
    if not attr.startswith('_'):
        val = getattr(result, attr)
        if not callable(val):
            print(f"  {attr}: {type(val).__name__} = {repr(val)[:100] if val else None}")

print("\n--- Signals ---")
for sig in result.signals:
    print(f"  {sig.signal_id}: {sig.event_type} ({sig.direction.value}) strength={sig.strength}")

print("\n--- Ti/Guest Branches ---")
if hasattr(result, 'ti_branches'):
    print(f"  ti_branches: {result.ti_branches}")
if hasattr(result, 'guest_branches'):
    print(f"  guest_branches: {result.guest_branches}")

print("\n--- Zuo Gong ---")
if hasattr(result, 'zuo_gong_methods'):
    print(f"  zuo_gong_methods: {result.zuo_gong_methods}")
