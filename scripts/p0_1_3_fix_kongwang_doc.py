"""P0-1.3：修复空亡函数注释，移除'力量减半'词汇"""

filepath = r"D:\shuntian\backend\src\tongshu\engines\bazi_engine.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

old_doc = '''    """计算空亡(根据日柱旬). 返回 (空亡地支1, 空亡地支2).
    P0-1.3：空亡作为 Relation Effect Modifier，不是 Strength Evidence。原典未找到"力量减半"依据（NOT_AUTHORIZED），禁止等同力量减半。
    """'''

new_doc = '''    """计算空亡(根据日柱旬). 返回 (空亡地支1, 空亡地支2).
    P0-1.3：空亡作为 Relation Effect Modifier（关系有效性修正），不是 Strength Evidence（强弱证据）。
    原典未找到空亡直接修正五行力量的明确依据（P0-1.2.1 NOT_AUTHORIZED），禁止将空亡等同于力量折减。
    """'''

if old_doc in content:
    content = content.replace(old_doc, new_doc)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 空亡函数注释已修复")
else:
    print("❌ 未找到旧注释")
    # 调试：查找 calc_kong_wang
    idx = content.find("def calc_kong_wang")
    if idx >= 0:
        print(repr(content[idx:idx+300]))
