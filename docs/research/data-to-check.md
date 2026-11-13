# Data still to check (for Yasmine)

**العربية باختصار:** هذه قائمة بالملفات التي لم نستطع تنزيلها أو لم نستخرج منها الأرقام بعد. ابدئي بالأولوية 1 لأنها تسد الثغرات الحقيقية في اللوحة (خصوصًا سرعة انتشار اللهب للعدسة 1). لكل ملف: الرابط، ما الذي نبحث عنه، وأين نحفظ الأرقام. لا تنزّلي ملفات الفيديو والصور الضخمة.

Everything we already have is in `data/curated/` and described in [dashboard-data-map.md](dashboard-data-map.md). This page lists what is **missing**, where to find it, and exactly what to pull out. Tick the box when done and tell Laila so the data can be loaded.

## How to work

1. Open the investigation page (link in each row). Scroll to **"Data files and documents"** and download only the named file. PDFs and spreadsheets only. **Never the videos or image folders** (hundreds of GB).
2. Copy the numbers into the CSV named in the row, one row per value, with the source (file name + page or figure + table number). If you read a value off a plot, write `plot-read` in `value_source`.
3. Put the downloaded file in `data/raw/docs/` (git-ignored). Commit only the CSV.
4. Never guess. If a value is unclear, leave it empty and write why in `notes`.

CSV columns for any new numbers (same idea as the rest of the data):

```
psi_id, run_or_test, material, o2_pct, pressure_psi, airflow_cm_s, quantity, value, unit, value_source, source_ref, doi, confidence, notes
```

`value_source` = `table`, `text` or `plot-read`. `confidence` = `high` (table), `medium` (text), `low` (plot-read).

## Priority 1: fills a real gap in the dashboard

| ☐ | What we need | Where | File | Size | What to extract | Save to |
|---|---|---|---|---|---|---|
| ☐ | **Flame spread rate vs airflow and oxygen** (Lens 1 is missing this) | [PSI-25 BASS-II](https://psi.nasa.gov/physci/repo/data/investigations/PSI-25) | `PSI-25_Reports_BASS-II Summary Report.pdf` | 49 MB (too big for our script, download by hand) | Tables or figures of spread rate (mm/s) with flow speed (cm/s) and oxygen (%) per material. Note opposed vs concurrent flow | `data/curated/spread_rates.csv` |
| ☐ | Spread rate and burn length for the Saffire fabric fires | [PSI-98 Saffire-I](https://psi.nasa.gov/physci/repo/data/investigations/PSI-98), [PSI-100 Saffire-III](https://psi.nasa.gov/physci/repo/data/investigations/PSI-100) | `PSI-98_Science Documents_SAFFIRE-1_MergeResult-jpeg_Update_Final_v2.xlsx`, `PSI-100_Science Documents_SAFFIRE-III_MergeResult-raw_Final.xlsx` | 8 to 12 MB each | Flame-front position over time, so spread rate = distance / time. Check the readme we already have (`data/raw/docs/PSI-98_Science Documents_SAFFIRE-I and SAFFIRE-III Readme.docx`) for column meaning first | `data/curated/spread_rates.csv` |
| ☐ | **BASS conditions**: oxygen per test (BASS used nitrogen dilution but the matrix has no oxygen value) | [PSI-26 BASS](https://psi.nasa.gov/physci/repo/data/investigations/PSI-26) | `PSI-26_Reports_BASS_FinalReport.pdf` (**our download failed: 404**) and `PSI-26_Science Documents_SRD_BASS.pdf` (0.9 MB) | small | Oxygen % per test or per test series; outcome (burned, extinguished) | add to `data/curated/spread_rates.csv` or tell Laila to update `runs.csv` |
| ☐ | Outcome for the 1,078 runs marked "tested" (did it burn, go out, or not ignite?) | BASS-II summary report (above), [PSI-107 SPICE](https://psi.nasa.gov/physci/repo/data/investigations/PSI-107) `PSI-107_Reports_SPICE_FinalReport.pdf` (**already in** `data/raw/docs/`) | see left | small | For each test: outcome word. Smoke point for SPICE | a new CSV `data/curated/outcomes.csv` (`run_id, outcome, source_ref`) |

## Priority 2: raises confidence of values we already show

| ☐ | What we need | Where | File | What to extract | Save to |
|---|---|---|---|---|---|
| ☐ | **Real cabin pressure** for BASS, BASS-II, Saffire, SPICE, SAME (today we assume ISS cabin air, 14.7 psi, 21 % O₂; 858 runs) | readmes and reports of each investigation | the Readme / SRD / Final Report | The pressure and oxygen during the tests, with page number | send to Laila; she replaces `assumed` with the sourced value |
| ☐ | Airflow in cm/s for BASS-II runs where we only have fan codes | [PSI-25](https://psi.nasa.gov/physci/repo/data/investigations/PSI-25) | `PSI-25_Reference Data_Fan calibration data.xlsx` (**already in** `data/raw/docs/`) | Use the table "fan display -> U cm/s" per restrictor to convert the `Fan display` column | `data/curated/bass2_airflow.csv` (`run_id, fan_display, restrictor, airflow_cm_s, source_ref`) |
| ☐ | Smoke particle size per run vs airflow (SAME-R shows size grows at low airflow) | [PSI-101 SAME-R](https://psi.nasa.gov/physci/repo/data/investigations/PSI-101) | `PSI-101_Reports_SAME-R_Final Report.pdf` (**already in** `data/raw/docs/`), figures 6 to 8 | Particle diameter vs air velocity for Teflon, Kapton, lampwick (plot-read) | `data/curated/smoke_vs_airflow.csv` |
| ☐ | Dust size distribution, not only the 1.65 µm average | [PSI-47 DAFT](https://psi.nasa.gov/physci/repo/data/investigations/PSI-47) | `PSI-47_Reports_DAFT_FinalReport.doc` (8.8 MB), `PSI-47_Analyzed Data_DAFT Retrieved Data Summary.xls` (1 MB) | Particle counts per size bin, or median and spread | `data/curated/smoke_dust_sizes.csv` (add rows) |
| ☐ | Cool-flame temperatures and extinction details | [PSI-39 CFI](https://psi.nasa.gov/physci/repo/data/investigations/PSI-39) `PSI-39_Reports_CFI Science Final Report.pdf` (**already in** `data/raw/docs/`); [PSI-159 ACME CFI-G](https://psi.nasa.gov/physci/repo/data/investigations/PSI-159) `PSI-159_Reports_FinalRpt_ACME.CFI-G.pdf` (3.9 MB) | Oxygen and pressure limits where cool flames appear, key sentences for the caption | `data/curated/coolflame_notes.csv` |

## Priority 3: nice to have

| ☐ | What | Where | Notes |
|---|---|---|---|
| ☐ | FLEX and FLEX-2 summary documents | [PSI-69 FLEX](https://psi.nasa.gov/physci/repo/data/investigations/PSI-69), [PSI-68 FLEX-2](https://psi.nasa.gov/physci/repo/data/investigations/PSI-68) | The PSI API lists only the experimental table for these (about 0.9 and 1.2 TB of raw data). Check the page for any report or readme; if none, use the publications list on the page |
| ☐ | Saffire-II documents | [PSI-99](https://psi.nasa.gov/physci/repo/data/investigations/PSI-99) | Only the table is listed. Its table already has some spread values (we use them) |
| ☐ | ACME E-FIELD flames | [PSI-22](https://psi.nasa.gov/physci/repo/data/investigations/PSI-22) | Only the table and 4 images listed. Low priority |
| ☐ | SPICE smoke points (thesis) | [PSI-107](https://psi.nasa.gov/physci/repo/data/investigations/PSI-107) `...DotsonThesis.pdf` (2.2 MB) | Smoke point by fuel; supports the smoke lens |

## Not in PSI at all (search elsewhere, cite only)

| ☐ | What | Where to look | Why it matters |
|---|---|---|---|
| ☐ | Saffire IV, V, VI (reduced pressure, higher oxygen) | NTRS: [Saffire VI preliminary results](https://ntrs.nasa.gov/citations/20240002981) | The only large-scale fires at lunar-like atmospheres. Cite in the pitch; do not mix into the run table without a table of values |
| ☐ | SoFIE and FM2 (lunar gravity) | [NASA Combustion Science page](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/) | Explains why lunar and Mars gravity show "No evidence" today |
| ☐ | Crew-safe oxygen limits (for a "breathable" zone) | NASA-STD-3001 Volume 2, requirements V2 6002 and V2 6003; [technical brief OCHMO-TB-003](https://www.nasa.gov/wp-content/uploads/2023/12/ochmo-tb-003-habitable-atmosphere.pdf) | We have not found the numbers yet. Never type a limit from memory |
| ☐ | The exact official challenge text | [Flame in Freefall](https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/) (our tool could not open it) | Quote it in the summary and slides |

## Do not download

Raw videos and image folders (`Raw Data`): BASS-II alone is about 256 GB, ACME runs are about 2 TB. We only need tables, reports and readmes.

## Already downloaded (no action)

In `data/raw/` (git-ignored, rebuild with `python scripts/fetch_psi.py` and `python scripts/fetch_psi_docs.py`): all 26 experimental tables; BASS-II test matrix, readme and fan calibration; BASS as-run and planned matrices; CFI data summary sheet and final report; SAME and SAME-R final reports; DAFT 30-day report; Saffire readme and objectives; SPICE final report.
