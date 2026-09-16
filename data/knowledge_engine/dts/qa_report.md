# DTS（滴天髓）知识工程 · 质检报告

## 底本复验
- 底本：`D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓_清洗版.md`
- SHA256 前 8：`e9a2021f`（与规范一致 ✓）
- 行数：6551（与规范一致 ✓）

## 文件级跳过项（规范第 2 节）
1. 文件头元信息块：第 1–7 行（`# 滴天髓阐微 完整全文` 至首个 `---`），不录入。
2. 书名行与现代简介：第 8–14 行，不录入。
3. `第 0 章 目录`：第 15–18 行，整章不录入。
4. 正文自 `第 1 章 滴天髓序` 起，共 65 章（001–065）。

## 产出文件
| 文件 | 行数 |
|---|---|
| sources.jsonl | 604 |
| rules_candidate.jsonl | 66 |
| unformalizable.jsonl | 86 |
| qa_report.md | 本文件 |
| summary.md | 摘要 |

## text_layer 分布
- ORIGINAL：136
- ANNOTATION（刘诚意原注 + 任铁樵注）：275
- LATER_COMMENTARY（白话译文/关键词/现代启示）：192
- UNVERIFIED：1（仅 DTS-009-023，己土韵句缺原注标记之残注）

## 章节覆盖
共 65 章录入（第 1–65 章），全部覆盖。

## DTS 特有混排处理
- 原文区 `**【原注】**` → ANNOTATION；`【任氏曰】：` 及其后解说 → ANNOTATION；其余 → ORIGINAL。
- Rule 仅绑定 ORIGINAL；ANNOTATION/LATER/UNVERIFIED 不提取 Rule。
- 特殊处理（穷尽诊断全书仅 5 处）：
  - ch9 丙火韵句跨行（`…必当焚灭(一本` + `作虎马犬乡，甲来成灭)。`）已合并为一条 ORIGINAL。
  - ch60 羊刃韵句跨行（`…虎头蛇` + `尾。`）已合并。
  - ch53 反局：一段原注连续注解同一首韵句，3 处命例残句误判已归回 ANNOTATION。
  - ch9 己土韵句缺 `**【原注】**` 标记：韵句本体归 ORIGINAL，其后残注归 UNVERIFIED 交 Human 裁定。

## 规范第 8 节检查项结果（20/20 通过）
- [x] source_id 全文件唯一
- [x] text_layer ∈ 四值
- [x] source_text 无 `D:\`/`C:\`/`http`/`www.`
- [x] 无 luckclub/qq群/收费50/技术支持 水印广告
- [x] 无 `\uFFFD` 及异常控制字符
- [x] source_text 开头 20 字（去空白）100% 在底本逐字命中
- [x] rule_id 唯一且以 `CAND-DTS-` 开头
- [x] 每条 Rule 的 source_id 均在 sources.jsonl 中
- [x] 每条 Rule 绑定的 Source text_layer == ORIGINAL
- [x] preconditions.type ∈ conjunction/disjunction
- [x] 每个 condition operator ∈ 白名单（equals/not_equals/in/has/absent）
- [x] 无 `>` `<` `>=` `<=`
- [x] 无嵌套 preconditions
- [x] operation ∈ emit/require/suppress
- [x] outputs 每项均有 field 与 value
- [x] status == CANDIDATE
- [x] 无跨经典引述
- [x] 无"用神=X"统一用神结论
- [x] 无 score/weight/point 评分字段
- [x] 质检脚本自跑通，输出逐项 ✓/✗

## 失败计数：0
