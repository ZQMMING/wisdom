# QTBJ《穷通宝鉴》知识工程 · 交付摘要（Candidate）

## 一、交付物（D:\shuntian\data\knowledge_engine\qtbj\）

| 文件 | 行数 | 说明 |
|---|---|---|
| `sources.jsonl` | 4368 | SourceRecord，UTF-8 无 BOM |
| `rules_candidate.jsonl` | 113 | RuleCandidate，rule_id 从 CAND-QTBJ-001 起 |
| `unformalizable.jsonl` | 13 | 总论描述性段落 + 命造说明，交 Human 裁定 |
| `qa_report.md` | — | 21 项质检逐项结果 |
| `summary.md` | — | 本文件 |

## 二、底本复验

- 底本：`D:\顺天系统资料\豆包资料\六部经典校对版\QTBJ_穷通宝鉴_清洗版.md`
- SHA256 前 8：**1830fe93** ✓（与规范一致）
- 行数：**9171** ✓（与规范一致）
- 跳过：文件头 1–15 行；第 0 章目录（第 16–156 行，spec §2.3）。

## 三、切分统计

- 章节：第 1–113 章全部覆盖（章号多位数中间含空格如 `第 1 0 章`，已归一匹配）。
- text_layer 分布：
  - ORIGINAL 原文：1507
  - ANNOTATION 徐乐吾注：1399（原文区内段首 `徐乐吾曰：/徐乐吾曰:` 全部识别，不从其提取 Rule）
  - LATER_COMMENTARY 白话译文/关键词/现代启示：1462
- 段落分隔：底本无空行、硬换行约 40 字/行，采用"上一行以句末标点（。！？；…）结尾则分段"的启发式；source_text 录入时段内换行归一为连续文本，逐字未改。

## 四、Rule 提取

- 共 **113** 条：111 条"日干 × 月令"调候用神矩阵项（rule_type=definition，scope=natal，operation=emit）+ 2 条"活木/死木"定义（subject=wood_state）。
- preconditions 一律 conjunction：`day_stem equals X` + `month_branch equals/in Y`。
- 合月章用 `month_branch in [...]`：
  - 丁火：八九月丁火拆为酉、戌两条；十一、十二月丁火 = in[子,丑]
  - 戊土：正二月 = in[寅,卯]；十一、十二月 = in[子,丑]
  - 己土：四五六月 = in[巳,午,未]；七八九月 = in[申,酉,戌]；十十一十二月 = in[亥,子,丑]
  - 甲木：五、六月甲木拆为午、未两条
- output field = `diao_hou_yong_shen`（活木/死木为 `wood_state`），value 保留原著用语（如"先取庚金，次用壬水"），不评分、不统一用神、不跨经典。

## 五、矩阵覆盖度

- 实际矩阵为 **10 天干 × 12 月令 = 120 格**（天干只有 10 个：甲乙丙丁戊己庚辛壬癸；任务书预估的 144 系按 12 日干推算，特此更正）。
- **覆盖 120/120 = 100%**，无空格。
- 总论章（甲木总论、论土、庚金总论、壬水总论）不对应具体月令，其描述性文字入 unformalizable，未强套矩阵。

## 六、质检（spec §8 全部 21 项）

- **通过 21 / 失败 0**。关键项：
  - source_id / rule_id 唯一 ✓
  - 所有 Rule 的 source_id 均存在且其 text_layer == ORIGINAL ✓
  - preconditions 无嵌套、无 `>` `<` 比较符、operator 全部在白名单 ✓
  - **source_text 在换行归一后与底本逐字子串比对 100% 命中** ✓
  - 无跨经典引述、无"用神=X"统一结论、无评分字段 ✓

## 七、抽样对照（5 条）

### 1. CAND-QTBJ-001（正月甲木）
- Rule：IF day_stem=甲 AND month_branch=寅 THEN diao_hou_yong_shen="丙火为主，癸水次之（癸藏丙透为寒木向阳）"
- 原文（QTBJ-002-001）：「正月甲木，初春尚有余寒，得丙癸逢，富贵双全。癸藏丙透，名寒木向阳，主大富贵。倘风水不及，亦不失儒林俊秀。如无丙癸，平常人也。」

### 2. CAND-QTBJ-035（十一月丙火）
- Rule：IF day_stem=丙 AND month_branch=子 THEN diao_hou_yong_shen="壬水为最，戊土佐之"
- 原文（QTBJ-035-001）：「十一月丙火，冬至一阳生，弱中复强，壬水为最，戊土佐之。」

### 3. CAND-QTBJ-096（九月壬水）
- Rule：IF day_stem=壬 AND month_branch=戌 THEN diao_hou_yong_shen="用丙火，甲制戌戊，戊出干为辅"
- 原文（QTBJ-098-001）：「九月壬水，亥水进气，其性将厚。若一派壬水，见一甲制戌中之戊，又见一戊出干，斯用丙火，此格清贵极矣……」

### 4. CAND-QTBJ-109（十月癸水）
- Rule：IF day_stem=癸 AND month_branch=亥 THEN diao_hou_yong_shen="宜用庚辛"
- 原文（QTBJ-111-001）：「十月癸水，旺中有弱……宜用庚辛为妙。」

### 5. CAND-QTBJ-112（活木定义）
- Rule：IF day_stem=甲 AND month_branch in [戌,亥,寅,卯,辰,巳] THEN wood_state="活木"
- 原文（QTBJ-001-001）：「甲戌、乙亥、木之源。甲寅、乙卯、木之乡。甲辰、乙巳、木之生。皆活木也。」（同段另有死木规则 CAND-QTBJ-113）

## 八、约束遵守

- 只落盘 `D:\shuntian\data\knowledge_engine\qtbj\`，未 commit、未 push、未动 `D:\shuntian\data\classics\original\`。
- 未改原著一字、未评分、未跨经典优先级；Rule 全部 CANDIDATE，待 Human 审批。
