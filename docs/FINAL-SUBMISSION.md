# NASA Space Apps 2026 — Final Submission Package (`FlameLens`)

> **Ready to Copy & Paste:** Every section below is written to the exact fields of the NASA Space Apps Challenge project submission page, followed by the exact text for your **7-Slide Deck** and **30-Second Video Script**.
> - **Live Public URL (No login required):** `https://flamelens-steel.vercel.app`
> - **Interactive API Documentation:** `https://flamelens-steel.vercel.app/docs`
> - **GitHub Repository:** `https://github.com/laila2005/FlameLens`

---

## Part 1 — Copy-Paste Form Fields for the Space Apps Submission Page

### 1. Project Name
```text
FlameLens — Space-Fire Data, Made Clear
```

### 2. High-Level Project Summary (Short Description / Elevator Pitch — under 50 words)
```text
FlameLens is an interactive, citation-verified decision dashboard built on 2,003 real NASA PSI microgravity combustion runs across 18 spaceflight investigations. Engineers enter a spacecraft, lunar base, or rover atmosphere to see exact evidence strength, untested safety gaps, the single highest-value next experiment, and safer tested atmospheres.
```

### 3. Link to Final Project (Publicly Accessible Demo)
```text
https://flamelens-steel.vercel.app
```

### 4. Link to Project Repository (Public GitHub)
```text
https://github.com/laila2005/FlameLens
```

### 5. Detailed Project Description (Problem, Solution, How It Works & Impact)
```text
PROBLEM
As humanity returns to the Moon and prepares for Mars, fire inside a pressurized habitat remains one of the deadliest mission hazards. To reduce spacesuit pre-breathing time, planned Moon Base and Pressurized Rover cabins are expected to operate at 30%+ oxygen and 10.2 psi or less—over a 40% increase in oxygen concentration compared to Earth air (21% O2 at 14.7 psi), making solid materials far more flammable. Furthermore, in microgravity and reduced gravity, hot gases do not rise: cabin ventilation feeds flames directly, thin fabrics burn up to 200x faster than thick slabs, and extinguished droplets can keep burning invisibly as 705–760 K cool flames producing toxic carbon monoxide.

Decades of NASA spaceflight combustion experiments live in NASA's Physical Sciences Informatics (PSI) database, but the data is spread across heterogeneous CSV tables, technical reports, and CFD archives—making it difficult for habitat engineers and researchers to compare conditions or spot dangerous gaps in test coverage.

OUR SOLUTION: FLAMELENS
FlameLens unifies 2,003 real spaceflight test runs across 18 executed NASA PSI combustion investigations (all 6 ACME investigations, Saffire-I/II/III, BASS, BASS-II, SPICE, SLICE, SAME, SAME-R, DAFT, FLEX, and CFI), plus PSI-68 (FLEX-2 parameter matrix), 5 PSI ground/CFD predictive modeling studies, 43 measured microgravity flame-spread rates, 153 BASS-II cabin gas sensor traces, and 27 NASA NTRS publications into a single interactive mission console:

1. Deterministic Evidence Case & Dual Evidence Strength Meter (0–100):
   Users select a preset (Moon Base, Pressurized Rover, Spacesuit, ISS Cabin, Mars Habitat) or dial in custom O2 %, pressure (psi), airflow (cm/s), fuel state (solid/liquid/gas), and gravity (0g, 0.16g, 0.38g, 1g). FlameLens evaluates each parameter and displays both Whole-Habitat Evidence Strength (0–100) and the 0g Atmosphere-Only Bound—backed by exact NASA test counts, measured-vs-assumed provenance badges, and clickable PSI investigation chips. For example, an ISS cabin (21% O2, 14.7 psi, 0g) is backed by 336 combined NASA runs (score 82.5/100), whereas a Pressurized Lunar Rover (30% O2, 10.2 psi, 8.1 cm/s, 0.16g, solid) reveals 0 partial-gravity runs in PSI and 0 combined 0g runs at that exact atmosphere.

2. "Run This Next" Campaign Planner & "Safer Tested Options":
   Instead of guessing where untested atmospheres are safe, FlameLens explicitly flags "No evidence" gaps, identifies the nearest real NASA run (such as PSI-25-0023 in BASS-II), lists the exact parameter deltas required to test the target habitat, and recommends tested atmospheres with at least 10% lower oxygen partial pressure.

3. Citation-Verified SI Explanation ("What the Evidence Says"):
   FlameLens pairs retrieval over the matched NASA runs with a strict deterministic Citation Verifier (/api/verify). Any AI-generated or template claim that cites a run outside the retrieved evidence, alters a number, or invents a safety threshold is automatically stripped and logged.

4. Six Interactive Visual Lenses & Side-by-Side Investigation Comparator:
   - Coverage Map: O2 % vs. Pressure (psi) across all 2,003 runs.
   - Cool Flames: 705–760 K cool-flame regimes, 85% O2 inverse flames (ACME CFI-G), and platinum thermocouple catalytic reignition (CFI).
   - Smoke vs. Dust: SAME-R fresh/aged smoke (0.04–0.32 um) vs. DAFT microgravity dust (1.57–1.72 um), showing how optical detectors avoid false alarms in dusty lunar cabins and terrestrial mines.
   - Flame Spread: 43 measured microgravity spread rates (mm/s vs. airflow cm/s) from BASS-II and Saffire-II.
   - Airflow Tested: O2 % vs. ventilation velocity across 684 runs.
   - Early Detection Simulator: Interactive cabin sensor placement paired with real BASS-II CO/CO2 traces.
```

### 6. NASA Data, Resources & Tools Used
```text
NASA PHYSICAL SCIENCES INFORMATICS (PSI) SPACEFLIGHT INVESTIGATIONS (CC0-1.0, 2,003 Real Runs):
- PSI-10: ACME Flame Design (327 runs, DOI: 10.60555/w4zy-bt45)
- PSI-20: ACME Burning Rate Emulator / BRE (43 runs, DOI: 10.60555/vb93-3y72)
- PSI-21: ACME Coflow Laminar Diffusion / CLD Flame (32 runs, DOI: 10.60555/23e1-9950)
- PSI-22: ACME E-FIELD Flames (20 runs, electric-field mimicked partial gravity, DOI: 10.60555/se5a-8c73)
- PSI-23: ACME Spherical Diffusion / s-Flame (23 runs, DOI: 10.60555/k57n-p030)
- PSI-159: ACME Cool Flames Investigation with Gases / CFI-G (333 runs up to 85% O2, DOI: 10.60555/cyt1-kh64)
- PSI-26: Burning and Suppression of Solids / BASS (122 runs, DOI: 10.60555/58h4-dy80)
- PSI-25: Burning and Suppression of Solids-II / BASS-II (129 runs, DOI: 10.60555/4qc4-de67) + NASA/TM-20210011385 Table 5.1 spread rates & Table 3.1 MSG fan calibration
- PSI-98: Spacecraft Fire Safety Experiment-I / Saffire-I (2 runs, DOI: 10.60555/0t15-1z43)
- PSI-99: Spacecraft Fire Experiment-II / Saffire-II (9 runs, DOI: 10.60555/2chp-m469)
- PSI-100: Spacecraft Fire Experiment-III / Saffire-III (2 runs, DOI: 10.60555/040q-4h36)
- PSI-107: Smoke Point In Co-flow Experiment / SPICE (469 runs, DOI: 10.60555/9kbh-e962)
- PSI-106: Structure & Liftoff In Combustion Experiment / SLICE (12 runs, DOI: 10.60555/pm12-rg61)
- PSI-102: Smoke and Aerosol Measurement Experiment / SAME (8 runs, DOI: 10.60555/gd4k-8h62)
- PSI-101: Smoke Aerosol Measurement Experiment-Reflight / SAME-R (109 runs + Final Report Table 1 aerosol sizes, DOI: 10.60555/2np7-jv14)
- PSI-47: Dust and Aerosol Measurement Feasibility Test / DAFT & DAFT-2 (2 flight sessions + 4 dust bag size distributions, DOI: 10.60555/ztgj-d202)
- PSI-69: Flame Extinguishment Experiment / FLEX (274 runs, DOI: 10.60555/mbq8-0451)
- PSI-39: Cool Flames Investigation / CFI (87 runs, DOI: 10.60555/m6pj-a914)
- PSI-68: Flame Extinguishment Experiment-2 / FLEX-2 (8-fuel parameter matrix, DOI: 10.60555/byp8-h018)

NASA PSI GROUND & CFD PREDICTIVE MODELING INVESTIGATIONS (CC0-1.0):
- PSI-60 (SPICE soot modeling, DOI: 10.60555/mzjm-yv57)
- PSI-62 (BASS/BASS-II UFGM flame-spread CFD, DOI: 10.60555/e9xp-ex83)
- PSI-115 (SAME smoke wake DNS modeling, DOI: 10.60555/q0v5-1v28)
- PSI-117 (FLEX 3D OpenFOAM cool-flame CFD, DOI: 10.60555/gz0q-b577)
- PSI-142 (FLEX counterflow cool-flame extinction boundaries, DOI: 10.60555/80qf-vj95)

OTHER NASA RESOURCES & TOOLS:
- NASA Technical Reports Server (NTRS API): 27 peer-reviewed microgravity combustion publications linked in data/curated/papers.csv
- NASA Spinoff Database: Mine smoke/dust discrimination (spinoff.nasa.gov/node/9407), firefighter PBI gear (node/9918), composite air tanks (node/9582)
- Tech Stack: Python 3.12, FastAPI, Pydantic, pytest (67 automated tests), Vanilla ES2022 JS, Custom SVG Charts, Vercel Serverless Deployment
```

### 7. AI-Use Disclosure (Copy-Paste for Form / Judges)
```text
1. In-Product AI & Guardrails: All engineering rankings, evidence strength scores (0–100), gap detection, "Run This Next" recommendations, and "Safer Tested Options" are computed by 100% deterministic arithmetic over NASA PSI tables—never by AI. In the "What the evidence says" explanation panel, a deterministic Citation Verifier (backend/app/explain.py) checks every claim against the retrieved NASA run IDs and removes any sentence with an unverified run ID, mismatched number, or invented safety threshold.
2. Development Tools: AI coding assistants (Claude / Gemini in Antigravity) assisted Team AstroSpark during the 24-hour hackathon with ETL script authoring, FastAPI route scaffolding, SVG chart code, and documentation formatting. Every scientific value and test case was validated against the raw NASA PSI CSV tables and Technical Memoranda.
```

---

## Part 2 — Exact 7-Slide Deck (Copy-Paste Slide Text + Screenshot Guide)

> **Rule Reminder:** Maximum **7 slides**, publicly accessible link, zero images/names/voices of anyone under 18. Keep text under ~35 words per slide and let the live screenshots shine.

### Slide 1 — Title & The Space-Fire Imperative
- **Headline:** **FlameLens: Space-Fire Data, Made Clear**
- **Bullets:**
  - In microgravity, flames form spheres fed by cabin air, spread **200× faster** on thin fabrics, and burn invisibly as **705–760 K cool flames**.
  - Planned Moon Bases & Rovers (**30%+ O₂, ≤10.2 psi**) raise oxygen >40% above Earth air.
- **Visual to include:** Screenshot of the top header + Habitat Design panel + Verdict banner on `https://flamelens-steel.vercel.app`.
- **Footer:** Team AstroSpark · NASA Space Apps Cairo 2026 · Live: `https://flamelens-steel.vercel.app`

### Slide 2 — The Problem: A Trove of Data, Hard to Act On
- **Headline:** **Decades of NASA Combustion Data—Scattered Across Files**
- **Bullets:**
  - NASA's PSI archive holds thousands of ISS & Cygnus burns across gases, droplets, and solids.
  - Engineers cannot quickly see **which habitat conditions are proven**, which rely on assumed cabin air, and **where dangerous evidence gaps hide**.
- **Visual to include:** Side-by-side of raw PSI CSV/report tables vs. FlameLens's unified **2,003 runs · 18 NASA PSI investigations · CC0** data chip.

### Slide 3 — Our Solution: From Raw PSI Tables to Defensible Decisions
- **Headline:** **Enter a Habitat Design. Get an Evidence-Backed Engineering Case.**
- **Bullets:**
  - **2,003 real flight runs** across **18 PSI spaceflight investigations** + **5 PSI CFD modeling studies** + **27 NTRS papers**.
  - Instant **Evidence Case**, **Dual Evidence Strength Meter (0–100)**, **Run This Next**, and **Safer Tested Options**.
- **Visual to include:** Full-screen screenshot of the Pressurized Rover preset (`30% O₂, 10.2 psi, 8.1 cm/s, 0.16 g, solid`) showing the Verdict, Evidence Strength Meter, and Closest Investigations.

### Slide 4 — Evidence Strength Meter & Gap Finder ("Run This Next")
- **Headline:** **Honest About What NASA Has Tested—And What It Hasn't**
- **Bullets:**
  - **ISS Cabin (`21% O₂, 14.7 psi, 0g`):** **336 matching NASA runs** (`82.5/100` strength).
  - **Lunar Rover (`30% O₂, 10.2 psi, 0.16g`):** **0 partial-g runs** and **0 combined 0g runs**—FlameLens pinpoints nearest run **`PSI-25-0023` (`BASS-II`)** to design the next test.
- **Visual to include:** Crop of the **Evidence Strength Meter** + **Run This Next** + **Safer Tested Options** panels.

### Slide 5 — Six Physics Lenses: Flame Spread, Cool Flames & Smoke vs. Dust
- **Headline:** **Six Interactive Lenses Reveal Microgravity Fire Physics**
- **Bullets:**
  - **Flame Spread (`43` pts):** Thin fabrics (`2.1–2.6 mm/s`) burn up to 200× faster than thick PMMA slabs (`0.012–0.144 mm/s`).
  - **Cool Flames (`CFI`, `CFI-G`, `FLEX`):** `705–760 K` invisible burn & thermocouple catalytic reignition.
  - **Smoke vs. Dust (`SAME-R`, `DAFT`):** Smoke (`0.04–0.32 µm`) vs. dust (`1.57–1.72 µm`).
- **Visual to include:** 3-panel collage of the **Flame spread**, **Cool flames**, and **Smoke vs dust** charts with the **Evidence Drawer** open on a clicked run.

### Slide 6 — Why Engineers Can Trust It: Deterministic Math + Citation Verifier
- **Headline:** **Zero Hallucinated Thresholds. Every Number Cites a NASA DOI.**
- **Bullets:**
  - Decisions use **100% deterministic math**—never AI guesses.
  - Every field is tagged **`measured`**, **`text`**, or **`assumed`**.
  - Our **Citation Verifier (`/api/verify`)** deletes any AI explanation sentence whose `run_id` or number does not match the retrieved NASA run.
- **Visual to include:** Screenshot of **"What the evidence says"** with green `✓ verified` run badges (`PSI-25-0023`) + Investigation side-by-side comparison (`BASS-II vs Saffire-II`).

### Slide 7 — Impact in Space & Back on Earth, Data Credits & AI Disclosure
- **Headline:** **Safer Lunar Habitats & Real Benefits Back on Earth**
- **Bullets:**
  - **Space & Predictive Modeling:** One-click CSV exports (`runs.csv`, `spread_rates.csv`) + direct links to 5 PSI CFD studies (`PSI-60, 62, 115, 117, 142`).
  - **Earth Spin-offs:** Dust-immune mine smoke detectors (`NASA Spinoff 9407`), firefighter gear (`9918`), lighter air tanks (`9582`), and cleaner engines.
  - **Credits & Disclosure:** NASA PSI (CC0-1.0, cited by DOI) & NTRS; deterministic engine + citation-verified AI explanations; AI coding assistants disclosed.
- **Visual to include:** Screenshot of the **"Use the data & predictive modeling"** and **"Back on Earth"** panels at the bottom of the dashboard.

---

## Part 3 — 30-Second Video Storyboard & Script (Alternative to Slides)

> **Recording tip:** Open `https://flamelens-steel.vercel.app` at 100% zoom (1920×1080), record screen only (no faces/voices of anyone under 18), and paste the on-screen captions below.

| Time | Screen Action on `https://flamelens-steel.vercel.app` | On-Screen Caption / Voiceover (75 words total) |
|---|---|---|
| **0:00–0:05** | Show the **Pressurized rover** preset (`30% O₂, 10.2 psi, 0.16g`) and the amber Verdict banner + **Evidence Strength Meter**. | *"In space, flames don't rise—and planned 30%-oxygen lunar rovers make materials far more flammable."* |
| **0:05–0:11** | Hover over the **Evidence Strength Meter** (`2,003 real NASA runs · 18 PSI investigations`) and click **ISS cabin** (`336 runs, 82.5/100`), then back to **Pressurized rover** (`0 runs`). | *"FlameLens unifies 2,003 real NASA PSI combustion runs to show where your habitat design is proven—and where zero evidence exists."* |
| **0:11–0:18** | Highlight **What the evidence says** (`✓ verified`), **Run this next** (`PSI-25-0023`), and **Safer tested options**; click `PSI-25-0023` to pop open the **Evidence Drawer** with its DOI. | *"Every claim is citation-verified. FlameLens pinpoints the exact next experiment to run and safer tested atmospheres—linked directly to NASA DOIs."* |
| **0:18–0:25** | Click through the **Flame spread**, **Cool flames**, **Smoke vs dust**, and **Early detection** tabs. | *"Six interactive lenses map microgravity flame spread, invisible cool flames, and smoke-versus-dust detection."* |
| **0:25–0:30** | Scroll to **Investigations comparison** and **Use the data & predictive modeling** CSV downloads. | *"FlameLens: Space-fire evidence you can trust."* |

---

## Part 4 — Final Pre-Submission Checklist (Do This Before Clicking Submit)

- [x] **Live URL Public (No Login):** `https://flamelens-steel.vercel.app` returns HTTP 200 in an incognito/private browser window.
- [x] **API & Data Exports Live:** `/api/health`, `/api/export/runs.csv`, `/api/export/spread_rates.csv`, and `/docs` open cleanly without authentication.
- [x] **Automated Tests Passing:** `67/67` backend & scientific-integrity tests passing (`python -m pytest backend/tests -q`).
- [x] **Open-Source License & README:** `LICENSE` (MIT + CC0-1.0 data notice) and judge-facing `README.md` committed on `main`.
- [ ] **Demo Link Public:** Upload either the **7-Slide Deck** or **30-Second Video** to Google Drive / YouTube (unlisted or public) and test the link in an incognito window.
- [ ] **Team Leader Submission:** Team leader submits on both the local Cairo form and the official NASA Space Apps page, and saves confirmation screenshots.
