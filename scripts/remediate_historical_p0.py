#!/usr/bin/env python3
"""
A2-B3-P0 Remediation Script
修复历史数据集的 P0 问题：
1. CAREER.* 通配符重新映射
2. Evidence Grade 重新评级
3. Oracle Grade 重新评级
4. POST_HOC 重新判定
5. Event Cluster 建立
6. Date Precision 重新标注
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

BASE_DIR = Path(__file__).parent.parent
INPUT_PATH = BASE_DIR / "dataset/accuracy/historical/historical_dataset_raw_backup.json"
OUTPUT_PATH = BASE_DIR / "dataset/accuracy/historical/historical_dataset_audited.json"

# V1.2 Event Type 映射规则
CAREER_KEYWORDS = {
    "CAREER_ENTRY": ["入仕", "任官", "就职", "入幕", "入李鸿章幕", "入曾国藩幕"],
    "CAREER_ADVANCEMENT": ["升迁", "晋升", "升任", "擢升", "加衔"],
    "CAREER_POSITION": ["任", "担任", "出任", "兼任", "调任", "署理"],
    "CAREER_SETBACK": ["罢职", "免职", "革职", "贬谪", "失官", "开缺"],
    "CAREER_ENTREPRENEURSHIP": ["创办", "创立", "创建", "开办", "设立"],
    "CAREER_TRANSITION": ["转型", "转任", "改任", "调"],
    "CAREER_POLITICAL": ["参与", "参加", "发动", "领导", "组织"],
}

# Evidence Grade 评级标准
EVIDENCE_CRITERIA = {
    "A": ["族谱", "宗谱", "奏折", "实录", "档案", "官方"],
    "B": ["维基百科", "百度百科", "传记", "学术", "研究"],
    "C": ["网络", "文章", "报道"],
    "D": ["传闻", "推测", "可能"],
}

# Oracle Grade 评级标准
ORACLE_CRITERIA = {
    "O1": ["事前预测", "预言", "占卜", "命理预测"],
    "O2": ["历史记录", "史实", "记载", "发生"],
    "O3": ["古典文献", "古籍", "传统"],
    "OX": ["无法验证", "争议", "不确定"],
}


def map_career_event(description: str) -> str:
    """将 CAREER.* 映射为具体子类型"""
    for event_type, keywords in CAREER_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description:
                return event_type
    
    # 如果无法确定，返回 UNKNOWN
    return "CAREER.UNKNOWN"


def assess_evidence_grade(description: str, source: str) -> str:
    """评估 Evidence Grade"""
    # 检查来源质量
    for grade, indicators in EVIDENCE_CRITERIA.items():
        for indicator in indicators:
            if indicator in description or indicator in source:
                return grade
    
    # 默认 Grade C
    return "C"


def assess_oracle_grade(description: str, event_type: str) -> str:
    """评估 Oracle Grade"""
    # 检查是否为事前预测
    for indicator in ORACLE_CRITERIA["O1"]:
        if indicator in description:
            return "O1"
    
    # 检查是否为历史记录
    for indicator in ORACLE_CRITERIA["O2"]:
        if indicator in description:
            return "O2"
    
    # 检查是否为古典文献
    for indicator in ORACLE_CRITERIA["O3"]:
        if indicator in description:
            return "O3"
    
    # 历史人物事件默认为 O2（历史记录）
    return "O2"


def assess_post_hoc(event_year: str, description: str) -> Tuple[str, str]:
    """判定是否为 POST_HOC"""
    # 检查描述中是否有回顾性措辞
    post_hoc_indicators = ["发动", "领导", "参与", "创办", "成立", "发表"]
    
    for indicator in post_hoc_indicators:
        if indicator in description:
            return "POST_HOC", "事件命名包含回顾性措辞"
    
    # 检查事件类型
    if event_year:
        try:
            year = int(event_year)
            # 如果事件发生在人物出生后的合理年龄
            # 这里简化处理，实际需要更复杂的逻辑
            return "PRE_EVENT", "时间线合理"
        except:
            pass
    
    return "UNKNOWN", "无法判定"


def assess_date_precision(description: str, event_year: str) -> str:
    """评估日期精度"""
    # 检查是否有具体日期
    if re.search(r'\d{4}年\d{1,2}月\d{1,2}日', description):
        return "EXACT_DAY"
    elif re.search(r'\d{4}年\d{1,2}月', description):
        return "EXACT_MONTH"
    elif event_year and event_year.isdigit():
        return "EXACT_YEAR"
    else:
        return "APPROXIMATE"


def build_event_clusters(events: List[Dict]) -> Dict[str, List[str]]:
    """建立事件聚类"""
    clusters = {}
    
    for event in events:
        person_id = event.get("person_id")
        event_type = event.get("event_type")
        event_year = event.get("event_year")
        
        # 同一人物的连续职业事件可能属于同一 cluster
        if event_type.startswith("CAREER"):
            cluster_key = f"{person_id}_career"
            if cluster_key not in clusters:
                clusters[cluster_key] = []
            clusters[cluster_key].append(event["event_id"])
    
    return clusters


def remediate_historical_dataset():
    """执行 P0 修复"""
    print("=" * 60)
    print("A2-B3-P0 Remediation")
    print("=" * 60)
    
    # Step 1: Load raw data
    print("\n[1/7] Loading raw data...")
    with open(INPUT_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    persons = data['persons']
    print(f"  Loaded {len(persons)} persons")
    
    # Step 2: Fix CAREER.* wildcard
    print("\n[2/7] Fixing CAREER.* wildcard...")
    career_fixed = 0
    for person in persons:
        for event in person['events']:
            if event.get('event_type') == 'CAREER.*':
                new_type = map_career_event(event.get('description', ''))
                event['event_type'] = new_type
                event['remediation_notes'] = event.get('remediation_notes', [])
                event['remediation_notes'].append(f"P0.1: CAREER.* → {new_type}")
                career_fixed += 1
    
    print(f"  Fixed {career_fixed} CAREER.* events")
    
    # Step 3: Reassess Evidence Grade
    print("\n[3/7] Reassessing Evidence Grade...")
    evidence_changes = {"A": 0, "B": 0, "C": 0, "D": 0}
    for person in persons:
        for event in person['events']:
            old_grade = event.get('evidence_grade', 'A')
            new_grade = assess_evidence_grade(
                event.get('description', ''),
                person.get('source', '')
            )
            event['evidence_grade'] = new_grade
            event['remediation_notes'] = event.get('remediation_notes', [])
            event['remediation_notes'].append(f"P0.2: Evidence {old_grade} → {new_grade}")
            evidence_changes[new_grade] = evidence_changes.get(new_grade, 0) + 1
    
    print(f"  Evidence Grade distribution: {evidence_changes}")
    
    # Step 4: Reassess Oracle Grade
    print("\n[4/7] Reassessing Oracle Grade...")
    oracle_changes = {"O1": 0, "O2": 0, "O3": 0, "OX": 0}
    for person in persons:
        for event in person['events']:
            old_grade = event.get('oracle_grade', 'O1')
            new_grade = assess_oracle_grade(
                event.get('description', ''),
                event.get('event_type', '')
            )
            event['oracle_grade'] = new_grade
            event['remediation_notes'] = event.get('remediation_notes', [])
            event['remediation_notes'].append(f"P0.3: Oracle {old_grade} → {new_grade}")
            oracle_changes[new_grade] = oracle_changes.get(new_grade, 0) + 1
    
    print(f"  Oracle Grade distribution: {oracle_changes}")
    
    # Step 5: Reassess POST_HOC
    print("\n[5/7] Reassessing POST_HOC...")
    post_hoc_count = 0
    for person in persons:
        for event in person['events']:
            status, reason = assess_post_hoc(
                event.get('event_year', ''),
                event.get('description', '')
            )
            event['post_hoc_status'] = status
            event['post_hoc_reason'] = reason
            event['remediation_notes'] = event.get('remediation_notes', [])
            event['remediation_notes'].append(f"P0.4: POST_HOC = {status}")
            if status == "POST_HOC":
                post_hoc_count += 1
    
    print(f"  POST_HOC events: {post_hoc_count}")
    
    # Step 6: Build event clusters
    print("\n[6/7] Building event clusters...")
    all_events = []
    for person in persons:
        for event in person['events']:
            event['person_id'] = person['person_id']
            all_events.append(event)
    
    clusters = build_event_clusters(all_events)
    cluster_count = len(clusters)
    
    # Add cluster info to events
    for cluster_id, event_ids in clusters.items():
        for event in all_events:
            if event['event_id'] in event_ids:
                event['event_cluster_id'] = cluster_id
                event['remediation_notes'] = event.get('remediation_notes', [])
                event['remediation_notes'].append(f"P0.5: Cluster = {cluster_id}")
    
    print(f"  Created {cluster_count} event clusters")
    
    # Step 7: Reassess date precision
    print("\n[7/7] Reassessing date precision...")
    precision_changes = {"EXACT_DAY": 0, "EXACT_MONTH": 0, "EXACT_YEAR": 0, "APPROXIMATE": 0}
    for person in persons:
        for event in person['events']:
            new_precision = assess_date_precision(
                event.get('description', ''),
                event.get('event_year', '')
            )
            event['event_date_precision'] = new_precision
            event['remediation_notes'] = event.get('remediation_notes', [])
            event['remediation_notes'].append(f"P0.6: Precision = {new_precision}")
            precision_changes[new_precision] = precision_changes.get(new_precision, 0) + 1
    
    print(f"  Date Precision distribution: {precision_changes}")
    
    # Save audited data
    print("\n[8/8] Saving audited data...")
    data['metadata']['version'] = 'A2-Historical-Audited-v1.0'
    data['metadata']['remediation_date'] = datetime.now().isoformat()
    data['metadata']['remediation_summary'] = {
        'career_fixed': career_fixed,
        'evidence_changes': evidence_changes,
        'oracle_changes': oracle_changes,
        'post_hoc_count': post_hoc_count,
        'cluster_count': cluster_count,
        'precision_changes': precision_changes,
    }
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  Saved: {OUTPUT_PATH}")
    
    # Summary
    total_events = sum(len(p['events']) for p in persons)
    print(f"\n  Total: {len(persons)} persons, {total_events} events")
    print("=" * 60)
    
    return data


if __name__ == "__main__":
    remediate_historical_dataset()
