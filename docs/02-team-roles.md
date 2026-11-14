# Team roles

Six people, six roles. Write your name in the table, then name a backup for every role. If someone is ill or offline, the backup takes over.

| Role | Name | Backup | Best fit | Owns | Pairs with | Task file |
|---|---|---|---|---|---|---|
| **A. Tech lead and backend** | Laila Mohamed | ______ | Strongest programmer | Repo, FastAPI, ranker, `/case` `/next` `/alternatives` logic, loader, deploy, merges | E | [A](roles/A-tech-lead-backend.md) |
| **B. Frontend lead** | Youssif Hassan | ______ | Programmer with UI taste | App shell, habitat picker, ranked cards, diff view, theme | C | [B](roles/B-frontend.md) |
| **C. Charts and lenses** | Yasmin Reda | ______ | Programmer comfortable with data | Plotly lenses 1–2 (3 if time), coverage map, Evidence case and Run-this-next panels | B, D | [C](roles/C-charts-lenses.md) |
| **D. Data extractor (lead)** | Judy Adham | F | Detail-oriented, reads PDFs well | PSI download, CSV, schema, sources, data checks. Takes the Prevention pillar | E | [D](roles/D-data.md) |
| **E. AI and retrieval** | Dai Alaa | ______ | Programmer who knows LLMs | Chunking, retriever, pillar prompts, verifier, answer cache, brief text | A, D | [E](roles/E-ai-retrieval.md) |
| **F. Research, docs, pitch, QA** | Mostafa Fathy | ______ | Writer and presenter | Rules and deadlines, fact-check, README, slides, video, demo, testing. Second extractor for Detection and Suppression in hours 1–8 | All | [F](roles/F-research-pitch-qa.md) |

Full names confirmed by Laila on 14 Nov (as shown in the demo video end card).

## How to choose roles

Start with [Choose your role / اختر دورك](roles/00-choose-your-role.md). It lists the experience each role needs, in English and Arabic, with a 5-minute self-check. Task files are also in Arabic: [docs/roles/ar](roles/ar).

1. Each person lists their top two roles in the chat.
2. A, B, C, E need real programming. D and F need patience and care more than code.
3. If two people want the same role, the tie goes to whoever has built something similar before.
4. Fill in this table, commit it, and everyone confirms with a thumbs-up.

## Why pairs

Pairs share a boundary, so nobody works alone on the critical path. Pairs sync at least every 2 hours during the hackathon.

## Shared duties

| Duty | Who |
|---|---|
| Merging to `main` | A (and the backup) |
| Test passes and bug list | F |
| Daily stand-up (15 min, 3 times in the event) | A runs it |
| Sleep shifts, never everyone asleep | A schedules, everyone follows |
| Submission | F leads, A checks the repo and deploy |

## Contingencies

- **Someone drops out:** their backup takes the role. A reassigns the backup's work.
- **Data is thin:** F joins D for longer, C reduces to two lenses.
- **A is blocked or ill:** the backup takes merges. B or C deploys using the notes in [A's task file](roles/A-tech-lead-backend.md).
