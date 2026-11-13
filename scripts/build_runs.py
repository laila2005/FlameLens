#!/usr/bin/env python3
"""Build data/curated/runs.csv from the PSI Experimental Table CSVs in data/raw/.

Run from the repo root, after scripts/fetch_psi.py and scripts/fetch_psi_docs.py:
    python scripts/build_runs.py

Every row says where each condition came from (the *_basis columns):
  measured  = a column in the PSI table
  text      = parsed from a free-text cell or report table (lower confidence)
  assumed   = not in the table, taken from the platform (for example ISS cabin air). Check these.
  unknown   = not available, left empty. "No evidence" is a valid result for the dashboard.

Needs openpyxl only for the CFI and BASS as-run spreadsheets (pip install openpyxl).
"""
import csv
import io
import os
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
        20: "ACME BRE", 102: "SAME", 101: "SAME-R", 47: "DAFT", 69: "FLEX", 68: "FLEX-2", 39: "CFI",
        159: "ACME CFI-G", 22: "ACME E-FIELD Flames", 10: "ACME Flame Design",
        21: "ACME CLD Flame", 23: "ACME s-Flame", 106: "SLICE"}

FIELDS = ["run_id", "psi_id", "investigation", "pillar", "fuel_or_material", "fuel_state", "o2_pct", "o2_basis",
          "pressure_psi", "pressure_basis", "airflow_cm_s", "airflow_basis", "gravity_g", "outcome",
          "metric_name", "metric_value", "value_source", "source_table", "doi", "confidence", "notes"]

# Documented BASS-II outcomes from NASA/TM-20210011385 (Sec. 3.1.1, Table 5.1, Table 7.1, and CSV notes)
BASS2_OUTCOMES = {
    "F1": "no ignition", "F2": "no ignition", "F3": "no ignition",
    "O12": "no ignition", "P8": "no ignition",
    "T9": "no ignition", "T10": "no ignition", "T12": "no ignition",
    "T23": "no ignition", "T28a": "no ignition", "T28b": "no ignition",
    "B18": "blowoff", "B19": "blowoff", "O7": "blowoff", "O8b": "blowoff",
    "O9": "blowoff", "O11": "blowoff", "O22": "blowoff", "T21": "blowoff",
    "B14": "quenched", "B21": "quenched", "O4": "quenched", "O6": "quenched",
    "O8a": "quenched", "O14": "quenched", "O19": "quenched", "P1": "quenched",
    "P5": "quenched", "P9": "quenched", "P10": "quenched", "P13a": "quenched",
    "P13b": "quenched", "P22a": "quenched", "P22b": "quenched", "P25": "quenched",
    "T4": "quenched", "T13": "quenched", "T14": "quenched", "T18": "quenched",
    "T20": "quenched", "T22": "quenched",
    **{f"M{i}": "burned" for i in range(1, 21)},
    **{t: "burned" for t in ("T1", "T2", "T5", "T6", "T11", "T15", "T16", "T17", "T19", "T24", "T25", "T26", "T27", "T29")},
}


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


def clean_gas_formula(s, test_type=""):
    """Fix spreadsheet drag-fill increments in NASA CSVs (e.g., '40% CH14' -> '40% CH4', 'with N5' -> 'with N2')."""
    raw = str(s or "").strip()
    fixed = re.sub(r"\bwith\s+N[3-9]\b", "with N2", raw)
    if "methane" in test_type.lower() or re.search(r"\bCH(?:[5-9]|\d{2,})\b", fixed):
        fixed = re.sub(r"\bCH(?:[5-9]|\d{2,})\b", "CH4", fixed)
    if "ethylene" in test_type.lower():
        fixed = re.sub(r"\bC2H(?:[5-9]|\d{2,})\b", "C2H4", fixed)
    elif re.search(r"\bC2H(?:[7-9]|\d{2,})\b", fixed):
        fixed = re.sub(r"\bC2H(?:[7-9]|\d{2,})\b", "C2H4", fixed)
    return fixed, raw


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

# ---------- BASS-II (PSI-25): material, oxygen, flow display, and report outcomes ----------
name, head, rows = read_csv("PSI-25__*BASS-II.csv")
for r in rows:
    tno = pick(r, "Test #").strip()
    o2 = num(pick(r, "initial O2"))
    air = pick(r, "Air display")
    flow = num(air) if re.match(r"^\s*\d", air) else None
    out = BASS2_OUTCOMES.get(tno, "tested")
    out_note = "outcome from NASA/TM-20210011385" if tno in BASS2_OUTCOMES else "outcome not in table"
    add(25, name, pick(r, "Fuel Sample Material"), "solid", o2, "measured" if o2 is not None else "unknown",
        CABIN_PSI, "assumed", flow, "text" if flow is not None else "unknown", out, vsrc="table",
        notes=f"test {tno}; air display (cm/s, first reading): {air}; fan {pick(r,'Fan display')}; pressure assumed ISS cabin; {out_note}")

# ---------- BASS (PSI-26): material and flow display (as-run test matrix) ----------
try:
    import openpyxl
    wb = openpyxl.load_workbook(DOCS / "PSI-26_Science Documents_As Run_Test Matrix.xlsx", read_only=True, data_only=True)
    ws = wb["as run matrix"]
    allrows = list(ws.iter_rows(values_only=True))
    hi = next(i for i, r in enumerate(allrows) if r and any(str(c or "").strip().lower() == "material" for c in r))
    hdr = [str(c or "").strip().lower() for c in allrows[hi]]
    imat, iair = hdr.index("material"), hdr.index("air display")
    # Per-test atmosphere and crew observations recorded in the same as-run matrix (columns AA..AD):
    # "O2 % by volume" is a fraction (0.221 = 22.1 %), "pressure, atm" is total pressure in atmospheres.
    io2 = next((i for i, h in enumerate(hdr) if h.startswith("o2 % by volume")), None)
    ipr = next((i for i, h in enumerate(hdr) if h.startswith("pressure, atm")), None)
    iobs = next((i for i, h in enumerate(hdr) if h.startswith("test observations")), None)
    ATM_PSI = 14.6959
    # Off by default: switching it on changes ISS-cabin counts (336 -> 427) and the engine's nearest runs, so the
    # cached AI explanations must be regenerated in the same change (scripts/build_explanations.py).
    USE_BASS_ATMOSPHERE = os.environ.get("FLAMELENS_BASS_ATMOSPHERE") == "1"
    if not USE_BASS_ATMOSPHERE:
        io2 = ipr = None
    for r in allrows[hi + 1:]:
        mat = r[imat] if r and len(r) > imat else None
        if not mat:
            continue
        air = str(r[iair] or "")
        flow = num(air) if re.match(r"^\s*\d", air) else None
        o2v = r[io2] if io2 is not None and len(r) > io2 else None
        prv = r[ipr] if ipr is not None and len(r) > ipr else None
        obs = " ".join(str(r[iobs] or "").split()) if iobs is not None and len(r) > iobs else ""
        o2_ok = isinstance(o2v, (int, float)) and 0.1 < o2v < 0.6
        pr_ok = isinstance(prv, (int, float)) and 0.5 < prv < 1.5
        o2_pct = round(o2v * 100, 3) if o2_ok else None
        psi = round(prv * ATM_PSI, 3) if pr_ok else CABIN_PSI
        add(26, "PSI-26 As Run Test Matrix.xlsx", str(mat), "solid", o2_pct, "measured" if o2_ok else "unknown",
            psi, "measured" if pr_ok else "assumed", flow,
            "text" if flow is not None else "unknown", "tested", vsrc="table" if (o2_ok or pr_ok) else "text",
            notes=(f"air display (cm/s, first reading): {air}; "
                   + (f"O2 {o2v:g} volume fraction and pressure {prv:g} atm (x 14.6959 = psi) from the as-run matrix; "
                      if (o2_ok and pr_ok) else "SRD_BASS.pdf p.8 requires initial ISS cabin >= 21% O2; per-test O2 and pressure are in the as-run matrix but not applied yet (FLAMELENS_BASS_ATMOSPHERE switch in build_runs.py); pressure assumed ISS cabin; ")
                   + (f"crew observation: {obs[:220]}" if obs else "")))
except Exception as exc:
    print("BASS as-run matrix not read:", exc)

# ---------- Saffire I, II, III ----------
for psi, pat in ((98, "PSI-98__*"), (99, "PSI-99__*"), (100, "PSI-100__*")):
    name, head, rows = read_csv(pat)
    last_mat = ""
    for r in rows:
        snum = pick(r, "Sample Number").strip()
        # Skip camera flow-visualization rows (F1C1/F1C2, F2C1/F2C2) and table footnotes (Note 1..4)
        if not snum or snum.lower().startswith(("f1c", "f2c", "note ")):
            continue
        mat = pick(r, "Material") or last_mat
        if mat:
            last_mat = mat
        flow = num(pick(r, "Air Flow"))
        o2 = num(pick(r, "Percent O2"))
        burn = pick(r, "Burn Time")
        direction = pick(r, "Flow Direction", "Direction")
        spread = pick(r, "?-g Spread Length", "0-g Spread Length", "1-g Spread Rate")
        if "insignificant" in burn.lower():
            outcome = "no sustained burn"
        elif direction:
            outcome = f"burned {direction.lower()}"
        else:
            outcome = "tested"
        add(psi, name, mat, "solid", o2, "measured" if o2 is not None else "unknown", CABIN_PSI, "assumed",
            flow, "text" if flow is not None else "unknown", outcome,
            "burn_time_s" if burn and num(burn) is not None else "", burn if num(burn) is not None else "", vsrc="text",
            notes=f"sample {snum}; thickness {pick(r,'Thickness','Samle Thickness')}; direction {direction}; burn time '{burn}'; spread info {spread}; pressure assumed cabin")

# ---------- SPICE (PSI-107): fuel and air rate ----------
name, head, rows = read_csv("PSI-107__*Spice.csv")
for r in rows:
    flow = num(pick(r, "Air Rate"))
    add(107, name, pick(r, "Fuel"), "gas", 21.0, "assumed", CABIN_PSI, "assumed", flow, "measured" if flow is not None else "unknown",
        "tested", notes="smoke-point study; oxygen and pressure assumed cabin air (not in table)")

# ---------- SLICE (PSI-106): laminar diffusion flame structure & liftoff in MSG flow duct ----------
name, head, rows = read_csv("PSI-106__*Slice.csv")
for r in rows:
    tdate = pick(r, "Test Date")
    raw_fuel = pick(r, "Fuel Type")
    m_fuel = re.match(r"^([0-9]+%\s*[A-Za-z0-9]+(?:\s*\(balance\s*N2\))?)", raw_fuel)
    fuel = m_fuel.group(1) if m_fuel else raw_fuel
    add(106, name, fuel, "gas", 21.0, "assumed", CABIN_PSI, "assumed", None, "unknown",
        "tested", vsrc="table",
        notes=f"test date: {tdate}; fuel detail: {raw_fuel}; MSG fan-driven flow duct (per-test coflow velocity in image overlays, not in summary table); oxygen and pressure assumed ISS cabin air")

# ---------- SAME and SAME-R ----------
for psi, pat, flowkey in ((102, "PSI-102__*SAME.csv", "Air Flow"), (101, "PSI-101__*SAME-R.csv", "Inlet velocity")):
    name, head, rows = read_csv(pat)
    for r in rows:
        flow = num(pick(r, flowkey))
        add(psi, name, pick(r, "Sample Material", "Sample Type"), "solid", 21.0, "assumed", CABIN_PSI, "assumed", flow,
            "measured" if flow is not None else "unknown", "smoke generated",
            notes="smoke particle sizes are in the investigation data files, not in this table; oxygen and pressure assumed cabin air")

# ---------- DAFT / DAFT-2 (PSI-47): dust aerosol validation of modified P-Trak vs DustTrak ----------
name, head, rows = read_csv("PSI-47__*DAFT.csv")
for r in rows:
    sess = pick(r, "Session Name")
    day = pick(r, "Actual Day")
    hw = pick(r, "Hardware Description")
    loc = pick(r, "Sampled Location")
    add(47, name, "Arizona Road Dust (ARD Fine)", "solid", 21.0, "assumed", CABIN_PSI, "assumed", None, "unknown",
        "dust aerosol sampled", vsrc="table",
        notes=f"session {sess} ({day}); hardware: {hw}; location: {loc}; flight dust diameters in smoke_dust_sizes.csv (DAFT Retrieved Data Summary.xls); ISS cabin air assumed")

# ---------- ACME BRE (PSI-20): oxygen levels per test day ----------
name, head, rows = read_csv("PSI-20__*BRE.csv")
for r in rows:
    levels = [num(x) for x in re.split(r";", pick(r, "Oxygen Conc")) if num(x) is not None]
    for lv in levels:
        add(20, name, pick(r, "Fuel Bottle"), "gas", lv, "measured", None, "unknown", None, "unknown",
            f"flames ignited that day: {pick(r,'Flames Ignited')}",
            notes="chamber pressure varied but not listed in the table; oxygen shown per test day, ignition count is for the whole day")

# ---------- ACME CLD Flame (PSI-21): coflow laminar diffusion flames (CH4, C2H4) ----------
name, head, rows = read_csv("PSI-21__*CLD_Flame.csv")
for r in rows:
    ttype = pick(r, "Test Type")
    tday = pick(r, "Test Day")
    fuel_clean, fuel_raw = clean_gas_formula(pick(r, "Fuel Bottle"), ttype)
    fconc = pick(r, "Fuel conc. Range")
    ign = pick(r, "Flames ignited")
    autofill_note = f" (normalized from spreadsheet autofill '{fuel_raw}')" if fuel_clean != fuel_raw else ""
    add(21, name, fuel_clean, "gas", None, "unknown", None, "unknown", None, "unknown",
        f"flames ignited that day: {ign}", "flames_ignited", ign, vsrc="table",
        notes=f"{ttype}; test day {tday}; fuel concentration range {fconc} (N2 diluted){autofill_note}; Fuel MFC {pick(r,'Fuel MFC')} slpm, N2 MFC {pick(r,'N2 MFC')} slpm; chamber O2 and pressure not in summary table")

# ---------- ACME E-FIELD Flames (PSI-22): electric-field effects mimicking partial gravity ----------
name, head, rows = read_csv("PSI-22__*E-FIELD*.csv")
efield_days = []
seen_efield = set()
for r in rows:
    tday = pick(r, "Test Day").strip()
    fconc = pick(r, "Fuel Conc").strip()
    if tday:
        key = (tday, pick(r, "Mesh Polarity").strip(), pick(r, "Fuel Bottle").strip(), pick(r, "Flames Ignited").strip())
        is_dup = key in seen_efield
        if not is_dup:
            seen_efield.add(key)
            efield_days.append({"row": r, "concs": [fconc] if fconc else [], "skip": False})
        else:
            efield_days.append({"row": r, "concs": [], "skip": True})
    elif fconc and efield_days and not efield_days[-1]["skip"]:
        if fconc not in efield_days[-1]["concs"]:
            efield_days[-1]["concs"].append(fconc)

for entry in efield_days:
    if entry["skip"]:
        continue
    r = entry["row"]
    ttype = pick(r, "Test Type")
    tday = pick(r, "Test Day")
    pol = pick(r, "Mesh Polarity")
    fuel_clean, _ = clean_gas_formula(pick(r, "Fuel Bottle"), ttype)
    ign = pick(r, "Flames Ignited")
    concs = ", ".join(entry["concs"])
    add(22, name, fuel_clean, "gas", None, "unknown", None, "unknown", None, "unknown",
        f"flames ignited that day: {ign}", "flames_ignited", ign, vsrc="table",
        notes=f"{ttype}; test day {tday}; mesh polarity: {pol} (up to 10 kV ion-driven convection mimicking partial gravity); fuel conc: {concs}; chamber O2 and pressure not in summary table")

# ---------- ACME s-Flame (PSI-23): spherical diffusion flames (~21% and ~30% O2 at ~1 atm) ----------
name, head, rows = read_csv("PSI-23__*s-Flame.csv")
for r in rows:
    ttype = pick(r, "Test Type")
    tday = pick(r, "Test Day")
    atm_clean, atm_raw = clean_gas_formula(pick(r, "Atmosphere"))
    fuel_clean, fuel_raw = clean_gas_formula(pick(r, "Fuel Bottle"))
    ign = pick(r, "Flames Ignited")
    o2_vals = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\s*%", atm_clean)]
    if not o2_vals:
        o2_vals = [None]
    for o2v in o2_vals:
        add(23, name, fuel_clean, "gas", o2v, "text" if o2v is not None else "unknown",
            CABIN_PSI, "text", None, "unknown",
            f"flames ignited that day: {ign}", "flames_ignited", ign, vsrc="table",
            notes=f"{ttype}; test day {tday}; atmosphere '{atm_clean}' (table footnote: ~1 atm nominal, pressure rises and O2 drops with vitiation); ignition count is for the whole test day")

# ---------- SPICE smoke points (per flame) from the Dotson thesis, linked by scripts/extract_spice_smoke_points.py ----------
SMOKE = ROOT / "data" / "curated" / "spice_smoke_points.csv"
if SMOKE.exists():
    by_run = {}
    for sp in csv.DictReader(open(SMOKE, encoding="utf-8")):
        if sp.get("run_id"):
            by_run.setdefault(sp["run_id"], []).append(sp)
    linked = 0
    for row in rows_out:
        pts = by_run.get(row["run_id"])
        if not pts:
            continue
        row["outcome"] = "smoke point"
        row["metric_name"], row["metric_value"] = "smoke_point_length_mm", pts[0]["smoke_point_length_mm"]
        row["notes"] += "; " + "; ".join(
            f"smoke point at {sp['gmt']} GMT: fuel {sp['fuel_rate_mg_s']} mg/s, air {sp['air_rate_cm_s']} cm/s, "
            f"luminous length {sp['smoke_point_length_mm']} mm ({sp['source_ref']})" for sp in pts)
        linked += 1
    print(f"SPICE smoke points linked to {linked} runs from {SMOKE.name}")

OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows_out)
print(f"Wrote {OUT} with {len(rows_out)} runs across {len(counter)} spaceflight investigations")
for psi in sorted(counter):
    print(f"  PSI-{psi:<4} {NAME.get(psi,''):22} {counter[psi]:4d} runs")
