#!/usr/bin/env python3
"""Fetch peer-reviewed NASA publications per combustion investigation from the public NASA NTRS API.

Writes data/curated/papers.csv (ntrs_id, title, year, psi_id, investigation, abstract, pdf_url, ntrs_url).
Run from the repo root: python scripts/fetch_ntrs_papers.py
"""
import concurrent.futures
import csv
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "curated" / "papers.csv"
NTRS_SEARCH = "https://ntrs.nasa.gov/api/citations/search"
HEADERS = {
    "User-Agent": "FlameLens-hackathon/1.0 (NASA Space Apps team project)",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# (psi_id, investigation_label, query, must_match_any_substring)
QUERIES = [
    ("PSI-25", "BASS-II", "Burning and Suppression of Solids II BASS-II", ("bass", "burning and suppression of solids")),
    ("PSI-26", "BASS", "Burning and Suppression of Solids microgravity flame spread", ("bass", "burning and suppression of solids")),
    ("PSI-98", "Saffire", "Spacecraft Fire Experiment Saffire microgravity", ("saffire", "spacecraft fire")),
    ("PSI-107", "SPICE", "Smoke Point In Co-flow Experiment SPICE microgravity", ("spice", "smoke point")),
    ("PSI-20", "ACME BRE", "Burning Rate Emulator ACME microgravity", ("burning rate emulator", "bre")),
    ("PSI-101", "SAME-R", "Smoke Aerosol Measurement Experiment SAME microgravity", ("smoke aerosol", "same")),
    ("PSI-47", "DAFT", "Dust and Aerosol Measurement Feasibility Test microgravity", ("dust", "aerosol")),
    ("PSI-69", "FLEX", "Flame Extinguishment Experiment FLEX droplet microgravity", ("flame extinguishment", "flex", "droplet")),
    ("PSI-39", "CFI", "cool flame droplet combustion microgravity International Space Station", ("cool flame", "droplet")),
    ("PSI-159", "ACME CFI-G", "spherical diffusion cool flame microgravity ACME", ("cool flame", "spherical", "acme")),
    ("PSI-22", "ACME E-FIELD", "Electric-Field Effects on Laminar Diffusion Flames microgravity", ("electric-field", "electric field", "e-field")),
    ("PSI-106", "SLICE", "Structure and Liftoff In Combustion Experiment SLICE microgravity", ("liftoff", "slice")),
    ("FUTURE", "Saffire IV-VI / Lunar (LUCI, FM2, SoFIE)", "Saffire reduced pressure flammability microgravity spacecraft fire", ("saffire", "sofie", "lunar", "flammability")),
]


def clean(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()


def query_one(item):
    import time
    psi_id, inv, q, must = item
    payload = json.dumps({"q": q, "page": {"size": 12, "from": 0}}).encode("utf-8")
    data = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(NTRS_SEARCH, data=payload, headers=HEADERS, method="POST")
            with urllib.request.urlopen(req, timeout=45) as r:
                data = json.loads(r.read().decode("utf-8", errors="replace"))
            break
        except Exception:
            if attempt == 3:
                raise
            time.sleep(1.5 * (attempt + 1))
    results = data.get("results") or []
    picked = []
    for doc in results:
        cid = doc.get("id")
        title = clean(doc.get("title"))
        abstract = clean(doc.get("abstract"))
        hay = (title + " " + abstract).lower()
        if not cid or not title:
            continue
        if must and not any(m in hay for m in must):
            continue
        pub_date = clean(doc.get("distributionDate") or doc.get("created") or "")
        year_m = re.search(r"(19|20)\d{2}", pub_date)
        year = year_m.group(0) if year_m else ""
        downloads = doc.get("downloads") or []
        pdf_url = ""
        for dl in downloads:
            links = (dl.get("links") or {})
            pdf = links.get("pdf") or ""
            if pdf:
                pdf_url = f"https://ntrs.nasa.gov{pdf}" if pdf.startswith("/") else pdf
                break
        picked.append({
            "ntrs_id": str(cid),
            "title": title,
            "year": year,
            "psi_id": psi_id,
            "investigation": inv,
            "abstract": abstract[:600],
            "pdf_url": pdf_url,
            "ntrs_url": f"https://ntrs.nasa.gov/citations/{cid}",
        })
        if len(picked) >= 3:
            break
    return inv, picked


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    all_rows = []
    seen = set()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        futs = {ex.submit(query_one, q): q[1] for q in QUERIES}
        for f in concurrent.futures.as_completed(futs):
            inv = futs[f]
            try:
                _, rows = f.result()
                print(f"  {inv}: {len(rows)} papers")
                for r in rows:
                    key = (r["ntrs_id"], r["psi_id"])
                    if key not in seen:
                        seen.add(key)
                        all_rows.append(r)
            except Exception as exc:
                print(f"  {inv} FAILED: {exc}")

    all_rows.sort(key=lambda r: (r["psi_id"], -(int(r["year"]) if r["year"].isdigit() else 0), r["ntrs_id"]))
    fields = ["ntrs_id", "title", "year", "psi_id", "investigation", "abstract", "pdf_url", "ntrs_url"]
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(all_rows)
    print(f"Wrote {OUT} ({len(all_rows)} papers)")


if __name__ == "__main__":
    main()
