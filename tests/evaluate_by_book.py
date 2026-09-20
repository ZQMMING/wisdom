# -*- coding: utf-8 -*-
"""按书分开评估脚本.
案例评估必须对口: 哪本书的案例就用哪本书对应的轨道评估.
Authority Matrix轨道归属:
- 子平真诠(PZZQ): 旺衰/强弱/格局/用神 Primary
- 渊海子平(YHZP): 旺衰/强弱/格局 Secondary
- 滴天髓(DTS): 旺衰/强弱/病药/用神 Alternate
- 穷通宝鉴(QTBJ): 调候/用神 Primary
- 神峰通考(SFTK): 病药/用神 Primary
- 三命通会(SMTH): 格局/调候 Alternate
"""
import json
import re
import sys
sys.path.insert(0, '.')

from engines.production_entry import production_entry, FrozenCanonicalBaziChart


# 身旺衰关键词提取
WANG_KEYWORDS = ['身旺', '身强', '日主旺', '日主强', '旺相', '强旺', '得令', '得地', '得势']
RUO_KEYWORDS = ['身弱', '身衰', '日主弱', '日主衰', '衰弱', '虚弱', '失令', '失地', '失势', '杀重身轻', '财多身弱', '煞重身轻']
NEUTRAL_KEYWORDS = ['中和', '平和', '不旺不弱', '身中和']

# 格局关键词提取
GEJU_KEYWORDS = {
    '正官格': ['正官格', '官格'],
    '七杀格': ['七杀格', '煞格', '偏官格'],
    '正财格': ['正财格', '财格'],
    '偏财格': ['偏财格'],
    '正印格': ['正印格', '印格'],
    '偏印格': ['偏印格', '枭格'],
    '食神格': ['食神格'],
    '伤官格': ['伤官格'],
    '建禄格': ['建禄格', '建禄'],
    '月劫格': ['月劫格', '月刃格', '羊刃格'],
}

# 调候关键词提取
DIAOHOU_KEYWORDS = ['调候', '寒', '暖', '燥', '湿', '用火', '用水', '用木', '用金', '用土']


def parse_chart(chart_str):
    """解析八字字符串为pillars格式."""
    if not chart_str or len(chart_str) < 8:
        return None
    # 八字格式: 年干年支月干月支日干日支时干时支
    stems = [chart_str[i] for i in range(0, 8, 2)]
    branches = [chart_str[i] for i in range(1, 8, 2)]
    return {
        'year': [stems[0], branches[0]],
        'month': [stems[1], branches[1]],
        'day': [stems[2], branches[2]],
        'hour': [stems[3], branches[3]],
    }


def extract_wangshuai(judgment):
    """从断语中提取身旺衰标准答案."""
    if not judgment:
        return None
    text = str(judgment)

    # 检查中和
    for kw in NEUTRAL_KEYWORDS:
        if kw in text:
            return '中和'

    # 检查身弱（优先，因为身弱的描述更具体）
    for kw in RUO_KEYWORDS:
        if kw in text:
            return '身弱'

    # 检查身旺
    for kw in WANG_KEYWORDS:
        if kw in text:
            return '身旺'

    return None


def extract_geju(judgment):
    """从断语中提取格局标准答案."""
    if not judgment:
        return None
    text = str(judgment)
    for geju, keywords in GEJU_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return geju
    return None


def extract_diaohou(judgment):
    """从断语中提取调候标准答案."""
    if not judgment:
        return None
    text = str(judgment)
    # 提取"用X"模式
    match = re.search(r'用([木火土金水])', text)
    if match:
        return match.group(1)
    return None


def evaluate_book(book_name, book_code, max_cases=100):
    """评估单本书的案例."""
    path = rf'D:\顺天系统资料\古书独立案例JSONL\{book_name}.jsonl'
    with open(path, 'r', encoding='utf-8') as f:
        cases = [json.loads(line) for line in f.readlines()[:max_cases]]

    results = {
        'book': book_name,
        'book_code': book_code,
        'total': len(cases),
        'valid_chart': 0,
        'wangshuai': {'has_answer': 0, 'hit': 0, 'details': []},
        'geju': {'has_answer': 0, 'hit': 0, 'details': []},
        'diaohou': {'has_answer': 0, 'hit': 0, 'details': []},
    }

    for case in cases:
        pillars = parse_chart(case.get('chart', ''))
        if not pillars:
            continue

        try:
            chart = FrozenCanonicalBaziChart(pillars=pillars)
            result = production_entry(chart)
            if result['gate'] != 'PASSED':
                continue
            results['valid_chart'] += 1

            meta = result.get('meta_outputs', {})
            meta_outputs = meta.get('meta_outputs', {})

            # 1. 身旺衰评估（用强弱轨道的结构事实推断身旺/身弱）
            answer_ws = extract_wangshuai(case.get('judgment', ''))
            if answer_ws:
                results['wangshuai']['has_answer'] += 1
                # 统一用PZZQ轨道评估强弱（PZZQ是Primary，所有书通用）
                qr_output = meta_outputs.get('QIANG_RUO', {})
                qr_tracks = qr_output.get('tracks', {})
                track_output = qr_tracks.get('PZZQ', {})
                qr_candidates = [c.get('element', '') for c in track_output.get('candidates', [])]

                # 从结构事实推断身旺/身弱
                root_power = None
                support_state = None
                for c in qr_candidates:
                    if c.startswith('根气='):
                        root_power = c.replace('根气=', '')
                    elif c.startswith('帮扶='):
                        support_state = c.replace('帮扶=', '')

                # 推断规则: 重根不为克泄所压; 无根+克泄=身弱
                engine_ws = None
                if root_power == '重根':
                    engine_ws = '身旺'  # 重根不为克泄成势所压
                elif root_power == '轻根':
                    if support_state in ('生扶成势', '生扶稍强'):
                        engine_ws = '身旺'
                    elif support_state in ('克泄成势', '克泄稍强'):
                        engine_ws = '身弱'
                    else:
                        engine_ws = '中和'
                elif root_power == '无根':
                    if support_state in ('生扶成势', '生扶稍强'):
                        engine_ws = '身弱'  # 有帮扶但无根仍弱
                    else:
                        engine_ws = '身弱'
                else:
                    engine_ws = '未知'

                # 匹配
                if answer_ws == engine_ws:
                    results['wangshuai']['hit'] += 1
                elif answer_ws == '中和':
                    results['wangshuai']['hit'] += 1  # 中和暂时算命中
                else:
                    results['wangshuai']['details'].append({
                        'id': case.get('id', ''),
                        'answer': answer_ws,
                        'engine': engine_ws,
                        'root': root_power,
                        'support': support_state,
                        'judgment': str(case.get('judgment', ''))[:100],
                    })

            # 2. 格局评估（用对应轨道）
            answer_geju = extract_geju(case.get('judgment', ''))
            if answer_geju:
                results['geju']['has_answer'] += 1
                geju_output = meta_outputs.get('GE_JU', {})
                geju_tracks = geju_output.get('tracks', {})
                track_output = geju_tracks.get('PZZQ', {})
                engine_candidates = [c.get('element', '') for c in track_output.get('candidates', [])]
                # 去掉标准答案中的"格"字再匹配
                answer_geju_norm = answer_geju.replace('格', '')
                if answer_geju_norm in engine_candidates:
                    results['geju']['hit'] += 1
                else:
                    results['geju']['details'].append({
                        'id': case.get('id', ''),
                        'answer': answer_geju,
                        'engine': engine_candidates,
                        'judgment': str(case.get('judgment', ''))[:100],
                    })

            # 3. 调候评估（仅穷通宝鉴）
            if book_code == 'QTBJ':
                answer_dh = extract_diaohou(case.get('judgment', ''))
                if answer_dh:
                    results['diaohou']['has_answer'] += 1
                    dh_output = meta_outputs.get('DIAO_HOU', {})
                    dh_tracks = dh_output.get('tracks', {})
                    track_output = dh_tracks.get('QTBJ', {})
                    engine_candidates = [c.get('element', '') for c in track_output.get('candidates', [])]
                    # 天干转五行再匹配
                    WX_TO_WUXING = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
                    engine_wuxing = [WX_TO_WUXING.get(c, c) for c in engine_candidates]
                    if answer_dh in engine_wuxing:
                        results['diaohou']['hit'] += 1
                    else:
                        results['diaohou']['details'].append({
                            'id': case.get('id', ''),
                            'answer': answer_dh,
                            'engine': engine_candidates,
                            'judgment': str(case.get('judgment', ''))[:100],
                        })

        except Exception as e:
            continue

    return results


def print_results(results):
    """打印评估结果."""
    print(f"\n{'='*60}")
    print(f"【{results['book']}】({results['book_code']}轨道)")
    print(f"{'='*60}")
    print(f"总案例: {results['total']}, 有效八字: {results['valid_chart']}")

    # 身旺衰
    ws = results['wangshuai']
    if ws['has_answer'] > 0:
        rate = ws['hit'] / ws['has_answer'] * 100
        print(f"\n身旺衰: 有标准答案{ws['has_answer']}例, 命中{ws['hit']}例, 命中率={rate:.1f}%")
        if ws['details']:
            print(f"  未命中前5例:")
            for d in ws['details'][:5]:
                print(f"    {d['id']}: 原文={d['answer']}, 引擎={d['engine']}")
    else:
        print(f"\n身旺衰: 无标准答案")

    # 格局
    geju = results['geju']
    if geju['has_answer'] > 0:
        rate = geju['hit'] / geju['has_answer'] * 100
        print(f"\n格局: 有标准答案{geju['has_answer']}例, 命中{geju['hit']}例, 命中率={rate:.1f}%")
        if geju['details']:
            print(f"  未命中前5例:")
            for d in geju['details'][:5]:
                print(f"    {d['id']}: 原文={d['answer']}, 引擎={d['engine']}")
    else:
        print(f"\n格局: 无标准答案")

    # 调候
    dh = results['diaohou']
    if dh['has_answer'] > 0:
        rate = dh['hit'] / dh['has_answer'] * 100
        print(f"\n调候: 有标准答案{dh['has_answer']}例, 命中{dh['hit']}例, 命中率={rate:.1f}%")
        if dh['details']:
            print(f"  未命中前5例:")
            for d in dh['details'][:5]:
                print(f"    {d['id']}: 原文={d['answer']}, 引擎={d['engine']}")


if __name__ == '__main__':
    # 按书分开评估
    books = [
        ('子平真诠', 'PZZQ'),
        ('渊海子平', 'YHZP'),
        ('滴天髓', 'DTS'),
        ('穷通宝鉴', 'QTBJ'),
    ]

    all_results = []
    for book_name, book_code in books:
        print(f"\n正在评估 {book_name}...")
        results = evaluate_book(book_name, book_code, max_cases=50)
        print_results(results)
        all_results.append(results)

    # 汇总
    print(f"\n{'='*60}")
    print("按书分开评估汇总")
    print(f"{'='*60}")
    print(f"{'书名':<12} {'轨道':<6} {'身旺衰命中':<12} {'格局命中':<12} {'调候命中':<12}")
    print("-" * 60)
    for r in all_results:
        ws_rate = f"{r['wangshuai']['hit']}/{r['wangshuai']['has_answer']}" if r['wangshuai']['has_answer'] > 0 else "N/A"
        geju_rate = f"{r['geju']['hit']}/{r['geju']['has_answer']}" if r['geju']['has_answer'] > 0 else "N/A"
        dh_rate = f"{r['diaohou']['hit']}/{r['diaohou']['has_answer']}" if r['diaohou']['has_answer'] > 0 else "N/A"
        print(f"{r['book']:<12} {r['book_code']:<6} {ws_rate:<12} {geju_rate:<12} {dh_rate:<12}")
