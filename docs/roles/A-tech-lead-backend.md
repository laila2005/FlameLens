# Role A: Tech lead and backend

**Name:** ______  **Backup:** ______  **Pairs with:** E

## Your job in one sentence

Keep the repo healthy and the backend correct, so six people can work in parallel without collisions, and make sure the app is deployed and working at hour 10, 24 and 40.

**العربية:** [النسخة العربية](ar/A-tech-lead-backend.md) · [Choose your role](00-choose-your-role.md)

## Experience needed

| | |
|---|---|
| **Required** | Python you can write and test, git and pull requests (including fixing merge conflicts), basic REST APIs |
| **Nice to have** | FastAPI or Flask, SQL and SQLite, Docker, deploying an app |
| **Learn in 2 days** | FastAPI basics, deploying on Render or Fly |
| **Personal fit** | Calm under pressure, decisive, likes unblocking people |

## You own

Repo settings and merges, FastAPI, the ranker, the decision routes (`/case`, `/next`, `/alternatives`, `/strength`, `/campaign`, `/journey`), the data loader, deployment, stand-ups and sleep shifts.

## Before the hackathon

Each task has a number. Tick it in [../../TASKS.md](../../TASKS.md) when done.

### A1. Repo access and settings (Mon 9 Nov, 30 min)
Steps:
1. GitHub repo, Settings, Collaborators: invite all five teammates with write access.
2. Settings, General: make sure Issues are on and the default branch is `main`.
3. Settings, Branches: add a rule for `main`: require a pull request before merging, allow admins to bypass.
Done when: a teammate can push a branch and open a pull request.

### A2. Labels (Mon 9 Nov, 15 min)
Create these labels, copy the commands if you use the GitHub CLI:
```bash
for l in role:A role:B role:C role:D role:E role:F must should stretch data bug blocked idea; do gh label create "$l" --repo laila2005/FlameLens 2>/dev/null; done
```
Done when: the labels exist on the Issues page.

### A3. Toolchain check (Mon 9 Nov, 15 min)
Run `python scripts/check_env.py`. You need Python 3.11+, Node 20+, git, and ideally Docker. Fix anything marked MISSING.
Done when: all REQUIRED lines say OK.

### A4. Choose hosting (Tue 10 Nov, 1 hour)
Compare Render and Fly (free tier, container support, cold start, how long a deploy takes). Pick one, create the account, write the choice and the reason in the **Decisions** section at the bottom of this file.
Done when: you can log in and the decision is written here.

### A5. Throwaway deploy test (Wed 11 Nov, 90 min)
Deploy a FastAPI hello-world with one static page from a **separate private repo** (for example `flamelens-deploy-test`, NOT this repo, because of the [rule check](../08-working-agreements.md#rule-check-before-writing-code)). Write the exact commands and settings into the **Deploy notes** section below so the backup can repeat it.
Done when: the public URL loads on your phone, and the steps are written down.

### A6. Ranker test cases on paper (Wed 11 Nov, 90 min)
In `docs/design/ranker-cases.md` write 5 hand-checked cases using the weights in [05](../05-architecture-and-api.md#ranker). Each case: the habitat, one run, each factor's closeness, the final score computed by hand. Include one case with a missing field (weights rescale) and one with no fuel match.
Done when: a teammate recomputes two cases and gets the same numbers.

### A7. Decision-route test cases on paper (Wed 11 Nov, 60 min)
In `docs/design/decision-cases.md` write 5 cases using `data/mock/runs_placeholder.csv`: for each, a habitat and the expected `/case` statuses, `/next` recommendation, `/alternatives` list and evidence strength (formula in [10](../10-idea-brainstorm.md#1-evidence-strength-meter-must)).
Done when: the cases cover a covered habitat, a partly covered habitat and a habitat with no evidence.

### A8. Kickoff pack (Thu 12 Nov, 45 min)
Prepare: the hour 0–2 checklist from [03](../03-prep-schedule.md), the stand-up times, a draft sleep-shift table (everyone covered, never all asleep), and the chat channel list (general, data, blockers).
Done when: you can paste all of it into the chat at the kickoff meeting.

### A9. Readiness check (Thu 12 Nov, 30 min)
Ask each member for: roles filled in, check_env passing, availability posted. List blockers.
Done when: you have a "ready" or "blocked, because X" for each of the six.

## At the hackathon

| Hour | You do |
|---|---|
| 0–2 | Confirm rules, agree the API contract, create branches, read the real field list from D and F, update the schema |
| 2–10 | Loader, SQLite, ranker with the 5 tests, `/rank`, mock JSON for every route |
| 10 | **Gate 1:** run the vertical slice, then choose up to two brainstorm ideas with the team |
| 10–24 | `/case`, `/next`, `/alternatives`, `/strength`, then `/campaign`, `/journey`, tune tolerances on real data |
| 24 | **Gate 2:** all "Must ship" works on the deployed URL |
| 24–40 | Merge bug fixes, deploy daily, run sleep shifts |
| 40 | Freeze and tag the release |
| 40–48 | Check repo, deploy, secrets, and help F submit |

## Hand-offs

| You give | To | When |
|---|---|---|
| API contract and mock JSON | B, C | Hour 1–2 |
| Running `/rank` and `/case` | B, C | Hour 10 |
| Loader that reads D's CSV | D | Hour 6 |
| Deployed URL | F | Hour 24 |

## If you are stuck or unavailable

The backup merges and deploys using the notes below.

## Deploy notes (fill in at A5)

_commands and settings here_

## Decisions

| Decision | Choice | Reason | Date |
|---|---|---|---|
| Hosting | | | |
