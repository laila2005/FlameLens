# Prep schedule: Mon 9 Nov to kickoff Fri 13 Nov

Four days. Every task has an owner, a due day and a "done when". The full lists with detail are in each [role file](roles). The tick-box version for the whole team is in [../TASKS.md](../TASKS.md).

## Monday 9 Nov: set up and read

| Who | Task | Done when |
|---|---|---|
| All | Read [start here](00-START-HERE.md) and the [brief](01-project-brief.md) | You can explain FlameLens in two sentences |
| All | Accept repo invite, clone, run `python scripts/check_env.py` | No MISSING for your role |
| All | Pick a role and backup in [02](02-team-roles.md), post availability for 13–14 Nov | Table filled in |
| A | Give all 6 members write access, enable Issues, create labels, turn on branch protection for `main` | Everyone can open a pull request |
| F | Find the official challenge page. Check the facts in [11 Event facts](11-event-facts.md) against the official site, fill gaps (final deadline, NASA submission steps, licence) | [Facts table](09-pitch-and-submission.md#facts-filled-in-from-the-official-pdfs-9-nov) matches the official site |
| D, F | Start reading investigations: D takes BASS, BASS-II, Saffire, SPICE, BRE. F takes SAME, SAME-R, DAFT, DAFT-2, FLEX, CFI | One research note started each |

## Tuesday 10 Nov: design and research

| Who | Task | Done when |
|---|---|---|
| F | Settle the open questions in [11 Event facts](11-event-facts.md#open-questions-to-settle): who is the team leader who submits, which 5 are onsite, are all members 18 or over for the demo. (The code question is already answered: no code before the hackathon.) | Answers in the chat |
| B, C | Design screens on paper or Figma from the [mockup](links.md): picker, ranked list, evidence case, lens page, diff | Sketches in `docs/design/` |
| D | Finish research notes for Prevention investigations, test the extraction template on one paper | 5 notes in `docs/research/` |
| F | Finish research notes for Detection and Suppression | 6 notes in `docs/research/` |
| E | Draft the three pillar prompts and verifier rules on paper | Drafts in [07](07-ai-guide.md) |
| A | Choose hosting, create the account | Account works |

## Wednesday 11 Nov: tooling and test runs

| Who | Task | Done when |
|---|---|---|
| A | Deploy a throwaway hello-world to the hosting service from a **separate private repo** | Public URL works, steps written in A's file |
| E | Install Ollama, run the 20-question bake-off on 2 models | Results table filled in [07](07-ai-guide.md) |
| D | Write the data-entry guide examples, agree units with F | [06](06-data-guide.md) reviewed by F |
| C | Sketch each lens with sample numbers, write the coverage and evidence-case spec | Specs in `docs/design/` |
| B | Component list and layout notes | `docs/design/components.md` |
| F | Fact-check list: every scientific claim we plan to show, each with a source | Claims table in `docs/research/claims.md` |
| F | Draft pitch outline and demo script | Drafts in [09](09-pitch-and-submission.md) |

## Thursday 12 Nov: rehearse and rest

| Who | Task | Done when |
|---|---|---|
| All | Kickoff meeting (30–45 min): confirm roles, review [timeline](04-hackathon-timeline.md), agree channels | Everyone knows their first 2 hours |
| A | Print or share the kickoff checklist below | Everyone has it |
| All | Sleep, charge laptops, pack food and chargers. Do not work late | Rested |
| F | Confirm event logistics: venue or online link, time zone, check-in | Written in chat |

## Friday 13 Nov: kickoff (hour 0 is 1:00 PM Cairo time)

| Clock | What happens |
|---|---|
| By 8:00 AM (onsite) | Arrive at SUT with national ID, laptop, charger, backup internet, sleeping bag. Registration from 9:00 AM (the guides differ, so arrive by 8:00 AM) |
| 10:00 AM | Virtual members join |
| 1:00 PM | **Hackathon begins.** Follow the hour 0–1 plan in [04 Hackathon timeline](04-hackathon-timeline.md) |
| 2:00 PM | Mentorship begins on Discord |

- [ ] A agrees the API contract and mock JSON
- [ ] D and F open every PSI file and report which fields really exist
- [ ] A and D compare the real fields with the [schema](06-data-guide.md), change it now if needed
- [ ] Everyone else starts on the placeholder data in `data/mock/`
- [ ] F writes the real deadline and the "submit by 10:00 AM" time at the top of the chat

## Prep that is allowed before kickoff

Allowed: reading, research notes, plans, task splits, designs on paper, accounts, tool installs, rehearsal, placeholder data for layout.
**Not allowed:** product code, or a "ready or half-finished project". The official guide says actual work starts at the hackathon start. Throwaway practice (Plotly, deploy test, Ollama) stays outside this repo and is never reused. See [08](08-working-agreements.md#rule-check-before-writing-code).

Weekday labels are checked: 13 Nov 2026 is a Friday.
