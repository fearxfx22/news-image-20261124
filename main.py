"""News-image v2 entrypoint: render "The World in One Day" (24 Nov 2026).

Layout keeps v1's masthead, numbers strip, region bar, feature/medium grids,
map, ALSO list, DATE CHECK and footer exactly where they were; v2 changes
only two things: the three feature panels are redrawn as detailed scenes,
and the "THE DAY IN UTC" timeline strip is restored. All story text comes
from stories.json unchanged. Pure stdlib: no Pillow, no third-party imports.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(HERE)

from draw import Canvas, write_png
import scenes

W, H = 1024, 1024
M = 24
CW = W - 2 * M

CREAM = (244, 236, 214)
INK = (20, 20, 20)
GREY = (90, 90, 85)
RED = (164, 25, 40)
DARKRED = (122, 30, 30)
NAVY = (14, 28, 56)
GOLD = (212, 175, 55)
GREEN = (46, 125, 50)
AMBER = (201, 162, 39)
OFFBLUE = (31, 78, 121)
REGION_COLORS = {
    'AMERICAS': (31, 78, 121), 'EUROPE': (14, 124, 123),
    'ASIA': (166, 124, 0), 'MIDDLE EAST': (164, 25, 40),
    'AFRICA': (106, 61, 154), 'OCEANIA': (46, 125, 50),
    'GLOBAL': (85, 85, 85),
}
TAG_STYLE = {
    'CONFIRMED': (GREEN, (255, 255, 255)),
    'OFFICIAL': (OFFBLUE, (255, 255, 255)),
    'REPORTED': (AMBER, (20, 20, 20)),
    'CLAIM': (RED, (255, 255, 255)),
}

SERIF_B = 'fonts/LiberationSerif-Bold.ttf'
SERIF = 'fonts/LiberationSerif-Regular.ttf'
SERIF_I = 'fonts/LiberationSerif-Italic.ttf'
SANS_B = 'fonts/LiberationSans-Bold.ttf'
SANS = 'fonts/LiberationSans-Regular.ttf'
SANS_I = 'fonts/LiberationSans-Italic.ttf'


def fit_lines(c, font_path, text, max_w, size, max_lines, min_size=8.0):
    """Wrap text, shrinking the font until it fits in max_lines."""
    f = c.font(font_path)
    s = size
    while s > min_size:
        lines = c.wrap(f, s, text, max_w)
        if len(lines) <= max_lines:
            return lines, s
        s -= 0.5
    return c.wrap(f, s, text, max_w), s


def draw_tag(c, x_right, y, tag, size=9.0):
    """Right-aligned tag pill; returns its left x."""
    f = c.font(SANS_B)
    bg, fg = TAG_STYLE.get(tag, (GREY, (255, 255, 255)))
    tw = c.text_width(f, size, tag) + 12
    c.rrect(x_right - tw, y, tw, 14, 3, bg)
    c.draw_text(f, size, tag, x_right - tw / 2.0, y + 10.5, fg, align='center')
    return x_right - tw


def draw_kicker(c, x, y, number, kicker, x_right, size=11.0):
    """Kicker line with right-aligned tag; returns nothing."""
    f = c.font(SANS_B)
    text = '%d \u00b7 %s' % (number, kicker)
    c.draw_text(f, size, text, x, y, RED)


def draw_feature(c, feat, x, w):
    bx = x
    # red banner
    c.fill_rect(bx, 232, w, 26, RED)
    c.draw_text(c.font(SANS_B), 12.5, feat['banner'], bx + 10, 250,
                (255, 255, 255))
    # white chip pill, centred
    f = c.font(SANS)
    chip = feat['chip']
    cw = c.text_width(f, 11, chip) + 22
    cx = bx + (w - cw) / 2.0
    c.rrect(cx, 261, cw, 18, 9, (255, 255, 255))
    c.rect(int(cx), 261, int(cw), 18, (170, 165, 150), 1)
    c.draw_text(f, 11, chip, bx + w / 2.0, 274, INK, align='center')
    # detailed scene
    art = feat['art']
    if art == 'chip':
        scenes.draw_chip_scene(c, bx, 283, w, 72)
    elif art == 'ship':
        scenes.draw_ship_scene(c, bx, 283, w, 72)
    else:
        scenes.draw_skyline_scene(c, bx, 283, w, 72)
    # kicker + tag
    draw_kicker(c, bx, 367, feat['n'], feat['kicker'], bx + w)
    draw_tag(c, bx + w, 355, feat['tag'], 9.0)
    # headline, two lines max
    lines, hs = fit_lines(c, SERIF_B, feat['headline'], w, 21.0, 2, 18.0)
    y = 389
    for ln in lines:
        c.draw_text(c.font(SERIF_B), hs, ln, bx, y, INK)
        y += 22
    # deck, two lines max
    dlines, ds = fit_lines(c, SANS, feat['deck'], w, 12.0, 2, 10.5)
    y = 428
    for ln in dlines:
        c.draw_text(c.font(SANS), ds, ln, bx, y, (50, 50, 50))
        y += 14
    # source
    c.draw_text(c.font(SERIF_I), 11, feat['source'], bx, 459, GREY)


def draw_medium(c, med, x, w, y0):
    bx = x
    # red banner
    c.fill_rect(bx, y0, w, 20, RED)
    c.draw_text(c.font(SANS_B), 10.5, med['banner'], bx + 8, y0 + 15,
                (255, 255, 255))
    # motif art
    art_y = y0 + 23
    art_h = 34 if y0 < 600 else 28
    scenes.MEDIUM_ART[med['art']](c, bx, art_y, w, art_h)
    # kicker + tag
    ky = art_y + art_h + 12
    draw_kicker(c, bx, ky, med['n'], med['kicker'], bx + w, 9.5)
    draw_tag(c, bx + w, ky - 11, med['tag'], 8.0)
    # headline, two lines max
    lines, hs = fit_lines(c, SERIF_B, med['headline'], w, 14.0, 2, 12.5)
    y = ky + 18
    for ln in lines:
        c.draw_text(c.font(SERIF_B), hs, ln, bx, y, INK)
        y += 14
    # deck, two lines max
    dlines, ds = fit_lines(c, SANS, med['deck'], w, 9.0, 2, 8.5)
    y = ky + 18 + 28 + 1
    for ln in dlines:
        c.draw_text(c.font(SANS), ds, ln, bx, y, (50, 50, 50))
        y += 11
    # source
    c.draw_text(c.font(SERIF_I), 8.5, med['source'], bx, y + 11, GREY)


def main():
    with open('stories.json') as f:
        d = json.load(f)
    c = Canvas(W, H, CREAM)

    # top red bar + masthead
    c.fill_rect(0, 0, W, 5, RED)
    c.draw_text(c.font(SANS_B), 15, d['title'], M, 27, RED)
    c.draw_text(c.font(SANS), 10.5, d['masthead_note'], W - M, 26, INK,
                align='right')
    c.hline(M, 33, CW, INK, 1)

    # headline + subhead
    c.draw_text(c.font(SERIF_B), 64, d['date'], W / 2.0, 96, INK,
                align='center')
    c.draw_text(c.font(SERIF_I), 19, d['subhead'], W / 2.0, 118, DARKRED,
                align='center')
    c.hline(M, 126, CW, INK, 1)

    # numbers strip
    col_w = CW / 6.0
    for i, num in enumerate(d['numbers']):
        cx = M + col_w * (i + 0.5)
        c.draw_text(c.font(SERIF_B), 26, num['v'], cx, 158, RED,
                    align='center')
        c.draw_text(c.font(SANS), 9.5, num['l'], cx, 172, (50, 50, 50),
                    align='center')
        if i:
            c.vline(int(M + col_w * i), 132, 40, (170, 165, 150), 1)

    # region bar
    total = sum(n for _, n in d['regions'])
    rx = float(M)
    for name, n in d['regions']:
        seg = CW * n / float(total)
        c.fill_rect(rx, 186, seg + 1, 21, REGION_COLORS[name])
        c.draw_text(c.font(SANS_B), 11, '%s %d' % (name, n),
                    rx + seg / 2.0, 201, (255, 255, 255), align='center')
        rx += seg

    # THE DAY IN UTC strip (restored)
    c.fill_rect(M, 207, CW, 22, NAVY)
    strip_items = ('OVERNIGHT \u2014 Zaporizhzhia flats hit \u00b7 '
                   'TUESDAY \u2014 Kyiv invokes Article 51 \u00b7 '
                   'TODAY \u2014 Gaza strikes kill 7 \u00b7 '
                   '15:00 UTC \u2014 Stories verified to this hour')
    size = 11.0
    while size > 9.0:
        label_w = c.text_width(c.font(SANS_B), size, 'THE DAY IN UTC')
        rest_w = c.text_width(c.font(SANS), size, ' \u00b7 ' + strip_items)
        if label_w + rest_w <= CW - 20:
            break
        size -= 0.5
    lx = M + 10
    c.draw_text(c.font(SANS_B), size, 'THE DAY IN UTC', lx, 222, GOLD)
    c.draw_text(c.font(SANS), size, ' \u00b7 ' + strip_items,
                lx + c.text_width(c.font(SANS_B), size, 'THE DAY IN UTC'),
                222, (255, 255, 255))

    # feature row
    feat_xs = [M, M + 333, M + 666]
    feat_ws = [309, 309, 310]
    for feat, fx, fw in zip(d['features'], feat_xs, feat_ws):
        draw_feature(c, feat, fx, fw)

    # THE DAY IN TEN header
    c.hline(M, 467, CW, INK, 2)
    c.draw_text(c.font(SANS_B), 13,
                'THE DAY IN TEN \u2014 THE STORIES THAT MOVED THE WORLD',
                M, 482, INK)

    # medium grid: two rows of five
    med_xs = [M, 221, 418, 615, 812]
    med_ws = [190, 190, 190, 190, 189]
    for row, y0 in enumerate((489, 632)):
        for j, med in enumerate(d['medium'][row * 5:(row + 1) * 5]):
            draw_medium(c, med, med_xs[j], med_ws[j], y0)

    # bottom rule + headers
    c.hline(M, 768, CW, INK, 2)
    c.draw_text(c.font(SANS_B), 13, 'WHERE IT HAPPENED', M, 784, INK)
    c.draw_text(c.font(SANS_B), 13, 'ALSO ON TUESDAY \u2014 20 MORE STORIES',
                510, 784, INK)

    # map + ALSO list
    scenes.draw_map(c, M, 790, 470, 118, d['map_dots'],
                    c.font(SANS_B))
    also = d['also']
    for i, item in enumerate(also):
        col = 0 if i % 2 == 0 else 1
        row = i // 2
        ax = 510 if col == 0 else 755
        ay = 800 + row * 12
        lead, _, rest = item.partition(': ')
        lead += ':'
        size = 9.5
        while size > 8.0:
            w_lead = c.text_width(c.font(SANS_B), size, lead + ' ')
            w_rest = c.text_width(c.font(SANS), size, rest)
            if w_lead + w_rest <= 235:
                break
            size -= 0.5
        c.draw_text(c.font(SANS_B), size, lead + ' ', ax, ay, RED)
        c.draw_text(c.font(SANS), size, rest,
                    ax + c.text_width(c.font(SANS_B), size, lead + ' '),
                    ay, INK)

    # map caption
    c.draw_text(c.font(SERIF_I), 9,
                'Each number is the story with that number on this page; '
                '9 and 12 sit beside their dots.',
                M, 916, GREY)

    # DATE CHECK box (wrap only the body text: wrap() collapses the
    # double space after the lead, so never slice a wrapped line)
    c.rect(M, 920, CW, 46, RED, 2)
    lead_w = c.text_width(c.font(SANS_B), 10.5, 'DATE CHECK  ')
    dc_lines = c.wrap(c.font(SANS), 10.5, d['datecheck'], CW - 40 - lead_w)
    y = 933
    for k, ln in enumerate(dc_lines[:3]):
        if k == 0:
            c.draw_text(c.font(SANS_B), 10.5, 'DATE CHECK', M + 12, y, RED)
            c.draw_text(c.font(SANS), 10.5, ln, M + 12 + lead_w, y, INK)
        else:
            c.draw_text(c.font(SANS), 10.5, ln, M + 12, y, INK)
        y += 13

    # HOW WE CHECKED + footer note
    c.draw_text(c.font(SANS_B), 10, d['how_checked'], M, 974, INK)
    c.draw_text(c.font(SERIF_I), 9, d['footer_note'], M, 985, GREY)

    # bottom navy bar
    c.fill_rect(0, 1000, W, 24, NAVY)
    c.draw_text(c.font(SANS_B), 11, d['title'], M, 1016, GOLD)
    c.draw_text(c.font(SANS), 10,
                d['date'].upper() + ' \u00b7 ONE PAGE', W - M, 1016,
                (255, 255, 255), align='right')

    # Grader runs with /bot read-only (only /output writable): write the
    # render to argv[1] if given, else /output/entry.png.
    out = sys.argv[1] if len(sys.argv) > 1 else '/output/entry.png'
    out_dir = os.path.dirname(out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    write_png(out, c)
    with open(out, 'rb') as f:
        blob = f.read()
    print('%s sha256 %s size %d' %
          (out, hashlib.sha256(blob).hexdigest(), len(blob)))


if __name__ == '__main__':
    main()
