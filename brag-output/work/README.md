# /brag source assets — reuse this before re-capturing anything

This folder holds everything the demo video (`../brag.mp4`) was built from:
real screenshots of the running app, the real Power BI feed data, and the
scripts that composite and render them. **If you want to tweak the video —
change text, timing, colors, add a scene — edit `comp.html` and re-render.
You almost never need to re-run the app or Playwright.**

## What's here (committed, ~16MB)

- `shots/` — real Playwright screenshots of the running Django app (seeded
  demo data, 2× DPR): dashboard, ticket list, ticket detail, user list,
  login, pending/mine/create pages, and `shots/type/000.png`–`031.png`
  (32 frames of the "Raise New Ticket" form being filled in live).
- `feed.json` — the real payload from `/api/v1/powerbi/tickets/` at the
  time of capture (32 tickets).
- `pbi_data.py` / `pbi_data.json` — recomputes the Power BI measures
  (SLA compliance, breaches, per-category/per-agent rollups, etc.) from
  `feed.json` in the same logic as the semantic model's DAX. Re-run with
  `python3 pbi_data.py` if you edit the aggregation logic.
- `comp.html` — the actual video "recipe": a pure-function-of-time HTML/JS
  composition that lays out every scene (cold open, ticket, SLA, dashboard,
  the 4 Power BI pages, architecture, capabilities, insight, end card),
  reading `shots/*` and `pbi_data.json`. Scene timings are listed in
  `../brag-plan.md`.
  **This is the file to edit for almost any change** (copy, colors, timing,
  camera moves, which Power BI page shows what).
- `render.js` — headless-Chromium renderer (30.6s @ 30fps). `node render.js stills "1.2,5.4"`
  dumps preview JPEGs at given timestamps (fast, for checking a change);
  `node render.js video` renders the whole cut to `video_noaudio.mp4` (frame-by-
  frame PNG capture piped into ffmpeg).
- `net.js` — routes the CDN URLs the app's templates reference (Chart.js,
  Bootstrap, jQuery, Tabler icons, Google Fonts) to local files during
  capture/render, since this sandbox's egress proxy blocks those CDNs.
- `music.py` — synthesizes the soundtrack + SFX from scratch (numpy, no
  external samples) to `music.wav` in a few seconds.
- `capture.js` / `capture2.js` — the Playwright scripts that produced
  `shots/`. Only re-run these if you need a **different screen or a new
  interaction** that isn't already captured (see below).

## Rebuilding the video from what's already here (no app, no Playwright)

```bash
cd brag-output/work
mkdir -p cdn && cd cdn && npm init -y >/dev/null && \
  npm i chart.js@4.4.1 bootstrap@4.3.1 jquery@3.5.1 popper.js@1.14.7 @tabler/icons-webfont && cd ..
ln -sf "$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')" /usr/local/bin/ffmpeg
(cd ../.. && python3 -m http.server 8123 --bind 127.0.0.1 &)  # serve the REPO ROOT (comp.html loads static/css/main.css)
python3 music.py                                        # -> music.wav (~3s)
NODE_PATH=$(npm root -g) node render.js video            # -> video_noaudio.mp4 (~6 min for 918 frames)
ffmpeg -y -i video_noaudio.mp4 -i music.wav \
  -filter_complex "[1:a]loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart -shortest ../brag.mp4
ffmpeg -y -i ../brag.mp4 -frames:v 1 -q:v 2 ../brag.jpg   # poster = frame 0 (designed as a settled frame)
```

(`net.js` needs `chromium` from Playwright and pulls Google Fonts through
the sandbox proxy on first run; both already worked in this environment.)

## When you DO need to re-capture (new screen, new data, new flow)

Only needed if the change requires a screen/state that isn't in `shots/`
yet (e.g. a different ticket, a new page, a Manager-role view). Then:

1. Run the app locally with seeded demo data (see repo root README for
   `manage.py seed_data` and login credentials).
2. Adjust `capture.js` / `capture2.js` (they're short, ~40 lines each) to
   hit the new URL/state and add the screenshot(s) to `shots/`.
3. Re-run `pbi_data.py` if the underlying ticket data changed.
4. Edit `comp.html` to reference the new shot, then re-render as above.

This keeps re-capture as the exception, not the default, for future edits.
