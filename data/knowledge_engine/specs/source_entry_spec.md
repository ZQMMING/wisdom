# Source 录入规范 v1.0（六部经典 · 知识工程 Agent）

本规范是《知识工程 Agent 施工方案》第七节的可执行细化。唯一底本、切分标记、命名规则、text_layer 判定均在此写死，执行者不得自行发明。

## 1. 唯一合法底本

> ⚠️ 路径变更记录（2026-09-14）：原计划使用 `D:\shuntian\data\classics\original\` 下六个 `_完整全文.md`，但该目录今晨 05:33 被另一进程整体替换为"现代知识梳理体"（hash 全部漂移，内容为现代白话整理稿，非古文原文）。为避免冲突不回写该目录，**施工底本改指向下表的本地清洗版**，SHA256 与行数与已确立事实完全一致。任何人若后续要恢复 `D:\shuntian\data\classics\original\`，以本表路径为恢复源。

| 书代号 | 中文书名 | 底本文件（本地清洗版） | SHA256前8 | 行数 | engine 字段 |
|---|---|---|---|---|---|
| YHZP | 渊海子平 | `D:\顺天系统资料\豆包资料\六部经典校对版\YHZP_渊海子平_清洗版.md` | 853582d6 | 18007 | `YUHAI_ZIPING` |
| PZZQ | 子平真诠 | `D:\顺天系统资料\豆包资料\六部经典校对版\PZZQ_子平真诠_清洗版.md` | cbda0c0d | 5185 | `ZIPIN_ZHENQUAN` |
| DTS  | 滴天髓   | `D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓_清洗版.md`  | e9a2021f | 6551 | `DI_TIAN_SUI` |
| QTBJ | 穷通宝鉴 | `D:\顺天系统资料\豆包资料\六部经典校对版\QTBJ_穷通宝鉴_清洗版.md` | 1830fe93 | 9171 | `QIONGTONG_BAOJIAN` |
| SMTH | 三命通会 | `D:\顺天系统资料\豆包资料\六部经典校对版\SMTH_三命通会_清洗版.md` | 9e71d67d | 23734 | `SANMING_TONGHUI` |
| SFTK | 神峰通考 | `D:\顺天系统资料\豆包资料\六部经典校对版\SFTK_神峰通考_OCR校对版.md` | 0091619f | 7358 | `SHENFENG_TONGKAO` |

铁律：`source_text` 必须逐字取自上表底本（含标点、括号、错字），不改字、不删字、不补字、不做校勘、不做繁简转换。任何 Rule 的 evidence 必须能回溯到唯一 `source_id`。
严禁使用 `D:\shuntian\data\classics\original\` 下当前的"知识梳理体"文件（hash 已漂移，非古文）；严禁使用 `D:\shuntian\data\sources\` 下旧产物作为内容来源。
严禁引入任何 luckclub / QQ 群 / 收费广告 / 页码 / 空《》行。

## 2. 文件级预处理（每部统一）

底本头部结构固定，按以下规则跳过：
1. 文件开头到第一个 `---`（含）：markdown 元信息块（`# 标题`、`> 引用`），**不录入**。
2. 紧随其后的书名行与一段现代简介（"《xxx》是……"）：**不录入**（现代整理者撰写，非原文）。
3. `第 0 章` / `目录` 整章：**不录入**（目录索引，无原文规则）。
   - 跳过项必须在该部 `qa_report.md` 中逐项记录跳过了哪些行范围。
4. 正文从 `第 1 章` 起。

## 3. 章节切分

- 章节边界：行首匹配 `^第\s*(\d+)\s*章\s*$`（如 `第 1 章`、`第 2 章`）。
- 章节标题：紧随其后的那一行（如 `论五行所生之始`），写入 `chapter` 字段。
- `CHAPTER` 编号：用 `第 N 章` 中的 N，三位零填充：`001`、`002`……
- 章内分区标记（行首独立出现）：
  - `原 文`（或 `原文`）：进入原文区
  - `白话译文`：进入现代译文区
  - `---`：分隔线
  - `关键词`：现代关键词解释区
  - `现代启示`：现代评论区
- 段落：在当前区内，按**空行**切分自然段落。一段 = 一条 Source。段落内换行不合并、不重排，保留原文换行后的文字；但录入 `source_text` 时把段落内换行与全角空格规范化为原文连续文本（保留原有标点），不得增删语义字符。

## 4. text_layer 判定（四选一）

只在 `原 文` 区内判 ORIGINAL / ANNOTATION；区外一律 LATER_COMMENTARY。

| 条件（行首） | text_layer |
|---|---|
| 段首匹配 `眉批：` 或 `【眉批】`（YHZP） | `ANNOTATION` |
| 段首匹配 `**【徐注】**` 或 `【徐注】`（PZZQ） | `ANNOTATION` |
| 段首匹配 `**【原注】**`（DTS 刘诚意原注） | `ANNOTATION` |
| 段首匹配 `【任氏曰】`（DTS 任铁樵注）；其后紧跟的任氏解说段落亦为 ANNOTATION | `ANNOTATION` |
| `白话译文` / `关键词` / `现代启示` 区内全部段落 | `LATER_COMMENTARY` |
| 原文区其余段落 | `ORIGINAL` |
| 无法判定（混排、标记缺失、古今文字同段无标记） | `UNVERIFIED` |

- ANNOTATION 条目照常录入 Source，但**不从 ANNOTATION 提取 Rule**（见 Rule 规范第 2 节）。
- UNVERIFIED 条目录入 Source，notes 写明无法判定原因，交 Human 裁定。
- 若同一物理段同时含原文与眉批且无法干净切分：整段标 `UNVERIFIED`，不得自行拆分。

## 5. 字段命名规则

以 `<B>` = 书代号大写（YHZP/PZZQ/DTS/QTBJ/SMTH/SFTK），`<b>` = 小写（yhzp/pzzq/dts/qtbj/smth/sftk），`<CHAP>` = 三位章节号，`<IDX>` = 段内三位序号（从 001 起，章内递增）。

| 字段 | 格式 | 示例 |
|---|---|---|
| `source_id` | `<B>-<CHAP>-<IDX>` | `YHZP-001-001` |
| `text_id` | `<B>-T-<CHAP>-<IDX>` | `YHZP-T-001-001` |
| `resource_id` | `SRC-<B>-<CHAP>`（每章一个 resource） | `SRC-YHZP-001` |
| `logical_uri` | `source://<b>/<CHAP>/<IDX>` | `source://yhzp/001/001` |
| `relative_path` | `sources/<b>/chapter_<CHAP>.md` | `sources/yhzp/chapter_001.md` |
| `engine` | 见第 1 节表 | `YUHAI_ZIPING` |
| `book` | 中文书名 | `渊海子平` |
| `chapter` | 章节标题（原文行） | `论五行所生之始` |
| `version` | 固定 | `1.0.0` |
| `status` | 固定 | `CANDIDATE` |
| `source_text` | 逐字原文 | （不改一字） |

## 6. SourceRecord 完整 Schema（方案第十节，字段不得增删）

```json
{
  "source_id": "YHZP-002-001",
  "engine": "YUHAI_ZIPING",
  "book": "渊海子平",
  "chapter": "论五行所生之始",
  "text_id": "YHZP-T-002-001",
  "text_layer": "ORIGINAL",
  "source_text": "盖闻天地未判……",
  "resource_id": "SRC-YHZP-002",
  "logical_uri": "source://yhzp/002/001",
  "relative_path": "sources/yhzp/chapter_002.md",
  "version": "1.0.0",
  "status": "CANDIDATE"
}
```

`notes` 字段仅在 UNVERIFIED / 含混排时使用，写不超过 40 字原因；其余条目不要加 notes。
