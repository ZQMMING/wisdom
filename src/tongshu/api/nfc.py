"""NFC Experience Layer API — DEPRECATED in V1

All NFC endpoints return 501 Not Implemented.
Reason: B-05 — /nfc/daily called non-existent methods (write_snapshot/calculate)
and would always 500. Authoritative baseline freezes NFC as entry-point only,
not part of the main pipeline. See DECISION_LOG_P0_DRAFT.md B-05.

Routes are preserved (not deleted) as a future recovery point.
"""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from typing import Optional

router = APIRouter(prefix="/nfc", tags=["NFC Experience"])

_NFC_UNAVAILABLE = JSONResponse(
    status_code=501,
    content={"detail": "NFC endpoints are not available in V1"},
)


@router.get("/daily")
def get_daily_tongshu(
    pendant_id: str = Query(..., description="NFC吊坠唯一标识"),
    date_str: Optional[str] = Query(None, description="查询日期 YYYY-MM-DD，默认今天"),
    gender: Optional[str] = Query(None, description="性别 male/female"),
    birth_date: Optional[str] = Query(None, description="出生日期 YYYY-MM-DD"),
    birth_time: Optional[str] = Query(None, description="出生时间 HH:MM"),
    timezone: Optional[str] = Query(None, description="IANA时区"),
    latitude: Optional[float] = Query(None, description="纬度"),
    longitude: Optional[float] = Query(None, description="经度"),
):
    """NFC 每日通书 — V1 不可用。"""
    return _NFC_UNAVAILABLE


@router.get("/relationship")
def get_relationship_timeline(
    pendant_id_a: str = Query(..., description="吊坠A ID"),
    pendant_id_b: str = Query(..., description="吊坠B ID"),
    date_str: Optional[str] = Query(None, description="查询日期"),
):
    """双人通书 — V1 不可用。"""
    return _NFC_UNAVAILABLE


@router.get("/state")
def get_daily_state(
    pendant_id: str = Query(..., description="吊坠ID"),
    date_str: Optional[str] = Query(None, description="查询日期"),
):
    """个人每日状态摘要 — V1 不可用。"""
    return _NFC_UNAVAILABLE
