/* FlameLens dashboard. Talks to the FastAPI backend on the same origin (/api/...). */
(function () {
  const FL = window.FL;
  const esc = FL.esc;
  const $ = (id) => document.getElementById(id);
  const API = "";

  const PILLAR_COLOR = { Prevention: "#5aebaa", Detection: "#ffc84a", Suppression: "#5cd6ff", Other: "#a99bff" };
  const OUTCOME_COLOR = { cool_flame: "#5cd6ff", hot_flame: "#ff8a24", no_ignition: "#9aa3c7", other: "#a99bff" };
  const OUTCOME_LABEL = { cool_flame: "Cool flame", hot_flame: "Hot flame", no_ignition: "Did not ignite", other: "Other end (extinction, disruption, completion)" };
  const FACTOR_COLOR = { o2: "#ff8a24", psi: "#5cd6ff", flow: "#a99bff", fuel: "#5aebaa", grav: "#ffc84a" };
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
    $("presetnote").innerHTML = `<span class="badge ${p.sourced ? "src" : "ex"}">${p.sourced ? "from the challenge text" : "example values"}</span> ${esc(p.note || "")}`;
    schedule(0);
  }

  // ---------------------------------------------------------------- render: decision

  const statusCls = (s) => (s === "No evidence" ? "s-No" : `s-${s}`);
  const runBtn = (id) => `<button class="runlink" data-run="${esc(id)}">${esc(id)}</button>`;

  function renderVerdict(c) {
    const el = $("verdict");
    const whole = c.whole.n, atmo = c.atmosphere ? c.atmosphere.n : 0;
    el.className = "verdict panel " + (whole >= 2 ? "good" : whole === 0 && atmo === 0 ? "bad" : "");
    let sub = "";
    if (whole === 0 && atmo === 0) sub = "No NASA experiment in PSI tested this combination. This is where new testing is needed.";
    else if (whole === 0) sub = "The atmosphere was tested, but not under these exact conditions (often gravity: every PSI run is microgravity).";
    if (c.conditions.some((x) => x.bounded)) sub += " PSI has no partial-gravity data yet (LUCI and FM2 are planned); microgravity results are one bound.";
    else sub = "Every number below links to the NASA run it came from.";
    el.innerHTML = `<div class="big">${esc(c.verdict)}</div><div class="sub">${esc(sub)}</div>`;
  }

  function renderConditions(c, st) {
    $("conditions").innerHTML = c.conditions.map((x) => {
      const s = st.conditions[x.key] || {};
      return `<button class="cond" data-list="${esc(x.key)}" title="Show matching runs">
        <span class="name">${esc(x.label)}</span>
        <span class="pill ${statusCls(x.status)}">${esc(x.status)}</span>
        <span class="n">${x.n.toLocaleString()} runs</span>
        <span class="meter" title="Evidence strength ${s.score ?? 0} of 100"><i style="width:${s.score ?? 0}%"></i></span>
        <span class="hint">strength ${Math.round(s.score ?? 0)}/100</span>
        ${x.note ? `<span class="gnote">${esc(x.note)}</span>` : ""}
      </button>`;
    }).join("");
    const a = c.atmosphere || { status: "No evidence", n: 0 };
    $("wholes").innerHTML =
      `<div class="whole ${statusCls(c.whole.status)}"><b>Whole design:</b> ${c.whole.n.toLocaleString()} runs match all five conditions. <span class="hint">Strength ${Math.round(c.whole.strength)}/100</span></div>` +
      `<div class="whole ${statusCls(a.status)}"><b>Atmosphere only:</b> ${a.n.toLocaleString()} runs match oxygen, pressure, airflow and fuel together, ignoring gravity.</div>`;
    $("conditions").dataset.lists = JSON.stringify(Object.fromEntries(c.conditions.map((x) => [x.key, { label: x.label, ids: x.run_ids }])));
    $("wholes").dataset.whole = JSON.stringify(c.whole.run_ids || []);
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
      <ul class="changes">${n.changes.map((c) => `<li>${esc(FIELD_LABEL[c.field] || c.field)}: ${esc(fmt(c.from))} → ${esc(fmt(c.to))}</li>`).join("")}</ul>` : ""}`;
  }

  function renderSafer(list, t) {
    const el = $("safer");
    const pp = ((t.o2_pct * t.pressure_psi) / 100).toFixed(2);
    if (!list.length) {
      el.innerHTML = `<h2>Safer tested options</h2><p>No tested run has at least 10 % lower oxygen partial pressure than your design (${pp} psi) with this material.</p>`;
      return;
    }
    el.innerHTML = `<h2>Safer tested options</h2><p class="hint">Real runs with at least 10 % less oxygen partial pressure than your ${pp} psi. Less oxygen means less to feed a fire.</p>` +
      list.map((a) => `<div class="alt">
        <span>${runBtn(a.run_id)} · ${esc(a.investigation)}: ${a.o2_pct} % O₂ at ${a.pressure_psi} psi</span>
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
    const t = lastTarget || target();
    document.querySelectorAll(".tab").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.lens === lens)));
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
        chart.innerHTML = FL.scatter({
          aria: "Tested atmospheres: oxygen against pressure",
          points: d.points.map((p) => ({ x: p.pressure_psi, y: p.o2_pct, id: p.run_id, color: PILLAR_COLOR[p.pillar] || "#888",
            opacity: p.pressure_basis === "assumed" || p.o2_basis === "assumed" ? 0.25 : 0.75,
            title: `${p.run_id} ${p.investigation}: ${p.o2_pct} % O2, ${p.pressure_psi} psi (${p.o2_basis}/${p.pressure_basis})` })),
          xDomain: [0, 75], yDomain: [10, 100], xLabel: "Pressure (psi)", yLabel: "Oxygen (%)",
          marker: { x: t.pressure_psi, y: t.o2_pct }, box: { x0: t.pressure_psi - 2, x1: t.pressure_psi + 2, y0: t.o2_pct - 6, y1: t.o2_pct + 6 },
        });
        legend(Object.entries(PILLAR_COLOR).map(([k, v]) => [k, v]).concat([["faint dot = assumed cabin air", "#55608a"]]));
        $("caption").textContent = `Each dot is one of ${d.n_points.toLocaleString()} NASA runs. The dashed box is "close to your design" (±6 oxygen points, ±2 psi). An empty box means no evidence. Click a dot to see its source.`;
      } else if (lens === "coolflame") {
        const d = await lensData("coolflame");
        chart.innerHTML = FL.scatter({
          aria: "Cool-flame outcomes by oxygen and pressure",
          points: d.points.map((p) => ({ x: p.pressure_psi, y: p.o2_pct, id: p.run_id, color: OUTCOME_COLOR[p.outcome] || "#888",
            opacity: p.outcome === "cool_flame" ? 0.95 : 0.55,
            title: `${p.run_id} ${p.investigation} (${p.fuel}): ${OUTCOME_LABEL[p.outcome] || p.outcome}${p.outcome_raw ? " - " + p.outcome_raw : ""}` })),
          xDomain: [0, 75], yDomain: [10, 100], xLabel: "Pressure (psi)", yLabel: "Oxygen (%)", r: 3.6,
          marker: { x: t.pressure_psi, y: t.o2_pct },
        });
        const c = d.counts_by_outcome;
        legend(Object.keys(OUTCOME_COLOR).map((k) => [`${OUTCOME_LABEL[k]} (${c[k] || 0})`, OUTCOME_COLOR[k]]));
        $("caption").textContent = "Cool flames keep burning invisibly after the visible flame goes out, making carbon monoxide and formaldehyde. Points come from the CFI, ACME CFI-G and FLEX droplet and gas-flame runs. Hiding a visible flame is not the same as putting the fire out.";
      } else if (lens === "aerosol") {
        const d = await lensData("aerosol");
        const rows = d.smoke.map((m) => ({
          label: m.material,
          values: [
            m.fresh && { x: m.fresh.geometric_mean_um, color: "#ff8a24", hollow: true, title: `${m.material} fresh smoke: ${m.fresh.geometric_mean_um} µm (${m.fresh.source_ref})` },
            m.aged_720s && { x: m.aged_720s.geometric_mean_um, color: "#ff8a24", hollow: false, title: `${m.material} smoke aged 720 s: ${m.aged_720s.geometric_mean_um} µm` },
          ].filter(Boolean),
        }));
        for (const dust of d.dust) rows.push({ label: dust.material.replace(" (fine)", ""), values: [{ x: dust.count_mean_um ?? dust.geometric_mean_um, color: "#5cd6ff", title: `${dust.material}: ${dust.count_mean_um} µm average (${dust.source_ref})` }] });
        chart.innerHTML = FL.sizePlot(rows, { aria: "Smoke and dust particle sizes", xDomain: [0.02, 5], xTicks: [0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5], xLabel: "Particle size (micrometres, log scale)" });
        legend([["Smoke, fresh (hollow)", "#ff8a24"], ["Smoke, aged 720 s (filled)", "#ff8a24"], ["Dust", "#5cd6ff"]]);
        $("caption").textContent = d.overlap_note + " Smoke values: SAME-R final report, Table 1. Dust: DAFT report. NASA's shuttle smoke detector, later used in mines, tells smoke from dust for exactly this reason.";
      } else if (lens === "tested") {
        const d = await lensData("tested");
        chart.innerHTML = FL.scatter({
          aria: "Tested conditions: oxygen against airflow",
          points: d.points.map((p) => ({ x: p.airflow_cm_s, y: p.o2_pct, id: p.run_id, color: PILLAR_COLOR[p.pillar] || "#888",
            opacity: p.o2_basis === "assumed" ? 0.3 : 0.8,
            title: `${p.run_id} ${p.investigation} (${p.fuel_state}): ${p.o2_pct} % O2, ${p.airflow_cm_s} cm/s (${p.o2_basis}/${p.airflow_basis})` })),
          xDomain: [0, 90], yDomain: [10, 40], xLabel: "Airflow (cm/s)", yLabel: "Oxygen (%)",
          marker: t.airflow_cm_s == null ? null : { x: t.airflow_cm_s, y: t.o2_pct },
          box: t.airflow_cm_s == null ? null : { x0: t.airflow_cm_s - 8, x1: t.airflow_cm_s + 8, y0: t.o2_pct - 6, y1: t.o2_pct + 6 },
        });
        legend([["Prevention", PILLAR_COLOR.Prevention], ["Detection", PILLAR_COLOR.Detection], ["faint dot = assumed cabin air", "#55608a"]]);
        $("caption").textContent = `${d.n_points} runs recorded both oxygen and airflow (BASS-II, Saffire, SPICE, SAME). Airflow matters in space because without gravity there is no rising hot air: the ventilation feeds the flame. Spread-rate curves are not in the PSI tables, so we show where tests were done.`;
      }
    } catch (e) {
      chart.innerHTML = `<p class="err">Could not load this lens: ${esc(e.message)}</p>`;
    }
  }

  // ---------------------------------------------------------------- evidence drawer

  function basisTag(b) { return b ? `<span class="basis b-${esc(b)}">${esc(b)}</span>` : ""; }

  async function openEvidence(runId) {
    const d = $("drawer");
    d.hidden = false;
    $("drawertitle").textContent = runId;
    $("drawerbody").innerHTML = "Loading…";
    try {
      const { run: r, investigation: inv } = await get(`/api/evidence/${encodeURIComponent(runId)}`);
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
    document.querySelectorAll(".tab").forEach((b) => b.addEventListener("click", () => { lens = b.dataset.lens; renderLens(); }));
    document.addEventListener("click", (e) => {
      const run = e.target.closest("[data-run]");
      if (run) return openEvidence(run.dataset.run);
      const pt = e.target.closest("circle.pt");
      if (pt) return openEvidence(pt.dataset.id);
      const cond = e.target.closest("[data-list]");
      if (cond) {
        const lists = JSON.parse($("conditions").dataset.lists || "{}");
        const l = lists[cond.dataset.list];
        return openList(`${l.label}: matching runs`, l.ids);
      }
    });
    $("drawerclose").addEventListener("click", () => { $("drawer").hidden = true; });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") $("drawer").hidden = true; });
  }


  // ---------------------------------------------------------------- investigations explorer

  let invAll = [], invSel = [], invPillar = "All";
  const rng = (r, unit) => (r ? (r[0] === r[1] ? `${r[0]} ${unit}` : `${r[0]}–${r[1]} ${unit}`) : "not recorded");

  function renderInvGrid() {
    const pillars = ["All", "Prevention", "Detection", "Suppression", "Other"];
    $("invfilters").innerHTML = pillars.map((p) => `<button class="tab" data-pillar="${p}" aria-selected="${p === invPillar}">${p}</button>`).join("");
    const list = invAll.filter((p) => invPillar === "All" || p.pillar === invPillar);
    $("invgrid").innerHTML = list.map((p) => `<button class="inv" data-inv="${esc(p.psi_id)}" aria-pressed="${invSel.includes(p.psi_id)}">
        <span class="t"><b>${esc(p.acronym)}</b><span class="tag p-${esc(p.pillar)}">${esc(p.pillar)}</span></span>
        <span class="rel">${esc(p.relevance || p.title)}</span>
        <span class="meta">${esc(p.psi_id)} · ${p.n_runs || 0} runs · ${esc(p.hardware_group || "")}${p.challenge_mentions ? " · named in the challenge" : ""}</span>
      </button>`).join("");
  }

  async function renderInvDetail() {
    const el = $("invdetail");
    if (!invSel.length) { el.innerHTML = `<h2>Details and comparison</h2><p class="hint">Select an investigation to see its objectives, fuels, conditions, what varied, and what was measured. Select a second one to compare.</p>`; return; }
    try {
      if (invSel.length === 1) {
        const p = await get(`/api/investigations/${encodeURIComponent(invSel[0])}`);
        const r = p.ranges || {};
        el.innerHTML = `<h2>${esc(p.acronym)}: ${esc(p.title)}</h2>
          <p class="hint">${esc(p.psi_id)} · ${esc(p.pillar)} · ${esc(p.hardware_group || "")} · ${esc(p.start_date || "")}–${esc(p.end_date || "")} ·
            <a href="${esc(p.psi_url)}" target="_blank" rel="noopener">PSI page</a>${p.doi ? ` · <a href="https://doi.org/${esc(p.doi)}" target="_blank" rel="noopener">DOI</a>` : ""}</p>
          <p><b>Why it matters:</b> ${esc(p.relevance || "")}</p>
          <p><b>Objective:</b> ${esc(p.objectives_summary || "not listed")}</p>
          <p><b>Approach:</b> ${esc(p.approach_summary || "not listed")}</p>
          <dl class="kv">
            <dt>Runs</dt><dd>${p.n_runs || 0}</dd>
            <dt>Fuels</dt><dd>${(p.fuels || []).map((f) => `${esc(f.name)} (${f.runs})`).join(", ") || "not recorded"}</dd>
            <dt>Oxygen</dt><dd>${rng(r.o2_pct, "%")}</dd>
            <dt>Pressure</dt><dd>${rng(r.pressure_psi, "psi")}</dd>
            <dt>Airflow</dt><dd>${rng(r.airflow_cm_s, "cm/s")}</dd>
            <dt>Varied</dt><dd>${esc((p.varied || []).join(", ") || "nothing recorded")}</dd>
            <dt>Held constant</dt><dd>${(p.constant || []).map((c) => `${esc(c.condition)}${c.value != null ? ` = ${esc(c.value)}` : " (not recorded)"}`).join(", ") || "–"}</dd>
            <dt>Measured</dt><dd>${esc((p.measurements_mentioned || []).join(", ") || "not stated in the PSI text")}</dd>
            <dt>Outcomes</dt><dd>${Object.entries(p.outcome_counts || {}).map(([k, v]) => `${esc(k)} ${v}`).join(", ") || "–"}</dd>
          </dl>
          ${p.research_impacts_summary ? `<p><b>Earth benefits (NASA):</b> ${esc(p.research_impacts_summary)}</p>` : ""}
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

  init();
  initInvestigations();
})();
