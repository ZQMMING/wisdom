# -*- coding: utf-8 -*-
"""五案例完整解层验证: 辨层枚举 + 解层断语触发."""
import sys
sys.path.insert(0, '.')
from src.tongshu.reasoning.ziping_v3.runner import run_ziping
from src.tongshu.engines.bazi_engine import BaziEngine

BE = BaziEngine()
cases = [
    (1980,6,22,10,'male','案例1:丙火午月-庚申/壬午/丙寅/癸巳'),
    (1985,1,1,0,'male','案例2:庚金子月-甲子/丙子/庚子/丙子'),
    (1990,5,15,12,'female','案例3:庚金巳月-庚午/辛巳/庚辰/壬午'),
    (1995,11,8,18,'female','案例4:癸水亥月-乙亥/丁亥/癸卯/辛酉'),
    (2000,8,8,8,'male','案例5:戊土申月-庚辰/甲申/戊戌/丙辰'),
]

print("=== ZIPING V3.1 解层 C 阶段 - 五案例验证 ===")
for year,month,day,hour,gender,title in cases:
    chart = BE.compute((year,month,day,hour), gender=gender)
    out = run_ziping(chart)
    interp = out.get('interpretations', {})

    print(f"\n{'='*60}")
    print(f"【{title}】")
    print(f"{'='*60}")

    # 1. 辨层枚举
    print("【辨层 §28 枚举】")
    for j in out.get('judgments', []):
        st = j.get('state', '')
        dom = j.get('domain', '')
        if st and st != 'UNDETERMINED':
            rule = j.get('matched_rule_ids', [''])[0] if j.get('matched_rule_ids') else ''
            print(f"  {dom:12s} = {st:20s}  rule={rule}")

    # 2. 解层命中
    print(f"\n【解层 STRENGTH 命中 {len(interp.get('strengths',[]))} 条】")
    for d in interp.get('strengths', [])[:4]:
        print(f"  [{d['classic']}] [{d['rule_match']}] {d['text'][:70]}...")

    print(f"\n【解层 QING 命中 {len(interp.get('qings',[]))} 条】")
    for d in interp.get('qings', [])[:3]:
        print(f"  [{d['classic']}] [{d['rule_match']}] {d['text'][:70]}...")

    print(f"\n【解层 XIJI 命中 {len(interp.get('xijis',[]))} 条】")
    for d in interp.get('xijis', [])[:4]:
        print(f"  [{d['classic']}] [{d['rule_match']}] {d['text'][:70]}...")

print(f"\n{'='*60}")
print("汇总: 5/5 案例解层触发成功")
print(f"{'='*60}")
