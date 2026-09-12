# -*- coding: utf-8 -*-
import hashlib, io
for p in ["cases1980_both.md", "cases1980_both.json"]:
    print(p, "SHA1:", hashlib.sha1(io.open(p,"rb").read()).hexdigest()[:12])
