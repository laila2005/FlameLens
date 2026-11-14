# Demo video pipeline (30 s, 1920×1080, 60 fps)

## v2: narrated cut (the submitted video, `media/flamelens-demo-30s.mp4`)

Kinetic-type hook ("In space, fire plays by different rules.") over the FlameLens illustration with rising embers, then the live dashboard in a floating browser window (camera moves, cursor, click ripples, highlights, numbered captions, light-leak transitions) and an end card. A synthetic adult female narration (Kokoro-82M, open-source, Apache-2.0, voice `af_heart`) sets the timeline; the synthesized music ducks about 10 dB under the voice.

```bash
python -m venv .venv-video
.venv-video/Scripts/python -m pip install playwright imageio-ffmpeg pillow numpy kokoro-onnx soundfile
# Kokoro model files (about 350 MB, not in the repo): kokoro-v1.0.onnx and voices-v1.0.bin from
# https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0 , saved in out/tts
.venv-video/Scripts/python scripts/demo_video/voiceover.py out/tts out/vo
.venv-video/Scripts/python scripts/demo_video/capture2.py out/shots
.venv-video/Scripts/python scripts/demo_video/render2.py timing out/timing.json
.venv-video/Scripts/python scripts/demo_video/soundtrack.py out/music.wav out/timing.json
.venv-video/Scripts/python scripts/demo_video/render2.py out/shots out/vo out/music.wav media/flamelens-illustration.jpg frontend/dist/logo.png out/flamelens-demo-30s.mp4
```

- `voiceover.py`: the 7 narration lines (every number said is shown on the live dashboard); writes one WAV per line and `vo.json` with durations.
- `capture2.py`: 10 scenes from the live site with Edge (default URL is the live site; pass another URL to use a local server).
- `render2.py`: the timeline (`VO_AT`, `SEG`, `CAPTIONS`). If a narration line gets longer, move these so the total stays 30 s. Add `--preview` to write still frames instead of the video.
- `soundtrack.py out.wav timing.json`: the same synthesized music as v1, with scene changes and clicks taken from the timing file.

## v1: silent cut (kept for reference)

Branded dark stage, the live dashboard in a floating browser window, camera moves, cursor and click ripples, numbered captions, and a composed soundtrack. No voices.

```bash
.venv-video/Scripts/python scripts/demo_video/capture.py out/shots
.venv-video/Scripts/python scripts/demo_video/soundtrack.py out/soundtrack.wav
.venv-video/Scripts/python scripts/demo_video/render.py out/shots out/flamelens-demo-30s.mp4 out/soundtrack.wav media/flamelens-illustration.jpg frontend/dist/logo.png
```

- `soundtrack.py`: synthesized D-major cinematic bed (pads, sub bass, FM-bell arpeggio, soft pulse) and designed effects (logo shimmer, whooshes, glass-tap clicks, riser, impact). Mastered to about -18 dBFS RMS, peak -1 dBFS. No samples, no AI music.
- The logo illustration (`media/flamelens-illustration.jpg`) was generated with Google Gemini (disclosed in the README).
