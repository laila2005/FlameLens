"""Ask the NASA reports: retrieval, the quote verifier and the AI-off fallback.

Run from the repo root: python -m pytest backend/tests/test_ask.py -q
"""
from fastapi.testclient import TestClient

from backend.app import ask
from backend.app.main import app

client = TestClient(app)
Q = "How did airflow affect flame spread or extinction?"


def _evidence():
    passages = ask.search("PSI-25", Q)
    runs = ask._runs_for("PSI-25", Q)
    p = passages[0]
    page_text = ask.library()["pages"][(p["source_file"], p["source_ref"])]
    return passages, runs, p, page_text


def test_library_covers_downloaded_reports():
    st = client.get("/api/library").json()
    assert st["n_chunks"] > 1000
    ids = {i["psi_id"] for i in st["investigations"]}
    assert {"PSI-25", "PSI-26", "PSI-101", "PSI-107", "PSI-159"} <= ids
    for c in ask.library()["chunks"][:50]:
        assert c["source_file"].startswith(c["psi_id"] + "_") and c["source_ref"]


def test_search_is_filtered_and_ranked():
    passages = ask.search("PSI-25", Q)
    assert passages and all(p["psi_id"] == "PSI-25" for p in passages)
    assert passages == sorted(passages, key=lambda p: -p["score"])


def test_verifier_keeps_a_verbatim_quote_and_rejects_fakes():
    passages, runs, p, page = _evidence()
    sentence = page[100:220]
    good = {"claim": "The BASS-II report describes how airflow changes the flame.", "supporting_quote": sentence,
            "source_file": p["source_file"], "source_ref": p["source_ref"], "run_id_reference": ""}
    cases = {
        "invented quote": dict(good, supporting_quote="The flame grew to 999 meters in every single test run."),
        "wrong page": dict(good, source_ref="PDF page 9999"),
        "invented number": dict(good, claim="Flames spread at 123456.7 mm/s."),
        "safety verdict": dict(good, claim="This shows the cabin is safe."),
        "unretrieved run": dict(good, run_id_reference="PSI-25-9999"),
        "short quote": dict(good, supporting_quote="airflow"),
    }
    kept, removed, _ = ask.verify({"claims": [good] + list(cases.values())}, passages, runs)
    assert len(kept) == 1 and kept[0]["verified"] and kept[0]["supporting_quote"] == sentence
    assert len(removed) == len(cases)


def test_verifier_caps_claims_and_cleans_recommendations_and_summary():
    passages, runs, p, page = _evidence()
    base = {"claim": "The report discusses airflow.", "supporting_quote": page[100:220],
            "source_file": p["source_file"], "source_ref": p["source_ref"]}
    claims = [dict(base, engineering_recommendation="Keep airflow below the threshold.")] + [dict(base)] * 4
    kept, removed, summary = ask.verify({"summary": "Flames are safe at 4242 cm/s.", "claims": claims}, passages, runs)
    assert len(kept) == ask.MAX_CLAIMS and any("more than" in r["reason"] for r in removed)
    assert kept[0]["engineering_recommendation"] == "" and "recommendation_note" in kept[0]
    assert summary == ""


def test_ask_without_model_returns_passages(monkeypatch):
    monkeypatch.delenv("ASK_LLM_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr(ask, "_load_cache", lambda: {})
    r = client.post("/api/ask", json={"psi_id": "PSI-25", "question": Q}).json()
    assert r["source"] == "passages" and r["claims"] == [] and r["passages"]
    assert all(p["source_file"] and p["source_ref"] for p in r["passages"])


def test_cached_answer_is_reverified(monkeypatch):
    passages, runs, p, page = _evidence()
    raw = {"summary": "", "claims": [
        {"claim": "Quoted from the report.", "supporting_quote": page[100:220], "source_file": p["source_file"], "source_ref": p["source_ref"]},
        {"claim": "Made up.", "supporting_quote": "this sentence is not in any NASA report at all", "source_file": p["source_file"], "source_ref": p["source_ref"]}]}
    monkeypatch.setattr(ask, "_load_cache", lambda: {ask._key("PSI-25", Q): {"raw": raw, "model": "test"}})
    r = client.post("/api/ask", json={"psi_id": "PSI-25", "question": Q}).json()
    assert r["source"] == "cache" and len(r["claims"]) == 1 and r["removed_count"] == 1


def test_ask_rejects_bad_input():
    assert client.post("/api/ask", json={"psi_id": "PSI-25; drop", "question": Q}).status_code == 422
    assert client.post("/api/ask", json={"psi_id": "PSI-25", "question": "x" * 400}).status_code == 422


def test_google_provider_request_and_parsing(monkeypatch):
    """Vertex/Gemini keys are read from the environment, sent in a header (never the URL), and the reply is parsed."""
    import io, json as _json
    monkeypatch.delenv("ASK_LLM_API_KEY", raising=False); monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("ASK_LLM_PROVIDER", raising=False)
    monkeypatch.setenv("GOOGLE_API_KEY", "AQ.fake-test-key")
    cfg = ask.config()
    assert cfg["provider"] == "gemini" and cfg["live"] and "aiplatform.googleapis.com" in cfg["fallback_url"]
    monkeypatch.setenv("GOOGLE_API_KEY", "AIzaFakeTestKey")
    assert ask.config()["provider"] == "gemini"
    seen = {}
    reply = {"candidates": [{"content": {"parts": [{"text": '```json\n{"summary": "", "claims": []}\n```'}]}}]}

    class Resp(io.BytesIO):
        def __enter__(self): return self
        def __exit__(self, *a): return False

    def fake_urlopen(req, timeout=0):
        seen["url"], seen["headers"], seen["body"] = req.full_url, dict(req.header_items()), _json.loads(req.data)
        return Resp(_json.dumps(reply).encode())
    monkeypatch.setattr(ask.urllib.request, "urlopen", fake_urlopen)
    out = ask._call(ask.config(), "question")
    assert out == {"summary": "", "claims": []}
    assert "AIzaFakeTestKey" not in seen["url"] and seen["headers"].get("X-goog-api-key") == "AIzaFakeTestKey"
    assert seen["body"]["generationConfig"]["responseMimeType"] == "application/json"


def test_xai_key_selects_grok(monkeypatch):
    for k in ("ASK_LLM_API_KEY", "GROQ_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY", "ASK_LLM_PROVIDER", "ASK_LLM_BASE_URL", "ASK_LLM_MODEL"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("XAI_API_KEY", "xai-fake-test-key")
    cfg = ask.config()
    assert cfg["live"] and cfg["base_url"] == "https://api.x.ai/v1" and cfg["model"].startswith("grok")


def test_google_key_wins_over_xai(monkeypatch):
    for k in ("ASK_LLM_API_KEY", "GROQ_API_KEY", "ASK_LLM_PROVIDER", "ASK_LLM_BASE_URL", "ASK_LLM_MODEL", "GEMINI_API_KEY"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("XAI_API_KEY", "xai-fake-test-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "AIzaFakeTestKey")
    assert ask.config()["provider"] == "gemini"


def test_provider_error_hides_key_and_links():
    import io, urllib.error
    body = b'{"error": "No credits for key xai-ABCDEFGH12345678. Buy at https://console.x.ai/team/123"}'
    e = urllib.error.HTTPError("u", 403, "Forbidden", {}, io.BytesIO(body))
    msg = ask._provider_message(e, "xai-ABCDEFGH12345678")
    assert "xai-" not in msg and "console.x.ai" not in msg and "No credits" in msg
