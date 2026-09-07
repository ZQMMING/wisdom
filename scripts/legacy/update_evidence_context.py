#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新证据指向合并后的passage并重新提取context
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import re

class EvidenceUpdater:
    """证据更新器"""
    
    def __init__(self, classics_dir: Path, evidence_dir: Path):
        self.classics_dir = classics_dir
        self.evidence_dir = evidence_dir
        self.original_passages = {}
        self.merged_passages = {}
        self.id_mapping = {}
        self.load_data()
    
    def load_data(self):
        """加载原典数据"""
        # 加载原始passages
        for f in self.classics_dir.glob('*段落数据.json'):
            data = json.load(open(f, 'r', encoding='utf-8'))
            prefix = f.stem.split('_')[0]
            self.original_passages[prefix] = {p['passage_id']: p for p in data['passages']}
        
        # 加载合并后的passages
        for f in self.classics_dir.glob('*_merged.json'):
            data = json.load(open(f, 'r', encoding='utf-8'))
            prefix = f.stem.split('_')[0]
            self.merged_passages[prefix] = {p['passage_id']: p for p in data['passages']}
        
        # 构建ID映射
        self.build_id_mapping()
    
    def build_id_mapping(self):
        """构建原ID到合并ID的映射"""
        for prefix, orig_map in self.original_passages.items():
            if prefix not in self.merged_passages:
                continue
            merged_map = self.merged_passages[prefix]
            
            for orig_id, orig_passage in orig_map.items():
                orig_text = orig_passage['text']
                for merged_id, merged_passage in merged_map.items():
                    if orig_text in merged_passage['text']:
                        if orig_id not in self.id_mapping:
                            self.id_mapping[orig_id] = {
                                'original': orig_id,
                                'merged': merged_id,
                                'classic': prefix
                            }
                        break
    
    def extract_context(self, passage_text: str, evidence_text: str, window: int = 300) -> Tuple[str, str]:
        """提取上下文"""
        if not evidence_text or not passage_text:
            return '', ''
        
        # 精确匹配
        if evidence_text in passage_text:
            idx = passage_text.find(evidence_text)
            start = max(0, idx - window)
            end = min(len(passage_text), idx + len(evidence_text) + window)
            
            context_before = passage_text[start:idx]
            context_after = passage_text[idx + len(evidence_text):end]
            
            return context_before, context_after
        
        # 模糊匹配
        short_text = evidence_text[:100] if len(evidence_text) > 100 else evidence_text
        if short_text in passage_text:
            idx = passage_text.find(short_text)
            start = max(0, idx - window)
            context_before = passage_text[start:idx]
            context_after = passage_text[idx + len(short_text):idx + len(short_text) + window]
            return context_before, context_after
        
        # 句子分割匹配
        sentences = re.split(r'[。！？]', passage_text)
        for i, s in enumerate(sentences):
            if evidence_text[:50] in s or s[:50] in evidence_text:
                before = '。'.join(sentences[max(0,i-2):i])
                after = '。'.join(sentences[i+1:min(len(sentences),i+3)])
                return before, after
        
        return '', ''
    
    def update_evidence(self, ev: Dict, classic: str, merged_passage: Dict) -> Dict:
        """更新单条证据"""
        # 更新passage_id
        original_id = ev.get('source_locator', {}).get('passage_id', '')
        if original_id in self.id_mapping and self.id_mapping[original_id]['classic'] == classic:
            ev['source_locator']['passage_id'] = self.id_mapping[original_id]['merged']
        
        # 提取上下文
        passage_text = merged_passage.get('text', '')
        original_text = ev.get('original_text', '')
        
        context_before, context_after = self.extract_context(passage_text, original_text)
        ev['evidence_text']['context_before'] = context_before
        ev['evidence_text']['context_after'] = context_after
        
        return ev
    
    def process_classic(self, classic_key: str, evidence_dir_name: str) -> Dict:
        """处理单个经典"""
        ev_dir = self.evidence_dir / evidence_dir_name
        if not ev_dir.exists():
            return {'updated': 0, 'with_context': 0}
        
        # 获取前缀
        prefix_map = {
            'di_tian_sui': 'DTS',
            'ziping_zhenquan': 'PZZQ',
            'qiong_tong_bao_jian': 'QTBJ',
            'san_ming_tong_hui': 'SMTH',
            'yuan_hai_zi_ping': 'YHZP'
        }
        prefix = prefix_map.get(classic_key, classic_key.upper())
        
        merged_map = self.merged_passages.get(prefix, {})
        
        updated = 0
        with_context = 0
        
        for ev_file in ev_dir.glob('E-*.json'):
            with open(ev_file, 'r', encoding='utf-8') as f:
                ev = json.load(f)
            
            passage_id = ev.get('source_locator', {}).get('passage_id', '')
            
            # 找到对应的合并后passage
            merged_passage = None
            if passage_id in merged_map:
                merged_passage = merged_map[passage_id]
            else:
                # 尝试在id_mapping中找
                if passage_id in self.id_mapping:
                    new_id = self.id_mapping[passage_id]['merged']
                    if new_id in merged_map:
                        merged_passage = merged_map[new_id]
                        ev['source_locator']['passage_id'] = new_id
            
            if merged_passage:
                ev = self.update_evidence(ev, prefix, merged_passage)
                
                with open(ev_file, 'w', encoding='utf-8') as f:
                    json.dump(ev, f, ensure_ascii=False, indent=2)
                
                updated += 1
                
                et = ev.get('evidence_text', {})
                if et.get('context_before') or et.get('context_after'):
                    with_context += 1
        
        return {'updated': updated, 'with_context': with_context}


def main():
    base_dir = Path('C:/Users/wisdom/wisdom')
    classics_dir = base_dir / 'data' / 'classics' / 'original'
    evidence_dir = base_dir / 'data' / 'evidence'
    
    updater = EvidenceUpdater(classics_dir, evidence_dir)
    
    # 处理五个经典
    classics = [
        ('di_tian_sui', 'di_tian_sui'),
        ('ziping_zhenquan', 'ziping_zhenquan'),
        ('qiong_tong_bao_jian', 'qiong_tong_bao_jian'),
        ('san_ming_tong_hui', 'san_ming_tong_hui'),
        ('yuan_hai_zi_ping', 'yuan_hai_zi_ping'),
    ]
    
    results = {}
    for classic_key, dir_name in classics:
        result = updater.process_classic(classic_key, dir_name)
        results[classic_key] = result
        print(f"{classic_key}: 更新 {result['updated']} 条, 有context {result['with_context']} 条")
    
    # 汇总
    total_updated = sum(r['updated'] for r in results.values())
    total_with_context = sum(r['with_context'] for r in results.values())
    
    print(f"\n总计: 更新 {total_updated} 条, 有context {total_with_context} 条")
    print(f"Context覆盖率: {total_with_context/total_updated*100:.1f}%" if total_updated > 0 else "N/A")


if __name__ == '__main__':
    main()
