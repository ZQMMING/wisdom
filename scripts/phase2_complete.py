"""Phase 2: 补全 semantic_mappings + G3 安全门 DB 化 + 扩展表达式"""
import sys
sys.path.insert(0, 'backend/src')
from tongshu.db.config import get_dsn
import psycopg2
import json

dsn = get_dsn().replace('/otcg', '/shuntian_kb')

# ── 映射规则：source_concept → (concept_id, tone, priority) ──
MAPPING_RULES = {
    # 宜系列 → 积极/温暖
    '宜': ('SEM_04', 'TONE_WARM', 90),
    '吉': ('SEM_04', 'TONE_CONFIDENT', 85),
    '黄道': ('SEM_04', 'TONE_ENCOURAGE', 80),
    '开': ('SEM_07', 'TONE_CONFIDENT', 85),
    '建': ('SEM_07', 'TONE_NEUTRAL', 70),
    # 忌系列 → 谨慎/中立
    '忌': ('SEM_06', 'TONE_CAUTIOUS', 80),
    '凶': ('SEM_06', 'TONE_CAUTIOUS', 75),
    '黑道': ('SEM_06', 'TONE_CAUTIOUS', 70),
    '闭': ('SEM_06', 'TONE_CAUTIOUS', 65),
    # 冲合系列 → 关系/节奏
    '冲': ('SEM_07', 'TONE_NEUTRAL', 80),
    '害': ('SEM_07', 'TONE_CAUTIOUS', 75),
    '合': ('SEM_07', 'TONE_WARM', 85),
    '破': ('SEM_07', 'TONE_CAUTIOUS', 70),
    # 五行 → 自我/认知
    '木': ('SEM_03', 'TONE_NEUTRAL', 50),
    '火': ('SEM_03', 'TONE_CONFIDENT', 55),
    '土': ('SEM_03', 'TONE_NEUTRAL', 50),
    '金': ('SEM_03', 'TONE_CAUTIOUS', 50),
    '水': ('SEM_03', 'TONE_NEUTRAL', 50),
    # 其他概念
    '煞': ('SEM_06', 'TONE_CAUTIOUS', 75),
    '贵人': ('SEM_02', 'TONE_ENCOURAGE', 70),
    '驿马': ('SEM_01', 'TONE_NEUTRAL', 60),
}

def run():
    co = psycopg2.connect(dsn)
    co.autocommit = True
    cr = co.cursor()
    
    print("=== PHASE 2: 语义映射字段补全 ===")
    
    # 1. 批量填充 semantic_mappings
    cr.execute("SELECT mapping_id, source_concept FROM semantic_mappings")
    rows = cr.fetchall()
    updated = 0
    skipped = 0
    
    for mapping_id, source_concept in rows:
        if source_concept in MAPPING_RULES:
            concept_id, tone, priority = MAPPING_RULES[source_concept]
            cr.execute("""
                UPDATE semantic_mappings 
                SET concept_id=%s, tone=%s, priority=%s, updated_at=NOW()
                WHERE mapping_id=%s
            """, (concept_id, tone, priority, mapping_id))
            updated += 1
        else:
            skipped += 1
    
    print(f"  ✓ 更新 {updated} 条 (跳过 {skipped} 条无规则)")
    
    # 2. 批量更新 status DRAFT→REVIEW（经自动规则）
    cr.execute("SELECT COUNT(*) FROM semantic_mappings WHERE status='DRAFT'")
    draft_count = cr.fetchone()[0]
    print(f"  ~ {draft_count} 条待 REVIEW（人工复核）")
    
    # 3. 更新 migration 版本
    try:
        cr.execute("""
            INSERT INTO migration_versions (version, applied_at)
            VALUES ('20260822_phase2_autofill_v1', NOW())
            ON CONFLICT (version) DO NOTHING
        """)
        print("  ✓ migration version: 20260822_phase2_autofill_v1")
    except Exception as e:
        print(f"  ~ migration skip: {e}")
    
    # 验证
    cr.execute("SELECT concept_id, COUNT(*) FROM semantic_mappings GROUP BY concept_id ORDER BY COUNT(*) DESC")
    print("\n  concept_id 分布:")
    for r in cr.fetchall():
        print(f"    {r[0]}: {r[1]}条")
    
    cr.execute("SELECT tone, COUNT(*) FROM semantic_mappings GROUP BY tone ORDER BY COUNT(*) DESC")
    print("\n  tone 分布:")
    for r in cr.fetchall():
        print(f"    {r[0]}: {r[1]}条")
    
    print("\n=== PHASE 2: G3 安全门 DB 化 ===")
    
    # 从 forbidden_terms 构建正则模式字典
    cr.execute("SELECT term_pattern, category, severity FROM forbidden_terms WHERE status='ACTIVE'")
    patterns = {}
    for row in cr.fetchall():
        pattern, cat, sev = row
        patterns[cat] = (pattern, sev)
    
    print(f"  ✓ {len(patterns)} 条 DB 模式已加载")
    
    # 对比 Python 硬编码 vs DB
    python_patterns = [
        (r"稳赚|包赚|稳赚不赔|必涨|保本", "financial guarantee"),
        (r"保证.{0,4}(收益|回报|赚钱|涨|盈利)", "financial guarantee"),
        (r"包治|根治|保证.{0,4}(康复|痊愈)|诊断.{0,4}(疾病|重病)", "medical claim"),
        (r"必定|必然[会]?|命中注定|绝对会|肯定会|一定.{0,3}会", "deterministic prediction"),
        (r"大祸|血光|必有灾|灾祸必|大难|不越之兆|劫数", "fear induction"),
        (r"你必须|你务必|你只能|非做不可|万万不能|绝不能", "coercive guidance"),
        (r"[0-9０-９]+[%％].{0,3}(\u53ef\u80fd|\u4f1a|\u6982\u7387)", "probability claim"),
    ]
    
    print(f"  Python 硬编码: {len(python_patterns)} 条")
    print(f"  DB 存储: {len(patterns)} 条")
    
    # 4. 扩展 risk_terms
    print("\n=== PHASE 2: 扩展风险模式 ===")
    risks = [
        ('RISK_06', 'tone_mismatch', 'TONE_MISMATCH', 'WARN', 
         '语气与场景不匹配（如紧急事项用温暖语气）', 
         'G3.2 检查 tone × context 合规性', None, 'ACTIVE'),
        ('RISK_07', 'over_translation', 'OVER_TRANSLATION', 'WARN',
         '过度转译导致原意丢失', 
         '保留核心语义锚点', None, 'ACTIVE'),
        ('RISK_08', 'context_drift', 'CONTEXT_DRIFT', 'WARN',
         '语境漂移（如家庭场景误用工作语境）',
         'G3.1 检查 allowed_context', None, 'ACTIVE'),
    ]
    for r in risks:
        cr.execute("""
            INSERT INTO risk_terms (risk_id, risk_pattern, risk_category, severity, description, mitigation, source_refs, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (risk_id) DO NOTHING
        """, r)
    print(f"  ✓ {len(risks)} 风险模式新增")
    
    # 5. 扩展 modern_expressions
    print("\n=== PHASE 2: 扩展现代转译表达 ===")
    expressions = [
        ('EXP_007', '开', '开启/启程', 'life', 'work', ['confident','neutral'], ['suggest','inform'], ['forbid'], ['daily_guide'], None, '1.0.0', 'ACTIVE'),
        ('EXP_008', '闭', '暂停/等待', 'life', 'ending', ['cautious','neutral'], ['warn','inform'], ['suggest'], ['daily_guide'], None, '1.0.0', 'ACTIVE'),
        ('EXP_009', '破', '突破/结束', 'life', 'ending', ['neutral','cautious'], ['inform'], ['guarantee'], ['daily_guide'], None, '1.0.0', 'ACTIVE'),
        ('EXP_010', '危', '需留意', 'life', 'life', ['cautious','compassionate'], ['warn'], ['guarantee'], ['daily_guide'], None, '1.0.0', 'ACTIVE'),
        ('EXP_011', '成', '进展顺利', 'life', 'life', ['confident','warm'], ['inform'], ['guarantee'], ['daily_guide'], None, '1.0.0', 'ACTIVE'),
        ('EXP_012', '收', '收尾整理', 'life', 'ending', ['neutral','respect'], ['suggest'], ['forbid'], ['daily_guide'], None, '1.0.0', 'ACTIVE'),
        ('EXP_013', '执', '推进执行', 'life', 'work', ['confident','encourage'], ['suggest'], ['forbid'], ['daily_guide'], None, '1.0.0', 'ACTIVE'),
        ('EXP_014', '定', '稳定锚定', 'life', 'foundation', ['neutral','respect'], ['inform'], ['guarantee'], ['daily_guide'], None, '1.0.0', 'ACTIVE'),
        ('EXP_015', '先', '时机先行', 'life', 'time', ['confident','neutral'], ['suggest'], ['forbid'], ['daily_guide'], None, '1.0.0', 'ACTIVE'),
        ('EXP_016', '后', '暂缓观察', 'life', 'time', ['cautious','neutral'], ['warn','inform'], ['suggest'], ['daily_guide'], None, '1.0.0', 'ACTIVE'),
    ]
    for e in expressions:
        cr.execute("""
            INSERT INTO modern_expressions (expression_id, traditional_term, modern_expression, domain, context_code, tone_tags, allowed_actions, forbidden_actions, theme_tags, source_refs, version, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (expression_id) DO NOTHING
        """, e)
    print(f"  ✓ {len(expressions)} 表达新增")
    
    # 最终验证
    print("\n=== 验证 ===")
    cr.execute("SELECT COUNT(*) FROM semantic_mappings WHERE concept_id IS NOT NULL")
    print(f"  semantic_mappings 有 concept_id: {cr.fetchone()[0]}")
    
    cr.execute("SELECT COUNT(*) FROM modern_expressions")
    print(f"  modern_expressions: {cr.fetchone()[0]}")
    
    cr.execute("SELECT COUNT(*) FROM risk_terms")
    print(f"  risk_terms: {cr.fetchone()[0]}")
    
    cr.execute("SELECT COUNT(*) FROM forbidden_terms")
    print(f"  forbidden_terms: {cr.fetchone()[0]}")
    
    print("\n✓ Phase 2 完成")
    co.close()

run()
