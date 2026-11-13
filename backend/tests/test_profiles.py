"""Investigation profiles, compare and export routes."""
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_profiles_list():
    items = client.get("/api/investigations").json()
    assert len(items) >= 19
    ids = {p["psi_id"] for p in items}
    assert {"PSI-25", "PSI-26", "PSI-69", "PSI-102", "PSI-159"} <= ids
    assert all("objectives" not in p and "objectives_summary" in p for p in items)


def test_bass2_profile():
    p = client.get("/api/investigations/PSI-25").json()
    assert p["hardware_group"] == "MSG flow duct (SPICE duct)"
    assert p["pillar"] == "Prevention"
    assert "o2" in p["varied"]
    assert p["n_runs"] == 129
    assert p["objectives"] and len(p["objectives_summary"]) <= 351


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
    assert len(lines) - 1 == 1922


def test_export_investigations_json():
    r = client.get("/api/export/investigations.json")
    assert r.status_code == 200
    assert len(r.json()) >= 19


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
