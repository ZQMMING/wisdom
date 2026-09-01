# FastAPI 服务入口
import sys, os

# 包路径由 run_server.py 管理，此处不再重复添加

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, datetime
from typing import Optional

from tongshu.calendar.almanac import get_day_info
from tongshu.calendar.output import build_daily_output, get_current_solar_term
from tongshu.calendar.bazi import calculate_bazi, BirthInfo, BaZiChart
from tongshu.calendar.types import DailyOutput

from .database import get_db, init_db, Profile, DailyGuidance, NFCTag

app = FastAPI(title="TONGSHU API", version="0.1.0", docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import pathlib
from fastapi.responses import FileResponse

WEB_DIR = pathlib.Path(__file__).resolve().parents[4] / "packages" / "tongshu-web"

@app.get("/")
def serve_home():
    return FileResponse(str(WEB_DIR / "standalone.html"), media_type="text/html")

@app.get("/manifest.json")
def serve_manifest():
    return FileResponse(str(WEB_DIR / "public" / "manifest.json"), media_type="application/json")


@app.on_event("startup")
def startup():
    init_db()


# ============================================================
# Health
# ============================================================

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0", "time": datetime.utcnow().isoformat()}


# ============================================================
# Calendar
# ============================================================

@app.get("/calendar/today")
def calendar_today():
    """今日历法信息"""
    today = date.today()
    info = get_day_info(today)
    return {
        "date": str(today),
        "lunar": str(info.lunar),
        "ganzhi": info.day_ganzhi.full,
        "solar_term": info.solar_term or get_current_solar_term(today),
        "jianchu": info.jianchu,
        "xiusu": info.xiusu,
        "nayin": info.nayin,
        "zodiac_clash": info.zodiac_clash,
    }


@app.get("/calendar/daily")
def calendar_daily(date_str: str = Query(None, description="YYYY-MM-DD, 默认今天")):
    """指定日期历法信息"""
    try:
        d = date.fromisoformat(date_str) if date_str else date.today()
    except ValueError:
        raise HTTPException(400, "日期格式错误，请使用 YYYY-MM-DD")
    info = get_day_info(d)
    return {
        "date": str(d),
        "lunar": str(info.lunar),
        "ganzhi": {
            "year": info.year_ganzhi.full,
            "month": info.month_ganzhi.full,
            "day": info.day_ganzhi.full,
        },
        "solar_term": info.solar_term or get_current_solar_term(d),
        "jianchu": info.jianchu,
        "xiusu": info.xiusu,
        "nayin": info.nayin,
        "zodiac_clash": info.zodiac_clash,
        "peng_taboo": info.peng_taboo,
        "lucky_direction": info.lucky_direction,
        "hour_lucky": [{"hour": h["hour"], "zhi": h["zhi"], "lucky": h["lucky"]} for h in info.hour_lucky],
    }


# ============================================================
# Daily Guidance
# ============================================================

@app.get("/daily")
def daily_guidance(date_str: str = Query(None), profile_id: Optional[str] = Query(None)):
    """每日完整指引"""
    try:
        d = date.fromisoformat(date_str) if date_str else date.today()
    except ValueError:
        raise HTTPException(400, "日期格式错误")

    yongshen = None
    if profile_id:
        db = next(get_db())
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if profile and profile.yongshen_json:
            yongshen = profile.yongshen_json

    out = build_daily_output(d, yongshen)
    return {
        "date": out.date,
        "lunar": out.lunar,
        "ganzhi": out.ganzhi,
        "solar_term": out.solar_term,
        "moduls": out.moduls,
        "personal": out.personal,
        "disclaimer": out.disclaimer,
    }


# ============================================================
# Profiles
# ============================================================

from pydantic import BaseModel

class ProfileCreate(BaseModel):
    device_id: str
    birth_date: str
    birth_time: str
    gender: str
    latitude: float = 0
    longitude: float = 0
    city: str = ""


@app.post("/profiles")
def create_profile(data: ProfileCreate):
    """创建个人资料"""
    db = next(get_db())
    try:
        bd = date.fromisoformat(data.birth_date)
    except ValueError:
        raise HTTPException(400, "birth_date 格式错误")

    # 排盘
    birth = BirthInfo(date=bd, time=data.birth_time, gender=data.gender,
                      city=data.city, lat=data.latitude, lon=data.longitude)
    chart = calculate_bazi(birth)

    profile = Profile(
        device_id=data.device_id,
        birth_date=bd,
        birth_time=data.birth_time,
        gender=data.gender,
        latitude=data.latitude,
        longitude=data.longitude,
        city=data.city,
        chart_json={
            "pillars": {k: v.full for k, v in chart.pillars.items()},
            "day_master": chart.day_master,
            "five_elements": chart.five_elements,
            "strength": chart.day_master_strength,
        },
        yongshen_json=chart.yongshen,
    )
    db.add(profile)
    db.commit()
    return {"id": profile.id, "yongshen": chart.yongshen, "chart": chart.pillars}


@app.get("/profiles/{profile_id}")
def get_profile(profile_id: str):
    """读取个人资料"""
    db = next(get_db())
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(404, "Profile not found")
    return {
        "id": profile.id,
        "birth_date": str(profile.birth_date),
        "birth_time": profile.birth_time,
        "gender": profile.gender,
        "city": profile.city,
        "chart": profile.chart_json,
        "yongshen": profile.yongshen_json,
        "created_at": str(profile.created_at),
    }


@app.delete("/profiles/{profile_id}")
def delete_profile(profile_id: str):
    """删除个人资料（GDPR）"""
    db = next(get_db())
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(404, "Profile not found")
    db.delete(profile)
    db.commit()
    return {"status": "deleted"}


# ============================================================
# NFC
# ============================================================

class NFCActivate(BaseModel):
    tag_id: str
    profile_id: str


@app.post("/nfc/activate")
def activate_nfc(data: NFCActivate):
    """NFC 标签绑定"""
    db = next(get_db())
    tag = NFCTag(id=data.tag_id, profile_id=data.profile_id, activated_at=datetime.utcnow())
    db.add(tag)
    db.commit()
    return {"status": "activated", "tag_id": data.tag_id}


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)