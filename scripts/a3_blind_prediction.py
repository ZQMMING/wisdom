#!/usr/bin/env python3
"""
A3.2 Blind Prediction Execution (Simplified)

对 86 个 BLIND 事件执行方向预测。

限制：
- 系统输出整体状态解释，不是事件特定预测
- 从 state 字段提取方向（吉/凶/平 → POSITIVE/NEGATIVE/NEUTRAL）
- 这是 Pilot-scale validation，不是生产级 accuracy certification
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.heluo.canonical import HeluoCanonical
from tongshu.engines.yi import YiInterpreter


def load_blind_events():
    """加载 BLIND 事件"""
    blind_path = Path(__file__).parent.parent / "dataset/accuracy/blind/blind_candidates.json"
    with open(blind_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['events']


def load_pilot_persons():
    """加载 Pilot 人物信息"""
    pilot_path = Path(__file__).parent.parent / "dataset/accuracy/pilot/pilot_dataset.json"
    with open(pilot_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    person_lookup = {}
    for p in data['persons']:
        person_lookup[p['person_id']] = {
            'birth_date': p.get('birth_date'),
            'birth_hour': p.get('birth_hour'),
            'gender': p.get('gender'),
        }
    return person_lookup


def parse_birth_info(birth_date: str, birth_hour: str):
    """解析出生信息"""
    if not birth_date or not birth_hour:
        return None
    
    parts = birth_date.split('-')
    if len(parts) != 3:
        return None
    
    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    
    # Map Chinese hour to actual hour (0-23)
    hour_map = {
        '子': 0, '丑': 2, '寅': 4, '卯': 6, '辰': 8, '巳': 10,
        '午': 12, '未': 14, '申': 16, '酉': 18, '戌': 20, '亥': 22
    }
    
    hour = hour_map.get(birth_hour, 12)
    
    return year, month, day, hour


def predict_direction(birth_date: str, birth_hour: str, gender: str) -> str:
    """
    预测方向
    
    流程:
    1. BaziEngine.compute() → 四柱
    2. HeluoCanonical.calculate() → 卦象
    3. YiInterpreter.interpret() → 解释
    4. 从 state 字段提取方向（吉/凶/平）
    """
    try:
        # Parse birth info
        birth_info = parse_birth_info(birth_date, birth_hour)
        if not birth_info:
            return "NEUTRAL"
        
        year, month, day, hour = birth_info
        
        # Step 1: Compute Bazi
        be = BaziEngine()
        bazi_chart = be.compute((year, month, day, hour), gender)
        
        # Step 2: Convert to Chinese format
        stem_map = {
            'JIA': '甲', 'YI': '乙', 'BING': '丙', 'DING': '丁', 'WU': '戊',
            'JI': '己', 'GENG': '庚', 'XIN': '辛', 'REN': '壬', 'GUI': '癸'
        }
        branch_map = {
            'ZI': '子', 'CHOU': '丑', 'YIN': '寅', 'MAO': '卯', 'CHEN': '辰', 'SI': '巳',
            'WU': '午', 'WEI': '未', 'SHEN': '申', 'YOU': '酉', 'XU': '戌', 'HAI': '亥'
        }
        
        bazi_list = [
            (stem_map[bazi_chart.year_pillar.heavenly_stem], branch_map[bazi_chart.year_pillar.earthly_branch]),
            (stem_map[bazi_chart.month_pillar.heavenly_stem], branch_map[bazi_chart.month_pillar.earthly_branch]),
            (stem_map[bazi_chart.day_pillar.heavenly_stem], branch_map[bazi_chart.day_pillar.earthly_branch]),
            (stem_map[bazi_chart.hour_pillar.heavenly_stem], branch_map[bazi_chart.hour_pillar.earthly_branch]),
        ]
        
        # Step 3: Run HeluoCanonical
        hc = HeluoCanonical()
        heluo_result = hc.calculate(bazi_list, gender, birth_hour)
        
        # Step 4: Run YiInterpreter
        hexagram_name = heluo_result.postnatal.hexagram_name
        lines = heluo_result.postnatal.lines
        yuantang_index = heluo_result.yuantang.yuantang_index
        
        yi = YiInterpreter()
        interpretation = yi.interpret(hexagram_name, lines, yuantang_index, heluo_result)
        
        # Step 5: Extract direction from state
        state = interpretation.state
        direction = extract_direction_from_state(state)
        
        return direction
    except Exception as e:
        print(f"  Prediction error: {e}")
        return "NEUTRAL"


def extract_direction_from_state(state: str) -> str:
    """
    从 state 字段提取方向
    
    吉 → POSITIVE
    凶 → NEGATIVE
    平/中性 → NEUTRAL
    """
    if not state:
        return "NEUTRAL"
    
    # Check for positive indicators
    positive_keywords = ['吉', '利', '顺', '成', '旺', '兴', '发']
    for kw in positive_keywords:
        if kw in state:
            return "POSITIVE"
    
    # Check for negative indicators
    negative_keywords = ['凶', '不利', '逆', '败', '衰', '困', '克']
    for kw in negative_keywords:
        if kw in state:
            return "NEGATIVE"
    
    # Default to NEUTRAL
    return "NEUTRAL"


def run_blind_prediction():
    """执行 BLIND 预测"""
    print("=" * 60)
    print("A3.2 Blind Prediction Execution")
    print("=" * 60)
    
    # Load data
    print("\n[1/4] Loading data...")
    events = load_blind_events()
    persons = load_pilot_persons()
    print(f"  BLIND events: {len(events)}")
    print(f"  Pilot persons: {len(persons)}")
    
    # Run predictions
    print("\n[2/4] Running predictions...")
    results = []
    
    for i, event in enumerate(events, 1):
        if i % 10 == 0:
            print(f"  Processing {i}/{len(events)}...")
        
        event_id = event.get('event_id')
        person_id = event.get('person_id')
        actual_direction = event.get('event_direction', 'NEUTRAL')
        
        # Get birth info
        person = persons.get(person_id)
        if not person:
            results.append({
                'event_id': event_id,
                'predicted': None,
                'actual': actual_direction,
                'match': False,
                'error': 'Person not found'
            })
            continue
        
        birth_date = person.get('birth_date')
        birth_hour = person.get('birth_hour')
        gender_cn = person.get('gender', '男')
        
        # Convert Chinese gender to English
        gender_map = {'男': 'male', '女': 'female'}
        gender = gender_map.get(gender_cn, 'male')
        
        if not birth_date or not birth_hour:
            results.append({
                'event_id': event_id,
                'predicted': None,
                'actual': actual_direction,
                'match': False,
                'error': 'Invalid birth info'
            })
            continue
        
        # Run prediction
        predicted = predict_direction(birth_date, birth_hour, gender)
        
        # Compare
        match = (predicted == actual_direction)
        
        results.append({
            'event_id': event_id,
            'person_id': person_id,
            'predicted': predicted,
            'actual': actual_direction,
            'match': match,
            'event_year': event.get('event_year'),
            'event_type': event.get('event_type'),
        })
    
    # Calculate metrics
    print("\n[3/4] Calculating metrics...")
    tp = sum(1 for r in results if r['match'] and r['predicted'] is not None)
    fp = sum(1 for r in results if not r['match'] and r['predicted'] is not None)
    fn = sum(1 for r in results if r['predicted'] is None)
    
    total = len(results)
    valid = sum(1 for r in results if r['predicted'] is not None)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    print(f"  Total events: {total}")
    print(f"  Valid predictions: {valid}")
    print(f"  TP: {tp}, FP: {fp}, FN: {fn}")
    print(f"  Precision: {precision:.3f}")
    print(f"  Recall: {recall:.3f}")
    print(f"  Micro-F1: {f1:.3f}")
    
    # Direction distribution
    pred_dist = Counter(r['predicted'] for r in results if r['predicted'])
    actual_dist = Counter(r['actual'] for r in results)
    print(f"\n  Predicted direction distribution: {dict(pred_dist)}")
    print(f"  Actual direction distribution: {dict(actual_dist)}")
    
    # Save results
    print("\n[4/4] Saving results...")
    output = {
        'metadata': {
            'version': 'A3.2-Blind-Prediction-v1.0',
            'created_at': datetime.now().isoformat(),
            'total_events': total,
            'valid_predictions': valid,
            'note': 'Pilot-scale validation, not production certification',
        },
        'metrics': {
            'tp': tp,
            'fp': fp,
            'fn': fn,
            'precision': precision,
            'recall': recall,
            'micro_f1': f1,
        },
        'results': results,
    }
    
    output_path = Path(__file__).parent.parent / "dataset/accuracy/blind/blind_prediction_results.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"  Saved: {output_path}")
    print("=" * 60)
    
    return output


if __name__ == "__main__":
    run_blind_prediction()
