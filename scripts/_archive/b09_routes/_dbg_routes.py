import sys, os
sys.path.insert(0, r"D:\today\backend\src")
os.environ["TONGSHU_AUTH_SECRET"] = "test-secret-" + "x" * 32
os.environ["TONGSHU_ALLOW_ZIWEI_STUB"] = "1"
from tongshu.api.app import create_app
from fastapi.testclient import TestClient
app = create_app()
print("Routes:")
for route in app.routes:
    p = getattr(route, "path", "")
    print(f"  {p}")
print("---")
client = TestClient(app)
r = client.get("/nfc/daily", params={"pendant_id": "p-1"})
print("Status:", r.status_code)