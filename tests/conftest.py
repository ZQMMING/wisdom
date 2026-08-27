# -*- coding: utf-8 -*-
"""Global test fixtures.

Ziwei stub opt-in (B-03a guard): iztro is not installed in the dev/test
environment, and the production guard raises ZiweiEngineUnavailableError unless
TONGSHU_ALLOW_ZIWEI_STUB=1. Individual suites were setting this env themselves;
suites that reach the ziwei engine transitively (api/pipeline/canonical tests)
were missed, causing 35 failures in clean environments. Centralizing it here so
every test runs with the same engine availability assumptions.

This does NOT weaken any test semantics: the stub behavior itself is identical;
only the env gate is satisfied. Production default remains fail-closed.
"""
import os

os.environ.setdefault("TONGSHU_ALLOW_ZIWEI_STUB", "1")
