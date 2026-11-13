"""Load the curated FlameLens tables once and share them across the app.

Files (see docs/research/dashboard-data-map.md):
  data/curated/runs.csv                  2,003 runs across 18 spaceflight PSIs, one schema
  data/curated/investigations.csv        26 PSI investigations with DOIs
  data/curated/smoke_dust_sizes.csv      smoke and dust particle sizes (SAME-R + DAFT)
  data/curated/spread_rates.csv          43 measured 0g flame spread / regression rates (BASS-II + Saffire-II)
  data/curated/coolflame_notes.csv       sourced cool-flame findings (ACME CFI-G, CFI, PSI-142)
  data/curated/papers.csv                NASA NTRS peer-reviewed paper library
Tests can pass another runs file (for example data/mock/runs_placeholder.csv) to load_runs().
"""
import csv
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CURATED = ROOT / "data" / "curated"
RUNS_CSV = CURATED / "runs.csv"
INVESTIGATIONS_CSV = CURATED / "investigations.csv"
SIZES_CSV = CURATED / "smoke_dust_sizes.csv"
SPREAD_CSV = CURATED / "spread_rates.csv"
COOLNOTES_CSV = CURATED / "coolflame_notes.csv"
PAPERS_CSV = CURATED / "papers.csv"

NUMERIC = ("o2_pct", "pressure_psi", "airflow_cm_s", "gravity_g")


def _num(value):
    try:
        return float(value) if value not in ("", None) else None
    except ValueError:
        return None


def load_runs(path=None):
    """Return a list of run dicts. Numeric fields are floats or None (never guessed)."""
    path = Path(path) if path else RUNS_CSV
    rows = []
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            for k in NUMERIC:
                r[k] = _num(r.get(k))
            r.setdefault("fuel_state", "")
            rows.append(r)
    return rows


@lru_cache(maxsize=1)
def runs():
    return load_runs()


@lru_cache(maxsize=1)
def investigations():
    with open(INVESTIGATIONS_CSV, encoding="utf-8", newline="") as f:
        return {r["psi_id"]: r for r in csv.DictReader(f)}


@lru_cache(maxsize=1)
def sizes():
    rows = []
    with open(SIZES_CSV, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            for k in ("aging_s", "geometric_mean_um", "count_mean_um", "avg_mass_diameter_um", "gsd"):
                r[k] = _num(r.get(k))
            rows.append(r)
    return rows


@lru_cache(maxsize=1)
def spread_rates():
    if not SPREAD_CSV.exists():
        return []
    rows = []
    num_cols = ("thickness_mm", "width_cm", "sides_burning", "airflow_cm_s",
                "o2_initial_pct", "o2_final_pct", "pressure_psi", "spread_rate_mm_s", "burn_time_s")
    with open(SPREAD_CSV, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            for k in num_cols:
                r[k] = _num(r.get(k))
            rows.append(r)
    return rows


@lru_cache(maxsize=1)
def coolflame_notes():
    if not COOLNOTES_CSV.exists():
        return []
    with open(COOLNOTES_CSV, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


@lru_cache(maxsize=1)
def papers():
    if not PAPERS_CSV.exists():
        return []
    with open(PAPERS_CSV, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def ranges(rows=None):
    """Min and max of oxygen, pressure and airflow in the data (used to normalise distances)."""
    rows = rows if rows is not None else runs()
    out = {}
    for key in ("o2_pct", "pressure_psi", "airflow_cm_s"):
        vals = [r[key] for r in rows if r[key] is not None]
        out[key] = (min(vals), max(vals)) if vals else (0.0, 1.0)
    return out


def run_by_id(run_id, rows=None):
    rows = rows if rows is not None else runs()
    return next((r for r in rows if r["run_id"] == run_id), None)
