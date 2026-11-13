# Field inventory (task D7, filled in at hour 0 to 1)

For each investigation's **Experimental Table** CSV, write the real column names and say which ones map to our schema ([06 Data guide](../06-data-guide.md)). Background: [psi-real-findings.md](psi-real-findings.md). Owners: Judy (Prevention) and F (Detection and Suppression).

Mapping key: **O2** = oxygen %, **P** = pressure, **Flow** = airflow, **Fuel** = fuel or material, **Out** = outcome (burned, extinguished, detected...). Write "none" if the table has no such column, and where the value comes from instead (for example "pressure: ISS cabin, from the description").

| PSI ID | Investigation | Table rows | O2 column | P column or source | Flow column | Fuel column | Outcome column | Notes (units, codes, gaps) | Done by |
|---|---|---|---|---|---|---|---|---|---|
| PSI-26 | BASS | | | | | | | | |
| PSI-25 | BASS-II | 130 | `Calibrated initial O2 % by vol` | not in table (ISS cabin) | `Flow restrictor`, `Fan display`, `Air display` (codes, need conversion; tunnel up to 40 cm/s) | `Fuel Sample Material` (free text) | none seen (check) | Oxygen varied below 21 % by adding nitrogen | Claude, 12:50 |
| PSI-98 | Saffire-I | | | | | | | | |
| PSI-99 | Saffire-II | | | | | | | | |
| PSI-100 | Saffire-III | | | | | | | | |
| PSI-107 | SPICE | | | | | | | | |
| PSI-20 | ACME BRE | | | | | | | | |
| PSI-102 | SAME | | | | | | | | |
| PSI-101 | SAME-R | | | | | | | | |
| PSI-47 | DAFT and DAFT-2 | | | | | | | | |
| PSI-69 | FLEX | | | | | | | | |
| PSI-68 | FLEX-2 | | | | | | | | |
| PSI-39 | CFI | | | | | | | | |
| PSI-159 | ACME CFI-G | | | | | | | | |
| PSI-22 | ACME E-FIELD Flames | | | | | | | | |
| PSI-10 | ACME Flame Design | | | | | | | | |
| PSI-21 | ACME CLD Flame | | | | | | | | |
| PSI-23 | ACME s-Flame | | | | | | | | |
| PSI-106 | SLICE | | | | | | | | |

## Order of work

1. Start with BASS, BASS-II, Saffire I to III, SAME, FLEX, FLEX-2, CFI. These cover prevention, detection and suppression.
2. Tell Laila after each 3 investigations so the loader can follow.
3. If a table has no oxygen or no fuel column, say so in the notes. "No evidence" for that condition is a valid result.
