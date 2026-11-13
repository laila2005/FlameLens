#!/usr/bin/env python3
"""Build data/curated/spread_rates.csv from NASA/TM-20210011385 (BASS-II Summary Report) and SAFFIRE-2 CSV.

Every value comes directly from a published NASA table or report text — nothing is digitized from curves or
interpolated:
  1. BASS-II Summary Report (NASA/TM-20210011385), Table 5.1, page 57 (PDF page 65):
     18 multi-velocity PMMA slab opposed-flow tests (M1..M5, M7..M11, M13..M20) -> 37 exact (airflow, spread_rate) pairs.
  2. BASS-II Summary Report text benchmarks:
     - Thin 100-um PMMA film maximum microgravity spread rate = 2.2 mm/s (Sec. 2.1.4, page 41 / PDF page 49, linked to B15).
     - Clear 0.95-cm (3/8") PMMA rod steady regression rate near quenching = 0.0385 mm/s at 1.5 cm/s, 14.8% O2 (Sec. 6.1.4.2, page 69 / PDF page 77, linked to O4).
  3. PSI-99 SAFFIRE-2 Experimental Table CSV:
     - Samples 2-5 and 2-6 (Cotton-Fiberglass SIBAL, 0.37 mm, 29x5 cm) concurrent spread = 2.1 mm/s and 2.6 mm/s at 20 cm/s, 22.1% O2.
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "data" / "curated" / "runs.csv"
OUT = ROOT / "data" / "curated" / "spread_rates.csv"

FIELDS = [
    "spread_id", "run_id", "psi_id", "investigation", "test_code", "material",
    "thickness_mm", "width_cm", "sides_burning", "flow_direction",
    "airflow_cm_s", "o2_initial_pct", "o2_final_pct", "pressure_psi",
    "spread_rate_mm_s", "burn_time_s", "value_source", "source_ref", "doi", "confidence", "notes",
]

# Exact rows from NASA/TM-20210011385 Table 5.1 (Report p. 57 / PDF p. 65). M6 and M12 say "Not tracked" and are omitted.
BASS2_TABLE_5_1 = [
    ("M1", 1.0, 2.2, 1, [9.0], [0.071], 6.4, 22.2, 21.9),
    ("M2", 3.0, 2.2, 1, [20.0, 15.0], [0.052, 0.033], 22.9, 22.2, 21.2),
    ("M3", 5.0, 2.2, 1, [10.0, 20.0], [0.029, 0.024], 20.1, 20.8, 19.7),
    ("M4", 5.0, 2.2, 2, [5.0, 3.0], [0.045, 0.033], 19.8, 21.8, 19.8),
    ("M5", 3.0, 2.2, 2, [10.0], [0.071], 27.2, 22.2, 19.0),
    ("M7", 1.0, 1.2, 2, [10.0, 6.0, 5.0, 3.0], [0.106, 0.099, 0.083, 0.07], 18.4, 18.9, 18.4),
    ("M8", 2.0, 1.2, 2, [10.0, 6.0, 5.0], [0.057, 0.056, 0.04], 25.2, 19.1, 18.2),
    ("M9", 3.0, 1.2, 2, [14.0], [0.025], 16.8, 18.0, 17.6),
    ("M10", 4.0, 1.2, 2, [15.0, 10.0], [0.0373, 0.03], 30.5, 20.1, 18.6),
    ("M11", 5.0, 1.2, 2, [21.0, 15.0, 13.0], [0.048, 0.028, 0.022], 28.5, 20.0, 18.5),
    ("M13", 4.0, 2.2, 2, [6.0, 5.0, 4.0], [0.047, 0.035, 0.033], 20.5, 20.8, 19.0),
    ("M14", 2.0, 2.2, 1, [15.0, 14.0, 10.0], [0.0624, 0.055, 0.0353], 15.4, 22.2, 21.6),
    ("M15", 4.0, 2.2, 1, [20.0], [0.045], 22.0, 21.0, 20.0),
    ("M16", 1.0, 2.2, 2, [5.0, 3.0, 2.0], [0.144, 0.1309, 0.1062], 8.4, 19.2, 18.7),
    ("M17", 2.0, 2.2, 2, [5.0, 4.0, 3.0], [0.053, 0.042, 0.026], 30.7, 18.8, 17.1),
    ("M18", 3.0, 2.2, 2, [10.0, 8.0], [0.026, 0.013], 25.5, 17.9, 16.8),
    ("M19", 4.0, 2.2, 2, [10.0, 6.0], [0.027, 0.0159], 25.7, 19.0, 17.4),
    ("M20", 5.0, 2.2, 2, [10.0], [0.012], 16.5, 18.0, 17.4),
]


def load_run_lookup():
    bass2 = {}
    saff2 = {}
    dois = {}
    with open(RUNS, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            dois[r["psi_id"]] = r["doi"]
            if r["psi_id"] == "PSI-25":
                m = re.search(r"\btest\s+([A-Za-z0-9]+);", r["notes"])
                if m:
                    bass2[m.group(1)] = r["run_id"]
            elif r["psi_id"] == "PSI-99":
                m = re.search(r"\bsample\s+([0-9\-]+);", r["notes"])
                if m:
                    saff2[m.group(1)] = r["run_id"]
    return bass2, saff2, dois


def main():
    bass2_ids, saff2_ids, dois = load_run_lookup()
    rows = []
    idx = 0

    for tcode, thick, width, sides, flows, rates, burn_min, o2_i, o2_f in BASS2_TABLE_5_1:
        assert len(flows) == len(rates), tcode
        rid = bass2_ids.get(tcode, "")
        for step_i, (vel, sr) in enumerate(zip(flows, rates), start=1):
            idx += 1
            step_note = f"velocity step {step_i}/{len(flows)} in multi-velocity test {tcode}" if len(flows) > 1 else f"single-velocity test {tcode}"
            rows.append({
                "spread_id": f"SPR-{idx:03d}",
                "run_id": rid,
                "psi_id": "PSI-25",
                "investigation": "BASS-II",
                "test_code": tcode,
                "material": f"PMMA slab ({thick:g} mm)",
                "thickness_mm": thick,
                "width_cm": width,
                "sides_burning": sides,
                "flow_direction": "opposed",
                "airflow_cm_s": vel,
                "o2_initial_pct": o2_i,
                "o2_final_pct": o2_f,
                "pressure_psi": 14.7,
                "spread_rate_mm_s": sr,
                "burn_time_s": round(burn_min * 60, 1),
                "value_source": "table",
                "source_ref": "BASS-II Summary Report (NASA/TM-20210011385), Table 5.1, p. 57 (PDF p. 65)",
                "doi": dois.get("PSI-25", "10.60555/fd5w-9b48"),
                "confidence": "high",
                "notes": f"{step_note}; {sides}-sided burning; pressure assumed ISS cabin (14.7 psi)",
            })

    # BASS-II text benchmark 1: thin 100 um PMMA film max microgravity spread rate = 2.2 mm/s (Sec. 2.1.4, p. 41 / PDF p. 49)
    idx += 1
    rows.append({
        "spread_id": f"SPR-{idx:03d}",
        "run_id": bass2_ids.get("B15", ""),
        "psi_id": "PSI-25",
        "investigation": "BASS-II",
        "test_code": "B15",
        "material": "PMMA thin film (0.1 mm)",
        "thickness_mm": 0.1,
        "width_cm": 2.0,
        "sides_burning": 2,
        "flow_direction": "opposed",
        "airflow_cm_s": 29.0,
        "o2_initial_pct": 21.0,
        "o2_final_pct": 20.8,
        "pressure_psi": 14.7,
        "spread_rate_mm_s": 2.2,
        "burn_time_s": "",
        "value_source": "text",
        "source_ref": "BASS-II Summary Report (NASA/TM-20210011385), Sec. 2.1.4, p. 41 (PDF p. 49) & Table A.1 (B15, pot 10 max flow ~29 cm/s)",
        "doi": dois.get("PSI-25", "10.60555/fd5w-9b48"),
        "confidence": "medium",
        "notes": "maximum microgravity opposed-flow spread rate reported for 100-um PMMA film (~50% faster than 1g downward spread); airflow from 0-restrictor pot 10 fan calibration",
    })

    # BASS-II text benchmark 2: 3/8" (9.52 mm diameter) PMMA rod steady regression near quenching = 0.0385 mm/s (Sec. 6.1.4.2, p. 69 / PDF p. 77)
    idx += 1
    rows.append({
        "spread_id": f"SPR-{idx:03d}",
        "run_id": bass2_ids.get("O4", ""),
        "psi_id": "PSI-25",
        "investigation": "BASS-II",
        "test_code": "O4",
        "material": "PMMA rod (9.5 mm dia)",
        "thickness_mm": 9.52,
        "width_cm": 0.95,
        "sides_burning": "",
        "flow_direction": "concurrent",
        "airflow_cm_s": 1.5,
        "o2_initial_pct": 14.8,
        "o2_final_pct": 13.6,
        "pressure_psi": 14.7,
        "spread_rate_mm_s": 0.0385,
        "burn_time_s": "",
        "value_source": "text",
        "source_ref": "BASS-II Summary Report (NASA/TM-20210011385), Sec. 6.1.4.2, p. 69 (PDF p. 77)",
        "doi": dois.get("PSI-25", "10.60555/fd5w-9b48"),
        "confidence": "high",
        "notes": "steady-state rod tip regression rate at 1.5 cm/s forced flow during lowest-O2 quenching test (14.8% initial to 13.6% final O2)",
    })

    # SAFFIRE-2 Experimental Table CSV: Samples 2-5 and 2-6 (Cotton-Fiberglass SIBAL, 0.37 mm, 5 cm wide x 29 cm long)
    for scode, sr, btime in (("2-5", 2.1, 145.0), ("2-6", 2.6, 115.0)):
        idx += 1
        rows.append({
            "spread_id": f"SPR-{idx:03d}",
            "run_id": saff2_ids.get(scode, ""),
            "psi_id": "PSI-99",
            "investigation": "Saffire-II",
            "test_code": scode,
            "material": "Cotton-Fiberglass (SIBAL)",
            "thickness_mm": 0.37,
            "width_cm": 5.0,
            "sides_burning": 2,
            "flow_direction": "concurrent",
            "airflow_cm_s": 20.0,
            "o2_initial_pct": 22.1,
            "o2_final_pct": "",
            "pressure_psi": 14.7,
            "spread_rate_mm_s": sr,
            "burn_time_s": btime,
            "value_source": "table",
            "source_ref": f"PSI-99_Experimental_table_SAFFIRE-2.csv, sample {scode}",
            "doi": dois.get("PSI-99", "10.60555/8328-bb04"),
            "confidence": "high",
            "notes": "spacecraft-scale concurrent flame spread over 29 cm SIBAL cloth aboard Cygnus; pressure assumed cabin (14.7 psi)",
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {OUT} with {len(rows)} measured microgravity flame spread / regression points")


if __name__ == "__main__":
    main()
