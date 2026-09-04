"""
P2.4 子平计算规则完整性验证

检查 src/tongshu/engines/bazi_engine.py 中的计算常量/规则
是否与 data/evidence/{五书} 中的 Evidence 存在引用关系。

验证维度：
1. 规则常量 → Evidence 引用（正面：有 Evidence 支持）
2. 规则常量 → 无 Evidence 引用（缺口：需标注）
3. Evidence passage_id → 实际引用规则的覆盖率
"""
import json
import re
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple

# ============================================================
# 1. 提取 bazi_engine.py 中的计算规则常量
# ============================================================

def extract_engine_rules(engine_path: str) -> Dict[str, dict]:
    """从 bazi_engine.py 提取所有计算规则常量。"""
    content = Path(engine_path).read_text(encoding='utf-8')
    
    rules = {}
    
    # 匹配常量定义: NAME = { ... } 或 NAME = [...]
    constant_pattern = re.compile(
        r'^([A-Z_]+)\s*=\s*(?:\{[^}]+\}|\[^[^\]]+\])',
        re.MULTILINE | re.DOTALL
    )
    
    for match in constant_pattern.finditer(content):
        name = match.group(1)
        # 跳过已知的非规则常量
        skip_names = {'HEAVENLY_STEMS', 'EARTHLY_BRANCHES', 'STEM_ELEMENT', 
                      'STEM_POLARITY', '_GENERATES', '_CONTROLS', '_BRANCH_HIDDEN_MAIN'}
        if name in skip_names:
            continue
        
        # 获取常量的注释（如果有）
        line_start = content.rfind('\n', 0, match.start()) + 1
        line_end = content.find('\n', match.start())
        line = content[line_start:line_end].strip()
        
        rules[name] = {
            'line': content[:match.start()].count('\n') + 1,
            'comment': line,
            'has_evidence_ref': bool(re.search(r'(YHZP|DTS|PZZQ|SMTH|QTBJ)_', line)),
        }
    
    return rules


# ============================================================
# 2. 提取五书 Evidence 的 passage_id 集合
# ============================================================

def extract_evidence_passage_ids(book_dir: str) -> Set[str]:
    """从 Evidence 目录提取所有 passage_id。"""
    passage_ids = set()
    base = Path('data/evidence') / book_dir
    if not base.exists():
        return passage_ids
    
    for f in base.glob('E-*.json'):
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
            pid = data.get('source_locator', {}).get('passage_id', '')
            if pid:
                passage_ids.add(pid)
        except:
            pass
    return passage_ids


# ============================================================
# 3. 建立规则 → Evidence 的映射
# ============================================================

def check_rule_evidence_coverage(
    rules: Dict[str, dict],
    evidence_passage_ids: Dict[str, Set[str]],
    engine_content: str,
) -> List[dict]:
    """检查每个规则常量的 Evidence 覆盖情况。"""
    results = []
    
    for rule_name, rule_info in rules.items():
        # 检查规则定义中是否引用 Evidence
        rule_line = None
        for line in engine_content.split('\n'):
            if f'{rule_name}' in line and '=' in line:
                rule_line = line
                break
        
        # 检查 rule_info['comment'] 中是否有 Evidence 引用
        evidence_refs = re.findall(r'(YHZP|DTS|PZZQ|SMTH|QTBJ)_\w+', rule_info.get('comment', ''))
        
        # 检查整个文件中该规则名附近的 Evidence 引用
        full_file_evidence = re.findall(r'(YHZP|DTS|PZZQ|SMTH|QTBJ)_\w+', engine_content)
        
        results.append({
            'rule_name': rule_name,
            'line': rule_info['line'],
            'evidence_in_comment': evidence_refs,
            'evidence_in_file': list(set(full_file_evidence)),
            'coverage_status': 'COVERED' if evidence_refs else 'UNVERIFIED',
        })
    
    return results


# ============================================================
# 4. 主验证流程
# ============================================================

def main():
    print("=" * 70)
    print("P2.4 子平计算规则完整性验证")
    print("=" * 70)
    
    # 1. 提取引擎规则
    engine_path = 'src/tongshu/engines/bazi_engine.py'
    engine_content = Path(engine_path).read_text(encoding='utf-8')
    rules = extract_engine_rules(engine_path)
    
    print(f"\n[1] 引擎规则常量: {len(rules)} 个")
    for name, info in sorted(rules.items(), key=lambda x: x[1]['line']):
        ref_marker = "✓" if info['has_evidence_ref'] else "✗"
        print(f"  {ref_marker} L{info['line']:3d}: {name}")
    
    # 2. 提取 Evidence passage_id
    books = ['yuan_hai_zi_ping', 'di_tian_sui', 'ziping_zhenquan', 
             'san_ming_tong_hui', 'qiong_tong_bao_jian']
    
    evidence_passage_ids = {}
    total_evidences = 0
    for book in books:
        pids = extract_evidence_passage_ids(book)
        evidence_passage_ids[book] = pids
        total_evidences += len(pids)
    
    print(f"\n[2] Evidence passage_id 覆盖: {total_evidences} 个唯一 passage")
    for book, pids in evidence_passage_ids.items():
        print(f"  {book}: {len(pids)} passages")
    
    # 3. 检查规则覆盖
    coverage_results = check_rule_evidence_coverage(rules, evidence_passage_ids, engine_content)
    
    covered = [r for r in coverage_results if r['coverage_status'] == 'COVERED']
    unverified = [r for r in coverage_results if r['coverage_status'] == 'UNVERIFIED']
    
    print(f"\n[3] 规则 Evidence 覆盖率:")
    print(f"  COVERED:    {len(covered)} 个规则")
    print(f"  UNVERIFIED: {len(unverified)} 个规则")
    
    if unverified:
        print(f"\n  未验证规则列表:")
        for r in sorted(unverified, key=lambda x: x['line']):
            print(f"    L{r['line']:3d}: {r['rule_name']}")
    
    # 4. 抽样验证：检查几个关键规则的 Evidence 对应
    print(f"\n[4] 关键规则抽样验证:")
    
    key_rules = ['BRANCH_CLASH', 'STEM_HE', 'PEACH_BLOSSOM_BY_DAY', 'KONG_WANG_BY_XUN']
    for rule_name in key_rules:
        # 找规则定义行及注释
        for line in engine_content.split('\n'):
            if f'{rule_name}' in line and '=' in line:
                # 向前找注释
                idx = engine_content.find(rule_name)
                if idx > 0:
                    # 找前面的注释行
                    before = engine_content[:idx]
                    comments = re.findall(r'#.*$', before, re.MULTILINE)
                    last_comment = comments[-1] if comments else ''
                else:
                    last_comment = ''
                print(f"  {rule_name}:")
                print(f"    定义行: {line.strip()[:80]}")
                print(f"    注释: {last_comment.strip()[:80]}")
                break
    
    # 5. 总结
    print("\n" + "=" * 70)
    print("验证总结")
    print("=" * 70)
    print(f"引擎规则总数: {len(rules)}")
    print(f"有 Evidence 引用: {len(covered)}")
    print(f"无 Evidence 引用: {len(unverified)}")
    print(f"覆盖率: {len(covered)/len(rules)*100:.1f}%" if rules else "N/A")
    
    return {
        'total_rules': len(rules),
        'covered': len(covered),
        'unverified': len(unverified),
        'coverage_rate': len(covered)/len(rules)*100 if rules else 0,
    }


if __name__ == '__main__':
    main()
