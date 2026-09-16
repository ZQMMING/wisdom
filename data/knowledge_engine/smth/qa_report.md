# SMTH（三命通会）质检报告

生成时间：2026-09-14
底本：`D:\顺天系统资料\豆包资料\六部经典校对版\SMTH_三命通会_清洗版.md`
SHA256 前 8：`9e71d67d`（已复验一致）；行数：23734（已复验一致）

## 一、机械切分跳过项

| 行范围（1-based） | 跳过内容 |
|---|---|
| 1–6 | 文件头 markdown 元信息块（`# 三命通会…`、`> 页数…`、首个 `---`） |
| 7–13 | 书名行《三命通会》与现代简介（明朝万民英…） |
| 14–433 | 第 0 章 目录（整章跳过） |

正文自第 1 章（行 434）起，至第 381 章（行 23644）止。

说明：本底本全书**无空行**，故"按空行切分自然段落"的机械结果为——章内每个分区（原 文 / 白话译文 / 关键词 / 现代启示）各成一条 Source，与 YHZP 的逐段粒度不同；这是底本排版所致，未自行发明切分规则。

## 二、质检脚本自证（规范第 8 节全部检查项）

### Source
- [x] `source_id` 全文件唯一（1488/1488）
- [x] `text_layer` ∈ {ORIGINAL, ANNOTATION, LATER_COMMENTARY, UNVERIFIED}
- [x] 无绝对路径：`source_text` 不含 `D:\` `C:\` `http` `www.`
- [x] 无水印广告：不含 luckclub / qq群 / QQ群 / 收费50 / 技术支持
- [x] 无 Unicode 替换符 `\uFFFD` 及异常控制字符（SMTH-004-001 底本含 1 个 NUL，已按全角空格同款归一规则剔除 C0 控制符后复验通过）
- [x] `source_text` 开头 20 字 100% 可在底本（去换行、去全角空格后）逐字命中（miss=0）

### Rule
- [x] `rule_id` 唯一，且以 `CAND-SMTH-` 开头（CAND-SMTH-001 ~ CAND-SMTH-193）
- [x] 每条 Rule 的 `source_id` 均在 sources.jsonl 中存在
- [x] 每条 Rule 绑定的 Source 其 `text_layer == ORIGINAL`
- [x] `preconditions.type` ∈ {conjunction, disjunction}
- [x] 每条 condition 的 `operator` ∈ {equals, not_equals, in, has, absent}
- [x] 无 `>` `<` `>=` `<=` 出现
- [x] 无嵌套 preconditions
- [x] `operation` ∈ {emit, require, suppress}
- [x] `outputs` 每项都有 `field` 与 `value`
- [x] `status == "CANDIDATE"`

### 整体
- [x] 无跨经典引述（notes 不提及其他书名作为依据）
- [x] 无"用神=X"统一用神结论
- [x] 无评分字段（score/weight/point）
- [x] 质检脚本自身跑通，输出每项 ✓/✗ 与失败计数：**通过 19 / 失败 0**

## 三、范围声明

- 只落盘 `D:\shuntian\data\knowledge_engine\smth\` 五文件；未 commit；未改动 `D:\shuntian\data\classics\original\`。
- 原著一字未改；未评分；未建跨经典优先级。
- 混排标记：全书未检出"眉批/原注/徐注/按/注曰"等段首注解标记，故无 ANNOTATION / UNVERIFIED 条目。
- Rule 优先从前 ~63 章结构化定义/关系章提取（十干合化、六合三合三刑六害六冲、禄刃贵驿马劫亡、人元司事、旺相休囚死、遁月遁时、十恶大败等）；第 184 章起的"六甲日×时断"及 304 章后的歌赋论说，Source 已全部切分录入，Rule 未逐条形式化（按用户授权，标注 unformalizable 或部分提取）。
