#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五经证据passage合并脚本
将短passage（<200字符）合并到相邻段落，形成有意义的上下文块
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import copy

class PassageMerger:
    """Passage合并器"""
    
    def __init__(self, classics_dir: Path):
        self.classics_dir = classics_dir
        self.min_length = 200  # 最短passage长度阈值
    
    def merge_short_passages(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """合并短passage"""
        passages = data['passages']
        if not passages:
            return data
        
        # 分组：找到需要合并的短passage
        merged_passages = []
        i = 0
        
        while i < len(passages):
            passage = passages[i]
            text = passage.get('text', '')
            
            # 如果当前passage够长，直接保留
            if len(text) >= self.min_length:
                merged_passages.append(passage)
                i += 1
                continue
            
            # 如果当前passage太短，尝试向后合并
            merged_text = text
            merged_source = passage.get('source', '')
            merged_passage_ids = [passage['passage_id']]
            
            # 向后合并最多2个短passage
            j = i + 1
            while j < len(passages) and len(merged_text) < self.min_length and j - i < 3:
                next_passage = passages[j]
                next_text = next_passage.get('text', '')
                
                # 添加分隔符
                if merged_text and next_text:
                    merged_text += '\n\n'
                
                merged_text += next_text
                merged_source = f"{merged_source}+{next_passage.get('source', '')}"
                merged_passage_ids.append(next_passage['passage_id'])
                j += 1
            
            # 创建合并后的passage
            merged_passage = {
                'passage_id': passage['passage_id'],  # 保留第一个ID
                'text': merged_text,
                'source': merged_source,
                'char_count': len(merged_text),
                'merged_from': merged_passage_ids,  # 记录合并来源
                'original_count': j - i  # 记录合并了几个
            }
            
            merged_passages.append(merged_passage)
            i = j  # 跳过已合并的passage
        
        data['passages'] = merged_passages
        data['total_passages'] = len(merged_passages)
        
        # 更新统计
        lengths = [len(p['text']) for p in merged_passages]
        data['length_stats'] = {
            'min': min(lengths),
            'max': max(lengths),
            'avg': sum(lengths) / len(lengths),
            'short_count': sum(1 for l in lengths if l < self.min_length)
        }
        
        return data
    
    def process_classic(self, classic_name: str) -> Dict[str, Any]:
        """处理单个经典"""
        # 查找原典文件
        files = list(self.classics_dir.glob(f'*{classic_name}*段落数据.json'))
        if not files:
            # 尝试模糊匹配
            for f in self.classics_dir.glob('*段落数据.json'):
                if classic_name in f.name or f.name.replace('_段落数据.json', '') in classic_name:
                    files.append(f)
                    break
        
        if not files:
            print(f"警告: 未找到 {classic_name} 的原典文件")
            return {}
        
        source_file = files[0]
        print(f"\n处理: {source_file.name}")
        
        # 加载数据
        with open(source_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 记录合并前状态
        before_count = len(data['passages'])
        before_short = sum(1 for p in data['passages'] if len(p.get('text', '')) < self.min_length)
        
        # 合并
        merged_data = self.merge_short_passages(copy.deepcopy(data))
        
        # 记录合并后状态
        after_count = len(merged_data['passages'])
        after_short = merged_data.get('length_stats', {}).get('short_count', 0)
        
        # 保存（写到临时文件）
        output_file = source_file.parent / f"{source_file.stem}_merged.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
        print(f"  合并前: {before_count} passages, {before_short} 短段落")
        print(f"  合并后: {after_count} passages, {after_short} 短段落")
        print(f"  输出: {output_file.name}")
        
        return merged_data


def main():
    base_dir = Path('C:/Users/wisdom/wisdom')
    classics_dir = base_dir / 'data' / 'classics' / 'original'
    
    merger = PassageMerger(classics_dir)
    
    # 处理五个经典
    classics = ['滴天髓', '子平真诠', '穷通宝鉴', '三命通会', '渊海子平']
    
    for classic in classics:
        result = merger.process_classic(classic)
        if result:
            print(f"  ✓ 完成")
    
    print("\n\n合并完成！")
    print("注意：合并后的文件保存在 *_merged.json，需要手动验证后替换原文件")


if __name__ == '__main__':
    main()
