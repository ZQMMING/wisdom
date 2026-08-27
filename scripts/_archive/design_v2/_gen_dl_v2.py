"""Design Locked V2.1 - aligned to FRONTEND_DESIGN_SHUNTIAN.md
NO vermillion. NO gold. Only ink + paper + greyscale.
"""
from PIL import Image, ImageDraw, ImageFont
import os, math

OUT = r"D:\today\docs\audit\_mockups"


def load_font(size_pt, bold=False, serif=False):
    size_px = max(8, int(size_pt * 1.5))
    cs = []
    if serif:
        cs += [("C:/Windows/Fonts/georgia.ttf", "C:/Windows/Fonts/georgiab.ttf"),
               ("C:/Windows/Fonts/times.ttf", "C:/Windows/Fonts/timesbd.ttf")]
    cs += [("C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/segoeuib.ttf"),
           ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
           ("C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/msyhbd.ttf")]
    for p1, p2 in cs:
        try: return ImageFont.truetype(p2 if (bold and p2) else p1, size_px)
        except: continue
    return ImageFont.load_default()


def center(d, x, y, t, f, c="#1A1B1E"):
    b = f.getbbox(t); tw = b[2] - b[0]
    d.text((x - tw/2, y), t, fill=c, font=f)


def right(d, x, y, t, f, c="#1A1B1E"):
    b = f.getbbox(t); tw = b[2] - b[0]
    d.text((x - tw, y), t, fill=c, font=f)


def left(d, x, y, t, f, c="#1A1B1E"):
    d.text((x, y), t, fill=c, font=f)


# 4 visual elements (monochrome only)
def draw_yin_yang(d, cx, cy, r):
    """Drawn as monochrome (black + paper)."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#1A1B1E")
    d.ellipse([cx - r//2, cy - r, cx + r//2, cy], fill="#F2EFE6")
    d.ellipse([cx - r//2, cy, cx + r//2, cy + r], fill="#F2EFE6")
    d.ellipse([cx - r//2 - 4, cy - r + 2, cx - r//2 + 4, cy - r + 10], fill="#1A1B1E")
    d.ellipse([cx + r//2 - 4, cy + r - 10, cx + r//2 + 4, cy + r - 2], fill="#1A1B1E")


def draw_hex(d, cx, cy, lines, scale=1.0):
    w = 64 * scale; lh = 2 * scale; gap = 8 * scale
    th = 6 * lh + 5 * gap; top = cy - th/2
    for i, ln in enumerate(lines):
        y = top + (5 - i) * (lh + gap)
        if ln == "yang":
            d.rectangle([cx - w/2, y, cx + w/2, y + lh], fill="#1A1B1E")
        else:
            sw = (w - gap) / 2
            d.rectangle([cx - w/2, y, cx - w/2 + sw, y + lh], fill="#1A1B1E")
            d.rectangle([cx + w/2 - sw, y, cx + w/2, y + lh], fill="#1A1B1E")


def draw_hetu(d, cx, cy, r):
    """Hetu 5-direction (classical).
    一六共宗 water (north)
    二七同道 fire (south)
    三八为朋 wood (east)
    四九为友 gold (west)
    五十同途 soil (center)
    All monochrome.
    """
    # Center 5 white dots (5 directions)
    d.ellipse([cx - 30, cy - 2, cx - 20, cy + 8], fill="#1A1B1E")
    d.ellipse([cx + 20, cy - 2, cx + 30, cy + 8], fill="#1A1B1E")
    d.ellipse([cx - 2, cy - 30, cx + 8, cy - 20], fill="#1A1B1E")
    d.ellipse([cx - 2, cy + 20, cx + 8, cy + 30], fill="#1A1B1E")
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill="#1A1B1E")

    # 生数内圈 (1, 3, 5, 7, 9) - 周圈 (5 each, all visible black)
    for cx2, cy2 in [(cx, cy - 50), (cx - 50, cy), (cx + 50, cy), (cx - 35, cy - 35),
                   (cx + 35, cy - 35), (cx, cy + 50), (cx + 35, cy + 35), (cx - 35, cy + 35)]:
        d.ellipse([cx2 - 3, cy2 - 3, cx2 + 3, cy2 + 3], fill="#1A1B1E")


# === Sheet 1: Design System (墨+纸) ===
def sheet1():
    W, H = 1100, 800
    img = Image.new("RGB", (W, H), "#F2EFE6")
    d = ImageDraw.Draw(img)
    center(d, W//2, 40, "Shuntian V2.1 . Design System", load_font(28, False, serif=True))
    center(d, W//2, 78, "Ink + Paper . Oranienbaum + MiSans . No color", load_font(12, True), "#6E6A5F")

    y = 130
    left(d, 60, y, "1. COLOR TOKENS (8)", load_font(11, True), "#6E6A5F")
    swatches = [
        ("--c-ink",            "#1A1B1E",  "Main ink"),
        ("--c-bg",             "#F2EFE6",  "Paper"),
        ("--c-surface",        "#FCFBF8",  "Card surface"),
        ("--c-secondary",      "#DCD7CA",  "Ring / Divider"),
        ("--c-text-secondary", "#6E6A5F",  "Secondary text"),
        ("--c-muted",           "#A9A398",  "Muted / Stroke"),
        ("--c-dark-bg",        "#121316",  "Dark screen (NFC/Evening)"),
        ("--c-white",          "#FFFFFF",  "On-dark text"),
    ]
    sw = 122
    for i, (nm, hx, ds) in enumerate(swatches):
        x = 60 + i * sw
        d.rounded_rectangle([x, y + 20, x + 100, y + 120], 6, fill=hx, outline="#A9A398", width=1)
        left(d, x, y + 130, nm, load_font(8, True))
        left(d, x, y + 144, hx, load_font(7, False), "#6E6A5F")
        left(d, x, y + 160, ds, load_font(7, False), "#96937F")

    # BANNER: No Color
    d.rectangle([60, 320, 1040, 360], fill="#1A1B1E")
    center(d, W//2, 333, "DISABLED: gold . vermillion . 5-elements color . semantic colors (success/warning/error/info) - ALL GRAYSCALE",
            load_font(11, True), "#F2EFE6")

    y = 400
    left(d, 60, y, "2. TYPOGRAPHY", load_font(11, True), "#6E6A5F")
    y += 24
    samples = [
        ("Display 44pt Oranienbaum",      "TODAY"),
        ("Theme 34pt Oranienbaum",        "Clarity"),
        ("Title 16pt Oranienbaum",        "When were you born?"),
        ("Body 14pt MiSans",              "A little wisdom for your day."),
        ("Button 8.5pt MiSans BOLD",      "CONTINUE"),
        ("Micro 9pt MiSans uppercase",     "WEDNESDAY"),
    ]
    for lb, t in samples:
        left(d, 60, y, lb, load_font(9, True), "#96937F")
        left(d, 300, y, t, load_font(15, False, serif=(lb[0]=="D" or lb[0]=="T" and "Theme" in lb)), "#1A1B1E")
        y += 38

    y = 660
    left(d, 60, y, "3. 4 VISUAL ELEMENTS (all monochrome)", load_font(11, True), "#6E6A5F")
    y += 30
    center(d, 200, y + 50, "1. YIN-YANG", load_font(11, True), "#1A1B1E")
    draw_yin_yang(d, 200, y + 130, 28)
    center(d, 470, y + 50, "2. YAO (6 lines)", load_font(11, True), "#1A1B1E")
    draw_hex(d, 470, y + 130, ["yang","yang","yin","yin","yang","yang"], scale=0.55)
    center(d, 740, y + 50, "3. RING / CYCLE", load_font(11, True), "#1A1B1E")
    for rr in (40, 30, 20, 10):
        d.ellipse([740 - rr, y + 130 - rr, 740 + rr, y + 130 + rr], outline="#1A1B1E", width=1)
    center(d, 1000, y + 50, "4. 8 GUA positions", load_font(11, True), "#1A1B1E")
    draw_hetu(d, 1000, y + 130, 40)

    right(d, W - 60, 770, "2026-08-22 . DESIGN LOCKED v2.1 . aligned to FRONTEND_DESIGN_SHUNTIAN.md",
           load_font(9, True), "#96937F")
    img.save(f"{OUT}/DESIGN_LOCKED_V2_1_system.png", "PNG")
    print("saved 1")


# === Sheet 2: Today Hero 5.5s state flow (no color) ===
def sheet2():
    W, H = 1500, 800
    img = Image.new("RGB", (W, H), "#F2EFE6")
    d = ImageDraw.Draw(img)
    center(d, W//2, 40, "Today Hero . 5.5s State Flow", load_font(28, False, serif=True))
    center(d, W//2, 78, "Hetu . Hexagram Transition / 4 stages . Monochrome", load_font(12, True), "#6E6A5F")

    pw, ph = 280, 580
    states = [
        ("P0 Silent (0-0.5s)",   0.5),
        ("P1 Hetu (0.5-1.9s)",   1.7),
        ("P3 Hex (3.0-4.2s)",    3.6),
        ("P4 Done (5.5s)",       5.5),
    ]
    for i, (label, t) in enumerate(states):
        x0 = 60 + i * 360
        d.rounded_rectangle([x0, 130, x0 + pw, 130 + ph], 24, fill="#F2EFE6", outline="#DCD7CA", width=1)
        left(d, x0, 100, label, load_font(11, True), "#1A1B1E")
        left(d, x0, 116, f"t={t}s", load_font(9, False), "#96937F")
        cy = 130 + 60
        cx = x0 + pw // 2
        if t < 1.0:
            for dx, col in [(-12, "#A9A398"), (0, "#1A1B1E"), (12, "#A9A398")]:
                d.ellipse([cx + dx - 4, cy - 4, cx + dx + 4, cy + 4], fill=col)
        elif t < 2.0:
            for r in (90, 70, 50, 30):
                d.ellipse([cx - r, cy - r, cx + r, cy + r], outline="#1A1B1E", width=1)
            for ang in range(0, 360, 30):
                rad = math.radians(ang); rd = 30 if ang < 180 else 50
                xd = cx + rd * math.cos(rad); yd = cy + rd * math.sin(rad)
                if 30 < ang < 150 or 210 < ang < 330:
                    d.ellipse([xd - 2.5, yd - 2.5, xd + 2.5, yd + 2.5], fill="#1A1B1E")
                else:
                    d.ellipse([xd - 2.5, yd - 2.5, xd + 2.5, yd + 2.5], fill="#F2EFE6", outline="#A9A398", width=1)
        elif t < 4.5:
            draw_hex(d, cx, cy - 20, ["yang","yang","yin","yin","yang","yang"], scale=0.65)
            center(d, cx, cy + 50, "Clarity", load_font(28, False, serif=True))
        else:
            draw_hex(d, cx, cy - 60, ["yang","yang","yin","yin","yang","yang"], scale=0.55)
            center(d, cx, cy - 18, "Clarity", load_font(24, False, serif=True))
            center(d, cx, cy + 16, "Move with clarity, not urgency.", load_font(11, False, serif=True), "#6E6A5F")
            center(d, cx, cy + 36, "Clarity about doing what truly matters.", load_font(10, False), "#96937F")

    right(d, W - 60, 770, "5.5s . 4 stages . DESIGN LOCKED v2.1 . monochrome only",
           load_font(9, True), "#96937F")
    img.save(f"{OUT}/DESIGN_LOCKED_V2_2_hero_states.png", "PNG")
    print("saved 2")


# === Sheet 3: 4 key screens (no color) ===
def sheet3():
    W, H = 1500, 800
    img = Image.new("RGB", (W, H), "#F2EFE6")
    d = ImageDraw.Draw(img)
    center(d, W//2, 40, "App . 4 Key Screens", load_font(28, False, serif=True))
    center(d, W//2, 78, "5-tab SPA . No color . Bottom Nav", load_font(12, True), "#6E6A5F")

    pw, ph = 280, 580
    screens = [("Today", "Today"), ("Calendar", "Calendar"),
               ("Personal", "Personal"), ("Settings", "Settings")]

    for i, (title, view) in enumerate(screens):
        x0 = 60 + i * 360
        # Phone frame (white-on-paper style)
        d.rounded_rectangle([x0, 130, x0 + pw, 130 + ph], 24, fill="#F2EFE6", outline="#DCD7CA", width=1)
        left(d, x0, 100, title, load_font(11, True), "#1A1B1E")

        cy = 130 + 40
        # top bar (no seal, no region color)
        left(d, x0 + 20, cy + 6, "*", load_font(14), "#6E6A5F")
        left(d, x0 + 60, cy + 4, "TONGSHU", load_font(10, True), "#1A1B1E")
        left(d, x0 + 60, cy + 16, "Sheng Huo Tong Shu", load_font(7, False), "#6E6A5F")
        # region (grey border)
        d.rounded_rectangle([x0 + pw - 70, cy, x0 + pw - 16, cy + 20], 7, outline="#A9A398", width=1)
        left(d, x0 + pw - 60, cy + 4, "CN BJ", load_font(8, False), "#1A1B1E")

        if i == 0:
            # Luoshu mandala (monochrome)
            pos = {4: (-80, -80), 9: (0, -80), 2: (80, -80),
                   3: (-80, 0), 5: (0, 0), 7: (80, 0),
                   8: (-80, 80), 1: (0, 80), 6: (80, 80)}
            for n, (px, py) in pos.items():
                pxx = x0 + pw//2 + px * 0.4
                pyy = 130 + 220 + py * 0.4
                rr = 6
                if n == 5:
                    d.ellipse([pxx - 10, pyy - 10, pxx + 10, pyy + 10], fill="#1A1B1E")
                else:
                    d.ellipse([pxx - rr, pyy - rr, pxx + rr, pyy + rr], fill="#F2EFE6", outline="#A9A398", width=1)
            center(d, x0 + pw//2, 130 + 320, "TODAY'S HEXAGRAM", load_font(8, True), "#96937F")
            center(d, x0 + pw//2, 130 + 350, "Clarity", load_font(24, False, serif=True))
            draw_hex(d, x0 + 80, 130 + 410, ["yang","yang","yin","yin","yang","yang"], scale=0.5)
            left(d, x0 + 130, 130 + 405, "T-ai", load_font(11, True))
            left(d, x0 + 130, 130 + 425, "TAI . Peace", load_font(9, True), "#6E6A5F")
        elif i == 1:
            center(d, x0 + pw//2, 130 + 100, "AUGUST 2026", load_font(11, True), "#1A1B1E")
            cal_y = 130 + 140
            for row in range(5):
                for col in range(7):
                    xd = x0 + 30 + col * 32
                    yd = cal_y + row * 36
                    day = row * 7 + col + 1
                    if day <= 31:
                        if day == 17:
                            d.ellipse([xd - 12, yd - 12, xd + 12, yd + 12], fill="#1A1B1E")
                            left(d, xd - 5, yd - 7, str(day), load_font(9, True), "#F2EFE6")
                        else:
                            left(d, xd - 5, yd - 7, str(day), load_font(9, False), "#1A1B1E")
            center(d, x0 + pw//2, 130 + 380, "Li Qiu - yin rises", load_font(9, False), "#6E6A5F")
        elif i == 2:
            yp = 130 + 100
            left(d, x0 + 20, yp, "BIRTH DATE", load_font(8, True), "#96937F")
            d.rounded_rectangle([x0 + 20, yp + 12, x0 + pw - 20, yp + 44], 4, fill="#FCFBF8", outline="#DCD7CA", width=1)
            left(d, x0 + 30, yp + 22, "1990 / 08 / 19", load_font(10, False), "#1A1B1E")
            yp += 60
            left(d, x0 + 20, yp, "BIRTH TIME", load_font(8, True), "#96937F")
            d.rounded_rectangle([x0 + 20, yp + 12, x0 + pw - 20, yp + 44], 4, fill="#FCFBF8", outline="#DCD7CA", width=1)
            left(d, x0 + 30, yp + 22, "16:00 (Shen)", load_font(10, False), "#1A1B1E")
            yp += 60
            left(d, x0 + 20, yp, "BIRTH PLACE", load_font(8, True), "#96937F")
            d.rounded_rectangle([x0 + 20, yp + 12, x0 + pw - 20, yp + 44], 4, fill="#FCFBF8", outline="#DCD7CA", width=1)
            left(d, x0 + 30, yp + 22, "Shanghai, China", load_font(10, False), "#1A1B1E")
            yp += 70
            # CTA: black, not vermillion
            d.rounded_rectangle([x0 + 20, yp, x0 + pw - 20, yp + 38], 19, fill="#1A1B1E")
            center(d, x0 + pw//2, yp + 11, "GENERATE TONG SHU", load_font(10, True), "#F2EFE6")
        else:
            settings = [("Country", "CN"), ("Region", "Beijing"),
                          ("Language", "Simplified Chinese"),
                          ("Day Boundary", "Zi-shi swap (system)"),
                          ("Time Zone", "Asia/Shanghai"),
                          ("True Solar", "Auto (from birthplace)"),
                          ("Engine Ver", "v1.0.0")]
            for j, (k, v) in enumerate(settings):
                ys = 130 + 110 + j * 50
                left(d, x0 + 20, ys, k, load_font(10, False), "#1A1B1E")
                right(d, x0 + pw - 20, ys, v, load_font(10, False), "#6E6A5F")
                d.line([(x0 + 20, ys + 16), (x0 + pw - 20, ys + 16)], fill="#DCD7CA", width=1)

        # Bottom nav (no vermillion, monochrome with active indicator)
        tab_y = 130 + ph - 60
        tab_w = (pw - 20) // 5
        tabs = ["Today", "Cal", "You", "Log", "Set"]
        for j, tname in enumerate(tabs):
            tx = x0 + 10 + j * tab_w
            if tname == tabs[i]:
                # Active: dark filled circle
                d.ellipse([tx + tab_w//2 - 14, tab_y - 12, tx + tab_w//2 + 14, tab_y + 16], fill="#1A1B1E")
                center(d, tx + tab_w//2, tab_y - 3, "*", load_font(14, True), "#F2EFE6")
            else:
                center(d, tx + tab_w//2, tab_y, tname, load_font(8, False), "#6E6A5F")

    right(d, W - 60, 770, "5 tabs . active = ink . DESIGN LOCKED v2.1 . monochrome only",
           load_font(9, True), "#96937F")
    img.save(f"{OUT}/DESIGN_LOCKED_V2_3_screens.png", "PNG")
    print("saved 3")


sheet1()
sheet2()
sheet3()
print("All done")
