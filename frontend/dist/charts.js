/* Small SVG chart helpers for FlameLens. No libraries, so the dashboard works offline. */
(function () {
  const FL = (window.FL = window.FL || {});

  FL.esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  // "nice" tick values between a and b
  function ticks(a, b, n) {
    const span = b - a;
    const raw = span / n;
    const mag = Math.pow(10, Math.floor(Math.log10(raw)));
    const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => span / s <= n) || 10 * mag;
    const out = [];
    for (let v = Math.ceil(a / step) * step; v <= b + 1e-9; v += step) out.push(+v.toFixed(6));
    return out;
  }

  /**
   * Scatter plot as an SVG string.
   * opts: points [{x, y, color, id, title}], xDomain [a,b], yDomain [a,b], xLabel, yLabel,
   *       logX (bool), xTicks, yTicks, marker {x, y, label}, box {x0, x1, y0, y1}, aria, r (radius)
   */
  FL.scatter = function (opts) {
    const W = opts.width || 640, H = opts.height || 420, L = 56, R = 18, T = 16, B = 48;
    const [x0, x1] = opts.xDomain, [y0, y1] = opts.yDomain;
    const lx = (v) => (opts.logX ? Math.log10(v) : v);
    const ly = (v) => (opts.logY ? Math.log10(v) : v);
    const X = (v) => L + ((lx(v) - lx(x0)) / (lx(x1) - lx(x0))) * (W - L - R);
    const Y = (v) => H - B - ((ly(v) - ly(y0)) / (ly(y1) - ly(y0))) * (H - T - B);
    const inX = (v) => v != null && v >= x0 && v <= x1;
    const inY = (v) => v != null && v >= y0 && v <= y1;
    let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${FL.esc(opts.aria || "chart")}">`;
    const xt = opts.xTicks || ticks(x0, x1, 7);
    const yt = opts.yTicks || ticks(y0, y1, 6);
    for (const v of xt) s += `<line class="grid" x1="${X(v)}" x2="${X(v)}" y1="${T}" y2="${H - B}"/><text x="${X(v)}" y="${H - B + 16}" text-anchor="middle">${v}</text>`;
    for (const v of yt) s += `<line class="grid" x1="${L}" x2="${W - R}" y1="${Y(v)}" y2="${Y(v)}"/><text x="${L - 8}" y="${Y(v) + 4}" text-anchor="end">${v}</text>`;
    s += `<line class="axis" x1="${L}" x2="${W - R}" y1="${H - B}" y2="${H - B}"/><line class="axis" x1="${L}" x2="${L}" y1="${T}" y2="${H - B}"/>`;
    s += `<text x="${(L + W - R) / 2}" y="${H - 8}" text-anchor="middle">${FL.esc(opts.xLabel)}</text>`;
    s += `<text transform="translate(14 ${(T + H - B) / 2}) rotate(-90)" text-anchor="middle">${FL.esc(opts.yLabel)}</text>`;
    if (opts.box) {
      const b = opts.box;
      const bx0 = X(Math.max(b.x0, x0)), bx1 = X(Math.min(b.x1, x1)), by0 = Y(Math.min(b.y1, y1)), by1 = Y(Math.max(b.y0, y0));
      if (bx1 > bx0 && by1 > by0) s += `<rect class="tolbox" x="${bx0}" y="${by0}" width="${bx1 - bx0}" height="${by1 - by0}"/>`;
    }
    const r = opts.r || 3.2;
    for (const p of opts.points) {
      if (!inX(p.x) || !inY(p.y)) continue;
      s += `<circle class="pt" data-id="${FL.esc(p.id)}" cx="${X(p.x).toFixed(1)}" cy="${Y(p.y).toFixed(1)}" r="${r}" fill="${p.color}" fill-opacity="${p.opacity ?? 0.7}"><title>${FL.esc(p.title)}</title></circle>`;
    }
    if (opts.marker && inX(opts.marker.x) && inY(opts.marker.y)) {
      const mx = X(opts.marker.x), my = Y(opts.marker.y);
      s += `<circle class="you" cx="${mx}" cy="${my}" r="9"/><line class="you" x1="${mx - 15}" x2="${mx + 15}" y1="${my}" y2="${my}"/><line class="you" x1="${mx}" x2="${mx}" y1="${my - 15}" y2="${my + 15}"/>`;
      s += `<text class="youtext" x="${Math.min(mx + 13, W - R - 80)}" y="${Math.max(my - 13, T + 12)}">${FL.esc(opts.marker.label || "your design")}</text>`;
    } else if (opts.marker) {
      s += `<text class="youtext" x="${W - R}" y="${T + 12}" text-anchor="end">your design is outside this chart</text>`;
    }
    return s + "</svg>";
  };

  /**
   * Particle-size dot plot on a log axis. rows: [{label, values: [{x, color, hollow, title}]}]
   */
  FL.sizePlot = function (rows, opts) {
    const W = 640, rowH = 34, T = 18, B = 50, L = 120, R = 18;
    const H = T + rows.length * rowH + B;
    const [x0, x1] = opts.xDomain;
    const X = (v) => L + ((Math.log10(v) - Math.log10(x0)) / (Math.log10(x1) - Math.log10(x0))) * (W - L - R);
    let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${FL.esc(opts.aria)}">`;
    for (const v of opts.xTicks) s += `<line class="grid" x1="${X(v)}" x2="${X(v)}" y1="${T}" y2="${H - B}"/><text x="${X(v)}" y="${H - B + 16}" text-anchor="middle">${v}</text>`;
    if (opts.band) s += `<rect x="${X(opts.band[0])}" y="${T}" width="${X(opts.band[1]) - X(opts.band[0])}" height="${H - B - T}" fill="rgba(255,200,74,.10)"/><text x="${X(opts.band[0]) + 4}" y="${T + 12}" style="fill:var(--amber)">${FL.esc(opts.bandLabel || "")}</text>`;
    rows.forEach((row, i) => {
      const y = T + i * rowH + rowH / 2;
      s += `<text x="${L - 10}" y="${y + 4}" text-anchor="end">${FL.esc(row.label)}</text><line class="grid" x1="${L}" x2="${W - R}" y1="${y}" y2="${y}"/>`;
      for (const v of row.values) {
        if (v.x == null) continue;
        s += `<circle cx="${X(v.x)}" cy="${y}" r="7" fill="${v.hollow ? "none" : v.color}" stroke="${v.color}" stroke-width="2.5"><title>${FL.esc(v.title)}</title></circle>`;
      }
    });
    s += `<text x="${(L + W - R) / 2}" y="${H - 10}" text-anchor="middle">${FL.esc(opts.xLabel)}</text>`;
    return s + "</svg>";
  };
})();
