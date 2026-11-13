# Data folder

| Folder | What goes here | In git? |
|---|---|---|
| `mock/` | Placeholder data in our row format. **Every value is invented.** Used to build the app before real data arrives | Yes |
| `raw/` | Real PSI downloads at kickoff | No (git-ignored). Share large files through the team drive |
| `curated/` | Our cleaned, sourced CSVs after kickoff | Yes |

Format and rules: [docs/06-data-guide.md](../docs/06-data-guide.md).

`mock/runs_placeholder.csv` has 20 rows, all with `confidence = placeholder` and `source_ref = placeholder`. The app must show a "sample data" banner while any of them is loaded. Never quote a placeholder value in the pitch, slides or video.

## Real data (13 Nov)

| File | What |
|---|---|
| `curated/runs.csv` | 1,922 runs from 13 PSI investigations, one schema. **This is the table the app uses** |
| `curated/investigations.csv` | 26 PSI investigations with DOIs and license (cite the DOI) |
| `curated/smoke_dust_sizes.csv` | Smoke and dust particle sizes for Lens 2, from the SAME-R and DAFT reports |
| `raw/` | Downloaded PSI tables and documents (git-ignored). Rebuild with `scripts/fetch_psi.py`, `scripts/fetch_psi_docs.py`, then `scripts/build_runs.py` |

What each column means and what is missing: [docs/research/dashboard-data-map.md](../docs/research/dashboard-data-map.md). `mock/runs_placeholder.csv` is now only a fallback for tests.
