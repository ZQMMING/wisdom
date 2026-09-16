# PZZQ《子平真诠》知识工程质检报告

## 0. 底本复验
- 底本：`D:\顺天系统资料\豆包资料\六部经典校对版\PZZQ_子平真诠_清洗版.md`
- SHA256 前 8：`cbda0c0d`（脚本内 assert 通过）
- 行数：5185（脚本内 assert 通过）
- engine：`ZIPIN_ZHENQUAN`；book：`子平真诠`

## 1. 文件级跳过项（规范第 2 节）
| 行范围(1-based) | 内容 | 处理 |
|---|---|---|
| 第 1–6 行 | markdown 元信息块（`# 子平真诠 完整全文`、`> 页数…`）至第一个 `---` | 不录入 |
| 第 7–17 行 | 书名行 `《子平真诠》`、现代简介一段、`第 0 章` 目录整章 | 不录入 |
| 第 18 行起 | `第 1 章 子平真诠评注序` | 正文起点 |

## 2. 切分约定说明（本底本特有）
- 全文件无空行，段落以分区标记（`原 文`/`原文`/`白话译文`/`---`/`关键词`/`现代启示`）及 `**【徐注】**`/`【徐注】`/`（林注` 行首为界。
- 章节编号 `第 1 0 章` 起中间带空格，按行首 `^第\s*\d[\s\d]*\s*章$` 识别，数字去空格后为章号。
- 段内多行直接拼接为连续文本（保留全部原有标点，含半角逗号），不改一字。
- text_layer：原文区段首 `**【徐注】**`/`【徐注】` → ANNOTATION（293 条，与全文徐注出现次数 293 一致）；段首 `（林注` → UNVERIFIED（15 条，notes 注明交 Human 裁定）；其余原文区 → ORIGINAL；白话译文/关键词/现代启示区 → LATER_COMMENTARY。

## 3. 质检项结果（规范第 8 节，共 22 项，全部通过）
| 检查项 | 结果 |
|---|---|
| source_id 全文件唯一 | ✓ |
| text_layer ∈ {ORIGINAL,ANNOTATION,LATER_COMMENTARY,UNVERIFIED} | ✓ |
| source_text 无绝对路径/网址 | ✓ |
| source_text 无 luckclub/QQ群/收费50/技术支持 水印 | ✓ |
| 无 \uFFFD 及异常控制字符 | ✓ |
| 100% source_text 开头 20 字在底本逐字命中 | ✓ |
| 抽样 20%（171/854）source_text 全文逐字命中底本 | ✓ |
| rule_id 唯一且以 CAND-PZZQ- 开头 | ✓ |
| 每条 rule 的 source_id 存在于 sources | ✓ |
| rule 绑定 source 的 text_layer == ORIGINAL | ✓ |
| preconditions.type ∈ {conjunction,disjunction} | ✓ |
| condition operator ∈ {equals,not_equals,in,has,absent} | ✓ |
| 无 > < >= <= 比较符 | ✓ |
| 无嵌套 preconditions | ✓ |
| operation ∈ {emit,require,suppress} | ✓ |
| outputs 每项都有 field 与 value | ✓ |
| status == "CANDIDATE" | ✓ |
| unformalizable 字段 {source_id,raw_text,reason} 且 source_id 存在 | ✓ |
| notes 无跨经典引述 | ✓ |
| 无“用神=X”统一用神结论 | ✓ |
| 无 score/weight/point 评分字段 | ✓ |

**失败计数：0。**

## 4. 交 Human 裁定项
- UNVERIFIED 15 条：均为 `（林注…）` 段首（现代林君毅补注），非规范定义的徐注标记，未提取 Rule，notes 已注明。
- unformalizable 320 条：题句、宇宙论/描述性铺垫、定性强弱比较（规范禁比较符）、逐造命例点评、PZZQ-050-002/051-002 现代评点，均未形式化。
