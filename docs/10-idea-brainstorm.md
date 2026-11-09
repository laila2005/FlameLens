# Idea brainstorm: making the dashboard smarter

Goal: stand out from other teams, who will mostly build search + ranked list + AI chat. Nobody can guarantee a win. What we can do is pick ideas that (a) judges can see in 30 seconds, (b) stay honest, (c) fit in 48 hours with a team of six.

Read [01 Project brief](01-project-brief.md) first. Everything here builds on the Evidence case, Run this next and Safer options.

## The principle behind every idea

**Engineers do not need more answers. They need to know how much to trust an answer and what to do about it.** Smart = uncertainty made visible and actionable, not more AI.

Rules for any idea we adopt:
1. It must work from the run table alone (no new data sources).
2. It must not claim anything the data does not show. "No evidence" is a valid output.
3. It must be demoable in under 30 seconds.
4. The decision logic is deterministic. AI may only parse or explain.

## Ideas, ranked

Effort: S = under 3 hours, M = 3–8 hours, L = over 8 hours (one person). Impact on judges: ★ to ★★★.

| # | Idea | What the user sees | Effort | Impact | Verdict |
|---|---|---|---|---|---|
| 1 | **Evidence strength meter** | One 0–100 gauge per condition and for the whole habitat, with a breakdown (how close, how reliable, how many runs, where values came from) | S | ★★★ | **Adopt (Must)** |
| 2 | **Test campaign planner** | "You can afford 3 experiments. Run these 3 to cover the most designs." A ranked list with "gaps closed" for each | M | ★★★ | **Adopt (Should, build early)** |
| 3 | **Atmosphere journey** | A mission is a sequence of atmospheres (cabin, airlock campout, rover). Shows the evidence for every stage and highlights the weakest stage | M | ★★★ | **Adopt (Should)** |
| 4 | **Breathable and tested zone** | Map of pressure vs oxygen with the crew-breathable region overlapped on the tested region. The sweet spot is where both are true | M | ★★★ | Adopt if F verifies the physiology limits by hour 0 |
| 5 | **Plain-language habitat entry** | Type "Artemis base at 8 psi with 32% oxygen" and the sliders fill in. AI only parses. User confirms | S | ★★ | Adopt (Should), cheap crowd-pleaser |
| 6 | **Reverse search** | "I must stay under 8.2 psi. Which atmospheres are tested?" Filters the table the other way round | S | ★★ | Adopt (Should) |
| 7 | **Risk passport export** | One-page printable evidence brief with run IDs and gaps, to attach to a design review | S | ★★ | Adopt (Should, already the safety brief) |
| 8 | **Surprise detector** | Highlights runs that break the expected trend (for example more oxygen but the flame went out) | M | ★★ | Stretch, needs real data |
| 9 | **Trend with uncertainty band** | Flame-speed curve drawn only inside the tested range, hatched "unknown" outside | M | ★★ | Stretch |
| 10 | **Audit mode** | Click any number to open its source paper, page and figure | S | ★★ | Already in Must as Evidence trail |

Ideas we considered and **rejected**:

| Idea | Why not |
|---|---|
| Physics simulation of fire spread | Cannot be validated in 48 hours. A judge who knows combustion will test it. We explore what experiments showed, not what we predict |
| Chat-only assistant | Every team builds it. Add the chat last, if at all |
| Predicting a "safe" yes/no | We are not a safety authority. We show evidence strength and gaps |
| Many AI agents | Slower, costlier, less reliable. One call per pillar is enough |

## Idea details

### 1. Evidence strength meter (Must)

A number from 0 to 100 for each condition and for the whole habitat. It is a transparency aid, **not a safety rating**, and the UI says so.

Starting formula (weights are guesses, tune on real data):

```
strength = 0.35 * proximity      # 1 minus normalised distance to the nearest matching run
         + 0.30 * reliability    # high 1.0, medium 0.7, low 0.4, placeholder 0
         + 0.20 * run_count      # min(1, matching runs / 3)
         + 0.15 * source_quality # table 1.0, text 0.8, plot-read 0.5
```

Show the four parts as small bars so it matches the ranker's "score you can see into" style. Route: `POST /api/strength` (returns the number and the four parts per condition).

### 2. Test campaign planner (Should)

Input: number of experiments N (default 3) and the set of designs of interest (the user's habitat plus the Artemis-style presets).

Algorithm (greedy coverage):
1. Build a grid of candidate atmospheres across the data's oxygen, pressure and airflow ranges.
2. For each candidate, count designs of interest that would become "Supported" if that experiment existed (using the same tolerances as `/case`).
3. Pick the candidate with the biggest gain, mark those designs covered, repeat N times.

Output: N experiments, each with the conditions, designs it covers, and the cumulative coverage ("3 tests take coverage from 40% to 85%"). Route: `POST /api/campaign`. Reuses the matching code from `/case`, so most of the work is the grid loop and a bar chart.

Pitch line: *"FlameLens does not only read the archive. It plans the next experiments."*

### 3. Atmosphere journey (Should)

A mission passes through several atmospheres. Example stages (A and F must verify real values before using them): cabin, airlock pre-breathe or campout, lunar rover.

Input: 2 to 5 stages, each an atmosphere. Output: the Evidence case strength per stage as a row of gauges, the weakest stage highlighted, and a combined verdict ("Stage 2 has no evidence"). Route: `POST /api/journey {stages:[target,...]}` which calls the case logic per stage.

It turns a single-point tool into a mission tool, and it demos well: change one stage and watch the verdict change.

### 4. Breathable and tested zone (adopt if verified)

Overlap two constraints on the pressure vs oxygen map:
- **Crew-breathable:** a region defined by minimum and maximum oxygen partial pressure for humans.
- **Tested:** the existing coverage map.

The result is a shaded sweet spot where the atmosphere is both livable and backed by experiments, plus a plain list of "livable but untested" corners.

**Blocker:** F must find the physiology limits in an official NASA or medical source and record the number and link in `docs/research/claims.md` before it appears anywhere. Never type a limit from memory. If F cannot source it by kickoff, drop this idea.

### 5. Plain-language habitat entry (Should)

A text box: "Artemis base at 8 psi with 32% oxygen, low airflow". The LLM returns JSON for the habitat sliders, validated against the allowed ranges, shown for the user to confirm. All downstream logic is the deterministic code. If the AI fails, the sliders still work.

### 6. Reverse search (Should)

Instead of "here is my design, what applies", answer "my limit is X, what is tested". Fixed limits on any slider (for example pressure at most 8.2 psi) filter the run table and list the tested atmospheres with evidence strength. Route: `POST /api/search {constraints}`.

### 7. Risk passport export (Should)

Already planned as the safety brief. Make it a printable page with: the habitat, the evidence case with run IDs, the strength numbers, the gaps, the recommended next experiment, and a footer "generated from PSI data, sources attached".

### 8 and 9. Surprise detector, trend with uncertainty band (Stretch)

Only if the real data supports them after hour 24. Both depend on having enough runs per material.

## Recommended plan

| When | What |
|---|---|
| Must ship | Evidence case, Run this next, Safer options, **Evidence strength** (small add on `/case`), Coverage map, Evidence trail |
| Should ship, in this order | **Campaign planner**, **Atmosphere journey**, Plain-language entry, Reverse search, Risk passport |
| Only if sourced | Breathable and tested zone |
| Stretch | Surprise detector, uncertainty band, BOM auditor |

Team limit: **at most two Should-ship brainstorm ideas are built before Gate 2 (hour 24).** More than that and the core loop suffers. Decision made at Gate 1 (hour 10) by A with the team, based on how clean the real data is.

## Who builds what

| Idea | Owner | Helper | When |
|---|---|---|---|
| Evidence strength | A (route), C (gauges) | D (check reliability tags) | Hours 10–14 |
| Campaign planner | A (algorithm), C (chart) | B (panel) | Hours 14–20 |
| Atmosphere journey | B (UI), A (route) | C | Hours 18–24 |
| Plain-language entry | E | B | Hours 14–18 |
| Reverse search | A | B | Hours 18–22 |
| Risk passport | E (text), B (print layout) | F | Hours 24–30 |
| Breathable zone | C | F (sourcing) | Only if F has a sourced limit |

## How we decide what stays

At each gate, ask three questions for any new idea:
1. Does it work on the real data we actually have?
2. Can someone who did not build it use it in 30 seconds?
3. Will it still work if the AI is off?

Two yeses or fewer: cut it. The pitch is stronger with four things that work than seven that half work.

## Pitch angle

Three sentences, in this order:
1. "Engineers today read papers for days to learn whether a design is covered by tests."
2. "FlameLens shows what is proven, how strong the evidence is, and plans the experiments to fill the gaps."
3. "Every claim points at a real run, and where there is no evidence, we say so."
