"""Decision engine: ranker, evidence case, next experiment, safer options, evidence strength.

Deterministic, no AI. Rules come from docs/design/ranker-cases.md, docs/design/decision-cases.md
and docs/10-idea-brainstorm.md (evidence strength). Every public function takes `rows`
(default: data.runs()) so tests can use data/mock/runs_placeholder.csv.

Return shapes (JSON-serialisable dicts):

rank(target, weights=None, k=10, rows=None) -> list of
    {psi_id, investigation, pillar, doi, score (0-100), breakdown {o2, psi, flow, fuel, grav: 0-1 or None},
     factors_used (int, of 5), n_runs, top_runs [run_id, ...], confidence ("high"|"medium"|"low")}
    Rank runs, then roll up to the investigation: mean of its best 3 run scores.

case(target, rows=None) -> {
    conditions: [{key ("o2"|"psi"|"flow"|"fuel"|"grav"), label, status ("Supported"|"Weak"|"No evidence"),
                  n (matching runs), run_ids (up to 10), strength (0-100)}],
    whole: {status, n, run_ids, strength},
    atmosphere: {status, n, run_ids, note}  (whole match ignoring gravity),
    supported_count (int), verdict (str)}

next_experiment(target, rows=None) -> {
    needed (bool), gaps [condition keys not Supported, or "whole"], recommended {o2_pct, pressure_psi,
    airflow_cm_s, gravity_g, fuel_state}, nearest_run {run_id, investigation, o2_pct, pressure_psi,
    airflow_cm_s, fuel_state}, changes [{field, from, to}], closes (int), message (str)}

alternatives(target, k=3, rows=None) -> list of
    {run_id, investigation, o2_pct, pressure_psi, o2_partial_pressure, target_partial_pressure,
     reduction_pct, changes [{field, from, to, delta}], confidence, doi}

strength(target, rows=None) -> {
    conditions: {key: {score 0-100, proximity, reliability, run_count, source_quality}},
    whole: {score, proximity, reliability, run_count, source_quality}, note ("not a safety rating")}

coverage(o2_pct, pressure_psi, rows=None) -> {
    in_range (bool), nearest [{run_id, investigation, o2_pct, pressure_psi, distance}], n_within (int)}

Rules and choices (starting guesses, tune on real data):
- Tolerances: O2 +-6 points, pressure +-2 psi, airflow +-8 cm/s, same fuel state ("any" matches all),
  same gravity. Supported = 2+ matching runs, Weak = 1, No evidence = 0.
- A run value that is missing never matches (values are never guessed).
- If the target airflow is None ("not specified") the airflow condition matches every run and the
  airflow factor is dropped from the ranker and from distances.
- Normalised distance: each of oxygen, pressure, airflow is divided by the data range (max - min).
  A run with a missing value on a dimension counts as 0.5 of the range apart on that dimension.
"""
from typing import Optional

from . import data
from .schemas import Target

TOLERANCE = {"o2": 6.0, "psi": 2.0, "flow": 8.0}
DEFAULT_WEIGHTS = {"o2": 0.35, "psi": 0.20, "flow": 0.20, "fuel": 0.15, "grav": 0.10}

EPS = 1e-9  # float slack so that 10.2 - 8.2 counts as exactly 2.0
KEYS = ("o2", "psi", "flow", "fuel", "grav")
LABELS = {"o2": "Oxygen level", "psi": "Pressure", "flow": "Airflow", "fuel": "Fuel type", "grav": "Gravity"}
FIELD = {"o2": "o2_pct", "psi": "pressure_psi", "flow": "airflow_cm_s", "fuel": "fuel_state", "grav": "gravity_g"}
# basis column per numeric condition (fuel and gravity have none)
BASIS = {"o2": "o2_basis", "psi": "pressure_basis", "flow": "airflow_basis"}
CONF_WEIGHT = {"high": 1.0, "medium": 0.7, "low": 0.4, "placeholder": 0.0}
SOURCE_QUALITY = {"table": 1.0, "text": 0.8, "plot-read": 0.5}
MISSING_DISTANCE = 0.5  # normalised distance used when a run lacks a value


# ---------------------------------------------------------------- helpers

def _rows(rows):
    return rows if rows is not None else data.runs()


def _clamp(x):
    return max(0.0, min(1.0, x))


def _r(x, n=3):
    return None if x is None else round(x, n)


def _match(run, target: Target) -> dict:
    """Which of the five conditions this run matches (missing run values never match)."""
    def near(value, goal, tol):
        return value is not None and abs(value - goal) <= tol + EPS

    return {
        "o2": near(run["o2_pct"], target.o2_pct, TOLERANCE["o2"]),
        "psi": near(run["pressure_psi"], target.pressure_psi, TOLERANCE["psi"]),
        "flow": True if target.airflow_cm_s is None else near(run["airflow_cm_s"], target.airflow_cm_s, TOLERANCE["flow"]),
        "fuel": target.fuel_state == "any" or run.get("fuel_state") == target.fuel_state,
        "grav": run["gravity_g"] is not None and abs(run["gravity_g"] - target.gravity_g) <= EPS,
    }


def _dist(run, target: Target, rng, use_flow=True) -> float:
    """Normalised distance on oxygen, pressure and (optionally) airflow. See module docstring."""
    pairs = [("o2_pct", target.o2_pct), ("pressure_psi", target.pressure_psi)]
    if use_flow and target.airflow_cm_s is not None:
        pairs.append(("airflow_cm_s", target.airflow_cm_s))
    total = 0.0
    for key, goal in pairs:
        lo, hi = rng[key]
        value = run[key]
        total += MISSING_DISTANCE ** 2 if value is None else ((value - goal) / ((hi - lo) or 1.0)) ** 2
    return total ** 0.5


def _closeness(goal, value, key, rng):
    """1 - |goal - value| / range, clamped to 0..1. None if the run has no value."""
    if value is None or goal is None:
        return None
    lo, hi = rng[key]
    span = hi - lo
    if span <= 0:
        return 1.0 if abs(goal - value) <= EPS else 0.0
    return _clamp(1 - abs(goal - value) / span)


def _factors(target: Target, run, rng) -> dict:
    """The five ranker factors for one run (None where a value is missing)."""
    if target.fuel_state == "any":
        fuel = 0.5
    elif not run.get("fuel_state"):
        fuel = None
    else:
        fuel = 1.0 if run["fuel_state"] == target.fuel_state else 0.0
    g = run["gravity_g"]
    if g is None:
        grav = None
    elif abs(g - target.gravity_g) <= EPS:
        grav = 1.0
    elif g < 1 and target.gravity_g < 1:
        grav = 0.5
    else:
        grav = 0.0
    return {
        "o2": _closeness(target.o2_pct, run["o2_pct"], "o2_pct", rng),
        "psi": _closeness(target.pressure_psi, run["pressure_psi"], "pressure_psi", rng),
        "flow": _closeness(target.airflow_cm_s, run["airflow_cm_s"], "airflow_cm_s", rng),
        "fuel": fuel,
        "grav": grav,
    }


def run_score(target: Target, run, rng, weights=None):
    """Score one run 0-100. Missing factors are dropped and the other weights rescaled.

    Returns (score, factors, factors_used). Public so tests can check the hand-calculated cases.
    """
    w = {**DEFAULT_WEIGHTS, **(weights or {})}
    factors = _factors(target, run, rng)
    used = {k: v for k, v in factors.items() if v is not None}
    wsum = sum(w[k] for k in used)
    if not used or wsum <= 0:
        return 0.0, factors, 0
    total = sum(w[k] / wsum * v for k, v in used.items())
    return 100 * total, factors, len(used)


def _round_factors(f):
    return {k: _r(v) for k, v in f.items()}


def _inv(run):
    """Investigation name (the placeholder CSV has no 'investigation' column, so fall back to psi_id)."""
    return run.get("investigation") or run.get("psi_id", "")


def _brief(run):
    return {"run_id": run["run_id"], "investigation": _inv(run), "o2_pct": run["o2_pct"],
            "pressure_psi": run["pressure_psi"], "airflow_cm_s": run["airflow_cm_s"],
            "fuel_state": run.get("fuel_state", "")}


# ---------------------------------------------------------------- rank

def rank(target: Target, weights: Optional[dict] = None, k: int = 10, rows=None) -> list:
    rows = _rows(rows)
    rng = data.ranges(rows)
    scored = {}
    for run in rows:
        score, factors, used = run_score(target, run, rng, weights)
        scored.setdefault(run["psi_id"], []).append((score, run, factors, used))
    info = data.investigations() if rows is data.runs() else {}
    out = []
    for psi_id, items in scored.items():
        items.sort(key=lambda x: -x[0])
        best3 = items[:3]
        top_score, top_run, top_factors, top_used = best3[0]
        out.append({
            "psi_id": psi_id,
            "investigation": _inv(top_run),
            "pillar": top_run.get("pillar", ""),
            "doi": top_run.get("doi") or info.get(psi_id, {}).get("doi", ""),
            "score": round(sum(s for s, *_ in best3) / len(best3), 1),
            "breakdown": _round_factors(top_factors),
            "factors_used": top_used,
            "n_runs": len(items),
            "top_runs": [r["run_id"] for _, r, _, _ in best3],
            "confidence": top_run.get("confidence", "low"),
        })
    out.sort(key=lambda x: -x["score"])
    return out[:k]


# ---------------------------------------------------------------- strength

def _status(n):
    return "Supported" if n >= 2 else ("Weak" if n == 1 else "No evidence")


def _strength_part(matching, target, rng, bases):
    """Evidence strength for a set of matching runs. `bases` = basis columns that count as assumptions."""
    zero = {"score": 0.0, "proximity": 0.0, "reliability": 0.0, "run_count": 0.0, "source_quality": 0.0}
    if not matching:
        return zero
    proximity = _clamp(1 - min(_dist(r, target, rng) for r in matching))
    rel, src = [], []
    for r in matching:
        w = CONF_WEIGHT.get(r.get("confidence", ""), 0.0)
        if any(r.get(b) == "assumed" for b in bases):
            w *= 0.6
        rel.append(w)
        src.append(SOURCE_QUALITY.get(r.get("value_source", ""), 0.5))
    reliability = sum(rel) / len(rel)
    run_count = min(1.0, len(matching) / 3)
    source_quality = sum(src) / len(src)
    score = 100 * (0.35 * proximity + 0.30 * reliability + 0.20 * run_count + 0.15 * source_quality)
    return {"score": round(score, 1), "proximity": _r(proximity), "reliability": _r(reliability),
            "run_count": _r(run_count), "source_quality": _r(source_quality)}


def _matches(target, rows):
    """All runs with their per-condition match flags."""
    return [(run, _match(run, target)) for run in rows]


def strength(target: Target, rows=None) -> dict:
    rows = _rows(rows)
    rng = data.ranges(rows)
    ms = _matches(target, rows)
    conditions = {}
    for key in KEYS:
        matching = [r for r, m in ms if m[key]]
        bases = [BASIS[key]] if key in BASIS else []
        conditions[key] = _strength_part(matching, target, rng, bases)
    whole = [r for r, m in ms if all(m.values())]
    return {"conditions": conditions,
            "whole": _strength_part(whole, target, rng, list(BASIS.values())),
            "note": "Evidence strength is a transparency aid, not a safety rating."}


# ---------------------------------------------------------------- case

def case(target: Target, rows=None) -> dict:
    rows = _rows(rows)
    rng = data.ranges(rows)
    ms = _matches(target, rows)
    st = strength(target, rows)
    conditions = []
    for key in KEYS:
        matching = sorted((r for r, m in ms if m[key]), key=lambda r: _dist(r, target, rng))
        conditions.append({"key": key, "label": LABELS[key], "status": _status(len(matching)),
                           "n": len(matching), "run_ids": [r["run_id"] for r in matching[:10]],
                           "strength": st["conditions"][key]["score"]})
    whole = sorted((r for r, m in ms if all(m.values())), key=lambda r: _dist(r, target, rng))
    whole_info = {"status": _status(len(whole)), "n": len(whole), "run_ids": [r["run_id"] for r in whole[:10]],
                  "strength": st["whole"]["score"]}
    # Same as "whole" but ignoring gravity: shows whether the ATMOSPHERE was tested at all (in microgravity),
    # so a lunar or Mars design does not hide that oxygen, pressure, airflow and fuel were never tested together.
    atmo = sorted((r for r, m in ms if all(m[k] for k in ("o2", "psi", "flow", "fuel"))), key=lambda r: _dist(r, target, rng))
    atmo_info = {"status": _status(len(atmo)), "n": len(atmo), "run_ids": [r["run_id"] for r in atmo[:10]],
                 "note": "runs matching oxygen, pressure, airflow and fuel together, ignoring gravity"}
    supported = [c for c in conditions if c["status"] == "Supported"]
    missing = [c for c in conditions if c["status"] != "Supported"]
    verdict = f"{len(supported)} of {len(conditions)} conditions supported"
    if whole:
        verdict += f", {len(whole)} run{'s' if len(whole) != 1 else ''} match the whole habitat"
    else:
        verdict += ", no run matches the whole habitat"
        if missing:
            verdict += " (" + ", ".join(f"no {c['label'].split()[0].lower()} evidence" if c["status"] == "No evidence"
                                       else f"weak {c['label'].split()[0].lower()} evidence" for c in missing) + ")"
    if not whole and atmo:
        verdict += f"; ignoring gravity, {len(atmo)} run{'s' if len(atmo) != 1 else ''} match the atmosphere"
    elif not whole and not atmo:
        verdict += "; even ignoring gravity, no run tested this atmosphere"
    return {"conditions": conditions, "whole": whole_info, "atmosphere": atmo_info,
            "supported_count": len(supported), "verdict": verdict}


# ---------------------------------------------------------------- next experiment

def _change(key, run, target):
    goal = {"o2": target.o2_pct, "psi": target.pressure_psi, "flow": target.airflow_cm_s,
            "fuel": target.fuel_state, "grav": target.gravity_g}[key]
    return {"field": FIELD[key], "from": run.get(FIELD[key]), "to": goal}


def next_experiment(target: Target, rows=None) -> dict:
    rows = _rows(rows)
    rng = data.ranges(rows)
    c = case(target, rows)
    gaps = [x["key"] for x in c["conditions"] if x["status"] != "Supported"]
    whole_n = c["whole"]["n"]
    recommended = {"o2_pct": target.o2_pct, "pressure_psi": target.pressure_psi,
                   "airflow_cm_s": target.airflow_cm_s, "gravity_g": target.gravity_g,
                   "fuel_state": target.fuel_state}
    ms = _matches(target, rows)
    if not gaps and whole_n >= 2:
        # Nothing new is needed: repeating the weakest matching run adds the most certainty.
        matching = [r for r, m in ms if all(m.values())]
        weakest = min(matching, key=lambda r: (CONF_WEIGHT.get(r.get("confidence", ""), 0.0), _dist(r, target, rng)))
        return {"needed": False, "gaps": [], "recommended": recommended, "nearest_run": _brief(weakest),
                "changes": [], "closes": 0,
                "message": f"No new test is needed for coverage. {whole_n} runs match this habitat. "
                           f"Repeating {weakest['run_id']} (confidence {weakest.get('confidence', 'unknown')}) "
                           f"would add the most certainty."}
    if not gaps:
        gaps = ["whole"]  # every condition is covered alone, but never together
    nearest = min(rows, key=lambda r: _dist(r, target, rng))
    m = _match(nearest, target)
    changes = [_change(k, nearest, target) for k in KEYS if not m[k]]
    names = [LABELS[g].lower() if g != "whole" else "the whole habitat together" for g in gaps]
    message = (f"Run an experiment at the target conditions. It would close {len(gaps)} gap"
               f"{'s' if len(gaps) != 1 else ''}: {', '.join(names)}. "
               f"The nearest existing run is {nearest['run_id']}")
    message += (f"; change {', '.join(ch['field'] for ch in changes)}." if changes else ".")
    return {"needed": True, "gaps": gaps, "recommended": recommended, "nearest_run": _brief(nearest),
            "changes": changes, "closes": len(gaps), "message": message}


# ---------------------------------------------------------------- alternatives

def _pp(o2, psi):
    return o2 * psi / 100


def alternatives(target: Target, k: int = 3, rows=None) -> list:
    rows = _rows(rows)
    rng = data.ranges(rows)
    target_pp = _pp(target.o2_pct, target.pressure_psi)
    info = data.investigations() if rows is data.runs() else {}
    candidates = []
    for r in rows:
        if r["o2_pct"] is None or r["pressure_psi"] is None:
            continue
        if target.fuel_state != "any" and r.get("fuel_state") != target.fuel_state:
            continue
        pp = _pp(r["o2_pct"], r["pressure_psi"])
        if pp <= 0.9 * target_pp + EPS:
            candidates.append((_dist(r, target, rng), r, pp))
    candidates.sort(key=lambda x: x[0])
    out = []
    for _, r, pp in candidates[:k]:
        changes = []
        for key in ("o2", "psi", "flow"):
            have, want = r[FIELD[key]], {"o2": target.o2_pct, "psi": target.pressure_psi, "flow": target.airflow_cm_s}[key]
            if have is not None and want is not None:
                changes.append({"field": FIELD[key], "from": want, "to": have, "delta": round(have - want, 2)})
        out.append({"run_id": r["run_id"], "investigation": _inv(r), "o2_pct": r["o2_pct"],
                    "pressure_psi": r["pressure_psi"], "o2_partial_pressure": round(pp, 2),
                    "target_partial_pressure": round(target_pp, 2),
                    "reduction_pct": round(100 * (1 - pp / target_pp), 1) if target_pp else 0.0,
                    "changes": changes, "confidence": r.get("confidence", ""),
                    "doi": r.get("doi") or info.get(r["psi_id"], {}).get("doi", "")})
    return out


# ---------------------------------------------------------------- coverage

def coverage(o2_pct: float, pressure_psi: float, rows=None) -> dict:
    rows = _rows(rows)
    rng = data.ranges(rows)
    t = Target(o2_pct=o2_pct, pressure_psi=pressure_psi)

    def d2(r):
        return _dist(r, t, rng, use_flow=False)

    within = [r for r in rows
              if r["o2_pct"] is not None and r["pressure_psi"] is not None
              and abs(r["o2_pct"] - o2_pct) <= TOLERANCE["o2"] + EPS
              and abs(r["pressure_psi"] - pressure_psi) <= TOLERANCE["psi"] + EPS]
    ranked = sorted((r for r in rows if r["o2_pct"] is not None and r["pressure_psi"] is not None), key=d2)[:3]
    return {"in_range": bool(within), "n_within": len(within),
            "nearest": [{"run_id": r["run_id"], "investigation": _inv(r), "o2_pct": r["o2_pct"],
                         "pressure_psi": r["pressure_psi"], "distance": round(d2(r), 3)} for r in ranked]}
