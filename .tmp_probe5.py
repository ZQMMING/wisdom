# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import src.tongshu.engines.bazi_engine as be_mod
print([n for n in dir(be_mod) if "Chart" in n or "Pillar" in n or "compute" in n])
import inspect
print(inspect.signature(be_mod.BaziChart.__init__))
