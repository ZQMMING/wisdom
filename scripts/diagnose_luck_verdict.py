#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""断语切片诊断脚本 - 统计luck_verdict可判率和失败原因分布

复用dayun_align.py的案例加载逻辑，直接从DTS原文解析案例。
"""

import re
import json
import sys
from collections import Counter

sys.path.insert(0, '.')
from scripts.dayun_align import luck_verdict, cases, GZ

def diagnose_all():
    """诊断所有案例的断语切片情况"""
    total_dayun = 0
    judgable = 0
    no_hit = 0
    no_ji_xiong = 0
    hun = 0
    lao = 0
    yuanzhu = 0

    no_hit_examples = []
    no_ji_xiong_examples = []

    for li, fp, dy, txt in cases:
        for gz in dy:
            if len(gz) < 2:
                continue
            g, z = gz[0], gz[1]
            total_dayun += 1
            v, blob = luck_verdict(txt, g, z)

            # 检查是否【原注】开头
            is_yuanzhu = bool(blob and blob.lstrip().startswith('【原注】'))

            if is_yuanzhu:
                yuanzhu += 1
            elif v in ('ji', 'xiong'):
                judgable += 1
            elif v == 'hun':
                hun += 1
            elif v == 'lao':
                lao += 1
            elif v is None and blob:
                no_ji_xiong += 1
                if len(no_ji_xiong_examples) < 10:
                    no_ji_xiong_examples.append({
                        'li': li, 'dayun': gz, 'blob': blob[:100]
                    })
            else:
                no_hit += 1
                if len(no_hit_examples) < 10:
                    no_hit_examples.append({
                        'li': li, 'dayun': gz, 'txt_sample': txt[:100]
                    })

    return {
        'total_cases': len(cases),
        'total_dayun': total_dayun,
        'judgable': judgable,
        'judgable_rate': f'{judgable/total_dayun*100:.1f}%',
        'no_hit': no_hit,
        'no_hit_rate': f'{no_hit/total_dayun*100:.1f}%',
        'no_ji_xiong': no_ji_xiong,
        'no_ji_xiong_rate': f'{no_ji_xiong/total_dayun*100:.1f}%',
        'hun': hun,
        'lao': lao,
        'yuanzhu': yuanzhu,
        'no_hit_examples': no_hit_examples,
        'no_ji_xiong_examples': no_ji_xiong_examples
    }

def analyze_context_window():
    """分析上下文窗口问题: 原局评价被误判为大运断语"""
    issues = []
    yuanju_words = ['身弱', '身旺', '身衰', '身强', '日元', '日主', '命局', '原局', '四柱', '八字', '格局']

    for li, fp, dy, txt in cases[:80]:
        for gz in dy[:3]:
            if len(gz) < 2:
                continue
            g, z = gz[0], gz[1]
            v, blob = luck_verdict(txt, g, z)
            if v in ('ji', 'xiong') and blob:
                has_yuanju = any(w in blob for w in yuanju_words)
                if has_yuanju:
                    issues.append({
                        'li': li, 'dayun': gz, 'verdict': v,
                        'blob': blob[:120]
                    })
    return issues

def analyze_semantic_role():
    """分析语义角色问题: "X衰极"指其他五行被误判为日主"""
    issues = []
    pattern = r'[金木水火土比劫印星食伤财官杀][衰极旺弱]+'

    for li, fp, dy, txt in cases[:80]:
        for gz in dy[:3]:
            if len(gz) < 2:
                continue
            g, z = gz[0], gz[1]
            v, blob = luck_verdict(txt, g, z)
            if v in ('ji', 'xiong') and blob:
                matches = re.findall(pattern, blob)
                if matches:
                    issues.append({
                        'li': li, 'dayun': gz, 'verdict': v,
                        'matches': matches, 'blob': blob[:120]
                    })
    return issues

def analyze_format_coverage():
    """分析格式覆盖问题: 哪些大运格式未被luck_verdict匹配"""
    # 统计原文中出现的大运相关格式
    formats = Counter()
    for li, fp, dy, txt in cases:
        # 查找"X运"格式
        for m in re.finditer(r'[甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥]运', txt):
            formats[m.group()] += 1
        # 查找"一交X"格式
        for m in re.finditer(r'一交[甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥]', txt):
            formats['一交X'] += 1
        # 查找"至X运"格式
        for m in re.finditer(r'至[甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥]+运', txt):
            formats['至X运'] += 1

    return formats.most_common(20)

def main():
    print('=== 断语切片诊断 ===\n')

    # 整体诊断
    result = diagnose_all()
    print(f'总案例数: {result["total_cases"]}')
    print(f'总大运数: {result["total_dayun"]}')
    print(f'可判: {result["judgable"]} ({result["judgable_rate"]})')
    print(f'无匹配: {result["no_hit"]} ({result["no_hit_rate"]})')
    print(f'匹配无吉凶: {result["no_ji_xiong"]} ({result["no_ji_xiong_rate"]})')
    print(f'吉凶混合: {result["hun"]}')
    print(f'寿元/归隐: {result["lao"]}')
    print(f'【原注】泛论: {result["yuanzhu"]}')

    # 无匹配示例
    print('\n=== 无匹配示例（前10）===')
    for ex in result['no_hit_examples']:
        print(f"  L{ex['li']} {ex['dayun']}: {ex['txt_sample'][:60]}")

    # 匹配无吉凶示例
    print('\n=== 匹配无吉凶示例（前10）===')
    for ex in result['no_ji_xiong_examples']:
        print(f"  L{ex['li']} {ex['dayun']}: {ex['blob'][:80]}")

    # 上下文窗口问题
    print('\n=== 上下文窗口问题（抽样80例）===')
    ctx_issues = analyze_context_window()
    print(f'发现原局评价混入大运断语: {len(ctx_issues)}例')
    for issue in ctx_issues[:5]:
        print(f"  L{issue['li']} {issue['dayun']}({issue['verdict']}): {issue['blob'][:80]}")

    # 语义角色问题
    print('\n=== 语义角色问题（抽样80例）===')
    sem_issues = analyze_semantic_role()
    print(f'发现"X衰极"等非日主描述: {len(sem_issues)}例')
    for issue in sem_issues[:5]:
        print(f"  L{issue['li']} {issue['dayun']}({issue['verdict']}): {issue['matches']} -> {issue['blob'][:80]}")

    # 格式覆盖
    print('\n=== 原文大运格式统计（前20）===')
    formats = analyze_format_coverage()
    for fmt, cnt in formats:
        print(f'  {fmt}: {cnt}')

    # 保存结果
    output = {
        'summary': {k: v for k, v in result.items() if 'examples' not in k},
        'context_window_issues': len(ctx_issues),
        'semantic_role_issues': len(sem_issues),
        'top_formats': formats
    }
    with open('luck_verdict_diagnosis.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print('\n诊断结果已保存到 luck_verdict_diagnosis.json')

if __name__ == '__main__':
    main()
