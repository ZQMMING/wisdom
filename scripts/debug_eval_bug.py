# -*- coding: utf-8 -*-
"""调试评估脚本的比较逻辑bug"""
import csv, re, sys
sys.path.insert(0, r'D:\shuntian-ziping-p0')

csv_path = r'D:\shuntian-ziping-p0\scripts\dts_513_output.csv'
dts_path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'

with open(csv_path, encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

with open(dts_path, encoding='utf-8-sig') as f:
    content = f.read()

# 找案例1: 庚寅壬午丁卯癸卯
target_chart = '庚寅壬午丁卯癸卯'
for row in rows:
    if row['chart'] == target_chart:
        print(f'八字: {row["chart"]}')
        print(f'dayun字段: {row.get("dayun", "")}')
        print(f'dayun_xiji字段: {row.get("dayun_xiji", "")}')
        print()
        
        # 解析engine_xiji
        engine_xiji = {}
        engine_xiji_labels = {}
        for item in row.get('dayun_xiji', '').split('|'):
            if ':' in item:
                parts = item.split(':')
                print(f'  item: {item}')
                print(f'  parts: {parts} (len={len(parts)})')
                if len(parts) >= 2:
                    engine_xiji[parts[0]] = parts[1]
                    if len(parts) >= 4:
                        engine_xiji_labels[parts[0]] = parts[3].split(',')
                    else:
                        engine_xiji_labels[parts[0]] = [parts[1]]
        
        print()
        print(f'engine_xiji: {engine_xiji}')
        print(f'engine_xiji_labels: {engine_xiji_labels}')
        
        # 测试丁亥
        gz = '丁亥'
        if gz in engine_xiji:
            engine_label = engine_xiji[gz]
            engine_labels = engine_xiji_labels.get(gz, [engine_label])
            print(f'\n大运={gz}')
            print(f'  engine_label: {engine_label}')
            print(f'  engine_labels: {engine_labels}')
            
            engine_xi = any(l in ('SUPPORT_USE_GOD', 'SUPPORT_XI_SHEN') for l in engine_labels)
            engine_ji = any(l == 'SUPPRESS_USE_GOD' for l in engine_labels)
            print(f'  engine_xi: {engine_xi}')
            print(f'  engine_ji: {engine_ji}')
        break
