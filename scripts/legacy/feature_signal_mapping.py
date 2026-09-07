#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feature / Signal Mapping - Phase 3 Entry
从 Semantic Normalization 进入 Feature/Signal Mapping
"""

import json
from pathlib import Path
from collections import defaultdict

def main():
    evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')
    canonical_dir = Path('C:/Users/wisdom/wisdom/data/canonical')
    
    print("=" * 70)
    print("Phase 3: Feature / Signal Mapping")
    print("=" * 70)
    print()
    
    # 1. 加载 Alias Mapping
    with open(canonical_dir / 'alias_mapping.json', 'r', encoding='utf-8') as f:
        alias_map = json.load(f)
    
    print("📋 Alias Mapping 加载完成")
    print(f"   映射条目: {len(alias_map['mappings'])}")
    print()
    
    # 2. 加载 Primitive Registry
    with open(canonical_dir / 'primitive_registry.json', 'r', encoding='utf-8') as f:
        primitives = json.load(f)
    
    print(f"📚 Primitive Registry: {len(primitives)} items")
    print()
    
    # 3. 分析 Evidence 的 Signal 分布
    signal_distribution = defaultdict(int)
    theme_distribution = defaultdict(int)
    classic_signal_matrix = defaultdict(lambda: defaultdict(int))
    
    for f in evidence_dir.rglob('E-*.json'):
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            
            signal = data.get('signal_type', 'GENERAL')
            theme = data.get('theme', 'GENERAL')
            classic = data.get('authority_type', 'UNKNOWN')
            
            signal_distribution[signal] += 1
            theme_distribution[theme[:30]] += 1
            classic_signal_matrix[classic][signal] += 1
        except:
            pass
    
    print("📊 Signal 分布:")
    for sig, count in sorted(signal_distribution.items(), key=lambda x: -x[1]):
        print(f"   {sig}: {count}")
    print()
    
    print("📊 Classic × Signal 矩阵:")
    for classic in sorted(classic_signal_matrix.keys()):
        signals = classic_signal_matrix[classic]
        total = sum(signals.values())
        signal_str = ", ".join([f"{s}:{c}" for s, c in sorted(signals.items(), key=lambda x: -x[1])])
        print(f"   {classic}: {total} ({signal_str})")
    print()
    
    # 4. 生成 Feature Mapping 草案
    feature_mapping = {
        "_metadata": {
            "version": "1.0",
            "date": "2026-09-02",
            "phase": "Feature/Signal Mapping",
            "total_evidence": sum(signal_distribution.values())
        },
        "signal_features": {},
        "classic_capabilities": {}
    }
    
    # 为每个信号创建 Feature 定义
    signal_features = {
        "STRENGTH": {
            "description": "日主旺衰判断",
            "source_classics": ["DTS", "YHZP"],
            "output_type": "enum",
            "values": ["极强", "强", "中和", "弱", "极弱"],
            "canonical_rules": ["DTS-PRIM-004", "DTS-PRIM-007"]
        },
        "CLIMATE": {
            "description": "调候寒暖需求",
            "source_classics": ["QTBJ"],
            "output_type": "enum",
            "values": ["寒", "暖", "燥", "湿", "中和"],
            "canonical_rules": []
        },
        "PATTERN": {
            "description": "格局分析",
            "source_classics": ["PZZQ", "YHZP"],
            "output_type": "struct",
            "fields": ["type", "clarity", "integrity"],
            "canonical_rules": []
        },
        "TEN_GOD": {
            "description": "十神配合",
            "source_classics": ["YHZP", "PZZQ"],
            "output_type": "list",
            "values": ["正官", "偏官", "正印", "偏印", "比肩", "劫财", "食神", "伤官", "偏财", "正财"],
            "canonical_rules": []
        },
        "FIVE_ELEMENTS": {
            "description": "五行流通",
            "source_classics": ["DTS", "SMTH"],
            "output_type": "relation",
            "canonical_rules": []
        },
        "YIN_YANG": {
            "description": "阴阳长生",
            "source_classics": ["DTS"],
            "output_type": "mapping",
            "canonical_rules": ["DTS-PRIM-015", "DTS-PRIM-016"]
        },
        "GENERAL": {
            "description": "通用论述",
            "source_classics": ["DTS", "QTBJ", "YHZP", "SMTH"],
            "output_type": "text",
            "canonical_rules": []
        }
    }
    
    feature_mapping["signal_features"] = signal_features
    
    # 为每个经典创建 Capability 定义
    classic_capabilities = {
        "DTS": {
            "authority": "PRINCIPLE_CONSTRAINT",
            "primary_signals": ["STRENGTH", "FIVE_ELEMENTS", "YIN_YANG"],
            "scope": "整体气势、进退之机、寒暖燥湿",
            "constraints": ["不直接给具体用神", "提供上层方法论约束"]
        },
        "QTBJ": {
            "authority": "CLIMATE_SEASONAL",
            "primary_signals": ["CLIMATE", "TEN_GOD"],
            "scope": "月份调候规则、十干月令喜忌",
            "constraints": ["不替代格局判断"]
        },
        "PZZQ": {
            "authority": "PATTERN_OPERATIONAL",
            "primary_signals": ["PATTERN", "TEN_GOD"],
            "scope": "格局成败、顺逆用神、相神救应",
            "constraints": ["不替代日主强弱判断"]
        },
        "YHZP": {
            "authority": "DAYMASTER_STRUCTURE",
            "primary_signals": ["STRENGTH", "PATTERN", "TEN_GOD"],
            "scope": "日主状态、根气强弱、十神配合",
            "constraints": ["不替代月令专求"]
        },
        "SMTH": {
            "authority": "ELEMENT_IDENTITY",
            "primary_signals": ["FIVE_ELEMENTS", "YIN_YANG"],
            "scope": "五行性质、神煞系统、种性理论",
            "constraints": ["不替代格局分析"]
        }
    }
    
    feature_mapping["classic_capabilities"] = classic_capabilities
    
    # 保存
    mapping_path = evidence_dir.parent / 'feature_signal_mapping.json'
    with open(mapping_path, 'w', encoding='utf-8') as f:
        json.dump(feature_mapping, f, ensure_ascii=False, indent=2)
    
    print("📄 Feature/Signal Mapping 草案已生成")
    print(f"   路径: {mapping_path}")
    print()
    
    # 5. 总结
    print("=" * 70)
    print("Phase 3 启动完成")
    print("=" * 70)
    print()
    print("下一步:")
    print("  1. 完善 Signal Features 定义")
    print("  2. 建立 Signal → Feature 映射规则")
    print("  3. 进入 Independent Verification")
    print()
    
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)