# SFTK《神峰通考》知识工程录入 · 摘要

## 概览

| 项 | 值 |
|---|---|
| engine / book | `SHENFENG_TONGKAO` / 神峰通考 |
| 底本 SHA256 前8 / 行数 | `0091619F` / 7358（复验一致） |
| Sources | **166** 条（全部 ORIGINAL） |
| Rule 候选 | **96** 条（`CAND-SFTK-001` ~ `CAND-SFTK-096`） |
| unformalizable | 70 条（歌賦/詩韻/總論，无法拆出干净 IF-THEN） |
| text_layer 分布 | ORIGINAL 166 / 其余 0 |
| 质检 | **21/21 全部通过，0 失败** |
| 正文总字数（去噪拼接） | 约 139,722 字 |

## Rule 结构分布

- rule_type：definition 42 / medicine 25 / resolution 21 / activation 5 / diagnosis 1 / effectiveness 1 / suppress 1
- scope：natal 80 / decade 13 / year 3
- evidence_requirement：A 67 / B 25 / C 4
- 覆盖 31 个 Source；重点覆盖病藥（diagnosis/medicine）、動靜、蓋頭、雕枯旺弱損益長生八法、正官/偏官格、神趣八法、神煞、起運、十干化氣。

## 章节覆盖

- 卷一：叙、卷一開篇、五星參悅頌、男女合婚說、總論子平謬說類、動靜說、蓋頭說、六親說、病藥說類、雕枯旺弱四病說類、損益生長四藥說類、正官格、偏官格、時上一位貴格、月支正財格、附傷官十論、卍綬格、陽刃格、專祿格、雜氣財官印綬格、金神格、飛天祿馬、子/丑遙巳、井欄叉、六乙鼠貴、六陰朝陽、刑合、合祿、曲直/稼穡/炎上/潤下/從革、從化、歲德扶殺、日德/日貴、魁罡、六壬趨艮、六甲趨乾、勾陳得位、玄武當權、財官雙美、拱祿拱貴、日祿歸時、四位純全、天元一氣、三合聚集、福德、神趣八法（屬/從/化/照/返/鬼/伏象）、論大運、論太歲、五星諸論、不換金骨髓歌斷。
- 卷四~卷六：十天干體象詩、十二支詩、干支所屬、神煞（天德/月德/學堂/華蓋/將星/驛馬/孤神/劫殺/破軍/懸針/紅艷/五鬼/流霞/紫暗/三坵五墓/天羅地網/太白/斧劈）、起八字訣、起大運法、看命入式、子平舉要、江湖摘錦、十干從化定訣、格歌、氣象篇、定真篇、一行禪師壬二元賦、相心賦、仙機賦、人鑑論、渊源集說、地支賦、病源賦。

## 抽样 3 条 Rule 与原文对照

### ① CAND-SFTK-009（definition · natal · A）
- 原文（SFTK-008 六親說）：「…偏財為父比劫重重損父親**正印為母**財星旺處雖損母…」
- Rule：preconditions = 空 conjunction；operation = `emit`；outputs = `[{field: mother, value: 正印為母}]`。

### ② CAND-SFTK-024（medicine · decade · A）
- 原文（SFTK-010 雕枯旺弱四病說類）：「…官星太旺者宜行傷官運以去其官星財星太旺者宜行比劫運以去財星**印星太旺者宜行財星運以破其印星**日干太旺者宜行官殺運以制其日主…」
- Rule：preconditions = `ten_god=印星 ∧ strength=太旺`；operation = `emit`；outputs = `[{field: luck_direction, value: 宜行財星運以破其印星}]`。

### ③ CAND-SFTK-055（resolution · year · A）
- 原文（SFTK-068 論大運）：「…不宜與太歲相尅若歲沖運不吉運沖歲則甚不利**歲運相生者吉**宜細推無不應驗。」
- Rule：preconditions = `has(year_luck_sheng)`；operation = `emit`；outputs = `[{field: status, value: 歲運相生者吉}]`。

## 处理要点

- 繁体保持繁体，未改一字、未校勘、未繁简转换；OCR 重复行/成环乱字（行 348、433–435 等）如实保留，详见 qa_report.md。
- 两册间与卷六后的书局广告/出版说明已删除，未录入。
- 只落盘，不 commit，未动 `D:\shuntian\data\classics\original\`。
- 预估 100–300 Source / 80–200 Rule；实际 166 Source / 96 Rule，落在区间内。
