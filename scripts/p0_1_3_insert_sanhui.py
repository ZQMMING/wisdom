"""P0-1.3：插入三会表到 bazi_engine.py"""

filepath = r"D:\shuntian\backend\src\tongshu\engines\bazi_engine.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 找到插入位置：BRANCH_SANHE 结束后，BRANCH_SANXING 开始前
old_marker = '    frozenset({"SI", "YOU", "CHOU"}): "METAL",\n}\n\n# 地支三刑(四组)'

sanhui_block = '''    frozenset({"SI", "YOU", "CHOU"}): "METAL",
}

# 地支三会局(四组) — standard 子平 fixed data.
# P0-1.3：三会组成 + 五行属性（AUTHORIZED，基于滴天髓方位五行）。
# 寅卯辰东方木、巳午未南方火、申酉戌西方金、亥子丑北方水。
# 依据：子平真诠"三方为会"；滴天髓 DTS_0079"寅卯辰属东方木位""巳午未南方火位""亥子丑北方水位"。
# 注意：工程上用"五行属性"而非"化气"（"化气"说法待原典确认，P0-1.2.3 PARTIAL）。
BRANCH_SANHUI = {
    frozenset({"YIN", "MAO", "CHEN"}): "WOOD",
    frozenset({"SI", "WU", "WEI"}): "FIRE",
    frozenset({"SHEN", "YOU", "XU"}): "METAL",
    frozenset({"HAI", "ZI", "CHOU"}): "WATER",
}

# 地支三刑(四组)'''

if old_marker in content:
    content = content.replace(old_marker, sanhui_block)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 三会表已成功插入")
else:
    print("❌ 未找到插入位置")
    # 调试
    idx = content.find("地支三刑")
    if idx >= 0:
        print(f"找到'地支三刑'在位置 {idx}")
        print(repr(content[idx-80:idx+20]))
