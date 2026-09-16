import json, os
ROOT = r'D:\shuntian\data\knowledge_engine'
books = ['yhzp','pzzq','dts','qtbj','smth','sftk']
allowed_op = {'equals','not_equals','in','has','absent'}
watermarks = ['luckclub','qq群','QQ群','收费50','技术支持','D:\\','http','\ufffd']

grand_src = grand_rul = grand_unf = 0
print(f"{'book':<6} {'src':>5} {'rul':>5} {'unf':>5} | sid_u rid_u bad_bad bad_txt bad_op nested | notes")
print('-'*100)
for b in books:
    base = os.path.join(ROOT, b)
    src = [json.loads(l) for l in open(os.path.join(base,'sources.jsonl'),encoding='utf-8')]
    rul = [json.loads(l) for l in open(os.path.join(base,'rules_candidate.jsonl'),encoding='utf-8')]
    unf_path = os.path.join(base,'unformalizable.jsonl')
    unf = [json.loads(l) for l in open(unf_path,encoding='utf-8')] if os.path.exists(unf_path) else []
    smap = {s['source_id']:s for s in src}
    ids = [s['source_id'] for s in src]
    rids = [r['rule_id'] for r in rul]
    bad_bind = sum(1 for r in rul if r['source_id'] not in smap or smap[r['source_id']]['text_layer']!='ORIGINAL')
    bad_txt = sum(1 for s in src if any(x in s['source_text'] for x in watermarks))
    bad_op = sum(1 for r in rul for c in r['preconditions']['conditions'] if c['operator'] not in allowed_op)
    nested = any('conditions' in c for r in rul for c in r['preconditions']['conditions'])
    grand_src += len(src); grand_rul += len(rul); grand_unf += len(unf)
    print(f"{b:<6} {len(src):>5} {len(rul):>5} {len(unf):>5} | "
          f"{len(ids)==len(set(ids))!s:>5} {len(rids)==len(set(rids))!s:>5} {bad_bind:>6} {bad_txt:>8} {bad_op:>7} {str(nested):>7} |")
print('-'*100)
print(f"{'TOTAL':<6} {grand_src:>5} {grand_rul:>5} {grand_unf:>5}")
