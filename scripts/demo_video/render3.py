"""v3 FlameLens video (30 s, 1920x1080, 60 fps): Laila on camera in a glowing circle, then the live dashboard
under her voice-over, word-by-word subtitles, an Apollo 1 memorial and the team end card.

Inputs come from prep3.py (cleaned voice pieces, face frames, aligned subtitle words) and capture2.py (shots).

Usage:
  render3.py timing <timing.json>
  render3.py <work_dir> <shots_dir> <music.wav> <illustration> <logo.png> <out.mp4> [--preview]
"""
import json
import math
import random
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

W, H, FPS, DUR, SR = 1920, 1080, 60, 30.0, 48000

# ---------------------------------------------------------------- timeline (seconds)
AT = {"intro": 0.0, "story": 5.85, "vo": 13.75}      # where each voice piece starts
TALK_END = 13.4                                      # Laila on camera until here, then the dashboard
FLAMELENS_AT = 10.0                                  # "That's why we have built FlameLens": colour and music return
MEMORIAL, END_CARD = 24.2, 26.85
SEG = [  # start, end, shot, camera start (cx, cy, zoom), camera end
    (13.4, 15.85, "a_top_rover", (960, 400, 1.05), (1000, 330, 1.35)),
    (15.85, 17.55, "a_top_rover", (1200, 260, 1.45), (1480, 200, 1.7)),
    (17.55, 19.0, "c_case_rover", (480, 520, 1.45), (460, 560, 1.6)),
    (19.0, 20.6, "g_drawer", (1150, 620, 1.15), (1560, 780, 1.42)),
    (20.6, 22.0, "c_case_rover", (480, 560, 1.6), (440, 620, 1.75)),
    (22.0, MEMORIAL, "h_campaign_n3", (1400, 420, 1.3), (1400, 520, 1.45)),
]
SCENES = [s[0] for s in SEG] + [MEMORIAL]
XFADE = 0.3

if len(sys.argv) > 2 and sys.argv[1] == "timing":
    Path(sys.argv[2]).write_text(json.dumps({"intro_end": FLAMELENS_AT, "end_card": END_CARD, "scenes": SCENES,
                                             "clicks": []}), encoding="utf-8")
    print("timing written"); sys.exit()

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont  # noqa: E402
import imageio_ffmpeg  # noqa: E402

WORK, SHOTS, MUSIC, ILLU, LOGO, OUT = (Path(a) for a in sys.argv[1:7])
PREVIEW = "--preview" in sys.argv
META = json.loads((SHOTS / "meta.json").read_text(encoding="utf-8"))
PIECES = json.loads((WORK / "pieces.json").read_text(encoding="utf-8"))
FRAMES = {k: np.load(WORK / f"{k}_frames.npy", mmap_mode="r") for k in ("intro", "story")}

F_B, F_SB, F_R, F_M, F_D, F_BL = ("C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/seguisb.ttf",
                                  "C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/consolab.ttf",
                                  "C:/Windows/Fonts/bahnschrift.ttf", "C:/Windows/Fonts/seguibl.ttf")
FLAME, CYAN, WHITE, GREEN, RED = (255, 138, 36), (92, 214, 255), (255, 255, 255), (80, 220, 150), (255, 96, 96)
font = lambda p, s: ImageFont.truetype(p if Path(p).exists() else F_B, s)
ease = lambda t: t * t * (3 - 2 * t)
eout = lambda t: 1 - (1 - t) ** 3
lerp = lambda a, b, t: a + (b - a) * t
clamp = lambda v: max(0.0, min(1.0, v))
win = lambda t, a, b, fi=0.4, fo=0.35: min(ease(clamp((t - a) / fi)), ease(clamp((b - t) / fo)))

CW, CH = 1520, 855
WX, BAR, WY = (W - CW) // 2, 38, 18
CX, CY = WX, WY + BAR

# ---------------------------------------------------------------- shared layers
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
    bg.paste(g.filter(ImageFilter.GaussianBlur(160)), (0, 0), g.filter(ImageFilter.GaussianBlur(160)))
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
    for i, col in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
        x = WX + 22 + i * 22
        d.ellipse((x - 6, WY + BAR / 2 - 6, x + 6, WY + BAR / 2 + 6), fill=col + (255,))
    pw = 420; px = WX + (CW - pw) / 2
    d.rounded_rectangle((px, WY + 7, px + pw, WY + BAR - 7), 12, fill=(30, 38, 80, 255))
    f = font(F_SB, 17); txt = "flamelens-steel.vercel.app"
    d.text((px + (pw - d.textlength(txt, font=f)) / 2 + 8, WY + 9), txt, font=f, fill=(190, 202, 235, 255))
    d.rounded_rectangle((WX, WY, WX + CW, CY + CH), 16, outline=(255, 255, 255, 40), width=1)
    return lay

STAGE = build_stage()
DARK = ImageEnhance.Brightness(STAGE).enhance(0.35)
WINDOW = build_window()
CONTENT_MASK = rounded_mask((CW, CH + 16), 16).crop((0, 16, CW, CH + 16))
ILL = Image.open(ILLU).convert("RGB")
LOGO_IM = Image.open(LOGO).convert("RGBA")

_er = random.Random(11)
EMBERS = [dict(x=_er.uniform(0, W), y0=_er.uniform(H * 0.3, H * 1.3), v=_er.uniform(70, 260), r=_er.uniform(1.4, 4.6),
               ph=_er.uniform(0, 6.28), sw=_er.uniform(10, 46), hue=_er.random()) for _ in range(150)]

def embers(frame, t, strength=1.0, speed=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for e in EMBERS:
        y = (e["y0"] - e["v"] * speed * (t + 1.5)) % (H * 1.3) - H * 0.15
        x = e["x"] + math.sin(t * 1.7 + e["ph"]) * e["sw"]
        fl = 0.55 + 0.45 * math.sin(t * 9 + e["ph"] * 3)
        a = int(235 * fl * strength * clamp(y / (H * 0.9) + 0.25))
        r = e["r"]
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, int(120 + 110 * e["hue"]), int(40 + 60 * e["hue"]), a))
    frame.alpha_composite(lay.filter(ImageFilter.GaussianBlur(5)))
    frame.alpha_composite(lay)

def gradient_text(text, f):
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    w = int(tmp.textlength(text, font=f)) + 20; h = int(f.size * 1.35)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((10, 0), text, font=f, fill=255)
    grad = Image.new("RGBA", (w, h)); gd = ImageDraw.Draw(grad)
    for x in range(w):
        u = x / max(1, w - 1)
        gd.line((x, 0, x, h), fill=(255, int(lerp(214, 118, u)), int(lerp(120, 30, u)), 255))
    grad.putalpha(mask)
    return grad

def fade_rgba(im, k):
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * k))); return im

# ---------------------------------------------------------------- voice level (drives the ring pulse)
def read_wav(path):
    with wave.open(str(path)) as w:
        n, ch, sr = w.getnframes(), w.getnchannels(), w.getframerate()
        a = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    return a.reshape(-1, ch)[:, 0], sr

VOICE = np.zeros(int(DUR * SR), np.float32)
for name, t0 in AT.items():
    x, sr = read_wav(WORK / f"{name}.wav")
    assert sr == SR, sr
    i = int(t0 * SR)
    VOICE[i:i + len(x)] += x[: len(VOICE) - i]
_hop = SR // FPS
LEVEL = np.sqrt(np.convolve(VOICE ** 2, np.ones(_hop * 4) / (_hop * 4), mode="same")[::_hop])
LEVEL = np.clip(LEVEL / (np.percentile(LEVEL[LEVEL > 1e-4], 95) + 1e-9), 0, 1)
level = lambda t: float(LEVEL[min(len(LEVEL) - 1, int(t * FPS))])

# ---------------------------------------------------------------- subtitles (word by word)
SUBS = []  # (t_show, t_hide, [(word, t0, t1)])
for name, t0 in AT.items():
    p = PIECES[name]
    for li, _ in enumerate(p["lines"]):
        ws = [(w["w"], t0 + w["t0"], t0 + w["t1"]) for w in p["words"] if w["line"] == li]
        SUBS.append([ws[0][1] - 0.12, ws[-1][2] + 0.45, ws])
for a, b in zip(SUBS, SUBS[1:]):
    a[1] = min(a[1], b[0])
F_SUB = font(F_SB, 42)

def draw_subtitle(frame, t, y=990):
    for a, b, ws in SUBS:
        if not (a <= t <= b):
            continue
        k = win(t, a, b, 0.15, 0.15)
        d0 = ImageDraw.Draw(frame)
        sp = d0.textlength(" ", font=F_SUB)
        widths = [d0.textlength(w, font=F_SUB) for w, _, _ in ws]
        total = sum(widths) + sp * (len(ws) - 1)
        x = (W - total) / 2
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.rounded_rectangle((x - 30, y - 14, x + total + 30, y + 62), 34, fill=(6, 9, 26, int(175 * k)))
        for (w, t0, t1), ww in zip(ws, widths):
            if t < t0:
                col, al = (205, 214, 240), 0.38
            elif t <= t1 + 0.05:
                col, al = (255, 196, 120), 1.0
            else:
                col, al = WHITE, 1.0
            lift = 6 * (1 - eout(clamp((t - t0) / 0.18))) if t >= t0 else 6
            d.text((x, y - 2 + lift), w, font=F_SUB, fill=col + (int(255 * al * k),))
            x += ww + sp
        frame.alpha_composite(ov)

# ---------------------------------------------------------------- talk scenes: Laila in a glowing circle
SQ = 440
F_KICK, F_NAME, F_TEAM = font(F_SB, 24), font(F_BL, 86), font(F_D, 40)
F_CH, F_AP, F_AP2, F_NAMES = font(F_BL, 104), font(F_BL, 120), font(F_SB, 40), font(F_SB, 30)
_ring_cache = {}

def face(t):
    name = "intro" if t < AT["story"] else "story"
    fr = FRAMES[name]
    i = min(len(fr) - 1, max(0, int((t - AT[name]) * 30)))
    return Image.fromarray(np.asarray(fr[i]))

def circle_mask(d):
    if d not in _ring_cache:
        m = Image.new("L", (d * 2, d * 2), 0)
        ImageDraw.Draw(m).ellipse((4, 4, d * 2 - 4, d * 2 - 4), fill=255)
        _ring_cache[d] = m.resize((d, d), Image.LANCZOS)
    return _ring_cache[d]

def portrait(frame, t, cx, cy, D, sat, warm):
    D = int(D)
    im = face(t).resize((D, D), Image.LANCZOS)
    if sat < 0.99:
        im = ImageEnhance.Color(im).enhance(sat)
        im = ImageEnhance.Brightness(im).enhance(lerp(0.82, 1.0, sat))
    pad = 120
    S = D + 2 * pad
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    R = D / 2; c = S / 2
    lv = level(t)
    ring_col = tuple(int(lerp(170, v, warm)) for v in FLAME)
    halo = R + 18 + 26 * lv
    d.ellipse((c - halo, c - halo, c + halo, c + halo), fill=ring_col + (int(lerp(60, 150, lv) * (0.5 + 0.5 * warm)),))
    lay = lay.filter(ImageFilter.GaussianBlur(26))
    d = ImageDraw.Draw(lay)
    for r_, col, w_, a0, span, spd in ((R + 16, ring_col, 6, 0, 120, 38), (R + 16, ring_col, 6, 180, 70, 38),
                                       (R + 32, CYAN, 3, 90, 150, -24), (R + 46, (255, 255, 255), 2, 250, 60, 15)):
        a = a0 + spd * t
        d.arc((c - r_, c - r_, c + r_, c + r_), a, a + span, fill=col + (230,), width=w_)
    d.ellipse((c - R - 5, c - R - 5, c + R + 5, c + R + 5), outline=(255, 255, 255, 70), width=2)
    lay.paste(im, (pad, pad), circle_mask(D))
    frame.alpha_composite(lay, (int(cx - S / 2), int(cy - S / 2)))

def text_at(d, x, y, s, f, col, k, dy=24):
    d.text((x, y + (1 - eout(k)) * dy), s, font=f, fill=col + (int(255 * k),))

_grad = {}
def grad(s, f):
    if s not in _grad:
        _grad[s] = gradient_text(s, f)
    return _grad[s]

def talk_frame(t):
    st = AT["story"]
    mood = ease(clamp((t - (st - 0.3)) / 0.6)) * (1 - ease(clamp((t - FLAMELENS_AT) / 0.9)))  # 1 = memorial mood
    frame = Image.blend(STAGE, DARK, 0.85 * mood).convert("RGBA")
    embers(frame, t, strength=lerp(0.8, 0.35, mood), speed=lerp(1.0, 0.45, mood))
    # circle moves left and shrinks a little for the story
    m2 = ease(clamp((t - (st - 0.35)) / 0.7))
    intro_in = eout(clamp(t / 0.7))
    cx, cy, D = lerp(610, 540, m2), 470, lerp(600, 560, m2) * lerp(0.86, 1.0, intro_in)
    sat = lerp(1.0, 0.25, mood)
    warm = 1 - mood
    portrait(frame, t, cx, cy, D, sat, warm)
    if t < 0.5:
        frame = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), frame, ease(t / 0.5))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    X = 1040
    # intro: who we are
    k = win(t, 0.25, 3.05)
    if k > 0:
        text_at(d, X, 300, "N A S A   S P A C E   A P P S   2 0 2 6", F_KICK, (255, 196, 140), k)
        text_at(d, X, 350, "Laila Mohamed", F_NAME, WHITE, win(t, 0.45, 3.05))
        text_at(d, X, 470, "TEAM ASTROSPARK", F_TEAM, FLAME, win(t, 1.6, 3.05))
    # intro: the challenge
    k = win(t, 3.1, st - 0.2)
    if k > 0:
        text_at(d, X, 330, "T H E   C H A L L E N G E", F_KICK, (255, 196, 140), k)
        g = fade_rgba(grad("Flame in", F_CH), win(t, 3.25, st - 0.2))
        ov.alpha_composite(g, (X - 10, int(370 + (1 - eout(win(t, 3.25, st - 0.2))) * 24)))
        g = fade_rgba(grad("Freefall", F_CH), win(t, 3.55, st - 0.2))
        ov.alpha_composite(g, (X - 10, int(500 + (1 - eout(win(t, 3.55, st - 0.2))) * 24)))
    # story: Apollo 1
    k = win(t, st + 0.05, FLAMELENS_AT - 0.1, 0.5, 0.45)
    if k > 0:
        text_at(d, X, 250, "27 JANUARY 1967  ·  LAUNCH COMPLEX 34", F_KICK, (200, 208, 230), k)
        text_at(d, X, 290, "APOLLO 1", F_AP, WHITE, k)
        k2 = win(t, st + 1.55, FLAMELENS_AT - 0.1, 0.5, 0.45)
        text_at(d, X, 450, "100 % oxygen  ·  16.7 psi", F_AP2, (255, 170, 110), k2)
        k3 = win(t, st + 2.85, FLAMELENS_AT - 0.1, 0.6, 0.45)
        d.rectangle((X, 540, X + 520 * eout(k3), 542), fill=(255, 255, 255, int(110 * k3)))
        for i, nm in enumerate(["Virgil Grissom", "Edward White", "Roger Chaffee"]):
            text_at(d, X, 562 + i * 46, nm, F_NAMES, (225, 230, 245), win(t, st + 2.95 + i * 0.25, FLAMELENS_AT - 0.1, 0.6, 0.45), 12)
    # message: FlameLens
    k = win(t, FLAMELENS_AT + 0.05, TALK_END + 0.4, 0.6, 0.2)
    if k > 0:
        lg = LOGO_IM.resize((150, 150), Image.LANCZOS)
        s = lerp(0.8, 1.0, eout(k))
        lg = fade_rgba(lg.resize((int(150 * s), int(150 * s)), Image.LANCZOS), k)
        ov.alpha_composite(lg, (int(X + 75 - lg.width / 2), int(330 - lg.height / 2 + 60)))
        g = fade_rgba(grad("FlameLens", F_CH), win(t, FLAMELENS_AT + 1.3, TALK_END + 0.4, 0.5, 0.2))
        ov.alpha_composite(g, (X - 10, 440))
        text_at(d, X, 590, "so their story stays alive", F_AP2, (225, 230, 245), win(t, FLAMELENS_AT + 2.5, TALK_END + 0.4, 0.5, 0.2))
    frame.alpha_composite(ov)
    return frame

# ---------------------------------------------------------------- dashboard scenes (same engine as v2)
_imgs = {}
def shot(name):
    if name not in _imgs:
        _imgs[name] = Image.open(SHOTS / f"{name}.png").convert("RGB")
    return _imgs[name]

def center(sh, key):
    x, y, w, h = META[sh][key]; return (x + w / 2, y + h / 2)

def cam_at(seg, t):
    s0, s1, _, a, b = seg
    u = ease(clamp((t - s0) / (s1 - s0)))
    return tuple(lerp(a[i], b[i], u) for i in range(3))

def box(cam):
    cx, cy, z = cam; w, h = W / z, H / z
    return min(max(cx - w / 2, 0), W - w), min(max(cy - h / 2, 0), H - h), w, h

def content(seg, t):
    x0, y0, w, h = box(cam_at(seg, t))
    return shot(seg[2]).resize((CW, CH), Image.BICUBIC, box=(x0 * 2, y0 * 2, (x0 + w) * 2, (y0 + h) * 2), reducing_gap=2.0)

def to_screen(seg, t, x, y):
    x0, y0, w, h = box(cam_at(seg, t))
    return (CX + (x - x0) / w * CW, CY + (y - y0) / h * CH)

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
    return frame.convert("RGBA"), seg

HIGHLIGHTS = [
    (14.3, 15.8, "a_top_rover", "controls", FLAME),
    (16.0, 17.5, "a_top_rover", "chip", CYAN),
    (19.2, 20.55, "g_drawer", "drawer", GREEN),
    (20.75, 21.95, "c_case_rover", "o2", RED), (20.95, 21.95, "c_case_rover", "psi", RED),
]
# every number here is on the live dashboard (rover preset; second audit 14 Nov)
CALLOUTS = [
    (14.4, 15.8, "a_top_rover", "controls", (1180, 560), "flame", "1 · Enter your cabin's air", "Moon rover: 30 % O₂ · 10.2 psi · Moon gravity", FLAME, None),
    (16.0, 17.5, "a_top_rover", "chip", (430, 470), "check", "{n}", "2 · real NASA PSI runs from 18 investigations", CYAN, (0, 2003, 16.0, 17.1)),
    (17.7, 18.95, "c_case_rover", "conditions", (1060, 300), "check", "Compared condition by condition", "rover: 2 of 5 conditions backed by matching runs", CYAN, None),
    (19.2, 20.55, "g_drawer", "drawer", (330, 300), "check", "3 · Every result cited", "PSI-25-0023 · BASS-II · doi 10.60555/4qc4-de67", GREEN, None),
    (20.75, 21.95, "c_case_rover", "o2", (1090, 240), "cross", "Not yet tested: 30 % O₂", "0 solid runs (134 gas and droplet runs not counted)", RED, None),
    (20.95, 21.95, "c_case_rover", "psi", (1090, 500), "cross", "Not yet tested: 10.2 psi", "0 solid runs (107 droplet runs not counted)", RED, None),
    (21.15, 21.95, "c_case_rover", None, (1090, 760), "check", "Tested: airflow", "308 solid runs back it", GREEN, None),
    (22.2, 24.1, "h_campaign_n3", "sum", (300, 560), "flame", "3 tests → 5 habitat designs", "Moon and Mars cabins: what NASA could test next", FLAME, None),
]
F_CT, F_CS, F_CB = font(F_B, 34), font(F_R, 22), font(F_BL, 64)

def icon(d, kind, x, y, col, a):
    r = 22
    d.ellipse((x - r, y - r, x + r, y + r), fill=col + (int(235 * a),))
    ink = (12, 16, 36, int(255 * a))
    if kind == "check":
        d.line((x - 10, y + 1, x - 3, y + 9, x + 11, y - 8), fill=ink, width=5, joint="curve")
    elif kind == "cross":
        d.line((x - 8, y - 8, x + 8, y + 8), fill=ink, width=5); d.line((x - 8, y + 8, x + 8, y - 8), fill=ink, width=5)
    elif kind == "flame":
        d.polygon([(x, y - 14), (x + 9, y + 2), (x + 6, y + 12), (x - 6, y + 12), (x - 9, y + 2)], fill=ink)

def overlays(frame, seg, t):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for a, b, sh, key, col in HIGHLIGHTS:
        if sh == seg[2] and a <= t <= b and META[sh].get(key):
            fade = min(1, (t - a) / 0.35, (b - t) / 0.3)
            x, y, w, h = META[sh][key]
            (sx0, sy0), (sx1, sy1) = to_screen(seg, t, x - 6, y - 6), to_screen(seg, t, x + w + 6, y + h + 6)
            sx0, sy0, sx1, sy1 = max(sx0, CX + 4), max(sy0, CY + 4), min(sx1, CX + CW - 4), min(sy1, CY + CH - 4)
            if sx1 > sx0 + 10 and sy1 > sy0 + 10:
                d.rounded_rectangle((sx0, sy0, sx1, sy1), 18, outline=col + (int(235 * fade),), width=5)
    frame.alpha_composite(ov.filter(ImageFilter.GaussianBlur(7)))
    frame.alpha_composite(ov)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for t0, t1, sh, key, (bx, by), ic, title, sub, col, counter in CALLOUTS:
        if not (t0 <= t <= t1) or sh != seg[2]:
            continue
        d = ImageDraw.Draw(ov)
        u = clamp((t - t0) / 0.45)
        a = min(eout(u), clamp((t1 - t) / 0.3))
        if counter:
            n0, n1, c0, c1 = counter
            title = title.replace("{n}", f"{int(round(lerp(n0, n1, eout(clamp((t - c0) / (c1 - c0)))))):,}")
            tf = F_CB
        else:
            tf = F_CT
        tw = max(d.textlength(title, font=tf), d.textlength(sub, font=F_CS))
        cw = int(tw + 112); ch = int(tf.size * 1.25 + 46)
        x0, y0 = bx, by + (1 - eout(u)) * 18
        if key and META[sh].get(key):
            ax, ay = to_screen(seg, t, *center(sh, key))
            ax = min(max(ax, CX + 8), CX + CW - 8); ay = min(max(ay, CY + 8), CY + CH - 8)
            sx = x0 if ax < x0 else (x0 + cw if ax > x0 + cw else ax)
            sy = y0 + ch / 2
            kk = eout(clamp((t - t0 - 0.15) / 0.4)) * a
            d.line((sx, sy, lerp(sx, ax, kk), lerp(sy, ay, kk)), fill=col + (int(220 * a),), width=3)
            if kk > 0.95:
                d.ellipse((ax - 9, ay - 9, ax + 9, ay + 9), outline=col + (int(255 * a),), width=3)
                d.ellipse((ax - 4, ay - 4, ax + 4, ay + 4), fill=col + (int(255 * a),))
        sh_ = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh_).rounded_rectangle((x0 + 6, y0 + 12, x0 + cw + 6, y0 + ch + 12), 20, fill=(0, 0, 0, int(150 * a)))
        ov.alpha_composite(sh_.filter(ImageFilter.GaussianBlur(14)))
        d = ImageDraw.Draw(ov)
        d.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 20, fill=(14, 19, 44, int(238 * a)), outline=col + (int(230 * a),), width=3)
        d.rectangle((x0 + 3, y0 + 18, x0 + 8, y0 + ch - 18), fill=col + (int(255 * a),))
        icon(d, ic, x0 + 50, y0 + ch / 2, col, a)
        d.text((x0 + 86, y0 + 14), title, font=tf, fill=(255, 255, 255, int(255 * a)))
        d.text((x0 + 86, y0 + 14 + tf.size * 1.2), sub, font=F_CS, fill=(190, 202, 235, int(255 * a)))
    frame.alpha_composite(ov)

LEAK = Image.new("RGBA", (W * 2, H), (0, 0, 0, 0))
_ld = ImageDraw.Draw(LEAK)
_ld.ellipse((700, -300, 1700, 1300), fill=(255, 150, 60, 150)); _ld.ellipse((1100, 100, 1500, 900), fill=(255, 220, 160, 120))
LEAK = LEAK.filter(ImageFilter.GaussianBlur(170))

def light_leak(frame, t):
    for s in SCENES[1:]:
        u = (t - (s - 0.22)) / 0.6
        if 0 <= u <= 1:
            a = math.sin(math.pi * u) * 0.5
            x = int(lerp(-W * 0.9, -W * 0.1, u))
            band = LEAK.crop((-x, 0, -x + W, H))
            frame.alpha_composite(fade_rgba(band, a))

# ---------------------------------------------------------------- memorial and end card
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
        a = np.clip(np.minimum.reduce([xx / e, (w - 1 - xx) / e, yy / 60.0, (h - 1 - yy) / e]), 0, 1)
        art.putalpha(Image.fromarray((ease(a) * 255).astype("uint8")))
        base = STAGE.copy().convert("RGBA")
        base.alpha_composite(art, ((W - w) // 2, 0))
        _end_art = base.convert("RGB")
    return _end_art

def art_frame(t):
    z = 1.0 + 0.012 * (t - MEMORIAL)
    cw, ch = W / z, H / z
    art = end_art().resize((W, H), Image.LANCZOS, box=((W - cw) / 2, (H - ch) / 2 * 0.6, (W + cw) / 2, (H - ch) / 2 * 0.6 + ch))
    f = art.convert("RGBA")
    embers(f, t, strength=0.55)
    return f

def ctext(d, y, s, f, col, k):
    d.text(((W - d.textlength(s, font=f)) / 2, y + (1 - k) * 14), s, font=f, fill=col + (int(255 * k),))

def memorial_frame(t):
    f = art_frame(t)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    k = win(t, MEMORIAL + 0.6, END_CARD + 0.05, 0.6, 0.35)
    ctext(d, 760, "I N   M E M O R Y   O F   T H E   A P O L L O   1   C R E W", F_KICK, (255, 196, 140), k)
    ctext(d, 806, "Virgil Grissom  ·  Edward White  ·  Roger Chaffee", END_F1, WHITE, win(t, MEMORIAL + 1.0, END_CARD + 0.05, 0.6, 0.35))
    f.alpha_composite(ov)
    return f

def end_frame(t):
    f = art_frame(t)
    te = t - END_CARD
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    k = ease(clamp((te - 0.1) / 0.5))
    ctext(d, 738, "Every crew deserves to come home", END_F1, WHITE, k)
    pw = 560
    d.rounded_rectangle(((W - pw) / 2, 806 + (1 - k) * 14, (W + pw) / 2, 858 + (1 - k) * 14), 26,
                        fill=(255, 138, 36, int(38 * k)), outline=FLAME + (int(220 * k),), width=2)
    ctext(d, 813, "flamelens-steel.vercel.app", END_F2, (255, 196, 140), k)
    ctext(d, 884, "TEAM  ASTROSPARK", END_TEAM, FLAME, ease(clamp((te - 0.4) / 0.5)))
    ctext(d, 944, "  ·  ".join(TEAM), END_NAMES, WHITE, ease(clamp((te - 0.65) / 0.5)))
    k4 = ease(clamp((te - 0.9) / 0.5))
    ctext(d, 1000, "NASA Space Apps 2026  ·  Flame in Freefall  ·  NASA PSI data (CC0)", END_F3, (178, 192, 232), k4)
    ctext(d, 1040, "Voice: Laila Mohamed  ·  every number from the live site  ·  in memory of the Apollo 1 crew", END_F4, (130, 142, 182), k4)
    f.alpha_composite(ov)
    return f

# ---------------------------------------------------------------- frame
def zoom(im, s):
    w2 = im.resize((int(W * s), int(H * s)), Image.BICUBIC)
    return w2.crop((int((W * s - W) / 2), int((H * s - H) / 2), int((W * s - W) / 2) + W, int((H * s - H) / 2) + H))

def dash_frame(t):
    frame, seg = window_frame(t)
    overlays(frame, seg, t)
    light_leak(frame, t)
    return frame

def render_frame(t):
    if t < TALK_END:
        f = talk_frame(t)
    elif t < TALK_END + 0.45:  # the talk scene pushes in and dissolves into the dashboard
        u = ease((t - TALK_END) / 0.45)
        a = zoom(talk_frame(t), 1 + 0.12 * u)
        b = zoom(dash_frame(t), 1.08 - 0.08 * u)
        f = Image.blend(a, b, u)
    elif t < MEMORIAL:
        f = dash_frame(t)
    elif t < MEMORIAL + 0.6:
        f = Image.blend(dash_frame(t), memorial_frame(t), ease((t - MEMORIAL) / 0.6))
    elif t < END_CARD:
        f = memorial_frame(t)
    elif t < END_CARD + 0.4:
        f = Image.blend(memorial_frame(t), end_frame(t), ease((t - END_CARD) / 0.4))
    else:
        f = end_frame(t)
    f = f.convert("RGBA")
    draw_subtitle(f, t)
    f = f.convert("RGB")
    if t > DUR - 0.6:
        f = Image.blend(f, Image.new("RGB", (W, H), (0, 0, 0)), ease((t - (DUR - 0.6)) / 0.6))
    return f

# ---------------------------------------------------------------- audio: Laila's voice over the music
def build_audio(path_out):
    with wave.open(str(MUSIC)) as w:
        music = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32).reshape(-1, 2) / 32768
    n = int(DUR * SR)
    music = np.pad(music, ((0, max(0, n - len(music))), (0, 0)))[:n]
    T = np.arange(n) / SR
    st = AT["story"]
    # music: soft under the intro, silent for the Apollo 1 story, back when FlameLens is named
    g = np.interp(T, [0, st - 0.6, st, FLAMELENS_AT, FLAMELENS_AT + 1.2, DUR], [0.45, 0.45, 0.0, 0.0, 1.0, 1.0])
    vo = VOICE * 10 ** (1 / 20)
    act = np.convolve((np.abs(vo) > 0.01).astype(np.float32), np.ones(int(0.05 * SR)) / (0.05 * SR), mode="same") > 0.02
    dk = np.where(act, 10 ** (-11 / 20), 1.0).astype(np.float32)
    sm = np.empty_like(dk); cur = 1.0
    a_att, a_rel = math.exp(-1 / (0.06 * SR)), math.exp(-1 / (0.45 * SR))
    for i in range(0, n, 64):
        tgt = dk[i]; cur = tgt + (cur - tgt) * (a_att if tgt < cur else a_rel) ** 64; sm[i:i + 64] = cur
    mix = music * (g * sm)[:, None] * 1.1 + vo[:, None]
    peak = np.max(np.abs(mix))
    if peak > 0.89:
        mix *= 0.89 / peak
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path_out), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    print("audio mixed:", path_out)

if PREVIEW:
    ts = [float(a) for a in sys.argv[sys.argv.index("--preview") + 1:]] or \
         [1.5, 4.5, 6.4, 8.0, 9.4, 11.0, 12.8, 13.6, 15.0, 16.8, 18.3, 19.8, 21.5, 23.0, 25.3, 28.5]
    for t in ts:
        render_frame(t).save(OUT.parent / f"pv3_{t:05.2f}.jpg", quality=85)
    print("previews written"); sys.exit()

mixed = OUT.with_suffix(".mix.wav")
build_audio(mixed)
ff = imageio_ffmpeg.get_ffmpeg_exe()
cmd = [ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-i", str(mixed), "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-profile:v", "high",
       "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", str(OUT)]
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
for fi in range(int(DUR * FPS)):
    proc.stdin.write(render_frame(fi / FPS).tobytes())
    if fi % 300 == 0:
        print("frame", fi, flush=True)
proc.stdin.close(); proc.wait()
print("wrote", OUT, proc.returncode)
