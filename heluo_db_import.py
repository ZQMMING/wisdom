#!/usr/bin/env python3
"""
HeluoRuleEvidenceMatrix 结构化入库脚本
将 HeluoRuleEvidenceMatrix_Final.md 中的14条规则录入独立SQLite数据库
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path.home() / "wisdom" / "heluo_rule_evidence.db"

# 数据库Schema
SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL CHECK(type IN ('original', 'auxiliary')),
    url TEXT,
    description TEXT,
    authority_score INTEGER CHECK(authority_score BETWEEN 1 AND 5),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL UNIQUE,
    rule_name TEXT NOT NULL,
    description TEXT,
    core_algorithm TEXT,
    implementation_type TEXT,
    verification_status TEXT NOT NULL CHECK(verification_status IN ('已验证', '已补全', '待细化', '未实现')),
    evidence_rating TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rule_evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    source_id INTEGER NOT NULL,
    evidence_type TEXT CHECK(evidence_type IN ('original_quote', 'algorithm', 'example', 'verification')),
    content TEXT NOT NULL,
    source_line_ref TEXT,
    confidence_score INTEGER CHECK(confidence_score BETWEEN 1 AND 5),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES rules(rule_id),
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

CREATE TABLE IF NOT EXISTS algorithm_specs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    spec_name TEXT NOT NULL,
    spec_content TEXT,
    language TEXT DEFAULT 'python',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES rules(rule_id)
);

CREATE TABLE IF NOT EXISTS verification_matrix (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    source_1 TEXT,
    source_2 TEXT,
    source_3 TEXT,
    source_4 TEXT,
    source_5 TEXT,
    cross_validation_result TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES rules(rule_id)
);

CREATE TABLE IF NOT EXISTS key_findings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    finding_text TEXT NOT NULL,
    evidence_source TEXT,
    resolution_status TEXT DEFAULT 'resolved',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hexagram_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    num INTEGER NOT NULL UNIQUE,
    gua_name TEXT NOT NULL,
    gua_symbol TEXT,
    trigram_upper TEXT,
    trigram_lower TEXT,
    note TEXT
);

CREATE INDEX idx_rule_evidence_rule ON rule_evidence(rule_id);
CREATE INDEX idx_rules_id ON rules(rule_id);
CREATE INDEX idx_sources_name ON sources(name);
"""

def init_db(conn):
    """初始化数据库表结构"""
    conn.executescript(SCHEMA)
    conn.commit()
    print(f"✓ 数据库表结构已创建: {DB_PATH}")

def insert_sources(conn):
    """录入证据来源"""
    sources = [
        ('《河洛真数》续修四库全书本·天一阁藏', 'original', 'diancang.xyz/21177', '权威底本，起例卷上/下完整内容', 5),
        ('《三才发秘·详元堂爻位式》', 'original', 'shidianguji.com', '原典p040-p056，元堂定位图示', 5),
        ('《易冒》·气候卦', 'original', None, '节候卦权威引用源（总集:210-211）', 5),
        ('《易楔·卷四》杭辛斋', 'auxiliary', 'diancang.xyz/yixie/62097', '辅助佐证，卦气推演', 4),
        ('倪师《天纪》教材', 'auxiliary', '360doc.com', '三至尊算法补充定义', 4),
        ('识典古籍', 'original', 'shidianguji.com', '原典全文检索', 4),
        ('中华典籍网(diancang.xyz)', 'original', 'diancang.xyz', '原典数字化', 4),
        ('CTEXT 中国哲学书电子化计划', 'original', 'ctext.org', '原典繁体版', 4),
        ('维基百科·河图洛书', 'auxiliary', 'zh.wikipedia.org', '辅助参考', 3),
        ('知乎专栏', 'auxiliary', 'zhuanlan.zhihu.com', '现代整理版本', 2),
        ('百度百科', 'auxiliary', 'baike.baidu.com', '基础概念参考', 2),
        ('本地资料集', 'auxiliary', 'E:/顺天资料/shuantian资料', '汇总整理文档', 3),
    ]
    
    for src in sources:
        conn.execute(
            "INSERT OR IGNORE INTO sources (name, type, url, description, authority_score) VALUES (?, ?, ?, ?, ?)",
            src
        )
    conn.commit()
    print(f"✓ 已录入 {len(sources)} 个证据来源")

def insert_rules(conn):
    """录入14条规则"""
    rules = [
        ('rule_01', '天干数', '十天干→洛书九宫数映射', 
         "壬甲从乾数(6)，乙癸向坤求(2)，庚来震上立(3)，辛在巽方游(4)，丙于艮门立(8)，丁向兑家流(7)，戊从坎处出(1)，己以离为头(9)",
         'dict', '已验证', '★★★★★'),
        ('rule_02', '地支数', '十二地支→河图生成数映射',
         "亥子一六水，寅卯三八真，巳午二七火，申酉四九金，辰戌丑未土五十总生成",
         'dict', '已验证', '★★★★★'),
        ('rule_03', '取卦法', '天数÷25余数取上卦 / 地数÷30余数取下卦，阴阳命分上下',
         "一数坎兮二数坤，三震四巽数中分。五寄中宫六乾是，七兑八艮九离门。阳男阴女天数在上，阴男阳女天数在下",
         'function', '已验证', '★★★★★'),
        ('rule_04', '寄宫法', '遇5数按三元甲子寄宫（中五无位）',
         "上元甲子男寄艮女寄坤，中元阳男阴女寄艮阴男阳女寄坤，下元男寄离女寄兑",
         'conditional', '已验证', '★★★★★'),
        ('rule_05', '元堂', '出生时辰→先天卦中特定爻位',
         "起元堂诗：阴阳一二重而寄，三位虽重没寄宫。四五无重应有寄，纯爻男女不相同。含12x7定位表+p040-p056图示",
         'lookup_table', '已验证', '★★★★★'),
        ('rule_06', '换后天', '上下卦互换 + 元堂爻阴阳反转',
         "先天卦上卦作后天卦下卦、下卦作上卦，同时元堂爻阴阳互变",
         'function', '已验证', '★★★★★'),
        ('rule_07', '三至尊', '坎/屯/蹇先天卦，元堂在九五/上六时换卦法则不同',
         "三至尊卦九五或上六元堂爻逢异性不易位，逢同性则易位。含阴阳月/阴阳令四象分支",
         'special_branch', '已补全', '★★★★☆'),
        ('rule_08', '元气', '年干卦/年支卦与先天卦同或反',
         "凡人与元气相友者如木人得兑火人得坎土人得震金人得离水人得坤之类。命中有此主平生所为不如意",
         'hex_compare', '已验证', '★★★★★'),
        ('rule_09', '化工', '月柱卦与先天卦同或反',
         "坎卦自冬至十一月中以后至惊蛰终止。震卦自春分二月中以后至芒种终止。离卦自夏至五月中以后至白露终止。兑卦自秋分八月中以后至大雪终止",
         'hex_compare', '已验证', '★★★★★'),
        ('rule_10', '运行（大运）', '阳爻管9年，阴爻管6年，自元堂起向上',
         "阳爻九年，阴爻六年。假令同人六二爻为元堂，则一变为乾九二，再变为履六三...",
         'loop', '已验证', '★★★★★'),
        ('rule_11', '月卦（流月）', '单月变爻，双月变应爻，从节气起',
         "凡起月卦，就年卦中前一位起，单月变爻，双月变应爻",
         'yin_yang_month', '已验证', '★★★★★'),
        ('rule_12', '日卦（流日）', '月卦下一爻起5次变爻，每卦管6天，遇节气调整',
         "凡起日卦，就月卦中前一位起，每日变一爻",
         'solar_anchor', '已验证', '★★★★☆'),
        ('rule_13', '节候卦', '冬至起山雷颐六四，一日行一爻，六十卦周期',
         "冬至起山雷颐六四，一日行一爻，六十卦周期。各卦管六日七分，逢节气换卦",
         'sixty_cycle', '已验证', '★★★★★'),
        ('rule_14', '卦气', '卦值时令五行旺相判断',
         "卦气歌：关关初起立春前，小过蒙兮渐泰发...六十卦配二十四节气，每卦主六日七分",
         'wuxing旺相', '已验证', '★★★★★'),
    ]
    
    for rule in rules:
        conn.execute(
            "INSERT OR IGNORE INTO rules (rule_id, rule_name, description, core_algorithm, implementation_type, verification_status, evidence_rating) VALUES (?, ?, ?, ?, ?, ?, ?)",
            rule
        )
    conn.commit()
    print(f"✓ 已录入 {len(rules)} 条规则")

def insert_algorithms(conn):
    """录入算法规范"""
    algorithms = [
        ('rule_01', 'TIAN_GAN_NUM', json.dumps({
            '甲': 6, '壬': 6, '乙': 2, '癸': 2,
            '庚': 3, '辛': 4, '丙': 8, '丁': 7,
            '戊': 1, '己': 9
        }, ensure_ascii=False)),
        ('rule_02', 'DI_ZHI_NUM', json.dumps({
            '亥': [1, 6], '子': [1, 6],
            '寅': [3, 8], '卯': [3, 8],
            '巳': [2, 7], '午': [2, 7],
            '申': [4, 9], '酉': [4, 9],
            '辰': [5, 10], '戌': [5, 10],
            '丑': [5, 10], '未': [5, 10]
        }, ensure_ascii=False)),
        ('rule_03', 'GUA_NUMBER_MAP', json.dumps({
            1: '坎', 2: '坤', 3: '震', 4: '巽',
            6: '乾', 7: '兑', 8: '艮', 9: '离'
        }, ensure_ascii=False)),
        ('rule_05', 'YUANTANG_TABLE_DESC', '12时辰×7阳爻数定位表，含女生冬至后夏至前、男生夏至后冬至前特例'),
        ('rule_07', 'SANZHIZUN_RULES', json.dumps({
            'special_hexagrams': ['坎', '屯', '蹇'],
            'special_lines': [5, 6],
            'rule': '逢异性不易位，逢同性则易位'
        }, ensure_ascii=False)),
    ]
    
    for algo in algorithms:
        conn.execute(
            "INSERT INTO algorithm_specs (rule_id, spec_name, spec_content) VALUES (?, ?, ?)",
            algo
        )
    conn.commit()
    print("✓ 已录入算法规范")

def insert_verification_matrix(conn):
    """录入多维度验证矩阵"""
    matrix = [
        ('rule_01', '起例卷上', '壹风水', '维基百科', 'CTEXT', '百度百科', '四源一致'),
        ('rule_02', '起例卷上', '维基百科', '河洛精蕴', 'CTEXT', '百度百科', '四源一致'),
        ('rule_03', '起例卷上', '维基百科', '知乎专栏', 'CTEXT', '本地资料集', '有完整示例'),
        ('rule_04', '起例卷上', '维基百科', 'CTEXT', '知乎专栏', '本地资料集', '三源一致'),
        ('rule_05', '三才发秘', '识典古籍', '原典p040-056', '知乎专栏', '本地资料集', '有完整定位表'),
        ('rule_06', '起例卷上', '总集:47-58', 'CTEXT', '-', '本地资料集', '有完整示例'),
        ('rule_07', '起例卷上', '倪师天纪', '总集:69-80', 'CTEXT', '本地资料集', '已补全'),
        ('rule_08', '起例卷上', '卷下', 'CTEXT', '知乎专栏', '本地资料集', '有原则论述'),
        ('rule_09', '起例卷下', '原典', 'CTEXT', '知乎专栏', '本地资料集', '有季节对应'),
        ('rule_10', '起例卷上', 'CTEXT', '知乎专栏', '-', '本地资料集', '有完整示例'),
        ('rule_11', '起例卷下', '易楔卷四', 'CTEXT', '知乎专栏', '本地资料集', '有完整流程'),
        ('rule_12', '起例卷上', 'CTEXT', '知乎专栏', '-', '本地资料集', '有完整流程'),
        ('rule_13', '易冒', '起例卷下', 'CTEXT', '知乎专栏', '本地资料集', '有对应表'),
        ('rule_14', '起例卷下', '周易图', '易楔卷四', 'CTEXT', '本地资料集', '有流转原则'),
    ]
    
    for row in matrix:
        conn.execute(
            """INSERT INTO verification_matrix 
               (rule_id, source_1, source_2, source_3, source_4, source_5, cross_validation_result) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            row
        )
    conn.commit()
    print("✓ 已录入验证矩阵")

def insert_key_findings(conn):
    """录入关键发现"""
    findings = [
        ('壬=6：原典明文"壬甲从乾数（六）"，四源一致，聊天记录"壬=4"为错误', '起例卷上·天干取数'),
        ('寄宫法：三源一致确认三元甲子寄宫规则', '起例卷上·五数寄宫例'),
        ('元堂定位：有完整12种爻数定位表+p040–p056图示索引', '三才发秘·详元堂爻位式'),
        ('化工规则：季节-卦对应完整，"坎是冬之化工，离是夏之化工"', '起例卷下·论化工'),
        ('运行规则："阳爻九年，阴爻六年"明确，有完整示例', '起例卷上·小象运行例'),
        ('节候卦：有完整24节气-卦对应表', '易冒·气候卦'),
        ('卦气歌：有完整原典，可推导六十卦配节气', '起例卷下·卦气歌'),
        ('正对反对：有明确定义，反对卦为内外卦互换', '起例卷上·反对二体'),
        ('三至尊：原典有标题"三至尊换卦不同例"，算法由倪师教材补全', '倪师《天纪》教材'),
    ]
    
    for finding in findings:
        conn.execute(
            "INSERT INTO key_findings (finding_text, evidence_source) VALUES (?, ?)",
            finding
        )
    conn.commit()
    print("✓ 已录入关键发现")

def insert_hexagram_table(conn):
    """录入八卦表"""
    hexagrams = [
        (1, '坎', '☵', '☵', '坎', '水，陷，险'),
        (2, '坤', '☷', '☷', '坤', '地，顺，承'),
        (3, '震', '☳', '☳', '震', '雷，动，起'),
        (4, '巽', '☴', '☴', '巽', '风，入，柔'),
        (6, '乾', '☰', '☰', '乾', '天，健，首'),
        (7, '兑', '☱', '☱', '兑', '泽，悦，口'),
        (8, '艮', '☶', '☶', '艮', '山，止，稳'),
        (9, '离', '☲', '☲', '离', '火，丽，明'),
    ]
    
    for h in hexagrams:
        conn.execute(
            "INSERT OR IGNORE INTO hexagram_table (num, gua_name, gua_symbol, trigram_upper, trigram_lower, note) VALUES (?, ?, ?, ?, ?, ?)",
            h
        )
    conn.commit()
    print("✓ 已录入八卦表")

def main():
    """主函数"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    print(f"初始化数据库: {DB_PATH}")
    init_db(conn)
    insert_sources(conn)
    insert_rules(conn)
    insert_algorithms(conn)
    insert_verification_matrix(conn)
    insert_key_findings(conn)
    insert_hexagram_table(conn)
    
    # 验证统计
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM rules")
    rule_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM sources")
    source_count = cursor.fetchone()[0]
    cursor.execute("SELECT verification_status, COUNT(*) FROM rules GROUP BY verification_status")
    status_counts = dict(cursor.fetchall())
    
    print("\n" + "="*50)
    print(f"数据库录入完成")
    print(f"  - 规则数: {rule_count}")
    print(f"  - 来源数: {source_count}")
    print(f"  - 状态分布: {status_counts}")
    print(f"  - 数据库路径: {DB_PATH}")
    print("="*50)
    
    conn.close()

if __name__ == "__main__":
    main()
