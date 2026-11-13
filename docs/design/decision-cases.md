# Decision-route test cases (task A7)

Cases for `/case`, `/next`, `/alternatives` on `data/mock/runs_placeholder.csv` (20 placeholder runs). Tolerances: O2 within 6 points, pressure within 2 psi, airflow within 8 cm/s, same fuel (any matches all), same gravity. Supported = 2 or more matching runs, Weak = 1, No evidence = 0.

| Habitat | Target (O2 %, psi, cm/s, fuel, g) |
|---|---|
| ISS cabin | 21, 14.7, 10, any, 0 |
| Lunar rover | 34, 10.2, 10, solid, 0.16 |
| Mars-like | 30, 8.2, 10, any, 0.38 |

## `/case`: matching runs per condition (count and status)

| Habitat | Oxygen | Pressure | Airflow | Fuel | Gravity | Runs matching all five |
|---|---|---|---|---|---|---|
| ISS cabin | 11 Supported | 16 Supported | 13 Supported | 20 Supported | 20 Supported | **8** (PH-02-R01 to R03, PH-03-R01, R02, PH-06-R01, R02, PH-07-R01) |
| Lunar rover | 9 Supported | 4 Supported | 13 Supported | 13 Supported | **0 No evidence** | **0** |
| Mars-like | 11 Supported | 4 Supported | 13 Supported | 20 Supported | **0 No evidence** | **0** |

Expected verdict lines: ISS cabin, "5 of 5 conditions supported, 8 runs match the whole habitat". Lunar rover and Mars-like, "4 of 5 conditions supported, no run matches the whole habitat (no gravity evidence)".

## `/next`

| Habitat | Result |
|---|---|
| ISS cabin | No gap. Recommend repeating the lowest-confidence matching run (all placeholder, so any) |
| Lunar rover | Gap: gravity. Nearest run **PH-05-R01**. Change: fuel gas -> solid, gravity 0 -> 0.16 |
| Mars-like | Gap: gravity. Nearest run **PH-05-R02**. Change: gravity 0 -> 0.38 |

## `/alternatives` (oxygen partial pressure at least 10% below the target, matching fuel)

| Habitat | Target O2 partial pressure | Result (run, its partial pressure) |
|---|---|---|
| ISS cabin | 3.09 psi | PH-04-R02 (2.14), PH-04-R01 (2.65) |
| Lunar rover | 3.47 psi | PH-04-R01 (2.65), PH-04-R02 (2.14), PH-02-R01 (3.09) |
| Mars-like | 2.46 psi | PH-04-R02 (2.14) |

## What these cases prove

- A covered habitat gives a full "Supported" case. A habitat in lunar or Mars gravity gives the product's signature output, "No evidence for gravity", because every placeholder run is microgravity.
- With real data the counts will change. Keep the **structure** of these cases and rewrite the numbers once the real table is loaded.
- Evidence strength numbers are not listed: every placeholder run has confidence `placeholder`, so reliability is 0 by the formula. Test strength on real rows.
