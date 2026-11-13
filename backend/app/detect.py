"""Real NASA numbers behind the early-detection simulation tab.

The simulation in the dashboard is an illustration, not a validated fire model. This module only returns
measured values: BASS-II gas readings (data/curated/detect_gas.csv), SAME-R / DAFT particle sizes and the
count of cool-flame runs.
"""
import csv
from functools import lru_cache

from . import data

GAS_CSV = data.CURATED / "detect_gas.csv"
NUMERIC = ("o2_initial_pct", "o2_final_pct", "co2_initial_pct", "co2_final_pct",
           "co_initial_ppm", "co_final_ppm", "co_rise_ppm", "co2_rise_pct")


@lru_cache(maxsize=1)
def gas_rows():
    rows = []
    with open(GAS_CSV, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            for k in NUMERIC:
                r[k] = data._num(r.get(k))
            rows.append(r)
    return rows


def _pct(values, q):
    """Simple percentile (nearest rank) on a sorted copy."""
    v = sorted(values)
    if not v:
        return None
    i = min(len(v) - 1, max(0, int(round(q * (len(v) - 1)))))
    return v[i]


def _summary(values, nd=2):
    if not values:
        return {"median": None, "p90": None, "max": None, "n": 0}
    return {"median": round(_pct(values, 0.5), nd), "p90": round(_pct(values, 0.9), nd),
            "max": round(max(values), nd), "n": len(values)}


def evidence():
    gas = gas_rows()
    co = [r["co_rise_ppm"] for r in gas if r["co_rise_ppm"] is not None]
    co2 = [r["co2_rise_pct"] for r in gas if r["co2_rise_pct"] is not None]
    top = sorted((r for r in gas if r["co_rise_ppm"] is not None), key=lambda r: -r["co_rise_ppm"])[:5]
    examples = [{"run_id": r["run_id"], "material": r["material"], "co_initial_ppm": r["co_initial_ppm"],
                 "co_final_ppm": r["co_final_ppm"], "co2_initial_pct": r["co2_initial_pct"],
                 "co2_final_pct": r["co2_final_pct"]} for r in top]

    # every BASS-II test with a measured CO rise, joined to its run (oxygen, airflow) so the
    # simulator can replay a real test instead of made-up numbers
    by_id = {r["run_id"]: r for r in data.runs()}
    tests = []
    for r in gas:
        run = by_id.get(r["run_id"], {})
        if r["co_rise_ppm"] is None:
            continue
        tests.append({"run_id": r["run_id"], "material": r["material"], "o2_pct": run.get("o2_pct"),
                      "airflow_cm_s": run.get("airflow_cm_s"), "airflow_basis": run.get("airflow_basis"),
                      "co_initial_ppm": r["co_initial_ppm"], "co_final_ppm": r["co_final_ppm"], "co_rise_ppm": r["co_rise_ppm"],
                      "co2_initial_pct": r["co2_initial_pct"], "co2_final_pct": r["co2_final_pct"], "co2_rise_pct": r["co2_rise_pct"]})
    tests.sort(key=lambda x: -x["co_rise_ppm"])

    sizes = data.sizes()
    smoke = [s["geometric_mean_um"] for s in sizes if s["kind"] == "smoke" and s["geometric_mean_um"] is not None]
    dust = next((s for s in sizes if s["kind"] == "dust"), None)

    cool = [r for r in data.runs() if r["outcome"] == "cool flame"]
    inv = data.investigations()
    doi = lambda pid: inv.get(pid, {}).get("doi", "")

    return {
        "gas": {
            "n_tests": len(gas),
            "co_rise_ppm": _summary(co, 1),
            "co2_rise_pct": _summary(co2, 2),
            "share_tests_co_rise_over_25ppm": round(sum(1 for x in co if x > 25) / len(co), 3) if co else None,
            "examples": examples,
            "tests": tests,
            "note": "CO in ppm and CO2 in % by volume, measured before and after each BASS-II test in the "
                    "glovebox. Readings marked over range in the source are left empty, so the maximum is a lower bound.",
        },
        "particles": {
            "smoke_geometric_mean_um_range": [min(smoke), max(smoke)] if smoke else None,
            "dust_mean_um": dust["count_mean_um"] if dust else None,
            # size boundary between the largest measured smoke and the dust (geometric middle)
            "smoke_dust_boundary_um": round((max(smoke) * dust["count_mean_um"]) ** 0.5, 3) if smoke and dust else None,
            "smoke": [{"material": s["material"], "aging_s": s["aging_s"], "geometric_mean_um": s["geometric_mean_um"]}
                      for s in sizes if s["kind"] == "smoke"],
        },
        "cool_flames": {
            "n_cool_flame_runs": len(cool),
            "investigations": sorted({r["investigation"] for r in cool}),
            "note": "cool flames make CO and formaldehyde with little light or heat (NASA FLEX finding)",
        },
        "sources": [
            {"label": "BASS-II Experimental Table (CO, CO2, O2)", "doi": doi("PSI-25"), "ref": "PSI-25"},
            {"label": "SAME-R Final Report, Table 1 (smoke sizes)", "doi": doi("PSI-101"), "ref": "PSI-101"},
            {"label": "DAFT 30-Day Post Flight Report (dust size)", "doi": doi("PSI-47"), "ref": "PSI-47"},
            {"label": "CFI and ACME CFI-G cool-flame outcomes", "doi": doi("PSI-39"), "ref": "PSI-39, PSI-159"},
        ],
        "note": "Real NASA PSI numbers. The sensor-network simulation that uses them is an illustration, "
                "not a validated fire model.",
    }
