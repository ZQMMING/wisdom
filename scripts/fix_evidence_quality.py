#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五经证据质量修复脚本
修复conditions缺失和context缺失问题
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

class EvidenceFixer:
    """证据质量修复器"""
    
    def __init__(self, classics_dir: Path, evidence_dir: Path):
        self.classics_dir = classics_dir
        self.evidence_dir = evidence_dir
        self.merged_passages = {}
        self.load_passages()
    
    def load_passages(self):
        """加载合并后的原典"""
        for f in self.classics_dir.glob('*_merged.json'):
            data = json.load(open(f, 'r', encoding='utf-8'))
            prefix = f.stem.split('_')[0]
            self.merged_passages[prefix] = {p['passage_id']: p for p in data['passages']}
    
    def extract_conditions_improved(self, text: str, evidence_type: str) -> List[str]:
        """改进的条件提取"""
        conditions = []
        
        # 模式1: 条件句式
        patterns = [
            r'若(.+?)，(.+?)[。.]',
            r'有(.+?)则(.+?)[。.]',
            r'无(.+?)则(.+?)[。.]',
            r'(.+?)喜(.+?)[。.]',
            r'(.+?)忌(.+?)[。.]',
            r'(.+?)宜(.+?)[。.]',
            r'(.+?)不宜(.+?)[。.]',
            r'得(.+?)则(.+?)[。.]',
            r'失(.+?)则(.+?)[。.]',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for m in matches:
                if isinstance(m, tuple):
                    cond = '，'.join(m)
                else:
                    cond = m
                if len(cond) > 5 and len(cond) < 150:
                    conditions.append(cond.strip())
        
        # 模式2: 从文本中提取关键词组合
        keyword_patterns = [
            (r'(.{0,20})(得令|失令)(.{0,30})', '得令/失令条件'),
            (r'(.{0,20})(得地|失地)(.{0,30})', '得地/失地条件'),
            (r'(.{0,20})(旺|衰)(.{0,30})', '旺衰条件'),
        ]
        
        for pattern, desc in keyword_patterns:
            matches = re.findall(pattern, text)
            for m in matches:
                if isinstance(m, tuple):
                    full = m[0] + m[1] + m[2]
                    if len(full) > 5:
                        conditions.append(full.strip())
        
        # 去重并限制数量
        conditions = list(dict.fromkeys(conditions))[:8]
        
        return conditions
    
    def fix_context(self, ev: Dict, classic_prefix: str) -> bool:
        """修复上下文"""
        passage_id = ev.get('source_locator', {}).get('passage_id', '')
        original_text = ev.get('original_text', '')
        
        if passage_id not in self.merged_passages.get(classic_prefix, {}):
            return False
        
        passage = self.merged_passages[classic_prefix][passage_id]
        passage_text = passage.get('text', '')
        
        if not original_text or not passage_text:
            return False
        
        # 提取上下文
        if original_text in passage_text:
            idx = passage_text.find(original_text)
            window = 300
            start = max(0, idx - window)
            end = min(len(passage_text), idx + len(original_text) + window)
            
            context_before = passage_text[start:idx]
            context_after = passage_text[idx + len(original_text):end]
            
            ev['evidence_text']['context_before'] = context_before
            ev['evidence_text']['context_after'] = context_after
            return True
        
        return False
    
    def fix_evidence(self, ev: Dict, classic_prefix: str) -> Dict:
        """修复单条证据"""
        evidence_type = ev.get('evidence_type', '')
        original_text = ev.get('original_text', '')
        
        # 修复conditions
        if not ev.get('conditions'):
            ev['conditions'] = self.extract_conditions_improved(original_text, evidence_type)
        
        # 修复context
        if not ev.get('evidence_text', {}).get('context_before') and not ev.get('evidence_text', {}).get('context_after'):
            self.fix_context(ev, classic_prefix)
        
        return ev
    
    def process_classic(self, classic_key: str, prefix: str) -> Dict:
        """处理单个经典"""
        ev_dir = self.evidence_dir / classic_key
        if not ev_dir.exists():
            return {'fixed': 0, 'with_conditions': 0, 'with_context': 0}
        
        fixed = 0
        with_conditions = 0
        with_context = 0
        
        for ev_file in ev_dir.glob('E-*.json'):
            with open(ev_file, 'r', encoding='utf-8') as f:
                ev = json.load(f)
            
            needs_fix = False
            if not ev.get('conditions'):
                needs_fix = True
            et = ev.get('evidence_text', {})
            if not et.get('context_before') and not et.get('context_after'):
                needs_fix = True
            
            if needs_fix:
                ev = self.fix_evidence(ev, prefix)
                
                with open(ev_file, 'w', encoding='utf-8') as f:
                    json.dump(ev, f, ensure_ascii=False, indent=2)
                
                fixed += 1
            
            if ev.get('conditions'):
                with_conditions += 1
            if ev.get('evidence_text', {}).get('context_before') or ev.get('evidence_text', {}).get('context_after'):
                with_context += 1
        
        return {
            'fixed': fixed,
            'with_conditions': with_conditions,
            'with_context': with_context
        }


def main():
    base_dir = Path('C:/Users/wisdom/wisdom')
    classics_dir = base_dir / 'data' / 'classics' / 'original'
    evidence_dir = base_dir / 'data' / 'evidence'
    
    fixer = EvidenceFixer(classics_dir, evidence_dir)
    
    # 处理五个经典
    classics = [
        ('di_tian_sui', 'DTS'),
        ('ziping_zhenquan', 'PZZQ'),
        ('qiong_tong_bao_jian', 'QTBJ'),
        ('san_ming_tong_hui', 'SMTH'),
        ('yuan_hai_zi_ping', 'YHZP'),
    ]
    
    results = {}
    for classic_key, prefix in classics:
        result = fixer.process_classic(classic_key, prefix)
        results[classic_key] = result
        print(f"{classic_key}: 修复 {result['fixed']} 条, conditions={result['with_conditions']}, context={result['with_context']}")
    
    # 汇总
    total_fixed = sum(r['fixed'] for r in results.values())
    total_conditions = sum(r['with_conditions'] for r in results.values())
    total_context = sum(r['with_context'] for r in results.values())
    
    print(f"\n总计: 修复 {total_fixed} 条")
    print(f"conditions覆盖率: {total_conditions}/1412 ({total_conditions/1412*100:.1f}%)")
    print(f"context覆盖率: {total_context}/1412 ({total_context/1412*100:.1f}%)")


if __name__ == '__main__':
    main()
