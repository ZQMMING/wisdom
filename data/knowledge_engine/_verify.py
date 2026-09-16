import json, os, random
books = {
    'pzzq': r'D:\顺天系统资料\豆包资料\六部经典校对版\PZZQ_子平真诠_清洗版.md',
    'dts':  r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓_清洗版.md',
    'qtbj': r'D:\顺天系统资料\豆包资料\六部经典校对版\QTBJ_穷通宝鉴_清洗版.md',
    'smth': r'D:\顺天系统资料\豆包资料\六部经典校对版\SMTH_三命通会_清洗版.md',
}
allowed_op = {'equals','not_equals','in','has','absent'}
watermarks = ['luckclub','qq群','QQ群','收费50','技术支持','D:\\','http','\ufffd']
random.seed(1)
for b, bottom_path in books.items():
    base = os.path.join(r'D:\shuntian\data\knowledge_engine', b)
    src = [json.loads(l) for l in open(os.path.join(base,'sources.jsonl'),encoding='utf-8')]
    rul = [json.loads(l) for l in open(os.path.join(base,'rules_candidate.jsonl'),encoding='utf-8')]
    unf_path = os.path.join(base,'unformalizable.jsonl')
    unf = [json.loads(l) for l in open(unf_path,encoding='utf-8')] if os.path.exists(unf_path) else []
    smap = {s['source_id']:s for s in src}
    ids = [s['source_id'] for s in src]
    rids = [r['rule_id'] for r in rul]
    bad_bind = [r['rule_id'] for r in rul if r['source_id'] not in smap or smap[r['source_id']]['text_layer']!='ORIGINAL']
    bad_txt = [s['source_id'] for s in src if any(x in s['source_text'] for x in watermarks)]
    bad_op = [(r['rule_id'],c['operator']) for r in rul for c in r['preconditions']['conditions'] if c['operator'] not in allowed_op]
    nested = any('conditions' in c for r in rul for c in r['preconditions']['conditions'])
    bottom = open(bottom_path, encoding='utf-8').read()
    sample = random.sample(src, min(5,len(src)))
    miss = [s['source_id'] for s in sample if s['source_text'].strip()[:30] not in bottom]
    print(f"[{b}] src={len(src)} rul={len(rul)} unf={len(unf)} "
          f"sid_uniq={len(ids)==len(set(ids))} rid_uniq={len(rids)==len(set(rids))} "
          f"bad_bind={len(bad_bind)} bad_txt={len(bad_txt)} bad_op={len(bad_op)} "
          f"nested={nested} hit={'OK' if not miss else miss}")
