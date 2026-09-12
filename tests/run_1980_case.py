# -*- coding: utf-8 -*-
"""1980案例端到端执行 - 严格按引擎输出."""
import sys
sys.path.insert(0, '.')

from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.reasoning.ziping_v3.runner import run_ziping
import json

print("=" * 60)
print("STEP 1: 八字排盘")
print("=" * 60)

BE = BaziEngine()
chart = BE.compute((1980, 6, 22, 10), gender='male')

print(f"出生时间: 1980年6月22日 10时 (庚申年)")
print(f"性别: 男")
print()
print(f"年柱: {chart.year_pillar.heavenly_stem}{chart.year_pillar.earthly_branch}")
print(f"月柱: {chart.month_pillar.heavenly_stem}{chart.month_pillar.earthly_branch}")
print(f"日柱: {chart.day_pillar.heavenly_stem}{chart.day_pillar.earthly_branch}")
print(f"时柱: {chart.hour_pillar.heavenly_stem}{chart.hour_pillar.earthly_branch}")
print(f"日主: {chart.day_master}")
print()

print("=" * 60)
print("STEP 2: 子平引擎辨层")
print("=" * 60)

result = run_ziping(chart)

# 输出15辨层域
print("\n【辨层域判定】")
for j in result.get('judgments', []):
    dom = j.get('domain', '')
    state = j.get('state', '')
    rules = j.get('matched_rule_ids', [])
    evidence = j.get('evidence_refs', [])
    print(f"  {dom:15s}: {state:20s} | 规则: {rules} | 证据: {evidence}")

print()
print("=" * 60)
print("STEP 3: 喜用神裁定")
print("=" * 60)

yong = result.get('yongshen', {})
print(f"  用神: {yong.get('main', '?')}")
print(f"  喜神: {yong.get('secondary', '?')}")
print(f"  忌神: {yong.get('ji_shen', '?')}")
print(f"  依据: {yong.get('basis', '?')}")
print(f"  原文: {yong.get('classic_quote', '?')}")
print(f"  出处: {yong.get('source', '?')}")

print()
print("=" * 60)
print("STEP 4: 大运输出")
print("=" * 60)

dayun = result.get('dayun', [])
print(f"  起运年龄: {chart.start_age:.2f}岁")
print()
for dy in dayun:
    age_range = dy.get('age_range', '')
    stem = dy.get('stem', '')
    branch = dy.get('branch', '')
    ten_god = dy.get('ten_god', '')
    print(f"  {age_range}岁: {stem}{branch} ({ten_god})")

print()
print("=" * 60)
print("STEP 5: 解层断语")
print("=" * 60)

interp = result.get('interpretations', {})
total = 0
for dom, hooks in sorted(interp.items()):
    if hooks:
        count = len(hooks)
        total += count
        # 取第一条断语的原文
        first_text = hooks[0].get('text', '')[:60] if hooks else ''
        print(f"  {dom:15s}: {count:3d}条 | {first_text}...")

print()
print(f"  {'总计':15s}: {total:3d}条")

print()
print("=" * 60)
print("STEP 6: 流年判定")
print("=" * 60)

liunian = result.get('liunian', [])
for ln in liunian[:5]:  # 只显示前5年
    year = ln.get('year', '')
    ji_xiong = ln.get('ji_xiong', '')
    reason = ln.get('reason', '')[:40]
    print(f"  {year}: {ji_xiong} | {reason}...")

print()
print("=" * 60)
print("STEP 7: 完整JSON输出")
print("=" * 60)

# 输出扁平化结构化结果
output = {
    "engine": "ZIPING_RULE_ENGINE",
    "version": "3.1",
    "birth": {
        "date": "1980-06-22",
        "time": "10:00",
        "gender": "male"
    },
    "four_pillars": {
        "year": f"{chart.year_pillar.heavenly_stem}{chart.year_pillar.earthly_branch}",
        "month": f"{chart.month_pillar.heavenly_stem}{chart.month_pillar.earthly_branch}",
        "day": f"{chart.day_pillar.heavenly_stem}{chart.day_pillar.earthly_branch}",
        "hour": f"{chart.hour_pillar.heavenly_stem}{chart.hour_pillar.earthly_branch}"
    },
    "day_master": chart.day_master,
    "judgments": result.get('judgments', []),
    "strength": result.get('strength', {}),
    "pattern": result.get('pattern', {}),
    "climate": result.get('climate', {}),
    "disease": result.get('disease', {}),
    "tongguan": result.get('tongguan', {}),
    "yongshen": result.get('yongshen', {}),
    "xiji": result.get('xiji', {}),
    "dayun": result.get('dayun', []),
    "liunian": result.get('liunian', []),
    "interpretations": {k: v for k, v in interp.items() if v}
}

print(json.dumps(output, ensure_ascii=False, indent=2))
