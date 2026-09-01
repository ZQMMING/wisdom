"""
M5 API 集成测试 — 需要服务器已启动（run_server.py）
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "packages", "tongshu-calendar"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "packages", "tongshu-server"))

import pytest
import httpx

BASE = "http://localhost:8000"


@pytest.fixture(scope="module")
def client():
    return httpx.Client(base_url=BASE, timeout=10)


class TestHealth:
    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


class TestCalendar:
    def test_today(self, client):
        r = client.get("/calendar/today")
        assert r.status_code == 200
        data = r.json()
        assert "date" in data
        assert "lunar" in data
        assert "ganzhi" in data

    def test_specific_date(self, client):
        r = client.get("/calendar/daily", params={"date_str": "2026-08-13"})
        assert r.status_code == 200
        data = r.json()
        assert data["ganzhi"]["day"] == "己未"
        assert data["jianchu"] == "闭"

    def test_invalid_date(self, client):
        r = client.get("/calendar/daily", params={"date_str": "not-a-date"})
        assert r.status_code == 400


class TestDaily:
    def test_daily(self, client):
        r = client.get("/daily", params={"date_str": "2026-08-13"})
        assert r.status_code == 200
        data = r.json()
        assert len(data["moduls"]) == 5
        assert data["lunar"] == "丙午年 七月初一"
        assert data["disclaimer"].startswith("Der Inhalt")


class TestProfiles:
    def test_crud(self, client):
        # 创建
        r = client.post("/profiles", json={
            "device_id": "pytest-device",
            "birth_date": "1983-05-15",
            "birth_time": "14:30",
            "gender": "male",
            "city": "Shanghai",
        })
        assert r.status_code == 200
        profile_id = r.json()["id"]
        assert r.json()["yongshen"]["favorable"] == ["水", "金"]

        # 读取
        r = client.get(f"/profiles/{profile_id}")
        assert r.status_code == 200
        assert r.json()["birth_date"] == "1983-05-15"

        # 删除 (GDPR)
        r = client.delete(f"/profiles/{profile_id}")
        assert r.status_code == 200
        assert r.json()["status"] == "deleted"

        # 删除后 404
        r = client.get(f"/profiles/{profile_id}")
        assert r.status_code == 404

    def test_personalized_daily(self, client):
        """创建 profile 后获取个性化每日"""
        r = client.post("/profiles", json={
            "device_id": "pytest-personal",
            "birth_date": "1990-08-18",
            "birth_time": "06:00",
            "gender": "female",
            "city": "Beijing",
        })
        profile_id = r.json()["id"]

        r = client.get("/daily", params={"date_str": "2026-08-13", "profile_id": profile_id})
        assert r.status_code == 200
        data = r.json()
        assert data["personal"] is not None
        assert data["personal"]["match"] in ("harmonious", "clashing", "neutral")

        client.delete(f"/profiles/{profile_id}")


class TestNFC:
    def test_activate(self, client):
        import uuid
        r = client.post("/nfc/activate", json={"tag_id": f"TAG-PYTEST-{uuid.uuid4().hex[:8]}", "profile_id": "test"})
        assert r.status_code == 200
        assert r.json()["status"] == "activated"