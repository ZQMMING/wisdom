# -*- coding: utf-8 -*-
"""易经数据完整性与准确性核实报告 - 最终版"""
import json
import re
from pathlib import Path
from collections import defaultdict

LOCAL_BASE = Path("C:/Users/wisdom/wisdom/src/tongshu/engines/yi")
MASTER_DATA = Path("E:/顺天资料/shuantian资料/大师文集/傅佩荣/Book-of-Changes-master")

def load_yao_ci_data():
    """从yao_ci_data.py加载爻辞数据"""
    yao_ci_path = LOCAL_BASE / "yao_ci_data.py"
    with open(yao_ci_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    yao_data = {}
    hexagram_pattern = r'"([^"]+)":\s*\[\s*'
    line_pattern = r'\(\s*(\d+)\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)'
    
    for match in re.finditer(hexagram_pattern, content):
        hex_name = match.group(1)
        start = match.end()
        next_match = re.search(hexagram_pattern, content[start:])
        if next_match:
            end = start + next_match.start()
        else:
            end = content.find(']', start) + 1
        
        section = content[start:end]
        lines = []
        for line_match in re.finditer(line_pattern, section):
            idx, pos, text, source = line_match.groups()
            lines.append({
                'index': int(idx),
                'position': pos,
                'text': text,
                'source': source
            })
        if lines:
            yao_data[hex_name] = lines
    
    return yao_data

def load_classical_texts():
    """从classical_text.py加载卦辞、彖辞、大象辞"""
    ct_path = LOCAL_BASE / "classical_text.py"
    with open(ct_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    texts = {}
    lines = content.split('\n')
    current_hex = None
    in_block = False
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('"') and ':' in line and not in_block:
            match = re.match(r'^"([^"]+)":\s*\{', line)
            if match:
                current_hex = match.group(1)
                in_block = True
                texts[current_hex] = {}
                continue
        
        if in_block and current_hex:
            if '"gua_ci":' in line:
                match = re.search(r'"gua_ci":\s*"([^"]*)"', line)
                if match:
                    texts[current_hex]['gua_ci'] = match.group(1)
            elif '"tuan_ci":' in line:
                match = re.search(r'"tuan_ci":\s*"([^"]*)"', line)
                if match:
                    texts[current_hex]['tuan_ci'] = match.group(1)
            elif '"da_xiang_ci":' in line:
                match = re.search(r'"da_xiang_ci":\s*"([^"]*)"', line)
                if match:
                    texts[current_hex]['da_xiang_ci'] = match.group(1)
            
            if line == '},' or line == '}':
                in_block = False
                current_hex = None
    
    return texts

def load_fupeirong_data():
    """从傅佩荣源文件加载解读数据"""
    fu_data = {}
    
    for md_file in sorted(MASTER_DATA.glob("*_cn.md")):
        hex_name = md_file.stem.replace('_cn', '')
        try:
            decoded_name = hex_name.encode('utf-8').decode('unicode_escape')
        except:
            decoded_name = hex_name
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取卦辞
        gua_ci_match = re.search(r'卦辞[：:]\s*(.+)', content)
        gua_ci = gua_ci_match.group(1).strip() if gua_ci_match else ""
        
        # 提取爻辞 - 获取原文（第一个匹配）
        lines = []
        line_pattern = r'(初九|九二|六三|九四|九五|上六|初六|六二|九三|六四|六五|上九)[：:]\s*([^\n。]+(?:。|[。]))'
        # Track which positions we've already added to avoid duplicates (原文 vs 译文)
        seen_positions = set()
        for match in re.finditer(line_pattern, content):
            pos = match.group(1)
            text = match.group(2).strip()
            # 只取每个爻位的第一次出现（原文），跳过译文
            if pos not in seen_positions and '译文' not in text and '注释' not in text:
                seen_positions.add(pos)
                lines.append({'position': pos, 'text': text})
        
        fu_data[hex_name] = {
            'name': decoded_name,
            'gua_ci': gua_ci,
            'lines': lines
        }
    
    return fu_data

def verify_completeness(yao_data, classical_texts):
    """验证数据完整性"""
    expected_names = [
        '乾为天', '坤为地', '水雷屯', '山水蒙', '水天需', '天水讼',
        '地水师', '水地比', '风天小畜', '天泽履', '地天泰', '天地否',
        '天火同人', '火天大有', '地山谦', '雷地豫', '泽雷随', '山风蛊',
        '地泽临', '风地观', '火雷噬嗑', '山火贲', '山地剥', '地雷复',
        '天雷无妄', '山天大畜', '山雷颐', '泽风大过', '坎为水', '离为火',
        '泽山咸', '雷风恒', '天山遁', '雷天大壮', '火地晋', '地火明夷',
        '风火家人', '火泽睽', '水山蹇', '雷水解', '山泽损', '风雷益',
        '泽天夬', '天风姤', '泽地萃', '地风升', '泽水困', '水风井',
        '泽火革', '火风鼎', '震为雷', '艮为山', '风山渐', '雷泽归妹',
        '雷火丰', '火山旅', '巽为风', '兑为泽', '风水涣', '水泽节',
        '风泽中孚', '雷山小过', '水火既济', '火水未济'
    ]
    
    results = {
        'hexagram_count': len(yao_data),
        'expected_hexagrams': 64,
        'hexagram_complete': len(yao_data) == 64,
        'line_count_total': sum(len(v) for v in yao_data.values()),
        'expected_lines': 384,
        'lines_complete': sum(len(v) for v in yao_data.values()) == 384,
        'gua_ci_count': len(classical_texts),
        'gua_ci_complete': len(classical_texts) == 64,
        'missing_hexagrams': [],
        'incomplete_hexagrams': [],
        'missing_gua_ci': []
    }
    
    for name in expected_names:
        if name not in yao_data:
            results['missing_hexagrams'].append(name)
        elif len(yao_data[name]) != 6:
            results['incomplete_hexagrams'].append(f"{name}({len(yao_data[name])}爻)")
        
        if name not in classical_texts:
            results['missing_gua_ci'].append(name)
    
    return results

def compare_with_master(yao_data, fu_data):
    """对比本地数据与傅佩荣源数据"""
    comparison = {
        'total_compared': 0,
        'exact_matches': 0,
        'partial_matches': 0,
        'mismatches': [],
    }
    
    for hex_name in yao_data.keys():
        local_lines = yao_data.get(hex_name, [])
        fu_entry = None
        
        for fu_key, fu_val in fu_data.items():
            if hex_name in fu_key or fu_key in hex_name:
                fu_entry = fu_val
                break
        
        comparison['total_compared'] += len(local_lines)
        
        for local_line in local_lines:
            pos = local_line['position']
            local_text = local_line['text']
            
            fu_text = None
            for fu_line in (fu_entry.get('lines', []) if fu_entry else []):
                if pos in fu_line.get('position', ''):
                    fu_text = fu_line['text']
                    break
            
            if fu_text is None:
                comparison['mismatches'].append({
                    'hexagram': hex_name,
                    'position': pos,
                    'local': local_text,
                    'fupeirong': '未找到'
                })
            elif local_text == fu_text:
                comparison['exact_matches'] += 1
            else:
                comparison['partial_matches'] += 1
                comparison['mismatches'].append({
                    'hexagram': hex_name,
                    'position': pos,
                    'local': local_text,
                    'fupeirong': fu_text,
                    'note': '文本略有差异'
                })
    
    return comparison

def verify_sources(yao_data):
    """验证爻辞来源标注"""
    source_stats = defaultdict(int)
    issues = []
    
    for hex_name, lines in yao_data.items():
        for line in lines:
            source = line.get('source', '')
            source_stats[source] += 1
            
            if '周易' not in source and '易经' not in source:
                issues.append({
                    'hexagram': hex_name,
                    'position': line['position'],
                    'source': source,
                    'issue': '来源未标注周易/易经'
                })
    
    return {
        'source_distribution': dict(source_stats),
        'total_sources_checked': sum(source_stats.values()),
        'source_issues': issues,
        'source_accuracy_rate': (len(source_stats) > 0 and len(issues) == 0)
    }

def generate_report():
    """生成完整的核实报告"""
    print("=" * 60)
    print("易经数据完整性与准确性核实报告")
    print("=" * 60)
    
    print("\n[1/4] 加载本地数据...")
    yao_data = load_yao_ci_data()
    classical_texts = load_classical_texts()
    print(f"  - 爻辞数据: {len(yao_data)} 卦, {sum(len(v) for v in yao_data.values())} 爻")
    print(f"  - 卦辞数据: {len(classical_texts)} 卦")
    
    print("\n[2/4] 加载傅佩荣解读数据...")
    try:
        fu_data = load_fupeirong_data()
        print(f"  - 傅佩荣数据: {len(fu_data)} 卦")
    except Exception as e:
        print(f"  - 傅佩荣数据加载失败: {e}")
        fu_data = {}
    
    print("\n[3/4] 执行数据完整性验证...")
    completeness = verify_completeness(yao_data, classical_texts)
    
    print(f"  - 卦数: {completeness['hexagram_count']}/64 {'✓' if completeness['hexagram_complete'] else '✗'}")
    print(f"  - 爻辞总数: {completeness['line_count_total']}/384 {'✓' if completeness['lines_complete'] else '✗'}")
    print(f"  - 卦辞数: {completeness['gua_ci_count']}/64 {'✓' if completeness['gua_ci_complete'] else '✗'}")
    
    if completeness['missing_hexagrams']:
        print(f"  ⚠ 缺失卦: {completeness['missing_hexagrams']}")
    if completeness['incomplete_hexagrams']:
        print(f"  ⚠ 不完整: {completeness['incomplete_hexagrams']}")
    if completeness['missing_gua_ci']:
        print(f"  ⚠ 缺失卦辞: {completeness['missing_gua_ci'][:5]}...")
    
    print("\n[4/4] 执行数据对比验证...")
    comparison = {}
    if fu_data:
        comparison = compare_with_master(yao_data, fu_data)
        print(f"  - 总对比: {comparison['total_compared']} 条爻辞")
        print(f"  - 完全匹配: {comparison['exact_matches']} 条")
        print(f"  - 部分匹配: {comparison['partial_matches']} 条")
        print(f"  - 差异数: {len(comparison['mismatches'])} 条")
    else:
        print("  - 跳过对比（无傅佩荣数据）")
    
    sources = verify_sources(yao_data)
    print(f"\n来源验证:")
    print(f"  - 检查总数: {sources['total_sources_checked']} 条")
    unique_sources = len(sources['source_distribution'])
    print(f"  - 唯一来源数: {unique_sources}")
    print(f"  - 准确率: {'100%' if sources['source_accuracy_rate'] else '存在异常'}")
    
    report = {
        "data_completeness": {
            "hexagram_count": completeness['hexagram_count'],
            "expected_hexagrams": 64,
            "hexagram_complete": completeness['hexagram_complete'],
            "line_count_total": completeness['line_count_total'],
            "expected_lines": 384,
            "lines_complete": completeness['lines_complete'],
            "gua_ci_count": completeness['gua_ci_count'],
            "gua_ci_complete": completeness['gua_ci_complete'],
            "missing_hexagrams": completeness['missing_hexagrams'],
            "incomplete_hexagrams": completeness['incomplete_hexagrams'],
            "missing_gua_ci": completeness['missing_gua_ci']
        },
        "master_interpretations": {
            "fupeirong_data_loaded": len(fu_data) > 0,
            "fupeirong_gua_count": len(fu_data),
            "sample_verification": {
                "total_compared": comparison.get('total_compared', 0),
                "exact_matches": comparison.get('exact_matches', 0),
                "partial_matches": comparison.get('partial_matches', 0),
                "mismatches": comparison.get('mismatches', [])[:20]
            },
            "comparison_summary": {
                "total_mismatches": len(comparison.get('mismatches', [])),
                "accuracy_rate": f"{((comparison.get('total_compared', 0) - len(comparison.get('mismatches', []))) / max(comparison.get('total_compared', 1), 1) * 100):.1f}%"
            }
        },
        "source_verification": {
            "total_checked": sources['total_sources_checked'],
            "unique_sources": unique_sources,
            "source_issues_count": len(sources['source_issues']),
            "source_accuracy_rate": sources['source_accuracy_rate']
        },
        "summary": f"易经数据核实完成：64卦{'完整' if completeness['hexagram_complete'] else '不完整'}，384爻辞{'全部' if completeness['lines_complete'] else '部分'}完整。卦辞数据{completeness['gua_ci_count']}条{'完整' if completeness['gua_ci_complete'] else '不完整'}。傅佩荣数据{'已对比，完全匹配' if comparison.get('exact_matches', 0) == comparison.get('total_compared', 0) else '已对比，差异' + str(len(comparison.get('mismatches', []))) + '条' if fu_data else '未加载'}。爻辞来源标注{'规范' if sources['source_accuracy_rate'] else '存在异常'}。",
        "verification_status": "PASS" if (
            completeness['hexagram_complete'] and 
            completeness['lines_complete'] and 
            completeness['gua_ci_complete'] and
            sources['source_accuracy_rate']
        ) else "FAIL_WITH_NOTES"
    }
    
    report_path = Path("C:/Users/wisdom/wisdom/yi_verification_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n报告已保存: {report_path}")
    
    return report

if __name__ == "__main__":
    report = generate_report()
    print("\n" + "=" * 60)
    print("核实结果摘要")
    print("=" * 60)
    print(json.dumps(report, ensure_ascii=False, indent=2))
