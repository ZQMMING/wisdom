#!/usr/bin/env python3
"""Probe all 20 golden cases to get actual engine output."""
import sys
from pathlib import Path

# ─── 路径独立定位 ──────────────────────────────────────────────────────────────
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / 'src'))

from tongshu.engines.blind_bazi_engine import compute_blind_bazi

cases = [
    ("BLIND-001", (1990, 5, 15, 10), "male"),
    ("BLIND-002", (1985, 3, 20, 14), "female"),
    ("BLIND-003", (1978, 8, 8, 8), "male"),
    ("BLIND-004", (1988, 6, 18, 16), "female"),
    ("BLIND-005", (1992, 1, 1, 12), "male"),
    ("BLIND-006", (1986, 11, 28, 10), "female"),
    ("BLIND-007", (1980, 9, 12, 14), "male"),
    ("BLIND-008", (1975, 4, 4, 10), "female"),
    ("BLIND-009", (1991, 7, 7, 8), "male"),
    ("BLIND-010", (1983, 2, 14, 22), "male"),
    ("BLIND-011", (1987, 10, 30, 6), "female"),
    ("BLIND-012", (1979, 5, 5, 18), "male"),
    ("BLIND-013", (1993, 8, 18, 12), "male"),
    ("BLIND-014", (1984, 12, 25, 14), "female"),
    ("BLIND-015", (1981, 6, 6, 16), "male"),
    ("BLIND-016", (1989, 3, 3, 10), "female"),
    ("BLIND-017", (1976, 9, 21, 8), "male"),
    ("BLIND-018", (1994, 1, 15, 20), "male"),
    ("BLIND-019", (1982, 7, 7, 12), "female"),
    ("BLIND-020", (1995, 12, 31, 0), "male"),
]

print("# Blind Golden Set - Engine Output Probe")
print()
for case_id, birth, gender in cases:
    result = compute_blind_bazi(birth, gender)
    print(f"## {case_id}")
    print(f"- birth: {birth}, gender: {gender}")
    print(f"- zuo_gong_type: {result.zuo_gong_type}")
    print(f"- main_branches: {sorted(result.main_branches)}")
    print(f"- guest_branches: {sorted(result.guest_branches)}")
    print(f"- ti_branches: {sorted(result.ti_branches)}")
    print(f"- yong_branches: {sorted(result.yong_branches)}")
    print(f"- zuo_gong_methods: {result.zuo_gong_methods}")
    print(f"- signals: {[s.signal_id for s in result.signals]}")
    print()
