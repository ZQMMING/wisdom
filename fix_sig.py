with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 改函数签名
old_sig = 'def cong_ge_pan(shi_dict: dict, stems: list, day_stem: str, month_branch: str, root_qi_val: float):'
new_sig = 'def cong_ge_pan(shi_dict: dict, stems: list, day_stem: str, month_branch: str, root_qi_val: float, branches: list = None):'
content = content.replace(old_sig, new_sig)

# 改调用处——加branches参数
old_call = 'if _tou_gan(stems, day_wx, "印") and not _yin_xu_tou_bei_zhi(stems, branches, day_wx):'
new_call = 'if _tou_gan(stems, day_wx, "印") and not _yin_xu_tou_bei_zhi(stems, branches or [month_branch], day_wx):'
content = content.replace(old_call, new_call)

with open('engines/cong_ge_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
