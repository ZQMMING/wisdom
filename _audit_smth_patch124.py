# -*- coding: utf-8 -*-
"""
PATCH-124 SMTH evidence classifier (organizer groundwork).
Reads registries/evidence/smth_evidence.jsonl (2530), tags every row with a
skip-reason bucket or CANDIDATE label. Deterministic; emits a ledger + a
candidate list for the semantic extraction subagent.
Buckets:
  RISHI_TABLE     六X日X時斷 verse divination tables -> skip (歌诀+断语)
  SHENSHA         static 神煞 / 吉神凶煞 markers -> EXCLUDED (no runtime rule)
  HUMAN_AFFAIRS   女命/六亲/寿夭/性情/富贵贫贱 ... -> 人事断语 skip
  CASE_EXAMPLE    某造/一命 concrete chart case -> case isolation skip
  COMMENTARY      子平說辯 / methodological prose -> skip
  CANDIDATE       structurally eligible (void mechanics / seal treasury /
                  de-xiu formula / organ mapping / luck-modifier interaction)
"""
import json, re, collections, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'registries', 'evidence', 'smth_evidence.jsonl')
OUT_LEDGER = os.path.join(HERE, 'registries', 'evidence', 'smth_patch124_buckets.json')
OUT_CANDID = os.path.join(HERE, 'registries', 'evidence', 'smth_patch124_candidates.json')

rows = [json.loads(l) for l in open(SRC, encoding='utf-8') if l.strip()]

RI_SHI_RE = re.compile(r'時斷')
# static shensha / auspicious-inauspicious-star chapter names
SHENSHA_CHAP = re.compile(
    r'神煞|天乙|太極貴|亡神|劫煞|災煞|勾絞|驛馬|華蓋|將星|咸池|桃花|魁罡|羊刃|飛刃|'
    r'天德|月德|天官|福星|學堂|詞館|祿神|貴人|德秀|六厄|元辰|孤辰|寡宿|天羅|地網|'
    r'空亡|暗金|的煞|劫煞|破碎|十惡大敗|互換|喪門|弔客|太歲|刑災|官符|白虎|五鬼|'
    r'年干|年支|月支神|神煞|貴科|科名星')
HUMAN_CHAP = re.compile(
    r'女命|小兒|六亲|六親|妻妾|兄弟|父母|子息|夫妻|旺夫|傷子|旺子|娼|淫|濫|濁|清|'
    r'富貴|貧賤|凶惡|壽夭|性情|相貌|孕生|產|招嫁|之福|安靜守分|引例章|橫天|'
    r'正偏自處|子平說辯|疾病|論德|論六')
CASE_RE = re.compile(r'一命|某造|年月日時|癸酉甲子|甲辰年|某命|昔有|古人|顏回|李廣')

def classify(r):
    ch = r['chapter']; q = r['quotation']
    if RI_SHI_RE.search(ch):
        return 'RISHI_TABLE'
    if CASE_RE.search(q):
        return 'CASE_EXAMPLE'
    if '子平說辯' in ch:
        return 'COMMENTARY'
    # --- positive candidate routing (structural, NOT human-affairs) ---
    if '空亡' in ch:
        return 'CANDIDATE'          # void mechanics: xun-cycle definition
    if '德秀' in ch or '六厄' in ch:
        return 'CANDIDATE'          # structural formula tables -> special_reference
    if '正印' in ch:
        return 'CANDIDATE'          # seal-treasury definition per stem
    if '疾病' in ch and ('膽' in q and '肝' in q and '心' in q and '肺' in q):
        return 'CANDIDATE'          # organ-stem mapping verse only
    if '羊刃' in ch and ('行運' in q or '運行' in q):
        return 'CANDIDATE'          # luck-cycle interaction with blade
    if ('刑衝' in ch or '刑沖' in ch or '戰關' in ch) and not CASE_RE.search(q):
        return 'CANDIDATE'          # clash/combine mechanism (garbled verse -> subagent decides)
    # --- exclusion routing ---
    if HUMAN_CHAP.search(ch):
        return 'HUMAN_AFFAIRS'
    if SHENSHA_CHAP.search(ch):
        return 'SHENSHA'
    return 'HUMAN_AFFAIRS'  # default: conservative skip (宁漏勿误)

buckets = collections.Counter()
by_bucket = collections.defaultdict(list)
for r in rows:
    b = classify(r)
    buckets[b] += 1
    by_bucket[b].append(r['evidence_id'])

cand = [r for r in rows if classify(r) == 'CANDIDATE']
json.dump({b: by_bucket[b] for b in by_bucket}, open(OUT_LEDGER, 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(cand, open(OUT_CANDID, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('=== PATCH-124 SMTH bucket ledger ===')
total = 0
for b, c in buckets.most_common():
    print(f'{b:16s} {c:5d}  ({100*c/len(rows):.1f}%)')
    total += c
print('TOTAL', total)
print()
print('CANDIDATE rows:', len(cand))
print('--- candidate chapter breakdown ---')
cc = collections.Counter(r['chapter'][:40] for r in cand)
for k, v in cc.most_common():
    print(f'  {v:3d}  {k}')
print()
print('ledger ->', OUT_LEDGER)
print('candidates ->', OUT_CANDID)
