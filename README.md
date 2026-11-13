# FlameLens: space-fire data, made clear

**Live app:** https://flamelens-steel.vercel.app (public, no login)
**API docs:** https://flamelens-steel.vercel.app/docs
**Demo video (30 s):** [`media/flamelens-demo-30s.mp4`](media/flamelens-demo-30s.mp4)
**Challenge:** *Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data*, NASA Space Apps Challenge 2026
**Team:** AstroSpark, NASA Space Apps Cairo

FlameLens answers one question for a habitat engineer: **"Is my cabin design backed by NASA fire experiments, how strong is that evidence, and what should be tested next?"**

It is built on **2,003 real spaceflight runs from 18 NASA PSI combustion investigations**. Every run links back to its NASA source table and DOI.

---

## 1. Why it matters

- In microgravity hot gas does not rise. A candle flame becomes a sphere fed by diffusion, and cabin airflow feeds a fire directly (challenge text).
- The planned Moon base and pressurized rovers are expected to use **30 % oxygen or more at 10.2 psi or less**, which is more than 40 % more oxygen than Earth air and makes materials much more flammable (challenge text).
- NASA's Physical Sciences Informatics (PSI) repository holds the experiments that could answer "has this been tested?", but they sit in separate tables, reports and archives with different columns. They are hard to find, compare and interpret.

## 2. What FlameLens does

You enter a design: oxygen %, pressure, airflow, material state and gravity. Presets cover the Moon base, a pressurized rover and a spacesuit (values from the challenge text), plus an ISS cabin (14.7 psia, 21 % O₂, from NASA-STD-3001 technical brief OCHMO-TB-003) and a Mars habitat at NASA's recommended exploration atmosphere (8.2 psia, 34 % O₂, NTRS 20220005716). Every preset cites its source; see `docs/research/claims.md`.

| Feature | What you get |
|---|---|
| **Evidence case** | Each condition marked Supported (2+ matching runs), Weak (1) or No evidence (0), with the matching run IDs. Two summary lines: runs matching the whole design, and runs matching the atmosphere alone (ignoring gravity). |
| **Evidence strength (0–100)** | A transparency score per condition: 0.35 closeness + 0.30 reliability + 0.20 run count + 0.15 source quality. **Not a safety rating.** |
| **Run this next** | The evidence gaps, the nearest existing NASA run, and the changes needed to turn it into the missing test. |
| **Lower-oxygen tested options** | Real runs with at least 10 % less oxygen partial pressure than the design, and what would change. |
| **Closest NASA evidence** | When no run matches the whole design, the runs that match everything except the fewest conditions, with exactly what differs. Nothing is interpolated. |
| **Test campaign planner** | "NASA can fly N more experiments": a greedy plan of tests that give the most designs a full match. It plans coverage only and never predicts results. |
| **Mission atmosphere journey** | One Artemis-style crew mission as a timeline (ISS cabin → spacesuit → pressurized rover → Moon base). Each stage shows its evidence strength from the same engine; the mission is only as well backed as its weakest stage, which is flagged with the test to run next (today: the spacesuit, 100 % O₂ at 4.3 psi). |
| **Ranked investigations** | The 18 flight investigations ranked by closeness to the design (weights: oxygen 0.35, pressure 0.20, airflow 0.20, material 0.15, gravity 0.10; a missing value scores a neutral 0.5). |
| **What the evidence says (AI)** | A short explanation where every sentence cites a run. A citation verifier removes any claim that cites a run outside the evidence, states a number not in that run, or gives a safety threshold. |
| **Seven lenses** | Coverage map, cool flames, smoke vs dust, **smoke points** (55 SPICE flames on the ISS at the moment they began to smoke, from the SPICE thesis Appendix 6.4; 45 linked to their runs), flame spread, airflow tested, and an early-detection simulator. |
| **Investigations explorer** | A profile of each investigation (objective, fuels, hardware, conditions, what varied, what was measured) and a side-by-side comparison. |
| **Design review brief** | A printable evidence brief for the current design, built from the same API. Open it directly with `/?brief=1`. |
| **Data downloads** | The curated run table, spread rates, papers and investigation profiles, for flammability modelling. |
| **Back on Earth** | NASA spin-offs linked to this research. |

### What it shows on the real data

- **ISS cabin** (21 % oxygen, 14.7 psi, 12.9 cm/s, microgravity): **336 runs** match the whole design. Evidence strength 82.5 of 100.
- **Pressurized rover** (30 % oxygen, 10.2 psi, 8.1 cm/s, solid material, lunar gravity): **0 runs** match the whole design, and 0 match the atmosphere even ignoring gravity. The nearest run is `PSI-25-0023` (BASS-II).
  - 308 solid-material runs share its airflow and material, but at 14.5–22.2 % oxygen and 14.7 psi.
  - 33 FLEX runs share its oxygen and pressure, but burned liquid droplets.
  - 153 runs share its oxygen partial pressure (shown as related, not equivalent).
- **Gravity:** every run in PSI is microgravity. For lunar or Mars gravity FlameLens says so: PSI has no partial-gravity combustion data yet (LUCI and FM2 are planned, challenge text), and microgravity results are one bound.
- **Campaign planner, 3 tests:** one lunar-gravity test at 30 % oxygen and 10.2 psi serves both the Moon base and the rover; the other two serve the spacesuit and the Mars habitat. Today only the ISS cabin has a full match.

### The lenses

| Lens | Data |
|---|---|
| Coverage map | Oxygen against pressure for the 1,772 runs that have both, with a "close to your design" box (±6 oxygen points, ±2 psi). |
| Cool flames | Cool-flame, hot-flame and no-ignition outcomes by oxygen and pressure (CFI, ACME CFI-G, FLEX). 56 runs record a cool flame. Sourced notes include inverse flames at up to 85 % oxygen (ACME CFI-G). |
| Smoke vs dust | Smoke particles 0.04–0.29 µm (SAME-R final report, Table 1, five materials, fresh and aged) against Arizona Road Dust test dust 1.57–1.72 µm (DAFT). This is why a detector that measures particle size can tell smoke from dust. |
| Flame spread | 43 measured microgravity spread or regression rates, 0.012–2.6 mm/s, at 1.5–29 cm/s airflow (41 from BASS-II, 2 from Saffire-II). Thin fuels spread far faster than thick slabs: 2.1–2.6 mm/s for thin fabric and film against 0.012–0.144 mm/s for 1–5 mm acrylic slabs. |
| Airflow tested | Oxygen against airflow for the 681 runs that recorded both. |
| Early detection | A cabin sensor simulator (an illustration, see section 3) anchored to real numbers: before-and-after CO and CO₂ readings from 129 BASS-II tests (median CO rise 44 ppm, maximum 575 ppm), and the SAME-R and DAFT particle sizes. |

## 3. Scientific integrity rules

1. **No invented data.** Every run, range, spread rate and particle size comes from a named NASA PSI table or report. Each condition carries a basis: `measured`, `text`, `assumed` or `unknown`.
2. **Assumptions are visible.** Where a source table gives no oxygen or pressure, FlameLens uses ISS cabin air (21 %, 14.7 psi), marks it `assumed` and lowers the confidence. Oxygen is measured in 1,191 runs and assumed in 600; pressure is measured in 1,020 and assumed in 864.
3. **"No evidence" is a valid answer.** FlameLens shows gaps and never fills them.
4. **Evidence strength is not a safety rating.** Many matching runs means "well tested", not "safe". Zero matching runs means "untested in PSI", not "unsafe".
5. **Decisions use no AI.** Ranking, the evidence case, strength, next experiment, alternatives, closest evidence, the campaign planner and the mission journey are plain arithmetic in `backend/app/engine.py`.
6. **The early-detection simulator is an illustration.** Its spread model and alarm thresholds are simplified and labelled so on screen. Only the CO levels and particle sizes come from NASA data.

## 4. The data (`data/curated/`)

| File | Records | Contents |
|---|---:|---|
| `runs.csv` | 2,003 | One row per run from 18 flight investigations: material, oxygen, pressure, airflow, gravity, outcome, the basis of each value, source table, DOI, confidence |
| `investigations.csv` | 26 | Every PSI record returned for "combustion", with DOI and license |
| `investigation_profiles.json` | 19 | Profiles of the 18 flight investigations plus FLEX-2 (PSI lists only its planned test matrix) |
| `spread_rates.csv` | 43 | Measured microgravity spread and regression rates (BASS-II summary report and the Saffire-II table) |
| `smoke_dust_sizes.csv` | 14 | 10 smoke sizes (SAME-R) and 4 dust sizes (DAFT) |
| `detect_gas.csv` | 129 | CO and CO₂ before and after each BASS-II test |
| `coolflame_notes.csv` | 6 | Sourced cool-flame findings with page references |
| `bass2_airflow.csv` | 20 | BASS-II fan calibration points |
| `modeling_studies.json` | 5 | PSI ground and CFD modelling studies, linked to the flight investigations they use |
| `papers.csv` | 27 | NASA NTRS publications (2018–2024) with links |
| `explanations.json` | 5 | Cached AI explanations for the five presets (see section 7) |

The raw PSI downloads are not in the repo. Rebuild them with `scripts/fetch_psi.py`, `scripts/fetch_psi_docs.py` and `scripts/build_runs.py`.

### NASA PSI flight investigations used (CC0-1.0, cite by DOI)

| PSI ID | Investigation | Pillar | Runs | DOI |
|---|---|---|---:|---|
| PSI-26 | BASS, Burning and Suppression of Solids | Prevention | 122 | [10.60555/58h4-dy80](https://doi.org/10.60555/58h4-dy80) |
| PSI-25 | BASS-II | Prevention | 129 | [10.60555/4qc4-de67](https://doi.org/10.60555/4qc4-de67) |
| PSI-98 | Saffire-I | Prevention | 2 | [10.60555/0t15-1z43](https://doi.org/10.60555/0t15-1z43) |
| PSI-99 | Saffire-II | Prevention | 9 | [10.60555/2chp-m469](https://doi.org/10.60555/2chp-m469) |
| PSI-100 | Saffire-III | Prevention | 2 | [10.60555/040q-4h36](https://doi.org/10.60555/040q-4h36) |
| PSI-107 | SPICE, Smoke Point In Co-flow Experiment | Prevention | 469 | [10.60555/9kbh-e962](https://doi.org/10.60555/9kbh-e962) |
| PSI-20 | ACME BRE, Burning Rate Emulator | Prevention | 43 | [10.60555/vb93-3y72](https://doi.org/10.60555/vb93-3y72) |
| PSI-102 | SAME, Smoke and Aerosol Measurement Experiment | Detection | 8 | [10.60555/gd4k-8h62](https://doi.org/10.60555/gd4k-8h62) |
| PSI-101 | SAME-R | Detection | 109 | [10.60555/2np7-jv14](https://doi.org/10.60555/2np7-jv14) |
| PSI-47 | DAFT and DAFT-2 | Detection | 2 | [10.60555/ztgj-d202](https://doi.org/10.60555/ztgj-d202) |
| PSI-69 | FLEX, Flame Extinguishment Experiment | Suppression | 274 | [10.60555/mbq8-0451](https://doi.org/10.60555/mbq8-0451) |
| PSI-39 | CFI, Cool Flames Investigation | Suppression | 87 | [10.60555/m6pj-a914](https://doi.org/10.60555/m6pj-a914) |
| PSI-159 | ACME CFI-G, Cool Flames Investigation with Gases | Suppression | 333 | [10.60555/cyt1-kh64](https://doi.org/10.60555/cyt1-kh64) |
| PSI-22 | ACME E-FIELD Flames | Suppression | 20 | [10.60555/se5a-8c73](https://doi.org/10.60555/se5a-8c73) |
| PSI-10 | ACME Flame Design | Other | 327 | [10.60555/w4zy-bt45](https://doi.org/10.60555/w4zy-bt45) |
| PSI-21 | ACME CLD Flame | Other | 32 | [10.60555/23e1-9950](https://doi.org/10.60555/23e1-9950) |
| PSI-23 | ACME s-Flame | Other | 23 | [10.60555/k57n-p030](https://doi.org/10.60555/k57n-p030) |
| PSI-106 | SLICE | Other | 12 | [10.60555/pm12-rg61](https://doi.org/10.60555/pm12-rg61) |
| PSI-68 | FLEX-2 (planned test matrix only, no per-run table in PSI) | Suppression | – | [10.60555/byp8-h018](https://doi.org/10.60555/byp8-h018) |

PSI ground and CFD modelling studies linked from the dashboard: PSI-60 ([10.60555/mzjm-yv57](https://doi.org/10.60555/mzjm-yv57)), PSI-62 ([10.60555/e9xp-ex83](https://doi.org/10.60555/e9xp-ex83)), PSI-115 ([10.60555/q0v5-1v28](https://doi.org/10.60555/q0v5-1v28)), PSI-117 ([10.60555/gz0q-b577](https://doi.org/10.60555/gz0q-b577)), PSI-142 ([10.60555/80qf-vj95](https://doi.org/10.60555/80qf-vj95)).

Not in PSI yet, and shown as gaps: partial-gravity experiments such as LUCI and FM2 (challenge text).

## 5. Architecture

A static frontend with no build step, served by a Python FastAPI backend. Custom SVG charts, no chart library. The decision logic is deterministic.

```text
backend/app/
  main.py       FastAPI routes under /api
  engine.py     ranker, evidence case, strength, next experiment, alternatives,
                closest evidence, campaign planner (no AI)
  explain.py    retrieval pack, citation verifier, cached AI text, template fallback
  lenses.py     data for the coverage, cool-flame, smoke-vs-dust, spread and airflow lenses
  detect.py     real gas and particle evidence behind the early-detection simulator
  profiles.py   investigation profiles, comparison, modelling links
  data.py       loads the curated tables
backend/tests/  73 automated tests
frontend/dist/  index.html, styles.css, app.js, charts.js, detect.js, brief.js,
                campaign.js, closest.js, journey.js, logo.png, favicon.png, og-image.png, apple-touch-icon.png
data/curated/   cleaned NASA tables with provenance
scripts/        fetch and build scripts, and validate_live.py (checks the live site)
api/index.py    Vercel entry point for the FastAPI app
```

Main API routes: `/api/habitats`, `/api/case`, `/api/strength`, `/api/next`, `/api/alternatives`, `/api/closest`, `/api/campaign`, `/api/journey`, `/api/rank`, `/api/explain`, `/api/verify`, `/api/evidence/{run_id}`, `/api/investigations`, `/api/compare`, `/api/modeling`, `/api/papers`, `/api/lens/*`, `/api/detect/evidence`, `/api/export/*`. The full list with request shapes is at `/docs`.

## 6. Run it locally

Needs Python 3.11 or newer.

```bash
pip install -r backend/requirements.txt
```

```bash
python -m uvicorn backend.app.main:app --port 8000
```

Open http://localhost:8000 for the dashboard and http://localhost:8000/docs for the API.

Run the tests (about 3 minutes):

```bash
python -m pytest backend/tests -q
```

Check the live site against the data:

```bash
python scripts/validate_live.py .
```

Deploy to Vercel from the repo root (project `flamelens`):

```bash
vercel deploy --prod --yes
```

## 7. Use of AI (disclosure)

**Inside the product**

- **No AI in the decisions.** Verdicts, statuses, strength scores, rankings, next experiment, alternatives and the campaign plan are deterministic arithmetic over the NASA tables.
- **"What the evidence says" panel.** For the five presets, the text was generated ahead of time by an open model (`qwen2.5:7b-instruct`) from the retrieved runs only: 5 claims per preset, 25 in total. The citation verifier in `backend/app/explain.py` re-checks every claim on every request and removed none of the 25. For a custom design the live site has no model, so the panel shows a plain summary filled from the runs and says "AI is off".
- **The verifier removes** any claim whose run ID is not in the retrieved evidence, whose numbers are not in that run, or that states a flammability threshold or a safety verdict. `/api/verify` exposes the same check.

**While building**

- AI coding assistants (Claude in Claude Code, and Claude and Gemini in Antigravity) helped the team write the data scripts, backend, frontend and documentation during the hackathon.
- The FlameLens logo illustration (a burning planet with a magnifying glass, `media/flamelens-illustration.jpg`) was generated with Google Gemini and chosen by the team; the site icon and social image use a crop of it.
- The 30-second demo video is composed by our scripts in `scripts/demo_video/` from screen captures of the live site. Its soundtrack is synthesized by code: no samples, no AI-generated music, no voices or faces.
- Numbers shown in the app come from the NASA files, not from an AI. They are checked by the 73 automated tests and by `scripts/validate_live.py`, which compares the live site with the curated data.

## 8. Credits and data sources

- **NASA Physical Sciences Informatics (PSI)**, combustion science: https://psi.nasa.gov . Experimental tables, final reports and investigation descriptions for the investigations listed above. PSI records state the license as CC0-1.0. Please cite each investigation by its DOI.
- **NASA Technical Reports Server (NTRS)**: https://ntrs.nasa.gov . 27 publications linked from the dashboard through the public NTRS API. We link to them and store titles and abstracts; each document keeps its own terms.
- **NASA Spinoff**: [fire detector that tells combustion particles from dust](https://spinoff.nasa.gov/node/9407), [firefighter breathing system](https://spinoff.nasa.gov/node/9582), [firefighter clothing](https://spinoff.nasa.gov/node/9918).
- **NASA Space Apps challenge text and resources** for the habitat atmospheres and the fire-safety background: https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/
- **Tools:** Python, FastAPI, Pydantic, pytest, plain JavaScript and SVG, Vercel. Fonts: Sora, IBM Plex Sans and IBM Plex Mono (Google Fonts).

NASA does not endorse this project. Any error in how the data is read or shown is ours.

## 9. Team and license

- **Team AstroSpark:** Laila Mohamed (tech lead, backend), Yousseif (frontend), Yasmine (charts and lenses), Judy (data), Dai (AI), Mostafa (research, pitch, QA).
- **Code:** [MIT License](LICENSE).
- **Data:** NASA PSI data is CC0-1.0. See [LICENSE](LICENSE) for the data notice.

Planning documents from before the event are in [`docs/`](docs). The submission texts are in [`docs/FINAL-SUBMISSION.md`](docs/FINAL-SUBMISSION.md).
