# 盲派 Case / Golden 母表 V2（测试体系，不进生产 Rule）

> **工程禁令**：Case_ID 不得成为 Rule_ID 的来源。
> 案例只做 Golden / Regression / Edge / Counter 测试，验证 Rule 命中与 Assertion 正确。

---

## 字段定义

| 字段 | 内容 |
|---|---|
| Case_ID | 唯一 ID |
| Source | 原典案例/实战案例 |
| Input | 八字/岁运 |
| Expected_Facts | 预期事实 |
| Expected_Assertion | 预期断言 |
| Expected_Timing | 预期应期 |
| Test_Type | GOLDEN / REGRESSION / EDGE / COUNTER |
| Evidence_Link | 对应 Rule Evidence ID |
| Status | PASS / FAIL |

---

## 案例库（待录入）

| Case_ID | Source | Input | Expected_Facts | Expected_Assertion | Expected_Timing | Test_Type | Evidence_Link | Status |
|---|---|---|---|---|---|---|---|---|
| C-001 | 朱元璋命 | 戊壬丁丁 辰戌丑未 | 日主合月令官 | 正局 | — | GOLDEN | R-PJ-001 | 待录 |
| C-002 | 坤造反局 | 丙戊丁丁 子戌丑未 | 日支合子水反局 | 反局 | — | GOLDEN | R-PJ-002 | 待录 |
| C-003 | 岳飞命 | 癸乙甲己 未卯子巳 | 羊刃库穿印 | 制象=军队 | — | GOLDEN | R-SX-005 | 待录 |
| C-004 | 孔祥熙命 | 庚乙癸庚 辰酉卯申 | 满盘金制卯 | 合象=银行 | — | GOLDEN | R-SX-002 | 待录 |

---

## 使用规则

1. 新案例录入此表，标注 Expected_Assertion 对应哪个 Rule Evidence
2. 跑案例时引擎输出 vs Expected_Assertion 对比
3. FAIL 的案例 → 查 Rule Evidence 是否有误，不是改 Rule 迎合案例
4. 案例不得反向生成 Rule；任何从案例发现的规律，必须先追溯原典补 Rule Evidence
