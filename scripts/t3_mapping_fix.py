# -*- coding: utf-8 -*-
"""T3 Mapping 修复脚本

为 A 类 6 条证据补充 Feature → Primitive 映射规则
"""
import json
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class FeatureType(str, Enum):
    """Feature 类型"""
    BOOLEAN = "boolean"        # 布尔值（得令/得地等）
    INTEGER = "integer"        # 整数（通根数/透干数）
    FLOAT = "float"            # 浮点数（生扶/泄耗计数）
    STRING = "string"          # 字符串（细节描述）
    LIST = "list"              # 列表（细节列表）


@dataclass
class FeatureMapping:
    """Feature → Primitive 映射规则"""
    evidence_id: str
    primitive_name: str
    condition_text: str
    feature_ref: str                # D1FeatureResult 字段名
    feature_type: FeatureType
    operator: str                   # >/</==/contains/exists
    value: Any                      # 阈值或预期值
    authorization: str              # 原典授权文本


def load_pending_analysis():
    """加载 PENDING 分析结果"""
    with open('data/t3_pending_analysis.json') as f:
        return json.load(f)


def load_validation_result():
    """加载验证结果"""
    with open('data/t3_primitive_validation_result.json') as f:
        return json.load(f)


def build_mapping_rules(pending_data: dict) -> List[FeatureMapping]:
    """构建 Mapping 规则"""
    
    # A 类证据的映射规则定义
    mapping_definitions = {
        "三命通会_强弱_得令": FeatureMapping(
            evidence_id="三命通会_强弱_得令",
            primitive_name="得令",
            condition_text="月令本气与日主同党，或十二长生位临官/帝旺",
            feature_ref="de_ling",
            feature_type=FeatureType.BOOLEAN,
            operator="==",
            value=True,
            authorization="《渊海子平》得令者临官帝旺也"
        ),
        "三命通会_强弱_得地": FeatureMapping(
            evidence_id="三命通会_强弱_得地",
            primitive_name="得地",
            condition_text="地支藏干见比劫印星",
            feature_ref="de_di",
            feature_type=FeatureType.INTEGER,
            operator=">=",
            value=1,
            authorization="《渊海子平》得地：地支通根"
        ),
        "三命通会_强弱_得势": FeatureMapping(
            evidence_id="三命通会_强弱_得势",
            primitive_name="得势",
            condition_text="天干透比劫印星",
            feature_ref="de_shi",
            feature_type=FeatureType.INTEGER,
            operator=">=",
            value=1,
            authorization="《渊海子平》得势：天干透比劫印星"
        ),
        "三命通会_强弱_身强条件": FeatureMapping(
            evidence_id="三命通会_强弱_身强条件",
            primitive_name="身强条件",
            condition_text="生扶 > 泄耗",
            feature_ref="support_count",
            feature_type=FeatureType.FLOAT,
            operator=">",
            value="drain_count",  # 相对值
            authorization="《滴天髓》生扶克泄耗"
        ),
        "三命通会_强弱_身弱条件": FeatureMapping(
            evidence_id="三命通会_强弱_身弱条件",
            primitive_name="身弱条件",
            condition_text="泄耗 > 生扶",
            feature_ref="drain_count",
            feature_type=FeatureType.FLOAT,
            operator=">",
            value="support_count",  # 相对值
            authorization="《滴天髓》泄耗克"
        ),
        "三命通会_强弱_身强三要素": FeatureMapping(
            evidence_id="三命通会_强弱_身强三要素",
            primitive_name="身强三要素",
            condition_text="得令 + 得地 + 得势",
            feature_ref="de_ling_de_di_de_shi",
            feature_type=FeatureType.BOOLEAN,
            operator="==",
            value=True,
            authorization="《渊海子平》身强三要素"
        ),
    }
    
    # 筛选 A 类
    a_class = [a for a in pending_data['analyses'] if a['category'] == 'A']
    
    mappings = []
    for item in a_class:
        mapping = mapping_definitions.get(item['evidence_id'])
        if mapping:
            mappings.append(mapping)
        else:
            print(f"⚠️ 未找到映射定义: {item['evidence_id']}")
    
    return mappings


def save_mapping_rules(mappings: List[FeatureMapping]):
    """保存 Mapping 规则"""
    output = {
        'total': len(mappings),
        'mappings': [
            {
                'evidence_id': m.evidence_id,
                'primitive_name': m.primitive_name,
                'condition_text': m.condition_text,
                'feature_ref': m.feature_ref,
                'feature_type': m.feature_type.value,
                'operator': m.operator,
                'value': m.value,
                'authorization': m.authorization,
            }
            for m in mappings
        ]
    }
    
    with open('data/t3_mapping_rules.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 保存 {len(mappings)} 条 Mapping 规则到 data/t3_mapping_rules.json")


def main():
    print("=== T3 Mapping 修复 ===\n")
    
    # 加载数据
    pending_data = load_pending_analysis()
    
    # 构建 Mapping 规则
    mappings = build_mapping_rules(pending_data)
    
    # 保存
    save_mapping_rules(mappings)
    
    # 输出统计
    print(f"\nA 类总计: {len([a for a in pending_data['analyses'] if a['category'] == 'A'])} 条")
    print(f"已定义 Mapping: {len(mappings)} 条")
    
    if len(mappings) < len([a for a in pending_data['analyses'] if a['category'] == 'A']):
        print(f"⚠️ 还有 {len([a for a in pending_data['analyses'] if a['category'] == 'A']) - len(mappings)} 条未定义 Mapping")


if __name__ == '__main__':
    main()
