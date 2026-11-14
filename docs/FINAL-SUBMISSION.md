# FlameLens: final submission package

Copy-paste text for the NASA Space Apps submission form, the 7-slide deck, and the script of the 30-second video.

- **Live demo (public, no login):** https://flamelens-steel.vercel.app
- **Repository:** https://github.com/laila2005/FlameLens
- **API docs:** https://flamelens-steel.vercel.app/docs

**Every number below was checked against `data/curated/` and the running app on 14 Nov 2026.** If the data changes, re-run `python scripts/validate_live.py .` and update the numbers before submitting. The field names follow earlier Space Apps forms; if the 2026 form names a field differently, use the closest text. Length limits are not confirmed, so check each box on the form.

---

## Part 1. Form fields

### 1. Project name

```text
FlameLens
```

### 2. Challenge

```text
Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data
```

### 3. High-level summary (short, 49 words)

```text
FlameLens is a web dashboard built on 2,003 real NASA PSI microgravity combustion runs from 18 flight investigations. Enter a spacecraft, Moon base or rover atmosphere and see which conditions are backed by experiments, how strong that evidence is, where the gaps are, and which experiment to run next.
```

### 4. Project summary (medium, about 130 words)

```text
Future Moon bases and pressurized rovers are expected to use 30 % oxygen or more at 10.2 psi or less, which makes materials much more flammable. NASA has decades of microgravity fire experiments in its PSI repository, but they are spread over many tables and reports and are hard to compare.

FlameLens brings 2,003 runs from 18 PSI flight investigations into one table and answers an engineer's question: is my cabin design backed by experiments? It marks each condition as supported, weak or not tested (counting only runs with the same material), scores the strength of the evidence, shows the nearest real runs and cited NASA tests outside PSI (down to lunar-gravity drop tests), proposes the next experiment, and explains the result in plain language. Users can also ask NASA's own reports questions and get answers that quote the exact page. Every statement links to a NASA run or document. Where there is no evidence, FlameLens says so instead of guessing.
```

### 5. Link to the final project

```text
https://flamelens-steel.vercel.app
```

### 6. Link to the demo (slides or video)

```text
(paste the public link to the 7 slides or the 30-second video here)
```

### 7. Link to the code

```text
https://github.com/laila2005/FlameLens
```

### 8. Detailed project description

```text
THE PROBLEM
Fire is one of the most serious hazards in a crewed spacecraft. In microgravity hot gas does not rise, so a flame is fed by diffusion and by the cabin airflow. The planned Moon base and pressurized rovers are expected to use 30 % oxygen or more at 10.2 psi or less, more than 40 % more oxygen than Earth air, which makes materials much more flammable.

NASA's Physical Sciences Informatics (PSI) repository holds the microgravity combustion experiments that could tell an engineer whether a cabin atmosphere has been tested. But each investigation has its own table, columns and reports. The data is hard to find, harder to compare and harder to interpret.

WHAT FLAMELENS DOES
FlameLens summarizes, ranks and interprets the PSI combustion investigations for one practical question: "Is my habitat design backed by NASA fire experiments, how strong is that evidence, and what should be tested next?"

The user picks a preset (Moon base, pressurized rover, spacesuit, ISS cabin, Mars habitat) or sets oxygen, pressure, airflow, material and gravity. FlameLens then shows:

1. Evidence case. Each condition is marked Supported, Weak or No evidence, with the number of matching NASA runs and their IDs. Only runs with the chosen material count: a 30 % oxygen gas flame is not evidence for a 30 % oxygen fabric fire ("Other fuels only").
2. Evidence strength, 0 to 100, for each condition and for the whole design. It is a transparency score, not a safety rating.
3. Closest NASA evidence. When no run matches the whole design, the runs that match everything except the fewest conditions, and exactly what differs. It also shows cited NASA tests outside PSI, never counted: the Saffire IV-VI spacecraft fires at reduced pressure and raised oxygen, drop-tower limits at lunar and Martian gravity, and NASA-STD-6001 material tests at 10.2 and 8.2 psia.
4. Run this next. The gaps, the nearest existing run, and the changes needed to turn it into the missing test.
5. Test campaign planner. If NASA can fly N more experiments, which ones give the most habitat designs a full match.
6. Lower-oxygen tested options. Real runs with at least 10 % less oxygen partial pressure.
7. Ranked investigations. The 18 flight investigations ordered by how close their runs are to the design.
8. What the evidence says. A short explanation in plain language where every sentence cites a run.
9. Seven lenses: coverage map, cool flames, smoke vs dust, smoke points (55 SPICE flames at the moment they began to smoke), flame spread, airflow tested, and an early-detection simulator.
10. An investigations explorer with a profile of each investigation and a side-by-side comparison. Conditions a PSI table leaves empty show the sourced NASA statement instead (16 notes with quotes and pages).
11. Mission atmosphere journey: ISS cabin, spacesuit, rover and Moon base as one mission, as strong as its weakest stage.
12. Ask the NASA reports: questions answered from 1,899 passages of 20 NASA PSI documents; every AI claim must quote its page word for word or it is removed.
13. A printable design review brief, and downloads of the curated data for modelling.

WHAT IT SHOWS
- ISS cabin (21 % oxygen, 14.7 psi, microgravity): 336 runs match the whole design. Evidence strength 82.5 of 100.
- Pressurized rover (30 % oxygen, 10.2 psi, solid material, lunar gravity): 2 of 5 conditions supported and 0 runs match the whole design. Its oxygen and pressure were tested only with gas flames and fuel droplets, never with a solid material. 308 solid-material runs share its airflow but were at 14.5 to 22.2 % oxygen and 14.7 psi. Outside PSI, NASA's Saffire V fire burned cotton at 26.2 % oxygen and 10.25 psi in a Cygnus spacecraft, and NASA drop-tower tests at lunar gravity and 10.2 psia show Ultem and Mylar films burning at lower oxygen than in 1 g (Olson and Ferkul 2012). The nearest PSI run is PSI-25-0023 from BASS-II.
- Gravity: every run in PSI is microgravity. FlameLens states that PSI has no partial-gravity combustion data yet and that microgravity results are one bound, and shows the cited drop-tower limits at lunar and Martian gravity.
- With three more experiments, the planner covers the Moon base and rover with one lunar-gravity test, and the spacesuit and Mars habitat with the other two.

HOW IT WORKS
- Data. We downloaded the PSI Experimental Table of each combustion investigation and merged them into one table of 2,003 runs. For every run we record the material, oxygen, pressure, airflow, gravity and outcome, and how each value was obtained: measured, read from text, assumed, or unknown. Where a table gives no oxygen or pressure we use ISS cabin air and mark it as assumed.
- Decisions. Matching, ranking, strength, next experiment and the campaign plan are plain arithmetic over that table. No AI is involved. A run matches a condition when it is within 6 oxygen points, 2 psi or 8 cm/s, or has the same material state and gravity.
- Explanation. The explanation panel uses text that an open language model wrote from the retrieved runs. A citation verifier re-checks every sentence and removes any that cites a run outside the evidence, states a number not in that run, or gives a safety threshold.
- Ask the NASA reports. BM25 search over 1,899 page-tagged passages, Gemini 2.5 Flash writes at most 3 claims, and the server keeps a claim only if its quote is word for word on the cited page and its numbers are on that page.
- Software. A Python FastAPI backend and a plain JavaScript frontend with our own SVG charts, deployed on Vercel. 95 automated tests and a 137-check script against the live site.

BENEFITS
- For habitat and life-support engineers: a defensible answer in minutes, with the gaps visible.
- For researchers and students: one comparable table of 2,003 runs, 43 measured flame-spread rates, investigation profiles and links to 27 NASA publications, all downloadable.
- For planning: a list of the experiments that would close the most gaps.
- On Earth: the same research supports smoke detectors that tell smoke from dust, firefighter clothing and breathing equipment, and water-mist extinguishers.

WHAT WE ARE CAREFUL ABOUT
FlameLens never invents a value and never gives a safety verdict. "No evidence" means untested in PSI, not unsafe. Assumed values are labelled. The early-detection simulator is an illustration with a simplified spread model; only its gas levels and particle sizes come from NASA data.
```

### 9. NASA data and resources used

```text
NASA Physical Sciences Informatics (PSI), combustion science (https://psi.nasa.gov). License CC0-1.0 as stated on the PSI records. Flight investigations used, with run counts and DOIs:
- PSI-26 BASS, 122 runs, DOI 10.60555/58h4-dy80
- PSI-25 BASS-II, 129 runs, DOI 10.60555/4qc4-de67 (also its summary report for flame-spread rates and its fan calibration)
- PSI-98 Saffire-I, 2 runs, DOI 10.60555/0t15-1z43
- PSI-99 Saffire-II, 9 runs, DOI 10.60555/2chp-m469
- PSI-100 Saffire-III, 2 runs, DOI 10.60555/040q-4h36
- PSI-107 SPICE, 469 runs, DOI 10.60555/9kbh-e962
- PSI-20 ACME BRE, 43 runs, DOI 10.60555/vb93-3y72
- PSI-102 SAME, 8 runs, DOI 10.60555/gd4k-8h62
- PSI-101 SAME-R, 109 runs, DOI 10.60555/2np7-jv14 (also its final report, Table 1, for smoke particle sizes)
- PSI-47 DAFT and DAFT-2, 2 runs, DOI 10.60555/ztgj-d202 (also its reports for dust particle sizes)
- PSI-69 FLEX, 274 runs, DOI 10.60555/mbq8-0451
- PSI-39 CFI, 87 runs, DOI 10.60555/m6pj-a914
- PSI-159 ACME CFI-G, 333 runs, DOI 10.60555/cyt1-kh64
- PSI-22 ACME E-FIELD Flames, 20 runs, DOI 10.60555/se5a-8c73
- PSI-10 ACME Flame Design, 327 runs, DOI 10.60555/w4zy-bt45
- PSI-21 ACME CLD Flame, 32 runs, DOI 10.60555/23e1-9950
- PSI-23 ACME s-Flame, 23 runs, DOI 10.60555/k57n-p030
- PSI-106 SLICE, 12 runs, DOI 10.60555/pm12-rg61
- PSI-68 FLEX-2, planned test matrix only, DOI 10.60555/byp8-h018

PSI ground and CFD modelling studies linked from the dashboard:
- PSI-60, DOI 10.60555/mzjm-yv57
- PSI-62, DOI 10.60555/e9xp-ex83
- PSI-115, DOI 10.60555/q0v5-1v28
- PSI-117, DOI 10.60555/gz0q-b577
- PSI-142, DOI 10.60555/80qf-vj95

NASA Technical Reports Server (NTRS), https://ntrs.nasa.gov : 27 publications linked from the dashboard, found through the public NTRS API.

NASA Spinoff: fire detector that tells combustion particles from dust (https://spinoff.nasa.gov/node/9407), firefighter breathing system (https://spinoff.nasa.gov/node/9582), firefighter clothing (https://spinoff.nasa.gov/node/9918).

NASA documents outside PSI (cited, never counted in the evidence case): Saffire IV-VI test conditions and outcomes (Urban et al., ICES-2021-266 and ICES-2024-365, NTRS 20210011521, 20240002981); partial-gravity flammability limits (Olson and Ferkul, ICES 2012, NTRS 20130010991, Table I); NASA-STD-6001 Test 1 limits at 10.2 psia (Hirsch et al. 2007, NTRS 20070018178; Hirsch et al. 2010, NTRS 20100015582) and at 8.2 psia (Aly et al., ICES-2026-301, NTRS 20260003042); ISS cabin atmosphere (NASA OCHMO-TB-003 Rev A); exploration atmosphere 8.2 psia / 34 % O2 (NTRS 20220005716); carbon monoxide limits (JSC 20584 Rev C).

NASA Space Apps challenge page and its resources, for the habitat atmospheres and background: https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/
NASA Combustion Science page: https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/
```

### 10. Space agency partner and other data

```text
No space agency partner data was used. Other tools: Python, FastAPI, Pydantic, pytest, plain JavaScript and SVG, Vercel hosting, Google Fonts (Sora, IBM Plex Sans, IBM Plex Mono), the open language model qwen2.5:7b-instruct for the explanation text, Google Gemini 2.5 Flash for "Ask the NASA reports", and Kokoro-82M (open-source, Apache-2.0) for the video narration.
```

### 11. Use of artificial intelligence

```text
In the product:
- Decisions use no AI. Evidence status, strength scores, rankings, the next experiment, the campaign plan and the lower-oxygen options are deterministic arithmetic over the NASA tables.
- The "What the evidence says" panel shows AI-written text. For the five presets, an open model (qwen2.5:7b-instruct) wrote 5 claims per preset ahead of time, using only the retrieved NASA runs. Our citation verifier re-checks every claim on every request. It removes any claim that cites a run outside the evidence, states a number that is not in that run, or gives a flammability threshold or safety verdict. All 25 cached claims pass. For a custom design the live site has no model and shows a plain summary filled from the runs, labelled "AI is off".
- "Ask the NASA reports" calls Google Gemini 2.5 Flash live. The model sees only retrieved passages from NASA PSI documents; the server keeps a claim only if its quote is word for word on the cited page, its numbers appear on that page, and it has no safety verdict. Without a key the panel shows the matching passages. The idea and first scripts came from a team member (Dai); we integrated and hardened them.
- AI-generated text is marked in the interface, and each claim shows the run or page it cites. Model suggestions are labelled "AI suggestion, not verified as a fact".

While building:
- AI coding assistants (Claude in Claude Code, and Claude and Gemini in Antigravity) helped the team write the data scripts, backend, frontend and documentation during the hackathon.
- The numbers shown in the app come from NASA files, not from an AI. They are checked by 95 automated tests and by a script that compares the live site with the curated data. An AI research agent helped find NASA papers outside PSI; we checked the values against the papers before adding them.
- The FlameLens logo illustration (a burning planet with a magnifying glass) was generated with Google Gemini and chosen by the team; the site icon is a crop of it.
- The demo video was composed by our own scripts from screen captures of the live site. The narration is a synthetic adult female voice made with Kokoro-82M, an open-source text-to-speech model (Apache-2.0), from our own script. The music is synthesized by code, with no samples and no AI-generated music. No real voices or faces are used.
```

### 12. References

```text
- NASA Physical Sciences Informatics (PSI) data repository, combustion science: https://psi.nasa.gov/physci/repo/search?q=combustion
- NASA Technical Reports Server: https://ntrs.nasa.gov
- NASA Space Apps Challenge 2026, Flame in Freefall: https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/
- NASA Combustion Science: https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/
- A Researcher's Guide to International Space Station Combustion Science: https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/
- NASA Spinoff: https://spinoff.nasa.gov/node/9407 , https://spinoff.nasa.gov/node/9582 , https://spinoff.nasa.gov/node/9918
- DOIs of every PSI investigation used are listed under "NASA data and resources used" and in the repository README.
```

### 13. Tags

```text
fire safety, microgravity, combustion, PSI, Moon base, rover, dashboard, open data, evidence, AI with citations
```

---

## Part 2. The 7 slides

Exactly 7 slides. No faces, names or voices of anyone under 18. Keep the text as short as written here and let the screenshots carry the slide. Take every screenshot from the live site.

### Slide 1. Title

- **Title:** FlameLens
- **Subtitle:** Is your habitat design backed by NASA fire experiments?
- **Line:** 2,003 real NASA PSI runs · 18 flight investigations · every claim cites a run
- **Footer:** Team AstroSpark · NASA Space Apps 2026, Cairo · flamelens-steel.vercel.app
- **Visual:** the top of the dashboard with the "Pressurized rover" preset selected.

### Slide 2. The problem

- **Title:** Fire has no "up" in space, and the Moon will add oxygen
- **Points:**
  - In microgravity hot gas does not rise. Cabin airflow feeds the flame.
  - Moon base and rovers: 30 % oxygen or more at 10.2 psi or less. Materials become much more flammable.
  - NASA has the experiments, but they are spread over many tables and reports.
- **Visual:** a raw PSI experimental table next to the FlameLens header chip "2,003 real runs · 18 NASA PSI investigations · CC0".

### Slide 3. The solution

- **Title:** Enter a design. See the evidence.
- **Points:**
  - Each condition: Supported, Weak or No evidence, with the matching NASA runs.
  - Evidence strength from 0 to 100. A transparency score, not a safety rating.
  - Works for any atmosphere, with presets from the challenge text.
- **Visual:** the "Evidence strength & case" panel for the ISS cabin preset (336 matching runs, strength 82.5).

### Slide 4. Honest about the gaps

- **Title:** No fabric has burned in rover air in PSI
- **Points:**
  - Pressurized rover, 30 % oxygen at 10.2 psi with solid materials: 2 of 5 conditions supported, 0 matching runs. Its oxygen and pressure were tested only with gas flames and droplets.
  - Closest evidence: 308 solid-material runs at 14.5 to 22.2 % oxygen; outside PSI, Saffire V and lunar-gravity drop-tower limits, cited but not counted.
  - PSI has no partial-gravity data yet. FlameLens says so.
- **Visual:** the verdict and the "Closest NASA evidence" block for the pressurized rover.

### Slide 5. What to test next

- **Title:** From a gap to a test plan
- **Points:**
  - "Run this next": the nearest real run (PSI-25-0023, BASS-II) and what to change.
  - Campaign planner: with 3 experiments, one lunar-gravity test serves both the Moon base and the rover.
  - Lower-oxygen options that were really tested.
- **Visual:** the "Run this next" panel and the "Test campaign planner" panel.

### Slide 6. The science, made visible

- **Title:** Seven lenses on the same data
- **Points:**
  - Flame spread: 43 measured rates. Thin fabric and film 2.1 to 2.6 mm/s, thick acrylic slabs 0.012 to 0.144 mm/s.
  - Smoke vs dust: smoke 0.04 to 0.29 µm, dust 1.57 to 1.72 µm. Size tells them apart.
  - Cool flames: 56 runs with a recorded cool flame, which makes little light or heat.
  - Smoke points: 55 ISS flames at the moment they began to smoke; propane makes the least soot, propylene the most.
- **Visual:** the "Flame spread", "Smoke vs dust" and "Cool flames" charts side by side.

### Slide 7. Trust, impact and credits

- **Title:** Evidence you can check
- **Points:**
  - Decisions use no AI. The AI only explains, and a verifier removes any claim without a matching NASA run.
  - Every run links to its NASA DOI. Assumed values are labelled.
  - On Earth: smoke detectors that ignore dust, firefighter clothing and breathing equipment.
  - Data: NASA PSI (CC0) and NTRS. AI use disclosed: an open model for explanations, AI coding assistants for development.
- **Visual:** the "What the evidence says" panel with a run opened in the evidence drawer, and the "Back on Earth" panel.

---

## Part 3. The 30-second video

**The video is made:** [`media/flamelens-demo-30s.mp4`](../media/flamelens-demo-30s.mp4) (1920 x 1080, 60 fps, 30.0 s, H.264 with AAC). It opens with a kinetic-type hook, then screen recordings of the live site with captions, a narrated voice-over and music that dips under the voice. **No faces, no names of people, no real voices**: the narration is a synthetic adult female voice (Kokoro-82M, open source, Apache-2.0). To re-make it, see [`scripts/demo_video/README.md`](../scripts/demo_video/README.md).

### Scenes, captions and narration (as in the video)

| Time | On screen | Caption | Narration |
|---|---|---|---|
| 0:00-0:03 | Hook: "In space, fire plays by different rules." over rising embers | – | In space, fire plays by different rules. |
| 0:03-0:08 | Pressurized rover preset: 30 % O₂, 10.2 psi, Moon gravity | Moon rover: 30 % O₂ at 10.2 psi | Moon rovers may breathe thirty percent oxygen. Would a cabin fabric burn in that air? |
| 0:08-0:12 | Data chip, ISS cabin strength meter (83/100, 336 runs) | 2,003 real NASA flight runs · 18 PSI investigations | FlameLens checks any habitat against two thousand real NASA flight runs. |
| 0:12-0:14 | Rover evidence case: oxygen and pressure "Other fuels only" | Rover: 2 of 5 conditions backed | For the rover: no exact match yet. |
| 0:14-0:18 | Outside-PSI limits: lunar-gravity drop tests (Olson and Ferkul 2012) | Closest evidence, down to lunar gravity | So it shows the closest evidence, down to lunar-gravity tests. |
| 0:18-0:21 | Verified AI claims; click a run, evidence drawer with DOI | Every AI sentence cites a real NASA run | Every AI sentence must cite a real run, or it's deleted. |
| 0:21-0:26 | Campaign planner (3 tests cover 5 designs), then Ask the NASA reports with a verified quote | What NASA should fly next · Ask the NASA reports | It plans what NASA should fly next, and quotes the exact report page. |
| 0:26-0:30 | End card | Space-fire data, made clear · flamelens-steel.vercel.app | FlameLens. Space-fire data, made clear. |

The dashboard shows the ISS strength as 83 because it rounds 82.5. The earlier silent cut is in git history.

### To submit the video

Upload the MP4 to YouTube (Unlisted or Public) or Google Drive ("Anyone with the link can view"). Open the link in a private window to check it plays without a login. Paste that link into field 6. The file is also in the public GitHub repo as a backup.

---

## Part 4. Before you press submit

- [ ] The live site opens in a private window without a login: https://flamelens-steel.vercel.app
- [ ] The repository is public: https://github.com/laila2005/FlameLens
- [ ] The video (`media/flamelens-demo-30s.mp4`) or the 7 slides are uploaded, and the link opens in a private window without a login
- [ ] The slides are exactly 7, or the video is 30 seconds or less
- [ ] No images, names or voices of anyone under 18 in the demo
- [ ] `python scripts/validate_live.py .` passes against the live site
- [ ] The numbers in the form match this file (if the data changed, update them)
- [ ] Team member names and roles are correct on the form and in the README
- [ ] The team leader submits on the local Cairo form, then on the official NASA Space Apps site
- [ ] Screenshots of both confirmations are saved
- [ ] Submitted by 12:30 PM Cairo time on Saturday 14 Nov (deadline 1:00 PM; late submissions are not accepted)
