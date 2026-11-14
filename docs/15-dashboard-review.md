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
| 8 | **Submission items not finished**: the 30 s video was postponed; slides and the official submission are with the leader. | – | Judges score the video or slides first. | Team task, not code. |

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

## 3. Suggested order before the 10 AM submit (hour 21)

1. Fix weakness 1 (material-aware oxygen and pressure), or at least label it: it is the one a NASA judge would catch.
2. Weaknesses 2, 3, 6 and 7: small wording and display fixes.
3. Weakness 5: "jump to" links so the journey, campaign planner and Ask are one click from the top.
4. Leave data gaps as they are and say them out loud in the pitch: "PSI has no solid-material runs at Moon or Mars atmospheres and no partial-gravity runs; FlameLens shows that gap and the cheapest test to close it."
