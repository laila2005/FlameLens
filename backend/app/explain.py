"""Cited explanation and citation verifier (docs/07-ai-guide.md).

The AI only explains. It never ranks or decides: the evidence it may talk about is retrieved here by the
deterministic engine (case, next experiment, safer options, ranker), and every claim it returns goes
through verify() before anyone sees it.

Sources of an explanation, in order (the fallback ladder in docs/07):
  1. "cache"    data/curated/explanations.json, written by scripts/build_explanations.py with an open model.
                Cached claims are re-verified on every request, so a data change can only remove claims.
  2. "live"     an OpenAI-compatible endpoint (Ollama, vLLM, ...) when LLM_BASE_URL is set and LLM_LIVE=true.
  3. "template" no AI: fixed sentences filled from the retrieved runs. Same schema, same verifier.

Verifier rules (a claim is removed, with the reason, if any is true):
  1. run_id_reference is missing or not in the retrieved runs, or the text names another run ID that is not.
  2. A number in the text is not in that run's row (any field, including notes), not one of the habitat
     inputs, not that run's or the habitat's oxygen partial pressure (2 decimals), and not one of the
     engine's own run counts. Numbers are compared exactly: 14.65 in the data does not allow "14.7".
  3. The text states a limit, threshold or safety verdict (safe, unsafe, limit, threshold, LOC, ...).
  4. The model output is not valid JSON after one retry (handled in _call_llm, all claims are lost).
psi_dataset_id, doi and confidence_level are always overwritten from the run row, never taken from the model.
"""
import json
import os
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from . import data, engine
from .schemas import Target

CACHE_PATH = data.CURATED / "explanations.json"
MAX_RUNS = 24  # runs handed to the model

# Fields whose numbers count as "in the run's row". run_id, psi_id, doi and file names are identifiers.
ID_FIELDS = {"run_id", "psi_id", "doi", "source_table"}
PROMPT_FIELDS = ("run_id", "investigation", "pillar", "fuel_or_material", "fuel_state", "o2_pct", "pressure_psi",
                 "airflow_cm_s", "gravity_g", "outcome", "metric_name", "metric_value", "confidence", "notes")

# A number not glued to letters, digits, '.' or '-' on the left (so O2, CO2, PSI-69, Saffire-4 are skipped).
NUMBER = re.compile(r"(?<![A-Za-z0-9_.\-])\d+(?:\.\d+)?(?![A-Za-z0-9])")
RUN_ID = re.compile(r"\bPSI-\d+-\d+\b")
VERDICT = re.compile(
    r"\b(safe|unsafe|safely|dangerous|hazardous|limit|limits|threshold|thresholds|LOC|LOI|non-?flammable|"
    r"will not (?:ignite|burn)|won't (?:ignite|burn)|cannot (?:ignite|burn)|guarantee[sd]?|certif(?:y|ied))\b",
    re.IGNORECASE)

SYSTEM_PROMPT = """You explain NASA microgravity combustion evidence to habitat engineers.
You get a habitat design and a list of real experiment runs, each with a run_id.
Rules:
- Use ONLY the runs given. Every claim cites exactly one run_id from the list.
- Copy numbers exactly as they appear in that run. Never round, convert or estimate a number.
- No safety verdicts, no limits, no thresholds. Do not say safe, unsafe, limit or threshold.
- If the runs do not support something, write a claim saying there is not enough data and cite the closest run.
- One factual sentence per claim, plain English for non-specialists.
Answer with JSON only, in this shape:
{"claims": [{"claim": "...", "run_id_reference": "PSI-..-....", "engineering_recommendation": "... or null"}]}
Give 3 to 5 claims."""


# ---------------------------------------------------------------- retrieval

def _key(t: Target) -> str:
    flow = "none" if t.airflow_cm_s is None else f"{t.airflow_cm_s:g}"
    return f"o2={t.o2_pct:g}|psi={t.pressure_psi:g}|flow={flow}|g={t.gravity_g:g}|fuel={t.fuel_state}"


def retrieve(target: Target) -> dict:
    """The evidence the explanation may use: runs named by the deterministic engine, plus the engine's counts."""
    c = engine.case(target)
    nxt = engine.next_experiment(target)
    alts = engine.alternatives(target, 3)
    ranked = engine.rank(target, k=5)
    ids = []

    def add(run_id):
        if run_id and run_id not in ids:
            ids.append(run_id)

    for cond in c["conditions"]:
        for rid in cond["run_ids"][:3]:
            add(rid)
    for rid in c["whole"]["run_ids"][:3] + c["atmosphere"]["run_ids"][:3]:
        add(rid)
    add(nxt["nearest_run"]["run_id"] if nxt.get("nearest_run") else None)
    for a in alts:
        add(a["run_id"])
    for r in ranked:
        add(r["top_runs"][0] if r["top_runs"] else None)
    ids = ids[:MAX_RUNS]
    runs = {rid: data.run_by_id(rid) for rid in ids}
    counts = {cond["n"] for cond in c["conditions"]} | {c["whole"]["n"], c["atmosphere"]["n"], c["supported_count"],
                                                         len(c["conditions"])}
    return {"target": target, "case": c, "next": nxt, "alternatives": alts, "rank": ranked,
            "run_ids": ids, "runs": {k: v for k, v in runs.items() if v}, "counts": counts}


# ---------------------------------------------------------------- verifier

def _numbers(text: str):
    text = RUN_ID.sub(" ", text or "")
    return [float(m) for m in NUMBER.findall(text)]


def _row_numbers(run) -> set:
    vals = set()
    for k, v in run.items():
        if k in ID_FIELDS or v in (None, ""):
            continue
        if isinstance(v, (int, float)):
            vals.add(float(v))
        else:
            vals.update(_numbers(str(v)))
    if run.get("o2_pct") is not None and run.get("pressure_psi") is not None:
        vals.add(round(run["o2_pct"] * run["pressure_psi"] / 100, 2))
    return vals


def _target_numbers(t: Target) -> set:
    vals = {t.o2_pct, t.pressure_psi, t.gravity_g, round(t.o2_pct * t.pressure_psi / 100, 2)}
    if t.airflow_cm_s is not None:
        vals.add(t.airflow_cm_s)
    return {float(v) for v in vals}


def _in(x, allowed) -> bool:
    return any(abs(x - v) < 1e-9 for v in allowed)


def verify(claims, pack) -> tuple:
    """Return (kept, removed). kept claims carry verified=True and fields copied from the run row."""
    kept, removed = [], []
    base_allowed = _target_numbers(pack["target"]) | {float(n) for n in pack["counts"]}
    for raw in claims if isinstance(claims, list) else []:
        if not isinstance(raw, dict):
            removed.append({"claim": str(raw), "run_id_reference": None, "reason": "not a claim object"})
            continue
        text = str(raw.get("claim") or "").strip()
        rec = raw.get("engineering_recommendation")
        rec = str(rec).strip() if rec not in (None, "", "null") else None
        rid = str(raw.get("run_id_reference") or "").strip()
        reason = None
        if not text:
            reason = "empty claim"
        elif not rid:
            reason = "no run ID cited"
        elif rid not in pack["runs"]:
            reason = f"run {rid} is not in the retrieved evidence"
        else:
            full = f"{text} {rec or ''}"
            others = [x for x in RUN_ID.findall(full) if x not in pack["runs"]]
            bad_numbers = [n for n in _numbers(full) if not _in(n, _row_numbers(pack["runs"][rid]) | base_allowed)]
            verdict = VERDICT.search(full)
            if others:
                reason = f"names run {others[0]}, which is not in the retrieved evidence"
            elif bad_numbers:
                reason = f"number {bad_numbers[0]:g} is not in run {rid}"
            elif verdict:
                reason = f"states a limit or safety verdict (\"{verdict.group(0)}\")"
        if reason:
            removed.append({"claim": text, "run_id_reference": rid or None, "reason": reason})
            continue
        run = pack["runs"][rid]
        kept.append({"claim": text, "psi_dataset_id": run["psi_id"], "investigation": run.get("investigation", ""),
                     "run_id_reference": rid, "confidence_level": run.get("confidence", ""),
                     "engineering_recommendation": rec, "doi": run.get("doi", ""), "verified": True})
    return kept, removed


# ---------------------------------------------------------------- template (AI off)

def _fmt(v):
    if v is None:
        return None
    return f"{int(v)}" if float(v).is_integer() else f"{v}"


def _conditions_text(run) -> str:
    parts = []
    if run.get("o2_pct") is not None:
        parts.append(f"{_fmt(run['o2_pct'])}% oxygen")
    if run.get("pressure_psi") is not None:
        parts.append(f"{_fmt(run['pressure_psi'])} psi")
    if run.get("airflow_cm_s") is not None:
        parts.append(f"airflow {_fmt(run['airflow_cm_s'])} cm/s")
    return ", ".join(parts) or "conditions not recorded"


def _desc(run) -> str:
    fuel = " ".join(str(run.get("fuel_or_material") or run.get("fuel_state") or "an unnamed fuel").split())
    out = f"{run['run_id']} ({run.get('investigation', run['psi_id'])}) tested {fuel} at {_conditions_text(run)}"
    if run.get("outcome") and run["outcome"].lower() != "tested":
        out += f"; recorded outcome: {run['outcome']}"
    return out + "."


def template_claims(pack) -> list:
    """Fixed sentences from the retrieved runs. No AI. Each sentence cites one run and copies its values."""
    c, runs = pack["case"], pack["runs"]
    claims = []
    if c["whole"]["run_ids"]:
        rid = c["whole"]["run_ids"][0]
        claims.append({"claim": f"The closest run matching the whole habitat: {_desc(runs[rid])}", "run_id_reference": rid,
                       "engineering_recommendation": None})
    elif c["atmosphere"]["run_ids"]:
        rid = c["atmosphere"]["run_ids"][0]
        claims.append({"claim": f"No run matches the whole habitat, but ignoring gravity the closest is {_desc(runs[rid])}",
                       "run_id_reference": rid,
                       "engineering_recommendation": "Treat this as microgravity evidence only; no partial-gravity data exists in PSI yet."
                       if 0 < pack["target"].gravity_g < 1 else None})
    nr = pack["next"].get("nearest_run") or {}
    if nr.get("run_id") in runs and pack["next"].get("needed"):
        names = {"o2_pct": "oxygen", "pressure_psi": "pressure", "airflow_cm_s": "airflow", "fuel_state": "fuel type",
                 "gravity_g": "gravity"}
        fields = ", ".join(names.get(ch["field"], ch["field"]) for ch in pack["next"]["changes"]) or "nothing"
        claims.append({"claim": f"There is not enough data at these exact conditions. The nearest tested run is {_desc(runs[nr['run_id']])}",
                       "run_id_reference": nr["run_id"],
                       "engineering_recommendation": f"Start the next test from this run and change: {fields}."})
    for cond in c["conditions"]:
        if cond["key"] == "o2" and cond["run_ids"]:
            rid = cond["run_ids"][0]
            claims.append({"claim": f"Oxygen level is {cond['status'].lower()} ({cond['n']} matching runs); the closest is {_desc(runs[rid])}",
                           "run_id_reference": rid, "engineering_recommendation": None})
    if pack["alternatives"]:
        a = pack["alternatives"][0]
        run = runs.get(a["run_id"])
        if run:
            claims.append({"claim": f"A tested condition with less oxygen: {_desc(run)} Its oxygen partial pressure is "
                                    f"{_fmt(a['o2_partial_pressure'])} psi against {_fmt(a['target_partial_pressure'])} psi for this habitat.",
                           "run_id_reference": a["run_id"], "engineering_recommendation": None})
    return claims


# ---------------------------------------------------------------- LLM (optional)

def _prompt_rows(pack, pillar=None):
    rows = []
    for rid in pack["run_ids"]:
        r = pack["runs"].get(rid)
        if r and (pillar is None or r.get("pillar") == pillar):
            rows.append({k: r.get(k) for k in PROMPT_FIELDS if r.get(k) not in (None, "")})
    return rows


def _user_prompt(pack, rows) -> str:
    t = pack["target"]
    habitat = {"o2_pct": t.o2_pct, "pressure_psi": t.pressure_psi, "airflow_cm_s": t.airflow_cm_s,
               "gravity_g": t.gravity_g, "fuel_state": t.fuel_state}
    return (f"Habitat design: {json.dumps(habitat)}\n"
            f"Deterministic evidence summary (do not change it): {pack['case']['verdict']}\n"
            f"Runs:\n{json.dumps(rows, ensure_ascii=False)}\n"
            "Explain what these runs tell an engineer about this habitat. JSON only.")


def llm_config() -> dict:
    return {"base_url": os.environ.get("LLM_BASE_URL", "").rstrip("/"),
            "model": os.environ.get("LLM_MODEL", "qwen2.5:7b-instruct"),
            "api_key": os.environ.get("LLM_API_KEY", ""),
            "temperature": float(os.environ.get("LLM_TEMPERATURE", "0.1")),
            "live": os.environ.get("LLM_LIVE", "false").lower() == "true"}


def _call_llm(cfg, system, user, timeout=180) -> list:
    """One chat call. Returns the claims list, or raises ValueError if the JSON fails twice (verifier rule 4)."""
    body = {"model": cfg["model"], "temperature": cfg["temperature"], "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    headers = {"Content-Type": "application/json"}
    if cfg["api_key"]:
        headers["Authorization"] = f"Bearer {cfg['api_key']}"
    last = None
    for _ in range(2):
        req = urllib.request.Request(f"{cfg['base_url']}/chat/completions", data=json.dumps(body).encode(), headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = json.loads(resp.read())["choices"][0]["message"]["content"]
        try:
            parsed = json.loads(content)
            claims = parsed.get("claims") if isinstance(parsed, dict) else parsed
            if isinstance(claims, list):
                return claims
        except json.JSONDecodeError as e:
            last = e
    raise ValueError(f"model output was not valid JSON after one retry: {last}")


def llm_claims(pack, cfg=None) -> list:
    """One call per pillar present in the retrieved runs (docs/07: one call per pillar, not many agents)."""
    cfg = cfg or llm_config()
    pillars = []
    for rid in pack["run_ids"]:
        p = pack["runs"][rid].get("pillar")
        if p and p not in pillars:
            pillars.append(p)
    out = []
    for p in pillars:
        rows = _prompt_rows(pack, p)
        if rows:
            out.extend(_call_llm(cfg, SYSTEM_PROMPT, _user_prompt(pack, rows)))
    return out


# ---------------------------------------------------------------- cache and entry point

def load_cache(path=None) -> dict:
    path = Path(path) if path else CACHE_PATH
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8")).get("entries", {})


def save_cache(entries: dict, path=None):
    path = Path(path) if path else CACHE_PATH
    path.write_text(json.dumps({"note": "Raw model claims. The API re-verifies them on every request (backend/app/explain.py).",
                                "entries": entries}, indent=2, ensure_ascii=False), encoding="utf-8")


def cache_entry(target: Target, habitat_id: str, cfg=None) -> dict:
    cfg = cfg or llm_config()
    pack = retrieve(target)
    return {"habitat_id": habitat_id, "target": target.model_dump(), "model": cfg["model"],
            "created": datetime.now(timezone.utc).isoformat(timespec="seconds"), "claims": llm_claims(pack, cfg)}


LABELS = {
    "cache": "AI explanation (open model, generated ahead and re-verified now)",
    "live": "AI explanation (open model, live)",
    "template": "AI is off: plain summary filled from the runs",
}


def explain(target: Target, cache_path=None) -> dict:
    pack = retrieve(target)
    source, model, raw, error = "template", None, None, None
    entry = load_cache(cache_path).get(_key(target))
    if entry:
        source, model, raw = "cache", entry.get("model"), entry.get("claims", [])
    else:
        cfg = llm_config()
        if cfg["base_url"] and cfg["live"]:
            try:
                raw, source, model = llm_claims(pack, cfg), "live", cfg["model"]
            except Exception as e:  # any model failure falls back to the template (app works with AI off)
                error = f"live model failed, showing the template instead: {e}"
    if raw is None:
        raw = template_claims(pack)
    kept, removed = verify(raw, pack)
    return {"source": source, "label": LABELS[source], "model": model, "summary": pack["case"]["verdict"],
            "claims": kept, "removed": removed, "removed_count": len(removed),
            "retrieved_run_ids": pack["run_ids"], "error": error,
            "note": "The decision panels are computed without AI. This text only explains them; every sentence "
                    "cites a run and was checked by the citation verifier. Not a safety rating."}
