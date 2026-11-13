# Demo video pipeline (30 s, 1920×1080, 60 fps)

Premium cut: the FlameLens illustration as intro and end card, the live dashboard in a floating browser window on a dark branded stage, camera moves, cursor and click ripples, numbered captions under the window, and a composed soundtrack. No faces and no voices.

```bash
python -m venv .venv-video
.venv-video\Scripts\python -m pip install playwright imageio-ffmpeg pillow numpy
.venv-video\Scripts\python scripts\demo_video\capture.py out\shots [http://localhost:8000]   # Edge drives the site; default is the live URL
.venv-video\Scripts\python scripts\demo_video\soundtrack.py out\soundtrack.wav
.venv-video\Scripts\python scripts\demo_videoender.py out\shots outlamelens-demo-30s.mp4 out\soundtrack.wav medialamelens-illustration.jpg frontend\dist\logo.png   # add --preview for still frames
```

- `capture.py`: 13 scene states at device scale 2, plus the screen position of every button and panel the cursor and highlights use.
- `soundtrack.py`: synthesized D-major cinematic bed (pads, sub bass, FM-bell arpeggio, soft pulse) and designed effects (logo shimmer, whooshes, glass-tap clicks, riser, impact). Mastered to about -18 dBFS RMS, peak -1 dBFS. No samples, no AI music.
- `render.py`: the timeline. Scene times, click times and the end-card time must match `soundtrack.py`. Captions may only use numbers shown on the live dashboard.
- The logo illustration (`media/flamelens-illustration.jpg`) was generated with Google Gemini (disclosed in the README).
