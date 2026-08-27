#!/usr/bin/env python3
"""
A3.6-A: AI Expert Simulation - 3 Raters Independent Rating

Raters:
  - Rater A: deepseek-v4-pro (Claude via MWX)
  - Rater B: qwen3.7-max (dsh via MWX)
  - Rater C: kimi-k2.7-code (via MWX)

Rubric: 7 dimensions, 0-3 scoring

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
RATERS = {
    'A': 'deepseek-v4-pro',
    'B': 'qwen3.7-max',
    'C': 'kimi-k2.7-code'
}

# Load cases
cases_dir = Path("dataset/accuracy/expert_pilot/cases_v2")
case_files = sorted(cases_dir.glob("SAMPLE_*_BLIND.md"))

print(f"Found {len(case_files)} case files")
print(f"Raters: {RATERS}")

def call_model(model, case_content, case_id):
    """Call model API to rate a case"""
    
    prompt = f"""{case_content}

请严格按照上述 Rubric 对系统输出进行评分，输出 JSON 格式。"""

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
        "max_tokens": 3000
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=data,
            timeout=120
        )
        response.raise_for_status()
        result = response.json()
        
        content = result['choices'][0]['message']['content']
        
        # Extract JSON from response
        content = content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        rating = json.loads(content)
        rating['rater'] = model
        rating['timestamp'] = datetime.now().isoformat()
        
        return rating, None
        
    except Exception as e:
        return None, str(e)

# Process cases (batch mode for efficiency)
results = {
    'metadata': {
        'created_at': datetime.now().isoformat(),
        'total_cases': len(case_files),
        'raters': RATERS,
        'rubric_version': 'v2-0-3'
    },
    'ratings': []
}

# Process in batches to avoid timeout
batch_size = 5
for batch_start in range(0, len(case_files), batch_size):
    batch_end = min(batch_start + batch_size, len(case_files))
    batch = case_files[batch_start:batch_end]
    
    print(f"\n=== Batch {batch_start//batch_size + 1}: Cases {batch_start+1}-{batch_end} ===")
    
    for i, case_file in enumerate(batch):
        case_num = batch_start + i + 1
        case_id = case_file.stem.replace('_BLIND', '')
        print(f"\n[{case_num}/{len(case_files)}] {case_id}")
        
        case_content = case_file.read_text(encoding='utf-8')
        
        ratings = {}
        errors = {}
        
        for rater_key, model in RATERS.items():
            print(f"  Rater {rater_key} ({model})...", end=' ')
            rating, error = call_model(model, case_content, case_id)
            if error:
                print(f"ERROR: {error[:50]}")
                errors[rater_key] = error
            else:
                total = sum(d.get('score', 0) for d in rating.get('dimensions', {}).values())
                print(f"Score: {total}/21")
                ratings[rater_key] = rating
            time.sleep(0.5)
        
        results['ratings'].append({
            'case_id': case_id,
            'ratings': ratings,
            'errors': errors
        })
    
    # Save intermediate results
    output_file = Path("dataset/accuracy/expert_pilot/ai_ratings_v2.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[Saved intermediate results: {len(results['ratings'])} cases]")

# Final summary
print(f"\n\n{'='*60}")
print(f"FINAL SUMMARY")
print(f"{'='*60}")
print(f"Total cases: {len(results['ratings'])}")

for rater_key, model in RATERS.items():
    success = sum(1 for r in results['ratings'] if rater_key in r['ratings'])
    print(f"Rater {rater_key} ({model}): {success}/{len(case_files)} successful")

print(f"\nResults saved to: {output_file}")
