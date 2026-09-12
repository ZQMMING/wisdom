# -*- coding: utf-8 -*-
import io, sys, inspect
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from src.tongshu.engines.blind_judgment import judge_blind, BlindJudgmentEngine
from src.tongshu.engines.blind_themes import aggregate_blind_themes
print("judge_blind:", inspect.signature(judge_blind))
print("aggregate:", inspect.signature(aggregate_blind_themes))
