"""K2G 新增 14 个证据文件: 补 M2-B provenance_note + 注册进 evidence_review_queue。"""
import json
from pathlib import Path
from collections import Counter

DATA = Path("data")
ev_dir = DATA / "evidence"
q_path = DATA / "evidence_meta" / "evidence_review_queue.json"

# 1. 给缺 M2-B 标记的证据补 provenance_note(保留原 K2G 信息)
fixed = 0
for f in sorted(ev_dir.glob("*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    note = d.get("provenance_note", "")
    if "M2-B" not in note:
        d["provenance_note"] = f"M2-B K2G 批次新增; {note}".strip("; ").strip()
        f.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        fixed += 1
print(f"provenance_note fixed: {fixed}")

# 2. review queue 补缺失条目
q = json.loads(q_path.read_text(encoding="utf-8"))
queued = {e["evidence_id"] for e in q["items"]}
all_ev = {f.stem for f in ev_dir.glob("*.json")}
missing = sorted(all_ev - queued)
for eid in missing:
    ev = json.loads((ev_dir / f"{eid}.json").read_text(encoding="utf-8"))
    verdict = (ev.get("citation") or {}).get("verification_status") or "blank"
    q["items"].append({
        "evidence_id": eid,
        "verdict": verdict,
        "review_status": "pending_manual_verification",
    })
if missing:
    q_path.write_text(json.dumps(q, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"queue added: {len(missing)} -> total {len(q['items'])}")

# 3. 输出新分布(供测试断言更新)
q = json.loads(q_path.read_text(encoding="utf-8"))
verdicts = Counter(e["verdict"] for e in q["items"])
statuses = Counter(e["review_status"] for e in q["items"])
print("verdicts:", dict(verdicts))
print("statuses:", dict(statuses))
