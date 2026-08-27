# -*- coding: utf-8 -*-
"""
Phase 6-A/B: NFC Experience Layer DDL 脚本

创建表:
- nfc_devices
- user_nfc_bindings
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

FROZEN_VERSION = 'v1.0.0'


def create_nfc_tables(conn) -> None:
    """创建NFC相关表结构。"""
    cur = conn.cursor()
    
    # 1. nfc_devices
    cur.execute('''
        CREATE TABLE IF NOT EXISTS nfc_devices (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            device_token VARCHAR(64) NOT NULL UNIQUE,
            device_type VARCHAR(20) NOT NULL CHECK (device_type IN ('pendant', 'tag', 'phone')),
            status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'revoked')),
            last_used_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            version VARCHAR(20) NOT NULL DEFAULT 'v1.0.0'
        );
    ''')
    logger.info('✓ 创建 nfc_devices 表')
    
    # 2. user_nfc_bindings
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user_nfc_bindings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
            device_id UUID NOT NULL REFERENCES nfc_devices(id) ON DELETE CASCADE,
            bind_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            unbind_time TIMESTAMPTZ,
            is_primary BOOLEAN NOT NULL DEFAULT false,
            UNIQUE(user_id, device_id)
        );
    ''')
    logger.info('✓ 创建 user_nfc_bindings 表')
    
    # 创建索引
    cur.execute('''
        CREATE INDEX IF NOT EXISTS idx_nfc_devices_token 
        ON nfc_devices(device_token)
    ''')
    cur.execute('''
        CREATE INDEX IF NOT EXISTS idx_nfc_bindings_user 
        ON user_nfc_bindings(user_id)
    ''')
    cur.execute('''
        CREATE INDEX IF NOT EXISTS idx_nfc_bindings_device 
        ON user_nfc_bindings(device_id)
    ''')
    logger.info('✓ 创建索引')
    
    conn.commit()
    logger.info('✅ NFC表创建完成')


def main():
    """主函数。"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info('连接到数据库 shuntian_kb')
        
        create_nfc_tables(conn)
        
        # 验证
        cur = conn.cursor()
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('nfc_devices', 'user_nfc_bindings')
        """)
        tables = [r[0] for r in cur.fetchall()]
        
        logger.info(f'✅ Phase 6 DDL 执行完成')
        logger.info(f'   新增表: {tables}')
        
    except Exception as e:
        logger.error(f'❌ 错误: {e}')
        raise
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    main()
