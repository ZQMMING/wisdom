# -*- coding: utf-8 -*-
"""
Phase 5-D: Relationship State Engine DDL 脚本

创建表:
- relationship_profiles
- relationship_states
- relationship_rules
"""
from __future__ import annotations
import logging
import psycopg2
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 5432,
    'dbname': 'shuntian_kb',
    'user': 'postgres',
    'password': 'postgres'
}

# 冻结版本
FROZEN_VERSION = 'v1.0.0'


def create_relationship_tables(conn) -> None:
    """创建关系引擎表结构。"""
    cur = conn.cursor()
    
    # 1. relationship_profiles
    cur.execute('''
        CREATE TABLE IF NOT EXISTS relationship_profiles (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            person_a_model_id UUID NOT NULL REFERENCES personal_heluo_models(id) ON DELETE CASCADE,
            person_b_model_id UUID NOT NULL REFERENCES personal_heluo_models(id) ON DELETE CASCADE,
            relationship_type VARCHAR(20) NOT NULL CHECK (relationship_type IN ('partner', 'family', 'business', 'friend')),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            version VARCHAR(20) NOT NULL DEFAULT 'v1.0.0'
        );
    ''')
    logger.info('✓ 创建 relationship_profiles 表')
    
    # 2. relationship_states
    cur.execute('''
        CREATE TABLE IF NOT EXISTS relationship_states (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            relationship_id UUID NOT NULL REFERENCES relationship_profiles(id) ON DELETE CASCADE,
            calculation_version VARCHAR(20) NOT NULL DEFAULT 'v1.0.0',
            element_relation VARCHAR(50) NOT NULL,
            hexagram_relation VARCHAR(50) NOT NULL,
            time_sync VARCHAR(50) NOT NULL,
            current_phase VARCHAR(50) NOT NULL,
            interaction_mode VARCHAR(50) NOT NULL,
            strength_level VARCHAR(20) NOT NULL CHECK (strength_level IN ('weak', 'moderate', 'strong')),
            attention_points TEXT,
            suggestions TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    ''')
    logger.info('✓ 创建 relationship_states 表')
    
    # 3. relationship_rules
    cur.execute('''
        CREATE TABLE IF NOT EXISTS relationship_rules (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            rule_code VARCHAR(20) NOT NULL UNIQUE,
            rule_type VARCHAR(20) NOT NULL CHECK (rule_type IN ('element', 'hexagram', 'time')),
            description TEXT NOT NULL,
            source_reference TEXT,
            algorithm_version VARCHAR(20) NOT NULL DEFAULT 'v1.0.0',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    ''')
    logger.info('✓ 创建 relationship_rules 表')
    
    conn.commit()
    logger.info('✅ 所有关系表创建完成')


def insert_initial_rules(conn) -> None:
    """插入初始规则种子数据。"""
    cur = conn.cursor()
    
    rules = [
        # 五行互动规则
        ('EL-GEN', 'element', '五行相生', '木→火→土→金→水→木', '《河图》生成数', FROZEN_VERSION),
        ('EL-KE', 'element', '五行相克', '木→土→水→火→金→木', '《河图》生成数', FROZEN_VERSION),
        ('EL-TONG', 'element', '五行同类', '同元素元素增强', '五行理论', FROZEN_VERSION),
        ('EL-XIE', 'element', '五行泄耗', '强元素泄弱元素', '五行理论', FROZEN_VERSION),
        
        # 卦象互动规则
        ('HG-SAME', 'hexagram', '同卦共振', '相同卦象产生共振效应', '《易经》', FROZEN_VERSION),
        ('HG-COMP', 'hexagram', '卦象互补', '对立卦象产生互补', '《易经》', FROZEN_VERSION),
        ('HG-CONFLICT', 'hexagram', '卦象冲突', '相冲卦象产生张力', '《易经》', FROZEN_VERSION),
        
        # 时间同步规则
        ('TIME-SYNC', 'time', '时间同步', '双方处于相同时间周期', '河洛理数', FROZEN_VERSION),
        ('TIME-ASYNC', 'time', '时间异步', '双方处于不同时间周期', '河洛理数', FROZEN_VERSION),
        ('TIME-COMP', 'time', '时间互补', '双方周期互补', '河洛理数', FROZEN_VERSION),
    ]
    
    for code, rtype, desc, src, ref, ver in rules:
        cur.execute('''
            INSERT INTO relationship_rules (rule_code, rule_type, description, source_reference, algorithm_version)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (rule_code) DO NOTHING
        ''', (code, rtype, desc, ref, ver))
    
    conn.commit()
    logger.info(f'✓ 插入 {len(rules)} 条规则种子')


def main():
    """主函数。"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info('连接到数据库 shuntian_kb')
        
        create_relationship_tables(conn)
        insert_initial_rules(conn)
        
        # 验证
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM relationship_rules")
        rule_count = cur.fetchone()[0]
        
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'relationship_%'
        """)
        tables = [r[0] for r in cur.fetchall()]
        
        logger.info(f'✅ Phase 5-D DDL 执行完成')
        logger.info(f'   表: {tables}')
        logger.info(f'   规则: {rule_count} 条')
        
    except Exception as e:
        logger.error(f'❌ 错误: {e}')
        raise
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    main()
