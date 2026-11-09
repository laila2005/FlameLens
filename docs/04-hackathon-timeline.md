# Hackathon timeline (24 hours)

**Hour 0 = Friday 13 Nov, 1:00 PM Cairo time. Deadline = Saturday 14 Nov, 1:00 PM (hour 24).** Official facts: [11 Event facts](11-event-facts.md). Nothing is built before hour 0.

Targets: feature freeze at hour 17 (6:00 AM Sat), **submit at hour 21 (10:00 AM)**, hours 21–24 are buffer only.

With 24 hours and 6 people, scope is cut to the bone. See "Scope for 24 hours" at the end.

## Clock

| Hour | Clock (Cairo) | Milestone |
|---|---|---|
| 0 | Fri 1:00 PM | Hackathon begins |
| 1 | Fri 2:00 PM | Mentorship begins |
| 6 | Fri 7:00 PM | **Gate 1:** vertical slice runs |
| 13 | Sat 2:00 AM | **Gate 2:** all "Must ship" works on the deployed URL |
| 15 | Sat 4:00 AM | Data freeze, AI cache ready |
| 17 | Sat 6:00 AM | **Feature freeze**, tag the release |
| 21 | Sat 10:00 AM | **Submit** (local form and NASA site) |
| 24 | Sat 1:00 PM | Deadline |

## Hour 0–1: Kickoff, lock the contract

- F confirms the deadline on Discord and writes it at the top of the chat.
- A agrees the [API contract](05-architecture-and-api.md) and mock JSON.
- D and F open every PSI file and fill the field inventory. If the real fields differ from the [schema](06-data-guide.md), change the schema **now** and tell A.
- Everyone else starts from `data/mock/runs_placeholder.csv`.
- Join the mentorship channel on Discord. Ask one mentor to sanity-check the idea if useful.

## Hour 1–6: Foundations (parallel)

| Role | Work |
|---|---|
| A | Loader, SQLite, ranker with 5 tests, `/rank` and `/case` live |
| B | App shell, habitat picker, ranked cards on mock data |
| C | Lens 1 on mock data, start the coverage map |
| D + F | First 15–20 real runs entered, batches every 2 hours |
| E | Chunk documents, retriever, first pillar prompt. Help D if data is thin |

## Hour 6: Gate 1, vertical slice

Pick a habitat, see ranked **real** cards. If not, stop adding features and fix integration. If it works, choose **at most one** idea from [10 Idea brainstorm](10-idea-brainstorm.md) (default: campaign planner). Ask the three questions at the end of that doc.

## Hour 6–13: Features

| Role | Work |
|---|---|
| A | `/next`, `/alternatives`, `/strength`, tune tolerances on real data, first deploy |
| B | Evidence case, Run this next, Safer options, strength meter, sample banner, evidence panel |
| C | Coverage map on real data, strength gauges, Lens 2 |
| D | Grow to 30–40 runs with sources and confidence |
| E | Verifier, `/explain`, answer cache for the demo habitats |
| F | Slide outline, 30-second video storyboard, test pass 1, README skeleton |

## Hour 13: Gate 2, core complete

Everything in "Must ship" works on the deployed URL. Sleep shifts start: nobody works more than about 16 hours straight, and never everyone asleep at once. Venue note: rest rooms exist but no beds. Bring a sleeping bag.

## Hour 13–17: Harden

- Fix bugs from F's checklist, empty and loading states, phone layout.
- Screen captures and screenshots for the demo.
- Lens 3 and the chosen idea only if Gate 2 was calm.
- Data freeze at hour 15 (D). AI cache ready at hour 15 (E).

## Hour 17: Feature freeze

Bug fixes only. A tags a release. The deployed app is the tagged build.

## Hour 17–21: Demo and submission pack

- F records the **30-second video** or finishes the **7 slides** against the tagged build (no faces or voices of anyone under 18).
- F writes the project summary and the resources list. The README lists data sources, tools and the **AI-use disclosure**.
- A checks the repo is public, no secrets, the deployed URL works, every link opens without login in a private window.
- QA: one last pass of the [QA checklist](09-pitch-and-submission.md#qa-checklist-f-tests-someone-who-did-not-write-the-code).

## Hour 21: Submit

Only the team leader submits. Submit to the local form first, then upload the same files on the official NASA Space Apps site. Save screenshots of both confirmations. Late submissions are not accepted and nothing can change after submission, so use hours 21–24 only for problems like a broken link or lost connection (use the backup connection).

## Stand-ups (10 minutes)

Hours 0, 6, 13, 17. Each person: done, doing, blocked.

## Scope for 24 hours

| Tier | Contents |
|---|---|
| **Must ship** | Habitat picker, ranker with score bars, Evidence case, Run this next, Safer options, Evidence strength meter, coverage gap map, evidence trail, Lens 1 (airflow), Lens 2 (smoke vs dust), sample-data banner |
| **Should ship** | Cited AI explanation with verifier, Lens 3, diff view, one brainstorm idea, CSV export |
| **Cut** | BOM auditor, Lens 4, free-text chat, shareable link, safety brief, journey (unless Gate 1 says otherwise) |

If the real data turns out thin by hour 6, cut Lens 2 and Lens 3 and keep the decision panels. Data targets: 15–20 runs by hour 6, 30–40 by hour 13.
