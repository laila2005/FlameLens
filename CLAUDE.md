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
- Roles named so far: A Laila (repo owner), B Yousseif, C Yasmine, D Judy (backup F). E tentatively Dai (confirming), F open: Mostafa is choosing and has not confirmed. Backups, hosting, LLM choice, repo licence, team leader who submits, which 5 are onsite: undecided (see "Open decisions" in `TASKS.md`).
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
