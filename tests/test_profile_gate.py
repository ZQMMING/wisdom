"""Profile Activation Gate tests (P0-2 §3.3 + 01_PROFILE_CONTRACT.md §1.3).

Covers:
  - resolve_profile 三态: NONE / VALID / INSUFFICIENT(拒绝)
  - gender REQUIRED (Profile Contract §1.2 forbidden_default=true):
      * 缺失 → 422 INSUFFICIENT_INPUT + missing_fields=["gender", ...]
      * 非法值 ("M"/"F"/"x") → 400 INVALID_INPUT
      * 显式 "male"/"female" → 通过
  - 400 mapping: unknown location / bad timezone / lunar & invalid calendar
  - API gate: personal endpoints 缺 gender/timezone|location → 422 + missing_fields;
    full profile → 200; location 单独提交 → timezone 派生(D4)
  - POST /v1/profile: §32 校验 + 标准化回执(无持久化)
"""

from __future__ import annotations
import os
import unittest
from contextlib import contextmanager

from fastapi.testclient import TestClient

from tongshu.api.app import create_app
from tongshu.api.errors import OTCGApiError
from tongshu.api.profile import (
    ProfileStatus,
    PROFILE_REQUIRED_FIELDS,
    require_gender,
    resolve_profile,
)
from tongshu.engines.time_resolver import TimeResolver

_LLM_ENV_VARS = (
    "TONGSHU_LLM_API_KEY",
    "TONGSHU_LLM_BASE_URL",
    "TONGSHU_LLM_MODEL",
    "DEEPSEEK_API_KEY",
)

_RESOLVER = TimeResolver()

# Phase 1 / Gender 重构:gender 编码统一为 male/female(Profile Contract §1.2)
_FULL_PROFILE = {
    "birth_date": "1984-12-07",
    "hour": 16,
    "gender": "male",
    "theme": "WORK",
    "analysis_date": "2026-08-17",
    "timezone": "Asia/Shanghai",
    "location": "Beijing",
}

# /v1/profile 完整请求体(包含嵌套 birth_time)
_FULL_PROFILE_REQUEST = {
    "birth_date": "1984-12-07",
    "birth_time": {"hour": 16, "minute": 30},
    "gender": "male",
    "timezone": "Asia/Shanghai",
    "location": "Beijing",
}


@contextmanager
def _env_without(*names: str):
    saved = {n: os.environ.pop(n, None) for n in names}
    try:
        yield
    finally:
        for n, v in saved.items():
            if v is not None:
                os.environ[n] = v


def _extract_field_names(detail: dict) -> str | None:
    """兼容两种 details 格式:
    1. OTCGApiError: {"field": "gender", "reason": "missing"} → "gender"
    2. Pydantic validation: {"loc": ["gender"], "msg": "...", "type": "..."} → "gender"
    """
    if "field" in detail:
        return detail["field"]
    if "loc" in detail:
        loc = detail["loc"]
        if isinstance(loc, list) and loc:
            return str(loc[-1])
    return None


class TestResolveProfile(unittest.TestCase):
    """State machine unit tests(零 HTTP)。"""

    def test_none_when_no_profile_fields(self):
        """NONE: 所有字段都为 None → NONE 状态(连拒绝都不算)。"""
        st = resolve_profile(
            timezone=None, calendar_system=None, location=None,
            gender=None, time_resolver=_RESOLVER,
        )
        self.assertEqual(st.status, ProfileStatus.NONE)
        self.assertEqual(st.missing_fields, [])

    def test_location_alone_derives_timezone(self):
        """location 单字段提交 → timezone 由 location 派生 → VALID。"""
        st = resolve_profile(
            timezone=None, calendar_system=None, location="北京",
            gender="male", time_resolver=_RESOLVER,
        )
        self.assertEqual(st.status, ProfileStatus.VALID)
        self.assertEqual(st.timezone, "Asia/Shanghai")
        self.assertEqual(st.calendar_system, "solar")
        self.assertEqual(st.gender, "male")

    def test_valid_and_ready_alias(self):
        """VALID 与 PROFILE_CALCULATION_READY 视为同一语义(V4.0.1 §3.3 兼容)。"""
        st = resolve_profile(
            timezone="Asia/Shanghai", calendar_system=None, location="Beijing",
            gender="female", time_resolver=_RESOLVER,
        )
        self.assertEqual(st.status, ProfileStatus.VALID)
        self.assertTrue(ProfileStatus.is_valid(st.status))

    def test_timezone_without_location_insufficient(self):
        """仅提交 timezone(缺 location/gender) → INSUFFICIENT + missing_fields。"""
        st = resolve_profile(
            timezone="Asia/Shanghai", calendar_system=None, location=None,
            gender=None, time_resolver=_RESOLVER,
        )
        self.assertEqual(st.status, ProfileStatus.INSUFFICIENT)
        # 缺失字段按 §1.2 顺序:gender 在前(缺失 gender 不允许默认值)
        self.assertIn("gender", st.missing_fields)
        self.assertIn("location", st.missing_fields)

    def test_gender_missing_returns_insufficient(self):
        """§1.2 红线:gender 缺失 → INSUFFICIENT + missing_fields=["gender"]。"""
        st = resolve_profile(
            timezone="Asia/Shanghai", calendar_system=None, location="Beijing",
            gender=None, time_resolver=_RESOLVER,
        )
        self.assertEqual(st.status, ProfileStatus.INSUFFICIENT)
        self.assertIn("gender", st.missing_fields)

    def test_gender_invalid_value_400(self):
        """§1.2 校验:gender 非法值("M"/"F"/"x" 等)→ 400 INVALID_INPUT。"""
        for bad in ("M", "F", "x", "Male", "male ", "男"):
            with self.assertRaises(OTCGApiError) as ctx:
                resolve_profile(
                    timezone="Asia/Shanghai", calendar_system=None, location="Beijing",
                    gender=bad, time_resolver=_RESOLVER,
                )
            self.assertEqual(ctx.exception.status_code, 400, f"gender={bad!r}")
            self.assertEqual(ctx.exception.code.value, "INVALID_INPUT")

    def test_unknown_location_400(self):
        with self.assertRaises(OTCGApiError) as ctx:
            resolve_profile(
                timezone=None, calendar_system=None, location="Atlantis",
                gender="male", time_resolver=_RESOLVER,
            )
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertEqual(ctx.exception.code.value, "INVALID_INPUT")

    def test_bad_timezone_400(self):
        with self.assertRaises(OTCGApiError):
            resolve_profile(
                timezone="Bad/Zone", calendar_system=None, location="北京",
                gender="male", time_resolver=_RESOLVER,
            )

    def test_lunar_unsupported_400(self):
        with self.assertRaises(OTCGApiError) as ctx:
            resolve_profile(
                timezone=None, calendar_system="lunar", location="北京",
                gender="male", time_resolver=_RESOLVER,
            )
        self.assertEqual(ctx.exception.status_code, 400)

    def test_invalid_calendar_system_400(self):
        with self.assertRaises(OTCGApiError):
            resolve_profile(
                timezone=None, calendar_system="mars", location="北京",
                gender="male", time_resolver=_RESOLVER,
            )

    def test_full_ready(self):
        st = resolve_profile(
            timezone="Asia/Shanghai", calendar_system=None, location="Beijing",
            gender="male", time_resolver=_RESOLVER,
        )
        self.assertEqual(st.status, ProfileStatus.VALID)
        self.assertEqual(st.timezone, "Asia/Shanghai")
        self.assertEqual(st.gender, "male")

    def test_missing_fields_ordered_by_contract(self):
        """missing_fields 顺序遵循 PROFILE_REQUIRED_FIELDS(§1.2 契约顺序)。

        仅提交 timezone（gender/location 缺失）→ 两个必填字段同时缺失。
        如果仅提交 location，则 timezone 会被 D4 机制派生，不会出现在 missing_fields 中。
        """
        st = resolve_profile(
            timezone="Asia/Shanghai", calendar_system=None, location=None,
            gender=None, time_resolver=_RESOLVER,
        )
        self.assertEqual(st.status, ProfileStatus.INSUFFICIENT)
        self.assertIn("gender", st.missing_fields)
        self.assertIn("location", st.missing_fields)
        # §1.2 顺序:gender 必填字段出现在 location 必填字段之前
        idx_gender = PROFILE_REQUIRED_FIELDS.index("gender")
        idx_location = PROFILE_REQUIRED_FIELDS.index("location")
        self.assertLess(idx_gender, idx_location)

    def test_location_only_derives_timezone(self):
        """仅提交 location → timezone 由 D4 派生 → INSUFFICIENT 仅是因为 gender 缺失。"""
        st = resolve_profile(
            timezone=None, calendar_system=None, location="Beijing",
            gender=None, time_resolver=_RESOLVER,
        )
        self.assertEqual(st.status, ProfileStatus.INSUFFICIENT)
        # timezone 已被 D4 派生，不会出现在 missing_fields 中
        self.assertNotIn("timezone", st.missing_fields)
        self.assertIn("gender", st.missing_fields)
        self.assertEqual(st.timezone, "Asia/Shanghai")  # D4 派生生效


class TestRequireGender(unittest.TestCase):
    """require_gender 独立校验函数。"""

    def test_valid_male(self):
        self.assertEqual(require_gender("male"), "male")

    def test_valid_female(self):
        self.assertEqual(require_gender("female"), "female")

    def test_none_raises_422(self):
        with self.assertRaises(OTCGApiError) as ctx:
            require_gender(None)
        self.assertEqual(ctx.exception.status_code, 422)
        self.assertEqual(ctx.exception.code.value, "INSUFFICIENT_INPUT")
        details = ctx.exception.details
        self.assertEqual(details[0]["field"], "gender")
        self.assertEqual(details[0]["reason"], "missing")

    def test_invalid_value_raises_400(self):
        with self.assertRaises(OTCGApiError) as ctx:
            require_gender("M")
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertEqual(ctx.exception.code.value, "INVALID_INPUT")


class TestProfileAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with _env_without(*_LLM_ENV_VARS):
            cls.client = TestClient(create_app())

    def _err(self, r) -> dict:
        return r.json()["error"]

    def _missing_fields(self, r) -> list:
        """提取 missing_fields 列表,兼容两种 details 格式。"""
        out = []
        for d in self._err(r)["details"]:
            name = _extract_field_names(d)
            if name:
                out.append(name)
        return out

    # ------------------------------------------------------------------ #
    # POST /v1/profile
    # ------------------------------------------------------------------ #

    def test_profile_full_receipt(self):
        """完整 profile → 200,profile_status=PROFILE_CALCULATION_READY(向后兼容)。"""
        r = self.client.post("/v1/profile", json=_FULL_PROFILE_REQUEST)
        self.assertEqual(r.status_code, 200)
        d = r.json()
        # Phase 1 / 代契§1.3: VALID 或兼容字符串 PROFILE_CALCULATION_READY
        self.assertIn(d["profile_status"], ("VALID", "PROFILE_CALCULATION_READY"))
        self.assertEqual(d["location"], "CN_BEIJING")
        self.assertEqual(d["timezone"], "Asia/Shanghai")
        rtp = d["resolved_time_policy"]
        self.assertEqual(rtp["day_boundary"], "23:00")
        self.assertEqual(rtp["birth_effective"]["date"], "1984-12-07")
        # minute 已提供 → 无时辰中点假设
        self.assertEqual(rtp["warnings"], [])

    def test_profile_location_derives_timezone(self):
        r = self.client.post("/v1/profile", json={
            "birth_date": "1984-12-07",
            "birth_time": {"hour": 16},
            "gender": "male",
            "location": "Berlin",
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["timezone"], "Europe/Berlin")

    def test_profile_missing_location_422(self):
        """缺 location → 422 + missing_fields 包含 location。"""
        r = self.client.post("/v1/profile", json={
            "birth_date": "1984-12-07",
            "birth_time": {"hour": 16},
            "gender": "male",
            "timezone": "Asia/Shanghai",
        })
        self.assertEqual(r.status_code, 422)
        self.assertEqual(self._err(r)["code"], "INSUFFICIENT_INPUT")
        self.assertIn("location", self._missing_fields(r))

    def test_profile_missing_gender_422(self):
        """Phase 1 / Gender 红线:gender 缺失 → 422 INSUFFICIENT_INPUT + missing_fields=['gender']。

        缺失触发 Pydantic 验证错误 → api/errors.py 映射为 422 INSUFFICIENT_INPUT。
        """
        r = self.client.post("/v1/profile", json={
            "birth_date": "1984-12-07",
            "birth_time": {"hour": 16},
            # 注意: gender 未提供
            "timezone": "Asia/Shanghai",
            "location": "Beijing",
        })
        self.assertEqual(r.status_code, 422)
        err = self._err(r)
        self.assertEqual(err["code"], "INSUFFICIENT_INPUT")
        self.assertIn("gender", self._missing_fields(r))

    def test_profile_invalid_gender_400(self):
        """gender 非法值 → 400 INVALID_INPUT(Pydantic pattern 拦截)。"""
        r = self.client.post("/v1/profile", json={
            "birth_date": "1984-12-07",
            "birth_time": {"hour": 16},
            "gender": "M",  # 非法: 必须 male/female
            "timezone": "Asia/Shanghai",
            "location": "Beijing",
        })
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self._err(r)["code"], "INVALID_INPUT")

    def test_profile_unknown_location_400(self):
        r = self.client.post("/v1/profile", json={
            "birth_date": "1984-12-07",
            "birth_time": {"hour": 16},
            "gender": "male",
            "location": "Atlantis",
        })
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self._err(r)["code"], "INVALID_INPUT")

    def test_profile_bad_timezone_400(self):
        r = self.client.post("/v1/profile", json={
            "birth_date": "1984-12-07",
            "birth_time": {"hour": 16},
            "gender": "male",
            "timezone": "Bad/Zone",
            "location": "Beijing",
        })
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self._err(r)["code"], "INVALID_INPUT")

    def test_profile_lunar_400(self):
        r = self.client.post("/v1/profile", json={
            "birth_date": "1984-12-07",
            "birth_time": {"hour": 16},
            "gender": "male",
            "calendar_system": "lunar",
            "location": "Beijing",
        })
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self._err(r)["code"], "INVALID_INPUT")

    # ------------------------------------------------------------------ #
    # 422 Gate on personal endpoints
    # ------------------------------------------------------------------ #

    def test_daily_guide_full_profile_200(self):
        r = self.client.post("/v1/daily-guide", json=_FULL_PROFILE)
        self.assertEqual(r.status_code, 200)

    def test_daily_guide_missing_gender_422(self):
        """Phase 1 / Gender 红线:daily-guide 缺 gender → 422。

        Pydantic schema 校验 gender REQUIRED,缺失触发验证错误,
        api/errors.py 映射为 422 INSUFFICIENT_INPUT(gender 在 _CRITICAL_FIELDS)。
        """
        r = self.client.post("/v1/daily-guide", json={
            "birth_date": "1984-12-07",
            "hour": 16,
            # gender 未提供
            "theme": "WORK",
            "timezone": "Asia/Shanghai",
            "location": "Beijing",
        })
        self.assertEqual(r.status_code, 422)
        self.assertEqual(self._err(r)["code"], "INSUFFICIENT_INPUT")
        self.assertIn("gender", self._missing_fields(r))

    def test_daily_guide_invalid_gender_400(self):
        """daily-guide gender 非法值 → 400 INVALID_INPUT。"""
        r = self.client.post("/v1/daily-guide", json={
            "birth_date": "1984-12-07",
            "hour": 16,
            "gender": "F",  # 非法:必须 male/female
            "theme": "WORK",
            "timezone": "Asia/Shanghai",
            "location": "Beijing",
        })
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self._err(r)["code"], "INVALID_INPUT")

    def test_daily_guide_missing_time_policy_422(self):
        r = self.client.post("/v1/daily-guide", json={
            "birth_date": "1984-12-07", "hour": 16, "gender": "male", "theme": "WORK",
        })
        self.assertEqual(r.status_code, 422)
        self.assertEqual(self._err(r)["code"], "INSUFFICIENT_INPUT")
        fields = set(self._missing_fields(r))
        self.assertTrue({"timezone", "location"} <= fields)

    def test_daily_guide_location_alone_derives_timezone_200(self):
        r = self.client.post("/v1/daily-guide", json={
            "birth_date": "1984-12-07", "hour": 16, "gender": "male", "theme": "WORK",
            "location": "北京",
        })
        self.assertEqual(r.status_code, 200)

    def test_daily_guide_unknown_location_400(self):
        r = self.client.post("/v1/daily-guide", json={
            "birth_date": "1984-12-07", "hour": 16, "gender": "male", "theme": "WORK",
            "location": "Atlantis",
        })
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self._err(r)["code"], "INVALID_INPUT")

    def test_daily_guide_bad_timezone_400(self):
        r = self.client.post("/v1/daily-guide", json={
            "birth_date": "1984-12-07", "hour": 16, "gender": "male", "theme": "WORK",
            "timezone": "Bad/Zone", "location": "Beijing",
        })
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self._err(r)["code"], "INVALID_INPUT")

    def test_calculate_full_profile_200(self):
        r = self.client.post("/v1/calculate", json=_FULL_PROFILE)
        self.assertEqual(r.status_code, 200)

    def test_calculate_missing_gender_422(self):
        """calculate 端点缺 gender → 422。"""
        r = self.client.post("/v1/calculate", json={
            "birth_date": "1984-12-07",
            "hour": 16,
            "theme": "WORK",
            "timezone": "Asia/Shanghai",
            "location": "Beijing",
        })
        self.assertEqual(r.status_code, 422)
        self.assertEqual(self._err(r)["code"], "INSUFFICIENT_INPUT")
        self.assertIn("gender", self._missing_fields(r))

    def test_calculate_missing_location_422(self):
        r = self.client.post("/v1/calculate", json={
            "birth_date": "1984-12-07", "hour": 16, "gender": "male", "theme": "WORK",
            "timezone": "Asia/Shanghai",
        })
        self.assertEqual(r.status_code, 422)
        self.assertEqual(self._err(r)["code"], "INSUFFICIENT_INPUT")

    def test_legacy_reading_full_profile_200(self):
        r = self.client.post("/api/reading", json=_FULL_PROFILE)
        self.assertEqual(r.status_code, 200)

    def test_legacy_reading_missing_gender_422(self):
        """deprecated /api/reading 也按 Gender 红线拦截。"""
        r = self.client.post("/api/reading", json={
            "birth_date": "1984-12-07",
            "hour": 16,
            "theme": "WORK",
            "timezone": "Asia/Shanghai",
            "location": "Beijing",
        })
        self.assertEqual(r.status_code, 422)
        self.assertEqual(self._err(r)["code"], "INSUFFICIENT_INPUT")
        self.assertIn("gender", self._missing_fields(r))

    def test_legacy_reading_missing_location_422(self):
        r = self.client.post("/api/reading", json={
            "birth_date": "1984-12-07", "hour": 16, "gender": "male", "theme": "WORK",
        })
        self.assertEqual(r.status_code, 422)
        self.assertEqual(self._err(r)["code"], "INSUFFICIENT_INPUT")


class TestProfileGateThreeState(unittest.TestCase):
    """Profile Gate 三态完整性测试(01_PROFILE_CONTRACT.md §1.3)。

    验证 NONE / INSUFFICIENT / VALID 三态均可通过 HTTP 接口触发。
    """

    @classmethod
    def setUpClass(cls):
        with _env_without(*_LLM_ENV_VARS):
            cls.client = TestClient(create_app())

    def _err(self, r) -> dict:
        return r.json()["error"]

    def _missing_fields(self, r) -> list:
        out = []
        for d in self._err(r)["details"]:
            name = _extract_field_names(d)
            if name:
                out.append(name)
        return out

    def test_state_none_empty_body(self):
        """NONE: 整个 request body 空 → Pydantic 必填字段校验失败 → 422 INSUFFICIENT_INPUT
        (真正的 NONE 仅在无任何 profile 时由 resolve_profile() 内部触发)。"""
        r = self.client.post("/v1/profile", json={})
        self.assertEqual(r.status_code, 422)

    def test_state_valid_full_profile(self):
        """VALID: 完整 profile → 200 + profile_status=PROFILE_CALCULATION_READY。"""
        r = self.client.post("/v1/profile", json=_FULL_PROFILE_REQUEST)
        self.assertEqual(r.status_code, 200)
        # Phase 1 / 代契§1.3: VALID 或兼容字符串
        self.assertIn(r.json()["profile_status"], ("VALID", "PROFILE_CALCULATION_READY"))

    def test_state_insufficient_missing_gender(self):
        """INSUFFICIENT: location/timezone 已交,但 gender 缺失 → 422 + missing_fields 包含 gender。"""
        r = self.client.post("/v1/profile", json={
            "birth_date": "1984-12-07",
            "birth_time": {"hour": 16},
            "timezone": "Asia/Shanghai",
            "location": "Beijing",
            # gender 缺失
        })
        self.assertEqual(r.status_code, 422)
        self.assertEqual(self._err(r)["code"], "INSUFFICIENT_INPUT")
        missing = self._missing_fields(r)
        self.assertIn("gender", missing)

    def test_state_insufficient_missing_location(self):
        """INSUFFICIENT: gender 已交,但 location 缺失 → 422 + missing_fields 包含 location。"""
        r = self.client.post("/v1/profile", json={
            "birth_date": "1984-12-07",
            "birth_time": {"hour": 16},
            "gender": "female",
            "timezone": "Asia/Shanghai",
            # location 缺失
        })
        self.assertEqual(r.status_code, 422)
        self.assertEqual(self._err(r)["code"], "INSUFFICIENT_INPUT")
        missing = self._missing_fields(r)
        self.assertIn("location", missing)


if __name__ == "__main__":
    unittest.main()
