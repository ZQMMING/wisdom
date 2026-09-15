# -*- coding: utf-8 -*-
"""关键二态/单值枚举完整定义审查"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

reg = json.load(open(r'D:\shuntian-ziping-p0\governance\enum_registry.json', encoding='utf-8'))
enums = {e['enum_id']: e for e in reg.get('enums', [])}

# 重点审查：与附录L冲突、可能被压缩、单值项
keys = [
    'dts_day_master_strength',   # 衰/旺 —— 附录L是六级，这个可能冲突
    'dts_hua_state',             # 真/假 —— 化/不化 是否缺第三态
    'dts_qing_state',            # 清浊四态（已知多态）—— 对照用
    'dts_shangguan_ge_state',    # 清/浊 —— 是否与 dts_qing_state 冲突
    'dts_wuxing_state',          # 不戾正清和/濁亂偏枯
    'dts_xiang_state',           # 单值 子衆母衰
    'dts_tian_status',           # 单值 全一氣
    'dts_di_status',             # 单值 全三物
    'dts_xing_state',            # 单值 形全
    'dts_cai_guan_state',        # NOT_STRONG/STRONG —— 用户早前裁决过
]
for k in keys:
    e = enums.get(k)
    if not e:
        print('!! 缺失:', k); continue
    print('='*70)
    print('enum_id:', e['enum_id'], '| status:', e['status'])
    print('values:', e['values'])
    print('desc:', e.get('description','')[:300])
    print()
