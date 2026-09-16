# Rule 提取规范 v1.0（六部经典 · 知识工程 Agent）

本规范是《知识工程 Agent 施工方案》第八节的可执行细化。Rule 候选只翻译原著陈述，不创造、不审批。

## 1. 什么算一条 Rule

可形式化为 **IF-THEN** 结构的原著陈述。即：在某个命局条件下，必然推出某个结论 / 要求某个操作。

正例（《渊海子平》类）：
- "官逢财印，又无刑冲破害，官格成也"
  → IF 十神=正官格 AND 天干有财 AND 天干有印 AND 无刑冲克害 THEN 成格（output: `pattern_status = 成`）
- "甲日见庚金，为七杀"
  → IF day_stem=甲 AND target_stem=庚 THEN output ten_god=七杀

## 2. 什么不算 Rule（不提取，原样留在 Source）

- 纯描述性 / 宇宙论铺垫（"夫五行者……""盖闻天地未判……"）
- 举例性文字（"如甲木……""且如某造……"）——除非原文明确说"凡如此者皆……"
- 歌赋、韵文、口诀中含义混糅、无法拆出干净 IF-THEN 的整段
- 含混多义、一词多指、无确定算子可写的句子
- **来自 ANNOTATION / LATER_COMMENTARY / UNVERIFIED 条目的任何陈述**（Rule 只绑定 text_layer=ORIGINAL 的 source_id）
- 现代整理者的"现代启示""关键词"——永不提取

无法形式化的句子不丢弃：逐条写入该部 `unformalizable.jsonl`，字段 `{source_id, raw_text, reason}`，交 Human 裁定，禁止猜测补全。

## 3. RuleCandidate Schema（方案第十节，字段不得增删）

```json
{
  "rule_id": "CAND-YHZP-001",
  "engine": "YUHAI_ZIPING",
  "source_id": "YHZP-002-003",
  "rule_type": "definition",
  "scope": "natal",
  "subject": "ten_god",
  "predicate": "is",
  "preconditions": {
    "type": "conjunction",
    "conditions": [
      {"field": "day_stem", "operator": "equals", "value": "甲"},
      {"field": "target_stem", "operator": "equals", "value": "庚"}
    ]
  },
  "operation": "emit",
  "outputs": [
    {"field": "ten_god", "value": "七杀"}
  ],
  "evidence_requirement": "A",
  "status": "CANDIDATE",
  "notes": "《渊海子平》卷一论十神"
}
```

## 4. 字段白名单

### rule_type（按方案第五节，从原著实际陈述选一个）
- `definition`：基础定义、十神、六亲、宫位、神煞定义、日干×月令矩阵项
- `resolution`：格局成败、用神取舍、旺衰根气判定
- `activation`：关系激活（合冲刑害、神煞生效条件）
- `effectiveness`：旺衰、气势、强弱对结论的影响
- `diagnosis`：病药之"病"、动静之偏、盖头之失
- `medicine`：病药之"药"、制伏、补救

### scope
- `natal`（本命四柱，默认）
- `decade`（涉及大运）
- `year`（涉及流年）
- 原文只谈本命结构 → `natal`。

### preconditions
- `type`：`conjunction`（AND）或 `disjunction`（OR）。不允许嵌套（无嵌套 Rule、无嵌套 condition 树）。
- `operator` 白名单（**严禁 `>` `<` `>=` `<=` `>` `contains_gt` 等比较符**）：
  - `equals` / `not_equals`
  - `in`（value 为数组，如 `{"field":"branch","operator":"in","value":["申","子","辰"]}`）
  - `has`（命局中存在某元素，value 为字段名或标签）
  - `absent`（命局中不存在某元素，与 `has` 配对）
- 所有 field 必须是稳定的命理字段名（用 snake_case：`day_stem`、`day_branch`、`month_branch`、`year_stem`、`hour_branch`、`ten_god`、`pattern`、`stem`、`branch`、`hidden_stem`、`na_yin`、`shen_sha`……）。不要用原文整句当 field。

### operation 白名单
- `emit`：产出一个结论 / 标签（最常用）
- `require`：要求命局必须满足某条件才算成立
- `suppress`：否定 / 禁止某情形

### outputs
- 数组，每项 `{"field": <snake_case 字段名>, "value": <字符串>}`。
- value 用原著用语（如"七杀""正官格""成""败""吉""凶"），不翻译成现代术语。

### evidence_requirement
- `A`：原文直接、明确陈述（"甲日见庚为七杀"）
- `B`：原文需一步直译（"官逢财印无刑冲，官格成" → 拆为三个 preconditions）
- `C`：原文为口诀/赋文，需轻度归一但仍可忠实翻译；notes 里写清楚归一理由

### status
- 一律 `"CANDIDATE"`。不得自行改为 APPROVED。

### notes
- 简短溯源说明，如"《渊海子平》卷一·论天干"。不超过 40 字。

## 5. rule_id 命名

- 格式：`CAND-<B>-<NNN>`，`<NNN>` 三位顺序号，从 `001` 起，**整部书内连续递增**，不按章重置。
- 例：`CAND-YHZP-001`、`CAND-YHZP-002`……

## 6. 提取纪律（对应方案第九节）

- 不得添加 Source 中没有的条件；不得删除 Source 中有的条件；不得改写 Source 逻辑。
- 不得用现代命理文章、现代术语替代原著。
- 不得跨经典引述；不得建立跨经典优先级。
- 不得统一用神；不得评分；不得打"吉凶"分数；不得引入 LLM 的主观判断。
- 一条 Source 可对应 0..n 条 Rule；若一条原文含多个独立 IF-THEN（如"正官格成……败……"），拆成多条 Rule，各自绑定同一 source_id。
- 歌赋整段若含可抽出的散句（如"官逢财印……"），按散句抽；整段不可拆则写入 unformalizable。

## 7. 输出物（每部，落盘到 `D:\shuntian\data\knowledge_engine\<b>\`）

| 文件 | 内容 |
|---|---|
| `sources.jsonl` | 每行一条 SourceRecord，UTF-8，无 BOM |
| `rules_candidate.jsonl` | 每行一条 RuleCandidate，UTF-8，无 BOM |
| `unformalizable.jsonl` | `{source_id, raw_text, reason}` 每行一条 |
| `qa_report.md` | 逐项质检结果（见第 8 节） |
| `summary.md` | 给 Human 看的可读摘要（条数、章节覆盖、抽样 3-5 条 Rule 展示） |

只落盘 jsonl 与上述 md；**不写入正式 Registry、不 git commit、不 push**。

## 8. 质检脚本必须自证的检查项

Source：
- [ ] `source_id` 全文件唯一
- [ ] `text_layer` ∈ {ORIGINAL, ANNOTATION, LATER_COMMENTARY, UNVERIFIED}
- [ ] 无绝对路径：`source_text` 不得含 `D:\`、`C:\`、`http`、`www.`
- [ ] 无水印广告：不得含 `luckclub`、`qq群`、`QQ群`、`收费50`、`技术支持`
- [ ] 无 Unicode 替换符 `\uFFFD` 及其他异常控制字符
- [ ] `source_text` 能在底本文件中检索到逐字子串（抽样 ≥ 20% 自动比对，100% 开头 20 字能命中）

Rule：
- [ ] `rule_id` 唯一，且以 `CAND-<B>-` 开头
- [ ] 每条 Rule 的 `source_id` 都在 sources.jsonl 中存在
- [ ] 每条 Rule 绑定的 Source 其 `text_layer == ORIGINAL`
- [ ] `preconditions.type` ∈ {conjunction, disjunction}
- [ ] 每条 condition 的 `operator` ∈ 第 4 节白名单
- [ ] 无 `>` `<` `>=` `<=` 出现
- [ ] 无嵌套 preconditions（无 `conditions` 套 `conditions`）
- [ ] `operation` ∈ {emit, require, suppress}
- [ ] `outputs` 每项都有 `field` 与 `value`
- [ ] `status == "CANDIDATE"`

整体：
- [ ] 无跨经典引述（单部 Rule 的 notes 不提及其他书名作为依据）
- [ ] 无"用神=X"这种统一用神结论
- [ ] 无评分字段（score/weight/point）
- [ ] 质检脚本自身跑通，输出每项 ✓/✗ 与失败计数
