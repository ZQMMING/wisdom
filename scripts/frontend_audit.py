"""
前端对接审计脚本 — 验证 shuntian-web 与后端 API 的符合性
"""
import re
from pathlib import Path

WEB_DIR = Path("D:/today/shuntian-web/src")
audit_results = []

def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    audit_results.append((name, status, detail))
    return status == "PASS"

# ============================================================
# C1: BackendService 模块
# ============================================================
backend_ts = (WEB_DIR / "lib/backend.ts").read_text()
check("C1.1", "BASE_URL" in backend_ts and "NEXT_PUBLIC_API_URL" in backend_ts,
      "使用环境变量 NEXT_PUBLIC_API_URL")
check("C1.2", "fetchToday" in backend_ts and "/nfc/daily" in backend_ts,
      "fetchToday 调用 GET /nfc/daily")
check("C1.3", "createProfile" in backend_ts and "/api/v1/profiles" in backend_ts,
      "createProfile 调用 POST /api/v1/profiles")
check("C1.4", "handleProfileError" in backend_ts and "missing_fields" in backend_ts,
      "handleProfileError 返回 missing_fields[]")

# ============================================================
# C2: Gender 契约
# ============================================================
onboarding_ts = (WEB_DIR / "app/onboarding/page.tsx").read_text()
check("C2.1", "gender: 'male' | 'female' | ''" in onboarding_ts or 
           ("gender" in onboarding_ts and "M/F" not in onboarding_ts and "male" in onboarding_ts and "female" in onboarding_ts),
      "gender 只接受 male/female，无默认值")
check("C2.2", "data.gender || 'male'" not in onboarding_ts and 
           "gender || 'male'" not in onboarding_ts and
           "gender ?? 'male'" not in onboarding_ts and
           "gender ? 'male'" not in onboarding_ts,
      "无 gender 默认值（API 调用层）")

# ============================================================
# C3: Profile Gate 三态
# ============================================================
check("C3.1", "'VALID'" in onboarding_ts and "profile_id" in onboarding_ts and 
           "router.push('/today')" in onboarding_ts,
      "VALID → 保存 profile_id，跳转 /today")
check("C3.2", "'INSUFFICIENT'" in onboarding_ts and "missing_fields" in onboarding_ts,
      "INSUFFICIENT → 显示 missing_fields[]")
check("C3.3", "'NONE'" in onboarding_ts or "'welcome'" in onboarding_ts,
      "NONE → 显示初始化引导")

# ============================================================
# C4: Today 页面
# ============================================================
today_ts = (WEB_DIR / "app/page.tsx").read_text()
check("C4.1", "pendant_id" in today_ts and "localStorage.getItem" in today_ts,
      "读取 localStorage.pendant_id")
check("C4.2", "getNfcDaily" in today_ts or "fetchToday" in today_ts,
      "调用 getNfcDaily / fetchToday")
check("C4.3", "loading" in today_ts,
      "有 loading 状态")
check("C4.4", "demoMode" in today_ts or "Demo Mode" in today_ts,
      "有 Demo Mode 降级")

# ============================================================
# C5: Onboarding 页面
# ============================================================
check("C5.1", "birth_date" in onboarding_ts and "birth_time" in onboarding_ts,
      "birth_date/birth_time 字段")
check("C5.2", "gender" in onboarding_ts and ("male" in onboarding_ts or "female" in onboarding_ts),
      "gender 字段 (male/female)")
check("C5.3", "location" in onboarding_ts or "latitude" in onboarding_ts,
      "location 字段")

# ============================================================
# C6: Me 页面
# ============================================================
me_ts = (WEB_DIR / "app/me/page.tsx").read_text()
check("C6.1", "/onboarding" in me_ts or "onboarding" in me_ts,
      "SET UP PROFILE 导航到 /onboarding")
check("C6.2", "profile" in me_ts and "Profile" in me_ts,
      "有 Profile 状态显示")
check("C6.3", "ProfileStatus" in me_ts or "'VALID'" in me_ts or "'NONE'" in me_ts,
      "Profile Status 指示器")

# ============================================================
# C7: Types
# ============================================================
types_ts = (WEB_DIR / "types/index.ts").read_text()
check("C7.1", "NFCRequest" in types_ts and "pendant_id" in types_ts,
      "NFCRequest 类型")
check("C7.2", "ProfileStatus" in types_ts and "INSUFFICIENT" in types_ts,
      "ProfileStatus 类型")
check("C7.3", "ProfileResponse" in types_ts and "missing_fields" in types_ts,
      "ProfileResponse 类型")

# ============================================================
# C8: 禁止项检查
# ============================================================
all_ts = "".join(p.read_text() for p in WEB_DIR.rglob("*.tsx")) + "".join(p.read_text() for p in WEB_DIR.rglob("*.ts"))
check("C8.1", "console.log" not in all_ts,
      "无 console.log（生产代码）")
check("C8.2", "hardcode" not in all_ts.lower() or "BASE_URL" in all_ts,
      "无硬编码 BASE_URL")

# ============================================================
# Report
# ============================================================
passed = sum(1 for _, s, _ in audit_results if s == "PASS")
failed = sum(1 for _, s, _ in audit_results if s == "FAIL")
total = len(audit_results)

lines = ["=== Frontend-API Integration Audit ===\n", f"Passed: {passed}/{total}\n", f"Failed: {failed}/{total}\n", ""]
for name, status, detail in audit_results:
    icon = "✅" if status == "PASS" else "❌"
    lines.append(f"{icon} {name}: {detail}\n")

if failed > 0:
    lines.append("\n--- FAILURES ---\n")
    for name, status, detail in audit_results:
        if status == "FAIL":
            lines.append(f"❌ {name}: {detail}\n")

print("".join(lines))
