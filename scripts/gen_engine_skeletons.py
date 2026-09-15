"""生成五部引擎骨架（Phase 1 结构 §60）：__init__ / contract.json / validator.py / calculation 转发 / tests。"""
import json
import shutil
from pathlib import Path

ROOT = Path(r"D:\shuntian-ziping-p0")
YHZP = ROOT / "engines" / "yuhai_ziping"

ENGINES = [
    ("ziping_zhenquan", "ZIPING_ZHENQUAN"),
    ("ditiansui", "DITIANSUI"),
    ("qiongtong_baojian", "QIONGTONG_BAOJIAN"),
    ("sanming_tonghui", "SANMING_TONGHUI"),
    ("shenfeng_tongkao", "SHENFENG_TONGKAO"),
]

for dirname, eid in ENGINES:
    d = ROOT / "engines" / dirname
    (d / "calculation" / "tests").mkdir(parents=True, exist_ok=True)
    (d / "rule").mkdir(parents=True, exist_ok=True)
    (d / "evidence").mkdir(parents=True, exist_ok=True)

    # __init__.py
    (d / "__init__.py").write_text(
        f'"""子平引擎族 · {dirname}（{eid}）· V2.2.2 FINAL。\n'
        f'共享计算层 engines/common（L0 映射/事实管线/EngineResult）；\n'
        f'Rule/Evidence 由 engines/yuhai_ziping 参数化实现（RuleEngine/EvidenceRegistry(engine=...)）。\n'
        f'Phase 6+ 各引擎自有派生（格局/旺衰/气势/病药等）在本引擎目录内实现。"""\n\n'
        f'ENGINE_ID = "{eid}"\nENGINE_VERSION = "0.1.0"\nCONTRACT_VERSION = "0.1.0"\n'
        f'__all__ = ["ENGINE_ID", "ENGINE_VERSION", "CONTRACT_VERSION"]\n',
        encoding="utf-8")

    # contract.json（复制 yuhai_ziping，改 engine 字段）
    c = json.loads((YHZP / "contract.json").read_text(encoding="utf-8"))
    c["engine"] = eid
    c["dependency"]["notes"] = f"§K-1 {eid} 仅允许 L0 core facts + L1 Knowledge Registry；禁读 L2B/L2C/L2D/L2E/L3/L4/L5/L6"
    (d / "contract.json").write_text(json.dumps(c, ensure_ascii=False, indent=2), encoding="utf-8")

    # validator.py（复制，ENGINE_DIR 自动定位本引擎 contract）
    shutil.copyfile(YHZP / "validator.py", d / "validator.py")

    # calculation/__init__.py：转发共享 FactsBuilder
    (d / "calculation" / "__init__.py").write_text(
        '"""计算层：转发共享 FactsBuilder（engine 参数化）。"""\n'
        'from __future__ import annotations\n'
        'from engines.common.facts_builder import FactsBuilder  # noqa: F401\n',
        encoding="utf-8")

    # rule/evidence/__init__.py 占位
    for sub in ("rule", "evidence"):
        (d / sub / "__init__.py").write_text(
            f'"""Rule/Evidence 层：由 engines/yuhai_ziping 参数化实现（RuleEngine/EvidenceRegistry(engine=...)）。"""\n',
            encoding="utf-8")

    # tests/test_engine_skeleton.py
    (d / "tests").mkdir(parents=True, exist_ok=True)
    (d / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (d / "tests" / "test_engine_skeleton.py").write_text(
        f'"""Phase 1 Skeleton 测试（§60）· {dirname}。"""\n'
        "from __future__ import annotations\n\n"
        "import sys\n"
        "from pathlib import Path\n\n"
        "import pytest\n\n"
        f"ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent\n"
        "sys.path.insert(0, str(ROOT))\n\n"
        "from engines.common.facts_builder import FactsBuilder, ENGINE_ID_MAP\n"
        "from engines.yuhai_ziping.rule.rule_engine import RuleEngine\n"
        "from engines.yuhai_ziping.evidence.evidence_registry import EvidenceRegistry\n\n"
        f'ENGINE = "{dirname}"\n'
        f'ENGINE_ID = "{eid}"\n\n\n'
        "def test_engine_id():\n"
        '    from importlib import import_module\n'
        '    m = import_module(f"engines.{ENGINE}")\n'
        '    assert m.ENGINE_ID == ENGINE_ID\n\n\n'
        "def test_contract_loads():\n"
        "    import json\n"
        "    c = json.load(open(ROOT / 'engines' / ENGINE / 'contract.json', encoding='utf-8'))\n"
        "    assert c['engine'] == ENGINE_ID\n"
        "    assert c['input']['allowed_fields']\n\n\n"
        "def test_facts_builder_engine_param():\n"
        "    fb = FactsBuilder(engine=ENGINE)\n"
        "    assert fb.engine_id == ENGINE_ID\n"
        "    assert len(fb.rules.rules) > 0\n\n\n"
        "def test_registry_load():\n"
        "    eng = RuleEngine(engine=ENGINE)\n"
        "    evd = EvidenceRegistry(engine=ENGINE)\n"
        "    assert len(eng.source_grade) > 0\n"
        "    assert evd.record_count > 0\n\n\n"
        "def test_empty_chart_smoke():\n"
        "    fb = FactsBuilder(engine=ENGINE)\n"
        "    r = fb.build({'canonical_input': {'ref': 'smoke', 'hash': 'x' * 12}})\n"
        "    assert r.engine == ENGINE_ID\n"
        "    assert set(r.to_dict()['facts'].keys()) == {\n"
        "        'ten_god_facts', 'six_relative_facts', 'palace_facts',\n"
        "        'basic_structure_facts', 'geju_candidates', 'relation_facts'}\n",
        encoding="utf-8")

    print("OK", dirname, eid)
print("done")
