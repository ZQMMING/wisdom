# -*- coding: utf-8 -*-
import json
with open(r'D:\顺天系统资料\用神案例JSONL\用神专项\DTS滴天髓阐微.jsonl', encoding='utf-8') as f:
    for line in f:
        d = json.loads(line)
        if '丙申己亥庚辰戊寅' in d.get('bazi','').replace(' ',''):
            raw = d.get('raw','')
            idx = raw.find('以火')
            print('位置:', idx)
            for i in range(idx, idx+6):
                ch = raw[i]
                print(f'  [{i}] {repr(ch)} U+{ord(ch):04X}')
            # 测试简单正则
            import re
            print()
            print('测试"以火为用":', re.search(r'以火为用', raw))
            print('测试"以.为用":', re.search(r'以.为用', raw))
            break
