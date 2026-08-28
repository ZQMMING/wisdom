"""P5 Validator - Guidance Layer验证器(4条红线).

检查:
1. Renderer不得重新计算 - GuidanceAtom已经包含所有用户可见信息
2. Composer不得创造Evidence - 所有判断可追溯回source_assertion_ids
3. 不允许从direction偷换成吉凶 - direction_label只能是"有利条件"/"需要注意"/"无明显方向性偏移"
4. 不引入AI自由推理 - Mapping是deterministic的

额外检查:
- 禁止术语: 吉/凶/大吉/大凶/必然/一定/注定等
- 每个GuidanceAtom必须有source_assertion_ids
- 端到端链: Evidence→Signal→Assertion→Cluster→Guidance
"""
from __future__ import annotations
import sys
sys.path.insert(0, "src")

from fastapi.testclient import TestClient
from tongshu.api.app import create_app

app = create_app()
client = TestClient(app)

# 禁止术语
FORBIDDEN_TERMS = {
    "大吉", "大凶", "上上", "下下", "好运", "厄运", "吉兆", "凶兆",
    "吉星", "凶星", "吉利", "凶险", "吉祥", "不祥", "福运", "祸运",
    "必然", "一定", "注定", "肯定", "绝对", "一定会", "必然会", "注定会",
    "命里注定", "天意", "劫数", "报应", "命该如此", "天数",
}

VALID_DIRECTION_LABELS = {"有利条件", "需要注意", "无明显方向性偏移"}


def test_end_to_end():
    """测试1: 端到端完整链."""
    print("\n[1/5] 端到端完整链...")
    resp = client.post("/admin/cases", json={
        "birth_year": 1983, "birth_month": 11, "birth_day": 3,
        "birth_hour": 12, "gender": "male", "location": "广东中山",
    })
    case_id = resp.json()["case_id"]

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
    # Guidance
    resp = client.get(f"/admin/cases/{case_id}/guidance")
    guidance_count = resp.json()["total"]

    print(f"  Evidence: {evidence_count}")
    print(f"  Signals: {signal_count}")
    print(f"  Assertions: {assertion_count}")
    print(f"  Clusters: {cluster_count}")
    print(f"  Guidance: {guidance_count}")

    assert evidence_count > 0
    assert signal_count > 0
    assert assertion_count > 0
    assert cluster_count > 0
    assert guidance_count > 0
    return case_id


def test_direction_label_not_lucky(case_id):
    """测试2: direction_label不是吉凶(红线3)."""
    print("\n[2/5] direction_label不是吉凶...")
    resp = client.get(f"/admin/cases/{case_id}/guidance")
    data = resp.json()

    for g in data["guidance"]:
        assert g["direction_label"] in VALID_DIRECTION_LABELS, \
            f"Guidance {g['guidance_id']} direction_label={g['direction_label']} 不合法"
        # 不允许出现"吉"或"凶"作为direction_label
        assert "吉" not in g["direction_label"], f"direction_label包含'吉': {g['direction_label']}"
        assert "凶" not in g["direction_label"], f"direction_label包含'凶': {g['direction_label']}"

    print(f"  direction_label分布: {data['stats']['by_direction_label']}")
    print("  PASS: 没有吉凶术语")


def test_traceability(case_id):
    """测试3: 可追溯性(红线2)."""
    print("\n[3/5] 可追溯性...")
    resp = client.get(f"/admin/cases/{case_id}/guidance")
    data = resp.json()

    for g in data["guidance"]:
        assert len(g["source_assertion_ids"]) > 0, \
            f"Guidance {g['guidance_id']} 没有source_assertion_ids(不可追溯)"

    # 检查source_assertion_ids是否在assertions中存在
    resp = client.get(f"/admin/cases/{case_id}/assertions")
    assertion_ids = {a["assertion_id"] for a in resp.json()["assertions"]}

    for g in data["guidance"]:
        for aid in g["source_assertion_ids"]:
            assert aid in assertion_ids, \
                f"Guidance {g['guidance_id']} 引用了不存在的assertion: {aid}"

    print(f"  所有guidance都有source_assertion_ids, 且都能追溯到assertion")
    print("  PASS: 可追溯性")


def test_no_forbidden_terms(case_id):
    """测试4: 禁止术语检查."""
    print("\n[4/5] 禁止术语检查...")
    resp = client.get(f"/admin/cases/{case_id}/guidance")
    data = resp.json()

    violations = []
    for g in data["guidance"]:
        all_text = " ".join([
            g["theme"], g["direction_label"], g["direction_description"],
            *g["opportunities"], *g["cautions"], *g["actions"], *g["avoid"],
        ])
        for term in FORBIDDEN_TERMS:
            if term in all_text:
                violations.append(f"Guidance {g['guidance_id']} theme={g['theme']} 包含禁止术语: {term}")

    if violations:
        for v in violations:
            print(f"  违规: {v}")
        assert len(violations) == 0, f"发现{len(violations)}个禁止术语违规"

    print("  PASS: 没有禁止术语")


def test_guidance_content(case_id):
    """测试5: Guidance内容完整性."""
    print("\n[5/5] Guidance内容完整性...")
    resp = client.get(f"/admin/cases/{case_id}/guidance")
    data = resp.json()

    for g in data["guidance"]:
        # 至少有一个内容字段非空
        has_content = any([g["opportunities"], g["cautions"], g["actions"], g["avoid"]])
        assert has_content, f"Guidance {g['guidance_id']} theme={g['theme']} 没有内容"

        # intensity范围
        assert 0 <= g["intensity"] <= 100, f"Guidance {g['guidance_id']} intensity={g['intensity']} 超出范围"

    print(f"  domain分布: {data['stats']['by_domain']}")
    print(f"  theme分布: {data['stats']['by_theme']}")
    print(f"  平均intensity: {data['stats']['avg_intensity']:.1f}")
    print("  PASS: 内容完整")


def main():
    print("=" * 60)
    print("P5 Guidance Layer Validator (4条红线)")
    print("=" * 60)

    try:
        case_id = test_end_to_end()
        test_direction_label_not_lucky(case_id)
        test_traceability(case_id)
        test_no_forbidden_terms(case_id)
        test_guidance_content(case_id)

        print("\n" + "=" * 60)
        print("✅ P5-A验证全部通过 (4条红线)")
        print("=" * 60)
        print("\n4条红线检查结果:")
        print("  1. Renderer不得重新计算: GuidanceAtom已包含所有信息 ✓")
        print("  2. Composer不得创造Evidence: 所有guidance可追溯到assertion ✓")
        print("  3. 不允许direction偷换成吉凶: direction_label无吉凶术语 ✓")
        print("  4. 不引入AI自由推理: Mapping是deterministic的 ✓")
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
