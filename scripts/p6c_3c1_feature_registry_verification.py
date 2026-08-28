"""P6-C-3C-1 Feature Registry验证 - 1983案例.

验证:
1. 子平Feature Adapter能否将BaziChart转换为Feature
2. 每个Feature是否有namespace和provenance
3. RESOLVED / UNMAPPED统计
4. 不产生direction/polarity/domain
"""
import sys
sys.path.insert(0, "src")

from tongshu.engines.bazi_engine import BaziEngine
from tongshu.feature_registry import FeatureRegistry, ZiPingFeatureAdapter


def main():
    print("=" * 70)
    print("P6-C-3C-1 Feature Registry验证 - 1983案例")
    print("=" * 70)

    # 1983案例: 男 1983-11-03 午时 广东中山
    print("\n[1] 计算子平八字...")
    engine = BaziEngine()
    chart = engine.compute((1983, 11, 3, 12), "male")
    print(f"  四柱: {chart.year_pillar.heavenly_stem}{chart.year_pillar.earthly_branch} "
          f"{chart.month_pillar.heavenly_stem}{chart.month_pillar.earthly_branch} "
          f"{chart.day_pillar.heavenly_stem}{chart.day_pillar.earthly_branch} "
          f"{chart.hour_pillar.heavenly_stem}{chart.hour_pillar.earthly_branch}")
    print(f"  日主: {chart.day_master}")
    print(f"  起运: {chart.start_age:.2f}岁")

    # Feature Registry
    print("\n[2] 初始化Feature Registry...")
    registry = FeatureRegistry()
    adapter = ZiPingFeatureAdapter(registry)
    print(f"  Registry统计: {registry.stats()}")

    # 转换Feature
    print("\n[3] 子平Feature Adapter转换...")
    result = adapter.adapt(chart)
    print(f"  总Evidence: {result.total_evidence}")
    print(f"  RESOLVED: {result.resolved}")
    print(f"  UNMAPPED: {result.unmapped}")
    print(f"  覆盖率: {result.coverage_rate:.1%}")

    # 显示Feature列表
    print("\n[4] Feature列表 (前20个):")
    for i, f in enumerate(result.resolved_features[:20]):
        val_str = str(f.value)[:50]
        print(f"  {i+1:2d}. {f.feature_id:40s} = {val_str}")
        print(f"      来源: {f.source_rule_id} / {f.source_field} / {f.source_evidence_ref}")

    if len(result.resolved_features) > 20:
        print(f"  ... 还有 {len(result.resolved_features) - 20} 个Feature")

    # 按分类统计
    print("\n[5] Feature分类统计:")
    categories = {}
    for f in result.resolved_features:
        categories[f.category] = categories.get(f.category, 0) + 1
    for cat, count in sorted(categories.items()):
        print(f"  {cat:15s}: {count}")

    # 验证provenance
    print("\n[6] Provenance验证:")
    no_provenance = [f for f in result.resolved_features if not f.source_rule_id or not f.source_field]
    print(f"  缺少provenance的Feature: {len(no_provenance)}")
    if no_provenance:
        for f in no_provenance:
            print(f"    - {f.feature_id}")

    # 验证namespace
    print("\n[7] Namespace验证:")
    wrong_ns = [f for f in result.resolved_features if not f.feature_id.startswith("ZP.")]
    print(f"  namespace错误的Feature: {len(wrong_ns)}")

    # 验证禁止字段
    print("\n[8] 禁止字段验证 (direction/polarity/domain):")
    forbidden = ["direction", "polarity", "domain", "positive", "negative", "confidence"]
    found_forbidden = []
    for f in result.resolved_features:
        for key in f.attributes:
            if key.lower() in forbidden:
                found_forbidden.append((f.feature_id, key))
    print(f"  发现禁止字段: {len(found_forbidden)}")
    if found_forbidden:
        for fid, key in found_forbidden:
            print(f"    - {fid}: {key}")

    # UNMAPPED列表
    if result.unmapped_evidence:
        print("\n[9] UNMAPPED列表:")
        for e in result.unmapped_evidence:
            print(f"  - {e['rule_id']}: {e['value'][:50]}")

    # 最终结论
    print("\n" + "=" * 70)
    print("P6-C-3C-1 验证结果")
    print("=" * 70)
    print(f"  子平Feature总数: {result.resolved}")
    print(f"  覆盖率: {result.coverage_rate:.1%}")
    print(f"  Provenance完整: {'✓' if len(no_provenance) == 0 else '✗'}")
    print(f"  Namespace正确: {'✓' if len(wrong_ns) == 0 else '✗'}")
    print(f"  无禁止字段: {'✓' if len(found_forbidden) == 0 else '✗'}")
    print(f"  UNMAPPED: {result.unmapped}")

    gate_pass = (
        result.coverage_rate > 0.9
        and len(no_provenance) == 0
        and len(wrong_ns) == 0
        and len(found_forbidden) == 0
    )
    print(f"\n  P6-C-3C-1 GATE: {'PASS' if gate_pass else 'FAIL'}")
    print("=" * 70)


if __name__ == "__main__":
    main()
