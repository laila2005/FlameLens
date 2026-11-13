#!/usr/bin/env python3
"""Build data/curated/detect_gas.csv: real CO, CO2 and O2 readings before and after each BASS-II test.

Run from the repo root (after scripts/fetch_psi.py and scripts/build_runs.py):
    python scripts/build_detect_evidence.py

Source: PSI-25 BASS-II Experimental Table (CDM sensor CO2, CO in ppm, calibrated O2).
Non-numeric cells ("none", "OR" = out of range, "over", ">500", empty) are left empty, never guessed;
they are listed in the notes column. Run ids match data/curated/runs.csv (file order, PSI-25-0001...).
"""
import csv
import io
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = next((ROOT / "data" / "raw").glob("PSI-25__*BASS-II.csv"))
RUNS = ROOT / "data" / "curated" / "runs.csv"
INV = ROOT / "data" / "curated" / "investigations.csv"
OUT = ROOT / "data" / "curated" / "detect_gas.csv"

COLS = {
    "o2_initial_pct": "initial O2", "o2_final_pct": "final O2",
    "co2_initial_pct": "Initial CO2 %", "co2_final_pct": "Final CO2 %",
    "co_initial_ppm": "Initial CO (ppm)", "co_final_ppm": "Final CO (ppm)",
}


def num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def main():
    text = SRC.read_bytes().decode("utf-8-sig", errors="replace")
    rows = [r for r in csv.reader(io.StringIO(text)) if any(c.strip() for c in r)]
    head = [h.strip() for h in rows[0]]
    idx = {k: next(i for i, h in enumerate(head) if v.lower() in h.lower()) for k, v in COLS.items()}
    i_test = head.index("Test #")
    i_mat = head.index("Fuel Sample Material")

    runs = [r for r in csv.DictReader(open(RUNS, encoding="utf-8")) if r["psi_id"] == "PSI-25"]
    doi = next(r["doi"] for r in csv.DictReader(open(INV, encoding="utf-8")) if r["psi_id"] == "PSI-25")
    if len(runs) != len(rows) - 1:
        raise SystemExit(f"run count mismatch: {len(runs)} runs vs {len(rows) - 1} table rows")

    out = []
    for run, r in zip(runs, rows[1:]):
        cells = [c.strip() for c in r] + [""] * (len(head) - len(r))
        material = cells[i_mat]
        if material != run["fuel_or_material"]:
            raise SystemExit(f"material mismatch at {run['run_id']}: {material!r} vs {run['fuel_or_material']!r}")
        vals = {k: num(cells[i]) for k, i in idx.items()}
        odd = [f"{k}='{cells[i]}'" for k, i in idx.items() if vals[k] is None]
        co_rise = None if vals["co_initial_ppm"] is None or vals["co_final_ppm"] is None else vals["co_final_ppm"] - vals["co_initial_ppm"]
        co2_rise = None if vals["co2_initial_pct"] is None or vals["co2_final_pct"] is None else vals["co2_final_pct"] - vals["co2_initial_pct"]
        notes = ""
        if odd:
            notes = "non-numeric source cells left empty: " + ", ".join(odd)
            if any("OR" in o or "over" in o or ">" in o for o in odd):
                notes += " (OR / over / >500 = sensor over range, so the true final value was high but is unknown)"
        fmt = lambda v: "" if v is None else round(v, 3)
        out.append({
            "run_id": run["run_id"], "test_no": cells[i_test], "material": material,
            **{k: fmt(v) for k, v in vals.items()},
            "co_rise_ppm": fmt(co_rise), "co2_rise_pct": fmt(co2_rise),
            "value_source": "table", "doi": doi, "notes": notes,
        })

    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    print(f"Wrote {OUT} ({len(out)} BASS-II tests)")


if __name__ == "__main__":
    main()
