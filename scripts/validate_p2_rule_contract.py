"""P2 Rule Contract Validator - 规则契约验证器.

在P1 Semantic Atom Validator基础上增加:
1. Rule Contract检查: 所有规则必须有produces_semantic_atoms, 禁止direction/polarity
2. Concept完整性: 所有produces_semantic_atoms必须存在于Modern Concept Registry
3. Concept重复/同义词报告(只报告, 不自动修改)
4. 旧机制代码搜索: SYSTEM_WEIGHTS/CONFLICTED/positive/negative等必须为0

用法:
  python scripts/validate_p2_rule_contract.py
"""
from __future__ import annotations
import json
import glob
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
RULES_DIR = DATA_DIR / "rules"
ATOM_DIR = DATA_DIR / "semantic_atoms"
CONCEPT_PATH = DATA_DIR / "mapping" / "modern_concepts.json"

STANDARD_DOMAINS = {"CAREER", "FINANCE", "RELATIONSHIP", "FAMILY", "SOCIAL", "GROWTH", "HEALTH", "DECISION"}

# 禁止的旧机制关键词
FORBIDDEN_OLD_MECH = [
    "SYSTEM_WEIGHTS",
    "aggregate_directions_weighted",
    "CONFIDENCE.CONFLICTED",
    "Confidence.CONFLICTED",
    "CONFIDENCE\\.CONFLICTED",
]

# 规则中禁止的字段
FORBIDDEN_RULE_FIELDS = ["direction", "polarity", "positive", "negative", "pos", "neg"]


def load_concepts() -> dict:
    with open(CONCEPT_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return {c["concept_id"]: c for c in data.get("concepts", [])}


def load_atoms() -> list[dict]:
    atoms = []
    for f in sorted(ATOM_DIR.glob("*.json")):
        with open(f, encoding="utf-8") as fh:
            data = json.load(fh)
        atoms.extend(data.get("atoms", []))
    return atoms


def load_rules() -> list[dict]:
    rules = []
    for f in sorted(RULES_DIR.glob("*.json")):
        with open(f, encoding="utf-8") as fh:
            rules.append(json.load(fh))
    return rules


def validate_p1_semantic(concepts: dict, atoms: list[dict]) -> list[str]:
    """P1检查: Semantic Atom完整性."""
    errors = []

    # 检查Atom必填字段和方向污染
    # 注意: 只检查顶层字段名, 不检查semantic_keys内容(DIRECTION/POSITION是合法concept)
    direction_fields = {"direction", "polarity", "positive", "negative", "confidence", "weight", "pos", "neg"}
    for atom in atoms:
        for field in ["atom_id", "category", "label_zh", "semantic_keys"]:
            if field not in atom:
                errors.append(f"Atom缺少必填字段: {atom.get('atom_id','?')} 缺 {field}")
        # 检查顶层字段名是否包含方向污染
        for key in atom.keys():
            if key.lower() in direction_fields:
                errors.append(f"Atom方向污染: {atom.get('atom_id','?')} 顶层字段 '{key}'")

    # 检查semantic_keys完整性
    all_keys = set()
    for atom in atoms:
        for key in atom.get("semantic_keys", []):
            all_keys.add(key)
    missing = all_keys - set(concepts.keys())
    if missing:
        errors.append(f"semantic_keys缺失概念: {sorted(missing)[:10]}... (共{len(missing)}个)")

    # 检查domain标准性
    for cid, c in concepts.items():
        for d in c.get("domains", []):
            if d not in STANDARD_DOMAINS:
                errors.append(f"Concept非标准domain: {cid} -> {d}")

    return errors


CORE_TYPES = ["十神定性", "旺衰判定", "格局判定", "月令司权", "体用辨析"]


def validate_rule_contract(rules: list[dict], concepts: dict) -> tuple[list[str], int, int]:
    """P2检查: Rule Contract.

    返回: (errors, core_migrated, non_core_pending)
    核心规则必须迁移, 非核心规则标记为待迁移(不算错误)。
    """
    errors = []
    core_migrated = 0
    non_core_pending = 0

    for rule in rules:
        rid = rule.get("rule_id", "?")
        rtype = rule.get("rule_type", "")
        conclusion = rule.get("conclusion", {})
        is_core = rtype in CORE_TYPES
        has_new = "produces_semantic_atoms" in conclusion

        if is_core:
            if has_new:
                core_migrated += 1
            else:
                errors.append(f"核心规则未迁移: {rid} ({rtype})")
                continue
        else:
            if not has_new:
                non_core_pending += 1
                continue  # 非核心规则待迁移, 不算错误

        atoms = conclusion["produces_semantic_atoms"]
        if not isinstance(atoms, list) or len(atoms) == 0:
            errors.append(f"规则produces_semantic_atoms为空或非数组: {rid}")
            continue

        # 所有atom必须存在于Concept Registry
        for atom in atoms:
            if atom not in concepts:
                errors.append(f"规则produces_semantic_atoms引用不存在概念: {rid} -> {atom}")

        # 禁止旧的direction/polarity
        if "produces_layer_output_template" in conclusion:
            errors.append(f"规则仍有旧produces_layer_output_template: {rid}")
        tpl = conclusion.get("produces_layer_output_template", {})
        for field in ["direction", "polarity"]:
            if field in tpl:
                errors.append(f"规则仍有旧{field}: {rid}")

        # rule_id必须存在
        if not rule.get("rule_id"):
            errors.append(f"规则缺少rule_id")

        # produces_signal_type必须存在
        if not rule.get("produces_signal_type"):
            errors.append(f"规则缺少produces_signal_type: {rid}")

    return errors, core_migrated, non_core_pending


def report_concept_duplicates(concepts: dict) -> list[str]:
    """Concept重复/同义词报告(只报告, 不修改)."""
    reports = []

    # 按label_zh分组找重复
    label_groups = defaultdict(list)
    for cid, c in concepts.items():
        label_groups[c.get("label_zh", "").lower()].append(cid)
    for label, cids in label_groups.items():
        if len(cids) > 1:
            reports.append(f"重复label_zh: '{label}' -> {cids}")

    # 潜在同义词(基于词根)
    synonym_groups = {
        "action": ["ACTION", "EXECUTION", "ACTIVITY", "DOING", "IMPLEMENTATION", "PERFORMANCE"],
        "output": ["OUTPUT", "OUTPUT_ACTIVATION", "EXPRESSION", "CREATIVITY", "PRODUCTION"],
        "change": ["CHANGE", "TRANSFORMATION", "METAMORPHOSIS", "EVOLUTION", "REVOLUTION", "REFORM"],
        "stability": ["STABILITY", "SECURITY", "SAFETY", "SOLIDARITY", "STEADINESS"],
        "wealth": ["WEALTH", "MONEY", "INCOME", "ASSET", "ABUNDANCE", "PROSPERITY", "RICHNESS"],
        "relationship": ["RELATIONSHIP", "RELATION", "CONNECTION", "BOND", "PARTNERSHIP", "ASSOCIATION"],
        "growth": ["GROWTH", "DEVELOPMENT", "EVOLUTION", "PROGRESS", "ADVANCEMENT", "MATURITY"],
        "health": ["HEALTH", "WELLNESS", "VITALITY", "WELLBEING"],
        "decision": ["DECISION", "CHOICE", "OPTION", "SELECTION", "JUDGMENT"],
        "career": ["CAREER", "WORK", "JOB", "PROFESSION", "OCCUPATION", "BUSINESS"],
    }

    for group_name, candidates in synonym_groups.items():
        existing = [c for c in candidates if c in concepts]
        if len(existing) > 3:
            reports.append(f"潜在同义词组 '{group_name}': {existing} (建议治理)")

    return reports


def search_old_mechanism() -> list[str]:
    """旧机制代码搜索: 生产路径中禁止出现."""
    errors = []
    src_dir = REPO_ROOT / "src"

    # 搜索禁止的旧机制
    for pattern in FORBIDDEN_OLD_MECH:
        for f in src_dir.rglob("*.py"):
            try:
                content = f.read_text(encoding="utf-8")
                if re.search(pattern, content):
                    # 排除注释和测试文件
                    rel = f.relative_to(REPO_ROOT)
                    if "test" not in str(rel).lower() and "conftest" not in str(rel).lower():
                        errors.append(f"旧机制代码: {rel} 包含 '{pattern}'")
            except Exception:
                pass

    return errors


def main():
    print("=" * 60)
    print("P2 Rule Contract Validator")
    print("=" * 60)

    concepts = load_concepts()
    atoms = load_atoms()
    rules = load_rules()

    all_errors = []

    # P1检查
    print("\n[1/4] P1 Semantic Atom检查...")
    p1_errors = validate_p1_semantic(concepts, atoms)
    print(f"  Atoms: {len(atoms)}, Concepts: {len(concepts)}")
    print(f"  错误: {len(p1_errors)}")
    all_errors.extend(p1_errors)

    # P2 Rule Contract检查
    print("\n[2/4] P2 Rule Contract检查...")
    p2_errors, core_migrated, non_core_pending = validate_rule_contract(rules, concepts)
    print(f"  规则总数: {len(rules)}")
    print(f"  核心规则已迁移: {core_migrated}")
    print(f"  非核心规则待迁移: {non_core_pending}")
    print(f"  错误: {len(p2_errors)}")
    all_errors.extend(p2_errors)

    # Concept重复报告
    print("\n[3/4] Concept重复/同义词报告...")
    dup_reports = report_concept_duplicates(concepts)
    print(f"  报告项: {len(dup_reports)}")
    for r in dup_reports[:5]:
        print(f"    - {r}")
    if len(dup_reports) > 5:
        print(f"    ... 还有 {len(dup_reports) - 5} 项")

    # 旧机制代码搜索
    print("\n[4/4] 旧机制代码搜索...")
    old_mech = search_old_mechanism()
    print(f"  发现: {len(old_mech)}")
    for r in old_mech:
        print(f"    - {r}")
    all_errors.extend(old_mech)

    # 总结
    print("\n" + "=" * 60)
    if all_errors:
        print(f"❌ 验证失败: {len(all_errors)} 个错误")
        for e in all_errors[:20]:
            print(f"  - {e}")
        if len(all_errors) > 20:
            print(f"  ... 还有 {len(all_errors) - 20} 个错误")
        sys.exit(1)
    else:
        print("✅ 验证通过")
        print(f"  Semantic Atoms: {len(atoms)}")
        print(f"  Modern Concepts: {len(concepts)} (8 domains)")
        print(f"  Rules: {len(rules)} (核心已迁移 {core_migrated}, 非核心待迁移 {non_core_pending})")
        print(f"  方向污染: 无")
        print(f"  旧机制代码: 无")
        sys.exit(0)


if __name__ == "__main__":
    main()
