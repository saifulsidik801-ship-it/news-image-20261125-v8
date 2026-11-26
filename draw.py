#!/usr/bin/env python3
"""news-image-20261125 v8 — draws entry.png (1024x1024) in code, PIL only.
Fresh build from the v8 study (~/workspace/news-image-20261125-v8-study.md).
38 stories, all first reported Wed 25 Nov 2026. Flat vector style, no photos.
Run: python3 draw.py  -> writes entry.png next to this file.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
MARGIN = 12
CW = W - 2 * MARGIN  # 1000

# ---- palette ----
NAVY = (15, 42, 74)
PAPER = (247, 243, 232)
RED = (185, 28, 28)
INK = (26, 26, 26)
GREY = (107, 114, 128)
LGREY = (210, 205, 190)
WHITE = (255, 255, 255)
CREAM_CARD = (255, 252, 244)

REGION = {
    "Europe": (29, 78, 216),
    "Asia": (180, 83, 9),
    "N. America": (14, 116, 144),
    "Mideast": (185, 28, 28),
    "Africa": (21, 128, 61),
    "Oceania": (124, 58, 237),
    "Latin Am": (219, 39, 119),
    "World": (71, 85, 105),
}
BADGE_COL = {"OFFICIAL": (29, 78, 216), "REPORTED": (180, 83, 9),
             "CLAIM": (185, 28, 28), "CONFIRMED": (21, 128, 61)}
BADGE_LETTER = {"CONFIRMED": "C", "OFFICIAL": "O", "REPORTED": "R", "CLAIM": "CL"}

# ---- fonts ----
def _font(paths, size):
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)

DJ = "/usr/share/fonts/truetype/dejavu/"
LB = "/usr/share/fonts/truetype/liberation/"

def serif_b(s):
    return _font([DJ + "DejaVuSerif-Bold.ttf", LB + "LiberationSerif-Bold.ttf"], s)

def serif(s):
    return _font([DJ + "DejaVuSerif.ttf", LB + "LiberationSerif-Regular.ttf"], s)

def serif_i(s):
    return _font([DJ + "DejaVuSerif-Italic.ttf", LB + "LiberationSerif-Italic.ttf"], s)

def sans(s):
    return _font([DJ + "DejaVuSans.ttf", LB + "LiberationSans-Regular.ttf"], s)

def sans_b(s):
    return _font([DJ + "DejaVuSans-Bold.ttf", LB + "LiberationSans-Bold.ttf"], s)

# ---- text helpers ----
def wrap(text, font, max_w):
    """Greedy word wrap to max_w pixels; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.getlength(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def fit(text, font, max_w, ell="..."):
    """Truncate with ellipsis to max_w pixels."""
    if font.getlength(text) <= max_w:
        return text
    while text and font.getlength(text + ell) > max_w:
        text = text[:-1]
    return text + ell

def draw_wrapped(d, x, y, text, font, color, max_w, lh, max_lines=None):
    lines = wrap(text, font, max_w)
    if max_lines:
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=font, fill=color)
    return len(lines)

def chip(d, x, y, text, font, fg, bg=None, pad=5, h=None):
    """Small label chip; returns width."""
    w = int(font.getlength(text)) + 2 * pad
    hh = h or (font.size + 2 * pad - 2)
    if bg:
        d.rounded_rectangle([x, y, x + w, y + hh], radius=3, fill=bg)
    d.text((x + pad, y + (hh - font.size) // 2 - 1), text, font=font, fill=fg)
    return w

def badge_word(d, x, y, word, size=10):
    """Outlined claim badge, right-aligned at x (x is right edge)."""
    f = sans_b(size)
    w = int(f.getlength(word)) + 10
    col = BADGE_COL[word]
    d.rounded_rectangle([x - w, y, x, y + size + 6], radius=2,
                        outline=col, width=1)
    d.text((x - w + 5, y + 2), word, font=f, fill=col)
    return w

# ================= STORY DATA (all verified Nov 25, see v8 study §6) =================
# heroes: (kicker, dateline, headline, body, why, source, badge, region)
HEROES = [
    ("TOP STORY", "WASHINGTON \u00b7 TRADE",
     "US proposes tariffs of up to 20% on EU, China and 12 more",
     "USTR ends 8-month probe of 16 partners. China hit hardest at 20%.",
     "Biggest US tariff escalation of the year.",
     "Reuters \u00b7 USTR", "OFFICIAL", "N. America"),
    ("MARKETS", "SEOUL \u00b7 TOKYO \u00b7 TAIPEI \u00b7 MARKETS",
     "AI doubts sink Asian chip stocks; Kospi closes \u22126.2%",
     "Kospi ends at 4,697.51; SK Hynix \u221211.1%, Samsung \u22129.9%. Taiex \u22124.8%, Nikkei \u22122.8%.",
     "Doubt over the AI spending boom.",
     "AP \u00b7 Barchart", "REPORTED", "Asia"),
    ("SPACE", "JIUQUAN, CHINA \u00b7 SPACE",
     "Pakistan's first astronaut docks at China's space station",
     "Muhammad Zeeshan Ali, 40, first foreigner on Tiangong; stays 5 to 10 days.",
     "First foreign astronaut on Tiangong.",
     "Reuters \u00b7 Xinhua", "OFFICIAL", "Asia"),
]

# mids: (num, dateline, headline, body, source, badge, region, art_key)
MIDS = [
    (4, "RAS TANURA \u00b7 WAR",
     "Iran says mines set two tankers on fire",
     "IRGC says two tankers hit mines and burned; unverified.",
     "Reuters", "CLAIM", "Mideast", "tankers"),
    (5, "WASHINGTON \u00b7 SECURITY",
     "FinCEN discloses breach probe",
     "FinCEN probes unauthorised access to its systems.",
     "BleepingComputer", "REPORTED", "N. America", "fincen"),
    (6, "CANBERRA \u00b7 DIPLOMACY",
     "Solomons sign security pact with Australia",
     "Australia is \u201cprimary security partner\u201d; A$740m over 10 years.",
     "pm.gov.au", "OFFICIAL", "Oceania", "treaty"),
    (7, "DHAKA \u00b7 LABOUR",
     "Garment workers offered 36% pay rise",
     "Wage board: Tk12,500 to Tk17,000 a month. Wires reported 17,500.",
     "TBS \u00b7 Daily Star", "REPORTED", "Asia", "wage"),
    (8, "BOGOR, JAVA \u00b7 DISASTER",
     "9 dead, 17 still trapped in flooded gold pit",
     "Rescuers pull bodies from a 100-metre pit in West Java.",
     "AP", "REPORTED", "Asia", "mine"),
    (9, "GAZA CITY \u00b7 WAR",
     "Strike kills Hamas security chief, family",
     "Mohammad Abuelouf, wife and two daughters die in Shati camp.",
     "Reuters", "REPORTED", "Mideast", "gaza"),
    (10, "SYDNEY \u00b7 ECONOMY",
     "Australia's inflation jumps to 4.9%",
     "October CPI up 4.9% on a year ago, highest since 2023.",
     "ABS", "OFFICIAL", "Oceania", "cpi"),
    (11, "MIDDLETOWN, IOWA \u00b7 SECURITY",
     "US Army blows up lead azide stockpile",
     "Two open-air blasts of ~5 tons; detonation complete, well-contained.",
     "US Army", "OFFICIAL", "N. America", "blast"),
    (12, "DAMAZIN, SUDAN \u00b7 WAR",
     "RSF drones kill 19 in Sudan's Blue Nile",
     "Rights group: 19 dead in Damazin, 20 hurt; drones hit homes and power sites. Reported Wed.",
     "Reuters", "REPORTED", "Africa", "drones"),
    (13, "LONDON \u00b7 ENERGY",
     "UK energy price cap rises 26% in January",
     "Ofgem: typical bill \u00a31,723 to \u00a32,166 a year from 1 Jan; ~20m households.",
     "Ofgem", "OFFICIAL", "Europe", "ofgem"),
    (14, "BRUSSELS \u00b7 EU",
     "EU hosts six Western Balkan leaders",
     "Summit on membership and the Growth Plan. Serbia absent.",
     "EC", "OFFICIAL", "Europe", "summit"),
    (15, "CARTAGENA \u00b7 CRIME",
     "Police free all hostages in supermarket siege",
     "All remaining ~20 freed in dawn rescue; one captor killed.",
     "AP", "REPORTED", "Latin Am", "rescue"),
    (16, "BRUSSELS \u00b7 TECH",
     "EU proposes \u20ac50bn fund for quantum tech",
     "Quantum Act aims to make Europe a global leader by 2030.",
     "Reuters", "OFFICIAL", "Europe", "quantum"),
]

# list: (num, city, headline, source, badge, region)
LIST = [
    (17, "Seoul", "Bithumb breach widens: 19 data types", "RTR", "OFFICIAL", "Asia"),
    (18, "Karachi", "Building collapse: 3 dead, 14 hurt", "AP", "REPORTED", "Asia"),
    (19, "Paran\u00e1", "Storms kill 6, ~10,000 affected", "Civil Def.", "REPORTED", "Latin Am"),
    (20, "Enugu", "Pete Edochie dies, 79", "Family", "OFFICIAL", "Africa"),
    (21, "London", "Met 'still institutionally racist'", "Review", "OFFICIAL", "Europe"),
    (22, "Jerusalem", "Judges urge dropping bribery charge", "RTR", "REPORTED", "Mideast"),
    (23, "Cape Town", "Ramaphosa wins Farmgate case", "Court", "OFFICIAL", "Africa"),
    (24, "London", "Eurostar strike cancels 8 trains", "RTR", "REPORTED", "Europe"),
    (25, "Pyongyang", "N. Korea expels Swiss envoy", "KCNA", "OFFICIAL", "Asia"),
    (26, "Cairo", "Fuel-tanker fire: 31 dead", "AP", "REPORTED", "Africa"),
    (27, "Perth", "Deloitte suspended over AI errors", "Govt", "OFFICIAL", "Oceania"),
    (28, "San Francisco", "GPT-6.2 reaches Copilot", "MS", "REPORTED", "World"),
    (29, "Vatican", "Pope Leo laments COP31 collapse", "RTR", "OFFICIAL", "World"),
    (30, "Kyiv", "Zaporizhzhia loses power, 17th time", "IAEA", "OFFICIAL", "Europe"),
    (31, "Moscow", "Kremlin dismisses 700k toll estimate", "RTR", "REPORTED", "Europe"),
    (32, "Sanaa", "Houthis threaten Saudi Red Sea ports", "RTR", "REPORTED", "Mideast"),
    (33, "Warsaw", "Poland may expel Russian envoy", "RTR", "REPORTED", "Europe"),
    (34, "Mississippi", "Plane: all 6 bodies found", "USCG", "REPORTED", "N. America"),
    (35, "Texas", "Dell falls 10% despite record sales", "RTR", "REPORTED", "N. America"),
    (36, "Washington", "US PCE inflation 3.8%", "BEA", "OFFICIAL", "N. America"),
    (37, "Washington", "US GDP revised to +4.3%", "BEA", "OFFICIAL", "N. America"),
    (38, "Brussels", "EU debates Costa's \u20ac1.78tn budget", "EP", "OFFICIAL", "Europe"),
]

REGION_ORDER = ["Europe", "Asia", "N. America", "Mideast", "Africa", "Oceania", "Latin Am", "World"]
REGION_COUNT = {"Europe": 9, "Asia": 7, "N. America": 7, "Mideast": 4,
                "Africa": 4, "Oceania": 3, "Latin Am": 2, "World": 2}

NUMBERS = [("\u22126.2%", "Kospi close, worst in AI sell-off"),
           ("20%", "top proposed US tariff on China"),
           ("+4.3%", "US GDP, fastest in 3 years"),
           ("+36%", "Bangladesh garment wage"),
           ("\u00a32,166", "Ofgem cap from January"),
           ("31", "Cairo tanker-fire dead")]

TIMELINE = [("00:18", "Shenzhou launches"), ("01:31", "Bodies found"),
            ("03:56", "Tiangong docks"), ("~04:00", "Gaza"),
            ("04:28", "Zaporizhzhia out"), ("06:30", "Rescue"),
            ("13:30", "PCE + GDP"), ("15:00", "Iowa blast")]

# ================= HERO ART (flat vector scenes, labels inside the art) =================
def art_tariffs(d, x, y, w, h):
    sky = (191, 217, 232)
    d.rectangle([x, y, x + w, y + h], fill=sky)
    d.rectangle([x, y + int(h * 0.62), x + w, y + h], fill=(30, 90, 138))
    # sun + clouds
    d.ellipse([x + w - 52, y + 8, x + w - 22, y + 38], fill=(250, 204, 21))
    d.ellipse([x + 14, y + 12, x + 54, y + 30], fill=WHITE)
    d.ellipse([x + 40, y + 6, x + 80, y + 24], fill=WHITE)
    # ship hull
    hy = y + int(h * 0.62)
    d.polygon([(x + 8, hy - 26), (x + w - 8, hy - 26), (x + w - 30, hy + 6),
               (x + 28, hy + 6)], fill=(15, 42, 74))
    # bridge tower
    d.rectangle([x + w - 62, hy - 62, x + w - 30, hy - 26], fill=(226, 232, 240))
    for i in range(3):
        d.rectangle([x + w - 58, hy - 56 + i * 11, x + w - 34, hy - 49 + i * 11],
                    fill=(15, 42, 74))
    # containers, 3 rows x 6 cols, region colours
    cols = [(185, 28, 28), (29, 78, 216), (250, 204, 21), (21, 128, 61),
            (234, 88, 12), (124, 58, 237)]
    cw_, ch_ = (w - 110) // 6, 12
    for r in range(3):
        for c in range(6):
            cx = x + 12 + c * (cw_ + 2)
            cy = hy - 26 - (r + 1) * (ch_ + 2)
            d.rectangle([cx, cy, cx + cw_, cy + ch_], fill=cols[(r * 6 + c) % 6],
                        outline=(255, 255, 255))
    # labels inside art
    d.text((x + 10, y + h - 18), "EU", font=sans_b(11), fill=WHITE)
    d.text((x + w - 152, hy - 26 - 3 * 14 - 8), "CHINA", font=sans_b(11), fill=WHITE)
    # red badge circle
    bx, by, br = x + w - 58, y + 44, 26
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=RED, outline=WHITE, width=2)
    d.text((bx - 20, by - 16), "UP TO", font=sans_b(10), fill=WHITE)
    d.text((bx - 20, by - 4), "20%", font=sans_b(15), fill=WHITE)
    # waves
    for i in range(4):
        d.arc([x + 10 + i * 80, hy + 12, x + 70 + i * 80, hy + 26],
              200, 340, fill=(147, 197, 253), width=2)

def art_kospi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(17, 24, 39))
    # grid
    for i in range(1, 4):
        gy = y + i * h // 4
        d.line([x + 8, gy, x + w - 8, gy], fill=(55, 65, 81), width=1)
    # falling red line
    pts = [(x + 62, y + 24), (x + w * 0.25, y + 30), (x + w * 0.45, y + 52),
           (x + w * 0.62, y + 48), (x + w * 0.8, y + 78), (x + w - 12, y + h - 62)]
    d.line(pts, fill=(239, 68, 68), width=4, joint="curve")
    for px, py in pts[1:-1]:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(239, 68, 68))
    # AI chip icon
    cx, cy = x + 22, y + h - 52
    d.rectangle([cx, cy, cx + 30, cy + 30], fill=(31, 41, 55), outline=(239, 68, 68), width=2)
    d.text((cx + 5, cy + 7), "AI", font=sans_b(15), fill=(239, 68, 68))
    for i in range(3):
        d.line([cx + 5 + i * 10, cy - 5, cx + 5 + i * 10, cy], fill=(239, 68, 68), width=2)
        d.line([cx + 5 + i * 10, cy + 30, cx + 5 + i * 10, cy + 35], fill=(239, 68, 68), width=2)
    # labels
    d.text((x + 12, y + 22), "KOSPI", font=sans_b(13), fill=(148, 163, 184))
    d.text((x + w - 78, y + 28), "\u22126.2%", font=sans_b(20), fill=(239, 68, 68))
    d.text((x + w - 108, y + h - 42), "SK HYNIX \u221211.1%", font=sans_b(11), fill=WHITE)
    d.text((x + w - 108, y + h - 24), "SAMSUNG \u22129.9%", font=sans_b(11), fill=WHITE)

def art_shenzhou(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(11, 16, 38))
    # stars
    import random
    rnd = random.Random(25)
    for _ in range(46):
        sx, sy = x + rnd.randint(4, w - 4), y + rnd.randint(4, h - 30)
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=(226, 232, 240))
    # Earth curve at bottom
    d.ellipse([x - w * 0.35, y + h - 34, x + w * 1.35, y + h + 90],
              fill=(37, 99, 235))
    d.ellipse([x + w * 0.1, y + h - 22, x + w * 0.45, y + h + 30], fill=(21, 128, 61))
    d.ellipse([x + w * 0.62, y + h - 16, x + w * 0.8, y + h + 18], fill=(21, 128, 61))
    # rocket (left, launching)
    rx, ry = x + 34, y + 44
    d.polygon([(rx + 12, ry - 22), (rx + 22, ry - 4), (rx + 2, ry - 4)], fill=(226, 232, 240))
    d.rectangle([rx + 2, ry - 4, rx + 22, ry + 34], fill=(241, 245, 249))
    d.rectangle([rx + 2, ry + 10, rx + 22, ry + 18], fill=(185, 28, 28))
    d.polygon([(rx - 6, ry + 34), (rx + 2, ry + 26), (rx + 2, ry + 40)], fill=(185, 28, 28))
    d.polygon([(rx + 30, ry + 34), (rx + 22, ry + 26), (rx + 22, ry + 40)], fill=(185, 28, 28))
    d.polygon([(rx + 6, ry + 40), (rx + 18, ry + 40), (rx + 12, ry + 58)], fill=(249, 115, 22))
    d.text((rx - 8, ry + 62), "LONG MARCH 2F", font=sans_b(9), fill=WHITE)
    # station (right): core + 2 solar panels
    sx, sy = x + w - 150, y + 26
    d.rectangle([sx, sy + 12, sx + 96, sy + 30], fill=(226, 232, 240))
    d.rectangle([sx + 34, sy, sx + 62, sy + 42], fill=(203, 213, 225))
    d.rectangle([sx - 42, sy + 16, sx, sy + 26], fill=(37, 99, 235))
    d.rectangle([sx + 96, sy + 16, sx + 138, sy + 26], fill=(37, 99, 235))
    for i in range(4):
        d.line([sx - 42 + i * 11, sy + 16, sx - 42 + i * 11, sy + 26],
               fill=(147, 197, 253), width=1)
        d.line([sx + 96 + i * 11, sy + 16, sx + 96 + i * 11, sy + 26],
               fill=(147, 197, 253), width=1)
    # flags: Pakistan green crescent + China red
    fx, fy = x + w - 150, y + 52
    d.rectangle([fx, fy, fx + 26, fy + 16], fill=(20, 120, 60))
    d.ellipse([fx + 5, fy + 3, fx + 15, fy + 13], fill=WHITE)
    d.ellipse([fx + 8, fy + 3, fx + 15, fy + 13], fill=(20, 120, 60))
    d.rectangle([fx + 32, fy, fx + 58, fy + 16], fill=(222, 41, 16))
    for _sx, _sy in [(fx + 38, fy + 4), (fx + 46, fy + 6), (fx + 44, fy + 11), (fx + 38, fy + 10)]:
        d.ellipse([_sx, _sy, _sx + 2, _sy + 2], fill=(255, 222, 0))
    # labels
    d.text((x + 12, y + 22), "SHENZHOU-24", font=sans_b(13), fill=WHITE)
    d.text((x + w - 100, y + h - 44), "TIANGONG", font=sans_b(13), fill=WHITE)
    d.text((x + w - 168, y + h - 26), "1ST PAKISTANI IN SPACE", font=sans_b(11),
           fill=(147, 197, 253))

HERO_ART = {"N. America": art_tariffs, "Asia": None}  # per-hero below

# ================= MID ART (real scenes, 2-4 elements + label inside) =================
def _label(d, x, y, text, size=13, color=WHITE, bg=None):
    f = sans_b(size)
    if bg:
        tw = int(f.getlength(text)) + 8
        d.rectangle([x, y, x + tw, y + size + 5], fill=bg)
        d.text((x + 4, y + 2), text, font=f, fill=color)
    else:
        d.text((x, y), text, font=f, fill=color)

def art_tankers(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(14, 116, 144))
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(8, 60, 80))
    d.rectangle([x + 10, y + h * 0.42, x + 78, y + h * 0.62], fill=(15, 42, 74))
    d.rectangle([x + 88, y + h * 0.48, x + 150, y + h * 0.62], fill=(30, 58, 80))
    for fx in (x + 26, x + 58, x + 104, x + 128):
        d.polygon([(fx, y + h * 0.42), (fx + 7, y + h * 0.14),
                   (fx + 14, y + h * 0.42)], fill=(249, 115, 22))
        d.polygon([(fx + 2, y + h * 0.30), (fx + 7, y + h * 0.14),
                   (fx + 12, y + h * 0.30)], fill=(250, 204, 21))
    _label(d, x + 6, y + 3, "2 TANKERS", 12)

def art_fincen(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(31, 41, 55))
    d.rectangle([x + w - 62, y + 6, x + w - 6, y + h - 6], fill=(17, 24, 39))
    for i in range(4):
        d.line([x + w - 56, y + 10 + i * 5, x + w - 12, y + 10 + i * 5],
               fill=(74, 222, 128) if i != 2 else (239, 68, 68), width=3)
    d.polygon([(x + 22, y + 6), (x + 42, y + 6), (x + 42, y + 20),
               (x + 32, y + 30), (x + 22, y + 20)], fill=(250, 204, 21))
    d.text((x + 29, y + 10), "!", font=sans_b(13), fill=(17, 24, 39))
    _label(d, x + 50, y + 8, "FINCEN", 13)
    _label(d, x + 50, y + 22, "BREACH PROBE", 10, (250, 204, 21))

def art_treaty(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(124, 58, 237))
    d.rectangle([x + 12, y + 8, x + 58, y + 26], fill=(0, 47, 108))
    d.rectangle([x + 12, y + 8, x + 58, y + 26], outline=WHITE, width=1)
    for sx in range(14, 56, 7):
        d.ellipse([sx, y + 11, sx + 3, y + 14], fill=WHITE)
    d.rectangle([x + 66, y + 8, x + 112, y + 26], fill=(20, 120, 60))
    d.polygon([(x + 89, y + 11), (x + 92, y + 17), (x + 98, y + 17),
               (x + 93, y + 21), (x + 95, y + 25), (x + 89, y + 22),
               (x + 83, y + 25), (x + 85, y + 21), (x + 80, y + 17),
               (x + 86, y + 17)], fill=(255, 215, 0))
    d.rectangle([x + 122, y + 5, x + w - 8, y + 29], fill=WHITE)
    d.text((x + 128, y + 7), "A$740M", font=sans_b(14), fill=(124, 58, 237))
    d.text((x + 128, y + 21), "10 YRS", font=sans_b(9), fill=(124, 58, 237))

def art_wage(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(180, 83, 9))
    d.rectangle([x + 10, y + 8, x + 70, y + h - 8], fill=(41, 37, 36))
    d.rectangle([x + 16, y + 12, x + 64, y + 20], fill=(120, 113, 108))
    d.ellipse([x + 52, y + 14, x + 58, y + 18], fill=(250, 204, 21))
    d.rectangle([x + 78, y + 6, x + w - 8, y + 22], fill=(21, 128, 61))
    d.text((x + 84, y + 8), "Tk 17,000", font=sans_b(14), fill=WHITE)
    d.text((x + 84, y + 23), "+36%  PAY RISE", font=sans_b(11), fill=WHITE)

def art_mine(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(28, 25, 23))
    d.polygon([(x + 8, y + 6), (x + 70, y + 6), (x + 58, y + h - 6),
               (x + 20, y + h - 6)], fill=(68, 64, 60))
    d.rectangle([x + 30, y + 10, x + 48, y + h - 10], fill=(12, 10, 9))
    d.ellipse([x + 74, y + 8, x + 84, y + 18], fill=(250, 204, 21))
    d.text((x + 90, y + 8), "9 DEAD", font=sans_b(13), fill=WHITE)
    d.text((x + 90, y + 22), "17 TRAPPED", font=sans_b(11), fill=(250, 204, 21))

def art_gaza(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(69, 26, 3))
    for bx, bw, bh in ((8, 26, 26), (38, 20, 34), (62, 30, 22), (96, 22, 30)):
        d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h], fill=(41, 37, 36))
        for wy in range(y + h - bh + 4, y + h - 4, 8):
            d.rectangle([x + bx + 4, wy, x + bx + 9, wy + 4], fill=(250, 204, 21))
    d.ellipse([x + 124, y + 6, x + 150, y + 24], fill=(107, 114, 128))
    d.ellipse([x + 132, y + 2, x + 162, y + 18], fill=(156, 163, 175))
    _label(d, x + 6, y + 3, "GAZA CITY", 11)

def art_cpi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(124, 58, 237))
    bars = [(12, 8), (34, 12), (56, 16), (78, 20)]
    for bx, bh in bars:
        d.rectangle([x + bx, y + h - 6 - bh, x + bx + 16, y + h - 6],
                    fill=(250, 204, 21) if bx == 78 else (196, 181, 253))
    d.text((x + 104, y + 6), "4.9%", font=sans_b(18), fill=WHITE)
    d.text((x + 104, y + 24), "CPI  OCT", font=sans_b(10), fill=(196, 181, 253))

def art_blast(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(14, 116, 144))
    cx, cy = x + 34, y + h // 2
    for r, col in ((14, (249, 115, 22)), (9, (250, 204, 21)), (4, WHITE)):
        d.polygon([(cx, cy - r), (cx + r * 0.4, cy - r * 0.4), (cx + r, cy),
                   (cx + r * 0.4, cy + r * 0.4), (cx, cy + r),
                   (cx - r * 0.4, cy + r * 0.4), (cx - r, cy),
                   (cx - r * 0.4, cy - r * 0.4)], fill=col)
    for bx in (66, 92, 118):
        d.rectangle([x + bx, y + h - 16, x + bx + 18, y + h - 6], fill=(41, 37, 36))
        d.rectangle([x + bx + 4, y + h - 22, x + bx + 14, y + h - 16], fill=(120, 113, 108))
    _label(d, x + 142, y + 8, "5 TONS", 13)
    _label(d, x + 142, y + 24, "DETONATED", 10, (250, 204, 21))

def art_drones(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(21, 128, 61))
    d.rectangle([x + 8, y + h - 22, x + w - 8, y + h - 6], fill=(20, 60, 30))
    for dx, dy in ((30, 10), (70, 18), (110, 8)):
        d.rectangle([x + dx, y + dy, x + dx + 18, y + dy + 6], fill=(15, 42, 74))
        d.line([x + dx - 6, y + dy + 3, x + dx + 24, y + dy + 3], fill=WHITE, width=2)
        d.ellipse([x + dx - 8, y + dy - 2, x + dx - 2, y + dy + 8], fill=(226, 232, 240))
        d.ellipse([x + dx + 20, y + dy - 2, x + dx + 26, y + dy + 8], fill=(226, 232, 240))
    _label(d, x + 132, y + 8, "19 KILLED", 13)
    _label(d, x + 132, y + 23, "DAMAZIN", 10, (187, 247, 208))

def art_ofgem(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(29, 78, 216))
    d.polygon([(x + 16, y + 22), (x + 34, y + 6), (x + 52, y + 22),
               (x + 46, y + 22), (x + 46, y + h - 6), (x + 22, y + h - 6),
               (x + 22, y + 22)], fill=(241, 245, 249))
    d.polygon([(x + 66, y + 8), (x + 58, y + 22), (x + 66, y + 22),
               (x + 60, y + 36), (x + 74, y + 20), (x + 66, y + 20)],
              fill=(250, 204, 21))
    d.rectangle([x + 84, y + 5, x + w - 8, y + 21], fill=WHITE)
    d.text((x + 90, y + 7), "\u00a32,166", font=sans_b(14), fill=(29, 78, 216))
    d.text((x + 90, y + 23), "+26%  FROM JAN", font=sans_b(10), fill=WHITE)

def art_summit(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(29, 78, 216))
    d.ellipse([x + 10, y + 3, x + 36, y + 29], fill=(15, 42, 74))
    for i in range(8):
        import math
        a = i * math.pi / 4
        sx = x + 23 + int(10 * math.cos(a)) - 1
        sy = y + 16 + int(10 * math.sin(a)) - 1
        d.ellipse([sx, sy, sx + 3, sy + 3], fill=(250, 204, 21))
    for i, col in enumerate([(185, 28, 28), (21, 128, 61), (250, 204, 21),
                             (124, 58, 237), (14, 116, 144), (219, 39, 119)]):
        fx = x + 48 + i * 18
        d.rectangle([fx, y + 5, fx + 14, y + 20], fill=col, outline=WHITE)
    _label(d, x + 48, y + 22, "6 LEADERS", 11)
    _label(d, x + 118, y + 10, "\u20ac6BN PLAN", 12)

def art_rescue(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(219, 39, 119))
    d.rectangle([x + 10, y + 12, x + 76, y + h - 8], fill=(241, 245, 249))
    d.rectangle([x + 16, y + 6, x + 70, y + 12], fill=(185, 28, 28))
    d.text((x + 20, y + 16), "MARKET", font=sans_b(11), fill=(185, 28, 28))
    for i in range(3):
        d.rectangle([x + 18 + i * 18, y + h - 14, x + 30 + i * 18, y + h - 4],
                    fill=(147, 197, 253))
    d.polygon([(x + 92, y + 8), (x + 110, y + 8), (x + 110, y + 22),
               (x + 101, y + 30), (x + 92, y + 22)], fill=(250, 204, 21))
    d.text((x + 98, y + 11), "!", font=sans_b(12), fill=(17, 24, 39))
    _label(d, x + 120, y + 10, "ALL FREED", 13)
    _label(d, x + 120, y + 23, "DAWN RESCUE", 10, (255, 255, 255))

def art_quantum(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(29, 78, 216))
    cx, cy = x + 30, y + h // 2
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(250, 204, 21))
    for rx, ry, ang in ((20, 7, 0), (20, 7, 60), (20, 7, 120)):
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=WHITE, width=2)
    d.text((x + 62, y + 6), "\u20ac50BN", font=sans_b(17), fill=WHITE)
    d.text((x + 62, y + 24), "QUANTUM ACT", font=sans_b(10), fill=(191, 219, 254))

MID_ART = {"tankers": art_tankers, "fincen": art_fincen, "treaty": art_treaty,
           "wage": art_wage, "mine": art_mine, "gaza": art_gaza, "cpi": art_cpi,
           "blast": art_blast, "drones": art_drones, "ofgem": art_ofgem,
           "summit": art_summit, "rescue": art_rescue, "quantum": art_quantum}

# ================= CARD RENDERERS =================
def draw_hero(img, d, x, y, w, h, num, hero, art_fn):
    kicker, dateline, headline, body, why, source, badge, region = hero
    # art: everything above the text block, drawn on a temp image so it
    # can never spill past its box
    ah = h - 146
    art_img = Image.new("RGB", (w, ah), (255, 255, 255))
    ad = ImageDraw.Draw(art_img)
    art_fn(ad, 0, 0, w, ah)
    img.paste(art_img, (x, y))
    # kicker tab on the art, top-left
    kf = sans_b(11)
    kw = int(kf.getlength(kicker)) + 12
    d.rectangle([x, y, x + kw, y + 17], fill=RED)
    d.text((x + 6, y + 3), kicker, font=kf, fill=WHITE)
    # story number badge, top-right of art
    nf = sans_b(13)
    d.ellipse([x + w - 24, y + 4, x + w - 4, y + 24], fill=RED, outline=WHITE, width=2)
    d.text((x + w - 17, y + 8), str(num), font=nf, fill=WHITE)
    # dateline + badge
    ty = y + ah + 5
    d.text((x + 2, ty), dateline, font=sans_b(10), fill=REGION[region])
    badge_word(d, x + w - 2, ty - 1, badge, size=10)
    # headline (serif bold, up to 3 lines)
    hy = ty + 14
    n = draw_wrapped(d, x + 2, hy, headline, serif_b(22), INK, w - 4, 23, max_lines=3)
    by = hy + n * 23 + 2
    draw_wrapped(d, x + 2, by, body, sans(13), (55, 65, 81), w - 4, 14, max_lines=2)
    wy = by + 30
    d.text((x + 2, wy), "WHY IT MATTERS  ", font=sans_b(11), fill=RED)
    wl = sans_b(11).getlength("WHY IT MATTERS  ")
    draw_wrapped(d, x + 2 + int(wl), wy, why, sans(11), INK, w - 4 - int(wl), 12, max_lines=1)
    sy = wy + 12
    d.text((x + 2, sy), "(" + source + ")", font=sans(10), fill=GREY)

def draw_mid(img, d, x, y, w, h, mid):
    num, dateline, headline, body, source, badge, region, art_key = mid
    ah = h - 72
    art_img = Image.new("RGB", (w, ah), (255, 255, 255))
    ad = ImageDraw.Draw(art_img)
    MID_ART[art_key](ad, 0, 0, w, ah)
    img.paste(art_img, (x, y))
    # number badge on art
    nf = sans_b(11)
    d.ellipse([x + w - 20, y + 3, x + w - 3, y + 20], fill=RED, outline=WHITE, width=1)
    d.text((x + w - 14, y + 6), str(num), font=nf, fill=WHITE)
    ty = y + ah + 4
    d.text((x + 2, ty), dateline, font=sans_b(9), fill=REGION[region])
    badge_word(d, x + w - 2, ty - 1, badge, size=9)
    hy = ty + 10
    n = draw_wrapped(d, x + 2, hy, headline, serif_b(14), INK, w - 4, 15, max_lines=2)
    by = hy + n * 15 + 2
    draw_wrapped(d, x + 2, by, body, sans(11), (55, 65, 81), w - 4, 12, max_lines=2)

# ================= WORLD MAP =================
CONTINENTS = {
    "NAm": [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-80, 73),
            (-75, 62), (-60, 55), (-55, 47), (-65, 45), (-75, 38), (-80, 32),
            (-90, 29), (-97, 26), (-105, 20), (-110, 23), (-120, 34), (-125, 40),
            (-130, 50), (-150, 60), (-165, 60)],
    "SAm": [(-80, 10), (-70, 12), (-60, 8), (-50, 0), (-40, -5), (-35, -10),
            (-40, -20), (-50, -30), (-60, -40), (-70, -50), (-75, -40),
            (-75, -25), (-80, -15), (-80, 0)],
    "Eur": [(-10, 36), (0, 37), (10, 38), (15, 40), (20, 45), (28, 45), (30, 40),
            (25, 38), (20, 36), (10, 37), (0, 43), (-5, 48), (-10, 50), (-5, 55),
            (0, 58), (5, 60), (10, 62), (18, 65), (25, 70), (20, 70), (12, 65),
            (5, 58), (-2, 50), (-10, 43)],
    "Afr": [(-10, 35), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28), (40, 20),
            (45, 12), (50, 11), (45, 5), (40, -2), (35, -10), (30, -20), (25, -30),
            (20, -35), (15, -30), (12, -18), (10, -5), (5, 4), (-5, 5), (-15, 10),
            (-17, 15), (-15, 25), (-10, 30)],
    "Asi": [(30, 36), (40, 38), (50, 40), (60, 42), (70, 45), (80, 50), (90, 55),
            (100, 60), (110, 65), (120, 70), (130, 72), (140, 72), (150, 70),
            (160, 65), (170, 66), (175, 65), (170, 60), (160, 55), (150, 50),
            (140, 45), (135, 40), (130, 35), (125, 30), (120, 25), (115, 20),
            (110, 15), (105, 10), (100, 8), (95, 10), (90, 15), (85, 20),
            (80, 15), (75, 10), (70, 8), (65, 12), (60, 15), (55, 20), (50, 25),
            (45, 30), (40, 35), (35, 36)],
    "Aus": [(113, -22), (120, -20), (130, -12), (135, -12), (142, -11), (147, -19),
            (150, -22), (153, -27), (150, -37), (140, -38), (130, -32),
            (120, -34), (113, -30)],
}
# (story num, lon, lat, dx, dy)
PINS = [(1, -77, 39, 0, 0), (2, 127, 37.5, 0, 0), (3, 100, 41, 0, 0),
        (4, 56.5, 26.5, 0, 0), (5, -77, 39, 9, 6), (6, 149, -35.3, -4, 4),
        (7, 90.4, 23.8, 0, 0), (8, 106.8, -6.6, 0, 0), (9, 34.5, 31.5, 0, 0),
        (10, 151, -34, 6, -6), (11, -91.5, 41.5, 0, 0), (12, 34.5, 11.8, 0, 0),
        (13, -0.1, 51.5, -5, -4), (14, 4.35, 50.85, 5, 2), (15, -75.5, 10.4, 0, 0),
        (16, 4.35, 50.85, -3, 7)]
PIN_REGION = {1: "N. America", 2: "Asia", 3: "Asia", 4: "Mideast", 5: "N. America",
              6: "Oceania", 7: "Asia", 8: "Asia", 9: "Mideast", 10: "Oceania",
              11: "N. America", 12: "Africa", 13: "Europe", 14: "Europe",
              15: "Latin Am", 16: "Europe"}

def draw_map(d, x, y, w, h):
    d.text((x, y), "WHERE IT HAPPENED", font=sans_b(11), fill=NAVY)
    d.text((x + 140, y), "pins = story numbers", font=sans(10), fill=GREY)
    my = y + 15
    mh = h - 15
    def proj(lon, lat):
        return (x + (lon + 170) / 360 * w, my + (75 - lat) / 130 * mh)
    for poly in CONTINENTS.values():
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=(216, 205, 180), outline=(247, 243, 232))
    for num, lon, lat, dx, dy in PINS:
        px, py = proj(lon, lat)
        px += dx
        py += dy
        col = REGION[PIN_REGION[num]]
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=col, outline=WHITE, width=1)
        f = sans_b(9)
        tw = f.getlength(str(num))
        d.text((px - tw / 2, py - 5), str(num), font=f, fill=WHITE)

def draw_list(d, x, y, w, h):
    d.text((x, y), "ALSO ON WEDNESDAY 25 NOVEMBER \u2014 22 MORE STORIES",
           font=sans_b(12), fill=NAVY)
    ly = y + 16
    col_w = (w - 10) // 2
    lf = sans(11)
    nf = sans_b(11)
    for i, (num, city, head, src, badge, region) in enumerate(LIST):
        col = i // 11
        row = i % 11
        lx = x + col * (col_w + 10)
        ry = ly + row * 11
        d.text((lx, ry), str(num), font=nf, fill=REGION[region])
        nw = nf.getlength(str(num)) + 4
        # badge letter chip + source at right
        bl = BADGE_LETTER[badge]
        bf = sans_b(9)
        bw = int(bf.getlength(bl)) + 6
        sw = lf.getlength(src)
        tx_w = col_w - nw - bw - sw - 14
        txt = fit(f"{city}: {head}", lf, tx_w)
        d.text((lx + nw, ry), txt, font=lf, fill=INK)
        bx = lx + col_w - bw - sw - 6
        d.rectangle([bx, ry, bx + bw, ry + 10], fill=BADGE_COL[badge])
        d.text((bx + 3, ry), bl, font=bf, fill=WHITE)
        d.text((lx + col_w - sw, ry), src, font=lf, fill=GREY)

# ================= MAIN LAYOUT =================
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 1
    # 1. top bar
    d.rectangle([0, y, W, y + 16], fill=NAVY)
    tb = "THE WORLD IN ONE DAY  \u00b7  38 STORIES  \u00b7  8 REGIONS  \u00b7  21 FIELDS  \u00b7  ALL FIRST REPORTED ON WEDNESDAY 25 NOVEMBER 2026"
    tf = sans_b(11)
    tw = tf.getlength(tb)
    d.text(((W - tw) / 2, y + 3), tb, font=tf, fill=WHITE)
    y += 16 + 3
    # 2. masthead
    mf = serif_b(52)
    d.text((MARGIN, y - 4), "Wednesday 25 November 2026", font=mf, fill=NAVY)
    y += 50 + 3
    # 3. lede
    lf = serif_i(18)
    d.text((MARGIN, y), "US proposes tariffs on 14 economies \u00b7 AI doubts sink Asian chip stocks \u00b7 Pakistan\u2019s first astronaut docks at Tiangong",
           font=lf, fill=RED)
    y += 18 + 3
    # 4. region strip
    rx = MARGIN
    rf = sans_b(11)
    for r in REGION_ORDER:
        t = f"{r} {REGION_COUNT[r]}"
        wch = chip(d, rx, y, t, rf, WHITE, bg=REGION[r], pad=6, h=16)
        rx += wch + 6
    y += 16 + 3
    # 5. number strip
    nx = MARGIN
    cell_w = CW // 6
    for i, (num, lab) in enumerate(NUMBERS):
        cx = MARGIN + i * cell_w
        d.text((cx, y), num, font=sans_b(19), fill=NAVY if i % 2 == 0 else RED)
        d.text((cx, y + 20), lab, font=sans(9), fill=GREY)
        if i:
            d.line([cx - 5, y + 2, cx - 5, y + 28], fill=LGREY, width=1)
    y += 28 + 3
    # 6. timeline
    d.rectangle([MARGIN, y, MARGIN + CW, y + 17], fill=NAVY)
    d.text((MARGIN + 6, y + 3), "THE DAY IN UTC", font=sans_b(10), fill=(250, 204, 21))
    tx = MARGIN + 92
    tlf = sans(10)
    tbf = sans_b(10)
    for t, ev in TIMELINE:
        d.text((tx, y + 3), t, font=tbf, fill=(250, 204, 21))
        twd = tbf.getlength(t) + 4
        d.text((tx + twd, y + 3), ev, font=tlf, fill=WHITE)
        tx += twd + tlf.getlength(ev) + 8
    y += 17 + 4
    # 7. heroes
    hw = (CW - 16) // 3
    hero_art = [art_tariffs, art_kospi, art_shenzhou]
    for i, hero in enumerate(HEROES):
        hx = MARGIN + i * (hw + 8)
        d.rectangle([hx, y, hx + hw, y + 292], fill=CREAM_CARD, outline=LGREY)
        draw_hero(img, d, hx + 2, y + 2, hw - 4, 288, i + 1, hero, hero_art[i])
    y += 292 + 4
    # 8. mids — 3 rows: 5 + 4 + 4
    rows = [MIDS[0:5], MIDS[5:9], MIDS[9:13]]
    for row in rows:
        mw = (CW - 8 * (len(row) - 1)) // len(row)
        for j, mid in enumerate(row):
            mx = MARGIN + j * (mw + 8)
            d.rectangle([mx, y, mx + mw, y + 110], fill=CREAM_CARD, outline=LGREY)
            draw_mid(img, d, mx + 2, y + 2, mw - 4, 106, mid)
        y += 110 + 4
    # 9. map + list
    map_w = 300
    draw_map(d, MARGIN, y, map_w, 140)
    draw_list(d, MARGIN + map_w + 10, y, CW - map_w - 10, 140)
    y += 140 + 4
    # 10. DATE CHECK
    d.rectangle([MARGIN, y, MARGIN + CW, y + 52], outline=RED, width=2)
    dc = sans(11)
    dcb = sans_b(11)
    dy = y + 4
    d.text((MARGIN + 6, dy), "DATE CHECK   ", font=dcb, fill=RED)
    d.text((MARGIN + 6 + int(dcb.getlength("DATE CHECK   ")), dy),
           "Every story above happened or was first reported on Wednesday 25 November 2026.",
           font=dc, fill=INK)
    dy += 13
    for ln in wrap("Left out as earlier news: Dow 50,018.70 (Tue 24) \u00b7 Huawei verdict (Tue 24) \u00b7 Riyadh tower strike, 11 hurt (Tue 24) \u00b7 Chen Jining probe (Tue 24) \u00b7 CIA\u2013ODNI breach first reported (Tue 24) \u00b7 UN femicide report (Tue 24) \u00b7 Nvidia reinstates Huang (Mon 23) \u00b7 COP31 collapse (Sun 22) \u00b7 Nepal quake (Tue 24) \u00b7 Miss Universe crowned (Tue 24).",
                   dc, CW - 12):
        d.text((MARGIN + 6, dy), ln, font=dc, fill=INK)
        dy += 12
    d.text((MARGIN + 6, dy), "Not yet: US Thanksgiving (Thu 26 Nov) \u00b7 Argentina 2027 budget vote (Thu 26 Nov).",
           font=dc, fill=INK)
    y += 52 + 2
    # 11. footer
    ff = sans(10)
    d.text((MARGIN, y), "OFFICIAL an authority's own word  \u00b7  REPORTED press report  \u00b7  CLAIM one side's say, unverified  \u00b7  CONFIRMED 2+ major outlets",
           font=ff, fill=GREY)
    y += 10
    d.text((MARGIN, y), "Sources: Reuters, AP, AFP, BBC, Al Jazeera, Xinhua, Yonhap, ABS, BEA, Ofgem, EC, NZX \u2014 all reported 25 November 2026.   Every drawing original \u2014 drawn in code, not photos.",
           font=ff, fill=GREY)
    y += 10
    assert y <= H, f"layout overflow: y={y}"
    return img

if __name__ == "__main__":
    im = build()
    out = os.path.join(HERE, "entry.png")
    im.save(out, optimize=True)
    print("saved", out, os.path.getsize(out), "bytes")
