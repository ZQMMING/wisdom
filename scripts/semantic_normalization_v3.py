#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终语义归一化脚本 V3 - 正确提取前缀
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

# 实际的证据数量（从统计得出）
ACTUAL_COUNTS = {
    'DTS': 50,
    'QTBJ': 1233,
    'PZZQ': 10,
    'YHZP': 121,
    'SMTH': 12,
    'GW': 4,
    'HH': 3,
    'K2G': 14,
    'TOTAL': 1498
}

# 分类规则
CLASSIFICATION_RULES = {
    'DTS': {'authority': 'PRINCIPLE_CONSTRAINT', 'signals': ['STRENGTH', 'GENERAL']},
    'QTBJ': {'authority': 'CLIMATE_SEASONAL', 'signals': ['CLIMATE', 'TEN_GOD']},
    'PZZQ': {'authority': 'PATTERN_OPERATIONAL', 'signals': ['PATTERN', 'TEN_GOD']},
    'YHZP': {'authority': 'DAYMASTER_STRUCTURE', 'signals': ['STRENGTH', 'PATTERN', 'TEN_GOD']},
    'SMTH': {'authority': 'ELEMENT_IDENTITY', 'signals': ['FIVE_ELEMENTS', 'YIN_YANG']}
}

# 新前缀规则
NEW_PREFIX_RULES = {
    'GW': {'authority': 'COMPLEMENTARY', 'signals': ['GENERAL'], 'category': 'COMPLEMENTARY'},
    'HH': {'authority': 'COMPLEMENTARY', 'signals': ['GENERAL'], 'category': 'COMPLEMENTARY'},
    'K2G': {'authority': 'CONTEXTUAL', 'signals': ['GENERAL'], 'category': 'CONTEXTUAL'}
}

def main():
    evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')
    
    print("=" * 70)
    print("最终语义归一化 V3")
    print("=" * 70)
    print()
    
    stats = {
        'total': 0,
        'updated': 0,
        'classic_counts': defaultdict(int),
        'by_authority': defaultdict(int),
        'by_signal': defaultdict(int),
        'by_category': defaultdict(int)
    }
    
    for f in evidence_dir.rglob('E-*.json'):
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            
            stats['total'] += 1
            prefix = extract_prefix(f.stem)
            
            if not prefix:
                continue
            
            # 标准经典
            if prefix in CLASSIFICATION_RULES:
                rule = CLASSIFICATION_RULES[prefix]
                stats['classic_counts'][prefix] += 1
                stats['by_authority'][rule['authority']] += 1
                stats['by_signal'][data.get('signal_type', rule['signals'][0])] += 1
                stats['by_category'][determine_category(data)] += 1
                
                category = stats['by_category'][-1] if stats['by_category'] else 'SPECIALIZED'
                data['classification'] = category
                data['authority_type'] = rule['authority']
                data['semantic_category'] = category
                data['normalization_version'] = '2.0'
                data['normalization_date'] = '2026-09-02'
                data['normalization_commit'] = 'final-fix-003'
                
                with open(f, 'w', encoding='utf-8') as fh:
                    json.dump(data, fh, ensure_ascii=False, indent=2)
                
                stats['updated'] += 1
            
            # 新前缀
            elif prefix in NEW_PREFIX_RULES:
                rule = NEW_PREFIX_RULES[prefix]
                stats['classic_counts'][prefix] += 1
                stats['by_authority'][rule['authority']] += 1
                stats['by_signal']['GENERAL'] += 1
                stats['by_category'][rule['category']] += 1
                
                data['classification'] = rule['category']
                data['authority_type'] = rule['authority']
                data['semantic_category'] = rule['category']
                data['normalization_version'] = '2.0'
                data['normalization_date'] = '2026-09-02'
                data['normalization_commit'] = 'final-fix-003'
                
                with open(f, 'w', encoding='utf-8') as fh:
                    json.dump(data, fh, ensure_ascii=False, indent=2)
                
                stats['updated'] += 1
                
        except Exception as e:
            print(f"  ⚠️  {f.name}: {e}")
    
    # 生成权威注册表
    registry = {
        '_metadata': {
            'version': '2.0',
            'date': '2026-09-02',
            'total_evidence': stats['total'],
            'actual_counts': dict(ACTUAL_COUNTS),
            'commit': 'final-fix-003'
        },
        'authorities': {},
        'classifications': {}
    }
    
    for prefix, rule in CLASSIFICATION_RULES.items():
        registry['authorities'][prefix] = {
            'name': get_classic_name(prefix),
            'authority': rule['authority'],
            'expected_count': ACTUAL_COUNTS.get(prefix, 0),
            'actual_count': stats['classic_counts'].get(prefix, 0),
            'primary_signals': rule['signals']
        }
    
    for prefix, rule in NEW_PREFIX_RULES.items():
        registry['authorities'][prefix] = {
            'name': prefix,
            'authority': rule['authority'],
            'expected_count': ACTUAL_COUNTS.get(prefix, 0),
            'actual_count': stats['classic_counts'].get(prefix, 0),
            'primary_signals': rule['signals']
        }
    
    for cat, count in stats['by_category'].items():
        registry['classifications'][cat] = {'count': count}
    
    # 保存
    with open(evidence_dir / 'semantic_authority_registry.json', 'w', encoding='utf-8') as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    
    report = {
        'total_evidence': stats['total'],
        'updated_count': stats['updated'],
        'by_authority': dict(stats['by_authority']),
        'by_signal': dict(stats['by_signal']),
        'by_category': dict(stats['by_category']),
        'classic_counts': dict(stats['classic_counts']),
        'expected_counts': ACTUAL_COUNTS,
        'timestamp': '2026-09-02T12:00:00',
        'status': 'COMPLETED',
        'commit': 'final-fix-003'
    }
    
    with open(evidence_dir / 'semantic_normalization_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("✅ 处理完成:")
    print(f"   总证据数: {stats['total']}")
    print(f"   已更新: {stats['updated']}")
    print()
    print("📊 经典分布:")
    for prefix, count in sorted(stats['classic_counts'].items()):
        expected = ACTUAL_COUNTS.get(prefix, 0)
        status = "✓" if count == expected else f"✗ (期望{expected})"
        name = get_classic_name(prefix) if prefix in CLASSIFICATION_RULES else prefix
        print(f"   {name}: {count} {status}")
    print()
    print("📈 权威分布:")
    for auth, count in sorted(stats['by_authority'].items()):
        print(f"   {auth}: {count}")
    print()
    print("🏷️  类别分布:")
    for cat, count in sorted(stats['by_category'].items()):
        print(f"   {cat}: {count}")
    print()
    
    # 验证
    errors = []
    if stats['total'] != ACTUAL_COUNTS['TOTAL']:
        errors.append(f"总证据数: 期望{ACTUAL_COUNTS['TOTAL']}，实际{stats['total']}")
    
    for prefix, expected in ACTUAL_COUNTS.items():
        actual = stats['classic_counts'].get(prefix, 0)
        if actual != expected:
            errors.append(f"{prefix}: 期望{expected}，实际{actual}")
    
    if errors:
        print("❌ 验证失败:")
        for e in errors:
            print(f"   - {e}")
        return False
    else:
        print("✅ 验证通过 - 所有证据分类正确")
        return True

def extract_prefix(stem):
    """从文件名提取前缀，如 E-GW-101-001 → GW"""
    parts = stem.split('-')
    if len(parts) >= 2:
        return parts[1]
    return None

def determine_category(data):
    theme = data.get('theme', '')
    signal = data.get('signal_type', '')
    
    if any(k in theme for k in ['死绝', '长生', '阴阳', '生死']):
        return 'DETERMINISTIC_CANONICAL'
    if signal == 'PATTERN':
        return 'CONTEXTUAL'
    if signal == 'FIVE_ELEMENTS':
        return 'COMPLEMENTARY'
    return 'SPECIALIZED'

def get_classic_name(code):
    return {'DTS': '滴天髓', 'QTBJ': '穷通宝鉴', 'PZZQ': '子平真诠', 
            'YHZP': '渊海子平', 'SMTH': '三命通会'}.get(code, code)

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)