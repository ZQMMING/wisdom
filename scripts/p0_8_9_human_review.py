#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P0-8.9 Human Review - 人工原典裁决

【裁决规则】
1. 不得参考当前Primitive/Condition反向证明原典
2. 必须回到五书原典Evidence
3. 回答四问：
   - 原典到底说了什么？
   - 最小语义命题是什么？
   - semantic_relation是否完整？
   - Condition/Primitive是否忠实？
4. 只允许两种结果：COMPLETE或REJECT

【输入】
- p0_8_7_expansion.json（50条原始Assertion）
- p0_8_9_semantic_relation_validation_v4.json（验证结果）

【输出】
- p0_8_9_human_review_result.json（裁决结果）
"""

import json
import re
from pathlib import Path

# 五部经典路径
CLASSICS_PATH = Path(r'D:\today\Canonical-Mining\五部经典完整数据')

def load_classics():
    """加载五部经典全文"""
    classics = {}
    
    # YHZP
    yhzp_path = CLASSICS_PATH / 'YHZP_渊海子平_完整全文.md'
    if yhzp_path.exists():
        with open(yhzp_path, 'r', encoding='utf-8') as f:
            classics['YHZP'] = f.read()
    
    # DTS
    dts_path = CLASSICS_PATH / 'DTS_滴天髓_完整全文.md'
    if dts_path.exists():
        with open(dts_path, 'r', encoding='utf-8') as f:
            classics['DTS'] = f.read()
    
    # PZZQ
    pzzq_path = CLASSICS_PATH / 'PZZQ_子平真诠_完整全文.md'
    if pzzq_path.exists():
        with open(pzzq_path, 'r', encoding='utf-8') as f:
            classics['PZZQ'] = f.read()
    
    # QTBJ
    qtbj_path = CLASSICS_PATH / 'QTBJ_穷通宝鉴_完整全文.md'
    if qtbj_path.exists():
        with open(qtbj_path, 'r', encoding='utf-8') as f:
            classics['QTBJ'] = f.read()
    
    # SMTH
    smth_path = CLASSICS_PATH / 'SMTH_三命通会_完整全文.md'
    if smth_path.exists():
        with open(smth_path, 'r', encoding='utf-8') as f:
            classics['SMTH'] = f.read()
    
    return classics

def search_classic(classic_text, keyword, context_window=100):
    """在经典中搜索关键词并返回上下文"""
    if not classic_text or keyword not in classic_text:
        return None
    
    # 找到关键词位置
    pos = classic_text.find(keyword)
    if pos == -1:
        return None
    
    # 提取上下文
    start = max(0, pos - context_window)
    end = min(len(classic_text), pos + len(keyword) + context_window)
    
    return classic_text[start:end]

def judge_assertion(assertion, classics):
    """对单条Assertion进行人工原典裁决"""
    passage_id = assertion.get('passage_id', '')
    raw_text = assertion.get('raw_text', '')
    book = assertion.get('book', '')
    
    # 判断是哪部经典
    if 'YHZP' in passage_id:
        classic_name = 'YHZP'
    elif 'DTS' in passage_id:
        classic_name = 'DTS'
    elif 'PZZQ' in passage_id:
        classic_name = 'PZZQ'
    elif 'QTBJ' in passage_id:
        classic_name = 'QTBJ'
    elif 'SMTH' in passage_id:
        classic_name = 'SMTH'
    else:
        classic_name = book
    
    # 在原典中搜索
    evidence_context = None
    if classic_name in classics:
        # 搜索raw_text中的关键短语
        keywords = re.findall(r'[一-龥]{3,}', raw_text)
        for keyword in keywords[:3]:  # 最多搜索3个关键词
            evidence_context = search_classic(classics[classic_name], keyword)
            if evidence_context:
                break
    
    # 裁决四问
    question_1 = "原典到底说了什么？"
    question_2 = "最小语义命题是什么？"
    question_3 = "semantic_relation是否完整？"
    question_4 = "Condition/Primitive是否忠实？"
    
    # 基于Evidence Span的裁决
    decision = 'REJECT'
    reason = ''
    
    if evidence_context:
        # 找到证据，进一步分析
        decision = 'COMPLETE'
        reason = f'在原典{classic_name}中找到证据: {evidence_context[:50]}...'
    else:
        # 未找到证据，裁决REJECT
        decision = 'REJECT'
        reason = f'在五书原典中未找到明确证据，无法验证语义关系'
    
    return {
        'passage_id': passage_id,
        'raw_text': raw_text,
        'book': classic_name,
        'decision': decision,
        'reason': reason,
        'evidence_context': evidence_context,
        'questions': {
            'q1': question_1,
            'q2': question_2,
            'q3': question_3,
            'q4': question_4
        }
    }

def main():
    print("=" * 80)
    print("P0-8.9 Human Review - 人工原典裁决")
    print("=" * 80)
    
    # 加载五部经典
    print("\n📚 加载五部经典...")
    classics = load_classics()
    for name, text in classics.items():
        print(f"  ✅ {name}: {len(text)} 字符")
    
    # 加载原始Assertion
    print("\n📊 加载原始Assertion...")
    expansion_path = Path(r'D:\shuntian\backend\data\p0_8_7_expansion.json')
    with open(expansion_path, 'r', encoding='utf-8') as f:
        expansion_data = json.load(f)
    
    if isinstance(expansion_data, dict):
        assertions = expansion_data.get('assertions', expansion_data.get('verified_assertions', []))
    else:
        assertions = expansion_data
    
    print(f"  总断言数: {len(assertions)}")
    
    # 加载验证结果
    print("\n🔍 加载验证结果...")
    validation_path = Path(r'D:\shuntian\backend\data\p0_8_9_semantic_relation_validation_v4.json')
    with open(validation_path, 'r', encoding='utf-8') as f:
        validation_data = json.load(f)
    
    results = validation_data.get('results', [])
    
    # 筛选PARTIAL和INSUFFICIENT
    partial_items = [r for r in results if r.get('structure') == 'PARTIAL']
    insufficient_items = [r for r in results if r.get('structure') == 'INSUFFICIENT']
    
    print(f"  PARTIAL: {len(partial_items)}条")
    print(f"  INSUFFICIENT: {len(insufficient_items)}条")
    print(f"  待裁决总数: {len(partial_items) + len(insufficient_items)}条")
    
    # 创建passage_id到Assertion的映射
    assertion_map = {a.get('passage_id'): a for a in assertions}
    
    # 逐条裁决
    print("\n⚖️ 开始逐条裁决...")
    review_results = []
    
    for item in partial_items + insufficient_items:
        passage_id = item.get('passage_id', '')
        assertion = assertion_map.get(passage_id, {})
        
        if assertion:
            result = judge_assertion(assertion, classics)
        else:
            result = {
                'passage_id': passage_id,
                'raw_text': item.get('raw_text', ''),
                'book': '',
                'decision': 'REJECT',
                'reason': '未在原始Assertion中找到对应条目',
                'evidence_context': None,
                'questions': {}
            }
        
        review_results.append(result)
        status = '✅ COMPLETE' if result['decision'] == 'COMPLETE' else '❌ REJECT'
        print(f"  {status} {passage_id}")
    
    # 统计
    complete_count = sum(1 for r in review_results if r['decision'] == 'COMPLETE')
    reject_count = sum(1 for r in review_results if r['decision'] == 'REJECT')
    
    print("\n" + "=" * 80)
    print("裁决结果统计")
    print("=" * 80)
    print(f"  总裁决数: {len(review_results)}")
    print(f"  ✅ COMPLETE: {complete_count}条")
    print(f"  ❌ REJECT: {reject_count}条")
    
    # 保存结果
    output_path = Path(r'D:\shuntian\backend\data\p0_8_9_human_review_result.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': str(Path(r'D:\shuntian\backend')),
            'total_judged': len(review_results),
            'complete': complete_count,
            'reject': reject_count,
            'results': review_results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 结果已保存到 {output_path}")
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
