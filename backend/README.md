# FlameLens backend

FastAPI service over `data/curated/runs.csv` (1,922 PSI combustion runs). The decision routes are deterministic, no AI.

## Run

From the repo root:

```bash
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

Open http://localhost:8000/docs for the interactive API page. If `frontend/dist` exists it is served at `/`.

## Test

```bash
python -m pytest backend/tests -q
```

## Routes

| Method and path | What it does |
|---|---|
| `GET /api/health` | Status, number of runs and investigations |
| `GET /api/habitats` | Four habitat presets (examples, `sourced: false`) |
| `GET /api/stats` | Counts by pillar, fuel state, basis, confidence, and value ranges |
| `POST /api/rank` | Rank investigations against a habitat `{target, weights?, k?}` |
| `POST /api/case` | Evidence case: Supported, Weak or No evidence per condition, plus the whole habitat |
| `POST /api/next` | The experiment that closes the most gaps, with the nearest run |
| `POST /api/alternatives` | Nearest tested conditions with lower oxygen partial pressure `{target, k?}` |
| `POST /api/strength` | Evidence strength 0 to 100 per condition (not a safety rating) |
| `GET /api/coverage?o2=&psi=` | Inside or outside the tested range, nearest runs |
| `GET /api/evidence/{run_id}` | One run with its source, DOI and license |
| `GET /api/investigation/{psi_id}` | Investigation metadata, outcome counts, first 50 runs |
| `GET /api/lens/coolflame` | Cool-flame regime points (CFI, ACME CFI-G, FLEX) and an oxygen x pressure grid |
| `GET /api/lens/aerosol` | Measured smoke and dust particle sizes |
| `GET /api/lens/tested` | Oxygen vs airflow scatter of tested conditions (replaces the spread-rate lens) |

`target` is `{o2_pct, pressure_psi, airflow_cm_s?, gravity_g, fuel_state}` with `fuel_state` one of `solid`, `liquid`, `gas`, `any`.

## Examples

```bash
curl http://localhost:8000/api/health
curl -X POST http://localhost:8000/api/case -H "Content-Type: application/json" \
  -d '{"target":{"o2_pct":34,"pressure_psi":10.2,"airflow_cm_s":10,"gravity_g":0.16,"fuel_state":"solid"}}'
curl "http://localhost:8000/api/coverage?o2=34&psi=10.2"
curl http://localhost:8000/api/evidence/PSI-69-0001
```

Real example responses for every route are in [docs/design/mock-json](../docs/design/mock-json), so the frontend can be built against the true shapes.

## Deploy

`Dockerfile` and `render.yaml` at the repo root. The image holds `backend/` and `data/curated/` only. If `frontend/package.json` exists the image builds the frontend and serves it.

## Deploy on Vercel

Live: https://flamelens-steel.vercel.app (Vercel project `flamelens`, account `laila-mohameds-projects`).

How it is set up:
- `frontend/dist` is served as static files (no build step).
- `api/index.py` is a Python serverless function that imports the FastAPI app (`backend.app.main:app`). It bundles `backend/**` and `data/curated/**` (`vercel.json`, `functions.includeFiles`).
- `vercel.json` rewrites `/api/(.*)`, `/docs` and `/openapi.json` to that function; the original path is kept, so the routes work unchanged.
- `requirements.txt` at the repo root lists only what the function needs (fastapi, pydantic). `.vercelignore` keeps `data/raw` and caches out of the upload.

Redeploy from the repo root (Vercel CLI logged in to the account):

```bash
vercel deploy --prod --yes
```

The repo is linked to the project in `.vercel/` (git-ignored). On a new computer run `vercel link --yes --project flamelens` first. The deploy uploads the working tree, so commit and test before deploying.
