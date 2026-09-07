#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五经证据语义字段补全脚本
"""

import json
from pathlib import Path
from typing import Dict, Any, List

class EvidenceCompleter:
    """证据字段补全器"""
    
    # 证据类型到主题映射
    TYPE_THEME_MAP = {
        # DTS类型
        '101': '三元本体论',
        '102': '地道五行',
        '103': '人道贵贱',
        '104': '知命顺逆',
        '105': '理气进退',
        '106': '五行生成',
        '107': '五行生克',
        '108': '五行流通',
        '109': '五行偏枯',
        '110': '五行补救',
        # PZZQ类型
        'KEY_CONCEPT': '关键概念',
        'YONGSHEN_VALID': '用神有力',
        'YONGSHEN_WEAK': '用神无力',
        'GEJU_SUCCESS': '格局成功',
        'GEJU_FAILURE': '格局失败',
        'TIAN_GAN_SUPPORT': '天干辅佐',
        'DI_ZHI_SUPPORT': '地支辅佐',
        'PATTERN_RESCUE': '格局救助',
        # QTBJ类型
        'TEM': '调候寒暖',
        'ADJ': '调候方法',
        # SMTH类型
        'KEY_PASSAGE': '关键段落',
        'JIANLU': '建禄格',
        'LU': '日禄',
        'SHW': '岁旺',
        'TIANYI': '天乙贵人',
        # YHZP类型
        'DAYMASTER_STRONG': '日主强旺',
        'DAYMASTER_WEAK': '日主衰弱',
        'MONTH_BRANCH_DOMINANT': '月令主导',
        'TEN_GODS_BALANCE': '十神平衡',
        'STRUCTURE_CLEAR': '格局清晰',
        'STRUCTURE_MIXED': '格局混杂',
    }
    
    def __init__(self, classics_dir: Path, evidence_dir: Path):
        self.classics_dir = classics_dir
        self.evidence_dir = evidence_dir
        self.passages = {}
        self.load_passages()
    
    def load_passages(self):
        """加载所有原典段落"""
        classic_map = {
            'DTS': 'di_tian_sui',
            'PZZQ': 'ziping_zhenquan',
            'QTBJ': 'qiong_tong_bao_jian',
            'SMTH': 'san_ming_tong_hui',
            'YHZP': 'yuan_hai_zi_ping'
        }
        
        for f in self.classics_dir.glob('*段落数据.json'):
            data = json.load(open(f, 'r', encoding='utf-8'))
            prefix = f.stem.split('_')[0]
            key = classic_map.get(prefix, prefix.lower())
            self.passages[key] = {p['passage_id']: p for p in data['passages']}
    
    def get_context(self, passage_text: str, evidence_text: str, window: int = 300) -> tuple:
        """提取上下文"""
        if evidence_text not in passage_text:
            return '', ''
        
        idx = passage_text.find(evidence_text)
        start = max(0, idx - window)
        end = min(len(passage_text), idx + len(evidence_text) + window)
        
        context_before = passage_text[start:idx]
        context_after = passage_text[idx + len(evidence_text):end]
        
        return context_before, context_after
    
    def enrich_evidence(self, ev: Dict[str, Any], classic: str, passage: Dict) -> Dict[str, Any]:
        """补全证据字段"""
        evidence_type = ev.get('evidence_type', '')
        original_text = ev.get('original_text', '')
        
        # 1. classical_theme
        theme = self.TYPE_THEME_MAP.get(evidence_type, evidence_type)
        ev['classical_theme'] = theme
        
        # 2. conditions - 从原文提取条件
        conditions = self.extract_conditions(original_text, evidence_type)
        ev['conditions'] = conditions
        
        # 3. trigger_conditions
        triggers = self.extract_triggers(original_text, evidence_type)
        ev['trigger_conditions'] = triggers
        
        # 4. semantic_result
        semantic = self.derive_semantic(original_text, evidence_type, theme)
        ev['semantic_result'] = semantic
        
        # 5. scope
        scope = self.determine_scope(evidence_type, theme)
        ev['scope'] = scope
        
        # 6. exceptions
        exceptions = self.identify_exceptions(evidence_type, original_text)
        ev['exceptions'] = exceptions
        
        # 7. source_version
        ev['source_version'] = passage.get('source', 'unknown')
        
        # 8. provenance
        ev['provenance'] = {
            'classic': classic,
            'work': ev.get('source_locator', {}).get('work', ''),
            'chapter': ev.get('source_locator', {}).get('chapter', ''),
            'passage_id': ev.get('source_locator', {}).get('passage_id', ''),
            'original_source': passage.get('source', ''),
            'extraction_method': 'manual_extraction'
        }
        
        # 9. context
        passage_text = passage.get('text', '')
        context_before, context_after = self.get_context(passage_text, original_text)
        ev['evidence_text']['context_before'] = context_before
        ev['evidence_text']['context_after'] = context_after
        
        return ev
    
    def extract_conditions(self, text: str, evidence_type: str) -> List[str]:
        """从原文提取条件"""
        conditions = []
        
        # 常见条件模式
        patterns = [
            r'若.*则.*',
            r'.*喜.*',
            r'.*忌.*',
            r'.*当.*',
            r'.*宜.*',
            r'.*不宜.*',
            r'有.*则.*',
            r'无.*则.*',
        ]
        
        import re
        for pattern in patterns:
            matches = re.findall(pattern, text)
            conditions.extend(matches[:2])  # 最多取2个
        
        return list(set(conditions))[:5]  # 去重并限制数量
    
    def extract_triggers(self, text: str, evidence_type: str) -> List[str]:
        """提取触发条件"""
        triggers = []
        
        # 根据证据类型推断触发场景
        if 'STRONG' in evidence_type or '旺' in text:
            triggers.append('日主旺相时')
        elif 'WEAK' in evidence_type or '衰' in text:
            triggers.append('日主衰弱时')
        elif 'SUCCESS' in evidence_type or '成' in text:
            triggers.append('格局成时')
        elif 'FAILURE' in evidence_type or '败' in text:
            triggers.append('格局破时')
        elif 'COLD' in evidence_type or '寒' in text:
            triggers.append('命局寒湿时')
        elif 'HOT' in evidence_type or '暖' in text:
            triggers.append('命局燥热时')
        
        return triggers if triggers else ['通用']
    
    def derive_semantic(self, text: str, evidence_type: str, theme: str) -> str:
        """推导语义结果"""
        sematics = {
            'DAYMASTER_STRONG': '日主得令得地，气势旺盛',
            'DAYMASTER_WEAK': '日主失令失地，气势衰弱',
            'GEJU_SUCCESS': '格局成立，用神有力',
            'GEJU_FAILURE': '格局破损，用神受伤',
            'TEM': '调候得宜，寒暖适中',
            'ADJ': '调候方法得当',
            'KEY_CONCEPT': '关键命理概念阐述',
        }
        
        return sematics.get(evidence_type, f'{theme}相关论述')
    
    def determine_scope(self, evidence_type: str, theme: str) -> str:
        """确定适用范围"""
        scopes = {
            'DAYMASTER_STRONG': '身旺命局',
            'DAYMASTER_WEAK': '身弱命局',
            'GEJU_SUCCESS': '成格命局',
            'GEJU_FAILURE': '破格命局',
            'TEM': '所有命局（调候通用）',
            'ADJ': '需调候命局',
            'KEY_CONCEPT': '理论基础适用',
        }
        
        return scopes.get(evidence_type, '通用')
    
    def identify_exceptions(self, evidence_type: str, text: str) -> List[str]:
        """识别例外情况"""
        exceptions = []
        
        # 检查是否包含例外关键词
        if '例外' in text or '惟' in text or '独' in text:
            exceptions.append('特殊命局可能例外')
        if '从' in text and ('格' in text or '化' in text):
            exceptions.append('从格/化格不适用')
        
        return exceptions if exceptions else ['无明确例外']
    
    def process_classic(self, classic: str, evidence_dir_name: str):
        """处理单个经典"""
        evidence_dir = self.evidence_dir / evidence_dir_name
        if not evidence_dir.exists():
            print(f"警告: {evidence_dir} 不存在")
            return 0
        
        passages = self.passages.get(classic, {})
        completed = 0
        
        for ev_file in evidence_dir.glob('E-*.json'):
            with open(ev_file, 'r', encoding='utf-8') as f:
                ev = json.load(f)
            
            passage_id = ev.get('source_locator', {}).get('passage_id', '')
            passage = passages.get(passage_id, {})
            
            if passage:
                ev = self.enrich_evidence(ev, classic, passage)
                
                with open(ev_file, 'w', encoding='utf-8') as f:
                    json.dump(ev, f, ensure_ascii=False, indent=2)
                
                completed += 1
        
        return completed


def main():
    base_dir = Path(__file__).parent.parent
    classics_dir = base_dir / 'data' / 'classics' / 'original'
    evidence_dir = base_dir / 'data' / 'evidence'
    
    completer = EvidenceCompleter(classics_dir, evidence_dir)
    
    # 处理五个经典
    classics = [
        ('di_tian_sui', 'di_tian_sui'),
        ('ziping_zhenquan', 'ziping_zhenquan'),
        ('qiong_tong_bao_jian', 'qiong_tong_bao_jian'),
        ('san_ming_tong_hui', 'san_ming_tong_hui'),
        ('yuan_hai_zi_ping', 'yuan_hai_zi_ping'),
    ]
    
    results = {}
    for classic, dir_name in classics:
        count = completer.process_classic(classic, dir_name)
        results[classic] = count
        print(f"{classic}: 完成 {count} 条")
    
    # 生成报告
    report = {
        'total_completed': sum(results.values()),
        'per_classic': results,
        'timestamp': '2026-09-02'
    }
    
    report_dir = base_dir / 'data' / 'reports'
    report_dir.mkdir(exist_ok=True)
    
    with open(report_dir / 'completion_summary.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n总计完成: {report['total_completed']} 条证据")
    print(f"报告已保存: {report_dir / 'completion_summary.json'}")


if __name__ == '__main__':
    main()
