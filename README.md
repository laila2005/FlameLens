# FlameLens — Space-Fire Data, Made Clear

**Live Application:** [https://flamelens-steel.vercel.app](https://flamelens-steel.vercel.app)  
**Interactive API Docs (OpenAPI / Swagger):** [https://flamelens-steel.vercel.app/docs](https://flamelens-steel.vercel.app/docs)  
**Challenge:** *Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data* — **NASA Space Apps Challenge 2026** (Team AstroSpark, Cairo)

---

## 1. The Problem & Our Solution

Fire in microgravity behaves nothing like fire on Earth. Without buoyancy-driven rising hot air, flames form spherical diffusion fronts fed entirely by molecular diffusion and cabin ventilation (`airflow_cm_s`), smolder into invisible low-temperature **cool flames (`705–760 K`)** that produce carbon monoxide and formaldehyde, and spread up to **200× faster** along thin fabrics (`2.1–2.6 mm/s` in `Saffire-II` and `0.1 mm` `BASS-II` films) than along thick acrylic slabs (`0.012–0.144 mm/s`). Meanwhile, future **Moon Base** and **Pressurized Rover** habitats plan to use **`30%+ O₂` at `10.2 psi or less`**—increasing oxygen concentration by more than 40% compared to Earth air (`21% O₂` at `14.7 psi`) and making solid materials significantly more flammable.

NASA's **Physical Sciences Informatics (PSI)** repository holds decades of Space Shuttle, ISS, and Cygnus combustion experiments, but the data is scattered across heterogeneous CSVs, summary reports, and CFD archives.

**FlameLens** turns **`2,003` real NASA spaceflight runs across `18` executed PSI investigations** (plus `PSI-68` `FLEX-2`'s planned matrix, `5` PSI ground/CFD modeling investigations, `43` measured microgravity flame-spread rates, and `27` peer-reviewed NASA NTRS publications) into an interactive decision engine:

1. **Evidence Strength Meter (`0–100`) & Evidence Case:** Evaluates any habitat design (`O₂ %`, `pressure psi`, `airflow cm/s`, `fuel state`, `gravity g`) condition-by-condition and as a combined environment. Computes both **Whole-Habitat Evidence Strength** and the **`0 g` Atmosphere-Only Bound**, showing the exact number of backing NASA runs, measured vs. assumed values, and contributing PSI investigations.
2. **Run This Next (Campaign Planner):** Pinpoints the exact experimental gap(s) in a habitat design (for example, `0` partial-gravity runs at `0.16 g` or `0` combined runs at `30% O₂ / 10.2 psi / 8.1 cm/s / solid`) and identifies the nearest existing NASA run (e.g., `PSI-25-0023` in `BASS-II`) with the smallest parameter changes needed for the next experiment.
3. **Safer Tested Options:** Finds real tested NASA runs with at least `10%` lower oxygen partial pressure (`P_O2 = O₂% × psi / 100`) and shows the exact parameter deltas required to reach them.
4. **Deterministic 5-Factor Investigation Ranker:** Ranks all 18 flight investigations by proximity to the user's habitat across oxygen (`0.30`), pressure (`0.20`), airflow (`0.20`), fuel state (`0.15`), and gravity (`0.15`), treating missing table columns as neutral (`0.50`) rather than penalties.
5. **Citation-Verified AI Explanation ("What the Evidence Says"):** Summarizes retrieved runs into structured claims with engineering recommendations. A deterministic **citation verifier (`backend/app/explain.py`)** strips any claim whose `run_id` is not in the retrieved evidence, whose numbers do not match that run, or that invents a flammability threshold or safety verdict.
6. **Six Interactive Visual Lenses + Side-by-Side Investigation Comparison:**
   - **Coverage Map (`O₂ %` vs. `Pressure psi`):** Plots tested atmospheres across all pillars (`Prevention`, `Detection`, `Suppression`, `Other`) with a live `±6% O₂, ±2 psi` tolerance box around the user's habitat.
   - **Cool Flames (`CFI`, `ACME CFI-G`, `FLEX`):** Maps visible vs. cool-flame and radiative/stretch extinction outcomes, plus sourced findings (`85% O₂` inverse flames, `705–760 K` cool flames, and Type-B platinum thermocouple catalytic hot-flame reignition).
   - **Smoke vs. Dust (`SAME-R` Table 1 & `DAFT`):** Log-scale aerosol diameter comparison showing why fresh/aged spacecraft smoke (`0.04–0.32 µm`) separates cleanly from cabin and lunar-simulant dust (`1.57–1.72 µm`).
   - **Flame Spread (`BASS-II` & `Saffire-II`):** Log-scale plot of `43` measured microgravity spread/regression rates (`mm/s`) vs. opposing/concurrent airflow (`0–32 cm/s`).
   - **Airflow Tested (`O₂ %` vs. `Airflow cm/s`):** Visualizes the `684` runs where both oxygen and ventilation flow were recorded.
   - **Early Detection Simulator + Real `BASS-II` Gas Evidence:** Interactive cabin sensor placement simulator paired with real `BASS-II` `CO`/`CO₂` burn traces (`153` runs) and `SAME-R`/`DAFT` particle size distributions.

---

## 2. Scientific Integrity Rules

FlameLens enforces three non-negotiable engineering rules across both backend and UI:
- **Zero invented numbers:** Every run, range, spread rate, particle size, and temperature comes from a named NASA PSI Experimental Table CSV or NASA Technical Memorandum (`NASA/TM`), with provenance recorded per field (`measured`, `text`, `assumed`, or `unknown`).
- **Evidence strength is a transparency aid, not a safety rating:** Having `336` matching runs for an ISS-like cabin (`82.5/100`) means the condition is *well-tested*, not that fire cannot occur; having `0` matching runs for a `30% O₂, 10.2 psi, 0.16 g` lunar rover means *untested in PSI*, never "unsafe."
- **Deterministic decisions, verified AI:** Ranking, evidence cases, strength scores, next-experiment recommendations, and safer alternatives use pure deterministic arithmetic (`backend/app/engine.py`). AI is restricted to natural-language explanation and must pass `explain.verify()`.

---

## 3. Curated NASA Dataset (`data/curated/`)

All curated datasets are downloadable directly from the dashboard or via `/api/export/*`:

| File | Records | Contents & Provenance |
|---|---:|---|
| [`data/curated/runs.csv`](data/curated/runs.csv) | **2,003 runs** | Unified run table across **18 NASA PSI spaceflight investigations** with `o2_basis`, `pressure_basis`, `airflow_basis`, `confidence`, `source_file`, `source_row`, and `doi` |
| [`data/curated/investigation_profiles.json`](data/curated/investigation_profiles.json) | **19 profiles** | Structured profiles of all 18 executed flight investigations + `PSI-68` (`FLEX-2` planned 8-fuel parameter matrix), hardware (`CIR/ACME`, `CIR/MDCA`, `MSG`, `Cygnus`), fuels, variables, sensors, and linked ground models |
| [`data/curated/spread_rates.csv`](data/curated/spread_rates.csv) | **43 points** | Measured microgravity flame spread / regression rates (`mm/s`) vs. airflow (`cm/s`) from `NASA/TM-20210011385` (`BASS-II` Table 5.1 & text) and `PSI-99` (`Saffire-II`) |
| [`data/curated/modeling_studies.json`](data/curated/modeling_studies.json) | **5 studies** | Official NASA PSI ground/CFD predictive modeling investigations (`PSI-60`, `PSI-62`, `PSI-115`, `PSI-117`, `PSI-142`) linked to their parent flight experiments |
| [`data/curated/smoke_dust_sizes.csv`](data/curated/smoke_dust_sizes.csv) | **15 rows** | `SAME-R` Table 1 fresh & 720s-aged smoke geometric mean diameters (`µm`) + `DAFT` (`PSI-47`) ground and in-flight microgravity dust bag diameters (`DST-01..04`) |
| [`data/curated/detect_gas.csv`](data/curated/detect_gas.csv) | **153 runs** | Real `BASS-II` (`PSI-25`) pre-burn and post-burn `CO` (ppm) and `CO₂` (%) cabin sensor readings |
| [`data/curated/coolflame_notes.csv`](data/curated/coolflame_notes.csv) | **6 findings** | Sourced cool-flame bounds (`705–760 K`), `85% O₂` inverse spherical flames (`ACME CFI-G`), and thermocouple catalytic reignition (`CFI` `PSI-39`) |
| [`data/curated/bass2_airflow.csv`](data/curated/bass2_airflow.csv) | **20 points** | MSG flow-duct fan calibration curve (`NASA/TM-20210011385` Table 3.1) |
| [`data/curated/papers.csv`](data/curated/papers.csv) | **27 papers** | Peer-reviewed NASA NTRS publications with direct PDF links per investigation |

### NASA PSI Investigations Included (CC0-1.0, Cited by DOI)

| PSI ID | Investigation | Pillar | Facility | Flight Runs | Official DOI |
|---|---|---|---|---:|---|
| `PSI-10` | **ACME Flame Design** | Other | ISS — CIR (ACME) | 327 | [`10.60555/w4zy-bt45`](https://doi.org/10.60555/w4zy-bt45) |
| `PSI-20` | **ACME BRE** (Burning Rate Emulator) | Prevention | ISS — CIR (ACME) | 43 | [`10.60555/vb93-3y72`](https://doi.org/10.60555/vb93-3y72) |
| `PSI-21` | **ACME CLD Flame** (Coflow Laminar Diffusion) | Other | ISS — CIR (ACME) | 32 | [`10.60555/23e1-9950`](https://doi.org/10.60555/23e1-9950) |
| `PSI-22` | **ACME E-FIELD Flames** (Mimicked partial-g via ion body force) | Suppression | ISS — CIR (ACME) | 20 | [`10.60555/se5a-8c73`](https://doi.org/10.60555/se5a-8c73) |
| `PSI-23` | **ACME s-Flame** (Spherical Diffusion Flames) | Other | ISS — CIR (ACME) | 23 | [`10.60555/k57n-p030`](https://doi.org/10.60555/k57n-p030) |
| `PSI-159` | **ACME CFI-G** (Cool Flames Investigation with Gases, up to 85% O₂) | Suppression | ISS — CIR (ACME) | 333 | [`10.60555/cyt1-kh64`](https://doi.org/10.60555/cyt1-kh64) |
| `PSI-26` | **BASS** (Burning and Suppression of Solids) | Prevention | ISS — MSG | 122 | [`10.60555/58h4-dy80`](https://doi.org/10.60555/58h4-dy80) |
| `PSI-25` | **BASS-II** (Burning and Suppression of Solids - II) | Prevention | ISS — MSG | 129 | [`10.60555/4qc4-de67`](https://doi.org/10.60555/4qc4-de67) |
| `PSI-98` | **Saffire-I** (Spacecraft Fire Safety Experiment-I) | Prevention | Cygnus OA-6 | 2 | [`10.60555/0t15-1z43`](https://doi.org/10.60555/0t15-1z43) |
| `PSI-99` | **Saffire-II** (Spacecraft Fire Experiment-II, 9 samples) | Prevention | Cygnus OA-5 | 9 | [`10.60555/2chp-m469`](https://doi.org/10.60555/2chp-m469) |
| `PSI-100` | **Saffire-III** (Spacecraft Fire Experiment-III) | Prevention | Cygnus OA-7 | 2 | [`10.60555/040q-4h36`](https://doi.org/10.60555/040q-4h36) |
| `PSI-107` | **SPICE** (Smoke Point In Co-flow Experiment) | Prevention | ISS — MSG | 469 | [`10.60555/9kbh-e962`](https://doi.org/10.60555/9kbh-e962) |
| `PSI-106` | **SLICE** (Structure & Liftoff In Combustion Experiment) | Other | ISS — MSG | 12 | [`10.60555/pm12-rg61`](https://doi.org/10.60555/pm12-rg61) |
| `PSI-102` | **SAME** (Smoke and Aerosol Measurement Experiment) | Detection | ISS — MSG | 8 | [`10.60555/gd4k-8h62`](https://doi.org/10.60555/gd4k-8h62) |
| `PSI-101` | **SAME-R** (Smoke Aerosol Measurement Experiment-Reflight) | Detection | ISS — MSG | 109 | [`10.60555/2np7-jv14`](https://doi.org/10.60555/2np7-jv14) |
| `PSI-47` | **DAFT / DAFT-2** (Dust and Aerosol Measurement Feasibility Test) | Detection | ISS | 2 | [`10.60555/ztgj-d202`](https://doi.org/10.60555/ztgj-d202) |
| `PSI-69` | **FLEX** (Flame Extinguishment Experiment) | Suppression | ISS — CIR (MDCA) | 274 | [`10.60555/mbq8-0451`](https://doi.org/10.60555/mbq8-0451) |
| `PSI-39` | **CFI** (Cool Flames Investigation) | Suppression | ISS — CIR (MDCA) | 87 | [`10.60555/m6pj-a914`](https://doi.org/10.60555/m6pj-a914) |
| `PSI-68` | **FLEX-2** *(8-fuel parameter matrix in PSI; per-drop log not archived)* | Suppression | ISS — CIR (MDCA) | *Matrix* | [`10.60555/byp8-h018`](https://doi.org/10.60555/byp8-h018) |

*Ground & CFD Predictive Modeling Studies in PSI:* `PSI-60` ([`10.60555/mzjm-yv57`](https://doi.org/10.60555/mzjm-yv57)), `PSI-62` ([`10.60555/e9xp-ex83`](https://doi.org/10.60555/e9xp-ex83)), `PSI-115` ([`10.60555/q0v5-1v28`](https://doi.org/10.60555/q0v5-1v28)), `PSI-117` ([`10.60555/gz0q-b577`](https://doi.org/10.60555/gz0q-b577)), and `PSI-142` ([`10.60555/80qf-vj95`](https://doi.org/10.60555/80qf-vj95)).  
*Follow-on & Lunar Campaigns Not Yet Archived in PSI:* `SoFIE`, `FLARE`, `LUCI`, and `FM2` are explicitly flagged in the Evidence Strength Meter as not yet archived in PSI.

---

## 4. Architecture & How to Run Locally

FlameLens uses a zero-build static frontend (`frontend/dist/` — vanilla ES2022 JS, custom SVG charts, dark mission-console CSS) served by a Python **FastAPI** backend (`backend/app/`).

```text
backend/
  app/
    main.py        # FastAPI routes (/api/case, /api/strength, /api/rank, /api/next, /api/alternatives, /api/explain, /api/lens/*)
    engine.py      # Deterministic ranker, evidence case, Evidence Strength Meter (0-100), next-test & safer-options solver
    explain.py     # Retrieval pack + deterministic citation verifier + template fallback + optional OpenAI-compatible LLM
    lenses.py      # Data builders for Coverage, Cool Flames, Smoke vs Dust, Flame Spread, and Airflow lenses
    detect.py      # Early-detection evidence endpoint (BASS-II CO/CO2 + SAME-R/DAFT aerosols + cool flames)
    profiles.py    # Investigation detail profiles, side-by-side comparator, and CFD modeling links
    data.py        # Curated CSV/JSON loader and validator
  tests/           # 67 pytest unit & integration tests verifying engine math, verifier rules, and API invariants
frontend/dist/
  index.html       # Single-page mission-console dashboard
  app.js           # State loop, Evidence Strength Meter, Evidence Drawer, comparison & modeling UI
  charts.js        # Custom dependency-free SVG scatter, log-Y flame spread, and log-X aerosol size plots
  detect.js        # Interactive cabin smoke/CO/thermal early-detection simulator
  styles.css       # Responsive dark aerospace theme
data/curated/      # Cleaned, provenance-tagged NASA PSI tables (CC0-1.0)
scripts/           # Reproducible ETL scripts (fetch_psi.py, build_runs.py, build_spread_rates.py, fetch_ntrs_papers.py)
```

### Quick Start (Local)

```bash
# 1. Install dependencies (Python 3.11+)
pip install -r backend/requirements.txt

# 2. Run the 67 automated backend & scientific-integrity tests
python -m pytest backend/tests -q

# 3. Start the server (serves both dashboard UI and API at http://127.0.0.1:8000)
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 5. AI-Use Disclosure

In accordance with NASA Space Apps Challenge rules, we disclose both how AI is used inside the product and how AI tools assisted the team during the 24-hour hackathon:

1. **Inside FlameLens (Product Architecture):**
   - **No AI in engineering decisions:** Habitat verdicts, condition statuses (`Supported` / `Weak` / `No evidence`), the `0–100` Evidence Strength Meter, investigation rankings, `Run this next`, and `Safer tested options` are computed by **100% deterministic arithmetic** in [`backend/app/engine.py`](backend/app/engine.py).
   - **Citation-Verified AI Explanation (`POST /api/explain` & `POST /api/verify`):** The *"What the evidence says"* panel uses retrieval-augmented generation (or a deterministic verified template when no external LLM is configured) constrained by [`backend/app/explain.py`](backend/app/explain.py). Every sentence must cite a retrieved `run_id`; our deterministic verifier automatically deletes any claim that cites a non-existent run, states a number not present in that run, or claims a flammability threshold or safety verdict.
2. **During Development (Build Process):**
   - AI coding assistants (Claude / Gemini in Antigravity) helped the team write ETL scripts to parse NASA PSI Experimental Table CSVs, build the FastAPI routes and SVG visualizations, and draft documentation. Every extracted number and test assertion was verified against the official NASA PSI CSV files and NASA Technical Memoranda (`67/67` automated tests passing).

---

## 6. Team AstroSpark & License

- **Team AstroSpark (NASA Space Apps Cairo 2026):** Laila Mohamed (Tech Lead & Backend), Yousseif B (Frontend Lead), Yasmine C (Charts & Visual Lenses), Judy D (NASA PSI Data Extraction), Dai E (AI & Citation Verifier), Mostafa F (Research, Pitch & QA).
- **Code License:** [MIT License](LICENSE).
- **Data License:** All NASA Physical Sciences Informatics (PSI) and NASA Technical Reports Server (NTRS) datasets are public domain under **CC0-1.0**; please cite the respective investigation DOIs above.
