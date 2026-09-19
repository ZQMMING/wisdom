# -*- coding: utf-8 -*-
import json, re
with open(r'D:\顺天系统资料\用神案例JSONL\用神专项\DTS滴天髓阐微.jsonl', encoding='utf-8') as f:
    for line in f:
        d = json.loads(line)
        if '丙申己亥庚辰戊寅' in d.get('bazi','').replace(' ',''):
            raw = d.get('raw','')
            m = re.search(r'以([甲乙丙丁戊己庚辛壬癸])为用', raw)
            print('正则匹配:', m.group(1) if m else None)
            # 测试extract_yongshen
            import sys
            sys.path.insert(0, r'D:\shuntian-ziping-p0')
            from scripts.calc_yongshen_all_books import extract_yongshen
            print('extract_yongshen:', extract_yongshen(raw))
            break
