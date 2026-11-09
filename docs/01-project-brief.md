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

## Scope in three tiers

**Must ship**
- Habitat selector: ISS, Lunar rover, Lunar base, Mars habitat, plus custom values
- Ranker with score breakdown and adjustable weights
- Investigation cards with pillar, hardware, key runs, source link
- Evidence case, Run this next, Safer options
- Evidence strength meter (0–100 per condition, with its four parts shown)
- Coverage gap map
- Evidence trail: click any claim to see run, source, page, confidence
- Lens 1 airflow, Lens 2 smoke vs dust, Lens 3 cool flames
- Cited AI explanation with verifier badge
- Diff view for two investigations

**Should ship**
- Confidence badge on every number
- Test campaign planner ("these 3 experiments cover the most designs")
- Atmosphere journey (evidence for each stage of a mission)
- Plain-language habitat entry, reverse search
- Habitat safety brief (one-click report)
- Compare two atmospheres
- "Explain simply" toggle, Artemis-style presets
- Earth spin-off text, CSV export, offline demo mode with cached AI answers

**Stretch (only if ahead at hour 24)**
- BOM cabin auditor, Lens 4 exploratory, free-text question box, shareable link

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
| Scope creep | Gates at hours 10 and 24, feature freeze at hour 40 |
| Code written before kickoff breaks rules | Ask organizers. Until answered, no product code in this repo |

## Open decisions (owner: tech lead unless stated)

- [ ] Final role assignment and backups (whole team, by 10 Nov)
- [ ] Hosting: Render or Fly (A, by 11 Nov)
- [ ] LLM provider: local Ollama or hosted open model (E, by 11 Nov, see [AI guide](07-ai-guide.md))
- [ ] Repo license (whole team, before going public)
- [ ] Whether pre-event code is allowed (F, ask by 10 Nov)
