# Prep schedule: Mon 9 Nov to kickoff Fri 13 Nov

Four days. Every task has an owner, a due day and a "done when". The full lists with detail are in each [role file](roles). The tick-box version for the whole team is in [../TASKS.md](../TASKS.md).

## Monday 9 Nov: set up and read

| Who | Task | Done when |
|---|---|---|
| All | Read [start here](00-START-HERE.md) and the [brief](01-project-brief.md) | You can explain FlameLens in two sentences |
| All | Accept repo invite, clone, run `python scripts/check_env.py` | No MISSING for your role |
| All | Pick a role and backup in [02](02-team-roles.md), post availability for 13–14 Nov | Table filled in |
| A | Give all 6 members write access, enable Issues, create labels, turn on branch protection for `main` | Everyone can open a pull request |
| F | Find the official challenge page. Write down deadline, video length, required fields, team size rule, rules on pre-event code | [Rule notes](09-pitch-and-submission.md#facts-to-confirm-f-fills-these-in) filled in |
| D, F | Start reading investigations: D takes BASS, BASS-II, Saffire, SPICE, BRE. F takes SAME, SAME-R, DAFT, DAFT-2, FLEX, CFI | One research note started each |

## Tuesday 10 Nov: design and research

| Who | Task | Done when |
|---|---|---|
| F | Ask organizers if pre-event code is allowed (use the message in [working agreements](08-working-agreements.md#rule-check-before-writing-code)) | Message sent, answer recorded |
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

## Friday 13 Nov: kickoff (hour 0)

Follow the hour 0–2 plan in [04 Hackathon timeline](04-hackathon-timeline.md). Summary:

- [ ] A creates the working branch structure, confirms the API contract
- [ ] D and F open every PSI file and report which fields really exist
- [ ] A and D compare the real fields with the [schema](06-data-guide.md), change the schema now if needed
- [ ] Everyone else starts on the placeholder data in `data/mock/`
- [ ] F writes the real deadline and submission time at the top of the chat

## Prep that is allowed before kickoff

Research, notes, designs, documents, accounts, tool installs, local model tests, placeholder data and rehearsal are safe. Writing product code is not safe until the organizers confirm. See [working agreements](08-working-agreements.md#rule-check-before-writing-code).

Note: the weekday labels above are calculated for 2026 (13 Nov is a Friday). If the official schedule says otherwise, trust the official one and update this page.
