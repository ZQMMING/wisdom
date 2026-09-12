# -*- coding: utf-8 -*-
import hashlib, io
for p in ["docs/v2/盲派9例对齐验证_V3.4.3.md", "cases15_l2_full.json"]:
    h = hashlib.sha1(io.open(p, "rb").read()).hexdigest()
    print(p, "SHA1:", h[:12])
