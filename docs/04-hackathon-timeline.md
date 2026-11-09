# Hackathon timeline (48 hours)

Hours count from kickoff. Replace with clock times once the official schedule is known. Targets: build done by hour 36, **feature freeze at hour 40**, submit at least 3 hours before the deadline.

## Hour 0–2: Kickoff, lock the contract

- Confirm challenge rules, deadline, submission format.
- Create working branches, confirm the [API contract](05-architecture-and-api.md).
- D and F open every PSI investigation file and report which fields really exist. Compare against the [schema](06-data-guide.md) and change the schema now if it differs.
- Everyone else starts on `data/mock/runs_placeholder.csv`.

## Hour 2–10: Foundations (parallel)

| Role | Work |
|---|---|
| A | Loader, SQLite, ranker with 5 unit tests, `/rank` live |
| B | App shell, habitat picker, ranked cards on mock data |
| C | Lens 1 chart on mock data, start coverage map |
| D + F | First 20 real runs entered, shared in batches every 2 hours |
| E | Chunk documents, retriever working, first pillar prompt |
| F | Claim fact-check list, README skeleton, slide outline |

## Hour 10: Gate 1, vertical slice

Pick a habitat, see ranked **real** cards on the deployed or local app. If not, stop adding features and fix integration.

If the slice works, choose **at most two** ideas from [10 Idea brainstorm](10-idea-brainstorm.md) (campaign planner and atmosphere journey are the default picks). Ask the three questions at the end of that doc for each.

## Hour 10–24: Features

| Role | Work |
|---|---|
| A + C | `/case`, `/next`, `/alternatives` and their panels (hours 10–18, they carry the pitch). Tune tolerances on real data |
| C | Lens 2 and Lens 3 on real data |
| E | Verifier, `/explain`, cache answers for demo cases |
| A + B | Diff endpoint and view, CSV export, weight sliders |
| D | Grow to 40–80 runs, fill confidence and sources |
| F | Start screen capture, test pass 1 |

## Hour 24: Gate 2, feature-complete core

Everything in "Must ship" works on the deployed URL. Decide as a team whether stretch work starts. Sleep in shifts from here, never everyone at once.

## Hour 24–36: Harden

- Fix bugs from F's checklist, empty states, loading states, mobile layout.
- Stretch (BOM auditor, Lens 4) only if Gate 2 was early and calm.
- Slides and demo video drafted with the existing FlameLens branding.

## Hour 36–40: Freeze

**Feature freeze at hour 40.** After this, bug fixes only. Tag a release. Record the demo video against the tagged build.

## Hour 40–48: Submit

The buffer is for submission, not for features. Final video, README, project text, links, team names, repo public. Submit at least 3 hours before the deadline. Check the official deadline and format.

## Daily stand-ups (15 minutes)

Hour 0 (kickoff), hour 10 (Gate 1), hour 24 (Gate 2), hour 36 (freeze plan). Each person answers: done, doing, blocked.
