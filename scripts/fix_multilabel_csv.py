# -*- coding: utf-8 -*-
# 修改dts_export_csv.py增加多标签输出
p1 = r'D:\shuntian-ziping-p0\scripts\dts_export_csv.py'
with open(p1, encoding='utf-8') as f:
    c1 = f.read()

c1 = c1.replace(
    "dy_xiji.append(f\"{step['ganzhi']}:{step['xiji_label']}:{step['ten_god']}\")",
    "labels_str = ','.join(step.get('xiji_labels', [step['xiji_label']]))\n                    dy_xiji.append(f\"{step['ganzhi']}:{step['xiji_label']}:{step['ten_god']}:{labels_str}\")"
)

with open(p1, 'w', encoding='utf-8', newline='') as f:
    f.write(c1)
print('dts_export_csv.py修改完成, 增加多标签输出')

# 修改calc_dayun_xiji_accuracy.py使用多标签匹配
p2 = r'D:\shuntian-ziping-p0\scripts\calc_dayun_xiji_accuracy.py'
with open(p2, encoding='utf-8') as f:
    c2 = f.read()

# 修改engine_xiji解析逻辑, 支持多标签
old_parse = """    engine_xiji = {}
    for item in row.get('dayun_xiji', '').split('|'):
        if ':' in item:
            parts = item.split(':')
            if len(parts) >= 2:
                engine_xiji[parts[0]] = parts[1]"""
new_parse = """    engine_xiji = {}
    engine_xiji_labels = {}
    for item in row.get('dayun_xiji', '').split('|'):
        if ':' in item:
            parts = item.split(':')
            if len(parts) >= 2:
                engine_xiji[parts[0]] = parts[1]
                if len(parts) >= 4:
                    engine_xiji_labels[parts[0]] = parts[3].split(',')
                else:
                    engine_xiji_labels[parts[0]] = [parts[1]]"""
c2 = c2.replace(old_parse, new_parse)

# 修改对齐逻辑, 使用多标签匹配
old_match = """        engine_label = engine_xiji[gz]
        case_total += 1
        total += 1
        
        # 映射: SUPPORT_USE_GOD/SUPPORT_XI_SHEN -> XI; SUPPRESS_USE_GOD -> JI
        engine_xi = engine_label in ('SUPPORT_USE_GOD', 'SUPPORT_XI_SHEN')
        engine_ji = engine_label == 'SUPPRESS_USE_GOD'"""
new_match = """        engine_label = engine_xiji[gz]
        engine_labels = engine_xiji_labels.get(gz, [engine_label])
        case_total += 1
        total += 1
        
        # 映射: SUPPORT_USE_GOD/SUPPORT_XI_SHEN -> XI; SUPPRESS_USE_GOD -> JI
        # 使用多标签匹配: 任何一个标签匹配则匹配
        engine_xi = any(l in ('SUPPORT_USE_GOD', 'SUPPORT_XI_SHEN') for l in engine_labels)
        engine_ji = any(l == 'SUPPRESS_USE_GOD' for l in engine_labels)"""
c2 = c2.replace(old_match, new_match)

with open(p2, 'w', encoding='utf-8', newline='') as f:
    f.write(c2)
print('calc_dayun_xiji_accuracy.py修改完成, 使用多标签匹配')
