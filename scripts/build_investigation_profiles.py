#!/usr/bin/env python3
"""Build data/curated/investigation_profiles.json: one summary profile per PSI combustion investigation.

Run from the repo root:  python scripts/build_investigation_profiles.py
Needs network only if data/raw/psi_json/ is missing. Text fields come from PSI; condition ranges, fuels,
outcomes and what varied come from data/curated/runs.csv. For FLEX-2 (PSI-68), whose PSI table lists an
8-fuel parameter matrix rather than executed runs, the matrix is attached as `planned_matrix` without
fabricating rows in runs.csv. Hardware groups follow the official challenge text.
"""
import csv
import html
import io
import json
import re
import time
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
RUNS = ROOT / "data" / "curated" / "runs.csv"
OUT = ROOT / "data" / "curated" / "investigation_profiles.json"
BASE = "https://psi.nasa.gov/geode-py/ws/repo/investigations/"
HEADERS = {"User-Agent": "FlameLens-hackathon/1.0 (NASA Space Apps team project)"}

IDS = [26, 25, 98, 99, 100, 107, 20, 102, 101, 47, 69, 68, 39, 159, 22, 10, 21, 23, 106]

PILLAR = {26: "Prevention", 25: "Prevention", 98: "Prevention", 99: "Prevention", 100: "Prevention",
          107: "Prevention", 20: "Prevention", 102: "Detection", 101: "Detection", 47: "Detection",
          69: "Suppression", 68: "Suppression", 39: "Suppression", 159: "Suppression", 22: "Suppression",
          10: "Other", 21: "Other", 23: "Other", 106: "Other"}

HARDWARE_GROUP = {26: "MSG flow duct (SPICE duct)", 25: "MSG flow duct (SPICE duct)", 107: "MSG flow duct (SPICE duct)",
                  106: "MSG flow duct (SPICE duct)",
                  69: "CIR / MDCA droplets", 68: "CIR / MDCA droplets", 39: "CIR / MDCA droplets",
                  20: "CIR / ACME gas flames", 159: "CIR / ACME gas flames", 10: "CIR / ACME gas flames",
                  21: "CIR / ACME gas flames", 22: "CIR / ACME gas flames", 23: "CIR / ACME gas flames",
                  98: "Cygnus spacecraft", 99: "Cygnus spacecraft", 100: "Cygnus spacecraft",
                  102: "MSG / SAME hardware", 101: "MSG / SAME hardware", 47: "MSG / SAME hardware"}

# Investigations named in the official challenge text, and why each matters for crew fire safety.
CHALLENGE_NAMED = {26, 25, 98, 99, 100, 102, 101, 47, 69, 68, 39, 159, 20, 22, 107, 106}
RELEVANCE = {
    26: "Solid-material flammability vs airflow and nitrogen-jet suppression (prevention), named in the challenge",
    25: "Solid-material flammability limits and spread rates vs airflow and oxygen (prevention), named in the challenge",
    98: "Large-scale fabric fire growth in a spacecraft (prevention), named in the challenge",
    99: "Large-scale material flammability and spread in a spacecraft (prevention), named in the challenge",
    100: "Large-scale fire growth in a spacecraft at higher flow (prevention), named in the challenge",
    107: "Sooting and smoke points of gas flames in the shared flow duct (prevention, hardware named in the challenge)",
    20: "Materials flammability in still atmospheres, emulated with gas burners (prevention), named in the challenge",
    102: "Smoke particle sizes for spacecraft smoke detection (detection), named in the challenge",
    101: "Smoke particle sizes and aging for spacecraft smoke detection (detection), named in the challenge",
    47: "Same instrument used for Arizona Road Dust in flight, separating dust from smoke (detection), named in the challenge",
    69: "Fire suppression by diluting the atmosphere with CO2 and helium (suppression), named in the challenge",
    68: "Bi-component and pure droplet burning & extinction matrix across 17–30% O2 and 0.5–3 atm (suppression hardware named in the challenge)",
    39: "Cool flames that keep burning after the visible flame goes out (suppression hardware named in the challenge)",
    159: "Highest-oxygen microgravity tests, up to 85 % oxygen, plus spherical gas cool flames (named in the challenge)",
    22: "High-voltage electric field (up to 10 kV) used to mimic partial-gravity buoyancy on flames (named in the challenge)",
    10: "Soot formation and radiative loss in normal and inverse spherical gas flames (indirect relevance)",
    21: "Coflow laminar CH4 and C2H4 diffusion flames (354 ignitions across 32 days) for soot and extinction model validation",
    23: "Spherical H2, CH4 and C2H4 diffusion flames and extinction at ~21% and ~30% O2 (lunar-relevant oxygen)",
    106: "Laminar diffusion flame structure and liftoff limits in the shared MSG flow duct (hardware named in the challenge)",
}

KEYWORDS = ["video", "camera", "radiometer", "thermocouple", "oxygen sensor", "CO2", "CO", "particle counter",
            "P-Trak", "DustTrak", "impactor", "spectrometer", "photodiode", "flow meter", "pressure transducer",
            "interferometer", "OH*", "soot", "laser", "infrared", "IR", "UV", "chemiluminescence", "gas chromatograph",
            "anemometer", "load cell", "image", "imaging"]


def clean(text):
    text = html.unescape(str(text or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def summary(text, limit=350):
    """Up to `limit` characters, cut at the end of a sentence when possible."""
    if len(text) <= limit:
        return text
    cut = text[:limit]
    ends = [m.end() for m in re.finditer(r"[.!?](\s|$)", cut)]
    return (cut[:ends[-1]].strip() if ends else cut.rsplit(" ", 1)[0] + "…")


def mentions(text):
    found = []
    for k in KEYWORDS:
        if re.search(r"(?<![A-Za-z0-9])" + re.escape(k) + r"(?![A-Za-z0-9])", text, flags=re.I if len(k) > 3 else 0):
            found.append(k)
    return found


def num(v):
    try:
        return float(v) if v not in ("", None) else None
    except ValueError:
        return None


def load_runs():
    by = {}
    with open(RUNS, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            by.setdefault(r["psi_id"], []).append(r)
    return by


def flex2_planned_matrix():
    """Parse PSI-68_Experimental_table_Flex2.csv as an explicit parameter matrix (not executed runs)."""
    paths = list(RAW.glob("PSI-68__*Flex2.csv"))
    if not paths:
        return {
            "source_table": "PSI-68_Experimental_table_Flex2.csv",
            "fuels": ["IsoOctane (pure)", "n-Octane (pure)", "Heptane (pure)", "Decane (pure)", "Ethanol (pure)",
                      "Propanol (95%) Glycerol (5%) (mixture)", "Heptane (50%) IsoOctane (50%) (mixture)",
                      "Propanol (80%) Glycerol (20%) (mixture)"],
            "droplet_diameter_mm": "1.5 - 5",
            "ambient_gas": "O2/N2 or O2/He",
            "o2_pct_levels": [17.0, 21.0, 25.0, 30.0],
            "pressure_atm_levels": [0.5, 1.0, 1.5, 2.0, 3.0],
            "pressure_psi_range": [7.35, 44.09],
            "airflow_cm_s_range": [0.1, 5.0],
            "temperature_c": 25.0,
            "note": "PSI-68 provides an 8-fuel test parameter matrix rather than an as-run per-droplet log; kept out of runs.csv so run counts reflect executed flight rows only.",
        }
    text = paths[0].read_bytes().decode("utf-8-sig", errors="replace")
    rows = [r for r in csv.reader(io.StringIO(text)) if any(c.strip() for c in r)]
    head = [h.strip() for h in rows[0]]
    recs = [dict(zip(head, [c.strip() for c in r])) for r in rows[1:]]
    fuels = [r.get("Sample (Fuel Type)", "") for r in recs if r.get("Sample (Fuel Type)")]
    return {
        "source_table": paths[0].name,
        "fuels": fuels,
        "droplet_diameter_mm": recs[0].get("Initial Droplet Diameter (mm)", "1.5 - 5") if recs else "1.5 - 5",
        "ambient_gas": recs[0].get("Ambient Gas Mixture", "O2/N2 or O2/He") if recs else "O2/N2 or O2/He",
        "o2_pct_levels": [17.0, 21.0, 25.0, 30.0],
        "pressure_atm_levels": [0.5, 1.0, 1.5, 2.0, 3.0],
        "pressure_psi_range": [7.35, 44.09],
        "airflow_cm_s_range": [0.1, 5.0],
        "temperature_c": 25.0,
        "note": "PSI-68 provides an 8-fuel test parameter matrix rather than an as-run per-droplet log; kept out of runs.csv so run counts reflect executed flight rows only.",
    }


def ranges(rows, key, basis_key, allowed):
    vals = [num(r[key]) for r in rows if r[basis_key] in allowed and num(r[key]) is not None]
    return [min(vals), max(vals)] if vals else None


def run_stats(rows):
    if not rows:
        return {"n_runs": 0, "fuels": [], "fuel_states": [], "ranges": None, "ranges_incl_assumed": None,
                "outcome_counts": {}, "varied": [], "constant": []}
    keys = (("o2_pct", "o2_basis", "o2"), ("pressure_psi", "pressure_basis", "pressure"),
            ("airflow_cm_s", "airflow_basis", "airflow"))
    rng = {k: ranges(rows, k, b, {"measured", "text"}) for k, b, _ in keys}
    rng_all = {k: ranges(rows, k, b, {"measured", "text", "assumed"}) for k, b, _ in keys}
    fuels = Counter(r["fuel_or_material"] for r in rows if r["fuel_or_material"])
    varied, constant = [], []
    for k, b, label in keys:
        r = rng_all[k]
        if r is None:
            constant.append({"condition": label, "value": None, "basis": "unknown"})
        elif r[1] - r[0] > 1e-6:
            varied.append(label)
        else:
            bases = sorted({x[b] for x in rows if num(x[k]) is not None})
            constant.append({"condition": label, "value": r[0], "basis": "/".join(bases)})
    if len(fuels) > 1:
        varied.append("fuel")
    else:
        constant.append({"condition": "fuel", "value": next(iter(fuels), None), "basis": "table"})
    return {
        "n_runs": len(rows),
        "fuels": [{"name": n, "runs": c} for n, c in fuels.most_common(8)],
        "n_distinct_fuels": len(fuels),
        "fuel_states": sorted({r["fuel_state"] for r in rows if r["fuel_state"]}),
        "ranges": rng,
        "ranges_incl_assumed": rng_all,
        "outcome_counts": dict(Counter(r["outcome"] for r in rows)),
        "varied": varied,
        "constant": constant,
    }


CACHE = ROOT / "data" / "raw" / "psi_json"  # git-ignored; lets a rerun skip records already fetched


def fetch(psi_id):
    """PSI record as a dict, cached in data/raw/psi_json. Returns None if the network keeps failing."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"PSI-{psi_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    req = urllib.request.Request(BASE + f"PSI-{psi_id}", headers=HEADERS)
    for attempt in range(5):  # venue network is unreliable and some records are several MB
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                raw = r.read().decode("utf-8", errors="replace")
            info = json.loads(raw)
            path.write_text(raw, encoding="utf-8")
            return info
        except Exception as exc:
            print(f"  PSI-{psi_id} attempt {attempt + 1} failed: {exc}")
            time.sleep(3)
    return None


def fallback_info(psi_id):
    """Title, acronym and DOI from data/curated/investigations.csv when PSI cannot be reached."""
    path = ROOT / "data" / "curated" / "investigations.csv"
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["psi_id"] == f"PSI-{psi_id}":
                return {"investigationAcronym": r["acronym"], "title": r["title"], "doi": r["doi"],
                        "licenseIdentifier": r["license"], "projectType": r["project_type"],
                        "flightProgram": r.get("flight_platform", ""), "_fallback": True}
    return {"_fallback": True}


def main():
    runs = load_runs()
    profiles = []
    for n in IDS:
        info = fetch(n)
        fetched = info is not None
        if not fetched:
            info = fallback_info(n)
        texts = {k: clean(info.get(src)) for k, src in
                 (("objectives", "objective"), ("approach", "approach"), ("hypothesis", "hypothesis"),
                  ("research_impacts", "researchImpacts"))}
        psi = f"PSI-{n}"
        stats = run_stats(runs.get(psi, []))
        p = {
            "psi_id": psi,
            "acronym": clean(info.get("investigationAcronym")) or psi,
            "title": clean(info.get("title")),
            "doi": info.get("doi") or "",
            "license": info.get("licenseIdentifier") or "",
            "psi_url": f"https://psi.nasa.gov/physci/repo/data/investigations/{psi}",
            "pillar": PILLAR[n],
            "hardware_group": HARDWARE_GROUP[n],
            "hardware": clean(info.get("experimentHardware")),
            "platform": clean(info.get("flightProgram")),
            "project_type": clean(info.get("projectType")),
            "start_date": info.get("investigationStartDate") or "",
            "end_date": info.get("investigationEndDate") or "",
            **texts,
            **{k + "_summary": summary(v) for k, v in texts.items()},
            "measurements_mentioned": mentions(" ".join([texts["objectives"], texts["approach"], texts["hypothesis"]])),
            "publications_count": len(info.get("publications") or []),
            "challenge_mentions": n in CHALLENGE_NAMED,
            "relevance": RELEVANCE[n],
            "psi_text_fetched": fetched,
            **stats,
        }
        if n == 68:
            p["planned_matrix"] = flex2_planned_matrix()
        profiles.append(p)
        print(f"{psi} {p['acronym']}: {p['n_runs']} runs, varied {p['varied']}, {len(p['measurements_mentioned'])} measurement words")
    order = {"Prevention": 0, "Detection": 1, "Suppression": 2, "Other": 3}
    profiles.sort(key=lambda p: (order[p["pillar"]], p["acronym"]))
    OUT.write_text(json.dumps(profiles, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB, {len(profiles)} profiles)")


if __name__ == "__main__":
    main()
