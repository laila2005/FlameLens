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
- Ranker: a missing run value scores a neutral 0.5 for that factor (it is not dropped, so missing data
  is never rewarded). factors_used counts only factors with real run values.
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
MISSING_CLOSENESS = 0.5  # ranker factor value used when a run lacks a value (neutral, not dropped)


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
    """Score one run 0-100.

    A factor the run has no value for scores a neutral MISSING_CLOSENESS (0.5): unknown is neither close
    nor far, so missing data is not rewarded. The only factor that is dropped (and the other weights
    rescaled) is airflow when the TARGET does not specify airflow.
    Returns (score, factors, factors_used): factors keep None for missing run values so the UI can show
    them, and factors_used counts only the factors with real run values ("based on N of 5 factors").
    Public so tests can check the hand-calculated cases.
    """
    w = {**DEFAULT_WEIGHTS, **(weights or {})}
    factors = _factors(target, run, rng)
    keys = [k for k in KEYS if not (k == "flow" and target.airflow_cm_s is None)]
    wsum = sum(w[k] for k in keys)
    if wsum <= 0:
        return 0.0, factors, 0
    total = sum(w[k] / wsum * (factors[k] if factors[k] is not None else MISSING_CLOSENESS) for k in keys)
    used = sum(1 for k in keys if factors[k] is not None)
    return 100 * total, factors, used


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
    zero = {"score": 0.0, "proximity": 0.0, "reliability": 0.0, "run_count": 0.0, "source_quality": 0.0,
            "n_runs": 0, "n_measured": 0, "n_investigations": 0, "investigations": []}
    if not matching:
        return zero
    proximity = _clamp(1 - min(_dist(r, target, rng) for r in matching))
    rel, src = [], []
    n_measured = 0
    by_inv = {}
    for r in matching:
        w = CONF_WEIGHT.get(r.get("confidence", ""), 0.0)
        is_assumed = any(r.get(b) == "assumed" for b in bases)
        if is_assumed:
            w *= 0.6
        else:
            n_measured += 1
        rel.append(w)
        src.append(SOURCE_QUALITY.get(r.get("value_source", ""), 0.5))
        pid = r.get("psi_id", "")
        iname = _inv(r)
        entry = by_inv.setdefault(pid, {"psi_id": pid, "name": iname, "runs": 0})
        entry["runs"] += 1
    reliability = sum(rel) / len(rel)
    run_count = min(1.0, len(matching) / 3)
    source_quality = sum(src) / len(src)
    score = 100 * (0.35 * proximity + 0.30 * reliability + 0.20 * run_count + 0.15 * source_quality)
    inv_list = sorted(by_inv.values(), key=lambda x: (-x["runs"], x["name"]))
    return {"score": round(score, 1), "proximity": _r(proximity), "reliability": _r(reliability),
            "run_count": _r(run_count), "source_quality": _r(source_quality),
            "n_runs": len(matching), "n_measured": n_measured,
            "n_investigations": len(inv_list), "investigations": inv_list[:8]}


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
    atmo = [r for r, m in ms if all(m[k] for k in ("o2", "psi", "flow", "fuel"))]
    # Distinct investigations contributing evidence across the primary atmosphere conditions (O2, pressure, airflow)
    atmo_any = [r for r, m in ms if (m["o2"] or m["psi"] or (target.airflow_cm_s is not None and m["flow"]))]
    by_inv = {}
    for r in atmo_any:
        pid = r.get("psi_id", "")
        entry = by_inv.setdefault(pid, {"psi_id": pid, "name": _inv(r), "runs": 0})
        entry["runs"] += 1
    backing_invs = sorted(by_inv.values(), key=lambda x: (-x["runs"], x["name"]))
    return {
        "conditions": conditions,
        "whole": _strength_part(whole, target, rng, list(BASIS.values())),
        "atmosphere": _strength_part(atmo, target, rng, list(BASIS.values())),
        "dataset": {
            "total_runs": len(rows),
            "total_investigations": len({r.get("psi_id", "") for r in rows if r.get("psi_id")}),
            "near_any_condition_runs": len(atmo_any),
            "backing_investigations": backing_invs[:10],
            "not_yet_in_psi": ["SoFIE", "FLARE", "LUCI", "FM2"],
        },
        "note": "Evidence strength is a transparency aid (0.35 proximity + 0.30 reliability + 0.20 test count + 0.15 source quality), not a safety rating.",
    }


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
    # The challenge text: PSI has no partial-gravity combustion data yet (LUCI and FM2 are planned);
    # microgravity and normal-gravity results bound intermediate gravity levels.
    for c in conditions:
        if c["key"] == "grav" and 0 < target.gravity_g < 1:
            c["note"] = ("No partial-gravity combustion data exists in PSI yet (LUCI and FM2 are planned). "
                         "Microgravity runs give one bound and normal-gravity results the other.")
            c["bounded"] = True
    supported = [c for c in conditions if c["status"] == "Supported"]
    missing = [c for c in conditions if c["status"] != "Supported"]
    verdict = f"{len(supported)} of {len(conditions)} conditions supported"
    if whole:
        verdict += f", {len(whole)} run{'s' if len(whole) != 1 else ''} match the whole habitat"
    else:
        verdict += ", no run matches the whole habitat"
        if missing:
            def why(c):
                if c["key"] == "grav" and c["status"] == "No evidence" and 0 < target.gravity_g < 1:
                    return "no partial-gravity data in PSI"
                word = c["label"].split()[0].lower()
                return f"no {word} evidence" if c["status"] == "No evidence" else f"weak {word} evidence"
            verdict += " (" + ", ".join(why(c) for c in missing) + ")"
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


# ---------------------------------------------------------------- campaign planner

def _would_match(exp: dict, hab: Target) -> bool:
    """Would a run flown at `exp` match habitat `hab` on all five conditions? Same rules as _match."""
    def near(value, goal, tol):
        return value is not None and abs(value - goal) <= tol + EPS
    return (near(exp["o2_pct"], hab.o2_pct, TOLERANCE["o2"])
            and near(exp["pressure_psi"], hab.pressure_psi, TOLERANCE["psi"])
            and (hab.airflow_cm_s is None or near(exp["airflow_cm_s"], hab.airflow_cm_s, TOLERANCE["flow"]))
            and (hab.fuel_state == "any" or exp["fuel_state"] == hab.fuel_state)
            and abs(exp["gravity_g"] - hab.gravity_g) <= EPS)


def _experiment(t: Target) -> dict:
    """Test conditions for one experiment. A real burn needs a real material: a design that allows "any"
    material is tested with solids (fabrics, plastics), the focus of flammability studies per the challenge text."""
    return {"o2_pct": t.o2_pct, "pressure_psi": t.pressure_psi, "airflow_cm_s": t.airflow_cm_s,
            "gravity_g": t.gravity_g, "fuel_state": "solid" if t.fuel_state == "any" else t.fuel_state}


def _midpoint(a: Target, b: Target):
    """One experiment halfway between two designs, or None if they cannot share one (gravity or material differ)."""
    if abs(a.gravity_g - b.gravity_g) > EPS:
        return None
    fa, fb = a.fuel_state, b.fuel_state
    if fa != "any" and fb != "any" and fa != fb:
        return None
    if a.airflow_cm_s is None or b.airflow_cm_s is None:
        flow = a.airflow_cm_s if a.airflow_cm_s is not None else b.airflow_cm_s
    else:
        flow = _r((a.airflow_cm_s + b.airflow_cm_s) / 2, 1)
    return _experiment(Target(o2_pct=_r((a.o2_pct + b.o2_pct) / 2, 1),
                              pressure_psi=_r((a.pressure_psi + b.pressure_psi) / 2, 2),
                              airflow_cm_s=flow, gravity_g=a.gravity_g, fuel_state=fa if fa != "any" else fb))


def campaign(targets: list, n: int = 3, rows=None) -> dict:
    """Choose up to n experiments that give the most designs a whole-design test (greedy set cover).

    targets: [{id, name, target: Target}]. A design already matched by 2+ runs on all five conditions needs
    no new test. Candidates are each open design's own conditions plus midpoints of pairs that can share one
    experiment. Each round picks the candidate covering the most still-open designs, then the one closing the
    most condition gaps, then the one closest to an existing run (cheapest to set up).
    Nothing is predicted: the plan says which test would cover which design, never what the test would show.
    """
    rows = _rows(rows)
    rng = data.ranges(rows)
    habs = []
    for t in targets:
        c = case(t["target"], rows)
        gaps = [x["key"] for x in c["conditions"] if x["status"] != "Supported"]
        n_whole = c["whole"]["n"]
        habs.append({"id": t["id"], "name": t["name"], "target": t["target"], "whole_n": n_whole,
                     "status": "covered" if n_whole >= 2 else ("weak" if n_whole == 1 else "gap"),
                     # "whole" = the five conditions were never tested together, even where each is covered alone
                     "gaps": gaps + (["whole"] if n_whole < 2 else []), "planned_by": None})
    open_habs = [h for h in habs if h["status"] != "covered"]

    cands = [_experiment(h["target"]) for h in open_habs]
    for i, a in enumerate(open_habs):
        for b in open_habs[i + 1:]:
            m = _midpoint(a["target"], b["target"])
            if m:
                cands.append(m)
    seen, uniq = set(), []
    for cnd in cands:
        key = tuple(cnd.values())
        if key not in seen:
            seen.add(key)
            uniq.append(cnd)

    def nearest_dist(exp):
        t = Target(**exp)
        return min(_dist(r, t, rng) for r in rows)

    picks, remaining = [], list(open_habs)
    while remaining and len(picks) < n:
        best, best_key = None, None
        for cnd in uniq:
            covers = [h for h in remaining if _would_match(cnd, h["target"])]
            if not covers:
                continue
            key = (len(covers), sum(len(h["gaps"]) for h in covers), -nearest_dist(cnd))
            if best_key is None or key > best_key:
                best, best_key = (cnd, covers), key
        if not best:
            break
        cnd, covers = best
        nx = next_experiment(Target(**cnd), rows)
        order = KEYS + ("whole",)
        gaps = sorted({g for h in covers for g in h["gaps"]}, key=order.index)
        g = cnd["gravity_g"]
        picks.append({
            "rank": len(picks) + 1, "conditions": cnd,
            "o2_partial_pressure": _r(_pp(cnd["o2_pct"], cnd["pressure_psi"]), 2),
            "covers": [h["id"] for h in covers], "covers_names": [h["name"] for h in covers],
            "gaps_closed": gaps, "partial_gravity": 0 < g < 1,
            "platform_note": ("Needs a partial-gravity platform: PSI has no partial-gravity combustion data yet "
                              "(LUCI and FM2 are planned, challenge text)." if 0 < g < 1 else
                              "Can fly in microgravity, like the existing PSI investigations." if g == 0 else
                              "Normal gravity: a ground test."),
            "material_note": ("The design allows any material; solids (fabrics, plastics) are the focus of NASA "
                              "flammability studies (challenge text)." if any(h["target"].fuel_state == "any" for h in covers) else ""),
            "nearest_run": nx["nearest_run"], "changes": nx["changes"]})
        for h in covers:
            h["planned_by"] = len(picks)
        remaining = [h for h in remaining if h["planned_by"] is None]

    covered_now = sum(h["status"] == "covered" for h in habs)
    planned = sum(h["planned_by"] is not None for h in habs)
    return {
        "n": n,
        "habitats": [{k: v for k, v in h.items() if k != "target"} for h in habs],
        "experiments": picks,
        "summary": {"designs": len(habs), "covered_now": covered_now, "planned": planned,
                    "covered_or_planned": covered_now + planned,
                    "still_open": [h["name"] for h in habs if h["status"] != "covered" and h["planned_by"] is None]},
        "note": "A plan for coverage, not a prediction: it says which test would cover which design, not what the test would show.",
    }
