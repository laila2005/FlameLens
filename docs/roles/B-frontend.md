# Role B: Frontend lead

**Name:** ______  **Backup:** ______  **Pairs with:** C

## Your job in one sentence

Turn the dashboard mockup into the real app: clear, fast, readable at phone width, and always honest about sample data and uncertainty.

**العربية:** [النسخة العربية](ar/B-frontend.md) · [Choose your role](00-choose-your-role.md)

## Experience needed

| | |
|---|---|
| **Required** | React and TypeScript basics, HTML and CSS, calling an API with `fetch` |
| **Nice to have** | Tailwind, Vite, responsive design, Figma, accessibility |
| **Learn in 2 days** | Tailwind, Plotly inside React |
| **Personal fit** | Good visual taste, notices small details |

## You own

App shell, habitat picker, ranked cards, Evidence case / Run this next / Safer options layout, diff view, journey view, theme, and the final look of the demo.

## Before the hackathon

### B1. Know the mockup (Mon 9 Nov, 45 min)
Open the [dashboard mockup](../links.md). Click everything. In `docs/design/ui-inventory.md` list every element and what it does: sliders, presets, cards, tabs, evidence panel, banner.
Done when: the list has at least 25 items and a teammate agrees it is complete.

### B2. Environment (Mon 9 Nov, 20 min)
Run `python scripts/check_env.py`. Make sure Node 20+ and npm work. Read the Vite and Tailwind getting-started pages.
Done when: check_env shows Node OK.

### B3. Screen designs (Tue 10 Nov, 2 hours)
Sketch on paper or Figma these screens, save images or the Figma link in `docs/design/screens/`:
1. Habitat picker with ranked list
2. Evidence case panel
3. Run this next panel
4. Safer options panel
5. A lens page
6. Diff view
7. Atmosphere journey (stages as a row)

Each screen needs four states drawn: **normal, loading, empty/no evidence, error**.
Done when: all 7 screens exist with 4 states, and C has seen them.

### B4. Design tokens (Tue 10 Nov, 45 min)
In `docs/design/tokens.md` write the colours, fonts and spacing taken from the mockup: dark navy background, flame orange, cool cyan, Sora for headings, IBM Plex Sans for text, IBM Plex Mono for numbers. Add the light-theme values.
Done when: a teammate can restyle a button from the file alone.

### B5. Component list (Wed 11 Nov, 90 min)
In `docs/design/components.md` list each React component with its props and states: `HabitatPanel`, `InvestigationCard`, `ScoreBars`, `EvidenceCase`, `StrengthGauge`, `NextExperiment`, `SaferOptions`, `LensTabs`, `EvidencePanel`, `SampleBanner`, `JourneyRow`.
Done when: every component says what data it needs (match the [API contract](../05-architecture-and-api.md)).

### B6. Library decisions (Wed 11 Nov, 45 min)
Decide: routing (probably none), state (React state is enough), Plotly wrapper (`react-plotly.js` or plain Plotly in a ref). Write the install commands to run at kickoff in `docs/design/setup-commands.md`.
Done when: you can set up the project in 10 minutes from the file.

### B7. Accessibility and phone checklist (Wed 11 Nov, 30 min)
Write 10 checks in `docs/design/ui-checks.md`: keyboard reachable, contrast, no horizontal scroll at 400px, sliders labelled, banner always visible, etc.
Done when: F can use it as part of the QA plan.

### B8. Agree interfaces with C (Thu 12 Nov, 45 min)
With C, agree the props between panels and charts, and the mock JSON for `/case`, `/next`, `/alternatives`, `/strength`. Save it as `docs/design/mock-json.md`.
Done when: you and C both sign off in the chat.

## At the hackathon

| Hour | You do |
|---|---|
| 0–2 | Read the real data field list, agree mock JSON with A |
| 2–10 | App shell, picker, ranked cards on mock data |
| 10 | Gate 1: first real cards on screen |
| 10–24 | Evidence case layout, Run this next, Safer options, diff view, weight sliders |
| 18–24 | Atmosphere journey UI (if chosen at Gate 1) |
| 24–40 | Empty, loading, error states, phone layout, risk-passport print layout |
| 40 | Freeze |

## Hand-offs

| You give | To | When |
|---|---|---|
| Component skeleton | C | Hour 4 |
| Phone-width bug list | F | Hour 30 |
| Final screenshots | F | Hour 38 |

## Rules for you

- The "sample data" banner is never hidden while placeholder rows exist.
- Never show a number without its unit and, for results, a link to its source.
- Always design the "no evidence" state first. It is our signature.
