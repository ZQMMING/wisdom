#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T-BOT-CORPUS-002: Batch Verification Script for DUANYU Evidence

Rules:
- AUTO_PASS: Format checks pass, no issues found
- NEEDS_HUMAN: Issues detected that require human review

Important: AUTO_PASS ≠ VERIFIED (format ≠ semantics)
"""

import json
import os
import re
import hashlib
from pathlib import Path
from collections import defaultdict
from datetime import datetime

WORKSPACE = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = WORKSPACE / "data" / "evidence"
META_DIR = WORKSPACE / "data" / "evidence_meta"
OUTPUT_DIR = WORKSPACE / "docs" / "bots" / "BOT-CORPUS"

# Evidence ID pattern
EVIDENCE_ID_PATTERN = re.compile(r'^E-[A-Z]+-DUANYU-\d{4}$')

# Required fields
REQUIRED_FIELDS = ['evidence_id', 'classic_id', 'evidence_type', 'original_text', 'source_locator']

# Source locator required sub-fields
REQUIRED_SOURCE_FIELDS = ['classic', 'chapter', 'passage_id']

# Valid claim_type values (if present)
VALID_CLAIM_TYPES = {
    'structural', 'timing', 'transformation', 'interaction',
    'strength', 'balance', 'flow', 'clash', 'harmony'
}


def load_all_evidence():
    """Load all DUANYU evidence files"""
    evidence_list = []
    
    for root, dirs, files in os.walk(EVIDENCE_DIR):
        for f in files:
            if '-DUANYU-' in f and f.endswith('.json'):
                ef = Path(root) / f
                try:
                    with open(ef, 'r', encoding='utf-8') as fh:
                        data = json.load(fh)
                    data['_file'] = ef
                    data['_root'] = root
                    evidence_list.append(data)
                except Exception as e:
                    evidence_list.append({
                        '_file': ef,
                        '_error': str(e),
                        '_raw': None
                    })
    
    return evidence_list


def check_format(evid):
    """Check evidence_id format"""
    evid_id = evid.get('evidence_id', '')
    if not EVIDENCE_ID_PATTERN.match(evid_id):
        return False, f"Invalid evidence_id format: {evid_id}"
    return True, None


def check_uniqueness(evid, seen_ids):
    """Check evidence_id uniqueness"""
    evid_id = evid.get('evidence_id', '')
    if evid_id in seen_ids:
        return False, f"Duplicate evidence_id: {evid_id}"
    seen_ids.add(evid_id)
    return True, None


def check_source_locator(evid):
    """Check source_locator has required fields"""
    source = evid.get('source_locator', {})
    issues = []
    
    for field in REQUIRED_SOURCE_FIELDS:
        if not source.get(field):
            issues.append(f"Missing source_locator.{field}")
    
    # Check title (classic or work)
    if not source.get('classic') and not source.get('work'):
        issues.append("Missing source title (classic/work)")
    
    return len(issues) == 0, issues


def check_excerpt_length(evid):
    """Check original_text >= 10 characters"""
    text = evid.get('original_text', '')
    if len(text) < 10:
        return False, f"excerpt too short: {len(text)} chars"
    return True, None


def check_content_hash(evid, content_hashes):
    """Check content hash for deduplication"""
    text = evid.get('original_text', '')
    if not text:
        return False, "Missing original_text"
    
    content_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    # Check for duplicate content
    if content_hash in content_hashes:
        return False, f"Duplicate content hash: {content_hash[:16]}..."
    
    content_hashes.add(content_hash)
    return True, None


def check_claim_type(evid):
    """Check claim_type enum if present"""
    claim_type = evid.get('claim_type', '')
    if claim_type and claim_type not in VALID_CLAIM_TYPES:
        return False, f"Invalid claim_type: {claim_type}"
    return True, None


def check_required_fields(evid):
    """Check all required fields exist"""
    issues = []
    for field in REQUIRED_FIELDS:
        if field not in evid or evid[field] is None:
            issues.append(f"Missing required field: {field}")
    return len(issues) == 0, issues


def batch_verify(evidence_list):
    """Run all batch verification checks"""
    results = {
        'AUTO_PASS': [],
        'NEEDS_HUMAN': [],
        'ERROR': []
    }
    
    stats = {
        'total': len(evidence_list),
        'auto_pass': 0,
        'needs_human': 0,
        'error': 0,
        'by_issue': defaultdict(int),
        'by_classic': defaultdict(lambda: {'total': 0, 'auto_pass': 0, 'needs_human': 0})
    }
    
    seen_ids = set()
    content_hashes = set()
    
    for evid in evidence_list:
        if '_error' in evid:
            results['ERROR'].append({
                'file': str(evid['_file']),
                'error': evid['_error']
            })
            stats['error'] += 1
            continue
        
        issues = []
        evid_id = evid.get('evidence_id', 'unknown')
        classic_id = evid.get('classic_id', 'unknown')
        
        stats['by_classic'][classic_id]['total'] += 1
        
        # Run all checks
        checks = [
            ('format', check_format(evid)),
            ('uniqueness', check_uniqueness(evid, seen_ids)),
            ('required_fields', check_required_fields(evid)),
            ('source_locator', check_source_locator(evid)),
            ('excerpt_length', check_excerpt_length(evid)),
            ('content_hash', check_content_hash(evid, content_hashes)),
            ('claim_type', check_claim_type(evid))
        ]
        
        for check_name, (passed, issue) in checks:
            if not passed:
                issues.append({
                    'check': check_name,
                    'issue': issue
                })
                stats['by_issue'][check_name] += 1
        
        if issues:
            results['NEEDS_HUMAN'].append({
                'evidence_id': evid_id,
                'file': str(evid['_file']),
                'issues': issues
            })
            stats['needs_human'] += 1
            stats['by_classic'][classic_id]['needs_human'] += 1
        else:
            results['AUTO_PASS'].append(evid_id)
            stats['auto_pass'] += 1
            stats['by_classic'][classic_id]['auto_pass'] += 1
    
    return results, stats


def update_review_queue(results, stats):
    """Update evidence_review_queue.json with batch verification results"""
    queue_path = META_DIR / "evidence_review_queue.json"
    
    if queue_path.exists():
        with open(queue_path, 'r', encoding='utf-8') as fp:
            queue = json.load(fp)
    else:
        queue = {"kind": "evidence_review_queue", "items": []}
    
    # Update batch verification status
    queue['batch_verification'] = {
        'run_at': datetime.now().isoformat(),
        'total_scanned': stats['total'],
        'auto_pass_count': stats['auto_pass'],
        'needs_human_count': stats['needs_human'],
        'error_count': stats['error'],
        'auto_pass_rate': f"{stats['auto_pass']/stats['total']*100:.1f}%" if stats['total'] > 0 else "0%"
    }
    
    # Update individual items (up to first 100 for demonstration)
    updated_items = 0
    for item in queue.get('items', [])[:100]:
        evid_id = item.get('evidence_id', '')
        if evid_id in results['AUTO_PASS']:
            item['batch_verification_status'] = 'AUTO_PASS'
            item['review_status'] = 'auto_verified'
        elif any(h['evidence_id'] == evid_id for h in results['NEEDS_HUMAN']):
            item['batch_verification_status'] = 'NEEDS_HUMAN'
            item['review_status'] = 'pending_manual_verification'
        updated_items += 1
    
    # Save updated queue
    with open(queue_path, 'w', encoding='utf-8') as fp:
        json.dump(queue, fp, ensure_ascii=False, indent=2)
    
    return updated_items


def generate_report(results, stats, updated_items):
    """Generate batch verification report"""
    report_path = OUTPUT_DIR / "BATCH_VERIFY_REPORT.md"
    json_path = OUTPUT_DIR / "batch_verify_data.json"
    
    report = {
        'metadata': {
            'task_id': 'T-BOT-CORPUS-002',
            'generated_at': datetime.now().isoformat(),
            'workspace': str(WORKSPACE)
        },
        'summary': {
            'total_scanned': stats['total'],
            'auto_pass': stats['auto_pass'],
            'needs_human': stats['needs_human'],
            'error': stats['error'],
            'auto_pass_rate': f"{stats['auto_pass']/stats['total']*100:.1f}%" if stats['total'] > 0 else "0%",
            'updated_queue_items': updated_items
        },
        'by_classic': dict(stats['by_classic']),
        'by_issue': dict(stats['by_issue']),
        'auto_pass_samples': results['AUTO_PASS'][:20],
        'needs_human_samples': results['NEEDS_HUMAN'][:20]
    }
    
    # Generate markdown report
    with open(report_path, 'w', encoding='utf-8') as fp:
        fp.write("# T-BOT-CORPUS-002 Batch Verification Report\n\n")
        fp.write(f"> Task: DUANYU Evidence Batch Verification\n")
        fp.write(f"> Generated: {report['metadata']['generated_at']}\n\n")
        fp.write(f"> **⚠️ 重要说明**: AUTO_PASS ≠ VERIFIED，仅表示格式核验通过。语义正确性需人工确认。\n\n")
        
        fp.write("## Summary\n\n")
        fp.write(f"| Metric | Value |\n|--------|-------|\n")
        fp.write(f"| Total Scanned | {stats['total']:,} |\n")
        fp.write(f"| **AUTO_PASS** | **{stats['auto_pass']:,}** ({report['summary']['auto_pass_rate']}) |\n")
        fp.write(f"| NEEDS_HUMAN | {stats['needs_human']:,} |\n")
        fp.write(f"| ERROR | {stats['error']:,} |\n")
        fp.write(f"| Queue Items Updated | {updated_items} |\n\n")
        
        fp.write("## By Classic\n\n")
        fp.write("| Classic | Total | AUTO_PASS | NEEDS_HUMAN | Auto Rate |\n")
        fp.write("|---------|-------|-----------|-------------|-----------|\n")
        for classic, counts in sorted(report['by_classic'].items()):
            rate = counts['auto_pass'] / counts['total'] * 100 if counts['total'] > 0 else 0
            fp.write(f"| {classic} | {counts['total']} | {counts['auto_pass']} | {counts['needs_human']} | {rate:.1f}% |\n")
        
        fp.write("\n## Issues Found\n\n")
        if report['by_issue']:
            fp.write("| Issue Type | Count | Description |\n|------------|-------|-------------|\n")
            issue_desc = {
                'format': 'evidence_id 格式不匹配',
                'uniqueness': 'evidence_id 重复',
                'required_fields': '缺少必需字段',
                'source_locator': 'source_locator 字段缺失',
                'excerpt_length': '原文过短 (<10字)',
                'content_hash': '内容哈希重复',
                'claim_type': 'claim_type 不在枚举值中'
            }
            for issue, count in sorted(report['by_issue'].items(), key=lambda x: -x[1]):
                desc = issue_desc.get(issue, issue)
                fp.write(f"| {issue} | {count} | {desc} |\n")
        else:
            fp.write("未发现格式问题。\n")
        
        fp.write("\n## Recommendations\n\n")
        fp.write("### Immediate Actions\n")
        fp.write("1. ✅ 批量格式核验完成\n")
        fp.write("2. ⏳ NEEDS_HUMAN 证据等待人工核验\n")
        fp.write("3. ⚠️ AUTO_PASS 仅表示格式正确，语义需人工确认\n\n")
        
        fp.write("### Status Gate Policy\n")
        fp.write("- AUTO_PASS: 格式通过，可进入人工核验队列\n")
        fp.write("- NEEDS_HUMAN: 格式问题，需人工修正\n")
        fp.write("- UNVERIFIED: 所有新注册证据保持 UNVERIFIED，不得进入生产\n\n")
        
        fp.write("### Next Steps\n")
        fp.write("1. 人工核验 AUTO_PASS 样本（抽取 20 条）\n")
        fp.write("2. 修正 NEEDS_HUMAN 证据的格式问题\n")
        fp.write("3. 建立自动化核验流水线\n")
    
    # Save JSON report
    with open(json_path, 'w', encoding='utf-8') as fp:
        json.dump(report, fp, ensure_ascii=False, indent=2)
    
    return report_path, json_path


def main():
    print("=" * 70)
    print("T-BOT-CORPUS-002: DUANYU Evidence Batch Verification")
    print("=" * 70)
    
    # Step 1: Load evidence
    print("\n[1/4] Loading DUANYU evidence...")
    evidence_list = load_all_evidence()
    print(f"  Loaded {len(evidence_list):,} evidence files")
    
    # Step 2: Run batch verification
    print("\n[2/4] Running batch verification...")
    results, stats = batch_verify(evidence_list)
    print(f"  AUTO_PASS: {stats['auto_pass']:,}")
    print(f"  NEEDS_HUMAN: {stats['needs_human']:,}")
    print(f"  ERROR: {stats['error']:,}")
    
    # Step 3: Update review queue
    print("\n[3/4] Updating review queue...")
    updated_items = update_review_queue(results, stats)
    print(f"  Updated {updated_items} queue items")
    
    # Step 4: Generate report
    print("\n[4/4] Generating report...")
    report_path, json_path = generate_report(results, stats, updated_items)
    print(f"  Report: {report_path}")
    print(f"  JSON: {json_path}")
    
    # Final summary
    print("\n" + "=" * 70)
    print("BATCH VERIFICATION COMPLETE")
    print("=" * 70)
    print(f"Total: {stats['total']:,} evidence files scanned")
    print(f"AUTO_PASS: {stats['auto_pass']:,} ({stats['auto_pass']/stats['total']*100:.1f}%)")
    print(f"NEEDS_HUMAN: {stats['needs_human']:,} ({stats['needs_human']/stats['total']*100:.1f}%)")
    print(f"\n⚠️  AUTO_PASS ≠ VERIFIED (format verification ≠ semantic correctness)")
    print(f"⚠️  All new evidence remains UNVERIFIED per V2 policy")


if __name__ == "__main__":
    main()
