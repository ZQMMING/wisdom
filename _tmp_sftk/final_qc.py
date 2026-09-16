# -*- coding: utf-8 -*-
"""Final offline QC: hash binding, source_text non-empty, rule->source binding quality."""
import json, hashlib, os, collections, re

ROOT = "D:/shuntian"
YB = open(os.path.join(ROOT, "data/classics/original/YHZP_渊海子平_完整全文.md"), "rb").read()
SB = open(os.path.join(ROOT, "data/classics/original/SFTK_神峰通考_完整全文.md"), "rb").read()
YH = hashlib.sha256(YB).hexdigest()
SH = hashlib.sha256(SB).hexdigest()

def check(tag, src_rel, rule_rel, disk_hash):
    srcs = [json.loads(l) for l in open(os.path.join(ROOT, src_rel), encoding="utf-8") if l.strip()]
    rules = [json.loads(l) for l in open(os.path.join(ROOT, rule_rel), encoding="utf-8") if l.strip()]
    sids = set(s["source_id"] for s in srcs)
    bound = collections.Counter(s["source_location"]["file_hash"][:12] for s in srcs)
    empty_txt = sum(1 for s in srcs if not s["source_text"].strip())
    dup_sid = [k for k, c in collections.Counter(s["source_id"] for s in srcs).items() if c > 1]
    dup_rid = [k for k, c in collections.Counter(r["rule_id"] for r in rules).items() if c > 1]
    unbound = sum(1 for r in rules for sid in r["source_ids"] if sid not in sids)
    empty_bind = sum(1 for r in rules if not r["source_ids"])
    opviol = 0
    for r in rules:
        blob = json.dumps(r, ensure_ascii=False)
        if ">" in blob or "<" in blob: opviol += 1
        if "D:/shuntian" in blob: opviol += 1
    print("== %s ==" % tag)
    print("  sources=%d rules=%d" % (len(srcs), len(rules)))
    print("  file_hash binding=%s disk=%s -> %s" % (dict(bound), disk_hash[:12], "MATCH" if set(bound)=={disk_hash[:12]} else "STALE"))
    print("  dup_source_id=%d dup_rule_id=%d" % (len(dup_sid), len(dup_rid)))
    print("  empty_source_text=%d" % empty_txt)
    print("  rule->source unbound_refs=%d empty_source_ids=%d op/abs-path-violations=%d" % (unbound, empty_bind, opviol))
    return srcs, rules

check("YHZP", "data/sources/yhzp_sources.jsonl", "data/rules/candidate/CAND-YHZP_rules.jsonl", YH)
check("SFTK", "data/sources/sftk_sources.jsonl", "data/rules/candidate/CAND-SFTK_rules.jsonl", SH)
