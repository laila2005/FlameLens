# Start now: resources, who reads what, first hour

Written 13 Nov at about 12:35 PM Cairo time, 25 minutes before the hackathon starts at **1:00 PM**. Reading is allowed now. **Product code starts at 1:00 PM, not before.**

## The plan in one picture

| Clock | Hour | What the team does |
|---|---|---|
| Now to 1:00 PM | before | Everyone reads their assigned item (20 minutes). Post 3 bullets in the chat: "what I learned that changes our product" |
| 1:00 PM | 0 | Hackathon starts. F posts the deadline (Sat 1:00 PM) and our submit time (Sat 10:00 AM) at the top of the chat |
| 1:00 to 2:00 PM | 0 to 1 | Lock the data fields and the API contract (steps below) |
| 2:00 to 7:00 PM | 1 to 6 | Build the vertical slice: pick a habitat, see ranked real cards |
| 7:00 PM | 6 | **Gate 1:** does the slice run? If not, stop adding features |

Full timeline: [04 Hackathon timeline](04-hackathon-timeline.md).

## The resources in plain words

NASA gave us 10 resources. Full links are in [12 Resources, section 0](12-resources.md#0-official-nasa-resources-shared-13-nov-the-day-of-the-hackathon).

| # | Resource | What it is, in one or two lines | What we take from it |
|---|---|---|---|
| 1 | **PSI Data Repository, combustion** | NASA's open archive of experiment data from the ISS and earlier flights. This is **the data our app is built on**. No documented API: expect manual downloads | The runs and fields for our table |
| 2 | **NASA Combustion Science page** | Short descriptions of the combustion investigations. Names FM2 (lunar gravity), SoFIE, FLARE, ACME, BASS, DAFT, FLEX, Saffire, SAME, SLICE, SPICE. Fact sheet PDFs for the archived ones | Which investigations exist, what each measured |
| 3 | **ScienceCasts video (3.6 min, 2018)** | Quick introduction to combustion research on the ISS | What the experiments look like, for our video |
| 4 | **Researcher's Guide to ISS Combustion Science (2015, 50+ pages)** | A review of NASA's combustion work, most of it found in PSI. Covers past research, lessons learned, future opportunities | Investigation descriptions, units, terms for the AI prompts |
| 5 | **Apollo 1** | 1967 launch-pad fire killed the crew. The cabin was pure oxygen, combustible materials fed the fire, and the hatch took about 90 seconds to open. Afterwards NASA restricted combustible materials, added fire-resistant suits and a fast hatch | Why oxygen level and materials matter. A real pitch hook |
| 6 | **Apollo 13** | An oxygen tank exploded on the way to the Moon. The cause was an overheated, damaged tank, later fixed with a redesign. The crew survived using the lunar module | Why oxygen systems need evidence, not guesses |
| 7 | **Fire aboard Mir (1997)** | A fire on the Russian space station caused by an oxygen generator failure | A second real example of fire in space |
| 8 | **Fire Detector (spin-off)** | A smoke detector built for the shuttle. It samples air for combustion particles and **tells smoke from dust**, so fewer false alarms. Used in mines | **Real Earth spin-off text. Links directly to our Lens 2 (smoke vs dust)** |
| 9 | **Fireman's Air Tanks (spin-off)** | 1970s spacesuit technology used to improve firefighters' air tanks and breathing gear | Earth spin-off example |
| 10 | **New Technology for the Fire Attire (spin-off)** | 1980s spacesuit technology used to improve firefighter clothing | Earth spin-off example |

Facts about Apollo 1 and 13 and the fire detector were checked on NASA's pages today. Mir and the two other spin-off pages were not opened by us, so check them yourself before quoting.

### What this tells us about the product

1. **The story is oxygen and materials.** Apollo 1 and 13 both come down to oxygen plus something that can burn. FlameLens answers exactly that for a new habitat. Use it as the opening of the video.
2. **PSI is the data, the Researcher's Guide is the explanation.** We rank and explain PSI runs, and use the guide and NASA pages to describe each investigation.
3. **Smoke vs dust is a real NASA success story.** The fire detector spin-off gives Lens 2 a real-world link and gives us sourced Earth spin-off text.
4. **No API, so extraction is manual.** Judy and the second extractor must start at 1:00 PM. The paper library (NTRS API) is the fast part.

## Who reads what (20 minutes, until 1:20 or until the clock says 1:00)

Everyone posts 3 bullets in the chat: what you learned, what it changes for the product, one question.

| Person | Role | Read | Look for | العربية |
|---|---|---|---|---|
| **Judy** | D data | **#1 PSI combustion search**: open 5 investigations (BASS, SAME, DAFT, FLEX, Saffire if present) | Which files each offers, which formats, which fields (oxygen, pressure, airflow, fuel, gravity, outcome). Write it in `docs/research/field-inventory.md` | افتح 5 تجارب في PSI وسجّل الملفات والصيغ والحقول |
| **Mostafa** (F, to confirm) | F research and QA | **The official challenge page** (`spaceappschallenge.org/2026/challenges/flame-in-freefall/`) and **#2 NASA Combustion Science page** | The exact challenge wording. Is an AI part expected ("SI-Powered")? Paste the text into [12 Resources](12-resources.md#1-the-official-challenge). Also confirm the deadline on Discord | اقرأ نص التحدي الرسمي وصفحة Combustion Science والصق النص في docs/12 |
| **Dai** (E, to confirm) | E AI | **#4 Researcher's Guide**: skim the chapters on BASS, SAME, DAFT, FLEX, Saffire | The quantities and units each experiment measured, and the terms the AI must use. Write 5 bullets for the prompts | تصفح دليل الباحث وسجّل الكميات والوحدات والمصطلحات للـ prompts |
| **Yasmine** | C charts | **#8 Fire Detector spin-off** and **#3 ScienceCasts video** | What smoke vs dust looks like and how the detector separates them (for Lens 2). What flames look like in microgravity. Sketch the first idea for Lens 1 and Lens 2 | اقرأ صفحة كاشف الحريق وشاهد الفيديو وارسم فكرة العدستين |
| **Yousseif** | B frontend | **#5 Apollo 1**, **#7 Mir**, **#9 Fireman's Air Tanks**, **#10 Fire Attire** | The story for the opening screen and video, and the wording for the "Earth spin-off" card. Pick a visual tone: serious, clear, dark theme | اقرأ أبولو 1 وMir وصفحتي التطبيقات الأرضية وجهّز نص بطاقة التطبيق الأرضي |
| **Laila** | A tech lead | **#1 PSI search** with Judy for 10 minutes (data shape), then **#6 Apollo 13** | Can we build one table from what Judy sees? What changes in the schema ([06](06-data-guide.md))? Decide the repo structure and branch plan | اطّلع مع Judy على شكل البيانات ثم اقرأ أبولو 13 وقرر هيكل المستودع |

If someone is not on the team yet (Mostafa, Dai), their reading goes to the backup: F's reading to Laila, E's reading to Yasmine.

## The first hour from 1:00 PM

1. **Everyone:** pull the repo, read the chat bullets (5 minutes).
2. **F:** write the deadline and the "submit by Sat 10:00 AM" line at the top of the chat. Join Discord and the mentor channel.
3. **Judy and F:** open the PSI combustion search together. List which investigations have **downloadable runs with oxygen, pressure and airflow**. Pick the first 6 to extract, in the order of easiest first.
4. **Laila:** compare Judy's field list with [06 Data guide](06-data-guide.md). Change the schema in the doc **before anyone writes code against it**, and tell everyone in the chat.
5. **Laila:** agree the [API contract](05-architecture-and-api.md) and write one mock JSON file per route. Yousseif and Yasmine need it by 1:45 PM.
6. **Yousseif:** create the app shell (picker, empty ranked list, "sample data" banner) from scratch. **Do not copy the old mockup.**
7. **Yasmine:** start Lens 1 on the placeholder CSV.
8. **Dai:** run the NTRS paper search (queries in `docs/design/retrieval.md` or the list in [12](12-resources.md)). Save titles and PDF links. The prompts can wait until the data fields are known.
9. **2:00 PM:** mentors start. Ask one mentor to sanity-check the idea if useful. 10-minute stand-up.

## Decisions to make in the first 30 minutes

| Decision | Who | Default |
|---|---|---|
| Who is the team leader who submits | Team | Laila, as repo owner |
| Who is onsite (max 5), who is virtual | Team | Decide now |
| Who owns F if Mostafa is unsure | Team | Pick one person at 1:00 PM, no later |
| Is the AI explanation Must ship | Laila with F | Yes if the challenge text expects AI |
| First 6 investigations to extract | Judy | The ones with the cleanest tables |

## If PSI turns out harder than expected

- Extract from the **papers and fact sheets** (tables inside the PDFs), not only PSI downloads. Tag every value `table`, `text` or `plot-read` as in [06](06-data-guide.md).
- Cut to the 4 investigations with the best data. The decision panels need 15 to 20 runs, not 80.
- Still show the app honestly: "No evidence" for gaps is a valid result and our signature.
