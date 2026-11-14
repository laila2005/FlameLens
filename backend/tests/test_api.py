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
    assert len(items) == 5
    assert all(h["note"] for h in items)
    names = {h["name"]: h for h in items}
    assert set(names) == {"Moon base", "Pressurized rover", "Spacesuit", "ISS cabin", "Mars habitat"}
    assert names["Moon base"]["sourced"] is True and names["Moon base"]["o2_pct"] == 30 and names["Moon base"]["pressure_psi"] == 10.2
    # ISS cabin and Mars habitat now cite NASA documents (OCHMO-TB-003 p. 8; NTRS 20220005716 slide 39)
    assert names["ISS cabin"]["sourced"] is True and "OCHMO-TB-003" in names["ISS cabin"]["note"]
    mars = names["Mars habitat"]
    assert mars["sourced"] is True and mars["o2_pct"] == 34 and mars["pressure_psi"] == 8.2 and "20220005716" in mars["note"]


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


# ------------------------------------------------------------ campaign planner

def test_campaign_presets_plan_covers_every_open_design():
    r = client.post("/api/campaign", json={"n": 3}).json()
    habs = {h["id"]: h for h in r["habitats"]}
    assert habs["iss-cabin"]["status"] == "covered" and habs["iss-cabin"]["planned_by"] is None  # ISS needs no new test
    first = r["experiments"][0]
    # Moon base and the pressurized rover share one lunar-gravity experiment (same O2, pressure, gravity)
    assert set(first["covers"]) == {"moon-base", "pressurized-rover"}
    assert first["conditions"]["gravity_g"] == 0.16 and first["partial_gravity"] is True
    assert "grav" in first["gaps_closed"] and "whole" in first["gaps_closed"]
    assert r["summary"]["still_open"] == [] and r["summary"]["covered_or_planned"] == 5


def test_campaign_respects_n_and_reports_open_designs():
    r = client.post("/api/campaign", json={"n": 1}).json()
    assert len(r["experiments"]) == 1
    assert set(r["summary"]["still_open"]) == {"Spacesuit", "Mars habitat"}


def test_campaign_starting_runs_are_real_and_conditions_come_from_designs():
    from backend.app import data
    ids = {row["run_id"] for row in data.runs()}
    r = client.post("/api/campaign", json={"n": 5}).json()
    for e in r["experiments"]:
        assert e["nearest_run"]["run_id"] in ids
        assert e["conditions"]["fuel_state"] in {"solid", "liquid", "gas"}  # a real burn needs a real material
        assert e["o2_partial_pressure"] == round(e["conditions"]["o2_pct"] * e["conditions"]["pressure_psi"] / 100, 2)


def test_campaign_custom_targets_and_nothing_needed():
    iss = {"id": "iss", "name": "ISS", "target": ISS}
    r = client.post("/api/campaign", json={"n": 3, "targets": [iss]}).json()
    assert r["experiments"] == [] and r["summary"]["covered_now"] == 1
    lunar = {"id": "lunar", "name": "Lunar", "target": LUNAR}
    r = client.post("/api/campaign", json={"n": 3, "targets": [iss, lunar]}).json()
    assert [e["covers"] for e in r["experiments"]] == [["lunar"]]


# ------------------------------------------------------------ closest evidence

ROVER = {"o2_pct": 30, "pressure_psi": 10.2, "airflow_cm_s": 8.1, "gravity_g": 0.16, "fuel_state": "solid"}


def test_closest_explains_the_rover_gap_with_real_runs():
    from backend.app import data
    by_id = {row["run_id"]: row for row in data.runs()}
    r = client.post("/api/closest", json={"target": ROVER}).json()
    assert r["needed"] is True and r["groups"]
    flex = [g for g in r["groups"] if set(g["relaxed"]) == {"flow", "fuel"}]
    assert flex and flex[0]["investigations"][0]["name"] == "FLEX"  # same atmosphere, liquid droplets
    for g in r["groups"]:
        for rid in g["run_ids"]:
            row = by_id[rid]
            assert row["gravity_g"] == 0  # PSI is microgravity only
            if "o2" in g["kept"] or "oxygen" in g["same"]:
                assert abs(row["o2_pct"] - 30) <= 6
            if "pressure" in g["same"]:
                assert abs(row["pressure_psi"] - 10.2) <= 2
    assert "LUCI" in r["gravity_note"]


def test_closest_not_needed_when_design_is_matched():
    r = client.post("/api/closest", json={"target": ISS}).json()
    assert r["needed"] is False


# ------------------------------------------------------------ mission atmosphere journey

def test_journey_default_mission_order_and_weakest_stage():
    r = client.post("/api/journey", json={}).json()
    assert [s["id"] for s in r["stages"]] == ["iss-cabin", "spacesuit", "pressurized-rover", "moon-base"]
    iss = r["stages"][0]
    assert iss["status"] == "Supported" and iss["whole_n"] >= 2 and not iss["weakest"]
    weak = [s for s in r["stages"] if s["weakest"]]
    assert len(weak) == 1 and weak[0]["id"] == r["weakest"] == "spacesuit"  # fewest supported conditions among the 0-strength stages
    assert r["mission_strength"] == min(s["strength"] for s in r["stages"])
    assert r["summary"]["fully_backed"] == 1


def test_journey_stage_numbers_match_single_design_routes():
    r = client.post("/api/journey", json={}).json()
    rover = next(s for s in r["stages"] if s["id"] == "pressurized-rover")
    t = rover["target"]
    case = client.post("/api/case", json={"target": t}).json()
    st = client.post("/api/strength", json={"target": t}).json()
    assert rover["whole_n"] == case["whole"]["n"] and rover["verdict"] == case["verdict"]
    assert rover["strength"] == round(st["whole"]["score"], 1)
    assert rover["o2_partial_pressure"] == round(t["o2_pct"] * t["pressure_psi"] / 100, 2)


def test_journey_custom_stages():
    stages = [{"id": "a", "name": "Cabin", "target": ISS}, {"id": "b", "name": "Lunar", "target": LUNAR}]
    r = client.post("/api/journey", json={"targets": stages}).json()
    assert [s["name"] for s in r["stages"]] == ["Cabin", "Lunar"] and r["weakest"] == "b"


# ------------------------------------------------------------ review fixes (14 Nov)

def test_unspecified_airflow_is_not_counted_as_evidence():
    suit = {"o2_pct": 100, "pressure_psi": 4.3, "airflow_cm_s": None, "gravity_g": 0.16, "fuel_state": "solid"}
    c = client.post("/api/case", json={"target": suit}).json()
    flow = next(x for x in c["conditions"] if x["key"] == "flow")
    assert flow["status"] == "Not specified" and c["counted"] == 4
    assert c["verdict"].startswith(f"{c['supported_count']} of 4 conditions supported")
    nx = client.post("/api/next", json={"target": suit}).json()
    assert "flow" not in nx["gaps"]


def test_closest_shows_gravity_only_group_and_never_lists_matching_values_as_different():
    t = {"o2_pct": 21, "pressure_psi": 14.7, "airflow_cm_s": 12.9, "gravity_g": 0.16, "fuel_state": "any"}
    r = client.post("/api/closest", json={"target": t}).json()
    g = r["groups"][0]
    assert g["relaxed"] == [] and g["n"] == 336 and len(g["differs"]) == 1 and "gravity" in g["differs"][0]
    rover = client.post("/api/closest", json={"target": ROVER}).json()
    for grp in rover["groups"]:
        for d in grp["differs"]:
            assert "(yours 14.7 psi)" not in d or not d.startswith("pressure 14.7 psi")


def test_rank_rejects_bad_weights():
    assert client.post("/api/rank", json={"target": ISS, "weights": {"o2": "abc"}}).status_code == 422
    assert client.post("/api/rank", json={"target": ISS, "weights": {"o2": -1}}).status_code == 422
    assert client.post("/api/rank", json={"target": ISS, "weights": {"o2": 0.5}}).status_code == 200


# ------------------------------------------------------------ SPICE smoke points (Dotson thesis, Appendix 6.4)

def test_smokepoint_lens_and_linked_runs():
    from backend.app import data
    d = client.get("/api/lens/smokepoint").json()
    assert d["n_points"] == 55 and d["counts_by_fuel"] == {"ethylene": 6, "propane": 6, "50% propylene": 7, "75% propylene": 14, "propylene": 22}
    by_id = {r["run_id"]: r for r in data.runs()}
    linked = {p["run_id"] for p in d["points"] if p["run_id"]}
    assert len(linked) == d["n_linked_runs"] == 45
    for rid in linked:
        row = by_id[rid]
        assert row["psi_id"] == "PSI-107" and row["outcome"] == "smoke point" and "Appendix 6.4" in row["notes"]
    # values are copied as printed: the first ethylene smoke point in Figure 6.3
    first = next(p for p in d["points"] if p["fuel"] == "ethylene" and p["gmt"] == "15:48:47")
    assert (first["fuel_rate_mg_s"], first["air_rate_cm_s"], first["smoke_point_length_mm"]) == (1.627, 18.53, 36.99)


# ------------------------------------------------------------ evidence outside PSI (Saffire IV-VI, cited, not counted)

def test_beyond_psi_saffire_matches_rover_moon_mars_but_never_counts():
    rover = client.post("/api/closest", json={"target": ROVER}).json()["beyond_psi"]["rows"]
    assert {r["id"] for r in rover} == {"SAFFIRE-V-2", "SAFFIRE-V-3", "SAFFIRE-V-4"}
    v2 = next(r for r in rover if r["id"] == "SAFFIRE-V-2")
    assert (v2["o2_pct"], v2["pressure_kpa"], v2["flow_cm_s"]) == (26.2, 70.7, 20.0)   # ICES-2024-365 Table 1
    assert "airflow" not in v2["same"] and "ntrs.nasa.gov" in v2["source_url"]
    mars = {"o2_pct": 34, "pressure_psi": 8.2, "airflow_cm_s": 12.9, "gravity_g": 0.38, "fuel_state": "any"}
    assert {r["id"] for r in client.post("/api/closest", json={"target": mars}).json()["beyond_psi"]["rows"]} == {"SAFFIRE-VI-2", "SAFFIRE-VI-3", "SAFFIRE-VI-4"}
    # never counted: the rover's evidence case still has 0 whole-design and 0 atmosphere matches
    case = client.post("/api/case", json={"target": ROVER}).json()
    assert case["whole"]["n"] == 0 and case["atmosphere"]["n"] == 0


def test_profiles_show_sourced_condition_notes():
    """Conditions the PSI table leaves empty get sourced NASA statements; every note has a quote and a source."""
    p = client.get("/api/investigations/PSI-100").json()
    notes = {n["condition"]: n for n in p["condition_notes"]}
    assert "21 %" in notes["o2"]["value"] and "ICES-2021-266" in notes["o2"]["source_ref"]
    from backend.app import profiles
    for n in profiles.condition_notes():
        assert n["quote"] and n["source_ref"] and n["source_url"].startswith("https://")
        assert n["condition"] in ("o2", "pressure", "airflow")
