"""五部引擎补 Phase 7-10 转发（judgment/golden/provenance/regression/production）。"""
from pathlib import Path

ROOT = Path(r"D:\shuntian-ziping-p0")

ENGINES = ["ziping_zhenquan", "ditiansui", "qiongtong_baojian", "sanming_tonghui", "shenfeng_tongkao"]

FORWARD = {
    "judgment": {
        "judgment_builder.py": (
            '"""Phase 7 Judgment Builder · 转发共享实现（引擎无关，结果结构 duck typing）。"""\n'
            "from __future__ import annotations\n"
            "from engines.yuhai_ziping.judgment.judgment_builder import (  # noqa: F401\n"
            "    JudgmentBuilder, build_assertions, GROUP_LABEL,\n"
            ")\n"),
        "__init__.py": '"""Judgment 层：转发 yuhai_ziping 实现。"""\n',
    },
    "golden": {
        "golden_runner.py": (
            '"""Phase 8 Golden Runner · 转发共享实现（TG/BG registry 引擎无关）。"""\n'
            "from __future__ import annotations\n"
            "from engines.yuhai_ziping.golden.golden_runner import GoldenRunner  # noqa: F401\n"),
        "__init__.py": '"""Golden 层：转发 yuhai_ziping 实现。"""\n',
    },
    "provenance": {
        "provenance.py": (
            '"""Phase 10 Provenance Recorder · 转发共享实现（engine 参数化）。"""\n'
            "from __future__ import annotations\n"
            "from engines.yuhai_ziping.provenance.provenance import ProvenanceRecorder  # noqa: F401\n"),
        "__init__.py": '"""Provenance 层：转发 yuhai_ziping 实现。"""\n',
    },
    "regression": {
        "regression_harness.py": (
            '"""Phase 8 Regression Harness · 转发共享实现（DEMO_CHART 通用）。"""\n'
            "from __future__ import annotations\n"
            "from engines.yuhai_ziping.regression.regression_harness import (  # noqa: F401\n"
            "    DEMO_CHART, normalize, snapshot_all, compare,\n"
            ")\n"),
        "__init__.py": '"""Regression 层：转发 yuhai_ziping 实现。"""\n',
    },
    "production": {
        "admission.py": (
            '"""Phase 10 Production Admission · 转发共享实现（engine 参数化）。"""\n'
            "from __future__ import annotations\n"
            "from engines.yuhai_ziping.production.admission import ProductionAdmission  # noqa: F401\n"),
        "__init__.py": '"""Production 层：转发 yuhai_ziping 实现。"""\n',
    },
}

for eng in ENGINES:
    base = ROOT / "engines" / eng
    for sub, files in FORWARD.items():
        d = base / sub
        d.mkdir(parents=True, exist_ok=True)
        for fname, content in files.items():
            (d / fname).write_text(content, encoding="utf-8")
    print("OK", eng)
print("done")
