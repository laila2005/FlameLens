#!/usr/bin/env python3
"""Build data/curated/runs.csv from the PSI Experimental Table CSVs in data/raw/.

Run from the repo root, after scripts/fetch_psi.py and scripts/fetch_psi_docs.py:
    python scripts/build_runs.py

Every row says where each condition came from (the *_basis columns):
  measured  = a column in the PSI table
  text      = parsed from a free-text cell (lower confidence)
  assumed   = not in the table, taken from the platform (for example ISS cabin air). Check these.
  unknown   = not available, left empty. "No evidence" is a valid result for the dashboard.

Needs openpyxl only for the CFI and BASS as-run spreadsheets (pip install openpyxl).
"""
import csv
import io
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
DOCS = RAW / "docs"
OUT = ROOT / "data" / "curated" / "runs.csv"

PSI_PER_ATM = 14.6959
PSI_PER_BAR = 14.5038
PSI_PER_MMHG = 0.0193368
CABIN_PSI = 14.7  # ISS cabin, assumed where a table gives no pressure

PILLAR = {26: "Prevention", 25: "Prevention", 98: "Prevention", 99: "Prevention", 100: "Prevention",
          107: "Prevention", 20: "Prevention", 102: "Detection", 101: "Detection", 47: "Detection",
          69: "Suppression", 68: "Suppression", 39: "Suppression", 159: "Suppression", 22: "Suppression",
          10: "Other", 21: "Other", 23: "Other", 106: "Other"}
NAME = {26: "BASS", 25: "BASS-II", 98: "Saffire-I", 99: "Saffire-II", 100: "Saffire-III", 107: "SPICE",
        20: "ACME BRE", 102: "SAME", 101: "SAME-R", 69: "FLEX", 39: "CFI", 159: "ACME CFI-G", 10: "ACME Flame Design"}

FIELDS = ["run_id", "psi_id", "investigation", "pillar", "fuel_or_material", "fuel_state", "o2_pct", "o2_basis",
          "pressure_psi", "pressure_basis", "airflow_cm_s", "airflow_basis", "gravity_g", "outcome",
          "metric_name", "metric_value", "value_source", "source_table", "doi", "confidence", "notes"]


def read_csv(pattern):
    path = next(RAW.glob(pattern))
    text = path.read_bytes().decode("utf-8-sig", errors="replace")
    rows = [r for r in csv.reader(io.StringIO(text)) if any(c.strip() for c in r)]
    head = [h.strip() for h in rows[0]]
    return path.name, head, [dict(zip(head, [c.strip() for c in r])) for r in rows[1:]]


def pick(row, *keys):
    """First non-empty value whose header contains any of the keys (case-insensitive)."""
    for k in keys:
        for h, v in row.items():
            if k.lower() in h.lower() and v not in ("", None):
                return v
    return ""


def num(s):
    m = re.search(r"-?\d+(?:\.\d+)?", str(s or ""))
    return float(m.group()) if m else None


def dois():
    out = {}
    p = ROOT / "data" / "curated" / "investigations.csv"
    if p.exists():
        for r in csv.DictReader(open(p, encoding="utf-8")):
            out[int(r["psi_id"].split("-")[1])] = r["doi"]
    return out


DOI = dois()
rows_out = []
counter = {}


def add(psi, table, fuel, state, o2, o2b, p, pb, flow, fb, outcome, mname="", mval="", vsrc="table", notes=""):
    counter[psi] = counter.get(psi, 0) + 1
    # sanity ranges: anything outside is a typo or a unit slip in the source, so leave it empty
    if o2 is not None and not (5 <= o2 <= 100):
        notes += f"; source oxygen value {o2:g} out of range, left empty"
        o2, o2b = None, "unknown"
    if p is not None and not (0.5 <= p <= 100):
        notes += f"; source pressure value {p:g} psi out of range, left empty"
        p, pb = None, "unknown"
    if flow is not None and not (0 <= flow <= 100):
        notes += f"; source airflow value {flow:g} out of range, left empty"
        flow, fb = None, "unknown"
    assumed = [b for b in (o2b, pb) if b == "assumed"]
    unknown = [b for b in (o2b, pb) if b == "unknown"]
    if o2b == "measured" and pb == "measured":
        conf = "high"
    elif len(unknown) == 2:
        conf = "low"
    elif unknown or assumed:
        conf = "medium"
    else:
        conf = "medium"
    if fb == "text":
        conf = "medium" if conf == "high" else conf
    rows_out.append({
        "run_id": f"PSI-{psi}-{counter[psi]:04d}", "psi_id": f"PSI-{psi}", "investigation": NAME.get(psi, f"PSI-{psi}"),
        "pillar": PILLAR.get(psi, "Other"), "fuel_or_material": fuel, "fuel_state": state,
        "o2_pct": "" if o2 is None else round(o2, 2), "o2_basis": o2b,
        "pressure_psi": "" if p is None else round(p, 2), "pressure_basis": pb,
        "airflow_cm_s": "" if flow is None else round(flow, 2), "airflow_basis": fb, "gravity_g": 0,
        "outcome": outcome, "metric_name": mname, "metric_value": mval, "value_source": vsrc,
        "source_table": table, "doi": DOI.get(psi, ""), "confidence": conf, "notes": notes})


# ---------- FLEX (PSI-69): droplet combustion, oxygen, pressure, diluent ----------
name, head, rows = read_csv("PSI-69__*FLEX.csv")
for r in rows:
    o2 = num(pick(r, "O initial"))
    p = num(pick(r, "Ambient pressure"))
    add(69, name, pick(r, "Fuel"), "liquid", None if o2 is None else o2 * 100, "measured" if o2 is not None else "unknown",
        None if p is None else p * PSI_PER_MMHG, "measured" if p is not None else "unknown", None, "unknown",
        pick(r, "Test end") or "tested", "burn_time_s", pick(r, "Burn time"),
        notes=f"N {pick(r,'N initial')}, CO2 {pick(r,'CO initial')}, He {pick(r,'He initial')} mole fraction; "
              f"droplet {pick(r,'Droplet initial')} mm; airflow not in table")

# ---------- ACME CFI-G (PSI-159): cool flame yes/no ----------
for kind, pat in (("normal", "PSI-159__*Normal*"), ("inverse", "PSI-159__*Inverse*")):
    name, head, rows = read_csv(pat)
    for r in rows:
        o2 = num(pick(r, "XO2 before", "XO2"))
        p = num(pick(r, "approx p"))
        cool = pick(r, "Cool flame?").lower()
        hot = pick(r, "Hot ignition").lower()
        cm = pick(r, "Comments")
        if cool.startswith("y"):
            out = "cool flame"
        elif hot.startswith("y"):
            out = "hot flame"
        elif "fail" in cm.lower() or hot.startswith("n"):
            out = "no ignition"
        else:
            out = "tested"
        add(159, name, pick(r, "Fuel"), "gas", None if o2 is None else o2 * 100, "measured" if o2 is not None else "unknown",
            None if p is None else p * PSI_PER_BAR, "measured" if p is not None else "unknown", None, "unknown", out,
            "burn_time_s", pick(r, "burn time"), notes=f"{kind} flame; {cm}"[:200])

# ---------- ACME Flame Design (PSI-10): oxygen and pressure tested (soot study) ----------
for kind, pat in (("normal", "PSI-10__*Normal*"), ("inverse", "PSI-10__*Inverse*")):
    name, head, rows = read_csv(pat)
    for r in rows:
        o2 = num(pick(r, "XO2 (init)", "XO2"))
        p = num(pick(r, "pmean", "pinit"))
        add(10, name, pick(r, "Fuel") or "C2H4", "gas", None if o2 is None else o2 * 100, "measured" if o2 is not None else "unknown",
            None if p is None else p * PSI_PER_ATM, "measured" if p is not None else "unknown", None, "unknown",
            "tested", notes=f"{kind} flame, soot study; outcome not in table")

# ---------- CFI (PSI-39): table + cool-flame result from the data summary sheet ----------
cool = {}
try:
    import openpyxl
    wb = openpyxl.load_workbook(DOCS / "PSI-39_Science Documents_CFI_DataSummary_Spreadsheet_Jan2021.xlsx", read_only=True, data_only=True)
    ws = wb["DATA"]
    it = ws.iter_rows(values_only=True)
    hdr = [str(c or "") for c in next(it)]
    ic = next((i for i, h in enumerate(hdr) if "ext,cool" in h.replace(" ", "").lower() or "dext,cool" in h.replace(" ", "").lower()), None)
    ih = next((i for i, h in enumerate(hdr) if "ext,hot" in h.replace(" ", "").lower()), None)
    for row in it:
        if row and row[0] is not None:
            cool[str(row[0]).strip()] = (row[ic] if ic is not None else None, row[ih] if ih is not None else None)
except Exception as exc:  # spreadsheet is optional
    print("CFI summary sheet not read:", exc)
name, head, rows = read_csv("PSI-39__*CFI.csv")
for r in rows:
    o2 = num(pick(r, "Oxygen"))
    p = num(pick(r, "Pressure"))
    c, h = cool.get(pick(r, "Flex Number"), (None, None))
    out = "cool flame" if c not in (None, "") else ("hot flame only" if h not in (None, "") else "tested")
    add(39, name, pick(r, "Fuel"), "liquid", None if o2 is None else o2 * 100, "measured" if o2 is not None else "unknown",
        None if p is None else p * PSI_PER_ATM, "measured" if p is not None else "unknown", None, "unknown", out,
        notes=f"fiber {pick(r,'Fiber')}; He {pick(r,'Helium')}; outcome from CFI data summary sheet")

# ---------- BASS-II (PSI-25): material, oxygen, flow display ----------
name, head, rows = read_csv("PSI-25__*BASS-II.csv")
for r in rows:
    o2 = num(pick(r, "initial O2"))
    air = pick(r, "Air display")
    flow = num(air) if re.match(r"^\s*\d", air) else None
    add(25, name, pick(r, "Fuel Sample Material"), "solid", o2, "measured" if o2 is not None else "unknown",
        CABIN_PSI, "assumed", flow, "text" if flow is not None else "unknown", "tested", vsrc="table",
        notes=f"air display (cm/s, first reading): {air}; fan {pick(r,'Fan display')}; pressure assumed ISS cabin, not in table; outcome not in table")

# ---------- BASS (PSI-26): material and flow display (as-run test matrix) ----------
try:
    import openpyxl
    wb = openpyxl.load_workbook(DOCS / "PSI-26_Science Documents_As Run_Test Matrix.xlsx", read_only=True, data_only=True)
    ws = wb["as run matrix"]
    allrows = list(ws.iter_rows(values_only=True))
    hi = next(i for i, r in enumerate(allrows) if r and any(str(c or "").strip().lower() == "material" for c in r))
    hdr = [str(c or "").strip().lower() for c in allrows[hi]]
    imat, iair = hdr.index("material"), hdr.index("air display")
    for r in allrows[hi + 1:]:
        mat = r[imat] if r and len(r) > imat else None
        if not mat:
            continue
        air = str(r[iair] or "")
        flow = num(air) if re.match(r"^\s*\d", air) else None
        # BASS SRD (PSI-26_Science Documents_SRD_BASS.pdf): testing was restricted to cabin oxygen at or above 21 %,
        # measured each test day, at ambient cabin pressure. So 21 % is a lower bound, not a measured value.
        add(26, "PSI-26 As Run Test Matrix.xlsx", str(mat), "solid", 21.0, "text", CABIN_PSI, "assumed", flow,
            "text" if flow is not None else "unknown", "tested", vsrc="text",
            notes=f"air display (cm/s, first reading): {air}; oxygen 21 % = lower bound (SRD: cabin oxygen at or above 21 %, not in the matrix); pressure = ambient cabin (SRD), 14.7 psi assumed")
except Exception as exc:
    print("BASS as-run matrix not read:", exc)

# ---------- Saffire I, II, III ----------
for psi, pat in ((98, "PSI-98__*"), (99, "PSI-99__*"), (100, "PSI-100__*")):
    name, head, rows = read_csv(pat)
    for r in rows:
        flow = num(pick(r, "Air Flow"))
        o2 = num(pick(r, "Percent O2"))
        mat = pick(r, "Material")
        burn = pick(r, "Burn Time")
        direction = pick(r, "Flow Direction", "Direction")
        spread = pick(r, "1-g Spread Rate", "0-g Spread Length", "?-g Spread Length")
        add(psi, name, mat, "solid", o2, "measured" if o2 is not None else "unknown", CABIN_PSI, "assumed",
            flow, "text" if flow is not None else "unknown", f"burned {direction.lower()}" if direction else "tested",
            "burn_time_s", burn, vsrc="text",
            notes=f"thickness {pick(r,'Thickness')}; direction {direction}; spread info {spread}; pressure assumed cabin")

# ---------- SPICE (PSI-107): fuel and air rate ----------
name, head, rows = read_csv("PSI-107__*Spice.csv")
for r in rows:
    flow = num(pick(r, "Air Rate"))
    add(107, name, pick(r, "Fuel"), "gas", 21.0, "assumed", CABIN_PSI, "assumed", flow, "measured" if flow is not None else "unknown",
        "tested", notes="smoke-point study; oxygen and pressure assumed cabin air (not in table)")

# ---------- SAME and SAME-R ----------
for psi, pat, flowkey in ((102, "PSI-102__*SAME.csv", "Air Flow"), (101, "PSI-101__*SAME-R.csv", "Inlet velocity")):
    name, head, rows = read_csv(pat)
    for r in rows:
        flow = num(pick(r, flowkey))
        add(psi, name, pick(r, "Sample Material", "Sample Type"), "solid", 21.0, "assumed", CABIN_PSI, "assumed", flow,
            "measured" if flow is not None else "unknown", "smoke generated",
            notes="smoke particle sizes are in the investigation data files, not in this table; oxygen and pressure assumed cabin air")

# ---------- ACME BRE (PSI-20): oxygen levels per test day ----------
name, head, rows = read_csv("PSI-20__*BRE.csv")
for r in rows:
    levels = [num(x) for x in re.split(r";", pick(r, "Oxygen Conc")) if num(x) is not None]
    for lv in levels:
        add(20, name, pick(r, "Fuel Bottle"), "gas", lv, "measured", None, "unknown", None, "unknown",
            f"flames ignited that day: {pick(r,'Flames Ignited')}",
            notes="chamber pressure varied but not listed in the table; oxygen shown per test day, ignition count is for the whole day")

OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows_out)
print(f"Wrote {OUT} with {len(rows_out)} runs")
for psi in sorted(counter):
    print(f"  PSI-{psi:<4} {NAME.get(psi,''):18} {counter[psi]:4d} runs")
