/* FlameLens mission atmosphere journey: one Artemis-style crew mission as a timeline of atmospheres
   (ISS cabin -> spacesuit -> pressurized rover -> Moon base), each with its evidence strength from the same
   deterministic engine. The weakest stage is flagged with the test to run next (POST /api/journey). */
(function () {
  const FL = window.FL;
  const esc = FL.esc;
  const $ = (id) => document.getElementById(id);
  const GAP = { o2: "oxygen", psi: "pressure", flow: "airflow", fuel: "material", grav: "gravity", whole: "the full combination" };
  const FIELD_LABEL = { o2_pct: "Oxygen %", pressure_psi: "Pressure psi", airflow_cm_s: "Airflow cm/s", gravity_g: "Gravity g", fuel_state: "Material" };
  const GRAV = { 0: "0 g", 0.16: "Moon 0.16 g", 0.38: "Mars 0.38 g", 1: "1 g" };
  const num = (v) => (v == null ? "–" : String(+(+v).toFixed(2)));
  const val = (v) => (typeof v === "number" ? num(v) : v == null || v === "" ? "–" : String(v));
  const tone = (s) => (s >= 65 ? "ok" : s >= 25 ? "amber" : "bad");
  const run = (id) => `<button class="runlink" data-run="${esc(id)}">${esc(id)}</button>`;

  function card(s) {
    const t = s.target, sc = Math.round(s.strength);
    const nx = s.next || {}, nr = nx.nearest_run;
    const gaps = (nx.gaps && nx.gaps.length ? nx.gaps : s.gaps).map((g) => GAP[g] || g);
    return `<li class="jstage ${s.weakest ? "jweak" : ""} j-${tone(sc)}">
      <div class="jtop"><span class="jnum">${s.order}</span><b>${esc(s.name)}</b>
        <span class="pill ${s.status === "No evidence" ? "s-No" : "s-" + esc(s.status)}">${esc(s.status)}</span></div>
      <div class="jchips"><span>${num(t.o2_pct)} % O₂</span><span>${num(t.pressure_psi)} psi</span><span>${esc(GRAV[t.gravity_g] || num(t.gravity_g) + " g")}</span>
        <span>${t.airflow_cm_s == null ? "airflow n/a" : num(t.airflow_cm_s) + " cm/s"}</span><span>${esc(t.fuel_state)}</span></div>
      <div class="jpp">O₂ partial pressure <b>${num(s.o2_partial_pressure)} psi</b></div>
      <div class="jscore"><strong class="t-${tone(sc)}">${sc}<small>/100</small></strong>
        <span class="hint">${s.whole_n.toLocaleString()} NASA run${s.whole_n === 1 ? "" : "s"} match all five conditions · ${s.supported_count} of 5 supported</span></div>
      <div class="sm-bar"><i style="width:${sc}%;background:var(--${tone(sc) === "ok" ? "ok" : tone(sc) === "amber" ? "amber" : "bad"})"></i></div>
      ${s.weakest ? `<div class="jnext"><div class="jflag">Weakest stage · test this next</div>
        <div>Closes: <b>${esc(gaps.join(", ") || "repeat for confidence")}</b></div>
        ${nr ? `<div>Start from ${run(nr.run_id)} (${esc(nr.investigation)}) and change ${(nx.changes || []).map((ch) => `${esc(FIELD_LABEL[ch.field] || ch.field)} ${esc(val(ch.from))} → ${esc(val(ch.to))}`).join("; ") || "nothing"}.</div>` : ""}
      </div>` : ""}
      <button type="button" class="btn jopen" data-open="${esc(s.id)}">Open this stage ↑</button>
    </li>`;
  }

  async function load() {
    let r;
    try { r = await FL.api.post("/api/journey", {}); } catch (e) {
      $("jlist").innerHTML = `<li class="err">Could not load the mission journey: ${esc(e.message)}</li>`; return;
    }
    const weak = r.stages.find((s) => s.weakest);
    const ms = Math.round(r.mission_strength ?? 0);
    $("jsum").innerHTML = `Mission evidence: <b class="t-${tone(ms)}">${ms}/100</b>, set by its weakest stage${weak ? `, <b>${esc(weak.name)}</b>` : ""}.
      <span class="hint">${r.summary.fully_backed} of ${r.summary.stages} stages ${r.summary.fully_backed === 1 ? "is" : "are"} backed by 2 or more NASA runs matching all five conditions.</span>`;
    $("jlist").innerHTML = r.stages.map(card).join("");
    $("jnote").textContent = r.note;
  }

  $("jlist").addEventListener("click", (e) => {
    const b = e.target.closest("[data-open]");
    if (!b) return;
    const pre = document.querySelector(`.pre[data-id="${b.dataset.open}"]`);
    if (pre) { pre.click(); window.scrollTo({ top: 0, behavior: "smooth" }); }
  });
  load();
})();
