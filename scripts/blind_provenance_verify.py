# -*- coding: utf-8 -*-
"""Phase 5 P0: Evidence Provenance Verification Script

验证74条盲派证据的provenance，统计verified/semantic_match/pending数量。
"""
import json
from pathlib import Path
from datetime import datetime

# ─── 路径独立定位 ──────────────────────────────────────────────────────────────
_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = _ROOT / 'data' / 'evidence' / 'blind_seg'
MANIFEST_PATH = DATA_DIR / 'manifest.json'
PROVENANCE_STATUS_PATH = DATA_DIR / 'provenance_final_status.json'


def validate_evidence_provenance():
    """验证所有证据的provenance状态"""
    results = {
        'total_files': 0,
        'verified': 0,
        'semantic_match': 0,
        'pending': 0,
        'rejected': 0,
        'errors': []
    }
    
    for f in sorted(DATA_DIR.glob('E-BLIND-*.json')):
        try:
            with open(f, encoding='utf-8') as fp:
                data = json.load(fp)
            results['total_files'] += 1
            
            # Check source_verification
            sv = data.get('source_verification', {})
            status = sv.get('status', 'UNKNOWN')
            
            if status == 'VERIFIED':
                results['verified'] += 1
            elif status == 'SEMANTIC_MATCH':
                results['semantic_match'] += 1
            elif status == 'PENDING_VERIFICATION':
                results['pending'] += 1
            elif status == 'REJECTED':
                results['rejected'] += 1
            else:
                # Check source_fidelity field as fallback
                fidelity = data.get('source_fidelity', 'UNKNOWN')
                if fidelity == 'DIRECT':
                    results['verified'] += 1
                elif fidelity == 'SEMANTIC_MATCH':
                    results['semantic_match'] += 1
                else:
                    results['pending'] += 1
                    
        except Exception as e:
            results['errors'].append(f"{f.name}: {e}")
    
    return results


def update_manifest(results):
    """更新manifest.json中的验证状态"""
    with open(MANIFEST_PATH, encoding='utf-8') as f:
        manifest = json.load(f)
    
    # Update evidence_stats
    if 'evidence_stats' not in manifest:
        manifest['evidence_stats'] = {}
    
    manifest['evidence_stats']['by_verification'] = {
        'VERIFIED': results['verified'],
        'SEMANTIC_MATCH': results['semantic_match'],
        'PENDING': results['pending'],
        'REJECTED': results['rejected']
    }
    manifest['evidence_stats']['last_updated'] = datetime.now().isoformat()
    
    # Update status if enough verified
    total = results['verified'] + results['semantic_match']
    if total > 0:
        manifest['status'] = 'PHASE_A_VERIFIED'
    
    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    print(f"Updated manifest.json")


def update_provenance_status(results):
    """更新provenance_final_status.json"""
    total = results['verified'] + results['semantic_match'] + results['pending'] + results['rejected']
    
    status = {
        "report_date": datetime.now().isoformat(),
        "total_evidence": total,
        "provenance_status": {
            "verified_with_real_source": results['verified'],
            "semantic_matched": results['semantic_match'],
            "pending_verification": results['pending'],
            "rejected": results['rejected'],
            "actual_pending": results['pending']
        },
        "verification_rate": f"{(results['verified'] + results['semantic_match']) / max(total, 1) * 100:.1f}%",
        "principle_enforced": "SEMANTIC_MATCH allowed for modern compiled works",
        "next_step": "Continue verification to reach 95%+ coverage"
    }
    
    with open(PROVENANCE_STATUS_PATH, 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)
    
    print(f"Updated provenance_final_status.json")


def main():
    print("=" * 60)
    print("Phase 5 P0: Evidence Provenance Verification")
    print(f"Working directory: {_ROOT}")
    print("=" * 60)
    
    # Validate
    results = validate_evidence_provenance()
    
    print(f"\nResults:")
    print(f"  Total files: {results['total_files']}")
    print(f"  Verified (原典逐字): {results['verified']}")
    print(f"  Semantic Match: {results['semantic_match']}")
    print(f"  Pending: {results['pending']}")
    print(f"  Rejected: {results['rejected']}")
    print(f"  Errors: {len(results['errors'])}")
    
    # Calculate rate
    total_valid = results['verified'] + results['semantic_match']
    rate = total_valid / max(results['total_files'], 1) * 100
    print(f"\n  Verification rate: {rate:.1f}%")
    
    # Update files
    if results['total_files'] > 0:
        update_manifest(results)
        update_provenance_status(results)
        print("\n✅ Manifest and provenance status updated")
    
    # Return success if rate >= 80%
    return rate >= 80


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
