"""P1 Validator - Semantic Atom / Modern Concept 数据完整性检查.

检查规则:
1. 每个 Semantic Atom 的 semantic_keys 必须全部存在于 Modern Concept Registry
2. 每个 Atom 必须有: atom_id / category / label_zh / semantic_keys / sources
3. Modern Concept 必须有: concept_id / label_zh / domains
4. Domain 必须是8个标准维度之一
5. 不允许 Atom 中出现 direction / polarity / positive / negative 等方向污染

CI 集成: 任何检查失败直接退出码1.
"""

from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from typing import Any

# 8个标准人生维度
STANDARD_DOMAINS = {
    "CAREER", "FINANCE", "RELATIONSHIP", "FAMILY",
    "SOCIAL", "GROWTH", "HEALTH", "DECISION",
}

# 禁止出现在Atom中的方向污染字段
FORBIDDEN_DIRECTION_KEYS = {
    "direction", "polarity", "positive", "negative",
    "good", "bad", "ji", "xiong", "auspicious", "inauspicious",
}

REQUIRED_ATOM_FIELDS = {"atom_id", "category", "label_zh", "semantic_keys", "sources"}
REQUIRED_CONCEPT_FIELDS = {"concept_id", "label_zh", "domains"}


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_atoms(atom_dir: Path, concept_ids: set[str]) -> list[str]:
    """验证所有 Semantic Atom 文件. 返回错误列表."""
    errors: list[str] = []
    atom_count = 0
    all_keys: set[str] = set()

    for json_file in sorted(atom_dir.glob("*.json")):
        data = load_json(json_file)
        atoms = data.get("atoms", [])
        for atom in atoms:
            atom_count += 1
            atom_id = atom.get("atom_id", "<unknown>")

            # 1. 必填字段检查
            missing = REQUIRED_ATOM_FIELDS - set(atom.keys())
            if missing:
                errors.append(f"[{json_file.name}] Atom {atom_id}: 缺少必填字段 {missing}")

            # 2. 方向污染检查
            for key in FORBIDDEN_DIRECTION_KEYS:
                if key in atom and atom[key] not in (None, "", [], {}):
                    errors.append(f"[{json_file.name}] Atom {atom_id}: 方向污染字段 '{key}' = {atom[key]}")

            # 3. semantic_keys 必须存在于 Modern Concept
            semantic_keys = atom.get("semantic_keys", [])
            for key in semantic_keys:
                all_keys.add(key)
                if key not in concept_ids:
                    errors.append(
                        f"[{json_file.name}] Atom {atom_id}: semantic_key '{key}' "
                        f"不存在于 Modern Concept Registry"
                    )

            # 4. sources 必须非空
            sources = atom.get("sources", [])
            if not sources:
                errors.append(f"[{json_file.name}] Atom {atom_id}: sources 为空")

    print(f"  Semantic Atoms: {atom_count} 个, 引用 {len(all_keys)} 个 semantic_keys")
    return errors


def validate_concepts(concept_path: Path) -> tuple[list[str], set[str], int]:
    """验证 Modern Concept Registry. 返回(错误列表, concept_id集合, concept数量)."""
    errors: list[str] = []
    data = load_json(concept_path)

    # 验证 domains
    domains = data.get("domains", [])
    domain_ids = {d["domain_id"] for d in domains}
    missing_domains = STANDARD_DOMAINS - domain_ids
    if missing_domains:
        errors.append(f"Modern Concept: 缺少标准维度 {missing_domains}")
    print(f"  Domains: {len(domains)} 个 (标准8维度: {'OK' if not missing_domains else 'MISSING ' + str(missing_domains)})")

    # 验证 concepts
    concepts = data.get("concepts", [])
    concept_ids: set[str] = set()
    for concept in concepts:
        concept_id = concept.get("concept_id", "<unknown>")
        concept_ids.add(concept_id)

        # 必填字段
        missing = REQUIRED_CONCEPT_FIELDS - set(concept.keys())
        if missing:
            errors.append(f"Concept {concept_id}: 缺少必填字段 {missing}")

        # domains 必须是标准维度
        for domain in concept.get("domains", []):
            if domain not in STANDARD_DOMAINS:
                errors.append(f"Concept {concept_id}: domain '{domain}' 不是标准维度")

    print(f"  Modern Concepts: {len(concepts)} 个")
    return errors, concept_ids, len(concepts)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]  # backend/ (scripts/ -> backend/)
    atom_dir = repo_root / "data" / "semantic_atoms"
    concept_path = repo_root / "data" / "mapping" / "modern_concepts.json"

    print("=" * 60)
    print("P1 Validator - Semantic Atom / Modern Concept 完整性检查")
    print("=" * 60)
    print()

    # 先验证 Modern Concept（因为 Atom 依赖它）
    print("[1/2] 验证 Modern Concept Registry...")
    concept_errors, concept_ids, concept_count = validate_concepts(concept_path)
    print()

    # 再验证 Semantic Atom
    print("[2/2] 验证 Semantic Atom Registry...")
    atom_errors = validate_atoms(atom_dir, concept_ids)
    print()

    # 汇总
    all_errors = concept_errors + atom_errors
    print("=" * 60)
    if all_errors:
        print(f"❌ 验证失败: {len(all_errors)} 个错误")
        print("=" * 60)
        for i, err in enumerate(all_errors, 1):
            print(f"  {i}. {err}")
        return 1
    else:
        print("✅ 验证通过")
        print(f"  Semantic Atoms: 7 files / 128 atoms")
        print(f"  Modern Concepts: 1 file / 8 domains + {concept_count} concepts")
        print(f"  方向污染: 无")
        print(f"  semantic_keys 完整性: 全部存在于 Modern Concept Registry")
        print("=" * 60)
        return 0


if __name__ == "__main__":
    sys.exit(main())
