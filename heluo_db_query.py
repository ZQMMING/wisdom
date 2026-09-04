#!/usr/bin/env python3
"""
HeluoRuleEvidence 数据库查询工具
"""

import sqlite3
from pathlib import Path

DB_PATH = Path.home() / "wisdom" / "heluo_rule_evidence.db"

def query_all():
    """查询所有规则"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    print("="*60)
    print("河洛理数证据矩阵数据库查询")
    print("="*60)
    
    # 1. 规则概览
    print("\n【规则总览】")
    cursor = conn.execute("""
        SELECT rule_id, rule_name, verification_status, evidence_rating 
        FROM rules ORDER BY rule_id
    """)
    for row in cursor.fetchall():
        status_icon = "✓" if row['verification_status'] in ['已验证', '已补全'] else "⚠"
        print(f"  {status_icon} {row['rule_id']} {row['rule_name']:10s} | {row['verification_status']:6s} | {row['evidence_rating']}")
    
    # 2. 证据来源
    print("\n【证据来源】")
    cursor = conn.execute("SELECT name, type, authority_score FROM sources ORDER BY authority_score DESC")
    for row in cursor.fetchall():
        icon = "★" if row['type'] == 'original' else "☆"
        print(f"  {icon} {row['name']} ({row['authority_score']}分)")
    
    # 3. 算法规范
    print("\n【算法规范】")
    cursor = conn.execute("SELECT rule_id, spec_name FROM algorithm_specs")
    for row in cursor.fetchall():
        print(f"  {row['rule_id']} → {row['spec_name']}")
    
    # 4. 八卦表
    print("\n【八卦速查】")
    cursor = conn.execute("SELECT num, gua_name, gua_symbol, note FROM hexagram_table ORDER BY num")
    for row in cursor.fetchall():
        print(f"  {row['num']} {row['gua_symbol']} {row['gua_name']} - {row['note']}")
    
    # 5. 关键发现
    print("\n【关键发现】")
    cursor = conn.execute("SELECT finding_text FROM key_findings")
    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"  {i}. {row['finding_text'][:50]}...")
    
    # 6. 验证矩阵
    print("\n【交叉验证状态】")
    cursor = conn.execute("SELECT rule_id, cross_validation_result FROM verification_matrix")
    for row in cursor.fetchall():
        print(f"  {row['rule_id']}: {row['cross_validation_result']}")
    
    conn.close()

def query_rule(rule_id):
    """查询单条规则详情"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # 规则基本信息
    cursor = conn.execute("SELECT * FROM rules WHERE rule_id = ?", (rule_id,))
    rule = cursor.fetchone()
    if not rule:
        print(f"未找到规则: {rule_id}")
        return
    
    print(f"\n{'='*60}")
    print(f"规则: {rule['rule_id']} - {rule['rule_name']}")
    print(f"{'='*60}")
    print(f"描述: {rule['description']}")
    print(f"核心算法: {rule['core_algorithm']}")
    print(f"实现类型: {rule['implementation_type']}")
    print(f"验证状态: {rule['verification_status']}")
    print(f"证据评级: {rule['evidence_rating']}")
    
    # 算法规范
    cursor = conn.execute("SELECT spec_name, spec_content FROM algorithm_specs WHERE rule_id = ?", (rule_id,))
    specs = cursor.fetchall()
    if specs:
        print(f"\n【算法规范】")
        for s in specs:
            print(f"  {s['spec_name']}: {s['spec_content'][:100]}...")
    
    # 验证信息
    cursor = conn.execute("SELECT * FROM verification_matrix WHERE rule_id = ?", (rule_id,))
    v = cursor.fetchone()
    if v:
        print(f"\n【交叉验证】")
        print(f"  源1: {v['source_1']}")
        print(f"  源2: {v['source_2']}")
        print(f"  源3: {v['source_3']}")
        print(f"  结果: {v['cross_validation_result']}")
    
    conn.close()

def export_json():
    """导出为JSON格式"""
    import json
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    data = {
        'meta': {
            'generated_at': '2026-09-04',
            'total_rules': 14,
            'verified': 13,
            'completed': 1
        },
        'rules': [],
        'sources': [],
        'findings': []
    }
    
    # 规则
    cursor = conn.execute("SELECT * FROM rules ORDER BY rule_id")
    for row in cursor.fetchall():
        data['rules'].append(dict(row))
    
    # 来源
    cursor = conn.execute("SELECT * FROM sources ORDER BY authority_score DESC")
    for row in cursor.fetchall():
        data['sources'].append(dict(row))
    
    # 关键发现
    cursor = conn.execute("SELECT finding_text FROM key_findings")
    for row in cursor.fetchall():
        data['findings'].append(row['finding_text'])
    
    conn.close()
    
    output_path = Path.home() / "wisdom" / "heluo_rule_evidence.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 已导出JSON: {output_path}")
    return output_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "query":
            query_rule(sys.argv[2] if len(sys.argv) > 2 else "rule_01")
        elif sys.argv[1] == "export":
            export_json()
        else:
            print(f"未知命令: {sys.argv[1]}")
    else:
        query_all()
