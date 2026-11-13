"""Tests for the decision engine.

Run from the repo root:  python -m pytest backend/tests -q

The hand-checked cases come from docs/design/ranker-cases.md and docs/design/decision-cases.md and use
the placeholder data (data/mock/runs_placeholder.csv). Smoke tests at the bottom use the real table.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.app import data, engine  # noqa: E402
from backend.app.schemas import Target  # noqa: E402

MOCK = data.load_runs(data.ROOT / "data" / "mock" / "runs_placeholder.csv")
MOCK_RNG = data.ranges(MOCK)
BY_ID = {r["run_id"]: r for r in MOCK}


def T(o2, psi, flow, fuel, g):
    return Target(o2_pct=o2, pressure_psi=psi, airflow_cm_s=flow, fuel_state=fuel, gravity_g=g)


# ------------------------------------------------------------ ranker (docs/design/ranker-cases.md)

def test_mock_ranges_match_the_doc():
    assert MOCK_RNG["o2_pct"] == (21.0, 40.0)
    assert MOCK_RNG["pressure_psi"] == (10.2, 14.7)
    assert MOCK_RNG["airflow_cm_s"] == (0.0, 20.0)


@pytest.mark.parametrize("name,target,run_id,no_airflow,expected,used", [
    ("R1", T(34, 10.2, 12, "gas", 0), "PH-05-R01", False, 100.0, 5),
    ("R2", T(21, 14.7, 0, "solid", 0), "PH-08-R01", False, 50.0, 5),
    ("R3", T(21, 14.7, 10, "solid", 0), "PH-02-R03", True, 82.6, 4),
    ("R4", T(30, 10.2, 12, "solid", 0), "PH-05-R02", False, 85.0, 5),
    ("R5", T(34, 10.2, 10, "solid", 0.16), "PH-04-R01", False, 75.3, 5),
])
def test_ranker_hand_checked_cases(name, target, run_id, no_airflow, expected, used):
    run = dict(BY_ID[run_id])
    if no_airflow:
        run["airflow_cm_s"] = None  # missing field: the factor scores a neutral 0.5 (not dropped)
    score, _, factors_used = engine.run_score(target, run, MOCK_RNG)
    assert round(score, 1) == expected
    assert factors_used == used


def test_rank_rolls_up_to_investigations_and_is_sorted():
    out = engine.rank(T(34, 10.2, 12, "gas", 0), rows=MOCK, k=20)
    scores = [x["score"] for x in out]
    assert scores == sorted(scores, reverse=True)
    assert out[0]["psi_id"] == "PH-05"  # the gas burner runs at 34% / 10.2 psi / 12 cm/s
    assert len({x["psi_id"] for x in out}) == len(out)
    assert all(len(x["top_runs"]) <= 3 and set(x["breakdown"]) == set(engine.KEYS) for x in out)
    assert len(engine.rank(T(34, 10.2, 12, "gas", 0), rows=MOCK, k=3)) == 3


def test_rank_custom_weights_change_the_order():
    t = T(21, 14.7, 10, "any", 0)
    by_default = engine.rank(t, rows=MOCK, k=1)[0]
    only_pressure = engine.rank(t, weights={"o2": 0, "psi": 1, "flow": 0, "fuel": 0, "grav": 0}, rows=MOCK, k=1)[0]
    assert only_pressure["score"] == 100.0
    assert by_default["score"] <= 100.0


# ------------------------------------------------------------ evidence case (docs/design/decision-cases.md)

ISS = T(21, 14.7, 10, "any", 0)
ROVER = T(34, 10.2, 10, "solid", 0.16)
MARS = T(30, 8.2, 10, "any", 0.38)


def counts(c):
    return {x["key"]: (x["n"], x["status"]) for x in c["conditions"]}


def test_case_iss_cabin():
    c = engine.case(ISS, rows=MOCK)
    assert counts(c) == {"o2": (11, "Supported"), "psi": (16, "Supported"), "flow": (13, "Supported"),
                         "fuel": (20, "Supported"), "grav": (20, "Supported")}
    assert c["whole"]["n"] == 8
    assert set(c["whole"]["run_ids"]) == {"PH-02-R01", "PH-02-R02", "PH-02-R03", "PH-03-R01", "PH-03-R02",
                                          "PH-06-R01", "PH-06-R02", "PH-07-R01"}
    assert c["supported_count"] == 5
    assert c["verdict"] == "5 of 5 conditions supported, 8 runs match the whole habitat"


def test_case_lunar_rover_has_no_gravity_evidence():
    c = engine.case(ROVER, rows=MOCK)
    assert counts(c) == {"o2": (9, "Supported"), "psi": (4, "Supported"), "flow": (13, "Supported"),
                         "fuel": (13, "Supported"), "grav": (0, "No evidence")}
    assert c["whole"]["n"] == 0 and c["whole"]["status"] == "No evidence"
    assert c["supported_count"] == 4
    assert c["verdict"] == ("4 of 5 conditions supported, no run matches the whole habitat (no gravity evidence); "
                            "even ignoring gravity, no run tested this atmosphere")
    # atmosphere = oxygen, pressure, airflow and fuel together, ignoring gravity
    assert c["atmosphere"]["n"] == 0 and c["atmosphere"]["status"] == "No evidence"


def test_case_atmosphere_ignores_gravity():
    # ISS-cabin atmosphere but lunar gravity: gravity has no evidence, the atmosphere itself was tested
    lunar_iss_air = engine.Target(o2_pct=21, pressure_psi=14.7, airflow_cm_s=10, gravity_g=0.16, fuel_state="any")
    c = engine.case(lunar_iss_air, rows=MOCK)
    assert c["whole"]["n"] == 0
    assert c["atmosphere"]["n"] == 8
    assert c["verdict"].endswith("ignoring gravity, 8 runs match the atmosphere")


def test_case_mars_like():
    c = engine.case(MARS, rows=MOCK)
    assert counts(c) == {"o2": (11, "Supported"), "psi": (4, "Supported"), "flow": (13, "Supported"),
                         "fuel": (20, "Supported"), "grav": (0, "No evidence")}
    assert c["whole"]["n"] == 0


def test_missing_values_never_match():
    rows = [dict(BY_ID["PH-02-R01"], airflow_cm_s=None, pressure_psi=None, o2_pct=None, gravity_g=None)]
    c = engine.case(ISS, rows=rows)
    assert all(x["n"] == 0 for x in c["conditions"] if x["key"] != "fuel")
    assert c["whole"]["n"] == 0


def test_airflow_not_specified_matches_all():
    t = Target(o2_pct=21, pressure_psi=14.7, fuel_state="any", gravity_g=0)  # airflow None
    c = engine.case(t, rows=MOCK)
    flow = next(x for x in c["conditions"] if x["key"] == "flow")
    assert flow["n"] == len(MOCK)


def test_weak_status_with_one_run():
    rows = [BY_ID["PH-05-R01"]]
    c = engine.case(T(34, 10.2, 12, "gas", 0), rows=rows)
    assert all(x["status"] == "Weak" for x in c["conditions"])


# ------------------------------------------------------------ next experiment

def test_next_iss_cabin_needs_nothing_new():
    n = engine.next_experiment(ISS, rows=MOCK)
    assert n["needed"] is False and n["gaps"] == [] and n["changes"] == []
    assert n["nearest_run"]["run_id"] in {r for r in engine.case(ISS, rows=MOCK)["whole"]["run_ids"]}


def test_next_lunar_rover():
    n = engine.next_experiment(ROVER, rows=MOCK)
    assert n["needed"] is True and n["gaps"] == ["grav"] and n["closes"] == 1
    assert n["nearest_run"]["run_id"] == "PH-05-R01"
    assert {(c["field"], c["from"], c["to"]) for c in n["changes"]} == {
        ("fuel_state", "gas", "solid"), ("gravity_g", 0, 0.16)}


def test_next_mars_like():
    n = engine.next_experiment(MARS, rows=MOCK)
    assert n["gaps"] == ["grav"]
    assert n["nearest_run"]["run_id"] == "PH-05-R02"
    assert [(c["field"], c["from"], c["to"]) for c in n["changes"]] == [("gravity_g", 0, 0.38)]


def test_next_conditions_covered_separately_but_not_together():
    # one run matches oxygen only, another matches pressure only (and so on): each condition is
    # Supported but no run matches all five
    a = dict(BY_ID["PH-02-R01"], run_id="A1", o2_pct=21, pressure_psi=30, airflow_cm_s=10)
    b = dict(BY_ID["PH-02-R01"], run_id="A2", o2_pct=21, pressure_psi=30, airflow_cm_s=10)
    c = dict(BY_ID["PH-02-R01"], run_id="B1", o2_pct=60, pressure_psi=14.7, airflow_cm_s=10)
    d = dict(BY_ID["PH-02-R01"], run_id="B2", o2_pct=60, pressure_psi=14.7, airflow_cm_s=10)
    n = engine.next_experiment(T(21, 14.7, 10, "any", 0), rows=[a, b, c, d])
    assert n["needed"] is True and n["gaps"] == ["whole"]


# ------------------------------------------------------------ alternatives

def alt_ids(t):
    return [(a["run_id"], a["o2_partial_pressure"]) for a in engine.alternatives(t, k=3, rows=MOCK)]


def test_alternatives_iss_cabin():
    assert alt_ids(ISS) == [("PH-04-R02", 2.14), ("PH-04-R01", 2.65)]


def test_alternatives_lunar_rover():
    assert alt_ids(ROVER) == [("PH-04-R01", 2.65), ("PH-04-R02", 2.14), ("PH-02-R01", 3.09)]


def test_alternatives_mars_like():
    assert alt_ids(MARS) == [("PH-04-R02", 2.14)]


def test_alternatives_fields():
    a = engine.alternatives(ROVER, k=1, rows=MOCK)[0]
    assert a["target_partial_pressure"] == 3.47
    assert a["reduction_pct"] == round(100 * (1 - 2.65 / 3.468), 1) or a["reduction_pct"] > 10
    assert {c["field"] for c in a["changes"]} >= {"o2_pct", "pressure_psi"}


# ------------------------------------------------------------ strength and coverage

def test_strength_parts_and_note():
    s = engine.strength(ISS, rows=MOCK)
    assert set(s["conditions"]) == set(engine.KEYS)
    for part in list(s["conditions"].values()) + [s["whole"]]:
        assert 0 <= part["score"] <= 100
        assert all(0 <= part[k] <= 1 for k in ("proximity", "reliability", "run_count", "source_quality"))
    assert "not a safety rating" in s["note"]


def test_strength_zero_without_evidence():
    s = engine.strength(ROVER, rows=MOCK)
    assert s["conditions"]["grav"]["score"] == 0 and s["whole"]["score"] == 0


def test_strength_assumed_basis_lowers_reliability():
    base = dict(BY_ID["PH-02-R01"], confidence="high", o2_basis="measured", value_source="table")
    rows_measured = [dict(base, run_id="M1"), dict(base, run_id="M2"), dict(base, run_id="M3")]
    rows_assumed = [dict(r, o2_basis="assumed") for r in rows_measured]
    t = T(21, 14.7, 10, "any", 0)
    m = engine.strength(t, rows=rows_measured)["conditions"]["o2"]
    a = engine.strength(t, rows=rows_assumed)["conditions"]["o2"]
    assert a["reliability"] < m["reliability"] and a["score"] < m["score"]


def test_coverage():
    cov = engine.coverage(21, 14.7, rows=MOCK)
    assert cov["in_range"] is True and cov["n_within"] > 0 and len(cov["nearest"]) == 3
    far = engine.coverage(34, 6.0, rows=MOCK)  # lowest mock pressure is 10.2 psi, so nothing within +-2 psi of 6
    assert far["in_range"] is False and far["n_within"] == 0
    dists = [n["distance"] for n in far["nearest"]]
    assert dists == sorted(dists)


# ------------------------------------------------------------ real data smoke tests

@pytest.fixture(scope="module")
def real():
    return data.load_runs()


def test_real_lunar_rover_has_no_whole_match_and_no_gravity_evidence(real):
    c = engine.case(T(34, 10.2, 10, "solid", 0.16), rows=real)
    grav = next(x for x in c["conditions"] if x["key"] == "grav")
    assert c["whole"]["n"] == 0
    assert grav["status"] == "No evidence"


def test_real_strength_in_range(real):
    s = engine.strength(T(21, 14.7, 10, "any", 0), rows=real)
    scores = [p["score"] for p in s["conditions"].values()] + [s["whole"]["score"]]
    assert all(0 <= x <= 100 for x in scores)
    assert s["whole"]["score"] > 0  # the ISS cabin is well covered


def test_everything_is_json_serialisable(real):
    t = T(34, 10.2, 10, "solid", 0.16)
    for out in (engine.rank(t, rows=real), engine.case(t, rows=real), engine.next_experiment(t, rows=real),
                engine.alternatives(t, rows=real), engine.strength(t, rows=real),
                engine.coverage(34, 10.2, rows=real),
                engine.next_experiment(T(21, 14.7, 10, "any", 0), rows=real)):
        json.dumps(out)


def test_real_rank_returns_investigations(real):
    out = engine.rank(T(21, 14.7, 10, "solid", 0), rows=real, k=5)
    assert len(out) == 5 and all(x["doi"] for x in out)
    assert [x["score"] for x in out] == sorted((x["score"] for x in out), reverse=True)
