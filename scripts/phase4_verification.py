#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 4 Comprehensive Five Classics Verification for BOT-CORPUS"""

import json
import os
import hashlib
from pathlib import Path
from collections import defaultdict
from datetime import datetime

WORKSPACE = Path("D:/shuntian")
CLASSICS_DIR = WORKSPACE / "data" / "classics" / "original"
EVIDENCE_DIR = WORKSPACE / "data" / "evidence"
RULES_DIR = WORKSPACE / "data" / "rules"
OUTPUT_DIR = Path("C:/Users/ming/wisdom/docs/bots/BOT-CORPUS")

def compute_hash(content):
    """Compute SHA256 hash of content"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def load_classics_data():
    """Load all passage data from classics"""
    classics = {}
    
    for f in CLASSICS_DIR.glob("*段落数据.json"):
        if "_merged" in f.name or f.name == "index.json":
            continue
        
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        
        book_code = data.get("book_code", f.stem.split("_")[0])
        classics[book_code] = {
            "name": data.get("book", f.stem),
            "total_passages": data.get("total_passages", 0),
            "total_chars": data.get("total_chars", 0),
            "passages": {},
            "sources": data.get("source_distribution", {})
        }
        
        for p in data.get("passages", []):
            pid = p.get("passage_id")
            if pid:
                classics[book_code]["passages"][pid] = {
                    "text": p.get("text", ""),
                    "source": p.get("source", ""),
                    "char_count": p.get("char_count", 0)
                }
    
    return classics

def verify_evidence_against_classics(evidence_file, classics):
    """Verify a single evidence file against classics data"""
    try:
        with open(evidence_file, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as e:
        return {"error": f"Parse error: {str(e)}", "valid": False}
    
    evid_id = data.get("evidence_id", evidence_file.stem)
    result = {
        "evidence_id": evid_id,
        "classic_id": data.get("classic_id", "unknown"),
        "valid": True,
        "issues": [],
        "verification": {}
    }
    
    # Check source_locator
    source_locator = data.get("source_locator", {})
    if not source_locator:
        result["issues"].append("missing_source_locator")
        result["valid"] = False
        return result
    
    passage_id = source_locator.get("passage_id", "")
    classic = source_locator.get("classic", "")
    
    if not passage_id:
        result["issues"].append("missing_passage_id")
        result["valid"] = False
        return result
    
    # Check passage exists in classics
    if classic in classics and passage_id in classics[classic]["passages"]:
        passage = classics[classic]["passages"][passage_id]
        
        # Verify text match (first 50 chars)
        evid_text = data.get("original_text", "")
        passage_text = passage.get("text", "")
        
        if evid_text and passage_text:
            if evid_text[:100] in passage_text[:500]:
                result["verification"]["text_match"] = True
            else:
                result["verification"]["text_match"] = False
                result["issues"].append("text_mismatch")
        else:
            result["verification"]["text_match"] = "no_text_to_compare"
        
        result["verification"]["passage_found"] = True
    else:
        result["verification"]["passage_found"] = False
        result["issues"].append("passage_not_found")
        result["valid"] = False
    
    # Check provenance completeness
    provenance = data.get("provenance", {})
    if not provenance:
        result["issues"].append("missing_provenance")
        result["valid"] = False
    
    required_fields = ["classic", "work", "chapter", "passage_id"]
    for field in required_fields:
        if field not in provenance and field not in source_locator:
            result["issues"].append(f"missing_field_{field}")
    
    # Check verification status
    verif_status = data.get("verification_status", "")
    citation = data.get("citation", {})
    verif_from_citation = citation.get("verification_status", "")
    
    if verif_status == "UNVERIFIED" or verif_from_citation == "pending_verification":
        result["issues"].append("pending_verification")
    
    return result

def analyze_coverage(classics, evidence_results):
    """Analyze coverage by topic"""
    coverage = {
        "five_elements": {"expected": 5, "found": set()},
        "ten_gods": {"expected": 10, "found": set()},
        "stems": {"expected": 10, "found": set()},
        "branches": {"expected": 12, "found": set()},
        "patterns": {"expected": 8, "found": set()},
        "climates": {"expected": 12, "found": set()}
    }
    
    # Analyze evidence types
    for result in evidence_results:
        evidence_type = result.get("evidence_type", "")
        evid_id = result.get("evidence_id", "")
        
        # Categorize by type
        if any(elem in evid_id.upper() for elem in ["WOOD", "WOOD", "JIA", "YI"]):
            coverage["five_elements"]["found"].add("WOOD")
        if any(elem in evid_id.upper() for elem in ["FIRE", "BING", "DING"]):
            coverage["five_elements"]["found"].add("FIRE")
        if any(elem in evid_id.upper() for elem in ["EARTH", "WU", "JI"]):
            coverage["five_elements"]["found"].add("EARTH")
        if any(elem in evid_id.upper() for elem in ["METAL", "GENG", "XIN"]):
            coverage["five_elements"]["found"].add("METAL")
        if any(elem in evid_id.upper() for elem in ["WATER", "REN", "GUI"]):
            coverage["five_elements"]["found"].add("WATER")
    
    return coverage

def main():
    print("=" * 70)
    print("BOT-CORPUS Phase 4: Five Classics Comprehensive Verification")
    print("=" * 70)
    
    # Load classics data
    print("\n[1/5] Loading classics data...")
    classics = load_classics_data()
    total_passages = sum(c["total_passages"] for c in classics.values())
    print(f"  Loaded {len(classics)} classics, {total_passages} total passages")
    
    # Collect all evidence files
    print("\n[2/5] Collecting evidence files...")
    evidence_files = []
    for root, dirs, files in os.walk(EVIDENCE_DIR):
        for f in files:
            if f.endswith(".json") and not f.startswith("_"):
                evidence_files.append(Path(root) / f)
    print(f"  Found {len(evidence_files)} evidence files")
    
    # Verify each evidence
    print("\n[3/5] Verifying evidence...")
    results = []
    stats = {
        "total": 0,
        "valid": 0,
        "invalid": 0,
        "issues": defaultdict(int)
    }
    
    for ef in evidence_files:
        stats["total"] += 1
        result = verify_evidence_against_classics(ef, classics)
        results.append(result)
        
        if result["valid"]:
            stats["valid"] += 1
        else:
            stats["invalid"] += 1
            for issue in result.get("issues", []):
                stats["issues"][issue] += 1
    
    print(f"  Verified: {stats['valid']}/{stats['total']}")
    print(f"  Invalid: {stats['invalid']}")
    
    # Analyze by classic
    print("\n[4/5] Analysis by classic...")
    by_classic = defaultdict(lambda: {"total": 0, "valid": 0, "invalid": 0})
    
    for result in results:
        classic = result.get("classic_id", "unknown")
        by_classic[classic]["total"] += 1
        if result["valid"]:
            by_classic[classic]["valid"] += 1
        else:
            by_classic[classic]["invalid"] += 1
    
    for classic, counts in sorted(by_classic.items()):
        rate = counts["valid"] / counts["total"] * 100 if counts["total"] > 0 else 0
        print(f"  {classic}: {counts['valid']}/{counts['total']} ({rate:.1f}%)")
    
    # Issue summary
    print("\n=== Issue Summary ===")
    for issue, count in sorted(stats["issues"].items(), key=lambda x: -x[1]):
        print(f"  {issue}: {count}")
    
    # Generate report
    print("\n[5/5] Generating report...")
    
    report = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "workspace": str(WORKSPACE),
            "total_passages": total_passages,
            "total_evidence": stats["total"]
        },
        "summary": {
            "total_evidence": stats["total"],
            "valid": stats["valid"],
            "invalid": stats["invalid"],
            "validation_rate": f"{stats['valid']/stats['total']*100:.1f}%" if stats["total"] > 0 else "N/A"
        },
        "by_classic": dict(by_classic),
        "issues": dict(stats["issues"]),
        "classics_data": {
            bc: {
                "name": c["name"],
                "total_passages": c["total_passages"],
                "total_chars": c["total_chars"],
                "sources": c["sources"]
            }
            for bc, c in classics.items()
        },
        "detailed_results": results[:100]  # First 100 for brevity
    }
    
    report_path = OUTPUT_DIR / "PHASE4_VALIDATION_REPORT.md"
    json_path = OUTPUT_DIR / "phase4_validation_data.json"
    
    # Write markdown report
    with open(report_path, "w", encoding="utf-8") as fp:
        fp.write("# BOT-CORPUS Phase 4 Validation Report\n\n")
        fp.write(f"> Generated: {report['metadata']['generated_at']}\n")
        fp.write(f"> Workspace: {report['metadata']['workspace']}\n\n")
        
        fp.write("## Summary\n\n")
        fp.write(f"| Metric | Value |\n|--------|-------|\n")
        fp.write(f"| Total Evidence | {report['summary']['total_evidence']} |\n")
        fp.write(f"| Valid | {report['summary']['valid']} |\n")
        fp.write(f"| Invalid | {report['summary']['invalid']} |\n")
        fp.write(f"| Validation Rate | {report['summary']['validation_rate']} |\n\n")
        
        fp.write("## By Classic\n\n")
        fp.write("| Classic | Total | Valid | Invalid | Rate |\n")
        fp.write("|---------|-------|-------|---------|------|\n")
        for classic, counts in sorted(by_classic.items()):
            rate = counts["valid"] / counts["total"] * 100 if counts["total"] > 0 else 0
            fp.write(f"| {classic} | {counts['total']} | {counts['valid']} | {counts['invalid']} | {rate:.1f}% |\n")
        
        fp.write("\n## Issue Classification\n\n")
        fp.write("### P0 (Critical)\n")
        p0_issues = [i for i in stats["issues"].keys() if "missing" in i.lower() or "not_found" in i.lower()]
        for issue in p0_issues:
            fp.write(f"- {issue}: {stats['issues'][issue]}\n")
        
        fp.write("\n### P1 (Warning)\n")
        p1_issues = [i for i in stats["issues"].keys() if "pending" in i.lower() or "mismatch" in i.lower()]
        for issue in p1_issues:
            fp.write(f"- {issue}: {stats['issues'][issue]}\n")
        
        fp.write("\n### P2 (Info)\n")
        p2_issues = [i for i in stats["issues"].keys() if i not in p0_issues + p1_issues]
        for issue in p2_issues:
            fp.write(f"- {issue}: {stats['issues'][issue]}\n")
        
        fp.write("\n## Classics Data Overview\n\n")
        for bc, data in report["classics_data"].items():
            fp.write(f"### {data['name']} ({bc})\n")
            fp.write(f"- Total passages: {data['total_passages']:,}\n")
            fp.write(f"- Total chars: {data['total_chars']:,}\n")
            fp.write(f"- Sources: {', '.join(data['sources'].keys())}\n\n")
    
    # Write JSON data
    with open(json_path, "w", encoding="utf-8") as fp:
        json.dump(report, fp, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Report saved to: {report_path}")
    print(f"✅ JSON data saved to: {json_path}")
    
    return report

if __name__ == "__main__":
    main()
