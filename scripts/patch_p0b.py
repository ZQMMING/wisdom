# -*- coding: utf-8 -*-
"""P0-b.1补丁：添加kepo_zw和guo_xie的减项，以及_gate_debug调试信息"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r'D:\shuntian-ziping-p0\engines\common\special_pattern.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. 在CONFIRMED_ZW的score部分添加kepo_zw和guo_xie的减项（第359行后插入）
# 第359行: if ganhe_tight: score += 1  # 天干五合紧邻（化气侧要件归位处）
# 插入: if kepo_zw: score -= 3  # P0-b.1: kepo_zw 从硬闸降为减项
# 插入: if guo_xie: score -= 2  # P0-b.1: guo_xie 从硬闸降为减项

# 2. 在CANDIDATE_ZW的score部分添加kepo_zw和guo_xie的减项（第372行后插入）
# 第372行: if ganhe_tight: score += 1  # 天干五合紧邻
# 插入: if kepo_zw: score -= 3  # P0-b.1: kepo_zw 从硬闸降为减项
# 插入: if guo_xie: score -= 2  # P0-b.1: guo_xie 从硬闸降为减项

# 3. 在专旺格判定结束后（第378行后插入），添加_gate_debug调试信息
# 第378行: out['zhuanwang_state'] = 'CANDIDATE'
# 插入: 
#     # P0-b: _gate_debug 调试信息（记录哪一道闸门拒收）
#     gate_debug = []
#     if not gate_ok:
#         if not (gs_ben_zw == 0 and gs_stem == 0 and gs_ju == 0):
#             gate_debug.append(f"官杀闸: gs_ben_zw={gs_ben_zw}, gs_stem={gs_stem}, gs_ju={gs_ju}")
#         if not (cai_ben_zw <= 1 and cai_stem == 0 and cai_ju == 0):
#             gate_debug.append(f"财星闸: cai_ben_zw={cai_ben_zw}, cai_stem={cai_stem}, cai_ju={cai_ju}")
#     if not day_in_row:
#         gate_debug.append(f"day_in_row: day_stem={day_stem}, dm_wx={dm_wx}")
#     if not tougan_row:
#         gate_debug.append(f"tougan_row: dm_stem={dm_stem}")
#     if dm_ju < 1:
#         gate_debug.append(f"dm_ju: {dm_ju} < 1")
#     
#     # P0-b: 输出_gate_debug调试信息
#     out['_gate_debug'] = gate_debug

# 从后往前插入，避免行号变化
# 3. 在第378行后插入_gate_debug调试信息
insert_lines_gate_debug = [
    "\n",
    "    # P0-b: _gate_debug 调试信息（记录哪一道闸门拒收）\n",
    "    gate_debug = []\n",
    "    if not gate_ok:\n",
    "        if not (gs_ben_zw == 0 and gs_stem == 0 and gs_ju == 0):\n",
    "            gate_debug.append(f\"官杀闸: gs_ben_zw={gs_ben_zw}, gs_stem={gs_stem}, gs_ju={gs_ju}\")\n",
    "        if not (cai_ben_zw <= 1 and cai_stem == 0 and cai_ju == 0):\n",
    "            gate_debug.append(f\"财星闸: cai_ben_zw={cai_ben_zw}, cai_stem={cai_stem}, cai_ju={cai_ju}\")\n",
    "    if not day_in_row:\n",
    "        gate_debug.append(f\"day_in_row: day_stem={day_stem}, dm_wx={dm_wx}\")\n",
    "    if not tougan_row:\n",
    "        gate_debug.append(f\"tougan_row: dm_stem={dm_stem}\")\n",
    "    if dm_ju < 1:\n",
    "        gate_debug.append(f\"dm_ju: {dm_ju} < 1\")\n",
    "\n",
    "    # P0-b: 输出_gate_debug调试信息\n",
    "    out['_gate_debug'] = gate_debug\n",
]

# 第378行是CANDIDATE_ZW的最后一行，索引是377
lines[378:378] = insert_lines_gate_debug

# 2. 在CANDIDATE_ZW的score部分添加kepo_zw和guo_xie的减项（第372行后插入）
# 注意：因为前面插入了行，行号会变，所以要重新找
# 找"if ganhe_tight: score += 1  # 天干五合紧邻"（CANDIDATE_ZW的那一行）
for i, line in enumerate(lines):
    if "if ganhe_tight: score += 1  # 天干五合紧邻" in line:
        # 在这一行后插入
        insert_lines = [
            "            if kepo_zw: score -= 3  # P0-b.1: kepo_zw 从硬闸降为减项\n",
            "            if guo_xie: score -= 2  # P0-b.1: guo_xie 从硬闸降为减项\n",
        ]
        lines[i+1:i+1] = insert_lines
        break

# 1. 在CONFIRMED_ZW的score部分添加kepo_zw和guo_xie的减项（第359行后插入）
# 找"if ganhe_tight: score += 1  # 天干五合紧邻（化气侧要件归位处）"
for i, line in enumerate(lines):
    if "if ganhe_tight: score += 1  # 天干五合紧邻（化气侧要件归位处）" in line:
        # 在这一行后插入
        insert_lines = [
            "            if kepo_zw: score -= 3  # P0-b.1: kepo_zw 从硬闸降为减项\n",
            "            if guo_xie: score -= 2  # P0-b.1: guo_xie 从硬闸降为减项\n",
        ]
        lines[i+1:i+1] = insert_lines
        break

# 写回文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ P0-b.1补丁完成：")
print("  - kepo_zw 从硬闸降为减项（score -= 3）")
print("  - guo_xie 从硬闸降为减项（score -= 2）")
print("  - 新增_gate_debug调试信息")
