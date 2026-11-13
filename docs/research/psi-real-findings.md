> **Follow-up:** the tables were downloaded and merged. See [dashboard-data-map.md](dashboard-data-map.md) for what the data answers and what is missing.

# What the real PSI site contains (checked 13 Nov, about 12:50 PM Cairo)

Found by opening the real PSI search in a browser and reading the pages (no files were downloaded). This replaces our earlier guesses. Owners: Judy (D) and F confirm and extend it at 1:00 PM.

## The headline

1. **Every microgravity combustion investigation has an "Experimental Table" CSV.** That is the structured run table we thought we would have to build by hand from PDFs. We still need to map each table's columns to our schema, but the rows already exist.
2. **PSI has a working web backend we can call.** It is undocumented, so treat it as "may change" and call it politely (a few requests, not a crawl).
3. **The data is open.** License CC0-1.0, each investigation has a DOI, and PSI asks users to **cite the DOI**. Add the DOIs to our resources list and README.
4. **The raw archives are huge** (hundreds of GB to TB of video and images per investigation). **Do not download the big files.** Only the small CSV tables and the readme or summary documents matter for our 24 hours.

## The 26 search results for "combustion"

Search URL: https://psi.nasa.gov/physci/repo/search?q=combustion&data_source=psi&data_type=investigation

### Microgravity investigations (19), all have an Experimental Table CSV

| PSI ID | Investigation | Likely pillar |
|---|---|---|
| PSI-26 | BASS: Burning and Suppression of Solids | Prevention |
| PSI-25 | BASS-II | Prevention |
| PSI-98, PSI-99, PSI-100 | Saffire-I, Saffire-II, Saffire-III (Cygnus spacecraft fires) | Prevention |
| PSI-107 | SPICE: Smoke Point in Co-flow Experiment | Prevention |
| PSI-20 | ACME BRE: Burning Rate Emulator | Prevention |
| PSI-102 | SAME: Smoke and Aerosol Measurement Experiment | Detection |
| PSI-101 | SAME-R (reflight) | Detection |
| PSI-47 | DAFT and DAFT-2 (one record for both) | Detection |
| PSI-69 | FLEX: Flame Extinguishment Experiment | Suppression |
| PSI-68 | FLEX-2 | Suppression |
| PSI-39 | CFI: Cool Flames Investigation | Suppression |
| PSI-159 | ACME CFI-G: Cool Flames Investigation with Gases | Suppression |
| PSI-22 | ACME E-FIELD Flames | Suppression |
| PSI-10 | ACME Flame Design (soot) | other |
| PSI-21 | ACME CLD Flame (coflow laminar diffusion) | other |
| PSI-23 | ACME s-Flame (spherical diffusion flames) | other |
| PSI-106 | SLICE: Structure and Liftoff in Combustion Experiment | other |

**This resolves the earlier open questions:** CFI, SAME-R, DAFT-2 and ACME E-FIELD Flames are all in PSI. Saffire IV to VI and SoFIE did not appear in this search.

### Ground and modeling investigations (5), likely not run tables

PSI-117 (cool flame CFD using FLEX data), PSI-142 (cool flame transitions, counterflow, uses FLEX data), PSI-62 (flame spread modeling compared with BASS), PSI-60 (SPICE data analysis), PSI-115 (smoke generation modeling using SAME data). Useful as sources and citations, not as run data.

### Not combustion (ignore)

PSI-181 (solders), PSI-108 (STDCE-1, fluid physics).

## What an investigation page offers

Example: PSI-25 (BASS-II). Version 4, about 256 GB.

- **Description:** objectives, approach, hypothesis, research impacts and Earth benefits, hardware, contacts, DOI (PSI-25: 10.60555/4qc4-de67), license CC0-1.0, related investigation (PSI-26).
- **Experimental Table:** a CSV, `PSI-25_Experimental table_BASS-II.csv`, shown in the page (130 rows).
- **Publications list** with DOIs (good for citations).
- **Data files:** 694 files (videos, documents, zips). Ignore the videos.

### The BASS-II table columns (real)

`PI, Test #, Date, GMT, Sample #, Fuel Sample Material, Flow restrictor, Fan display, Air display, Radiometer gain, Total Frames Shot, Calibrated initial O2 % by vol, Calibrated final O2 % by vol, Initial CO2 % by vol, Final CO2 % by vol, Initial CO (ppm), Final CO (ppm)`

Example rows: PMMA films of 100, 200 and 300 micron, 2 cm wide, initial oxygen 22.2 %, CO2 about 0.44 %.

## What this means for our schema ([06 Data guide](../06-data-guide.md))

1. **Oxygen is real and per run** (`Calibrated initial O2 % by vol`). BASS-II varied oxygen **below 21 %** by adding nitrogen (page text) and the rows we saw are about 22 %. **Our 34 % lunar-rover preset is probably outside most data.** The coverage map will show "No evidence" there. That is the honest and interesting result, not a bug.
2. **Pressure is not a column in the BASS-II table.** It is the cabin pressure and is the same for the whole investigation (ISS ambient). Record it per investigation (from the description), and expect a few investigations to vary it (FLEX-2 varied pressure, page text mentions 0.5 atm as the lower end). Add a per-investigation `pressure_psi_note` with the source.
3. **Airflow is not a clean cm/s column.** BASS-II has `Flow restrictor`, `Fan display` and `Air display`, and its description says the wind tunnel reaches up to 40 cm/s. Converting display codes to cm/s needs the readme or the hardware document. Until then, airflow may be empty (`confidence = low`), and `/case` airflow will show "Weak" or "No evidence" in many places.
4. **Fuel** is a free-text sample description (for example "100 micron PMMA film 2 cm wide"). Our new `fuel_state` column (solid, liquid, gas) must be filled by hand per investigation.
5. **Gravity:** microgravity for all 19 flight investigations. Lunar and Mars gravity will show **"No evidence"**, as in our test cases.
6. **Columns differ per investigation.** We need one mapping per investigation, not one loader. Start with BASS, BASS-II, Saffire I to III, SAME, FLEX, FLEX-2, CFI, and map only the columns we need: material or fuel, oxygen, pressure, airflow, outcome, source.

## Endpoints used by the PSI site (unofficial, may change)

| Purpose | URL |
|---|---|
| Search | `https://psi.nasa.gov/geode-py/ws/repo/search?term=combustion&source=psi&type=investigation&from=0&size=25` |
| One investigation (JSON, large, includes the file list and the field `experimentalTable`) | `https://psi.nasa.gov/geode-py/ws/repo/investigations/PSI-25` |
| Download a file | `https://psi.nasa.gov/geode-py/ws/studies/PSI-25/download?file=PSI-25_Experimental%20table_BASS-II.csv&version=1&redirect=false` |

The investigation JSON can be about 190 KB. The CSV tables are small. Pull only the 19 tables and the readme or summary documents.

## What to do at 1:00 PM

1. Judy and F: open the Experimental Table of each investigation in the table above, copy the column names into [field-inventory.md](field-inventory.md), and mark which columns map to oxygen, pressure, airflow, fuel and outcome.
2. Laila: with Judy, decide the mapping per investigation and update [06](../06-data-guide.md). Keep the final schema, not the 17 raw BASS-II columns.
3. Download the 19 CSV tables into `data/raw/` (git-ignored). **Ask first**: they are downloads (small files from psi.nasa.gov).
4. Cite the PSI DOIs in the README and the submission (PSI asks for it).
