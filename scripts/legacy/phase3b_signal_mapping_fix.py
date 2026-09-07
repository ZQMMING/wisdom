#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3B: Evidence → Feature/Signal 实际映射修复
修复三个核心问题：
1. 将1484条GENERAL证据映射到具体Signal
2. TEN_GOD降级为Canonical State/Derived Signal
3. STRENGTH从Classic直接计算改为Canonical + Semantic Authority
"""

import json
from pathlib import Path
from collections import defaultdict
import re

# Canonical Rules Reference（已从primitive_registry验证）
CANONICAL_RULES = {
    'TEN_GOD': 'data/semantic_atoms/ten_gods.json + data/rules/ZPZ-*.json',
    'STRENGTH': 'Canonical Chart State + Month Command + Root Analysis',
    'CLIMATE': 'Seasonal Temperature + Dry/Wet Balance',
    'PATTERN': 'Month Command Structure + Success/Failure Conditions',
    'FIVE_ELEMENTS': 'Element Generation/Restriction Cycles',
    'YIN_YANG': 'DTS-PRIM-004, DTS-PRIM-007, DTS-PRIM-014-018'
}

# Signal提取规则（基于observation_dimension和relation_semantics）
SIGNAL_EXTRACTION_RULES = {
    'CLIMATE': {
        'patterns': ['寒暖', '燥湿', '调候', '季节', '月令', '气候', '温度'],
        'keywords': ['冬', '夏', '春', '秋', '寒', '暖', '燥', '湿', '冷', '热']
    },
    'PATTERN': {
        'patterns': ['格局', '用神', '相神', '成败', '救应', '顺逆'],
        'keywords': ['格', '局', '成', '败', '贵', '富', '清', '浊']
    },
    'STRENGTH': {
        'patterns': ['旺衰', '强弱', '得令', '失令', '根气'],
        'keywords': ['旺', '强', '弱', '衰', '得', '失', '根', '支持']
    },
    'FIVE_ELEMENTS': {
        'patterns': ['五行', '流通', '生克', '通关', '制化'],
        'keywords': ['木', '火', '土', '金', '水', '生', '克', '泄', '耗']
    },
    'TEN_GOD': {
        'patterns': ['十神', '官杀', '印绶', '食伤', '财星'],
        'keywords': ['正官', '七杀', '正印', '偏印', '食神', '伤官', '偏财', '正财', '比肩', '劫财']
    }
}

def extract_signal_from_evidence(data):
    """从证据内容提取信号类型"""
    text = ' '.join([
        str(data.get('observation_dimension', '')),
        str(data.get('relation_semantics', '')),
        str(data.get('canonical_state', '')),
        str(data.get('original_text', '')),
        str(data.get('evidence_text', ''))
    ])
    
    # 检查每个信号模式
    for signal, rules in SIGNAL_EXTRACTION_RULES.items():
        # 检查patterns匹配
        for pattern in rules['patterns']:
            if pattern in text:
                return signal
        # 检查keywords匹配
        for keyword in rules['keywords'][:3]:  # 只检查前3个关键词避免误判
            if keyword in text:
                return signal
    
    return 'GENERAL'

def fix_evidence_signal_mapping():
    evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')
    
    print("=" * 70)
    print("Phase 3B: Evidence → Feature/Signal 实际映射修复")
    print("=" * 70)
    print()
    
    stats = {
        'total': 0,
        'updated': 0,
        'by_signal': defaultdict(int),
        'by_classic_signal': defaultdict(lambda: defaultdict(int))
    }
    
    for f in evidence_dir.rglob('E-*.json'):
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            
            stats['total'] += 1
            classic = data.get('authority_type', 'UNKNOWN')
            
            # 提取信号类型
            current_signal = data.get('signal_type', 'GENERAL')
            new_signal = extract_signal_from_evidence(data)
            
            # 更新证据（如果信号不同或为空）
            if new_signal != 'GENERAL' and (current_signal == 'GENERAL' or not current_signal):
                data['signal_type'] = new_signal
                data['feature_mapped'] = True
                data['feature_map_version'] = '3.0'
                data['feature_map_date'] = '2026-09-02'
                data['feature_map_commit'] = 'phase3b-fix-001'
                
                # 添加语义特征信息
                data['semantic_features'] = {
                    'signal': new_signal,
                    'extraction_method': 'pattern_matching',
                    'confidence': 'high' if new_signal != 'GENERAL' else 'low'
                }
                
                with open(f, 'w', encoding='utf-8') as fh:
                    json.dump(data, fh, ensure_ascii=False, indent=2)
                
                stats['updated'] += 1
                stats['by_signal'][new_signal] += 1
                stats['by_classic_signal'][classic][new_signal] += 1
            
        except Exception as e:
            print(f"  ⚠️  {f.name}: {e}")
    
    # 打印结果
    print("✅ 处理完成:")
    print(f"   总证据数: {stats['total']}")
    print(f"   已更新: {stats['updated']}")
    print()
    print("📊 信号分布:")
    for sig, count in sorted(stats['by_signal'].items(), key=lambda x: -x[1]):
        print(f"   {sig}: {count}")
    print()
    print("📈 经典×信号矩阵:")
    for classic in sorted(stats['by_classic_signal'].keys()):
        signals = stats['by_classic_signal'][classic]
        total = sum(signals.values())
        signal_str = ", ".join([f"{s}:{c}" for s, c in sorted(signals.items(), key=lambda x: -x[1])])
        print(f"   {classic}: {total} ({signal_str})")
    print()
    
    return stats

def update_feature_mapping(stats):
    """更新Feature/Signal Mapping文件"""
    mapping_path = Path('C:/Users/wisdom/wisdom/data/feature_signal_mapping.json')
    
    with open(mapping_path, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    
    # 修正TEN_GOD的定义：从Classic-owned改为Canonical-Derived
    if 'TEN_GOD' in mapping.get('signal_features', {}):
        mapping['signal_features']['TEN_GOD']['status'] = 'CANONICAL_DERIVED'
        mapping['signal_features']['TEN_GOD']['description'] = '十神（Canonical计算结果，经典提供语义解释）'
        mapping['signal_features']['TEN_GOD']['calculation_source'] = 'data/semantic_atoms/ten_gods.json'
        mapping['signal_features']['TEN_GOD']['interpretation_authority'] = ['YHZP', 'PZZQ', 'QTBJ']
    
    # 修正STRENGTH的定义：从Classic直接计算改为Canonical+Semantic
    if 'STRENGTH' in mapping.get('signal_features', {}):
        mapping['signal_features']['STRENGTH']['status'] = 'CANONICAL_WITH_SEMANTIC'
        mapping['signal_features']['STRENGTH']['description'] = '日主旺衰（Canonical计算 + DTS/YHZP语义权威）'
        mapping['signal_features']['STRENGTH']['calculation_source'] = 'Canonical Chart State Engine'
        mapping['signal_features']['STRENGTH']['semantic_authority'] = ['DTS', 'YHZP']
    
    # 更新Classic Capabilities
    if 'classic_capabilities' in mapping:
        for classic in mapping['classic_capabilities']:
            caps = mapping['classic_capabilities'][classic]
            # 移除TEN_GOD作为primary signal
            if 'TEN_GOD' in caps.get('primary_signals', []):
                caps['primary_signals'].remove('TEN_GOD')
                caps['semantic_dependency'] = caps.get('semantic_dependency', [])
                caps['semantic_dependency'].append('TEN_GOD')
    
    # 保存
    with open(mapping_path, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    
    print("📄 Feature Mapping 已更新")
    print()

if __name__ == '__main__':
    stats = fix_evidence_signal_mapping()
    update_feature_mapping(stats)
    
    # 验证结果
    print("=" * 70)
    print("验证结果:")
    print("=" * 70)
    
    evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')
    signal_counts = defaultdict(int)
    total = 0
    
    for f in evidence_dir.rglob('E-*.json'):
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            signal = data.get('signal_type', 'GENERAL')
            signal_counts[signal] += 1
            total += 1
        except:
            pass
    
    print(f"总证据数: {total}")
    print("信号分布:")
    for sig, count in sorted(signal_counts.items(), key=lambda x: -x[1]):
        print(f"   {sig}: {count}")
    
    general_count = signal_counts.get('GENERAL', 0)
    mapped_count = total - general_count
    print()
    print(f"已映射: {mapped_count}/{total} ({mapped_count/total*100:.1f}%)")
    print(f"仍为GENERAL: {general_count} ({general_count/total*100:.1f}%)")