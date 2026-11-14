"""FlameLens demo soundtrack (30 s, 48 kHz stereo), synthesized from scratch: no samples, no copyright.

Cinematic-tech bed in D major (D - Bm - G - A, resolving to D on the end card): warm pads, sub bass with gentle
pumping, FM-bell arpeggio, soft pulse, plus designed effects: logo shimmer swell, whooshes on scene changes,
glass-tap UI clicks, a riser into the end card and an impact with a bell chord.

Usage: python soundtrack.py out.wav [timing.json]
Timing constants below must match render.py (scene changes, clicks, end card); the narrated cut passes them in a file.
"""
import sys, wave
import numpy as np

SR, DUR = 48000, 30.0
N = int(SR * DUR)
T = np.arange(N) / SR
rng = np.random.default_rng(2026)

INTRO_END = 1.6           # logo sting -> dashboard
END_CARD = 27.6           # impact + logo end card
SCENES = [1.6, 5.2, 8.9, 13.3, 17.6, 21.9, 25.4]   # whooshes
CLICKS = [5.0, 15.1, 18.6, 23.05, 24.25]           # button presses
# Optional timing file (narrated cut): soundtrack.py out.wav timing.json  {"intro_end", "end_card", "scenes", "clicks"}
if len(sys.argv) > 2:
    import json
    _tm = json.loads(open(sys.argv[2], encoding="utf-8").read())
    INTRO_END, END_CARD = _tm["intro_end"], _tm["end_card"]
    SCENES, CLICKS = _tm["scenes"], _tm["clicks"]
RISER_START = END_CARD - 2.0
BPM = 96.0
BEAT = 60.0 / BPM

mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)


def stereo(x, pan=0.0):
    """pan -1 (left) .. +1 (right), equal-power."""
    a = (pan + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], axis=1)


def fft_filter(x, lo=None, hi=None, slope=0.15):
    """Zero-phase band filter with soft (log-frequency) edges."""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR) + 1e-6
    g = np.ones_like(f)
    if lo:
        g *= 1 / (1 + (lo / f) ** (2 / slope * 0.1 + 2))
    if hi:
        g *= 1 / (1 + (f / hi) ** (2 / slope * 0.1 + 2))
    return np.fft.irfft(X * g, n)


def place(buf, start, sig):
    i = int(start * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    if i < 0:
        sig, i = sig[-i:], 0
    buf[i:j] += sig[: j - i]


def env_adsr(n, a, r, sustain_len):
    t = np.arange(n) / SR
    e = np.clip(t / a, 0, 1)
    e = e * e * (3 - 2 * e)
    rel = np.clip((t - sustain_len) / r, 0, 1)
    return e * (1 - rel) ** 2


# ---------------------------------------------------------------- instruments

def pad_note(freq, length, a=1.4, r=2.2):
    n = int((length + r) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for det in (-7, 0, 7):  # cents
        f = freq * 2 ** (det / 1200)
        ph = rng.uniform(0, 2 * np.pi)
        for h in range(1, 9):
            out += np.sin(2 * np.pi * f * h * t + ph * h) * (1 / h) * np.exp(-h / 5.0)
    out *= 1 / 3
    lfo = 1 + 0.08 * np.sin(2 * np.pi * 0.23 * t + rng.uniform(0, 6))
    return out * lfo * env_adsr(n, a, r, length)


def fm_bell(freq, length=1.2, index=2.2, decay=0.45):
    n = int(length * SR)
    t = np.arange(n) / SR
    mod = index * np.exp(-t / 0.18) * np.sin(2 * np.pi * freq * 2.0 * t)
    s = np.sin(2 * np.pi * freq * t + mod) + 0.25 * np.sin(2 * np.pi * freq * 3.01 * t) * np.exp(-t / 0.12)
    att = np.clip(t / 0.004, 0, 1)
    return s * att * np.exp(-t / decay)


def sub(freq, length):
    n = int((length + 0.8) * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * freq * t) + 0.18 * np.sin(2 * np.pi * 2 * freq * t)
    return s * env_adsr(n, 0.6, 0.8, length)


def thump(level=1.0):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 46 + 70 * np.exp(-t / 0.03)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return level * np.sin(ph) * np.exp(-t / 0.16) * np.clip(t / 0.002, 0, 1)


def hat():
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    x = fft_filter(rng.standard_normal(n), lo=7000)
    return x * np.exp(-t / 0.012)


def whoosh(length=0.75):
    n = int(length * SR)
    t = np.arange(n) / SR
    u = t / length
    env = np.sin(np.pi * u) ** 2 * (0.6 + 0.4 * u)
    noise = rng.standard_normal(n)
    low = fft_filter(noise, lo=250, hi=1800)
    high = fft_filter(noise, lo=1800, hi=7500)
    x = low * (1 - u) + high * u  # brightens as it passes: an airy sweep
    x = x / (np.max(np.abs(x)) + 1e-9) * env
    pans = -0.8 + 1.6 * u
    return np.stack([x * np.cos((pans + 1) * np.pi / 4), x * np.sin((pans + 1) * np.pi / 4)], axis=1)


def glass_tap():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * 2093 * t) * np.exp(-t / 0.06) + 0.6 * np.sin(2 * np.pi * 3136 * t) * np.exp(-t / 0.035)
         + 0.35 * np.sin(2 * np.pi * 4699 * t) * np.exp(-t / 0.02))
    click = np.zeros(n)
    m = int(0.004 * SR)
    click[:m] = fft_filter(rng.standard_normal(m), lo=3000) * np.linspace(1, 0, m)
    return 0.8 * s * np.clip(t / 0.0015, 0, 1) + 0.5 * click


def riser(length):
    n = int(length * SR)
    t = np.arange(n) / SR
    u = t / length
    noise = fft_filter(rng.standard_normal(n), lo=600, hi=9000)
    f = 220 * 2 ** (u * 2.3)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.5 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR)
    env = u ** 2.2
    return (0.6 * noise / np.max(np.abs(noise)) + 0.35 * tone) * env


def impact():
    n = int(2.4 * SR)
    t = np.arange(n) / SR
    f = 32 + 60 * np.exp(-t / 0.05)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.7)
    crack = fft_filter(rng.standard_normal(n), hi=1400) * np.exp(-t / 0.12)
    crack /= np.max(np.abs(crack)) + 1e-9
    return boom + 0.45 * crack


def reverb(x, seconds=2.6, tau=0.55, wet=0.35, seed=0):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-t / tau)
    ir = fft_filter(ir, lo=180, hi=6500)
    ir[: int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
    ir /= np.sqrt(np.sum(ir ** 2))
    L = len(x) + n
    size = 1 << int(np.ceil(np.log2(L)))
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[: len(x)]
    return y * wet


# ---------------------------------------------------------------- arrangement

D, Bm, G, A = ([50, 57, 61, 64, 66], [47, 54, 57, 61, 62], [43, 50, 57, 59, 66], [45, 52, 59, 61, 64])
PROG = [(INTRO_END, D), (8.1, Bm), (14.6, G), (21.1, A)]
ROOT = {id(D): 38, id(Bm): 35, id(G): 31, id(A): 33}

music = np.zeros((N, 2))
fx = np.zeros((N, 2))

# Intro: shimmering Dmaj9 swell under the logo reveal
intro = np.zeros(N)
for m in D:
    place(intro, 0.0, pad_note(mtof(m + 12), 1.4, a=0.9, r=1.6) * 0.18)
bell_intro = np.zeros(N)
for k, m in enumerate([74, 78, 81, 85, 86, 90]):
    place(bell_intro, 0.25 + k * 0.09, fm_bell(mtof(m), 1.6, index=1.4, decay=0.6) * 0.14)
music += stereo(intro, -0.1) + stereo(bell_intro, 0.25)

# Pads, sub, pulse, arp across the main section
pad = np.zeros(N)
bass = np.zeros(N)
for i, (start, chord) in enumerate(PROG):
    end = PROG[i + 1][0] if i + 1 < len(PROG) else END_CARD
    for m in chord:
        place(pad, start - 0.3, pad_note(mtof(m), end - start + 0.3) * 0.16)
    place(bass, start, sub(mtof(ROOT[id(chord)]), end - start) * 0.5)

pulse = np.zeros(N)
hats = np.zeros(N)
arp = np.zeros(N)
arp_r = np.zeros(N)
beat = INTRO_END
k = 0
pattern = [0, 2, 1, 3, 2, 4, 3, 1]
while beat < END_CARD - 0.2:
    if k % 2 == 0:
        place(pulse, beat, thump(0.55))
    place(hats, beat + BEAT / 2, hat() * 0.05)
    chord = next(c for s, c in reversed(PROG) if s <= beat + 1e-6)
    for h in range(2):
        tt = beat + h * BEAT / 2
        if tt < 3.0 or tt >= END_CARD - 0.3:
            continue
        idx = pattern[(2 * k + h) % len(pattern)]
        note = sorted(chord)[1:][idx % 4] + 12
        b = fm_bell(mtof(note), 0.9, index=1.8, decay=0.28) * 0.12
        place(arp, tt, b)
        place(arp_r, tt + BEAT * 0.75, b * 0.45)  # dotted echo, other side
    k += 1
    beat += BEAT

# gentle "pumping" on pads and bass, ducked on each pulse
duck = np.ones(N)
b0 = INTRO_END
while b0 < END_CARD:
    i = int(b0 * SR)
    n = int(BEAT * 2 * SR)
    seg = 1 - 0.28 * np.exp(-np.arange(min(n, N - i)) / SR / 0.22)
    duck[i:i + len(seg)] *= seg
    b0 += BEAT * 2
pad *= duck
bass *= duck

music += stereo(pad, 0.0) * 1.0 + stereo(bass, 0.0) * 0.38 + stereo(pulse, 0.0) * 0.3 + stereo(hats, 0.35) * 1.6
music += stereo(arp, -0.45) + stereo(arp_r, 0.5)

# End card: resolve to D with a bell chord and long pad
end_pad = np.zeros(N)
for m in D + [69, 73]:
    place(end_pad, END_CARD, pad_note(mtof(m + 12), DUR - END_CARD, a=0.25, r=1.5) * 0.14)
place(end_pad, END_CARD, sub(mtof(38), DUR - END_CARD) * 0.3)
bells = np.zeros(N)
for k2, m in enumerate([74, 78, 81, 85, 88, 90]):
    place(bells, END_CARD + 0.02 + k2 * 0.035, fm_bell(mtof(m), 2.4, index=1.2, decay=0.9) * 0.16)
music += stereo(end_pad, 0.0) + stereo(bells, 0.15)

# ---------------------------------------------------------------- effects
for s in SCENES:
    w = whoosh(0.7) * 0.3
    i = int((s - 0.38) * SR)
    fx[i:i + len(w)] += w[: max(0, min(len(w), N - i))]
for c in CLICKS:
    g = glass_tap() * 0.22
    place(fx[:, 0], c, g * 0.9)
    place(fx[:, 1], c, g)
rz = riser(END_CARD - RISER_START) * 0.16
place(fx[:, 0], RISER_START, rz)
place(fx[:, 1], RISER_START, rz)
imp = impact() * 0.42
place(fx[:, 0], END_CARD, imp)
place(fx[:, 1], END_CARD, imp)
# logo reveal at the very start: soft low hit + airy swell
place(fx[:, 0], 0.05, impact()[: int(1.6 * SR)] * 0.28)
place(fx[:, 1], 0.05, impact()[: int(1.6 * SR)] * 0.28)
sw = fft_filter(rng.standard_normal(int(1.5 * SR)), lo=2000, hi=10000)
sw = sw / np.max(np.abs(sw)) * np.linspace(0, 1, len(sw)) ** 2 * 0.07
place(fx[:, 0], 0.1, sw)
place(fx[:, 1], 0.1, sw[::-1][::-1])

# ---------------------------------------------------------------- mix and master
music[:, 0] = music[:, 0] - 0.45 * fft_filter(music[:, 0], hi=110)
music[:, 1] = music[:, 1] - 0.45 * fft_filter(music[:, 1], hi=110)
mix = music + fx
wet = np.stack([reverb(mix[:, 0], seed=1), reverb(mix[:, 1], seed=2)], axis=1)
mix = mix * 0.85 + wet
mix = fft_filter(mix[:, 0], lo=28), fft_filter(mix[:, 1], lo=28)
mix = np.stack(mix, axis=1)
fade_in = np.clip(T / 0.05, 0, 1)
fade_out = np.clip((DUR - T) / 0.9, 0, 1) ** 1.5
mix *= (fade_in * fade_out)[:, None]
TARGET_RMS_DB = -18.0                            # calm background level
mix *= 10 ** (TARGET_RMS_DB / 20) / (np.sqrt(np.mean(mix ** 2)) + 1e-12)
ceil = 10 ** (-1.0 / 20)                         # soft-limit only what pokes above -3 dB, ceiling -1 dBFS
knee = 10 ** (-3.0 / 20)
a = np.abs(mix)
over = a > knee
mix[over] = np.sign(mix[over]) * (knee + (ceil - knee) * np.tanh((a[over] - knee) / (ceil - knee)))

pcm = (mix * 32767).astype(np.int16)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
rms = np.sqrt(np.mean(mix ** 2))
peak = np.max(np.abs(mix))
print(f"wrote {sys.argv[1]}  peak {20 * np.log10(peak):.1f} dBFS  rms {20 * np.log10(rms):.1f} dBFS")
# per-second loudness, to check the arc (quiet intro, steady bed, lift into the end card)
sec = [20 * np.log10(np.sqrt(np.mean(mix[int(i * SR):int((i + 1) * SR)] ** 2)) + 1e-12) for i in range(int(DUR))]
print("per-second rms dB:", " ".join(f"{v:.0f}" for v in sec))
