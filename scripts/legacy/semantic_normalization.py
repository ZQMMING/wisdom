#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五经证据语义归一化脚本
根据仲裁裁决重构证据分类体系
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional

class SemanticNormalizer:
    """语义归一化器 - 根据仲裁裁决重构证据分类"""
    
    # 五类语义问题分类
    SEMANTIC_CATEGORIES = {
        'SEMANTIC_AUTHORITY': 'A. Semantic Authority - 谁负责什么',
        'SEMANTIC_COMPOSITION': 'B. Semantic Composition - 信号如何共同作用',
        'CLASSIFICATION_AXES': 'C. Classification Axes - 分类维度',
        'DETERMINISTIC_CANONICAL': 'D. Deterministic Canonical Rules - 确定性规则',
        'GENUINE_CONTRADICTION': 'E. Genuine Contradictions - 真正矛盾'
    }
    
    # 证据关系类型
    RELATIONSHIP_TYPES = {
        'COMPLEMENTARY': '互补 - 不同维度描述',
        'SPECIALIZED': '专精 - 特定领域权威',
        'CONTEXTUAL': '情境依赖 - 条件触发',
        'TRUE_CONFLICT': '真正冲突 - 相同条件互斥结论',
        'REDUNDANT': '冗余 - 重复证据',
        'REJECTED': '废弃 - 错误证据'
    }
    
    def __init__(self, evidence_dir: Path):
        self.evidence_dir = evidence_dir
        self.evidences = []
        self.authority_map = {}
        self.signal_map = {}
        
    def load_evidences(self):
        """加载所有证据"""
        print("[1] 加载证据...")
        
        for ev_dir in self.evidence_dir.iterdir():
            if not ev_dir.is_dir() or ev_dir.name.startswith('_'):
                continue
            
            classic_name = ev_dir.name
            for ev_file in ev_dir.glob('E-*.json'):
                ev = json.load(open(ev_file, 'r', encoding='utf-8'))
                ev['_classic'] = classic_name
                self.evidences.append(ev)
        
        print(f"  总证据数: {len(self.evidences)}")
        return len(self.evidences)
    
    def classify_by_authority(self):
        """根据仲裁裁决分类证据权威"""
        print("\n[2] 证据权威分类...")
        
        # DTS: Principle Constraint Authority
        # QTBJ: Climate/Seasonal Authority
        # PZZQ: Pattern Operational Authority
        # YHZP: Daymaster/Structure Authority
        # SMTH: Element Identity Authority
        
        authority_map = defaultdict(list)
        
        for ev in self.evidences:
            classic = ev['_classic']
            
            if classic == 'di_tian_sui':
                authority = 'PRINCIPLE_CONSTRAINT'
            elif classic == 'qiong_tong_bao_jian':
                authority = 'CLIMATE_SEASONAL'
            elif classic == 'ziping_zhenquan':
                authority = 'PATTERN_OPERATIONAL'
            elif classic == 'yuan_hai_zi_ping':
                authority = 'DAYMASTER_STRUCTURE'
            elif classic == 'san_ming_tong_hui':
                authority = 'ELEMENT_IDENTITY'
            else:
                authority = 'UNKNOWN'
            
            ev['authority'] = authority
            authority_map[authority].append(ev['evidence_id'])
        
        self.authority_map = dict(authority_map)
        
        print("  权威分类统计:")
        for auth, ids in authority_map.items():
            print(f"    {auth}: {len(ids)}条")
        
        return authority_map
    
    def classify_by_signal_type(self):
        """根据仲裁裁决分类信号类型"""
        print("\n[3] 信号类型分类...")
        
        signal_map = defaultdict(lambda: defaultdict(list))
        
        for ev in self.evidences:
            classic = ev['_classic']
            text = ev.get('evidence_text', {}).get('original_text', '')
            conditions = ev.get('conditions', [])
            
            # 识别信号类型
            signals = []
            
            # 旺衰信号
            if any(kw in text for kw in ['衰旺', '旺衰', '得令', '失令', '得地', '失地', '身旺', '身弱']):
                signals.append('STRENGTH')
            
            # 调候信号
            if any(kw in text for kw in ['调候', '寒暖', '燥湿', '需水', '需火', '喜水', '喜火']):
                signals.append('CLIMATE')
            
            # 格局信号
            if any(kw in text for kw in ['格局', '成败', '相神', '救应', '用神', '月令']):
                signals.append('PATTERN')
            
            # 十神信号
            if any(kw in text for kw in ['财官', '印绶', '食神', '伤官', '七杀', '正官']):
                signals.append('TEN_GOD')
            
            # 五行信号
            if any(kw in text for kw in ['五行', '金木水火土', '流通', '种性']):
                signals.append('FIVE_ELEMENTS')
            
            # 阴阳信号
            if any(kw in text for kw in ['阴阳', '长生', '十二支']):
                signals.append('YIN_YANG')
            
            # 如果没有识别到信号，标记为通用
            if not signals:
                signals.append('GENERAL')
            
            ev['signals'] = signals
            
            for sig in signals:
                signal_map[sig][classic].append(ev['evidence_id'])
        
        self.signal_map = dict(signal_map)
        
        print("  信号类型统计:")
        for sig, classics in signal_map.items():
            total = sum(len(ids) for ids in classics.values())
            print(f"    {sig}: {total}条")
        
        return signal_map
    
    def reclassify_conflicts(self):
        """重新分类冲突为五类语义问题"""
        print("\n[4] 重新分类冲突...")
        
        reclassification = {
            'CONF_1_WANGSHUAI_TIAOHOU': {
                'original': '旺衰 vs 调候',
                'new_category': 'SEMANTIC_COMPOSITION',
                'new_type': 'COMPLEMENTARY',
                'reason': '两套独立Signals，不设绝对优先级',
                'resolution': 'Strength Signal + Climate Signal 并行计算'
            },
            'CONF_2_MONTH_DAYMASTER': {
                'original': '月令用神 vs 日主状态',
                'new_category': 'SEMANTIC_AUTHORITY',
                'new_type': 'SPECIALIZED',
                'reason': '需要语义拆分：Pattern / Strength / Utility',
                'resolution': 'PZZQ负责Pattern，YHZP负责Daymaster'
            },
            'CONF_3_DTS_PZZQ_METHOD': {
                'original': 'DTS vs PZZQ方法论',
                'new_category': 'SEMANTIC_AUTHORITY',
                'new_type': 'SPECIALIZED',
                'reason': 'Principle Constraint vs Pattern Operational',
                'resolution': 'DTS提供上层约束，PZZQ提供操作方法'
            },
            'CONF_4_PATTERN_BINARY_TERNARY': {
                'original': '格局二分 vs 三分',
                'new_category': 'CLASSIFICATION_AXES',
                'new_type': 'CONTEXTUAL',
                'reason': '不同classification axis，不创建第三格',
                'resolution': 'PatternType + PatternClarity + PatternIntegrity'
            },
            'CONF_5_FLOW_IDENTITY': {
                'original': '流通 vs 种性',
                'new_category': 'SEMANTIC_COMPOSITION',
                'new_type': 'COMPLEMENTARY',
                'reason': '不同语义层：动态 vs 静态',
                'resolution': 'SMTH负责Element Identity，DTS负责Qi Flow'
            },
            'CONF_6_YINYANG_LIFE_DEATH': {
                'original': '阴阳生死',
                'new_category': 'DETERMINISTIC_CANONICAL',
                'new_type': 'TRUE_CONFLICT',
                'reason': 'Deterministic Engine必须统一规则',
                'resolution': 'Frozen: 采用DTS阴阳同生同死canonical mapping'
            }
        }
        
        print("  冲突重新分类:")
        for conf_id, info in reclassification.items():
            print(f"    {conf_id}: {info['original']} → {info['new_category']} ({info['new_type']})")
        
        return reclassification
    
    def generate_authority_registry(self):
        """生成语义权威注册表"""
        print("\n[5] 生成语义权威注册表...")
        
        registry = {
            'metadata': {
                'version': '1.0.0',
                'created': '2026-09-02',
                'arbitration_status': 'CONDITIONAL_PASS',
                'total_evidences': len(self.evidences)
            },
            'authorities': {},
            'signals': {},
            'classifications': {}
        }
        
        # DTS: Principle Constraint Authority
        registry['authorities']['di_tian_sui'] = {
            'name': '滴天髓',
            'authority_type': 'PRINCIPLE_CONSTRAINT',
            'description': '上层方法论约束，纠正机械套格',
            'scope': ['旺衰', '进退', '寒暖燥湿', '五行作用', '反机械化'],
            'evidence_count': len(self.authority_map.get('PRINCIPLE_CONSTRAINT', [])),
            'key_principles': [
                '须观日主之衰旺，察生时之浅深，究四柱之用神',
                '进退之机，不可不知也',
                '命贵中和，偏枯终于有损'
            ]
        }
        
        # QTBJ: Climate/Seasonal Authority
        registry['authorities']['qiong_tong_bao_jian'] = {
            'name': '穷通宝鉴',
            'authority_type': 'CLIMATE_SEASONAL',
            'description': '月令调候专门权威',
            'scope': ['寒暖', '燥湿', '月份调候', '十干月份规则'],
            'evidence_count': len(self.authority_map.get('CLIMATE_SEASONAL', [])),
            'key_principles': [
                '秋月之木，氣漸淒涼',
                '寒暖适中时为吉',
                '调候得宜为用'
            ]
        }
        
        # PZZQ: Pattern Operational Authority
        registry['authorities']['ziping_zhenquan'] = {
            'name': '子平真诠',
            'authority_type': 'PATTERN_OPERATIONAL',
            'description': '格局成败救应操作体系',
            'scope': ['格局', '成败', '救应', '相神', '顺逆'],
            'evidence_count': len(self.authority_map.get('PATTERN_OPERATIONAL', [])),
            'key_principles': [
                '八字用神，专求月令',
                '相神无破，贵格已成',
                '当顺而顺，当逆而逆'
            ]
        }
        
        # YHZP: Daymaster/Structure Authority
        registry['authorities']['yuan_hai_zi_ping'] = {
            'name': '渊海子平',
            'authority_type': 'DAYMASTER_STRUCTURE',
            'description': '日主状态与格局综合判断',
            'scope': ['日主强弱', '格局清浊', '十神配合', '案例'],
            'evidence_count': len(self.authority_map.get('DAYMASTER_STRUCTURE', [])),
            'key_principles': [
                '以日为主，大要看日加临于甚度',
                '月为提纲',
                '身旺杀旺为贵'
            ]
        }
        
        # SMTH: Element Identity Authority
        registry['authorities']['san_ming_tong_hui'] = {
            'name': '三命通会',
            'authority_type': 'ELEMENT_IDENTITY',
            'description': '五行性质与神煞汇编',
            'scope': ['五行种性', '神煞', '禄马', '天乙贵人'],
            'evidence_count': len(self.authority_map.get('ELEMENT_IDENTITY', [])),
            'key_principles': [
                '金有金之种，木有木之种',
                '各各完具不相假借',
                '禄马旺相为贵'
            ]
        }
        
        # Signals
        registry['signals'] = {}
        for sig, classics in self.signal_map.items():
            registry['signals'][sig] = {
                'description': f'{sig}信号',
                'sources': {c: len(ids) for c, ids in classics.items()},
                'total': sum(len(ids) for ids in classics.values())
            }
        
        # Classifications
        registry['classifications'] = {
            'pattern_type': {
                'axis': '格局类型',
                'values': ['正官', '偏官', '正财', '偏财', '正印', '偏印', '食神', '伤官', '比肩', '劫财']
            },
            'pattern_clarity': {
                'axis': '格局清纯程度',
                'values': ['清', '浊', '混']
            },
            'pattern_integrity': {
                'axis': '格局完整程度',
                'values': ['成', '败', '救']
            },
            'strength_level': {
                'axis': '日主旺衰等级',
                'values': ['极旺', '旺', '中和', '弱', '极弱']
            },
            'climate_condition': {
                'axis': '寒暖燥湿状态',
                'values': ['寒', '暖', '燥', '湿', '中和']
            }
        }
        
        return registry
    
    def generate_reclassification_report(self):
        """生成重新分类报告"""
        print("\n[6] 生成重新分类报告...")
        
        report = {
            'metadata': {
                'title': '五经证据语义归一化报告',
                'date': '2026-09-02',
                'status': 'ARBITRATION_CONDITIONAL_PASS',
                'total_evidences': len(self.evidences)
            },
            'summary': {
                'semantic_categories': len(self.SEMANTIC_CATEGORIES),
                'relationship_types': len(self.RELATIONSHIP_TYPES),
                'authorities_defined': len(self.authority_map),
                'signal_types_defined': len(self.signal_map)
            },
            'authority_distribution': self.authority_map,
            'signal_distribution': {
                sig: {c: len(ids) for c, ids in classics.items()}
                for sig, classics in self.signal_map.items()
            },
            'conflict_reclassification': {
                'CONF_1_WANGSHUAI_TIAOHOU': {
                    'status': 'RECLASSIFIED_TO_COMPLEMENTARY',
                    'new_framework': 'Strength Signal + Climate Signal'
                },
                'CONF_2_MONTH_DAYMASTER': {
                    'status': 'RECLASSIFIED_TO_SPECIALIZED',
                    'new_framework': 'Pattern / Strength / Utility三层拆分'
                },
                'CONF_3_DTS_PZZQ_METHOD': {
                    'status': 'RECLASSIFIED_TO_SPECIALIZED',
                    'new_framework': 'Principle Constraint + Pattern Operational'
                },
                'CONF_4_PATTERN_BINARY_TERNARY': {
                    'status': 'RECLASSIFIED_TO_CONTEXTUAL',
                    'new_framework': 'PatternType + PatternClarity + PatternIntegrity'
                },
                'CONF_5_FLOW_IDENTITY': {
                    'status': 'RECLASSIFIED_TO_COMPLEMENTARY',
                    'new_framework': 'Element Identity + Qi Flow'
                },
                'CONF_6_YINYANG_LIFE_DEATH': {
                    'status': 'RECLASSIFIED_TO_TRUE_CONFLICT',
                    'new_framework': 'Frozen Canonical: DTS 阴阳同生同死'
                }
            },
            'next_steps': [
                '1. 语义归一化完成',
                '2. 进入Authority Assignment阶段',
                '3. Feature/Signal Mapping',
                '4. Independent Verification',
                '5. Production Admission'
            ]
        }
        
        return report
    
    def run(self):
        """执行完整归一化流程"""
        print("="*60)
        print("五经证据语义归一化流程")
        print("="*60)
        
        # 1. 加载证据
        total = self.load_evidences()
        if total == 0:
            print("❌ 没有证据可处理")
            return None
        
        # 2. 权威分类
        authority_map = self.classify_by_authority()
        
        # 3. 信号分类
        signal_map = self.classify_by_signal_type()
        
        # 4. 冲突重新分类
        reclassification = self.reclassify_conflicts()
        
        # 5. 生成权威注册表
        registry = self.generate_authority_registry()
        
        # 6. 生成报告
        report = self.generate_reclassification_report()
        
        # 保存结果
        output_dir = Path('C:/Users/wisdom/wisdom/data/evidence')
        
        # 保存权威注册表
        registry_file = output_dir / 'semantic_authority_registry.json'
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 权威注册表已保存: {registry_file}")
        
        # 保存报告
        report_file = output_dir / 'semantic_normalization_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"✅ 归一化报告已保存: {report_file}")
        
        # 更新证据文件中的分类信息
        print("\n[7] 更新证据分类信息...")
        updated_count = 0
        for ev in self.evidences:
            ev_path = self.evidence_dir / ev['_classic'] / f"{ev['evidence_id'].replace('-', '_')}.json"
            if ev_path.exists():
                # 读取原文件
                with open(ev_path, 'r', encoding='utf-8') as f:
                    ev_data = json.load(f)
                
                # 添加新字段
                ev_data['semantic_classification'] = {
                    'authority': ev.get('authority', ''),
                    'signals': ev.get('signals', []),
                    'category': self._classify_evidence(ev)
                }
                
                # 写回文件
                with open(ev_path, 'w', encoding='utf-8') as f:
                    json.dump(ev_data, f, ensure_ascii=False, indent=2)
                
                updated_count += 1
        
        print(f"✅ 已更新 {updated_count} 条证据的分类信息")
        
        return {
            'total_evidences': total,
            'authorities': authority_map,
            'signals': signal_map,
            'reclassification': reclassification,
            'registry_file': str(registry_file),
            'report_file': str(report_file)
        }
    
    def _classify_evidence(self, ev: Dict) -> str:
        """分类单条证据到语义类别"""
        text = ev.get('evidence_text', {}).get('original_text', '')
        signals = ev.get('signals', [])
        
        # 确定性规则类
        if any(sig in signals for sig in ['YIN_YANG']):
            return 'DETERMINISTIC_CANONICAL'
        
        # 真正冲突类
        if any(kw in text for kw in ['荒唐', '谬书', '妄谈', '非关命理']):
            return 'TRUE_CONFLICT'
        
        # 互补类
        if any(sig in signals for sig in ['FIVE_ELEMENTS']):
            return 'COMPLEMENTARY'
        
        # 专精类
        if ev.get('authority') in ['PRINCIPLE_CONSTRAINT', 'CLIMATE_SEASONAL', 'PATTERN_OPERATIONAL']:
            return 'SPECIALIZED'
        
        # 情境依赖类
        if any(sig in signals for sig in ['PATTERN', 'TEN_GOD']):
            return 'CONTEXTUAL'
        
        # 默认
        return 'COMPLEMENTARY'


def main():
    evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')
    
    normalizer = SemanticNormalizer(evidence_dir)
    result = normalizer.run()
    
    if result:
        print("\n" + "="*60)
        print("语义归一化完成")
        print("="*60)
        print(f"总证据数: {result['total_evidences']}")
        print(f"权威分类数: {len(result['authorities'])}")
        print(f"信号类型数: {len(result['signals'])}")
        print(f"\n输出文件:")
        print(f"  - {result['registry_file']}")
        print(f"  - {result['report_file']}")


if __name__ == '__main__':
    main()
