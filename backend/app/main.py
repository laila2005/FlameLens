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
from .schemas import AlternativesRequest, CampaignRequest, RankRequest, Target, TargetRequest, VerifyRequest

app = FastAPI(title="FlameLens", description="Evidence-backed decisions from NASA PSI combustion data")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

CHALLENGE = "Official challenge text (Flame in Freefall, NASA Space Apps 2026)"
HABITATS = [
    {"id": "moon-base", "name": "Moon base", "o2_pct": 30, "pressure_psi": 10.2, "airflow_cm_s": 12.9, "gravity_g": 0.16,
     "fuel_state": "any", "sourced": True,
     "note": "Challenge text: Moon Base oxygen likely 30 % or greater at 10.2 psi or less. Airflow 12.9 cm/s = median of all NASA runs with recorded airflow.",
     "source": CHALLENGE},
    {"id": "pressurized-rover", "name": "Pressurized rover", "o2_pct": 30, "pressure_psi": 10.2, "airflow_cm_s": 8.1,
     "gravity_g": 0.16, "fuel_state": "solid", "sourced": True,
     "note": "Challenge text: rovers like the Moon Base, 30 % oxygen or greater at 10.2 psi or less. Airflow 8.1 cm/s = median of the 352 NASA solid-material runs with recorded airflow (BASS, BASS-II, Saffire, SAME).",
     "source": CHALLENGE},
    {"id": "spacesuit", "name": "Spacesuit", "o2_pct": 100, "pressure_psi": 4.3, "airflow_cm_s": None, "gravity_g": 0.16,
     "fuel_state": "solid", "sourced": True,
     "note": "Challenge text: spacesuits are filled with 100 % oxygen at 4.3 psi.", "source": CHALLENGE},
    {"id": "iss-cabin", "name": "ISS cabin", "o2_pct": 21, "pressure_psi": 14.7, "airflow_cm_s": 12.9, "gravity_g": 0,
     "fuel_state": "any", "sourced": False,
     "note": "Earth-like air (14.7 psi is Earth sea level, from the challenge text). ISS cabin values not separately sourced. Airflow 12.9 cm/s = median of NASA runs with recorded airflow.",
     "source": ""},
    {"id": "mars-habitat", "name": "Mars habitat", "o2_pct": 30, "pressure_psi": 10.2, "airflow_cm_s": 12.9, "gravity_g": 0.38,
     "fuel_state": "any", "sourced": False,
     "note": "Assumed similar to the Moon base; no Mars atmosphere value is given in the challenge text.", "source": ""},
]


@app.get("/api/health", tags=["meta"], summary="Service status and data size")
def health():
    return {"status": "ok", "runs": len(data.runs()), "investigations": len(data.investigations())}


@app.get("/api/habitats", tags=["meta"], summary="Habitat presets; 'sourced' says whether the values come from the challenge text")
def habitats():
    return HABITATS


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


MISSION = ["iss-cabin", "spacesuit", "pressurized-rover", "moon-base"]  # Artemis-style order: cabin, EVA, rover, base


@app.post("/api/journey", tags=["engine"], summary="Mission atmosphere journey: evidence for each stage; the weakest stage is flagged")
def journey(req: CampaignRequest):
    if req.targets:
        stages = [{"id": t.id, "name": t.name, "target": t.target} for t in req.targets]
    else:
        keys = ("o2_pct", "pressure_psi", "airflow_cm_s", "gravity_g", "fuel_state")
        by_id = {h["id"]: h for h in HABITATS}
        stages = [{"id": i, "name": by_id[i]["name"], "target": Target(**{k: by_id[i][k] for k in keys})} for i in MISSION]
    return engine.journey(stages)


@app.post("/api/closest", tags=["engine"], summary="When nothing matches: the closest runs NASA did fly, and exactly what differs")
def closest(req: TargetRequest):
    return engine.closest_evidence(req.target)


@app.post("/api/campaign", tags=["engine"], summary="Test campaign planner: n experiments giving the most designs a whole-design test")
def campaign(req: CampaignRequest):
    if req.targets:
        targets = [{"id": t.id, "name": t.name, "target": t.target} for t in req.targets]
    else:
        keys = ("o2_pct", "pressure_psi", "airflow_cm_s", "gravity_g", "fuel_state")
        targets = [{"id": h["id"], "name": h["name"], "target": Target(**{k: h[k] for k in keys})} for h in HABITATS]
    return engine.campaign(targets, req.n)


@app.post("/api/strength", tags=["engine"], summary="Evidence strength 0-100 per condition (not a safety rating)")
def strength(req: TargetRequest):
    return engine.strength(req.target)


@app.post("/api/explain", tags=["ai"], summary="Cited explanation: cached or live open model, else a template; always verified")
def explain(req: TargetRequest):
    from . import explain as ex
    return ex.explain(req.target)


@app.post("/api/verify", tags=["ai"], summary="Run the citation verifier on any claims for a habitat")
def verify_claims(req: VerifyRequest):
    from . import explain as ex
    pack = ex.retrieve(req.target)
    kept, removed = ex.verify(req.claims, pack)
    return {"claims": kept, "removed": removed, "removed_count": len(removed), "retrieved_run_ids": pack["run_ids"]}


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


@app.get("/api/lens/spread", tags=["lenses"], summary="Measured microgravity flame spread and regression rates vs airflow")
def lens_spread():
    return lenses.spread()


@app.get("/api/lens/smokepoint", tags=["lenses"], summary="SPICE microgravity smoke points per flame (luminous length vs air rate)")
def lens_smokepoint():
    return lenses.smokepoint()


@app.get("/api/detect/evidence", tags=["detect"], summary="Real NASA numbers behind the early-detection simulation")
def detect_evidence():
    from . import detect
    return detect.evidence()


@app.get("/api/lens/coverage", tags=["lenses"], summary="Oxygen vs pressure of every tested run (coverage map)")
def lens_coverage():
    return lenses.coverage_points()


# ---------------------------------------------------------------- investigation profiles and export
# Summaries and comparisons asked for in the challenge text (docs/challenge-statement.md).

@app.get("/api/investigations", tags=["investigations"], summary="Summary profile of every combustion investigation")
def investigations():
    from . import profiles
    return profiles.all_profiles()


@app.get("/api/investigations/{psi_id}", tags=["investigations"], summary="Full profile: objectives, approach, conditions, what varied")
def investigation_profile(psi_id: str):
    from . import profiles
    p = profiles.profile(psi_id)
    if p is None:
        raise HTTPException(status_code=404, detail=f"Unknown investigation {psi_id}")
    return p


@app.get("/api/compare", tags=["investigations"], summary="What is the same and what differs between two investigations")
def compare_investigations(a: str, b: str):
    from . import profiles
    out = profiles.compare(a, b)
    if out is None:
        raise HTTPException(status_code=404, detail=f"Unknown investigation {a} or {b}")
    return out


@app.get("/api/modeling", tags=["investigations"], summary="Ground and CFD modeling investigations in PSI built on the flight datasets")
def modeling_investigations():
    from . import profiles
    studies = profiles.modeling_studies()
    return {
        "count": len(studies),
        "note": "Ground/CFD modeling studies in NASA PSI that consume spaceflight datasets (BASS, BASS-II, SPICE, SAME, FLEX). Kept separate from runs.csv so the Evidence Case counts only physical burn experiments.",
        "studies": studies,
    }


@app.get("/api/papers", tags=["investigations"], summary="Peer-reviewed NASA NTRS publications linked to PSI combustion investigations")
def ntrs_papers():
    items = data.papers()
    return {"count": len(items), "papers": items}


@app.get("/api/export/runs.csv", tags=["export"], summary="Download the curated run table (CSV) for predictive modeling")
def export_runs():
    from fastapi.responses import Response
    body = data.RUNS_CSV.read_text(encoding="utf-8")
    return Response(content=body, media_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="flamelens_runs.csv"'})


@app.get("/api/export/spread_rates.csv", tags=["export"], summary="Download measured microgravity flame spread rates (CSV)")
def export_spread_rates():
    from fastapi.responses import Response
    body = data.SPREAD_CSV.read_text(encoding="utf-8")
    return Response(content=body, media_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="flamelens_spread_rates.csv"'})


@app.get("/api/export/papers.csv", tags=["export"], summary="Download NASA NTRS paper library (CSV)")
def export_papers():
    from fastapi.responses import Response
    body = data.PAPERS_CSV.read_text(encoding="utf-8")
    return Response(content=body, media_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="flamelens_ntrs_papers.csv"'})


@app.get("/api/export/investigations.json", tags=["export"], summary="Download all investigation profiles (JSON)")
def export_investigations():
    from fastapi.responses import JSONResponse
    from . import profiles
    return JSONResponse(content=profiles._profiles(),
                        headers={"Content-Disposition": 'attachment; filename="flamelens_investigations.json"'})


FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
else:
    @app.get("/", include_in_schema=False)
    def root():
        return {"app": "FlameLens API", "docs": "/docs", "health": "/api/health", "note": "frontend/dist not built yet"}
