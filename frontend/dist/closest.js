/* FlameLens "Closest NASA evidence": when no run matches the whole design, show what NASA did test nearest
   and exactly what differs (POST /api/closest). Real runs and recorded values only; nothing is interpolated. */
(function () {
  const FL = window.FL;
  const esc = FL.esc;
  const $ = (id) => document.getElementById(id);
  const run = (id) => `<button class="runlink" data-run="${esc(id)}">${esc(id)}</button>`;
  let seq = 0;

  async function load(e) {
    const t = (e && e.detail) || FL.target();
    const my = ++seq;
    let r;
    try { r = await FL.api.post("/api/closest", { target: t }); } catch (err) { $("closest").hidden = true; return; }
    if (my !== seq) return;
    const el = $("closest");
    if (!r.needed || (!r.groups.length && !r.same_partial_pressure)) { el.hidden = true; return; }
    const g0 = t.gravity_g > 0;
    el.innerHTML = `
      <div class="ptitle"><h2>Closest NASA evidence</h2><span class="hint">NASA tested parts of this design, never all of them together. Here is what is nearest, and what differs.</span></div>
      <div class="clgrid">
        ${r.groups.map((g) => `<div class="clcard">
          <div class="clhead"><b>${g.n.toLocaleString()} run${g.n === 1 ? "" : "s"}</b>
            <span class="hint">${esc(g.investigations.slice(0, 4).map((i) => `${i.name} (${i.runs})`).join(", "))}</span></div>
          <div class="clsame">✓ Same ${esc(g.same.join(" + ") || "—")}${g0 ? " · in microgravity" : ""}</div>
          <ul class="cldiff">${g.differs.map((d) => `<li>≠ ${esc(d)}</li>`).join("")}</ul>
          <div class="runlist">${g.run_ids.slice(0, 3).map(run).join("")}</div>
        </div>`).join("")}
        ${r.same_partial_pressure ? `<div class="clcard clpp">
          <div class="clhead"><b>${r.same_partial_pressure.n.toLocaleString()} run${r.same_partial_pressure.n === 1 ? "" : "s"}</b>
            <span class="hint">same O₂ partial pressure ≈ ${r.same_partial_pressure.o2_partial_pressure} psi</span></div>
          <div class="clsame">≈ Related, not equivalent</div>
          <ul class="cldiff"><li>≠ oxygen ${esc(r.same_partial_pressure.o2)} (yours ${t.o2_pct} %)</li><li>≠ pressure ${esc(r.same_partial_pressure.psi)} (yours ${t.pressure_psi} psi)</li></ul>
          <p class="hint">${esc(r.same_partial_pressure.note)}</p>
          <div class="runlist">${r.same_partial_pressure.run_ids.slice(0, 3).map(run).join("")}</div>
        </div>` : ""}
      </div>
      ${r.gravity_note ? `<p class="hint clgrav">${esc(r.gravity_note)}</p>` : ""}
      <button type="button" class="btn clcta" id="clgo">Close this gap: see the test campaign planner →</button>`;
    el.hidden = false;
    $("clgo").addEventListener("click", () => $("campaign").scrollIntoView({ behavior: "smooth", block: "start" }));
  }

  document.addEventListener("fl:update", load);
})();
