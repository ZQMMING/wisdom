with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''        if has_yin_cang:
            # 有印藏支，检查食伤是否绝对碾压
            shi_val = shi_dict.get("食伤", 0)
            yin_val = shi_dict.get("印", 0)
            if yin_val > 0 and shi_val / yin_val < 3:
                return None  # 印藏支且食伤未绝对碾压，退回正格'''

new = '''        if has_yin_cang:
            # 有印藏支，检查食伤是否绝对碾压（注意：印已合并为印比键）
            shi_val = shi_dict.get("食伤", 0)
            yin_val = shi_dict.get("印比", 0)  # 印比合并键
            if yin_val > 0 and shi_val / yin_val < 3:
                return None  # 印藏支且食伤未绝对碾压，退回正格'''

content = content.replace(old, new)

with open('engines/cong_ge_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
