# -*- coding: utf-8 -*-
"""ZIPING V3.1 解层全量 15 维 - 五案例端到端验证.

链路: 八字排盘 (BaziEngine) → 子平辨层 (§28 枚举) → 解层断语触发 (五经 11478 条)
"""
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

DOMAIN_ORDER = ['ling', 'growth', 'root', 'party', 'strength', 'qing',
                'climate', 'tongguan', 'disease', 'qi',
                'pattern', 'pattern_quality', 'true', 'special',
                'yong', 'xiang', 'xiji', 'temporal']

print('=== ZIPING V3.1 解层全量 (15域) - 五案例端到端验证 ===')
grand_total = 0
for year,month,day,hour,gender,title in cases:
    chart = BE.compute((year,month,day,hour), gender=gender)
    out = run_ziping(chart)
    interp = out.get('interpretations', {})
    
    # 辨层枚举
    diag_states = {}
    for j in out.get('judgments', []):
        dom = getattr(j, 'domain', j.get('domain','')) if hasattr(j,'domain') or isinstance(j,dict) else ''
        st = getattr(j, 'state', j.get('state','')) if hasattr(j,'domain') or isinstance(j,dict) else ''
        if st and str(st) != 'UNDETERMINED':
            diag_states[dom] = st
    
    sep = "=" * 72
    print(f'\n{sep}')
    print(f'【{title}】')
    print(f'{sep}')
    
    # 辨层
    print('[辨层 §28 枚举]')
    for dom, st in diag_states.items():
        print(f'  {dom:15s} = {st}')
    
    # 解层
    total_hits = 0
    print(f'\n[解层 五经断语触发]')
    for field in DOMAIN_ORDER:
        hits = interp.get(field, [])
        total_hits += len(hits)
        if hits:
            sample = hits[0]
            text = sample.get('text', '')[:50] if isinstance(sample, dict) else str(sample)[:50]
            cls = sample.get('classic', '?') if isinstance(sample, dict) else '?'
            print(f'  {field:15s}: {len(hits):3d}条 [{cls}] {text}...')
    
    # 未实现域
    undet = interp.get('undetermined_domains', [])
    if undet:
        print(f'\n  fail-closed 域: {", ".join(undet)}')
    
    print(f'\n  ═ 解层断语命中: {total_hits} 条')
    grand_total += total_hits

sep2 = "=" * 72
print(f'\n{sep2}')
print(f'汇总: 5 案例 | 解层断语命中总计: {grand_total} 条')
print(f'      断语库: 11,478 条 (五部经典: 渊海4549+三命2967+滴天髓2672+真诠645+宝鉴645)')
print(f'      可触发: ~7,805 条 (68%, 含若/如/见/逢/忌/喜等条件钩子)')
print(f'{sep2}')
