# Project brief

## Problem

Spacecraft fire safety depends on experiments run on the ISS (BASS, Saffire, SAME, DAFT, FLEX, CFI and others). The data is public but hard to use: values live in tables, plots and papers, and each experiment varies different conditions. Engineers designing Moon and Mars habitats need to know which atmospheres are covered by evidence and which are not.

## Solution in one paragraph

FlameLens takes a habitat design and returns an evidence-backed decision: what is proven, what is not, what to test next, and what to change to be safer. A deterministic ranker scores experiments. Charts show the physics. AI explains in plain language but every claim must cite a real run, or a verifier removes it.

## What makes us different

Most teams will build search plus a ranked list plus an AI chat. We end with a decision:

- **Evidence case.** Supported, Weak or No evidence for oxygen, pressure, airflow, fuel, gravity, and the whole design together.
- **Run this next.** The experiment that closes the most gaps, with the nearest existing run as a starting point.
- **Safer options.** Nearest tested conditions with lower oxygen partial pressure, never extrapolated.
- **Honesty by design.** Placeholder, plot-read and low-confidence values are visibly labelled. The AI cannot fill a gap.

One-line pitch: *"Today an engineer spends days reading papers to answer one question. FlameLens answers it in a minute, shows which parts are proven, and tells you what to test next."*

## Going further than other teams

The ideas that make the dashboard smarter (evidence strength meter, test campaign planner, atmosphere journey, breathable-and-tested zone, plain-language entry, reverse search) are ranked by impact and effort in [10 Idea brainstorm](10-idea-brainstorm.md). The evidence strength meter is Must ship. At most two others are built before Gate 2.

## Users

Habitat and life-support engineers, fire-safety reviewers, students and educators. Tone: serious and clear, with an "Earth spin-off" note per investigation.

## Scope in three tiers (24-hour event)

**Must ship**
- Habitat picker with ISS, Lunar rover, Lunar base, Mars habitat presets plus custom values
- Ranker with score breakdown bars
- Evidence case, Run this next, Safer options
- Evidence strength meter (0–100 per condition, with its four parts shown)
- Coverage gap map and evidence trail (click any claim to see run, source, confidence)
- Lens 1 (airflow) and Lens 2 (smoke vs dust)
- "Sample data" banner while placeholder rows exist

**Should ship**
- Cited AI explanation with verifier badge
- Lens 3 (cool flames), diff view, CSV export
- One idea from [10 Idea brainstorm](10-idea-brainstorm.md) (default: campaign planner)

**Cut** (not in 24 hours)
- BOM auditor, Lens 4, free-text chat, shareable link, safety brief, atmosphere journey, plain-language entry, reverse search unless Gate 1 says there is room

If the real data is thin at hour 6, drop Lens 2 and Lens 3 and keep the decision panels.

## Non-goals

- No physics simulation. We explore *what the experiments showed*, not predict beyond them.
- No claim that is not sourced. If the data does not say it, we say "no evidence".
- No database server, no microservices, no three-agent AI. See [architecture](05-architecture-and-api.md).

## Biggest risks

| Risk | Plan |
|---|---|
| Dataset arrives at kickoff and is messier than expected | Two data extractors, placeholder data, 2 hours at kickoff to confirm the schema |
| Not enough usable runs for a lens | Cut that lens or show a cited summary. Two strong lenses beat three weak ones |
| AI invents a number | Verifier rejects it. App works with AI off |
| Scope creep | Gates at hours 6 and 13, feature freeze at hour 17 (24-hour event) |
| Code written before kickoff breaks the rules | **Confirmed forbidden** by the official guide. No product code before Fri 1:00 PM. Docs and plans only |

## Open decisions (owner: tech lead unless stated)

- [ ] Final role assignment and backups (whole team, by 10 Nov)
- [ ] Hosting: Render or Fly (A, by 11 Nov)
- [ ] LLM provider: local Ollama or hosted open model (E, by 11 Nov, see [AI guide](07-ai-guide.md))
- [ ] Repo license (whole team, before going public)
- [x] Pre-event code: not allowed (see [11 Event facts](11-event-facts.md))
- [ ] Team leader who submits, and which 5 are onsite (team, by 12 Nov)
