# QTBJ 穷通宝鉴 · 知识工程质检报告

## 1. 底本复验

- 底本：`D:\顺天系统资料\豆包资料\六部经典校对版\QTBJ_穷通宝鉴_清洗版.md`
- SHA256 前 8：**1830fe93**（与规范一致 ✓）
- 行数：**9171**（与规范一致 ✓）

## 2. 预处理跳过项

- 文件头 1–15 行（`# 标题`、`>` 引用、首条 `---`、书名行、现代简介）：不录入。
- 第 0 章（第 16–156 行，目录）：整章跳过（spec §2.3）。

## 3. 切分结果

- Sources 总数：**4368**
  - ORIGINAL 原文：1507
  - ANNOTATION 徐乐吾注：1399
  - LATER_COMMENTARY 白话/关键词/现代启示：1462
  - UNVERIFIED：0
- Rules 候选：**113**
- Unformalizable：**13**

## 4. 质检逐项

- [✓] source_id 全文件唯一
- [✓] text_layer ∈ {ORIGINAL,ANNOTATION,LATER_COMMENTARY,UNVERIFIED}
- [✓] source_text 无绝对路径/URL
- [✓] source_text 无水印广告
- [✓] source_text 无 U+FFFD/异常控制字符
- [✓] source_text 逐字可在底本检索（换行归一后 100% 命中）
- [✓] source_text 开头 20 字 100% 命中
- [✓] rule_id 唯一
- [✓] rule_id 均以 CAND-QTBJ- 开头
- [✓] 每条 Rule 的 source_id 均存在于 sources.jsonl
- [✓] Rule 绑定 Source 的 text_layer == ORIGINAL
- [✓] preconditions.type ∈ {conjunction,disjunction}
- [✓] condition.operator ∈ 白名单
- [✓] preconditions 无 > < >= <= 比较符
- [✓] preconditions 无嵌套 conditions
- [✓] operation ∈ {emit,require,suppress}
- [✓] outputs 每项含 field 与 value
- [✓] status == "CANDIDATE"
- [✓] Rule notes 无跨经典引述
- [✓] 无"用神=X"式统一用神结论
- [✓] Rule 无评分字段

**合计：21 项检查，通过 21，失败 0。**

## 5. 说明

- 章节切分：底本多位数章号中间含空格（如 `第 1 0 章`），按 spec 正则去空格归一后匹配，共 113 章（第 1–113 章）。
- 原文区段落分隔：底本无空行、硬换行约 40 字/行，采用"上一行以句末标点（。！？；…）结尾则分段"的启发式；段首 `徐乐吾曰` 一律 ANNOTATION（含全角 `：` 与半角 `:` 两种写法）。
- source_text 录入时将段内换行与全角空格归一为连续文本，逐字未改；底本子串校验据此在换行归一后比对。
