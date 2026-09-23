with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''        if has_chong:
            return None  # 食伤与印星相冲，气势不纯'''

new = '''        if has_chong:
            return None  # 食伤与印星相冲，气势不纯
        
        # 新增：官杀/财星透干破格→退回正格
        guansha_wx = WUXING_OF[day_wx]["官杀"]
        cai_wx = WUXING_OF[day_wx]["财"]
        for i, s in enumerate(stems):
            if i == 2: continue  # 跳过日干
            s_wx = STEM_WUXING.get(s, "")
            if s_wx == guansha_wx or s_wx == cai_wx:
                return None  # 官杀/财星透干破格，退回正格'''

content = content.replace(old, new)

with open('engines/cong_ge_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
