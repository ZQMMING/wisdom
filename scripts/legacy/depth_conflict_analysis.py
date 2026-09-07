#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五经证据多维度冲突分析脚本
从理论、实践、条件三个维度深度分析冲突
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
import re

def load_evidence():
    """加载所有证据"""
    evidence_dir = Path('C:/Users/wisdom/wisdom/data/evidence')
    classics = {}
    
    for ev_dir in evidence_dir.iterdir():
        if not ev_dir.is_dir() or ev_dir.name.startswith('_'):
            continue
        
        classic_name = ev_dir.name
        classics[classic_name] = []
        
        for ev_file in ev_dir.glob('E-*.json'):
            ev = json.load(open(ev_file, 'r', encoding='utf-8'))
            classics[classic_name].append(ev)
    
    return classics

def analyze_dts_qtbj_conflict(classics):
    """分析DTS vs QTBJ的旺衰vs调候冲突"""
    dts = classics.get('di_tian_sui', [])
    qtbj = classics.get('qiong_tong_bao_jian', [])
    
    # 提取DTS关于旺衰的论述
    dts_wangshuai_texts = []
    dts_tiaohou_texts = []
    
    # 提取QTBJ关于调候的论述
    qtbj_tiaohou_texts = []
    qtbj_wangshuai_texts = []
    
    for ev in dts:
        content = ev.get('content', '')
        source_text = ev.get('source_text', '')
        full_text = content + ' ' + source_text
        
        # DTS关于旺衰的论述
        if any(kw in full_text for kw in ['衰旺', '旺衰', '日主', '得令', '失令', '得地', '失地']):
            dts_wangshuai_texts.append(full_text[:300])
        
        # DTS关于调候的论述
        if any(kw in full_text for kw in ['调候', '寒暖', '季节', '气候']):
            dts_tiaohou_texts.append(full_text[:300])
    
    for ev in qtbj:
        content = ev.get('content', '')
        source_text = ev.get('source_text', '')
        full_text = content + ' ' + source_text
        
        # QTBJ关于调候的论述
        if any(kw in full_text for kw in ['调候', '寒暖', '需水', '需火', '喜水', '喜火']):
            qtbj_tiaohou_texts.append(full_text[:300])
        
        # QTBJ关于旺衰的论述
        if any(kw in full_text for kw in ['旺', '弱', '强', '衰']):
            qtbj_wangshuai_texts.append(full_text[:300])
    
    return {
        'dts_wangshuai': dts_wangshuai_texts,
        'dts_tiaohou': dts_tiaohou_texts,
        'qtbj_tiaohou': qtbj_tiaohou_texts,
        'qtbj_wangshuai': qtbj_wangshuai_texts
    }

def analyze_pzzq_yhzp_conflict(classics):
    """分析PZZQ vs YHZP的用神标准冲突"""
    pzzq = classics.get('ziping_zhenquan', [])
    yhzp = classics.get('yuan_hai_zi_ping', [])
    
    # 提取PZZQ关于用神的论述
    pzzq_yongshen_texts = []
    pzzq_geju_texts = []
    
    # 提取YHZP关于格局的论述
    yhzp_geju_texts = []
    yhzp_rizhu_texts = []
    
    for ev in pzzq:
        content = ev.get('content', '')
        source_text = ev.get('source_text', '')
        full_text = content + ' ' + source_text
        
        # PZZQ关于用神的论述
        if any(kw in full_text for kw in ['用神', '月令', '专求']):
            pzzq_yongshen_texts.append(full_text[:300])
        
        # PZZQ关于格局的论述
        if any(kw in full_text for kw in ['格局', '成败', '相神']):
            pzzq_geju_texts.append(full_text[:300])
    
    for ev in yhzp:
        content = ev.get('content', '')
        source_text = ev.get('source_text', '')
        full_text = content + ' ' + source_text
        
        # YHZP关于格局的论述
        if any(kw in full_text for kw in ['格局', '清浊', '混杂']):
            yhzp_geju_texts.append(full_text[:300])
        
        # YHZP关于日主的论述
        if any(kw in full_text for kw in ['身旺', '身弱', '日主', '强弱']):
            yhzp_rizhu_texts.append(full_text[:300])
    
    return {
        'pzzq_yongshen': pzzq_yongshen_texts,
        'pzzq_geju': pzzq_geju_texts,
        'yhzp_geju': yhzp_geju_texts,
        'yhzp_rizhu': yhzp_rizhu_texts
    }

def analyze_dts_pzzq_conflict(classics):
    """分析DTS vs PZZQ的方法论冲突"""
    dts = classics.get('di_tian_sui', [])
    pzzq = classics.get('ziping_zhenquan', [])
    
    # 提取DTS批判的论述
    dts_critique_texts = []
    
    # 提取PZZQ精细化的论述
    pzzq_fine_texts = []
    
    for ev in dts:
        content = ev.get('content', '')
        source_text = ev.get('source_text', '')
        full_text = content + ' ' + source_text
        
        # DTS关于批判奇格异局的论述
        if any(kw in full_text for kw in ['奇格', '异局', '神杀', '荒唐', '谬书']):
            dts_critique_texts.append(full_text[:400])
        
        # DTS关于回归本质的论述
        if any(kw in full_text for kw in ['用神', '本质', '根本']):
            dts_critique_texts.append(full_text[:400])
    
    for ev in pzzq:
        content = ev.get('content', '')
        source_text = ev.get('source_text', '')
        full_text = content + ' ' + source_text
        
        # PZZQ关于精细化的论述
        if any(kw in full_text for kw in ['成败', '救应', '相神', '配成']):
            pzzq_fine_texts.append(full_text[:400])
    
    return {
        'dts_critique': dts_critique_texts,
        'pzzq_fine': pzzq_fine_texts
    }

def main():
    print("=== 五经证据多维度冲突分析 ===\n")
    
    classics = load_evidence()
    
    # 1. DTS vs QTBJ: 旺衰 vs 调候
    print("\n" + "="*60)
    print("【冲突1】旺衰优先 vs 调候优先 (DTS vs QTBJ)")
    print("="*60)
    
    conflict1 = analyze_dts_qtbj_conflict(classics)
    print(f"\nDTS旺衰论述: {len(conflict1['dts_wangshuai'])}条")
    print(f"DTS调候论述: {len(conflict1['dts_tiaohou'])}条")
    print(f"QTBJ调候论述: {len(conflict1['qtbj_tiaohou'])}条")
    print(f"QTBJ旺衰论述: {len(conflict1['qtbj_wangshuai'])}条")
    
    # 2. PZZQ vs YHZP: 用神标准
    print("\n" + "="*60)
    print("【冲突2】取用神标准差异 (PZZQ vs YHZP)")
    print("="*60)
    
    conflict2 = analyze_pzzq_yhzp_conflict(classics)
    print(f"\nPZZQ用神论述: {len(conflict2['pzzq_yongshen'])}条")
    print(f"PZZQ格局论述: {len(conflict2['pzzq_geju'])}条")
    print(f"YHZP格局论述: {len(conflict2['yhzp_geju'])}条")
    print(f"YHZP日主论述: {len(conflict2['yhzp_rizhu'])}条")
    
    # 3. DTS vs PZZQ: 方法论
    print("\n" + "="*60)
    print("【冲突3】方法论分歧: 简化 vs 精细 (DTS vs PZZQ)")
    print("="*60)
    
    conflict3 = analyze_dts_pzzq_conflict(classics)
    print(f"\nDTS批判论述: {len(conflict3['dts_critique'])}条")
    print(f"PZZQ精细化论述: {len(conflict3['pzzq_fine'])}条")
    
    # 输出关键原文
    print("\n" + "="*60)
    print("【关键原文摘录】")
    print("="*60)
    
    print("\n--- DTS关于旺衰的核心论述 ---")
    for text in conflict1['dts_wangshuai'][:3]:
        print(f"  {text[:200]}...")
        print()
    
    print("\n--- QTBJ关于调候的核心论述 ---")
    for text in conflict1['qtbj_tiaohou'][:3]:
        print(f"  {text[:200]}...")
        print()
    
    print("\n--- PZZQ关于用神的核心论述 ---")
    for text in conflict2['pzzq_yongshen'][:3]:
        print(f"  {text[:200]}...")
        print()
    
    print("\n--- YHZP关于日主的核心论述 ---")
    for text in conflict2['yhzp_rizhu'][:3]:
        print(f"  {text[:200]}...")
        print()
    
    print("\n--- DTS关于批判的核心论述 ---")
    for text in conflict3['dts_critique'][:3]:
        print(f"  {text[:200]}...")
        print()
    
    print("\n--- PZZQ关于精细化的核心论述 ---")
    for text in conflict3['pzzq_fine'][:3]:
        print(f"  {text[:200]}...")
        print()

if __name__ == '__main__':
    main()
