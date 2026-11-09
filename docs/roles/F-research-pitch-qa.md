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

### F1. Check the event facts (Mon 9 Nov, 60 min)
Read [11 Event facts](../11-event-facts.md) and compare it with the official NASA Space Apps and Cairo pages. Fill the gaps in the [facts table](../09-pitch-and-submission.md#facts-filled-in-from-the-official-pdfs-9-nov): the licence rule, data access instructions, and the steps for the official NASA submission site.
Done when: every row in the table has an answer or says "confirm on Discord".

### F2. Read Detection and Suppression investigations (Mon–Tue 9–10 Nov, 3 hours)
**SAME, SAME-R, DAFT, DAFT-2, FLEX, FLEX-2, CFI, ACME E-FIELD**. Copy [../research/TEMPLATE.md](../research/TEMPLATE.md) to `docs/research/<NAME>.md` for each and fill it in.
Done when: at least six notes exist with source links.

### F3. Settle the open questions (Tue 10 Nov, 30 min)
The official guide already answers the code question: **no product code before the hackathon starts**. Use the time for the questions in [11 Event facts](../11-event-facts.md#open-questions-to-settle): who is the team leader who submits, who are the 5 onsite and the virtual sixth, and are all members 18 or over for the demo.
Done when: each question has an answer in the chat and in that file.

### F4. Bake-off questions (Tue 10 Nov, 45 min, with E)
Write 20 fair questions about the investigations, including 5 that have no answer in the data. Add them to [07](../07-ai-guide.md#day-one-bake-off-20-questions).
Done when: E has tested at least three questions on a model.

### F5. Claims table (Wed 11 Nov, 2 hours)
In `docs/research/claims.md` list every scientific statement we plan to show in the UI or pitch, with its source and a status: **confirmed**, **needs source**, **drop**. Include:
- Earth air oxygen partial pressure of about 3.1 psi
- The crew-breathable oxygen limits (needed for the [breathable zone idea](../10-idea-brainstorm.md#4-breathable-and-tested-zone-adopt-if-verified), find an official source, never write one from memory)
- Any example atmospheres we use in presets (ISS, Artemis-style, airlock campout)
Done when: every claim has a link or a "drop" decision.

### F6. Video script and slide outline (Wed 11 Nov, 90 min)
Turn the 30-second storyboard and the 7-slide outline in [09](../09-pitch-and-submission.md) into final wording. Add the 3-sentence pitch from [10](../10-idea-brainstorm.md#pitch-angle). Reuse the branding of the existing 5-slide deck. Remember: no under-18 images, names or voices.
Done when: you can read the video script aloud in 30 seconds and the 7 slides each have a title and one sentence.

### F7. QA plan (Wed 11 Nov, 60 min)
In `docs/design/qa-plan.md` write test cases as a table: what to do, what should happen, pass/fail column. Start from the [QA checklist](../09-pitch-and-submission.md#qa-checklist-f-tests-someone-who-did-not-write-the-code) and B's UI checks.
Done when: there are at least 20 test cases.

### F8. README and submission skeleton (Wed 11 Nov, 45 min)
Prepare the final README outline (what it does, how to run it, data sources, credits) in `docs/design/readme-outline.md`.
Done when: you only need to fill in the facts at the end.

### F9. Logistics and kickoff agenda (Thu 12 Nov, 45 min)
Confirm venue or online link, time zone, check-in time. Prepare the kickoff meeting agenda: roles, timeline, channels, sleep shifts. Remind everyone about chargers and food.
Done when: details are posted in the chat.

## At the hackathon (24 hours, hour 0 = Fri 13 Nov, 1:00 PM Cairo time)

| Hour | You do |
|---|---|
| 0–1 | Write the real deadline (Sat 14 Nov, 1:00 PM Cairo) and our "submit by" time (10:00 AM) at the top of the chat. Join Discord. Open the PSI files with D |
| 1–8 | Extract Detection and Suppression runs (SAME, DAFT, FLEX, CFI). Push a batch every 2 hours |
| 8–13 | Slide outline, 30-second video storyboard, test pass 1, README skeleton, AI-use disclosure text |
| 13–17 | Test pass 2 with the QA plan, screen capture, fact-check every screen |
| 17–21 | Record the 30-second video or finish the 7 slides against the tagged build. Project summary, resources list, check every link opens without a login |
| 21 | Submit with the team leader on the local form **and** the official NASA Space Apps site. Save the confirmation |

## Hand-offs

| You give | To | When |
|---|---|---|
| Rule facts | Everyone | Before kickoff |
| Claims table decisions | B, C, E | Wed 11 Nov |
| Bug list | Owner role | After each test pass |
| Final slides or video, README | A | Hour 20 |

## Rules for you

- Nothing scientific ships without a source in `claims.md`.
- You decide whether a claim ships. Say so in the chat.
- Test like a stranger: fresh browser, deployed URL, phone width.
