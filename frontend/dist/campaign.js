/* FlameLens test campaign planner: "NASA can fly N more experiments. Fly these."
   Calls POST /api/campaign (deterministic greedy cover over the habitat presets, plus the user's own design
   when it is not a preset). It plans coverage only: it never predicts what a test would show. */
(function () {
  const FL = window.FL;
  const esc = FL.esc;
  const $ = (id) => document.getElementById(id);
  const GAP = { o2: "oxygen", psi: "pressure", flow: "airflow", fuel: "material", grav: "gravity", whole: "the full combination" };
  const FIELD_LABEL = { o2_pct: "Oxygen %", pressure_psi: "Pressure psi", airflow_cm_s: "Airflow cm/s", gravity_g: "Gravity g", fuel_state: "Material" };
  const GNAME = (g) => (g === 0 ? "Microgravity" : g === 0.16 ? "Lunar-gravity" : g === 0.38 ? "Mars-gravity" : g === 1 ? "Earth-gravity" : `${g} g`);
  const num = (v) => (v == null ? "–" : String(+(+v).toFixed(2)));
  let n = 3, habitats = null, profiles = null, lastKey = "", timer = null;

  function presetTargets() {
    return habitats.map((h) => ({ id: h.id, name: h.name, target: { o2_pct: h.o2_pct, pressure_psi: h.pressure_psi,
      airflow_cm_s: h.airflow_cm_s, gravity_g: h.gravity_g, fuel_state: h.fuel_state } }));
  }

  async function load() {
    if (!habitats) habitats = await FL.api.get("/api/habitats");
    if (!profiles) {
      const p = await FL.api.get("/api/investigations");
      profiles = Object.fromEntries((Array.isArray(p) ? p : p.investigations || []).map((x) => [x.psi_id, x]));
    }
    const targets = presetTargets();
    const custom = !document.querySelector(".pre[aria-pressed='true']");
    if (custom) targets.push({ id: "your-design", name: "Your design", target: FL.target() });
    const key = JSON.stringify([n, targets]);
    if (key === lastKey) return;
    lastKey = key;
    const r = await FL.api.post("/api/campaign", { n, targets });
    if (key === lastKey) render(r);
  }

  function render(r) {
    const s = r.summary;
    const coveredNames = r.habitats.filter((h) => h.status === "covered").map((h) => h.name);
    $("cmpsum").innerHTML = `Today <b>${s.covered_now} of ${s.designs}</b> designs ${s.covered_now === 1 ? "has" : "have"} 2 or more NASA runs matching all five conditions${coveredNames.length ? ` (${esc(coveredNames.join(", "))})` : ""}.
      This plan gives <b>${s.planned}</b> more a test: <b>${s.covered_or_planned} of ${s.designs}</b> covered or planned${s.still_open.length ? `, still open: ${esc(s.still_open.join(", "))}` : ""}.`;

    $("cmphabs").innerHTML = r.habitats.map((h) => {
      const cls = h.status === "covered" ? "ok" : h.planned_by ? "plan" : "open";
      const tag = h.status === "covered" ? `${h.whole_n.toLocaleString()} runs` : h.planned_by ? `test #${h.planned_by}` : (h.status === "weak" ? "1 run" : "no runs");
      return `<span class="cmph cmph-${cls}" title="${esc(h.name)}: ${h.whole_n} runs match all five conditions">${esc(h.name)}<small>${tag}</small></span>`;
    }).join("");

    $("cmplist").innerHTML = r.experiments.length ? r.experiments.map((e) => {
      const c = e.conditions, nr = e.nearest_run || {};
      const prof = profiles[String(nr.run_id || "").replace(/-\d{4}$/, "")] || {};
      return `<li class="cmpx">
        <div class="cmprank">#${e.rank}</div>
        <div class="cmpbody">
          <div class="cmpt"><b>${esc(GNAME(c.gravity_g))} test, ${esc(c.fuel_state)} materials</b>
            <span class="cmpcov">covers ${esc(e.covers_names.join(" + "))}</span></div>
          <div class="cmpchips">
            <span>${num(c.o2_pct)} % O₂</span><span>${num(c.pressure_psi)} psi</span>
            <span>${c.airflow_cm_s == null ? "airflow not specified" : num(c.airflow_cm_s) + " cm/s"}</span>
            <span>${num(c.gravity_g)} g</span><span>${esc(c.fuel_state)}</span><span>O₂ partial pressure ${num(e.o2_partial_pressure)} psi</span>
          </div>
          <div class="cmpline">Closes: <b>${esc(e.gaps_closed.map((g) => GAP[g] || g).join(", "))}</b></div>
          ${nr.run_id ? `<div class="cmpline">Start from <button class="runlink" data-run="${esc(nr.run_id)}">${esc(nr.run_id)}</button> (${esc(nr.investigation)}${prof.hardware_group ? `, ${esc(prof.hardware_group)}` : ""}) and change ${e.changes.map((ch) => `${esc(FIELD_LABEL[ch.field] || ch.field)} ${num(ch.from)} → ${esc(typeof ch.to === "number" ? num(ch.to) : ch.to)}`).join("; ") || "nothing"}.</div>` : ""}
          <div class="cmpnote ${e.partial_gravity ? "warn" : ""}">${esc(e.platform_note)}${e.material_note ? ` ${esc(e.material_note)}` : ""}</div>
        </div></li>`;
    }).join("") : `<li class="hint">Every design already has 2 or more NASA runs matching all five conditions. No new experiment is needed for coverage.</li>`;
    $("cmpnote").textContent = r.note + " Matching uses the same rules as the evidence case (±6 oxygen points, ±2 psi, ±8 cm/s, same material and gravity).";
  }

  function schedule() { clearTimeout(timer); timer = setTimeout(() => load().catch((e) => { $("cmplist").innerHTML = `<li class="err">Could not plan the campaign: ${esc(e.message)}</li>`; }), 250); }

  $("cmpn").addEventListener("click", (e) => {
    const b = e.target.closest("[data-n]");
    if (!b) return;
    n = +b.dataset.n;
    document.querySelectorAll("#cmpn [data-n]").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    schedule();
  });
  document.addEventListener("fl:update", schedule);
  FL.campaign = { refresh: schedule };
})();
