#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 5: Cross-Bot Evidence Asset Comprehensive Verification"""

import json
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime

WORKSPACE = Path("D:/shuntian")
EVIDENCE_DIR = WORKSPACE / "data" / "evidence"
RULES_DIR = WORKSPACE / "data" / "rules"
OUTPUT_DIR = Path("C:/Users/ming/wisdom/docs/bots/BOT-MASTER")

def verify_evidence_file(ef):
    """Verify a single evidence file structure and content"""
    try:
        with open(ef, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as e:
        return {
            "file": str(ef),
            "valid": False,
            "error": f"Parse error: {str(e)}",
            "issues": ["parse_error"]
        }
    
    evid_id = data.get("evidence_id", ef.stem)
    result = {
        "file": str(ef),
        "evidence_id": evid_id,
        "valid": True,
        "issues": [],
        "fields": {}
    }
    
    # Check required fields based on system type
    system = data.get("system", "")
    
    if system == "BLIND_SEGMENT":
        # Blind evidence schema
        required = ["evidence_id", "system", "provenance_layer", "source", "conditions"]
        for field in required:
            if field not in data or not data[field]:
                result["issues"].append(f"missing_{field}")
                result["valid"] = False
    else:
        # Five classics evidence schema
        required = ["evidence_id", "classic_id", "source_locator", "original_text"]
        for field in required:
            if field not in data or not data[field]:
                result["issues"].append(f"missing_{field}")
                result["valid"] = False
        
        # Check source_locator structure
        source_locator = data.get("source_locator", {})
        if source_locator:
            if "passage_id" not in source_locator:
                result["issues"].append("missing_passage_id")
                result["valid"] = False
    
    # Check verification status
    verif_status = data.get("verification_status", "")
    source_verif = data.get("source_verification", {}).get("status", "")
    
    result["fields"]["verification_status"] = verif_status or source_verif
    result["fields"]["source_fidelity"] = data.get("source_fidelity", "")
    result["fields"]["authority_status"] = data.get("authority_status", "")
    
    if verif_status == "UNVERIFIED" or source_verif == "PENDING":
        result["issues"].append("pending_verification")
    
    return result

def analyze_bot_evidence():
    """Analyze evidence for each bot"""
    
    bots = {
        "BOT-CORPUS": {"dir": None, "files": []},  # Five classics - handled separately
        "BOT-BLIND": {"dir": EVIDENCE_DIR / "blind_seg", "files": []},
        "BOT-ZIWEI": {"dir": EVIDENCE_DIR / "ziwei", "files": []},
        "BOT-HELUO": {"dir": EVIDENCE_DIR / "heluo", "files": []},
        "BOT-YI": {"dir": EVIDENCE_DIR / "yi", "files": []}
    }
    
    # Check which directories exist
    for bot_name, bot_info in bots.items():
        if bot_info["dir"] and bot_info["dir"].exists():
            bot_info["files"] = [f for f in bot_info["dir"].glob("*.json") if not f.name.startswith("_")]
        elif bot_name == "BOT-CORPUS":
            # Collect from all subdirectories
            for subdir in EVIDENCE_DIR.iterdir():
                if subdir.is_dir() and subdir.name not in ["blind_seg", "ziwei", "heluo", "yi", "reports"]:
                    bot_info["files"].extend([f for f in subdir.glob("*.json") if not f.name.startswith("_")])
            # Also include top-level evidence files
            bot_info["files"].extend([f for f in EVIDENCE_DIR.glob("E-*.json") if not f.name.startswith("_")])
    
    return bots

def main():
    print("=" * 70)
    print("BOT-CORPUS Phase 5: Cross-Bot Evidence Asset Verification")
    print("=" * 70)
    
    # Analyze bots
    print("\n[1/4] Scanning bot evidence directories...")
    bots = analyze_bot_evidence()
    
    for bot_name, bot_info in bots.items():
        print(f"  {bot_name}: {len(bot_info['files'])} evidence files")
    
    # Verify each bot's evidence
    print("\n[2/4] Verifying evidence files...")
    results = {bot: {"total": 0, "valid": 0, "invalid": 0, "issues": defaultdict(int)} for bot in bots}
    
    for bot_name, bot_info in bots.items():
        for ef in bot_info["files"]:
            results[bot_name]["total"] += 1
            result = verify_evidence_file(ef)
            
            if result["valid"]:
                results[bot_name]["valid"] += 1
            else:
                results[bot_name]["invalid"] += 1
            
            for issue in result.get("issues", []):
                results[bot_name]["issues"][issue] += 1
    
    # Print results
    print("\n=== Verification Results ===")
    for bot_name, stats in results.items():
        total = stats["total"]
        valid = stats["valid"]
        invalid = stats["invalid"]
        rate = valid / total * 100 if total > 0 else 0
        
        print(f"\n{bot_name}:")
        print(f"  Total: {total}, Valid: {valid}, Invalid: {invalid} ({rate:.1f}%)")
        
        if stats["issues"]:
            print(f"  Issues:")
            for issue, count in sorted(stats["issues"].items(), key=lambda x: -x[1])[:5]:
                print(f"    - {issue}: {count}")
    
    # Test coverage check
    print("\n[3/4] Checking test coverage...")
    tests_dir = WORKSPACE / "tests"
    test_files = []
    
    for pattern in ["test_blind*.py", "test_ziwei*.py", "test_heluo*.py", "test_yi*.py"]:
        test_files.extend(list(tests_dir.glob(pattern)))
    
    print(f"  Found {len(test_files)} test files for non-CORPUS bots")
    
    # Run tests if possible
    test_results = {}
    for tf in test_files[:5]:  # Sample first 5
        test_name = tf.stem
        test_results[test_name] = "SKIPPED"  # Would need pytest to run
    
    print(f"  Test results (first 5): {list(test_results.items())[:5]}")
    
    # Generate report
    print("\n[4/4] Generating report...")
    
    report = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "workspace": str(WORKSPACE),
            "verification_scope": "Cross-bot evidence assets"
        },
        "bots": {},
        "test_coverage": {
            "total_test_files": len(test_files),
            "results": test_results
        },
        "summary": {
            "total_evidence": sum(r["total"] for r in results.values()),
            "total_valid": sum(r["valid"] for r in results.values()),
            "total_invalid": sum(r["invalid"] for r in results.values()),
            "overall_rate": f"{sum(r['valid'] for r in results.values())/sum(r['total'] for r in results.values())*100:.1f}%" if sum(r['total'] for r in results.values()) > 0 else "N/A"
        }
    }
    
    for bot_name, stats in results.items():
        report["bots"][bot_name] = {
            "total": stats["total"],
            "valid": stats["valid"],
            "invalid": stats["invalid"],
            "rate": f"{stats['valid']/stats['total']*100:.1f}%" if stats["total"] > 0 else "N/A",
            "issues": dict(stats["issues"])
        }
    
    # Save reports
    report_path = OUTPUT_DIR / "PHASE5_ALIGNMENT_REPORT.md"
    json_path = OUTPUT_DIR / "phase5_alignment_data.json"
    
    with open(report_path, "w", encoding="utf-8") as fp:
        fp.write("# BOT-CORPUS Phase 5: Cross-Bot Evidence Asset Alignment Report\n\n")
        fp.write(f"> Generated: {report['metadata']['generated_at']}\n")
        fp.write(f"> Scope: All Bot evidence assets\n\n")
        
        fp.write("## Summary\n\n")
        fp.write(f"| Metric | Value |\n|--------|-------|\n")
        fp.write(f"| Total Evidence Files | {report['summary']['total_evidence']:,} |\n")
        fp.write(f"| Valid | {report['summary']['total_valid']:,} |\n")
        fp.write(f"| Invalid | {report['summary']['total_invalid']:,} |\n")
        fp.write(f"| **Overall Validation Rate** | **{report['summary']['overall_rate']}** |\n\n")
        
        fp.write("## By Bot\n\n")
        fp.write("| Bot | Total | Valid | Invalid | Rate |\n")
        fp.write("|-----|-------|-------|---------|------|\n")
        for bot_name, data in report["bots"].items():
            fp.write(f"| {bot_name} | {data['total']} | {data['valid']} | {data['invalid']} | {data['rate']} |\n")
        
        fp.write("\n## Issue Classification\n\n")
        
        # Aggregate issues
        all_issues = defaultdict(int)
        for bot_name, data in report["bots"].items():
            for issue, count in data.get("issues", {}).items():
                all_issues[issue] += count
        
        p0_issues = [i for i in all_issues if "missing" in i.lower() or "parse" in i.lower()]
        p1_issues = [i for i in all_issues if "pending" in i.lower() or "mismatch" in i.lower()]
        p2_issues = [i for i in all_issues if i not in p0_issues + p1_issues]
        
        fp.write("### P0 (Critical)\n\n")
        for issue in p0_issues:
            fp.write(f"- {issue}: {all_issues[issue]}\n")
        
        fp.write("\n### P1 (Warning)\n\n")
        for issue in p1_issues:
            fp.write(f"- {issue}: {all_issues[issue]}\n")
        
        fp.write("\n### P2 (Info)\n\n")
        for issue in p2_issues:
            fp.write(f"- {issue}: {all_issues[issue]}\n")
        
        fp.write("\n## Recommendations\n\n")
        fp.write("### Immediate (P0)\n")
        fp.write("1. Fix all parse errors in evidence files\n")
        fp.write("2. Add missing required fields\n\n")
        
        fp.write("### Short-term (P1)\n")
        fp.write("1. Complete pending_verification evidence\n")
        fp.write("2. Resolve text mismatches\n\n")
        
        fp.write("### Ongoing (P2)\n")
        fp.write("1. Establish regular evidence validation pipeline\n")
    
    with open(json_path, "w", encoding="utf-8") as fp:
        json.dump(report, fp, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Report saved to: {report_path}")
    print(f"✅ JSON data saved to: {json_path}")
    
    return report

if __name__ == "__main__":
    main()
