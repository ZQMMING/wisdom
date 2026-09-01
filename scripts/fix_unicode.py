# Fix all non-ASCII characters in docstrings that cause pytest AST parse errors
path = r"tests\spec\test_production_admission_security.py"
content = open(path, "r", encoding="utf-8").read()

# Replace common non-ASCII chars used in docstrings
replacements = {
    "\u274c": "[X]",      # ❌
    "\u2714": "[OK]",     # ✅
    "\u2192": "->",       # ->
    "\u2500": "-",        # bar chars
    "\u2514": "`-",       # corner
}
for old, new in replacements.items():
    content = content.replace(old, new)

open(path, "w", encoding="utf-8").write(content)
print("Fixed all non-ASCII")
