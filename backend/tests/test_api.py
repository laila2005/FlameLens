"""API tests. Run from the repo root: python -m pytest backend/tests/test_api.py -q"""
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

LUNAR = {"o2_pct": 34, "pressure_psi": 10.2, "airflow_cm_s": 10, "gravity_g": 0.16, "fuel_state": "solid"}
ISS = {"o2_pct": 21, "pressure_psi": 14.7, "airflow_cm_s": 10, "gravity_g": 0, "fuel_state": "any"}


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok" and body["runs"] > 1000 and body["investigations"] == 26


def test_habitats():
    r = client.get("/api/habitats")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 4
    assert all(h["sourced"] is False and h["note"] for h in items)
    assert {h["name"] for h in items} == {"ISS cabin", "Lunar rover", "Lunar base", "Mars habitat"}


def test_evidence_found_and_missing():
    ok = client.get("/api/evidence/PSI-69-0001")
    assert ok.status_code == 200
    body = ok.json()
    assert body["run"]["psi_id"] == "PSI-69"
    assert body["investigation"]["doi"].startswith("10.")
    assert body["investigation"]["license"] == "CC0-1.0"
    assert client.get("/api/evidence/NOPE-0000").status_code == 404


def test_stats():
    body = client.get("/api/stats").json()
    assert body["runs"] > 1000
    assert set(body["by_pillar"]) >= {"Prevention", "Detection", "Suppression"}
    assert set(body["o2_basis"]) >= {"measured"}
    assert body["ranges"]["o2_pct"][0] < body["ranges"]["o2_pct"][1]


def test_investigation():
    body = client.get("/api/investigation/PSI-25").json()
    assert body["psi_id"] == "PSI-25" and body["n_runs"] == 129
    assert len(body["runs"]) == 50 and body["metadata"]["doi"]
    assert client.get("/api/investigation/PSI-9999").status_code == 404


def test_lens_coolflame():
    body = client.get("/api/lens/coolflame").json()
    assert body["counts_by_outcome"].get("cool_flame", 0) >= 50
    assert all(p["o2_pct"] is not None and p["pressure_psi"] is not None for p in body["points"])
    assert body["regime_grid"] and body["n_points"] == len(body["points"])


def test_lens_aerosol():
    body = client.get("/api/lens/aerosol").json()
    kapton = next(s for s in body["smoke"] if s["material"] == "Kapton")
    assert kapton["fresh"]["geometric_mean_um"] == pytest.approx(0.042)
    assert kapton["aged_720s"]["geometric_mean_um"] == pytest.approx(0.089)
    assert body["dust"][0]["count_mean_um"] == pytest.approx(1.65)
    assert "overlap_note" in body


def test_lens_tested():
    body = client.get("/api/lens/tested").json()
    assert 600 < body["n_points"] < 800
    assert all(p["o2_pct"] is not None and p["airflow_cm_s"] is not None for p in body["points"])


# ---- engine-backed routes (need fork A's engine) ----

def test_rank():
    r = client.post("/api/rank", json={"target": ISS, "k": 5})
    assert r.status_code == 200
    items = r.json()
    assert 1 <= len(items) <= 5
    assert items[0]["score"] >= items[-1]["score"]
    assert {"psi_id", "score", "breakdown"} <= set(items[0])


def test_case_lunar_rover_has_no_gravity_evidence():
    r = client.post("/api/case", json={"target": LUNAR})
    assert r.status_code == 200
    body = r.json()
    grav = next(c for c in body["conditions"] if c["key"] == "grav")
    assert grav["status"] == "No evidence"
    assert body["whole"]["status"] == "No evidence"


def test_case_iss_is_well_covered():
    body = client.post("/api/case", json={"target": ISS}).json()
    assert body["supported_count"] >= 4
    assert body["whole"]["n"] > 0


def test_next():
    body = client.post("/api/next", json={"target": LUNAR}).json()
    assert body["needed"] is True and "grav" in body["gaps"] and body["nearest_run"]["run_id"]


def test_alternatives():
    r = client.post("/api/alternatives", json={"target": LUNAR, "k": 3})
    assert r.status_code == 200
    items = r.json()
    assert len(items) <= 3
    assert all(i["o2_partial_pressure"] < i["target_partial_pressure"] for i in items)


def test_strength():
    body = client.post("/api/strength", json={"target": ISS}).json()
    assert 0 <= body["whole"]["score"] <= 100
    assert "o2" in body["conditions"] and "note" in body


def test_coverage():
    body = client.get("/api/coverage", params={"o2": 21, "psi": 14.7}).json()
    assert body["in_range"] is True and len(body["nearest"]) >= 1


def test_bad_request_is_422():
    assert client.post("/api/case", json={"target": {"o2_pct": 150, "pressure_psi": 10}}).status_code == 422


def test_lens_coverage():
    j = client.get("/api/lens/coverage").json()
    assert j["n_points"] > 1000
    assert all(p["o2_pct"] is not None and p["pressure_psi"] is not None for p in j["points"])


def test_detect_evidence():
    j = client.get("/api/detect/evidence").json()
    assert j["gas"]["n_tests"] > 50
    assert j["gas"]["co_rise_ppm"]["median"] >= 0
    assert j["particles"]["dust_mean_um"] == 1.65
    assert j["cool_flames"]["n_cool_flame_runs"] >= 50
