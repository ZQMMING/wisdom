# PZZQ《子平真诠》知识工程摘要

## 1. 产出条数
| 文件 | 条数 |
|---|---|
| sources.jsonl | 854 |
| rules_candidate.jsonl | 138 |
| unformalizable.jsonl | 320 |

## 2. text_layer 分布
| layer | 条数 |
|---|---|
| ORIGINAL | 396 |
| ANNOTATION（徐乐吾注） | 293 |
| LATER_COMMENTARY（白话译文/关键词/现代启示） | 150 |
| UNVERIFIED（林注，交 Human） | 15 |

## 3. 章节覆盖
- 51 个实质章节（第 1–51 章）全覆盖；第 0 章目录、文件头按规范跳过。
- 实质论说章节（论用神、论十干、论格局成败救应、八格及取运等）均有 Rule 绑定。

## 4. Rule 分布
- scope：natal 122，decade（行运）16。
- rule_type：resolution 69，definition 32，diagnosis 25，medicine 5，activation 4，effectiveness 2，suppress 1。
- evidence_requirement：A（直述定义）为主，B（一步直译的格局成败条件）为主，无 C。
- 全部 status=CANDIDATE，未评分、未统一用神、未跨经典优先级。

## 5. 抽样 Rule 对照（3 条）

### 样例 1：CAND-PZZQ-001（十干定义）
```json
{"rule_id":"CAND-PZZQ-001","engine":"ZIPIN_ZHENQUAN","source_id":"PZZQ-004-007","rule_type":"definition","scope":"natal","subject":"ten_stem","predicate":"is","preconditions":{"type":"conjunction","conditions":[{"field":"stem","operator":"equals","value":"甲"}]},"operation":"emit","outputs":[{"field":"stem_element","value":"木"},{"field":"stem_yinyang","value":"阳"}],"evidence_requirement":"A","status":"CANDIDATE","notes":"《子平真诠》论阴阳生克"}
```
对应原文（PZZQ-004-007）：「即以甲乙庚辛言之。**甲者，阳木也**，木之生气也；乙者，阴木也……」

### 样例 2：CAND-PZZQ-046（七煞格成）
```json
{"rule_id":"CAND-PZZQ-046","engine":"ZIPIN_ZHENQUAN","source_id":"PZZQ-011-003","rule_type":"resolution","scope":"natal","subject":"pattern","predicate":"成","preconditions":{"type":"conjunction","conditions":[{"field":"pattern","operator":"equals","value":"七煞格"},{"field":"day_master_strength","operator":"equals","value":"强"},{"field":"食制","operator":"has"}]},"operation":"emit","outputs":[{"field":"pattern_status","value":"成"}],"evidence_requirement":"B","status":"CANDIDATE","notes":"身强七煞逢制煞格成"}
```
对应原文（PZZQ-011-003）：「……食神生财，或食带煞而无财，弃食就煞而透印，食格成也。**身强七煞逢制，煞格成也。**伤官生财……」

### 样例 3：CAND-PZZQ-138（从煞破格条件）
```json
{"rule_id":"CAND-PZZQ-138","engine":"ZIPIN_ZHENQUAN","source_id":"PZZQ-049-015","rule_type":"diagnosis","scope":"natal","subject":"follow_pattern","predicate":"broken","preconditions":{"type":"conjunction","conditions":[{"field":"pattern","operator":"equals","value":"弃命从煞"},{"field":"bad","operator":"in","value":["有伤食","有印"]}]},"operation":"suppress","outputs":[{"field":"pattern_status","value":"格不成"}],"evidence_requirement":"B","status":"CANDIDATE","notes":"从煞有伤食或有印则不从"}
```
对应原文（PZZQ-049-015）：「有弃命从煞者，四柱皆煞，而日主无根，舍而从之，格成大贵。**若有伤食，则煞受制而不从，有印则印以化煞而不从。**」

## 6. 说明
- source_text 逐字取自底本（含半角逗号、`**【徐注】**` 标记本身），不改一字。
- 定性强弱比较句（“得一比肩不如得一墓库”之类）因规范禁止比较符，一律入 unformalizable，未硬拆。
- 仅落盘，未写入正式 Registry、未 git commit、未 push。
