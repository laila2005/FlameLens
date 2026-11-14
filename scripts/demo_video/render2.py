"""Narrated 30 s FlameLens demo (v2): 1920x1080, 60 fps, H.264 + AAC.

Kinetic-type hook over the FlameLens illustration with rising embers, then the live dashboard in a floating browser
window (camera moves, cursor, click ripples, highlights, numbered captions, light-leak transitions), and an end card.
The narration (voiceover.py, Kokoro open-source TTS) sets the timeline; the music (soundtrack.py) ducks under it.

Usage:
  render2.py timing <timing.json>                       write scene timing for soundtrack.py
  render2.py <shots_dir> <vo_dir> <music.wav> <illustration> <logo.png> <out.mp4> [--preview]
"""
import json
import math
import random
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

W, H, FPS, DUR = 1920, 1080, 60, 30.0
SR = 48000

# ---------------------------------------------------------------- timeline (seconds)
HOOK_END, END_CARD = 3.2, 26.0
VO_AT = [0.40, 3.05, 7.85, 12.20, 18.05, 21.45, 26.35]          # start of each narration line
SEG = [  # start, end, shot, camera start (cx, cy, zoom), camera end   (CSS px of the 1920x1080 capture)
    (3.2, 7.7, "a_top_rover", (960, 380, 1.08), (1000, 330, 1.42)),
    (7.7, 9.6, "b_meter_iss", (1300, 300, 1.05), (480, 300, 1.45)),
    (9.6, 12.0, "b_meter_iss", (480, 300, 1.45), (480, 420, 1.62)),
    (12.0, 14.4, "c_case_rover", (480, 420, 1.55), (330, 560, 1.85)),
    (14.4, 17.9, "e_limits_rover", (480, 300, 1.75), (480, 560, 1.55)),
    (17.9, 19.6, "f_explain", (480, 330, 1.6), (480, 300, 1.7)),
    (19.6, 21.4, "g_drawer", (1150, 620, 1.15), (1560, 780, 1.42)),
    (21.4, 23.5, "h_campaign_n3", (1400, 420, 1.35), (1400, 560, 1.5)),
    (23.5, 24.3, "i_ask_q", (1300, 200, 1.6), (1330, 200, 1.66)),
    (24.3, 26.0, "j_ask_answer", (960, 420, 1.0), (960, 470, 1.04)),
]
SCENE_STARTS = [3.2, 7.7, 12.0, 14.4, 17.9, 21.4, 23.5]
CLICKS = [19.45, 21.62, 24.12]
XFADE = 0.30
CAPTIONS = [  # every number here is shown on the live dashboard
    (3.45, 7.6, "Moon rover: 30 % O₂ at 10.2 psi", "the lunar atmosphere named in the NASA challenge"),
    (7.85, 11.9, "2,003 real NASA flight runs · 18 PSI investigations", "ISS cabin: 336 runs match all five conditions"),
    (12.15, 14.35, "Rover: 2 of 5 conditions backed", "its 30 % O₂ runs are gas flames and droplets, not fabrics"),
    (14.5, 17.85, "Closest evidence, down to lunar gravity", "NASA drop-tower limits: cited, never counted"),
    (18.0, 21.35, "Every AI sentence cites a real NASA run", "unverifiable claims are deleted, not shown"),
    (21.55, 23.45, "What NASA should fly next", "3 experiments give all 5 habitat designs a test"),
    (23.6, 25.95, "Ask the NASA reports", "each quote checked on its report page"),
]

if len(sys.argv) > 2 and sys.argv[1] == "timing":
    Path(sys.argv[2]).write_text(json.dumps({"intro_end": HOOK_END, "end_card": END_CARD, "scenes": SCENE_STARTS,
                                             "clicks": CLICKS}), encoding="utf-8")
    print("timing written"); sys.exit()

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance  # noqa: E402
import imageio_ffmpeg  # noqa: E402

SHOTS, VO_DIR, MUSIC, ILLU, LOGO, OUT = (Path(a) for a in sys.argv[1:7])
PREVIEW = "--preview" in sys.argv
META = json.loads((SHOTS / "meta.json").read_text(encoding="utf-8"))
VO = json.loads((VO_DIR / "vo.json").read_text(encoding="utf-8"))
F_B, F_SB, F_R, F_M, F_D = ("C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/seguisb.ttf", "C:/Windows/Fonts/segoeui.ttf",
                            "C:/Windows/Fonts/consolab.ttf", "C:/Windows/Fonts/bahnschrift.ttf")
F_BL = "C:/Windows/Fonts/seguibl.ttf"
FLAME, CYAN, WHITE = (255, 138, 36), (92, 214, 255), (255, 255, 255)
font = lambda p, s: ImageFont.truetype(p if Path(p).exists() else F_B, s)
ease = lambda t: t * t * (3 - 2 * t)
eout = lambda t: 1 - (1 - t) ** 3
lerp = lambda a, b, t: a + (b - a) * t
clamp = lambda v: max(0.0, min(1.0, v))

CW, CH = 1520, 855
WX, BAR, WY = (W - CW) // 2, 38, 26
CX, CY = WX, WY + BAR
CAP_Y = CY + CH + 18

_imgs = {}
def img(name):
    if name not in _imgs:
        _imgs[name] = Image.open(SHOTS / f"{name}.png").convert("RGB")
    return _imgs[name]

def center(shot, key):
    x, y, w, h = META[shot][key]
    return (x + w / 2, y + h / 2)

c = center
CURSOR = [  # time, shot, x, y (CSS px of that shot)
    (17.95, "f_explain", 600, 520), (19.35, "f_explain", *c("f_explain", "run1")), (19.6, "f_explain", *c("f_explain", "run1")),
    (21.45, "h_campaign_n3", 1300, 330), (21.55, "h_campaign_n3", *c("h_campaign_n3", "n3")), (22.3, "h_campaign_n3", 1250, 420),
    (23.5, "i_ask_q", 1450, 300), (24.05, "i_ask_q", *c("i_ask_q", "btn")), (24.3, "i_ask_q", *c("i_ask_q", "btn")),
]
CURSOR_ON = [(17.95, 19.6), (21.45, 22.3), (23.5, 24.3)]
HIGHLIGHTS = [  # time window, shot, key, colour
    (4.6, 7.6, "a_top_rover", "controls", FLAME),
    (8.2, 9.6, "b_meter_iss", "chip", CYAN), (9.9, 11.9, "b_meter_iss", "meter", FLAME),
    (12.4, 14.35, "c_case_rover", "o2", FLAME), (12.7, 14.35, "c_case_rover", "psi", FLAME),
    (15.0, 17.85, "e_limits_rover", "row1", CYAN),
    (19.9, 21.35, "g_drawer", "drawer", CYAN),
    (24.6, 25.95, "j_ask_answer", "quote", CYAN),
]

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
    rnd = random.Random(7)
    for _ in range(260):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.choice([0.6, 0.8, 1.0, 1.3])
        sd.ellipse((x - r, y - r, x + r, y + r), fill=(220, 230, 255, rnd.randint(40, 150)))
    bg.paste(stars, (0, 0), stars)
    return bg

def build_window():
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((WX + 10, WY + 30, WX + CW - 10, CY + CH + 30), 22, fill=(0, 0, 0, 190))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(34)))
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
CONTENT_MASK = rounded_mask((CW, CH + 16), 16).crop((0, 16, CW, CH + 16))
ILL = Image.open(ILLU).convert("RGB")
LOGO_IM = Image.open(LOGO).convert("RGBA")

def cover(im, scale=1.0, focus=(0.5, 0.5)):
    r = max(W / im.width, H / im.height) * scale
    w, h = im.width * r, im.height * r
    x0, y0 = (w - W) * focus[0], (h - H) * focus[1]
    return im.resize((W, H), Image.LANCZOS, box=(x0 / r, y0 / r, (x0 + W) / r, (y0 + H) / r))

# light leak: a warm blurred blob that sweeps across at each scene change
LEAK = Image.new("RGBA", (W * 2, H), (0, 0, 0, 0))
_ld = ImageDraw.Draw(LEAK)
_ld.ellipse((700, -300, 1700, 1300), fill=(255, 150, 60, 150))
_ld.ellipse((1100, 100, 1500, 900), fill=(255, 220, 160, 120))
LEAK = LEAK.filter(ImageFilter.GaussianBlur(170))

def light_leak(frame, t):
    for s in SCENE_STARTS[1:]:
        u = (t - (s - 0.22)) / 0.6
        if 0 <= u <= 1:
            a = math.sin(math.pi * u) * 0.55
            x = int(lerp(-W * 0.9, -W * 0.1, u))
            band = LEAK.crop((-x, 0, -x + W, H))
            band.putalpha(band.getchannel("A").point(lambda v, a=a: int(v * a)))
            frame.paste(band, (0, 0), band)

# ---------------------------------------------------------------- dashboard scenes
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
            if sx1 > sx0 + 10 and sy1 > sy0 + 10:
                d.rounded_rectangle((sx0, sy0, sx1, sy1), 18, outline=col + (int(235 * fade),), width=5)
    on = any(a <= t <= b for a, b in CURSOR_ON)
    p = cursor_pos(t) if on else None
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
    if p:
        cur = cursor_sprite()
        if any(ck <= t <= ck + 0.12 for ck in CLICKS):
            cur = cur.resize((29, 41))
        frame.paste(cur, (int(sx - 2), int(sy - 2)), cur)

F_H, F_S, F_N, F_U = font(F_B, 44), font(F_R, 30), font(F_D, 46), font(F_SB, 21)
MINI = LOGO_IM.resize((44, 44), Image.LANCZOS)

def draw_caption_row(frame, t, alpha=1.0):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    url = "flamelens-steel.vercel.app"
    uw = d.textlength(url, font=F_U)
    ux = WX + CW - uw
    m = MINI.copy(); m.putalpha(m.getchannel("A").point(lambda v: int(v * alpha)))
    ov.paste(m, (int(ux - 56), CAP_Y + 30), m)
    d.text((ux, CAP_Y + 40), url, font=F_U, fill=(170, 182, 220, int(200 * alpha)))
    for i, (a, b, l1, l2) in enumerate(CAPTIONS):
        if a <= t <= b:
            fin = ease(clamp((t - a) / 0.35)); fout = ease(clamp((b - t) / 0.25))
            k = min(fin, fout) * alpha
            dy = (1 - fin) * 16
            d.text((WX, CAP_Y + 18 + dy), f"{i + 1:02d}", font=F_N, fill=FLAME + (int(255 * k),))
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

# ---------------------------------------------------------------- hook: kinetic type over embers
HOOK_BG = ImageEnhance.Brightness(cover(ILL, 1.55, (0.5, 0.12)).filter(ImageFilter.GaussianBlur(9))).enhance(0.36)
_vig = Image.new("L", (W, H), 0)
ImageDraw.Draw(_vig).ellipse((-W * 0.25, -H * 0.35, W * 1.25, H * 1.35), fill=255)
VIGNETTE = _vig.filter(ImageFilter.GaussianBlur(220))
_er = random.Random(11)
EMBERS = [dict(x=_er.uniform(0, W), y0=_er.uniform(H * 0.3, H * 1.3), v=_er.uniform(70, 260), r=_er.uniform(1.4, 4.6),
               ph=_er.uniform(0, 6.28), sw=_er.uniform(10, 46), hue=_er.random()) for _ in range(190)]
F_HOOK, F_HOOK2, F_KICK = font(F_BL, 132), font(F_BL, 150), font(F_SB, 26)
HOOK_WORDS = [(0.40, "In space,", F_HOOK, WHITE, 300), (0.98, "fire plays by", F_HOOK, WHITE, 455),
              (1.55, "different rules.", F_HOOK2, None, 630)]

def embers(t, strength=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for e in EMBERS:
        y = (e["y0"] - e["v"] * (t + 1.5)) % (H * 1.3) - H * 0.15
        x = e["x"] + math.sin(t * 1.7 + e["ph"]) * e["sw"]
        fl = 0.55 + 0.45 * math.sin(t * 9 + e["ph"] * 3)
        a = int(235 * fl * strength * clamp(y / (H * 0.9) + 0.25))
        col = (255, int(120 + 110 * e["hue"]), int(40 + 60 * e["hue"]))
        r = e["r"]
        d.ellipse((x - r, y - r, x + r, y + r), fill=col + (a,))
    glow = lay.filter(ImageFilter.GaussianBlur(6))
    return glow, lay

def gradient_text(text, f):
    """Text filled with a flame gradient (white-gold to orange)."""
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    w = int(tmp.textlength(text, font=f)) + 20
    h = int(f.size * 1.35)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((10, 0), text, font=f, fill=255)
    grad = Image.new("RGBA", (w, h))
    gd = ImageDraw.Draw(grad)
    for x in range(w):
        u = x / max(1, w - 1)
        gd.line((x, 0, x, h), fill=(255, int(lerp(214, 118, u)), int(lerp(120, 30, u)), 255))
    grad.putalpha(mask)
    return grad

_grad_cache = {}
def hook_frame(t):
    z = 1.0 + 0.045 * t
    bg = HOOK_BG.resize((W, H), Image.BICUBIC, box=((W - W / z) / 2, (H - H / z) / 2, (W + W / z) / 2, (H + H / z) / 2))
    dark = Image.new("RGB", (W, H), (4, 6, 18))
    frame = Image.composite(bg, dark, VIGNETTE)
    frame = Image.blend(dark, frame, ease(clamp(t / 0.5)))
    glow, sharp = embers(t)
    frame = frame.convert("RGBA")
    frame.alpha_composite(glow); frame.alpha_composite(sharp)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    ka = ease(clamp((t - 0.15) / 0.4))
    kick = "NASA SPACE APPS 2026  ·  FLAME IN FREEFALL"
    spaced = " ".join(kick)
    d.text(((W - d.textlength(spaced, font=F_KICK)) / 2, 190), spaced, font=F_KICK, fill=(255, 196, 140, int(200 * ka)))
    out_k = 1 - ease(clamp((t - 2.55) / 0.35))
    for t0, word, f, col, y in HOOK_WORDS:
        u = clamp((t - t0) / 0.38)
        if u <= 0:
            continue
        k = eout(u) * out_k
        if col is None:
            if word not in _grad_cache:
                _grad_cache[word] = gradient_text(word, f)
            g = _grad_cache[word]
            s = 1.12 - 0.12 * eout(u)
            gs = g.resize((int(g.width * s), int(g.height * s)), Image.LANCZOS)
            gs.putalpha(gs.getchannel("A").point(lambda v, k=k: int(v * k)))
            gl = gs.filter(ImageFilter.GaussianBlur(18))
            px, py = int((W - gs.width) / 2), int(y - (gs.height - g.height) / 2)
            ov.alpha_composite(gl, (px, py)); ov.alpha_composite(gl, (px, py)); ov.alpha_composite(gs, (px, py))
        else:
            dy = (1 - eout(u)) * 40
            d.text(((W - d.textlength(word, font=f)) / 2, y + dy), word, font=f, fill=col + (int(255 * k),))
    frame.alpha_composite(ov)
    return frame.convert("RGB")

# ---------------------------------------------------------------- end card
END_F1, END_F2, END_F3, END_F4 = font(F_SB, 46), font(F_M, 31), font(F_SB, 24), font(F_R, 19)
END_TEAM, END_NAMES = font(F_D, 40), font(F_SB, 31)
TEAM = ["Laila Mohamed", "Judy Adham", "Mostafa Fathy", "Yasmin Reda", "Youssif Hassan", "Dai Alaa"]
_end_art = None
def end_art():
    global _end_art
    if _end_art is None:
        h = 730; w = int(ILL.width * h / ILL.height)
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
    z = 1.0 + 0.03 * (t / 4.0)
    art = end_art()
    cw, ch = W / z, H / z
    art = art.resize((W, H), Image.LANCZOS, box=((W - cw) / 2, (H - ch) / 2 * 0.6, (W + cw) / 2, (H - ch) / 2 * 0.6 + ch))
    base = art.convert("RGBA")
    glow, sharp = embers(t + 4.0, strength=0.55)
    base.alpha_composite(glow); base.alpha_composite(sharp)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    k = ease(clamp((t - 0.3) / 0.5))
    def ctext(y, s, f, col, kk=k):
        d.text(((W - d.textlength(s, font=f)) / 2, y + (1 - kk) * 14), s, font=f, fill=col + (int(255 * kk),))
    ctext(738, "Space-fire data, made clear", END_F1, WHITE)
    pw = 560
    d.rounded_rectangle(((W - pw) / 2, 806 + (1 - k) * 14, (W + pw) / 2, 858 + (1 - k) * 14), 26,
                        fill=(255, 138, 36, int(38 * k)), outline=FLAME + (int(220 * k),), width=2)
    ctext(813, "flamelens-steel.vercel.app", END_F2, (255, 196, 140))
    k2 = ease(clamp((t - 0.7) / 0.5))
    ctext(884, "TEAM  ASTROSPARK", END_TEAM, FLAME, k2)
    k3 = ease(clamp((t - 1.0) / 0.5))
    ctext(944, "  ·  ".join(TEAM), END_NAMES, WHITE, k3)
    k4 = ease(clamp((t - 1.3) / 0.5))
    ctext(1000, "NASA Space Apps 2026  ·  NASA PSI data (CC0)", END_F3, (178, 192, 232), k4)
    ctext(1040, "Narration: Kokoro open-source AI voice  ·  every number from the live site",
          END_F4, (130, 142, 182), k4)
    base.alpha_composite(ov)
    return base.convert("RGB")

# ---------------------------------------------------------------- frame
def render_frame(t):
    if t < HOOK_END:
        im = hook_frame(t)
        if t > HOOK_END - 0.5:  # zoom-dissolve into the stage
            w, seg = window_frame(HOOK_END)
            draw_caption_row(w, HOOK_END, alpha=0.0)
            u = ease((t - (HOOK_END - 0.5)) / 0.5)
            s = 1.0 + 0.08 * (1 - u)
            w2 = w.resize((int(W * s), int(H * s)), Image.BICUBIC).crop((int((W * s - W) / 2), int((H * s - H) / 2),
                                                                          int((W * s + W) / 2), int((H * s + H) / 2)))
            im = Image.blend(im, w2.resize((W, H)), u)
        return im
    if t >= END_CARD:
        e = end_card(t - END_CARD)
        if t < END_CARD + 0.5:
            w, seg = window_frame(END_CARD - 1e-3)
            draw_caption_row(w, END_CARD - 1e-3)
            e = Image.blend(w, e, ease((t - END_CARD) / 0.5))
        if t > DUR - 0.6:
            e = Image.blend(e, Image.new("RGB", (W, H), (0, 0, 0)), ease((t - (DUR - 0.6)) / 0.6))
        return e
    frame, seg = window_frame(t)
    overlay_ui(frame, seg, t)
    light_leak(frame, t)
    draw_caption_row(frame, t, alpha=ease(clamp((t - HOOK_END) / 0.4)))
    return frame

# ---------------------------------------------------------------- audio: narration over ducked music
def read_wav(path):
    with wave.open(str(path)) as w:
        n, ch, sr = w.getnframes(), w.getnchannels(), w.getframerate()
        a = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    return a.reshape(-1, ch), sr

def resample(x, sr_in, sr_out):
    if sr_in == sr_out:
        return x
    import soundfile  # noqa: F401  (only to fail early if the venv is incomplete)
    n_out = int(len(x) * sr_out / sr_in)
    # windowed-sinc band-limited interpolation (factor 2 for 24 kHz -> 48 kHz)
    t_out = np.arange(n_out) * sr_in / sr_out
    k = np.arange(-16, 17)
    idx = np.floor(t_out).astype(int)
    frac = t_out - idx
    out = np.zeros(n_out, dtype=np.float32)
    xp = np.pad(x, (16, 17))
    for kk in k:
        arg = frac - kk
        wgt = np.sinc(arg) * (0.5 + 0.5 * np.cos(np.pi * arg / 17))
        out += xp[idx + kk + 16] * wgt
    return out

def build_audio(path_out):
    music, msr = read_wav(MUSIC)
    assert msr == SR, msr
    n = int(DUR * SR)
    music = np.pad(music, ((0, max(0, n - len(music))), (0, 0)))[:n]
    vo = np.zeros(n, dtype=np.float32)
    for line, t0 in zip(VO["lines"], VO_AT):
        x, sr = read_wav(VO_DIR / line["file"])
        x = resample(x[:, 0], sr, SR)
        x = x / (np.sqrt(np.mean(x ** 2)) + 1e-9) * 10 ** (-17 / 20)        # each line at -17 dBFS RMS
        i = int(t0 * SR)
        vo[i:i + len(x)] += x[: max(0, n - i)]
    # sidechain ducking: music drops about 10 dB under the voice (60 ms attack, 400 ms release)
    env = np.abs(vo) > 0.003
    act = np.convolve(env.astype(np.float32), np.ones(int(0.05 * SR)) / (0.05 * SR), mode="same") > 0.02
    g = np.where(act, 10 ** (-10 / 20), 1.0).astype(np.float32)
    sm = np.empty_like(g); cur = 1.0
    a_att, a_rel = math.exp(-1 / (0.06 * SR)), math.exp(-1 / (0.40 * SR))
    for i in range(0, n, 64):  # block-wise smoothing is enough at this resolution
        tgt = g[i]
        a = a_att if tgt < cur else a_rel
        cur = tgt + (cur - tgt) * a ** 64
        sm[i:i + 64] = cur
    mix = music * sm[:, None] * 1.15 + vo[:, None] * np.array([0.98, 1.0], dtype=np.float32)
    peak = np.max(np.abs(mix))
    if peak > 0.89:
        mix *= 0.89 / peak
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path_out), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    print("audio mixed:", path_out)

if PREVIEW:
    for t in [0.7, 1.4, 2.2, 2.95, 3.6, 5.5, 8.6, 10.9, 13.3, 14.35, 16.0, 18.6, 19.5, 20.5, 22.4, 24.0, 25.2, 26.6, 27.2, 29.0]:
        render_frame(t).save(OUT.parent / f"pv2_{t:05.2f}.jpg", quality=88)
    print("previews written"); sys.exit()

mixed = OUT.with_suffix(".mix.wav")
build_audio(mixed)
ff = imageio_ffmpeg.get_ffmpeg_exe()
cmd = [ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-i", str(mixed), "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-profile:v", "high",
       "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", str(OUT)]
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
for f in range(int(DUR * FPS)):
    proc.stdin.write(render_frame(f / FPS).tobytes())
    if f % 300 == 0:
        print("frame", f, flush=True)
proc.stdin.close(); proc.wait()
print("wrote", OUT, proc.returncode)
