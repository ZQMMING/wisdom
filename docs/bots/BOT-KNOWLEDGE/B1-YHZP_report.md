# B1-YHZP 批次执行报告（BOT-KNOWLEDGE）

> 任务单：BOT-MASTER → B1-YHZP + B4-SFTK 并行
> 分支：agent/knowledge-b1-yhzp ｜ BASE COMMIT：345769dc
> ENGINE：YUHAI_ZIPING ｜ 经典：《渊海子平》
> 日期：2026-09-14

---

## 一、底稿变更声明（重要）

本批基于**当前冻结原典**生成，而原典已被替换为「完整版本」：

- 原典：`data/classics/original/YHZP_渊海子平_完整全文.md`
- 当前版本：**2026-09-14 完整版**（宋·徐升整理，luckclub 古籍典藏提取，305 章节，777 页，含原文+白话译文+现代启示）
- 冻结 hash（SHA-256）：`853582d61b8a`（21,122 → 18,007 行，CRLF）
- **本批次 305 条 source 的 `file_hash` 全部绑定到该 hash，已独立验证 MATCH。**

## 二、CHANGED FILES（仅 ALLOWED PATHS 内）

| 文件 | 状态 | 说明 |
|------|------|------|
| `data/sources/yhzp_sources.jsonl` | 重写 | Source Registry 候选，**305 条** |
| `data/rules/candidate/CAND-YHZP_rules.jsonl` | 重写 | Rule 候选，**143 条** |
| `docs/bots/BOT-KNOWLEDGE/B1-YHZP_report.md` | 重写 | 本报告 |

未 commit（按任务单约定，由 BOT-MASTER 代为提交）。

## 三、统计

### Source（305 条）
- 粒度：按「章→篇（段）」聚合，**非逐段过细**。
- 305 章节 = 卷一~卷五，第 0 章（目录）+ 第 1~304 章。
- text_layer 分布：
  - `ORIGINAL` 304（宋·徐升《渊海子平》古典正文，含眉批/附注古注未拆分）
  - `UNVERIFIED` 1（第 0 章目录区，交 Human 裁定）
- evidence_grade 与 text_layer 硬绑定：A(ORIGINAL) 304 / D(UNVERIFIED) 1。
- 眉批/附注未拆分者标 `handling_status = NEEDS_REVIEW`，其余 `RESOLVED`。

### Rule 候选（143 条）
- 以 definition 为主（135），resolution 8。
- 主题覆盖：十神定义、十神×日干五行、地支关系（六冲/三合/六合/刑/藏干）、格局定义（20）、用神规则（19）、十二长生（12）、天干体象/纳音（18）、六亲（10）。
- 全部绑定真实 source_id，**无悬空**（QC 验证 unbound_refs=0）。
- evidence_requirement 统一 C，metadata 标注 `source_coverage=8.9%`（spec §11.1，YHZP 整书覆盖率上限）。
- 算子仅 `equals/in/not_in/exists/not_exists`，无 `> < >= <=`。

## 四、质检结果（独立脚本 `_tmp_sftk/final_qc.py`）

- source_id 唯一：dup=0 ✓
- resource_id 一一对应（`SRC-`+source_id）：✓
- 无绝对路径（D:/ C:\\）：✓
- 无违禁算子：op/abs-path violations=0 ✓
- Rule→Source 绑定：unbound_refs=0，empty_source_ids=0 ✓
- evidence_grade 与 text_layer 硬绑定：✓
- `file_hash` 与磁盘一致：YHZP=`853582d61b8a` MATCH ✓

## 五、底稿来源说明

- **原文**：宋·徐升整理《渊海子平》，305 章节，777 页，含白话译文与现代启示。
- **提取渠道**：luckclub 古籍典藏（www.luckclub.cn），自动提取于 2026-08-12。
- **整理时间**：2026-09-14（完整版）。
- **眉批/附注**：部分章节含「眉批：」「附注」古注，已保留于 source_text 内，标 `handling_status=NEEDS_REVIEW`，待 Human 签核后拆分。
- **白话译文/现代启示**：属 LATER_COMMENTARY，本条 source 仅录原文块，白话/现代启示分离不录（`collation_note` 标注）。

## 六、遗留 / 交 Human

- 第 0 章（目录）text_layer=UNVERIFIED，交 Human 裁定。
- 含眉批/附注古注的章节，`handling_status=NEEDS_REVIEW`，待 Human 签核拆分。
- 6 条原 UNVERIFIED 段（旧版 240 条数据中的）已随本次重写覆盖，新数据 305 条中仅第 0 章 1 条 UNVERIFIED。
