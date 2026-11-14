"""Prepare Laila's clips for the v3 video (render3.py).

- Cleans each voice piece (high-pass, light denoise, loudness -18 LUFS) and writes 48 kHz mono WAVs.
- Crops the selfie clips to a square around the face (for the circle frame) and stores the frames as .npy.
- Transcribes each piece with faster-whisper and aligns the script words to the spoken words, so every
  subtitle word gets a start and end time (words the model mishears keep the script spelling).

Usage: prep3.py <work_dir> <intro_clip> <story_clip> <closing_voice (wav/mp3/mp4)>
"""
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
import numpy as np
import soundfile as sf

FF = imageio_ffmpeg.get_ffmpeg_exe()
CROP = "crop=440:440:5:200"          # square around the face in the 478x850 selfie clips
SQ = 440
PIECES = {  # name: (source arg index, start s, end s or None, subtitle lines exactly as spoken)
    "intro": (2, 4.60, 9.35, [  # starts after a false start ("Hi, I'm...") at 3.7 s
                               "Hi, I'm Laila, from Team AstroSpark.",
                               "We chose Flame in Freefall because of a story we could not forget."]),
    "story": (3, 0.30, 7.85, ["Apollo 1:", "three astronauts, trapped by fire,",
                               "in a test no one thought it was dangerous.",
                               "That's why we have built FlameLens", "to make their story alive."]),
    "vo": (4, None, None, ["You can easily enter your cabin air,", "and FlameLens compares it with NASA PSI experiments.",
                           "Every result cited,", "showing what's been tested and what hasn't,",
                           "because behind every cabin on the Moon or Mars,", "there is a crew",
                           "and a family waiting for them to come home."]),
}
# gentle: no denoise, no speed change; cut rumble, a little less mud, a little more presence, light compression
AF = ("highpass=f=80,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.5:g=3,"
      "acompressor=threshold=-24dB:ratio=2.5:attack=8:release=120:makeup=2,loudnorm=I=-16:TP=-1.5:LRA=9,afade=t=in:d=0.03")

work = Path(sys.argv[1]); work.mkdir(parents=True, exist_ok=True)
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())


def run(args):
    subprocess.run([FF, "-v", "error", "-y", *args], check=True)


def trim_args(a, b):
    out = []
    if a is not None:
        out += ["-ss", f"{a}"]
    if b is not None:
        out += ["-t", f"{b - (a or 0)}"]
    return out


from faster_whisper import WhisperModel  # noqa: E402
model = WhisperModel("small.en", device="cpu", compute_type="int8")
meta = {}
for name, (idx, a, b, lines) in PIECES.items():
    src = sys.argv[idx]
    wav = work / f"{name}.wav"
    run([*trim_args(a, b), "-i", src, "-vn", "-af", AF, "-ar", "48000", "-ac", "1", str(wav)])
    x, sr = sf.read(str(wav), dtype="float32")
    if name == "vo":  # trim leading/trailing silence of a separate recording
        loud = np.where(np.abs(x) > 0.02)[0]
        x = x[max(0, loud[0] - int(0.05 * sr)): loud[-1] + int(0.15 * sr)]
        sf.write(str(wav), x, sr)
    if name != "vo":
        raw = subprocess.run([FF, "-v", "error", *trim_args(a, b), "-i", src, "-vf",
                              f"{CROP},eq=contrast=1.05:saturation=1.08", "-r", "30", "-f", "rawvideo",
                              "-pix_fmt", "rgb24", "-"], check=True, capture_output=True).stdout
        np.save(work / f"{name}_frames.npy", np.frombuffer(raw, np.uint8).reshape(-1, SQ, SQ, 3))
    # word timings
    a16 = subprocess.run([FF, "-v", "error", "-i", str(wav), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         check=True, capture_output=True).stdout
    segs, _ = model.transcribe(np.frombuffer(a16, np.float32), word_timestamps=True, beam_size=5, language="en")
    heard = [(w.start, w.end, w.word.strip()) for s in segs for w in s.words]
    script = [(li, w) for li, line in enumerate(lines) for w in line.split()]
    times = [None] * len(script)
    sm = difflib.SequenceMatcher(a=[norm(w) for _, w in script], b=[norm(w[2]) for w in heard], autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        n, m = i2 - i1, j2 - j1
        if op == "equal" or (op == "replace" and n == m):
            for k in range(n):
                times[i1 + k] = heard[j1 + k][:2]
        elif op == "replace":  # n script words for m heard words: spread over the heard word boundaries
            bounds = [h[0] for h in heard[j1:j2]] + [heard[j2 - 1][1]]
            at = lambda p: np.interp(p, np.arange(m + 1), bounds)
            for k in range(n):
                times[i1 + k] = (float(at(k * m / n)), float(at((k + 1) * m / n)))
    # fill words the model missed by interpolating between neighbours
    for i in range(len(times)):
        if times[i] is None:
            prev = next((times[j][1] for j in range(i - 1, -1, -1) if times[j]), 0.0)
            nxt = next((times[j][0] for j in range(i + 1, len(times)) if times[j]), len(x) / sr)
            times[i] = (prev, max(prev + 0.05, nxt))
    if name == "vo":  # keep from the first word to the last script word ("come home."); drop anything said after it
        s0, end = max(0.0, heard[0][0] - 0.15), times[-1][1] + 0.35
        x = x[int(s0 * sr): int(end * sr)]
        sf.write(str(wav), x, sr)
        times = [(t0 - s0, t1 - s0) for t0, t1 in times]
        heard = [(h0 - s0, h1 - s0, w) for h0, h1, w in heard if h0 < end]
    words = [{"line": li, "w": w, "t0": round(t[0], 3), "t1": round(t[1], 3)} for (li, w), t in zip(script, times)]
    meta[name] = {"dur": round(len(x) / sr, 3), "frames": name != "vo", "heard": " ".join(h[2] for h in heard),
                  "heard_words": [[round(h[0], 2), round(h[1], 2), h[2]] for h in heard],
                  "words": words, "lines": lines}
    print(f"{name}: {len(x) / sr:.2f} s  heard: {meta[name]['heard']}")
(work / "pieces.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
print("wrote", work / "pieces.json")
