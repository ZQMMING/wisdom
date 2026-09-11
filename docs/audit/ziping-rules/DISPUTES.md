# 子平引擎 经典分歧矩阵（DISPUTES）— §40 / §75 完整 YAML

> 依《子平生产规则注册表 V3.1-FINAL》§75 REV-DISPUTE：每条分歧写完整 YAML（rule_a/rule_b/conflict_when/resolution/status），conflict_when 写具体触发条件，OPEN 项相关规则输出 METHOD_UNRESOLVED，禁止 Agent 自行融合。
> 原文双源印证：每条附『经典名·篇名 + passage_id』引文。单源处标 confidence=low。

## D-001 五行寄生十二宫（阳顺阴逆 vs 阴阳同宫）
- **status**：CLOSED（已裁决）
```yaml
dispute_id: D-001
rule_a:
  source: 《渊海子平》
  method_scope: yang_shun_yin_ni
  conditions: 十二长生阳干顺行阴干逆行
rule_b:
  source: 《滴天髓》/通行
  method_scope: yin_yang_same_palace
  conditions: 十干长生同宫排列
conflict_when: 计算阴干长生（如乙木长生在午 还是 阴干逆排）时
resolution:
  shuntian_rule: PENDING→已裁决：属 Bazi 基础事实，冻结于 Bazi Canonical Contract（§72 REV-GROWTH），ZiPing 只消费。VERIFY-007 CONFIRMED。
status: CLOSED
```
  - 原文：《渊海子平·外格类》YHZP_1575_P0：「亥卯未逢于甲乙，富贵无疑」

## D-002 调候取用（穷通专书 vs 三命兼论）
- **status**：OPEN
```yaml
dispute_id: D-002
rule_a:
  source: 《穷通宝鉴》
  method_scope: qiong_tong_bao_jian
  conditions: 寒暖燥湿专书取用（首用/次用）
rule_b:
  source: 《三命通会》
  method_scope: san_ming_tong_hui
  conditions: 兼论格局财官，同日主同月取用有出入
conflict_when: 同日干同月令，穷通『调候用神』与三命『财官喜用』结论不一致（如 甲午月：穷通用癸为主，三命以财官喜用论）
resolution:
  shuntian_rule: PENDING-DECISION：以穷通宝鉴为主（调候法），分歧条目列出；V3.1 §44 登记值与穷通原文出入 101 格，须按穷通 QTBJ_1460 修正。
status: OPEN
```
  - 原文：《穷通宝鉴·调候用神总表》QTBJ_1460_P0：「穷通宝鉴-AI知识库_全文 > 来源：穷通宝鉴-AI知识库.docx > 段落数：493，表格数：1 > 自动提取时间：2026-08-11 15:44 --- 穷通宝鉴 AI算命智能体知识库 —— 完整版 —— 第一部分：基础知识 一、五行总论 二、十干体性概述 三、调候用神原理 第二部分：十干论命详解 一、甲木论（总论+正月至十二月） 二、乙木论（总论+正月至十二月） 三、丙火论（总论+正月至十二月） 四、丁火论（总论+正月至十二月」
  - 原文：《三命通会·论墓库》SMTH_0001_P0：「八、财富论 财星为用：财星旺而身旺，能任财，主富 财星入库：逢冲开库之年发财 财多身弱：富屋贫人，财多而难得 身旺财旺：白手起家，财源滚滚 九、功名论 官星为用：官星清正，身旺能任，主贵 杀印相生：武贵功名 官印相生：文贵功名 伤官伤尽：宜武职 文昌学堂：利科举 ═══════════════════════════════════════════════════════════════ 卷十一·六甲趋干与六壬趋艮 ══════════」

## D-003 专旺格成立宽严（外格类 vs 形象）
- **status**：OPEN
```yaml
dispute_id: D-003
rule_a:
  source: 《渊海子平》
  method_scope: yuan_hai_zi_ping
  conditions: 全X无克即成专旺（外格类）
rule_b:
  source: 《滴天髓》
  method_scope: di_tian_sui
  conditions: 形象：有破象之神则象破不成（五气聚而成形，形不可害）
conflict_when: 某五行专旺但局中见克该行之神（全木见金、全火见水等），成格与否判定分歧
resolution:
  shuntian_rule: PENDING-DECISION：method_scope=disputed，§47 附录D 逐格独立五态（Required/Forbidden/Formation/Failure/Rescue）核证后裁定。
status: OPEN
```
  - 原文：《渊海子平·外格类》YHZP_0001_P0：「曲直仁寿格：全木，无金克」
  - 原文：《滴天髓·形象》DTS_0398_P0：「五氣聚而成形，形不可害也」

## D-004 从格条件宽严（有根可否从）
- **status**：OPEN
```yaml
dispute_id: D-004
rule_a:
  source: 《渊海子平》
  method_scope: yuan_hai_zi_ping
  conditions: 弃命从财须要会财 / 弃命从杀须要会杀（须会局）
rule_b:
  source: 《滴天髓》
  method_scope: di_tian_sui
  conditions: 五阳从气不从势；有印比帮身则不从（有根不从）
conflict_when: 日主微弱但微有印比/根气时，是否仍可从（从财/从杀/从儿）判定分歧
resolution:
  shuntian_rule: PENDING-DECISION：V3.1 §63 主导条件树（月令归属+透干+有效根+生化链+无有效反制+破从条件不成立），破从条件逐条核证后裁定。
status: OPEN
```
  - 原文：《渊海子平·从财》YHZP_2148_P0：「弃命从财，须要会财」
  - 原文：《滴天髓·从化》DTS_0261_P0：「五陽從氣不從勢，五陰從勢無情義」

## D-005 墓库开库（冲刑开 vs 合闭）
- **status**：OPEN
```yaml
dispute_id: D-005
rule_a:
  source: 《三命通会》
  method_scope: san_ming_tong_hui
  conditions: 逢冲开库（入库逢冲开库之年发财）
rule_b:
  source: 《渊海子平》
  method_scope: yuan_hai_zi_ping
  conditions: 合则闭库，刑冲须看藏干透否
conflict_when: 墓支（辰戌丑未）逢冲/刑/合时，开库 vs 闭库 判定（冲开 vs 合闭并存按 §30 INORDER 判先后）
resolution:
  shuntian_rule: PENDING-DECISION：§45/§66 STORE/REV-STORE 逐条补录原文后裁定；STORE-014 冲合并存按 §30 生克先后。
status: OPEN
```
  - 原文：《三命通会·论墓库》SMTH_0001_P0：「八、财富论 财星为用：财星旺而身旺，能任财，主富 财星入库：逢冲开库之年发财 财多身弱：富屋贫人，财多而难得 身旺财旺：白手起家，财源滚滚 九、功名论 官星为用：官星清正，身旺能任，主贵 杀印相生：武贵功名 官印相生：文贵功名 伤官伤尽：宜武职 文昌学堂：利科举 ═══════════════════════════════════════════════════════════════ 卷十一·六甲趋干与六壬趋艮 ══════════」

## D-006 建禄月刃取用次序
- **status**：OPEN
```yaml
dispute_id: D-006
rule_a:
  source: 《子平真诠》
  method_scope: ziping_zhenquan
  conditions: 建禄用官，月劫用财（建禄月劫格透官逢财印/透财逢食伤）
rule_b:
  source: 《渊海子平》
  method_scope: yuan_hai_zi_ping
  conditions: 建禄月刃另取法，喜忌不同（外格类羊刃架杀等）
conflict_when: 月令本气为比肩（建禄）或劫财（月刃）时，取官/杀/财/印之次序分歧
resolution:
  shuntian_rule: PENDING-DECISION：§15.7/15.8 PATTERN-建禄/月刃 + §55 十项逐格核证后裁定。
status: OPEN
```
  - 原文：《子平真诠·建禄月劫》PZZQ_0142_P0：「阳刃透官煞而露财印,不⻅伤官,阳刃格成也」
  - 原文：《渊海子平·建禄》YHZP_0001_P0：「（二）从格（特殊格局）：从格是指日干极弱或极旺，无法从自身五行取用，只能顺从命局中最旺的五行」

> OPEN 项处理（§75 REV-DISPUTE-003）：相关规则输出 METHOD_UNRESOLVED，禁止自行融合；User 裁决后 method_scope 全局固化、status=CLOSED（REV-DISPUTE-004）。
