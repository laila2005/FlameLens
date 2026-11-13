"""Generate a 30 s ambient 'mission console' bed: low drone, soft air hiss, UI clicks, transition whooshes.
All synthesized here (no samples, no copyright). Usage: audio.py out.wav clicks_csv whooshes_csv"""
import sys, wave
import numpy as np

SR = 48000
DUR = 30.0
out = sys.argv[1]
clicks = [float(x) for x in sys.argv[2].split(",") if x]
whooshes = [float(x) for x in sys.argv[3].split(",") if x]
t = np.arange(int(SR * DUR)) / SR
rng = np.random.default_rng(7)

# Drone: A1/E2/A2 with slow beating and a gentle swell
drone = np.zeros_like(t)
for f, a in [(55.0, 0.5), (82.41, 0.32), (110.0, 0.22), (164.8, 0.08), (220.0, 0.05)]:
    drone += a * np.sin(2 * np.pi * f * t + 0.6 * np.sin(2 * np.pi * 0.11 * t)) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.07 * t + f))
# Soft high shimmer
drone += 0.04 * np.sin(2 * np.pi * 880 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.25 * t)) ** 4

# Air hiss: low-passed noise
noise = rng.standard_normal(t.size)
k = 60
hiss = np.convolve(noise, np.ones(k) / k, mode="same") * 0.6

bed = 0.18 * drone + 0.10 * hiss
# Swell into the final title card
bed *= 1 + 0.6 * np.clip((t - 27.5) / 1.5, 0, 1) * np.clip((29.6 - t) / 0.4, 0, 1)

fx = np.zeros_like(t)
for c in clicks:  # short tick
    i = int(c * SR); n = int(0.03 * SR)
    if i + n < t.size:
        e = np.exp(-np.arange(n) / (0.004 * SR))
        fx[i:i + n] += 0.35 * e * np.sin(2 * np.pi * 2400 * np.arange(n) / SR)
for w in whooshes:  # filtered noise sweep
    i = int((w - 0.25) * SR); n = int(0.5 * SR)
    if i < 0 or i + n >= t.size:
        continue
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    nn = rng.standard_normal(n)
    nn = np.convolve(nn, np.ones(18) / 18, mode="same")
    fx[i:i + n] += 0.5 * env * nn

mix = bed + fx
fade = np.minimum(1, np.minimum(t / 0.8, (DUR - t) / 0.9))
mix *= np.clip(fade, 0, 1)
mix = mix / np.max(np.abs(mix)) * 0.35  # about -9 dBFS peak, quiet background
st = np.stack([mix, np.roll(mix, 240) * 0.97], axis=1)
pcm = (st * 32767).astype(np.int16)
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("wrote", out)
