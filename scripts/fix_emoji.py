# Fix all emoji docstrings that cause pytest AST parse errors
path = r"tests\spec\test_production_admission_security.py"
content = open(path, "r", encoding="utf-8").read()

# Replace all ❌ with [X] in docstrings
import re
content = re.sub(r'"""❌', '"""[X]', content)

open(path, "w", encoding="utf-8").write(content)
print("Fixed emoji docstrings")
