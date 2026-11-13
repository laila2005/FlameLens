"""Citation verifier and /api/explain. Run from the repo root: python -m pytest backend/tests/test_explain.py -q"""
import json

from fastapi.testclient import TestClient

from backend.app import explain as ex
from backend.app.main import app
from backend.app.schemas import Target

client = TestClient(app)
MOON = {"o2_pct": 30, "pressure_psi": 10.2, "airflow_cm_s": 12.9, "gravity_g": 0.16, "fuel_state": "any"}
ISS = {"o2_pct": 21, "pressure_psi": 14.7, "airflow_cm_s": 12.9, "gravity_g": 0, "fuel_state": "any"}


def _pack(t=MOON):
    return ex.retrieve(Target(**t))


def test_retrieve_only_real_runs():
    pack = _pack()
    assert 0 < len(pack["run_ids"]) <= ex.MAX_RUNS
    assert set(pack["run_ids"]) == set(pack["runs"])


def test_verifier_keeps_exact_numbers_and_overwrites_metadata():
    pack = _pack()
    rid = pack["run_ids"][0]
    run = pack["runs"][rid]
    o2 = f"{run['o2_pct']:g}"
    kept, removed = ex.verify([{"claim": f"Run {rid} was tested at {o2}% oxygen.", "run_id_reference": rid,
                                "psi_dataset_id": "WRONG", "confidence_level": "high"}], pack)
    assert not removed and kept[0]["verified"] is True
    assert kept[0]["psi_dataset_id"] == run["psi_id"] and kept[0]["confidence_level"] == run["confidence"]


def test_verifier_removes_bad_claims():
    pack = _pack()
    rid = pack["run_ids"][0]
    bad = [
        {"claim": "Something.", "run_id_reference": "PSI-1-9999"},              # rule 1: not retrieved
        {"claim": "Something.", "run_id_reference": ""},                        # rule 1: no citation
        {"claim": "See also PSI-1-0001.", "run_id_reference": rid},             # rule 1: names another run
        {"claim": "Spread rate was 3.14159 mm/s.", "run_id_reference": rid},   # rule 2: invented number
        {"claim": "This atmosphere is safe.", "run_id_reference": rid},         # rule 3: verdict
        {"claim": "The flammability limit is reached.", "run_id_reference": rid},  # rule 3: limit
        "not an object",
    ]
    kept, removed = ex.verify(bad, pack)
    assert kept == [] and len(removed) == len(bad)


def test_verifier_rejects_rounded_values():
    pack = _pack(ISS)
    rid = next(r for r in pack["run_ids"] if pack["runs"][r]["pressure_psi"] == 14.65) if any(
        pack["runs"][r]["pressure_psi"] == 14.65 for r in pack["run_ids"]) else None
    if rid is None:  # build a pack containing a run with an unrounded pressure
        rid = "PSI-69-0001"
        pack["runs"][rid] = ex.data.run_by_id(rid)
    assert pack["runs"][rid]["pressure_psi"] == 14.65
    kept, removed = ex.verify([{"claim": "It ran at 14.8 psi.", "run_id_reference": rid}], pack)
    assert not kept and "14.8" in removed[0]["reason"]


def test_chemical_formulas_are_not_numbers():
    assert ex._numbers("CO2 and O2 at PSI-69-0001 in Saffire-4") == []
    assert ex._numbers("21% oxygen at 14.65 psi") == [21.0, 14.65]


def test_template_claims_all_pass_for_every_preset():
    for h in client.get("/api/habitats").json():
        t = {k: h[k] for k in ("o2_pct", "pressure_psi", "airflow_cm_s", "gravity_g", "fuel_state")}
        body = client.post("/api/explain", json={"target": t}).json()
        assert body["source"] == "cache", h["name"]
        assert len(body["claims"]) >= 4, h["name"]
        assert body["removed_count"] == 0, body["removed"]
        assert all(c["run_id_reference"] in body["retrieved_run_ids"] for c in body["claims"])
        assert all(c["verified"] is True for c in body["claims"])
        # Also verify the deterministic template fallback directly when cache is bypassed
        tpl = ex.explain(Target(**t), cache_path="does-not-exist.json")
        assert tpl["source"] == "template" and tpl["claims"] and tpl["removed_count"] == 0


def test_cache_is_reverified(tmp_path):
    pack = _pack()
    rid = pack["run_ids"][0]
    path = tmp_path / "explanations.json"
    ex.save_cache({ex._key(Target(**MOON)): {"habitat_id": "moon-base", "model": "test-model", "claims": [
        {"claim": f"Run {rid} is in the evidence.", "run_id_reference": rid},
        {"claim": "Made up.", "run_id_reference": "PSI-1-9999"},
    ]}}, path)
    body = ex.explain(Target(**MOON), cache_path=path)
    assert body["source"] == "cache" and body["model"] == "test-model"
    assert len(body["claims"]) == 1 and body["removed_count"] == 1
    assert json.loads(path.read_text(encoding="utf-8"))["entries"]


def test_live_model_failure_falls_back(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "http://127.0.0.1:9")  # nothing listens here
    monkeypatch.setenv("LLM_LIVE", "true")
    body = ex.explain(Target(**MOON), cache_path="does-not-exist.json")
    assert body["source"] == "template" and body["error"] and body["claims"]


def test_verify_endpoint():
    body = client.post("/api/verify", json={"target": MOON, "claims": [
        {"claim": "Nothing to see.", "run_id_reference": "NOPE"}]}).json()
    assert body["removed_count"] == 1 and body["claims"] == []
