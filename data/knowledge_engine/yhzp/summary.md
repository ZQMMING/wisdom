# 渊海子平 (YHZP) 知识工程候选数据摘要

生成时间: 2026-09-14

## 一、总量统计

| 指标 | 数值 |
|---|---|
| Source 总数 | 1695 |
| Rule 候选总数 | 465 |
| unformalizable 总数 | 126 |

## 二、章节覆盖

- 共处理 **304** 章（001-304）
- 跳过第 0 章（目录）整章
- 跳过文件头 markdown 元信息块（行1-7）
- 跳过书名行与现代简介（行8-15）

## 三、text_layer 分布

| text_layer | 数量 |
|---|---|
| LATER_COMMENTARY | 840 |
| ORIGINAL | 488 |
| ANNOTATION | 367 |

## 四、Rule type 分布

| rule_type | 数量 |
|---|---|
| definition | 413 |
| activation | 34 |
| resolution | 6 |
| diagnosis | 6 |
| medicine | 5 |
| effectiveness | 1 |

## 五、抽样 Rule 候选（3 条）

### 抽样 1: CAND-YHZP-001

**Rule JSON:**

```json
{
  "rule_id": "CAND-YHZP-001",
  "engine": "YUHAI_ZIPING",
  "source_id": "YHZP-003-001",
  "rule_type": "definition",
  "scope": "natal",
  "preconditions": {
    "type": "conjunction",
    "conditions": [
      {
        "field": "stem",
        "operator": "equals",
        "value": "甲"
      }
    ]
  },
  "operation": "emit",
  "outputs": [
    {
      "field": "stem_yinyang",
      "value": "阳"
    }
  ],
  "evidence_requirement": "A",
  "status": "CANDIDATE",
  "notes": "天干甲为阳干"
}
```

**对应 source_text 原文（YHZP-003-001, ORIGINAL）:**

> 论天地干支所出窃以奸诈生，妖怪出。黄帝时有蚩尤神扰乱，当是之时，黄帝甚忧民之苦，遂战蚩尤于涿鹿之野（涿鹿，郡名）。流血百里，不能治之（时帝始制干戈刀剑之器），黄 帝于是斋戒筑坛祀天，方丘礼地。天乃降十干（即：甲、乙、丙、丁、戊、己、庚、辛、壬、癸），十二支（即：子、丑、寅、卯、辰、巳、午、未、申、酉、戌、 亥）。帝乃将十干圆布象天形；十二支方布象地形。始以干为天，支为地，合光仰职门放之，然后乃能治

### 抽样 2: CAND-YHZP-051

**Rule JSON:**

```json
{
  "rule_id": "CAND-YHZP-051",
  "engine": "YUHAI_ZIPING",
  "source_id": "YHZP-007-001",
  "rule_type": "activation",
  "scope": "natal",
  "preconditions": {
    "type": "conjunction",
    "conditions": [
      {
        "field": "branch",
        "operator": "equals",
        "value": "寅"
      },
      {
        "field": "target_branch",
        "operator": "equals",
        "value": "亥"
      }
    ]
  },
  "operation": "emit",
  "outputs": [
    {
      "field": "branch_six_combine",
      "value": "寅亥合"
    },
    {
      "field": "combine_wuxing",
      "value": "木"
    }
  ],
  "evidence_requirement": "A",
  "status": "CANDIDATE",
  "notes": "地支寅亥合化木"
}
```

**对应 source_text 原文（YHZP-007-001, ORIGINAL）:**

> 论十二支六合渊海子平卷一论十二支六合子与丑合土，寅与亥合木，卯与戌合火，辰与酉合金，巳与申合水，午与未合火，午太阳、未太阴也。

### 抽样 3: CAND-YHZP-201

**Rule JSON:**

```json
{
  "rule_id": "CAND-YHZP-201",
  "engine": "YUHAI_ZIPING",
  "source_id": "YHZP-054-001",
  "rule_type": "definition",
  "scope": "natal",
  "preconditions": {
    "type": "conjunction",
    "conditions": [
      {
        "field": "stem",
        "operator": "equals",
        "value": "癸"
      }
    ]
  },
  "operation": "emit",
  "outputs": [
    {
      "field": "stem_yangren",
      "value": "丑"
    }
  ],
  "evidence_requirement": "A",
  "status": "CANDIDATE",
  "notes": "天干癸羊刃在丑"
}
```

**对应 source_text 原文（YHZP-054-001, ORIGINAL）:**

> 论羊刃渊海子平卷一论羊刃羊刃对宫即飞刃。甲生人，羊刃在卯，酉飞刃；乙生人，羊刃在辰，戌飞刃；丙生人，羊刃在午，子飞刃；丁生人，羊刃在未，丑飞刃；戊生人，羊刃在午，子飞刃；己生人，羊刃在未，丑飞刃；庚生人，羊刃在酉，卯飞刃；辛生人，羊刃在戌，辰飞刃；壬生人，羊刃在子，午飞刃；癸生人，羊刃在丑，未飞刃。羊，主刚也。刃者，主刑也。禄过则刃生，功成当退不退，乃狠而进也。言进而有伤官，羊刃当居禄前一辰，谓吉

