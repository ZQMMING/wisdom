"""API smoke tests (FastAPI TestClient).

Exercises the public contract without starting a real server. These run with
the deterministic Stub renderer, so the reading assertions are byte-stable and
no real LLM calls are made. Because the env-gated factory flips to the real
LLM as soon as an API key exists (backend/.env), setUpClass clears the key
env vars before building the app — the live path is exercised separately by
scripts/verify_real_llm.py, not by this suite.

V3.6 coverage (Block B/C): /v1/* endpoints, §32 error envelope, trace id,
X-Process-Time-Ms / X-Render-Time-Ms scenario distinction, and deprecated-path
telemetry on /api/*.
"""

from __future__ import annotations
import os
import unittest
from contextlib import contextmanager

from fastapi.testclient import TestClient

from tongshu.api.app import create_app
from tongshu.api.tracing import reset_deprecated_counts

_LLM_ENV_VARS = (
    "TONGSHU_LLM_API_KEY",
    "TONGSHU_LLM_BASE_URL",
    "TONGSHU_LLM_MODEL",
    "DEEPSEEK_API_KEY",
)

# P0-2 Profile Gate:个人端点须提交 timezone+location(缺则 422 INSUFFICIENT_INPUT)。
# 这里补全 golden001 的出生时间政策字段,保持 daily-guide/calculate 200 语义不变。
_GOLDEN001_BODY = {
    "birth_date": "1984-12-07",
    "hour": 16,
    "gender": "male",
    "theme": "WORK",
    "analysis_date": "2026-08-17",
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


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with _env_without(*_LLM_ENV_VARS):
            os.environ["TONGSHU_AUTH_SECRET"] = "test-secret-for-unit-tests"
            cls.client = TestClient(create_app())

    def setUp(self):
        reset_deprecated_counts()

    # ------------------------------------------------------------------ #
    # Health
    # ------------------------------------------------------------------ #

    def test_health(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertEqual(d["status"], "ok")
        self.assertEqual(d["renderer"], "stub")
        self.assertEqual(d["model_id"], "stub")
        self.assertEqual(d["version"], "0.2.0")
        self.assertEqual(d["deprecated_calls"], 0)
        self.assertEqual(d["deprecated_calls_by_path"], {})
        # V3.6 §63 G*_block_rate telemetry (block E/F)
        self.assertEqual(d["gates_blocked"], 0)
        self.assertEqual(
            d["gates_blocked_by_gate"], {"G1": 0, "G2": 0, "G3": 0, "G4": 0}
        )

    # ------------------------------------------------------------------ #
    # /v1/daily-guide
    # ------------------------------------------------------------------ #

    def test_v1_daily_guide_golden001(self):
        r = self.client.post("/v1/daily-guide", json=_GOLDEN001_BODY)
        self.assertEqual(r.status_code, 200)
        d = r.json()
        # B-02 (User 终裁 2026-08-23): ALIGNED→PARTIAL。当时依赖 stub 引擎,
        # 阳历直送产生偏差, 观测为 PARTIAL。
        # B-03b 强制复核(2026-08-25): 真 iztro 修复(P0-B 闰月负月 + P0-C fallback)
        # 后, cross 正确计算为 ALIGNED, 与 GOLDEN-001.yaml 原始期望
        # (cross = SUPPORT x SUPPORT -> ALIGNED) 一致 → 改回 ALIGNED。
        self.assertEqual(d["cross_status"], "ALIGNED")
        self.assertEqual(d["source"], "llm_renderer")
        self.assertTrue(d["validation_passed"])
        self.assertEqual(d["signal_counts"]["BASELINE"], 4)
        self.assertTrue(d["rendered_text"])
        # observability headers
        self.assertTrue(r.headers.get("x-trace-id"))
        self.assertTrue(r.headers.get("x-process-time-ms"))
        self.assertTrue(r.headers.get("x-render-time-ms"))

    # ------------------------------------------------------------------ #
    # /v1/calculate (compute_only — no renderer)
    # ------------------------------------------------------------------ #

    def test_v1_calculate_compute_only(self):
        r = self.client.post("/v1/calculate", json=_GOLDEN001_BODY)
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertEqual(d["source"], "computed")
        self.assertEqual(d["canonical_id"][:3], "CC-")
        # B-02 (User 终裁 2026-08-23): ALIGNED→PARTIAL。
        # 反映农历修正后真实 cross 状态——阳历 1984-12-07 经 ZiweiAdapter
        # 转农历为甲子年闰十月十五(乙亥日)，非此前阳历直送(偏差51天)。
        # 钉因果（农历转换中间事实）:
        from lunar_python import Solar
        _lunar = Solar.fromYmd(1984, 12, 7).getLunar()
        self.assertEqual(_lunar.getYearInGanZhi(), "甲子")
        self.assertEqual(_lunar.getMonth(), -10)  # 闰十月
        self.assertEqual(_lunar.getDay(), 15)
        self.assertEqual(_lunar.getDayInGanZhi(), "乙亥")
        # B-02 (User 终裁 2026-08-23): ALIGNED→PARTIAL, 依赖 stub 引擎。
        # B-03b 强制复核(2026-08-25): 真 iztro 修复后 cross 正确计算为 ALIGNED,
        # 与 GOLDEN-001.yaml 原始期望一致 → 改回 ALIGNED。
        self.assertEqual(d["cross_analysis"]["status"], "ALIGNED")
        self.assertEqual(sorted(d["signals"]), ["BASELINE", "CYCLE_CONTEXT", "DAILY_ACTIVATION"])
        self.assertTrue(len(d["atomic_claims"]) >= 1)
        self.assertTrue(r.headers.get("x-trace-id"))
        self.assertTrue(r.headers.get("x-process-time-ms"))
        # compute_only MUST NOT emit the renderer-only header
        self.assertIsNone(r.headers.get("x-render-time-ms"))
        # V3.6 §6 meta is part of the computation SIR
        self.assertEqual(d["meta"]["schema_version"], "3.6.0")
        self.assertEqual(d["meta"]["document_id"], d["canonical_id"])

    # ------------------------------------------------------------------ #
    # /v1/today
    # ------------------------------------------------------------------ #

    def test_v1_today_computed_ganzhi(self):
        r = self.client.get("/v1/today", params={"date": "2026-08-17", "region": "Beijing"})
        self.assertEqual(r.status_code, 200)
        d = r.json()
        names = [g["name"] for g in d["ganZhi"]]
        self.assertEqual(names, ["丙午", "丙申", "癸亥"])
        self.assertEqual(d["weekday"], "星期一")
        self.assertEqual(d["day"], 17)
        self.assertEqual(d["provenance"]["ganZhi"], "computed")

    def test_v1_today_calendar_real_not_mock(self):
        """Calendar 去 Mock (V4.0.1 §7.4): 黄历字段实时计算,非静态文案."""
        r = self.client.get("/v1/today", params={"date": "2026-08-17", "region": "Beijing"})
        self.assertEqual(r.status_code, 200)
        d = r.json()
        cal = d["calendar"]
        self.assertEqual(d["lunarMonth"], "农历七月 · 孟秋")
        # 黄历字段来自实时计算(来源登记 lunar_python 1.4.8 + 日柱锚定)
        self.assertEqual(cal["jianchu"], "平")
        self.assertEqual(cal["zhishen"], "勾陈")
        self.assertEqual(cal["chong"], "巳")
        self.assertEqual(cal["sha"], "西")
        self.assertEqual(cal["day_ganzhi"], "癸亥")
        self.assertEqual(cal["sheng_xiao"], "马")
        self.assertEqual(cal["prev_jie_qi"]["name"], "立秋")
        self.assertTrue(cal["yi"])
        self.assertTrue(cal["ji"])
        self.assertEqual(
            set(cal["source_ids"]), {"lunar_python", "day_stem_branch_anchor", "ganzhi_daily_hexagram"}
        )
        # provenance 声明黄历已 computed
        self.assertIn("computed", d["provenance"]["lunarMonth/yi/ji/calendar"])

    # ------------------------------------------------------------------ #
    # Deprecated /api/* paths
    # ------------------------------------------------------------------ #

    def test_api_reading_legacy_deprecated_headers(self):
        r = self.client.post("/api/reading", json=_GOLDEN001_BODY)
        self.assertEqual(r.status_code, 200)  # status stays 200 on success
        self.assertEqual(r.headers.get("deprecation"), "true")
        self.assertEqual(r.headers.get("sunset"), "2027-08-18")
        self.assertTrue(r.headers.get("x-deprecated-warning"))

    def test_api_today_legacy_deprecated_headers(self):
        r = self.client.get("/api/today", params={"date": "2026-08-17"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers.get("deprecation"), "true")
        self.assertEqual(r.headers.get("sunset"), "2027-08-18")

    def test_deprecated_telemetry_counter(self):
        self.client.post("/api/reading", json=_GOLDEN001_BODY)
        self.client.get("/api/today")
        h = self.client.get("/health").json()
        self.assertEqual(h["deprecated_calls"], 2)
        self.assertEqual(h["deprecated_calls_by_path"], {"/api/reading": 1, "/api/today": 1})

    # ------------------------------------------------------------------ #
    # §32 error envelope
    # ------------------------------------------------------------------ #

    def _assert_error_envelope(self, r, status: int, code: str):
        self.assertEqual(r.status_code, status)
        err = r.json()["error"]
        self.assertEqual(
            sorted(err.keys()),
            ["code", "details", "message", "request_id", "trace_id"],
        )
        self.assertEqual(err["code"], code)
        self.assertTrue(err["request_id"].startswith("RR-"))
        self.assertTrue(err["trace_id"].startswith("TRACE-"))

    def test_error_invalid_field_400(self):
        r = self.client.post(
            "/v1/daily-guide",
            json={"birth_date": "1984-12-07", "hour": 25, "gender": "male"},
        )
        self._assert_error_envelope(r, 400, "INVALID_INPUT")

    def test_error_missing_critical_422(self):
        r = self.client.post("/v1/daily-guide", json={"birth_date": "1984-12-07", "gender": "male"})
        self._assert_error_envelope(r, 422, "INSUFFICIENT_INPUT")

    def test_error_bad_date_422(self):
        r = self.client.post(
            "/v1/daily-guide",
            json={"birth_date": "not-a-date", "hour": 16, "gender": "male"},
        )
        self._assert_error_envelope(r, 422, "INSUFFICIENT_INPUT")

    def test_error_envelope_has_trace_and_process_headers(self):
        r = self.client.post(
            "/v1/daily-guide",
            json={"birth_date": "not-a-date", "hour": 16, "gender": "male"},
        )
        self.assertTrue(r.headers.get("x-trace-id"))
        self.assertTrue(r.headers.get("x-process-time-ms"))

    # ------------------------------------------------------------------ #
    # Trace id propagation
    # ------------------------------------------------------------------ #

    def test_trace_id_echoes_client_header(self):
        r = self.client.post(
            "/v1/daily-guide", json=_GOLDEN001_BODY, headers={"X-Trace-ID": "TRACE-PM-0001"}
        )
        self.assertEqual(r.headers.get("x-trace-id"), "TRACE-PM-0001")

    def test_trace_id_generated_when_absent(self):
        r = self.client.get("/v1/today")
        self.assertTrue(r.headers.get("x-trace-id", "").startswith("TRACE-"))


if __name__ == "__main__":
    unittest.main()
