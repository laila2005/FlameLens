# Data folder

| Folder | What goes here | In git? |
|---|---|---|
| `mock/` | Placeholder data in our row format. **Every value is invented.** Used to build the app before real data arrives | Yes |
| `raw/` | Real PSI downloads at kickoff | No (git-ignored). Share large files through the team drive |
| `curated/` | Our cleaned, sourced CSVs after kickoff | Yes |

Format and rules: [docs/06-data-guide.md](../docs/06-data-guide.md).

`mock/runs_placeholder.csv` has 20 rows, all with `confidence = placeholder` and `source_ref = placeholder`. The app must show a "sample data" banner while any of them is loaded. Never quote a placeholder value in the pitch, slides or video.
