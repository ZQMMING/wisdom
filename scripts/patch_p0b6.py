# -*- coding: utf-8 -*-
"""P0-b.6补丁：修score作用域bug + 修旧变量名残留"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r'D:\shuntian-ziping-p0\engines\common\special_pattern.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修score=0 bug：删除_gate_debug前的score=0初始化
content = content.replace(
    "    # P0-b: score初始化（用于gate_debug）\n    score = 0\n    \n    # P0-b: _gate_debug 调试信息（记录哪一道闸门拒收）",
    "    # P0-b: _gate_debug 调试信息（记录哪一道闸门拒收）"
)

# 2. 修kepo_zw的旧变量名残留（第340行）
content = content.replace(
    "kepo_zw = (gs_ben_zw >= 1 and gs_stem >= 1) or (cai_ben_zw >= 2 and cai_stem >= 1)",
    "kepo_zw = (gs_ben_zw >= 1 and gs_stem_zw >= 1) or (cai_ben_zw >= 2 and cai_stem_zw >= 1)  # P0-b.6: 使用zw版本"
)

# 3. 修gate_debug里的官杀闸旧变量名（第411行）
content = content.replace(
    "if not (gs_ben_zw == 0 and gs_stem == 0 and gs_ju == 0):",
    "if not (gs_ben_zw == 0 and gs_stem_zw == 0 and gs_ju == 0):  # P0-b.6: 使用zw版本"
)

# 4. 修gate_debug里的财星闸旧变量名（第413行）
content = content.replace(
    "if not (cai_ben_zw <= 1 and cai_stem == 0 and cai_ju == 0):",
    "if not (cai_ben_zw <= 1 and cai_stem_zw == 0 and cai_ju == 0):  # P0-b.6: 使用zw版本"
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ P0-b.6补丁完成：")
print("  - 修score作用域bug（删除_gate_debug前的score=0初始化）")
print("  - 修kepo_zw旧变量名残留（gs_stem→gs_stem_zw, cai_stem→cai_stem_zw）")
print("  - 修gate_debug官杀闸旧变量名残留")
print("  - 修gate_debug财星闸旧变量名残留")
