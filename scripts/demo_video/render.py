"""Compose the 30 s FlameLens demo (1920x1080, 60 fps) from 2x screenshots: camera moves, cursor, captions, title card.
Usage: render.py <shots_dir> <out.mp4> <audio.wav> [--preview]"""
import json, math, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import imageio_ffmpeg

SHOTS, OUT, WAV = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
PREVIEW = "--preview" in sys.argv
W, H, FPS, DUR = 1920, 1080, 60, 30.0
META = json.loads((SHOTS / "meta.json").read_text(encoding="utf-8"))
FONT_B = "C:/Windows/Fonts/segoeuib.ttf"
FONT_SB = "C:/Windows/Fonts/seguisb.ttf"
FONT_M = "C:/Windows/Fonts/consolab.ttf"
NAVY, FLAME = (20, 33, 61), (224, 88, 28)

_imgs = {}
def img(name):
    if name not in _imgs:
        _imgs[name] = Image.open(SHOTS / f"{name}.png").convert("RGB")
    return _imgs[name]

def center(shot, key):
    x, y, w, h = META[shot][key]
    return (x + w / 2, y + h / 2)

ease = lambda t: t * t * (3 - 2 * t)
lerp = lambda a, b, t: a + (b - a) * t

# ---------------------------------------------------------------- timeline
# segment: (start, end, shot, cam_from (cx, cy, zoom), cam_to)
SEG = [
    (0.0, 4.2, "s1_top_rover", (960, 540, 1.0), (960, 330, 1.15)),
    (4.2, 5.6, "s2_top_iss", (960, 330, 1.15), (900, 320, 1.2)),
    (5.6, 8.4, "s2_meter_iss", (479, 330, 1.55), (479, 300, 1.7)),
    (8.4, 13.2, "s3_closest", (478, 190, 1.6), (478, 420, 1.42)),
    (13.2, 15.4, "s4_explain", (478, 330, 1.55), (478, 300, 1.6)),
    (15.4, 17.8, "s4_drawer", (900, 560, 1.15), (1560, 800, 1.5)),
    (17.8, 19.0, "s5_campaign_n1", (478, 300, 1.5), (478, 300, 1.52)),
    (19.0, 22.4, "s5_campaign_n3", (478, 300, 1.52), (478, 600, 1.4)),
    (22.4, 23.7, "s6_spread", (1405, 362, 1.6), (1405, 360, 1.62)),
    (23.7, 25.0, "s6_coolflame", (1405, 362, 1.6), (1405, 360, 1.62)),
    (25.0, 26.2, "s6_aerosol", (1405, 362, 1.6), (1405, 360, 1.62)),
    (26.2, 28.4, "s7_brief_top", (960, 540, 1.0), (960, 470, 1.25)),
    (28.4, 30.0, "TITLE", None, None),
]
XFADE = 0.32

CAPTIONS = [
    (0.25, 4.15, "Planned Moon rovers: 30 % oxygen at 10.2 psi.", "Has NASA ever tested fire in that air?"),
    (4.3, 8.35, "FlameLens checks any habitat design against", "2,003 real NASA flight runs from 18 PSI investigations"),
    (8.5, 13.15, "No exact match for the rover? It shows the closest", "real NASA tests, and exactly what differs"),
    (13.3, 17.75, "Every sentence is citation-verified and links", "to its NASA run and DOI", "top"),
    (17.9, 22.35, "Campaign planner: 3 experiments NASA could fly next", "to give all 5 habitat designs a matching test"),
    (22.5, 26.15, "Physics lenses from real runs:", "flame spread, cool flames, smoke vs dust"),
    (26.3, 28.35, "One click: a printable design-review brief", "with every NASA source"),
]

# cursor: list of (t, shot-for-coords, x, y); clicks at times
S = lambda shot, key: (shot,) + center(shot, key)
CURSOR = [
    (2.6, "s1_top_rover", 1150, 620), (3.95, *S("s1_top_rover", "iss")[0:1], *center("s1_top_rover", "iss")),
    (4.25, "s1_top_rover", *center("s1_top_rover", "iss")), (5.5, "s1_top_rover", 1500, 420),
    (13.4, "s4_explain", 520, 520), (15.15, "s4_explain", *center("s4_explain", "run1")),
    (15.6, "s4_explain", *center("s4_explain", "run1")),
    (17.9, "s5_campaign_n1", 560, 420), (18.85, "s5_campaign_n1", *center("s5_campaign_n1", "n3")),
    (19.6, "s5_campaign_n1", *center("s5_campaign_n1", "n3")), (21.0, "s5_campaign_n1", 640, 380),
    (22.5, "s6_spread", 1500, 300), (23.6, "s6_spread", *center("s6_spread", "coolflame")),
    (24.9, "s6_spread", *center("s6_spread", "aerosol")), (26.0, "s6_spread", *center("s6_spread", "aerosol")),
]
CURSOR_ON = [(2.6, 5.5), (13.4, 15.9), (17.9, 21.0), (22.5, 26.0)]
CLICKS = [4.0, 15.2, 18.9, 23.65, 24.95]
HIGHLIGHTS = [  # (start, end, shot, rect key, color)
    (6.0, 8.3, "s2_meter_iss", "meter", FLAME),
    (9.6, 13.1, "s3_closest", "closest", (10, 111, 176)),
    (16.0, 17.7, "s4_drawer", "drawer", (10, 111, 176)),
]

# ---------------------------------------------------------------- drawing helpers
def cam_at(seg, t):
    s0, s1, _, a, b = seg
    u = ease(min(1, max(0, (t - s0) / (s1 - s0))))
    return tuple(lerp(a[i], b[i], u) for i in range(3))

def box(cam):
    cx, cy, z = cam
    w, h = W / z, H / z
    x0 = min(max(cx - w / 2, 0), W - w); y0 = min(max(cy - h / 2, 0), H - h)
    return x0, y0, w, h

def frame_of(seg, t):
    shot = seg[2]
    if shot == "TITLE":
        return title_card(t - seg[0])
    x0, y0, w, h = box(cam_at(seg, t))
    im = img(shot).resize((W, H), Image.BICUBIC, box=(x0 * 2, y0 * 2, (x0 + w) * 2, (y0 + h) * 2), reducing_gap=2.0)
    return im

def to_screen(seg, t, x, y):
    x0, y0, w, h = box(cam_at(seg, t))
    return ((x - x0) / w * W, (y - y0) / h * H)

_cur = None
def cursor_sprite():
    global _cur
    if _cur is None:
        s = 3
        c = Image.new("RGBA", (40 * s, 56 * s), (0, 0, 0, 0))
        d = ImageDraw.Draw(c)
        pts = [(2, 2), (2, 40), (12, 31), (19, 48), (26, 45), (19, 29), (32, 29)]
        shadow = Image.new("RGBA", c.size, (0, 0, 0, 0))
        ImageDraw.Draw(shadow).polygon([(x * s + 4, y * s + 5) for x, y in pts], fill=(0, 0, 0, 110))
        shadow = shadow.filter(ImageFilter.GaussianBlur(5))
        c.alpha_composite(shadow)
        d.polygon([(x * s, y * s) for x, y in pts], fill=(255, 255, 255, 255), outline=(15, 20, 35, 255), width=2 * s)
        _cur = c.resize((40, 56), Image.LANCZOS)
    return _cur

def cursor_pos(t):
    pts = [p for p in CURSOR]
    for (ta, sa, xa, ya), (tb, sb, xb, yb) in zip(pts, pts[1:]):
        if ta <= t <= tb:
            u = ease((t - ta) / (tb - ta)) if tb > ta else 1
            return sa, lerp(xa, xb, u), lerp(ya, yb, u)
    return None

def rrect(d, xy, r, **kw):
    d.rounded_rectangle(xy, r, **kw)

def fit(font_path, size):
    return ImageFont.truetype(font_path, size)

CAP_F = fit(FONT_B, 50)

def draw_caption(im, t):
    for cap in CAPTIONS:
        a, b, l1, l2 = cap[:4]
        top = len(cap) > 4 and cap[4] == "top"
        if a <= t <= b:
            fade = min(1, (t - a) / 0.25, (b - t) / 0.25)
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(ov)
            lines = [l for l in (l1, l2) if l]
            widths = [d.textlength(l, font=CAP_F) for l in lines]
            bw = max(widths) + 110; lh = 66
            bh = lh * len(lines) + 44
            x0 = (W - bw) / 2; y0 = (46 - (1 - ease(fade)) * 14) if top else H - bh - 46 + (1 - ease(fade)) * 14
            rrect(d, (x0, y0, x0 + bw, y0 + bh), 26, fill=(14, 22, 44, int(232 * fade)))
            rrect(d, (x0, y0, x0 + 12, y0 + bh), 6, fill=FLAME + (int(255 * fade),))
            for i, l in enumerate(lines):
                d.text(((W - widths[i]) / 2 + 6, y0 + 20 + i * lh), l, font=CAP_F, fill=(255, 255, 255, int(255 * fade)))
            im.paste(ov, (0, 0), ov)
            return

def draw_highlight(im, seg, t):
    for a, b, shot, key, col in HIGHLIGHTS:
        if shot == seg[2] and a <= t <= b and META[shot].get(key):
            fade = min(1, (t - a) / 0.35, (b - t) / 0.3)
            x, y, w, h = META[shot][key]
            (sx0, sy0), (sx1, sy1) = to_screen(seg, t, x - 6, y - 6), to_screen(seg, t, x + w + 6, y + h + 6)
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(ov)
            rrect(d, (sx0, sy0, sx1, sy1), 22, outline=col + (int(230 * fade),), width=6)
            ov = Image.alpha_composite(ov.filter(ImageFilter.GaussianBlur(8)), ov)
            im.paste(ov, (0, 0), ov)

def draw_cursor(im, seg, t):
    if not any(a <= t <= b for a, b in CURSOR_ON):
        return
    p = cursor_pos(t)
    if not p:
        return
    shot, x, y = p
    s = next((sg for sg in SEG if sg[2] == shot), seg)
    # cursor coordinates are in the CSS space of `shot`; use the current segment's camera when shots share layout
    sx, sy = to_screen(seg if seg[2] != "TITLE" else s, t, x, y)
    for c in CLICKS:
        if c <= t <= c + 0.45:
            u = (t - c) / 0.45
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(ov)
            r = 14 + 44 * ease(u)
            d.ellipse((sx - r, sy - r, sx + r, sy + r), outline=FLAME + (int(255 * (1 - u)),), width=6)
            d.ellipse((sx - 12, sy - 12, sx + 12, sy + 12), fill=FLAME + (int(150 * (1 - u)),))
            im.paste(ov, (0, 0), ov)
    press = any(c <= t <= c + 0.12 for c in CLICKS)
    cur = cursor_sprite() if not press else cursor_sprite().resize((34, 48))
    im.paste(cur, (int(sx - 2), int(sy - 2)), cur)

_title_bg = None
def title_card(u):
    global _title_bg
    if _title_bg is None:
        bg = Image.new("RGB", (W, H), (238, 242, 248))
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        g = ImageDraw.Draw(glow)
        g.ellipse((-300, -380, 1000, 520), fill=(255, 166, 112, 90))
        g.ellipse((1100, -300, 2300, 700), fill=(120, 170, 240, 90))
        glow = glow.filter(ImageFilter.GaussianBlur(120))
        bg.paste(glow, (0, 0), glow)
        d = ImageDraw.Draw(bg)
        # flame sphere
        sph = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
        for i in range(110, 0, -1):
            f = i / 110
            col = (int(lerp(255, 122, f ** 1.6)), int(lerp(241, 36, f ** 1.1)), int(lerp(196, 0, f ** 0.8)), 255)
            off = int((1 - f) * 26)
            ImageDraw.Draw(sph).ellipse((110 - i - off, 110 - i - off, 110 + i - off, 110 + i - off), fill=col)
        mask = Image.new("L", (220, 220), 0); ImageDraw.Draw(mask).ellipse((0, 0, 219, 219), fill=255)
        bg.paste(sph, (W // 2 - 110, 190), mask)
        f1, f2, f3, f4 = fit(FONT_B, 132), fit(FONT_SB, 54), fit(FONT_M, 46), fit(FONT_SB, 32)
        def ctext(y, s, f, fill):
            d.text(((W - d.textlength(s, font=f)) / 2, y), s, font=f, fill=fill)
        ctext(430, "FlameLens", f1, NAVY)
        ctext(600, "Space-fire data, made clear", f2, (93, 105, 135))
        rrect(d, (W / 2 - 400, 712, W / 2 + 400, 792), 40, fill=(253, 238, 228))
        ctext(726, "flamelens-steel.vercel.app", f3, FLAME)
        ctext(880, "Team AstroSpark  ·  NASA Space Apps Cairo 2026  ·  NASA PSI data (CC0)", f4, (93, 105, 135))
        _title_bg = bg
    return _title_bg.copy()

# ---------------------------------------------------------------- render
def render_frame(t):
    i = next(k for k, s in enumerate(SEG) if s[0] <= t < s[1] or k == len(SEG) - 1)
    seg = SEG[i]
    im = frame_of(seg, t)
    if i > 0 and t < seg[0] + XFADE:  # crossfade from the previous segment's last look
        prev = SEG[i - 1]
        a = ease((t - seg[0]) / XFADE)
        im = Image.blend(frame_of(prev, prev[1] - 1e-3), im, a)
    if seg[2] != "TITLE":
        draw_highlight(im, seg, t)
        draw_cursor(im, seg, t)
    draw_caption(im, t)
    if t < 0.35:
        im = Image.blend(Image.new("RGB", (W, H), (238, 242, 248)), im, ease(t / 0.35))
    return im

if PREVIEW:
    for t in [1.0, 3.9, 4.1, 6.5, 10.5, 15.2, 16.8, 18.9, 20.5, 23.65, 25.5, 27.5, 29.4]:
        render_frame(t).save(OUT.parent / f"preview_{t:05.2f}.jpg", quality=88)
    print("previews written"); sys.exit()

ff = imageio_ffmpeg.get_ffmpeg_exe()
cmd = [ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-i", str(WAV), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-profile:v", "high",
       "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(OUT)]
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
N = int(DUR * FPS)
for f in range(N):
    proc.stdin.write(render_frame(f / FPS).tobytes())
    if f % 300 == 0:
        print("frame", f, flush=True)
proc.stdin.close(); proc.wait()
print("wrote", OUT, proc.returncode)
