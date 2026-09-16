# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from tongshu.engines.heluo import canping_lookup
print('=== 1980 wood 寅巳 ===')
r = canping_lookup.lookup('木部', day_zhi='寅', hour_zhi='巳')
print(r['status'], r.get('source'), str(r.get('source_text'))[:40])
print('=== stats ===')
import json
print(json.dumps(canping_lookup.index_stats(), ensure_ascii=False, indent=2))
