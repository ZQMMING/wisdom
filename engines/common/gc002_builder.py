# -*- coding: utf-8 -*-
"""GC-002 命局构造工具：标准干支排盘（用于 Golden Case 输入，不进核心引擎）

- 日柱：儒略日(JDN) mod 60，以 1900-01-01=甲戌 为锚
- 年柱：立春分界（year-4 干支；立春前=上一年）
- 月柱：五虎遁（节气分界，简化节气表；扫描避开边界日）
- 时柱：五鼠遁（日干起子时）
- 校验锚：1983-11-03 11:30 → 癸亥 壬戌 乙未 壬午（用户已验证 GC-001）
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

GAN = "甲乙丙丁戊己庚辛壬癸"
ZHI = "子丑寅卯辰巳午未申酉戌亥"
# 藏干（本气,中气,余气）
HIDDEN = {
    "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"], "卯": ["乙"],
    "辰": ["戊", "乙", "癸"], "巳": ["丙", "庚", "戊"], "午": ["丁", "己"], "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"], "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"],
}
# 节气近似日（月支分界，扫描避开 ±3 日边界）
JIEQI = [("寅", 2, 4), ("卯", 3, 6), ("辰", 4, 5), ("巳", 5, 6), ("午", 6, 6), ("未", 7, 7),
         ("申", 8, 8), ("酉", 9, 8), ("戌", 10, 8), ("亥", 11, 8), ("子", 12, 7), ("丑", 1, 6)]


def jdn(y, m, d):
    a = (14 - m) // 12
    yy, mm = y + 4800 - a, m + 12 * a - 3
    return d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045


def day_ganzhi(y, m, d):
    diff = (jdn(y, m, d) - jdn(1900, 1, 1)) % 60   # 1900-01-01 = 甲戌日(索引10)
    idx = (10 + diff) % 60
    return GAN[idx % 10] + ZHI[idx % 12]


def month_branch(y, m, d):
    if m == 1:
        return "丑"          # 1 月整月为丑月（腊月）
    mb = "丑"
    for zi, mm, dd in JIEQI:
        if mm == 1:
            continue
        if (m > mm) or (m == mm and d >= dd):
            mb = zi
    return mb


def year_ganzhi(y, m, d):
    mb = month_branch(y, m, d)
    yy = y - 1 if mb == "丑" else y   # 丑月（腊月）干支属上一年
    return GAN[(yy - 4) % 10] + ZHI[(yy - 4) % 12]


def month_gan(yg, mb):
    # 五虎遁（偏移=寅月天干索引）：甲己→丙(2) 乙庚→戊(4) 丙辛→庚(6) 丁壬→壬(8) 戊癸→甲(0)
    yi = {"甲": 2, "己": 2, "乙": 4, "庚": 4, "丙": 6, "辛": 6, "丁": 8, "壬": 8, "戊": 0, "癸": 0}[yg]
    zhi_i = ZHI.index(mb)
    g = (yi + zhi_i - 2) % 10
    return GAN[g] + mb


def hour_gan(dg, h):
    # 五鼠遁（偏移=子时天干索引）：甲己→甲(0) 乙庚→丙(2) 丙辛→戊(4) 丁壬→庚(6) 戊癸→壬(8)
    yi = {"甲": 0, "己": 0, "乙": 2, "庚": 2, "丙": 4, "辛": 4, "丁": 6, "壬": 6, "戊": 8, "癸": 8}[dg]
    hz = (h + 1) // 2 % 12
    g = (yi + hz) % 10
    return GAN[g], ZHI[hz]


def paipan(y, m, d, h):
    yg, yz = year_ganzhi(y, m, d)[0], year_ganzhi(y, m, d)[1]
    mb = month_branch(y, m, d)
    mg = month_gan(yg, mb)[0]
    dg, dz = day_ganzhi(y, m, d)
    hg, hz = hour_gan(dg, h)
    stems = {"年": yg, "月": mg, "日": dg, "时": hg}
    branches = {"年": yz, "月": mb, "日": dz, "时": hz}
    hidden = {k: HIDDEN[v] for k, v in branches.items()}
    return {"pillars": f"{yg}{yz} {mg}{mb} {dg}{dz} {hg}{hz}", "stems": stems, "branches": branches,
            "hidden": hidden, "month_order": mb, "day_master": dg}


if __name__ == "__main__":
    print("==== 排盘自校验（GC-001 锚：1983-11-03 11:30 → 癸亥 壬戌 乙未 壬午） ====")
    r = paipan(1983, 11, 3, 11)
    print("  ", r["pillars"], "→", "PASS ✓" if r["pillars"] == "癸亥 壬戌 乙未 壬午" else f"FAIL ✘ {r['pillars']}")
    print("\n==== 扫描印格命局（1990-1995 每月 15 日，避节气边界） ====")
    ELEM = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
    BENQI_TG = {k: v[0] for k, v in HIDDEN.items()}
    found = []
    for y in range(1990, 1996):
        for m in range(1, 13):
            p = paipan(y, m, 15, 10)
            dm, mb = p["day_master"], p["month_order"]
            bq = BENQI_TG[mb]
            gd, gb = ELEM[dm], ELEM[bq]
            gen = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
            if gen[gb] == gd:  # 月令本气生日主 = 印格
                found.append((p, "印格"))
    for p, g in found[:6]:
        print(f"  {p['pillars']}  日主={p['day_master']} 月={p['month_order']} → {g}")
    print(f"\n  印格候选共 {len(found)} 个，取第一个作 GC-002")
