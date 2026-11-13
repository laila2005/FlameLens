#!/usr/bin/env python3
"""Download the Experimental Table CSVs of the PSI combustion investigations.

Run from the repo root:  python scripts/fetch_psi.py

What it does (a few dozen small requests, not a crawl):
  1. Searches PSI for "combustion" (the same call the PSI website makes).
  2. For every investigation that has an "Experimental table" file, downloads the CSV
     into data/raw/ (git-ignored).
  3. Writes data/curated/investigations.csv (id, acronym, title, DOI, platform, license,
     table file names). PSI asks users to cite the DOI, so this file is committed.

The PSI web endpoints are unofficial and may change. Data license: CC0-1.0.
"""
import csv
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://psi.nasa.gov/geode-py/ws"
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
CURATED = ROOT / "data" / "curated"
HEADERS = {"User-Agent": "FlameLens-hackathon/1.0 (NASA Space Apps team project)"}


def get(url, binary=False):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", errors="replace")


def search(term="combustion", size=50):
    url = f"{BASE}/repo/search?term={urllib.parse.quote(term)}&source=psi&type=investigation&from=0&size={size}"
    hits = json.loads(get(url))["hits"]["hits"]
    return [h["_source"] for h in hits]


def download_table(psi_id, file_name, versions):
    q = urllib.parse.quote(file_name)
    for v in versions:
        url = f"{BASE}/studies/{psi_id}/download?file={q}&version={v}&redirect=false"
        try:
            signed = get(url).strip()
            if signed.startswith("http"):
                return get(signed, binary=True)
        except Exception as exc:  # try the next version number
            last = exc
    raise RuntimeError(f"could not download {file_name}: {last}")


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    CURATED.mkdir(parents=True, exist_ok=True)
    rows = []
    for src in search():
        psi_id = src.get("Accession")
        if not psi_id:
            continue
        time.sleep(0.3)
        info = json.loads(get(f"{BASE}/repo/investigations/{psi_id}"))
        tables = info.get("experimentalTable") or []
        saved = []
        for t in tables:
            name = t["file_name"]
            versions = [t.get("version"), 1, info.get("version")]
            versions = [v for v in dict.fromkeys(versions) if v]
            try:
                data = download_table(psi_id, name, versions)
            except Exception as exc:
                print(f"  FAILED {psi_id} {name}: {exc}")
                continue
            out = RAW / f"{psi_id}__{name.replace(' ', '_')}"
            out.write_bytes(data)
            saved.append(out.name)
            print(f"  saved {out.name} ({len(data)} bytes)")
            time.sleep(0.3)
        rows.append({
            "psi_id": psi_id,
            "acronym": info.get("investigationAcronym") or "",
            "title": info.get("title") or src.get("Title") or "",
            "doi": info.get("doi") or "",
            "project_type": info.get("projectType") or "",
            "flight_platform": src.get("Flight Platform") or "",
            "research_area": info.get("researchArea") or "",
            "license": info.get("licenseIdentifier") or "",
            "table_files": ";".join(saved),
        })
        print(f"{psi_id} {rows[-1]['acronym'] or rows[-1]['title'][:40]}: {len(saved)} table(s)")
    rows.sort(key=lambda r: int(r["psi_id"].split("-")[1]))
    with open(CURATED / "investigations.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {CURATED / 'investigations.csv'} ({len(rows)} investigations)")


if __name__ == "__main__":
    main()
