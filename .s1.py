# -*- coding: utf-8 -*-
import io, re
s = io.open(r"盲派Judgment_Evidence母表_V1.md", encoding="utf-8").read()
est = len(re.findall(r"- \*\*STATUS\*\*：ESTABLISHED", s))
inp = len(re.findall(r"- \*\*STATUS\*\*：IN_PROGRESS", s))
not_est = len(re.findall(r"- \*\*STATUS\*\*：NOT_ESTABLISHED", s))
print(f"ESTABLISHED: {est}")
print(f"IN_PROGRESS: {inp}")
print(f"NOT_ESTABLISHED: {not_est}")
