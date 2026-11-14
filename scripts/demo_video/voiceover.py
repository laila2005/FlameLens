"""Narration for the FlameLens demo, made locally with Kokoro-82M (open-source TTS, Apache-2.0), voice af_heart.

Each line is rendered separately so the video timeline can follow the voice. Writes <out_dir>/vo_XX.wav (24 kHz mono)
and <out_dir>/vo.json with every line's text and duration.

Model files (not in the repo): kokoro-v1.0.onnx and voices-v1.0.bin from
https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0

Usage: voiceover.py <model_dir> <out_dir> [voice] [speed]
"""
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

# Every number said here is shown on the live dashboard (2,003 runs; 30 % oxygen at 10.2 psi is the challenge text).
LINES = [  # story: Nour, a fictional habitat engineer, uses FlameLens on a Moon rover cabin
    "In space, fire plays by different rules.",
    "Nour is designing a Moon rover cabin: thirty percent oxygen, ten point two psi.",
    "She checks it against two thousand real NASA flight runs.",
    "The honest answer: no PSI run burned a fabric in that air. Only gas flames and droplets.",
    "So FlameLens shows the closest proof, down to lunar-gravity tests.",
    "Every AI sentence she reads cites a real run.",
    "Then she plans NASA's next tests, and asks the reports herself.",
    "FlameLens. Space-fire data, made clear.",
]

model_dir, out = Path(sys.argv[1]), Path(sys.argv[2])
voice = sys.argv[3] if len(sys.argv) > 3 else "af_heart"
speed = float(sys.argv[4]) if len(sys.argv) > 4 else 1.2
out.mkdir(parents=True, exist_ok=True)
k = Kokoro(str(model_dir / "kokoro-v1.0.onnx"), str(model_dir / "voices-v1.0.bin"))
meta = {"voice": voice, "speed": speed, "model": "Kokoro-82M v1.0 (Apache-2.0)", "lines": []}
for i, text in enumerate(LINES):
    samples, sr = k.create(text, voice=voice, speed=speed, lang="en-us")
    samples = np.asarray(samples, dtype=np.float32)
    # trim leading/trailing near-silence so lines can be placed tightly
    loud = np.where(np.abs(samples) > 0.01)[0]
    if loud.size:
        samples = samples[max(0, loud[0] - int(0.02 * sr)): loud[-1] + int(0.08 * sr)]
    path = out / f"vo_{i:02d}.wav"
    sf.write(str(path), samples, sr)
    meta["lines"].append({"i": i, "text": text, "file": path.name, "sr": sr, "dur": round(len(samples) / sr, 3)})
    print(f"{i}: {len(samples) / sr:5.2f} s  {text}")
meta["total"] = round(sum(x["dur"] for x in meta["lines"]), 2)
(out / "vo.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
print("total speech", meta["total"], "s")
