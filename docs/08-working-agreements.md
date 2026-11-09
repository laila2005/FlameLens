# Working agreements

How we work together so six people do not trip over each other.

## Rule check before writing code

**Answered by the official guide (see [11 Event facts](11-event-facts.md)):** preparing the general plan and splitting tasks before the hackathon is allowed, but **presenting ready or half-finished projects is completely prohibited, and actual work starts at the hackathon start (Fri 13 Nov, 1:00 PM Cairo).**

- **Allowed now:** reading, research notes, plans, task lists, designs on paper, accounts, tool installs, rehearsal, and placeholder data for layout.
- **Not allowed until Fri 1:00 PM:** product code in this repo (loader, ranker, API, UI, charts) or anything that looks like a built project.
- **Practice code** (a Plotly test, a hello-world deploy, an Ollama test) is learning, not the project. Keep it **outside this repo**, delete it afterwards, and never reuse it in the hackathon.
- **The interactive dashboard mockup** made during planning is a design sketch. Do not reuse its code, do not present it as a built product, and rebuild everything from scratch after 1:00 PM. If unsure, ask a mentor on Friday.

If the organizers announce something different on Discord, follow the announcement and update this page.

## Branches and pull requests (once coding is allowed)

- `main` is always working and deployable. Only A and the backup merge into it.
- Branch names: `role/short-task`, e.g. `c/lens-ventilation`, `d/data-prevention-batch1`.
- Keep branches small: under half a day of work. Merge often.
- Every merge goes through a pull request using the [template](../.github/PULL_REQUEST_TEMPLATE.md). One reviewer from the pair is enough. Reviews take minutes, not hours.
- During the hackathon, if a review would block someone for more than 20 minutes, A can merge after a quick check.
- Never force-push to `main`.
- Commit messages: short, present tense, e.g. `Add airflow lens on mock data`.

## Tasks

- Each task is a GitHub issue created from the [task template](../.github/ISSUE_TEMPLATE/task.md), with one owner and a "done when".
- Labels: `role:A` to `role:F`, `must`, `should`, `stretch`, `data`, `bug`, `blocked`.
- A task is **done** only when its "done when" is true and a teammate has seen it work.
- Pre-event, tasks are tracked in [../TASKS.md](../TASKS.md).

## Definition of done for features

- Works on the deployed URL, not only on your laptop
- Works on placeholder data and real data
- No number on screen without a source or an obvious label
- Empty and loading states exist
- Looks fine at phone width

## Communication

- One team chat for everything. Use threads.
- Post blockers immediately. "Blocked on X" is useful. Silence is not.
- Pairs sync at least every 2 hours during the event.
- Stand-ups at hours 0, 6, 13, 17 (10 minutes): done, doing, blocked.
- Decisions go in the chat and, if lasting, in these docs.

## Health and sleep

- A schedules sleep shifts. Never everyone asleep at once.
- Everyone sleeps at least 4–5 hours across the event. Tired people write bugs.
- Food, water and breaks are part of the plan.

## Scope control

- Gate 1 (hour 6): vertical slice runs. Gate 2 (hour 13): all "Must ship" works.
- New ideas go in the chat as `idea:` and are only considered at a gate.
- **Feature freeze at hour 17 (6:00 AM Saturday).** After that, bug fixes only. Submit at hour 21 (10:00 AM).

## Secrets

- Never commit API keys or tokens. Use `.env` (git-ignored). Share keys privately.
- Copy `.env.example` to `.env` and fill it in.

## Respect the data

- Never invent or round a scientific value.
- If unsure about a claim, tag it and ask F. F decides whether it ships.
