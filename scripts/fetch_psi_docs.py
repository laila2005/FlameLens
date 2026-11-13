#!/usr/bin/env python3
"""Download a short list of small PSI documents (test matrices, readmes, final reports).

Run from the repo root:  python scripts/fetch_psi_docs.py

Files go to data/raw/docs/ (git-ignored). Only small files are fetched. Unofficial PSI
endpoints, data license CC0-1.0, cite the investigation DOI when you use anything.
"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://psi.nasa.gov/geode-py/ws"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "docs"
HEADERS = {"User-Agent": "FlameLens-hackathon/1.0 (NASA Space Apps team project)"}

# (PSI id, part of the file name)
WANTED = [
    (25, "BASS-II_Test.Matrices.xlsx"),
    (25, "BASS-II_ReadMe.docx"),
    (25, "Fan calibration data.xlsx"),
    (26, "As Run_Test Matrix.xlsx"),
    (26, "Planned_Test Matrix.xlsx"),
    (26, "BASS_FinalReport.pdf"),
    (39, "CFI_DataSummary_Spreadsheet_Jan2021.xlsx"),
    (39, "CFI Science Final Report.pdf"),
    (102, "SAME_Final Science Report.pdf"),
    (101, "SAME-R_Final Report.pdf"),
    (47, "DAFT_30Day.PostFlightReport.pdf"),
    (98, "SAFFIRE-I and SAFFIRE-III Readme.docx"),
    (98, "SAFFIRE Objectives, Development and Status.pdf"),
    (107, "SPICE_FinalReport.pdf"),
    (107, "DotsonThesis"),
    (107, "SPICE_30-DayPostFlightReport"),
    (107, "Laminar Smoke Points in Coflow Measured Aboard ISS"),
]


def get(url, binary=False):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", errors="replace")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cache = {}
    for psi_id, part in WANTED:
        if psi_id not in cache:
            cache[psi_id] = json.loads(get(f"{BASE}/repo/investigations/PSI-{psi_id}"))
            time.sleep(0.3)
        info = cache[psi_id]
        found = None
        for key in ("added", "files"):
            for f in info.get(key) or []:
                if isinstance(f, dict) and part in f.get("file_name", ""):
                    found = f
                    break
            if found:
                break
        if not found:
            print(f"NOT FOUND PSI-{psi_id} {part}")
            continue
        name = found["file_name"]
        versions = [found.get("version"), info.get("version"), 1]
        data = None
        for v in dict.fromkeys(x for x in versions if x):
            try:
                url = f"{BASE}/studies/PSI-{psi_id}/download?file={urllib.parse.quote(name)}&version={v}&redirect=false"
                signed = get(url).strip()
                if signed.startswith("http"):
                    data = get(signed, binary=True)
                    break
            except Exception as exc:
                last = exc
        if data is None:
            print(f"FAILED PSI-{psi_id} {name}: {last}")
            continue
        (OUT / name).write_bytes(data)
        print(f"saved {name} ({len(data)/1e6:.2f} MB)")
        time.sleep(0.3)


if __name__ == "__main__":
    main()
