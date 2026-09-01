# Replace ALL CJK punctuation in the file
path = r"tests\spec\test_production_admission_security.py"
content = open(path, "r", encoding="utf-8").read()

import unicodedata

# Find all non-ASCII chars in the file
non_ascii = set(c for c in content if ord(c) > 127)
print(f"Non-ASCII chars found: {sorted(non_ascii, key=ord)}")

# Replace all CJK punctuation and symbols
cjk_replacements = {
    "\u3000": " ",    # IDEOGRAPHIC SPACE
    "\u3001": ",",    # 、
    "\u3002": ".",    # 。
    "\u300a": "<",    # 《
    "\u300b": ">",    # 》
    "\u300c": "\"",   # 「
    "\u300d": "\"",   # 」
    "\u300e": "\"",   # 『
    "\u300f": "\"",   # 『
    "\u3010": "[",    # 【
    "\u3011": "]",    # 】
    "\u3008": "<",    # 〈
    "\u3009": ">",    # 〉
    "\u3008": "<",    # 〈
    "\uff01": "!",    # ！
    "\uff02": "=",    # ＂ (not used)
    "\uff03": "#",    # ＃
    "\uff04": "$",    # ＄
    "\uff05": "%",    # ％
    "\uff06": "&",    # ＆
    "\uff07": "'",    # ＇
    "\uff08": "(",    # （
    "\uff09": ")",    # ）
    "\uff0a": "*",    # ＊
    "\uff0b": "+",    # ＋
    "\uff0c": ",",    # ，
    "\uff0d": "-",    # －
    "\uff0e": ".",    # ．
    "\uff0f": "/",    # ／
    "\uff1a": ":",    # ：
    "\uff1b": ";",    # ；
    "\uff1c": "<",    # ＜
    "\uff1d": "=",    # ＝
    "\uff1e": ">",    # ＞
    "\uff1f": "?",    # ？
    "\uff20": "@",    # ＠
    "\uff3b": "[",    # ［
    "\uff3c": "\\",   # ＼
    "\uff3d": "]",    # ］
    "\uff3e": "^",    # ＾
    "\uff3f": "_",    # ＿
    "\uff40": "`",    # ｀
    "\uff5b": "{",    # ［
    "\uff5c": "|",    # ｜
    "\uff5d": "}",    # ］
    "\uff5e": "~",    # ～
    "\u2014": "--",   # —
    "\u2013": "-",    # –
    "\u201c": "\"",   # "
    "\u201d": "\"",   # "
    "\u2018": "'",    # '
    "\u2019": "'",    # '
    "\u2192": "->",   # →
    "\u2190": "<-",   # ←
    "\u2191": "^",    # ↑
    "\u2193": "v",    # ↓
    "\u21d2": "->",   # =>
    "\u21d0": "<-",   # <=
}

for old, new in cjk_replacements.items():
    content = content.replace(old, new)

# Also replace remaining CJK characters with ASCII approximations
remaining = set(c for c in content if ord(c) > 127)
if remaining:
    print(f"Remaining non-ASCII: {sorted(remaining, key=ord)}")
    # Strip all remaining non-ASCII
    content = ''.join(c for c in content if ord(c) <= 127 or c == '\n' or c == '\r' or c == '\t')

open(path, "w", encoding="utf-8").write(content)
print("Done")
