# -*- coding: utf-8 -*-
"""R1-05 准备：定位各领域关键证据 source_id"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

targets = {
  'yhzp': ['旺相', '得時俱為旺', '無氣遇劫', '身旺', '旺而'],
  'pzzq': ['專求月令', '月令', '用神'],
  'smth': ['黨盛為強', '地支至切', '得勢', '暗夫得勢'],
  'sftk': ['病', '藥', '得垣', '歸垣', '持勢', '月提得令', '先看月令', '次看淺深'],
  'dts': ['傷官七煞混', '清濁', '清奇'],
}
for eng, kws in targets.items():
    lines = open(rf'D:\shuntian-ziping-p0\registries\source\sources.{eng}.jsonl', encoding='utf-8').read().splitlines()
    books = [json.loads(l) for l in lines if l.strip()]
    print(f'=== {eng} ===')
    for kw in kws:
        found = False
        for s in books:
            t = s.get('source_text', '')
            if kw in t:
                print(f'  {s["source_id"]} [{s.get("chapter")}] {s.get("text_layer")}/{s.get("evidence_grade")}: ...{t[max(0,t.find(kw)-15):t.find(kw)+35]}...')
                found = True
                break
        if not found:
            print(f'  [{kw}] 未找到')
