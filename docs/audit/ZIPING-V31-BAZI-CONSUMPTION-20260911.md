# 子平引擎 V3.1-FINAL 实施 — 八字消费项审计

> 依据: docs/v2/子平生产规则注册表_实现规格_V3.1-FINAL.md §0.3（Bazi 已提供的事实直接消费，不在 ZiPing 重算）
> 审计范围: src/tongshu/engines/bazi_engine.py (BaziChart) + src/tongshu/reasoning/bazi_ten_gods.py + src/tongshu/models/canonical_bazi.py

## 一、事实消费矩阵（V3.1 段 → Bazi 现有字段）

| V3.1 段 | 需要的 facts | Bazi 提供 | 状态 |
|---|---|---|---|
| FACT (§3) | 日主/四柱/藏干/十神/长生/干支关系/节气/大运 | BaziChart.day_master / four_pillars / hidden_stems / Pillar.stem_ten_god / twelve_growth / raw_relations / luck_pillars | ✅ 齐 |
| LING (§4) | 月支本气五行 vs 日主五行 → SAME/SUPPORTIVE/DRAINING/CONSUMING/OPPOSING | 由 Bazi 事实做**确定性枚举推导**（Pillar.branch_element 已有） | ✅ 派生 |
| GROWTH (§5) | 十二长生 | BaziChart.twelve_growth (日主对四支, 中文值) | ✅ 直接消费 |
| ROOT (§6) | 藏干本/中/余气 | BaziChart.hidden_stems[pos]={main,middle,residual,all} | ✅ 直接消费 |
| STEM (§7) | 透干 | 天干直接可见 + branch_hidden 对应 | ✅ 派生 |
| SUPPORT/DRAIN/WEALTH/OFFICER (§8) | 十神 | Pillar.stem_ten_god（BAZI 已算，P0-1-C） | ✅ 直接消费 |
| COMB (§9) | 天干五合 | BaziChart.stem_he_pairs | ✅ 直接消费 |
| REL (§10) | 合/冲/刑/害/破/三合/三会 | branch_clash_map / branch_harm_map / branch_he_map / branch_sanhe_map / branch_sanxing_map / branch_po_pairs | ✅ 直接消费 |
| FLOW/QI/PARTY (§11-13) | 结构组合 | 由上游段中间状态推导 | ✅ 层内 |
| 时间层 (§25/§39) | 大运干支 + 起运 | BaziChart.luck_pillars (Pillar list) + start_age | ✅ 直接消费 |
| 时间层 流年/流月/流日 | 外部输入干支 | **Bazi 无此事实** — 属 caller 侧输入（V3.1 §25 设计即 overlay 注入，非 Bazi 职责） | ⚠️ 输入缺省→相关判断 UNDETERMINED (FACT_MISSING) |
| 节气司令 | 月令司令/节气交界 | 月支已由 Bazi 按节气切分（月支即月令）；节气交界 TRANSITIONAL 判定需节气时刻事实 | ⚠️ Bazi 无节气时刻事实 → LING-012 该分支按 EVIDENCE_UNVERIFIED/FACT_MISSING fail-closed，不得自行补算 |

## 二、NOT_AUTHORIZED 字段禁用清单（V3.1 §0.6 合规）

BaziChart 以下字段带 `authority_status=NOT_AUTHORIZED`（启发/辅助信号），**子平规则条件一律不得消费**：
- five_element_balance / five_element_imbalance（百分比口径，REV-FORBIDDEN 等价物）
- spouse_star / spouse_star_attack / spouse_star_strength / officer_mixed / peach_blossom
- 所有 calc_* 的 AUXILIARY_SIGNAL 派生

子平只消费：四柱、stem_ten_god、hidden_stems、branch_ten_gods、stem_branch_polarity、twelve_growth、
stem_he_pairs / stem_clash_pairs / branch_*_map / branch_po_pairs、kong_wang、nayin、shensha、
tai_yuan/tai_xi/ming_gong/shen_gong、luck_pillars、start_age、gender、birth_datetime。

## 三、时间层输入约定

大运：BaziChart.luck_pillars（十柱，Pillar.heavenly_stem/earthly_branch）。
流年/流月/流日：调用方在 TemporalOverlay 输入中提供干支；缺省 → §39 域 UNDETERMINED。
Overlay 生命周期：NATAL > LUCK > YEAR > MONTH > DAY（§73 REV-TEMPORAL-002），只叠加不改 Natal。

## 四、实施顺序（§43 对齐）

P0 FACT 适配 → P1 特殊格 → P2 月令/根/支持对立/众寡 → P3 气势源流顺逆 → P4 格局+病象+生克先后
→ P5 清浊真假+有情有力 → P6 寒暖燥湿+调候+病药+通关 → P7 身强 → P8 用神/用神变化/相神 →
P9 格局高低 → P10 喜忌 → P11 时间 overlay → §41 COVERAGE 门禁 + §27/§81 ARCH 门禁全绿。
