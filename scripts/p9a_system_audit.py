# -*- coding: utf-8 -*-
"""Phase 9A: 系统架构审核脚本（修复编码）"""
import sys
sys.path.insert(0, 'src')

import psycopg2
import os
import json

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'shuntian_kb',
    'user': 'tongshu',
    'password': os.environ.get('TONGSHU_DB_PASSWORD', 'tongshu_secret')
}

print("=== Phase 9A 系统架构审核 ===\n")

results = {}

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # 1. 表结构
    print("【表结构统计】")
    cur.execute("""
        SELECT table_name, 
               (SELECT COUNT(*) FROM information_schema.columns c 
                WHERE c.table_schema='public' AND c.table_name=t.table_name) as col_count
        FROM information_schema.tables t
        WHERE table_schema='public'
        ORDER BY table_name
    """)
    tables = cur.fetchall()
    results['table_count'] = len(tables)
    print(f"总表数: {len(tables)}")
    
    for name, cols in tables:
        cur.execute(f'SELECT COUNT(*) FROM "{name}"')
        count = cur.fetchone()[0]
        print(f"  {name:45s} {cols:>3d}列 {count:>8,d}行")
    
    # 2. 行数汇总
    total_rows = sum(r[1] for r in tables)
    results['total_rows'] = total_rows
    print(f"\n总行数: {total_rows:,d}")
    
    # 3. 外键检查
    print("\n【外键约束】")
    cur.execute("""
        SELECT tc.table_name, kcu.column_name, 
               ccu.table_name AS foreign_table, ccu.column_name AS foreign_column
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
    """)
    fks = cur.fetchall()
    results['foreign_keys'] = len(fks)
    if fks:
        for fk in fks[:10]:
            print(f"  {fk[0]}.{fk[1]} -> {fk[2]}.{fk[3]}")
        if len(fks) > 10:
            print(f"  ... 还有 {len(fks)-10} 个外键")
    else:
        print("  无显式外键（应用层管理）")
    
    # 4. 有version字段的表
    print("\n【Version字段】")
    cur.execute("""
        SELECT DISTINCT table_name 
        FROM information_schema.columns 
        WHERE table_schema='public' AND column_name LIKE '%version%'
        ORDER BY table_name
    """)
    version_tables = cur.fetchall()
    results['version_fields'] = [r[0] for r in version_tables]
    for vt in version_tables:
        print(f"  {vt[0]}")
    
    # 5. 主键检查
    print("\n【主键检查】")
    cur.execute("""
        SELECT tc.table_name, kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_schema = 'public'
        ORDER BY tc.table_name
    """)
    pks = cur.fetchall()
    results['primary_keys'] = len(pks)
    missing_pk = []
    for name, _ in tables:
        if not any(r[0] == name for r in pks):
            missing_pk.append(name)
    if missing_pk:
        print(f"  ⚠ 无主键的表: {missing_pk}")
    else:
        print("  ✓ 所有表都有主键")
    
    conn.close()
    print("\n✅ 数据库审核完成")
    
except Exception as e:
    print(f"❌ 数据库连接失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 输出JSON结果供后续使用
print("\n=== AUDIT_RESULTS ===")
print(json.dumps(results, ensure_ascii=False, indent=2))
