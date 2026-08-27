import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
os.environ["TONGSHU_ALLOW_ZIWEI_STUB"] = "1"
for v in ("TONGSHU_LLM_API_KEY", "TONGSHU_LLM_BASE_URL", "TONGSHU_LLM_MODEL", "DEEPSEEK_API_KEY"):
    os.environ.pop(v, None)
from fastapi.testclient import TestClient
from tongshu.api.app import create_app

c = TestClient(create_app())
r = c.post("/v1/calculate", json={
    "birth_date": "1984-12-07", "hour": 16, "gender": "male",
    "theme": "WORK", "analysis_date": "2026-08-17",
    "timezone": "Asia/Shanghai", "location": "Beijing",
})
d = r.json()
print("cross_status:", d["cross_analysis"]["status"])
print("signals keys:", sorted(d["signals"].keys()))
for k, v in d["signals"].items():
    for s in v:
        print(f"  {k}: type={s.get('ontology_type')} polarity={s.get('polarity')} direction={s.get('direction')} rule_refs={s.get('rule_refs')}")
