"""Build the NASA report library for "Ask the NASA reports" (data/curated/doc_chunks.jsonl).

Based on Dai's build_library.py (team AstroSpark): every downloaded PSI document in data/raw/docs (reports, theses,
readmes, test matrices) becomes text chunks tagged with the PSI investigation, file name and page, so an answer can
quote the exact page it came from. Built locally (data/raw is not deployed); the chunk file ships in data/curated.

Changes from the original: our folders; page numbers kept as PDF page numbers ("PDF page 12"); .xls read with xlrd;
.docx read without extra packages; camera-frame logs (Saffire "MergeResult" spreadsheets) skipped because they are
image indexes, not findings; chunks keep their page text whole when short; a manifest records every file's status.

Run from the repo root:  python scripts/build_doc_library.py     (needs pypdfium2 or pypdf, openpyxl, xlrd)
"""
import csv
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "data" / "raw" / "docs"
OUT = ROOT / "data" / "curated" / "doc_chunks.jsonl"
MANIFEST = ROOT / "data" / "curated" / "doc_manifest.csv"
SKIP = re.compile(r"MergeResult", re.I)       # Saffire camera-frame download logs, not findings
SIZE, OVERLAP = 1100, 150                       # Dai's chunk size and overlap (characters)
MAX_SHEET_ROWS = 250


def investigations():
    names = {}
    with open(ROOT / "data" / "curated" / "investigations.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            names[r["psi_id"]] = r.get("acronym") or r["psi_id"]
    return names


def psi_of(name):
    m = re.match(r"PSI-(\d+)", name)
    return f"PSI-{m.group(1)}" if m else ""


def clean(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


def add_chunks(chunks, path, ref, page, text, names):
    text = clean(text)
    if len(text) < 40:          # blank pages, figure-only pages
        return
    if len(re.findall(r"(?:\.\s?){6,}|(?:…\s?){3,}", text)) >= 3:   # table of contents / list of figures
        return
    psi = psi_of(path.name)
    start = 0
    while start < len(text):
        piece = text[start:start + SIZE]
        chunks.append({"chunk_id": f"doc_{len(chunks) + 1:06d}", "psi_id": psi, "investigation": names.get(psi, psi),
                       "source_file": path.name, "source_ref": ref, "page": page, "text": piece})
        if start + SIZE >= len(text):
            break
        start += SIZE - OVERLAP


def read_pdf(path, chunks, names):
    try:
        import pypdfium2 as pdfium
        doc = pdfium.PdfDocument(str(path))
        pages = [doc[i].get_textpage().get_text_range() for i in range(len(doc))]
    except ImportError:
        from pypdf import PdfReader
        pages = [p.extract_text() or "" for p in PdfReader(str(path)).pages]
    for i, text in enumerate(pages, 1):
        add_chunks(chunks, path, f"PDF page {i}", i, text, names)
    return len(pages)


def read_docx(path, chunks, names):
    with zipfile.ZipFile(path) as z:
        root = ElementTree.fromstring(z.read("word/document.xml"))
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    paras = ["".join(t.text or "" for t in p.iter(ns + "t")) for p in root.iter(ns + "p")]
    add_chunks(chunks, path, "Word document (no page numbers)", None, "\n".join(paras), names)
    return 1


def sheet_text(title, rows):
    lines = [f"Sheet: {title}"]
    for r in rows[:MAX_SHEET_ROWS]:
        cells = [clean(c) for c in r if c not in (None, "")]
        if cells:
            lines.append(" | ".join(cells))
    return "\n".join(lines)


def read_xlsx(path, chunks, names):
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    for ws in wb.worksheets:
        rows = list(ws.iter_rows(values_only=True))
        add_chunks(chunks, path, f"Excel sheet: {ws.title}", None, sheet_text(ws.title, rows), names)
    return len(wb.worksheets)


def read_xls(path, chunks, names):
    import xlrd
    wb = xlrd.open_workbook(str(path))
    for sh in wb.sheets():
        rows = [sh.row_values(i) for i in range(min(sh.nrows, MAX_SHEET_ROWS))]
        add_chunks(chunks, path, f"Excel sheet: {sh.name}", None, sheet_text(sh.name, rows), names)
    return wb.nsheets


READERS = {".pdf": read_pdf, ".docx": read_docx, ".xlsx": read_xlsx, ".xls": read_xls}


def main():
    names = investigations()
    chunks, manifest = [], []
    for path in sorted(p for p in DOCS.iterdir() if p.is_file()):
        reader = READERS.get(path.suffix.lower())
        before = len(chunks)
        if SKIP.search(path.name):
            status, units = "skipped: camera-frame log, not findings", 0
        elif reader is None:
            status, units = f"skipped: {path.suffix} not supported", 0
        else:
            try:
                units = reader(path, chunks, names)
                status = "indexed"
            except Exception as exc:  # keep going; the manifest records the failure
                status, units = f"failed: {exc}"[:200], 0
        manifest.append({"file": path.name, "psi_id": psi_of(path.name), "status": status,
                         "pages_or_sheets": units, "chunks": len(chunks) - before})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    with open(MANIFEST, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["file", "psi_id", "status", "pages_or_sheets", "chunks"])
        w.writeheader(); w.writerows(manifest)
    print(f"{len(chunks)} chunks from {sum(m['status'] == 'indexed' for m in manifest)} of {len(manifest)} files "
          f"-> {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1e6:.1f} MB)")
    for m in manifest:
        print(f"  {m['status'][:40]:40} {m['chunks']:5d}  {m['file'][:80]}")


if __name__ == "__main__":
    main()
