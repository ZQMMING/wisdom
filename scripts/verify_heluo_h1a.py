# -*- coding: utf-8 -*-
"""H1-A 入库完整性核验(写 UTF-8 结果文件避免 GBK 控制台乱码)。"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import psycopg2  # noqa: E402
from tongshu.db.config import get_dsn  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "docs" / "v40" / "heluo_research" / "h1a_verify.md"
dsn = get_dsn().replace("/otcg", "/shuntian_kb")
conn = psycopg2.connect(dsn)
cur = conn.cursor()
lines = ["# H1-A 入库核验", "", f"时间:2026-08-21", ""]

q = lambda sql: cur.execute(sql) or cur.fetchall()

# 1. 各表 HELUO 计数
lines.append("## 1. HELUO-LISHU 计数")
for tbl, cond in [
    ("sources", "source_id='HELUO-LISHU'"),
    ("passages", "source_id='HELUO-LISHU'"),
    ("claims", "passage_id LIKE 'P-HL-%'"),
    ("evidence", "source_id='HELUO-LISHU'"),
    ("rules", "source_id='HELUO-LISHU'"),
    ("hl_algorithms", "algorithm_id IN ('HL-ALG-001','HL-ALG-002')"),
    ("hl_algorithm_evidence", "source_id='HELUO-LISHU'"),
    ("golden_cases", "case_id='HL-G-R-0001'"),
]:
    n = q(f"SELECT count(*) FROM {tbl} WHERE {cond}")[0][0]
    lines.append(f"- {tbl}: {n}")

# 2. 级联不变量: EVD.status == 源 passage.status
lines.append("")
lines.append("## 2. 级联不变量 EVD.status==passage.status")
rows = q("""
    SELECT e.evidence_id, e.verification_status, p.verification_status
    FROM evidence e JOIN passages p USING (passage_id)
    WHERE e.source_id='HELUO-LISHU' ORDER BY e.evidence_id""")
ok = all(es == ps for _, es, ps in rows)
for eid, es, ps in rows:
    lines.append(f"- {eid}: EVD={es} / passage={ps} {'✓' if es==ps else '✗'}")
lines.append(f"不变量: {'PASS' if ok else 'FAIL'}")

# 3. rules 状态
lines.append("")
lines.append("## 3. rules 状态(DRAFT 且 provenance=classical)")
for rid, st, prov, pid in q("""
        SELECT rule_id, rule_status, provenance, passage_id FROM rules
        WHERE source_id='HELUO-LISHU' ORDER BY rule_id"""):
    lines.append(f"- {rid}: {st} / {prov} / passage={pid}")

# 4. hl_algorithms + links
lines.append("")
lines.append("## 4. hl_algorithms")
for aid, status, ver in q("SELECT algorithm_id,status,hl_calc_version FROM hl_algorithms WHERE algorithm_id LIKE 'HL-ALG-%' ORDER BY algorithm_id"):
    lines.append(f"- {aid}: {status} / {ver}")
lines.append("")
lines.append("## 4b. hl_algorithm_evidence links")
for lid, ltype, pid, eid, rid, gid in q("""
        SELECT link_id, link_type, passage_id, evidence_id, rule_id, golden_case_id
        FROM hl_algorithm_evidence WHERE source_id='HELUO-LISHU' ORDER BY link_id"""):
    lines.append(f"- {lid}: {ltype} p={pid} e={eid} r={rid} g={gid}")

# 5. golden
lines.append("")
lines.append("## 5. golden HL-G-R-0001")
g = q("SELECT case_id, verification_status, version FROM golden_cases WHERE case_id='HL-G-R-0001'")[0]
lines.append(f"- {g[0]}: {g[1]} / {g[2]}")

# 6. FK 完整性(悬空引用检查)
lines.append("")
lines.append("## 6. 引用完整性")
for name, sql in [
    ("evidence.passage_id 悬空", "SELECT count(*) FROM evidence e LEFT JOIN passages p USING(passage_id) WHERE e.source_id='HELUO-LISHU' AND p.passage_id IS NULL"),
    ("evidence.claim_id 悬空", "SELECT count(*) FROM evidence e LEFT JOIN claims c USING(claim_id) WHERE e.source_id='HELUO-LISHU' AND c.claim_id IS NULL"),
    ("rules.passage_id 悬空", "SELECT count(*) FROM rules r LEFT JOIN passages p USING(passage_id) WHERE r.source_id='HELUO-LISHU' AND p.passage_id IS NULL"),
    ("rules.claim_id 悬空", "SELECT count(*) FROM rules r LEFT JOIN claims c USING(claim_id) WHERE r.source_id='HELUO-LISHU' AND c.claim_id IS NULL"),
]:
    n = q(sql)[0][0]
    lines.append(f"- {name}: {n} {'✓' if n==0 else '✗'}")

OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("verify done ->", OUT)
