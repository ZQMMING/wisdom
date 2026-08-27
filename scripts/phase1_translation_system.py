"""Phase 1: Modern Interpretation Mapping System - DDL + Data Import"""
import sys
sys.path.insert(0, 'backend/src')
from tongshu.db.config import get_dsn
import psycopg2
import json

dsn = get_dsn().replace('/otcg', '/shuntian_kb')

def run():
    with psycopg2.connect(dsn) as co:
        co.autocommit = True
        cr = co.cursor()

        # ── 1. 7 NEW TABLES ──────────────────────────────────────────
        print("=== CREATING 7 NEW TABLES ===")

        cr.execute("""
        CREATE TABLE IF NOT EXISTS life_domains (
            domain_id TEXT PRIMARY KEY,
            domain_code TEXT NOT NULL UNIQUE,
            domain_name_cn TEXT NOT NULL,
            definition TEXT,
            priority INTEGER DEFAULT 50,
            allowed_context_codes TEXT[] DEFAULT '{}',
            forbidden_context_codes TEXT[] DEFAULT '{}',
            status TEXT DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','DEPRECATED','DRAFT')),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """)
        print("  ✓ life_domains")

        cr.execute("""
        CREATE TABLE IF NOT EXISTS semantic_concepts (
            concept_id TEXT PRIMARY KEY,
            concept_name TEXT NOT NULL,
            definition TEXT,
            domain TEXT REFERENCES life_domains(domain_id) ON DELETE SET NULL,
            related_traditional_terms TEXT[] DEFAULT '{}',
            source_refs JSONB,
            evidence_id TEXT REFERENCES evidence(evidence_id),
            status TEXT DEFAULT 'DRAFT' CHECK (status IN ('DRAFT','REVIEW','VALIDATED','ACTIVE','DEPRECATED')),
            notes TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """)
        print("  ✓ semantic_concepts")

        cr.execute("""
        CREATE TABLE IF NOT EXISTS modern_expressions (
            expression_id TEXT PRIMARY KEY,
            traditional_term TEXT NOT NULL,
            modern_expression TEXT NOT NULL,
            domain TEXT REFERENCES life_domains(domain_id) ON DELETE SET NULL,
            context_code TEXT REFERENCES life_domains(domain_id) ON DELETE SET NULL,
            tone_tags TEXT[] DEFAULT '{}',
            allowed_actions TEXT[] DEFAULT '{}',
            forbidden_actions TEXT[] DEFAULT '{}',
            theme_tags TEXT[] DEFAULT '{}',
            source_refs JSONB,
            evidence_id TEXT REFERENCES evidence(evidence_id),
            version TEXT DEFAULT '1.0.0',
            status TEXT DEFAULT 'DRAFT' CHECK (status IN ('DRAFT','REVIEW','VALIDATED','ACTIVE','DEPRECATED')),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """)
        print("  ✓ modern_expressions")

        cr.execute("""
        CREATE TABLE IF NOT EXISTS tone_lexicon (
            tone_id TEXT PRIMARY KEY,
            tone_code TEXT NOT NULL UNIQUE,
            tone_name_cn TEXT NOT NULL,
            description TEXT,
            usage_context TEXT[] DEFAULT '{}',
            examples TEXT[] DEFAULT '{}',
            status TEXT DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','DEPRECATED','DRAFT')),
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """)
        print("  ✓ tone_lexicon")

        cr.execute("""
        CREATE TABLE IF NOT EXISTS forbidden_terms (
            term_id TEXT PRIMARY KEY,
            term_pattern TEXT NOT NULL UNIQUE,
            pattern_type TEXT NOT NULL CHECK (pattern_type IN ('WORD','PHRASE','REGEX','PATTERN')),
            category TEXT NOT NULL CHECK (category IN ('FINANCIAL_GUARANTEE','MEDICAL_CLAIM','DETERMINISTIC_PREDICTION','FEAR_INDUCTION','COERCIVE_GUIDANCE','PROBABILITY_CLAIM','AI_HALLUCINATION','CERTAINTY_ESCALATION')),
            severity TEXT NOT NULL DEFAULT 'BLOCK' CHECK (severity IN ('BLOCK','WARN','INFO')),
            description TEXT,
            source_refs JSONB,
            status TEXT DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','DEPRECATED')),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """)
        print("  ✓ forbidden_terms")

        cr.execute("""
        CREATE TABLE IF NOT EXISTS risk_terms (
            risk_id TEXT PRIMARY KEY,
            risk_pattern TEXT NOT NULL UNIQUE,
            risk_category TEXT NOT NULL,
            severity TEXT DEFAULT 'WARN' CHECK (severity IN ('BLOCK','WARN','INFO')),
            description TEXT,
            mitigation TEXT,
            source_refs JSONB,
            status TEXT DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','DEPRECATED')),
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """)
        print("  ✓ risk_terms")

        cr.execute("""
        CREATE TABLE IF NOT EXISTS templates (
            template_id TEXT PRIMARY KEY,
            template_name TEXT NOT NULL,
            template_type TEXT NOT NULL CHECK (template_type IN ('OUTPUT','REVIEW','AUDIT','CONTENT')),
            domain TEXT REFERENCES life_domains(domain_id) ON DELETE SET NULL,
            tone_id TEXT REFERENCES tone_lexicon(tone_id) ON DELETE SET NULL,
            context_code TEXT,
            structure JSONB NOT NULL,
            examples JSONB DEFAULT '[]',
            source_refs JSONB,
            version TEXT DEFAULT '1.0.0',
            status TEXT DEFAULT 'DRAFT' CHECK (status IN ('DRAFT','REVIEW','VALIDATED','ACTIVE','DEPRECATED')),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """)
        print("  ✓ templates")

        cr.execute("""
        CREATE TABLE IF NOT EXISTS template_versions (
            version_id TEXT PRIMARY KEY,
            template_id TEXT NOT NULL REFERENCES templates(template_id) ON DELETE CASCADE,
            version TEXT NOT NULL,
            changes TEXT,
            changelog JSONB,
            status TEXT DEFAULT 'CURRENT' CHECK (status IN ('CURRENT','SUPERSEDED','ARCHIVED')),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(template_id, version)
        );
        """)
        print("  ✓ template_versions")

        # ── 2. EXTEND semantic_mappings with new columns ─────────────
        print("\n=== EXTENDING semantic_mappings ===")
        for col, ctype in [
            ('concept_id', 'TEXT REFERENCES semantic_concepts(concept_id)'),
            ('expression_refs', 'JSONB'),
            ('tone', 'TEXT REFERENCES tone_lexicon(tone_id)'),
            ('priority', 'INTEGER DEFAULT 50'),
            ('evidence_id', 'TEXT REFERENCES evidence(evidence_id)'),
            ('rule_id', 'TEXT'),
        ]:
            try:
                cr.execute(f"ALTER TABLE semantic_mappings ADD COLUMN {col} {ctype}")
                print(f"  ✓ {col}")
            except Exception as e:
                if 'already exists' in str(e).lower():
                    print(f"  ~ {col} (exists)")
                else:
                    raise

        # ── 3. INSERT life_domains ───────────────────────────────────
        print("\n=== INSERTING life_domains ===")
        domains = [
            ('life', 'LIFE', '生活', '日常生活综合场景', 10, ['DAILY','LIFE']),
            ('work', 'WORK', '工作', '工作事务与职业发展', 20, ['WORK','CRITICAL_WORK','EXECUTION']),
            ('health', 'HEALTH', '健康', '身体健康与养生', 30, ['HEALTH','SELF']),
            ('finance', 'FINANCE', '财务', '财务收支与投资', 40, ['FINANCE','FINANCE_MAJOR','INVESTMENT']),
            ('relationship', 'RELATIONSHIP', '关系', '人际关系与社交', 50, ['RELATIONSHIP','SOCIAL','TEAM']),
            ('social', 'SOCIAL', '社交', '社交往来活动', 55, ['SOCIAL','COMMUNICATION']),
            ('self', 'SELF', '自我关照', '自我成长与内心关照', 60, ['SELF','INTERNAL','GROWTH']),
            ('learning', 'LEARNING', '学习成长', '学习与发展', 65, ['LEARNING','GROWTH']),
            ('family', 'FAMILY', '家庭', '家庭成员关系与家庭事务', 70, ['DAILY','LIFE','RELATIONSHIP']),
            ('environment', 'ENVIRONMENT', '环境', '居住环境与周围环境', 75, ['DAILY','LIFE','HOME']),
            ('communication', 'COMMUNICATION', '沟通', '人际沟通与表达', 80, ['DAILY','SOCIAL','RELATIONSHIP']),
            ('digital_life', 'DIGITAL_LIFE', '数字生活', '数字与线上生活', 90, ['DIGITAL_LIFE']),
            ('internal', 'INTERNAL', '内心', '内在独处与精神世界', 95, ['INTERNAL','SELF']),
            ('creativity', 'CREATIVE', '创意创造', '创意表达与创作', 100, ['CREATIVE','INNOVATION']),
            ('decision', 'DECISION', '决策判断', '决策与判断事项', 105, ['DECISION','DECISION_MAJOR','CRITICAL_DECISION']),
            ('execution', 'EXECUTION', '执行推进', '任务执行与推进', 110, ['EXECUTION','CRITICAL_WORK']),
            ('growth', 'GROWTH', '成长发展', '个人成长与发展', 115, ['GROWTH','LEARNING']),
            ('travel', 'TRAVEL', '出行', '出行与搬迁移动', 120, ['TRAVEL','RELOCATION']),
            ('rest', 'REST', '休息恢复', '休息与恢复', 125, ['REST','LIFE']),
            ('challenge', 'CHALLENGE', '挑战攻坚', '挑战与攻坚事项', 130, ['CHALLENGE','CRITICAL_WORK']),
            ('adventure', 'ADVENTURE', '探索冒险', '探索与冒险', 135, ['ADVENTURE','EXPANSION']),
            ('expansion', 'EXPANSION', '扩张拓展', '扩张与拓展', 140, ['EXPANSION','ADVENTURE']),
            ('foundation', 'FOUNDATION', '基础建设', '基础建设与筹备', 145, ['FOUNDATION','PLANNING','STARTING']),
            ('ending', 'ENDING', '收尾结束', '收尾与结束', 150, ['ENDING','SETTLEMENT']),
            ('settlement', 'SETTLEMENT', '结算交割', '结算与交割', 155, ['SETTLEMENT','FINANCE']),
            ('perception', 'PERCEPTION', '感知直觉', '感知与直觉判断', 160, ['PERCEPTION','INTERNAL']),
            ('innovation', 'INNOVATION', '创新', '创新与突破', 165, ['INNOVATION','CREATIVE']),
            ('team', 'TEAM', '团队协作', '团队协作', 170, ['TEAM','WORK','SOCIAL']),
            ('adaptation', 'ADAPTATION', '适应变化', '适应变化与状态切换', 175, ['ADAPTATION','CHANGE']),
            ('emergency', 'EMERGENCY', '应急突发', '应急与突发事项', 180, ['EMERGENCY','RISK']),
            ('general', 'GENERAL', '通用', '无特定场景限制', 200, ['GENERAL']),
            ('time', 'TIME', '时间节律', '时间节律与周期', 210, ['TIME']),
            ('home', 'HOME', '家居内务', '家居内务管理', 220, ['HOME','DAILY','LIFE']),
        ]
        for d in domains:
            cr.execute("""
                INSERT INTO life_domains (domain_id, domain_code, domain_name_cn, definition, priority, allowed_context_codes, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVE')
                ON CONFLICT (domain_id) DO UPDATE SET
                    domain_code=EXCLUDED.domain_code,
                    domain_name_cn=EXCLUDED.domain_name_cn,
                    definition=EXCLUDED.definition,
                    priority=EXCLUDED.priority,
                    allowed_context_codes=EXCLUDED.allowed_context_codes,
                    updated_at=NOW()
            """, (d[0], d[1], d[2], d[3], d[4], d[5]))
        print(f"  ✓ {len(domains)} domains inserted")

        # ── 4. INSERT semantic_concepts (SEM_* from spec) ───────────
        print("\n=== INSERTING semantic_concepts ===")
        concepts = [
            ('SEM_01', '生活智慧', '从传统术语转译为现代产品语言的智慧应用', 'life', ['traditional_terms'], None, 'ACTIVE', None),
            ('SEM_02', '情绪价值', '产品提供被理解感与被关照感的核心价值', 'self', ['traditional_terms'], None, 'ACTIVE', None),
            ('SEM_03', '文化底气', '传统文化作为现代人精神支撑的确定性来源', 'learning', ['traditional_terms'], None, 'ACTIVE', None),
            ('SEM_04', '确定性陪伴', '黄历通书作为日常确定性指引的产品定位', 'life', ['traditional_terms'], None, 'ACTIVE', None),
            ('SEM_05', '双向选择', '传统宜忌与现代产品选择的双向匹配', 'decision', ['traditional_terms'], None, 'ACTIVE', None),
            ('SEM_06', '风险缓冲', '通过传统智慧降低决策风险的心理缓冲', None, ['traditional_terms'], None, 'ACTIVE', None),
            ('SEM_07', '节奏匹配', '个人八字节奏与时间节律的匹配', 'relationship', ['traditional_terms'], None, 'ACTIVE', None),
            ('SEM_08', '语境适配', '不同语境下的现代转译适配策略', 'communication', ['traditional_terms'], None, 'ACTIVE', None),
            ('SEM_09', '安全护栏', '禁用词与风险词的自动防护机制', None, ['traditional_terms'], None, 'ACTIVE', None),
            ('SEM_10', '证据链追溯', '每条转译都有可追溯的经典依据', None, ['traditional_terms'], None, 'ACTIVE', None),
        ]
        for c in concepts:
            cr.execute("""
                INSERT INTO semantic_concepts (concept_id, concept_name, definition, domain, related_traditional_terms, source_refs, status, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (concept_id) DO NOTHING
            """, c)
        print(f"  ✓ {len(concepts)} concepts inserted")

        # ── 5. INSERT tone_lexicon ───────────────────────────────────
        print("\n=== INSERTING tone_lexicon ===")
        tones = [
            ('TONE_WARM', 'TONE_WARM', '温暖陪伴', '温和、亲切、不带压力的表达', ['DAILY','LIFE','SELF'], ['今天的能量很温柔', '适合慢慢来'], 'ACTIVE'),
            ('TONE_RESPECT', 'TONE_RESPECT', '尊重自主', '尊重用户选择权，不强制', ['DECISION','SELF','RELATIONSHIP'], ['你可以参考', '选择权在你'], 'ACTIVE'),
            ('TONE_CONFIDENT', 'TONE_CONFIDENT', '坚定自信', '明确但不傲慢的表达', ['EXECUTION','CHALLENGE'], ['这是好时机', '建议把握'], 'ACTIVE'),
            ('TONE_CAUTIOUS', 'TONE_CAUTIOUS', '谨慎提示', '风险提示但不恐吓', ['RISK','EMERGENCY','FINANCE'], ['需留意', '可能有波动'], 'ACTIVE'),
            ('TONE_NEUTRAL', 'TONE_NEUTRAL', '中性客观', '陈述事实不带情绪', ['WORK','LEARNING','GENERAL'], ['今日宜...', '传统认为...'], 'ACTIVE'),
            ('TONE_ENCOURAGE', 'TONE_ENCOURAGE', '鼓励支持', '正向激励但不夸大', ['GROWTH','CREATIVE','ADVENTURE'], ['潜力不错', '适合尝试'], 'ACTIVE'),
            ('TONE_COMPASSIONATE', 'TONE_COMPASSIONATE', '慈悲关怀', '带有传统文化关怀色彩', ['HEALTH','SELF','INTERNAL'], ['身心宜养护', '宜静心'], 'ACTIVE'),
        ]
        for t in tones:
            cr.execute("""
                INSERT INTO tone_lexicon (tone_id, tone_code, tone_name_cn, description, usage_context, examples, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (tone_id) DO NOTHING
            """, t)
        print(f"  ✓ {len(tones)} tones inserted")

        # ── 6. MIGRATE G3 FORBIDDEN PATTERNS ────────────────────────
        print("\n=== MIGRATING G3 FORBIDDEN PATTERNS ===")
        forbidden = [
            ('FORB_FIN_01', r'steady|guaranteed_profit|must_rise|principal', 'REGEX', 'FINANCIAL_GUARANTEE', 'BLOCK', '财务保证类禁用词', None, 'ACTIVE'),
            ('FORB_FIN_02', r'guarantee.*return|guarantee.*profit', 'REGEX', 'FINANCIAL_GUARANTEE', 'BLOCK', '保证收益类禁用词', None, 'ACTIVE'),
            ('FORB_MED_01', r'cure|radical_cure|guarantee.*recovery', 'REGEX', 'MEDICAL_CLAIM', 'BLOCK', '医疗承诺类禁用词', None, 'ACTIVE'),
            ('FORB_DET_01', r'definitely|inevitably|destined|absolutely', 'REGEX', 'DETERMINISTIC_PREDICTION', 'BLOCK', '确定性预测禁用词', None, 'ACTIVE'),
            ('FORB_FEAR_01', r'calamity|blood|disaster|doom', 'REGEX', 'FEAR_INDUCTION', 'BLOCK', '恐惧诱导禁用词', None, 'ACTIVE'),
            ('FORB_COER_01', r'must|must_not|forbidden|unacceptable', 'REGEX', 'COERCIVE_GUIDANCE', 'BLOCK', '强制性引导禁用词', None, 'ACTIVE'),
            ('FORB_PROB_01', r'[0-9]{1,3}%.*(possible|will|probab)', 'REGEX', 'PROBABILITY_CLAIM', 'BLOCK', '概率声称禁用词', None, 'ACTIVE'),
        ]
        for f in forbidden:
            cr.execute("""
                INSERT INTO forbidden_terms (term_id, term_pattern, pattern_type, category, severity, description, source_refs, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (term_id) DO NOTHING
            """, f)
        print(f"  ✓ {len(forbidden)} forbidden terms imported")

        # ── 7. INSERT RISK TERMS ────────────────────────────────────
        print("\n=== INSERTING risk_terms ===")
        risks = [
            ('RISK_01', 'probability_escalation', 'CERTAINTY_ESCALATION', 'WARN', '概率词升级（可能→很可能→一定）', '保持概率表述克制'),
            ('RISK_02', 'modality_escalation', 'CERTAINTY_ESCALATION', 'WARN', '模态词升级（可以→应该→必须）', '尊重用户自主权'),
            ('RISK_03', 'prediction_precision', 'CERTAINTY_ESCALATION', 'WARN', '预测精准化（趋势→精准时间）', '避免过度具体化'),
            ('RISK_04', 'ancient_method_fabrication', 'AI_HALLUCINATION', 'WARN', '古法强引（无来源的"古法曰"）', '必须可追溯'),
            ('RISK_05', 'insufficient_evidence_assertion', 'AI_HALLUCINATION', 'WARN', '证据不足断言', '双源核验原则'),
        ]
        for r in risks:
            cr.execute("""
                INSERT INTO risk_terms (risk_id, risk_pattern, risk_category, severity, description, mitigation, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVE')
                ON CONFLICT (risk_id) DO NOTHING
            """, r)
        print(f"  ✓ {len(risks)} risk terms inserted")

        # ── 8. INSERT SAMPLE MODERN EXPRESSIONS ────────────────────
        print("\n=== INSERTING modern_expressions (sample) ===")
        expressions = [
            ('EXP_001', '宜', '适合做...', 'life', 'life', ['warm','respect'], ['suggest'], ['advise_mandatory'], ['daily_guide'], None, '1.0.0', 'ACTIVE'),
            ('EXP_002', '忌', '建议避免...', 'life', 'life', ['cautious','respect'], ['warn'], ['forbid'], ['daily_guide'], None, '1.0.0', 'ACTIVE'),
            ('EXP_003', '吉', '能量良好', 'life', 'life', ['confident','warm'], ['inform'], ['guarantee'], ['daily_guide'], None, '1.0.0', 'ACTIVE'),
            ('EXP_004', '凶', '需留意', 'life', 'life', ['cautious','compassionate'], ['warn','inform'], ['fear_induce'], ['daily_guide'], None, '1.0.0', 'ACTIVE'),
            ('EXP_005', '冲', '能量碰撞', 'relationship', 'relationship', ['neutral','respect'], ['explain'], ['predict'], ['relationship_guide'], None, '1.0.0', 'ACTIVE'),
            ('EXP_006', '合', '能量契合', 'relationship', 'relationship', ['warm','encourage'], ['inform','suggest'], ['guarantee'], ['relationship_guide'], None, '1.0.0', 'ACTIVE'),
        ]
        for e in expressions:
            cr.execute("""
                INSERT INTO modern_expressions (expression_id, traditional_term, modern_expression, domain, context_code, tone_tags, allowed_actions, forbidden_actions, theme_tags, source_refs, version, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (expression_id) DO NOTHING
            """, e)
        print(f"  ✓ {len(expressions)} expressions inserted")

        # ── 9. INSERT TEMPLATE ──────────────────────────────────────
        print("\n=== INSERTING templates ===")
        templates = [
            ('TPL_DAILY_GUIDE', '每日指南模板', 'OUTPUT', 'life', 'TONE_WARM', 'life',
             json.dumps({"sections": ["今日宜", "今日忌", "能量提示", "行动建议"]}),
             json.dumps([{"宜": "适合开启新项目", "忌": "避免重大决策"}]), None, '1.0.0', 'ACTIVE'),
            ('TPL_RELATIONSHIP', '关系匹配模板', 'OUTPUT', 'relationship', 'TONE_RESPECT', 'relationship',
             json.dumps({"sections": ["契合度", "共同节奏", "注意事项", "建议"]}),
             json.dumps([{"契合度": "高", "共同节奏": "同步"}]), None, '1.0.0', 'ACTIVE'),
            ('TPL_AUDIT_CHECK', '审计检查模板', 'AUDIT', 'general', 'TONE_NEUTRAL', 'general',
             json.dumps({"sections": ["G1证据链", "G2转译规范", "G3安全门", "G4输出质量"]}),
             json.dumps([]), None, '1.0.0', 'ACTIVE'),
        ]
        for t in templates:
            cr.execute("""
                INSERT INTO templates (template_id, template_name, template_type, domain, tone_id, context_code, structure, examples, source_refs, version, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (template_id) DO NOTHING
            """, t)
        print(f"  ✓ {len(templates)} templates inserted")

        # ── 10. UPDATE MIGRATION VERSIONS ──────────────────────────
        print("\n=== UPDATING MIGRATION VERSIONS ===")
        cr.execute("""
            INSERT INTO migration_versions (version, applied_at, status)
            VALUES ('20260821_translation_system_v1', NOW(), 'APPLIED')
            ON CONFLICT (version) DO NOTHING
        """)
        print("  ✓ migration version recorded")

        # ── VERIFICATION ───────────────────────────────────────────
        print("\n=== VERIFICATION ===")
        tables_to_check = ['life_domains', 'semantic_concepts', 'modern_expressions', 
                          'tone_lexicon', 'forbidden_terms', 'risk_terms', 'templates']
        for t in tables_to_check:
            cr.execute(f"SELECT COUNT(*) FROM {t}")
            count = cr.fetchone()[0]
            print(f"  {t}: {count} rows")
        
        cr.execute("SELECT COUNT(*) FROM semantic_mappings")
        print(f"  semantic_mappings (original): {cr.fetchone()[0]} rows")

        print("\n✓ Phase 1 COMPLETE")

run()
