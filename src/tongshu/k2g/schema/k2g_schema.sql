-- ============================================================
-- K2G Schema V1.0 — 顺天 Knowledge to Guidance 数据库定义
-- 配套文档: docs/k2g/K2G_DEVELOPMENT_SPEC_V1.0.md
-- ============================================================

-- 启用扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 公共字段混入（通过视图或继承实现）
-- 所有表共享的基础审计字段
-- ============================================================

-- 通用审计混合表（供参考，实际部署时按需添加到各表）
CREATE TABLE IF NOT EXISTS k2g_audit_base (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    registry_id     VARCHAR(50) NOT NULL,
    version         VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    status          VARCHAR(20) NOT NULL DEFAULT 'DRAFT'
        CHECK (status IN ('DRAFT', 'REVIEW', 'VALIDATED', 'ACTIVE', 'DEPRECATED')),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by      VARCHAR(100),
    reviewed_by     VARCHAR(100),
    reviewed_at     TIMESTAMP,
    audit_log       JSONB
);

-- ============================================================
-- 1. k2g_concepts — 传统概念注册表
-- ============================================================
CREATE TABLE k2g_concepts (
    concept_id          VARCHAR(50) PRIMARY KEY,
    domain              VARCHAR(20) NOT NULL
        CHECK (domain IN ('BAZI', 'BLIND', 'ZIWEI', 'YIJING', 'HELUO', 'TONGSHU')),
    school              VARCHAR(50),
    concept_type        VARCHAR(50) NOT NULL,
    traditional_term    VARCHAR(100) NOT NULL,
    alternative_terms   JSONB DEFAULT '[]'::jsonb,
    canonical_definition JSONB,
    source_refs         JSONB NOT NULL DEFAULT '[]'::jsonb,
    verification_status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (verification_status IN ('pending', 'approved', 'rejected', 'deprecated')),
    evidence_refs       JSONB DEFAULT '[]'::jsonb,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(domain, traditional_term)
);

CREATE INDEX idx_k2g_concepts_domain ON k2g_concepts(domain);
CREATE INDEX idx_k2g_concepts_type ON k2g_concepts(concept_type);
CREATE INDEX idx_k2g_concepts_status ON k2g_concepts(verification_status);

-- ============================================================
-- 2. k2g_semantics — 产品语义注册表
-- ============================================================
CREATE TABLE k2g_semantics (
    semantic_id         VARCHAR(50) PRIMARY KEY,
    canonical_label     VARCHAR(100) NOT NULL,
    short_label         VARCHAR(50),
    keywords            JSONB DEFAULT '{"positive": [], "negative": []}'::jsonb,
    dimensions          JSONB DEFAULT '[]'::jsonb,
    allowed_context     JSONB DEFAULT '[]'::jsonb,
    forbidden_claims    JSON[] NOT NULL DEFAULT '{}',
    related_semantics   JSONB DEFAULT '[]'::jsonb,
    parent_theme        VARCHAR(20) NOT NULL
        CHECK (parent_theme IN ('XING', 'SHI', 'REN', 'JU', 'YANG', 'SHI_T')),
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(canonical_label)
);

CREATE INDEX idx_k2g_semantics_theme ON k2g_semantics(parent_theme);
CREATE INDEX idx_k2g_semantics_id ON k2g_semantics(semantic_id);

-- ============================================================
-- 3. k2g_mappings — Fact → Semantic 映射注册表
-- ============================================================
CREATE TABLE k2g_mappings (
    mapping_id          VARCHAR(50) PRIMARY KEY,
    source_domain       VARCHAR(20) NOT NULL
        CHECK (source_domain IN ('BAZI', 'BLIND', 'ZIWEI', 'YIJING', 'HELUO', 'TONGSHU')),
    source_school       VARCHAR(50),
    source_concept      VARCHAR(100) NOT NULL,
    trigger             JSONB NOT NULL,
    target_semantics    JSONB NOT NULL,
    mapping_type        VARCHAR(20) NOT NULL DEFAULT 'semantic'
        CHECK (mapping_type IN ('semantic', 'relational', 'contextual')),
    allowed_context     JSONB DEFAULT '[]'::jsonb,
    evidence_refs       JSONB NOT NULL DEFAULT '[]'::jsonb,
    rule_refs           JSONB DEFAULT '[]'::jsonb,
    conflict_resolution JSONB,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (source_concept) REFERENCES k2g_concepts(traditional_term)
);

CREATE INDEX idx_k2g_mappings_domain ON k2g_mappings(source_domain);
CREATE INDEX idx_k2g_mappings_concept ON k2g_mappings(source_concept);
CREATE INDEX idx_k2g_mappings_type ON k2g_mappings(mapping_type);

-- ============================================================
-- 4. k2g_relations — 关系融合注册表
-- ============================================================
CREATE TABLE k2g_relations (
    relation_id         VARCHAR(50) PRIMARY KEY,
    inputs              JSONB NOT NULL,
    relation_type       VARCHAR(20) NOT NULL
        CHECK (relation_type IN (
            'SUPPORT', 'CONTRADICT', 'QUALIFY', 'AMPLIFY',
            'REDUCE', 'COMPLEMENT', 'CONFLICT', 'SEQUENCE', 'CONDITION'
        )),
    output              JSONB NOT NULL,
    conditions          JSONB DEFAULT '[]'::jsonb,
    fallback            JSONB,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_k2g_relations_type ON k2g_relations(relation_type);
CREATE INDEX idx_k2g_relations_inputs ON k2g_relations USING GIN(inputs);

-- ============================================================
-- 5. k2g_contexts — 场景上下文注册表
-- ============================================================
CREATE TABLE k2g_contexts (
    context_id          VARCHAR(50) PRIMARY KEY,
    parent_theme        VARCHAR(20) NOT NULL
        CHECK (parent_theme IN ('XING', 'SHI', 'REN', 'JU', 'YANG', 'SHI_T')),
    product_label       VARCHAR(100) NOT NULL,
    aliases             JSONB DEFAULT '[]'::jsonb,
    allowed_semantics   JSONB NOT NULL DEFAULT '[]'::jsonb,
    forbidden_semantics JSONB DEFAULT '[]'::jsonb,
    usage_rules         JSONB DEFAULT '[]'::jsonb,
    related_contexts    JSONB DEFAULT '[]'::jsonb,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_k2g_contexts_theme ON k2g_contexts(parent_theme);

-- ============================================================
-- 6. k2g_states — 状态向量注册表
-- ============================================================
CREATE TABLE k2g_states (
    state_id            VARCHAR(50) PRIMARY KEY,
    signals             JSONB NOT NULL,
    supporting_signals  JSONB DEFAULT '[]'::jsonb,
    transition_rules    JSONB DEFAULT '[]'::jsonb,
    evidence_provenance JSONB,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_k2g_states_id ON k2g_states(state_id);

-- ============================================================
-- 7. k2g_daily_guidance — 每日指引注册表 (DGR)
-- ============================================================
CREATE TABLE k2g_daily_guidance (
    guidance_id         VARCHAR(50) PRIMARY KEY,
    state_conditions    JSONB NOT NULL,
    context             JSONB NOT NULL,
    theme               JSONB,
    opportunity         JSONB,
    risk                JSONB,
    action              JSONB,
    rhythm              JSONB,
    priority            INTEGER NOT NULL DEFAULT 50
        CHECK (priority >= 0 AND priority <= 100),
    evidence_refs       JSONB NOT NULL DEFAULT '[]'::jsonb,
    mapping_refs        JSONB DEFAULT '[]'::jsonb,
    relation_refs       JSONB DEFAULT '[]'::jsonb,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_k2g_guidance_state ON k2g_daily_guidance USING GIN(state_conditions);
CREATE INDEX idx_k2g_guidance_context ON k2g_daily_guidance USING GIN(context);
CREATE INDEX idx_k2g_guidance_priority ON k2g_daily_guidance(priority DESC);

-- ============================================================
-- 8. k2g_actions — 行动建议注册表
-- ============================================================
CREATE TABLE k2g_actions (
    action_id           VARCHAR(50) PRIMARY KEY,
    semantic_id         VARCHAR(50) NOT NULL,
    context             VARCHAR(50) NOT NULL,
    action_type         VARCHAR(20) NOT NULL
        CHECK (action_type IN ('execution', 'reflection', 'communication', 'adjustment', 'rest')),
    templates           JSONB NOT NULL,
    forbidden_phrases   JSON[] NOT NULL DEFAULT '{}',
    constraints         JSONB NOT NULL DEFAULT '{}'::jsonb,
    related_semantics   JSONB DEFAULT '[]'::jsonb,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (semantic_id) REFERENCES k2g_semantics(semantic_id)
);

CREATE INDEX idx_k2g_actions_semantic ON k2g_actions(semantic_id);
CREATE INDEX idx_k2g_actions_context ON k2g_actions(context);

-- ============================================================
-- 9. k2g_expressions — 表达模板注册表
-- ============================================================
CREATE TABLE k2g_expressions (
    expression_id       VARCHAR(50) PRIMARY KEY,
    semantic_id         VARCHAR(50) NOT NULL,
    action_ref          VARCHAR(50),
    style               JSONB DEFAULT '{}'::jsonb,
    text                JSONB NOT NULL,
    variants            JSONB DEFAULT '[]'::jsonb,
    forbidden_patterns  JSON[] NOT NULL DEFAULT '{}',
    locale              VARCHAR(20) NOT NULL DEFAULT 'zh-CN'
        CHECK (locale IN ('zh-CN', 'en-US')),
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (semantic_id) REFERENCES k2g_semantics(semantic_id)
);

CREATE INDEX idx_k2g_expr_semantic ON k2g_expressions(semantic_id);
CREATE INDEX idx_k2g_expr_locale ON k2g_expressions(locale);

-- ============================================================
-- 10. k2g_safety — 安全约束注册表
-- ============================================================
CREATE TABLE k2g_safety (
    safety_rule_id      VARCHAR(50) PRIMARY KEY,
    rule_type           VARCHAR(50) NOT NULL,
    severity            VARCHAR(20) NOT NULL DEFAULT 'BLOCK'
        CHECK (severity IN ('BLOCK', 'WARN', 'INFO')),
    description         TEXT NOT NULL,
    patterns            JSONB NOT NULL,
    applies_to          JSONB NOT NULL,
    check_level         VARCHAR(20) NOT NULL DEFAULT 'pre_output'
        CHECK (check_level IN ('pre_write', 'pre_output', 'post_render')),
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_k2g_safety_type ON k2g_safety(rule_type);
CREATE INDEX idx_k2g_safety_severity ON k2g_safety(severity);

-- ============================================================
-- 横向支撑表
-- ============================================================

-- 证据绑定
CREATE TABLE k2g_evidence_bindings (
    binding_id      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    concept_id      VARCHAR(50) REFERENCES k2g_concepts(concept_id),
    mapping_id      VARCHAR(50) REFERENCES k2g_mappings(mapping_id),
    evidence_id     VARCHAR(50) NOT NULL,
    source_layer    VARCHAR(50) NOT NULL,
    binding_type    VARCHAR(20) NOT NULL
        CHECK (binding_type IN ('supports', 'conflicts', 'qualifies')),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_k2g_evidence_mapping ON k2g_evidence_bindings(mapping_id);
CREATE INDEX idx_k2g_evidence_concept ON k2g_evidence_bindings(concept_id);

-- 黄金案例
CREATE TABLE k2g_golden_cases (
    case_id           VARCHAR(50) PRIMARY KEY,
    domain            VARCHAR(20) NOT NULL,
    case_type         VARCHAR(50) NOT NULL,
    input_profile     JSONB NOT NULL,
    expected_state    VARCHAR(50) NOT NULL,
    expected_guidance VARCHAR(50) NOT NULL,
    expected_action   VARCHAR(50) NOT NULL,
    expected_expression VARCHAR(50),
    source_ref        VARCHAR(200),
    verification_status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (verification_status IN ('pending', 'passed', 'failed')),
    created_at        TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_k2g_golden_domain ON k2g_golden_cases(domain);
CREATE INDEX idx_k2g_golden_status ON k2g_golden_cases(verification_status);

-- 版本追踪
CREATE TABLE k2g_versions (
    version_id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    version           VARCHAR(20) NOT NULL,
    change_type       VARCHAR(20) NOT NULL
        CHECK (change_type IN ('MAJOR', 'MINOR', 'PATCH')),
    description       TEXT NOT NULL,
    changed_by        VARCHAR(100) NOT NULL,
    changed_at        TIMESTAMP NOT NULL DEFAULT NOW(),
    affected_tables   JSONB,
    backward_compatible BOOLEAN NOT NULL DEFAULT true
);

-- ============================================================
-- 视图：常用查询聚合
-- ============================================================

-- 已批准的概念列表
CREATE VIEW v_k2g_approved_concepts AS
SELECT concept_id, domain, school, concept_type, traditional_term,
       verification_status, source_refs
FROM k2g_concepts
WHERE verification_status = 'approved';

-- 有 Evidence 支持的 Mapping
CREATE VIEW v_k2g_mapped_with_evidence AS
SELECT m.mapping_id, m.source_domain, m.source_concept,
       m.target_semantics, COUNT(DISTINCT e.evidence_id) as evidence_count
FROM k2g_mappings m
LEFT JOIN k2g_evidence_bindings e ON m.mapping_id = e.mapping_id
GROUP BY m.mapping_id;

-- ============================================================
-- 初始数据：Safety Registry 基础规则
-- ============================================================
INSERT INTO k2g_safety (safety_rule_id, rule_type, severity, description, patterns, applies_to, check_level) VALUES
('SAFETY_001', 'CLAIM_ESCALATION', 'BLOCK', '禁止将"建议"升级为"必须"', '["\\b一定\\b", "\\b必然\\b", "\\b保证\\b", "\\b肯定\\b", "\\b绝对不会\\b"]', '["EXPRESSION_REGISTRY", "ACTION_REGISTRY", "DAILY_GUIDANCE_REGISTRY"]', 'pre_output'),
('SAFETY_002', 'SEMANTIC_DRIFT', 'BLOCK', '禁止语义漂移', '["边界.*隔离", "收束.*封闭", "留白.*空白"]', '["EXPRESSION_REGISTRY"]', 'pre_output'),
('SAFETY_003', 'TEMPORAL_DRIFT', 'BLOCK', '禁止时间范围漂移', '["今日.*一生", "今天.*永远", "\\b必然\\b.*未来\\b三年\\b"]', '["EXPRESSION_REGISTRY", "ACTION_REGISTRY"]', 'pre_output'),
('SAFETY_004', 'MEDICAL_CLAIM', 'BLOCK', '禁止具体医疗建议', '["治疗", "治愈", "服药", "诊断", "疾病.*一定", "病症"]', '["EXPRESSION_REGISTRY", "ACTION_REGISTRY"]', 'pre_output'),
('SAFETY_005', 'FINANCIAL_CERTAINTY', 'BLOCK', '禁止财务确定性预测', '["一定.*发财", "必定.*盈利", " guaranteed.*profit", "稳赚"]', '["EXPRESSION_REGISTRY", "ACTION_REGISTRY"]', 'pre_output'),
('SAFETY_006', 'RELATIONSHIP_CERTAINTY', 'BLOCK', '禁止关系确定性判断', '["一定会.*分手", "必然.*离婚", "注定.*分离", "必定.*复合"]', '["EXPRESSION_REGISTRY", "ACTION_REGISTRY"]', 'pre_output'),
('SAFETY_007', 'FALSE_CAUSALITY', 'WARN', '标记可能的虚假因果', '["因为.*所以.*一定", "由于.*必然.*导致"]', '["EXPRESSION_REGISTRY"]', 'pre_output'),
('SAFETY_008', 'UNSUPPORTED_PREDICTION', 'WARN', '标记无依据的预测性陈述', '["你会.*遇到", "明天.*会.*", "将来.*必然"]', '["EXPRESSION_REGISTRY"]', 'pre_output'),
('SAFETY_009', 'SCOPE_DRIFT', 'WARN', '标记范围漂移', '["特定.*所有", "某个.*全部", "个别.*普遍"]', '["EXPRESSION_REGISTRY"]', 'pre_output'),
('SAFETY_010', 'CERTAINTY_DRIFT', 'BLOCK', '禁止确定性升级', '["可能.*一定", "适合.*必须", "建议.*应该.*一定"]', '["EXPRESSION_REGISTRY", "ACTION_REGISTRY"]', 'pre_output');
