# Fix truncated docstring on line 385
path = r"tests\spec\test_production_admission_security.py"
lines = open(path, "r", encoding="utf-8").readlines()
for i, line in enumerate(lines):
    if 'verification failure' in line and line.strip().startswith('"""'):
        lines[i] = '        """Verify identity change breaks hash."""\n'
        print(f"Fixed line {i+1}")
open(path, "w", encoding="utf-8").write("".join(lines))
print("Done")
