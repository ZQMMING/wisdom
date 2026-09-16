# -*- coding: utf-8 -*-
"""Inspect EXISTING B1/B4 deliverables: what they're bound to, counts, integrity.
Read-only. Determines whether B1/B4 are already complete vs. still needed."""
import json, os, hashlib, collections

ROOT = "D:/shuntian"
def p(*a): return os.path.join(ROOT, *a)

def cur_hash(path):
    try:
        return hashlib.sha256(open(path, encoding="utf-8").read().encode()).hexdigest()
    except Exception as e:
        return "ERR:%s" % e

print("=" * 70)
print("CURRENT ORIGINALS (frozen on disk)")
yhzp_h = cur_hash(p("data/classics/original/YHZP_渊海子平_完整全文.md"))
sftk_h = cur_hash(p("data/classics/original/SFTK_神峰通考_完整全文.md"))
print("  YHZP hash:", yhzp_h[:16], "lines:", len(open(p("data/classics/original/YHZP_渊海子平_完整全文.md"), encoding="utf-8").read().splitlines()))
print("  SFTK hash:", sftk_h[:16], "lines:", len(open(p("data/classics/original/SFTK_神峰通考_完整全文.md"), encoding="utf-8").read().splitlines()))

def inspect(src_rel, rule_rel):
    print("\n" + "=" * 70)
    print("DELIVERABLE: " + src_rel)
    sp = p(src_rel); rp = p(rule_rel)
    exists = os.path.exists(sp) and os.path.exists(rp)
    print("  exists:", os.path.exists(sp), os.path.exists(rp))
    if not (os.path.exists(sp) and os.path.exists(rp)):
        print("  -> MISSING. This deliverable still needs to be generated.")
        return
    srcs = [json.loads(l) for l in open(sp, encoding="utf-8") if l.strip()]
    rules = [json.loads(l) for l in open(rp, encoding="utf-8") if l.strip()]
    print("  source records:", len(srcs))
    print("  rule candidates:", len(rules))
    # what original hash are sources bound to?
    hashes = collections.Counter(s.get("file_hash", "?")[:12] for s in srcs)
    print("  source file_hash binding:", dict(hashes))
    print("  source text_layer dist:", dict(collections.Counter(s.get("text_layer") for s in srcs)))
    print("  source status dist:", dict(collections.Counter(s.get("status") for s in srcs)))
    # rule binding check
    src_ids = set(s.get("source_id") for s in srcs)
    rule_sids = set()
    for r in rules:
        # source may be single or list
        sid = r.get("source_id") or r.get("source_ids") or r.get("sources")
        if isinstance(sid, list): rule_sids.update(sid)
        elif sid: rule_sids.add(sid)
    unbound = rule_sids - src_ids
    print("  rules referencing source_ids NOT in source set:", len(unbound))
    if unbound: print("   sample unbound:", sorted(unbound)[:5])
    print("  rule type dist:", dict(collections.Counter(r.get("rule_type") for r in rules)))
    print("  rule status dist:", dict(collections.Counter(r.get("status") for r in rules)))
    # sample first source + first rule
    print("  --- sample source[0] ---")
    for k in ("source_id","engine","book","chapter","section","text_layer","status","file_hash","resource_id"):
        if k in srcs[0]: print("    %s = %s" % (k, str(srcs[0][k])[:60]))
    print("  --- sample rule[0] ---")
    print("   ", json.dumps(rules[0], ensure_ascii=False)[:400])

inspect("data/sources/yhzp_sources.jsonl", "data/rules/candidate/CAND-YHZP_rules.jsonl")
inspect("data/sources/sftk_sources.jsonl", "data/rules/candidate/CAND-SFTK_rules.jsonl")

# other classics committed in the batch
print("\n" + "=" * 70)
print("OTHER CLASSICS (context for the batch, not my task)")
for code, rel in [("PZZQ","pzzq_sources.jsonl"),("DTS","dts_sources.jsonl"),
                  ("QTBJ","qtbj_sources.jsonl"),("SMTH","smth_sources.jsonl")]:
    fp = p("data/sources/"+rel)
    if os.path.exists(fp):
        print("  %s: %d records" % (code, sum(1 for l in open(fp, encoding="utf-8") if l.strip())))
    else:
        print("  %s: MISSING" % code)
