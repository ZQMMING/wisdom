# -*- coding: utf-8 -*-
import io, sys, inspect
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import src.tongshu.engines.bazi_engine as be_mod
print("compute sig:", inspect.signature(be_mod.BaziEngine.compute))
