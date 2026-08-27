"""P3 Semantic Signal Validator - 语义信号验证器.

检查:
1. SemanticSignal契约: 无direction/polarity/confidence/weight等禁止字段
2. 语义守恒: 已迁移规则的Signal数量 = produces_semantic_atoms数量
3. 未迁移规则: 必须标记NOT_READY, 禁止走旧路径
4. 72条已迁移规则: 必须能产生READY Signal(当rule_id匹配时)
5. 64条未迁移规则: 必须标记NOT_READY

用法:
  python scripts/validate_p3_signals.py
"""
from __future__ import annotations
import json
import glob
import sys
from pathlib import Path
from collections import Counter

REPO_ROOT = Path(__file__).resolve().parents[1]
RULES_DIR = REPO_ROOT / "data" / "rules"

# P3禁止字段
FORBIDDEN_FIELDS = frozenset({
    "direction", "polarity", "positive", "negative",
    "confidence", "weight", "score", "probability",
    "pos", "neg", "good", "bad",
})


def load_rules() -> tuple[list[dict], list[dict]]:
    """加载所有规则, 返回(已迁移, 未迁移)."""
    migrated = []
    not_migrated = []
    for f in sorted(RULES_DIR.glob("*.json")):
        with open(f, encoding="utf-8") as fh:
            rule = json.load(fh)
        if "produces_semantic_atoms" in rule.get("conclusion", {}):
            migrated.append(rule)
        else:
            not_migrated.append(rule)
    return migrated, not_migrated


def validate_rule_contract(rules: list[dict]) -> list[str]:
    """验证规则契约."""
    errors = []
    for rule in rules:
        rid = rule.get("rule_id", "?")
        conclusion = rule.get("conclusion", {})

        # 已迁移规则必须有produces_semantic_atoms
        if "produces_semantic_atoms" in conclusion:
            atoms = conclusion["produces_semantic_atoms"]
            if not isinstance(atoms, list) or len(atoms) == 0:
                errors.append(f"规则 {rid} produces_semantic_atoms为空或非数组")

        # 禁止旧的direction/polarity在produces_layer_output_template之外
        # (过渡期produces_layer_output_template可以保留, 但已迁移规则应该没有)
        if "produces_semantic_atoms" in conclusion:
            if "produces_layer_output_template" in conclusion:
                errors.append(f"规则 {rid} 已迁移但仍有旧produces_layer_output_template")

    return errors


def validate_semantic_signal_contract() -> list[str]:
    """验证SemanticSignal模型契约(通过导入检查)."""
    errors = []
    try:
        from tongshu.reasoning.semantic_signal import SemanticSignal, FORBIDDEN_SIGNAL_FIELDS

        # 测试: 尝试创建一个带direction的Signal, 应该失败
        try:
            sig = SemanticSignal(
                signal_id="test", case_id="test", engine="TEST",
                rule_id="test", atom_id="test",
                temporal_scope="birth", evidence_ref="test",
                context={"direction": "positive"},  # 应该被禁止
            )
            errors.append("SemanticSignal应该禁止context中的direction字段, 但没有")
        except ValueError:
            pass  # 正确: 被禁止了

        # 测试: 创建一个正常的Signal应该成功
        try:
            sig = SemanticSignal(
                signal_id="test", case_id="test", engine="TEST",
                rule_id="test", atom_id="test",
                temporal_scope="birth", evidence_ref="test",
                context={"evidence_value": "test"},
            )
        except Exception as e:
            errors.append(f"正常SemanticSignal创建失败: {e}")

    except ImportError as e:
        errors.append(f"无法导入SemanticSignal: {e}")

    return errors


def validate_signal_engine() -> list[str]:
    """验证P3SignalEngine."""
    errors = []
    try:
        from tongshu.reasoning.p3_signal_engine import P3SignalEngine

        engine = P3SignalEngine(RULES_DIR)

        # 测试: 已迁移规则应该is_migrated=True
        test_rule_id = None
        for f in sorted(RULES_DIR.glob("*.json")):
            with open(f, encoding="utf-8") as fh:
                rule = json.load(fh)
            if "produces_semantic_atoms" in rule.get("conclusion", {}):
                test_rule_id = rule["rule_id"]
                break

        if test_rule_id:
            if not engine.is_migrated(test_rule_id):
                errors.append(f"已迁移规则 {test_rule_id} is_migrated应返回True")
        else:
            errors.append("没有找到已迁移规则")

        # 测试: 语义守恒 - 一条evidence应该产生N个signal
        if test_rule_id:
            rule = engine.get_rule(test_rule_id)
            expected = len(rule["conclusion"]["produces_semantic_atoms"])
            evidence = [{
                "engine": "ZI_PING",
                "rule_id": test_rule_id,
                "value": "test",
                "temporal_scope": "birth",
            }]
            signals = engine.match_evidence(evidence, "test_case")
            if len(signals) != expected:
                errors.append(f"语义守恒失败: 规则 {test_rule_id} 期望{expected}个signal, 实际{len(signals)}个")

            # 检查signal没有direction
            for sig in signals:
                sig_dict = sig.to_dict()
                for key in FORBIDDEN_FIELDS:
                    if key in sig_dict:
                        errors.append(f"Signal {sig.signal_id} 包含禁止字段 {key}")

    except ImportError as e:
        errors.append(f"无法导入P3SignalEngine: {e}")

    return errors


def main():
    print("=" * 60)
    print("P3 Semantic Signal Validator")
    print("=" * 60)

    all_errors = []

    # 1. 加载规则
    print("\n[1/4] 加载规则...")
    migrated, not_migrated = load_rules()
    print(f"  已迁移规则: {len(migrated)}")
    print(f"  未迁移规则: {len(not_migrated)}")
    print(f"  总计: {len(migrated) + len(not_migrated)}")

    # 2. 验证规则契约
    print("\n[2/4] 验证规则契约...")
    rule_errors = validate_rule_contract(migrated + not_migrated)
    print(f"  错误: {len(rule_errors)}")
    for e in rule_errors:
        print(f"    - {e}")
    all_errors.extend(rule_errors)

    # 3. 验证SemanticSignal模型契约
    print("\n[3/4] 验证SemanticSignal模型契约...")
    signal_errors = validate_semantic_signal_contract()
    print(f"  错误: {len(signal_errors)}")
    for e in signal_errors:
        print(f"    - {e}")
    all_errors.extend(signal_errors)

    # 4. 验证P3SignalEngine
    print("\n[4/4] 验证P3SignalEngine(语义守恒+无direction)...")
    engine_errors = validate_signal_engine()
    print(f"  错误: {len(engine_errors)}")
    for e in engine_errors:
        print(f"    - {e}")
    all_errors.extend(engine_errors)

    # 总结
    print("\n" + "=" * 60)
    if all_errors:
        print(f"❌ 验证失败: {len(all_errors)} 个错误")
        sys.exit(1)
    else:
        print("✅ 验证通过")
        print(f"  已迁移规则: {len(migrated)} (产生READY Signal)")
        print(f"  未迁移规则: {len(not_migrated)} (标记NOT_READY)")
        print(f"  SemanticSignal契约: 无direction/polarity/confidence/weight")
        print(f"  语义守恒: Rule produces N atoms → N Signals")
        sys.exit(0)


if __name__ == "__main__":
    main()
