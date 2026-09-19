# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\scripts\dts_export_csv.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 1. 添加import
old_import = "from engines.common.qtbj_climate_candidates import build_climate_candidates"
new_import = "from engines.common.qtbj_climate_candidates import build_climate_candidates\nfrom engines.common.dayun_xiji import build_dayun_xiji"
content = content.replace(old_import, new_import)

# 2. 在大运处理部分计算大运喜忌 (在dy_clash之后)
old_dy = """        rows.append({'line': li + 1, 'chart': s, 'daymaster': dm, 'month_god': month_god,"""
new_dy = """        # 大运喜忌结构
        dy_xiji = []
        if dy:
            try:
                dx = build_dayun_xiji(p, ye, dy)
                for step in dx['per_step']:
                    dy_xiji.append(f"{step['ganzhi']}:{step['xiji_label']}:{step['ten_god']}")
            except Exception:
                pass
        rows.append({'line': li + 1, 'chart': s, 'daymaster': dm, 'month_god': month_god,"""
content = content.replace(old_dy, new_dy)

# 3. 在dayun_clash之后添加dayun_xiji
old_field = """                     'dayun': '|'.join(dy), 'dayun_spectrum': '|'.join(dy_spec),
                     'dayun_clash': '|'.join(dy_clash)})"""
new_field = """                     'dayun': '|'.join(dy), 'dayun_spectrum': '|'.join(dy_spec),
                     'dayun_clash': '|'.join(dy_clash),
                     'dayun_xiji': '|'.join(dy_xiji)})"""
content = content.replace(old_field, new_field)

# 4. 更新FIELDS
old_fields = """          'dayun', 'dayun_spectrum', 'dayun_clash']"""
new_fields = """          'dayun', 'dayun_spectrum', 'dayun_clash', 'dayun_xiji']"""
content = content.replace(old_fields, new_fields)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('dts_export_csv.py已添加大运喜忌列')
