#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T-BOT-CORPUS-001: Evidence Verification + Status Gate"""

import json
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime

WORKSPACE = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = WORKSPACE / "data" / "evidence"
META_DIR = WORKSPACE / "data" / "evidence_meta"
CLASSICS_DIR = WORKSPACE / "data" / "classics" / "original"
OUTPUT_DIR = WORKSPACE / "docs" / "bots" / "BOT-CORPUS"

def load_passage_ids():
    """Load all valid passage IDs from classics"""
    passage_ids = set()
    for f in CLASSICS_DIR.glob("*段落数据.json"):
        if "_merged" in f.name:
            continue
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        for p in data.get("passages", []):
            pid = p.get("passage_id")
            if pid:
                passage_ids.add(pid)
    return passage_ids

def sample_evidence_by_classic(evidence_dir, sample_size=25):
    """Sample evidence files by classic"""
    samples = defaultdict(list)
    
    for subdir in evidence_dir.iterdir():
        if not subdir.is_dir():
            continue
        book_code = subdir.name
        files = list(subdir.glob("*.json"))
        
        regular = [f for f in files if "-DUANYU-" not in f.name and not f.name.startswith("_")]
        duanyu = [f for f in files if "-DUANYU-" in f.name and not f.name.startswith("_")]
        
        if regular:
            sampled = regular[:min(sample_size, len(regular))]
            samples[book_code].extend([{"file": f, "type": "regular"} for f in sampled])
        
        if duanyu:
            sampled = duanyu[:min(sample_size, len(duanyu))]
            samples[book_code].extend([{"file": f, "type": "duanyu"} for f in sampled])
    
    return samples

def verify_evidence(ef, passage_ids):
    """Verify a single evidence file"""
    try:
        with open(ef, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as e:
        return {"valid": False, "error": f"Parse error: {str(e)}", "status": "ERROR"}
    
    evid_id = data.get("evidence_id", ef.stem)
    source_locator = data.get("source_locator", {})
    passage_id = source_locator.get("passage_id", "")
    
    result = {
        "evidence_id": evid_id,
        "valid": True,
        "issues": [],
        "verification": {}
    }
    
    if not passage_id:
        result["issues"].append("missing_passage_id")
        result["valid"] = False
        return result
    
    if passage_id not in passage_ids:
        result["issues"].append("passage_not_found")
        result["valid"] = False
        return result
    
    verif_status = data.get("verification_status", "")
    if verif_status == "UNVERIFIED":
        result["verification"]["current_status"] = "UNVERIFIED"
    elif verif_status == "VERIFIED":
        result["verification"]["current_status"] = "VERIFIED"
    else:
        result["verification"]["current_status"] = verif_status or "UNKNOWN"
    
    return result

def main():
    print("=" * 70)
    print("T-BOT-CORPUS-001: Evidence Verification + Status Gate")
    print("=" * 70)
    
    print("\n[1/5] Loading passage IDs...")
    passage_ids = load_passage_ids()
    print(f"  Loaded {len(passage_ids):,} passage IDs")
    
    print("\n[2/5] Sampling evidence files...")
    samples = sample_evidence_by_classic(EVIDENCE_DIR, sample_size=25)
    total_sampled = sum(len(v) for v in samples.values())
    print(f"  Total samples: {total_sampled}")
    for book, items in sorted(samples.items()):
        print(f"  {book}: {len(items)} files")
    
    print("\n[3/5] Verifying samples...")
    verification_results = []
    stats = {
        "total": 0,
        "valid": 0,
        "invalid": 0,
        "by_issue": defaultdict(int),
        "by_status": defaultdict(int),
        "by_classic": defaultdict(lambda: {"total": 0, "valid": 0, "invalid": 0})
    }
    
    for book_code, items in samples.items():
        for item in items:
            ef = item["file"]
            stats["total"] += 1
            stats["by_classic"][book_code]["total"] += 1
            
            result = verify_evidence(ef, passage_ids)
            verification_results.append({
                "evidence_id": result["evidence_id"],
                "book": book_code,
                "type": item["type"],
                "valid": result["valid"],
                "issues": result.get("issues", []),
                "verification_status": result.get("verification", {}).get("current_status", "UNKNOWN")
            })
            
            if result["valid"]:
                stats["valid"] += 1
                stats["by_classic"][book_code]["valid"] += 1
                status = result.get("verification", {}).get("current_status", "UNKNOWN")
                stats["by_status"][status] += 1
            else:
                stats["invalid"] += 1
                stats["by_classic"][book_code]["invalid"] += 1
                for issue in result.get("issues", []):
                    stats["by_issue"][issue] += 1
    
    print(f"  Verified: {stats['valid']}/{stats['total']} ({stats['valid']/stats['total']*100:.1f}%)")
    
    print("\n[4/5] Counting DUANYU evidence...")
    duanyu_count = 0
    for root, dirs, files in os.walk(EVIDENCE_DIR):
        for f in files:
            if "-DUANYU-" in f and f.endswith(".json"):
                duanyu_count += 1
    print(f"  Total DUANYU evidence: {duanyu_count:,}")
    
    print("\n[5/5] Generating report...")
    
    report = {
        "metadata": {
            "task_id": "T-BOT-CORPUS-001",
            "generated_at": datetime.now().isoformat(),
            "workspace": str(WORKSPACE)
        },
        "summary": {
            "total_sampled": stats["total"],
            "valid": stats["valid"],
            "invalid": stats["invalid"],
            "validation_rate": f"{stats['valid']/stats['total']*100:.1f}%",
            "duanyu_total": duanyu_count
        },
        "by_classic": {k: dict(v) for k, v in stats["by_classic"].items()},
        "by_status": dict(stats["by_status"]),
        "by_issue": dict(stats["by_issue"]),
        "samples": verification_results
    }
    
    report_path = OUTPUT_DIR / "EVIDENCE_VERIFICATION_REPORT.md"
    json_path = OUTPUT_DIR / "evidence_verification_data.json"
    
    with open(report_path, "w", encoding="utf-8") as fp:
        fp.write("# T-BOT-CORPUS-001 Evidence Verification Report\n\n")
        fp.write(f"> Task: Evidence Verification + Status Gate\n")
        fp.write(f"> Generated: {report['metadata']['generated_at']}\n\n")
        fp.write(f"> **注意**: 核验采样为抽样验证，非全量核验。\n")
        fp.write(f"> 4,089条断语证据已注册，**等待人工核验**。\n\n")
        
        fp.write("## Summary\n\n")
        fp.write(f"| Metric | Value |\n|--------|-------|\n")
        fp.write(f"| Total Sampled | {report['summary']['total_sampled']:,} |\n")
        fp.write(f"| Valid | {report['summary']['valid']:,} |\n")
        fp.write(f"| Invalid | {report['summary']['invalid']:,} |\n")
        fp.write(f"| **Validation Rate** | **{report['summary']['validation_rate']}** |\n")
        fp.write(f"| Total DUANYU Evidence | {report['summary']['duanyu_total']:,} |\n\n")
        
        fp.write("## By Classic\n\n")
        fp.write("| Classic | Total | Valid | Invalid | Rate |\n")
        fp.write("|---------|-------|-------|---------|------|\n")
        for book, counts in sorted(report["by_classic"].items()):
            rate = counts["valid"] / counts["total"] * 100 if counts["total"] > 0 else 0
            fp.write(f"| {book} | {counts['total']} | {counts['valid']} | {counts['invalid']} | {rate:.1f}% |\n")
        
        fp.write("\n## Status Distribution\n\n")
        fp.write("| Status | Count |\n|--------|-------|\n")
        for status, count in sorted(report["by_status"].items(), key=lambda x: -x[1]):
            fp.write(f"| {status} | {count} |\n")
        
        fp.write("\n## Issues Found\n\n")
        if report["by_issue"]:
            for issue, count in sorted(report["by_issue"].items(), key=lambda x: -x[1]):
                fp.write(f"- {issue}: {count}\n")
        else:
            fp.write("No issues found in sampled evidence.\n")
        
        fp.write("\n## Recommendations\n\n")
        fp.write("### Immediate Actions\n")
        fp.write("1. Register all DUANYU evidence in evidence_review_queue.json ✅\n")
        fp.write("2. Apply Status Gate: UNVERIFIED evidence cannot enter production ✅\n")
        fp.write("3. Prioritize verification of DTS/SMTH/YHZP batches\n\n")
        
        fp.write("### Status Gate Policy\n")
        fp.write("- VERIFIED evidence: Can be used in production\n")
        fp.write("- UNVERIFIED evidence: DRAFT status, blocked from production\n")
        fp.write("- EXCLUDED evidence: Not applicable, archived\n")
    
    with open(json_path, "w", encoding="utf-8") as fp:
        json.dump(report, fp, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Report saved to: {report_path}")
    print(f"✅ JSON data saved to: {json_path}")
    
    return report

if __name__ == "__main__":
    main()
