"""Ask the NASA reports: question answering over the PSI documents with verbatim, verified quotes.

Built on Dai's explain_ai.py (team AstroSpark): retrieve report passages for one investigation, ask an
OpenAI-compatible model (Groq gpt-oss-120b by default) for JSON claims that each carry an exact supporting quote,
file and page, then verify every claim against the original page text. Enhanced here:
- BM25 retrieval with stop words (rare terms weigh more) over data/curated/doc_chunks.jsonl, built by
  scripts/build_doc_library.py; runs come from the real run table (data/curated/runs.csv).
- The verifier keeps Dai's checks (cited source exists, quote is verbatim on the cited page, run ID was retrieved,
  claim numbers appear in the cited page or run) and adds FlameLens rules: no safety verdicts, limits or thresholds
  in claims or recommendations (shared with explain.py), at most 3 claims, quotes of at least 20 characters,
  recommendations and the summary are checked too (dropped if they carry an unverified number or a verdict),
  run IDs and chemical formulas are not counted as numbers.
- Works with AI off: answers come from a committed cache (re-verified on every request) or, without a cache
  entry or API key, the best matching passages are returned with file and page so the user can read the source.
The decision engine never uses this module.
"""
import hashlib
import json
import math
import os
import re
import unicodedata
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from . import data
from .explain import NUMBER, RUN_ID, VERDICT, _row_numbers

ROOT = Path(__file__).resolve().parents[2]
CHUNKS = ROOT / "data" / "curated" / "doc_chunks.jsonl"
CACHE = ROOT / "data" / "curated" / "ask_cache.json"
TOP_CHUNKS, MAX_RUNS, MAX_CLAIMS, MIN_QUOTE = 6, 8, 3, 20

STOP = set("""a about above after again against all also am an and any are as at be because been before being below
between both but by can could did do does doing down during each few for from further had has have having he her here
hers him his how i if in into is it its itself just me more most my no nor not now of off on once only or other our out
over own same she should so some such than that the their them then there these they this those through to too under
until up very was we were what when where which while who whom why will with would you your was were what's does did
investigation experiment experiments nasa psi report reports study tested test tests show shows""".split())

SYSTEM_PROMPT = """You are FlameLens, an evidence-only explainer of NASA microgravity combustion reports.
You get one PSI investigation, a question, report passages (each with source_file and source_ref) and some runs.
STRICT RULES:
1. Use ONLY the supplied passages and runs. Never invent values, run IDs or page numbers.
2. Every claim must give source_file and source_ref copied exactly from one supplied passage.
3. Every claim must include supporting_quote: a sentence copied word for word from that passage (at least 20 characters).
   If you cannot quote it exactly, leave the claim out.
4. Copy numbers exactly as written in the quote. Never round, convert or estimate.
5. Use run_id_reference only for a run ID in the supplied runs; otherwise use "".
6. Distinguish measured results from plans, objectives and recommendations.
7. No safety verdicts, no limits, no thresholds, no risk scores. Do not say safe, unsafe, limit or threshold.
8. At most 3 claims, one plain-English sentence each, for non-specialists.
9. If the passages do not answer the question, return an empty claims list and say so in the summary.
Return ONLY JSON:
{"summary": "...", "claims": [{"claim": "...", "supporting_quote": "...", "source_file": "...", "source_ref": "...",
 "run_id_reference": "", "confidence_level": "high|medium|low", "engineering_recommendation": "... or empty"}]}"""

SUGGESTIONS = {
    "Prevention": "How did airflow or oxygen affect flame spread or extinction?",
    "Detection": "How did smoke particle size depend on the material and on aging?",
    "Suppression": "What happened when the flame went out, and what was measured?",
    "Other": "What was measured about the flames, and how?",
}
GENERIC = ["What were the main findings?", "What test conditions (oxygen, pressure, airflow) were used?",
           "What instruments or measurements were used?"]


# ---------------------------------------------------------------- library and retrieval

def _tokens(text):
    return [w for w in re.findall(r"[a-z0-9]+(?:\.[0-9]+)?", text.lower()) if w not in STOP and len(w) > 1]


@lru_cache(maxsize=1)
def library():
    chunks = []
    if CHUNKS.exists():
        with open(CHUNKS, encoding="utf-8") as f:
            chunks = [json.loads(line) for line in f if line.strip()]
    toks = [Counter(_tokens(c["text"])) for c in chunks]
    df = Counter()
    for t in toks:
        df.update(t.keys())
    n = max(1, len(chunks))
    idf = {w: math.log(1 + (n - d + 0.5) / (d + 0.5)) for w, d in df.items()}
    avg = sum(sum(t.values()) for t in toks) / n
    pages = {}
    for c in chunks:
        pages.setdefault((c["source_file"], c["source_ref"]), []).append(c["text"])
    return {"chunks": chunks, "toks": toks, "idf": idf, "avg": avg,
            "pages": {k: " ".join(v) for k, v in pages.items()}}


# Reports say "results" or "conclusions" where people ask for "findings": expand a few question words.
EXPAND = {"findings": ["results", "conclusions", "concluded", "observed", "found", "summary"],
          "finding": ["results", "conclusions", "observed", "found"],
          "conditions": ["oxygen", "pressure", "airflow", "flow", "velocity", "concentration"],
          "instruments": ["camera", "sensor", "thermocouple", "radiometer", "anemometer", "diagnostics"],
          "measurements": ["measured", "measurement", "camera", "sensor", "thermocouple", "radiometer"],
          "measured": ["measurement", "camera", "sensor", "thermocouple", "radiometer"],
          "extinction": ["extinguished", "quenched", "blowoff"], "spread": ["spreading", "spread rate"],
          "smoke": ["soot", "particle", "particles"], "size": ["diameter", "particle"]}


def _expand(tokens):
    out = list(tokens)
    for t in tokens:
        for e in EXPAND.get(t, []):
            out.extend(_tokens(e))
    return out


def search(psi_id, question, k=TOP_CHUNKS):
    """BM25 over report passages (question words plus a few synonyms), filtered to one investigation."""
    lib = library()
    q = _expand(_tokens(question))
    k1, b = 1.4, 0.75
    scored = []
    for c, t in zip(lib["chunks"], lib["toks"]):
        if psi_id and c["psi_id"] != psi_id:
            continue
        length = sum(t.values()) or 1
        s = sum(lib["idf"].get(w, 0) * t[w] * (k1 + 1) / (t[w] + k1 * (1 - b + b * length / lib["avg"])) for w in q if w in t)
        if s > 0:
            scored.append((s, c))
    scored.sort(key=lambda x: -x[0])
    return [dict(c, score=round(s, 3)) for s, c in scored[:k]]


def stats():
    lib = library()
    by = {}
    for c in lib["chunks"]:
        e = by.setdefault(c["psi_id"], {"psi_id": c["psi_id"], "investigation": c["investigation"], "chunks": 0, "files": set()})
        e["chunks"] += 1
        e["files"].add(c["source_file"])
    out = [dict(e, files=sorted(e["files"])) for e in by.values()]
    out.sort(key=lambda e: int(e["psi_id"].split("-")[1]))
    return {"n_chunks": len(lib["chunks"]), "n_files": len({c["source_file"] for c in lib["chunks"]}),
            "investigations": out}


def suggestions(psi_id):
    pillar = next((r.get("pillar") for r in data.runs() if r["psi_id"] == psi_id), None)
    return GENERIC[:1] + [SUGGESTIONS.get(pillar or "Other", SUGGESTIONS["Other"])] + GENERIC[1:]


def _runs_for(psi_id, question, limit=MAX_RUNS):
    q = set(_tokens(question))
    runs = [r for r in data.runs() if r["psi_id"] == psi_id]
    def overlap(r):
        text = " ".join(str(r.get(k) or "") for k in ("fuel_or_material", "outcome", "metric_name", "notes"))
        return len(q & set(_tokens(text)))
    runs.sort(key=lambda r: -overlap(r))
    return runs[:limit]


# ---------------------------------------------------------------- verification

def _norm(text):
    text = unicodedata.normalize("NFKC", str(text or ""))
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"[‐-―−]", "-", text)
    return re.sub(r"\s+", " ", text).strip().casefold()


def _nums(text):
    text = RUN_ID.sub(" ", str(text or ""))
    text = re.sub(r"\bPSI-\d+\b", " ", text)
    return {float(x) for x in NUMBER.findall(text)}


def verify(result, passages, runs):
    """Keep only claims whose quote is verbatim on the cited page and whose numbers appear in the cited evidence."""
    lib = library()
    keys = {(p["source_file"], p["source_ref"]) for p in passages}
    by_run = {r["run_id"]: r for r in runs}
    kept, removed = [], []
    claims = result.get("claims") if isinstance(result, dict) else None
    for raw in (claims if isinstance(claims, list) else []):
        if not isinstance(raw, dict):
            continue
        c = {k: str(raw.get(k) or "").strip() for k in ("claim", "supporting_quote", "source_file", "source_ref",
                                                         "run_id_reference", "confidence_level", "engineering_recommendation")}
        reason = None
        key = (c["source_file"], c["source_ref"])
        if not c["claim"]:
            reason = "empty claim"
        elif len(kept) >= MAX_CLAIMS:
            reason = f"more than {MAX_CLAIMS} claims"
        elif key not in keys:
            reason = "cited source was not among the retrieved passages"
        elif len(c["supporting_quote"]) < MIN_QUOTE:
            reason = "supporting quote missing or too short"
        elif _norm(c["supporting_quote"]) not in _norm(lib["pages"].get(key, "")):
            reason = "quote is not word for word on the cited page"
        elif c["run_id_reference"] and c["run_id_reference"] not in by_run:
            reason = f"run {c['run_id_reference']} was not retrieved"
        elif VERDICT.search(c["claim"]):
            reason = f"states a limit or safety verdict (\"{VERDICT.search(c['claim']).group(0)}\")"
        else:
            evidence = _nums(lib["pages"].get(key, ""))
            if c["run_id_reference"]:
                evidence |= _row_numbers(by_run[c["run_id_reference"]])
            bad = sorted(_nums(c["claim"]) - evidence)
            if bad:
                reason = f"number {bad[0]:g} is not on the cited page"
            else:
                rec = c["engineering_recommendation"]
                if rec and (VERDICT.search(rec) or (_nums(rec) - evidence)):
                    c["engineering_recommendation"] = ""
                    c["recommendation_note"] = "recommendation removed: it stated a limit or an unverified number"
                c["page"] = next((p.get("page") for p in passages if (p["source_file"], p["source_ref"]) == key), None)
                c["verified"] = True
                kept.append(c)
                continue
        removed.append({"claim": c["claim"][:300], "source_ref": c["source_ref"], "reason": reason})
    summary = str(result.get("summary") or "").strip() if isinstance(result, dict) else ""
    cited = set()
    for c in kept:
        cited |= _nums(lib["pages"].get((c["source_file"], c["source_ref"]), ""))
    if summary and (VERDICT.search(summary) or (_nums(summary) - cited)):
        summary = ""
    return kept, removed, summary


# ---------------------------------------------------------------- model, cache, answer

def config():
    key = os.environ.get("ASK_LLM_API_KEY") or os.environ.get("GROQ_API_KEY") or ""
    return {"base_url": os.environ.get("ASK_LLM_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/"),
            "model": os.environ.get("ASK_LLM_MODEL", "openai/gpt-oss-120b"), "api_key": key, "live": bool(key)}


def _call(cfg, user, timeout=60):
    body = {"model": cfg["model"], "temperature": 0.1, "max_tokens": 1500, "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}]}
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {cfg['api_key']}",
               "User-Agent": "FlameLens/1.0"}
    for attempt in range(2):
        req = urllib.request.Request(f"{cfg['base_url']}/chat/completions", data=json.dumps(body).encode(), headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                content = json.loads(resp.read())["choices"][0]["message"]["content"] or "{}"
        except urllib.error.HTTPError as e:
            if e.code == 400 and attempt == 0:   # endpoint without JSON mode: retry plain
                body.pop("response_format", None)
                continue
            raise
        content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            s, e2 = content.find("{"), content.rfind("}")
            if s >= 0 and e2 > s:
                return json.loads(content[s:e2 + 1])
            raise ValueError("model did not return JSON")
    raise ValueError("model call failed")


def _key(psi_id, question):
    return hashlib.sha256(f"{psi_id}|{_norm(question)}".encode()).hexdigest()[:24]


def _load_cache():
    try:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_cache(entry_key, entry):
    try:
        cache = _load_cache()
        cache[entry_key] = entry
        CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    except OSError:
        pass   # read-only filesystem (Vercel): the answer is still returned


def _user_prompt(psi_id, question, passages, runs):
    keep = ("run_id", "fuel_or_material", "fuel_state", "o2_pct", "pressure_psi", "airflow_cm_s", "gravity_g",
            "outcome", "metric_name", "metric_value", "notes")
    packet = {"psi_id": psi_id, "question": question,
              "passages": [{"source_file": p["source_file"], "source_ref": p["source_ref"], "text": p["text"]} for p in passages],
              "runs": [{k: r.get(k) for k in keep} for r in runs]}
    return "Answer the question using only this evidence packet.\n" + json.dumps(packet, ensure_ascii=False)


def answer(psi_id, question, use_model=True):
    question = " ".join(str(question).split())[:300]
    passages = search(psi_id, question)
    runs = _runs_for(psi_id, question)
    inv = next((c["investigation"] for c in library()["chunks"] if c["psi_id"] == psi_id), psi_id)
    base = {"psi_id": psi_id, "investigation": inv, "question": question,
            "passages": [{"source_file": p["source_file"], "source_ref": p["source_ref"], "page": p.get("page"),
                          "text": p["text"][:700], "score": p["score"]} for p in passages[:4]]}
    if not passages:
        return dict(base, source="none", claims=[], removed=[], removed_count=0, summary="",
                    note="No passage in the downloaded NASA documents for this investigation matches the question.")
    cfg = config()
    k = _key(psi_id, question)
    cached = _load_cache().get(k)
    raw, source, model = None, None, None
    if cached:
        raw, source, model = cached.get("raw"), "cache", cached.get("model")
    elif use_model and cfg["live"]:
        try:
            raw = _call(cfg, _user_prompt(psi_id, question, passages, runs))
            source, model = "model", cfg["model"]
            _save_cache(k, {"psi_id": psi_id, "question": question, "model": cfg["model"], "raw": raw,
                            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
        except Exception as e:   # network, quota, bad JSON: fall back to passages
            base["error"] = f"model unavailable ({type(e).__name__})"
    if raw is None:
        return dict(base, source="passages", claims=[], removed=[], removed_count=0, summary="",
                    note="AI answer not available (no API key or no cached answer). These are the best matching "
                         "passages from the NASA documents, with file and page.")
    kept, removed, summary = verify(raw, passages, runs)
    return dict(base, source=source, model=model, summary=summary, claims=kept, removed=removed,
                removed_count=len(removed),
                note="AI-written answer. Every claim quotes the NASA document word for word and was checked against "
                     "the cited page; claims that failed were removed. Not a safety rating.")
