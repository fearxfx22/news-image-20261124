"""Detailed illustration scenes for news-image v2.

All artwork is flat vector drawing on the Canvas: layered silhouettes,
gradients, lit windows, suns and moons, in the style of the 22 Nov entry's
rich feature panels. Written fresh for the v2 build.
"""
import math

# --------------------------------------------------------------------------
# Feature scenes (each ~309 x 77 px)
# --------------------------------------------------------------------------

def draw_chip_scene(c, x, y, w, h):
    """Nvidia: a silicon chip on a circuit board with a rising chart."""
    c.gradient_rect(x, y, w, h, (10, 30, 60), (22, 64, 110))
    # faint board grid
    for gx in range(x + 14, x + w, 26):
        c.vline(gx, y + 4, h - 8, (32, 66, 104), 1)
    for gy in range(y + 12, y + h, 18):
        c.hline(x + 4, gy, w - 8, (32, 66, 104), 1)
    # circuit traces radiating from the chip
    cx0, cy0 = x + w * 0.42, y + h * 0.52
    for (ex, ey, col) in [
            (x + 8, y + 8, (212, 175, 55)), (x + w - 10, y + 10, (90, 200, 130)),
            (x + 12, y + h - 10, (212, 175, 55)), (x + w - 8, y + h - 8, (90, 200, 130)),
            (x + w * 0.55, y + 6, (212, 175, 55)), (x + w * 0.15, y + h - 6, (90, 200, 130))]:
        c.polyline([(cx0, cy0), ((cx0 + ex) / 2, (cy0 + ey) / 2), (ex, ey)], col, 2)
        c.circle(int(ex), int(ey), 3, col)
    # small board components
    for (bx, by, bw, bh, col) in [
            (x + w * 0.08, y + h * 0.14, 14, 7, (200, 170, 60)),
            (x + w * 0.82, y + h * 0.62, 14, 7, (200, 170, 60)),
            (x + w * 0.72, y + h * 0.10, 10, 10, (150, 155, 165)),
            (x + w * 0.06, y + h * 0.66, 10, 10, (150, 155, 165))]:
        c.fill_rect(bx, by, bw, bh, col)
    # the chip: body, pins on four sides, die with circuit grid
    bx, by = x + w * 0.30, y + h * 0.18
    bw, bh = w * 0.34, h * 0.64
    for px in range(int(bx) + 6, int(bx + bw) - 4, 11):
        c.fill_rect(px, int(by) - 6, 5, 6, (190, 195, 205))
        c.fill_rect(px, int(by + bh), 5, 6, (190, 195, 205))
    for py in range(int(by) + 6, int(by + bh) - 4, 11):
        c.fill_rect(int(bx) - 6, py, 6, 5, (190, 195, 205))
        c.fill_rect(int(bx + bw), py, 6, 5, (190, 195, 205))
    c.fill_rect(bx, by, bw, bh, (42, 46, 54))
    c.fill_rect(bx, by, bw, 3, (110, 116, 128))
    dx, dy = bx + bw * 0.16, by + bh * 0.16
    dw, dh = bw * 0.68, bh * 0.68
    c.fill_rect(dx, dy, dw, dh, (24, 28, 38))
    for gx in range(int(dx) + 5, int(dx + dw) - 3, 8):
        c.vline(gx, int(dy) + 3, int(dh) - 6, (60, 90, 130), 1)
    for gy in range(int(dy) + 5, int(dy + dh) - 3, 8):
        c.hline(int(dx) + 3, gy, int(dw) - 6, (60, 90, 130), 1)
    c.fill_rect(dx + dw * 0.38, dy + dh * 0.38, dw * 0.24, dh * 0.24, (90, 200, 130))
    # rising chart line with arrow
    pts = [(x + w * 0.62, y + h * 0.86), (x + w * 0.70, y + h * 0.72),
           (x + w * 0.76, y + h * 0.76), (x + w * 0.84, y + h * 0.50),
           (x + w * 0.90, y + h * 0.54), (x + w * 0.97, y + h * 0.24)]
    c.polyline(pts, (80, 220, 130), 3)
    ex, ey = pts[-1]
    c.polygon([(ex, ey), (ex - 11, ey + 2), (ex - 3, ey + 9)], (80, 220, 130))
    for (px, py) in pts[1:-1]:
        c.circle(int(px), int(py), 2, (220, 240, 200))


def draw_ship_scene(c, x, y, w, h):
    """Libya: a corvette at dusk, drones overhead, smoke and fire."""
    c.gradient_rect(x, y, w, h * 0.55, (127, 168, 201), (240, 192, 96))
    c.circle(int(x + w * 0.80), int(y + h * 0.22), 13, (250, 220, 140))
    c.circle(int(x + w * 0.80), int(y + h * 0.22), 17, (240, 200, 110))
    # distant headland
    c.polygon([(x, y + h * 0.55), (x + w * 0.16, y + h * 0.40),
               (x + w * 0.30, y + h * 0.55)], (90, 110, 130))
    # sea
    c.gradient_rect(x, y + h * 0.55, w, h * 0.45, (27, 74, 107), (14, 42, 68))
    for wy in [0.62, 0.72, 0.84, 0.94]:
        yy = int(y + h * wy)
        c.polyline([(x + 6, yy), (x + w * 0.3, yy - 2), (x + w * 0.6, yy + 1),
                    (x + w - 8, yy - 2)], (140, 180, 205), 1)
    # 7 drones in the sky with trails
    drones = [(0.10, 0.10), (0.22, 0.06), (0.34, 0.14), (0.46, 0.08),
              (0.58, 0.16), (0.68, 0.06), (0.88, 0.10)]
    for (fx, fy) in drones:
        dx, dy = int(x + w * fx), int(y + h * fy)
        c.polyline([(dx - 12, dy + 4), (dx, dy)], (90, 105, 125), 1)
        c.polygon([(dx - 4, dy), (dx + 4, dy), (dx, dy + 3)], (40, 45, 55))
        c.fill_rect(dx - 1, dy - 3, 2, 3, (40, 45, 55))
    # corvette: hull, bow, superstructure, mast, radar
    hx, hy = x + w * 0.18, y + h * 0.62
    hw, hh = w * 0.58, h * 0.16
    c.polygon([(hx, hy), (hx + hw * 0.92, hy), (hx + hw, hy + hh * 0.55),
               (hx + hw * 0.88, hy + hh), (hx + hw * 0.06, hy + hh),
               (hx, hy + hh * 0.55)], (96, 102, 110))
    c.fill_rect(hx, hy, hw * 0.92, 3, (140, 146, 154))
    c.fill_rect(hx + hw * 0.30, hy - h * 0.13, hw * 0.22, h * 0.13, (120, 126, 134))
    c.fill_rect(hx + hw * 0.55, hy - h * 0.20, hw * 0.10, h * 0.20, (120, 126, 134))
    c.vline(int(hx + hw * 0.60), int(hy - h * 0.34), int(h * 0.16), (70, 76, 84), 2)
    c.fill_rect(int(hx + hw * 0.56), int(hy - h * 0.36), int(hw * 0.09), 3, (70, 76, 84))
    for wx in range(int(hx) + 8, int(hx + hw * 0.9), 14):
        c.fill_rect(wx, int(hy) + 4, 6, 4, (200, 210, 220))
    # wake foam
    c.polygon([(hx + hw * 0.92, hy + hh), (hx + w * 0.24, hy + hh + 3),
               (hx + w * 0.20, hy + hh + 7), (hx + hw * 0.86, hy + hh + 4)],
              (190, 215, 230))
    # fire glow + smoke at the stern
    c.circle(int(hx + hw * 0.12), int(hy + 2), 8, (240, 140, 50))
    c.circle(int(hx + hw * 0.12), int(hy + 2), 4, (250, 210, 90))
    for (sx, sy, sr, col) in [
            (0.22, 0.42, 9, (110, 110, 120)), (0.25, 0.30, 12, (130, 130, 140)),
            (0.29, 0.18, 10, (150, 150, 160)), (0.33, 0.08, 7, (165, 165, 175))]:
        c.circle(int(x + w * sx), int(y + h * sy), sr, col)


def draw_skyline_scene(c, x, y, w, h):
    """Gaza: a dusk skyline with lit windows, smoke and a low sun."""
    c.gradient_rect(x, y, w, h, (42, 23, 69), (140, 70, 60))
    # stars
    for (sx, sy) in [(0.06, 0.10), (0.16, 0.06), (0.28, 0.12), (0.40, 0.05),
                      (0.52, 0.10), (0.64, 0.06), (0.74, 0.12), (0.92, 0.06),
                      (0.86, 0.16), (0.34, 0.20), (0.58, 0.20)]:
        c.fill_rect(int(x + w * sx), int(y + h * sy), 2, 2, (230, 220, 200))
    # low sun
    c.circle(int(x + w * 0.84), int(y + h * 0.52), 16, (240, 150, 55))
    c.circle(int(x + w * 0.84), int(y + h * 0.52), 11, (250, 190, 90))
    # searchlight beams
    c.polygon([(x + w * 0.30, y + h), (x + w * 0.36, y + h),
               (x + w * 0.52, y + h * 0.10)], (235, 225, 180))
    c.polygon([(x + w * 0.62, y + h), (x + w * 0.66, y + h),
               (x + w * 0.78, y + h * 0.22)], (235, 225, 180))
    # buildings with lit windows, back row then front row
    back = [(0.00, 0.42, 0.10, 0.58), (0.12, 0.34, 0.09, 0.66),
            (0.24, 0.46, 0.11, 0.54), (0.38, 0.38, 0.08, 0.62),
            (0.48, 0.44, 0.10, 0.56), (0.60, 0.36, 0.09, 0.64),
            (0.71, 0.44, 0.10, 0.56), (0.83, 0.38, 0.09, 0.62),
            (0.94, 0.46, 0.06, 0.54)]
    for (bx, by, bw, bh) in back:
        c.fill_rect(x + w * bx, y + h * by, w * bw, h * bh, (48, 30, 62))
    front = [(0.05, 0.58, 0.13, 0.42), (0.20, 0.50, 0.11, 0.50),
             (0.33, 0.60, 0.12, 0.40), (0.47, 0.52, 0.10, 0.48),
             (0.59, 0.62, 0.12, 0.38), (0.73, 0.54, 0.11, 0.46),
             (0.86, 0.60, 0.13, 0.40)]
    for (bx, by, bw, bh) in front:
        c.fill_rect(x + w * bx, y + h * by, w * bw, h * bh, (22, 12, 34))
    # lit windows on front buildings
    for (bx, by, bw, bh) in front:
        for wy in range(int(y + h * by) + 4, int(y + h), 9):
            for wx in range(int(x + w * bx) + 4, int(x + w * (bx + bw)) - 4, 9):
                if (wx * 7 + wy * 13) % 5 < 3:
                    c.fill_rect(wx, wy, 3, 4, (255, 200, 80))
    # minaret + dome
    c.fill_rect(int(x + w * 0.155), int(y + h * 0.30), 6, int(h * 0.70), (22, 12, 34))
    c.polygon([(x + w * 0.155 - 2, y + h * 0.30), (x + w * 0.155 + 8, y + h * 0.30),
               (x + w * 0.155 + 3, y + h * 0.20)], (22, 12, 34))
    c.ellipse(int(x + w * 0.44), int(y + h * 0.60), 10, 6, (22, 12, 34))
    # smoke plumes
    for (sx, sy, sr, col) in [
            (0.26, 0.44, 8, (130, 118, 132)), (0.28, 0.32, 11, (145, 133, 147)),
            (0.31, 0.20, 9, (160, 148, 162)), (0.66, 0.48, 7, (130, 118, 132)),
            (0.68, 0.36, 10, (145, 133, 147)), (0.70, 0.24, 8, (160, 148, 162))]:
        c.circle(int(x + w * sx), int(y + h * sy), sr, col)
    # birds
    for (bx, by) in [(0.45, 0.14), (0.50, 0.10), (0.55, 0.16)]:
        px, py = int(x + w * bx), int(y + h * by)
        c.polyline([(px - 4, py), (px, py - 2), (px + 4, py)], (30, 20, 40), 1)


# --------------------------------------------------------------------------
# Medium-cell motifs (each ~190 x 38 px)
# --------------------------------------------------------------------------

def _blast(c, x, y, w, h):
    c.fill_rect(x, y, w, h, (216, 201, 160))
    cx, cy = x + w * 0.82, y + h * 0.30
    for i in range(8):
        ang = math.pi * i / 4.0
        c.polyline([(cx, cy), (cx + 13 * math.cos(ang), cy + 13 * math.sin(ang))],
                   (240, 150, 50), 2)
    c.circle(int(cx), int(cy), 7, (240, 150, 50))
    for (bx, bw, bh) in [(0.06, 0.22, 0.52), (0.30, 0.20, 0.66), (0.52, 0.20, 0.44)]:
        c.fill_rect(x + w * bx, y + h - h * bh, w * bw, h * bh, (70, 70, 78))
        for wy in range(int(y + h - h * bh) + 3, int(y + h) - 3, 7):
            for wx in range(int(x + w * bx) + 3, int(x + w * (bx + bw)) - 3, 8):
                c.fill_rect(wx, wy, 3, 3, (255, 200, 80))


def _tanker(c, x, y, w, h):
    c.gradient_rect(x, y, w, h * 0.55, (190, 215, 230), (220, 232, 238))
    c.fill_rect(x, y + h * 0.55, w, h * 0.45, (28, 90, 130))
    c.polyline([(x + 6, y + h * 0.66), (x + w * 0.4, y + h * 0.64),
                (x + w * 0.7, y + h * 0.67), (x + w - 6, y + h * 0.65)],
               (160, 200, 225), 1)
    hx, hy = x + w * 0.14, y + h * 0.42
    c.polygon([(hx, hy), (hx + w * 0.62, hy), (hx + w * 0.58, hy + h * 0.20),
               (hx + w * 0.04, hy + h * 0.20)], (178, 52, 48))
    c.fill_rect(hx + w * 0.40, hy - h * 0.16, w * 0.12, h * 0.16, (235, 235, 235))
    c.fill_rect(hx + w * 0.52, hy - h * 0.10, 3, h * 0.10, (120, 120, 120))
    for (mx, my) in [(0.80, 0.30), (0.88, 0.20), (0.72, 0.16)]:
        c.circle(int(x + w * mx), int(y + h * my), 3, (40, 45, 55))
        c.fill_rect(int(x + w * mx) - 4, int(y + h * my), 9, 1, (40, 45, 55))
        c.fill_rect(int(x + w * mx), int(y + h * my) - 4, 1, 9, (40, 45, 55))


def _satellite(c, x, y, w, h):
    c.fill_rect(x, y, w, h, (12, 24, 52))
    for (sx, sy) in [(0.08, 0.2), (0.2, 0.12), (0.85, 0.15), (0.92, 0.35),
                      (0.05, 0.6), (0.9, 0.65), (0.4, 0.08)]:
        c.fill_rect(int(x + w * sx), int(y + h * sy), 2, 2, (230, 230, 220))
    cx, cy = x + w * 0.50, y + h * 0.50
    c.ellipse(cx, cy, w * 0.46, h * 0.34, (12, 24, 52))
    for ang in [0.5, 1.1, 2.0, 2.8, 3.6, 4.4, 5.2]:
        ex = cx + math.cos(ang) * w * 0.44
        ey = cy + math.sin(ang) * h * 0.30
        c.fill_rect(int(ex), int(ey), 2, 2, (150, 170, 200))
    c.polygon([(cx - 22, cy - 8), (cx - 8, cy - 8), (cx - 8, cy + 8),
               (cx - 22, cy + 8)], (60, 100, 170))
    c.polygon([(cx + 8, cy - 8), (cx + 22, cy - 8), (cx + 22, cy + 8),
               (cx + 8, cy + 8)], (60, 100, 170))
    c.fill_rect(cx - 8, cy - 6, 16, 12, (235, 235, 235))
    c.fill_rect(cx - 3, cy - 12, 6, 6, (220, 220, 220))


def _rocket(c, x, y, w, h):
    c.gradient_rect(x, y, w, h, (200, 222, 235), (245, 240, 220))
    c.circle(int(x + w * 0.82), int(y + h * 0.22), 7, (250, 210, 90))
    rx, ry = x + w * 0.42, y + h * 0.14
    c.polygon([(rx + 8, ry), (rx + 14, ry + 10), (rx + 2, ry + 10)], (200, 60, 50))
    c.fill_rect(rx, ry + 10, 16, 16, (235, 235, 235))
    c.fill_rect(rx, ry + 10, 16, 3, (200, 60, 50))
    c.polygon([(rx, ry + 26), (rx + 16, ry + 26), (rx + 8, ry + 36)], (240, 140, 50))
    c.polygon([(rx + 2, ry + 34), (rx + 14, ry + 34), (rx + 8, ry + 40)], (250, 210, 90))
    c.circle(int(rx + 8), int(ry + 16), 3, (60, 120, 200))
    for (sx, sy, sr) in [(0.30, 0.72, 5), (0.36, 0.82, 7), (0.44, 0.92, 6)]:
        c.circle(int(x + w * sx), int(y + h * sy), sr, (220, 220, 215))
    c.polygon([(x + w * 0.62, y + h), (x + w * 0.78, y + h),
               (x + w * 0.86, y + h * 0.62), (x + w * 0.70, y + h * 0.62)],
              (90, 110, 80))


def _bars(c, x, y, w, h):
    c.fill_rect(x, y, w, h, (250, 248, 240))
    vals = [(0.18, 0.62, (30, 60, 110), '78.9', 'US'),
            (0.44, 0.56, (178, 52, 48), '73.6', 'CN'),
            (0.70, 0.34, (46, 125, 50), '40.5', 'IN')]
    for (fx, fh, col, v, lab) in vals:
        bx = x + w * fx
        bh = (h - 18) * (fh / 0.62)
        c.fill_rect(bx, y + 10, w * 0.16, bh, col)
        c.draw_text(c.font('fonts/LiberationSans-Bold.ttf'), 8, v,
                    bx + w * 0.08, y + 8, (30, 30, 30), align='center')
        c.draw_text(c.font('fonts/LiberationSans-Bold.ttf'), 8, lab,
                    bx + w * 0.08, y + h - 2, (30, 30, 30), align='center')


def _mountains(c, x, y, w, h):
    c.gradient_rect(x, y, w, h, (190, 215, 230), (235, 240, 235))
    c.circle(int(x + w * 0.80), int(y + h * 0.24), 7, (250, 210, 90))
    c.polygon([(x + w * 0.02, y + h), (x + w * 0.30, y + h * 0.30),
               (x + w * 0.58, y + h)], (90, 130, 80))
    c.polygon([(x + w * 0.30, y + h * 0.30), (x + w * 0.36, y + h * 0.42),
               (x + w * 0.24, y + h * 0.42)], (245, 245, 240))
    c.polygon([(x + w * 0.42, y + h), (x + w * 0.68, y + h * 0.18),
               (x + w * 0.96, y + h)], (60, 100, 60))
    c.polygon([(x + w * 0.68, y + h * 0.18), (x + w * 0.74, y + h * 0.32),
               (x + w * 0.62, y + h * 0.32)], (245, 245, 240))


def _factory(c, x, y, w, h):
    c.gradient_rect(x, y, w, h, (210, 210, 205), (235, 232, 225))
    c.fill_rect(x + w * 0.10, y + h * 0.45, w * 0.60, h * 0.55, (110, 110, 112))
    c.polygon([(x + w * 0.10, y + h * 0.45), (x + w * 0.22, y + h * 0.28),
               (x + w * 0.34, y + h * 0.45), (x + w * 0.46, y + h * 0.28),
               (x + w * 0.58, y + h * 0.45), (x + w * 0.70, y + h * 0.45)],
              (90, 90, 92))
    c.fill_rect(x + w * 0.74, y + h * 0.18, w * 0.07, h * 0.82, (90, 90, 92))
    c.fill_rect(x + w * 0.86, y + h * 0.28, w * 0.07, h * 0.72, (90, 90, 92))
    c.polygon([(x + w * 0.74, y + h * 0.18), (x + w * 0.81, y + h * 0.18),
               (x + w * 0.775, y + h * 0.02)], (240, 140, 50))
    c.polygon([(x + w * 0.86, y + h * 0.28), (x + w * 0.93, y + h * 0.28),
               (x + w * 0.895, y + h * 0.12)], (240, 140, 50))
    for wx in range(int(x + w * 0.14), int(x + w * 0.66), 14):
        c.fill_rect(wx, int(y + h * 0.58), 7, 8, (250, 200, 80))


def _scales(c, x, y, w, h):
    c.fill_rect(x, y, w, h, (240, 232, 210))
    cx = x + w * 0.50
    c.fill_rect(cx - 2, y + h * 0.14, 4, h * 0.62, (90, 70, 40))
    c.fill_rect(cx - 12, y + h * 0.76, 24, 3, (90, 70, 40))
    c.fill_rect(cx - w * 0.34, y + h * 0.16, w * 0.68, 3, (90, 70, 40))
    for sgn in (-1, 1):
        px = cx + sgn * w * 0.30
        c.vline(int(px), int(y + h * 0.19), int(h * 0.24), (90, 70, 40), 1)
        c.polygon([(px - 12, y + h * 0.44), (px + 12, y + h * 0.44),
                   (px, y + h * 0.62)], (180, 150, 60))
        c.fill_rect(px - 12, y + h * 0.44, 24, 2, (120, 95, 40))
    c.circle(int(cx), int(y + h * 0.14), 4, (180, 150, 60))


def _columns(c, x, y, w, h):
    c.fill_rect(x, y, w, h, (238, 234, 222))
    c.polygon([(x + w * 0.08, y + h * 0.42), (x + w * 0.50, y + h * 0.16),
               (x + w * 0.92, y + h * 0.42)], (150, 140, 115))
    c.fill_rect(x + w * 0.08, y + h * 0.42, w * 0.84, 3, (120, 110, 85))
    for fx in [0.16, 0.36, 0.56, 0.76]:
        c.fill_rect(x + w * fx, y + h * 0.46, w * 0.05, h * 0.34, (190, 180, 150))
    c.fill_rect(x + w * 0.06, y + h * 0.80, w * 0.88, 3, (120, 110, 85))
    c.fill_rect(x + w * 0.04, y + h * 0.86, w * 0.92, 3, (120, 110, 85))


def _cricket(c, x, y, w, h):
    c.fill_rect(x, y, w, h, (110, 160, 90))
    c.fill_rect(x + w * 0.10, y + h * 0.30, w * 0.80, h * 0.46, (200, 180, 120))
    c.hline(int(x + w * 0.10), int(y + h * 0.30), int(w * 0.80), (255, 255, 255), 1)
    c.hline(int(x + w * 0.10), int(y + h * 0.76), int(w * 0.80), (255, 255, 255), 1)
    for sx in [0.20, 0.24, 0.28]:
        c.fill_rect(int(x + w * sx), int(y + h * 0.40), 2, int(h * 0.22), (240, 230, 200))
    for sx in [0.72, 0.76, 0.80]:
        c.fill_rect(int(x + w * sx), int(y + h * 0.40), 2, int(h * 0.22), (240, 230, 200))
    c.circle(int(x + w * 0.56), int(y + h * 0.55), 5, (178, 52, 48))
    c.fill_rect(int(x + w * 0.56) - 5, int(y + h * 0.55), 10, 1, (255, 255, 255))


MEDIUM_ART = {
    'blast': _blast, 'tanker': _tanker, 'satellite': _satellite,
    'rocket': _rocket, 'bars': _bars, 'mountains': _mountains,
    'factory': _factory, 'scales': _scales, 'columns': _columns,
    'cricket': _cricket,
}


# --------------------------------------------------------------------------
# World map (equirectangular, lon/lat polygons)
# --------------------------------------------------------------------------

MAP_LAND = [
    # North America
    [(-168, 66), (-158, 58), (-152, 60), (-140, 60), (-135, 58), (-130, 54),
     (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-108, 24), (-105, 20),
     (-97, 16), (-92, 15), (-86, 13), (-83, 9), (-79, 9), (-77, 7), (-80, 9),
     (-83, 12), (-88, 15), (-91, 19), (-96, 19), (-97, 26), (-93, 30),
     (-89, 30), (-84, 30), (-81, 26), (-80, 32), (-76, 35), (-74, 40),
     (-70, 42), (-68, 45), (-65, 44), (-60, 47), (-55, 47), (-60, 52),
     (-64, 58), (-68, 58), (-72, 62), (-78, 62), (-82, 66), (-86, 66),
     (-92, 66), (-95, 69), (-100, 69), (-110, 68), (-120, 69), (-128, 70),
     (-135, 69), (-145, 70), (-155, 71), (-162, 70), (-166, 68)],
    # Greenland
    [(-58, 64), (-52, 60), (-44, 60), (-40, 64), (-32, 68), (-22, 70),
     (-25, 74), (-35, 77), (-50, 76), (-58, 74), (-60, 70)],
    # South America
    [(-79, 9), (-77, 4), (-80, 1), (-81, -4), (-80, -8), (-77, -12),
     (-72, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50),
     (-70, -54), (-66, -55), (-65, -50), (-65, -45), (-62, -41), (-58, -34),
     (-52, -33), (-48, -28), (-41, -23), (-39, -17), (-35, -9), (-35, -6),
     (-40, -3), (-44, -2), (-50, 0), (-52, 4), (-58, 6), (-62, 9), (-68, 11),
     (-72, 12), (-76, 10)],
    # Africa
    [(-17, 15), (-16, 20), (-15, 27), (-10, 31), (-6, 33), (-2, 35),
     (3, 37), (10, 37), (11, 34), (15, 32), (20, 32), (25, 32), (30, 31),
     (32, 31), (34, 28), (36, 28), (38, 22), (39, 18), (41, 12), (44, 11),
     (48, 11), (51, 12), (51, 10), (48, 5), (44, 0), (41, -2), (40, -8),
     (39, -13), (36, -18), (33, -22), (32, -26), (31, -29), (28, -33),
     (25, -34), (20, -35), (18, -33), (17, -29), (15, -27), (13, -22),
     (12, -17), (13, -12), (13, -8), (12, -4), (9, -1), (9, 4), (6, 4),
     (3, 6), (-3, 5), (-8, 4), (-12, 8), (-15, 11)],
    # Eurasia
    [(-10, 36), (-9, 38), (-9, 43), (-4, 44), (-2, 47), (-4, 48), (-2, 50),
     (0, 51), (2, 51), (4, 53), (7, 54), (8, 57), (10, 59), (13, 56),
     (18, 56), (21, 55), (24, 58), (26, 59), (28, 61), (30, 62), (32, 65),
     (35, 66), (40, 67), (45, 68), (50, 69), (55, 69), (60, 69), (66, 70),
     (72, 72), (78, 73), (85, 74), (92, 75), (100, 76), (108, 74),
     (115, 73), (122, 72), (130, 71), (138, 72), (145, 72), (152, 70),
     (158, 69), (162, 66), (166, 66), (170, 66), (173, 64), (170, 60),
     (163, 60), (159, 56), (156, 52), (150, 59), (144, 58), (142, 54),
     (141, 50), (140, 45), (138, 42), (135, 43), (132, 42), (130, 38),
     (129, 35), (127, 35), (126, 38), (122, 37), (120, 32), (120, 28),
     (118, 25), (114, 22), (110, 20), (108, 18), (108, 12), (106, 10),
     (104, 9), (102, 8), (100, 7), (98, 10), (97, 14), (94, 17), (92, 21),
     (90, 22), (88, 22), (86, 20), (83, 18), (80, 16), (77, 8), (76, 10),
     (75, 12), (73, 17), (72, 20), (70, 22), (68, 23), (66, 25), (62, 25),
     (58, 25), (56, 26), (54, 26), (52, 26), (50, 29), (48, 30), (47, 30),
     (44, 29), (43, 28), (41, 26), (40, 23), (39, 21), (38, 20), (36, 18),
     (35, 16), (34, 14), (33, 12), (32, 15), (31, 18), (30, 20), (29, 22),
     (28, 27), (27, 30), (27, 33), (26, 36), (23, 36), (22, 37), (20, 40),
     (18, 40), (15, 42), (14, 44), (12, 44), (10, 44), (8, 44), (6, 43),
     (3, 43), (0, 40), (-1, 38), (-3, 36), (-6, 35), (-8, 34)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (-1, 51)],
    # Japan
    [(130, 31), (132, 33), (134, 34), (137, 35), (139, 37), (141, 39),
     (142, 42), (144, 44), (141, 45), (140, 41), (138, 38), (135, 35),
     (132, 33)],
    # Australia
    [(113, -22), (114, -28), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (144, -38), (147, -39),
     (150, -37), (153, -32), (153, -27), (150, -23), (146, -19), (142, -15),
     (142, -11), (138, -12), (136, -12), (135, -15), (132, -12), (130, -13),
     (127, -14), (124, -15), (122, -17), (119, -20), (116, -21)],
    # Indonesia islands (rough blobs)
    [(95, 5), (98, 3), (100, 0), (102, -3), (100, -5), (96, -2), (94, 2)],
    [(105, -6), (108, -7), (112, -7), (114, -8), (112, -10), (108, -9),
     (105, -8)],
    [(119, -8), (122, -9), (125, -9), (124, -11), (120, -10)],
    [(128, -3), (132, -2), (135, -3), (136, -5), (132, -5), (129, -4)],
    # New Zealand
    [(167, -35), (170, -37), (173, -39), (175, -41), (174, -42), (171, -43),
     (168, -45), (167, -43), (168, -40), (166, -37)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24), (44, -25),
     (43, -21), (43, -17)],
]


def draw_map(c, x, y, w, h, dots, font_bold):
    """Equirectangular world map: pale ocean, tan land, numbered red dots."""
    c.fill_rect(x, y, w, h, (191, 211, 224))
    # graticule every 30 degrees
    for lon in range(-150, 181, 30):
        gx = x + (lon + 180) / 360.0 * w
        c.vline(int(gx), y, h, (225, 235, 242), 1)
    for lat in range(-60, 81, 30):
        gy = y + (80 - lat) / 138.0 * h
        c.hline(x, int(gy), w, (225, 235, 242), 1)
    # land
    for poly_ll in MAP_LAND:
        pts = []
        for (lon, lat) in poly_ll:
            px = x + (lon + 180) / 360.0 * w
            py = y + (80 - lat) / 138.0 * h
            pts.append((px, py))
        c.polygon(pts, (216, 190, 133))
    c.rect(x, y, w, h, (120, 120, 110), 1)
    # dots: red circles with white numbers; offset dots (9, 12) get a white
    # box with a red border and red number beside the location
    for d in dots:
        lon, lat = d['lon'], d['lat']
        dx = d.get('dx', 0)
        dy = d.get('dy', 0)
        px = x + (lon + 180) / 360.0 * w + dx
        py = y + (80 - lat) / 138.0 * h + dy
        if dx or dy:
            c.fill_rect(int(px) - 7, int(py) - 7, 14, 14, (255, 255, 255))
            c.rect(int(px) - 7, int(py) - 7, 14, 14, (164, 25, 40), 1)
            c.draw_text(font_bold, 8, str(d['n']), int(px), int(py) + 3,
                        (164, 25, 40), align='center')
        else:
            c.circle(int(px), int(py), 7, (164, 25, 40))
            c.draw_text(font_bold, 8, str(d['n']), int(px), int(py) + 3,
                        (255, 255, 255), align='center')
