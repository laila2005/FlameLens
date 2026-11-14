# CLAUDE.md: project context for Claude

Read this first in every new session. It is the handoff file: it says what the project is, what has been decided, what state things are in, and how to work with this team. Humans can read it too.

**Keep it current.** When a decision is made or a task changes state, update the relevant section and the "Status log" at the bottom in the same session, then commit. If this file and another doc disagree, ask the user which is right, then fix both.

## 1. What this is

**FlameLens** is the project of **Team AstroSpark** (6 people) for the **NASA Space Apps Challenge 2026**. The hackathon is **Fri 13 Nov to Sat 14 Nov 2026** (**24 hours**: Fri 13 Nov 1:00 PM to Sat 14 Nov 1:00 PM Cairo time, kickoff is hour 0). The challenge is about NASA's **PSI (Physical Sciences Informatics)** fire-safety experiments run on the ISS: the data is public but scattered across experiment pages, papers and plots.

**Critical constraint: the real dataset is not available until kickoff on 13 Nov.** Everything before then is preparation: plan, docs, designs, accounts, research notes, placeholder data. The schema in `docs/06-data-guide.md` is a *hypothesis* to verify in the first 2 hours of the event.

**Repo:** https://github.com/laila2005/FlameLens (branch `main`, owner account `laila2005`).

## 2. The solution in brief

An engineer enters a habitat design (oxygen %, pressure, airflow, fuel, gravity). FlameLens returns a decision they can defend, not a search result list:

1. **Evidence case:** each condition marked Supported (2+ matching runs), Weak (1) or No evidence (0), plus a whole-design line, each with run IDs.
2. **Run this next:** the experiment that closes the most gaps, with the nearest existing run as the cheapest first step.
3. **Safer options:** nearest *tested* conditions with at least 10% lower oxygen partial pressure, never extrapolated.
4. **Evidence strength meter (0–100):** four visible parts (proximity, reliability, run count, source quality). Not a safety rating.

Supporting pieces: a deterministic ranker (weights 0.35 O₂, 0.20 pressure, 0.20 airflow, 0.15 fuel, 0.10 gravity), three lenses (airflow vs flame spread, smoke vs dust, cool flames), a coverage gap map, an evidence trail (click any claim to see run, source, confidence), and a cited AI explanation.

**Core design principles (do not violate):**
- The decision logic (`/case`, `/next`, `/alternatives`, `/strength`, ranker) is **deterministic, no AI**.
- AI only explains or parses text. A **citation verifier** removes any claim whose run ID is not in the retrieved input or whose number is not in that run.
- The app **must work with the AI off**.
- **No source, no row.** Never invent or round a scientific value. Missing stays empty. "No evidence" is a valid answer.
- Placeholder data is always labelled and the UI shows a "sample data" banner while any placeholder row is loaded.
- Never claim a safety verdict. We show evidence and gaps.

## 3. Where everything is

| What | Where |
|---|---|
| Overview and doc map | `README.md` |
| New-member onboarding | `docs/00-START-HERE.md` |
| Brief, scope tiers, risks | `docs/01-project-brief.md` |
| Roles, backups | `docs/02-team-roles.md` |
| Day-by-day prep (9–13 Nov) | `docs/03-prep-schedule.md` |
| Hour-by-hour plan for the 24 h | `docs/04-hackathon-timeline.md` |
| **Official event facts, rules, submission format, judging criteria** | `docs/11-event-facts.md` (from the organizers' two PDFs) |
| Web research: challenge name, PSI access routes, NTRS API, papers, investigations | `docs/12-resources.md` |
| Hackathon-day start: resource summary, reading assignments, first hour | `docs/13-start-now.md` |
| **Validation report: what was tested, fixes, what is left before submitting** | `docs/14-validation-report.md` (re-run `python scripts/validate_live.py .`) |
| **Dashboard review: weaknesses and missing data (hour 19.9)** | `docs/15-dashboard-review.md` |
| Stack, API contract, ranker, decision-route rules | `docs/05-architecture-and-api.md` |
| Data row format and extraction rules | `docs/06-data-guide.md` |
| AI model, prompts, verifier rules, bake-off | `docs/07-ai-guide.md` |
| Git flow, rule check, communication | `docs/08-working-agreements.md` |
| Demo script, QA checklist, submission checklist | `docs/09-pitch-and-submission.md` |
| Idea brainstorm (smarter-than-others features) | `docs/10-idea-brainstorm.md` |
| Role chooser with required experience (EN + AR) | `docs/roles/00-choose-your-role.md` |
| Per-role tasks A–F | `docs/roles/*.md` (English), `docs/roles/ar/*.md` (Arabic) |
| Team checklist (EN + AR) | `TASKS.md` |
| Research notes template and index | `docs/research/` |
| Design and spec files (written by role tasks) | `docs/design/` (see its README for expected file names) |
| Placeholder data (all values invented) | `data/mock/runs_placeholder.csv` |
| Environment check | `python scripts/check_env.py` |
| Remaining planning pages | `docs/links.md` |

### Interactive pages (private Claude artifacts)

Made during planning. They are private; the owner shares them. They may need re-reading with the Artifact tool's `read` action.

- Dashboard mockup: https://claude.ai/artifact/QaSxsDvZYuo2VtRu6nngeh (design sketch only, see Rule 1; its inline script was the reference for the matching logic)
- FlameLens Explained: https://claude.ai/artifact/Q522NGdaw1VpjqoVGdK9Ua
- Earlier deliverable, team slide deck (5 slides): https://claude.ai/artifact/2woKjf9i4HGW5CNtuazYJQ
- **Outdated, ignore** (old 48-hour plan, superseded by the repo): Master plan, Team Split, AI Model Guide, Team Prep Checklist artifacts. They were removed from `docs/links.md`.

## 4. Decisions made

| Topic | Decision |
|---|---|
| Stack | Vite + React + TypeScript + Tailwind, Plotly.js, FastAPI, SQLite or DuckDB, one container host (Render or Fly, not yet chosen) |
| Text retrieval | Filter by `psi_id` first, then small local embedding model (MiniLM or bge-small) or keyword match. No pgvector |
| LLM | Open model first: Qwen Instruct 7–14B, backup Llama 3.x 8B, Hermes if JSON breaks, hosted proprietary only as last resort. Via Ollama or an OpenAI-compatible endpoint. One call per pillar, not three agents |
| Data | Hand-curate 30–40 runs (24-hour event) with `source_ref`, `value_source`, `confidence`. Plot-read values allowed but tagged low confidence |
| Data owners | D takes Prevention (BASS, BASS-II, Saffire, SPICE, BRE). F is second extractor for Detection and Suppression (SAME, SAME-R, DAFT, DAFT-2, FLEX, FLEX-2, CFI, ACME E-FIELD) in hours 0–14 |
| Terminology | Use LOC (limiting oxygen concentration) in the UI, mention LOI in a tooltip |
| Oxygen partial pressure | pressure × O₂ fraction; Earth air is about 3.1 psi; shown on every result |
| Decision-route tolerances | O₂ within 6 points, pressure within 2 psi, airflow within 8 cm/s, same fuel, same gravity. **Starting guesses, tune on real data hours 6–10** |
| Evidence strength formula | 0.35 proximity + 0.30 reliability + 0.20 run count + 0.15 source quality. **Guess weights, tune** |
| Scope control | 24-hour event: Gate 1 at hour 6 (Fri 7 PM), Gate 2 at hour 13 (Sat 2 AM), freeze at hour 17 (Sat 6 AM), submit at hour 21 (Sat 10 AM), deadline hour 24 (Sat 1 PM). At most ONE brainstorm idea before Gate 2, chosen at Gate 1 |
| Rejected | Physics simulation, chat-only assistant, yes/no safety verdicts, many AI agents, pgvector, treating Lens 4 / Electric-Gravity Bridge as validated |

Brainstorm ideas, ranked (details and formulas in `docs/10-idea-brainstorm.md`): evidence strength (Must), campaign planner, atmosphere journey, breathable-and-tested zone (only if role F finds an official sourced limit), plain-language entry, reverse search, risk passport; stretch: surprise detector, uncertainty band, BOM auditor.

## 5. Team

Six roles (names in `docs/02-team-roles.md`): A tech lead and backend, B frontend, C charts and lenses, D data extractor (lead), E AI and retrieval, F research, docs, pitch and QA. Task IDs: A1–A9, B1–B8, C1–C6, D1–D7, E1–E8, F1–F9 (see `TASKS.md`). The team is Arabic-speaking and uses English for technical work, so **role docs exist in English and Arabic** and task lists in `TASKS.md` are bilingual. Keep the Arabic files in sync when you change an English role file.

## 6. Rules for working in this repo

1. **No product code before the hackathon starts (Fri 13 Nov, 1:00 PM Cairo).** The official guide: planning and task split are allowed, presenting ready or half-finished projects is prohibited, actual work starts at the start. Docs, designs, research notes and tooling are fine. Practice code stays outside the repo and is never reused. The interactive dashboard mockup is a design sketch only: rebuild everything from scratch after 1:00 PM and do not present it as built.
2. Earth spin-off text must come from the NASA spin-off pages in `docs/12-resources.md` section 0; never invent one.
3. Do not invent scientific values, thresholds, oxygen limits or experiment results. Anything scientific needs a source in `docs/research/claims.md` (task F5) or must be labelled as an example/guess.
4. Do not put secrets in the repo. `.env` is git-ignored; `.env.example` documents the variables.
5. **Commit and push to `main` automatically, without asking** (Laila's standing instruction, 13 Nov). Before each push: run `python -m pytest backend/tests -q` if backend code changed, `git fetch` and merge `origin/main` (teammates push too), never force-push, never commit secrets or `data/raw/`. Commit messages end with the attribution line the session instructs. Report what was pushed in one line.
6. Keep docs plain and short: sentences a non-expert can follow, tables for structure, no jargon without a definition.
7. When you change a task, role or decision, update all places: the doc, `TASKS.md`, the Arabic copy if one exists, and the Status log below.

## 7. About the user and how to help

- The user leads or coordinates the team and writes informal English with typos. Read for intent, answer in clear simple English (or Arabic when asked).
- Likes: clear organisation, one document per purpose, tasks that say exactly what to do and when "done" is, honest answers over hype. Asked for "a guarantee to win" once; the honest answer is that nobody can guarantee it, so we maximise odds.
- Prefers that planning outputs be put in front of the team (docs in the repo, interactive pages) rather than only chat text.
- The user asks you to proceed in steps ("yes", "update the plan accordingly"). Do what was asked, then state clearly what is not verified.

## 8. Known gaps and open items

- Real PSI data format unknown until 13 Nov. Field names, units and file types are guesses.
- Team decision (9 Nov): the guidebook line about not changing the registered idea is read as "do not change the challenge"; we keep the same core FlameLens idea and only add features. Follow a mentor if told otherwise.
- Event facts now confirmed from the official PDFs (`docs/11-event-facts.md`): 24 hours, 7 slides or a 30-second video, only the team leader submits, links must be public, AI use must be disclosed, no under-18 faces or voices. Still to confirm on Discord: the final deadline and the steps for the official NASA site; the arrival time differs between guides (8:00 vs 9:00 AM).
- Team (full names, confirmed 14 Nov): A Laila Mohamed (repo owner), B Youssif Hassan, C Yasmin Reda, D Judy Adham (backup F), E Dai Alaa, F Mostafa Fathy. Backups, hosting, LLM choice, repo licence, team leader who submits, which 5 are onsite: undecided (see "Open decisions" in `TASKS.md`).
- GitHub collaborators not yet added (task A1).
- Arabic task files were written by Claude and have not been reviewed by a native speaker on the team. Ask a teammate to proofread.
- The master-plan artifact lacks the brainstorm section; the dashboard mockup lacks campaign planner, journey and strength meter views.
- Nothing has been viewed rendered on GitHub or at phone width.
- Dates and weekdays: 13 Nov 2026 is a **Friday**. Current prep window is Mon 9 to Thu 12 Nov.

## 9. Earlier work (before the repo)

For the same team a short promotional video montage and thumbnail for FlameLens, plus a 5-slide deck, were produced earlier (1080p and 720p preview). The video files lived in a temporary session folder that no longer exists; the deck is the artifact linked above. Branding to reuse: dark navy background, flame orange (#FF8A24 range) and cool cyan accents, Sora for headings, IBM Plex Sans for text, IBM Plex Mono for numbers.

## 10. How to continue in a new session

Typical openers and what to do:

| User says | Do |
|---|---|
| "Continue" or "what's next" | Read `TASKS.md` and the Status log, report what is done, what is overdue for today's date, and propose the next step |
| "Review the docs" | Check consistency between `docs/`, `TASKS.md`, role files and Arabic copies |
| Reports a teammate's results (e.g. rules answer, hosting choice, bake-off table) | Record it in the right doc and in Section 8 and the Status log |
| Kickoff day (13 Nov) | Follow `docs/04-hackathon-timeline.md` hour 0–1; first update `docs/06-data-guide.md` with the real fields and tell the team the schema changed |
| "Build X" | Check Rule 1 first. If code is allowed, follow `docs/05-architecture-and-api.md` and the owning role's file |

Useful local commands:

```bash
python scripts/check_env.py       # tool check for the team
gh auth status                    # GitHub CLI login for pushing
```

## Status log

Newest first. One line per change: date, what, who or what session.

- 2026-11-14 5:10 AM Cairo, REAL clock (hour 16.2): second audit of `README.md`, `LICENSE` and `docs/FINAL-SUBMISSION.md` on commit `f4156be` against `data/curated/` and the running app (Claude Code session on Laila's first laptop). **Clock warning: the 14 Nov entries below were written about 6 hours ahead of the real time** (the "Material-aware evidence" commit was made at 04:09 by `git log --date=iso`, but is logged as ~10:20 AM). Checked against network time. The deadline is still 1:00 PM; check a phone, not this log. Confirmed: 2,003 runs / 18 investigations and every per-investigation count; ISS 336 runs and 82.5; rover 2 of 5, 0 whole, 0 atmosphere, nearest `PSI-25-0023`; 308 / 33 / 153 closest-evidence groups; campaign n=3; journey weakest = spacesuit; lens counts (1,772, 56, 43, 681, 55); 1,899 passages / 20 documents / 9 investigations; the seven NTRS numbers for outside-PSI sources exist and match their titles; 95 tests pass; `validate_live.py` 137 of 137; live files equal the repo; phone width 375 px has no sideways scroll. Fixed in the texts: the AI panel has cached text for 4 presets (20 claims), not 5 (the Mars preset changed to 8.2 psia / 34 % after the text was made and shows the plain summary); smoke points are 46 linked to 45 runs; added the six new data files, the smoke-points lens row, `ask.py` and `ask.js` to the README; "Ask" moved under "Inside the product" in the AI disclosure; Olson and Ferkul wording now says the lunar values are tabulated there and that low-gravity criteria differ from 1 g (paper abstract); project summary label 161 words; slide 7 AI line lists all AI uses. Not changed: the favicon stays the team logo PNG (no SVG); the simulator's median CO rise 44 ppm is the nearest-rank median (the two middle values are 44 and 46). No redeploy needed: only `.md` files changed and they are not uploaded.

- 2026-11-14 ~10:50 AM Cairo (hour 21.8): Laila: "work autonomously, finish the dashboard, then an exceptional narrated video, prepare submission". Narrated v2 video pipeline: `scripts/demo_video/voiceover.py` (Kokoro-82M open-source TTS, Apache-2.0, voice af_heart, 7 lines, 26.1 s), `capture2.py` (10 live-site scenes incl. "Other fuels only", lunar-g limits, Ask with a verified Gemini quote), `render2.py` (kinetic hook with embers, light-leak transitions, captions, music ducked about 10 dB under the voice), `soundtrack.py` takes a timing file. `docs/FINAL-SUBMISSION.md`, README and the site's AI note updated (material rule, outside-PSI sources, Gemini Ask, synthetic narration, 95 tests, submit by 12:30). TASKS.md rows updated (EN + AR).

- 2026-11-14 ~10:20 AM Cairo (hour 21.3): Laila: fix plan phases 1-2 done and live. (1) Conditions count only runs with the chosen material; new status "Other fuels only" (rover 2 of 5: its 30 % O2 and 10.2 psi matches are gas flames and fuel droplets; spacesuit 1 of 4). (2) Strength meter explains a 0 and shows the one-at-a-time score. (3) "Tested options with less oxygen" (renamed): runs at the design pressure first, warning when none. (4) Outside-PSI material limits (`data/curated/beyond_psi_limits.csv`, 16 rows): Olson & Ferkul 2012 drop-tower limits at lunar and Mars g (Mylar, Ultem 10.2 psia; Nomex 14.7), Hirsch 2007/2010 Test 1 at 10.2 psia (Nomex and Lexan fail at 30 %), ICES-2026-301 at 8.2 psia; shown in Closest NASA evidence, not counted. Research notes `docs/research/beyond-psi-sources.md`. (5) ACME day-count outcomes relabelled, map caption counts unplotted runs, AI suggestions labelled, note on the two AI helpers, sticky Jump-to bar, drawer text wraps. 95 tests. Phase 3 (BASS atmosphere, FLEX table) skipped for the video.

- 2026-11-14 ~9:05 AM Cairo (hour 20): Laila: plan to fix all weaknesses and gaps. Added section 3 "Fix plan" to `docs/15-dashboard-review.md`: phase 1 logic (material-aware support, meter, options) 9:10–9:50; phase 2 display (ACME labels, map caption, AI labels, jump bar) to 10:20 + checkpoint deploy; phase 3 data (BASS measured atmosphere on, FLEX lowest-oxygen-that-burned table, result pointers) 10:30–11:30; phase 4 Mars AI text, final checks 11:30–12:00; freeze 12:00, submit 12:30 (leader must agree). TASKS.md rows added. Not started.

- 2026-11-14 ~8:55 AM Cairo (hour 19.9): Laila: dashboard review. Wrote `docs/15-dashboard-review.md`: 8 weaknesses (top: oxygen/pressure 'Supported' for solid designs comes only from gas and droplet runs; double 0/100 meter; 'safer options' at a different pressure; two AI systems; 26-screen page on phone) and the missing data (0 solid runs above 22.7 % O2 or below 14 psi, 0 partial-gravity runs, 962 runs outcome 'tested' only, 1,215 without airflow, 960 with assumed pressure). Nothing changed in the app.

- 2026-11-14 ~8:40 AM Cairo (hour 19.7): Ask the NASA reports is LIVE with AI: Laila set GOOGLE_API_KEY (new key, 'AQ.' format) in Vercel. Google keys now try the Gemini API first and Vertex AI second (new AI Studio keys also start with 'AQ.'); Gemini 2.5 thinking turned off (it truncated the JSON). Checked live: BASS-II airflow question -> 3 verified claims, 0 removed (BASS-II Summary Report pp. 44, 49); SPICE question -> 1 kept, 2 removed by the verifier (quote not word for word; number 52 not on page). xAI key has no credits and is not used while the Google key is set. Regenerate both keys after the demo. 93 tests.

- 2026-11-14 ~8:10 AM Cairo (hour 19.2): Laila set XAI_API_KEY in Vercel (Production) herself; redeployed. Ask reaches xAI but xAI answers 403 "team doesn't have any credits", so the panel still shows passages. Code now shows the provider's reason (key and links removed) and a Google key (GOOGLE_API_KEY, free Gemini tier) takes priority over XAI_API_KEY. To make Ask live: buy xAI credits, or add GOOGLE_API_KEY (or GROQ_API_KEY) in Vercel and redeploy. 93 tests.

- 2026-11-14 ~7:45 AM Cairo (hour 18.7): Laila: (1) mission journey zeros explained: every PSI run is at 0 g, so lunar stages cannot match all five conditions; each card now shows the score when conditions are tested one at a time (ISS 92, spacesuit 41, rover 67, Moon 68), a 'Why 0' line with any other untested condition, and the outside-PSI Saffire note. (2) 'not recorded' in investigation profiles replaced with sourced NASA statements (`data/curated/condition_notes.csv`, 16 rows: ICES-2021-266 Table 2, BASS as-run matrix, BASS-II TM p.19, SPICE reports, DAFT report, PSI page text) or 'assumed ISS cabin air (not in the PSI table)'. Display only: counts, verdicts and AI text unchanged. (3) Ask supports xAI Grok keys (XAI_API_KEY, api.x.ai). Keys only as Vercel env vars, set by Laila; the pasted xAI key should be regenerated after the demo. 91 tests, 137 of 137 checks.

- 2026-11-14 ~7:05 AM Cairo (hour 18): Laila: deep search for the rover's 'no run tested this atmosphere' gap. Outside PSI, NASA's Saffire IV-VI large-scale fires (Cygnus, microgravity) tested it: Saffire V at 70.7-72.6 kPa (10.25-10.53 psi) with 25.4-26.2 % O2, Saffire VI at 54.1-55.2 kPa with 28.8-31.0 % O2 (ICES-2021-266 and ICES-2024-365, Tables 1-2). Added `data/curated/beyond_psi_runs.csv` (8 tests with outcomes) and an 'Outside PSI, cited, not counted' card in Closest NASA evidence (rover/Moon: Saffire V; Mars: Saffire VI). Counts, verdicts and strength unchanged. Claims in `docs/research/claims.md`. 89 tests.

- 2026-11-14 ~6:20 AM Cairo: Ask supports Google keys: set GOOGLE_API_KEY in Vercel (AI Studio 'AIza' -> Gemini API, Vertex 'AQ' -> Vertex AI; model gemini-2.5-flash; key sent in a header). Keys only as Vercel env vars, never in the repo. A key was pasted in chat: Laila should restrict or regenerate it. 88 tests.

- 2026-11-14 ~6:00 AM Cairo (hour 17): Laila: integrate Dai's AI scripts properly. `scripts/build_doc_library.py` (from Dai's build_library.py) -> `data/curated/doc_chunks.jsonl` (1,899 page-tagged passages, 20 PSI documents, 9 investigations; camera logs and tables of contents skipped). `backend/app/ask.py` (from Dai's explain_ai.py): BM25 retrieval + synonyms, Dai's quote verifier plus FlameLens rules (no verdicts, max 3 claims, checked recommendation/summary), cache re-verified per request, Groq gpt-oss-120b only if ASK_LLM_API_KEY/GROQ_API_KEY is set (Vercel env var, never in repo), passages fallback. Routes /api/library, /api/library/search, /api/ask, /api/ask/suggestions; panel 'Ask the NASA reports' (`frontend/dist/ask.js`). `scripts/build_ask_cache.py` pre-generates answers once a key exists. 87 tests.

- 2026-11-14 ~5:10 AM Cairo (hour 16.2): Laila: replace generic content with NASA data. All 5 presets now sourced: ISS cabin 14.7 psia / 21 % O2 (NASA OCHMO-TB-003 Rev A p. 8), Mars habitat changed to NASA's exploration atmosphere 8.2 psia / 34 % O2 (EAWG, NTRS 20220005716 slide 39; Mars AI text falls back to the verified template until the model is re-run). Simulator CO alarm = NASA long-mission SMAC 15 ppm and a crew-exposure line vs all CO SMACs (JSC 20584 Rev C p. 11). New `docs/research/claims.md` register. 80 tests.

- 2026-11-14 ~4:25 AM Cairo (hour 15.4): Laila: extract the SPICE outcomes. Downloaded the SPICE Dotson thesis, 30-day report and AIAA slides (PSI-107). Appendix 6.4 lists all 55 microgravity smoke points; `scripts/extract_spice_smoke_points.py` -> `data/curated/spice_smoke_points.csv`, 46 linked to 45 SPICE runs by burn window (outcome 'smoke point', metric smoke_point_length_mm, source in notes; build_runs.py applies it). New 'Smoke points' lens (`/api/lens/smokepoint`). ACME Flame Design table has no outcome column: 'tested' is honest. Verdicts, counts and AI explanations unchanged. 80 tests.

- 2026-11-14 ~3:40 AM Cairo (hour 14.7): Laila: deep search for unprocessed data. PSI has no combustion investigations we lack (26 of 26 ingested); PSI-179 aerosol has no files; Saffire-I/III spreadsheets are camera logs. Found BASS as-run matrix O2/pressure/observations: crew observations added to BASS notes (live); measured O2/pressure ready behind `FLAMELENS_BASS_ATMOSPHERE=1` but OFF because it changes ISS 336->427 and needs regenerated AI explanations. Details in `docs/research/data-to-check.md`.

- 2026-11-14 ~2:40 AM Cairo (hour 13.7): Laila: deep review against requirements, report and fix. Requirements all covered. Fixed 11 issues (list in `docs/14-validation-report.md` section 4): balanced desktop layout, closest-evidence logic (gravity-only group, honest 'differs'), unspecified airflow now 'Not specified' and not counted (spacesuit 2 of 4), lens-tab race, campaign error retry, empty change list, Escape order, 'null' in simulator, stale drawer/explain, rank weights validation, smoke size text. 79 tests, 131 of 131 checks. Redeployed.

- 2026-11-14 ~1:40 AM Cairo (hour 12.7): Laila: logo + mission journey. New logo: round crop of the team's Gemini-generated illustration (`media/flamelens-illustration.jpg`) in header, favicon, touch icon, brief and social image (teammate's `build_og_image.py` now draws it); AI disclosure updated. Premium video pipeline (`scripts/demo_video/soundtrack.py`, `render.py`) built; final premium video render POSTPONED by Laila. Added Mission atmosphere journey: `engine.journey()` + `POST /api/journey`, panel below the dashboard (`frontend/dist/journey.js`): ISS cabin 83 -> spacesuit 0 (weakest, 3 of 5 supported, test this next from PSI-10-0230) -> rover 0 -> Moon base 0; mission strength = weakest stage. 3 tests (76 pass), 3 live checks. Not yet redeployed.

- 2026-11-14 ~1:00 AM Cairo (hour 12): Audit of the submission package against `data/curated/` and the running app (Claude Code session on Laila's first laptop). Rewrote `README.md`, `LICENSE` and `docs/FINAL-SUBMISSION.md` with verified numbers only. Fixed: spread-rate airflow range is 1.5–29 cm/s (not 0–32); `smoke_dust_sizes.csv` has 14 rows (not 15); 73 tests (not 67); DAFT dust is Arizona Road Dust (not lunar simulant); 705–760 K is from a ground companion experiment in the CFI-G final report, so it is no longer described as a flight cool-flame temperature; removed unsourced "PBI", "composite" and Cygnus OA-5/6/7 labels; NTRS documents are not described as CC0; team names no longer carry role letters as surname initials (confirm names and roles with Laila). Added `frontend/dist/og-image.png` and `apple-touch-icon.png` (built by `scripts/build_og_image.py` from the run table), OpenGraph/Twitter tags, larger touch targets on phones. On this laptop `git fetch` needed `git config core.longpaths true`.

- 2026-11-14 ~12:50 AM Cairo (hour 11.8): Laila: make the video. Made `media/flamelens-demo-30s.mp4` (30.0 s, 1920x1080, 60 fps, H.264 + AAC, 29 MB) from the live site: rover hook, ISS 83/100 (2,003 runs), closest NASA evidence, verified claims + evidence drawer with DOI, campaign planner 1 -> 3 tests, three lenses, design review brief, title card. Captions only, synthesized background sound, no faces or voices. Pipeline saved in `scripts/demo_video/` (Edge + Playwright capture, Pillow + ffmpeg render). Storyboard in `docs/FINAL-SUBMISSION.md` Part 3. Still to do: the leader uploads it (YouTube unlisted or Drive) and tests the link.

- 2026-11-14 ~12:20 AM Cairo (hour 11.3): Laila: find a solution for the rover's 'no run matches' dead end. Added `engine.closest_evidence()` + `POST /api/closest` and a "Closest NASA evidence" block under the verdict (`frontend/dist/closest.js`), shown only when 0 runs match the whole design: the fewest conditions to relax, the real runs that match everything else, and exactly what differs. Rover: 308 solid runs (same airflow and material, but at most 22.2 % O2 at 14.7 psi), 33 FLEX runs (same O2 and pressure, liquid droplets), 153 runs at the same O2 partial pressure (labelled related, not equivalent), then a link to the campaign planner. 2 new tests, 4 live checks.

- 2026-11-13 ~11:55 PM Cairo (hour 11): Laila: build the test campaign planner. `engine.campaign()` + `POST /api/campaign {n, targets}` (greedy cover over the presets plus the user's own design, same matching rules, candidates = each design and midpoints, picks most designs covered then most gaps then nearest run), panel "Test campaign planner" with NASA can fly 1/2/3/5 (`frontend/dist/campaign.js`). Result: Moon base + rover share a lunar-gravity test at 30 % O2 / 10.2 psi; 3 tests cover all 5 presets (only ISS has a full match today). 4 new tests (71 pass); `scripts/validate_live.py` now 124 checks. Redeployed with the design review brief and the lens-tab fix.

- 2026-11-13 ~11:25 PM Cairo (hour 10.4): Laila: build the design review brief. Added a "Design review brief" button in the header (`frontend/dist/brief.js`, styles in `styles.css`): a print preview of a 2–3 page A4 evidence brief (inputs, verdict, strength, evidence case, run this next, lower-oxygen options, verified claims, closest investigations, cited DOIs, method) built fresh from the API, white paper in both themes, `?brief=1` opens it directly. Checked: all 5 presets and a custom design (template text) build it; headless Edge prints 3 clean pages. Fixed README ranker weights (engine uses O₂ 0.35 and gravity 0.10). Not yet redeployed. Next: test campaign planner (Laila chose it).

- 2026-11-13 ~11:10 PM Cairo (hour 10.2): Laila: test the requirements and validations. Added `scripts/validate_live.py` (117 checks: data provenance, every preset's decision routes, adversarial citation-verifier claims, evidence trail, public access, challenge features). Result: 117 of 117 pass on the live site. Fixed wrong numbers in README and FINAL-SUBMISSION (smoke 0.04–0.29 µm, not 0.32; airflow lens 681 runs, not 684; BASS-II gas traces 129, not 153; "up to 200×"). Fixed a lens-tab bug that cleared the investigation filter highlight (`app.js`, needs a redeploy). Report and remaining tasks: `docs/14-validation-report.md`; TASKS.md has a new "Before submitting" list.

- 2026-11-13 ~10:50 PM Cairo (hour 9.8): Laila: dashboard redesign from her laptop screenshots. New light, frosted-card look is now the default, and the old dark "mission console" sits behind a sun/moon toggle in the header (saved per browser). Habitat controls moved to a full-width row of cards at the top (presets as pills, custom sliders), evidence on the left, sticky lenses on the right, and a 3-column footer. Fonts are Sora, IBM Plex Sans and IBM Plex Mono from Google Fonts, falling back to system fonts offline. Chart and simulator colours now come from theme variables. No data, numbers or wording changed. 67 tests pass. Laila: redeploy. Live at https://flamelens-steel.vercel.app from ~10:46 PM (deployment dpl_GsVxuUXY4zaDjgwB8R4njorgnBnT); checked: light theme loads, data chip and API work, no console errors. Demo video paused; record it from the live site next.

- 2026-11-13 ~9:18 PM Cairo (hour 8.3): Generated and verified `data/curated/explanations.json` for all 5 habitat presets (`moon-base`, `pressurized-rover`, `spacesuit`, `iss-cabin`, `mars-habitat`, 5 claims each = 25 claims total, `0` removed by `explain.verify()`), fixed `<input id="flow" step="0.1">` in `frontend/dist/index.html` so preset airflows (`12.9` and `8.1 cm/s`) match their exact cache keys, and updated `backend/tests/test_explain.py` to assert `source == "cache"` with `0` removed claims.
- 2026-11-13 ~9:10 PM Cairo (hour 8.2): Finalized judge-facing `README.md` (full architecture, 19 PSI spaceflight DOIs + 5 CFD studies, NTRS & Spinoff credits, local quickstart, and AI-use disclosure), added MIT `LICENSE` (with CC0-1.0 NASA PSI notice), added `frontend/dist/favicon.svg` + OpenGraph/Twitter meta tags (`frontend/dist/index.html`) + 375px mobile responsiveness (`frontend/dist/styles.css`), and created `docs/FINAL-SUBMISSION.md` with copy-paste Space Apps submission fields, 7-slide deck text, and 30-second video storyboard.
- 2026-11-13 ~8:45 PM Cairo (hour 7.8): Connected the full NASA PSI curated dataset (`2,003` real runs across `18` spaceflight PSI investigations) directly into an interactive **Evidence Strength Meter** (`backend/app/engine.py`, `frontend/dist/app.js`, `index.html`, `styles.css`): shows `Whole-Habitat Evidence Strength` (0–100) + `Atmosphere-Only Bound (0g)` (0–100), exact NASA test & measured-run counts backing the result, 4-pillar formula breakdown (`Proximity 35%`, `Reliability 30%`, `Test count 20%`, `Source quality 15%`), clickable PSI investigation chips & run drawers, and transparent `Not yet in PSI archive: SoFIE, FLARE, LUCI, FM2` status; also enabled public Vercel access (`ssoProtection: null`) on `https://flamelens-steel.vercel.app`.
- 2026-11-13 ~8:20 PM Cairo (hour 7.3): Completed analysis & dashboard integration of all remaining PSI combustion investigations (`PSI-21` ACME CLD 32 days, `PSI-22` ACME E-FIELD 20 days, `PSI-23` ACME s-Flame 23 days at ~21% & ~30% O2, `PSI-47` DAFT 2 sessions + 3 flight dust bags, `PSI-106` SLICE 12 days, `PSI-68` FLEX-2 8-fuel parameter matrix; `runs.csv` now 2,003 runs across 18 spaceflight PSIs, plus enriched BASS-II & Saffire outcomes). Built & wired `spread_rates.csv` (43 measured 0g spread/regression points from `NASA/TM-20210011385` Table 5.1 & `SAFFIRE-2` CSV -> new **Flame spread** lens + `/api/lens/spread`), `coolflame_notes.csv` (705–760 K cool flames, 85% O2, catalytic reignition), `bass2_airflow.csv` (20 fan calibration points), and `papers.csv` (27 NASA NTRS papers with PDF links). 67 backend tests passing.
- 2026-11-13 ~7:50 PM Cairo (hour 6.8): Laila: deploy. Redeployed to https://flamelens-steel.vercel.app from this laptop (Vercel CLI logged in as laila2005, project linked in `.vercel/`). Live now: AI panel with verifier, /api/explain, /api/verify, /api/modeling, cleaner-engines source fix. Added `.vercelignore` (uploads only the app; keeps `.env.local` and `data/raw` out). Redeploy: `vercel deploy --prod --yes` from the repo root. Still not linked to GitHub, so pushes do not deploy by themselves.

- 2026-11-13 ~7:30 PM Cairo (hour 6.5): Added the 5 official PSI ground/CFD predictive modeling studies (`PSI-60`, `PSI-62`, `PSI-115`, `PSI-117`, `PSI-142`) in `data/curated/modeling_studies.json`, exposed via `GET /api/modeling` and linked to their parent flight investigations (`BASS`, `BASS-II`, `SPICE`, `SAME`, `FLEX`) in `profiles.py`, Investigation Details, and the "Use the data & predictive modeling" dashboard panel without mixing CFD simulations into `runs.csv`. Checked `PSI-68` (`FLEX-2`): confirmed 0 non-media report files exist in PSI beyond the 1 KB planned matrix CSV and 48 publication citations.

- 2026-11-13 ~4 PM Cairo: Laila: drop Vercel redeploys for now. The live URL still serves the 1:51 PM build (no AI panel). Vercel CLI 65.15.0 is installed on this laptop but not logged in. Run locally with `python -m uvicorn backend.app.main:app --port 8000` (serves dashboard + API at http://localhost:8000). Decide hosting for the final submission before hour 17 (links must be public).

- 2026-11-13 ~3:30 PM Cairo (hour 2.5): AI part built (challenge asks for "SI-powered"): `backend/app/explain.py` (retrieval from the engine, citation verifier, template fallback, optional OpenAI-compatible model), `POST /api/explain`, `POST /api/verify`, `scripts/build_explanations.py`, dashboard panel "What the evidence says", 9 new tests (64 pass). No model downloaded (Laila: not now), so the panel shows the verified template until Dai pushes `data/curated/explanations.json`. Fixed verdict subtitle bug (0 g, no match showed the wrong line). Laila confirmed: auto commit and push (rule 5). Vercel CLI is not installed on this laptop, so this push is NOT yet on the live site.

- 2026-11-13 afternoon: LIVE at https://flamelens-steel.vercel.app (Vercel project flamelens, team laila-mohameds-projects; not linked to GitHub, redeploy with `vercel deploy --prod --yes`). Dashboard is static HTML/JS in frontend/dist (no build step, works offline). Added: ranker missing values = neutral 0.5; early-detection simulator tab (illustration) + /api/detect/evidence (real BASS-II CO/CO2, SAME-R/DAFT sizes, cool flames). 49 tests.

- 2026-11-13: backend pushed (0417f6a): FastAPI engine, /api routes, lens data, Dockerfile, render.yaml, mock JSON, 47 tests. Laila: commit and push automatically from now on (rule 5).

- 2026-11-13 hackathon day: user approved downloading. Fetched all 26 PSI Experimental Tables + 13 small documents; built `data/curated/runs.csv` (1,922 runs, 13 investigations, basis columns for each condition), `investigations.csv` (DOIs), `smoke_dust_sizes.csv` (SAME-R Table 1 + DAFT). Findings and gaps in `docs/research/dashboard-data-map.md`. Lens 1 (spread rate vs airflow) has no table data: replace with a tested-conditions scatter. Lunar rover 34% O2 / 10.2 psi / solid has 0 matching runs. Scripts: `scripts/fetch_psi.py`, `fetch_psi_docs.py`, `build_runs.py`.

- 2026-11-13 12:55 Cairo: opened the real PSI site. Every flight combustion investigation has an Experimental Table CSV (19 of them), PSI has an unofficial JSON backend, license CC0, cite DOIs. BASS-II oxygen is about 22% or below, pressure is per investigation, airflow is display codes. CFI, SAME-R, DAFT-2, ACME E-FIELD are all in PSI. Full notes: `docs/research/psi-real-findings.md`. Nothing downloaded yet.

- 2026-11-13 12:35 Cairo: added `docs/13-start-now.md` (resource summary, reading assignments per person, first-hour plan, decisions to make). Hackathon starts 1:00 PM.

- 2026-11-13 (hackathon day, 8:30 AM Cairo when written; hackathon starts 1:00 PM): NASA shared the official resource list; added to `docs/12-resources.md` section 0. PSI combustion search is the data source. Spin-off text must come from the three NASA spin-off pages. Investigation list re-checked against NASA's Combustion Science page: CFI, SAME-R, DAFT-2, ACME E-FIELD still unverified.

- 2026-11-09: Web research added as `docs/12-resources.md`. Our challenge is "Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data". PSI has no documented API (manual downloads), NTRS API works for papers, AWS bucket `nasa-psi` may not hold combustion data. The official challenge page was NOT read (certificate error in the research tool): F must read it and paste the statement into docs/12. If it expects an AI component, move the cited AI explanation to Must ship.

- 2026-11-09: Read the two official PDFs (Hackathon Guide, Participant Guidebook). Key facts: the event is 24 hours not 48, no pre-event code, demo is 7 slides or 30-second video, only the leader submits. Rescaled timeline, scope, role schedules (EN and AR) and submission docs; added `docs/11-event-facts.md`. Names added: Laila A, Yousseif B, Yasmine C, Judy D.

- 2026-11-09: Repo initialised with the full documentation set, bilingual role tasks, TASKS.md, scaffold and placeholder data (commit `2145bb7`, pushed to `main`). Added this CLAUDE.md.
- 2026-11-09: Brainstorm doc `docs/10-idea-brainstorm.md` added; evidence strength made Must ship; campaign planner and atmosphere journey are the default Should-ship picks.
- 2026-11-06: Dashboard mockup got Evidence case, Run this next and Safer options tabs; master plan artifact updated with the "What makes FlameLens different" section.
- 2026-11-05: Planning artifacts created (plan, prep checklist, explainer, team split, model guide, dashboard mockup) after the team shared the FlameLens idea.
