import subprocess, sys, glob, os
files = sorted(glob.glob("tests/test_blind*.py")) + sorted(glob.glob("tests/test_ziwei*.py"))
print("FILES:", files)
for f in files:
    if "test_blind" in f or True:
        r = subprocess.run([".venv/Scripts/python.exe", "-m", "pytest", f, "-q", "--no-header"], capture_output=True, text=True)
        tail = (r.stdout + r.stderr).strip().splitlines()
        print("="*70)
        print(f, "->", r.returncode)
        print("\n".join(tail[-6:]))
