#!/usr/bin/env python3
"""Build data/curated/bass2_airflow.csv from PSI-25_Reference Data_Fan calibration data.xlsx.

Documents the exact SPICE/BASS-II MSG flow-duct fan calibration curves across 0, 1, and 2 flow restrictors
plus NASA's centerline calibration relation U (cm/s) = 1.0066 * Air_Display (at 56 mm downstream, 36 mm from bottom).
"""
import csv
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / "data" / "raw" / "docs" / "PSI-25_Reference Data_Fan calibration data.xlsx"
OUT = ROOT / "data" / "curated" / "bass2_airflow.csv"

FIELDS = [
    "restrictors", "pot_setting", "fan_display", "fan_voltage_v",
    "air_display", "calibrated_u_cm_s", "formula_note", "source_ref", "doi",
]


def main():
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    raw = list(ws.iter_rows(values_only=True))

    rows = []
    restrictor = None
    for r in raw:
        line_txt = " ".join(str(c or "") for c in r[:6]).lower()
        if "no restrictor" in line_txt:
            restrictor = 0
            continue
        if "1 restrictor" in line_txt:
            restrictor = 1
            continue
        if "2 resrictor" in line_txt or "2 restrictor" in line_txt:
            restrictor = 2
            continue
        if restrictor is not None and isinstance(r[0], (int, float)) and isinstance(r[1], (int, float)):
            pot, fan_disp, air_disp, fan_v, u_cms = r[0], r[1], r[2], r[3], r[4]
            rows.append({
                "restrictors": restrictor,
                "pot_setting": pot,
                "fan_display": fan_disp,
                "fan_voltage_v": fan_v if fan_v is not None else "",
                "air_display": air_disp if air_disp is not None else "",
                "calibrated_u_cm_s": round(float(u_cms), 4) if isinstance(u_cms, (int, float)) else "",
                "formula_note": "U = 1.0066 * Air_Display (centerline, 56 mm downstream, 36 mm from bottom; fan turns off near 3.8 V)",
                "source_ref": "PSI-25_Reference Data_Fan calibration data.xlsx (GMT 2014-043)",
                "doi": "10.60555/fd5w-9b48",
            })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {OUT} with {len(rows)} fan calibration points")


if __name__ == "__main__":
    main()
