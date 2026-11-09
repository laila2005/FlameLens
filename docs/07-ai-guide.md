# AI guide

Owner: E. The AI explains. It never ranks, never calculates the decision panels, and never states anything the data does not contain.

## Model choice

| Priority | Model | Notes |
|---|---|---|
| First | Qwen Instruct 7–14B | Strong at structured JSON, runs locally or hosted |
| Backup | Llama 3.x 8B | Good general quality |
| If JSON keeps breaking | Hermes fine-tune | Built for function calling and JSON |
| Last resort | Hosted proprietary model | Only if open models fail the bake-off |

Run through Ollama locally or a hosted open-model service with an OpenAI-compatible API.

Confirm model names and licenses on the model pages before choosing. Versions change.

## Configuration

Keep everything swappable through environment variables (see [.env.example](../.env.example)):

```
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen2.5:7b-instruct
LLM_TEMPERATURE=0.1
LLM_CACHE=true
```

## Output schema

```json
{
  "claim": "string, one factual sentence",
  "psi_dataset_id": "BASS",
  "run_id_reference": "BASS-R03",
  "confidence_level": "high | medium | low",
  "engineering_recommendation": "string or null",
  "verified": false
}
```

`verified` is set by our code, never by the model.

## Verifier rules

A claim is removed and counted if any of these is true:

1. `run_id_reference` is not in the retrieved input.
2. A number in the claim does not appear in that run's row.
3. The claim contains a limit or threshold with no run supporting it.
4. The JSON does not parse after one retry.

The UI shows "N claims removed". If the AI is off or fails, the app still works.

## Prompt rules

Do:
- Give the model only the retrieved runs and chunks, each with its ID.
- Ask for JSON in the schema above and nothing else.
- Say: "If the data does not support a claim, say there is not enough data."
- Keep one call per pillar (Prevention, Detection, Suppression), not three parallel agents.

Don't:
- Let the model see runs that were not retrieved.
- Ask it to compute scores or coverage.
- Ask it for safety verdicts or thresholds.

## Day-one bake-off (20 questions)

Write the questions before kickoff. Test each candidate model on all of them and fill the table. Pass means: valid JSON, all claims cite a real run, no invented numbers.

| # | Question | Qwen | Llama | Notes |
|---|---|---|---|---|
| 1 | What did BASS test at 21% oxygen? | | | |
| 2 | Is 34% oxygen at 10.2 psi covered by any experiment? | | | |
| 3 | What is the safe airflow limit? (should answer: not enough data) | | | |
| 4 to 20 | E and F add: one per investigation, plus trick questions that have no answer | | | |

Add the pass count at the bottom. Choose by pass count, then speed.

## Fallback ladder

1. Cached answers for the demo cases (always prepared by hour 30)
2. Local small model
3. Hosted open model
4. Hosted proprietary model
5. AI off: the app shows ranked results, charts and the deterministic panels

## Embeddings

Small local model (MiniLM or bge-small). Filter by `psi_id` before ranking chunks. A few hundred chunks need no vector database.
