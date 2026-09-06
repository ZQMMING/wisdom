# Phase 3 P0 Judgment 层重写报告

**任务**: [BOT-ZIPING] Phase 3 P0 Judgment 层重写
**裁决依据**: BOT-MASTER 基于 `judgment.py:121-244` 的实际代码审查
**状态**: 三大域重写完成 + 新增测试 14/14 PASS + 发现并 BLOCK 2 处证据缺口

---

## 一、重写前后对比

| 域 | 重写前 (脚手架) | 重写后 (确定性算法) |
|----|----------------|---------------------|
| WANGSHUAI | `has_sheng and not has_ke` 布尔判断 | 三维评分: 得令 +3/-2, 得地 ±2/±1/0, 党众 ±2 |
| GEJU | `type in ("ACTION","OUTPUT")` | 月令→透干→成格/破格 五级链 |
| YONGSHEN | 返回 `UNKNOWN` 占位符 | 格局→扶抑→调候→通关→病药 五级优先级 |

原文件 375 行 (13,125 chars), 重写后 1091 行。

---

## 二、P0-1 WANGSHUAI: 得令 + 得地 + 得势

```
1. 得令 (月令司权)
   月支主气对日主为 印/比/劫 → +3   [DTS-101]
   月支主气为 官/杀/财/食/伤 → -2   [DTS-102]
   得令但月令被局中他柱支冲   → -2   [DTS-106]

2. 得地 (十二干生旺死绝)
   日主于月支 临官/帝旺  → +2   [DTS-104]
   日主于月支 沐浴/冠带  → +1   [SMTH-101]
   日主于月支 死/墓/绝   → -2   [SMTH-102]

3. 得势 (党众 = 四柱透干, 不含藏干)
   印比劫 > 克泄耗 → +2   [DTS-105]
   印比劫 < 克泄耗 → -2
   相等          →  0

综合: >=4 → STRONG ; <=-3 → WEAK ; 否则 MODERATE
```

### 关键修正 1: 党众口径 (STRONG 分支从不可达 → 可达)

初版把**地支藏干也计入**党众。后果: 克泄耗藏干(每支 2-3 个)天然多于帮身藏干,
党众恒为负 → **STRONG 分支永远不可达**, 7 个命例 STRONG=0。

修正依据 DTS-105 原文「党众(比劫**透干**)」— "党"指明面上之党:

```python
def _count_dangzhong(...):
    """党众只看四柱透干; 藏干根属通根/得地范畴(DTS-103/DTS-104),
    在此重复计数会与得地评分双重计数。"""
```

修正后: 甲木寅月印比齐备 → `score=7 → STRONG`, 三分支全覆盖
(`STRONG=1 / MODERATE=3 / WEAK=3`)。

### 关键修正 2: MODERATE 无硬编码 fallback

`MODERATE` 仅由 `total_score ∈ (-3, +4)` 区间导出。新增测试断言:
MODERATE 结论必须伴随非空 `score_detail.total_score`, 否则视为伪造 fallback。

### 寒暖燥湿归属调整

BOT-MASTER 要求 WANGSHUAI 含「寒暖燥湿」。核查证据库: **不存在 QTB 旺衰规则**
(QTB-014 为工程种子规则, source 非经典, 不可引用)。为避免臆造映射,
调候移出 WANGSHUAI, 保留在 YONGSHEN 域(五级链第 3 级), 并在代码注释显式声明。

---

## 三、P0-2 GEJU: 月令 → 透干 → 成格 / 破格

```
1. 变格检测            → BLOCKED (见下)
2. 特殊格: 建禄 [SMTH-103] / 阳刃 [YHZP-101] / 月劫 [YHZP-104]
3. 月令取格 → 透干成格 [ZPZ-111] / [ZPZ-120]
   杂气月(辰戌丑未)主气不透干 → 改取中气/余气
4. 破格: 财破印 [ZPZ-108] / 伤官见官 [ZPZ-106+110] / 杀无制 [ZPZ-107]
        / 月令受冲 [DTS-106]
```

### 关键修正 3: 变格 (从格/专旺/化格) 改为 BLOCKED

重写时发现 `ZPZ-105` 被误当作从格规则依据。实际读取该规则:

```json
"rule_id": "ZPZ-105",
"title": "官杀当令 → CONSTRAINT",
"rule_type": "月令司权",
"produces_signal_type": "CONSTRAINT"
```

**这是"官杀当令"规则, 根本不是从格规则。** 全库检索 `从格|专旺|化格|从财|从杀`
→ **0 匹配**, 证据库不存在任何变格规则与证据文件。

按「宁可保持 BLOCKED, 也不做测试迎合实现」原则: 变格不再输出 `ESTABLISHED`,
改返回 `UNKNOWN` 并标注 `ge_type="疑似从格(证据缺口)"`, 且 `evidence_refs` 保持为空。

### 关键修正 4: 月令受冲检测

`_chong_partner(month_branch) in month_branches` 中 `month_branches` 含月支自身
(非自身冲自身, 逻辑安全), 但需排除月支自身以避免歧义。用例验证:
`月支=WEI + 时支=CHOU (牛未相冲)` → `BROKEN`; 无冲对 → 正常成格。

---

## 四、P0-3 YONGSHEN: 五级优先级链

```
1. 格局用神 (优先)  建禄/月劫取财官 [SMTH-103] / 阳刃取杀制 [YHZP-101] /
                    偏印取财 / 伤官取财 / 官格取印 [ZPZ-106] ...
2. 扶抑用神         身旺→克泄耗, 身弱→生扶
3. 调候用神 (补充)  冬生→丙火, 夏生→壬水
4. 通关用神 (特殊)  伤官见官取财通关 / 枭神夺食取财通关
5. 病药用神 (特殊)  score>=8 过旺取克泄, score<=-7 过弱取生扶
```

### 关键修正 5: 调候/通关不降级 PRIMARY

原实现无条件执行 `conclusion = SECONDARY`, 导致**已成功取得格局用神 PRIMARY
后被调候覆盖降级**。改为仅在 `conclusion is None` 时才提升为 SECONDARY,
符合《子平真诠·论用神》"格局用神为主, 调候为补"的次序。

### 关键修正 6: 移除无差别证据引用

原实现末尾无条件追加 `ZPZ-101`(印绶当令)到**每个**用神判断, 属臆造映射。
已移除 — 证据引用现严格按实际命理学条件累加。

---

## 五、证据可追溯性 (CITATION 单一登记表)

引入 `CITATION` 字典 + `_Citations` 累加器, 所有 `rule_refs` / `evidence_refs`
经同一入口登记, 去重保序, 未登记键直接 `KeyError` 报错(防止笔误造出假 ID)。

每条 evidence 均经文件系统核验存在:

| 状态 | 条数 |
|------|------|
| rule + evidence 均存在 | 17 |
| 规则存在但证据文件缺失 (只记 rule, 不记 evidence) | 2 |

| 缺口 | 说明 |
|------|------|
| `DTS-102` | 规则 `evidence_refs` 指向 `E-DTS-101-001` (得令), 无自身文件 |
| `SMTH-102` | 同上, 引用 `E-SMTH-101-001` |
| `YHZP-105` | 规则存在, 但 `E-YHZP-105-001` 文件不存在 |

**均设 `None`, 绝不伪造 ID。** 新增测试 `test_all_refs_resolve_to_real_files`
强制所有产出的 ref 对应真实文件。

---

## 六、工厂层确定性排序

`JudgmentFactory.judge_all` 核心三域按依赖顺序执行 (旺衰 → 格局 → 用神),
并将上游结果注入下游 (`synthesis.wangshuai` / `synthesis.geju`)。
其余域 (SHISHEN / SHIJIAN) 保持原顺序处理。

---

## 七、测试结果

| 测试 | 结果 |
|------|------|
| `tests/test_phase3_p0_judgment.py` (新增) | **14/14 PASS** |
| `tests/spec/` | 351 passed (含 judgment 边界 47/47) |
| `tests/test_p0_1c_negative.py` | 5/5 PASS |
| `tests/test_phase3_p0.py` | 1/1 PASS |
| 合计 (相关范围) | **371 passed** |

新增测试覆盖:

- 旺衰三分支全覆盖 (STRONG / WEAK / MODERATE)
- MODERATE 必伴随评分明细 (反硬编码 fallback)
- 建禄格 / 阳刃格成立
- 月令受冲 → BROKEN
- 变格证据缺口 → UNKNOWN (且 `evidence_refs` 为空)
- 用神格局优先级 + 调候不降级 PRIMARY
- 三大域所有 ref 文件真实存在
- 工厂层核心域依赖排序
- 缺失 context → fail-closed UNKNOWN

### 已知预存失败 (非本次引入)

`tests/spec/test_p15_shadow_integration.py` 等 5 项失败, 根因:

```
AttributeError: 'ZiweiChart' object has no attribute 'palaces'
  src/tongshu/engines/ziwei/evidence_producer.py:90
```

属紫微引擎预存缺陷, 与本次 ZIPING 改动无关 (改动前后失败项完全一致)。

---

## 八、向 BOT-MASTER 报告的 BLOCKED 项

### BLOCKED-1: 变格 (从格 / 专旺格 / 化格) 无证据支撑

- 证据库检索 `从格|专旺|化格|从财|从杀|从儿` → **0 匹配**
- 无 rule, 无 evidence
- 已实现为检测 + 返回 UNKNOWN + 标注证据缺口, 不作 ESTABLISHED 结论
- **需授权: 补充 ZPZ 变格规则与证据后方可解除**

### BLOCKED-2: QTB (穷通宝鉴) 旺衰/调候规则缺失

- 现有 `QTB-014` 为工程种子规则 (`source` 非经典文本), 不可作为经典证据引用
- 无 QTB 旺衰规则 → 寒暖燥湿已移至 YONGSHEN 域, WANGSHUAI 不引用
- **需授权: 补充 QTB 调候规则与证据**

### 待裁决: 证据文件缺口 3 处

`DTS-102` / `SMTH-102` / `YHZP-105` 规则存在但对应 evidence 文件缺失。
当前处理: 只记 rule_refs, 不记 evidence_refs, 不伪造。
**需裁决: 补证据文件, 或正式确认以 rule_refs 为引用上限。**

---

## 九、修改文件清单

```
src/tongshu/reasoning/judgment.py        (375 → 1091 行, 三大域重写)
tests/test_phase3_p0_judgment.py         (新增, 14 测试)
docs/bots/BOT-ZIPING/PHASE3_P0_JUDGMENT_FIX.md (本报告)
```

未修改: BAZI 代码, Golden Dataset, 任何 token/凭据。
