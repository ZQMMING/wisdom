with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    # F2 从财
    if main_family == "财":
        if _tou_gan(stems, day_wx, "比"):
            return ("从财", "REJECT", "F2①·比劫争财")
        # 印透硬闸：印虚透被制不算破格（印无根+被克）
        if _tou_gan(stems, day_wx, "印") and not _yin_xu_tou_bei_zhi(stems, branches or [month_branch], day_wx):
            return ("从财", "REJECT", "F2②·印透生身")'''

new = '''    # F2 从财
    if main_family == "财":
        if _tou_gan(stems, day_wx, "比"):
            return None  # 比劫争财→不是从财，退回正格
        # 印透硬闸：印虚透被制不算破格（印无根+被克）
        if _tou_gan(stems, day_wx, "印") and not _yin_xu_tou_bei_zhi(stems, branches or [month_branch], day_wx):
            return None  # 印透生身→不是从财，退回正格'''

content = content.replace(old, new)

# F1/F3同理——硬闸退回正格，不是判REJECT
old2 = '''    # F1 从杀
    if main_family == "官杀":
        # 硬闸① 印透化煞（只看透干，藏印不拦）
        if _tou_gan(stems, day_wx, "印"):
            return ("从杀", "REJECT", "F1①·印透化煞")'''

new2 = '''    # F1 从杀
    if main_family == "官杀":
        # 硬闸① 印透化煞（只看透干，藏印不拦）
        if _tou_gan(stems, day_wx, "印"):
            return None  # 印透化煞→不是从杀，退回正格'''

content = content.replace(old2, new2)

old3 = '''    # F3 从儿
    if main_family == "食伤":
        if _tou_gan(stems, day_wx, "印"):
            return ("从儿", "REJECT", "F3①·枭夺食")'''

new3 = '''    # F3 从儿
    if main_family == "食伤":
        if _tou_gan(stems, day_wx, "印"):
            return None  # 枭夺食→不是从儿，退回正格'''

content = content.replace(old3, new3)

with open('engines/cong_ge_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
