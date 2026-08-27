#!/usr/bin/env python3
"""
A3.6-A: Regenerate 40 Blind Cases with new Rubric (0-3, 7 dimensions)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, 'src')

from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.heluo.canonical import HeluoCanonical

# Load data
with open('dataset/accuracy/pilot/pilot_dataset.json', 'r', encoding='utf-8') as f:
    pilot = json.load(f)

with open('dataset/accuracy/expert_pilot/frozen_sample.json', 'r', encoding='utf-8') as f:
    frozen = json.load(f)

persons = {p['person_id']: p for p in pilot['persons']}
be = BaziEngine()
hc = HeluoCanonical()

hour_map = {
    '子': 23, '丑': 1, '寅': 3, '卯': 5, '辰': 7, '巳': 9,
    '午': 11, '未': 13, '申': 15, '酉': 17, '戌': 19, '亥': 21
}
gender_map = {'男': 'male', '女': 'female'}

output_dir = Path('dataset/accuracy/expert_pilot/cases_v2')
output_dir.mkdir(exist_ok=True, parents=True)

RUBRIC_SECTION = """
## 评分任务

你是「顺天 V1.3 Accuracy Validation」项目的独立专家评价员。

你的唯一任务是：在严格的盲评条件下，根据预先冻结的评价标准，对「顺天系统生成的关系式解释」进行专家级质量评价。

### 最重要的原则

1. 评价系统，不重新计算系统 — 不得自行重新计算八字/河洛/紫微
2. 评价关系，不评价语言漂亮程度
3. 历史事实不能自动证明预测正确
4. 禁止事后合理化 — 宽泛语言适配大量事件不得视为高质量
5. 证据不足时必须使用 NOT_EVALUABLE

### 评分维度 (0-3 分)

| 维度 | 3 (STRONG) | 2 (ACCEPTABLE) | 1 (WEAK) | 0 (FAIL) |
|------|-----------|---------------|---------|---------|
| Temporal Alignment | 时间关系清晰，集中于目标窗口 | 基本对应，时间边界较宽 | 时间对应较弱，明显泛化 | 无法建立时间对应 |
| Event Correspondence | 对事件类型及性质有明确对应 | 存在合理对应，不够具体 | 只能通过宽泛解释勉强对应 | 无合理对应 |
| Relational Coherence | 关系结构高度一致 | 基本一致，轻微缺口 | 关系链存在明显断裂 | 自相矛盾或无法成立 |
| Evidence Support | 核心判断均有明确证据支持 | 大部分判断有证据支持 | 证据薄弱或存在明显跳跃 | 核心结论基本没有证据支持 |
| Directionality | 方向明确且证据充分 | 基本合理 | 方向模糊或存在明显冲突 | 方向与证据明显相反 |
| Specificity | 高度具体，具有明显约束力 | 有一定具体性 | 高度泛化 | 几乎完全属于通用套话 |
| Overall Interpretability | 整体解释成熟、连贯、可审计 | 基本成立，存在明显不足 | 解释零散或逻辑薄弱 | 无法形成有效解释 |

### 输出格式

必须严格输出 JSON，不得输出 Markdown 或额外解释：

```json
{
  "case_id": "...",
  "evaluable": true,
  "dimensions": {
    "temporal_alignment": {"score": 0, "status": "PASS|WEAK|FAIL|NOT_EVALUABLE", "reason": "..."},
    "event_correspondence": {"score": 0, "status": "PASS|WEAK|FAIL|NOT_EVALUABLE", "reason": "..."},
    "relational_coherence": {"score": 0, "status": "PASS|WEAK|FAIL|NOT_EVALUABLE", "reason": "..."},
    "evidence_support": {"score": 0, "status": "PASS|WEAK|FAIL|NOT_EVALUABLE", "reason": "..."},
    "directionality": {"score": 0, "status": "PASS|WEAK|FAIL|NOT_EVALUABLE", "reason": "..."},
    "specificity": {"score": 0, "status": "PASS|WEAK|FAIL|NOT_EVALUABLE", "reason": "..."},
    "overall_interpretability": {"score": 0, "status": "PASS|WEAK|FAIL|NOT_EVALUABLE", "reason": "..."}
  },
  "strengths": ["..."],
  "weaknesses": ["..."],
  "contradictions": ["..."],
  "unsupported_claims": ["..."],
  "overall_assessment": "...",
  "confidence": "HIGH|MEDIUM|LOW"
}
```

### 禁止行为

- 不得因为相信/不相信命理而评分
- 不得因为系统使用传统术语而加分
- 不得因为语言优美/冗长而加分
- 不得因为"看起来很准"而直接加分
- 不得使用事后已知信息反向修改评分标准
- 不得为系统寻找合理化解释或制造缺失证据
- 不得自己重新计算系统结果并将其作为 Ground Truth
"""

count = 0
for sample in frozen['samples']:
    sample_id = sample['sample_id']
    person_id = sample['person_id']
    
    if person_id not in persons:
        continue
    
    person = persons[person_id]
    birth_date = person.get('birth_date', '')
    birth_hour_cn = person.get('birth_hour', '子')
    gender_cn = person.get('gender', '男')
    
    if not birth_date:
        continue
    
    parts = birth_date.split('-')
    if len(parts) != 3:
        continue
    
    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    hour = hour_map.get(birth_hour_cn, 0)
    gender = gender_map.get(gender_cn, 'male')
    
    try:
        chart = be.compute((year, month, day, hour), gender)
        pillars_cn = chart.get_pillars_chinese()
        
        pillars = []
        for pn in ['year', 'month', 'day', 'hour']:
            cn = pillars_cn[pn]
            pillars.append((cn[0], cn[1]))
        
        result = hc.calculate(pillars, gender, birth_hour_cn, 'zhong')
        
        md = f"""# {sample_id} — Blind Evaluation (v2)

## 人物基本信息

- **人物ID**: {person_id}
- **性别**: {gender_cn}
- **出生年**: {year}
- **出生月**: {month}
- **出生日**: {day}
- **出生时**: {birth_hour_cn}时

## 系统输入

```json
{{
  "birth_info": {{
    "year": {year},
    "month": {month},
    "day": {day},
    "hour": "{birth_hour_cn}",
    "gender": "{gender}"
  }}
}}
```

## 系统原始输出

### 八字四柱

- 年柱: {pillars_cn['year']}
- 月柱: {pillars_cn['month']}
- 日柱: {pillars_cn['day']}
- 时柱: {pillars_cn['hour']}

### 河洛卦象

- **先天卦**: {result.prenatal.hexagram_name}（上卦{result.prenatal.upper_gua}，下卦{result.prenatal.lower_gua}）
- **后天卦**: {result.postnatal.hexagram_name}（上卦{result.postnatal.upper_gua}，下卦{result.postnatal.lower_gua}）
- **元堂**: {result.yuantang.yuantang}（{result.yuantang.yao_nature}）

### 天地数

- 天数: {result.numbers.tian_shu}（化简: {result.numbers.tian_reduced}）
- 地数: {result.numbers.di_shu}（化简: {result.numbers.di_reduced}）

### 计算细节

{chr(10).join(result.numbers.details)}

---

{RUBRIC_SECTION}

---

**禁止信息**: 本文件不包含 Ground Truth、其他 Rater 评分、系统内部计算链、系统 confidence 值。
"""
        
        md_path = output_dir / f"{sample_id}_BLIND.md"
        md_path.write_text(md, encoding='utf-8')
        count += 1
        
    except Exception as e:
        print(f"ERROR {sample_id}: {e}")
        continue

print(f"Generated {count} case files in {output_dir}")
