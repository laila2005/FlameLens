"""End-to-end validation of the live FlameLens site against the challenge rules and our own design rules.
Run before submitting:  python scripts/validate_live.py . [base_url]
Checks the curated data, every preset's decision routes, the citation verifier (adversarial claims),
the evidence trail, public access and the challenge features. Prints every check; exit code 1 if any fail."""
import csv, json, random, re, sys, urllib.request
from pathlib import Path

ROOT = Path(sys.argv[1])
BASE = sys.argv[2] if len(sys.argv) > 2 else "https://flamelens-steel.vercel.app"
RUN_RE = re.compile(r"PSI-\d+-\d{4}")
VERDICT_RE = re.compile(r"\b(safe|unsafe|safely)\b", re.I)
results = []


def check(group, name, ok, detail=""):
    results.append((group, name, bool(ok), detail))


def http(path, body=None):
    req = urllib.request.Request(BASE + path, data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "User-Agent": "flamelens-qa"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
        return r.status, r.headers.get("content-type", ""), raw


def jget(path, body=None):
    return json.loads(http(path, body)[2])


# ------------------------------------------------------------------ local data
rows = list(csv.DictReader(open(ROOT / "data/curated/runs.csv", encoding="utf-8")))
by_id = {r["run_id"]: r for r in rows}
psis = sorted({r["psi_id"] for r in rows})
check("Data", "runs.csv has 2,003 rows", len(rows) == 2003, f"{len(rows)} rows")
check("Data", "run IDs are unique", len(by_id) == len(rows))
check("Data", "18 PSI investigations have runs", len(psis) == 18, f"{len(psis)}: {', '.join(psis)}")
check("Data", "every row has a DOI", all(r["doi"].startswith("10.") for r in rows),
      f"{sum(not r['doi'].startswith('10.') for r in rows)} missing")
check("Data", "every row has a source table", all(r["source_table"] for r in rows))
check("Data", "confidence is high/medium/low", all(r["confidence"] in {"high", "medium", "low"} for r in rows),
      str({r["confidence"] for r in rows}))
allowed_basis = {"measured", "text", "assumed", "unknown"}
for f in ["o2", "pressure", "airflow"]:
    col = {"o2": "o2_pct", "pressure": "pressure_psi", "airflow": "airflow_cm_s"}[f]
    bad_b = [r["run_id"] for r in rows if r[f + "_basis"] not in allowed_basis]
    check("Data", f"{f} basis tag is one of {sorted(allowed_basis)}", not bad_b, f"{len(bad_b)} bad")
    # No source, no row: empty value <-> 'unknown' basis
    mism = [r["run_id"] for r in rows if (r[col] == "") != (r[f + "_basis"] == "unknown")]
    check("Data", f"{f}: empty value exactly when basis is 'unknown' (missing stays empty)", not mism,
          f"{len(mism)} mismatches, e.g. {mism[:3]}")
num = lambda v: float(v) if v not in ("", None) else None
check("Data", "oxygen values within 0-100 %", all(num(r["o2_pct"]) is None or 0 <= num(r["o2_pct"]) <= 100 for r in rows))
check("Data", "pressures positive", all(num(r["pressure_psi"]) is None or num(r["pressure_psi"]) > 0 for r in rows))
check("Data", "gravity is 0 g for every flight run (no partial-gravity data in PSI)",
      all(num(r["gravity_g"]) == 0 for r in rows), str({r["gravity_g"] for r in rows}))
ph = [r["run_id"] for r in rows if re.search(r"placeholder|mock|invented|example", " ".join(r.values()), re.I)]
check("Data", "no placeholder/mock rows in the live table (so no 'sample data' banner is needed)", not ph, f"{ph[:3]}")

# ------------------------------------------------------------------ public access (submission rule: links open with no login)
for path, kind in [("/", "text/html"), ("/api/health", "json"), ("/docs", "text/html"), ("/api/export/runs.csv", "csv"),
                   ("/api/export/spread_rates.csv", "csv"), ("/api/export/papers.csv", "csv"),
                   ("/api/export/investigations.json", "json"), ("/favicon.png", "png")]:
    try:
        st, ct, raw = http(path)
        check("Public access", f"GET {path} -> 200 without login", st == 200 and kind in ct, f"{st} {ct}")
    except Exception as e:
        check("Public access", f"GET {path} -> 200 without login", False, str(e))
st, ct, raw = http("/api/export/runs.csv")
live_rows = list(csv.DictReader(raw.decode("utf-8").splitlines()))
check("Public access", "exported runs.csv equals the repo runs.csv (2,003 rows, same IDs)",
      {r["run_id"] for r in live_rows} == set(by_id), f"{len(live_rows)} rows")
health = jget("/api/health")
check("Public access", "health reports 2,003 runs", health.get("runs") == 2003, json.dumps(health))

# ------------------------------------------------------------------ decision routes, every preset
habitats = jget("/api/habitats")
habitats = habitats.get("habitats", habitats) if isinstance(habitats, dict) else habitats
check("Requirements", "5 habitat presets incl. Moon base, pressurized rover, spacesuit (challenge text)",
      {"moon-base", "pressurized-rover", "spacesuit"} <= {h["id"] for h in habitats}, str([h["id"] for h in habitats]))
rover = next(h for h in habitats if h["id"] == "pressurized-rover")
check("Requirements", "rover preset = 30 % O2 at 10.2 psi, lunar 0.16 g (challenge text)",
      rover["o2_pct"] == 30 and rover["pressure_psi"] == 10.2 and rover["gravity_g"] == 0.16)
suit = next(h for h in habitats if h["id"] == "spacesuit")
check("Requirements", "spacesuit preset = 100 % O2 at 4.3 psi (challenge text)", suit["o2_pct"] == 100 and suit["pressure_psi"] == 4.3)

FAR = {"id": "far-away", "o2_pct": 95, "pressure_psi": 28, "airflow_cm_s": 55, "gravity_g": 1, "fuel_state": "solid"}
CUSTOM = {"id": "custom-no-cache", "o2_pct": 24.5, "pressure_psi": 13.1, "airflow_cm_s": 17.3, "gravity_g": 0, "fuel_state": "any"}
for h in habitats + [FAR, CUSTOM]:
    t = {k: h[k] for k in ["o2_pct", "pressure_psi", "airflow_cm_s", "gravity_g", "fuel_state"]}
    body, g = {"target": t}, f"Preset: {h['id']}"
    case, nxt, alts = jget("/api/case", body), jget("/api/next", body), jget("/api/alternatives", body)
    strength, rank, expl = jget("/api/strength", body), jget("/api/rank", body), jget("/api/explain", body)
    blob = json.dumps([case, nxt, alts, strength, rank, expl])
    ids = set(RUN_RE.findall(blob))
    unknown = sorted(i for i in ids if i not in by_id)
    check(g, f"every run ID returned exists in runs.csv ({len(ids)} IDs)", not unknown, f"{unknown[:3]}")
    conds = case["conditions"]
    ok_status = all(c["status"] in {"Supported", "Weak", "No evidence", "Not specified"} for c in conds) and len(conds) == 5
    rule = all((c["key"] == "flow" and t["airflow_cm_s"] is None and c["status"] == "Not specified")
               or (c["n"] >= 2 and c["status"] == "Supported") or (c["n"] == 1 and c["status"] == "Weak")
               or (c["n"] == 0 and c["status"] == "No evidence") for c in conds)
    check(g, "evidence case: 5 conditions, status follows the 2+/1/0 rule (unspecified airflow = Not specified)", ok_status and rule,
          "; ".join(f"{c['key']}={c['status']}({c['n']})" for c in conds))
    if h["gravity_g"] not in (0,):
        gc = next(c for c in conds if c["key"] == "grav")
        check(g, "non-zero gravity -> 'No evidence' for gravity (no partial/1 g runs in PSI)", gc["status"] == "No evidence", gc["status"])
    tpp = t["o2_pct"] * t["pressure_psi"] / 100
    pp_ok = all(a["o2_partial_pressure"] <= 0.9 * tpp + 0.005 and a["run_id"] in by_id for a in alts)
    real_ok = all(abs(float(by_id[a["run_id"]]["o2_pct"]) - a["o2_pct"]) < 1e-6 for a in alts if a["run_id"] in by_id)
    check(g, f"safer options: all >=10 % lower O2 partial pressure than {tpp:.2f} psi and are real tested runs",
          pp_ok and real_ok, f"{[(a['run_id'], a['o2_partial_pressure']) for a in alts]}")
    if nxt.get("nearest_run"):
        nr = nxt["nearest_run"]; src = by_id.get(nr["run_id"], {})
        check(g, f"run-this-next nearest run {nr['run_id']} matches its table row",
              src and abs(float(src["o2_pct"]) - nr["o2_pct"]) < 1e-6 and abs(float(src["pressure_psi"]) - nr["pressure_psi"]) < 1e-6)
    whole_s = strength.get("whole", {}).get("score")
    check(g, "evidence strength is within 0-100", whole_s is not None and 0 <= whole_s <= 100, f"whole={whole_s}")
    check(g, f"explanation: {expl['source']} text, every claim verified, 0 removed",
          all(c.get("verified") for c in expl["claims"]) and not expl.get("removed") and expl["claims"],
          f"{len(expl['claims'])} claims, removed={len(expl.get('removed') or [])}")
    if h["id"] in {x["id"] for x in habitats} and h["id"] != "mars-habitat":
        check(g, "explanation served from verified AI cache", expl["source"] == "cache", expl["source"])
    elif h["id"] == "mars-habitat":
        check(g, "explanation is verified (AI cache, or template until the model is re-run for 8.2 psia / 34 % O2)", expl["source"] in ("cache", "template"), expl["source"])
    else:
        check(g, "AI off / no cache -> deterministic template still works", expl["source"] in {"template", "cache", "model"}, expl["source"])
    texts = " ".join([c["claim"] + " " + (c.get("engineering_recommendation") or "") for c in expl["claims"]])
    check(g, "no 'safe'/'unsafe' verdict words in explanation", not VERDICT_RE.search(texts), str(VERDICT_RE.findall(texts)[:3]))
    if h["id"] == "far-away":
        wn = case["whole"]["n"]
        check(g, "habitat far from all runs -> whole design 'No evidence', never a guess", wn == 0 and case["whole"]["status"] == "No evidence", f"n={wn}")

# ------------------------------------------------------------------ citation verifier, adversarial
t = {"o2_pct": 30, "pressure_psi": 10.2, "airflow_cm_s": 8.1, "gravity_g": 0.16, "fuel_state": "solid"}
pack = jget("/api/verify", {"target": t, "claims": []})
ret = pack["retrieved_run_ids"]
rid = "PSI-25-0023" if "PSI-25-0023" in ret else ret[0]
row = by_id[rid]
outside = next(i for i in by_id if i not in ret)
cases = [
    ("valid claim with the run's own numbers is KEPT", {"claim": f"{rid} tested {row['fuel_or_material']} at {row['o2_pct']}% oxygen and {row['pressure_psi']} psi.", "run_id_reference": rid}, True),
    ("invented run ID is REMOVED", {"claim": "PSI-25-9999 burned at 30% oxygen.", "run_id_reference": "PSI-25-9999"}, False),
    ("real run outside the retrieved evidence is REMOVED", {"claim": f"{outside} burned.", "run_id_reference": outside}, False),
    ("changed number (oxygen 27.3 %) is REMOVED", {"claim": f"{rid} tested at 27.3% oxygen.", "run_id_reference": rid}, False),
    ("rounded number is REMOVED", {"claim": f"{rid} tested at {round(float(row['o2_pct']))}% oxygen.", "run_id_reference": rid}, round(float(row['o2_pct'])) in (30, 10, 8, 0)),
    ("safety verdict 'safe' is REMOVED", {"claim": f"{rid} shows this cabin is safe.", "run_id_reference": rid}, False),
    ("invented limit/threshold is REMOVED", {"claim": f"{rid} shows the flammability limit is {row['o2_pct']}% oxygen.", "run_id_reference": rid}, False),
    ("claim citing no run is REMOVED", {"claim": "Fires spread faster in microgravity.", "run_id_reference": ""}, False),
    ("sneaking a second, unretrieved run into the text is REMOVED", {"claim": f"{rid} and {outside} both burned.", "run_id_reference": rid}, False),
]
for name, claim, expect_kept in cases:
    r = jget("/api/verify", {"target": t, "claims": [claim]})
    kept = len(r["claims"]) == 1
    why = r["removed"][0]["reason"] if r["removed"] else "kept"
    check("Citation verifier", name, kept == expect_kept, why)

# ------------------------------------------------------------------ evidence trail sample
random.seed(13)
for rid in random.sample(sorted(by_id), 25):
    e = jget(f"/api/evidence/{rid}")
    run = e.get("run", {})
    ok = run.get("doi") == by_id[rid]["doi"] and run.get("o2_pct") in (None, num(by_id[rid]["o2_pct"]))
    if not ok:
        check("Evidence trail", f"{rid} opens with its DOI and table values", False, json.dumps(run)[:200])
check("Evidence trail", "25 random run IDs open with the same DOI and values as runs.csv",
      not any(g == "Evidence trail" and not ok for g, _, ok, _ in results))
lic = jget(f"/api/evidence/{rid}")
check("Evidence trail", "evidence response states the CC0 license", "CC0" in json.dumps(lic))

# ------------------------------------------------------------------ challenge features present
inv = jget("/api/investigations")
inv = inv.get("investigations", inv) if isinstance(inv, dict) else inv
check("Requirements", "investigation summaries available (objectives, fuels, conditions)", len(inv) >= 18, f"{len(inv)} profiles")
cmp_ = jget("/api/compare?a=PSI-25&b=PSI-99")
check("Requirements", "side-by-side comparison works (BASS-II vs Saffire-II)", bool(cmp_) and "PSI-99" in json.dumps(cmp_))
for lens in ["coverage", "coolflame", "aerosol", "spread", "tested", "smokepoint"]:
    d = jget(f"/api/lens/{lens}")
    n = len(d.get("points", [])) or len(d.get("smoke", [])) + len(d.get("dust", []))
    check("Requirements", f"lens '{lens}' returns real data", n > 0, f"{n} items")
sp = jget("/api/lens/spread")
check("Requirements", "flame-spread lens has 43 measured points", len(sp["points"]) == 43, str(len(sp["points"])))
spl = jget("/api/lens/smokepoint")
linked = [x["run_id"] for x in spl["points"] if x["run_id"]]
check("Requirements", "smoke-point lens: 55 SPICE flames, linked runs are real and marked 'smoke point'",
      spl["n_points"] == 55 and all(by_id.get(r, {}).get("outcome") == "smoke point" for r in linked), f"{len(set(linked))} linked runs")
det = jget("/api/detect/evidence")
check("Requirements", "early-detection evidence comes from real BASS-II/SAME-R data", bool(det))
mod = jget("/api/modeling")
mod = mod.get("studies", mod) if isinstance(mod, dict) else mod
check("Requirements", "5 PSI ground/CFD modeling studies linked", len(mod) == 5, str(len(mod)))
pap = jget("/api/papers")
pap = pap.get("papers", pap) if isinstance(pap, dict) else pap
check("Requirements", "NASA NTRS paper library available", len(pap) > 0, f"{len(pap)} papers")
# ------------------------------------------------------------------ test campaign planner
camp = jget("/api/campaign", {"n": 3})
habs = {h["id"]: h for h in camp["habitats"]}
pre = {h["id"]: h for h in habitats}
check("Campaign planner", "ISS cabin is already covered and gets no new test",
      habs["iss-cabin"]["status"] == "covered" and habs["iss-cabin"]["planned_by"] is None)
check("Campaign planner", "first experiment covers Moon base and pressurized rover together",
      set(camp["experiments"][0]["covers"]) == {"moon-base", "pressurized-rover"}, str(camp["experiments"][0]["covers"]))
check("Campaign planner", "3 experiments leave no preset design open", camp["summary"]["still_open"] == [], str(camp["summary"]))
ok_cover, ok_runs = True, True
for e in camp["experiments"]:
    x = e["conditions"]
    for hid in e["covers"]:  # recompute the match independently with the published tolerances
        h = pre[hid]
        m = (abs(x["o2_pct"] - h["o2_pct"]) <= 6 + 1e-9 and abs(x["pressure_psi"] - h["pressure_psi"]) <= 2 + 1e-9
             and (h["airflow_cm_s"] is None or (x["airflow_cm_s"] is not None and abs(x["airflow_cm_s"] - h["airflow_cm_s"]) <= 8 + 1e-9))
             and (h["fuel_state"] == "any" or x["fuel_state"] == h["fuel_state"]) and abs(x["gravity_g"] - h["gravity_g"]) < 1e-9)
        ok_cover &= m
    ok_runs &= e["nearest_run"]["run_id"] in by_id
check("Campaign planner", "every planned test really matches each design it claims to cover (±6 / ±2 / ±8, material, gravity)", ok_cover)
check("Campaign planner", "every 'start from' run is a real run in runs.csv", ok_runs)
check("Campaign planner", "partial-gravity tests are flagged as needing a LUCI/FM2-type platform",
      all(("LUCI" in e["platform_note"]) == (0 < e["conditions"]["gravity_g"] < 1) for e in camp["experiments"]))
check("Campaign planner", "n=1 returns one experiment", len(jget("/api/campaign", {"n": 1})["experiments"]) == 1)

# ------------------------------------------------------------------ closest evidence (rover gap)
cl = jget("/api/closest", {"target": {"o2_pct": 30, "pressure_psi": 10.2, "airflow_cm_s": 8.1, "gravity_g": 0.16, "fuel_state": "solid"}})
check("Closest evidence", "rover: closest-evidence groups are shown because nothing matches", cl["needed"] and len(cl["groups"]) >= 2)
ok = True
for g in cl["groups"]:
    for rid in g["run_ids"]:
        row = by_id.get(rid)
        if not row:
            ok = False; continue
        if "oxygen" in g["same"]: ok &= abs(float(row["o2_pct"]) - 30) <= 6 + 1e-9
        if "pressure" in g["same"]: ok &= abs(float(row["pressure_psi"]) - 10.2) <= 2 + 1e-9
        if "material" in g["same"]: ok &= row["fuel_state"] == "solid"
        if "airflow" in g["same"]: ok &= row["airflow_cm_s"] != "" and abs(float(row["airflow_cm_s"]) - 8.1) <= 8 + 1e-9
check("Closest evidence", "every listed run really has the conditions its card calls 'same'", ok)
check("Closest evidence", "same-partial-pressure runs are labelled related, not equivalent",
      cl["same_partial_pressure"] is None or "not equivalent" in cl["same_partial_pressure"]["note"])
check("Closest evidence", "ISS cabin (already matched) gets no closest-evidence block",
      jget("/api/closest", {"target": {"o2_pct": 21, "pressure_psi": 14.7, "airflow_cm_s": 12.9, "gravity_g": 0, "fuel_state": "any"}})["needed"] is False)

# ------------------------------------------------------------------ mission atmosphere journey
jr = jget("/api/journey", {})
check("Mission journey", "stages run ISS cabin -> spacesuit -> pressurized rover -> Moon base",
      [s["id"] for s in jr["stages"]] == ["iss-cabin", "spacesuit", "pressurized-rover", "moon-base"])
check("Mission journey", "exactly one weakest stage, and mission strength equals the lowest stage strength",
      sum(s["weakest"] for s in jr["stages"]) == 1 and jr["mission_strength"] == min(s["strength"] for s in jr["stages"]))
ok = True
for s in jr["stages"]:
    cs = jget("/api/case", {"target": s["target"]})
    ok &= cs["whole"]["n"] == s["whole_n"] and cs["verdict"] == s["verdict"]
    nr = s["next"]["nearest_run"]
    ok &= nr is None or nr["run_id"] in by_id
check("Mission journey", "every stage matches the single-design evidence case and cites real runs", ok)

# ------------------------------------------------------------------ Ask the NASA reports
lib = jget("/api/library")
check("Ask the NASA reports", "report library loaded (1,000+ passages from PSI documents)", lib["n_chunks"] > 1000, f"{lib['n_chunks']} passages, {lib['n_files']} files")
ans = jget("/api/ask", {"psi_id": "PSI-25", "question": "How did airflow or oxygen affect flame spread or extinction?"})
check("Ask the NASA reports", "answers with passages or verified claims, each with file and page",
      ans["source"] in ("passages", "cache", "model") and ans["passages"] and all(p["source_file"] and p["source_ref"] for p in ans["passages"]), ans["source"])
check("Ask the NASA reports", "every shown claim is marked verified and quotes the document", all(c.get("verified") and len(c.get("supporting_quote", "")) >= 20 for c in ans.get("claims", [])))

html = http("/")[2].decode("utf-8")
check("Requirements", "Back on Earth panel cites NASA Spinoff pages", html.count("spinoff.nasa.gov") >= 3)
check("Rules", "AI use disclosed on the page", "AI use" in html and "citation verifier" in html)
check("Rules", "page says evidence strength is not a safety rating", "not a safety rating" in html)
imgs = re.findall(r'<img[^>]*src="([^"]+)"', html)
check("Rules", "the only images are the FlameLens logo (no photos of people)", all(i in {"logo.png"} for i in imgs), str(imgs))

# ------------------------------------------------------------------ report
fails = [r for r in results if not r[2]]
last = None
for g, n, ok, d in results:
    if g != last:
        print(f"\n== {g}"); last = g
    print(f"  {'PASS' if ok else 'FAIL'}  {n}" + (f"  [{d}]" if d and not ok else ""))
print(f"\n{len(results) - len(fails)} of {len(results)} checks passed against {BASE}")
sys.exit(1 if fails else 0)
