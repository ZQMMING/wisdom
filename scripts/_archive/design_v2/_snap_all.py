from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path="C:/Program Files/Google/Chrome/Application/chrome.exe", args=["--no-sandbox","--disable-gpu"])
    ctx = b.new_context(viewport={"width":480,"height":900})
    page = ctx.new_page()
    screens = [
        ("a1", "onboarding-a1-welcome"),
        ("a2", "onboarding-a2-birthdate"),
        ("a3", "onboarding-a3-birthtime"),
        ("a4", "onboarding-a4-birthplace"),
        ("a5", "onboarding-a5-confirm"),
        ("a6", "onboarding-a6-pattern"),
        ("b1", "today-b1-nfc"),
        ("b2", "today-b2-hero"),
        ("b3", "today-b3-theme"),
        ("b4", "today-b4-guidance"),
        ("b5", "today-b5-action"),
        ("b6", "today-b6-why"),
        ("b7", "today-b7-evidence"),
        ("b8", "today-b8-evening"),
        ("c1", "me-c1-details"),
        ("c2", "me-c2-editplace"),
        ("c3", "me-c3-settings"),
        ("c4", "me-c4-wisdom"),
        ("c5", "me-c5-about"),
    ]
    for view_id, slug in screens:
        if view_id in ("a2","a3","a4","a5","a6","b2","b3","b4","b5","b6","b7","b8","c1","c2","c3","c4","c5"):
            if view_id == "a2": route = "#/onboarding/a2"
            elif view_id == "a3": route = "#/onboarding/a3"
            elif view_id == "a4": route = "#/onboarding/a4"
            elif view_id == "a5": route = "#/onboarding/a5"
            elif view_id == "a6": route = "#/onboarding/a6"
            elif view_id == "b2": route = "#/today"
            elif view_id == "b3": route = "#/today/theme"
            elif view_id == "b4": route = "#/today/guidance"
            elif view_id == "b5": route = "#/today/action"
            elif view_id == "b6": route = "#/why-today"
            elif view_id == "b7": route = "#/evidence"
            elif view_id == "b8": route = "#/evening"
            elif view_id == "c1": route = "#/me"
            elif view_id == "c2": route = "#/me/edit-place"
            elif view_id == "c3": route = "#/settings"
            elif view_id == "c4": route = "#/wisdom"
            elif view_id == "c5": route = "#/about"
        else:
            if view_id == "a1": route = "#/onboarding/a1"
            elif view_id == "b1": route = "#/nfc"
        page.goto("http://127.0.0.1:8765/" + route, wait_until="domcontentloaded")
        page.wait_for_timeout(8000 if view_id in ("b2","a6","b8") else 1500)
        out = "D:/today/docs/audit/_mockups/screen_" + slug + ".png"
        page.screenshot(path=out, full_page=True)
        print("  saved", slug, "hero=" + str(page.locator(".stage-screen").count()))
    b.close()
