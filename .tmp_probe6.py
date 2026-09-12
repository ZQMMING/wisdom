# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import src.tongshu.engines.blind_judgment as bj
print([n for n in dir(bj) if not n.startswith("_")])
import src.tongshu.engines.blind_themes as bt
print([n for n in dir(bt) if not n.startswith("_")])
