#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五经证据conditions优化脚本
使用更智能的提取逻辑补全缺失的条件字段
"""

import json
import re
from pathlib import Path
from typing import Dict, List

class ConditionExtractor:
    """条件提取器"""
    
    # 证据类型对应的默认条件模板
    TYPE_CONDITION_TEMPLATES = {
        '101': ['三元存在时', '五行流通时'],
        '102': ['得令时', '失令时', '得地时', '失地时'],
        '103': ['人贵时', '人贱时', '中和时'],
        '104': ['顺局时', '悖局时'],
        '105': ['进气时', '退气时', '旺相时', '休囚时'],
        '106': ['水生木时', '木生火时', '火生土时', '土生金时', '金生水时'],
        '107': ['相生时', '相克时', '相侮时', '相乘时'],
        '108': ['流通无阻时', '阻滞不通时'],
        '109': ['偏枯时', '太过时', '不及时候'],
        '110': ['补救得宜时', '补救不当时候'],
        'KEY_CONCEPT': ['概念适用时', '理论阐述时'],
        'YONGSHEN_VALID': ['用神有力时', '用神护卫时'],
        'YONGSHEN_WEAK': ['用神无力时', '用神受制时'],
        'GEJU_SUCCESS': ['格局成立时', '相神得力时'],
        'GEJU_FAILURE': ['格局破损时', '相神受伤时'],
        'TIAN_GAN_SUPPORT': ['天干透出时', '干支配合时'],
        'DI_ZHI_SUPPORT': ['地支根气时', '支中藏干时'],
        'PATTERN_RESCUE': ['格局救助时', '有病得药时'],
        'TEM': ['寒暖适中时', '调候得宜时'],
        'ADJ': ['需调候时', '寒暖偏颇时'],
        'KEY_PASSAGE': ['关键论述时', '理论阐述时'],
        'JIANLU': ['建禄格成时', '月令建禄时'],
        'LU': ['日禄归时', '禄旺时'],
        'SHW': ['岁旺时', '时旺时'],
        'TIANYI': ['天乙贵人遇时', '贵人人场时'],
        'DAYMASTER_STRONG': ['日主强旺时', '印比帮身时'],
        'DAYMASTER_WEAK': ['日主衰弱时', '官杀克身时'],
        'MONTH_BRANCH_DOMINANT': ['月令主导时', '提纲有力时'],
        'TEN_GODS_BALANCE': ['十神平衡时', '喜用有力时'],
        'STRUCTURE_CLEAR': ['格局清晰时', '清纯不杂时'],
        'STRUCTURE_MIXED': ['格局混杂时', '杂气破格时'],
    }
    
    def __init__(self):
        self.patterns = [
            # 条件句式
            (r'若(.+?)，(.+?)[。.]', '若...则'),
            (r'有(.+?)则(.+?)[。.]', '有...则'),
            (r'无(.+?)则(.+?)[。.]', '无...则'),
            (r'(.+?)喜(.+?)[。.]', '喜'),
            (r'(.+?)忌(.+?)[。.]', '忌'),
            (r'(.+?)宜(.+?)[。.]', '宜'),
            (r'(.+?)不宜(.+?)[。.]', '不宜'),
            (r'得(.+?)则(.+?)[。.]', '得...则'),
            (r'失(.+?)则(.+?)[。.]', '失...则'),
            (r'当(.+?)，(.+?)[。.]', '当...'),
            (r'见(.+?)则(.+?)[。.]', '见...则'),
            (r'逢(.+?)则(.+?)[。.]', '逢...则'),
            (r'遇(.+?)则(.+?)[。.]', '遇...则'),
            (r'(.+?)方(.+?)[。.]', '方'),
            (r'(.+?)乃(.+?)[。.]', '乃'),
            (r'(.+?)斯(.+?)[。.]', '斯'),
            # 关键词
            (r'(.{0,10}得令.{0,20})', '得令'),
            (r'(.{0,10}失令.{0,20})', '失令'),
            (r'(.{0,10}得地.{0,20})', '得地'),
            (r'(.{0,10}失地.{0,20})', '失地'),
            (r'(.{0,10}旺相.{0,20})', '旺相'),
            (r'(.{0,10}休囚.{0,20})', '休囚'),
            (r'(.{0,10}长生.{0,20})', '长生'),
            (r'(.{0,10}帝旺.{0,20})', '帝旺'),
            (r'(.{0,10}墓库.{0,20})', '墓库'),
            (r'(.{0,10}通根.{0,20})', '通根'),
            (r'(.{0,10}透干.{0,20})', '透干'),
            (r'(.{0,10}藏支.{0,20})', '藏支'),
        ]
    
    def extract_conditions(self, text: str, evidence_type: str) -> List[str]:
        """提取条件"""
        conditions = []
        
        # 1. 先尝试从模板获取默认条件
        template = self.TYPE_CONDITION_TEMPLATES.get(evidence_type, [])
        if template:
            conditions.extend(template)
        
        # 2. 从文本中提取具体条件
        for pattern, desc in self.patterns:
            try:
                matches = re.findall(pattern, text)
                for m in matches:
                    if isinstance(m, tuple):
                        cond = m[0] if len(m) == 1 else '，'.join(m)
                    else:
                        cond = m
                    if len(cond) > 3 and len(cond) < 100:
                        conditions.append(cond.strip())
            except:
                pass
        
        # 3. 去重
        conditions = list(dict.fromkeys(conditions))
        
        # 4. 限制数量
        return conditions[:10]
    
    def should_use_template(self, text: str) -> bool:
        """判断是否应该使用模板条件"""
        # 如果文本很短，可能没有明确条件
        if len(text) < 30:
            return True
        # 如果文本包含明显条件句式
        if re.search(r'(若|有|无|喜|忌|宜|当|得|失)', text):
            return False
        return True
    
    def enrich_conditions(self, ev: Dict) -> Dict:
        """优化条件字段"""
        original_text = ev.get('original_text', '')
        evidence_type = ev.get('evidence_type', '')
        
        # 如果已有conditions且数量足够，不修改
        existing = ev.get('conditions', [])
        if len(existing) >= 3:
            return ev
        
        # 提取新条件
        new_conditions = self.extract_conditions(original_text, evidence_type)
        
        # 合并
        all_conditions = list(dict.fromkeys(existing + new_conditions))
        ev['conditions'] = all_conditions[:10]
        
        return ev


def main():
    evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')
    extractor = ConditionExtractor()
    
    # 统计
    stats = {'total': 0, 'updated': 0, 'with_conditions': 0}
    
    for ev_dir in evidence_dir.iterdir():
        if not ev_dir.is_dir() or ev_dir.name.startswith('_'):
            continue
        
        for ev_file in ev_dir.glob('E-*.json'):
            stats['total'] += 1
            
            with open(ev_file, 'r', encoding='utf-8') as f:
                ev = json.load(f)
            
            # 检查是否需要更新
            needs_update = False
            if not ev.get('conditions') or len(ev.get('conditions', [])) < 2:
                needs_update = True
            
            if needs_update:
                ev = extractor.enrich_conditions(ev)
                
                with open(ev_file, 'w', encoding='utf-8') as f:
                    json.dump(ev, f, ensure_ascii=False, indent=2)
                
                stats['updated'] += 1
            
            if ev.get('conditions') and len(ev['conditions']) > 0:
                stats['with_conditions'] += 1
    
    print("="*60)
    print("         Conditions优化完成")
    print("="*60)
    print(f"\n处理证据数: {stats['total']}")
    print(f"更新证据数: {stats['updated']}")
    print(f"有conditions: {stats['with_conditions']} ({stats['with_conditions']/stats['total']*100:.1f}%)")


if __name__ == '__main__':
    main()
