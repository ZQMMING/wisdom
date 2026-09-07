#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五经证据语义字段补全脚本 v2
改进版：更好的conditions提取和上下文填充
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple

class EvidenceCompleterV2:
    """证据字段补全器 v2 - 改进版"""
    
    # 证据类型到主题映射
    TYPE_THEME_MAP = {
        # DTS类型
        '101': '三元本体论', '102': '地道五行', '103': '人道贵贱',
        '104': '知命顺逆', '105': '理气进退', '106': '五行生成',
        '107': '五行生克', '108': '五行流通', '109': '五行偏枯', '110': '五行补救',
        # PZZQ类型
        'KEY_CONCEPT': '关键概念', 'YONGSHEN_VALID': '用神有力', 'YONGSHEN_WEAK': '用神无力',
        'GEJU_SUCCESS': '格局成功', 'GEJU_FAILURE': '格局失败',
        'TIAN_GAN_SUPPORT': '天干辅佐', 'DI_ZHI_SUPPORT': '地支辅佐', 'PATTERN_RESCUE': '格局救助',
        # QTBJ类型
        'TEM': '调候寒暖', 'ADJ': '调候方法',
        # SMTH类型
        'KEY_PASSAGE': '关键段落', 'JIANLU': '建禄格', 'LU': '日禄',
        'SHW': '岁旺', 'TIANYI': '天乙贵人',
        # YHZP类型
        'DAYMASTER_STRONG': '日主强旺', 'DAYMASTER_WEAK': '日主衰弱',
        'MONTH_BRANCH_DOMINANT': '月令主导', 'TEN_GODS_BALANCE': '十神平衡',
        'STRUCTURE_CLEAR': '格局清晰', 'STRUCTURE_MIXED': '格局混杂',
    }
    
    def __init__(self, classics_dir: Path, evidence_dir: Path):
        self.classics_dir = classics_dir
        self.evidence_dir = evidence_dir
        self.passages = {}
        self.load_passages()
    
    def load_passages(self):
        """加载所有原典段落"""
        classic_map = {
            'DTS': 'di_tian_sui', 'PZZQ': 'ziping_zhenquan',
            'QTBJ': 'qiong_tong_bao_jian', 'SMTH': 'san_ming_tong_hui',
            'YHZP': 'yuan_hai_zi_ping'
        }
        
        for f in self.classics_dir.glob('*段落数据.json'):
            data = json.load(open(f, 'r', encoding='utf-8'))
            prefix = f.stem.split('_')[0]
            key = classic_map.get(prefix, prefix.lower())
            self.passages[key] = {p['passage_id']: p for p in data['passages']}
    
    def extract_conditions_v2(self, text: str, evidence_type: str) -> List[str]:
        """改进的条件提取"""
        conditions = []
        
        # 模式1: 提取"若...则..."、"有...则..."等条件句式
        patterns = [
            r'若(.+?)，(.+?)[。.]',  # 若X，则Y
            r'有(.+?)，(则|乃|是).+?[。.]',  # 有X，则Y
            r'无(.+?)，(则|乃|是).+?[。.]',  # 无X，则Y
            r'(.+?)喜(.+?)[。.]',  # X喜Y
            r'(.+?)忌(.+?)[。.]',  # X忌Y
            r'(.+?)宜(.+?)[。.]',  # X宜Y
            r'(.+?)不宜(.+?)[。.]',  # X不宜Y
            r'当(.+?)，(.+?)[。.]',  # 当X，Y
            r'得(.+?)则(.+?)[。.]',  # 得X则Y
            r'失(.+?)则(.+?)[。.]',  # 失X则Y
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for m in matches:
                if isinstance(m, tuple):
                    cond = '，'.join(m)
                else:
                    cond = m
                if len(cond) > 3 and len(cond) < 100:
                    conditions.append(cond.strip())
        
        # 模式2: 提取关键词短语
        keywords = ['得令', '失令', '得地', '失地', '旺相', '休囚', '长生', '帝旺', '墓库']
        for kw in keywords:
            if kw in text:
                # 找包含该词的句子
                sentences = re.split(r'[。！？]', text)
                for s in sentences:
                    if kw in s and len(s) > 5:
                        conditions.append(s.strip())
        
        # 去重
        conditions = list(dict.fromkeys(conditions))[:10]
        
        return conditions
    
    def extract_context(self, passage_text: str, evidence_text: str, window: int = 300) -> Tuple[str, str]:
        """提取上下文"""
        if not evidence_text or not passage_text:
            return '', ''
        
        # 尝试精确匹配
        if evidence_text in passage_text:
            idx = passage_text.find(evidence_text)
            start = max(0, idx - window)
            end = min(len(passage_text), idx + len(evidence_text) + window)
            
            context_before = passage_text[start:idx]
            context_after = passage_text[idx + len(evidence_text):end]
            
            return context_before, context_after
        
        # 尝试模糊匹配（取前100字符）
        short_text = evidence_text[:100] if len(evidence_text) > 100 else evidence_text
        if short_text in passage_text:
            idx = passage_text.find(short_text)
            start = max(0, idx - window)
            context_before = passage_text[start:idx]
            context_after = passage_text[idx + len(short_text):idx + len(short_text) + window]
            return context_before, context_after
        
        # 如果找不到，尝试按句子分割
        sentences = re.split(r'[。！？]', passage_text)
        for i, s in enumerate(sentences):
            if evidence_text[:50] in s or s[:50] in evidence_text:
                before = '。'.join(sentences[max(0,i-2):i])
                after = '。'.join(sentences[i+1:min(len(sentences),i+3)])
                return before, after
        
        return '', ''
    
    def enrich_evidence(self, ev: Dict[str, Any], classic: str, passage: Dict) -> Dict[str, Any]:
        """补全证据字段"""
        evidence_type = ev.get('evidence_type', '')
        original_text = ev.get('original_text', '')
        
        # 1. classical_theme
        theme = self.TYPE_THEME_MAP.get(evidence_type, evidence_type)
        ev['classical_theme'] = theme
        
        # 2. conditions - 改进提取
        conditions = self.extract_conditions_v2(original_text, evidence_type)
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
        
        # 9. context - 改进提取
        passage_text = passage.get('text', '')
        context_before, context_after = self.extract_context(passage_text, original_text)
        ev['evidence_text']['context_before'] = context_before
        ev['evidence_text']['context_after'] = context_after
        
        return ev
    
    def extract_triggers(self, text: str, evidence_type: str) -> List[str]:
        """提取触发条件"""
        triggers = []
        
        # 根据证据类型推断触发场景
        type_triggers = {
            'DAYMASTER_STRONG': ['日主旺相时', '印比帮身时'],
            'DAYMASTER_WEAK': ['日主衰弱时', '官杀克身时'],
            'GEJU_SUCCESS': ['格局成立时', '用神有力时'],
            'GEJU_FAILURE': ['格局破损时', '用神受伤时'],
            'TEM': ['命局寒湿时', '命局燥热时'],
            'ADJ': ['需调候命局', '寒暖偏颇时'],
            'KEY_CONCEPT': ['基础理论适用时'],
        }
        
        triggers = type_triggers.get(evidence_type, ['通用情况'])
        
        # 检查文本中是否有特殊触发词
        if '从' in text and ('格' in text or '化' in text):
            triggers.append('从格/化格特殊情况')
        
        return triggers
    
    def derive_semantic(self, text: str, evidence_type: str, theme: str) -> str:
        """推导语义结果"""
        sematics = {
            'DAYMASTER_STRONG': '日主得令得地，气势旺盛，宜泄宜克',
            'DAYMASTER_WEAK': '日主失令失地，气势衰弱，宜生宜扶',
            'GEJU_SUCCESS': '格局成立，用神有力，主富贵',
            'GEJU_FAILURE': '格局破损，用神受伤，主贫贱',
            'TEM': '调候得宜，寒暖适中，五行平衡',
            'ADJ': '调候方法得当，可改善命局',
            'KEY_CONCEPT': '阐述关键命理概念，为基础理论依据',
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
        exception_patterns = [
            r'例外[：:].+',
            r'惟.+?[。.]',
            r'独.+?[。.]',
            r'从.+?格.+?不适用',
            r'化.+?格.+?例外',
        ]
        
        for pattern in exception_patterns:
            matches = re.findall(pattern, text)
            exceptions.extend(matches)
        
        # 特定类型的例外
        if evidence_type in ['GEJU_SUCCESS', 'GEJU_FAILURE']:
            exceptions.append('从格/化格可能例外')
        if evidence_type in ['DAYMASTER_STRONG', 'DAYMASTER_WEAK']:
            exceptions.append('从格/化格不适用')
        
        return list(set(exceptions))[:3] if exceptions else ['无明确例外']
    
    def process_classic(self, classic: str, evidence_dir_name: str) -> int:
        """处理单个经典"""
        evidence_dir = self.evidence_dir / evidence_dir_name
        if not evidence_dir.exists():
            print(f"警告: {evidence_dir} 不存在")
            return 0
        
        passages = self.passages.get(classic, {})
        completed = 0
        updated = 0
        
        for ev_file in evidence_dir.glob('E-*.json'):
            with open(ev_file, 'r', encoding='utf-8') as f:
                ev = json.load(f)
            
            passage_id = ev.get('source_locator', {}).get('passage_id', '')
            passage = passages.get(passage_id, {})
            
            if passage:
                # 检查是否需要更新
                needs_update = False
                if not ev.get('classical_theme'):
                    needs_update = True
                if not ev.get('conditions'):
                    needs_update = True
                if not ev.get('evidence_text', {}).get('context_before'):
                    needs_update = True
                
                if needs_update:
                    ev = self.enrich_evidence(ev, classic, passage)
                    
                    with open(ev_file, 'w', encoding='utf-8') as f:
                        json.dump(ev, f, ensure_ascii=False, indent=2)
                    
                    updated += 1
            
            completed += 1
        
        return updated


def main():
    base_dir = Path('C:/Users/wisdom/wisdom')
    classics_dir = base_dir / 'data' / 'classics' / 'original'
    evidence_dir = base_dir / 'data' / 'evidence'
    
    completer = EvidenceCompleterV2(classics_dir, evidence_dir)
    
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
        print(f"{classic}: 更新 {count} 条")
    
    # 生成报告
    report = {
        'total_updated': sum(results.values()),
        'per_classic': results,
        'timestamp': '2026-09-02',
        'version': 'v2'
    }
    
    report_dir = base_dir / 'data' / 'reports'
    report_dir.mkdir(exist_ok=True)
    
    with open(report_dir / 'completion_summary_v2.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n总计更新: {report['total_updated']} 条证据")
    print(f"报告已保存: {report_dir / 'completion_summary_v2.json'}")


if __name__ == '__main__':
    main()
