/* "Ask the NASA reports": questions answered from NASA's own PSI documents (POST /api/ask).
   Every AI claim quotes the report word for word with file and page, and was verified on the server.
   With AI off (no key, no cached answer) the best matching passages are shown instead. */
(function () {
  const FL = window.FL;
  const esc = FL.esc;
  const $ = (id) => document.getElementById(id);
  let covered = [], seq = 0;

  const fileTitle = (f) => String(f).replace(/^PSI-\d+_(Reports|Science Documents|Presentations|Reference Data|Analyzed Data)_/, "").replace(/\.(pdf|docx|xlsx?|csv)$/i, "");
  const refText = (p) => p.page ? `page ${p.page}` : p.source_ref;

  function highlight(text, question) {
    const words = (question.toLowerCase().match(/[a-z0-9]{4,}/g) || []).filter((w) => !["what", "were", "with", "that", "this", "from", "have", "used", "does", "when", "main"].includes(w));
    let h = esc(text);
    for (const w of new Set(words)) h = h.replace(new RegExp(`\\b(${w}[a-z]*)`, "gi"), "<mark>$1</mark>");
    return h;
  }

  async function init() {
    try {
      const st = await FL.api.get("/api/library");
      covered = st.investigations;
      $("asksel").innerHTML = covered.map((i) => `<option value="${esc(i.psi_id)}">${esc(i.investigation)} (${esc(i.psi_id)}) · ${i.files.length} document${i.files.length === 1 ? "" : "s"}</option>`).join("");
      $("askstat").textContent = `${st.n_files} NASA documents · ${st.n_chunks.toLocaleString()} passages · ${covered.length} investigations`;
      await loadSuggestions();
    } catch (e) {
      $("askout").innerHTML = `<p class="err">Report library unavailable: ${esc(e.message)}</p>`;
    }
  }

  async function loadSuggestions() {
    const psi = $("asksel").value;
    try {
      const s = await FL.api.get(`/api/ask/suggestions?psi=${encodeURIComponent(psi)}`);
      $("asksug").innerHTML = s.questions.map((q) => `<button type="button" class="modchip asksugq">${esc(q)}</button>`).join("");
    } catch (e) { $("asksug").innerHTML = ""; }
  }

  function render(r) {
    const passages = (r.passages || []).map((p) => `<li><div class="askcite">${esc(fileTitle(p.source_file))} · ${esc(refText(p))}</div>
      <div class="askpass">${highlight(p.text, r.question)}…</div></li>`).join("");
    const badge = r.source === "model" || r.source === "cache"
      ? `<span class="badge src">AI answer · ${esc(r.model || "model")} · quotes verified</span>`
      : `<span class="badge ex">AI off · best matching passages</span>`;
    const claims = (r.claims || []).map((c) => `<li>
        <div class="askclaim">${esc(c.claim)}</div>
        <blockquote class="askquote">“${esc(c.supporting_quote)}”</blockquote>
        <div class="askcite">${esc(fileTitle(c.source_file))} · ${esc(c.page ? "page " + c.page : c.source_ref)} · <span class="ok">✓ quote verified on the page</span>${c.run_id_reference ? ` · <button class="runlink" data-run="${esc(c.run_id_reference)}">${esc(c.run_id_reference)}</button>` : ""}</div>
        ${c.engineering_recommendation ? `<div class="askrec">Consider: ${esc(c.engineering_recommendation)}</div>` : ""}
      </li>`).join("");
    $("askout").innerHTML = `
      <div class="askhead">${badge} <span class="hint">${esc(r.investigation)} · “${esc(r.question)}”</span></div>
      ${r.summary ? `<p class="asksum">${esc(r.summary)}</p>` : ""}
      ${claims ? `<ol class="askclaims">${claims}</ol>` : ""}
      ${r.removed_count ? `<p class="hint">${r.removed_count} claim${r.removed_count === 1 ? " was" : "s were"} removed by the verifier (quote not on the page, unverified number, or a safety verdict).</p>` : ""}
      ${passages ? `<details class="askpassages" ${claims ? "" : "open"}><summary>${claims ? "Matching passages" : "Best matching passages from the NASA documents"}</summary><ol>${passages}</ol></details>` : ""}
      <p class="hint">${esc(r.note || "")}</p>`;
  }

  async function ask(question) {
    const q = (question || $("askq").value || "").trim();
    if (q.length < 3) { $("askq").focus(); return; }
    $("askq").value = q;
    const my = ++seq;
    $("askbtn").disabled = true;
    $("askout").innerHTML = `<p class="hint">Searching ${esc($("asksel").selectedOptions[0]?.textContent || "the reports")}…</p>`;
    try {
      const r = await FL.api.post("/api/ask", { psi_id: $("asksel").value, question: q });
      if (my === seq) render(r);
    } catch (e) {
      if (my === seq) $("askout").innerHTML = `<p class="err">Could not answer: ${esc(e.message)}</p>`;
    } finally {
      if (my === seq) $("askbtn").disabled = false;
    }
  }

  $("asksel").addEventListener("change", () => { $("askout").innerHTML = ""; loadSuggestions(); });
  $("askbtn").addEventListener("click", () => ask());
  $("askq").addEventListener("keydown", (e) => { if (e.key === "Enter") ask(); });
  $("asksug").addEventListener("click", (e) => { const b = e.target.closest(".asksugq"); if (b) ask(b.textContent); });
  // picking an investigation in the explorer pre-selects it here when its documents are in the library
  $("invgrid").addEventListener("click", (e) => {
    const b = e.target.closest("[data-inv]");
    if (b && covered.some((i) => i.psi_id === b.dataset.inv) && $("asksel").value !== b.dataset.inv) {
      $("asksel").value = b.dataset.inv; $("askout").innerHTML = ""; loadSuggestions();
    }
  });
  init();
})();
