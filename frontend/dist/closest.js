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
      <div class="ptitle"><h2>Closest NASA evidence</h2><span class="hint">${r.groups.length && !r.groups[0].relaxed.length ? "NASA tested this atmosphere, but only in microgravity. Here are those runs." : "NASA tested parts of this design, never all of them together. Here is what is nearest, and what differs."}</span></div>
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
      ${(r.beyond_psi && r.beyond_psi.rows.length) ? `<div class="clbeyond">
        <div class="clbhead"><b>Outside PSI: NASA Saffire spacecraft fires tested this atmosphere</b>
          <span class="hint">cited, not counted in the score</span></div>
        <ul class="clbrows">${r.beyond_psi.rows.slice(0, 3).map((b) => `<li>
          <div><b>${esc(b.id.replace("SAFFIRE-", "Saffire "))}</b> · ${esc(b.material)} · ${b.o2_pct} % O₂ at ${b.pressure_kpa} kPa (${b.pressure_psi} psi) · ${b.flow_cm_s} cm/s ${esc(b.flow_direction)} flow · microgravity</div>
          <div class="clsame">✓ Same ${esc(b.same.join(" + "))}</div>
          ${b.differs.length ? `<ul class="cldiff">${b.differs.map((d) => `<li>≠ ${esc(d)}</li>`).join("")}</ul>` : ""}
          <div class="clbout">${esc(b.outcome)}</div>
          <div class="hint">Source: <a href="${esc(b.source_url)}" target="_blank" rel="noopener">${esc(b.source_ref)}</a></div>
        </li>`).join("")}</ul>
        <p class="hint">${esc(r.beyond_psi.note)}</p>
      </div>` : ""}
      ${(r.beyond_psi_limits && r.beyond_psi_limits.rows.length) ? `<div class="clbeyond cllimits">
        <div class="clbhead"><b>Outside PSI: where NASA saw these materials stop burning</b>
          <span class="hint">cited, not counted in the score</span></div>
        <ul class="clbrows">${r.beyond_psi_limits.rows.map((b) => `<li>
          <div><b>${esc(b.material)}</b> · ${esc(b.gravity_label)} · ${b.pressure_psi} psi · <span class="hint">${esc(b.platform)}</span></div>
          <div class="clsame">✓ Tested at ${esc(b.matches.join(" + "))}</div>
          <div class="clbout">${esc(b.result)}</div>
          <div class="hint">Source: <a href="${esc(b.source_url)}" target="_blank" rel="noopener">${esc(b.source_ref)}</a> · “${esc(b.quote)}”</div>
        </li>`).join("")}</ul>
        <p class="hint">${esc(r.beyond_psi_limits.note)}</p>
      </div>` : ""}
      ${r.gravity_note ? `<p class="hint clgrav">${esc(r.gravity_note)}</p>` : ""}
      <button type="button" class="btn clcta" id="clgo">Close this gap: see the test campaign planner →</button>`;
    el.hidden = false;
    $("clgo").addEventListener("click", () => $("campaign").scrollIntoView({ behavior: "smooth", block: "start" }));
  }

  document.addEventListener("fl:update", load);
})();
