# -*- coding: utf-8 -*-
"""P0-b.4补丁：修改gate_debug输出使用cai_stem_zw和gs_stem_zw"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r'D:\shuntian-ziping-p0\engines\common\special_pattern.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 修改gate_debug里的财星闸输出
content = content.replace(
    'gate_debug.append(f"财星闸: cai_ben_zw={cai_ben_zw}, cai_stem={cai_stem}, cai_ju={cai_ju}")',
    'gate_debug.append(f"财星闸: cai_ben_zw={cai_ben_zw}, cai_stem_zw={cai_stem_zw}, cai_ju={cai_ju}")'
)

# 修改gate_debug里的官杀闸输出
content = content.replace(
    'gate_debug.append(f"官杀闸: gs_ben_zw={gs_ben_zw}, gs_stem={gs_stem}, gs_ju={gs_ju}")',
    'gate_debug.append(f"官杀闸: gs_ben_zw={gs_ben_zw}, gs_stem_zw={gs_stem_zw}, gs_ju={gs_ju}")'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ P0-b.4补丁完成：gate_debug输出使用cai_stem_zw和gs_stem_zw")
