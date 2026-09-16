# 六部经典知识工程 · 总质检报告 v1.0

生成时间：2026-09-14
范围：渊海子平 / 子平真诠 / 滴天髓 / 穷通宝鉴 / 三命通会 / 神峰通考

## 0. 底本路径变更（重要，需 Human 知悉）

开工初期发现：`D:\shuntian\data\classics\original\` 下六个 `_完整全文.md` 在 2026-09-14 05:33 被另一并行进程整体替换为"现代知识梳理体"（SHA256 全部漂移、内容为现代白话整理稿，非古文原文）。为不破坏该进程，**未回写该目录**，施工底本改指本地同源清洗版：

```
D:\顺天系统资料\豆包资料\六部经典校对版\
  YHZP_渊海子平_清洗版.md          (853582d6, 18007 行)
  PZZQ_子平真诠_清洗版.md          (cbda0c0d, 5185 行)
  DTS_滴天髓_清洗版.md             (e9a2021f, 6551 行)
  QTBJ_穷通宝鉴_清洗版.md          (1830fe93, 9171 行)
  SMTH_三命通会_清洗版.md          (9e71d67d, 23734 行)
  SFTK_神峰通考_OCR校对版.md       (0091619f, 7358 行)
```

六部 SHA256 与行数均与方案已确立事实一致，已逐部复验。

## 1. 总产出

| 经典 | Source | Rule 候选 | unformalizable | 子目录 |
|---|---:|---:|---:|---|
| 渊海子平 YHZP | 1695 | 465 | 126 | `yhzp/` |
| 子平真诠 PZZQ | 854 | 138 | 320 | `pzzq/` |
| 滴天髓 DTS | 604 | 66 | 86 | `dts/` |
| 穷通宝鉴 QTBJ | 4368 | 113 | 13 | `qtbj/` |
| 三命通会 SMTH | 1488 | 193 | 352 | `smth/` |
| 神峰通考 SFTK | 166 | 96 | 70 | `sftk/` |
| **合计** | **9175** | **1071** | **967** | |

Rule 候选 1071 条落在方案预估区间 600–1600 内。Source 总量高于预估（含现代白话译文/关键词/现代启示段，这些段不入 Rule 但入 Source 供溯源）。

## 2. 硬指标独立复核（编排者亲自跑）

| 检查项 | 结果 |
|---|---|
| source_id 全书唯一 | ✅ 六部全通过 |
| rule_id 唯一且前缀 CAND-<BOOK>- | ✅ 六部全通过 |
| Rule 绑定的 source_id 存在且 text_layer=ORIGINAL | ✅ 0 条坏绑定 |
| 无 luckclub/QQ群/收费50/技术支持 水印 | ✅ |
| 无绝对路径、无 http、无 U+FFFD | ✅ |
| operator ∈ {equals, not_equals, in, has, absent} | ✅ 0 条非法 |
| 无 > < >= <= 比较符 | ✅ |
| 无嵌套 preconditions | ✅ |
| source_text 抽样回底本逐字命中（换行归一后） | ✅ 六部全命中 |
| status 一律 CANDIDATE | ✅ |
| 无跨经典引述、无统一用神、无评分字段 | ✅ |

## 3. 各部特殊情况（需 Human 关注）

- **PZZQ**：15 条 `（林注…）` 非规范注解标记，子代理标 UNVERIFIED 未提 Rule，交 Human 裁定。
- **DTS**：1 条 `DTS-009-023`（己土韵句残注）标 UNVERIFIED。Rule 66 条低于预估——滴天髓正文多为韵文宇宙论铺垫，干净 IF-THEN 集中在何知/性情/疾病等章，未强行凑数。
- **QTBJ**：矩阵 10 天干 × 12 月令 = 120 格 100% 覆盖。
- **SMTH**：全书无空行，机械切分粒度到"每原 文 区一条 Source"（比 YHZP 粗）；第 184 章起六甲日×时断及 304 章后歌赋，Source 已切分录入但 Rule 按 unformalizable 交 Human 裁定。
- **SFTK**：OCR 繁体版，19 组重复行/成环乱字未修补、如实保留；上下二册页码重置已处理；章节按 curated 白名单标题切分。

## 4. 交付物清单

```
D:\shuntian\data\knowledge_engine\
├── specs\
│   ├── source_entry_spec.md      # Source 录入规范 v1.0
│   └── rule_extraction_spec.md   # Rule 提取规范 v1.0
├── yhzp\    sources.jsonl / rules_candidate.jsonl / unformalizable.jsonl / qa_report.md / summary.md
├── pzzq\    （同上五件套）
├── dts\     （同上五件套）
├── qtbj\    （同上五件套）
├── smth\    （同上五件套）
├── sftk\    （同上五件套）
└── qa_report_master.md           # 本报告
```

## 5. 待 Human 审批

- 1071 条 Rule 候选（status=CANDIDATE），请逐部对照原著审批
- 967 条 unformalizable 条目，请裁定是否可形式化或废弃
- 各部 qa_report.md 中记录的 UNVERIFIED / 底本特情
- 审批通过后，按方案第十一节去 CAND 前缀、写入正式 RuleRegistry，方可交主施工 Agent 消费
