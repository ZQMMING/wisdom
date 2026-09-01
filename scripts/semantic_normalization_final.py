#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终语义归一化脚本 - 处理所有证据包括新前缀
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
    'SMTH': 12,  # SAN 8 + SMTH 4
    'OTHER': 72,  # GW, HH, K2G等新前缀
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

PREFIX_MAPPING = {'SAN': 'SMTH', 'ZIPI': 'PZZQ'}

# 新前缀的默认分类
NEW_PREFIX_RULES = {
    'GW': {'authority': 'COMPLEMENTARY', 'signals': ['GENERAL']},
    'HH': {'authority': 'COMPLEMENTARY', 'signals': ['GENERAL']},
    'K2G': {'authority': 'CONTEXTUAL', 'signals': ['GENERAL']}
}

def main():
    evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')
    
    print("=" * 70)
    print("最终语义归一化 - 完整版本")
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
            classic = classify_evidence(f)
            
            if classic and classic in CLASSIFICATION_RULES:
                rule = CLASSIFICATION_RULES[classic]
                stats['classic_counts'][classic] += 1
                stats['by_authority'][rule['authority']] += 1
                stats['by_signal'][data.get('signal_type', rule['signals'][0])] += 1
                stats['by_category'][determine_category(data)] += 1
                
                data['classification'] = get_category_from_stats(stats['by_category'])
                data['authority_type'] = rule['authority']
                data['semantic_category'] = data['classification']
                data['normalization_version'] = '2.0'
                data['normalization_date'] = '2026-09-02'
                data['normalization_commit'] = 'final-fix-002'
                
                with open(f, 'w', encoding='utf-8') as fh:
                    json.dump(data, fh, ensure_ascii=False, indent=2)
                
                stats['updated'] += 1
                
            elif classic and classic in NEW_PREFIX_RULES:
                # 处理新前缀
                rule = NEW_PREFIX_RULES[classic]
                stats['classic_counts'][classic] += 1
                stats['by_authority'][rule['authority']] += 1
                stats['by_signal']['GENERAL'] += 1
                stats['by_category']['COMPLEMENTARY'] += 1
                
                data['classification'] = 'COMPLEMENTARY'
                data['authority_type'] = rule['authority']
                data['semantic_category'] = 'COMPLEMENTARY'
                data['normalization_version'] = '2.0'
                data['normalization_date'] = '2026-09-02'
                data['normalization_commit'] = 'final-fix-002'
                
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
            'commit': 'final-fix-002'
        },
        'authorities': {},
        'classifications': {}
    }
    
    for classic, rule in CLASSIFICATION_RULES.items():
        registry['authorities'][classic] = {
            'name': get_classic_name(classic),
            'authority': rule['authority'],
            'expected_count': ACTUAL_COUNTS.get(classic, 0),
            'actual_count': stats['classic_counts'].get(classic, 0),
            'primary_signals': rule['signals']
        }
    
    for classic, rule in NEW_PREFIX_RULES.items():
        registry['authorities'][classic] = {
            'name': f'{classic} (新前缀)',
            'authority': rule['authority'],
            'expected_count': ACTUAL_COUNTS.get('OTHER', 0),
            'actual_count': stats['classic_counts'].get(classic, 0),
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
        'commit': 'final-fix-002'
    }
    
    with open(evidence_dir / 'semantic_normalization_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("✅ 处理完成:")
    print(f"   总证据数: {stats['total']}")
    print(f"   已更新: {stats['updated']}")
    print()
    print("📊 经典分布:")
    for classic, count in sorted(stats['classic_counts'].items()):
        expected = ACTUAL_COUNTS.get(classic, 0)
        status = "✓" if count == expected else f"✗ (期望{expected})"
        print(f"   {get_classic_name(classic) if classic in CLASSIFICATION_RULES else classic}: {count} {status}")
    print()
    print("📈 权威分布:")
    for auth, count in sorted(stats['by_authority'].items()):
        print(f"   {auth}: {count}")
    print()
    print("🏷️  类别分布:")
    for cat, count in sorted(stats['by_category'].items(), key=lambda x: str(x[0])):
        print(f"   {cat}: {count}")
    print()
    
    # 验证
    errors = []
    if stats['total'] != ACTUAL_COUNTS['TOTAL']:
        errors.append(f"总证据数: 期望{ACTUAL_COUNTS['TOTAL']}，实际{stats['total']}")
    
    for classic, expected in ACTUAL_COUNTS.items():
        if classic == 'TOTAL':
            continue
        actual = stats['classic_counts'].get(classic, 0)
        if actual != expected:
            errors.append(f"{classic}: 期望{expected}，实际{actual}")
    
    if errors:
        print("❌ 验证失败:")
        for e in errors:
            print(f"   - {e}")
        return False
    else:
        print("✅ 验证通过 - 所有证据分类正确")
        return True

def classify_evidence(f):
    stem = f.stem
    
    # 先检查标准前缀
    for c in ['DTS', 'QTBJ', 'PZZQ', 'YHZP', 'SMTH']:
        if stem.startswith(f'E-{c}-') or stem.startswith(f'E-{c}_'):
            return c
    
    # 再检查映射前缀
    for prefix, mapped in PREFIX_MAPPING.items():
        if stem.startswith(f'E-{prefix}-') or stem.startswith(f'E-{prefix}_'):
            return mapped
    
    # 检查新前缀
    for prefix in NEW_PREFIX_RULES.keys():
        if stem.startswith(f'E-{prefix}-') or stem.startswith(f'E-{prefix}_'):
            return prefix
    
    # 最后检查目录名
    parts = f.parts
    for part in reversed(parts):
        part_lower = part.lower()
        if 'di_tian_sui' in part_lower or 'DTS' in part:
            return 'DTS'
        elif 'qiong_tong' in part_lower or 'QTBJ' in part:
            return 'QTBJ'
        elif 'zi_ping' in part_lower or 'PZZQ' in part:
            return 'PZZQ'
        elif 'yuan_hai' in part_lower or 'YHZP' in part:
            return 'YHZP'
        elif 'san_ming' in part_lower or 'SMTH' in part:
            return 'SMTH'
    
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

def get_category_from_stats(categories):
    if not categories:
        return 'SPECIALIZED'
    # 返回最后一个非None的类别
    for cat in reversed(categories):
        if cat:
            return cat
    return 'SPECIALIZED'

def get_classic_name(code):
    return {'DTS': '滴天髓', 'QTBJ': '穷通宝鉴', 'PZZQ': '子平真诠', 
            'YHZP': '渊海子平', 'SMTH': '三命通会'}.get(code, code)

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)