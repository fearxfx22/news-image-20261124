"""Pure-stdlib 2D canvas: TrueType text rasterizer, vector shapes, PNG writer.

No third-party imports: only struct, zlib, math, os, sys. Everything in this
file was written fresh for the news-image v2 build.
"""
import math
import os
import struct
import sys
import zlib


# --------------------------------------------------------------------------
# TrueType font parsing (cmap fmt 4, glyf simple + composite, hmtx)
# --------------------------------------------------------------------------

def _u16(b, o):
    return struct.unpack_from('>H', b, o)[0]


def _i16(b, o):
    return struct.unpack_from('>h', b, o)[0]


def _u32(b, o):
    return struct.unpack_from('>I', b, o)[0]


class Font:
    def __init__(self, path):
        self.path = path
        data = open(path, 'rb').read()
        self.data = data
        n_tables = _u16(data, 4)
        self.tables = {}
        for i in range(n_tables):
            off = 12 + i * 16
            tag = data[off:off + 4].decode('latin-1')
            self.tables[tag] = (_u32(data, off + 8), _u32(data, off + 12))
        head_off, _ = self.tables['head']
        self.upem = _u16(data, head_off + 18)
        self.loc_fmt = _i16(data, head_off + 50)
        maxp_off, _ = self.tables['maxp']
        self.num_glyphs = _u16(data, maxp_off + 4)
        hhea_off, _ = self.tables['hhea']
        self.ascender = _i16(data, hhea_off + 4)
        self.descender = _i16(data, hhea_off + 6)
        self.num_hmetrics = _u16(data, hhea_off + 34)
        self._cmap = self._parse_cmap()
        self._glyph_cache = {}

    def _table(self, tag):
        off, ln = self.tables[tag]
        return self.data[off:off + ln]

    def _parse_cmap(self):
        data = self._table('cmap')
        n = _u16(data, 2)
        best = None
        for i in range(n):
            plat = _u16(data, 4 + i * 8)
            enc = _u16(data, 6 + i * 8)
            off = _u32(data, 8 + i * 8)
            fmt = _u16(data, off)
            if fmt == 4 and plat == 3:
                return ('fmt4', off)
            if fmt == 4 and best is None:
                best = ('fmt4', off)
            if fmt == 12 and best is None:
                best = ('fmt12', off)
        return best

    def glyph_index(self, ch):
        kind, off = self._cmap
        data = self._table('cmap')
        if kind == 'fmt4':
            seg_count = _u16(data, off + 6) // 2
            end_off = off + 14
            start_off = end_off + 2 * seg_count + 2
            delta_off = start_off + 2 * seg_count
            range_off = delta_off + 2 * seg_count
            for i in range(seg_count):
                end = _u16(data, end_off + 2 * i)
                if ch > end:
                    continue
                start = _u16(data, start_off + 2 * i)
                if ch < start:
                    return 0
                delta = _i16(data, delta_off + 2 * i)
                ro = _u16(data, range_off + 2 * i)
                if ro == 0:
                    return (ch + delta) & 0xFFFF
                addr = range_off + 2 * i + ro + 2 * (ch - start)
                g = _u16(data, addr)
                if g == 0:
                    return 0
                return (g + delta) & 0xFFFF
            return 0
        # format 12
        n_groups = _u32(data, off + 12)
        for i in range(n_groups):
            go = off + 16 + i * 12
            start = _u32(data, go)
            end = _u32(data, go + 4)
            base = _u32(data, go + 8)
            if start <= ch <= end:
                return base + (ch - start)
        return 0

    def _glyph_offset(self, gid):
        loca = self._table('loca')
        if self.loc_fmt == 0:
            o1 = _u16(loca, gid * 2) * 2
            o2 = _u16(loca, gid * 2 + 2) * 2
        else:
            o1 = _u32(loca, gid * 4)
            o2 = _u32(loca, gid * 4 + 4)
        return o1, o2

    def advance(self, gid):
        hmtx = self._table('hmtx')
        if gid < self.num_hmetrics:
            return _u16(hmtx, gid * 4)
        return _u16(hmtx, (self.num_hmetrics - 1) * 4)

    def outline(self, gid):
        """Return list of contours; each contour is a list of (x, y, on_curve)."""
        if gid in self._glyph_cache:
            return self._glyph_cache[gid]
        glyf = self._table('glyf')
        o1, o2 = self._glyph_offset(gid)
        if o2 <= o1:
            self._glyph_cache[gid] = []
            return []
        n_contours = _i16(glyf, o1)
        if n_contours >= 0:
            contours = self._simple_outline(glyf, o1, n_contours)
        else:
            contours = self._composite_outline(glyf, o1)
        self._glyph_cache[gid] = contours
        return contours

    def _simple_outline(self, glyf, o, n_contours):
        end_pts = [_u16(glyf, o + 10 + 2 * i) for i in range(n_contours)]
        n_points = end_pts[-1] + 1 if end_pts else 0
        instr_len = _u16(glyf, o + 10 + 2 * n_contours)
        p = o + 10 + 2 * n_contours + 2 + instr_len
        flags = []
        while len(flags) < n_points:
            f = glyf[p]
            p += 1
            flags.append(f)
            if f & 0x08:
                rep = glyf[p]
                p += 1
                flags.extend([f] * rep)
        xs = []
        x = 0
        for f in flags:
            if f & 0x02:
                d = glyf[p]
                p += 1
                x += d if (f & 0x10) else -d
            elif f & 0x10:
                pass
            else:
                x += _i16(glyf, p)
                p += 2
            xs.append(x)
        ys = []
        y = 0
        for f in flags:
            if f & 0x04:
                d = glyf[p]
                p += 1
                y += d if (f & 0x20) else -d
            elif f & 0x20:
                pass
            else:
                y += _i16(glyf, p)
                p += 2
            ys.append(y)
        contours = []
        start = 0
        for end in end_pts:
            pts = [(xs[i], ys[i], bool(flags[i] & 0x01))
                   for i in range(start, end + 1)]
            contours.append(pts)
            start = end + 1
        return contours

    def _composite_outline(self, glyf, o):
        p = o + 10
        contours = []
        while True:
            flags = _u16(glyf, p)
            comp_gid = _u16(glyf, p + 2)
            p += 4
            if flags & 0x0001:
                dx = _i16(glyf, p)
                dy = _i16(glyf, p + 2)
                p += 4
            else:
                dx = glyf[p] if not (flags & 0x0002) else 0
                dy = glyf[p + 1] if not (flags & 0x0002) else 0
                # ARGS_ARE_XY_VALUES with bytes: signed bytes
                if flags & 0x0002:
                    dx = glyf[p] - 256 if glyf[p] > 127 else glyf[p]
                    dy = glyf[p + 1] - 256 if glyf[p + 1] > 127 else glyf[p + 1]
                p += 2
            a = d = 1.0
            b = c = 0.0
            if flags & 0x0008:
                s = _i16(glyf, p) / 16384.0
                p += 2
                a = d = s
            elif flags & 0x0040:
                a = _i16(glyf, p) / 16384.0
                d = _i16(glyf, p + 2) / 16384.0
                p += 4
            elif flags & 0x0080:
                a = _i16(glyf, p) / 16384.0
                b = _i16(glyf, p + 2) / 16384.0
                c = _i16(glyf, p + 4) / 16384.0
                d = _i16(glyf, p + 6) / 16384.0
                p += 8
            for contour in self.outline(comp_gid):
                out = []
                for (x, y, on) in contour:
                    nx = a * x + b * y + dx
                    ny = c * x + d * y + dy
                    out.append((nx, ny, on))
                contours.append(out)
            if not (flags & 0x0020):
                break
        return contours


# --------------------------------------------------------------------------
# Outline flattening + scanline fill
# --------------------------------------------------------------------------

def _flatten_contour(pts):
    """Walk a TrueType contour into a polyline of (x, y) points."""
    if not pts:
        return []
    n = len(pts)
    # expand: insert implied on-curve midpoints between consecutive
    # off-curve points (including wraparound)
    exp = []
    for i in range(n):
        p = pts[i]
        q = pts[(i + 1) % n]
        exp.append(p)
        if not p[2] and not q[2]:
            exp.append(((p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0, True))
    si = None
    for i, p in enumerate(exp):
        if p[2]:
            si = i
            break
    if si is None:
        return []
    rot = exp[si:] + exp[:si]
    poly = [rot[0][:2]]
    cur = rot[0][:2]
    i = 1
    m = len(rot)
    while i < m:
        p = rot[i]
        if p[2]:
            poly.append(p[:2])
            cur = p[:2]
            i += 1
        else:
            end = rot[(i + 1) % m][:2]
            cx, cy = p[0], p[1]
            x0, y0 = cur
            x1, y1 = end
            chord = math.hypot(x1 - x0, y1 - y0) + math.hypot(cx - x0, cy - y0)
            segs = max(2, min(24, int(chord / 90.0) + 2))
            for s in range(1, segs + 1):
                t = s / float(segs)
                mt = 1 - t
                poly.append((mt * mt * x0 + 2 * mt * t * cx + t * t * x1,
                             mt * mt * y0 + 2 * mt * t * cy + t * t * y1))
            cur = end
            i += 2
    return poly


def _fill_polys(mask, mw, mh, polys):
    """Even-odd scanline fill of polygons into a byte mask (0/255)."""
    edges = []
    for poly in polys:
        if len(poly) < 3:
            continue
        for i in range(len(poly)):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % len(poly)]
            if y1 == y2:
                continue
            edges.append((x1, y1, x2, y2))
    if not edges:
        return
    ys = [e[1] for e in edges] + [e[3] for e in edges]
    y0 = max(0, int(math.floor(min(ys))))
    y1 = min(mh, int(math.ceil(max(ys))))
    for y in range(y0, y1):
        yc = y + 0.5
        xs = []
        for (x1, y1e, x2, y2e) in edges:
            if (y1e <= yc < y2e) or (y2e <= yc < y1e):
                xs.append(x1 + (yc - y1e) * (x2 - x1) / (y2e - y1e))
        if len(xs) < 2:
            continue
        xs.sort()
        row = y * mw
        for k in range(0, len(xs) - 1, 2):
            xa = int(math.ceil(xs[k] - 0.5))
            xb = int(math.floor(xs[k + 1] - 0.5))
            if xb < 0 or xa >= mw:
                continue
            xa = max(0, xa)
            xb = min(mw - 1, xb)
            for xx in range(xa, xb + 1):
                mask[row + xx] = 255


# --------------------------------------------------------------------------
# Canvas
# --------------------------------------------------------------------------

SS = 2  # glyph supersampling factor


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)
        self._fonts = {}
        self._glyph_masks = {}

    # -- low level ------------------------------------------------------
    def _set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, int(x))
        y0 = max(0, int(y))
        x1 = min(self.w, int(x + w))
        y1 = min(self.h, int(y + h))
        if x1 <= x0 or y1 <= y0:
            return
        r, g, b = color
        row_bytes = bytes((r, g, b)) * (x1 - x0)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            self.px[base:base + (x1 - x0) * 3] = row_bytes

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def rect(self, x, y, w, h, color, thick=1):
        self.hline(x, y, w, color, thick)
        self.hline(x, y + h - thick, w, color, thick)
        self.vline(x, y, h, color, thick)
        self.vline(x + w - thick, y, h, color, thick)

    def circle(self, cx, cy, r, color):
        r = int(r)
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def ellipse(self, cx, cy, rx, ry, color):
        for dy in range(-int(ry), int(ry) + 1):
            t = 1 - (dy * dy) / float(ry * ry)
            if t < 0:
                continue
            dx = int(rx * math.sqrt(t))
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def polygon(self, pts, color):
        if len(pts) < 3:
            return
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        bx0 = max(0, int(math.floor(min(xs))))
        by0 = max(0, int(math.floor(min(ys))))
        bx1 = min(self.w, int(math.ceil(max(xs))) + 1)
        by1 = min(self.h, int(math.ceil(max(ys))) + 1)
        if bx1 <= bx0 or by1 <= by0:
            return
        mw = bx1 - bx0
        mh = by1 - by0
        shifted = [[(x - bx0, y - by0) for (x, y) in pts]]
        mask = bytearray(mw * mh)
        _fill_polys(mask, mw, mh, shifted)
        r, g, b = color
        for yy in range(by0, by1):
            mrow = (yy - by0) * mw
            prow = (yy * self.w + bx0) * 3
            for xx in range(mw):
                if mask[mrow + xx]:
                    i = prow + xx * 3
                    self.px[i] = r
                    self.px[i + 1] = g
                    self.px[i + 2] = b

    def rrect(self, x, y, w, h, r, color):
        x, y, w, h, r = int(x), int(y), int(w), int(h), int(r)
        r = min(r, w // 2, h // 2)
        for yy in range(y, y + h):
            if yy < y + r:
                t = yy - y
                inset = r - int(math.sqrt(max(0, r * r - (r - t) * (r - t))))
            elif yy >= y + h - r:
                t = (y + h - 1) - yy
                inset = r - int(math.sqrt(max(0, r * r - (r - t) * (r - t))))
            else:
                inset = 0
            self.fill_rect(x + inset, yy, w - 2 * inset, 1, color)

    def gradient_rect(self, x, y, w, h, top, bottom):
        for yy in range(int(y), int(y + h)):
            t = (yy - y) / float(max(1, h - 1))
            c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
            self.fill_rect(x, yy, w, 1, c)

    def polyline(self, pts, color, width=2):
        if len(pts) < 2:
            return
        hw = width / 2.0
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            dx, dy = x2 - x1, y2 - y1
            ln = math.hypot(dx, dy)
            if ln == 0:
                continue
            nx, ny = -dy / ln * hw, dx / ln * hw
            self.polygon([(x1 + nx, y1 + ny), (x2 + nx, y2 + ny),
                          (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)], color)
            self.circle(int(round(x1)), int(round(y1)), int(math.ceil(hw)), color)
        self.circle(int(round(pts[-1][0])), int(round(pts[-1][1])),
                    int(math.ceil(hw)), color)

    # -- fonts ----------------------------------------------------------
    def font(self, path):
        if path not in self._fonts:
            self._fonts[path] = Font(path)
        return self._fonts[path]

    def _glyph_mask(self, font, ch, size):
        key = (font.path, ch, size)
        if key in self._glyph_masks:
            return self._glyph_masks[key]
        gid = font.glyph_index(ord(ch))
        scale = size * SS / float(font.upem)
        adv = font.advance(gid) * size / float(font.upem)
        if gid == 0:
            res = (None, 0, 0, 0, 0, adv)
            self._glyph_masks[key] = res
            return res
        contours = font.outline(gid)
        polys = []
        minx = miny = None
        maxx = maxy = None
        for contour in contours:
            poly = _flatten_contour(contour)
            if not poly:
                continue
            # flip y (TTF y up -> screen y down), scale by SS
            sp = [(x * scale, -y * scale) for (x, y) in poly]
            polys.append(sp)
            for (px, py) in sp:
                minx = px if minx is None else min(minx, px)
                maxx = px if maxx is None else max(maxx, px)
                miny = py if miny is None else min(miny, py)
                maxy = py if maxy is None else max(maxy, py)
        if not polys:
            res = (None, 0, 0, 0, 0, adv)
            self._glyph_masks[key] = res
            return res
        ox = int(math.floor(minx))
        oy = int(math.floor(miny))
        mw = int(math.ceil(maxx)) - ox + 1
        mh = int(math.ceil(maxy)) - oy + 1
        shifted = [[(x - ox, y - oy) for (x, y) in poly] for poly in polys]
        mask = bytearray(mw * mh)
        _fill_polys(mask, mw, mh, shifted)
        # downsample SS x SS -> grayscale 1x mask
        gw = (mw + SS - 1) // SS
        gh = (mh + SS - 1) // SS
        gray = bytearray(gw * gh)
        for gy in range(gh):
            for gx in range(gw):
                s = 0
                n = 0
                for dy in range(SS):
                    for dx in range(SS):
                        sx = gx * SS + dx
                        sy = gy * SS + dy
                        if sx < mw and sy < mh:
                            s += mask[sy * mw + sx]
                            n += 1
                gray[gy * gw + gx] = (s * 255) // (255 * n) if n else 0
        res = (gray, gw, gh, ox / float(SS), oy / float(SS), adv)
        self._glyph_masks[key] = res
        return res

    def text_width(self, font, size, text):
        w = 0.0
        for ch in text:
            gid = font.glyph_index(ord(ch))
            w += font.advance(gid) * size / float(font.upem)
        return w

    def draw_text(self, font, size, text, x, y, color, align='left'):
        """Draw text with baseline at y. align: left/center/right on x."""
        if align == 'center':
            x -= self.text_width(font, size, text) / 2.0
        elif align == 'right':
            x -= self.text_width(font, size, text)
        pen = x
        for ch in text:
            gray, gw, gh, ox, oy, adv = self._glyph_mask(font, ch, size)
            if gray is not None:
                gx0 = int(round(pen + ox))
                gy0 = int(round(y + oy))
                for gy in range(gh):
                    dy = gy0 + gy
                    if dy < 0 or dy >= self.h:
                        continue
                    row = dy * self.w
                    for gx in range(gw):
                        a = gray[gy * gw + gx]
                        if a == 0:
                            continue
                        dx = gx0 + gx
                        if dx < 0 or dx >= self.w:
                            continue
                        i = (row + dx) * 3
                        if a == 255:
                            self.px[i] = color[0]
                            self.px[i + 1] = color[1]
                            self.px[i + 2] = color[2]
                        else:
                            self.px[i] = (self.px[i] * (255 - a) + color[0] * a) // 255
                            self.px[i + 1] = (self.px[i + 1] * (255 - a) + color[1] * a) // 255
                            self.px[i + 2] = (self.px[i + 2] * (255 - a) + color[2] * a) // 255
            pen += adv
        return pen

    def wrap(self, font, size, text, max_w):
        """Greedy word wrap; returns list of lines."""
        words = text.split(' ')
        lines = []
        cur = ''
        for wd in words:
            trial = (cur + ' ' + wd).strip()
            if self.text_width(font, size, trial) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


# --------------------------------------------------------------------------
# PNG writer (deterministic: fixed filters, fixed zlib level)
# --------------------------------------------------------------------------

def _chunk(typ, payload):
    c = struct.pack('>I', len(payload)) + typ + payload
    c += struct.pack('>I', zlib.crc32(typ + payload) & 0xFFFFFFFF)
    return c


def write_png(path, canvas):
    w, h = canvas.w, canvas.h
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += canvas.px[y * w * 3:(y + 1) * w * 3]
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    data = b'\x89PNG\r\n\x1a\n'
    data += _chunk(b'IHDR', ihdr)
    comp = zlib.compress(bytes(raw), 6)
    data += _chunk(b'IDAT', comp)
    data += _chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(data)
