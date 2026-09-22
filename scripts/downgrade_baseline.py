# -*- coding: utf-8 -*-
"""T0：降级baseline为structural.json + 写_provenance元信息"""
import sys
import io
import json
import shutil
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 读取原baseline
with open(r'D:\shuntian-ziping-p0\baseline_special_20260922.json', 'r', encoding='utf-8') as f:
    baseline = json.load(f)

# 添加_provenance元信息
baseline_with_meta = {
    "_meta": {
        "provenance": "C",
        "note": "本文件由旧引擎dump生成（commit 05ab0f20），special/yongshen字段为旧引擎输出，非原著判据。禁止用于PASS/FAIL裁决，仅用于：①幂等性 ②互斥性 ③可观测性 ④行为变更检测（变更≠错误）。",
        "frozen_at": "2026-09-22",
        "do_not_edit": True,
        "source_commit": "05ab0f20",
        "original_file": "baseline_special_20260922.json"
    },
    "cases": baseline
}

# 保存到tests/regression/
output_dir = Path(r'D:\shuntian-ziping-p0\tests\regression')
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / 'structural_20260922.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(baseline_with_meta, f, ensure_ascii=False, indent=2)

print(f"✅ baseline已降级为structural.json")
print(f"   原文件: baseline_special_20260922.json")
print(f"   新文件: {output_file}")
print(f"   条数: {len(baseline)}")
print(f"   provenance: C（旧引擎dump，非原著判据）")
print()
print(f"=== _meta元信息 ===")
print(json.dumps(baseline_with_meta['_meta'], ensure_ascii=False, indent=2))
