"""Extract the SPICE microgravity smoke points (per flame) and match each to its run in the SPICE table.

Source: PSI-107 report "Smoke points of microgravity and normal gravity coflow diffusion flames" (Dotson thesis),
Appendix 6.4 "Microgravity Flame Images", Figures 6.3-6.13: for every smoke-point flame it lists fuel, nozzle (mm),
day of year, GMT, fuel rate (mg/s), air rate (cm/s) and smoke-point luminous flame length (mm).

Matching to data/raw/PSI-107__PSI-107_Experimental_table_Spice.csv (row i -> run PSI-107-{i+1:04d}, the order used by
build_runs.py): the table lists each burn's settings at ignition, and the crew then ramped fuel and air flow during the
burn until the flame began to smoke. So a smoke point is linked to the burn during which it happened: same day, fuel and
nozzle (within 0.01 mm), and the smoke-point GMT between that row's ignition and flame-off times. The smoke-point fuel
and air rates are kept as printed in the thesis (they differ from the ignition settings in the table).
Values are copied as printed; nothing is interpolated. Unmatched points are kept with an empty run_id.

Run from the repo root (needs pypdfium2):  python scripts/extract_spice_smoke_points.py
Writes data/curated/spice_smoke_points.csv
"""
import csv
import re
from pathlib import Path

import pypdfium2 as pdfium

ROOT = Path(__file__).resolve().parent.parent
PDF = next((ROOT / "data" / "raw" / "docs").glob("PSI-107_Reports_SMOKE POINTS*DotsonThesis.pdf"))
TABLE = ROOT / "data" / "raw" / "PSI-107__PSI-107_Experimental_table_Spice.csv"
OUT = ROOT / "data" / "curated" / "spice_smoke_points.csv"
SOURCE = "PSI-107 Dotson thesis (Smoke points of microgravity and normal gravity coflow diffusion flames), Appendix 6.4"


def norm_fuel(s):
    s = s.lower().replace(" ", "")
    return {"ethylene": "ethylene", "propane": "propane", "propylene": "propylene",
            "75%propylene": "75% propylene", "50%propylene": "50% propylene"}.get(s, s)


def secs(hms):
    h, m, s = (int(x) for x in hms.strip().split(":"))
    return h * 3600 + m * 60 + s


def parse_points():
    doc = pdfium.PdfDocument(str(PDF))
    text = "\n".join(doc[i].get_textpage().get_text_range() for i in range(len(doc)))
    start = text.index("6.4.Microgravity Flame Images")
    body = text[start:text.index("Bibliography", start)]
    parts = re.split(r"(Figure 6\.\d+\.)", body)
    points = []
    for k in range(1, len(parts), 2):
        data, fig, cap = parts[k - 1], parts[k], " ".join(parts[k + 1].split())[:200]
        m = re.search(r"for (?:additional )?(75% propylene|50% propylene|propylene|propane|ethylene)", cap)
        fuel = m.group(1) if m else ""

        def row(label):
            mm = re.search(label + r"\s+([^\n]+)", data)
            return mm.group(1).split() if mm else []

        cols = [row(r"Nozzle \(mm\)"), row(r"Day of Year"), row(r"GMT"), row(r"Fuel Rate \(mg/s\)"),
                row(r"Air Rate \(cm/s\)"), row(r"Length \(mm\)")]
        n = len(cols[0])
        if not fuel or any(len(c) != n for c in cols):
            raise SystemExit(f"could not parse {fig} ({fuel!r}, sizes {[len(c) for c in cols]})")
        for j in range(n):
            points.append({"figure": fig.rstrip("."), "fuel": fuel, "nozzle_mm": cols[0][j], "day_of_year": cols[1][j],
                           "gmt": cols[2][j], "fuel_rate_mg_s": cols[3][j], "air_rate_cm_s": cols[4][j],
                           "smoke_point_length_mm": cols[5][j]})
    return points


def main():
    points = parse_points()
    rows = list(csv.DictReader(open(TABLE, encoding="utf-8-sig")))
    matched = 0
    for p in points:
        cands = []
        for i, r in enumerate(rows):
            try:
                if int(float(r["GMT date"])) != int(p["day_of_year"]) or norm_fuel(r["Fuel"]) != p["fuel"]:
                    continue
                if abs(float(r["Nozzle (mm)"]) - float(p["nozzle_mm"])) > 0.01:
                    continue
                t, t0, t1 = secs(p["gmt"]), secs(r["GMT ignition"]), secs(r["GMT  Flame Off "])
                if not (t0 <= t <= t1):
                    continue
            except (ValueError, KeyError):
                continue
            cands.append(i)
        if cands:  # within the burn, the recorded setting closest to the smoke-point fuel and air rates
            fr, ar = float(p["fuel_rate_mg_s"]), float(p["air_rate_cm_s"])
            def gap(i):
                r = rows[i]
                return abs(float(r["Fuel Rate (mg/s)"]) - fr) / max(fr, 1e-9) + abs(float(r["Air Rate (cm/s)"]) - ar) / max(ar, 1e-9)
            best = min(cands, key=gap)
            p["run_id"] = f"PSI-107-{best + 1:04d}"
            p["match_note"] = ("smoke point reached during this burn (same day, fuel, nozzle; GMT within ignition..flame-off)"
                               + (f"; burn has {len(cands)} recorded settings, nearest to the smoke-point rates used" if len(cands) > 1 else ""))
        else:
            p["run_id"] = ""
            p["match_note"] = "no SPICE table burn contains this time (kept, not linked)"
        p["source_ref"] = f"{SOURCE}, {p['figure']}"
        matched += bool(cands)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    cols = ["run_id", "fuel", "nozzle_mm", "day_of_year", "gmt", "fuel_rate_mg_s", "air_rate_cm_s",
            "smoke_point_length_mm", "figure", "source_ref", "match_note"]
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(points)
    print(f"{len(points)} smoke points parsed, {matched} matched to SPICE runs -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
