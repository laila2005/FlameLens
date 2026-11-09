# Resources found by web research (9 Nov)

Reading and research are allowed before the hackathon. Building is not (see [11 Event facts](11-event-facts.md)). This page lists what is public, how to reach it, and what to do with it on Friday. Everything here comes from web pages read on 9 Nov 2026. Items marked **unverified** came from third parties or could not be confirmed. Re-check before relying on them.

## 1. The official challenge

| Item | Finding |
|---|---|
| Name | **"Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data"** |
| Official page | https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/ |
| Our access | The page could not be opened by our research tool (a certificate error), so **we have not read the official text**. **F reads it in a normal browser tonight and copies the exact statement into this file** |
| What a third-party summary says (unverified) | Build a dashboard that **summarizes, ranks and explains** decades of NASA microgravity combustion results, to inform fire safety for Moon and Mars missions. Difficulty: intermediate to advanced. Category: space exploration |
| What "SI-Powered" means | Not confirmed. A third-party site reads it as "super intelligence", meaning AI. If the official text expects an AI component, **move the cited AI explanation from Should ship to Must ship** |
| Official resource list | A third-party source says the official resources open on the Space Apps site on 13 Nov |

Why it matters: "summarize, rank and explain" matches FlameLens (summary cards, ranker, evidence case with explanation). Quote the challenge wording in our summary and slides.

Third-party page with a first-hour checklist (unverified, not NASA): https://spacedata.swapniltamse.com/challenges/flame-in-freefall/

## 2. Getting the data (PSI)

| Route | What we know | Use |
|---|---|---|
| **PSI web repository** | https://psi.nasa.gov . Search page: `https://psi.nasa.gov/physci/repo/search?q=&data_source=psi&data_type=investigation` . Example investigation page: `https://psi.nasa.gov/physci/repo/data/investigations/PSI-178` . The site is rendered by JavaScript, so our tool could not list results. Open it in a browser | D explores by hand: how an investigation page looks, which files are offered, which formats |
| **AWS open data bucket** | Bucket `nasa-psi`, region us-west-2, anonymous access: `aws s3 ls --no-sign-request s3://nasa-psi/` . Browser view: https://nasa-psi.s3.us-west-2.amazonaws.com/index.html . The registry page names only two datasets (DSI, OASIS), so **combustion data may not be in the bucket** (unverified). License: "no restrictions on use" per the registry | Test the `ls` command once. Do not mirror data before Friday |
| **API** | **No documented public PSI API** was found. Expect manual downloads. A NASA page mentions a "New File Download Process for PSI Large Requests" (contents not seen) | Plan for manual download plus spreadsheet entry, as in [06 Data guide](06-data-guide.md) |
| **Tutorials** | PSI Database Tutorial (PDF), PSI Workspace Tutorial (PDF), "Researcher's Guide to PSI" (PDF/EPUB), demo video https://youtu.be/9uXgDUuWxTo . Links are on https://science.nasa.gov/physical-sciences-informatics-psi/ | D and F read the Database Tutorial tonight |
| **Microgravity Tool** | NASA's analysis platform for PSI: https://science.nasa.gov/physical-sciences-informatics-psi/microgravity-analytics-tool/ | Look at it, note what it already does so we do not duplicate it |
| **Contacts** | https://www.nasa.gov/content/psi-contacts-tutorials-and-related-links | Ask on Friday if a file is unclear |
| **Login** | A third-party page mentions an Earthdata login for some downloads (unverified). Create the account now if the PSI downloads ask for it | Judy creates it if needed |

Scale (NASA text): over 100 investigation datasets, about 30 TB, six disciplines (biophysics, combustion science, complex fluids, fluid physics, fundamental physics, materials science). Each study offers raw and processed data, documentation and publication lists.

## 3. Papers and reports through the NTRS API (verified working)

NASA Technical Reports Server has full-text PDFs and a public JSON API:

- Search: `https://ntrs.nasa.gov/api/citations/search?q=<words>&page.size=<n>`
- API docs: https://ntrs.nasa.gov/api/openapi/
- A test query for "Saffire flame spread" returned 12 results as JSON with fields `id`, `title`, `abstract`, `keywords`, `created`, `downloadsAvailable`, and `downloads` (each with `links.pdf`). PDF paths are relative, so prepend `https://ntrs.nasa.gov`.
- Record page pattern: `https://ntrs.nasa.gov/citations/<id>`

**Use:** E's retrieval corpus on Friday can be built from NTRS abstracts and PDFs in minutes. Prepare the **query list now** (text only, no code): one query per investigation name plus "microgravity flame", "spacecraft fire safety", "cool flame", "smoke detection spacecraft". Run it after 1:00 PM Friday.

Useful documents found (open and read, all public):

| Topic | Link |
|---|---|
| Saffire VI preliminary results | https://ntrs.nasa.gov/citations/20240002981 |
| Saffire large-scale combustion overview | https://core.ac.uk/works/56977844 |
| Saffire final presentation (ICES 2021) | https://ntrs.nasa.gov/api/citations/20210017780/downloads/Saffire%20ICES%202021%20Saffire%20Final%20presentation%20compressed.pdf |
| Spacecraft fire safety demonstration (Saffire) | https://www.nasa.gov/wp-content/uploads/2025/07/spacecraft-fire-safety-demonstration-saffire.pdf |
| Saffire and BASS concurrent flame spread data (thin charring fuels, NASA/UCL) | https://par.nsf.gov/servlets/purl/10313745 |
| SAME smoke and detection summary (2017) | https://ntrs.nasa.gov/citations/20170007283 |
| Fire detection white paper | https://ntrs.nasa.gov/api/citations/20210022143/downloads/Fire%20detection%20white%20paper%20final%20211031.pdf |
| Combustion in reduced gravity mini-book (NASA) | https://www.nasa.gov/sites/default/files/atoms/files/np-2015-10-034-jsc_combustion_in_reduced_gravity-iss-mini-book-011116-508.pdf |
| Flame spread over thin hollow cylindrical fuels in microgravity | https://arxiv.org/pdf/2311.09041 |
| Buoyancy effects on concurrent flame spread over thick PMMA | https://ntrs.nasa.gov/citations/20200000557 |

## 4. Investigations (from NASA pages read on 9 Nov)

Source: https://www.nasa.gov/missions/station/iss-research/studying-combustion-and-fire-safety/ and the NASA explainer https://science.nasa.gov/biological-physical/resources/explainers-infographics/why-nasa-is-studying-flames-in-space/

| Investigation | What it studied | Pillar |
|---|---|---|
| BASS | One of the first studies of extinguishing fuels burning in microgravity: flame geometry, material, extinguishing methods | Prevention / Suppression |
| BASS-II | How varied fuel samples burn in microgravity vs normal gravity; flame spread vs fuel regression. Fires suppressed with nitrogen | Prevention |
| Saffire (I to VI) | Larger fires in uncrewed Cygnus spacecraft after they leave the station: flame spread, heat release, effect of lower pressure | Prevention |
| SoFIE (GEL, MIST) | Ignition and flammability of solid fuels, including fuel temperature; spherical samples | Prevention |
| BRE (ACME) | Burning Rate Emulator: gaseous fuels simulate solid/liquid flammability; 59 burn tests with heat flow, flame size, fuel mixture flow | Prevention |
| Flame Design (ACME) | Soot under different flame conditions | (other) |
| FLEX, FLEX-2 | Suppressant effectiveness, discovery of cool flames; droplet burn rates, soot, evaporation | Suppression |
| Confined Combustion (ISS National Lab) | Flame spread in confined spaces of different shapes | Prevention |
| SAME, DAFT | Smoke particle size and a particle counter on the ISS; the ISS detector failed to alarm on Kapton smoke in half the tests (SAME paper) | Detection |
| SPICE | Hardware used with BASS (slightly modified); details not confirmed | Prevention |
| FLARE (JAXA) | Material flammability in microgravity; no detail found | (other) |

Not found on those NASA pages and so **unverified**: CFI, DAFT-2, SAME-R, ACME E-FIELD Flames. They came from the original idea text. D and F check each on PSI. Update [02](02-team-roles.md), [06](06-data-guide.md) and the research index if the real list differs.

NASA text also says: some materials may be **more flammable in partial gravity**, and a planned study (Flammability of Materials on the Moon, FM2) will test flame size and spread. This supports why Moon habitats need this data.

## 5. Crew oxygen and cabin pressure (for the "breathable and tested" idea)

Not confirmed. What the search found (read the standards yourselves before using any number):

- NASA-STD-3001 Volume 2 has a requirement (V2 6003) on inspired oxygen partial pressure ranges, and V2 6002 requires at least 30% diluent gas in the cabin. **The numeric ranges were not seen.**
- A NASA technical brief on habitable atmospheres (OCHMO-TB-003) says that with the 30% diluent rule, the lowest achievable cabin pressure is 5.0 psia: https://www.nasa.gov/wp-content/uploads/2023/12/ochmo-tb-003-habitable-atmosphere.pdf
- A Constellation-era NASA paper says flammability thresholds in oxygen concentration and partial pressure depend on total pressure, nearly linearly over the tested range: https://ntrs.nasa.gov/citations/20070005041
- **We could not confirm the "8.2 psi, 34% oxygen" Artemis-style preset** or the "10.2 psi, 26.5% airlock campout" values. Treat all presets as examples until F sources them in `docs/research/claims.md`.

## 6. Dates note

Some third-party pages say the global event is 14–15 Nov with kickoff on 13 Nov. The Cairo guide says the hackathon is 13–14 Nov, 1:00 PM to 1:00 PM. **Follow the Cairo guide** and confirm on Discord.

## 7. Recommended actions (tonight and tomorrow)

| Who | Action |
|---|---|
| F | Open the official challenge page in a normal browser. Copy the exact challenge statement and listed resources into this file. Check if an AI/"SI" component is expected |
| D and Judy | Open the PSI site, read the Database Tutorial, browse 5 combustion investigations by hand. Record in `docs/research/psi-access.md`: what files each offers and in which formats. **Do not build the dataset yet** |
| D | Test `aws s3 ls --no-sign-request s3://nasa-psi/` once and note whether combustion folders exist |
| E (Dai) | Write the NTRS query list (text). Read the Saffire VI, SAME and fire detection documents above to draft the pillar prompts |
| C and B | Read the Microgravity Tool page and note what it already visualises, so our views add something different |
| Laila | Keep the decision to move the AI explanation to Must open until F reports the official wording |

## 8. What this changes in our plan

1. Data will be **manual download plus extraction** (no PSI API). Our 24-hour data targets are realistic only if D and F start at minute 0 and the NTRS API supplies the text corpus.
2. NTRS gives E a fast, legal corpus for retrieval and citations.
3. The challenge wording "summarize, rank and explain" confirms our direction. Add an explicit **investigation summary card** to the Must-ship ranked list if it is not already visible.
4. PSI may contain more or other combustion investigations than our list. The Friday field inventory will settle it.
