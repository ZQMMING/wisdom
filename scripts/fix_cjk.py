# Replace all CJK punctuation in docstrings
path = r"tests\spec\test_production_admission_security.py"
content = open(path, "r", encoding="utf-8").read()

# CJK punctuation replacements
replacements = {
    "\u3002": ".",    # 。
    "\uff01": "!",    # ！
    "\uff1f": "?",    # ？
    "\uff0c": ",",    # ，
    "\u2014": "--",   # —
    "\u201c": '"',    # "
    "\u201d": '"',    # "
    "\u2018": "'",    # '
    "\u2019": "'",    # '
    "\u300a": "<",    # 《
    "\u300b": ">",    # 》
}
for old, new in replacements.items():
    content = content.replace(old, new)

open(path, "w", encoding="utf-8").write(content)
print("Fixed CJK punctuation")
