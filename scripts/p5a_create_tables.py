# -*- coding: utf-8 -*-
"""
Phase 5-A: User Identity Layer DDL 脚本

创建表:
- user_profiles
- birth_profiles
- personal_heluo_models
- daily_state
"""
from __future__ import annotations
import logging
import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)


def create_user_identity_tables(conn):
    """创建 User Identity Layer 表结构。"""
    cur = conn.cursor()
    
    # 1. user_profiles
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            anonymous_id VARCHAR(64) UNIQUE,
            locale VARCHAR(10) DEFAULT 'zh-CN',
            timezone VARCHAR(50) DEFAULT 'Asia/Shanghai',
            language VARCHAR(10) DEFAULT 'zh',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            metadata JSONB DEFAULT '{}'
        )
    """)
    logger.info("Created table: user_profiles")
    
    # 2. birth_profiles
    cur.execute("""
        CREATE TABLE IF NOT EXISTS birth_profiles (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
            birth_date DATE NOT NULL,
            birth_time TIME,
            birth_location_ganzhi VARCHAR(20),
            timezone VARCHAR(50) NOT NULL DEFAULT 'Asia/Shanghai',
            longitude DECIMAL(10, 6),
            latitude DECIMAL(10, 6),
            true_solar_time TIME,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """)
    logger.info("Created table: birth_profiles")
    
    # 3. personal_heluo_models
    cur.execute("""
        CREATE TABLE IF NOT EXISTS personal_heluo_models (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
            benming_hexagram VARCHAR(20) NOT NULL,
            benming_trigram_upper VARCHAR(10),
            benming_trigram_lower VARCHAR(10),
            yuan_tang VARCHAR(10),
            postnatal_hexagram VARCHAR(20),
            postnatal_trigram_upper VARCHAR(10),
            postnatal_trigram_lower VARCHAR(10),
            dominant_element VARCHAR(10),
            element_strength DECIMAL(5, 2),
            da_yun_snapshot JSONB,
            liu_nian_snapshot JSONB,
            created_version INT DEFAULT 1,
            calculation_context JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id)
        )
    """)
    logger.info("Created table: personal_heluo_models")
    
    # 4. daily_state
    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_state (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
            state_date DATE NOT NULL,
            energy_state VARCHAR(50),
            energy_score DECIMAL(5, 2),
            hexagram_state JSONB,
            element_balance JSONB,
            advice_context TEXT,
            source_type VARCHAR(20) DEFAULT 'algorithm',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, state_date)
        )
    """)
    logger.info("Created table: daily_state")
    
    # 创建索引
    cur.execute("CREATE INDEX IF NOT EXISTS idx_user_profiles_anonymous ON user_profiles(anonymous_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_user_profiles_locale ON user_profiles(locale)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_birth_profiles_user ON birth_profiles(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_heluo_models_user ON personal_heluo_models(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_daily_state_user_date ON daily_state(user_id, state_date)")
    
    conn.commit()
    logger.info("User Identity Layer tables created successfully")
    return True


def insert_sample_data(conn):
    """插入样本数据用于测试。"""
    cur = conn.cursor()
    
    # 插入测试用户
    cur.execute("""
        INSERT INTO user_profiles (anonymous_id, locale, timezone, language, metadata)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, ('test-device-001', 'zh-CN', 'Asia/Shanghai', 'zh', '{"source": "nfc"}'))
    user_id = cur.fetchone()[0]
    
    # 插入出生信息
    cur.execute("""
        INSERT INTO birth_profiles (user_id, birth_date, birth_time, timezone, longitude, latitude, true_solar_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (user_id, '1990-05-15', '14:30:00', 'Asia/Shanghai', 121.47, 31.23, '14:22:03'))
    
    # 插入个人河洛模型
    cur.execute("""
        INSERT INTO personal_heluo_models (user_id, benming_hexagram, yuan_tang, postnatal_hexagram, dominant_element, element_strength, calculation_context)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (user_id, '乾上乾下', '天', '乾上坤下', '火', 85.50, '{"birth_ganzhi": {"year": "庚午", "month": "辛巳", "day": "戊子", "hour": "未时"}}'))
    
    # 插入今日状态
    from datetime import date, timedelta
    today = date.today()
    cur.execute("""
        INSERT INTO daily_state (user_id, state_date, energy_state, energy_score, hexagram_state, element_balance, advice_context)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (user_id, today, '旺盛', 85.50, 
          '{"current": "乾卦", "trend": "上升"}',
          '{"金": 0.2, "木": 0.1, "水": 0.15, "火": 0.4, "土": 0.15}',
          '今日阳气旺盛，宜主动进取，把握机遇'))
    
    conn.commit()
    logger.info("Sample data inserted")
    return user_id


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        dbname="shuntian_kb",
        user="postgres",
        password="postgres"
    )
    
    try:
        create_user_identity_tables(conn)
        user_id = insert_sample_data(conn)
        print(f"✅ User Identity Layer ready. Sample user: {user_id}")
    finally:
        conn.close()
