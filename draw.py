#!/usr/bin/env python3
"""Render the Tuesday 24 November 2026 front page (1024x1024 PNG).

Reads stories.json next to this file and draws the paper: masthead, date,
numbers strip, region bar, three illustrated features, ten illustrated
medium cells, a world map with numbered dots, the ALSO list, a DATE CHECK
box and the verification footer.

Fonts: Liberation TrueType, bundled in ./fonts/ (falling back to the system
Liberation install). Pillow is used when available; when it is not, main.py
copies the pre-rendered entry.png instead, so both paths are byte-identical.
"""

import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (20, 20, 20)
RED = (180, 30, 30)
DARKRED = (140, 25, 25)
NAVY = (31, 58, 95)
DARKNAVY = (16, 36, 64)
GRAY = (96, 92, 84)
LINE = (178, 168, 148)
OCEAN = (191, 217, 232)
LAND = (232, 217, 168)
WHITE = (255, 255, 255)
CREAMBOX = (255, 252, 244)

TAG_FILL = {
    "CONFIRMED": (34, 120, 60),
    "OFFICIAL": (31, 58, 95),
    "REPORTED": (176, 120, 0),
    "CLAIM": (180, 30, 30),
}

REGION_FILL = {
    "AMERICAS": (31, 58, 95),
    "EUROPE": (46, 110, 142),
    "ASIA": (172, 124, 12),
    "MIDDLE EAST": (180, 30, 30),
    "AFRICA": (107, 79, 161),
    "OCEANIA": (46, 125, 91),
    "GLOBAL": (90, 90, 90),
}

SERIF_B = "LiberationSerif-Bold.ttf"
SERIF = "LiberationSerif-Regular.ttf"
SERIF_I = "LiberationSerif-Italic.ttf"
SANS_B = "LiberationSans-Bold.ttf"
SANS = "LiberationSans-Regular.ttf"
SANS_I = "LiberationSans-Italic.ttf"


def _font(name, size):
    here = os.path.dirname(os.path.abspath(__file__))
    for base in (os.path.join(here, "fonts"),
                 "/usr/share/fonts/truetype/liberation"):
        path = os.path.join(base, name)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wrap(d, text, font, max_w):
    """Word-wrap text to a list of lines fitting max_w pixels."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(d, text, font_name, start_size, min_size, max_w, max_lines):
    """Largest font size (from start_size down) fitting max_lines lines."""
    size = start_size
    while size >= min_size:
        font = _font(font_name, size)
        lines = wrap(d, text, font, max_w)
        if len(lines) <= max_lines:
            return font, lines
        size -= 1
    font = _font(font_name, min_size)
    return font, wrap(d, text, font, max_w)[:max_lines]


def tag_pill(d, x, y, tag):
    """Right-aligned verification tag pill; returns its left edge."""
    font = _font(SANS_B, 9)
    tw = d.textlength(tag, font=font)
    w = int(tw) + 12
    d.rounded_rectangle([x - w, y, x, y + 13], radius=3,
                        fill=TAG_FILL.get(tag, GRAY))
    d.text((x - w + 6, y + 2), tag, font=font, fill=WHITE)
    return x - w


# ---------------------------------------------------------------- illustrations

def art_chip(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=DARKNAVY)
    cx0, cy0 = x + 16, y + 16
    cx1, cy1 = x + 126, y + h - 16
    d.rectangle([cx0, cy0, cx1, cy1], fill=(200, 206, 214),
                outline=(120, 128, 138), width=2)
    d.rectangle([cx0 + 14, cy0 + 10, cx1 - 14, cy1 - 10], fill=(90, 96, 106))
    for i in range(4):
        px = cx0 + 18 + i * 26
        d.line([px, cy0 - 8, px, cy0], fill=(200, 206, 214), width=3)
        d.line([px, cy1, px, cy1 + 8], fill=(200, 206, 214), width=3)
    for j in range(3):
        py = cy0 + 12 + j * 12
        d.line([cx0 - 8, py, cx0, py], fill=(200, 206, 214), width=3)
        d.line([cx1, py, cx1 + 8, py], fill=(200, 206, 214), width=3)
    pts = [(x + 150, y + h - 14), (x + 182, y + h - 32),
           (x + 212, y + h - 24), (x + 252, y + 18), (x + 300, y + 10)]
    d.line(pts, fill=(74, 222, 128), width=4)
    d.polygon([(x + 300, y + 10), (x + 290, y + 8), (x + 296, y + 20)],
              fill=(74, 222, 128))


def art_ship(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(217, 232, 240))
    d.rectangle([x, y + int(h * 0.55), x + w, y + h], fill=(46, 110, 142))
    d.polygon([(x + 12, y + h - 12), (x + w - 12, y + h - 12),
               (x + w - 26, y + h - 32), (x + 26, y + h - 32)],
              fill=(60, 60, 66))
    d.rectangle([x + 30, y + h - 50, x + 62, y + h - 32], fill=(180, 30, 30))
    d.rectangle([x + 66, y + h - 50, x + 96, y + h - 32], fill=(232, 180, 40))
    for dx, dy in ((18, 10), (44, 4), (70, 12)):
        d.ellipse([x + w - dx - 22, y + dy, x + w - dx - 14, y + dy + 8],
                  fill=(40, 40, 44))
        d.line([x + w - dx - 18, y + dy + 8, x + w - dx - 18, y + dy + 22],
               fill=(40, 40, 44), width=1)
    d.line([x + 8, y + h - 8, x + w - 8, y + h - 8], fill=WHITE, width=2)


def art_skyline(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(58, 46, 79))
    d.ellipse([x + w - 52, y + 8, x + w - 16, y + 44], fill=(232, 180, 90))
    for bx, bw, bh in ((6, 22, 46), (32, 18, 62), (54, 24, 38),
                       (82, 18, 56), (104, 22, 44)):
        d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h], fill=(24, 20, 32))
        for wy in range(y + h - bh + 6, y + h - 6, 10):
            for wx in range(x + bx + 4, x + bx + bw - 4, 8):
                d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 214, 90))
    for cx, cy, r in ((58, 18, 9), (70, 10, 12), (84, 20, 8)):
        d.ellipse([x + cx - r, y + cy - r, x + cx + r, y + cy + r],
                  fill=(150, 150, 158))


def art_blast(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(216, 210, 196))
    d.rectangle([x + 12, y + 10, x + w - 12, y + h - 4], fill=(196, 178, 140))
    for row in range(2):
        for col in range(4):
            d.rectangle([x + 18 + col * 14, y + 15 + row * 9,
                         x + 26 + col * 14, y + 21 + row * 9],
                        fill=(60, 52, 40))
    import math
    cx, cy = x + w // 2, y + 15
    for k in range(8):
        ang = k * 3.14159 / 4
        x1 = cx + int(6 * math.cos(ang))
        y1 = cy + int(6 * math.sin(ang))
        x2 = cx + int(12 * math.cos(ang))
        y2 = cy + int(12 * math.sin(ang))
        d.line([x1, y1, x2, y2], fill=(232, 110, 20), width=3)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 200, 60))


def art_tanker(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(46, 110, 142))
    d.polygon([(x + 8, y + h - 8), (x + w - 8, y + h - 8),
               (x + w - 20, y + h - 20), (x + 20, y + h - 20)],
              fill=(120, 40, 36))
    d.rectangle([x + 26, y + 4, x + 52, y + h - 20], fill=(232, 232, 232))
    cx, cy = x + w - 26, y + 11
    for k in range(8):
        import math
        ang = k * 3.14159 / 4
        d.line([cx + int(6 * math.cos(ang)), cy + int(6 * math.sin(ang)),
                cx + int(11 * math.cos(ang)), cy + int(11 * math.sin(ang))],
               fill=(20, 20, 24), width=2)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(20, 20, 24))
    d.line([x + 8, y + h - 4, x + w - 8, y + h - 4], fill=WHITE, width=2)


def art_satellite(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(15, 30, 51))
    d.ellipse([x - 30, y + h - 20, x + 44, y + h], fill=(210, 180, 120))
    d.ellipse([x + 20, y + 8, x + w - 20, y + h - 8], outline=(150, 180, 210),
              width=2)
    sx, sy = x + w - 34, y + 14
    d.rectangle([sx - 12, sy - 3, sx - 4, sy + 3], fill=(90, 140, 200))
    d.rectangle([sx + 4, sy - 3, sx + 12, sy + 3], fill=(90, 140, 200))
    d.rectangle([sx - 4, sy - 5, sx + 4, sy + 5], fill=(232, 232, 232))
    d.ellipse([sx - 2, sy - 9, sx + 2, sy - 5], fill=(232, 232, 232))
    for px, py in ((18, 26), (34, 12), (52, 30)):
        d.ellipse([x + px, y + py, x + px + 2, y + py + 2], fill=WHITE)


def art_rocket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(191, 217, 232))
    d.ellipse([x + w - 40, y + 2, x + w - 14, y + 22], fill=(255, 220, 120))
    cx = x + w // 2 - 6
    d.polygon([(cx + 6, y + 2), (cx, y + 12), (cx + 12, y + 12)],
              fill=(180, 30, 30))
    d.rectangle([cx, y + 12, cx + 12, y + h - 12], fill=(232, 232, 232),
                outline=(120, 120, 120), width=1)
    d.polygon([(cx, y + h - 12), (cx - 6, y + h - 4), (cx + 2, y + h - 12)],
              fill=(180, 30, 30))
    d.polygon([(cx + 12, y + h - 12), (cx + 18, y + h - 4),
               (cx + 10, y + h - 12)], fill=(180, 30, 30))
    d.polygon([(cx + 2, y + h - 12), (cx + 10, y + h - 12),
               (cx + 6, y + h - 2)], fill=(255, 160, 40))
    d.ellipse([x + 8, y + h - 14, x + 30, y + h - 4], outline=(90, 90, 90),
              width=2)


def art_bars(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=WHITE)
    vals = [("US", 78.9, NAVY), ("CN", 73.6, RED), ("IN", 40.5, (46, 125, 91))]
    base = y + h - 10
    top = y + 10
    bw = 34
    for i, (lab, v, col) in enumerate(vals):
        bh = max(3, int((v / 80.0) * (base - top)))
        bx = x + 14 + i * 48
        f = _font(SANS_B, 8)
        d.text((bx + 2, y + 1), str(v), font=f, fill=INK)
        d.rectangle([bx, base - bh, bx + bw, base], fill=col)
        f2 = _font(SANS_B, 9)
        d.text((bx + 8, base + 1), lab, font=f2, fill=INK)


def art_mountains(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(217, 232, 240))
    d.ellipse([x + w - 34, y + 4, x + w - 14, y + 24], fill=(255, 220, 120))
    d.polygon([(x + 4, y + h), (x + 34, y + 10), (x + 64, y + h)],
              fill=(110, 130, 110))
    d.polygon([(x + 28, y + 18), (x + 34, y + 10), (x + 40, y + 18)],
              fill=WHITE)
    d.polygon([(x + 40, y + h), (x + 74, y + 22), (x + 108, y + h)],
              fill=(80, 105, 85))
    d.polygon([(x + 68, y + 29), (x + 74, y + 22), (x + 80, y + 29)],
              fill=WHITE)
    d.line([x + w - 18, y + h - 26, x + w - 18, y + h - 6], fill=INK, width=2)
    d.polygon([(x + w - 18, y + h - 26), (x + w - 6, y + h - 22),
               (x + w - 18, y + h - 18)], fill=(180, 30, 30))


def art_factory(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 220, 200))
    d.rectangle([x + 10, y + 20, x + w - 10, y + h - 6], fill=(150, 140, 120))
    for i in range(4):
        bx = x + 14 + i * 22
        d.polygon([(bx, y + 20), (bx + 11, y + 10), (bx + 22, y + 20)],
                  fill=(120, 110, 92))
    d.rectangle([x + 16, y + h - 22, x + 30, y + h - 6], fill=(60, 52, 40))
    cx, cy = x + w - 26, y + 16
    d.polygon([(cx - 10, cy + 12), (cx - 2, cy - 8), (cx + 4, cy + 2),
               (cx + 10, cy - 10), (cx + 12, cy + 12)], fill=(255, 140, 20))
    d.polygon([(cx - 5, cy + 12), (cx, cy + 2), (cx + 6, cy + 12)],
              fill=(255, 210, 60))
    for sx, sy, r in ((x + 30, y + 8, 6), (x + 44, y + 4, 8)):
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(170, 170, 178))


def art_scales(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(239, 231, 211))
    cx = x + w // 2
    d.line([cx, y + 8, cx, y + h - 8], fill=(90, 70, 40), width=3)
    d.line([cx - 26, y + 14, cx + 26, y + 14], fill=(90, 70, 40), width=3)
    d.ellipse([cx - 4, y + 4, cx + 4, y + 12], fill=(180, 150, 60))
    for sgn in (-1, 1):
        px = cx + sgn * 26
        d.line([px, y + 14, px - 7, y + 26], fill=(90, 70, 40), width=2)
        d.line([px, y + 14, px + 7, y + 26], fill=(90, 70, 40), width=2)
        d.pieslice([px - 9, y + 24, px + 9, y + 32], 0, 180,
                   fill=(180, 150, 60))
    d.rectangle([cx - 12, y + h - 6, cx + 12, y + h - 2], fill=(90, 70, 40))


def art_columns(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 210))
    d.polygon([(x + 8, y + 12), (x + w // 2, y + 2), (x + w - 8, y + 12)],
              fill=(120, 100, 70))
    for i in range(3):
        bx = x + 16 + i * 34
        d.rectangle([bx, y + 16, bx + 12, y + h - 12], fill=(200, 188, 160),
                    outline=(120, 100, 70), width=1)
        d.rectangle([bx - 2, y + 14, bx + 14, y + 17], fill=(120, 100, 70))
    d.rectangle([x + 8, y + h - 10, x + w - 8, y + h - 6], fill=(120, 100, 70))


def art_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(62, 125, 78))
    d.rectangle([x + w // 2 - 12, y + 2, x + w // 2 + 12, y + h - 2],
                fill=(222, 200, 150))
    for sy in (y + 8, y + h - 14):
        for k in range(3):
            d.line([x + w // 2 - 8 + k * 8, sy,
                    x + w // 2 - 8 + k * 8, sy + 6], fill=(240, 230, 200),
                   width=2)
    d.rectangle([x + 16, y + 10, x + 30, y + 30], fill=(222, 190, 130),
                outline=(120, 90, 40), width=1)
    d.ellipse([x + w - 30, y + h - 22, x + w - 18, y + h - 10],
              fill=(180, 30, 30))


ART = {
    "chip": art_chip, "ship": art_ship, "skyline": art_skyline,
    "blast": art_blast, "tanker": art_tanker, "satellite": art_satellite,
    "rocket": art_rocket, "bars": art_bars, "mountains": art_mountains,
    "factory": art_factory, "scales": art_scales, "columns": art_columns,
    "cricket": art_cricket,
}

# ---------------------------------------------------------------- world map

NORTH_AMERICA = [(-168, 66), (-165, 60), (-158, 58), (-152, 60), (-140, 60),
    (-135, 58), (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-114, 29),
    (-110, 24), (-105, 20), (-97, 16), (-94, 17), (-90, 14), (-86, 12),
    (-83, 9), (-80, 8), (-79, 9), (-77, 7), (-81, 25), (-80, 32), (-76, 35),
    (-74, 40), (-70, 42), (-68, 45), (-65, 44), (-60, 47), (-55, 47),
    (-60, 52), (-65, 60), (-68, 58), (-78, 62), (-85, 66), (-92, 66),
    (-95, 69), (-110, 68), (-125, 70), (-140, 70), (-155, 71), (-165, 68)]
GREENLAND = [(-58, 64), (-52, 60), (-44, 60), (-40, 64), (-32, 68),
    (-22, 70), (-20, 74), (-25, 78), (-35, 80), (-45, 78), (-55, 76),
    (-58, 70)]
SOUTH_AMERICA = [(-80, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12),
    (-72, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50),
    (-70, -54), (-66, -55), (-68, -50), (-65, -45), (-62, -41), (-58, -35),
    (-52, -32), (-48, -28), (-41, -23), (-39, -17), (-35, -9), (-35, -6),
    (-40, -3), (-44, -2), (-50, 0), (-53, 4), (-58, 6), (-62, 9),
    (-68, 11), (-72, 12), (-77, 8)]
AFRICA = [(-17, 15), (-16, 20), (-15, 27), (-10, 31), (-6, 34), (0, 36),
    (10, 37), (11, 34), (19, 32), (25, 32), (30, 31), (32, 31), (34, 28),
    (37, 22), (39, 18), (43, 12), (48, 11), (51, 10), (46, 5), (42, 0),
    (40, -5), (40, -10), (37, -15), (35, -20), (33, -26), (28, -33),
    (20, -35), (17, -32), (15, -27), (13, -18), (12, -12), (13, -6),
    (9, -1), (9, 4), (-8, 5), (-13, 8), (-17, 12)]
EURASIA = [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48),
    (0, 50), (2, 51), (5, 53), (8, 55), (8, 57), (10, 59), (5, 60),
    (5, 62), (10, 64), (13, 66), (18, 69), (25, 71), (30, 70), (35, 68),
    (40, 68), (45, 68), (50, 69), (55, 69), (60, 69), (65, 70), (70, 72),
    (75, 73), (80, 73), (85, 74), (90, 75), (95, 76), (100, 77),
    (105, 77), (110, 74), (115, 73), (120, 73), (125, 72), (130, 72),
    (135, 71), (140, 72), (145, 72), (150, 70), (155, 69), (160, 69),
    (165, 66), (170, 66), (178, 65), (178, 62), (170, 60), (162, 60),
    (158, 53), (156, 51), (150, 59), (142, 59), (140, 53), (138, 46),
    (135, 43), (130, 42), (127, 40), (126, 38), (122, 38), (120, 32),
    (118, 25), (110, 20), (108, 18), (105, 10), (103, 8), (100, 7),
    (98, 10), (95, 16), (92, 21), (89, 22), (86, 20), (80, 15), (77, 8),
    (75, 12), (73, 16), (70, 20), (66, 25), (62, 25), (58, 26), (56, 27),
    (52, 28), (50, 29), (48, 30), (50, 26), (54, 24), (57, 22), (59, 22),
    (55, 17), (52, 15), (48, 14), (44, 13), (43, 12), (40, 15), (38, 18),
    (35, 20), (34, 22), (32, 25), (30, 28), (28, 30), (25, 31), (22, 32),
    (19, 31), (15, 32), (11, 33), (10, 37), (8, 38), (3, 37), (0, 36),
    (-2, 36), (-6, 36), (-9, 37)]
AUSTRALIA = [(114, -22), (114, -30), (115, -34), (118, -35), (124, -33),
    (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
    (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
    (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
    (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)]
SUMATRA = [(95, 5), (100, 0), (104, -3), (106, -6), (101, -5), (97, 2)]
BORNEO = [(109, 1), (113, 4), (117, 6), (119, 1), (116, -3), (111, -3),
    (109, 0)]
NEWGUINEA = [(131, -1), (136, -2), (141, -3), (146, -6), (147, -9),
    (143, -8), (138, -8), (133, -4)]
JAVA = [(105, -6), (110, -7), (114, -8), (114, -9), (108, -8)]
BRITAIN = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
    (1, 51), (-2, 50)]
JAPAN = [(130, 31), (132, 33), (134, 34), (137, 35), (139, 37), (141, 39),
    (141, 41), (143, 42), (145, 44), (142, 45), (140, 42), (139, 38),
    (137, 36), (133, 35), (130, 33)]
CONTINENTS = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EURASIA,
              AUSTRALIA, SUMATRA, BORNEO, NEWGUINEA, JAVA, BRITAIN, JAPAN]


def draw_map(d, x, y, w, h, dots):
    d.rectangle([x, y, x + w, y + h], fill=OCEAN)
    d.rectangle([x, y, x + w, y + h], outline=LINE, width=1)
    for lon in range(-150, 181, 30):
        gx = x + int((lon + 180) / 360.0 * w)
        d.line([gx, y, gx, y + h], fill=(160, 190, 205), width=1)
    for lat in (-30, 0, 30, 60):
        gy = y + int((84 - lat) / 144.0 * h)
        d.line([x, gy, x + w, gy], fill=(160, 190, 205), width=1)

    def px(lon, lat):
        return (x + int((lon + 180) / 360.0 * w),
                y + int((84 - lat) / 144.0 * h))

    for poly in CONTINENTS:
        d.polygon([px(lon, lat) for lon, lat in poly], fill=LAND,
                  outline=(180, 165, 120))
    num_font = _font(SANS_B, 9)
    for dot in dots:
        cx, cy = px(dot["lon"], dot["lat"])
        dx, dy = dot.get("dx", 0), dot.get("dy", 0)
        if dx or dy:
            d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED,
                      outline=WHITE, width=1)
            lx, ly = cx + dx, cy + dy
            d.line([cx, cy, lx, ly], fill=GRAY, width=1)
            d.rectangle([lx - 8, ly - 7, lx + 8, ly + 7], fill=WHITE,
                        outline=RED, width=1)
            label = str(dot["n"])
            d.text((lx - d.textlength(label, font=num_font) / 2, ly - 5),
                   label, font=num_font, fill=RED)
        else:
            d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED,
                      outline=WHITE, width=1)
            label = str(dot["n"])
            d.text((cx - d.textlength(label, font=num_font) / 2, cy - 5),
                   label, font=num_font, fill=WHITE)


# ---------------------------------------------------------------- page

def render(stories, out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, W, 4], fill=RED)

    # masthead
    f_mast = _font(SANS_B, 19)
    d.text((24, 10), stories["title"], font=f_mast, fill=RED)
    f_note = _font(SANS_B, 12)
    note = stories["masthead_note"]
    d.text((1000 - d.textlength(note, font=f_note), 14), note, font=f_note,
           fill=INK)
    d.line([24, 36, 1000, 36], fill=INK, width=2)

    # date headline
    f_date = _font(SERIF_B, 62)
    date = stories["date"]
    d.text(((W - d.textlength(date, font=f_date)) / 2, 40), date,
           font=f_date, fill=INK)
    f_sub = _font(SERIF_I, 17)
    sub = stories["subhead"]
    d.text(((W - d.textlength(sub, font=f_sub)) / 2, 108), sub, font=f_sub,
           fill=DARKRED)
    d.line([24, 132, 1000, 132], fill=LINE, width=1)

    # numbers strip
    nums = stories["numbers"]
    cell = 976 / len(nums)
    f_num = _font(SERIF_B, 28)
    f_lab = _font(SANS, 9)
    for i, item in enumerate(nums):
        cx = 24 + cell * i
        v, lab = item["v"], item["l"]
        d.text((cx + (cell - d.textlength(v, font=f_num)) / 2, 138), v,
               font=f_num, fill=RED)
        d.text((cx + (cell - d.textlength(lab, font=f_lab)) / 2, 168), lab,
               font=f_lab, fill=GRAY)
        if i:
            d.line([cx, 140, cx, 178], fill=LINE, width=1)
    d.line([24, 182, 1000, 182], fill=LINE, width=1)

    # region bar
    total = sum(c for _, c in stories["regions"])
    rx = 24
    f_reg = _font(SANS_B, 10)
    for name, count in stories["regions"]:
        seg = 976 * count / total
        d.rectangle([rx, 186, rx + seg, 206],
                    fill=REGION_FILL.get(name, GRAY))
        label = "%s %d" % (name, count)
        d.text((rx + (seg - d.textlength(label, font=f_reg)) / 2, 191),
               label, font=f_reg, fill=WHITE)
        rx += seg

    # features
    fx = [24, 353, 682]
    fw = 317
    for i, feat in enumerate(stories["features"]):
        x = fx[i]
        y = 210
        d.rectangle([x, y, x + fw, y + 28], fill=RED)
        f_ban = _font(SANS_B, 16)
        d.text((x + 10, y + 6), feat["banner"], font=f_ban, fill=WHITE)
        f_chip = _font(SANS, 11)
        chip = feat["chip"]
        cw = d.textlength(chip, font=f_chip) + 18
        cx0 = x + (fw - cw) / 2
        d.rounded_rectangle([cx0, y + 32, cx0 + cw, y + 52], radius=9,
                            fill=WHITE, outline=LINE, width=1)
        d.text((cx0 + 9, y + 37), chip, font=f_chip, fill=INK)
        ART[feat["art"]](d, x, y + 56, fw, 76)
        ky = y + 136
        f_kick = _font(SANS_B, 10)
        d.text((x, ky), "%d · %s" % (feat["n"], feat["kicker"]), font=f_kick,
               fill=RED)
        tag_pill(d, x + fw, ky - 1, feat["tag"])
        f_head, lines = fit_lines(d, feat["headline"], SERIF_B, 23, 19,
                                  fw, 2)
        ly = ky + 15
        for line in lines:
            d.text((x, ly), line, font=f_head, fill=INK)
            ly += 25
        f_deck = _font(SANS, 12)
        dlines = wrap(d, feat["deck"], f_deck, fw)[:2]
        ly = ky + 15 + 50
        for line in dlines:
            d.text((x, ly), line, font=f_deck, fill=INK)
            ly += 14
        f_src = _font(SANS_I, 10)
        d.text((x, ky + 15 + 50 + 28), feat["source"], font=f_src,
               fill=GRAY)

    # the day in ten
    d.line([24, 452, 1000, 452], fill=INK, width=2)
    f_sec = _font(SANS_B, 13)
    d.text((24, 456), "THE DAY IN TEN — THE STORIES THAT MOVED THE WORLD",
           font=f_sec, fill=INK)

    # medium grid
    for i, cell in enumerate(stories["medium"]):
        col, row = i % 5, i // 5
        x = 24 + col * 197
        y = 476 + row * 136
        w = 189
        d.rectangle([x, y, x + w, y + 20], fill=RED)
        f_ban = _font(SANS_B, 12)
        d.text((x + 6, y + 4), cell["banner"], font=f_ban, fill=WHITE)
        ART[cell["art"]](d, x, y + 20, w, 34)
        ky = y + 56
        f_kick = _font(SANS_B, 9)
        d.text((x, ky), "%d · %s" % (cell["n"], cell["kicker"]),
               font=f_kick, fill=RED)
        tag_pill(d, x + w, ky - 1, cell["tag"])
        f_head, lines = fit_lines(d, cell["headline"], SERIF_B, 15, 12,
                                  w, 2)
        ly = ky + 13
        for line in lines:
            d.text((x, ly), line, font=f_head, fill=INK)
            ly += 17
        f_deck = _font(SANS, 10)
        dlines = wrap(d, cell["deck"], f_deck, w)[:2]
        ly = ky + 13 + 34
        for line in dlines:
            d.text((x, ly), line, font=f_deck, fill=INK)
            ly += 12
        f_src = _font(SANS_I, 9)
        d.text((x, ky + 13 + 34 + 24), cell["source"], font=f_src,
               fill=GRAY)

    # map + also headers
    d.line([24, 748, 1000, 748], fill=INK, width=2)
    d.text((24, 752), "WHERE IT HAPPENED", font=f_sec, fill=INK)
    d.text((440, 752), "ALSO ON TUESDAY — 20 MORE STORIES", font=f_sec,
           fill=INK)
    draw_map(d, 24, 770, 400, 126, stories["map_dots"])
    f_cap = _font(SANS_I, 9)
    d.text((24, 900), "Each number is the story with that number on this "
           "page; 9 and 12 sit beside their dots.", font=f_cap, fill=GRAY)

    # also list
    f_also = _font(SANS, 10)
    f_also_b = _font(SANS_B, 10)
    for i, line in enumerate(stories["also"]):
        col, row = i % 2, i // 2
        ax = 440 + col * 284
        ay = 770 + row * 13
        num, rest = line.split(" ", 1)
        d.text((ax, ay), num, font=f_also_b, fill=RED)
        d.text((ax + d.textlength(num + " ", font=f_also_b), ay), rest,
               font=f_also, fill=INK)

    # date check
    d.rectangle([24, 918, 1000, 972], outline=RED, width=2, fill=CREAMBOX)
    f_dc = _font(SANS, 11)
    f_dc_b = _font(SANS_B, 11)
    sentences = stories["datecheck"].split(". ")
    d.text((32, 924), "DATE CHECK", font=f_dc_b, fill=RED)
    lx = 32 + d.textlength("DATE CHECK  ", font=f_dc_b)
    ly = 924
    for j, s in enumerate(sentences):
        s = s if s.endswith(".") else s + "."
        if j == 0:
            d.text((lx, ly), s, font=f_dc, fill=INK)
        else:
            d.text((32, ly), s, font=f_dc, fill=INK)
        ly += 14
    # if the first sentence wrapped, it would collide; sentences are short
    # enough to fit one line each at 11px across 936px.

    # footer
    f_foot = _font(SANS_B, 9)
    d.text((24, 978), stories["how_checked"], font=f_foot, fill=INK)
    f_note2 = _font(SANS_I, 9)
    d.text((24, 990), stories["footer_note"], font=f_note2, fill=GRAY)

    # bottom bar
    d.rectangle([0, 1002, W, H], fill=DARKNAVY)
    f_bot = _font(SANS_B, 12)
    d.text((24, 1008), stories["title"], font=f_bot, fill=WHITE)
    tail = "TUESDAY 24 NOVEMBER 2026 · ONE PAGE"
    d.text((1000 - d.textlength(tail, font=f_bot), 1008), tail,
           font=f_bot, fill=WHITE)

    img.save(out_path, "PNG")
    return out_path


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "stories.json"), encoding="utf-8") as f:
        stories = json.load(f)
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here,
                                                             "entry.png")
    render(stories, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
