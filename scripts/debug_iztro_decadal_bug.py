#!/usr/bin/env python3
"""Debug script to reproduce iztro decadal direction bug.

This script demonstrates that iztro's decadal direction calculation
is systematically wrong for all four yin-yang combinations.
"""

import subprocess
import json
import sys
from pathlib import Path

def run_iztro_test(name, solar_date, hour, gender):
    """Run iztro and return decadal direction."""
    # Convert to time index
    if hour == 23:
        ti = 12
    elif hour in (0, 24):
        ti = 0
    else:
        ti = ((hour + 1) // 2) % 12
    
    script = f'''
const {{ bySolar }} = require('iztro').astro;
const a = bySolar('{solar_date}', {ti}, '{gender}', false);
const decadalMap = {{}};
for (const p of a.palaces) {{
    if (p.decadal && p.decadal.range) {{
        decadalMap[p.decadal.range[0]] = p.name;
    }}
}}
const order = Object.keys(decadalMap).sort((a,b) => a-b).map(k => decadalMap[k]);
const second = order[1] || '';
const dir = second === '兄弟' ? 'forward' : 'reverse';
console.log(JSON.stringify({{
    dir: dir,
    second_palace: second,
    order: order
}}));
'''
    
    result = subprocess.run(
        ['node', '-e', script],
        capture_output=True,
        text=True,
        encoding='utf-8',
        cwd=str(Path(__file__).parent.parent / 'node_modules'),
        timeout=20,
    )
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return None
    
    return json.loads(result.stdout)


def get_traditional_direction(year, gender):
    """Compute expected direction from traditional rules.
    
    Rule: 阳男阴女顺，阴男阳女逆
    Based on year stem yin/yang, NOT branch.
    """
    STEMS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    YANG_STEMS = {'甲', '丙', '戊', '庚', '壬'}
    
    stem = STEMS[(year - 4) % 10]
    stem_yinyang = 'yang' if stem in YANG_STEMS else 'yin'
    
    if stem_yinyang == 'yang' and gender == 'male':
        return 'forward'
    elif stem_yinyang == 'yang' and gender == 'female':
        return 'reverse'
    elif stem_yinyang == 'yin' and gender == 'male':
        return 'reverse'
    else:  # yin + female
        return 'forward'


def main():
    print("=" * 70)
    print("IZTRO DECADAL DIRECTION BUG REPRODUCTION")
    print("=" * 70)
    print()
    
    # Test cases covering all 4 combinations
    cases = [
        ("阳男甲辰", "2024-2-10", 12, "male"),      # 甲(阳) + male → should be 顺
        ("阳女甲辰", "2024-2-10", 12, "female"),    # 甲(阳) + female → should be 逆
        ("阴男乙巳", "2025-2-10", 12, "male"),      # 乙(阴) + male → should be 逆
        ("阴女乙巳", "2025-2-10", 12, "female"),    # 乙(阴) + female → should be 顺
    ]
    
    all_passed = True
    
    for name, date, hour, gender in cases:
        year = int(date.split('-')[0])
        expected = get_traditional_direction(year, gender)
        result = run_iztro_test(name, date, hour, gender)
        
        if result is None:
            print(f"{name}: ERROR - could not run iztro")
            all_passed = False
            continue
        
        actual = result['dir']
        match = (actual == expected)
        
        if not match:
            all_passed = False
        
        status = "✓ PASS" if match else "✗ FAIL"
        
        print(f"{name}:")
        print(f"  Year: {year}, Gender: {gender}")
        print(f"  Expected: {expected} (传统规则)")
        print(f"  Actual: {actual} (iztro输出)")
        print(f"  Second palace: {result['second_palace']}")
        print(f"  {status}")
        print()
    
    print("=" * 70)
    if all_passed:
        print("All tests passed (unexpected!)")
        sys.exit(0)
    else:
        print("CONFIRMED: iztro decadal direction bug affects ALL cases")
        sys.exit(1)


if __name__ == "__main__":
    main()
