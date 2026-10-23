/**
 * chart.js — SVG bar chart renderer
 * Used in the Overview view for the 7-day messages chart.
 */
const Chart = (() => {

  /**
   * Renders a stacked bar chart into an HTML string (SVG + legend).
   * @param {Object} opts
   * @param {string[]} opts.labels   - X-axis labels (RTL order, index 0 = oldest)
   * @param {number[]} opts.primary  - Primary series values (AI replies)
   * @param {number[]} opts.secondary - Secondary series values (human handoffs)
   * @param {string}  opts.primaryLabel
   * @param {string}  opts.secondaryLabel
   * @param {number}  opts.maxY      - Y-axis max
   * @returns {string} HTML string
   */
  function stackedBar({ labels, primary, secondary, primaryLabel, secondaryLabel, maxY = 250 }) {
    const W = 560, H = 240, L = 36, R = 8, T = 10, B = 28;
    const chartW = W - L - R;
    const chartH = H - T - B;
    const cw = chartW / labels.length;
    const bw = cw * 0.52;

    let gridLines = '';
    let bars = '';

    // Horizontal grid lines
    for (let v = 0; v <= maxY; v += 50) {
      const y = T + chartH * (1 - v / maxY);
      gridLines += `<line x1="${L}" x2="${W - R}" y1="${y}" y2="${y}" stroke="var(--line)" stroke-width="1"/>`;
      gridLines += `<text x="${L - 6}" y="${y + 4}" text-anchor="end" font-size="11" fill="var(--muted)">${v}</text>`;
    }

    labels.forEach((label, i) => {
      // Layout is RTL: index 0 drawn on the right, last index on the left
      const x = W - R - (i + 1) * cw + (cw - bw) / 2;
      const hP = chartH * primary[i] / maxY;
      const hS = chartH * secondary[i] / maxY;
      const yP = H - B - hP;
      const yS = yP - hS;
      const isLast = i === labels.length - 1;

      bars += `<rect x="${x}" y="${yP}" width="${bw}" height="${hP}" rx="3" fill="var(--accent)"/>`;
      bars += `<rect x="${x}" y="${yS}" width="${bw}" height="${hS}" rx="3" fill="var(--c2)"/>`;
      bars += `<text x="${x + bw / 2}" y="${H - 9}" text-anchor="middle" font-size="11"
                fill="${isLast ? 'var(--fg)' : 'var(--muted)'}"
                font-weight="${isLast ? 600 : 400}">${label}</text>`;

      if (isLast) {
        bars += `<text x="${x + bw / 2}" y="${yS - 5}" text-anchor="middle"
                  font-size="12" font-weight="600" fill="var(--fg)">${primary[i] + secondary[i]}</text>`;
      }
    });

    return `
      <svg viewBox="0 0 ${W} ${H}" width="100%" role="img"
           aria-label="رسم بياني للرسائل خلال آخر 7 أيام">
        ${gridLines}${bars}
      </svg>
      <div class="legend">
        <span><i style="background:var(--accent)"></i>${primaryLabel}</span>
        <span><i style="background:var(--c2)"></i>${secondaryLabel}</span>
      </div>`;
  }

  return { stackedBar };
})();
