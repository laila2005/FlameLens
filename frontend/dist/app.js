/* FlameLens dashboard. Talks to the FastAPI backend on the same origin (/api/...). */
(function () {
  const FL = window.FL;
  const esc = FL.esc;
  const $ = (id) => document.getElementById(id);
  const API = "";

  const PILLAR_COLOR = { Prevention: "var(--c-green)", Detection: "var(--c-gold)", Suppression: "var(--c-cyan)", Other: "var(--c-violet)" };
  const OUTCOME_COLOR = { cool_flame: "var(--c-cyan)", hot_flame: "var(--c-flame)", no_ignition: "var(--c-grey)", other: "var(--c-violet)" };
  const OUTCOME_LABEL = { cool_flame: "Cool flame", hot_flame: "Hot flame", no_ignition: "Did not ignite", other: "Other end (extinction, disruption, completion)" };
  const FACTOR_COLOR = { o2: "var(--c-flame)", psi: "var(--c-cyan)", flow: "var(--c-violet)", fuel: "var(--c-green)", grav: "var(--c-gold)" };
  const WEIGHTS = { o2: 0.35, psi: 0.2, flow: 0.2, fuel: 0.15, grav: 0.1 };
  const FIELD_LABEL = { o2_pct: "Oxygen %", pressure_psi: "Pressure psi", airflow_cm_s: "Airflow cm/s", gravity_g: "Gravity g", fuel_state: "Fuel" };
  const EARTH_PP = 21 * 14.7 / 100; // oxygen partial pressure of sea-level air, psi

  let lens = "coverage";
  const lensCache = {};
  let lastTarget = null;
  let timer = null;

  // ---------------------------------------------------------------- api

  async function get(path) {
    const r = await fetch(API + path);
    if (!r.ok) throw new Error(`${path}: ${r.status}`);
    return r.json();
  }
  async function post(path, body) {
    const r = await fetch(API + path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    if (!r.ok) throw new Error(`${path}: ${r.status}`);
    return r.json();
  }

  // ---------------------------------------------------------------- controls

  function target() {
    const off = $("flowoff").checked;
    return {
      o2_pct: +$("o2").value,
      pressure_psi: +$("psi").value,
      airflow_cm_s: off ? null : +$("flow").value,
      gravity_g: +$("grav").value,
      fuel_state: $("fuel").value,
    };
  }

  function renderControls(t) {
    $("o2o").textContent = `${t.o2_pct} %`;
    $("psio").textContent = `${t.pressure_psi.toFixed(1)} psi`;
    $("flowo").textContent = t.airflow_cm_s == null ? "not specified" : `${t.airflow_cm_s} cm/s`;
    $("flow").disabled = t.airflow_cm_s == null;
    for (const id of ["o2", "psi", "flow"]) { // filled part of each slider track
      const el = $(id);
      el.style.setProperty("--p", `${((el.value - el.min) / (el.max - el.min)) * 100}%`);
    }
    const pp = (t.o2_pct * t.pressure_psi) / 100;
    $("ppv").textContent = `${pp.toFixed(2)} psi`;
    const d = (pp / EARTH_PP - 1) * 100;
    $("ppc").textContent = Math.abs(d) < 2 ? "About the same as sea-level air (3.09 psi)" :
      `${Math.abs(Math.round(d))} % ${d > 0 ? "more" : "less"} oxygen than sea-level air (3.09 psi)`;
  }

  function setPreset(p, btn) {
    $("o2").value = p.o2_pct;
    $("psi").value = p.pressure_psi;
    $("flowoff").checked = p.airflow_cm_s == null;
    if (p.airflow_cm_s != null) $("flow").value = p.airflow_cm_s;
    $("grav").value = String(p.gravity_g);
    $("fuel").value = p.fuel_state;
    document.querySelectorAll(".pre").forEach((b) => b.setAttribute("aria-pressed", String(b === btn)));
    $("presetnote").innerHTML = `<span class="badge ${p.sourced ? "src" : "ex"}">${esc(p.source_label || (p.sourced ? "from the challenge text" : "example values"))}</span> ${esc(p.note || "")}${p.source && p.source.startsWith("http") ? ` <a href="${esc(p.source)}" target="_blank" rel="noopener">Source</a>` : ""}`;
    schedule(0);
  }

  // ---------------------------------------------------------------- render: decision

  const statusCls = (s) => (s === "No evidence" ? "s-No" : s === "Not specified" ? "s-Na" : s === "Other fuels only" ? "s-Other" : `s-${s}`);
  const runBtn = (id) => `<button class="runlink" data-run="${esc(id)}">${esc(id)}</button>`;

  function renderVerdict(c) {
    const el = $("verdict");
    const whole = c.whole.n, atmo = c.atmosphere ? c.atmosphere.n : 0;
    el.className = "verdict panel " + (whole >= 2 ? "good" : whole === 0 && atmo === 0 ? "bad" : "");
    let sub = "";
    if (whole === 0 && atmo === 0) sub = "No NASA experiment in PSI tested this combination. This is where new testing is needed.";
    else if (whole === 0) sub = "The atmosphere was tested, but not under these exact conditions (often gravity: every PSI run is microgravity).";
    if (c.conditions.some((x) => x.bounded)) sub += " PSI has no partial-gravity data yet (LUCI and FM2 are planned); microgravity results are one bound.";
    if (!sub) sub = "Every number below links to the NASA run it came from.";
    el.innerHTML = `<div class="big">${esc(c.verdict)}</div><div class="sub">${esc(sub)}</div>`;
  }

  function meterColor(score) {
    return score >= 65 ? "var(--ok)" : score >= 25 ? "var(--amber)" : "var(--bad)";
  }

  function renderConditions(c, st) {
    const w = st.whole || { score: 0, n_runs: 0, n_measured: 0, n_investigations: 0, proximity: 0, reliability: 0, run_count: 0, source_quality: 0, investigations: [] };
    const at = st.atmosphere || { score: 0, n_runs: 0, n_measured: 0, n_investigations: 0, investigations: [] };
    const ds = st.dataset || { total_runs: 2003, total_investigations: 18, near_any_condition_runs: 0, backing_investigations: [], not_yet_in_psi: ["SoFIE", "FLARE", "LUCI", "FM2"] };
    const wScore = Math.round(w.score ?? 0);
    const atScore = Math.round(at.score ?? 0);
    const activePart = w.n_runs > 0 ? w : (at.n_runs > 0 ? at : null);
    const activeLabel = w.n_runs > 0 ? "Whole-habitat factors" : (at.n_runs > 0 ? "0g atmosphere-bound factors" : "Whole-habitat factors");
    const subFactors = [
      ["Proximity (35%)", Math.round(100 * (activePart?.proximity ?? 0))],
      ["Reliability (30%)", Math.round(100 * (activePart?.reliability ?? 0))],
      ["Test count (20%)", Math.round(100 * (activePart?.run_count ?? 0))],
      ["Source quality (15%)", Math.round(100 * (activePart?.source_quality ?? 0))],
    ];
    const invSource = (w.investigations && w.investigations.length) ? w.investigations
      : ((at.investigations && at.investigations.length) ? at.investigations : (ds.backing_investigations || []));
    const invChips = invSource.slice(0, 7).map((iv) =>
      `<button type="button" class="modchip" data-jump-inv="${esc(iv.psi_id)}" title="Jump to ${esc(iv.name)} (${esc(iv.psi_id)}) profile">${esc(iv.name)} (${iv.runs})</button>`
    ).join(" ");

    // With no run matching all conditions, every score and factor is 0: say why, and give the per-condition view.
    let whyZero = "";
    if (!activePart) {
      const counted = c.conditions.filter((x) => x.status !== "Not specified");
      const sep = counted.length ? Math.round(counted.reduce((a, x) => a + ((st.conditions[x.key] || {}).score || 0), 0) / counted.length) : 0;
      const sup = counted.filter((x) => x.status === "Supported").length;
      whyZero = `<div class="sm-why"><b>Why 0:</b> no NASA run matches all these conditions together, so there is nothing to score as a whole
        and the four parts below are empty. Tested one condition at a time, this design scores
        <b style="color:${meterColor(sep)}">${sep}/100</b> (${sup} of ${counted.length} conditions supported).
        <a href="#closest" class="sm-jump">See the closest NASA evidence ↑</a></div>`;
    }
    $("strengthmeter").innerHTML = `
      <div class="sm-top">
        <div class="sm-main">
          <div class="sm-head">
            <span class="sm-title">Whole-Habitat Evidence Strength</span>
            <strong class="sm-score" style="color:${meterColor(wScore)}">${wScore}<small>/100</small></strong>
          </div>
          <div class="sm-bar" role="progressbar" aria-valuenow="${wScore}" aria-valuemin="0" aria-valuemax="100">
            <i style="width:${wScore}%;background:${meterColor(wScore)}"></i>
          </div>
          <div class="sm-backing">
            Backed by <b>${(w.n_runs || 0).toLocaleString()}</b> of <b>${(ds.total_runs || 2003).toLocaleString()}</b> real NASA runs across <b>${ds.total_investigations || 18}</b> PSI flight investigations
            ${w.n_runs > 0 ? `(${w.n_measured} directly measured across ${w.n_investigations} ${w.n_investigations === 1 ? "investigation" : "investigations"})` : "(0 exact 5-condition matches)"}
          </div>
        </div>
        <div class="sm-atmo">
          <div class="sm-head">
            <span class="sm-title">Atmosphere-Only Bound (0g)</span>
            <strong class="sm-score" style="color:${meterColor(atScore)}">${atScore}<small>/100</small></strong>
          </div>
          <div class="sm-bar"><i style="width:${atScore}%;background:${meterColor(atScore)}"></i></div>
          <div class="sm-backing"><b>${(at.n_runs || 0).toLocaleString()}</b> NASA runs match O₂ + pressure + flow + fuel in 0g</div>
        </div>
      </div>
      ${whyZero}
      <div class="sm-factors" aria-label="${esc(activeLabel)}" ${activePart ? "" : 'hidden'}>
        ${subFactors.map(([lbl, pct]) => `<div class="sm-f"><span>${esc(lbl)}</span><b>${pct}%</b><div class="meter"><i style="width:${pct}%"></i></div></div>`).join("")}
      </div>
      <div class="sm-invs">
        <span class="hint">${w.n_runs > 0 ? "Matching PSI investigations:" : (at.n_runs > 0 ? "0g atmosphere PSI investigations:" : `Closest PSI investigations (${(ds.near_any_condition_runs || 0).toLocaleString()} runs match ≥1 condition):`)}</span>
        ${invChips || `<span class="hint">none in tolerance</span>`}
        <span class="sm-planned">Not yet in PSI archive: ${(ds.not_yet_in_psi || ["SoFIE", "FLARE", "LUCI", "FM2"]).join(", ")}</span>
      </div>`;

    $("conditions").innerHTML = c.conditions.map((x) => {
      const s = st.conditions[x.key] || {};
      const sc = Math.round(s.score ?? 0);
      return `<button class="cond" data-list="${esc(x.key)}" title="Click to inspect matching NASA runs">
        <span class="name">${esc(x.label)}</span>
        <span class="pill ${statusCls(x.status)}">${esc(x.status)}</span>
        <span class="n">${x.n.toLocaleString()} runs${s.n_investigations ? ` · ${s.n_investigations} PSIs` : ""}</span>
        <span class="meter" title="Evidence strength ${s.score ?? 0} of 100"><i style="width:${s.score ?? 0}%;background:${meterColor(sc)}"></i></span>
        <span class="hint">strength ${sc}/100</span>
        ${x.note ? `<span class="gnote">${esc(x.note)}</span>` : ""}
      </button>`;
    }).join("");
    const a = c.atmosphere || { status: "No evidence", n: 0, run_ids: [] };
    $("wholes").innerHTML =
      `<button type="button" class="whole ${statusCls(c.whole.status)}" data-list="whole" title="Inspect NASA runs matching all 5 conditions"><b>Whole design:</b> ${c.whole.n.toLocaleString()} NASA runs match all five conditions. <span class="hint">Strength ${wScore}/100</span></button>` +
      `<button type="button" class="whole ${statusCls(a.status)}" data-list="atmo" title="Inspect NASA runs matching atmosphere in 0g"><b>Atmosphere only (0g):</b> ${a.n.toLocaleString()} NASA runs match O₂, pressure, airflow &amp; fuel. <span class="hint">Strength ${atScore}/100</span></button>`;
    const listMap = Object.fromEntries(c.conditions.map((x) => [x.key, (x.run_ids || []).length || !(x.other_run_ids || []).length
      ? { label: x.label, ids: x.run_ids }
      : { label: `${x.label}: runs with other fuels (not counted for this material)`, ids: x.other_run_ids }]));
    listMap.whole = { label: "Whole habitat design (all 5 conditions)", ids: c.whole.run_ids || [] };
    listMap.atmo = { label: "Atmosphere only (O2 + pressure + airflow + fuel in 0g)", ids: a.run_ids || [] };
    $("conditions").dataset.lists = JSON.stringify(listMap);
  }

  function renderExplain(x) {
    $("explainsrc").textContent = x.label + (x.model ? ` · ${x.model}` : "");
    $("claims").innerHTML = x.claims.length
      ? x.claims.map((c) => `<li>
          <span>${esc(c.claim)}</span>
          <span class="cite">${runBtn(c.run_id_reference)} <span class="hint">${esc(c.investigation)} · confidence ${esc(c.confidence_level)} · <span class="ok">✓ verified</span></span></span>
          ${c.engineering_recommendation ? `<span class="rec">${esc(c.engineering_recommendation)}</span>` : ""}
        </li>`).join("")
      : "<li>Not enough data to explain this design. See the evidence case below.</li>";
    $("removed").innerHTML = x.removed_count
      ? `<details class="removed"><summary>${x.removed_count} claim${x.removed_count === 1 ? "" : "s"} removed by the citation verifier</summary>
          <ul>${x.removed.map((r) => `<li><s>${esc(r.claim)}</s> <span class="hint">${esc(r.reason)}</span></li>`).join("")}</ul></details>`
      : `<p class="hint">0 claims removed by the citation verifier. ${x.error ? esc(x.error) : ""}</p>`;
    $("explainnote").textContent = x.note;
  }

  async function updateExplain(t) {
    try {
      const x = await post("/api/explain", { target: t });
      if (lastTarget === t) renderExplain(x);
    } catch (e) {
      if (lastTarget === t) $("claims").innerHTML = `<li class="hint">Explanation unavailable (${esc(e.message)}). The panels below do not need it.</li>`;
    }
  }

  function fmt(v) { return v == null ? "not specified" : typeof v === "number" ? +v.toFixed(2) : v; }

  function renderNext(n) {
    const el = $("next");
    if (!n.needed) {
      el.innerHTML = `<h2>Run this next</h2><p>Your design is already covered by several runs. The most useful next test is a repeat of the least certain one, to raise confidence.</p>${n.nearest_run ? `<p class="hint">Repeat: ${runBtn(n.nearest_run.run_id)}</p>` : ""}`;
      return;
    }
    const r = n.recommended, nr = n.nearest_run;
    const GAP = { o2: "oxygen", psi: "pressure", flow: "airflow", fuel: "material", grav: "gravity", whole: "the full combination" };
    const gaps = (n.gaps || []).map((g) => GAP[g] || g);
    el.innerHTML = `<h2>Run this next</h2>
      <p>Test your exact design. It closes ${gaps.length} evidence gap${gaps.length === 1 ? "" : "s"}: <b>${esc(gaps.join(", "))}</b>.</p>
      <dl class="kv">
        <dt>Oxygen</dt><dd>${fmt(r.o2_pct)} %</dd>
        <dt>Pressure</dt><dd>${fmt(r.pressure_psi)} psi</dd>
        <dt>Airflow</dt><dd>${fmt(r.airflow_cm_s)}${r.airflow_cm_s == null ? "" : " cm/s"}</dd>
        <dt>Gravity</dt><dd>${fmt(r.gravity_g)} g</dd>
        <dt>Material</dt><dd>${esc(r.fuel_state)}</dd>
      </dl>
      ${nr ? `<p class="hint">Cheapest first step: start from ${runBtn(nr.run_id)} (${esc(nr.investigation)}) and change:</p>
      <ul class="changes">${n.changes.length ? n.changes.map((c) => `<li>${esc(FIELD_LABEL[c.field] || c.field)}: ${esc(fmt(c.from))} → ${esc(fmt(c.to))}</li>`).join("") : `<li>nothing: it already matches every condition you set, so repeat it to add confidence</li>`}</ul>` : ""}`;
  }

  function renderSafer(list, t) {
    const el = $("safer");
    const pp = ((t.o2_pct * t.pressure_psi) / 100).toFixed(2);
    const head = `<h2>Tested options with less oxygen</h2>`;
    if (!list.length) {
      el.innerHTML = head + `<p>No tested run has at least 10 % lower oxygen partial pressure than your design (${pp} psi) with this material.</p>`;
      return;
    }
    const atP = list.filter((a) => a.same_pressure).length;
    const pNote = atP ? "" : `<p class="altwarn">None of these is at your pressure (${+t.pressure_psi} psi ± 2): they are a different atmosphere, shown only as the nearest tested lower-oxygen runs.</p>`;
    el.innerHTML = head + `<p class="hint">Real NASA runs with at least 10 % less oxygen partial pressure than your ${pp} psi, runs at your own pressure first. Less oxygen means less to feed a fire; this is evidence, not a safety rating.</p>` + pNote +
      list.map((a) => `<div class="alt">
        <span>${runBtn(a.run_id)} · ${esc(a.investigation)}: ${a.o2_pct} % O₂ at ${a.pressure_psi} psi${a.same_pressure ? ' <span class="pill s-Supported">at your pressure</span>' : ""}</span>
        <span class="meta">O₂ partial pressure ${a.o2_partial_pressure} psi, ${a.reduction_pct} % below yours · confidence ${esc(a.confidence)}</span>
        <span class="meta">To get there: ${a.changes.filter((c) => c.delta).map((c) => `${esc(FIELD_LABEL[c.field] || c.field)} ${c.delta > 0 ? "+" : ""}${c.delta}`).join(", ") || "no change"}</span>
      </div>`).join("");
  }

  function renderRanked(list) {
    $("ranked").innerHTML = list.slice(0, 8).map((r) => {
      const parts = Object.entries(r.breakdown).filter(([, v]) => v != null);
      const total = parts.reduce((s, [k, v]) => s + WEIGHTS[k] * v, 0) || 1;
      const bars = parts.map(([k, v]) => `<i style="width:${(100 * WEIGHTS[k] * v) / total}%;background:${FACTOR_COLOR[k]}" title="${k} ${v}"></i>`).join("");
      return `<li>
        <div class="score">${Math.round(r.score)}<small>/100</small></div>
        <div class="rmain">
          <div class="t"><b>${esc(r.investigation)}</b><span class="tag p-${esc(r.pillar)}">${esc(r.pillar)}</span><span class="hint">${esc(r.psi_id)}</span></div>
          <div class="bars">${bars}</div>
          <div class="rmeta">${r.n_runs} runs · based on ${r.factors_used} of 5 factors · confidence ${esc(r.confidence)}${r.doi ? ` · <a href="https://doi.org/${esc(r.doi)}" target="_blank" rel="noopener">DOI</a>` : ""}</div>
          <div class="runlist">${r.top_runs.map(runBtn).join("")}</div>
        </div></li>`;
    }).join("");
  }

  // ---------------------------------------------------------------- render: lenses

  function legend(items) {
    $("legend").innerHTML = items.map(([label, color]) => `<span style="--c:${color}">${esc(label)}</span>`).join("");
  }

  async function lensData(name) {
    if (!lensCache[name]) lensCache[name] = await get(`/api/lens/${name}`);
    return lensCache[name];
  }

  async function renderLens() {
    const want = lens; // a slower earlier fetch must not draw under a newer tab
    const t = lastTarget || target();
    document.querySelectorAll(".lenses .tab").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.lens === lens)));
    const chart = $("chart");
    if (lens !== "detect" && FL.detect) FL.detect.stop();
    try {
      if (lens === "detect") {
        // the simulator keeps its own state; only build it when the tab is opened, not on every habitat change
        if (!chart.querySelector("#detmap")) FL.detect.render(chart, $("legend"), $("caption"));
        return;
      }
      if (lens === "coverage") {
        const d = await lensData("coverage");
        if (lens !== want) return;
        chart.innerHTML = FL.scatter({
          aria: "Tested atmospheres: oxygen against pressure",
          points: d.points.map((p) => ({ x: p.pressure_psi, y: p.o2_pct, id: p.run_id, color: PILLAR_COLOR[p.pillar] || "var(--c-grey)",
            opacity: p.pressure_basis === "assumed" || p.o2_basis === "assumed" ? 0.25 : 0.75,
            title: `${p.run_id} ${p.investigation}: ${p.o2_pct} % O2, ${p.pressure_psi} psi (${p.o2_basis}/${p.pressure_basis})` })),
          xDomain: [0, 75], yDomain: [10, 100], xLabel: "Pressure (psi)", yLabel: "Oxygen (%)",
          marker: { x: t.pressure_psi, y: t.o2_pct }, box: { x0: t.pressure_psi - 2, x1: t.pressure_psi + 2, y0: t.o2_pct - 6, y1: t.o2_pct + 6 },
        });
        legend(Object.entries(PILLAR_COLOR).map(([k, v]) => [k, v]).concat([["faint dot = assumed cabin air", "var(--c-faint)"]]));
        $("caption").textContent = `Each dot is one of ${d.n_points.toLocaleString()} NASA runs. The dashed box is "close to your design" (±6 oxygen points, ±2 psi). An empty box means no evidence. Click a dot to see its source.`;
      } else if (lens === "coolflame") {
        const d = await lensData("coolflame");
        if (lens !== want) return;
        chart.innerHTML = FL.scatter({
          aria: "Cool-flame outcomes by oxygen and pressure",
          points: d.points.map((p) => ({ x: p.pressure_psi, y: p.o2_pct, id: p.run_id, color: OUTCOME_COLOR[p.outcome] || "var(--c-grey)",
            opacity: p.outcome === "cool_flame" ? 0.95 : 0.55,
            title: `${p.run_id} ${p.investigation} (${p.fuel}): ${OUTCOME_LABEL[p.outcome] || p.outcome}${p.outcome_raw ? " - " + p.outcome_raw : ""}` })),
          xDomain: [0, 75], yDomain: [10, 100], xLabel: "Pressure (psi)", yLabel: "Oxygen (%)", r: 3.6,
          marker: { x: t.pressure_psi, y: t.o2_pct },
        });
        const c = d.counts_by_outcome;
        legend(Object.keys(OUTCOME_COLOR).map((k) => [`${OUTCOME_LABEL[k]} (${c[k] || 0})`, OUTCOME_COLOR[k]]));
        const fList = (d.findings || []).slice(0, 4).map((f) => `<li><b>${esc(f.investigation)} (${esc(f.measured_values)}):</b> ${esc(f.finding)} <span class="hint">[${esc(f.source_ref)}]</span></li>`).join("");
        $("caption").innerHTML = `Cool flames keep burning invisibly after the visible flame goes out, making carbon monoxide and formaldehyde. Points come from CFI, ACME CFI-G and FLEX runs.${fList ? `<ul class="modlist" style="margin-top:.55rem">${fList}</ul>` : ""}`;
      } else if (lens === "aerosol") {
        const d = await lensData("aerosol");
        if (lens !== want) return;
        const rows = d.smoke.map((m) => ({
          label: m.material,
          values: [
            m.fresh && { x: m.fresh.geometric_mean_um, color: "var(--c-flame)", hollow: true, title: `${m.material} fresh smoke: ${m.fresh.geometric_mean_um} µm (${m.fresh.source_ref})` },
            m.aged_720s && { x: m.aged_720s.geometric_mean_um, color: "var(--c-flame)", hollow: false, title: `${m.material} smoke aged 720 s: ${m.aged_720s.geometric_mean_um} µm` },
          ].filter(Boolean),
        }));
        for (const dust of d.dust) rows.push({ label: dust.material.replace(" (fine)", ""), values: [{ x: dust.count_mean_um ?? dust.geometric_mean_um, color: "var(--c-cyan)", title: `${dust.material}: ${dust.count_mean_um} µm average (${dust.source_ref})` }] });
        chart.innerHTML = FL.sizePlot(rows, { aria: "Smoke and dust particle sizes", xDomain: [0.02, 5], xTicks: [0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5], xLabel: "Particle size (micrometres, log scale)" });
        legend([["Smoke, fresh (hollow)", "var(--c-flame)"], ["Smoke, aged 720 s (filled)", "var(--c-flame)"], ["Dust", "var(--c-cyan)"]]);
        $("caption").textContent = d.overlap_note + " Smoke values: SAME-R final report, Table 1. Dust: DAFT report. NASA's shuttle smoke detector, later used in mines, tells smoke from dust for exactly this reason.";
      } else if (lens === "smokepoint") {
        const d = await lensData("smokepoint");
        if (lens !== want) return;
        const FUEL_COLOR = { "propane": "var(--c-green)", "ethylene": "var(--c-cyan)", "50% propylene": "var(--c-gold)",
          "75% propylene": "var(--c-flame)", "propylene": "var(--c-violet)" };
        chart.innerHTML = FL.scatter({
          aria: "SPICE microgravity smoke points: luminous flame length against coflow air rate",
          points: d.points.map((p) => ({ x: p.air_rate_cm_s, y: p.smoke_point_length_mm, id: p.run_id || "", color: FUEL_COLOR[p.fuel] || "var(--c-grey)",
            opacity: p.run_id ? 0.9 : 0.45,
            title: `${p.fuel}, ${p.nozzle_mm} mm nozzle: smoke point at ${p.fuel_rate_mg_s} mg/s fuel, ${p.air_rate_cm_s} cm/s air, luminous length ${p.smoke_point_length_mm} mm${p.run_id ? " (" + p.run_id + ")" : " (not linked to a table run)"}` })),
          xDomain: [0, 70], yDomain: [0, 110], xLabel: "Coflow air rate (cm/s)", yLabel: "Smoke-point flame length (mm)", r: 5,
        });
        legend(Object.entries(FUEL_COLOR).map(([k, v]) => [`${k} (${d.counts_by_fuel[k] || 0})`, v]).concat([["faint dot = not linked to a table run", "var(--c-faint)"]]));
        $("caption").textContent = `${d.n_points} SPICE flames on the ISS at the moment each began to smoke (its smoke point), from the SPICE thesis, Appendix 6.4 (PSI-107). A longer smoke-point flame means a fuel that makes less soot: soot rises from propane to ethylene, 50 % propylene, 75 % propylene and propylene (thesis conclusions). ${d.n_linked_runs} runs are linked; click a dot to open its run.`;
      } else if (lens === "spread") {
        const d = await lensData("spread");
        if (lens !== want) return;
        const colorOf = (p) => (p.investigation === "Saffire-II" ? "var(--c-gold)" : (p.thickness_mm != null && p.thickness_mm < 0.5 ? "var(--c-cyan)" : "var(--c-flame)"));
        chart.innerHTML = FL.scatter({
          aria: "Measured microgravity flame spread rate against airflow",
          points: d.points.map((p) => ({
            x: p.airflow_cm_s, y: p.spread_rate_mm_s, id: p.run_id, color: colorOf(p), opacity: 0.9,
            title: `${p.spread_id} (${p.run_id || p.psi_id} ${p.test_code}): ${p.material}, ${p.flow_direction} ${p.airflow_cm_s} cm/s, ${p.o2_initial_pct}% O2 -> ${p.spread_rate_mm_s} mm/s (${p.source_ref})`
          })),
          xDomain: [0, 32], yDomain: [0.01, 4], logY: true,
          yTicks: [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 4],
          xLabel: "Airflow velocity (cm/s)", yLabel: "Spread rate (mm/s, log scale)", r: 4.4,
        });
        legend([
          ["BASS-II thick PMMA slabs/rods (1–9.5 mm)", "var(--c-flame)"],
          ["BASS-II thin PMMA film (0.1 mm)", "var(--c-cyan)"],
          ["Saffire-II SIBAL fabric (0.37 mm, Cygnus)", "var(--c-gold)"],
        ]);
        $("caption").textContent = `${d.n_points} measured microgravity spread/regression points from NASA/TM-20210011385 (BASS-II Table 5.1 & text) and PSI-99 (Saffire-II). Thin fabrics and 0.1 mm films spread at 2.1–2.6 mm/s — about 15 to over 200 times faster than 1–5 mm PMMA slabs (0.012–0.144 mm/s). Click any dot to inspect its flight run.`;
      } else if (lens === "tested") {
        const d = await lensData("tested");
        if (lens !== want) return;
        chart.innerHTML = FL.scatter({
          aria: "Tested conditions: oxygen against airflow",
          points: d.points.map((p) => ({ x: p.airflow_cm_s, y: p.o2_pct, id: p.run_id, color: PILLAR_COLOR[p.pillar] || "var(--c-grey)",
            opacity: p.o2_basis === "assumed" ? 0.3 : 0.8,
            title: `${p.run_id} ${p.investigation} (${p.fuel_state}): ${p.o2_pct} % O2, ${p.airflow_cm_s} cm/s (${p.o2_basis}/${p.airflow_basis})` })),
          xDomain: [0, 90], yDomain: [10, 40], xLabel: "Airflow (cm/s)", yLabel: "Oxygen (%)",
          marker: t.airflow_cm_s == null ? null : { x: t.airflow_cm_s, y: t.o2_pct },
          box: t.airflow_cm_s == null ? null : { x0: t.airflow_cm_s - 8, x1: t.airflow_cm_s + 8, y0: t.o2_pct - 6, y1: t.o2_pct + 6 },
        });
        legend([["Prevention", PILLAR_COLOR.Prevention], ["Detection", PILLAR_COLOR.Detection], ["faint dot = assumed cabin air", "var(--c-faint)"]]);
        $("caption").textContent = `${d.n_points} runs recorded both oxygen and airflow (BASS-II, Saffire, SPICE, SAME). Airflow matters in space because without gravity there is no rising hot air: cabin ventilation feeds the flame. Open the Flame spread tab for measured spread rates (mm/s).`;
      }
    } catch (e) {
      chart.innerHTML = `<p class="err">Could not load this lens: ${esc(e.message)}</p>`;
    }
  }

  // ---------------------------------------------------------------- evidence drawer

  function basisTag(b) { return b ? `<span class="basis b-${esc(b)}">${esc(b)}</span>` : ""; }

  let drawerSeq = 0;
  async function openEvidence(runId) {
    const my = ++drawerSeq;
    const d = $("drawer");
    d.hidden = false;
    $("drawertitle").textContent = runId;
    $("drawerbody").innerHTML = "Loading…";
    try {
      const { run: r, investigation: inv } = await get(`/api/evidence/${encodeURIComponent(runId)}`);
      if (my !== drawerSeq) return; // a newer click is loading
      $("drawerbody").innerHTML = `
        <p><b>${esc(inv?.title || r.investigation)}</b> (${esc(r.psi_id)}, ${esc(r.pillar)})</p>
        <dl class="kv">
          <dt>Material</dt><dd>${esc(r.fuel_or_material)} (${esc(r.fuel_state)})</dd>
          <dt>Oxygen</dt><dd>${r.o2_pct ?? "–"} % ${basisTag(r.o2_basis)}</dd>
          <dt>Pressure</dt><dd>${r.pressure_psi ?? "–"} psi ${basisTag(r.pressure_basis)}</dd>
          <dt>Airflow</dt><dd>${r.airflow_cm_s ?? "–"} cm/s ${basisTag(r.airflow_basis)}</dd>
          <dt>Gravity</dt><dd>${r.gravity_g} g</dd>
          <dt>Outcome</dt><dd>${esc(r.outcome)}</dd>
          ${r.metric_name ? `<dt>${esc(r.metric_name)}</dt><dd>${esc(r.metric_value)}</dd>` : ""}
          <dt>Confidence</dt><dd>${esc(r.confidence)}</dd>
          <dt>Source</dt><dd>${esc(r.source_table)} (${esc(r.value_source)})</dd>
          <dt>License</dt><dd>${esc(inv?.license || "")}</dd>
        </dl>
        ${r.doi ? `<p>Cite: <a href="https://doi.org/${esc(r.doi)}" target="_blank" rel="noopener">doi.org/${esc(r.doi)}</a></p>` : ""}
        ${r.notes ? `<p class="hint">${esc(r.notes)}</p>` : ""}`;
    } catch (e) {
      $("drawerbody").innerHTML = `<p class="err">${esc(e.message)}</p>`;
    }
  }

  function openList(title, ids) {
    $("drawer").hidden = false;
    $("drawertitle").textContent = title;
    $("drawerbody").innerHTML = ids.length
      ? `<p class="hint">Closest matching runs (up to 10). Click one to see its source.</p><div class="runlist">${ids.map(runBtn).join("")}</div>`
      : "<p>No NASA run in PSI matches this condition. That is a gap in the evidence, not a safety verdict.</p>";
  }

  // ---------------------------------------------------------------- update loop

  async function update() {
    const t = target();
    lastTarget = t;
    renderControls(t);
    const body = { target: t };
    try {
      const [c, st, nx, alt, rk] = await Promise.all([
        post("/api/case", body), post("/api/strength", body), post("/api/next", body),
        post("/api/alternatives", { target: t, k: 3 }), post("/api/rank", { target: t, k: 8 }),
      ]);
      if (lastTarget !== t) return; // a newer request is on its way
      renderVerdict(c); renderConditions(c, st); renderNext(nx); renderSafer(alt, t); renderRanked(rk);
      renderLens();
      updateExplain(t);
      document.dispatchEvent(new CustomEvent("fl:update", { detail: t })); // campaign.js listens
    } catch (e) {
      $("verdict").innerHTML = `<p class="err">Could not reach the FlameLens API (${esc(e.message)}). Is the backend running?</p>`;
    }
  }

  function schedule(ms = 180) { clearTimeout(timer); timer = setTimeout(update, ms); }

  function wire() {
    ["o2", "psi", "flow", "flowoff", "grav", "fuel"].forEach((id) => $(id).addEventListener("input", () => {
      document.querySelectorAll(".pre").forEach((b) => b.setAttribute("aria-pressed", "false"));
      renderControls(target()); schedule();
    }));
    document.querySelectorAll(".lenses .tab").forEach((b) => b.addEventListener("click", () => { lens = b.dataset.lens; renderLens(); }));
    document.addEventListener("click", (e) => {
      const run = e.target.closest("[data-run]");
      if (run) return openEvidence(run.dataset.run);
      const pt = e.target.closest("circle.pt");
      if (pt && pt.dataset.id) return openEvidence(pt.dataset.id);
      const jump = e.target.closest("[data-jump-inv]");
      if (jump) {
        invPillar = "All";
        invSel = [jump.dataset.jumpInv];
        renderInvGrid();
        renderInvDetail();
        $("invdetail")?.scrollIntoView({ behavior: "smooth", block: "nearest" });
        return;
      }
      const cond = e.target.closest("[data-list]");
      if (cond) {
        const lists = JSON.parse($("conditions").dataset.lists || "{}");
        const l = lists[cond.dataset.list];
        return openList(`${l.label}: matching runs`, l.ids);
      }
    });
    $("drawerclose").addEventListener("click", () => { $("drawer").hidden = true; });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && $("briefwrap").hidden) $("drawer").hidden = true; });
  }


  // ---------------------------------------------------------------- investigations explorer

  let invAll = [], invSel = [], invPillar = "All";
  const rng = (r, unit) => (r ? (r[0] === r[1] ? `${r[0]} ${unit}` : `${r[0]}–${r[1]} ${unit}`) : "not recorded");

  // Oxygen / pressure / airflow in a profile: the PSI table range first; when the table leaves it empty, the
  // assumed cabin value (labelled) and any sourced NASA statement from data/curated/condition_notes.csv.
  const NOTE_KEY = { o2: "o2", pressure: "pressure", airflow: "airflow", flow: "airflow", psi: "pressure" };
  function condNotes(p, cond) { return (p.condition_notes || []).filter((n) => n.condition === (NOTE_KEY[cond] || cond)); }
  function condNoteShort(p, cond) {
    return condNotes(p, cond).length ? " (NASA source above)" : " (not in the PSI table)";
  }
  function condCell(p, key, cond, unit) {
    const r = (p.ranges || {})[key], ra = (p.ranges_incl_assumed || {})[key], notes = condNotes(p, cond);
    let head;
    if (r) head = rng(r, unit);
    else if (ra) head = `${rng(ra, unit)} <span class="hint">assumed ISS cabin air (not in the PSI table)</span>`;
    else head = notes.length ? "" : `<span class="hint">not in the PSI table</span>`;
    const src = notes.map((n) => `<div class="cnote"><b>${esc(n.value)}</b> <span class="hint">· ${esc(n.basis)}: “${esc(n.quote)}” (${n.source_url ? `<a href="${esc(n.source_url)}" target="_blank" rel="noopener">${esc(n.source_ref)}</a>` : esc(n.source_ref)})</span></div>`).join("");
    return head + src;
  }

  function renderInvGrid() {
    const pillars = ["All", "Prevention", "Detection", "Suppression", "Other"];
    $("invfilters").innerHTML = pillars.map((p) => `<button class="tab" data-pillar="${p}" aria-selected="${p === invPillar}">${p}</button>`).join("");
    const list = invAll.filter((p) => invPillar === "All" || p.pillar === invPillar);
    $("invgrid").innerHTML = list.map((p) => `<button class="inv" data-inv="${esc(p.psi_id)}" aria-pressed="${invSel.includes(p.psi_id)}">
        <span class="t"><b>${esc(p.acronym)}</b><span class="tag p-${esc(p.pillar)}">${esc(p.pillar)}</span></span>
        <span class="rel">${esc(p.relevance || p.title)}</span>
        <span class="meta">${esc(p.psi_id)} · ${p.n_runs ? `${p.n_runs} runs` : (p.planned_matrix ? "parameter matrix" : "0 runs")} · ${esc(p.hardware_group || "")}${p.challenge_mentions ? " · named in the challenge" : ""}${modCountLabel(p.modeling_count)}</span>
      </button>`).join("");
  }

  function modCountLabel(n) {
    return n ? ` · ${n} PSI ${n === 1 ? "model study" : "model studies"}` : "";
  }

  async function renderInvDetail() {
    const el = $("invdetail");
    if (!invSel.length) { el.innerHTML = `<h2>Details and comparison</h2><p class="hint">Select an investigation to see its objectives, fuels, conditions, what varied, and what was measured. Select a second one to compare.</p>`; return; }
    try {
      if (invSel.length === 1) {
        const p = await get(`/api/investigations/${encodeURIComponent(invSel[0])}`);
        const r = p.ranges || {};
        const mods = p.modeling_studies || [];
        const papers = p.papers || [];
        const pm = p.planned_matrix;
        el.innerHTML = `<h2>${esc(p.acronym)}: ${esc(p.title)}</h2>
          <p class="hint">${esc(p.psi_id)} · ${esc(p.pillar)} · ${esc(p.hardware_group || "")} · ${esc(p.start_date || "")}–${esc(p.end_date || "")} ·
            <a href="${esc(p.psi_url)}" target="_blank" rel="noopener">PSI page</a>${p.doi ? ` · <a href="https://doi.org/${esc(p.doi)}" target="_blank" rel="noopener">DOI</a>` : ""}</p>
          <p><b>Why it matters:</b> ${esc(p.relevance || "")}</p>
          <p><b>Objective:</b> ${esc(p.objectives_summary || "not listed")}</p>
          <p><b>Approach:</b> ${esc(p.approach_summary || "not listed")}</p>
          <dl class="kv">
            <dt>Runs</dt><dd>${p.n_runs || 0}${pm ? " (parameter matrix published; see below)" : ""}</dd>
            <dt>Fuels</dt><dd>${(p.fuels || []).map((f) => `${esc(f.name)} (${f.runs})`).join(", ") || (pm ? esc(pm.fuels.join(", ")) : "not recorded")}</dd>
            <dt>Oxygen</dt><dd>${condCell(p, "o2_pct", "o2", "%")}</dd>
            <dt>Pressure</dt><dd>${condCell(p, "pressure_psi", "pressure", "psi")}</dd>
            <dt>Airflow</dt><dd>${condCell(p, "airflow_cm_s", "airflow", "cm/s")}</dd>
            <dt>Varied</dt><dd>${esc((p.varied || []).join(", ") || "nothing recorded")}</dd>
            <dt>Held constant</dt><dd>${(p.constant || []).map((c) => `${esc(c.condition)}${c.value != null ? ` = ${esc(c.value)}` : condNoteShort(p, c.condition)}`).join(", ") || "–"}</dd>
            <dt>Measured</dt><dd>${esc((p.measurements_mentioned || []).join(", ") || "not stated in the PSI text")}</dd>
            <dt>Outcomes</dt><dd>${Object.entries(p.outcome_counts || {}).map(([k, v]) => `${esc(k)} ${v}`).join(", ") || "–"}</dd>
          </dl>
          ${pm ? `<div class="modbox"><h3>Published parameter matrix (${esc(pm.source_table)})</h3><p class="hint">${esc(pm.note)}</p><p><b>Oxygen levels:</b> ${esc(pm.o2_pct_levels.join(", "))}% · <b>Pressure:</b> ${esc(pm.pressure_atm_levels.join(", "))} atm (${esc(pm.pressure_psi_range.join("–"))} psi) · <b>Flow:</b> ${esc(pm.airflow_cm_s_range.join("–"))} cm/s · <b>Droplet:</b> ${esc(pm.droplet_diameter_mm)} mm in ${esc(pm.ambient_gas)}</p></div>` : ""}
          ${p.research_impacts_summary ? `<p><b>Earth benefits (NASA):</b> ${esc(p.research_impacts_summary)}</p>` : ""}
          ${mods.length ? `<div class="modbox"><h3>Predictive models built from ${esc(p.acronym)} data (PSI ground studies)</h3><ul class="modlist">${mods.map((m) => `<li><b>${esc(m.psi_id)}:</b> ${esc(m.title)} <span class="hint">(${esc(m.method)})</span> · <a href="${esc(m.psi_url)}" target="_blank" rel="noopener">PSI</a>${m.doi ? ` · <a href="https://doi.org/${esc(m.doi)}" target="_blank" rel="noopener">DOI</a>` : ""}</li>`).join("")}</ul></div>` : ""}
          ${papers.length ? `<div class="modbox"><h3>NASA NTRS publications (${papers.length})</h3><ul class="modlist">${papers.map((pp) => `<li><b>${esc(pp.title)}</b> ${pp.year ? `<span class="hint">(${esc(pp.year)})</span>` : ""} · <a href="${esc(pp.ntrs_url)}" target="_blank" rel="noopener">NTRS</a>${pp.pdf_url ? ` · <a href="${esc(pp.pdf_url)}" target="_blank" rel="noopener">PDF</a>` : ""}</li>`).join("")}</ul></div>` : ""}
          <p class="hint">Ranges count measured and text values only. Select a second investigation to compare.</p>`;
      } else {
        const c = await get(`/api/compare?a=${encodeURIComponent(invSel[0])}&b=${encodeURIComponent(invSel[1])}`);
        const val = (v) => esc(Array.isArray(v) ? v.join(", ") : v ?? "–");
        el.innerHTML = `<h2>${esc(c.a.acronym)} vs ${esc(c.b.acronym)}</h2>
          <table class="cmp"><thead><tr><th>Attribute</th><th>${esc(c.a.acronym)}</th><th>${esc(c.b.acronym)}</th></tr></thead><tbody>
          ${c.different.map((d) => `<tr><td>${esc(d.field)}</td><td class="diff">${val(d.a)}</td><td class="diff">${val(d.b)}</td></tr>`).join("")}
          ${c.same.map((s) => `<tr><td>${esc(s.field)}</td><td colspan="2">same: ${val(s.value)}</td></tr>`).join("")}
          </tbody></table>
          ${c.measurements ? `<p class="hint">Measurements: both ${val(c.measurements.shared)} · only ${esc(c.a.acronym)} ${val(c.measurements.only_a)} · only ${esc(c.b.acronym)} ${val(c.measurements.only_b)}</p>` : ""}
          <p class="hint">Orange = differs. Click a selected card again to remove it.</p>`;
      }
    } catch (e) {
      el.innerHTML = `<h2>Details and comparison</h2><p class="err">${esc(e.message)}</p>`;
    }
  }

  async function initModeling() {
    const listEl = $("modelinglist"), noteEl = $("modelingnote");
    if (!listEl) return;
    try {
      const d = await get("/api/modeling");
      noteEl.textContent = d.note;
      listEl.innerHTML = (d.studies || []).map((m) => {
        const chips = (m.uses_flight_psi_ids || []).map((fid, idx) => {
          const acr = (m.uses_acronyms || [])[idx] || fid;
          return `<button type="button" class="modchip" data-jump-inv="${esc(fid)}" title="Inspect ${esc(acr)} (${esc(fid)}) flight investigation">${esc(acr)}</button>`;
        }).join(" ");
        return `<li>
          <div class="modhead"><b>${esc(m.psi_id)}</b> · <a href="${esc(m.psi_url)}" target="_blank" rel="noopener">${esc(m.title)}</a></div>
          <div class="modsub">${esc(m.objective_summary)}</div>
          <div class="modmeta">Uses flight data: ${chips} · Method: ${esc(m.method)}${m.doi ? ` · <a href="https://doi.org/${esc(m.doi)}" target="_blank" rel="noopener">doi.org/${esc(m.doi)}</a>` : ""}</div>
        </li>`;
      }).join("");
    } catch (e) {
      noteEl.textContent = `Could not load modeling studies (${e.message}).`;
    }
  }

  async function initInvestigations() {
    try {
      invAll = await get("/api/investigations");
      renderInvGrid();
    } catch (e) {
      $("invgrid").innerHTML = `<p class="err">Could not load investigations (${esc(e.message)}).</p>`;
    }
    $("invfilters").addEventListener("click", (e) => { const b = e.target.closest("[data-pillar]"); if (b) { invPillar = b.dataset.pillar; renderInvGrid(); } });
    $("invgrid").addEventListener("click", (e) => {
      const b = e.target.closest("[data-inv]"); if (!b) return;
      const id = b.dataset.inv;
      invSel = invSel.includes(id) ? invSel.filter((x) => x !== id) : [...invSel, id].slice(-2);
      renderInvGrid(); renderInvDetail();
    });
  }

  async function init() {
    wire();
    renderControls(target());
    try {
      const [habitats, stats] = await Promise.all([get("/api/habitats"), get("/api/stats")]);
      $("datachip").textContent = `${stats.runs.toLocaleString()} real runs · ${Object.keys(stats.by_investigation).length} NASA PSI investigations · CC0`;
      $("presets").innerHTML = habitats.map((h) => `<button class="pre" data-id="${esc(h.id)}" aria-pressed="false">${esc(h.name)}</button>`).join("");
      document.querySelectorAll(".pre").forEach((b) => b.addEventListener("click", () => setPreset(habitats.find((h) => h.id === b.dataset.id), b)));
      const start = document.querySelector('.pre[data-id="pressurized-rover"]') || document.querySelector(".pre");
      if (start) start.click(); else update();
    } catch (e) {
      $("datachip").textContent = "API not reachable";
      $("datachip").classList.add("err");
      update();
    }
  }

  FL.api = { get, post }; // shared with brief.js
  FL.target = target;

  init();
  initInvestigations();
  initModeling();
})();
