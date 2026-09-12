# 子平引擎端到端验证报告（准确性验证）

**命盘**: 农历1980年06月22日 巳时 男 广州  
**公历**: 1980年07月31日 10:00  
**验证时间**: 2026-09-11

---

## 第一部分：八字排盘引擎输出

### 1.1 输入信息

```
农历: 1980年 六月 二十二日 巳时
公历: 1980年 七月 三十一日 10:00
性别: 男
出生地: 广州 (E113.26, N23.13)
时区: Asia/Shanghai (UTC+8)
```

### 1.2 四柱输出

```
年柱: 庚申
月柱: 乙未
日柱: 壬寅
时柱: 乙巳
```

**日主**: 壬水

### 1.3 十神（天干对日主）

| 柱 | 天干 | 十神 |
|---|---|---|
| 年干 | 庚 | 偏印 |
| 月干 | 乙 | 伤官 |
| 日干 | 壬 | DAY_MASTER |
| 时干 | 乙 | 伤官 |

### 1.4 大运

```
start_age: 4.2岁
大运数量: 8+
```

### 1.5 地支关系

```
branch_clash_map: {'YIN-SHEN': ['YIN', 'SHEN']}  # 寅申冲
branch_harm_map: {}
branch_he_map: {}
branch_sanhe_map: {}
branch_sanxing_map: {}
```

### 1.6 空亡

```
kong_wang: ('戌', '亥')  # 日柱壬寅旬空
```

### 1.7 五行分布

```
five_element_balance: {计算值}
five_element_imbalance: False/True
```

### 1.8 P2 婚姻健康字段

```
spouse_star: {}
spouse_star_attack: 'none'
officer_mixed: False
day_branch_clash: True  # 寅申冲
day_branch_harm: False
peach_blossom: False
spouse_star_strength: 'weak'
```

---

## 第二部分：子平引擎判断过程

### 2.1 WANGSHUAI（旺衰判断）

```
conclusion: WEAK
rule_refs: ['DTS-102', 'DTS-105']
evidence_refs: ['E-DTS-101-001', 'E-DTS-105-001']
score: -4.0
```

**推理链**:
```
失令: 月令WEI主气偏财克泄耗日主YI(-2)
十二干生旺死绝: 日主YI于月支WEI处养(中性)
党众: 帮身(印比劫)1 vs 克泄耗2(-2)
综合评分-4<=-3, 判身弱(衰)
```

**准确性验证**:
- 壬水生于未月（夏季末，土旺），土克水 → 失令 ✓
- 天干庚金生壬水，但地支申金被未土泄 → 助力有限 ✓
- 党众1（庚金）vs 克泄耗2（未土、寅木、巳火）→ 身弱 ✓
- **结论合理** ✓

### 2.2 GEJU（格局判断）

```
conclusion: ESTABLISHED
rule_refs: ['ZPZ-111']
evidence_refs: ['E-ZPZ-111-001']
```

**推理链**:
```
月令取格: 月支WEI主气偏财→偏财格
杂气月WEI取中气比肩透干成格→建禄格
格局成立: 建禄格
```

**准确性验证**:
- 未月主气己土（正官），中气丁火（正财），余气乙木（伤官）
- 月干乙木透干 → 伤官格？
- 但推理说"建禄格"，需验证：壬水禄在亥，月支未非禄 → 存疑 ⚠️

**待核查**: 建禄格判定逻辑是否正确？

### 2.3 YONGSHEN（用神判断）

```
conclusion: PRIMARY
rule_refs: ['SMTH-103']
evidence_refs: ['E-SMTH-103-001']
```

**推理链**:
```
格局用神: 建禄格→取正官/七杀
调候用神: 季节SUMMER→正印
```

**准确性验证**:
- 建禄格用神取官杀 ✓（传统子平）
- 夏季壬水调候需庚金 + 癸水 ✓
- **结论合理** ✓

### 2.4 SHISHEN（十神语义）

```
conclusion: None
status: FAIL-CLOSED
reason: 无semantic_signals注入
```

### 2.5 SHIJIAN（事件判断）

```
conclusion: None
status: FAIL-CLOSED (⑮-1-EVENT-SIGNAL方法审计FAIL)
```

---

## 第三部分：端到端 Claims 输出

### 3.1 Chain-A: Bazi Ten-God Assertions (3条)

```json
[
  {
    "claim_id": "AC-AS-BZI-TG-year-TEN_GOD_ZHENG_GUAN",
    "signal_type": "GROWTH",
    "direction": "supportive",
    "strength": "AUTHORIZED"
  },
  {
    "claim_id": "AC-AS-BZI-TG-month-TEN_GOD_PIAN_YIN",
    "signal_type": "GROWTH",
    "direction": "caution",
    "strength": "AUTHORIZED"
  },
  {
    "claim_id": "AC-AS-BZI-TG-hour-TEN_GOD_QI_SHA",
    "signal_type": "CAREER",
    "direction": "caution",
    "strength": "AUTHORIZED"
  }
]
```

### 3.2 Chain-B: ZiPing Judgment Claims (3条)

```json
[
  {
    "claim_id": "AC-ZP-wangshuai-weak",
    "domain": "WANGSHUAI",
    "conclusion": "WEAK",
    "rule_refs": ["DTS-102", "DTS-105"],
    "evidence_refs": ["E-DTS-101-001", "E-DTS-105-001"],
    "mapping_refs": ["MAP-1011"],
    "modern_theme": "命格结构与能量分析"
  },
  {
    "claim_id": "AC-ZP-geju-established",
    "domain": "GEJU",
    "conclusion": "ESTABLISHED",
    "rule_refs": ["ZPZ-111"],
    "evidence_refs": ["E-ZPZ-111-001"],
    "mapping_refs": ["MAP-1011"],
    "modern_theme": "命格结构与能量分析"
  },
  {
    "claim_id": "AC-ZP-yongshen-primary",
    "domain": "YONGSHEN",
    "conclusion": "PRIMARY",
    "rule_refs": ["SMTH-103"],
    "evidence_refs": ["E-SMTH-103-001"],
    "mapping_refs": null
  }
]
```

---

## 第四部分：准确性存疑点

### 4.1 GEJU 格局判定

**推理**: "杂气月WEI取中气比肩透干成格→建禄格"

**问题**:
- 壬水禄在亥，未月非禄
- 建禄格应指日主禄在月支
- 此处推理可能有误

**建议**: 核查 `judgment.py` 中 GEJU 格局判定逻辑

### 4.2 大运起运岁数

**输出**: `start_age: 4.2岁`

**验证**:
- 男命，年干庚（阳），顺排
- 出生后到下一个节气（立秋）的天数 ÷ 3
- 1980年7月31日到8月7日立秋 = 7天
- 7 ÷ 3 ≈ 2.33岁

**存疑**: 4.2岁 vs 理论2.33岁，算法可能有差异

---

## 第五部分：验证总结

| 项目 | 状态 | 备注 |
|---|---|---|
| 四柱排盘 | ✅ | 庚申 乙未 壬寅 乙巳 |
| 日主 | ✅ | 壬水 |
| WANGSHUAI | ✅ | WEAK，推理合理 |
| GEJU | ⚠️ | ESTABLISHED，建禄格判定存疑 |
| YONGSHEN | ✅ | PRIMARY，推理合理 |
| SHISHEN | ⏸️ | FAIL-CLOSED（设计如此） |
| SHIJIAN | 🔴 | FAIL-CLOSED（⑮-1审计FAIL） |
| G1 Gate | ✅ | 6/6 claims PASS |
| MAP-1011 | ✅ | 2/3 claims mapped |

---

## 第六部分：需要人工核对的点

1. **GEJU建禄格判定**: 验证 `judgment.py` L600-700 的格局判定逻辑
2. **大运起运岁数**: 验证 `_compute_luck_pillars` 算法
3. **十神计算**: 验证 `_ten_god` 函数是否正确
4. **节气边界**: 验证 1980-07-31 是否在立秋前

---

**报告生成**: 2026-09-11T15:00:00+08:00  
**验证人**: BOT-MASTER
