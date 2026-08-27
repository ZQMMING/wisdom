"""Phase 2 完整收尾：验证 + 总结"""
import sys
sys.path.insert(0, 'backend/src')
from tongshu.db.config import get_dsn
import psycopg2
import json

dsn = get_dsn().replace('/otcg', '/shuntian_kb')

def run():
    co = psycopg2.connect(dsn)
    co.autocommit = True
    cr = co.cursor()
    
    print("=== Phase 2 验证 ===\n")
    
    # 1. 新表统计
    tables_stats = [
        ('life_domains', '领域域'),
        ('semantic_concepts', '语义概念'),
        ('modern_expressions', '现代表达'),
        ('tone_lexicon', '语气标签'),
        ('forbidden_terms', '禁用词'),
        ('risk_terms', '风险模式'),
        ('templates', '模板'),
        ('template_versions', '模板版本'),
        ('semantic_mappings', '语义映射（扩展）'),
    ]
    
    print("【表统计】")
    for table, desc in tables_stats:
        try:
            cr.execute(f"SELECT COUNT(*) FROM {table}")
            count = cr.fetchone()[0]
            print(f"  {table} ({desc}): {count} 条")
        except Exception as e:
            print(f"  {table}: 错误 - {e}")
    
    # 2. semantic_mappings 扩展字段填充率
    print("\n【semantic_mappings 扩展字段填充率】")
    cr.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(concept_id) as has_concept,
            COUNT(tone) as has_tone,
            COUNT(expression_refs) as has_expression,
            COUNT(evidence_id) as has_evidence
        FROM semantic_mappings
    """)
    row = cr.fetchone()
    total, has_concept, has_tone, has_expression, has_evidence = row
    print(f"  total: {total}")
    print(f"  concept_id: {has_concept}/{total} ({has_concept*100//total}%)")
    print(f"  tone: {has_tone}/{total} ({has_tone*100//total}%)")
    print(f"  expression_refs: {has_expression}/{total} ({has_expression*100//total}%)")
    print(f"  evidence_id: {has_evidence}/{total} ({has_evidence*100//total}%)")
    
    # 3. G3 模式数量
    print("\n【G3 安全门模式】")
    cr.execute("SELECT COUNT(*) FROM forbidden_terms WHERE status='ACTIVE'")
    g3_count = cr.fetchone()[0]
    print(f"  forbidden_terms (ACTIVE): {g3_count} 条")
    
    # 4. 迁移版本
    print("\n【迁移版本】")
    cr.execute("SELECT version, applied_at FROM migration_versions ORDER BY applied_at DESC LIMIT 5")
    for row in cr.fetchall():
        print(f"  {row[0]} @ {row[1]}")
    
    # 5. family/environment/communication 新增领域
    print("\n【新增语境码验证】")
    cr.execute("""
        SELECT domain_id, domain_name_cn 
        FROM life_domains 
        WHERE domain_id IN ('family', 'environment', 'communication')
    """)
    for row in cr.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    # 6. G3 模式样例（前5条）
    print("\n【G3 模式样例（前5条）】")
    cr.execute("""
        SELECT term_id, category, LEFT(term_pattern, 30) as pattern_preview
        FROM forbidden_terms 
        WHERE status='ACTIVE'
        ORDER BY category, term_id
        LIMIT 5
    """)
    for row in cr.fetchall():
        print(f"  {row[0]}: [{row[1]}] {row[2]}...")
    
    print("\n✓ Phase 2 验证完成")
    co.close()

run()
