"""Premium 30 s FlameLens demo (1920x1080, 60 fps): branded dark stage, the live dashboard in a floating browser
window with camera moves, cursor and click ripples, numbered captions below the window, and the FlameLens
illustration as intro and end card.

Usage: render.py <shots_dir> <out.mp4> <soundtrack.wav> <illustration.(png|jpg)> <logo.png> [--preview]
Timing must match soundtrack.py (scene changes, clicks, end card).
"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import imageio_ffmpeg

SHOTS, OUT, WAV, ILLU, LOGO = (Path(a) for a in sys.argv[1:6])
PREVIEW = "--preview" in sys.argv
W, H, FPS, DUR = 1920, 1080, 60, 30.0
META = json.loads((SHOTS / "meta.json").read_text(encoding="utf-8"))
F_B, F_SB, F_R, F_M = ("C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/seguisb.ttf",
                       "C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/consolab.ttf")
F_D = "C:/Windows/Fonts/bahnschrift.ttf"
FLAME, CYAN, WHITE = (255, 138, 36), (92, 214, 255), (255, 255, 255)
font = lambda p, s: ImageFont.truetype(p, s)

# stage layout: browser window with a 16:9 content area, captions below it
CW, CH = 1520, 855
WX, BAR = (W - CW) // 2, 38
WY = 26
CX, CY = WX, WY + BAR            # content top-left on screen
CAP_Y = CY + CH + 18             # caption row

ease = lambda t: t * t * (3 - 2 * t)
lerp = lambda a, b, t: a + (b - a) * t
clamp = lambda v: max(0.0, min(1.0, v))

_imgs = {}
def img(name):
    if name not in _imgs:
        _imgs[name] = Image.open(SHOTS / f"{name}.png").convert("RGB")
    return _imgs[name]

def center(shot, key):
    x, y, w, h = META[shot][key]
    return (x + w / 2, y + h / 2)

# ---------------------------------------------------------------- timeline
INTRO_END, END_CARD = 1.6, 27.6
SEG = [
    (1.6, 5.2, "s1_top_rover", (960, 540, 1.0), (960, 330, 1.15)),
    (5.2, 6.3, "s2_top_iss", (960, 330, 1.15), (900, 320, 1.2)),
    (6.3, 8.9, "s2_meter_iss", (479, 330, 1.55), (479, 300, 1.7)),
    (8.9, 13.3, "s3_closest", (478, 190, 1.6), (478, 420, 1.42)),
    (13.3, 15.3, "s4_explain", (478, 330, 1.55), (478, 300, 1.6)),
    (15.3, 17.6, "s4_drawer", (900, 560, 1.15), (1560, 800, 1.5)),
    (17.6, 18.7, "s5_campaign_n1", (478, 300, 1.5), (478, 300, 1.52)),
    (18.7, 21.9, "s5_campaign_n3", (478, 300, 1.52), (478, 600, 1.4)),
    (21.9, 23.1, "s6_spread", (1405, 362, 1.6), (1405, 360, 1.62)),
    (23.1, 24.3, "s6_coolflame", (1405, 362, 1.6), (1405, 360, 1.62)),
    (24.3, 25.4, "s6_aerosol", (1405, 362, 1.6), (1405, 360, 1.62)),
    (25.4, 27.6, "s7_brief_top", (960, 540, 1.0), (960, 470, 1.25)),
]
XFADE = 0.32
CAPTIONS = [
    (1.85, 5.15, "Planned Moon rovers: 30 % oxygen at 10.2 psi.", "Has NASA ever tested fire in that air?"),
    (5.3, 8.85, "FlameLens checks any habitat design", "against 2,003 real NASA flight runs from 18 PSI investigations"),
    (9.0, 13.25, "No exact match for the rover?", "It shows the closest real NASA tests, and exactly what differs"),
    (13.4, 17.55, "Every sentence is citation-verified", "and links to its NASA run and DOI"),
    (17.7, 21.85, "Campaign planner: what NASA could fly next", "3 experiments give all 5 habitat designs a matching test"),
    (22.0, 25.35, "Physics lenses built from real runs", "flame spread, cool flames, smoke vs dust"),
    (25.5, 27.55, "One click: a printable design-review brief", "with every NASA source cited"),
]
c = lambda shot, key: center(shot, key)
CURSOR = [
    (3.5, "s1_top_rover", 1150, 620), (4.95, "s1_top_rover", *c("s1_top_rover", "iss")),
    (5.3, "s1_top_rover", *c("s1_top_rover", "iss")), (6.2, "s1_top_rover", 1500, 420),
    (13.5, "s4_explain", 520, 520), (15.05, "s4_explain", *c("s4_explain", "run1")),
    (15.5, "s4_explain", *c("s4_explain", "run1")),
    (17.7, "s5_campaign_n1", 560, 420), (18.55, "s5_campaign_n1", *c("s5_campaign_n1", "n3")),
    (19.3, "s5_campaign_n1", *c("s5_campaign_n1", "n3")), (20.6, "s5_campaign_n1", 640, 380),
    (22.0, "s6_spread", 1500, 300), (23.0, "s6_spread", *c("s6_spread", "coolflame")),
    (24.2, "s6_spread", *c("s6_spread", "aerosol")), (25.3, "s6_spread", *c("s6_spread", "aerosol")),
]
CURSOR_ON = [(3.5, 6.2), (13.5, 15.8), (17.7, 20.6), (22.0, 25.3)]
CLICKS = [5.0, 15.1, 18.6, 23.05, 24.25]
HIGHLIGHTS = [(6.7, 8.8, "s2_meter_iss", "meter", FLAME), (10.1, 13.2, "s3_closest", "closest", CYAN),
              (15.9, 17.5, "s4_drawer", "drawer", CYAN)]

# ---------------------------------------------------------------- static layers
def rounded_mask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), r, fill=255)
    return m

def build_stage():
    bg = Image.new("RGB", (W, H), (6, 9, 26))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    d.ellipse((-500, 500, 900, 1500), fill=(255, 110, 30, 70))
    d.ellipse((1200, -500, 2500, 600), fill=(60, 140, 255, 60))
    d.ellipse((600, 200, 1400, 900), fill=(40, 60, 140, 40))
    g = g.filter(ImageFilter.GaussianBlur(160))
    bg.paste(g, (0, 0), g)
    stars = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stars)
    import random
    rnd = random.Random(7)
    for _ in range(260):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.choice([0.6, 0.8, 1.0, 1.3])
        a = rnd.randint(40, 150)
        sd.ellipse((x - r, y - r, x + r, y + r), fill=(220, 230, 255, a))
    bg.paste(stars, (0, 0), stars)
    return bg

def build_window():
    """Shadow + chrome bar + border as an RGBA layer (content pasted per frame)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((WX + 10, WY + 30, WX + CW - 10, CY + CH + 30), 22, fill=(0, 0, 0, 190))
    sh = sh.filter(ImageFilter.GaussianBlur(34))
    lay.alpha_composite(sh)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle((WX - 2, WY - 2, WX + CW + 2, CY + CH + 2), 20, outline=FLAME + (90,), width=3)
    lay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((WX, WY, WX + CW, CY + CH), 16, fill=(16, 22, 52, 255))
    d.rectangle((WX, WY + 16, WX + CW, CY), fill=(16, 22, 52, 255))
    for i, col in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
        x = WX + 22 + i * 22
        d.ellipse((x - 6, WY + BAR / 2 - 6, x + 6, WY + BAR / 2 + 6), fill=col + (255,))
    pill_w = 420
    px = WX + (CW - pill_w) / 2
    d.rounded_rectangle((px, WY + 7, px + pill_w, WY + BAR - 7), 12, fill=(30, 38, 80, 255))
    f = font(F_SB, 17)
    txt = "flamelens-steel.vercel.app"
    d.text((px + (pill_w - d.textlength(txt, font=f)) / 2 + 8, WY + 9), txt, font=f, fill=(190, 202, 235, 255))
    d.ellipse((px + 16, WY + 15, px + 24, WY + 23), outline=(120, 220, 160, 255), width=2)
    d.rounded_rectangle((WX, WY, WX + CW, CY + CH), 16, outline=(255, 255, 255, 40), width=1)
    return lay

STAGE = build_stage()
WINDOW = build_window()
CONTENT_MASK = Image.new("L", (CW, CH), 255)
ImageDraw.Draw(CONTENT_MASK).rectangle((0, 0, CW, CH), fill=255)
_m = rounded_mask((CW, CH + 16), 16).crop((0, 16, CW, CH + 16))
CONTENT_MASK = _m

ILL = Image.open(ILLU).convert("RGB") if ILLU.exists() else None
LOGO_IM = Image.open(LOGO).convert("RGBA")

def cover(im, scale=1.0, focus=(0.5, 0.5)):
    """Scale an image to cover the frame (with extra zoom), cropping around focus."""
    r = max(W / im.width, H / im.height) * scale
    w, h = im.width * r, im.height * r
    x0 = (w - W) * focus[0]; y0 = (h - H) * focus[1]
    return im.resize((W, H), Image.LANCZOS, box=(x0 / r, y0 / r, (x0 + W) / r, (y0 + H) / r))

def fallback_card():
    card = STAGE.copy()
    lg = LOGO_IM.resize((560, 560), Image.LANCZOS)
    card.paste(lg, ((W - 560) // 2, 120), lg)
    d = ImageDraw.Draw(card)
    f = font(F_B, 120)
    d.text(((W - d.textlength("FlameLens", font=f)) / 2, 660), "FlameLens", font=f, fill=WHITE)
    return card

# ---------------------------------------------------------------- per-frame helpers
def cam_at(seg, t):
    s0, s1, _, a, b = seg
    u = ease(clamp((t - s0) / (s1 - s0)))
    return tuple(lerp(a[i], b[i], u) for i in range(3))

def box(cam):
    cx, cy, z = cam
    w, h = W / z, H / z
    return min(max(cx - w / 2, 0), W - w), min(max(cy - h / 2, 0), H - h), w, h

def content(seg, t):
    x0, y0, w, h = box(cam_at(seg, t))
    return img(seg[2]).resize((CW, CH), Image.BICUBIC, box=(x0 * 2, y0 * 2, (x0 + w) * 2, (y0 + h) * 2), reducing_gap=2.0)

def to_screen(seg, t, x, y):
    x0, y0, w, h = box(cam_at(seg, t))
    return (CX + (x - x0) / w * CW, CY + (y - y0) / h * CH)

_cur = None
def cursor_sprite():
    global _cur
    if _cur is None:
        s = 3
        cimg = Image.new("RGBA", (40 * s, 56 * s), (0, 0, 0, 0))
        pts = [(2, 2), (2, 40), (12, 31), (19, 48), (26, 45), (19, 29), (32, 29)]
        sh = Image.new("RGBA", cimg.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).polygon([(x * s + 4, y * s + 5) for x, y in pts], fill=(0, 0, 0, 120))
        cimg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
        ImageDraw.Draw(cimg).polygon([(x * s, y * s) for x, y in pts], fill=(255, 255, 255, 255), outline=(15, 20, 35, 255), width=2 * s)
        _cur = cimg.resize((34, 48), Image.LANCZOS)
    return _cur

def cursor_pos(t):
    for (ta, sa, xa, ya), (tb, sb, xb, yb) in zip(CURSOR, CURSOR[1:]):
        if ta <= t <= tb:
            u = ease((t - ta) / (tb - ta)) if tb > ta else 1
            return lerp(xa, xb, u), lerp(ya, yb, u)
    return None

def overlay_ui(frame, seg, t):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for a, b, shot, key, col in HIGHLIGHTS:
        if shot == seg[2] and a <= t <= b and META[shot].get(key):
            fade = min(1, (t - a) / 0.35, (b - t) / 0.3)
            x, y, w, h = META[shot][key]
            (sx0, sy0), (sx1, sy1) = to_screen(seg, t, x - 6, y - 6), to_screen(seg, t, x + w + 6, y + h + 6)
            sx0, sy0, sx1, sy1 = max(sx0, CX + 4), max(sy0, CY + 4), min(sx1, CX + CW - 4), min(sy1, CY + CH - 4)
            d.rounded_rectangle((sx0, sy0, sx1, sy1), 20, outline=col + (int(235 * fade),), width=5)
    if any(a <= t <= b for a, b in CURSOR_ON):
        p = cursor_pos(t)
        if p:
            sx, sy = to_screen(seg, t, *p)
            for ck in CLICKS:
                if ck <= t <= ck + 0.45:
                    u = (t - ck) / 0.45
                    r = 12 + 40 * ease(u)
                    d.ellipse((sx - r, sy - r, sx + r, sy + r), outline=FLAME + (int(255 * (1 - u)),), width=5)
                    d.ellipse((sx - 11, sy - 11, sx + 11, sy + 11), fill=FLAME + (int(150 * (1 - u)),))
    glow = ov.filter(ImageFilter.GaussianBlur(7))
    frame.paste(glow, (0, 0), glow)
    frame.paste(ov, (0, 0), ov)
    if any(a <= t <= b for a, b in CURSOR_ON):
        p = cursor_pos(t)
        if p:
            sx, sy = to_screen(seg, t, *p)
            cur = cursor_sprite()
            if any(ck <= t <= ck + 0.12 for ck in CLICKS):
                cur = cur.resize((29, 41))
            frame.paste(cur, (int(sx - 2), int(sy - 2)), cur)

F_H, F_S, F_N, F_U = font(F_B, 44), font(F_R, 30), font(F_D, 46), font(F_SB, 21)
MINI = LOGO_IM.resize((44, 44), Image.LANCZOS)

def draw_caption_row(frame, t, alpha=1.0):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    # brand mark on the right of the caption row
    a_brand = int(200 * alpha)
    url = "flamelens-steel.vercel.app"
    uw = d.textlength(url, font=F_U)
    ux = WX + CW - uw
    m = MINI.copy(); m.putalpha(m.getchannel("A").point(lambda v: int(v * alpha)))
    ov.paste(m, (int(ux - 56), CAP_Y + 30), m)
    d.text((ux, CAP_Y + 40), url, font=F_U, fill=(170, 182, 220, a_brand))
    for i, (a, b, l1, l2) in enumerate(CAPTIONS):
        if a <= t <= b:
            fin = ease(clamp((t - a) / 0.35)); fout = ease(clamp((b - t) / 0.25))
            k = min(fin, fout) * alpha
            dy = (1 - fin) * 16
            num = f"{i + 1:02d}"
            d.text((WX, CAP_Y + 18 + dy), num, font=F_N, fill=FLAME + (int(255 * k),))
            d.rectangle((WX + 68, CAP_Y + 22 + dy, WX + 71, CAP_Y + 104 + dy), fill=(255, 255, 255, int(70 * k)))
            d.text((WX + 92, CAP_Y + 8 + dy), l1, font=F_H, fill=(255, 255, 255, int(255 * k)))
            d.text((WX + 92, CAP_Y + 62 + dy), l2, font=F_S, fill=(178, 192, 232, int(255 * k)))
    frame.paste(ov, (0, 0), ov)

def window_frame(t):
    i = next((k for k, s in enumerate(SEG) if s[0] <= t < s[1]), len(SEG) - 1)
    seg = SEG[i]
    cont = content(seg, t)
    if i > 0 and t < seg[0] + XFADE:
        prev = SEG[i - 1]
        cont = Image.blend(content(prev, prev[1] - 1e-3), cont, ease((t - seg[0]) / XFADE))
    frame = STAGE.copy()
    frame.paste(WINDOW, (0, 0), WINDOW)
    frame.paste(cont, (CX, CY), CONTENT_MASK)
    return frame, seg

def intro_card(t):
    base = cover(ILL, 1.0 + 0.05 * (t / 2.2), (0.5, 0.45)) if ILL else fallback_card()
    shade = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.blend(shade, base, ease(clamp(t / 0.45)))

END_F1, END_F2, END_F3 = font(F_SB, 44), font(F_M, 34), font(F_SB, 25)
_end_art = None
def end_art():
    """Illustration contained in the upper part of the stage, edges feathered into the dark background."""
    global _end_art
    if _end_art is None:
        if ILL is None:
            _end_art = fallback_card(); return _end_art
        import numpy as np
        h = 790; w = int(ILL.width * h / ILL.height)
        art = ILL.resize((w, h), Image.LANCZOS).convert("RGBA")
        yy, xx = np.mgrid[0:h, 0:w].astype(float)
        e = 150.0
        a = np.minimum.reduce([xx / e, (w - 1 - xx) / e, yy / 60.0, (h - 1 - yy) / e])
        a = np.clip(a, 0, 1); a = a * a * (3 - 2 * a)
        art.putalpha(Image.fromarray((a * 255).astype("uint8")))
        base = STAGE.copy().convert("RGBA")
        base.alpha_composite(art, ((W - w) // 2, 0))
        _end_art = base.convert("RGB")
    return _end_art

def end_card(t):
    z = 1.0 + 0.035 * (t / 2.4)
    art = end_art()
    if z > 1.0:  # slow push-in
        cw, ch = W / z, H / z
        art = art.resize((W, H), Image.LANCZOS, box=((W - cw) / 2, (H - ch) / 2 * 0.6, (W + cw) / 2, (H - ch) / 2 * 0.6 + ch))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    k = ease(clamp((t - 0.3) / 0.5))
    def ctext(y, s, f, col):
        d.text(((W - d.textlength(s, font=f)) / 2, y + (1 - k) * 14), s, font=f, fill=col + (int(255 * k),))
    ctext(812, "Space-fire data, made clear", END_F1, WHITE)
    pw = 600
    d.rounded_rectangle(((W - pw) / 2, 884 + (1 - k) * 14, (W + pw) / 2, 942 + (1 - k) * 14), 29,
                        fill=(255, 138, 36, int(38 * k)), outline=FLAME + (int(220 * k),), width=2)
    ctext(893, "flamelens-steel.vercel.app", END_F2, (255, 196, 140))
    ctext(982, "Team AstroSpark  ·  NASA Space Apps Cairo 2026  ·  NASA PSI data (CC0)", END_F3, (178, 192, 232))
    base = art.convert("RGBA"); base.alpha_composite(ov)
    return base.convert("RGB")

def render_frame(t):
    if t < INTRO_END:
        im = intro_card(t)
        if t > INTRO_END - 0.45:  # dissolve into the stage with the window rising in
            w, _ = window_frame(INTRO_END)
            u = ease((t - (INTRO_END - 0.45)) / 0.45)
            im = Image.blend(im, w, u)
        return im
    if t >= END_CARD:
        e = end_card(t - END_CARD)
        if t < END_CARD + 0.5:
            w, seg = window_frame(END_CARD - 1e-3)
            draw_caption_row(w, END_CARD - 1e-3)
            e = Image.blend(w, e, ease((t - END_CARD) / 0.5))
        if t > DUR - 0.5:
            e = Image.blend(e, Image.new("RGB", (W, H), (0, 0, 0)), ease((t - (DUR - 0.5)) / 0.5))
        return e
    frame, seg = window_frame(t)
    overlay_ui(frame, seg, t)
    draw_caption_row(frame, t, alpha=ease(clamp((t - INTRO_END) / 0.4)))
    return frame

if PREVIEW:
    for t in [0.8, 1.45, 2.4, 4.97, 7.5, 11.0, 15.08, 16.8, 18.62, 20.5, 23.06, 26.5, 27.9, 29.2]:
        render_frame(t).save(OUT.parent / f"pv_{t:05.2f}.jpg", quality=88)
    print("previews written"); sys.exit()

ff = imageio_ffmpeg.get_ffmpeg_exe()
cmd = [ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-i", str(WAV), "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-profile:v", "high",
       "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", str(OUT)]
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
for f in range(int(DUR * FPS)):
    proc.stdin.write(render_frame(f / FPS).tobytes())
    if f % 300 == 0:
        print("frame", f, flush=True)
proc.stdin.close(); proc.wait()
print("wrote", OUT, proc.returncode)
