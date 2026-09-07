#!/usr/bin/env python3
"""Provenance Monotonicity Validator - 强制执行 PM 规则"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class ProvenanceValidator:
    """Provenance Monotonicity 验证器"""
    
    LAYER_MAPPING = {
        'A': 'PRIMARY_TRADITION',
        'B': 'SYSTEMATIZED',
        'C': 'CASE_EVIDENCE',
        'D': 'DERIVED'
    }
    
    def __init__(self, evidence_dir: Path):
        self.evidence_dir = evidence_dir
        self.errors: List[Dict] = []
        self.warnings: List[Dict] = []
    
    def validate_all(self) -> Tuple[List[Dict], List[Dict]]:
        """验证所有 evidence 文件"""
        files = list(self.evidence_dir.glob('E-BLIND-*.json'))
        
        for f in files:
            self.validate_single(f)
        
        return self.errors, self.warnings
    
    def validate_single(self, filepath: Path):
        """验证单个 evidence 文件"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        evidence_id = data.get('evidence_id', filepath.name)
        
        # PM-002: Authority Consistency
        self._check_authority_consistency(evidence_id, data)
        
        # PM-003: Source Traceability (分层要求)
        self._check_source_traceability(evidence_id, data)
        
        # PM-005: Original Text Integrity
        self._check_original_text(evidence_id, data)
    
    def _check_authority_consistency(self, evidence_id: str, data: Dict):
        """PM-002: 检查 authority_status 与 layer 匹配"""
        layer = data.get('provenance_layer')
        authority = data.get('authority_status')
        
        expected = self.LAYER_MAPPING.get(layer)
        if expected and authority != expected:
            self.errors.append({
                'rule': 'PM-002',
                'evidence_id': evidence_id,
                'issue': f'authority_status mismatch: layer={layer}, authority={authority}, expected={expected}'
            })
    
    def _check_source_traceability(self, evidence_id: str, data: Dict):
        """PM-003: 检查 source 可追溯性（分层要求）"""
        layer = data.get('provenance_layer')
        source = data.get('source', {})
        fidelity = data.get('source_fidelity', '')
        
        if fidelity != 'DIRECT':
            return  # 非 DIRECT fidelity 不检查此规则
        
        requirements = {
            'A': {'required': ['locator', 'edition', 'author', 'chapter'], 'edition': 'REQUIRED'},
            'B': {'required': ['locator', 'author', 'chapter'], 'edition': 'RECOMMENDED'},
            'C': {'required': ['locator'], 'edition': 'OPTIONAL'},
            'D': {'required': ['locator'], 'edition': 'NOT_APPLICABLE'}
        }
        
        reqs = requirements.get(layer)
        if not reqs:
            return
        
        # 检查必填字段
        for field in reqs['required']:
            if not source.get(field):
                self.errors.append({
                    'rule': 'PM-003',
                    'evidence_id': evidence_id,
                    'issue': f'Missing required field: {field}'
                })
        
        # A层必须有 edition
        if layer == 'A' and reqs['edition'] == 'REQUIRED':
            if not source.get('edition'):
                self.errors.append({
                    'rule': 'PM-003',
                    'evidence_id': evidence_id,
                    'issue': 'A-layer evidence must have edition field'
                })
        
        # C层 edition 可选，但如果有应记录
        if layer == 'C' and source.get('edition'):
            self.warnings.append({
                'rule': 'PM-003',
                'evidence_id': evidence_id,
                'issue': 'C-layer has edition field (optional), consider adding source_verification_status'
            })
    
    def _check_original_text(self, evidence_id: str, data: Dict):
        """PM-005: 检查 original_text 完整性"""
        original_text = data.get('original_text', '')
        
        # 检查是否过短（可能是人工截断）
        if len(original_text) < 10:
            self.warnings.append({
                'rule': 'PM-005',
                'evidence_id': evidence_id,
                'issue': f'original_text very short ({len(original_text)} chars), verify authenticity'
            })
        
        # 检查是否异常长（可能是人工扩写）
        if len(original_text) > 500:
            self.warnings.append({
                'rule': 'PM-005',
                'evidence_id': evidence_id,
                'issue': f'original_text unusually long ({len(original_text)} chars), verify it is source text'
            })
    
    def generate_report(self) -> Dict:
        """生成验证报告"""
        errors, warnings = self.validate_all()
        
        return {
            'validator_version': '1.0',
            'generated_at': datetime.now().isoformat(),
            'total_errors': len(errors),
            'total_warnings': len(warnings),
            'errors': errors,
            'warnings': warnings,
            'status': 'PASS' if not errors else 'FAIL'
        }


def main():
    """主验证函数"""
    evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence/blind_seg')
    
    validator = ProvenanceValidator(evidence_dir)
    report = validator.generate_report()
    
    print("=" * 70)
    print("Provenance Monotonicity Validation Report")
    print("=" * 70)
    print(f"\nGenerated: {report['generated_at']}")
    print(f"Status: {report['status']}")
    print(f"Errors: {report['total_errors']}")
    print(f"Warnings: {report['total_warnings']}")
    
    if report['errors']:
        print("\n❌ Errors:")
        for err in report['errors']:
            print(f"  [{err['rule']}] {err['evidence_id']}: {err['issue']}")
    
    if report['warnings']:
        print("\n⚠️ Warnings:")
        for warn in report['warnings']:
            print(f"  [{warn['rule']}] {warn['evidence_id']}: {warn['issue']}")
    
    # 保存报告
    report_path = evidence_dir / 'provenance_validation_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\nReport saved: {report_path}")
    
    return report['status'] == 'PASS'


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
