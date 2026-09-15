# -*- coding: utf-8 -*-
"""统一第一批（9领域）为16字段 cell schema；缺失字段标 TO_VERIFY 待 003B 核验"""
import json, io, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\shuntian-ziping-p0\governance\r1_05_verified_scope.json'
data = json.load(io.open(P, encoding='utf-8'))

GRADE_ATTR = {'A': 'ORIGINAL_AUTHOR', 'B1': 'ORIGINAL_ANNOTATION', 'B': 'ORIGINAL_ANNOTATION',
              'C': 'LATER_COMMENTARY', 'D': 'UNKNOWN'}

def parse_evidence(ev):
    """解析 evidence 字符串 → (source_id, chapter, surface, grade)"""
    m = re.match(r'^(YHZP|PZZQ|DTS|QTBJ|SMTH|SFTK)-\d+-\d+', ev)
    sid = m.group(0) if m else None
    rest = ev[m.end():].strip() if m else ev
    grade_m = re.search(r'[（(](A|B1?|C|D)[）)]\s*$', rest)
    grade = grade_m.group(1) if grade_m else 'UNKNOWN'
    if grade_m:
        rest = rest[:grade_m.start()].strip()
    # 章节/标题：取第一个分隔符（：、——、 ）前
    chapter = 'TO_VERIFY'
    for sep in ['：', ':', '——', ' ', '（']:
        idx = rest.find(sep)
        if idx > 0:
            chapter = rest[:idx].strip()
            break
    surface = rest[:60]
    return sid, chapter, surface, grade

FIRST_BATCH = ['domain_01_wang_qiang_shuai', 'domain_02_ling_shi_di_gen', 'domain_03_shi',
               'domain_04_yue_ling', 'domain_05_ge_ju', 'domain_06_yong_shen',
               'domain_07_bing_yao', 'domain_08_qing_zhuo_zhen_jia', 'domain_09_cong_hua']

converted = 0
for dkey in FIRST_BATCH:
    dom = data[dkey]
    if not isinstance(dom.get('books'), dict):
        continue
    # 判断是否已是 cell 列表（2-5批格式）
    first_val = next(iter(dom['books'].values()))
    if isinstance(first_val, list):
        continue
    cluster = dom.get('term_cluster', [])
    new_books = {}
    for b, info in dom['books'].items():
        cells = []
        for ev in info.get('evidence', []):
            sid, chapter, surface, grade = parse_evidence(ev)
            if not sid:
                continue
            cells.append({
                'domain_id': dom['domain_id'],
                'term_cluster_id': cluster[0] if cluster else dom['domain_id'],
                'surface_form': surface,
                'source_id': sid,
                'chapter_id': chapter,
                'text_layer': 'TO_VERIFY',
                'object_type': 'TO_VERIFY',
                'semantic_role': 'TO_VERIFY',
                'semantic_definition': ev,
                'verified_scope': info.get('verified_scope', 'PENDING'),
                'scope_priority': info.get('scope_priority', '—'),
                'excluded_scope': info.get('excluded_scope', '—'),
                'evidence_grade': grade,
                'attribution': GRADE_ATTR.get(grade, 'UNKNOWN'),
                'execution_eligibility': info.get('eligibility', 'PENDING'),
            })
        new_books[b] = cells
        converted += len(cells)
    dom['books'] = new_books

json.dump(data, io.open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'第一批已转换：{converted} 个 cell（缺失字段标 TO_VERIFY，待 003B 核验）')
