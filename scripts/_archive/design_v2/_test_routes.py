from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path="C:/Program Files/Google/Chrome/Application/chrome.exe", args=["--no-sandbox","--disable-gpu"])
    ctx = b.new_context(viewport={"width":480,"height":900})
    page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append("PE: " + str(e)[:300]))
    page.on("console", lambda m: errs.append("C[" + m.type + "]: " + m.text[:200]) if m.type == "error" else None)

    routes = [
        "#/onboarding/a1", "#/onboarding/a2", "#/onboarding/a3",
        "#/onboarding/a4", "#/onboarding/a5", "#/onboarding/a6",
        "#/nfc", "#/today", "#/today/theme", "#/today/guidance",
        "#/today/action", "#/why-today", "#/evidence", "#/evening",
        "#/me", "#/me/edit-place", "#/settings", "#/wisdom", "#/about",
    ]

    results = []
    for r in routes:
        url = "http://127.0.0.1:8765/" + r
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=8000)
            page.wait_for_timeout(300)
            has_hero = page.locator(".stage-screen").count()
            has_dark = page.locator(".dark-screen").count()
            results.append((r, has_hero, has_dark, list(errs)))
            errs.clear()
        except Exception as e:
            results.append((r, 0, 0, ["TIMEOUT: " + str(e)]))

    print("=== 19 routes test ===")
    for r, hero, dark, errs_list in results:
        e = errs_list[0] if errs_list else "-"
        print("  " + r.ljust(28) + " hero=" + str(hero) + " dark=" + str(dark) + " err=" + e[:80])

    b.close()
