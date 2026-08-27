#!/usr/bin/env python3
"""
A3.6-A: Generate 40 Blind Case MD files for AI Expert Simulation

Generates CASE_xxxx_BLIND.md files with:
- Person birth info
- System output (HeluoCanonical)
- Rubric scoring instructions
- NO ground truth
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

# Build person lookup
persons = {p['person_id']: p for p in pilot['persons']}

# Initialize engines
be = BaziEngine()
hc = HeluoCanonical()

# Hour mapping
hour_map = {
    '子': 23, '丑': 1, '寅': 3, '卯': 5, '辰': 7, '巳': 9,
    '午': 11, '未': 13, '申': 15, '酉': 17, '戌': 19, '亥': 21
}

# Gender mapping
gender_map = {'男': 'male', '女': 'female'}

# Generate cases
output_dir = Path('dataset/accuracy/expert_pilot/cases')
output_dir.mkdir(exist_ok=True)

for sample in frozen['samples']:
    sample_id = sample['sample_id']
    person_id = sample['person_id']
    
    if person_id not in persons:
        print(f"WARNING: {person_id} not found in pilot dataset")
        continue
    
    person = persons[person_id]
    
    # Parse birth info
    birth_date = person.get('birth_date', '')
    birth_hour_cn = person.get('birth_hour', '子')
    gender_cn = person.get('gender', '男')
    
    if not birth_date:
        print(f"WARNING: {person_id} missing birth_date")
        continue
    
    # Parse date
    parts = birth_date.split('-')
    if len(parts) != 3:
        print(f"WARNING: {person_id} invalid birth_date: {birth_date}")
        continue
    
    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    hour = hour_map.get(birth_hour_cn, 0)
    gender = gender_map.get(gender_cn, 'male')
    
    # Compute Bazi
    try:
        chart = be.compute((year, month, day, hour), gender)
        chart_dict = chart.to_dict()
            
        # Get Chinese pillars
        pillars_cn = chart.get_pillars_chinese()
            
        # Extract pillars for Heluo (need to parse Chinese)
        stem_branch_map = {
            '甲': ('JIA', 'ZI'), '乙': ('YI', 'CHOU'), '丙': ('BING', 'YIN'),
            '丁': ('DING', 'MAO'), '戊': ('WU', 'CHEN'), '己': ('JI', 'SI'),
            '庚': ('GENG', 'WU'), '辛': ('XIN', 'WEI'), '壬': ('REN', 'SHEN'),
            '癸': ('GUI', 'YOU')
        }
            
        # Parse Chinese pillars to tuples
        pillars = []
        for pillar_name in ['year', 'month', 'day', 'hour']:
            cn = pillars_cn[pillar_name]
            stem = cn[0]
            branch = cn[1]
            pillars.append((stem, branch))
            
        # Compute Heluo
        result = hc.calculate(pillars, gender, birth_hour_cn, 'zhong')
        
        # Generate MD content
        md_content = f"""# {sample_id} — Blind Evaluation

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

- **先天卦**: {result.prenatal.hexagram_name}
- **后天卦**: {result.postnatal.hexagram_name}
- **元堂**: {result.yuantang.yuantang}

### 天地数

- 天数: {result.numbers.tian_shu} (化简: {result.numbers.tian_reduced})
- 地数: {result.numbers.di_shu} (化简: {result.numbers.di_reduced})

### 解释

先天卦 {result.prenatal.hexagram_name}，元堂{result.yuantang.yuantang}，后天卦 {result.postnatal.hexagram_name}。

---

## 评分任务

请按照以下 Rubric 对系统输出进行评分：

### 评分维度 (0-2 分)

| Dimension | 2分 (优秀) | 1分 (合格) | 0分 (不合格) |
|-----------|-----------|-----------|-------------|
| STATE | 准确引用卦名、卦象、体用关系 | 基本正确但有遗漏 | 错误或缺失 |
| OPPORTUNITY | 识别具体机会，有经典依据 | 识别但缺乏依据 | 未识别或错误 |
| RISK | 识别具体风险，有经典依据 | 识别但缺乏依据 | 未识别或错误 |
| REMEDIATION | 建议与RISK对应，符合易理 | 建议合理但不具体 | 矛盾或缺失 |
| ACTION | 建议具体可执行 | 建议可操作但关联不强 | 不可操作或矛盾 |
| TEMPORAL | 正确映射时间状态 | 基本正确但有偏差 | 错误或缺失 |
| EVIDENCE | 引用具体经典 | 有引用但不具体 | 无引用或错误 |

### NOT_EVALUABLE

如果某维度无法评估，标记为 NOT_EVALUABLE 并说明原因：
- INSUFFICIENT_EVIDENCE: 系统未提供足够信息
- AMBIGUOUS: 输出模糊无法判断
- NOT_APPLICABLE: 该维度不适用
- MISSING: 维度完全缺失

### 输出格式

请输出 JSON 格式的评分结果：

```json
{{
  "case_id": "{sample_id}",
  "rater": "GPT",
  "timestamp": "2026-08-22T10:00:00Z",
  "scores": {{
    "state": {{"status": "SCORED", "score": 0, "reason": "...", "confidence": "HIGH/MEDIUM/LOW"}},
    "opportunity": {{"status": "SCORED", "score": 0, "reason": "...", "confidence": "HIGH/MEDIUM/LOW"}},
    "risk": {{"status": "SCORED", "score": 0, "reason": "...", "confidence": "HIGH/MEDIUM/LOW"}},
    "remediation": {{"status": "SCORED", "score": 0, "reason": "...", "confidence": "HIGH/MEDIUM/LOW"}},
    "action": {{"status": "SCORED", "score": 0, "reason": "...", "confidence": "HIGH/MEDIUM/LOW"}},
    "temporal": {{"status": "SCORED", "score": 0, "reason": "...", "confidence": "HIGH/MEDIUM/LOW"}},
    "evidence": {{"status": "SCORED", "score": 0, "reason": "...", "confidence": "HIGH/MEDIUM/LOW"}}
  }},
  "evaluable_dimensions": 7,
  "total_score": 0,
  "normalized_score": 0.0,
  "comments": "..."
}}
```

---

## 禁止信息

本文件**不包含**：
- ❌ Ground Truth (历史事件结果)
- ❌ 其他 Rater 评分
- ❌ 系统内部计算链
- ❌ 系统 confidence 值

---

**生成者**: Hermes (Engineering Auditor)
**日期**: 2026-08-22
**版本**: A3.6-A-CaseFormat-v1
"""
        
        # Write MD file
        md_path = output_dir / f"{sample_id}_BLIND.md"
        md_path.write_text(md_content, encoding='utf-8')
        print(f"Generated: {md_path.name}")
        
    except Exception as e:
        print(f"ERROR processing {sample_id}: {e}")
        continue

print(f"\nGenerated {len(list(output_dir.glob('*.md')))} case files in {output_dir}")
