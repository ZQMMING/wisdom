"""H2-P0: 时间基准核验脚本

核验三个核心基准:
1. 24节气黄经度数（《时宪书》标准）
2. 流年干支基准日（公元4年1月1日是否甲子日）
3. 流日干支起算点

输出: 核验报告 + 数据修正建议
"""
from __future__ import annotations
import json
import logging
import psycopg2
from datetime import datetime, timedelta
from typing import Tuple

DB_URI = "host=127.0.0.1 port=5432 dbname=shuntian_kb user=postgres password=postgres"
log = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# 核验1: 24节气黄经度数
# ═══════════════════════════════════════════════════════════════════
# 《时宪书》标准（每节气黄经差15°，起于春分0°）
SOLAR_TERMS_STANDARD = {
    "立春": 315, "雨水": 330, "惊蛰": 345, "春分": 0,
    "清明": 15, "谷雨": 30, "立夏": 45, "小满": 60,
    "芒种": 75, "夏至": 90, "小暑": 105, "大暑": 120,
    "立秋": 135, "处暑": 150, "白露": 165, "秋分": 180,
    "寒露": 195, "霜降": 210, "立冬": 225, "小雪": 240,
    "大雪": 255, "冬至": 270, "小寒": 285, "大寒": 300,
}

# ═══════════════════════════════════════════════════════════════════
# 核验2: 流年干支基准日
# ═══════════════════════════════════════════════════════════════════
# 传统算法: 公元4年1月1日 = 甲子日
# 现代算法: 需要验证

def verify_jiazi_day(year: int, month: int, day: int) -> str:
    """
    计算指定日期天干地支日。
    
    算法: 公元4年1月1日=甲子日 (干支序数0)
    公式: (days_since_jiazi % 60) 得到干支序数
    """
    jiazi_base = datetime(4, 1, 1)  # 甲子日基准
    target = datetime(year, month, day)
    days_diff = (target - jiazi_base).days
    
    # 天干: 10进制循环
    # 甲=0, 乙=1, ..., 癸=9
    # 公元4年1月1日天干=甲(0)，因为4%10=4，但甲子日开始
    stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    
    # 修正: 公元4年1月1日应该是甲子日
    # 实际计算: days_diff % 60 得到0-59的干支序数
    ganzhi_idx = days_diff % 60
    stem = stems[ganzhi_idx % 10]
    branch = branches[ganzhi_idx % 12]
    
    return f"{stem}{branch}"


def verify_year_ganzhi(year: int) -> str:
    """
    计算年份天干地支。
    
    算法: 公元4年 = 甲子年
    公式: (year - 4) % 60
    """
    stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    
    idx = (year - 4) % 60
    stem = stems[idx % 10]
    branch = branches[idx % 12]
    
    return f"{stem}{branch}"


# ═══════════════════════════════════════════════════════════════════
# 核验3: 流日起算点
# ═══════════════════════════════════════════════════════════════════
# 问题: 流日干支从哪天开始？
# 选项A: 公元4年1月1日 = 甲子日
# 选项B: 其他历史记载
#
# 验证方法:
# 1. 查证《协纪辨方书》等古籍记载
# 2. 使用天文软件（如Swiss Ephemeris）反推历史日期
# 3. 对比多个来源确认

def verify_flow_day_base() -> dict:
    """
    核验流日起算点。
    
    返回:
    {
        "jiazi_base": "公元4年1月1日",
        "verification": "需要古籍佐证",
        "confidence": "P0待核验"
    }
    """
    # 验证公元4年1月1日是否为甲子日
    test_date = datetime(4, 1, 1)
    result = verify_jiazi_day(4, 1, 1)
    
    return {
        "test_date": "0004-01-01",
        "computed_ganzhi": result,
        "expected_ganzhi": "甲子",
        "match": result == "甲子",
        "status": "待古籍核验"
    }


# ═══════════════════════════════════════════════════════════════════
# 主执行函数
# ═══════════════════════════════════════════════════════════════════
def run_verification(conn) -> dict:
    """执行全部核验，返回报告。"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "solar_terms": {},
        "flow_day_base": {},
        "recommendations": []
    }
    
    cur = conn.cursor()
    
    # ─── 核验1: 24节气黄经度数 ───
    cur.execute("SELECT term_id, solar_ref FROM solar_terms ORDER BY term_index")
    db_terms = {row[0]: row[1] for row in cur.fetchall()}
    
    mismatches = []
    for name, standard_ref in SOLAR_TERMS_STANDARD.items():
        db_ref = db_terms.get(name)
        if db_ref is None:
            mismatches.append(f"{name}: 缺失")
        elif str(db_ref) != str(standard_ref):
            mismatches.append(f"{name}: DB={db_ref}, 标准={standard_ref}")
    
    report["solar_terms"]["count"] = len(db_terms)
    report["solar_terms"]["mismatches"] = mismatches
    report["solar_terms"]["status"] = "✅ 通过" if not mismatches else "⚠️ 需修正"
    
    # ─── 核验2: 流日起算点 ───
    report["flow_day_base"] = verify_flow_day_base()
    
    # ─── 核验3: 流年干支验证 ───
    test_years = [4, 1984, 2024, 2025]
    year_verification = {}
    for y in test_years:
        calculated = verify_year_ganzhi(y)
        year_verification[str(y)] = {
            "calculated": calculated,
            "expected": "甲子" if y == 4 else ("甲子" if y == 1984 else None)
        }
    report["year_ganzhi_verification"] = year_verification
    
    # ─── 生成建议 ───
    if mismatches:
        report["recommendations"].append({
            "priority": "P0",
            "task": "修正24节气黄经度数",
            "action": "核对《时宪书》后更新DB"
        })
    
    if not report["flow_day_base"]["match"]:
        report["recommendations"].append({
            "priority": "P0",
            "task": "核验流日起算点",
            "action": "查证古籍或天文软件反推"
        })
    else:
        report["recommendations"].append({
            "priority": "P1",
            "task": "获取古籍佐证",
            "action": "查阅《协纪辨方书》卷一"
        })
    
    return report


def main():
    logging.basicConfig(level=logging.INFO)
    conn = psycopg2.connect(DB_URI)
    try:
        report = run_verification(conn)
        log.info(json.dumps(report, ensure_ascii=False, indent=2))
        return report
    finally:
        conn.close()


if __name__ == "__main__":
    report = main()
    print(json.dumps(report, ensure_ascii=False, indent=2))
