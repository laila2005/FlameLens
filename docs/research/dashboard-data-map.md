# Data map: what the real PSI data gives each dashboard question

Built on 13 Nov from the real PSI Experimental Tables, a few small PSI documents and three NASA reports. Everything is public (CC0). **Cite the PSI DOI of each investigation** (listed in `data/curated/investigations.csv`).

## Bottom line

| Dashboard feature | Can the real data answer it? | Data used |
|---|---|---|
| Evidence case (oxygen, pressure, airflow, fuel, gravity) | **Yes** for oxygen, pressure and fuel. **Partly** for airflow. **Gravity: all runs are microgravity**, so lunar and Mars gravity will always show "No evidence" | `data/curated/runs.csv`, 2,003 runs across 18 spaceflight PSIs (+ `PSI-68` FLEX-2 parameter matrix) |
| Run this next, Safer options, Coverage map | **Yes** | same table |
| Evidence strength, evidence trail | **Yes**: every row carries its source table, DOI, `value_source`, and a basis for each condition | same table |
| Lens 3, cool flames | **Yes**: CFI (`PSI-39`), ACME CFI-G (`PSI-159`), and FLEX (`PSI-69`) outcomes + sourced temperature/reignition findings | `runs.csv` + `data/curated/coolflame_notes.csv` |
| Lens 2, smoke vs dust particle size | **Yes**: 10 smoke measurements (5 materials, fresh and aged) + 4 dust values (1 ground analysis + 3 DAFT flight dust bags: 1.72, 1.57, 1.65 µm) | `data/curated/smoke_dust_sizes.csv` (SAME-R Table 1, DAFT report & `Logged Data Summary`) |
| Lens 1, flame spread vs airflow | **Yes**: 43 measured 0g spread/regression points (39 BASS-II Table 5.1 PMMA slab steps + 2 BASS-II text benchmarks + 2 Saffire-II SIBAL concurrent points) | `data/curated/spread_rates.csv` (`NASA/TM-20210011385` Table 5.1 & `SAFFIRE-2` CSV) |
| AI explanation with citations & literature | **Yes**: 27 peer-reviewed NTRS papers with PDF links + citation verifier | `data/curated/papers.csv`, `/api/explain`, `/api/verify` |

## What was built (reproducible)

| File | What it is |
|---|---|
| `scripts/fetch_psi.py` | Searches PSI and downloads every Experimental Table CSV into `data/raw/` (git-ignored). Writes `data/curated/investigations.csv` (id, title, DOI, license) |
| `scripts/fetch_psi_docs.py` | Downloads PSI documents (test matrices, fan calibration, readmes, final reports) into `data/raw/docs/` |
| `scripts/build_runs.py` | Merges all 18 executed spaceflight PSI tables into `data/curated/runs.csv` (2,003 runs) and records where each value came from |
| `scripts/build_spread_rates.py` | Extracts 43 measured 0g flame spread / regression points into `data/curated/spread_rates.csv` |
| `scripts/build_bass2_airflow.py` | Extracts 20 MSG flow-duct fan calibration points into `data/curated/bass2_airflow.csv` |
| `scripts/fetch_ntrs_papers.py` | Queries NASA NTRS API for 27 peer-reviewed combustion papers in `data/curated/papers.csv` |
| `data/curated/runs.csv` | **2,003 runs from 18 spaceflight investigations**, one schema |
| `data/curated/spread_rates.csv` | **43 measured 0g flame spread / regression points** (BASS-II + Saffire-II) |
| `data/curated/smoke_dust_sizes.csv` | **14 smoke & dust particle size records** (SAME-R + DAFT ground & flight bags) |
| `data/curated/coolflame_notes.csv` | **6 sourced cool-flame findings** (ACME CFI-G, CFI, PSI-142) |
| `data/curated/modeling_studies.json` | **5 PSI Ground/CFD modeling studies** (`PSI-60, 62, 115, 117, 142`) linked to flight datasets |
| `data/curated/investigations.csv` | 26 PSI investigations with DOIs and license |

Run order: `python scripts/fetch_psi.py`, then `python scripts/fetch_psi_docs.py`, then `python scripts/build_runs.py`.

## The unified schema (`runs.csv`)

`run_id, psi_id, investigation, pillar, fuel_or_material, fuel_state, o2_pct, o2_basis, pressure_psi, pressure_basis, airflow_cm_s, airflow_basis, gravity_g, outcome, metric_name, metric_value, value_source, source_table, doi, confidence, notes`

Each condition has a **basis** column, which is the honesty mechanism:

| Basis | Meaning | Count (oxygen / pressure / airflow) |
|---|---|---|
| measured | a column in the PSI table | 1,191 / 1,020 / 549 |
| text | parsed from a free-text cell (display reading, report string) | 0 / 0 / 239 |
| assumed | not in the table, taken from the platform (ISS cabin air, about 14.7 psi, 21 % O2). **Lower confidence** | 586 / 858 / 0 |
| unknown | left empty, never guessed | the rest |

Confidence: `high` = oxygen and pressure both measured (1,009 runs), `medium` = one assumed or unknown (911), `low` = both missing (2).

## How many runs per question (examples, current tolerances)

| Habitat | Runs near this oxygen (±6 pts) | Runs near this pressure (±2 psi) | Runs in the same fuel state | Runs matching oxygen, pressure and fuel together |
|---|---|---|---|---|
| ISS cabin, 21 %, 14.7 psi | 1,231 | 1,433 | all | 1,020 |
| Enriched 40 %, 14.7 psi | 297 | 1,433 | all | 158 |
| Low oxygen 17 %, 14.7 psi, solid | 1,215 | 1,433 | 389 solid | 257 |
| Mars-like 30 %, 8.2 psi | 126 | 97 | all | **22** |
| **Lunar rover 34 %, 10.2 psi, solid** | 328 | 107 | 389 solid | **0** |

That last line is the signature result: **no solid-fuel experiment covers a 34 % oxygen, 10.2 psi atmosphere**, and no experiment covers lunar gravity. The dashboard will show that honestly, which is exactly the point of the Evidence case and Run this next.

Ranges in the data (after cleaning): oxygen 12 to 85 %, pressure 6.3 to 73.5 psi, airflow 0 to 85 cm/s. Pressure and oxygen spread widely because the cool-flame and ACME experiments used high pressures and enriched oxygen. Measured oxygen bands: below 18 % (172 runs), 18 to 21 (205), 21 to 25 (277), 25 to 30 (39), 30 to 40 (317), above 40 (181). The 25 to 30 % band is thin.

Runs by pillar: Prevention 784, Suppression 694, Detection 117, Other 327. Fuel state: gas 1,172, solid 389, liquid 361. **Solid materials, the ones that matter most for habitats, are the thinnest group.**

## What each investigation contributes

| Investigation | Runs | What we got | Missing |
|---|---|---|---|
| FLEX (PSI-69) | 274 | fuel (methanol, heptane), oxygen, pressure (8 runs above 30 psi), diluents, droplet size, burn time, outcome (extinction, disruption, completion) | airflow |
| ACME CFI-G (PSI-159) | 333 | fuel, oxygen, pressure, cool flame yes/no, hot ignition, burn time | airflow. 84 runs are above 30 psi (up to 73 psi) |
| CFI (PSI-39) | 87 | fuel (dodecane), oxygen, helium, pressure, cool-flame outcome from the summary sheet | airflow |
| ACME Flame Design (PSI-10) | 327 | fuel (ethylene), oxygen, pressure | outcome (soot study) |
| BASS-II (PSI-25) | 129 | material, calibrated oxygen (13.6 to 22.2 %), flow readings in cm/s | outcome and spread rate (in plots and the summary report); pressure assumed |
| BASS (PSI-26) | 122 | material, flow readings | oxygen (nitrogen dilution was used but no value in the matrix) |
| Saffire I, II, III (PSI-98, 99, 100) | 21 | material, airflow (20 to 30 cm/s), oxygen 21.5 to 22.1 %, burn time, direction; Saffire-II has some spread results | few runs; pressure assumed |
| SPICE (PSI-107) | 469 | fuel, air rate in cm/s | oxygen and pressure assumed cabin air |
| SAME (PSI-102), SAME-R (PSI-101) | 117 | material (Kapton, Teflon, lampwick, silicone, Pyrell), airflow | particle sizes are in the reports, now in `smoke_dust_sizes.csv` |
| ACME BRE (PSI-20) | 43 | oxygen levels 21, 25, 26.5, 34, 40 % per test day (ethylene) | pressure (varied but not listed), per-run outcome (day totals only) |

Not used as run data: DAFT (2 session rows), SLICE, ACME CLD, E-FIELD and s-Flame (fuel mix and flame counts only), FLEX-2 (a planned matrix of oxygen 0.17 to 0.25, pressure 0.5 to 2 atm, flow 0.1 to 5 cm/s, not run results), the ground and modeling investigations.

## Real facts learned from the documents

- **BASS-II oxygen:** the calibrated initial oxygen across its 129 tests runs from 13.6 to 22.2 %, at or below cabin air. BASS-II studied flames **below** 21 %, never enriched oxygen.
- **Airflow conversion:** the BASS-II readme says "Air display" is the flow speed in the duct in cm/s (slow response, about 1 minute). A fan calibration sheet maps fan display to cm/s (for example fan display 122 is about 29 cm/s with no restrictor). Flow restrictors 0 (highest flow) to 2 (lowest flow) narrow the range.
- **Smoke particle size (SAME-R):** fresh Kapton smoke is very small (geometric mean 0.042 µm) and Teflon about 0.08 µm. Silicone and lampwick are larger (0.09 to 0.13 µm fresh, up to 0.27 µm aged). Aging 720 s roughly doubles the size for most materials. The report says small Kapton and Teflon particles are hard for light-scattering detectors to catch, while dust is large, which is why a smoke detector needs size discrimination. This is the story for Lens 2.
- **Dust (DAFT):** Arizona Road Dust (fine) averaged 1.65 µm (range 1.56 to 1.7) in the sample analysis. That is far larger than the smoke particles.
- **Cool flames (CFI):** the summary sheet lists extinction diameters for hot and cool flames per test, which is where the cool-flame outcome comes from.

## Gaps and what to do

The step-by-step list of files to fetch and numbers to extract is in [data-to-check.md](data-to-check.md).


| Gap | Impact | Proposed fix | Owner |
|---|---|---|---|
| **No spread-rate table** (Lens 1) | The original Lens 1 (spread rate vs airflow per oxygen level) cannot be drawn from tables | **Change Lens 1** to "Where flames were tested": oxygen vs airflow scatter from the 681 runs that have both, coloured by pillar and outcome. If time allows, plot-read a few spread rates from the BASS-II summary report (49 MB PDF) or Saffire-II and label them `plot-read` | Yasmin and Judy |
| Assumed ISS cabin pressure and air (858 pressure, 586 oxygen) | Lower confidence badges on BASS, BASS-II, Saffire, SPICE, SAME | Verify the cabin pressure for each platform in the readmes and reports and replace `assumed` with a sourced value | F and Judy |
| Outcomes missing for 1,078 of 1,922 runs ("tested") | Safer options can say "tested here", but not "it burned here" | Use the 684 runs that have a real outcome (FLEX 274, ACME CFI-G 325, CFI 72, Saffire 13); add more from the Saffire spreadsheets and BASS-II summary if time | Judy |
| BASS-II airflow is the first display reading only; multi-step flow ramps are collapsed | Airflow for those runs is approximate | Keep the confidence note; do not show spread-vs-flow curves | Yasmin |
| Few runs between 25 and 30 % oxygen | Coverage map will show a thin band | A true finding, show it | Everyone |
| Saffire IV to VI (reduced pressure, higher oxygen) and SoFIE are not in the PSI search | Solid-material evidence at lunar-like atmospheres is missing | Mention in "what next"; use the Saffire VI NTRS paper only as a citation, not run data | F |
| Gravity: microgravity only | Lunar and Mars gravity always "No evidence" | This is correct and honest. FM2 (lunar gravity) is a planned experiment | none |
| Crew-safe oxygen limits | Needed for the "breathable zone" idea | Official source still to be found | F |

## What changes in the product

1. **Gravity condition:** keep it, but expect "No evidence" for anything except microgravity. Offer a "microgravity only" note.
2. **Lens 1** becomes the "tested conditions" scatter, which also feeds the coverage map.
3. **Lens 3** (cool flames) is now the best-supported lens: 56 cool-flame runs plus hot and no-ignition outcomes.
4. **Evidence strength** uses `confidence`, `o2_basis`, `pressure_basis`, `value_source`, and run count, all present now.
5. **Presets** should come from real conditions: the Lunar rover (34 % oxygen, 10.2 psi) is a good "no evidence" demo, ISS cabin a good "well covered" demo.
6. The earlier placeholder CSV and the schema in [06](../06-data-guide.md) are replaced by `data/curated/runs.csv`.

## Early detection evidence (13 Nov)

The early-detection tab simulates a sensor network. **The simulation is an illustration, not a validated fire model.** It is anchored to these real NASA numbers:

| File or route | What |
|---|---|
| `scripts/build_detect_evidence.py` | Reads the BASS-II Experimental Table (PSI-25) and writes `data/curated/detect_gas.csv` |
| `data/curated/detect_gas.csv` | 129 BASS-II tests: O2, CO2 (%) and CO (ppm) before and after each burn, the rise, DOI, notes. Run ids match `runs.csv` |
| `GET /api/detect/evidence` | Summary of the gas rises, smoke and dust sizes, cool-flame run count, sources |

Key numbers (BASS-II, measured in the glovebox before and after each test):

- **CO rise:** median 44 ppm, 90th percentile 412 ppm, maximum 575 ppm (118 tests with both readings). **62 % of tests** raised CO by more than 25 ppm.
- **CO2 rise:** median 0.24 %, 90th percentile 1.01 %, maximum 2.78 % (121 tests).
- Biggest CO rises: PSI-25-0066 (3/8" clear PMMA rod, 176 to 751 ppm), PSI-25-0062 (1/2" PMMA rod, 389 to 950 ppm), PSI-25-0030 (5 mm PMMA, 2 to 561 ppm).
- 4 tests have a final CO marked over range (">500", "OR", "over") and are left empty, so the true maximum rise is higher than 575 ppm. One test (PSI-25-0024) shows a small CO drop (-23 ppm). 12 tests have empty cells, listed in `notes`.
- **Smoke vs dust:** smoke geometric mean 0.042 to 0.293 µm (SAME-R), dust 1.65 µm average (DAFT).
- **Cool flames:** 56 runs (CFI, ACME CFI-G) with cool flames, which make CO and formaldehyde with little light or heat, so a heat-only or infrared-only detector can miss them.

What this supports: a gas (CO) channel sees most of these fires, and particle size separates smoke from dust. The simulated sensor positions, heat spread and detection times in the tab are illustrative.

## Investigation profiles (13 Nov)

The challenge asks the dashboard to summarize and compare investigations (objectives, fuels, conditions, what varied, measurements). `scripts/build_investigation_profiles.py` builds `data/curated/investigation_profiles.json` (19 profiles, about 117 KB) from the PSI records (objectives, approach, hypothesis, research impacts and Earth benefits, hardware, platform, dates, DOI, license, publication count) plus `runs.csv` (run count, top fuels, condition ranges measured-only and including assumed values, outcome counts, which conditions varied and which stayed constant). Hardware groups follow the challenge text: MSG flow duct (BASS, BASS-II, SPICE, SLICE), CIR / MDCA droplets (FLEX, FLEX-2, CFI), CIR / ACME gas flames (BRE, CFI-G, Flame Design, CLD, E-FIELD, s-Flame), Cygnus spacecraft (Saffire), MSG / SAME hardware (SAME, SAME-R, DAFT).

- `measurements_mentioned` lists only keywords that literally appear in the PSI objective, approach or hypothesis text (BASS, CFI and CFI-G mention none of the listed words, so their list is empty: check the reports for sensors).
- Six investigations have no rows in `runs.csv` (DAFT, FLEX-2, E-FIELD, CLD, s-Flame, SLICE): their profile has PSI text but `n_runs` 0 and no ranges.
- Raw PSI records are cached in `data/raw/psi_json/` (git-ignored). The CFI record (about 4 MB) needed several attempts on the venue network.

Routes: `GET /api/investigations`, `GET /api/investigations/{psi_id}`, `GET /api/compare?a=&b=` (same, different, measurements shared or only in one), `GET /api/export/runs.csv` (curated run table for modeling), `GET /api/export/investigations.json`.


## BASS conditions from its SRD (13 Nov, evening)

Source: `PSI-26_Science Documents_SRD_BASS.pdf`. It states (a) pressure is the **ambient cabin pressure** (same as SPICE), and (b) the cabin oxygen was measured on each test day and **testing was restricted to oxygen at or above 21 %**. The 122 BASS runs keep oxygen **empty** (no per-test value exists), with the note recording the SRD requirement; the dashboard does not turn a lower bound into a measurement. Download tip: for files whose `redirect=false` link comes back empty, use `...&redirect=true` and follow the redirect.
