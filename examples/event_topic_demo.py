"""调用方示例 — 如何接入 EVENT_TOPIC 引擎到断事流程"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from tongshu.reasoning.event_topic import EventTopicEngine
from tongshu.engines.bazi_engine import BaziEngine


def load_active_rules(rules_dir: str = 'data/rules') -> list[dict]:
    """加载所有 active 规则文件"""
    rules = []
    rules_path = Path(__file__).parent.parent / rules_dir
    for json_file in rules_path.glob('*.json'):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'rules' in data:
                rules.extend(data['rules'])
    return rules


def evaluate_birth_event_topics(birth_info: dict) -> dict:
    """
    评估命局的 EVENT_TOPIC 信号（婚姻/健康风险）。
    
    参数:
        birth_info: {year, month, day, hour_start, gender}
    
    返回:
        {
            'chart': BaziChart,
            'signals': list[EventTopicSignal],
            'marriage_risk': float,
            'health_risk': float,
        }
    """
    # 加载规则
    rules = load_active_rules()
    print(f'Loaded {len(rules)} active rules')
    
    # 排盘
    be = BaziEngine()
    gender = 'female' if birth_info.get('gender') == '女' else 'male'
    chart = be.compute(
        (birth_info['year'], birth_info['month'], birth_info['day'], 
         birth_info.get('hour_start', 12)),
        gender=gender
    )
    
    # 创建引擎
    engine = EventTopicEngine(rules)
    
    # 匹配信号
    signals = engine.match(chart)
    
    # 计算风险分数
    marriage_score = sum(
        1.0 if s.ontology_type == 'MARRIAGE_RISK' else 
        (-0.5 if s.ontology_type == 'MARRIAGE_OPPORTUNITY' else 0.0)
        for s in signals
    )
    health_score = sum(
        1.0 if s.ontology_type == 'HEALTH_RISK' else 0.0
        for s in signals
    )
    
    return {
        'chart': chart,
        'signals': signals,
        'marriage_risk': marriage_score,
        'health_risk': health_score,
    }


if __name__ == '__main__':
    # 测试案例
    test_cases = [
        {'year': 1982, 'month': 9, 'day': 27, 'hour_start': 15, 'gender': '女'},
        {'year': 1960, 'month': 12, 'day': 10, 'hour_start': 10, 'gender': '男'},
    ]
    
    for bc in test_cases:
        print(f'\n=== 案例: {bc["year"]}-{bc["month"]:02d}-{bc["day"]:02d} ({bc["gender"]}) ===')
        result = evaluate_birth_event_topics(bc)
        print(f"  Marriage risk: {result['marriage_risk']}")
        print(f"  Health risk: {result['health_risk']}")
        print(f"  Signals: {len(result['signals'])}")
        for s in result['signals']:
            print(f"    - {s.signal_id}: {s.ontology_type}")
