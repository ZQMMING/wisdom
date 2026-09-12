# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import src.tongshu.engines.blind_judgment as bj
print([n for n in dir(bj.BlindJudgmentResult) if not n.startswith("_")])
