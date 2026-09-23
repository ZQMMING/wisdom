with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    # F3 从儿
    if main_family == "食伤":
        if _tou_gan(stems, day_wx, "印"):
            return None  # 枭夺食→不是从儿，退回正格
        
        # 官星透干破格→退回正格（伤官见官）
        guansha_wx = WUXING_OF[day_wx]["官杀"]
        for i, s in enumerate(stems):
            if i == 2: continue  # 跳过日干
            if STEM_WUXING.get(s, "") == guansha_wx:
                return None  # 官星透干破格，退回正格'''

new = '''    # F3 从儿
    if main_family == "食伤":
        if _tou_gan(stems, day_wx, "印"):
            return None  # 枭夺食→不是从儿，退回正格'''

content = content.replace(old, new)

with open('engines/cong_ge_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
