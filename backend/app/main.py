"""FlameLens API.

Deterministic evidence engine over the curated NASA PSI combustion runs. AI is not used here.
Run from the repo root: uvicorn backend.app.main:app --reload
"""
from collections import Counter
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import data, engine, lenses
from .schemas import AlternativesRequest, RankRequest, TargetRequest

app = FastAPI(title="FlameLens", description="Evidence-backed decisions from NASA PSI combustion data")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

HABITATS = [
    {"id": "iss-cabin", "name": "ISS cabin", "o2_pct": 21, "pressure_psi": 14.7, "airflow_cm_s": 10, "gravity_g": 0, "fuel_state": "any"},
    {"id": "lunar-rover", "name": "Lunar rover", "o2_pct": 34, "pressure_psi": 10.2, "airflow_cm_s": 10, "gravity_g": 0.16, "fuel_state": "solid"},
    {"id": "lunar-base", "name": "Lunar base", "o2_pct": 30, "pressure_psi": 10.2, "airflow_cm_s": 15, "gravity_g": 0.16, "fuel_state": "any"},
    {"id": "mars-habitat", "name": "Mars habitat", "o2_pct": 30, "pressure_psi": 8.2, "airflow_cm_s": 10, "gravity_g": 0.38, "fuel_state": "any"},
]
PRESET_NOTE = "Example values, not yet sourced. Confirm against an official source before presenting them as real mission atmospheres."


@app.get("/api/health", tags=["meta"], summary="Service status and data size")
def health():
    return {"status": "ok", "runs": len(data.runs()), "investigations": len(data.investigations())}


@app.get("/api/habitats", tags=["meta"], summary="Habitat presets (examples, not sourced)")
def habitats():
    return [{**h, "sourced": False, "note": PRESET_NOTE} for h in HABITATS]


@app.get("/api/stats", tags=["meta"], summary="Counts by pillar, fuel state and basis, plus value ranges")
def stats():
    rows = data.runs()
    rng = data.ranges(rows)
    return {
        "runs": len(rows),
        "by_pillar": dict(Counter(r["pillar"] for r in rows)),
        "by_fuel_state": dict(Counter(r["fuel_state"] for r in rows)),
        "by_investigation": dict(Counter(r["investigation"] for r in rows)),
        "o2_basis": dict(Counter(r["o2_basis"] for r in rows)),
        "pressure_basis": dict(Counter(r["pressure_basis"] for r in rows)),
        "airflow_basis": dict(Counter(r["airflow_basis"] for r in rows)),
        "confidence": dict(Counter(r["confidence"] for r in rows)),
        "ranges": {"o2_pct": list(rng["o2_pct"]), "pressure_psi": list(rng["pressure_psi"]), "airflow_cm_s": list(rng["airflow_cm_s"])},
    }


@app.post("/api/rank", tags=["engine"], summary="Rank investigations against a habitat")
def rank(req: RankRequest):
    return engine.rank(req.target, req.weights, req.k)


@app.post("/api/case", tags=["engine"], summary="Evidence case: supported, weak or no evidence per condition")
def case(req: TargetRequest):
    return engine.case(req.target)


@app.post("/api/next", tags=["engine"], summary="The experiment that closes the most gaps")
def next_experiment(req: TargetRequest):
    return engine.next_experiment(req.target)


@app.post("/api/alternatives", tags=["engine"], summary="Nearest tested conditions with lower oxygen partial pressure")
def alternatives(req: AlternativesRequest):
    return engine.alternatives(req.target, req.k)


@app.post("/api/strength", tags=["engine"], summary="Evidence strength 0-100 per condition (not a safety rating)")
def strength(req: TargetRequest):
    return engine.strength(req.target)


@app.get("/api/coverage", tags=["engine"], summary="Is this atmosphere inside the tested range? Nearest runs")
def coverage(o2: float, psi: float):
    return engine.coverage(o2, psi)


@app.get("/api/evidence/{run_id}", tags=["data"], summary="One run with its source, DOI and license")
def evidence(run_id: str):
    run = data.run_by_id(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Unknown run_id {run_id}")
    inv = data.investigations().get(run["psi_id"], {})
    return {"run": run, "investigation": {"psi_id": run["psi_id"], "title": inv.get("title"), "acronym": inv.get("acronym"),
                                          "doi": inv.get("doi"), "license": inv.get("license"), "project_type": inv.get("project_type")}}


@app.get("/api/investigation/{psi_id}", tags=["data"], summary="Investigation metadata, outcome counts and first 50 runs")
def investigation(psi_id: str):
    inv = data.investigations().get(psi_id)
    runs = [r for r in data.runs() if r["psi_id"] == psi_id]
    if inv is None and not runs:
        raise HTTPException(status_code=404, detail=f"Unknown investigation {psi_id}")
    return {
        "psi_id": psi_id, "metadata": inv, "n_runs": len(runs),
        "outcome_counts": dict(Counter(r["outcome"] for r in runs)),
        "runs": runs[:50],
    }


@app.get("/api/lens/coolflame", tags=["lenses"], summary="Cool-flame regime points (CFI, ACME CFI-G, FLEX)")
def lens_coolflame():
    return lenses.coolflame()


@app.get("/api/lens/aerosol", tags=["lenses"], summary="Measured smoke and dust particle sizes")
def lens_aerosol():
    return lenses.aerosol()


@app.get("/api/lens/tested", tags=["lenses"], summary="Oxygen vs airflow scatter of tested conditions")
def lens_tested():
    return lenses.tested()


@app.get("/api/lens/coverage", tags=["lenses"], summary="Oxygen vs pressure of every tested run (coverage map)")
def lens_coverage():
    return lenses.coverage_points()


FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
else:
    @app.get("/", include_in_schema=False)
    def root():
        return {"app": "FlameLens API", "docs": "/docs", "health": "/api/health", "note": "frontend/dist not built yet"}
