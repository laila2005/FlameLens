# Role E: AI and retrieval

**Name:** ______  **Backup:** ______  **Pairs with:** A and D

## Your job in one sentence

Make the AI useful and safe: it explains what the data says, parses plain-language input, and can never state anything that is not backed by a real run.

**العربية:** [النسخة العربية](ar/E-ai-retrieval.md) · [Choose your role](00-choose-your-role.md)

## Experience needed

| | |
|---|---|
| **Required** | Python, JSON, calling APIs |
| **Nice to have** | Prompting or LLM experience, Ollama or Hugging Face, embeddings, testing mindset |
| **Learn in 2 days** | Ollama basics, simple retrieval |
| **Personal fit** | Naturally sceptical, tests before trusting |

## You own

Chunking, retriever, pillar prompts, the citation verifier, the answer cache, plain-language habitat entry, the text of the risk passport.

## Before the hackathon

Read [07 AI guide](../07-ai-guide.md) first.

### E1. Install Ollama (Mon 9 Nov, 45 min)
Install Ollama, pull one small model, and ask it a question. Run `python scripts/check_env.py`.
Done when: the model answers locally on your laptop.

### E2. Draft prompts (Tue 10 Nov, 2 hours)
In `docs/design/prompts.md` write four prompts: Prevention explainer, Detection explainer, Suppression explainer, and the habitat parser (plain text to JSON). Each prompt needs: role, the input format (runs and chunks with IDs), the output JSON schema from [07](../07-ai-guide.md#output-schema), and the line "if the data does not support a claim, say there is not enough data".
Done when: A reads them and understands the inputs and outputs.

### E3. Verifier cases (Tue 10 Nov, 60 min)
In `docs/design/verifier-cases.md` write 10 test cases as a table: a model output, the retrieved run IDs, and whether each claim should **pass** or be **removed** and why. Include: unknown run ID, number not in the run, a limit with no support, broken JSON, a perfectly valid claim.
Done when: each of the four [verifier rules](../07-ai-guide.md#verifier-rules) is covered.

### E4. Bake-off questions (Tue 10 Nov, 45 min, with F)
Write the 20 questions with F and add them to the table in [07](../07-ai-guide.md#day-one-bake-off-20-questions). Include at least 5 trick questions that have no answer in the data.
Done when: 20 questions exist and F has checked they are fair.

### E5. Run the bake-off (Wed 11 Nov, 2 hours)
Pull two models (for example Qwen Instruct 7B and Llama 3.1 8B, check current names). Ask all 20 questions with the draft prompt on mock data. Record passes, JSON failures, speed.
Done when: the table in [07](../07-ai-guide.md) is filled and you can say which model to start with.

### E6. Retrieval plan (Wed 11 Nov, 60 min)
In `docs/design/retrieval.md` write: chunk size and overlap, metadata per chunk (`psi_id`, `paper`, `page`), how to filter by `psi_id` first, and which embedding model (MiniLM or bge-small).
Done when: D agrees the metadata can be produced from their notes.

### E7. Cache plan (Wed 11 Nov, 45 min)
Write the cache design in the same file: key = hash of (prompt version, retrieved run IDs, target), value = verified claims JSON, one file per key. Plan to pre-generate answers for the demo habitats by hour 30.
Done when: A confirms the design fits the backend.

### E8. Habitat parser tests (Thu 12 Nov, 45 min)
Write 10 sample sentences and the JSON each should produce, for example "Artemis base at 8 psi with 32% oxygen" in `docs/design/prompts.md`. Include 3 vague or impossible ones that should return an error asking the user to confirm.
Done when: the cases show what happens when the sentence is unclear.

## At the hackathon

| Hour | You do |
|---|---|
| 0–2 | Pick the model from the bake-off, set `.env`, test on first real data |
| 2–10 | Chunk and index the documents, retriever working, first pillar prompt |
| 10 | Gate 1: one real explanation with citations |
| 10–24 | Verifier, `/explain`, answer cache for demo habitats |
| 14–18 | Plain-language habitat entry (if chosen at Gate 1) |
| 24–36 | Risk passport text, prompt tuning, cache pre-generation (done by hour 30) |
| 40 | Freeze |

## Hand-offs

| You give | To | When |
|---|---|---|
| Prompts and schema | A | Hour 2 |
| Verifier code | A | Hour 12 |
| Cached demo answers | F | Hour 30 |

## Rules for you

- The AI never ranks, never computes coverage, never decides safety.
- `verified` is set by our code, never by the model.
- The app must work with the AI off. Test it.
- Temperature low. Cache everything for the demo.
