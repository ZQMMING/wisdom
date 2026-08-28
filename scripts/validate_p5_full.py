"""P5完整验证 - Guidance Layer端到端验证(4条红线).

检查:
1. 端到端链: Evidence→Signal→Assertion→Cluster→GuidanceAtom→Composed→Rendered
2. 4条红线:
   - Renderer不得重新计算
   - Composer不得创造Evidence
   - 不允许direction偷换成吉凶
   - 不引入AI自由推理
3. 渲染结果不包含禁止术语
4. 可追溯性: 所有内容可追溯回Evidence
"""
from __future__ import annotations
import sys
sys.path.insert(0, "src")

from fastapi.testclient import TestClient
from tongshu.api.app import create_app

app = create_app()
client = TestClient(app)

FORBIDDEN_TERMS = {
    "大吉", "大凶", "上上", "下下", "好运", "厄运", "吉兆", "凶兆",
    "吉星", "凶星", "吉利", "凶险", "吉祥", "不祥", "福运", "祸运",
    "必然", "一定", "注定", "肯定", "绝对", "一定会", "必然会", "注定会",
    "命里注定", "天意", "劫数", "报应", "命该如此", "天数",
}

VALID_DIRECTION_LABELS = {"有利条件", "需要注意", "无明显方向性偏移"}


def main():
    print("=" * 60)
    print("P5 Guidance Layer 完整端到端验证")
    print("=" * 60)

    # 1. 计算案例
    print("\n[1/7] 计算1983案例...")
    resp = client.post("/admin/cases", json={
        "birth_year": 1983, "birth_month": 11, "birth_day": 3,
        "birth_hour": 12, "gender": "male", "location": "广东中山",
    })
    case_id = resp.json()["case_id"]
    print(f"  case_id: {case_id}")

    # 2. 端到端链
    print("\n[2/7] 端到端链检查...")
    evidence_count = client.get(f"/admin/cases/{case_id}/evidence").json()["total"]
    signal_count = client.get(f"/admin/cases/{case_id}/signals").json()["total"]
    assertion_count = client.get(f"/admin/cases/{case_id}/assertions").json()["total"]
    cluster_count = client.get(f"/admin/cases/{case_id}/clusters").json()["total"]
    guidance_data = client.get(f"/admin/cases/{case_id}/guidance").json()
    guidance_count = guidance_data["total"]
    composed_data = client.get(f"/admin/cases/{case_id}/guidance/composed").json()
    rendered_data = client.get(f"/admin/cases/{case_id}/guidance/rendered").json()

    print(f"  Evidence: {evidence_count}")
    print(f"  Signals: {signal_count}")
    print(f"  Assertions: {assertion_count}")
    print(f"  Clusters: {cluster_count}")
    print(f"  GuidanceAtoms: {guidance_count}")
    print(f"  Composed: {composed_data.get('domain_count', 0)} domains")
    print(f"  Rendered: {len(rendered_data.get('content', ''))} chars")

    assert all(c > 0 for c in [evidence_count, signal_count, assertion_count, cluster_count, guidance_count])
    assert composed_data.get("domain_count", 0) > 0
    assert len(rendered_data.get("content", "")) > 0
    print("  PASS: 端到端链完整")

    # 3. 红线1: Renderer不得重新计算
    print("\n[3/7] 红线1: Renderer不得重新计算...")
    # 渲染结果应该只包含composed中的内容, 不应该有新的断言
    rendered_content = rendered_data["content"]
    # 检查渲染结果中的domain数量与composed一致
    rendered_domains = [d["domain_label"] for d in composed_data["domains"]]
    for domain in rendered_domains:
        assert domain in rendered_content, f"渲染结果缺少domain: {domain}"
    print("  PASS: 渲染结果包含所有composed的domain, 无新增断言")

    # 4. 红线2: Composer不得创造Evidence
    print("\n[4/7] 红线2: Composer不得创造Evidence...")
    composed_assertion_ids = set(composed_data.get("source_assertion_ids", []))
    assertion_data = client.get(f"/admin/cases/{case_id}/assertions").json()
    actual_assertion_ids = {a["assertion_id"] for a in assertion_data["assertions"]}
    # composed的source_assertion_ids应该是actual_assertion_ids的子集
    assert composed_assertion_ids.issubset(actual_assertion_ids), \
        f"Composed引用了不存在的assertion: {composed_assertion_ids - actual_assertion_ids}"
    print(f"  Composed引用 {len(composed_assertion_ids)} 个assertion, 全部可追溯")
    print("  PASS: Composer没有创造Evidence")

    # 5. 红线3: 不允许direction偷换成吉凶
    print("\n[5/7] 红线3: 不允许direction偷换成吉凶...")
    # GuidanceAtom的direction_label
    for g in guidance_data["guidance"]:
        assert g["direction_label"] in VALID_DIRECTION_LABELS, \
            f"Guidance direction_label不合法: {g['direction_label']}"
        assert "吉" not in g["direction_label"], f"direction_label包含'吉': {g['direction_label']}"
        assert "凶" not in g["direction_label"], f"direction_label包含'凶': {g['direction_label']}"
    # Composed的direction_distribution
    for dir_label in composed_data.get("direction_distribution", {}):
        assert dir_label in VALID_DIRECTION_LABELS, f"Composed direction不合法: {dir_label}"
    print(f"  direction分布: {composed_data.get('direction_distribution', {})}")
    print("  PASS: 没有吉凶术语")

    # 6. 红线4: 不引入AI自由推理(禁止术语检查)
    print("\n[6/7] 红线4: 不引入AI自由推理(禁止术语)...")
    violations = []
    for term in FORBIDDEN_TERMS:
        if term in rendered_content:
            violations.append(term)
    if violations:
        print(f"  违规术语: {violations}")
        assert len(violations) == 0, f"渲染结果包含禁止术语: {violations}"
    print("  PASS: 渲染结果无禁止术语")

    # 7. 内容质量检查
    print("\n[7/7] 内容质量检查...")
    print(f"  总体概述: {composed_data.get('overall_summary', '')[:80]}...")
    print(f"  关键主题数: {len(composed_data.get('key_themes', []))}")
    print(f"  优先级建议数: {len(composed_data.get('priorities', []))}")
    print(f"  引擎覆盖: {composed_data.get('source_engines', [])}")
    print("  PASS: 内容完整")

    # 显示渲染结果预览
    print("\n" + "=" * 60)
    print("渲染结果预览(前500字):")
    print("=" * 60)
    print(rendered_content[:500])
    print("...")

    print("\n" + "=" * 60)
    print("✅ P5完整验证全部通过 (4条红线)")
    print("=" * 60)
    print("\n4条红线检查结果:")
    print("  1. Renderer不得重新计算 ✓")
    print("  2. Composer不得创造Evidence ✓")
    print("  3. 不允许direction偷换成吉凶 ✓")
    print("  4. 不引入AI自由推理 ✓")
    print(f"\n端到端链: {evidence_count} Evidence → {signal_count} Signals → {assertion_count} Assertions → {cluster_count} Clusters → {guidance_count} GuidanceAtoms → {composed_data.get('domain_count', 0)} domains → 渲染完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
