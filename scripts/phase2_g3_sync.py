"""Phase 2: G3 安全门 DB 化 - 统一中英文模式"""
import sys
sys.path.insert(0, 'backend/src')
from tongshu.db.config import get_dsn
import psycopg2

dsn = get_dsn().replace('/otcg', '/shuntian_kb')

def run():
    co = psycopg2.connect(dsn)
    co.autocommit = True
    cr = co.cursor()
    
    print("=== G3 安全门对齐 ===")
    
    # 从 g3_safety.py 提取的官方模式（权威源）
    official_patterns = [
        # 财务保证类
        ('FORB_FIN_01', r'稳赚|包赚|稳赚不赔|必涨|保本', 'FINANCIAL_GUARANTEE', 'BLOCK', '财务保证类禁用词-短语', None),
        ('FORB_FIN_02', r'保证.{0,4}(收益|回报|赚钱|涨|盈利)', 'FINANCIAL_GUARANTEE', 'BLOCK', '财务保证类禁用词-保证收益', None),
        ('FORB_FIN_03', r'建议买入|肯定赚钱|明天会跌|保证收益', 'FINANCIAL_GUARANTEE', 'BLOCK', '财务保证类禁用词-固定词组', None),
        # 医疗声称类
        ('FORB_MED_01', r'包治|根治|保证.{0,4}(康复|痊愈)|诊断.{0,4}(疾病|重病)', 'MEDICAL_CLAIM', 'BLOCK', '医疗承诺类禁用词', None),
        # 确定性预测类
        ('FORB_DET_01', r'必定|必然[会]?|命中注定|绝对会|肯定会|一定.{0,3}会', 'DETERMINISTIC_PREDICTION', 'BLOCK', '确定性预测禁用词', None),
        # 恐惧诱导类
        ('FORB_FEAR_01', r'大祸|血光|必有灾|灾祸必|大难|不越之兆|劫数', 'FEAR_INDUCTION', 'BLOCK', '恐惧诱导禁用词', None),
        # 强制引导类
        ('FORB_COER_01', r'你必须|你务必|你只能|非做不可|万万不能|绝不能', 'COERCIVE_GUIDANCE', 'BLOCK', '强制性引导禁用词', None),
        # 概率声称类
        ('FORB_PROB_01', r'[0-9０-９]+[%％].{0,3}(可能|会|概率)', 'PROBABILITY_CLAIM', 'BLOCK', '概率声称禁用词', None),
    ]
    
    # 清空并重建
    cr.execute("DELETE FROM forbidden_terms")
    print("  ✓ 清空旧数据")
    
    for p in official_patterns:
        cr.execute("""
            INSERT INTO forbidden_terms (term_id, term_pattern, pattern_type, category, severity, description, source_refs, status)
            VALUES (%s, %s, 'REGEX', %s, %s, %s, %s, 'ACTIVE')
        """, p)
    
    print(f"  ✓ 插入 {len(official_patterns)} 条官方模式")
    
    # 添加英文兜底（DBA 双语）
    english_fallbacks = [
        ('ENG_FIN_01', r'must.*rise|guaranteed.*profit|steady.*gain', 'FINANCIAL_GUARANTEE', 'WARN', '英文财务保证兜底', None),
        ('ENG_MED_01', r'cure.*guarantee|radical.*cure', 'MEDICAL_CLAIM', 'WARN', '英文医疗兜底', None),
        ('ENG_DET_01', r'definitely|inevitably|certainly.*(will|would)', 'DETERMINISTIC_PREDICTION', 'WARN', '英文确定性兜底', None),
        ('ENG_FEAR_01', r'calamity|blood.*disaster|doom|misfortune', 'FEAR_INDUCTION', 'WARN', '英文恐惧兜底', None),
    ]
    
    for p in english_fallbacks:
        cr.execute("""
            INSERT INTO forbidden_terms (term_id, term_pattern, pattern_type, category, severity, description, source_refs, status)
            VALUES (%s, %s, 'REGEX', %s, %s, %s, %s, 'ACTIVE')
        """, p)
    
    print(f"  ✓ 新增 {len(english_fallbacks)} 条英文兜底")
    
    # 更新 migration 版本
    cr.execute("""
        INSERT INTO migration_versions (version, applied_at)
        VALUES ('20260822_phase2_g3_sync_v1', NOW())
        ON CONFLICT (version) DO NOTHING
    """)
    print("  ✓ migration version: 20260822_phase2_g3_sync_v1")
    
    # 验证
    cr.execute("SELECT COUNT(*) FROM forbidden_terms WHERE status='ACTIVE'")
    count = cr.fetchone()[0]
    print(f"\n  ✓ 总数: {count} 条")
    
    cr.execute("SELECT pattern_type, COUNT(*) FROM forbidden_terms GROUP BY pattern_type")
    print("  按类型分布:")
    for r in cr.fetchall():
        print(f"    {r[0]}: {r[1]}条")
    
    print("\n✓ G3 对齐完成")
    co.close()

run()
