"""快速验证JPL集成"""
import sys
sys.path.insert(0, '/d/today/backend/src')
from tongshu.engines.astronomy.ephemeris import JPLEphemerisEngine
from datetime import datetime

engine = JPLEphemerisEngine()
result = engine.calculate_solar_longitude(datetime(2026, 8, 21, 12, 0, 0), "Asia/Shanghai")
print(f"太阳黄经: {result.solar_longitude}°")
print(f"精度: ±{result.accuracy_seconds}秒")
print("✅ JPL集成正常")