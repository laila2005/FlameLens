# Pitch and submission

Owner: F, with A checking the repo and deployment. Official rules are in [11 Event facts](11-event-facts.md).

## What we submit

There is **no live pitching**. Judges see only what we upload.

| Item | Detail |
|---|---|
| **Demo** | **Either** exactly 7 slides **or** a 30-second video, on a publicly accessible platform. No images, names or voices of anyone under 18 |
| **Links** | Final project link, GitHub repo, other code links. All must open without password, account or access request |
| **Project summary** | Problem, solution, impact, how it meets the challenge |
| **Resources** | Datasets, sources, references, tools used |
| **Disclosure** | AI use disclosed (in the product and in how we built it) |
| **Who and where** | Only the team leader submits: first the local form, then the same files on the official NASA Space Apps site |

## Facts (filled in from the official PDFs, 9 Nov)

| Fact | Answer |
|---|---|
| Hackathon | Fri 13 Nov 1:00 PM to Sat 14 Nov 1:00 PM, Cairo time (24 hours) |
| Our submit-by time | Sat 14 Nov 10:00 AM (3 hours early) |
| Demo format | 7 slides or 30-second video |
| Required fields | Demo, project links (final link, GitHub), summary, resources |
| Team size | 6, with at most 5 onsite |
| Pre-event code | **Not allowed.** Plan and task split only. Actual work starts at the hackathon |
| License rule | Not stated in the guides. Choose an open license (see below) |
| Judging criteria | Impact, Creativity, Validity, Relevance, Presentation |
| Data access | Not stated in the guides. Confirm on Discord |
| Still to confirm on Friday | Final deadline, official NASA submission site steps |

## 30-second video storyboard (default demo)

Plain words, no jargon, readable on a phone. Screen recording of the tagged build plus captions. A voice-over or text-only captions both work.

| Seconds | Show | Say or caption |
|---|---|---|
| 0–5 | Space visuals, flame with no "up" | "Fire behaves differently in space" |
| 5–10 | Messy papers and plots | "Engineers spend days digging through experiment data" |
| 10–14 | Habitat picker, ranked results | "FlameLens takes your habitat design" |
| 14–20 | Evidence case with Supported, Weak, No evidence | "Shows what is proven, and what is not" |
| 20–25 | Run this next and Safer options | "Tells you what to test next and what to change" |
| 25–30 | Logo, "Every claim cites a real run" | "FlameLens: evidence you can trust" |

Hook options that are real and sourced (see [12 Resources](12-resources.md#0-official-nasa-resources-shared-13-nov-the-day-of-the-hackathon)): the Apollo 1 pre-launch fire, the 1997 fire on the Mir space station, or the NASA smoke detector that tells smoke from dust and ended up in mines.

## 7-slide outline (backup, or if we choose slides)

1. Challenge: what NASA asks and why fire safety in space matters
2. The problem: the data is scattered, engineers cannot tell what is covered
3. Our solution: FlameLens in one picture
4. How it works: evidence case, next experiment, safer options, strength meter
5. Why you can trust it: real runs, sources, verifier, "no evidence" when true
6. Impact: who benefits, Earth spin-offs, what it saves
7. Next steps, data credits, tools, AI-use disclosure, team

## What judges will ask (in the written materials)

| Question | Answer |
|---|---|
| Is it real data? | Source links and confidence badges, PSI data credited |
| Can the AI be wrong? | The decision panels use no AI. The verifier removes unsupported claims |
| Who is it for? | Habitat engineers, safety reviewers, students |
| What next? | Auto-ingest from PSI, partial-gravity data when released |

## QA checklist (F tests, someone who did not write the code)

- [ ] Every habitat preset returns results, an evidence case and a Run-this-next answer
- [ ] A habitat far from any run shows "no evidence", never a guess
- [ ] Every run ID shown opens its source
- [ ] No chart shows an unlabeled or invented number
- [ ] Weights at extremes do not break the ranking
- [ ] AI off: the app still works
- [ ] Fresh browser, deployed URL, phone width
- [ ] "Sample data" banner shows when placeholder rows are loaded and is gone when they are not
- [ ] Demo video or slides match the tagged build

## Submission checklist (hours 17–21)

- [ ] Release tagged, deployed URL works in a private window with no login
- [ ] Repo public, license chosen, no secrets in history
- [ ] 30-second video uploaded and public, **or** 7 slides exactly, public link
- [ ] No under-18 images, names or voices in the demo
- [ ] README final: what it does, how to run it, data sources and credits, **AI-use disclosure**
- [ ] Project summary written and proofread
- [ ] Resources list: PSI data, papers, tools
- [ ] Team names listed
- [ ] Every link opened in a private window
- [ ] Team leader submits on the local form at hour 21 (10:00 AM)
- [ ] Same files uploaded on the official NASA Space Apps site
- [ ] Screenshots of both confirmations saved
- [ ] Backup internet connection ready (venue Wi-Fi may be congested)

## Licence

Not stated in the guides. Suggested default: MIT for code, with data credited to NASA PSI. Decide as a team before the repo is made public for judging (check that PSI terms allow redistribution of anything we commit).

## Branding

Dark aerospace theme, flame orange and cool cyan accents, as in the earlier team video and deck.
