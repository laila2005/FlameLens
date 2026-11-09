# Role D: Data extractor (lead)

**Name:** Judy  **Backup:** F  **Pairs with:** E (and F as second extractor)

## Your job in one sentence

Turn NASA's experiment records into a clean, sourced table, so every number in the app can be traced to a paper. You take the **Prevention** pillar. F takes Detection and Suppression.

**العربية:** [النسخة العربية](ar/D-data.md) · [Choose your role](00-choose-your-role.md)

## Experience needed

| | |
|---|---|
| **Required** | Spreadsheets (Excel or Google Sheets), reading English scientific papers and PDFs, attention to detail, unit conversion |
| **Nice to have** | Science or engineering background, Python with pandas for cleaning CSV, reading charts |
| **Learn in 2 days** | The row format and extraction rules |
| **Personal fit** | Patient, precise, never guesses |
| **Coding?** | Not required |

## You own

PSI download, CSV extraction, the schema, source references, data checks, the research notes for your investigations.

## Before the hackathon

### D1. Read your investigations (Mon 9 Nov, 3 hours)
Find the public pages and papers for: **BASS, BASS-II, Saffire, SPICE, BRE**. For each one, copy [../research/TEMPLATE.md](../research/TEMPLATE.md) to `docs/research/<NAME>.md` and fill it in: what was varied, what was measured, which values are in tables vs plots, links.
Done when: five notes exist, each with at least one source link.

### D2. Practise extraction (Tue 10 Nov, 2 hours)
Pick one paper. Enter 5 runs in a scratch CSV using the [row format](../06-data-guide.md#row-format). Time yourself. Note every annoyance (units, missing columns, plot values).
Done when: you know how long one run takes and have a list of conventions to agree with F.

### D3. Shared spreadsheet (Tue 10 Nov, 45 min)
Create a shared sheet with the row-format columns. Add dropdowns for `value_source` and `confidence`, number validation for the numeric columns, and a frozen header. Write the export steps (File, Download, CSV) at the bottom of this file.
Done when: F can open it, edit it, and you can export clean CSV.

### D4. Extraction examples (Wed 11 Nov, 2 hours)
In `docs/research/extraction-examples.md` write three worked examples: a value from a table, a value from the text, a value read from a plot (tagged `plot-read`, confidence `low`). Then swap 10 rows with F and check each other's work.
Done when: F's 10 rows and your 10 rows follow the same conventions.

### D5. Units and ranges cheat sheet (Wed 11 Nov, 45 min)
In `docs/research/units.md`: conversions (kPa to psi, m/s to cm/s), and the realistic range for oxygen, pressure and airflow so impossible values stand out.
Done when: a typo like 340% oxygen would be caught by your own rules.

### D6. PSI access plan (Wed 11 Nov, 45 min)
Find where PSI data will be downloaded from and in which formats (the PSI site, any API). Write what you know and what you do not in `docs/research/psi-access.md`. If you cannot tell, write the questions to ask at kickoff.
Done when: you know your first three steps at hour 0.

### D7. Kickoff template (Thu 12 Nov, 30 min)
Create `docs/research/field-inventory.md` as a table: investigation, files found, fields present, units, gaps. This is what you fill in during hours 0–2.
Done when: the table exists, empty, ready.

### D8. Read the PSI tutorial and browse by hand (Tue 10 Nov, 90 min, with F)
1. Read the PSI Database Tutorial PDF (linked from [12 Resources](../12-resources.md#2-getting-the-data-psi)).
2. Open `psi.nasa.gov` in a browser and look at 5 combustion investigations. For each, note which files are offered and in which formats in `docs/research/psi-access.md`.
3. Run `aws s3 ls --no-sign-request s3://nasa-psi/` once (install the AWS CLI first if needed) and note whether combustion folders exist.
4. If downloads ask for an Earthdata login, create the account now.
**Do not download everything or build the dataset before Friday 1:00 PM.** This is reading only.
Done when: `psi-access.md` lists the formats seen and what the S3 listing showed.

## At the hackathon (24 hours, hour 0 = Fri 13 Nov, 1:00 PM Cairo time)

| Hour | You do |
|---|---|
| 0–1 | Open every PSI file with F. Fill the field inventory. Tell A at once if the schema must change |
| 1–6 | First 15–20 real runs across at least 6 investigations. Push a batch every 2 hours |
| 6–13 | Grow to 30–40 runs, with `source_ref` and confidence on every row |
| 13–15 | Data checks: duplicates, impossible values, missing sources. **Data freeze at hour 15** |
| 15–21 | Credits and dataset list for the submission. Help C and E with questions |

## Hand-offs

| You give | To | When |
|---|---|---|
| Field inventory | A, C, E | Hour 1 |
| First CSV batch | A | Hour 3 |
| Further CSV batches | A | Every 2 hours |
| Credits and dataset list | F | Hour 15 |

## Rules for you

- **No source, no row.** Never invent or round a value.
- If a plot is unreadable, leave it empty and say why in `notes`.
- Mark every plot-read value. The UI shows a lower-confidence badge, which is a feature.
- Tell E which text chunks come from which paper, so citations work.
