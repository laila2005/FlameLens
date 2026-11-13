"""Lens data for the dashboard: pure functions, JSON-friendly, honest about the data.

Only measured numbers from data/curated are returned. Nothing is smoothed, interpolated or invented.
"""
from collections import Counter, defaultdict

from . import data

COOL_INVESTIGATIONS = ("CFI", "ACME CFI-G", "FLEX")

OUTCOME_MAP = {
    "cool flame": "cool_flame",
    "hot flame": "hot_flame",
    "hot flame only": "hot_flame",
    "no ignition": "no_ignition",
}


def _bin(value, width):
    lo = int(value // width) * width
    return lo, lo + width


def coolflame(rows=None):
    """Cool-flame regime points from CFI, ACME CFI-G and FLEX (oxygen, pressure, outcome)."""
    rows = rows if rows is not None else data.runs()
    points = []
    for r in rows:
        if r["investigation"] not in COOL_INVESTIGATIONS:
            continue
        if r["o2_pct"] is None or r["pressure_psi"] is None:
            continue
        outcome = OUTCOME_MAP.get(r["outcome"], "other")
        points.append({
            "run_id": r["run_id"], "psi_id": r["psi_id"], "investigation": r["investigation"],
            "fuel": r["fuel_or_material"], "o2_pct": r["o2_pct"], "pressure_psi": r["pressure_psi"],
            "outcome": outcome, "outcome_raw": r["outcome"],
            "o2_basis": r["o2_basis"], "pressure_basis": r["pressure_basis"], "confidence": r["confidence"],
        })
    grid = defaultdict(Counter)
    for p in points:
        o_lo, o_hi = _bin(p["o2_pct"], 5)
        p_lo, p_hi = _bin(p["pressure_psi"], 5)
        grid[(o_lo, o_hi, p_lo, p_hi)][p["outcome"]] += 1
    regime_grid = [
        {"o2_from": k[0], "o2_to": k[1], "pressure_from": k[2], "pressure_to": k[3],
         "total": sum(c.values()), "counts": dict(c)}
        for k, c in sorted(grid.items())
    ]
    return {
        "points": points,
        "n_points": len(points),
        "counts_by_outcome": dict(Counter(p["outcome"] for p in points)),
        "counts_by_fuel": dict(Counter(p["fuel"] for p in points)),
        "regime_grid": regime_grid,
        "findings": data.coolflame_notes(),
        "note": ("Outcomes come from the PSI Experimental Tables (CFI summary sheet, ACME CFI-G table, FLEX table). "
                 "FLEX outcomes (extinction, disruption, completion) are kept as 'other' with the raw label in outcome_raw."),
    }


def aerosol(sizes=None):
    """Measured smoke and dust particle sizes (SAME-R Table 1, DAFT report & flight bags). No distributions are invented."""
    sizes = sizes if sizes is not None else data.sizes()
    smoke = defaultdict(dict)
    dust = []

    def row(s):
        return {
            "source_id": s["source_id"], "psi_id": s["psi_id"], "investigation": s["investigation"],
            "material": s["material"], "aging_s": s["aging_s"],
            "geometric_mean_um": s["geometric_mean_um"], "count_mean_um": s["count_mean_um"],
            "avg_mass_diameter_um": s["avg_mass_diameter_um"], "gsd": s["gsd"],
            "value_source": s["value_source"], "source_ref": s["source_ref"], "doi": s["doi"],
            "confidence": s["confidence"], "notes": s["notes"],
        }

    for s in sizes:
        if s["kind"] == "smoke":
            key = "aged_720s" if (s["aging_s"] or 0) > 0 else "fresh"
            smoke[s["material"]][key] = row(s)
        elif s["kind"] == "dust":
            dust.append(row(s))
    smoke_list = [{"material": m, **v} for m, v in smoke.items()]
    smoke_gm = [x["geometric_mean_um"] for m in smoke.values() for x in m.values() if x["geometric_mean_um"] is not None]
    return {
        "smoke": smoke_list,
        "dust": dust,
        "smoke_geometric_mean_range_um": [min(smoke_gm), max(smoke_gm)] if smoke_gm else None,
        "overlap_note": ("Dust (Arizona Road Dust, 1.57–1.72 um across DAFT flight bags, 1.65 um average) is much larger than smoke "
                         + (f"particles (geometric mean {min(smoke_gm):.2f} to {max(smoke_gm):.2f} um in SAME-R)" if smoke_gm
                            else "particles")
                         + ", so a detector that measures particle size can tell them apart."),
    }


def spread(rows=None):
    """Measured microgravity flame spread and rod regression rates vs airflow (BASS-II Summary Report + SAFFIRE-2)."""
    rows = rows if rows is not None else data.spread_rates()
    points = [r for r in rows if r.get("airflow_cm_s") is not None and r.get("spread_rate_mm_s") is not None]
    flows = [p["airflow_cm_s"] for p in points]
    rates = [p["spread_rate_mm_s"] for p in points]
    return {
        "points": points,
        "n_points": len(points),
        "counts_by_investigation": dict(Counter(p["investigation"] for p in points)),
        "counts_by_direction": dict(Counter(p["flow_direction"] for p in points)),
        "airflow_range_cm_s": [min(flows), max(flows)] if flows else None,
        "spread_rate_range_mm_s": [min(rates), max(rates)] if rates else None,
        "note": ("Measured microgravity flame spread and regression rates from NASA/TM-20210011385 (BASS-II Summary Report, "
                 "Table 5.1 & text) and PSI-99 (SAFFIRE-2 CSV). Thin fabrics/films (0.1–0.37 mm) spread at 2.1–2.6 mm/s, "
                 "nearly two orders of magnitude faster than thick PMMA slabs (1–5 mm, 0.012–0.144 mm/s)."),
    }


def tested(rows=None):
    """Oxygen vs airflow scatter of tested conditions."""
    rows = rows if rows is not None else data.runs()
    points = []
    for r in rows:
        if r["o2_pct"] is None or r["airflow_cm_s"] is None:
            continue
        points.append({
            "run_id": r["run_id"], "psi_id": r["psi_id"], "investigation": r["investigation"],
            "pillar": r["pillar"], "fuel_state": r["fuel_state"], "o2_pct": r["o2_pct"],
            "airflow_cm_s": r["airflow_cm_s"], "outcome": r["outcome"], "o2_basis": r["o2_basis"],
            "airflow_basis": r["airflow_basis"], "confidence": r["confidence"],
        })
    return {
        "points": points,
        "n_points": len(points),
        "counts_by_pillar": dict(Counter(p["pillar"] for p in points)),
        "counts_by_investigation": dict(Counter(p["investigation"] for p in points)),
        "note": ("Where flames were tested. Runs that have both oxygen and airflow. "
                 "Airflow with basis 'text' is the first display reading and is approximate."),
    }


def coverage_points(rows=None):
    """Every run with both oxygen and pressure: the tested atmospheres for the coverage map."""
    rows = rows if rows is not None else data.runs()
    points = [{"run_id": r["run_id"], "investigation": r["investigation"], "pillar": r["pillar"],
               "fuel_state": r.get("fuel_state", ""), "o2_pct": r["o2_pct"], "pressure_psi": r["pressure_psi"],
               "o2_basis": r["o2_basis"], "pressure_basis": r["pressure_basis"], "confidence": r["confidence"]}
              for r in rows if r["o2_pct"] is not None and r["pressure_psi"] is not None]
    return {"points": points, "n_points": len(points),
            "counts_by_investigation": dict(Counter(p["investigation"] for p in points)),
            "note": "Each dot is one run. Points with an assumed basis use ISS cabin air (about 14.7 psi, 21 % O2) "
                    "because the source table gave no value."}
