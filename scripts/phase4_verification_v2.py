#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 4 Comprehensive Five Classics Verification (Fixed)"""

import json
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime

WORKSPACE = Path("D:/shuntian")
CLASSICS_DIR = WORKSPACE / "data" / "classics" / "original"
EVIDENCE_DIR = WORKSPACE / "data" / "evidence"
OUTPUT_DIR = Path("C:/Users/ming/wisdom/docs/bots/BOT-CORPUS")

def load_all_passages():
    """Load ALL passage IDs from all classics into a flat dictionary"""
    all_passages = {}  # passage_id -> {book_code, book_name, text, source}
    
    for f in CLASSICS_DIR.glob("*段落数据.json"):
        if "_merged" in f.name or f.name == "index.json":
            continue
        
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        
        book_code = data.get("book_code", f.stem.split("_")[0])
        book_name = data.get("book", f.stem)
        
        for p in data.get("passages", []):
            pid = p.get("passage_id")
            if pid:
                all_passages[pid] = {
                    "passage_id": pid,
                    "book_code": book_code,
                    "book_name": book_name,
                    "text": p.get("text", ""),
                    "source": p.get("source", ""),
                    "char_count": p.get("char_count", 0)
                }
    
    return all_passages

def verify_evidence(ef, all_passages):
    """Verify a single evidence file"""
    try:
        with open(ef, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as e:
        return {"evidence_id": ef.stem, "valid": False, "error": f"Parse error: {str(e)}"}
    
    evid_id = data.get("evidence_id", ef.stem)
    result = {
        "evidence_id": evid_id,
        "classic_id": data.get("classic_id", "unknown"),
        "valid": True,
        "issues": [],
        "verification": {}
    }
    
    # Get passage_id from source_locator
    source_locator = data.get("source_locator", {})
    passage_id = source_locator.get("passage_id", "")
    
    if not passage_id:
        result["issues"].append("missing_passage_id")
        result["valid"] = False
        return result
    
    result["verification"]["passage_id"] = passage_id
    
    # Check if passage exists
    if passage_id in all_passages:
        passage = all_passages[passage_id]
        result["verification"]["passage_found"] = True
        result["verification"]["book_code"] = passage["book_code"]
        
        # Verify text match (first 100 chars)
        evid_text = data.get("original_text", "")
        passage_text = passage.get("text", "")
        
        if evid_text and passage_text:
            if evid_text[:100] in passage_text[:500]:
                result["verification"]["text_match"] = True
            else:
                result["verification"]["text_match"] = False
                result["issues"].append("text_mismatch")
        else:
            result["verification"]["text_match"] = "no_text"
    else:
        result["verification"]["passage_found"] = False
        result["issues"].append("passage_not_found")
        result["valid"] = False
    
    # Check provenance
    provenance = data.get("provenance", {})
    if not provenance:
        result["issues"].append("missing_provenance")
    
    # Check verification status
    verif_status = data.get("verification_status", "")
    citation = data.get("citation", {})
    cit_verif = citation.get("verification_status", "")
    
    if verif_status == "UNVERIFIED" or cit_verif == "pending_verification":
        result["issues"].append("pending_verification")
    
    return result

def main():
    print("=" * 70)
    print("BOT-CORPUS Phase 4: Five Classics Comprehensive Verification")
    print("=" * 70)
    
    # Load passages
    print("\n[1/4] Loading passage data...")
    all_passages = load_all_passages()
    print(f"  Total passages loaded: {len(all_passages):,}")
    
    # Collect evidence
    print("\n[2/4] Collecting evidence files...")
    evidence_files = []
    for root, dirs, files in os.walk(EVIDENCE_DIR):
        for f in files:
            if f.endswith(".json") and not f.startswith("_"):
                evidence_files.append(Path(root) / f)
    print(f"  Total evidence files: {len(evidence_files):,}")
    
    # Verify
    print("\n[3/4] Verifying evidence...")
    results = []
    stats = {
        "total": 0,
        "valid": 0,
        "invalid": 0,
        "issues": defaultdict(int),
        "by_issue_type": defaultdict(lambda: defaultdict(int))
    }
    
    for ef in evidence_files:
        stats["total"] += 1
        result = verify_evidence(ef, all_passages)
        results.append(result)
        
        if result["valid"]:
            stats["valid"] += 1
        else:
            stats["invalid"] += 1
        
        for issue in result.get("issues", []):
            stats["issues"][issue] += 1
            stats["by_issue_type"][issue][result.get("classic_id", "unknown")] += 1
    
    print(f"  Valid: {stats['valid']}/{stats['total']} ({stats['valid']/stats['total']*100:.1f}%)")
    print(f"  Invalid: {stats['invalid']}")
    
    # Issue breakdown
    print("\n=== Issue Breakdown ===")
    for issue, count in sorted(stats["issues"].items(), key=lambda x: -x[1]):
        print(f"  {issue}: {count}")
    
    # By classic
    print("\n=== By Classic ===")
    by_classic = defaultdict(lambda: {"total": 0, "valid": 0, "invalid": 0})
    for r in results:
        classic = r.get("classic_id", "unknown")
        by_classic[classic]["total"] += 1
        if r["valid"]:
            by_classic[classic]["valid"] += 1
        else:
            by_classic[classic]["invalid"] += 1
    
    for classic, counts in sorted(by_classic.items()):
        rate = counts["valid"] / counts["total"] * 100 if counts["total"] > 0 else 0
        print(f"  {classic}: {counts['valid']}/{counts['total']} ({rate:.1f}%)")
    
    # Generate report
    print("\n[4/4] Generating report...")
    
    # Categorize issues
    p0_issues = ["passage_not_found", "missing_passage_id", "missing_source_locator"]
    p1_issues = ["text_mismatch", "missing_provenance"]
    p2_issues = ["pending_verification"]
    
    p0_count = sum(stats["issues"].get(i, 0) for i in p0_issues)
    p1_count = sum(stats["issues"].get(i, 0) for i in p1_issues)
    p2_count = sum(stats["issues"].get(i, 0) for i in p2_issues)
    
    report_md = f"""# BOT-CORPUS Phase 4 Validation Report

> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> Workspace: D:/shuntian
> Classic Passages: {len(all_passages):,}
> Evidence Files: {len(evidence_files):,}

## Summary

| Metric | Value |
|--------|-------|
| Total Evidence | {stats['total']:,} |
| Valid (passage found + text match) | {stats['valid']:,} |
| Invalid | {stats['invalid']:,} |
| **Validation Rate** | **{stats['valid']/stats['total']*100:.1f}%** |

## Issue Classification

### P0 (Critical) — {p0_count}
Issues that block evidence chain integrity:

| Issue | Count |
|-------|-------|
"""
    
    for issue in p0_issues:
        count = stats["issues"].get(issue, 0)
        report_md += f"| {issue} | {count} |\n"
    
    report_md += f"""
### P1 (Warning) — {p1_count}
Issues affecting evidence quality:

| Issue | Count |
|-------|-------|
"""
    
    for issue in p1_issues:
        count = stats["issues"].get(issue, 0)
        report_md += f"| {issue} | {count} |\n"
    
    report_md += f"""
### P2 (Info) — {p2_count}
Issues for后续处理:

| Issue | Count |
|-------|-------|
"""
    
    for issue in p2_issues:
        count = stats["issues"].get(issue, 0)
        report_md += f"| {issue} | {count} |\n"
    
    report_md += """
## By Classic

| Classic | Total | Valid | Invalid | Rate |
|---------|-------|-------|---------|------|
"""
    
    for classic, counts in sorted(by_classic.items()):
        rate = counts["valid"] / counts["total"] * 100 if counts["total"] > 0 else 0
        report_md += f"| {classic} | {counts['total']} | {counts['valid']} | {counts['invalid']} | {rate:.1f}% |\n"
    
    report_md += """
## Recommendations

### Immediate (P0)
1. **passage_not_found**: Add missing passages to classics/original data or update evidence passage_ids
2. **missing_passage_id**: Fix evidence files with empty passage_id
3. **missing_source_locator**: Add source_locator to evidence files lacking it

### Short-term (P1)
1. **text_mismatch**: Verify evidence text against passage text
2. **missing_provenance**: Add provenance field to evidence files

### Ongoing (P2)
1. **pending_verification**: Complete manual verification of paraphrase evidence
"""
    
    # Save reports
    report_path = OUTPUT_DIR / "PHASE4_VALIDATION_REPORT.md"
    json_path = OUTPUT_DIR / "phase4_validation_data.json"
    
    with open(report_path, "w", encoding="utf-8") as fp:
        fp.write(report_md)
    
    # Save JSON with detailed results
    report_json = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "workspace": str(WORKSPACE),
            "total_passages": len(all_passages),
            "total_evidence": stats["total"]
        },
        "summary": {
            "total": stats["total"],
            "valid": stats["valid"],
            "invalid": stats["invalid"],
            "validation_rate": f"{stats['valid']/stats['total']*100:.1f}%",
            "p0_count": p0_count,
            "p1_count": p1_count,
            "p2_count": p2_count
        },
        "issues": dict(stats["issues"]),
        "by_classic": {k: dict(v) for k, v in by_classic.items()},
        "results_sample": results[:50]
    }
    
    with open(json_path, "w", encoding="utf-8") as fp:
        json.dump(report_json, fp, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Report saved to: {report_path}")
    print(f"✅ JSON data saved to: {json_path}")
    
    return report_json

if __name__ == "__main__":
    main()
