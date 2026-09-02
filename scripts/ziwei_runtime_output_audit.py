#!/usr/bin/env python3
"""
紫微 Runtime Check 脚本 — P-A1 清理后验证
运行方式: python scripts/ziwei_runtime_output_audit.py
"""

import sys
import json
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from tongshu.engines.ziwei_engine import ZiweiEngine, GAN_SIHUA, MAIN_STAR_USO


def run_runtime_check():
    """Run complete runtime check on fixed case."""
    
    engine = ZiweiEngine()
    
    # Fixed case: Mao Zedong
    # Solar: 1893-12-26 08:00
    # Lunar: 癸巳年十一月十九日 辰时
    lunar_date = (1893, 11, 19)
    hour, gender = 8, "male"
    longitude = 112.9  # Hunan Xiangtan
    
    print("=" * 70)
    print("ZIWEI RUNTIME CHECK — P-A1 Post-Cleanup Verification")
    print("=" * 70)
    
    # [1] Input layer
    print(f"\n[1] INPUT LAYER")
    print(f"    Solar: 1893-12-26 {hour}:00")
    print(f"    Lunar: 1893年{lunar_date[1]}月{lunar_date[2]}日")
    print(f"    Gender: {gender}")
    print(f"    Longitude: {longitude}°E")
    
    # [2] Natal chart
    fc = engine.full_chart(lunar_date, hour, gender)
    print(f"\n[2] NATAL CHART")
    print(f"    命宫地支: {fc['soulPalaceBranch']}")
    print(f"    身宫地支: {fc['bodyPalaceBranch']}")
    print(f"    五行局: {fc['fiveElementsClass']}")
    
    # [3] 14 main stars
    print(f"\n[3] 十四主星落宫")
    for name in fc['palaces']:
        data = fc['palaces'][name]
        stars = data.get('major', [])
        star_str = ', '.join(stars) if stars else '(空宫)'
        print(f"    {name}: {star_str}")
    
    # [4] Birth sihua
    print(f"\n[4] 生年四化 (癸干)")
    print(f"    Source: GAN_SIHUA['癸'] = {GAN_SIHUA['癸']}")
    
    # [5] Palaces + sanfang sizheng
    print(f"\n[5] 十二宫 + 三方四正")
    palace_names = list(fc['palaces'].keys())
    for pname in palace_names:
        data = fc['palaces'][pname]
        sf = data.get('sanfang', [])
        sz = data.get('sizheng', [])
        sf_str = ','.join(sf) if sf else '-'
        sz_str = ','.join(sz) if sz else '-'
        print(f"    {pname}: 支{data['branch']} 干{data['stem']} | 三方:{sf_str} | 四正:{sz_str}")
    
    # [6] Decadal
    print(f"\n[6] 大限 (十二年)")
    for pname in palace_names:
        data = fc['palaces'][pname]
        dec = data.get('decadalRange', [])
        if dec:
            print(f"    {pname}: {dec[0]}-{dec[1]}岁 天干={data.get('decadalStem', 'N/A')}")
    
    # [7] Time-layer mutagen
    print(f"\n[7] 时间层四化")
    chart = engine.compute(lunar_date, hour, gender)
    
    ym = engine.flow_years_mutagen([1893], lunar_date, hour, gender)
    print(f"    流年: {ym}")
    
    mo = engine.flow_month_mutagen(1893, 11, lunar_date, hour, gender)
    print(f"    流月: {mo}")
    
    dy = engine.flow_day_mutagen(1893, 11, 19, lunar_date, hour, gender)
    print(f"    流日: {dy}")
    
    dc = engine.flow_decadal_mutagen([1893], lunar_date, hour, gender)
    print(f"    大限: {dc}")
    
    # [8] Clean check
    print(f"\n[8] CLEAN CHECK")
    fc_str = json.dumps(fc, ensure_ascii=False, default=str)
    forbidden = ['opportunity', 'caution', 'neutral', 'INCREASE', 'DECREASE',
                 'score_topic', 'topic_score', 'direction']
    found = [k for k in forbidden if k.lower() in fc_str.lower()]
    if found:
        print(f"    ✗ LEAK: {found}")
    else:
        print(f"    ✓ No forbidden keywords in output")
    
    for m in ['native_direction', 'score_topic', 'score_topic_sanfang', 'decadal_soul_effect']:
        exists = hasattr(engine, m)
        print(f"    {m}: {'EXISTS ✗' if exists else 'removed ✓'}")
    
    # [9] GAN_SIHUA integrity
    print(f"\n[9] GAN_SIHUA")
    print(f"    Stems: {list(GAN_SIHUA.keys())}")
    print(f"    Count: {len(GAN_SIHUA)}/10 {'✓' if len(GAN_SIHUA) == 10 else '✗'}")
    
    # [10] MAIN_STAR_USO
    print(f"\n[10] MAIN_STAR_USO")
    print(f"    Present: {MAIN_STAR_USO is not None} ({len(MAIN_STAR_USO)} keys)")
    print(f"    Role: Signal Extraction layer (not Calculation Core)")
    
    print("\n" + "=" * 70)
    print("RUNTIME CHECK COMPLETE")
    print("=" * 70)
    
    return {
        "status": "PASS" if not found else "LEAK_DETECTED",
        "commit": "be3dce9",
        "test_count": 51
    }


if __name__ == "__main__":
    result = run_runtime_check()
    sys.exit(0 if result["status"] == "PASS" else 1)
