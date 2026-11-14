"""Investigation profiles: summarize and compare PSI combustion investigations.

Data: data/curated/investigation_profiles.json, built by scripts/build_investigation_profiles.py
(texts from PSI, conditions and outcomes from data/curated/runs.csv, hardware groups from the challenge text).
"""
import json
from functools import lru_cache

from . import data

PROFILES_JSON = data.CURATED / "investigation_profiles.json"
MODELING_JSON = data.CURATED / "modeling_studies.json"
NOTES_CSV = data.CURATED / "condition_notes.csv"   # sourced statements for conditions the run table leaves empty
LONG_TEXT = ("objectives", "approach", "hypothesis", "research_impacts")

# Multi-flight series share NTRS overview papers where appropriate
SHARED_PAPER_IDS = {
    "PSI-99": ("PSI-99", "PSI-98"),
    "PSI-100": ("PSI-100", "PSI-98"),
    "PSI-102": ("PSI-102", "PSI-101"),
    "PSI-68": ("PSI-68", "PSI-69"),
}


@lru_cache(maxsize=1)
def _profiles():
    with open(PROFILES_JSON, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def modeling_studies():
    if not MODELING_JSON.exists():
        return []
    with open(MODELING_JSON, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def condition_notes():
    """Sourced statements (NASA papers, reports, test matrices, PSI page text) for oxygen, pressure or airflow
    values that the PSI Experimental Table does not record. Shown in profiles only; never used for matching."""
    import csv
    if not NOTES_CSV.exists():
        return []
    with open(NOTES_CSV, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def notes_for(psi_id):
    return [n for n in condition_notes() if n["psi_id"] == psi_id]


def modeling_for(psi_id):
    return [m for m in modeling_studies() if psi_id in (m.get("uses_flight_psi_ids") or [])]


def papers_for(psi_id):
    targets = SHARED_PAPER_IDS.get(psi_id, (psi_id,))
    seen = set()
    out = []
    for p in data.papers():
        if p.get("psi_id") in targets and p["ntrs_id"] not in seen:
            seen.add(p["ntrs_id"])
            out.append(p)
    return out


def _summary(p):
    """Profile without the full long texts (their *_summary versions stay)."""
    out = {k: v for k, v in p.items() if k not in LONG_TEXT}
    out["modeling_count"] = len(modeling_for(p["psi_id"]))
    out["papers_count"] = len(papers_for(p["psi_id"]))
    return out


def all_profiles():
    return [_summary(p) for p in _profiles()]


def profile(psi_id):
    p = next((p for p in _profiles() if p["psi_id"] == psi_id), None)
    if p is None:
        return None
    return {**p, "modeling_studies": modeling_for(psi_id), "papers": papers_for(psi_id),
            "condition_notes": notes_for(psi_id)}


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
