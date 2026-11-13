# Demo video pipeline (30 s, 1920×1080, 60 fps)

Re-record the demo from the live site in a few minutes after any dashboard change. No faces, no voices: screen captures, captions and a synthesized background track (made here, no samples, no copyright).

```bash
python -m venv .venv-video
.venv-video\Scripts\python -m pip install playwright imageio-ffmpeg pillow numpy
.venv-video\Scripts\python scripts\demo_video\capture.py out\shots          # drives the live site in Microsoft Edge, 2x screenshots + element positions
.venv-video\Scripts\python scripts\demo_video\audio.py out\audio.wav "4.0,15.2,18.9,23.65,24.95" "4.2,8.4,13.2,17.8,22.4,26.2,28.4"
.venv-video\Scripts\python scripts\demo_video\render.py out\shots out\flamelens-demo-30s.mp4 out\audio.wav   # add --preview for still frames first
```

- `capture.py` opens https://flamelens-steel.vercel.app at 1920×1080 (device scale 2) and captures 13 scene states: rover verdict, ISS cabin 83/100, closest NASA evidence, verified claims and the evidence drawer, the campaign planner (1 and 3 experiments), three lenses, the design review brief.
- `render.py` holds the timeline: camera moves, cursor path and clicks, caption text and timing, title card. Captions must only use numbers shown on the live dashboard.
- `audio.py` makes the quiet background bed with UI clicks and transition swishes (times in seconds).
