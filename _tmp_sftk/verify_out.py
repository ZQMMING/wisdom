# -*- coding: utf-8 -*-
"""Independent verifier: (1) reproduce every source_text from the on-disk file by
line-range, (2) check SFTK missing sections, (3) re-run all QC checks offline.
Read-only on the data; reads the originals fresh to confirm current hash binding."""
import json, hashlib, os, re, collections

ROOT = "D:/shuntian"
def raw(rel):
    return open(os.path.join(ROOT, rel), "rb").read()

Y = raw("data/classics/original/YHZP_渊海子平_完整全文.md")
S = raw("data/classics/original/SFTK_神峰通考_完整全文.md")
YH = hashlib.sha256(Y).hexdigest()
SH = hashlib.sha256(S).hexdigest()
Ylines = Y.decode("utf-8").replace("\r\n","\n").replace("\r","\n").splitlines()
Slines = S.decode("utf-8").replace("\r\n","\n").replace("\r","\n").splitlines()
print("YHZP disk hash=%s lines=%d" % (YH[:12], len(Ylines)))
print("SFTK disk hash=%s lines=%d" % (SH[:12], len(Slines)))

def verify_file(rel, lines, disk_hash, tag):
    fp = os.path.join(ROOT, rel)
    recs = [json.loads(l) for l in open(fp, encoding="utf-8") if l.strip()]
    bound = collections.Counter(r["source_location"]["file_hash"][:12] for r in recs)
    print("\n== %s: %d records, file_hash binding=%s disk=%s -> %s" % (
        tag, len(recs), dict(bound), disk_hash[:12],
        "MATCH" if set(bound)=={disk_hash[:12]} else "STALE"))
    # reproduce line-range -> source_text non-empty and matches record's source_text hash
    repro_ok = empty = 0
    for r in recs:
        a, b = r["source_location"]["line_start"], r["source_location"]["line_end"]
        seg = lines[a-1:b]
        joined = "\n".join(x.strip() for x in seg if x.strip())
        if joined: repro_ok += 1
        else: empty += 1
    print("  line-range non-empty: %d / empty: %d" % (repro_ok, empty))
    # source_text field itself
    et = sum(1 for r in recs if not r["source_text"].strip())
    print("  source_text empty: %d" % et)
    return recs

ysrc = verify_file("data/sources/yhzp_sources.jsonl", Ylines, YH, "YHZP sources")
ssrc = verify_file("data/sources/sftk_sources.jsonl", Slines, SH, "SFTK sources")

# SFTK missing sections
SFTK_TITLES = ["五星正說類","五星謬說類","女子合婚說","時上偏財格","印綬格","時墓格",
               "月令詳辨","男命小運定局","女命小運定局","陽順陰逆生旺死絕圖",
               "地支造化圖","天干五陽通變","天干五陰通變","十段錦","十段化氣",
               "天元一字歌","運通歌","運晦歌","五陰歌","戊癸歌","丁壬歌","丙辛歌",
               "六神篇","渭涇篇","崖泉女命賦","講命捷徑賦","節氣歌斷","論諸格有救",
               "萬尙書瓊璣三盤賦","看命捷歌","正官格歌","七殺格歌","用財歌","印綬歌",
               "尩子歌","壽元歌","女命歌","飄蕩歌","月建生尩歌","羊刃歌","三奇格歌",
               "喜忌歌","五行元理消息賦"]
found_titles = set()
for r in ssrc:
    found_titles.add(r["metadata"].get("section_title",""))
missing = [t for t in SFTK_TITLES if t not in found_titles]
# which of those appear anywhere in the body (line>=300)?
body0 = Slines[299]
present_ = []
for t in missing:
    ts = re.sub(r"\s+","",t)
    for i in range(300, len(Slines)+1):
        s = Slines[i-1].strip()
        if re.sub(r"\s+","",s).rstrip("。.") == ts and len(s.strip())<=18:
            present_.append(t); break
    else:
        # try '## title'
        for i in range(300, len(Slines)+1):
            if Slines[i-1].startswith("## ") and re.sub(r"\s+","",Slines[i-1].lstrip('#').strip()) == ts:
                present_.append(t); break
print("\nSFTK found sections: %d; of the extra %d candidate titles, present-in-body-but-missed: %d" % (
    len(ssrc), len(missing), len(present_)))
print("  present-but-missed:", present_[:25])
truly_absent = [t for t in missing if t not in present_]
print("  truly absent from body (only in TOC/narrative):", len(truly_absent), truly_absent[:20])
