# QA Report - 渊海子平 (YHZP)

质检时间: 2026-09-14

## 汇总

- 通过项: **19**
- 失败项: **0**
- Source 总数: 1695
- Rule 候选总数: 465
- unformalizable 总数: 126

## 跳过记录

- 文件头到第一个 `---`（行1-7）：markdown 元信息块
- 行8-15：书名行与现代简介
- 行16-349：第 0 章 目录整章

## 逐项检查

| # | 状态 | 检查项 | 详情 |
|---|---|---|---|
| 1 | ✓ | Source: source_id 唯一 | total=1695, unique=1695 |
| 2 | ✓ | Source: text_layer 四选一 | invalid=0 |
| 3 | ✓ | Source: 无绝对路径/http/www | bad=0 |
| 4 | ✓ | Source: 无水印广告 | bad=0 |
| 5 | ✓ | Source: 无\uFFFD | bad=0 |
| 6 | ✓ | Source: 抽样339条source_text可检索 | missed=0: [] |
| 7 | ✓ | Rule: rule_id唯一且前缀正确 | total=465, unique=465 |
| 8 | ✓ | Rule: source_id存在于sources | missing=0 |
| 9 | ✓ | Rule: 绑定Source为ORIGINAL | bad=0 |
| 10 | ✓ | Rule: preconditions.type合法 | bad=0 |
| 11 | ✓ | Rule: operator在白名单 | bad=0 |
| 12 | ✓ | Rule: 无比较符 | bad=0 |
| 13 | ✓ | Rule: 无嵌套preconditions | nested=0 |
| 14 | ✓ | Rule: operation合法 | bad=0 |
| 15 | ✓ | Rule: outputs有field和value | bad=0 |
| 16 | ✓ | Rule: status=CANDIDATE | bad=0 |
| 17 | ✓ | 整体: 无跨经典引述 | bad=0 |
| 18 | ✓ | 整体: 无统一用神 | bad=0 |
| 19 | ✓ | 整体: 无评分字段 | bad=0 |
