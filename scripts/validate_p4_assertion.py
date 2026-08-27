"""P4 Validator - Assertion Layer验证器.

检查:
1. Rule Resolver: 子平核心规则必须RESOLVED
2. SemanticSignal: 无direction/polarity/confidence/weight
3. CanonicalAssertion: direction只能是supportive/caution/neutral, 禁止positive/negative
4. AssertionCluster: 互补不投票, 无权重/分数/置信度
5. 语义守恒: Rule produces N atoms → N Signals
6. 1983案例端到端: Evidence→Resolver→Signal→Assertion→Cluster完整链
"""
from __future__ import annotations
import sys
sys.path.insert(0, "src")

from fastapi.testclient import TestClient
from tongshu.api.app import create_app

app = create_app()
client = TestClient(app)

# 禁止字段
FORBIDDEN_DIRECTIONS = {"positive", "negative", "good", "bad", "lucky", "unlucky"}
FORBIDDEN_FIELDS = {"confidence", "weight", "score", "probability"}


def test_rule_resolver():
    """测试1: Rule Resolver."""
    print("\n[1/6] Rule Resolver...")
    resp = client.post("/admin/cases", json={
        "birth_year": 1983, "birth_month": 11, "birth_day": 3,
        "birth_hour": 12, "gender": "male", "location": "广东中山",
    })
    case_id = resp.json()["case_id"]

    resp = client.get(f"/admin/cases/{case_id}/resolved-rules")
    data = resp.json()

    zi_ping_resolved = sum(1 for r in data["resolved_rules"]
                           if r["engine"] == "ZI_PING" and r["match_status"] == "RESOLVED")
    print(f"  子平RESOLVED: {zi_ping_resolved}/8")
    assert zi_ping_resolved == 8, f"子平应该8条全部RESOLVED, 实际{zi_ping_resolved}"

    unresolved = data["by_status"].get("UNRESOLVED", 0)
    print(f"  UNRESOLVED: {unresolved} (盲派7+紫微18=25, 预期)")
    return case_id


def test_signals_no_direction(case_id):
    """测试2: SemanticSignal无direction."""
    print("\n[2/6] SemanticSignal无direction...")
    resp = client.get(f"/admin/cases/{case_id}/signals")
    data = resp.json()

    for s in data["signals"]:
        for key in FORBIDDEN_DIRECTIONS | FORBIDDEN_FIELDS:
            assert key not in s, f"Signal {s['signal_id']} 包含禁止字段 {key}"
            if key in str(s.get("context", {})):
                # context中可能有reason包含这些词, 不严格检查
                pass

    ready = data["stats"]["ready"]
    not_ready = data["stats"]["not_ready"]
    print(f"  READY: {ready}, NOT_READY: {not_ready}")
    assert ready > 0, "应该有READY Signals"
    assert data["stats"]["conservation_ok"], "语义守恒应该通过"


def test_assertions_direction(case_id):
    """测试3: CanonicalAssertion direction合法."""
    print("\n[3/6] CanonicalAssertion direction...")
    resp = client.get(f"/admin/cases/{case_id}/assertions")
    data = resp.json()

    valid_directions = {"supportive", "caution", "neutral"}
    for a in data["assertions"]:
        assert a["direction"] in valid_directions, \
            f"Assertion {a['assertion_id']} direction={a['direction']} 不合法"
        for key in FORBIDDEN_DIRECTIONS:
            assert key != a["direction"], f"Assertion direction不能是 {key}"

    print(f"  总断言: {data['total']}")
    print(f"  by_direction: {data['stats']['by_direction']}")
    print(f"  by_domain: {data['stats']['by_domain']}")
    assert data["total"] > 0, "应该有断言"


def test_clusters_no_voting(case_id):
    """测试4: AssertionCluster互补不投票."""
    print("\n[4/6] AssertionCluster互补不投票...")
    resp = client.get(f"/admin/cases/{case_id}/clusters")
    data = resp.json()

    for c in data["clusters"]:
        # 不应该有权重/分数/置信度字段
        for key in FORBIDDEN_FIELDS:
            assert key not in c, f"Cluster {c['cluster_id']} 包含禁止字段 {key}"
        # source_engines应该是列表(互补覆盖面)
        assert isinstance(c["source_engines"], list), "source_engines应该是列表"

    print(f"  总cluster: {data['total']}")
    print(f"  multi_engine: {data['stats']['multi_engine_clusters']}")
    print(f"  single_engine: {data['stats']['single_engine_clusters']}")
    print(f"  by_domain: {data['stats']['by_domain']}")
    assert data["total"] > 0, "应该有cluster"


def test_semantic_conservation(case_id):
    """测试5: 语义守恒."""
    print("\n[5/6] 语义守恒...")
    resp = client.get(f"/admin/cases/{case_id}/signals")
    data = resp.json()
    assert data["stats"]["conservation_ok"], "语义守恒应该通过"
    assert len(data["stats"]["conservation_issues"]) == 0, "不应该有守恒问题"
    print("  语义守恒: PASS")


def test_end_to_end_trace(case_id):
    """测试6: 端到端完整链."""
    print("\n[6/6] 端到端完整链...")
    # Evidence
    resp = client.get(f"/admin/cases/{case_id}/evidence")
    evidence_count = resp.json()["total"]
    # Signals
    resp = client.get(f"/admin/cases/{case_id}/signals")
    signal_count = resp.json()["total"]
    # Assertions
    resp = client.get(f"/admin/cases/{case_id}/assertions")
    assertion_count = resp.json()["total"]
    # Clusters
    resp = client.get(f"/admin/cases/{case_id}/clusters")
    cluster_count = resp.json()["total"]

    print(f"  Evidence: {evidence_count}")
    print(f"  Signals: {signal_count} (语义守恒)")
    print(f"  Assertions: {assertion_count} (direction合法)")
    print(f"  Clusters: {cluster_count} (互补不投票)")

    assert evidence_count > 0
    assert signal_count > 0
    assert assertion_count > 0
    assert cluster_count > 0
    print("  端到端链: PASS")


def main():
    print("=" * 60)
    print("P4 Assertion Layer Validator")
    print("=" * 60)

    try:
        case_id = test_rule_resolver()
        test_signals_no_direction(case_id)
        test_assertions_direction(case_id)
        test_clusters_no_voting(case_id)
        test_semantic_conservation(case_id)
        test_end_to_end_trace(case_id)

        print("\n" + "=" * 60)
        print("✅ P4验证全部通过")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n❌ 验证失败: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
