# 14 Validation report (Fri 13 Nov 2026, about 11 PM Cairo, hour 10)

What was tested, what passed, what was fixed, and what is still open before we submit. Re-run the automatic part any time:

```bash
python scripts/validate_live.py .
```

It checks the live site https://flamelens-steel.vercel.app against `data/curated/runs.csv` and prints PASS or FAIL for each check. Result tonight: **117 of 117 passed**; after adding the campaign planner (11:55 PM) **124 of 124**.

## 1. What the script checks

| Group | What it proves | Result |
|---|---|---|
| Data (16 checks) | `runs.csv` has 2,003 unique runs from 18 PSI investigations. Every row has a DOI, a source table and a confidence of high, medium or low. Every oxygen, pressure and airflow value has a basis tag (measured, text, assumed, unknown). A value is empty exactly when its basis is "unknown", so missing stays empty. All runs are 0 g. No placeholder rows, so no "sample data" banner is needed | all pass |
| Public access (10) | The page, `/docs`, the API and all four downloads open with no login. The downloaded `runs.csv` is identical to the repo copy | all pass |
| Requirements (15) | Presets match the challenge text (rover 30 % O₂ at 10.2 psi and 0.16 g; spacesuit 100 % at 4.3 psi). Investigation summaries and the side-by-side comparison work. All 5 chart lenses return real data, including 43 flame-spread points. Detection evidence, 5 CFD studies, the NTRS papers and the NASA Spinoff links are present | all pass |
| Each preset + 2 extra designs (55) | For Moon base, rover, spacesuit, ISS cabin, Mars habitat, a design far from every run and a custom design: every run ID returned exists in the table. Each condition's label follows the rule: Supported needs 2 or more matching runs, Weak 1, No evidence 0. Any gravity above 0 shows No evidence. Each safer option has at least 10 % less oxygen partial pressure and is a real run. The "Run this next" starting run matches its table row. Strength scores stay within 0–100. Every explanation sentence is verified, with 0 removed and no "safe" or "unsafe" wording. The far-away design gets "No evidence", never a guess | all pass |
| Citation verifier (9) | The verifier keeps a correct claim and **removes** each of these: an invented run ID, a real run that was not retrieved, a changed number (27.3 %), a rounded number (22 % for a run at 22.2 %), the word "safe", an invented limit, a claim with no run cited, and a second unretrieved run named in the text | all pass |
| Evidence trail (2) | 25 random run IDs open with the same DOI and values as the table; the response states the CC0 licence | all pass |
| Campaign planner (7) | ISS needs no new test; Moon base and rover share test #1; 3 tests leave no preset open; every planned test really matches each design it claims (recomputed independently); every starting run is real; partial-gravity tests are flagged; n=1 gives one test | all pass |
| Rules (3) | AI use is disclosed on the page. The page says evidence strength is "not a safety rating". There are no images of people | all pass |

**Checked by hand in the browser (live site):** each of the 5 presets shows a verdict, 5 verified claims, "Run this next" and 3 safer options. The run links I clicked (4 per preset) opened the evidence drawer with a NASA DOI. The light and dark themes both work, as does phone width (375 px) with no sideways scroll. There are no console errors. The GitHub repo opens without login, and only `.env.example` and `data/raw/.gitkeep` are tracked (no secrets). `python -m pytest backend/tests -q` passes 67 tests.

## 2. Problems found and fixed tonight

| Problem | Fix |
|---|---|
| README and submission text said smoke is 0.04–0.32 µm; the data (SAME-R Table 1) and the dashboard say 0.04–0.29 µm | Corrected in `README.md` and `docs/FINAL-SUBMISSION.md` |
| "Airflow tested" lens described as 684 runs; it plots 681 | Corrected in both files |
| BASS-II gas traces described as 153 runs; `detect_gas.csv` has 129 | Corrected in both files |
| Slide 1 said thin fabrics spread "200× faster"; the data gives 20–200× | Now "up to 200× faster" |
| Switching lens tabs cleared the highlight on the selected investigation filter (Prevention, Detection, …), because both used the same `tab` class | `app.js` now only updates the lens tabs. Needs a Vercel redeploy to reach the live site |

Known, harmless: `/api/health` reports `investigations: 26` (all profiles, including ground and CFD studies). The dashboard's "18" counts flight investigations that have runs.

## 3. Still open before submission

| # | Task | Owner | By |
|---|---|---|---|
| 1 | **Demo:** a 30-second screen video (no faces or voices of anyone under 18) or exactly 7 slides, on a public link. The storyboard is in `docs/FINAL-SUBMISSION.md` Part 3. Record it from the live site after the final redeploy | Yousseif / Laila | Sat 9:00 AM |
| 2 | Choose the **team leader** who submits | Team | Now |
| 3 | Confirm the final deadline (Sat 1:00 PM?) on Discord | F / Laila | Sat morning |
| 4 | A teammate proofreads the project summary in `docs/FINAL-SUBMISSION.md` | Any | Sat 9:00 AM |
| 5 | Tag the release that the demo shows (`git tag v1.0` then push the tag) | Laila | Before recording |
| 6 | Open every link (site, repo, demo) in a private window | Leader | Before submitting |
| 7 | Submit on the **local form**, then the same files on the **official NASA Space Apps site**; save screenshots of both confirmations | Leader | Sat 10:00 AM (deadline 1:00 PM) |
| 8 | Backup internet ready (venue Wi-Fi may be slow) | Leader | Sat morning |
| 9 | Remember: Vercel is not linked to GitHub. After any code change, redeploy with `vercel deploy --prod --yes`, then re-run `python scripts/validate_live.py .` | Laila | After each change |
| 10 | A native speaker proofreads the Arabic task files (written by Claude) | Any | Optional |
