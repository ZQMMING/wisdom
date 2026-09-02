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

P1.5 update: When iztro is installed, tests should run with real Runtime
(TONGSHU_ALLOW_ZIWEI_STUB unset). The stub is only for development when iztro
is unavailable. See tests/spec/test_p15_shadow_integration.py Gate A.

P2.1-B: Register test authority credential so test fixtures with
authority_source='admission_registry' pass G2 authority check.
"""
import os
from pathlib import Path

# Check if real iztro is available
_project_root = Path(__file__).parent.parent
_iztro_path = _project_root / "node_modules" / "iztro"
_iztro_available = _iztro_path.exists()

if not _iztro_available:
    # Fall back to stub for development
    os.environ.setdefault("TONGSHU_ALLOW_ZIWEI_STUB", "1")


def pytest_configure(config):
    """Register test authority credentials before tests run."""
    from tongshu.assertion.admission_registry import register_authority_credential, clear_authority_credentials
    # Clear any leftover credentials from previous tests
    clear_authority_credentials()
    # Register test authority sources used by production data and test fixtures
    register_authority_credential("admission_registry", "test-cred-hash")
    register_authority_credential("architecture-governance", "arch-gov-cred")
