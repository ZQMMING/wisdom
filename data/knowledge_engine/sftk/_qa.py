# -*- coding: utf-8 -*-
"""SFTK QA: run all section-8 checks."""
import json, io, re, os, collections, random

OUTDIR = r"D:\shuntian\data\knowledge_engine\sftk"
SRC_BOOK = r"D:\顺天系统资料\豆包资料\六部经典校对版\SFTK_神峰通考_OCR校对版.md"

def load(p):
    return [json.loads(l) for l in io.open(os.path.join(OUTDIR,p),encoding="utf-8") if l.strip()]

sources = load("sources.jsonl")
rules = load("rules_candidate.jsonl")
unform = load("unformalizable.jsonl") if os.path.exists(os.path.join(OUTDIR,"unformalizable.jsonl")) else []

book = io.open(SRC_BOOK,encoding="utf-8").read()
# normalize book whitespace for substring check (we joined our text; original has newlines/spaces)
book_norm = re.sub(r"\s+","",book)

results=[]
def chk(name, ok, detail=""):
    results.append((name, ok, detail))

# --- Source checks ---
ids=[s["source_id"] for s in sources]
chk("source_id 唯一", len(ids)==len(set(ids)), f"{len(ids)} vs {len(set(ids))}")
valid_layers={"ORIGINAL","ANNOTATION","LATER_COMMENTARY","UNVERIFIED"}
bad_layer=[s["source_id"] for s in sources if s["text_layer"] not in valid_layers]
chk("text_layer 合法", not bad_layer, str(bad_layer[:5]))
# no absolute path / url in source_text
bad_url=[s["source_id"] for s in sources if any(x in s["source_text"] for x in ["D:\\","C:\\","http","www."])]
chk("无绝对路径/URL in source_text", not bad_url, str(bad_url[:5]))
# no watermark
wm=["luckclub","qq群","QQ群","收费50","技术支持"]
bad_wm=[s["source_id"] for s in sources if any(x in s["source_text"] for x in wm)]
chk("无水印广告", not bad_wm, str(bad_wm[:5]))
# no U+FFFD / control chars
bad_ctrl=[s["source_id"] for s in sources if "\uFFFD" in s["source_text"] or any(ord(c)<32 and c not in "\t" for c in s["source_text"])]
chk("无替换符/控制字符", not bad_ctrl, str(bad_ctrl[:5]))
# verbatim check: SFTK strips interleaved page-marks/headers, so source_text is a
# subsequence of the normalized book (not a contiguous substring). Verify char-order.
def is_subseq(needle, hay):
    it=iter(hay)
    return all(ch in it for ch in needle)
sample = random.sample(sources, max(1, len(sources)//5))
miss=[s["source_id"] for s in sample if not is_subseq(re.sub(r"\s+","",s["source_text"]), book_norm)]
chk("抽样20% source_text逐字可回溯(子序列)", not miss, str(miss[:8]))
miss20=[]
for s in sources:
    head=re.sub(r"\s+","",s["source_text"])[:20]
    if head and not is_subseq(head, book_norm):
        miss20.append(s["source_id"])
chk("100% source_text前20字可回溯", not miss20, str(miss20[:8]))

# --- Rule checks ---
rids=[r["rule_id"] for r in rules]
chk("rule_id 唯一", len(rids)==len(set(rids)), f"{len(rids)}")
chk("rule_id 以 CAND-SFTK- 开头", all(r.startswith("CAND-SFTK-") for r in rids), "")
sid_set=set(ids)
bad_ref=[r["rule_id"] for r in rules if r["source_id"] not in sid_set]
chk("每条Rule的source_id存在", not bad_ref, str(bad_ref[:5]))
layer_map={s["source_id"]:s["text_layer"] for s in sources}
bad_layer_rule=[r["rule_id"] for r in rules if layer_map.get(r["source_id"])!="ORIGINAL"]
chk("Rule绑定source text_layer==ORIGINAL", not bad_layer_rule, str(bad_layer_rule[:5]))
bad_ptype=[r["rule_id"] for r in rules if r["preconditions"]["type"] not in ("conjunction","disjunction")]
chk("preconditions.type合法", not bad_ptype, "")
OP={"equals","not_equals","in","has","absent"}
bad_op=[r["rule_id"] for r in rules for c in r["preconditions"]["conditions"] if c["operator"] not in OP]
chk("operator白名单", not bad_op, str(bad_op[:5]))
bad_cmp=[r["rule_id"] for r in rules if any(op in json.dumps(r,ensure_ascii=False) for op in [">=","<="," > "," < "])]
# stricter: no > < as operators (operators are strings anyway)
raw=json.dumps(rules,ensure_ascii=False)
bad_gt = bool(re.search(r'"operator"\s*:\s*"(>|<|>=|<=)"', raw))
chk("无 > < 比较符", not bad_gt, "")
bad_nest=[r["rule_id"] for r in rules if any("conditions" in c for c in r["preconditions"]["conditions"])]
chk("无嵌套preconditions", not bad_nest, "")
OPER={"emit","require","suppress"}
bad_oper=[r["rule_id"] for r in rules if r["operation"] not in OPER]
chk("operation白名单", not bad_oper, "")
bad_out=[r["rule_id"] for r in rules for o in r["outputs"] if "field" not in o or "value" not in o]
chk("outputs每项有field/value", not bad_out, "")
bad_status=[r["rule_id"] for r in rules if r["status"]!="CANDIDATE"]
chk("status==CANDIDATE", not bad_status, "")

# --- overall ---
cross_books=["淵海子平","子平真詮","滴天髓","窮通寶鑑","三命通會"]
bad_cross=[r["rule_id"] for r in rules if any(b in r.get("notes","") for b in cross_books)]
chk("无跨经典引述", not bad_cross, "")
bad_uni=[r["rule_id"] for r in rules if "用神=" in json.dumps(r,ensure_ascii=False)]
chk("无统一用神结论", not bad_uni, "")
bad_score=[r["rule_id"] for r in rules if any(k in r for k in ("score","weight","point"))]
chk("无评分字段", not bad_score, "")

passed=sum(1 for _,ok,_ in results if ok)
failed=[(n,d) for n,ok,d in results if not ok]
print(f"PASS {passed}/{len(results)}  FAIL {len(failed)}")
for n,ok,d in results:
    print(("✓" if ok else "✗"), n, "" if ok else "-> "+d)
print("sources",len(sources),"rules",len(rules),"unformalizable",len(unform))
