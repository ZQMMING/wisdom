# -*- coding: utf-8 -*-
"""P0-b.2补丁：score接进confidence + _gate_debug补四项"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r'D:\shuntian-ziping-p0\engines\common\special_pattern.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 把score接进confidence
# 当前代码：
# out['zhuanwang_state'] = 'CONFIRMED'
# 
# 需要改成：
# out['zhuanwang_state'] = 'CONFIRMED' if score >= 1 else 'MID'

# 2. _gate_debug补四项
# 在gate_debug里添加：
# - score
# - party
# - dm_ben_eff
# - ganhe_tight

# 先找CONFIRMED_ZW的结尾
content = content.replace(
    "out['zhuanwang'] = zw\n            out['zhuanwang_state'] = 'CONFIRMED'",
    "out['zhuanwang'] = zw\n            out['zhuanwang_state'] = 'CONFIRMED' if score >= 1 else 'MID'"
)

# 再找CANDIDATE_ZW的结尾
content = content.replace(
    "out['zhuanwang'] = zw\n            out['zhuanwang_state'] = 'CANDIDATE'",
    "out['zhuanwang'] = zw\n            out['zhuanwang_state'] = 'CANDIDATE' if score >= 0 else 'LOW'"
)

# 3. _gate_debug补四项
# 在out['_gate_debug'] = gate_debug前添加
content = content.replace(
    "    # P0-b: 输出_gate_debug调试信息\n    out['_gate_debug'] = gate_debug",
    "    # P0-b: _gate_debug补充中间量\n    gate_debug.append(f\"score={score if 'score' in dir() else 'N/A'}\")\n    gate_debug.append(f\"party={party}, dm_ben_eff={dm_ben_eff}, ganhe_tight={ganhe_tight}\")\n    \n    # P0-b: 输出_gate_debug调试信息\n    out['_gate_debug'] = gate_debug"
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ P0-b.2补丁完成：")
print("  - score 接进 confidence（CONFIRMED/MID/CANDIDATE/LOW）")
print("  - _gate_debug 补充中间量（score/party/dm_ben_eff/ganhe_tight）")
