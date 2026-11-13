"""Investigation profiles, compare, spread lens, papers, and export routes."""
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_profiles_list():
    items = client.get("/api/investigations").json()
    assert len(items) == 19
    ids = {p["psi_id"] for p in items}
    assert {"PSI-21", "PSI-22", "PSI-23", "PSI-25", "PSI-26", "PSI-47", "PSI-68", "PSI-69", "PSI-102", "PSI-106", "PSI-159"} <= ids
    assert all("objectives" not in p and "objectives_summary" in p for p in items)


def test_bass2_profile():
    p = client.get("/api/investigations/PSI-25").json()
    assert p["hardware_group"] == "MSG flow duct (SPICE duct)"
    assert p["pillar"] == "Prevention"
    assert "o2" in p["varied"]
    assert p["n_runs"] == 129
    assert p["outcome_counts"].get("quenched", 0) >= 15
    assert p["outcome_counts"].get("no ignition", 0) >= 8
    assert p["objectives"] and len(p["objectives_summary"]) <= 351
    assert len(p["papers"]) >= 1


def test_remaining_psis_analyzed():
    # PSI-23 ACME s-Flame has ~21% and ~30% O2 spherical flame days
    sflame = client.get("/api/investigations/PSI-23").json()
    assert sflame["n_runs"] == 23
    assert sflame["ranges"]["o2_pct"] == [21.0, 30.0]

    # PSI-21 ACME CLD (32 days) and PSI-22 ACME E-FIELD (20 deduplicated days)
    assert client.get("/api/investigations/PSI-21").json()["n_runs"] == 32
    assert client.get("/api/investigations/PSI-22").json()["n_runs"] == 20

    # PSI-106 SLICE (12 days) and PSI-47 DAFT (2 flight sessions)
    assert client.get("/api/investigations/PSI-106").json()["n_runs"] == 12
    assert client.get("/api/investigations/PSI-47").json()["n_runs"] == 2

    # PSI-68 FLEX-2 stays n_runs == 0 with explicit 8-fuel planned_matrix
    flex2 = client.get("/api/investigations/PSI-68").json()
    assert flex2["n_runs"] == 0
    assert len(flex2["planned_matrix"]["fuels"]) == 8
    assert flex2["planned_matrix"]["o2_pct_levels"] == [17.0, 21.0, 25.0, 30.0]


def test_unknown_profile_404():
    assert client.get("/api/investigations/PSI-9999").status_code == 404
    assert client.get("/api/compare?a=PSI-25&b=PSI-9999").status_code == 404


def test_compare():
    c = client.get("/api/compare?a=PSI-25&b=PSI-26").json()
    assert c["a"]["psi_id"] == "PSI-25" and c["b"]["psi_id"] == "PSI-26"
    fields_same = {x["field"] for x in c["same"]}
    assert "hardware_group" in fields_same and "pillar" in fields_same
    assert isinstance(c["different"], list)
    assert set(c["measurements"]) == {"shared", "only_a", "only_b"}


def test_export_runs_csv():
    r = client.get("/api/export/runs.csv")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    assert "flamelens_runs.csv" in r.headers["content-disposition"]
    lines = [l for l in r.text.splitlines() if l.strip()]
    assert lines[0].startswith("run_id,")
    assert len(lines) - 1 == 2003


def test_spread_lens_and_exports():
    sp = client.get("/api/lens/spread").json()
    assert sp["n_points"] == 43
    assert set(sp["counts_by_investigation"]) == {"BASS-II", "Saffire-II"}
    assert sp["spread_rate_range_mm_s"][0] == pytest.approx(0.012)
    assert sp["spread_rate_range_mm_s"][1] == pytest.approx(2.6)

    exp_sp = client.get("/api/export/spread_rates.csv")
    assert exp_sp.status_code == 200 and "SPR-001" in exp_sp.text

    papers = client.get("/api/papers").json()
    assert papers["count"] >= 25
    exp_pp = client.get("/api/export/papers.csv")
    assert exp_pp.status_code == 200 and "ntrs.nasa.gov" in exp_pp.text


def test_export_investigations_json():
    r = client.get("/api/export/investigations.json")
    assert r.status_code == 200
    assert len(r.json()) == 19


def test_modeling_studies_endpoint_and_links():
    m = client.get("/api/modeling").json()
    assert m["count"] == 5
    mod_ids = {s["psi_id"] for s in m["studies"]}
    assert mod_ids == {"PSI-60", "PSI-62", "PSI-115", "PSI-117", "PSI-142"}
    assert all(s["doi"] and s["uses_flight_psi_ids"] for s in m["studies"])

    # FLEX (PSI-69) should link to PSI-117 and PSI-142; BASS-II (PSI-25) to PSI-62
    flex = client.get("/api/investigations/PSI-69").json()
    assert {s["psi_id"] for s in flex["modeling_studies"]} == {"PSI-117", "PSI-142"}
    bass2 = client.get("/api/investigations/PSI-25").json()
    assert {s["psi_id"] for s in bass2["modeling_studies"]} == {"PSI-62"}

    # Ensure ground/CFD modeling studies never pollute physical flight runs in runs.csv
    runs_csv = client.get("/api/export/runs.csv").text
    for mid in mod_ids:
        assert f",{mid}," not in runs_csv
