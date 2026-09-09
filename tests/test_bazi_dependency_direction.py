"""P0-FNDR-03 (R-09 ⑦ 十神 audit fix): 依赖方向架构验证。

User 第七轮审计核心要求:
"事实表 → 确定性引擎 → BaziEngine"
而不是: "BaziEngine ↔ 十神引擎"

本测试通过 AST 静态分析验证模块间依赖方向:
1. facts.bazi_facts 不依赖任何 tongshu 上层模块
2. reasoning.bazi_ten_gods 只依赖 facts
3. engines.bazi_engine 依赖 facts 和 reasoning，但不形成循环
"""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def _get_internal_imports(filepath: str) -> list[tuple[int, str, list[str]]]:
    """提取文件中所有 import 内部 tongshu.* 模块的语句 (含相对路径)。"""
    with open(filepath, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            # level > 0 表示相对导入, 一律算内部依赖
            is_relative = node.level > 0
            # 匹配 tongshu.* 绝对导入 或相对导入 (..facts.* 等)
            if module.startswith("tongshu") or is_relative:
                imports.append((node.lineno, module, [n.name for n in node.names]))
        elif isinstance(node, ast.Import):
            for n in node.names:
                if n.name.startswith("tongshu"):
                    imports.append((node.lineno, n.name, []))
    return imports


# 文件路径 (相对 repo root)
# tests/test_bazi_dependency_direction.py -> parents[1] = repo_root
REPO_ROOT = Path(__file__).resolve().parents[1]
FACTS_FILE = REPO_ROOT / "src" / "tongshu" / "facts" / "bazi_facts.py"
TEN_GODS_FILE = REPO_ROOT / "src" / "tongshu" / "reasoning" / "bazi_ten_gods.py"
BAZI_ENGINE_FILE = REPO_ROOT / "src" / "tongshu" / "engines" / "bazi_engine.py"


class TestDependencyDirection(unittest.TestCase):
    """P0-FNDR-03: 验证依赖方向单向无环."""

    def test_01_facts_has_no_internal_dependencies(self):
        """bazi_facts.py 不应 import 任何 tongshu 内部模块。

        这是依赖图最底层的事实层, 必须保持纯净。
        """
        deps = _get_internal_imports(str(FACTS_FILE))
        self.assertEqual(
            deps, [],
            f"bazi_facts.py 不应有 tongshu 内部依赖, 实际: {deps}",
        )

    def test_02_ten_gods_only_depends_on_facts(self):
        """bazi_ten_gods.py 只应依赖 facts 层, 不应反向依赖 engines。

        依赖图: facts → bazi_ten_gods
        """
        deps = _get_internal_imports(str(TEN_GODS_FILE))
        # 允许: from .facts.bazi_facts import ...
        # 允许: from . import ... 同包内
        # 不允许: from ..engines.bazi_engine import ...
        for line, mod, names in deps:
            self.assertNotIn(
                "engines.bazi_engine", mod,
                f"L{line}: bazi_ten_gods.py 不得 import engines.bazi_engine "
                f"(反向依赖会导致循环). Found: {mod}",
            )

    def test_03_bazi_engine_depends_on_facts_and_ten_gods(self):
        """bazi_engine.py 依赖 facts 和 reasoning, 但不形成循环。

        依赖图: facts → bazi_ten_gods → bazi_engine
        单向无环.
        """
        deps = _get_internal_imports(str(BAZI_ENGINE_FILE))
        # 合并模块名用于子串匹配
        joined = " ".join(f"{d[1]}" for d in deps)

        # 必须包含 facts 依赖
        self.assertIn(
            "facts", joined,
            f"bazi_engine.py 必须 import facts 层获取基础事实表. 实际 deps: {deps}",
        )

        # 必须包含 reasoning.bazi_ten_gods 依赖
        self.assertIn(
            "bazi_ten_gods", joined,
            f"bazi_engine.py 必须 import canonical bazi_ten_gods. 实际 deps: {deps}",
        )

    def test_04_no_circular_dependency(self):
        """完整依赖图必须无环。

        检查方法: 加载三个模块, 验证 import 链能完整解析 (无 ImportError)。
        """
        # 清缓存
        import importlib
        for mod_name in list(sys.modules.keys()):
            if mod_name.startswith("tongshu.facts") or \
               mod_name.startswith("tongshu.reasoning.bazi_ten_gods") or \
               mod_name.startswith("tongshu.engines.bazi_engine"):
                del sys.modules[mod_name]

        # 应能干净 import 三个模块, 无 ImportError
        try:
            from tongshu.facts import bazi_facts
            from tongshu.reasoning.bazi_ten_gods import ten_god
            from tongshu.engines.bazi_engine import _ten_god
        except ImportError as e:
            self.fail(f"循环依赖未消除: {e}")

        # 验证同一函数
        self.assertIs(_ten_god, ten_god)


class TestBaziFactsSoleSource(unittest.TestCase):
    """事实层单一来源验证."""

    def test_05_bazi_facts_constants_match(self):
        """bazi_facts 的常量与 bazi_engine 之前定义的内容一致。

        这是验证: 我们把 STEM_ELEMENT 等迁移到 bazi_facts, 但语义未变。
        """
        from tongshu.facts.bazi_facts import (
            STEM_ELEMENT, STEM_POLARITY, BRANCH_ELEMENT,
        )
        from tongshu.engines.bazi_engine import (
            STEM_ELEMENT as ENGINE_SE, STEM_POLARITY as ENGINE_SP,
            BRANCH_ELEMENT as ENGINE_BE,
        )

        self.assertEqual(STEM_ELEMENT, ENGINE_SE)
        self.assertEqual(STEM_POLARITY, ENGINE_SP)
        self.assertEqual(BRANCH_ELEMENT, ENGINE_BE)

    def test_06_bazi_facts_constants_complete(self):
        """bazi_facts 必须提供完整的基础事实表."""
        from tongshu.facts.bazi_facts import (
            HEAVENLY_STEMS, EARTHLY_BRANCHES,
            STEM_ELEMENT, STEM_POLARITY, BRANCH_ELEMENT,
            BRANCH_HIDDEN_STEMS, GENERATES, CONTROLS,
        )
        # 10 天干
        self.assertEqual(len(HEAVENLY_STEMS), 10)
        # 12 地支
        self.assertEqual(len(EARTHLY_BRANCHES), 12)
        # STEM_ELEMENT 完整
        for stem in HEAVENLY_STEMS:
            self.assertIn(stem, STEM_ELEMENT)
            self.assertIn(stem, STEM_POLARITY)
        # BRANCH_ELEMENT 完整
        for branch in EARTHLY_BRANCHES:
            self.assertIn(branch, BRANCH_ELEMENT)
            self.assertIn(branch, BRANCH_HIDDEN_STEMS)
        # 五行 5 个
        self.assertEqual(len(GENERATES), 5)
        self.assertEqual(len(CONTROLS), 5)


class TestEvidenceMetadata(unittest.TestCase):
    """Evidence 元数据."""

    def test_07_evidence_ids_present(self):
        """EVIDENCE_IDS 必须存在."""
        from tongshu.facts.bazi_facts import EVIDENCE_IDS
        self.assertIsInstance(EVIDENCE_IDS, dict)
        self.assertGreater(len(EVIDENCE_IDS), 0)

    def test_08_all_key_facts_have_evidence(self):
        """每个事实常量必须有 evidence id."""
        from tongshu.facts.bazi_facts import EVIDENCE_IDS
        required = {
            "STEM_ELEMENT",
            "STEM_POLARITY",
            "BRANCH_ELEMENT",
            "BRANCH_HIDDEN_STEMS",
            "GENERATES",
            "CONTROLS",
        }
        for key in required:
            self.assertIn(
                key, EVIDENCE_IDS,
                f"事实 {key} 必须在 EVIDENCE_IDS 中标注证据来源",
            )


if __name__ == "__main__":
    unittest.main()
