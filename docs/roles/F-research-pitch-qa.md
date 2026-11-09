# Role F: Research, docs, pitch and QA

**Name:** ______  **Backup:** ______  **Pairs with:** everyone

## Your job in one sentence

Own the facts, the story and the quality bar: confirm the rules, check every scientific claim, write the pitch, test the product, and submit on time. At the hackathon you are also the second data extractor for the Detection and Suppression pillars (hours 0–14).

**العربية:** [النسخة العربية](ar/F-research-pitch-qa.md) · [Choose your role](00-choose-your-role.md)

## Experience needed

| | |
|---|---|
| **Required** | Clear writing and speaking (Arabic and English), organised, curious |
| **Nice to have** | Presenting or pitching, video editing, slides or Figma, software testing, reading research papers |
| **Learn in 2 days** | Reading research papers, the QA plan |
| **Personal fit** | Organised, likes checking facts, confident in front of people |
| **Coding?** | Not required |

## You own

Rules and deadlines, fact-check, README, slides, video, demo script, QA testing, submission, research notes for Detection and Suppression.

## Before the hackathon

### F1. Confirm the rules (Mon 9 Nov, 90 min)
Open the official NASA Space Apps challenge and event pages. Fill every row in the [facts table](../09-pitch-and-submission.md#facts-to-confirm-f-fills-these-in): deadline, video limit, required fields, team size, pre-event code rule, license rule, judging criteria, data access.
Done when: no row is empty, and each has a source link or says "not stated".

### F2. Read Detection and Suppression investigations (Mon–Tue 9–10 Nov, 3 hours)
**SAME, SAME-R, DAFT, DAFT-2, FLEX, FLEX-2, CFI, ACME E-FIELD**. Copy [../research/TEMPLATE.md](../research/TEMPLATE.md) to `docs/research/<NAME>.md` for each and fill it in.
Done when: at least six notes exist with source links.

### F3. Ask the organizers (Tue 10 Nov, 15 min)
Send the message in [08](../08-working-agreements.md#rule-check-before-writing-code) through the official contact or local organizer. Record the answer and date in that file.
Done when: the answer is written down, or the "no answer yet" is posted in the chat and you will chase it on Thursday.

### F4. Bake-off questions (Tue 10 Nov, 45 min, with E)
Write 20 fair questions about the investigations, including 5 that have no answer in the data. Add them to [07](../07-ai-guide.md#day-one-bake-off-20-questions).
Done when: E has tested at least three questions on a model.

### F5. Claims table (Wed 11 Nov, 2 hours)
In `docs/research/claims.md` list every scientific statement we plan to show in the UI or pitch, with its source and a status: **confirmed**, **needs source**, **drop**. Include:
- Earth air oxygen partial pressure of about 3.1 psi
- The crew-breathable oxygen limits (needed for the [breathable zone idea](../10-idea-brainstorm.md#4-breathable-and-tested-zone-adopt-if-verified), find an official source, never write one from memory)
- Any example atmospheres we use in presets (ISS, Artemis-style, airlock campout)
Done when: every claim has a link or a "drop" decision.

### F6. Pitch and demo script (Wed 11 Nov, 90 min)
Turn the table in [09](../09-pitch-and-submission.md#three-minute-demo-path) into a spoken script with timings. Add the 3-sentence pitch from [10](../10-idea-brainstorm.md#pitch-angle). Review the existing 5-slide deck to reuse branding.
Done when: you can read it aloud in 3 minutes.

### F7. QA plan (Wed 11 Nov, 60 min)
In `docs/design/qa-plan.md` write test cases as a table: what to do, what should happen, pass/fail column. Start from the [QA checklist](../09-pitch-and-submission.md#qa-checklist-f-tests-someone-who-did-not-write-the-code) and B's UI checks.
Done when: there are at least 20 test cases.

### F8. README and submission skeleton (Wed 11 Nov, 45 min)
Prepare the final README outline (what it does, how to run it, data sources, credits) in `docs/design/readme-outline.md`.
Done when: you only need to fill in the facts at the end.

### F9. Logistics and kickoff agenda (Thu 12 Nov, 45 min)
Confirm venue or online link, time zone, check-in time. Prepare the kickoff meeting agenda: roles, timeline, channels, sleep shifts. Remind everyone about chargers and food.
Done when: details are posted in the chat.

## At the hackathon

| Hour | You do |
|---|---|
| 0–2 | Write the real deadline and "submit by" time at the top of the chat. Open the PSI files with D |
| 2–14 | Extract Detection and Suppression runs (SAME, DAFT, FLEX, CFI). Push batches every 2 hours |
| 14–24 | README skeleton, slide outline, test pass 1 |
| 24–36 | Test pass 2 with the QA plan, screen capture, demo script rehearsal x3, fact-check every screen |
| 36–40 | Record the demo video against the tagged build |
| 40–48 | Submit at least 3 hours early, then save the confirmation |

## Hand-offs

| You give | To | When |
|---|---|---|
| Rule facts | Everyone | Mon 9 Nov |
| Claims table decisions | B, C, E | Wed 11 Nov |
| Bug list | Owner role | After each test pass |
| Final README and video | A | Hour 44 |

## Rules for you

- Nothing scientific ships without a source in `claims.md`.
- You decide whether a claim ships. Say so in the chat.
- Test like a stranger: fresh browser, deployed URL, phone width.
