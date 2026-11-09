# Data guide

**The dataset is the real project.** The UI and the AI are only as good as the curated table. Owners: D (lead) and F (second extractor). The dataset arrives on 13 Nov, so the schema below is a **hypothesis** to check in the first 2 hours.

## Row format

One row per run. File: CSV, UTF-8, one header row.

```
run_id, psi_id, material, geometry, o2_pct, pressure_psi, airflow_cm_s, diluent,
gravity_g, outcome, spread_rate_mm_s, value_source, source_ref, confidence, notes
```

| Column | Meaning | Rule |
|---|---|---|
| `run_id` | Unique, e.g. `BASS-R03` | Never reuse an ID |
| `psi_id` | Investigation, e.g. `BASS` | Same spelling every time |
| `material`, `geometry` | What burned and how it was arranged | Free text, short |
| `o2_pct` | Oxygen percent by volume | Number only |
| `pressure_psi` | Total pressure in psi | Convert kPa: psi = kPa × 0.145 |
| `airflow_cm_s` | Flow speed in cm/s | Convert m/s × 100 |
| `diluent` | Added gas such as nitrogen, with percent | Text |
| `gravity_g` | `0`, `0.16`, `0.38`, `1` | Number |
| `outcome` | e.g. `burned`, `extinguished`, `cool flame` | Short label |
| `spread_rate_mm_s` | Flame spread rate | Number or empty |
| `value_source` | `table`, `plot-read` or `text` | Required for every number row |
| `source_ref` | Paper plus page or figure | Required. No source, no row |
| `confidence` | `high`, `medium`, `low`, or `placeholder` | See below |
| `notes` | Anything odd | Free text |

## Golden rules

1. **No source, no row.** Every row has a `source_ref` someone else can open.
2. **Missing stays empty.** Never guess a value to fill a column. The ranker handles empty fields.
3. **Never invent.** If a plot is unreadable, leave it empty and note why.
4. **Units are converted at entry**, and the original unit goes in `notes` if it was not psi, cm/s or percent.
5. **Two people, one convention.** D and F check each other's first 10 rows.

## Confidence

| Value | When |
|---|---|
| `high` | Number copied from a table or the text |
| `medium` | Number from text with a stated approximation |
| `low` | Number read off a plot (also tag `value_source = plot-read`) |
| `placeholder` | Fake sample data. See below |

Plot-read numbers are allowed but show a lower-confidence badge in the UI. This turns a weakness into a visible honesty feature.

## Placeholder data

`data/mock/runs_placeholder.csv` contains invented rows in the same format so everyone can build before the real data arrives.

- Every placeholder row has `confidence = placeholder` and `source_ref = placeholder`.
- The UI shows a visible **"sample data"** banner while any placeholder row is loaded.
- Real rows replace placeholders file by file. The banner disappears only when none are left.
- **Never** quote a placeholder value in the pitch, slides or video.

## Extraction process on the day

1. D and F open every investigation file and list the fields that actually exist.
2. Compare with this schema and change it in the first 2 hours if needed. Tell A immediately.
3. Split by pillar: D takes Prevention (BASS, BASS-II, Saffire, SPICE, BRE). F takes Detection and Suppression (SAME, SAME-R, DAFT, DAFT-2, FLEX, FLEX-2, CFI, ACME E-FIELD).
4. Enter runs into one shared CSV per pillar. Push a batch every 2 hours so A can load it.
5. First target: 15–20 runs across at least 6 investigations by hour 6, then 30–40 by hour 13. Data freeze at hour 15.

## Minimum data per feature

| Feature | Minimum |
|---|---|
| Ranker, Evidence case, Run this next, Safer options | 20–30 runs across at least 8 investigations with O₂, pressure, fuel and geometry |
| Lens 1 Ventilation | Spread rate vs flow speed at 2–3 O₂ levels for one or two materials (BASS, BASS-II, Saffire) |
| Lens 2 Aerosol | Particle-size mean and spread for 3–4 smoke sources and one dust profile (SAME, SAME-R, DAFT, DAFT-2) |
| Lens 3 Cool flames | Droplet runs with regime label vs O₂ and diluent (FLEX, FLEX-2, CFI) |
| Diff | Any two investigations with hardware, constants and outcomes filled in |

If a lens has no usable data by hour 6, cut it or show its published trend as a cited summary.

## Terminology

Use **LOC** (limiting oxygen concentration) in the UI, mention LOI (the ground-test name) in a tooltip.

## Folders

- `data/raw/`: real downloads. Git-ignored. Share through the team drive if large.
- `data/mock/`: placeholder data, committed.
- `data/curated/`: our cleaned CSVs after kickoff, committed.
