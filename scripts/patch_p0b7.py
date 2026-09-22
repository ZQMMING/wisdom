# -*- coding: utf-8 -*-
"""P0-b.7补丁：修从旺格/从杀格并列候选的旧变量名残留"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r'D:\shuntian-ziping-p0\engines\common\special_pattern.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修从旺格并列候选（第431行）
old_text = """        if (_shi(dm) and (yin.get('ben_n',0) >= 1 or yin.get('stem_n',0) >= 1)
                and gs_ben == 0 and gs_stem <= 1 and cai_stem == 0 and not ss_ling):"""

new_text = """        if (_shi(dm) and (yin.get('ben_n',0) >= 1 or yin.get('stem_n',0) >= 1)
                and gs_ben_zw == 0 and gs_stem_zw <= 1 and cai_stem_zw == 0 and not ss_ling):  # P0-b.7: 使用zw版本"""

content = content.replace(old_text, new_text)

# 2. 修从杀格并列候选（第437行）
old_text = """        if (gs_stem >= 1 and cai_ben >= 1 and not ss_ling
                and ss_stem <= 2 and dm_ben_eff <= 1 and yin_ben_eff <= 1):"""

new_text = """        if (gs_stem_zw >= 1 and cai_ben_zw >= 1 and not ss_ling  # P0-b.7: 使用zw版本
                and ss_stem <= 2 and dm_ben_eff <= 1 and yin_ben_eff <= 1):"""

content = content.replace(old_text, new_text)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ P0-b.7补丁完成：")
print("  - 从旺格并列候选：gs_ben→gs_ben_zw, gs_stem→gs_stem_zw, cai_stem→cai_stem_zw")
print("  - 从杀格并列候选：gs_stem→gs_stem_zw, cai_ben→cai_ben_zw")
