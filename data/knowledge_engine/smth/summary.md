# 三命通会 (SMTH) 知识工程候选数据摘要

生成时间：2026-09-14
底本：`SMTH_三命通会_清洗版.md`（SHA256 前 8 = 9e71d67d，行数 23734，已复验）

## 一、总量统计

| 指标 | 数值 |
|---|---|
| Source 总数 | 1488 |
| Rule 候选总数 | 193 |
| unformalizable 总数 | 352 |

## 二、章节覆盖

- 共处理 **381** 章（001–381），第 0 章（目录）整章跳过。
- 跳过：文件头元信息块（行 1–6）、书名行与现代简介（行 7–13）、第 0 章目录（行 14–433）。
- 注：本底本全书无空行，故每个分区（原 文/白话译文/关键词/现代启示）各成一条 Source；Rule 绑定在 ORIGINAL 分区 Source 上。

## 三、text_layer 分布

| text_layer | 数量 |
|---|---|
| ORIGINAL | 381 |
| LATER_COMMENTARY | 1107 |
| ANNOTATION | 0 |
| UNVERIFIED | 0 |

（全书未检出段首注解标记。）

## 四、rule_type 分布

| rule_type | 数量 |
|---|---|
| definition | 141 |
| activation | 50 |
| resolution | 1 |
| diagnosis | 1 |

规则以 activation（合冲刑害、神煞生效条件）为主、definition（干支/神煞/十二长生定义）为辅，符合 SMTH 底本特点。

## 五、抽样 Rule 候选（3 条，原文对照）

### 抽样 1：CAND-SMTH-001

```json
{
  "rule_id": "CAND-SMTH-001",
  "engine": "SANMING_TONGHUI",
  "source_id": "SMTH-014-001",
  "rule_type": "definition",
  "scope": "natal",
  "preconditions": {"type": "conjunction", "conditions": [{"field": "stem", "operator": "equals", "value": "甲"}]},
  "operation": "emit",
  "outputs": [{"field": "stem_yinyang", "value": "阳"}],
  "evidence_requirement": "A",
  "status": "CANDIDATE",
  "notes": "《三命通会》论天干阴阳生死：甲为阳干"
}
```

对应原文（SMTH-014-001, ORIGINAL）：

> …甲木乃十干之首，主宰四时，生育万物；在天为雷为龙，在地为梁为栋，谓之阳木。其禄到寅…长生于亥…故甲木死于午。经云：木不南奔。

### 抽样 2：CAND-SMTH-051

```json
{
  "rule_id": "CAND-SMTH-051",
  "engine": "SANMING_TONGHUI",
  "source_id": "SMTH-041-001",
  "rule_type": "definition",
  "scope": "natal",
  "preconditions": {"type": "conjunction", "conditions": [{"field": "stem", "operator": "equals", "value": "甲"}]},
  "operation": "emit",
  "outputs": [{"field": "jinyu_branch", "value": "辰"}],
  "evidence_requirement": "B",
  "status": "CANDIDATE",
  "notes": "《三命通会》论金舆：金舆居禄前二辰，甲在辰"
}
```

对应原文（SMTH-041-001, ORIGINAL）：

> 故金舆常居禄前二辰，如甲子人禄在寅，辰为金舆是也。…紫虚局云："禄前二辰号金舆，遇此之人福最殊。"

### 抽样 3：CAND-SMTH-100

```json
{
  "rule_id": "CAND-SMTH-100",
  "engine": "SANMING_TONGHUI",
  "source_id": "SMTH-037-001",
  "rule_type": "activation",
  "scope": "natal",
  "preconditions": {"type": "conjunction", "conditions": [{"field": "branch", "operator": "equals", "value": "申"}, {"field": "target_branch", "operator": "equals", "value": "亥"}]},
  "operation": "emit",
  "outputs": [{"field": "branch_six_harm", "value": "申亥害"}],
  "evidence_requirement": "A",
  "status": "CANDIDATE",
  "notes": "《三命通会》论六害：申与亥相害"
}
```

对应原文（SMTH-037-001, ORIGINAL）：

> 申亥相害者，谓名恃临官，竞嫉才能，争进相害。故申见亥，亥见申均为害…

## 六、产出文件

- `sources.jsonl` — 1488 行
- `rules_candidate.jsonl` — 193 行
- `unformalizable.jsonl` — 352 行
- `qa_report.md` / `summary.md`
