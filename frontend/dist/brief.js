/* FlameLens design review brief: a one-to-two page, printable evidence summary of the current habitat design.
   Fetches fresh results from the same deterministic API routes as the dashboard (never stale, never extra numbers),
   shows them as a paper preview, and prints or saves as PDF with the browser's print dialog. */
(function () {
  const FL = window.FL;
  const esc = FL.esc;
  const $ = (id) => document.getElementById(id);
  const EARTH_PP = (21 * 14.7) / 100;
  const COND_LABEL = { o2: "Oxygen", psi: "Pressure", flow: "Airflow", fuel: "Material", grav: "Gravity" };
  const GAP = { o2: "oxygen", psi: "pressure", flow: "airflow", fuel: "material", grav: "gravity", whole: "the full combination" };
  const FIELD_LABEL = { o2_pct: "Oxygen %", pressure_psi: "Pressure psi", airflow_cm_s: "Airflow cm/s", gravity_g: "Gravity g", fuel_state: "Material" };
  const GRAV = { 0: "Microgravity (0 g)", 0.16: "Moon (0.16 g)", 0.38: "Mars (0.38 g)", 1: "Earth (1 g)" };
  const FUEL = { any: "Any material", solid: "Solid (fabric, plastic)", liquid: "Liquid (fuel droplets)", gas: "Gas" };
  let profiles = null;
  let lastFocus = null;

  const num = (v) => (v == null || v === "" ? "–" : String(+(+v).toFixed(2)));
  const val = (v) => (typeof v === "number" ? num(v) : v == null || v === "" ? "–" : String(v)); // numbers or words (material)
  const psiOf = (runId) => String(runId).replace(/-\d{4}$/, "");
  const tone = (s) => (s >= 65 ? "ok" : s >= 25 ? "amber" : "bad");
  const stTone = (s) => (s === "Supported" ? "ok" : s === "Weak" ? "amber" : "bad");
  const doiLink = (doi) => (doi ? `<a href="https://doi.org/${esc(doi)}" target="_blank" rel="noopener">doi.org/${esc(doi)}</a>` : "–");
  const pill = (text, t) => `<span class="bp bp-${t}">${esc(text)}</span>`;
  const run = (id) => `<span class="brun">${esc(id)}</span>`;

  async function data() {
    const t = FL.target();
    const body = { target: t };
    const [c, st, nx, alt, rk, ex] = await Promise.all([
      FL.api.post("/api/case", body), FL.api.post("/api/strength", body), FL.api.post("/api/next", body),
      FL.api.post("/api/alternatives", { target: t, k: 3 }), FL.api.post("/api/rank", { target: t, k: 5 }),
      FL.api.post("/api/explain", body),
    ]);
    if (!profiles) {
      const p = await FL.api.get("/api/investigations");
      profiles = Object.fromEntries((Array.isArray(p) ? p : p.investigations || []).map((x) => [x.psi_id, x]));
    }
    return { t, c, st, nx, alt, rk, ex };
  }

  function render({ t, c, st, nx, alt, rk, ex }) {
    const pressed = document.querySelector(".pre[aria-pressed='true']");
    const name = pressed ? pressed.textContent.trim() : "Custom design";
    const noteEl = $("presetnote").cloneNode(true);
    noteEl.querySelectorAll(".badge").forEach((b) => b.remove());
    const note = pressed ? noteEl.textContent.trim() : "Values entered by the user.";
    const pp = (t.o2_pct * t.pressure_psi) / 100;
    const dpp = (pp / EARTH_PP - 1) * 100;
    const ppText = Math.abs(dpp) < 2 ? "about the same as sea-level air (3.09 psi)" : `${Math.abs(Math.round(dpp))} % ${dpp > 0 ? "more" : "less"} than sea-level air (3.09 psi)`;
    const ref = `FL-${num(t.o2_pct)}-${num(t.pressure_psi)}-${t.airflow_cm_s == null ? "na" : num(t.airflow_cm_s)}-${num(t.gravity_g)}-${t.fuel_state}`;
    const now = new Date();
    const when = now.toLocaleString(undefined, { year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
    const w = st.whole || {}, at = st.atmosphere || {}, ds = st.dataset || {};
    const wS = Math.round(w.score ?? 0), aS = Math.round(at.score ?? 0);
    const part = w.n_runs > 0 ? w : at.n_runs > 0 ? at : w;
    const factors = [["Proximity", 35, part.proximity], ["Reliability", 30, part.reliability], ["Run count", 20, part.run_count], ["Source quality", 15, part.source_quality]];
    const verdictTone = c.whole.n >= 2 ? "ok" : c.whole.n === 0 && (c.atmosphere?.n || 0) === 0 ? "bad" : "amber";

    // every PSI investigation this brief cites, for the reference list
    const cited = new Set();
    c.conditions.forEach((x) => (x.run_ids || []).slice(0, 3).forEach((id) => cited.add(psiOf(id))));
    (c.whole.run_ids || []).slice(0, 5).forEach((id) => cited.add(psiOf(id)));
    if (nx.nearest_run) cited.add(psiOf(nx.nearest_run.run_id));
    alt.forEach((a) => cited.add(psiOf(a.run_id)));
    ex.claims.forEach((x) => cited.add(psiOf(x.run_id_reference)));
    rk.forEach((r) => cited.add(r.psi_id));
    const refs = [...cited].filter((p) => profiles[p]).sort((a, b) => +a.split("-")[1] - +b.split("-")[1]);

    const sub = c.whole.n >= 2 ? `${c.whole.n.toLocaleString()} NASA runs match all five conditions.`
      : c.whole.n === 1 ? "Only one NASA run matches all five conditions."
      : "No NASA run in PSI matches all five conditions. This combination is a gap in the evidence.";

    const nextHtml = !nx.needed
      ? `<p>The design is already covered by several runs. The most useful next test repeats the least certain one to raise confidence${nx.nearest_run ? ` (start from ${run(nx.nearest_run.run_id)})` : ""}.</p>`
      : `<p>Testing this exact design closes <b>${(nx.gaps || []).length}</b> evidence gap${(nx.gaps || []).length === 1 ? "" : "s"}: <b>${esc((nx.gaps || []).map((g) => GAP[g] || g).join(", "))}</b>.</p>
         <table class="bt"><tr><th>Oxygen</th><th>Pressure</th><th>Airflow</th><th>Gravity</th><th>Material</th></tr>
         <tr><td>${num(nx.recommended.o2_pct)} %</td><td>${num(nx.recommended.pressure_psi)} psi</td><td>${nx.recommended.airflow_cm_s == null ? "not specified" : num(nx.recommended.airflow_cm_s) + " cm/s"}</td><td>${num(nx.recommended.gravity_g)} g</td><td>${esc(nx.recommended.fuel_state)}</td></tr></table>
         ${nx.nearest_run ? `<p>Cheapest first step: start from ${run(nx.nearest_run.run_id)} (${esc(nx.nearest_run.investigation)}) and change ${nx.changes.map((ch) => `${esc(FIELD_LABEL[ch.field] || ch.field)} ${esc(val(ch.from))} → ${esc(val(ch.to))}`).join("; ")}.</p>` : ""}`;

    const altHtml = alt.length
      ? `<table class="bt"><tr><th>Run</th><th>Investigation</th><th>O₂</th><th>Pressure</th><th>O₂ partial pressure</th><th>Below yours</th><th>Confidence</th></tr>
         ${alt.map((a) => `<tr><td>${run(a.run_id)}</td><td>${esc(a.investigation)}</td><td>${num(a.o2_pct)} %</td><td>${num(a.pressure_psi)} psi</td><td>${num(a.o2_partial_pressure)} psi</td><td>${num(a.reduction_pct)} %</td><td>${esc(a.confidence)}</td></tr>`).join("")}</table>
         <p class="bnote">Real tested runs only, never extrapolated. Less oxygen means less to feed a fire; it is not a verdict that the option is safe.</p>`
      : `<p>No tested run has at least 10 % lower oxygen partial pressure than ${num(pp)} psi with this material.</p>`;

    const aiLabel = ex.source === "template"
      ? "Fixed template (AI off), checked by the citation verifier."
      : `Written by an open AI model${ex.model ? ` (${esc(ex.model)})` : ""}, then checked by the citation verifier: every sentence cites a run, and every number must appear in that run.`;

    $("brief").innerHTML = `
      <header class="bhead">
        <div class="bbrand"><img class="bmark" src="logo.png" alt="" width="44" height="44"><div><div class="bkicker">FlameLens · Design review evidence brief</div>
          <h2 id="brieftitle">${esc(name)}</h2></div></div>
        <dl class="bmeta"><dt>Reference</dt><dd>${esc(ref)}</dd><dt>Generated</dt><dd>${esc(when)}</dd>
          <dt>Data</dt><dd>${(ds.total_runs || 2003).toLocaleString()} NASA PSI flight runs · ${ds.total_investigations || 18} investigations · CC0</dd></dl>
      </header>
      <p class="bdisc"><b>Evidence summary, not a safety rating or certification.</b> It shows what NASA PSI microgravity flight experiments have and have not tested for this design. Every number below comes from a cited run.</p>

      <section class="bsec"><h3>1 · Design under review</h3>
        <div class="bgrid">
          <div><span>Oxygen</span><b>${num(t.o2_pct)} %</b></div>
          <div><span>Pressure</span><b>${num(t.pressure_psi)} psi</b></div>
          <div><span>O₂ partial pressure</span><b>${pp.toFixed(2)} psi</b><small>${esc(ppText)}</small></div>
          <div><span>Airflow</span><b>${t.airflow_cm_s == null ? "not specified" : num(t.airflow_cm_s) + " cm/s"}</b></div>
          <div><span>Gravity</span><b>${esc(GRAV[t.gravity_g] || num(t.gravity_g) + " g")}</b></div>
          <div><span>Material</span><b>${esc(FUEL[t.fuel_state] || t.fuel_state)}</b></div>
        </div>
        <p class="bnote">${esc(note)}</p>
      </section>

      <section class="bsec bverdict bv-${verdictTone}"><h3>2 · Verdict on the evidence</h3>
        <p class="bbig">${esc(c.verdict)}</p><p>${esc(sub)}</p></section>

      <section class="bsec"><h3>3 · Evidence strength (0–100, transparency aid)</h3>
        <div class="bscores">
          <div><span>Whole habitat</span><b class="t-${tone(wS)}">${wS}<small>/100</small></b><i class="bbar"><i class="f-${tone(wS)}" style="width:${wS}%"></i></i>
            <small>Backed by ${(w.n_runs || 0).toLocaleString()} of ${(ds.total_runs || 2003).toLocaleString()} runs${w.n_runs ? `, ${w.n_measured} directly measured, ${w.n_investigations} investigation${w.n_investigations === 1 ? "" : "s"}` : ""}</small></div>
          <div><span>Atmosphere only, in 0 g</span><b class="t-${tone(aS)}">${aS}<small>/100</small></b><i class="bbar"><i class="f-${tone(aS)}" style="width:${aS}%"></i></i>
            <small>${(at.n_runs || 0).toLocaleString()} runs match oxygen, pressure, airflow and material in microgravity</small></div>
        </div>
        <p class="bnote">Score = 35 % proximity + 30 % reliability + 20 % run count + 15 % source quality: ${factors.map(([l, , v]) => `${l} ${Math.round(100 * (v ?? 0))} %`).join(" · ")}.</p>
      </section>

      <section class="bsec"><h3>4 · Evidence case, condition by condition</h3>
        <table class="bt"><tr><th>Condition</th><th>Status</th><th>Matching runs</th><th>Strength</th><th>Example runs</th></tr>
        ${c.conditions.map((x) => { const s = (st.conditions || {})[x.key] || {}; return `<tr><td>${esc(x.label || COND_LABEL[x.key])}</td><td>${pill(x.status, stTone(x.status))}</td>
          <td>${x.n.toLocaleString()}${s.n_investigations ? ` · ${s.n_investigations} PSIs` : ""}</td><td>${Math.round(s.score ?? 0)}/100</td>
          <td>${(x.run_ids || []).slice(0, 3).map(run).join(" ") || "none"}${x.note ? `<div class="bnote">${esc(x.note)}</div>` : ""}</td></tr>`; }).join("")}
        <tr class="btot"><td>Whole design</td><td>${pill(c.whole.status, stTone(c.whole.status))}</td><td>${c.whole.n.toLocaleString()}</td><td>${wS}/100</td><td>${(c.whole.run_ids || []).slice(0, 3).map(run).join(" ") || "none"}</td></tr>
        </table>
        <p class="bnote">A run matches a condition when it is within ±6 oxygen points, ±2 psi or ±8 cm/s airflow, with the same material and gravity. Supported = 2 or more runs, Weak = 1, No evidence = 0. "No evidence" marks a gap, not a hazard.</p>
      </section>

      <section class="bsec"><h3>5 · Gap to close: run this next</h3>${nextHtml}</section>

      <section class="bsec"><h3>6 · Lower-oxygen options NASA has tested</h3>${altHtml}</section>

      <section class="bsec"><h3>7 · What the evidence says</h3>
        <p class="bnote">${aiLabel} ${ex.removed_count ? `${ex.removed_count} sentence${ex.removed_count === 1 ? " was" : "s were"} removed.` : "0 sentences were removed."}</p>
        <ol class="bclaims">${ex.claims.map((x) => `<li>${esc(x.claim)}<div class="bcite">${run(x.run_id_reference)} · ${esc(x.investigation)} · confidence ${esc(x.confidence_level)} · ✓ verified · ${doiLink(x.doi)}</div>
          ${x.engineering_recommendation ? `<div class="brec">Consider: ${esc(x.engineering_recommendation)}</div>` : ""}</li>`).join("") || "<li>Not enough data to explain this design; see the evidence case.</li>"}</ol>
      </section>

      <section class="bsec"><h3>8 · Closest NASA investigations</h3>
        <table class="bt"><tr><th>Score</th><th>Investigation</th><th>Pillar</th><th>Runs</th><th>Factors used</th><th>Confidence</th><th>DOI</th></tr>
        ${rk.map((r) => `<tr><td><b>${Math.round(r.score)}</b></td><td>${esc(r.investigation)} <span class="bmuted">${esc(r.psi_id)}</span></td><td>${esc(r.pillar)}</td><td>${r.n_runs}</td><td>${r.factors_used} of 5</td><td>${esc(r.confidence)}</td><td>${doiLink(r.doi)}</td></tr>`).join("")}
        </table>
      </section>

      <section class="bsec"><h3>9 · Sources cited in this brief</h3>
        <ul class="brefs">${refs.map((p) => { const x = profiles[p]; return `<li><b>${esc(x.acronym || p)}</b> (${esc(p)}): ${esc(x.title || "")}. NASA Physical Sciences Informatics, ${esc(x.license || "CC0-1.0")}. ${doiLink(x.doi)}</li>`; }).join("")}</ul>
      </section>

      <footer class="bfoot">
        <p><b>Method.</b> Verdict, evidence case, strength, next test, lower-oxygen options and ranking are plain arithmetic on the NASA PSI run table, with no AI. Values marked <i>assumed</i> in the source (for example ISS cabin air where a table gave no pressure) carry lower confidence. PSI holds no partial-gravity combustion data yet (LUCI and FM2 are planned), so microgravity runs give one bound only.</p>
        <p>Made with FlameLens · Team AstroSpark, NASA Space Apps Cairo 2026 · https://flamelens-steel.vercel.app · Check any run ID in the dashboard's evidence drawer.</p>
      </footer>`;
  }

  async function openBrief() {
    const wrap = $("briefwrap");
    lastFocus = document.activeElement;
    wrap.hidden = false;
    document.body.classList.add("brief-open");
    $("brief").innerHTML = `<p class="bloading">Building the brief from the NASA PSI run table…</p>`;
    $("briefprint").disabled = true;
    try {
      render(await data());
      $("briefprint").disabled = false;
    } catch (e) {
      $("brief").innerHTML = `<p class="err">Could not build the brief: ${esc(e.message)}. Is the FlameLens API reachable?</p>`;
    }
    $("briefclose").focus();
  }

  function closeBrief() {
    $("briefwrap").hidden = true;
    document.body.classList.remove("brief-open");
    if (lastFocus) lastFocus.focus();
  }

  $("briefbtn").addEventListener("click", openBrief);
  $("briefclose").addEventListener("click", closeBrief);
  $("briefprint").addEventListener("click", () => window.print());
  $("briefwrap").addEventListener("click", (e) => { if (e.target.id === "briefwrap") closeBrief(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !$("briefwrap").hidden) closeBrief(); });
  FL.brief = { open: openBrief, close: closeBrief };

  // deep link: ?brief=1 opens the brief once the starting preset has loaded (handy for demos and PDF export)
  if (/[?&]brief=1(&|$)/.test(location.search)) {
    let tries = 0;
    const wait = setInterval(() => {
      if (document.querySelector(".pre[aria-pressed='true']") || ++tries > 40) { clearInterval(wait); setTimeout(openBrief, 300); }
    }, 150);
  }
})();
