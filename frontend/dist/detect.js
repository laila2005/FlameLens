/* FlameLens early-detection simulator.
 *
 * ILLUSTRATION, not a validated fire model: a top-down cabin with 8 sensors, a simple
 * advection-diffusion spread (in microgravity there is no rising hot air, so ventilation and slow
 * mixing carry heat, gas and smoke), and three ways to raise an alarm:
 *   heat-only, smoke-only (no particle size), and sensor fusion (rate of rise + CO + small particles + IR flame).
 * Real NASA numbers it is anchored to come from /api/detect/evidence (BASS-II CO and CO2 rises,
 * SAME-R smoke and DAFT dust particle sizes, FLEX/CFI cool flames).
 */
(function () {
  const FL = (window.FL = window.FL || {});
  const esc = FL.esc;

  // cabin geometry (metres) and grid
  const LX = 10, LY = 4, NX = 50, NY = 20, DX = LX / NX;
  const D = 0.06; // effective mixing (m2/s), illustrative
  const HEAT_LOSS = 0.01; // 1/s, heat lost to walls and equipment
  const SENSORS = [
    [0.6, 0.5], [5, 0.4], [9.4, 0.5], [0.6, 3.5], [5, 3.6], [9.4, 3.5], [2.8, 2], [7.2, 2],
  ].map(([x, y], i) => ({ id: i + 1, x, y }));

  // thresholds (illustrative)
  const TH = { heat: 8, rate: 0.08, co: 25, small: 0.3, smokeDet: 0.6, irRange: 7 };

  // scenarios: source strengths per second at full growth (illustrative), plus flags
  const SCENARIOS = {
    flaming: { label: "Flaming fire (solid material)", ignite: 5, grow: 60, heat: 160, co: 4, small: 6, dust: 0, ir: true, fire: true },
    smoulder: { label: "Overheating cable, smouldering", ignite: 5, grow: 120, heat: 10, co: 2.5, small: 8, dust: 0, ir: false, fire: true },
    cool: { label: "Cool flame (fuel droplet, invisible)", ignite: 5, grow: 40, heat: 4, co: 3, small: 0.4, dust: 0, ir: false, fire: true },
    hotspot: { label: "Hot laptop or battery (not a fire)", ignite: 5, grow: 20, heat: 150, co: 0, small: 0, dust: 0, ir: false, fire: false },
    dust: { label: "Dust cloud after cleaning (not a fire)", ignite: 5, grow: 5, heat: 0, co: 0, small: 0, dust: 25, ir: false, fire: false, stop: 30 },
  };

  let evidence = null;
  // CO near the source at full growth (ppm). Flaming replays a real BASS-II test's measured CO rise;
  // smouldering uses the median BASS-II rise; the cool flame uses the 90th percentile (no CO data for it).
  let coPeak = 412;
  let boundary = 0.695; // µm: geometric middle between the largest measured smoke and dust (from /api/detect/evidence)
  const st = { scenario: "flaming", airflow: 5, show: "co", src: { x: 3.5, y: 1.6 }, running: false, t: 0, timer: null,
    testId: "PSI-25-0030", material: "Silicone" };
  const realTest = () => (evidence?.gas?.tests || []).find((x) => x.run_id === st.testId) || (evidence?.gas?.tests || [])[0];
  const smokeSize = () => {
    const s = (evidence?.particles?.smoke || []).find((x) => x.material === st.material && !x.aging_s);
    return s ? s.geometric_mean_um : 0.128;
  };
  const dustSize = () => evidence?.particles?.dust_mean_um ?? 1.65;
  function setCoPeak() {
    const g = evidence?.gas || {};
    if (st.scenario === "flaming" && realTest()) coPeak = realTest().co_rise_ppm;
    else if (st.scenario === "smoulder" && g.co_rise_ppm?.median) coPeak = g.co_rise_ppm.median;
    else if (g.co_rise_ppm?.p90) coPeak = g.co_rise_ppm.p90;
  }

  function newFields() {
    const z = () => new Float32Array(NX * NY);
    return { T: z(), CO: z(), SM: z(), DU: z() };
  }
  let F = newFields();
  let hist = []; // sensor temperature history for the rate of rise
  let result = null;

  const idx = (i, j) => j * NX + i;
  const cellOf = (x, y) => [Math.min(NX - 1, Math.max(0, Math.floor(x / DX))), Math.min(NY - 1, Math.max(0, Math.floor(y / DX)))];

  function step(dt) {
    const s = SCENARIOS[st.scenario];
    const u = st.airflow / 100; // cm/s -> m/s, flow along +x, out through the right wall
    const nsub = Math.max(1, Math.ceil((u * dt) / (0.5 * DX)), Math.ceil((D * dt) / (0.2 * DX * DX)));
    const h = dt / nsub;
    const age = st.t - s.ignite;
    const g = age <= 0 || (s.stop && age > s.stop) ? 0 : Math.min(1, Math.pow(age / s.grow, 2));
    const [si, sj] = cellOf(st.src.x, st.src.y);
    for (let k = 0; k < nsub; k++) {
      for (const key of ["T", "CO", "SM", "DU"]) {
        const c = F[key], n = new Float32Array(c.length);
        for (let j = 0; j < NY; j++) for (let i = 0; i < NX; i++) {
          const p = idx(i, j);
          const left = i > 0 ? c[idx(i - 1, j)] : 0; // clean air enters on the left
          const right = i < NX - 1 ? c[idx(i + 1, j)] : c[p];
          const up = j > 0 ? c[idx(i, j - 1)] : c[p];
          const down = j < NY - 1 ? c[idx(i, j + 1)] : c[p];
          const adv = -u * (c[p] - left) / DX;
          const dif = D * (left + right + up + down - 4 * c[p]) / (DX * DX);
          n[p] = Math.max(0, c[p] + h * (adv + dif - (key === "T" ? HEAT_LOSS * c[p] : 0)));
        }
        F[key] = n;
      }
      const p = idx(si, sj);
      F.T[p] += h * g * s.heat;
      F.CO[p] += h * g * s.co * coPeak * 0.5;
      F.SM[p] += h * g * s.small;
      F.DU[p] += h * g * s.dust;
    }
    st.t += dt;
  }

  function readSensors() {
    const s = SCENARIOS[st.scenario];
    const lit = s.ir && st.t > s.ignite + 3;
    return SENSORS.map((q) => {
      const p = idx(...cellOf(q.x, q.y));
      const dist = Math.hypot(q.x - st.src.x, q.y - st.src.y);
      return { ...q, T: F.T[p], CO: F.CO[p], SM: F.SM[p], DU: F.DU[p], ir: lit && dist <= TH.irRange ? 1 / Math.max(1, dist * dist) : 0 };
    });
  }

  function evaluate(readings) {
    hist.push({ t: st.t, T: readings.map((r) => r.T) });
    while (hist.length && st.t - hist[0].t > 10) hist.shift();
    const old = hist[0];
    readings.forEach((r, k) => {
      r.rate = old && st.t > old.t ? (r.T - old.T[k]) / (st.t - old.t) : 0;
      r.flags = { rate: r.rate >= TH.rate, co: r.CO >= TH.co, small: r.SM >= TH.small, ir: r.ir > 0, dustOnly: r.DU >= TH.small && r.SM < TH.small };
    });
    const any = (f) => readings.some((r) => r.flags[f]);
    // 1) heat-only detector  2) smoke-only detector (cannot tell particle size)
    if (result.heat == null && readings.some((r) => r.T >= TH.heat)) result.heat = st.t;
    if (result.smoke == null && readings.some((r) => r.SM + r.DU >= TH.smokeDet)) result.smoke = st.t;
    // 3) fusion: needs two independent signs, and knows what each pattern means
    let verdict = null;
    if (any("ir") && (any("co") || any("rate"))) verdict = "Flaming fire";
    else if (any("co") && any("small")) verdict = "Smouldering / overheating (pre-fire)";
    else if (any("co") && !any("ir") && !readings.some((r) => r.T >= TH.heat)) verdict = "Possible cool flame: invisible combustion";
    else if (any("small")) verdict = "Smoke confirmed by particle size (not dust)";
    if (verdict && result.fused == null) {
      result.fused = st.t;
      result.verdict = verdict;
      // locate: weighted centre of the sensors that see the most
      let wx = 0, wy = 0, ws = 0;
      for (const r of readings) {
        const w = r.CO / TH.co + r.SM / TH.small + r.T / TH.heat + r.ir * 20;
        wx += w * r.x; wy += w * r.y; ws += w;
      }
      if (ws > 0) result.loc = { x: wx / ws, y: wy / ws, err: Math.hypot(wx / ws - st.src.x, wy / ws - st.src.y) };
    }
    if (!result.note) {
      if (any("dustOnly")) result.note = "Large particles only: fusion classifies this as dust, not smoke.";
      else if (any("rate") && !any("co") && !any("small") && !any("ir")) result.note = "Heat rising with no gas, smoke or flame: a hot spot to check, not a fire alarm.";
    }
    return readings;
  }

  // ---------------------------------------------------------------- drawing

  function color(v, max) {
    const a = Math.min(1, v / max);
    return a < 0.02 ? null : `rgba(255,${Math.round(170 - 120 * a)},40,${(0.15 + 0.75 * a).toFixed(2)})`;
  }

  function svg(readings) {
    const W = 640, H = 290, L = 20, T = 30, S = (W - 2 * L) / LX; // px per metre
    const X = (x) => L + x * S, Y = (y) => T + y * S;
    const field = { co: F.CO, heat: F.T, smoke: F.SM }[st.show];
    const max = { co: 150, heat: 40, smoke: 4 }[st.show];
    let s = `<svg viewBox="0 0 ${W} ${H}" id="detsvg" role="img" aria-label="Cabin sensor simulation">`;
    s += `<rect x="${X(0)}" y="${Y(0)}" width="${LX * S}" height="${LY * S}" rx="6" style="fill:var(--c-room);stroke:var(--c-roomline);stroke-width:2"/>`;
    for (let j = 0; j < NY; j++) for (let i = 0; i < NX; i++) {
      const c = color(field[idx(i, j)], max);
      if (c) s += `<rect x="${X(i * DX)}" y="${Y(j * DX)}" width="${DX * S + 0.5}" height="${DX * S + 0.5}" fill="${c}"/>`;
    }
    s += `<text x="${X(0)}" y="${T - 10}">air in →</text><text x="${X(LX)}" y="${T - 10}" text-anchor="end">→ air out (${st.airflow} cm/s)</text>`;
    if (st.airflow === 0) s += `<text x="${W / 2}" y="${T - 10}" text-anchor="middle" style="fill:var(--amber)">ventilation off: only slow mixing moves smoke</text>`;
    // source
    s += `<g transform="translate(${X(st.src.x)} ${Y(st.src.y)})"><circle r="9" style="fill:none;stroke:var(--c-flame);stroke-width:2.5"/><path d="M0 -6 C 4 -1, 4 4, 0 6 C -4 4, -4 -1, 0 -6 Z" style="fill:var(--c-flame)"/></g>`;
    // estimated location
    if (result && result.loc) {
      const { x, y } = result.loc;
      s += `<g transform="translate(${X(x)} ${Y(y)})" style="stroke:var(--c-cyan);stroke-width:2.5"><line x1="-8" y1="-8" x2="8" y2="8"/><line x1="-8" y1="8" x2="8" y2="-8"/></g>`;
    }
    for (const r of readings) {
      const f = r.flags || {};
      const n = (f.rate ? 1 : 0) + (f.co ? 1 : 0) + (f.small ? 1 : 0) + (f.ir ? 1 : 0);
      const fill = n >= 2 ? "var(--c-red)" : n === 1 ? "var(--c-gold)" : "var(--c-green)";
      s += `<circle cx="${X(r.x)}" cy="${Y(r.y)}" r="8" style="fill:${fill};stroke:var(--c-ink-on);stroke-width:2"><title>Sensor ${r.id}: +${r.T.toFixed(1)} K, ${r.CO.toFixed(0)} ppm CO, smoke ${r.SM.toFixed(2)}, dust ${r.DU.toFixed(2)}${r.ir ? ", IR flame seen" : ""}${r.SM > 0.05 ? `, smoke particles ${smokeSize()} µm` : ""}${r.DU > 0.05 ? `, dust particles ${dustSize()} µm` : ""}</title></circle>`;
      s += `<text x="${X(r.x)}" y="${Y(r.y) + 4}" text-anchor="middle" style="fill:var(--c-ink-on);font-weight:700">${r.id}</text>`;
    }
    s += `<text x="${L}" y="${H - 8}">t = ${st.t.toFixed(0)} s · showing ${st.show === "co" ? "CO gas" : st.show === "heat" ? "temperature rise" : "smoke particles"} · click the cabin to move the source</text>`;
    return s + "</svg>";
  }

  const fmtT = (v) => (v == null ? "—" : `${v.toFixed(0)} s`);

  function resultsHtml() {
    const s = SCENARIOS[st.scenario];
    const r = result;
    const falseA = (t) => (t != null && !s.fire ? ' <span class="pill s-No">false alarm</span>' : "");
    const missed = (t) => (t == null && s.fire && st.t > s.ignite + 30 ? ' <span class="pill s-Weak">not yet</span>' : "");
    return `<table class="dettable"><thead><tr><th>Detector</th><th>First alarm</th><th>Comment</th></tr></thead><tbody>
      <tr><td>Heat only (+${TH.heat} K)</td><td>${fmtT(r.heat)}${falseA(r.heat)}${missed(r.heat)}</td><td>${s.fire ? "Waits for heat to travel to a sensor." : "Heat alone cannot tell a hot laptop from a fire."}</td></tr>
      <tr><td>Smoke only (any particle)</td><td>${fmtT(r.smoke)}${falseA(r.smoke)}${missed(r.smoke)}</td><td>Cannot tell smoke from dust.</td></tr>
      <tr><td><b>FlameLens fusion</b></td><td><b>${fmtT(r.fused)}</b>${falseA(r.fused)}${missed(r.fused)}</td><td>${r.verdict ? esc(r.verdict) : esc(r.note || "Watching: needs two independent signs.")}${r.loc ? `<br>Located within ${r.loc.err.toFixed(1)} m (blue ×).` : ""}</td></tr>
    </tbody></table>`;
  }

  function evidenceHtml() {
    if (!evidence) return `<p class="hint">Real NASA numbers behind this simulation load from /api/detect/evidence.</p>`;
    const g = evidence.gas || {}, p = evidence.particles || {}, c = evidence.cool_flames || {};
    const co = g.co_rise_ppm || {}, co2 = g.co2_rise_pct || {};
    const sm = p.smoke_geometric_mean_um_range || [];
    return `<div class="detev"><b>Real NASA numbers this is built on</b><ul>
      <li>Burning in BASS-II raised CO by a median of ${co.median ?? "?"} ppm (90th percentile ${co.p90 ?? "?"}, max ${co.max ?? "?"}) over ${g.n_tests ?? "?"} tests; CO₂ by a median of ${co2.median ?? "?"} %. A gas channel sees fires.</li>
      <li>Smoke particles are ${sm[0] ?? "?"}–${sm[1] ?? "?"} µm (SAME-R); test dust is about ${p.dust_mean_um ?? "?"} µm (DAFT). Size tells them apart.</li>
      <li>${c.n_cool_flame_runs ?? "?"} cool-flame runs (CFI, ACME CFI-G): ${esc(c.note || "")}</li>
    </ul><p class="hint">${esc(evidence.note || "")}</p></div>`;
  }

  // ---------------------------------------------------------------- control

  function reset() {
    stop();
    F = newFields(); hist = []; st.t = 0;
    setCoPeak();
    result = { heat: null, smoke: null, fused: null, verdict: null, loc: null, note: null };
    paint(evaluate(readSensors()));
    const info = document.getElementById("detinfo");
    if (info) info.innerHTML = scenarioInfo();
  }

  function tick() {
    let rs = null;
    for (let k = 0; k < 2; k++) { step(0.5); rs = evaluate(readSensors()); }
    paint(rs);
    if (st.t >= 240) stop();
  }
  let lastFlags = [];

  function paint(readings) {
    lastFlags = readings.map((r) => r.flags);
    const map = document.getElementById("detmap");
    if (!map) return stop();
    map.innerHTML = svg(readings);
    document.getElementById("detresults").innerHTML = resultsHtml();
    document.getElementById("detrun").textContent = st.running ? "Pause" : st.t > 0 ? "Resume" : "Start";
  }

  function start() { if (st.running) return; st.running = true; st.timer = setInterval(tick, 80); }
  function stop() { st.running = false; clearInterval(st.timer); const b = document.getElementById("detrun"); if (b) b.textContent = st.t > 0 ? "Resume" : "Start"; }

  async function loadEvidence() {
    try {
      const r = await fetch("/api/detect/evidence");
      if (!r.ok) return;
      evidence = await r.json();
      if (evidence?.particles?.smoke_dust_boundary_um) boundary = evidence.particles.smoke_dust_boundary_um;
      fillSelectors();
      reset();
      const box = document.getElementById("detevidence");
      if (box) box.innerHTML = evidenceHtml();
    } catch (e) { /* the simulation still runs with its default numbers */ }
  }

  function fillSelectors() {
    const ts = document.getElementById("dettest"), ms = document.getElementById("detmat");
    const tests = evidence?.gas?.tests || [];
    if (ts && tests.length) ts.innerHTML = tests.map((x) => `<option value="${esc(x.run_id)}"${x.run_id === st.testId ? " selected" : ""}>${esc(x.run_id)} · ${esc(x.material)} · CO +${Math.round(x.co_rise_ppm)} ppm</option>`).join("");
    const mats = (evidence?.particles?.smoke || []).filter((x) => !x.aging_s);
    if (ms && mats.length) ms.innerHTML = mats.map((x) => `<option value="${esc(x.material)}"${x.material === st.material ? " selected" : ""}>${esc(x.material)} · ${x.geometric_mean_um} µm</option>`).join("");
  }
  function showSelectors() {
    const a = document.getElementById("dettestwrap"), b = document.getElementById("detmatwrap");
    if (a) a.hidden = st.scenario !== "flaming";
    if (b) b.hidden = st.scenario !== "smoulder";
  }
  function scenarioInfo() {
    const g = evidence?.gas || {};
    if (!evidence) return "Loading the real NASA numbers…";
    if (st.scenario === "flaming") {
      const x = realTest();
      return x ? `Replaying real test <b>${esc(x.run_id)}</b> (${esc(x.material)}, ${x.o2_pct ?? "?"} % O₂, ${x.airflow_cm_s ?? "?"} cm/s): CO ${x.co_initial_ppm} → ${x.co_final_ppm} ppm, CO₂ ${x.co2_initial_pct} → ${x.co2_final_pct} %. The measured CO rise (${Math.round(x.co_rise_ppm)} ppm) is the CO level at the source.` : "";
    }
    if (st.scenario === "smoulder") return `CO at the source = median BASS-II rise (${g.co_rise_ppm?.median} ppm). Smoke particles: ${esc(st.material)} ${smokeSize()} µm (SAME-R), below the ${boundary} µm smoke/dust boundary, so fusion counts them as smoke.`;
    if (st.scenario === "cool") return `No CO was recorded for cool flames in PSI tables; CO at the source uses the BASS-II 90th percentile (${g.co_rise_ppm?.p90} ppm) as a stand-in. ${evidence.cool_flames?.n_cool_flame_runs ?? ""} cool-flame runs exist (CFI, ACME CFI-G).`;
    if (st.scenario === "dust") return `Dust particles ${dustSize()} µm (DAFT, Arizona Road Dust), above the ${boundary} µm boundary, so fusion does not call it smoke.`;
    return "A heat source with no gas, smoke or flame. No NASA run is replayed: this is the nuisance case.";
  }

  FL.detect = {
    render(chart, legend, caption) {
      chart.innerHTML = `
        <div class="detctl">
          <label>Scenario <select id="detscen">${Object.entries(SCENARIOS).map(([k, v]) => `<option value="${k}"${k === st.scenario ? " selected" : ""}>${esc(v.label)}</option>`).join("")}</select></label>
          <label>Ventilation <output id="detflowo">${st.airflow} cm/s</output><input id="detflow" type="range" min="0" max="40" step="1" value="${st.airflow}"></label>
          <label>Show <select id="detshow"><option value="co"${st.show === "co" ? " selected" : ""}>CO gas</option><option value="heat"${st.show === "heat" ? " selected" : ""}>Temperature rise</option><option value="smoke"${st.show === "smoke" ? " selected" : ""}>Smoke particles</option></select></label>
          <label id="dettestwrap">Real NASA test (BASS-II) <select id="dettest"><option>loading…</option></select></label>
          <label id="detmatwrap" hidden>Smoke material (SAME-R) <select id="detmat"><option>loading…</option></select></label>
          <span class="detbtns"><button class="btn" id="detrun">Start</button><button class="btn" id="detreset">Reset</button></span>
        </div>
        <p class="hint" id="detinfo"></p>
        <div id="detmap"></div>
        <div id="detresults"></div>
        <div id="detevidence">${evidenceHtml()}</div>`;
      legend.innerHTML = `<span style="--c:var(--c-green)">sensor quiet</span><span style="--c:var(--c-gold)">one sign</span><span style="--c:var(--c-red)">two or more signs</span><span style="--c:var(--c-flame)">true source</span><span style="--c:var(--c-cyan)">estimated source (×)</span>`;
      caption.textContent = "Illustration, not a validated fire model. Eight sensors in a 10 × 4 m module. In microgravity hot gas does not rise, so ventilation and slow mixing decide what each sensor sees. Heat alone cannot prove a fire; FlameLens fuses temperature rate of rise, CO, particle size and infrared flame signals. Thresholds are illustrative; real use needs engineering tests and certification.";
      const re = () => reset();
      document.getElementById("detscen").addEventListener("change", (e) => { st.scenario = e.target.value; showSelectors(); re(); });
      document.getElementById("dettest").addEventListener("change", (e) => {
        st.testId = e.target.value;
        const tt = realTest();
        if (tt && tt.airflow_cm_s != null) { st.airflow = Math.round(tt.airflow_cm_s); document.getElementById("detflow").value = st.airflow; document.getElementById("detflowo").textContent = `${st.airflow} cm/s`; }
        re();
      });
      document.getElementById("detmat").addEventListener("change", (e) => { st.material = e.target.value; re(); });
      fillSelectors(); showSelectors();
      document.getElementById("detflow").addEventListener("input", (e) => { st.airflow = +e.target.value; document.getElementById("detflowo").textContent = `${st.airflow} cm/s`; re(); });
      document.getElementById("detshow").addEventListener("change", (e) => { st.show = e.target.value; paint(readSensors().map((r, i) => Object.assign(r, { flags: lastFlags[i] || {} }))); });
      document.getElementById("detrun").addEventListener("click", () => (st.running ? stop() : start()));
      document.getElementById("detreset").addEventListener("click", re);
      document.getElementById("detmap").addEventListener("click", (e) => {
        const svgEl = document.getElementById("detsvg");
        if (!svgEl) return;
        const pt = svgEl.createSVGPoint(); pt.x = e.clientX; pt.y = e.clientY;
        const p = pt.matrixTransform(svgEl.getScreenCTM().inverse());
        const S = (640 - 40) / LX, x = (p.x - 20) / S, y = (p.y - 30) / S;
        if (x >= 0 && x <= LX && y >= 0 && y <= LY) { st.src = { x, y }; re(); }
      });
      reset();
      if (!evidence) loadEvidence();
    },
    stop,
    /** Run a scenario without drawing (for checks): returns alarm times, verdict and location error. */
    simulate(scenario, airflow = 10, src = { x: 3.5, y: 1.6 }, seconds = 240) {
      const saved = { ...st, src: { ...st.src } };
      stop();
      Object.assign(st, { scenario, airflow, src, t: 0 });
      setCoPeak();
      F = newFields(); hist = [];
      result = { heat: null, smoke: null, fused: null, verdict: null, loc: null, note: null };
      while (st.t < seconds) { step(0.5); evaluate(readSensors()); }
      const out = { ...result, loc: result.loc && { ...result.loc } };
      Object.assign(st, saved);
      return out;
    },
  };
})();
