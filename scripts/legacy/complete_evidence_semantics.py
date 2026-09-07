"""
补全 DTS 和 PZZQ 证据的语义字段（v4 重写）
"""
import json
import glob
import re
from datetime import datetime, timezone

BASE = r"C:/Users/wisdom/wisdom/data"
EVIDENCE_DIR = BASE + "/evidence"
RULES_DIR = BASE + "/rules"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_dts_enum_val(eid):
    m = re.search(r"E-DTS-(\d+)-", eid)
    return m.group(1) if m else None  # keep as string to match dict keys


def load_dts_rules():
    rules = {}
    for fpath in sorted(glob.glob(RULES_DIR + "/DTS-*.json")):
        with open(fpath, encoding="utf-8") as f:
            d = json.load(f)
        rid = d["rule_id"]
        for er in d.get("evidence_refs", []):
            m = re.search(r"E-DTS-(\d+)-", er)
            if m:
                enum_val = m.group(1)
                if enum_val not in rules:
                    rules[enum_val] = []
                rules[enum_val].append(rid)
    return rules


def extract_note_type(notes):
    if not notes:
        return None
    m = re.search(r"证据类型:\s*([^\s，,、]+)", notes)
    if m:
        return m.group(1)
    return None


def complete_dts_evidence():
    dts_rules = load_dts_rules()
    print(f"Loaded {len(dts_rules)} DTS rule mappings: {dts_rules}")
    
    pattern = EVIDENCE_DIR + "/di_tian_sui/E-DTS-*.json"
    dts_files = sorted(glob.glob(pattern))
    completed = 0
    for fpath in dts_files:
        with open(fpath, encoding="utf-8") as f:
            d = json.load(f)
        eid = d["evidence_id"]
        enum_val = get_dts_enum_val(eid)
        notes = d.get("notes", "")
        note_type = extract_note_type(notes)
        
        print(f"  Processing {eid}: enum_val={enum_val}, note_type={note_type}")
        print(f"    dts_rules.get({enum_val!r}) = {dts_rules.get(enum_val)}")

        # observation_dimension
        if not d.get("observation_dimension"):
            d["observation_dimension"] = note_type or "OTHER"

        # rule_refs
        if "rule_refs" not in d or not d.get("rule_refs"):
            d["rule_refs"] = dts_rules.get(enum_val, [f"DTS-{enum_val}"])

        # citation
        if "citation" not in d:
            original_text = d.get("original_text", "")
            citation = {"original_text": original_text, "language": "classical_chinese"}
            if original_text.startswith("(待校,paraphrase)"):
                citation["verification_status"] = "pending_verification"
            d["citation"] = citation

        # source_layer
        if "source_layer" not in d:
            ct = d.get("citation", {}).get("original_text", "")
            d["source_layer"] = "paraphrase" if ct.startswith("(待校,paraphrase)") else "classical_original"

        # evidence_strength
        if "evidence_strength" not in d:
            d["evidence_strength"] = "tertiary" if d.get("source_layer") == "paraphrase" else "primary"

        # version
        if "version" not in d:
            d["version"] = "1.0.0"

        # timestamps
        if "created_at" not in d:
            d["created_at"] = NOW
        d["updated_at"] = NOW

        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        completed += 1
        print(f"    -> dim={d['observation_dimension']}, refs={d.get('rule_refs')}")
    return completed


def complete_pzzq_evidence():
    pattern = EVIDENCE_DIR + "/ziping_zhenquan/E-ZIPI-*.json"
    pzzq_files = sorted(glob.glob(pattern))
    completed = 0
    for fpath in pzzq_files:
        with open(fpath, encoding="utf-8") as f:
            d = json.load(f)
        eid = d["evidence_id"]
        etype = d.get("evidence_type", "")

        if "rule_refs" not in d or not d.get("rule_refs"):
            d["rule_refs"] = [f"PZZQ-{etype}"]

        if not d.get("observation_dimension"):
            d["observation_dimension"] = etype

        if "citation" not in d:
            d["citation"] = {"original_text": d.get("original_text", ""), "language": "classical_chinese"}

        if "source_layer" not in d:
            d["source_layer"] = "classical_original"

        if "evidence_strength" not in d:
            d["evidence_strength"] = "primary"

        if "version" not in d:
            d["version"] = "1.0.0"

        if "created_at" not in d:
            d["created_at"] = NOW
        d["updated_at"] = NOW

        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        completed += 1
        print(f"  ✓ {eid}: type={etype}")
    return completed


if __name__ == "__main__":
    print("=== DTS ===")
    dts_n = complete_dts_evidence()
    print(f"DTS done: {dts_n}")
    print("\n=== PZZQ ===")
    pzzq_n = complete_pzzq_evidence()
    print(f"PZZQ done: {pzzq_n}")
    print(f"\nTotal: DTS={dts_n}, PZZQ={pzzq_n}")
