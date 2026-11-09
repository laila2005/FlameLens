# Role C: Charts and lenses

**Name:** Yasmine  **Backup:** ______  **Pairs with:** B and D

## Your job in one sentence

Make the data visible: three lenses, the coverage map, the evidence strength gauges and the campaign planner chart, each with a caption that says what it shows and a clear empty state.

**العربية:** [النسخة العربية](ar/C-charts-lenses.md) · [Choose your role](00-choose-your-role.md)

## Experience needed

| | |
|---|---|
| **Required** | Any charting library (Plotly, Matplotlib, D3, Chart.js), comfortable with axes and units |
| **Nice to have** | React, simple geometry (distances and circles), numerical thinking |
| **Learn in 2 days** | Plotly.js basics |
| **Personal fit** | Likes turning numbers into clear pictures, careful with units |

## You own

Plotly lenses 1–3, coverage gap map, Evidence case and Run-this-next chart pieces, strength gauges, campaign planner chart, confidence badges.

## Before the hackathon

### C1. Understand the science in plain words (Mon 9 Nov, 45 min)
Read the interactive [FlameLens Explained](../links.md) page, especially pressure vs oxygen. In `docs/design/c-notes.md` write 5 sentences, in your own words: what is oxygen partial pressure, what is a cool flame, why does airflow change flame speed.
Done when: F confirms the sentences are right.

### C2. Plotly practice (Tue 10 Nov, 2 hours)
Outside this repo (scratch folder or notebook) build four throwaway charts with fake numbers: (1) several lines with hover, (2) two overlapping curves with log x axis, (3) a heatmap grid with labels, (4) ellipses or shaded circles over a scatter plot with a marker you can move.
Done when: you can build the coverage-map style plot in 30 minutes without looking things up.

### C3. Lens specs (Tue 10 – Wed 11 Nov, 2 hours)
In `docs/design/lenses.md` for each lens write: purpose, x and y axes with units, the data fields it needs (see [06](../06-data-guide.md)), what the caption says, the empty state, and the fallback if data is missing.
- Lens 1: flame spread vs airflow, lines per oxygen level (BASS, BASS-II, Saffire)
- Lens 2: smoke vs dust particle size, log axis, the overlap zone (SAME, DAFT)
- Lens 3: cool-flame regime grid, oxygen vs diluent (FLEX, CFI)

Done when: D confirms the data fields can plausibly be found.

### C4. Coverage, strength and campaign specs (Wed 11 Nov, 90 min)
In `docs/design/decision-charts.md` write:
- Coverage map: axes, how "tested" is drawn (circles sized by tolerance), the user's habitat marker, the in/out message
- Strength gauge: the four parts as bars ([formula](../10-idea-brainstorm.md#1-evidence-strength-meter-must)), colours, the "not a safety rating" note
- Campaign planner chart: bars "coverage before and after N tests"
Done when: B has read it and has no questions.

### C5. Agree interfaces with B (Thu 12 Nov, 45 min)
Same session as B8: props and mock JSON for the panels. See [B](B-frontend.md).
Done when: both sign off in the chat.

### C6. Fallback plan (Thu 12 Nov, 30 min)
For each lens write the cheap fallback if data is missing: a cited text summary instead of a chart. Save in `docs/design/lenses.md`.
Done when: all three lenses have a fallback line.

### C7. Study NASA's Microgravity Tool (Tue 10 Nov, 30 min, with B)
Look at the [Microgravity Tool](../12-resources.md#2-getting-the-data-psi). In `docs/design/c-notes.md` write which charts it already offers, so our lenses add something different.
Done when: you can name two charts it has and the one thing our lenses show that it does not.

## At the hackathon (24 hours, hour 0 = Fri 13 Nov, 1:00 PM Cairo time)

| Hour | You do |
|---|---|
| 0–1 | Check lens data with D and F. Cut a lens now if the data is missing |
| 1–6 | Lens 1 on mock data, start the coverage map |
| 6 | **Gate 1:** one lens works on real data |
| 6–13 | Coverage map on real data, strength gauges, Evidence case chart parts, Lens 2 |
| 13–17 | Lens 3 only if data and time allow. Captions, empty states, confidence badges, chart screenshots |
| 17 | **Freeze** |

## Hand-offs

| You give | To | When |
|---|---|---|
| Chart components with props | B | Hour 3 and 8 |
| List of fields you still need | D | Hour 2 |
| Chart screenshots | F | Hour 16 |

## Rules for you

- Every chart shows its units and a caption.
- Plot-read and placeholder values are visibly marked.
- Never smooth or extend a curve beyond the tested range. Outside the data, show hatching and "unknown".
