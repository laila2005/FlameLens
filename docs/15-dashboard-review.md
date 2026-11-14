# Dashboard review: what makes it weak, and what data is missing

Reviewed 14 Nov 2026, about 8:50 AM Cairo (hour 19.8), on the live site https://flamelens-steel.vercel.app (desktop and 375 px phone), plus a count over `data/curated/runs.csv` (2,003 runs).

What works: no console errors, no sideways scroll on a phone, 137 of 137 live checks pass, every number traces to a run or a cited document, and "Ask the NASA reports" gives live, quote-verified answers.

## 1. Weaknesses, most serious first

| # | Weakness | What a judge sees | Why it matters | Fix (size) |
|---|---|---|---|---|
| 1 | **Conditions are judged one at a time, across all fuel types.** For the rover (solid material, 30 % O₂, 10.2 psi), "Oxygen: Supported, 134 runs" comes only from gas flames (85) and fuel droplets (49), and "Pressure: Supported, 107 runs" only from droplets (FLEX 103, CFI 4). Not one solid-material run is at 30 % O₂ or near 10.2 psi. | "4 of 5 conditions supported" next to "0 runs match" | Overstates the evidence for cabin materials, the challenge's main question. "Run this next" then says it closes only one gap (gravity), which is wrong for solids. | Judge oxygen and pressure within the chosen material type, or add "(gas and liquid fuels only)" to the pill. Small–medium; it changes decision logic, so the cached AI text and validation must be re-run. |
| 2 | **Two zeros at the top of the strength meter** (whole habitat 0/100, atmosphere-only 0/100, all four parts 0 %) for every lunar and Mars design. | The meter looks broken for 4 of 5 presets | The useful evidence (closest runs, Saffire V, per-condition scores) is lower on the page. | Show the "tested one at a time" score (as the journey cards now do) next to the 0. Small. |
| 3 | **"Safer tested options" are not realistic for the design.** For the rover it suggests 18.7 % O₂ at 14.7 psi (+4.5 psi, a different atmosphere) in 0 g. | Advice that ignores the pressure the design was built around | The word "safer" also sits close to a safety verdict, which the rules forbid. | Rename to "Tested options with less oxygen"; prefer runs at the design's own pressure; say when none exist. Small. |
| 4 | **Two different AI systems.** The evidence panel uses pre-generated qwen2.5:7b text (Mars falls back to a template); "Ask the NASA reports" uses live Gemini. Some qwen recommendations go beyond the evidence (e.g. "place smoke sensors in the return path"). | Mixed labels and models | Harder to explain in 30 s; the recommendations read like design advice. | Say in one line which model does what; regenerate Mars; consider hiding the recommendation lines. Small. |
| 5 | **The page is very long**: about 21,000 px on a phone (about 26 screens): habitat, verdict, closest evidence, AI text, strength, case, run this next, options, 6 lenses, campaign planner, journey, Ask, investigations, data, footer. | Judges see the top 2–3 screens only | Best features (journey, campaign, Ask) are far down. | Add a sticky section menu or "jump to" links; collapse secondary panels. Small–medium. |
| 6 | **ACME outcomes are day counts, not run results.** BRE, CLD, s-Flame and E-FIELD (118 runs) show outcomes like "flames ignited that day: 8". | Odd labels in run drawers and outcome lists | Looks like a parsing bug. | Relabel as "day: N flames ignited (per-flame result not in the table)". Small. |
| 7 | **Coverage map leaves out 231 runs** (1,772 of 2,003 plotted) that have no oxygen or pressure value. | A gap between the "2,003 runs" chip and the map | Minor, but a judge may notice. | Say "231 runs without O₂ or pressure are not plotted". Small. |
| 8 | **Submission items not finished**: the 30 s video exists (`media/flamelens-demo-30s.mp4`) but is not uploaded; the premium version was postponed; slides and the official submission are with the leader. | – | Judges score the video or slides first. | Team task, not code. |

## 2. Missing data (what NASA PSI does not give us)

| Gap | Size | Where it hurts | Can we fill it? |
|---|---|---|---|
| **Solid materials in raised oxygen or reduced pressure** | 0 of 383 solid runs are above 22.7 % O₂ or below 14 psi | Moon base, rover and Mars presets: the core challenge question | Not in PSI. Saffire IV–VI (outside PSI, 8 tests, cited) already fill part of it. NASA-STD-6001 Test 1 results (1 g) would add more, but they are ground tests. |
| **Partial gravity (Moon 0.16 g, Mars 0.38 g)** | 0 of 2,003 runs; all are 0 g | Every lunar or Mars design scores 0 for the whole design | No. LUCI and FM2 are planned, not flown. We say so. |
| **Outcome is only "tested"** | 962 runs (48 %): SPICE 424, ACME Flame Design 327, BASS 122, BASS-II 54, CFI 15, SLICE 12, CFI-G 8 | Run drawers say what was tested, not what happened | Partly: SPICE smoke points done (45 runs). Flame Design and BASS results are in reports and plots (plot-read, low confidence). |
| **Airflow not in the table** | 1,215 runs (61 %), mostly gas flames and droplets | Airflow condition can't be matched for those runs | Partly: BRE quiescent, CLD/E-FIELD/SLICE coflow now shown in profiles as sourced notes; speeds are not published per run. |
| **Pressure assumed (cabin air)** | 960 runs (48 %); oxygen assumed or missing for 789 | Lower reliability scores | BASS measured O₂ and pressure exist for 123 tests (as-run matrix) but are switched off (`FLAMELENS_BASS_ATMOSPHERE`), because turning them on changes ISS counts 336 → 427 and needs the AI text regenerated. |
| **Flame spread rates** | 43 measured points only (`spread_rates.csv`) vs 251 BASS and BASS-II runs | Flame spread lens is thin | More are in BASS-II report figures (plot-read, low confidence). |
| **Flammability limits (LOC) per material and pressure** | Not derived | "How much oxygen is too much" is the question engineers ask | FLEX has 186 extinction runs with oxygen and pressure; a limiting-oxygen table per fuel could be computed from them (droplets, not solids). |
| **Smoke and detection data** | Particle sizes: 14 summary rows; CO/CO₂ traces: BASS-II only | Detection lens and simulator rely on few sources | SAME-R per-run size files exist in PSI but were not downloaded. |
| **Investigations not in PSI** | SoFIE, FLARE, LUCI, FM2 | Newer solid-fuel work missing | No public data yet; shown as "not yet in PSI archive". |

## 3. Fix plan

Written about 9:05 AM Cairo (hour 20). Deadline 1:00 PM (hour 24). The plan moves the code freeze to 12:00 and the submit to 12:30, so the leader must agree (it replaces "submit at hour 21" in `docs/04-hackathon-timeline.md`). Claude does phases 1–4; the team does phase 5 in parallel. W = weakness (section 1), G = data gap (section 2).

### Phase 1, 9:10–9:50: decision logic (W1, W2, W3)

| Item | What changes | Done when |
|---|---|---|
| W1 material-aware support | In `engine.case()`, oxygen and pressure count as Supported only if 2+ runs match that condition **with the same material type**. If only other fuels match, the status is "Other fuels only" (a gap, not supported). "Run this next", journey, campaign and brief use the same rule. | Rover reads "2 of 5 conditions supported" and "Run this next" closes oxygen, pressure and gravity. ISS still 5 of 5. Tests updated. |
| W2 meter | Under the two 0/100 numbers, show the "tested one at a time" score and one line: "0 because no run matches all conditions together; see Closest NASA evidence". | No preset shows only zeros without an explanation. |
| W3 options | Rename to "Tested options with less oxygen". Prefer runs within 2 psi of the design's pressure; if none, say "none at your pressure; these are at 14.7 psi". | Rover shows the honest "none at your pressure" line. |

### Phase 2, 9:50–10:20: display and wording (W4, W5, W6, W7)

| Item | What changes | Done when |
|---|---|---|
| W6 ACME outcomes | Show "day result: N flames ignited (per-flame result not in the PSI table)" instead of "flames ignited that day: N". | No run drawer shows the old label. |
| W7 coverage map | Caption: "231 runs without oxygen or pressure values are not plotted." | Caption matches the API count. |
| W4 AI labels | One line in each AI panel: "Evidence panel: open model (qwen2.5), written ahead and re-checked live. Ask: Gemini, live, quote-checked." Hide "engineering recommendation" lines behind "Show suggestions". | Both panels say which model and how it is checked. |
| W5 long page | Sticky "Jump to" bar under the header: Verdict, Evidence, Lenses, Campaign, Journey, Ask, Investigations. | On a phone every main section is one tap away. |

**Checkpoint 10:20:** run tests and `validate_live.py`, deploy, check in the browser. If anything fails, roll back to the last good deploy.

### Phase 3, 10:30–11:30: data gaps we can close

| Item | What changes | Done when |
|---|---|---|
| G5 BASS measured atmosphere | Turn on `FLAMELENS_BASS_ATMOSPHERE` (123 tests get measured O₂ and pressure from NASA's as-run matrix). Re-check the cached ISS AI text with the verifier; drop any claim that fails. | ISS counts update (about 336 → 427), 0 unverified claims shown, validation updated. |
| G7 oxygen limits (observed only) | New table from FLEX: per fuel and pressure, the lowest oxygen at which a droplet still burned in the PSI table. Labelled "observed in these runs, not a flammability limit". | A small "Lowest oxygen that burned" lens, every cell links to its run. |
| G3 outcome "tested" | Run drawers say where the result is: "result in report figures (not in the PSI table)" with the report link, for Flame Design, BASS and BASS-II. No values read from plots. | No run says just "tested" without a pointer. |
| G4/G6 | Profiles already show sourced notes; add the same note in run drawers ("airflow: quiescent, per PSI text"). | Run drawers match the profiles. |

### Phase 4, 11:30–12:00: AI text, final checks, docs

| Item | What changes | Done when |
|---|---|---|
| Mars AI text | Optional, needs Laila's Google key on her laptop: run `scripts/build_explanations.py mars-habitat` against Gemini's OpenAI-compatible endpoint. Otherwise keep the verified template and say so. | Mars shows verified AI text or the labelled template. |
| Final | Tests, `validate_live.py`, deploy, README and `FINAL-SUBMISSION.md` numbers updated (rover verdict, ISS counts), CLAUDE.md status log. | All checks pass on the live site; docs match it. |

**Code freeze 12:00.** After that only wording fixes.

### Phase 5, team, in parallel from now

| Owner | Task | Done when |
|---|---|---|
| Leader | Upload `media/flamelens-demo-30s.mp4` (YouTube unlisted or Drive) and test the link in a private window | Link opens logged out |
| Leader / F | Slides (7) from `docs/FINAL-SUBMISSION.md`; add the "missing data" slide below | Deck done by 12:15 |
| Leader | Submit on the official site with the live URL, repo, video and AI disclosure | Submitted by 12:30 |

### Gaps that no code can close (say them in the pitch)

| Gap | Pitch line |
|---|---|
| G1 solid materials at Moon/Mars atmospheres, G2 partial gravity, G9 SoFIE/FLARE/LUCI/FM2 | "NASA's PSI archive has no fabric or plastic burned at Moon or Mars atmospheres and no partial-gravity runs. FlameLens shows that gap, the nearest real evidence (including Saffire V outside PSI), and the cheapest test to close it." |
| G3 plot-only results, G8 per-run smoke sizes | "Where a result exists only in a report figure, we link the figure instead of guessing a number." |

If time runs short, cut from the bottom: G7 first, then W5, then G5. Never cut W1: it is the one a NASA judge would catch.
