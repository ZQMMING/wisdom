# -*- coding: utf-8 -*-
"""基于 agnes-2.5-flash 重跑 Expert Pilot 评分（替代失效的 token.mwx.cn）。
从 Hermes config.yaml 读取 agnes key/base_url。输出 ai_ratings_agnes.json。"""
import json, os, time, yaml, requests
from pathlib import Path
from datetime import datetime

# 读取 agnes 配置
cfg = yaml.safe_load(open(r'C:\Users\ming\AppData\Local\hermes\config.yaml', encoding='utf-8'))
agn = cfg.get('providers', {}).get('agnes-cn', {})
API_KEY = agn.get('api_key', '')
BASE_URL = agn.get('base_url', '')

# 模型：agnes-2.5-flash（reasoning 模型）
RATERS = {'A': 'agnes-2.5-flash'}

cases_dir = Path("dataset/accuracy/expert_pilot/cases_v2")
case_files = sorted(cases_dir.glob("SAMPLE_*_BLIND.md"))
print(f"Found {len(case_files)} case files | raters={RATERS}")

def call_model(model, case_content):
    prompt = f"""{case_content}

请严格按照上述 Rubric 对系统输出进行评分，输出 JSON 格式。"""
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3, "max_tokens": 4000}
    try:
        resp = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=data, timeout=180)
        resp.raise_for_status()
        content = resp.json()['choices'][0]['message']['content']
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

results = {'metadata': {'created_at': datetime.now().isoformat(), 'total_cases': len(case_files),
                        'raters': RATERS, 'rubric_version': 'v2-0-3'}, 'ratings': []}

for i, cf in enumerate(case_files):
    case_id = cf.stem.replace('_BLIND', '')
    content = cf.read_text(encoding='utf-8')
    rating, err = call_model('agnes-2.5-flash', content)
    entry = {'case_id': case_id, 'ratings': {}, 'errors': {}}
    if err:
        entry['errors']['A'] = err
        print(f"[{i+1}/{len(case_files)}] {case_id} ERROR {err[:60]}")
    else:
        entry['ratings']['A'] = rating
        print(f"[{i+1}/{len(case_files)}] {case_id} OK")
    results['ratings'].append(entry)
    # 每5个保存中间结果
    if (i + 1) % 5 == 0:
        with open("dataset/accuracy/expert_pilot/ai_ratings_agnes.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"  [saved {i+1}]")
    time.sleep(0.5)

with open("dataset/accuracy/expert_pilot/ai_ratings_agnes.json", 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\nDONE saved to ai_ratings_agnes.json")
