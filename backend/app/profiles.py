"""Investigation profiles: summarize and compare PSI combustion investigations.

Data: data/curated/investigation_profiles.json, built by scripts/build_investigation_profiles.py
(texts from PSI, conditions and outcomes from data/curated/runs.csv, hardware groups from the challenge text).
"""
import json
from functools import lru_cache

from . import data

PROFILES_JSON = data.CURATED / "investigation_profiles.json"
LONG_TEXT = ("objectives", "approach", "hypothesis", "research_impacts")


@lru_cache(maxsize=1)
def _profiles():
    with open(PROFILES_JSON, encoding="utf-8") as f:
        return json.load(f)


def _summary(p):
    """Profile without the full long texts (their *_summary versions stay)."""
    return {k: v for k, v in p.items() if k not in LONG_TEXT}


def all_profiles():
    return [_summary(p) for p in _profiles()]


def profile(psi_id):
    return next((p for p in _profiles() if p["psi_id"] == psi_id), None)


def _range_text(r):
    if not r:
        return None
    lo, hi = r
    return f"{lo:g}" if abs(hi - lo) < 1e-9 else f"{lo:g}–{hi:g}"


def compare(a_id, b_id):
    a, b = profile(a_id), profile(b_id)
    if a is None or b is None:
        return None
    same, different = [], []

    def add(field, va, vb):
        if va == vb:
            same.append({"field": field, "value": va})
        else:
            different.append({"field": field, "a": va, "b": vb})

    for field in ("pillar", "hardware_group", "platform"):
        add(field, a.get(field), b.get(field))
    add("fuel_states", sorted(a.get("fuel_states") or []), sorted(b.get("fuel_states") or []))
    add("varied_conditions", sorted(a.get("varied") or []), sorted(b.get("varied") or []))
    for key, label in (("o2_pct", "oxygen_range_pct"), ("pressure_psi", "pressure_range_psi"), ("airflow_cm_s", "airflow_range_cm_s")):
        ra = (a.get("ranges_incl_assumed") or {}).get(key)
        rb = (b.get("ranges_incl_assumed") or {}).get(key)
        add(label, _range_text(ra), _range_text(rb))
    ma, mb = set(a.get("measurements_mentioned") or []), set(b.get("measurements_mentioned") or [])
    measurements = {"shared": sorted(ma & mb), "only_a": sorted(ma - mb), "only_b": sorted(mb - ma)}
    return {"a": _summary(a), "b": _summary(b), "same": same, "different": different, "measurements": measurements}
