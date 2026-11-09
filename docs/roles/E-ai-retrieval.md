# Role E: AI and retrieval

**Name:** Dai (tentative)  **Backup:** ______  **Pairs with:** A and D

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
Write the cache design in the same file: key = hash of (prompt version, retrieved run IDs, target), value = verified claims JSON, one file per key. Plan to pre-generate answers for the demo habitats by hour 15.
Done when: A confirms the design fits the backend.

### E9. NTRS query list (Wed 11 Nov, 30 min)
In `docs/design/retrieval.md` list the search queries for the NASA Technical Reports Server API ([12 Resources](../12-resources.md#3-papers-and-reports-through-the-ntrs-api-verified-working)): one per investigation name plus "microgravity flame", "spacecraft fire safety", "cool flame", "smoke detection spacecraft". Text only. Run it after 1:00 PM Friday.
Done when: at least 15 queries are listed.

### E8. Habitat parser tests (Thu 12 Nov, 45 min)
Write 10 sample sentences and the JSON each should produce, for example "Artemis base at 8 psi with 32% oxygen" in `docs/design/prompts.md`. Include 3 vague or impossible ones that should return an error asking the user to confirm.
Done when: the cases show what happens when the sentence is unclear.

### E10. Read the key papers (Tue 10 – Wed 11 Nov, 90 min)
Read the abstracts and conclusions of the Saffire VI, SAME and fire detection documents listed in [12 Resources](../12-resources.md#3-papers-and-reports-through-the-ntrs-api-verified-working). Use them to improve the pillar prompts in `docs/design/prompts.md` (real terms, real units, what the experiments measured).
Done when: each pillar prompt mentions at least two real quantities from the papers.

## At the hackathon (24 hours, hour 0 = Fri 13 Nov, 1:00 PM Cairo time)

| Hour | You do |
|---|---|
| 0–1 | Pick the model from the bake-off, set `.env`. Use a local model: venue Wi-Fi is shared and may be congested |
| 1–6 | Chunk and index documents, retriever working, first pillar prompt. If real data is too thin at hour 6, help D extract runs |
| 6 | **Gate 1:** one real explanation with citations |
| 6–13 | Verifier, `/explain`, answer cache for the demo habitats |
| 13–17 | Risk-passport text, plain-language entry only if chosen. **Cache pre-generated by hour 15** |
| 17 | **Freeze** |

## Hand-offs

| You give | To | When |
|---|---|---|
| Prompts and schema | A | Hour 1 |
| Verifier code | A | Hour 8 |
| Cached demo answers | F | Hour 15 |

## Rules for you

- The AI never ranks, never computes coverage, never decides safety.
- `verified` is set by our code, never by the model.
- The app must work with the AI off. Test it.
- Temperature low. Cache everything for the demo.
