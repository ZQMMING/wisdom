# B1-YHZP 批次执行报告（BOT-KNOWLEDGE）

> 任务单：BOT-MASTER → B1-YHZP
> 分支：agent/knowledge-b1-yhzp ｜ BASE COMMIT：345769dc
> ENGINE：YUHAI_ZIPING ｜ 经典：《渊海子平》
> 日期：2026-09-14

---

## 一、CHANGED FILES（仅 ALLOWED PATHS 内）

| 文件 | 状态 | 说明 |
|------|------|------|
| `data/sources/yhzp_sources.jsonl` | 重写 | Source Registry 候选，**240 条** |
| `data/rules/candidate/CAND-YHZP_rules.jsonl` | 新增 | Rule 候选，**113 条** |
| `docs/bots/BOT-KNOWLEDGE/B1-YHZP_report.md` | 新增 | 本报告 |

未 commit（按任务单约定，由 BOT-MASTER 代为提交）。

---

## 二、统计

### Source（240 条）
- 粒度：按「卷→章→篇（段块）」聚合，**非** 2472 条逐段过细粒度（遵 Step 3「预估 200-500 条」）。
- text_layer 分布：
  - `LATER_COMMENTARY` 31（现代白话整理 docx：卷1-6 章1-21 正文 + 附录1-3 + 表格速查聚类）
  - `ORIGINAL` 203（徐大升《渊海子平》古典正文，本地HTML/FOR-BAZI 解析）
  - `UNVERIFIED` 6（编辑/编译器框注、混入「渊源」与编辑语，交 Human 裁定）
- evidence_grade 与 text_layer 硬绑定：A(ORIGINAL) 203 / C(LATER_COMMENTARY) 31 / D(UNVERIFIED) 6。
- source_id 唯一性：已通过（0 重复）。
- 无绝对路径、无中文字符、provenance 完整。

### Rule（113 条）
- rule_type 分布：`definition` 95 / `resolution` 18（以 definition 为主，遵 Step 6）。
- 全部绑定真实 source_id（引用 13 个 source，全在 240 条内，无悬空）。
- evidence_requirement 统一 = **C**（应用 spec_v10 §11.1：YHZP 整书覆盖率 8.9%，evidence_grade 不得高于 C；rule metadata 已标注 `source_coverage=8.9%`）。
- operator 语义：definition→emit，resolution→evaluate（符合 rule_type×operator 矩阵）。
- preconditions 仅用 `equals/in/exists`（封板 §46 白名单），无 `> < >= <=`。
- rule_id 格式 `CAND-YHZP-001…113`，status/lifecycle_status=CANDIDATE，match_state=null。

### 覆盖内容
- 十神 10 定义、五行相生 5 + 相克 5、地支藏干 12、天干五合 5、三合 4、六冲 6、六合 6、纳音 10、
  扶抑用神 2、大运方向 4、正格 10、特殊格局 11、通关 4、调候 4、古典喜忌 8、六亲 7 等。

---

## 三、TESTS / 质检

自实现 `qc_b1.py` 全量校验，结果 **NONE - all checks passed**：
- [x] source_id 唯一（0 重复）
- [x] 每条 Source 有 text_layer
- [x] 每条 Rule 绑定 ≥1 真实 source_id（无 unbound）
- [x] source_id 纯 ASCII（无中文）
- [x] 无绝对路径（C:/ D:/ /home/ /srv/ 全检）
- [x] preconditions 无比较运算符 > < >= <=
- [x] rule_type × operator 矩阵合规（definition→emit，resolution→evaluate）
- [x] evidence_grade 未突破 text_layer 上限
- [x] Rule evidence_requirement 未高于 C（YHZP 覆盖率上限）

---

## 四、底稿来源说明（provenance）

| 区块 | 行号范围 | 来源（原著内标注） | text_layer 判定 |
|------|---------|-------------------|----------------|
| 第1段：卷1-6 章1-21（两组合并去重，group1=group2 逐字节相同） | L16–1127 | 《渊海子平》完整知识梳理.docx（现代白话整理，自动提取 2026-08-11 15:44） | LATER_COMMENTARY（整理者改动字词/增删按语，白话翻译） |
| 第1段：附录1-3 | L476–573 | 同上 docx | LATER_COMMENTARY |
| 第1段：表格 1-78（速查表） | L1128–2007 | bazi-engine 渊海子平 | LATER_COMMENTARY（按主题聚成 7 条） |
| 第2段起：古典正文（喜忌篇/继善篇/古法/星家 等） | L2019–20397 | 本地HTML解析（2285）+ FOR-BAZI 渊海子平（185），徐大升《渊海子平》 | ORIGINAL（正文） |
| 编辑/编译框注段 | 散布 Part B | 「《渊海子平》（宋·徐大升编）。本篇为知识库…」等编辑语 + 混入「渊源」 | UNVERIFIED（交 Human 裁定） |

原著冻结 hash：`file_sha256 = 3389f2f2d35bed46…`（`data/classics/original/YHZP_渊海子平_完整全文.md`，20397 行）。

### 关键判定说明
1. **为什么 docx 区不是 ORIGINAL**：spec §6.3 明确「整理者改动字词、增删按语 → LATER_COMMENTARY」。该 docx 是现代白话知识梳理（含「象征勤奋助人」等现代意象、表格速查），非徐大升逐字原文，故全标 LATER_COMMENTARY + grade C，不冒称 ORIGINAL。
2. **为什么 Part B 主体是 ORIGINAL**：喜忌篇/继善篇等古典散文与 FOR-BAZI 带【原文】/【全文】标注的古法口诀，是《渊海子平》古典正文 → ORIGINAL + grade A（source 层），但受 §11.1 覆盖率上限约束，Rule 引用时 evidence 封顶 C。
3. **UNVERIFIED 仅 6 条**：只把编辑/编译器框注、混源段落标 UNVERIFIED，**未全标 LATER_COMMENTARY**（遵 Step 5 红线）。

---

## 五、遗留 / 待 Human 裁定

- 6 条 UNVERIFIED source（frame 段）需 Human 逐条签核 text_layer。
- 表格区 7 条为「主题聚类」粒度（表格 1-5/8-13/14-17/18-24/25-33/34-66/67-78），若需更细可再拆。
- Rule 113 条全部 CANDIDATE，待 Phase 4 审批；STOP Protocol：因 YHZP 覆盖率仅 8.9%，被引用段落若不在仓库 index.json 中应走 Gap Report（SOURCE_GAP），本批已按段落存在性预检，无缺失。

## 六、复现
生成器与质检器曾位于 `_tmp_yhzp/gen_b1.py`、`_tmp_yhzp/qc_b1.py`（任务边界外，已清理；逻辑记录于本报告「底稿来源说明」+ 上方统计）。
