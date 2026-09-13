# B4-SFTK 批次执行报告（BOT-KNOWLEDGE）

> 任务单：BOT-MASTER → B1-YHZP + B4-SFTK 并行
> 分支：agent/knowledge-b1-yhzp ｜ BASE COMMIT：345769dc
> ENGINE：SHENFENG_TONGKAO ｜ 经典：《神峰通考》（明·张楠）
> 日期：2026-09-14

---

## 一、底稿变更声明（重要）

本批基于**当前冻结原典**生成，而原典已被替换为「完整版本」：

- 原典：`data/classics/original/SFTK_神峰通考_完整全文.md`
- 当前版本：**国图扫描·Qianfan-OCR 校对版**（NLC511-027032013020556，繁体，7,358 行）
- 冻结 hash（SHA-256）：`0091619fe0d9`
- **本批次 69 条 source 的 `file_hash` 全部绑定到该 hash，已独立验证 MATCH。**

## 二、CHANGED FILES（仅 ALLOWED PATHS 内）

| 文件 | 状态 | 说明 |
|------|------|------|
| `data/sources/sftk_sources.jsonl` | 重写 | Source Registry 候选，**69 条** |
| `data/rules/candidate/CAND-SFTK_rules.jsonl` | 重写 | Rule 候选，**31 条** |
| `docs/bots/BOT-KNOWLEDGE/B4-SFTK_report.md` | 新增 | 本报告 |

未 commit（按任务单约定，由 BOT-MASTER 代为提交）。

## 三、统计

### Source（69 条）
- 粒度：按「卷→类/说/格/论/赋（章节）」聚合，**非逐段过细**（OCR 版章节多为裸短行标题 + `## ` 标题混排）。
- 卷分布：卷一（八法/说类/格论断主体）→ 卷二~卷三（诸格）→ 卷四（图诀/泛论/歌断）→ 卷五（小运定局/独步/捷径赋/身弱论）→ 卷六（赋/论/集说）。
- text_layer 分布：`ORIGINAL` 69（张楠自撰八法、病药、格论断、图诀、赋歌，均为作者原文）。
- evidence_grade：A（ORIGINAL 硬绑定）。
- source_id 用 `SEC%03d` 顺序编号（ASCII，无中文），中文名保留在 `source_location.path[].name`。

### Rule 候选（31 条）
- definition 21 / resolution 10，以 definition 为主。
- 八法定义 9（病药/雕损/枯涸/弱陷/旺亢/损益/动静/盖头/六亲说）。
- 格局定义 12（正官/偏官/月支正财/杂气财官印绶/金神/井欄叉/夾丘拱財/專財/陽刃/十天干体象/五行元理消息赋/一行禅师天元赋）。
- 用神 resolution 10（有病去病/杀印相生/伤官配印/喜忌取用/定格局/十干从化/身弱取扶/弃命从杀/阴阳通变/泛论取用）。
- 全部绑定真实 source_id，**无悬空**（QC 验证 unbound_refs=0）。
- evidence_requirement 统一 C；算子仅 `equals/in/not_in/exists/not_exists`，无 `> < >= <=`。

## 四、质检结果（独立脚本 `_tmp_sftk/final_qc.py`）

- source_id 唯一：dup=0 ✓
- resource_id 一一对应（`SRC-`+source_id）：✓
- 无绝对路径（D:/ C:\\）：✓
- 无违禁算子：op/abs-path violations=0 ✓
- Rule→Source 绑定：unbound_refs=0，empty_source_ids=0 ✓
- evidence_grade 与 text_layer 硬绑定：A=A ✓
- `file_hash` 与磁盘一致：SFTK=`0091619fe0d9` MATCH ✓

## 五、底稿来源说明

- **原文**：明·张楠（临川西溪逸叟）撰《神峰通考》（又名《命理正宗》），八法/病药/雕枯旺弱四病/损益生长四药/动静/盖头/六亲诸说类 + 诸格论断 + 图诀 + 赋歌。
- **提取渠道**：国家图书馆扫描版 NLC511-027032013020556，Qianfan-OCR 校对（2026-09-14）。
- **OCR 特性**：繁体，章节标题多为裸短行，部分带 `## ` 前缀；页脚 `===== 第 N 页 =====` 与「神峰通考 卷X」running header 已在 source_text 中剔除；卷首目录区（LATER_COMMENTARY）未单列 source（属整理排版，非张楠正文）。
- **叙（张楠自叙）**：已录入（SEC001），text_layer=ORIGINAL（作者本人序言）。

## 六、遗留 / 交 Human

- 69 条 source 全部 ORIGINAL，但 OCR 校对可能引入错字，`handling_status=RESOLVED`，建议 Human 抽验（尤其八法/病药核心段）。
- 卷五/卷六部分赋歌（講命捷徑賦/萬尙書瓊璣三盤賦/節氣歌斷/論諸格有救）是否全部独立成节，verifier 显示部分仅在 TOC 出现，本批按「正文在列才录入」原则取舍，未录入者可在下批补。
