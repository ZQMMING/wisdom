#!/usr/bin/env python3
"""
A3.6-A: AI Expert Simulation - Independent Rating

Calls deepseek-v4-pro and qwen3.7-max to rate 40 cases independently.

Required environment variables:
  SENSENOVA_API_KEY - API key for the MWX/SenseNova token endpoint
"""

import json
import os
import requests
import time
from pathlib import Path
from datetime import datetime

# API config
API_KEY = os.environ["SENSENOVA_API_KEY"]
BASE_URL = "https://token.mwx.cn/v1"

# Models
RATER_A = "deepseek-v4-pro"
RATER_B = "qwen3.7-max"

# Load cases
cases_dir = Path("dataset/accuracy/expert_pilot/cases")
case_files = sorted(cases_dir.glob("SAMPLE_*_BLIND.md"))

print(f"Found {len(case_files)} case files")

def call_model(model, case_content, case_id):
    """Call model API to rate a case"""
    
    prompt = f"""你是一位易学专家，请按照以下 Rubric 对顺天系统的河洛卦象解释进行评分。

{case_content}

请输出 JSON 格式的评分结果，包含以下字段：
- case_id: 案例ID
- rater: 评分者名称
- timestamp: 评分时间
- scores: 7个维度的评分对象，每个维度包含 status, score, reason, confidence
- evaluable_dimensions: 可评维度数
- total_score: 总分
- normalized_score: 归一化评分
- comments: 总体评价

评分维度 (0-2分):
1. STATE: 卦象状态描述准确性
2. OPPORTUNITY: 机会识别合理性
3. RISK: 风险识别合理性
4. REMEDIATION: 化解建议一致性
5. ACTION: 行动建议可操作性
6. TEMPORAL: 时间状态映射正确性
7. EVIDENCE: 经典引用具体性

如果某维度无法评估，标记 status 为 "NOT_EVALUABLE" 并说明原因。

请只输出 JSON，不要其他内容。"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        
        content = result['choices'][0]['message']['content']
        
        # Try to parse JSON from response
        # Remove markdown code blocks if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        rating = json.loads(content)
        rating['rater'] = model
        rating['timestamp'] = datetime.now().isoformat()
        
        return rating, None
        
    except Exception as e:
        return None, str(e)

# Process cases
results = {
    'metadata': {
        'created_at': datetime.now().isoformat(),
        'total_cases': len(case_files),
        'rater_a': RATER_A,
        'rater_b': RATER_B
    },
    'ratings': []
}

for i, case_file in enumerate(case_files):
    case_id = case_file.stem.replace('_BLIND', '')
    print(f"\n[{i+1}/{len(case_files)}] Processing {case_id}")
    
    # Read case content
    case_content = case_file.read_text(encoding='utf-8')
    
    # Call Rater A
    print(f"  Calling {RATER_A}...")
    rating_a, error_a = call_model(RATER_A, case_content, case_id)
    if error_a:
        print(f"    ERROR: {error_a}")
    else:
        print(f"    Score: {rating_a.get('total_score', 'N/A')}/14")
    
    # Call Rater B
    print(f"  Calling {RATER_B}...")
    rating_b, error_b = call_model(RATER_B, case_content, case_id)
    if error_b:
        print(f"    ERROR: {error_b}")
    else:
        print(f"    Score: {rating_b.get('total_score', 'N/A')}/14")
    
    # Store results
    results['ratings'].append({
        'case_id': case_id,
        'rater_a': rating_a,
        'rater_a_error': error_a,
        'rater_b': rating_b,
        'rater_b_error': error_b
    })
    
    # Rate limit
    time.sleep(1)

# Save results
output_file = Path("dataset/accuracy/expert_pilot/ai_ratings.json")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n\nResults saved to {output_file}")
print(f"Total ratings: {len(results['ratings'])}")

# Summary
success_a = sum(1 for r in results['ratings'] if r['rater_a'])
success_b = sum(1 for r in results['ratings'] if r['rater_b'])
print(f"Rater A ({RATER_A}): {success_a}/{len(case_files)} successful")
print(f"Rater B ({RATER_B}): {success_b}/{len(case_files)} successful")
