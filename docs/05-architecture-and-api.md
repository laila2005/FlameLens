# Architecture and API

## Stack (simplified for a 24-hour event)

| Layer | Choice | Why |
|---|---|---|
| Frontend | Vite + React + TypeScript + Tailwind | Fast to start, familiar |
| Charts | Plotly.js | Lenses and coverage map without writing chart code from scratch |
| Backend | FastAPI (Python) | Quick to write, automatic API docs |
| Data | SQLite or DuckDB, loaded from CSV | No database server to run |
| Text retrieval | Filter by `psi_id`, then rank chunks with a small local embedding model (MiniLM or bge-small) or keyword match | A few hundred chunks do not need pgvector |
| LLM | Open model first (Qwen Instruct 7–14B, backup Llama 3.x 8B) behind an OpenAI-compatible API | See [AI guide](07-ai-guide.md) |
| Hosting | One container (Render or Fly) | One URL for judges |

Principle: **the ranker and all charts work without the LLM.** If the AI is down, the app still ranks and plots.

## Flow

```
Habitat input -> /rank (deterministic score) -> ranked investigations
                 /case /next /alternatives (deterministic matching) -> decision panels
                 /lens/* -> chart data
                 /explain -> LLM -> verifier -> only verified claims shown
```

## API contract

Agree on this in hour 1. Commit mock JSON for every route on day one so the frontend never waits for the backend.

```
GET  /api/habitats                       -> presets (o2, psi, airflow, gravity)
POST /api/rank        {target, weights, k}   -> [{psi_id, score, breakdown, confidence, top_runs}]
GET  /api/investigation/{psi_id}         -> metadata, runs, spin-off text, source links
GET  /api/lens/ventilation?psi_ids=&o2_levels=  -> series for Lens 1
GET  /api/lens/aerosol                   -> smoke and dust distributions for Lens 2
GET  /api/lens/coolflame                 -> regime grid for Lens 3
GET  /api/coverage?o2=&psi=              -> tested regions, in-range flag, 3 nearest runs
GET  /api/evidence/{run_id}              -> run values, value_source, source_ref, confidence
POST /api/case        {target}           -> per-condition status (supported | weak | none) with run_ids,
                                            whole-habitat matches, verdict line
POST /api/next        {target}           -> recommended experiment, gaps closed, nearest run, variables to change
POST /api/alternatives {target, k}       -> nearest tested runs with lower O2 partial pressure, deltas
POST /api/strength    {target}           -> evidence strength 0-100 per condition and whole habitat,
                                            with the four parts (proximity, reliability, run_count, source_quality)
POST /api/campaign    {n, targets}       -> n experiments chosen greedily, designs each covers, coverage before/after
POST /api/journey     {stages:[target]}  -> /case and /strength per stage, weakest stage, combined verdict
POST /api/search      {constraints}      -> tested atmospheres that satisfy fixed limits, with strength
POST /api/parse       {text}             -> habitat JSON parsed by the LLM, validated against allowed ranges
POST /api/brief       {target, psi_ids}  -> safety brief (markdown) built from /case, with citations and gaps
POST /api/diff        {psi_ids:[a,b]}    -> constants, variables, outcomes, cited explanation
POST /api/explain     {pillar, psi_ids, target}
                                         -> [{claim, psi_dataset_id, run_id_reference,
                                              confidence_level, engineering_recommendation, verified}]
```

`target` = `{o2_pct, pressure_psi, airflow_cm_s, gravity, fuel}`.

## Ranker

Weighted closeness score from 0 to 100.

| Factor | Default weight |
|---|---|
| Oxygen | 0.35 |
| Pressure | 0.20 |
| Airflow | 0.20 |
| Fuel match | 0.15 |
| Gravity fit | 0.10 |

Rules:
- If a run lacks a field, drop that term, rescale the other weights, and show "based on N of 5 factors".
- Normalise with the dataset's actual min and max and clamp to 0–1.
- Return the per-term breakdown so the UI can draw it.
- Rank runs, then roll up to the investigation using the best 3 runs.
- Always compute **oxygen partial pressure = pressure × oxygen fraction**. Earth air is about 3.1 psi.
- Unit-test with 5 hand-checked cases.

## Decision routes (no AI)

`/case`, `/next` and `/alternatives` are tolerance matching and distance sorting over the run table. The dashboard mockup script is the reference for the logic (see [links](links.md)).

Starting tolerances (tune on real data in hours 6–10; these are guesses, not validated science):

| Condition | Matches when |
|---|---|
| Oxygen | within 6 percentage points |
| Pressure | within 2 psi |
| Airflow | within 8 cm/s |
| Fuel | same fuel (any if the user chose "any") |
| Gravity | same gravity |

Status per condition: **Supported** = 2 or more matching runs, **Weak** = 1, **No evidence** = 0. The whole-habitat line counts runs matching all five at once.

`/next`: gaps = conditions that are not Supported. Recommend the target conditions themselves, with the nearest run (by normalised distance on oxygen, pressure, airflow) as the cheapest first step and the list of variables to change. If nothing is a gap, recommend repeating the lowest-confidence matching run.

`/alternatives`: runs with oxygen partial pressure at least 10% below the target and a matching fuel, sorted by distance, top 3, with the changes needed.

## AI guardrails

- The prompt receives only retrieved runs and chunks, each with its ID.
- Output must be JSON with the five fields above.
- The verifier rejects any `run_id_reference` not in the input and any number not found in that run.
- Rejected claims are hidden and counted ("2 claims removed").
- Low temperature. Cache answers for demo cases.

## Things we are deliberately not doing

pgvector, three parallel agents, custom physics models, an Electric-Gravity Bridge as a validated model, microservices.
