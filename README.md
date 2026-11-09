# FlameLens

**Space-fire data, made clear.** Team AstroSpark, NASA Space Apps Challenge 2026, Cairo. **24 hours: Fri 13 Nov 1:00 PM to Sat 14 Nov 1:00 PM (Cairo time).**

FlameLens helps spacecraft and habitat engineers use NASA's Physical Sciences Informatics (PSI) fire-safety experiments. An engineer enters a habitat design (oxygen, pressure, airflow, fuel, gravity) and gets a decision they can defend, not just a list of search results:

1. **Evidence case.** Which parts of the design are backed by experiments, which are weak, and which have no evidence. Every line points at real run IDs.
2. **Run this next.** The one experiment that would remove the most uncertainty, and the cheapest first step to get there.
3. **Safer options.** The nearest *tested* conditions with less oxygen, and what to change to reach them.

A deterministic ranker scores the experiments. AI only explains, and a citation verifier removes any claim that does not point at a real run.

## New here? Start with this

1. Read [docs/00-START-HERE.md](docs/00-START-HERE.md) (10 minutes).
2. Pick a role with [Choose your role / اختر دورك](docs/roles/00-choose-your-role.md), write your name in [docs/02-team-roles.md](docs/02-team-roles.md), and open your task file in [docs/roles/](docs/roles) (Arabic: [docs/roles/ar/](docs/roles/ar)).
3. Run the environment check: `python scripts/check_env.py`
4. Tick off your tasks. The whole team's status is in [TASKS.md](TASKS.md).

## Documentation map

| Doc | What it answers |
|---|---|
| [00 Start here](docs/00-START-HERE.md) | What we are building and what to do first |
| [01 Project brief](docs/01-project-brief.md) | Problem, solution, what makes us different, scope |
| [02 Team roles](docs/02-team-roles.md) | Who owns what, who pairs with whom |
| [03 Prep schedule](docs/03-prep-schedule.md) | Day-by-day plan from 9 Nov to kickoff |
| [04 Hackathon timeline](docs/04-hackathon-timeline.md) | Hour-by-hour plan for the 24-hour event |
| [05 Architecture and API](docs/05-architecture-and-api.md) | Stack, API contract, ranker, decision routes |
| [06 Data guide](docs/06-data-guide.md) | Row format, extraction rules, placeholder rules |
| [07 AI guide](docs/07-ai-guide.md) | Model choice, guardrails, verifier, bake-off |
| [08 Working agreements](docs/08-working-agreements.md) | Git flow, reviews, communication, rule check |
| [09 Pitch and submission](docs/09-pitch-and-submission.md) | Demo script, QA checklist, submission checklist |
| [11 Event facts](docs/11-event-facts.md) | Official dates, rules, submission format and judging criteria from the organizers' guides |
| [10 Idea brainstorm](docs/10-idea-brainstorm.md) | How we make the dashboard smarter than other teams, ranked by impact and effort |
| [Choose your role / اختر دورك](docs/roles/00-choose-your-role.md) | Experience needed for each role, so you can pick the one that fits you (English and Arabic) |
| [Role task files](docs/roles) · [بالعربية](docs/roles/ar) | Each member's tasks before and during the hackathon, in English and Arabic |
| [TASKS.md](TASKS.md) | One checklist for the whole team, in English and Arabic |
| [Links](docs/links.md) | Interactive plan, mockup, explainer (private pages) |

## Repository layout

```
docs/            All documentation (read in numbered order)
docs/roles/      One task file per role, A to F
docs/research/   One-page summaries of each PSI investigation (role D and F fill these in)
data/mock/       Placeholder data in our row format (never shown as real)
data/raw/        Real PSI downloads go here at kickoff (git-ignored)
scripts/         Small helper scripts (environment check)
.github/         Issue and pull request templates
```

## Ground rules in one minute

- No scientific number or claim goes in the UI without a source. See [data guide](docs/06-data-guide.md).
- Placeholder data is always labelled "sample data" in the UI.
- Work in small branches, merge through pull requests. See [working agreements](docs/08-working-agreements.md).
- **No product code before the hackathon starts (Fri 13 Nov, 1:00 PM Cairo).** The official guide forbids presenting ready or half-finished projects. Docs and plans are fine.

## License

Not chosen yet. Decide as a team before the repo goes public (see [pitch and submission](docs/09-pitch-and-submission.md)).
