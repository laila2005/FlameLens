# Ranker test cases (task A6)

Hand-checked cases for the ranker, to become unit tests at hour 1. Placeholder data ranges used: oxygen 21 to 40 %, pressure 10.2 to 14.7 psi, airflow 0 to 20 cm/s. **With real data, recompute the ranges from the loaded table.**

## Formula (decided 13 Nov, tune on real data)

For each factor, closeness = `1 - |target - value| / (max - min)`, clamped to 0 to 1.

| Factor | Weight | Rule |
|---|---|---|
| Oxygen | 0.35 | closeness on `o2_pct` |
| Pressure | 0.20 | closeness on `pressure_psi` |
| Airflow | 0.20 | closeness on `airflow_cm_s` |
| Fuel | 0.15 | 1 if same `fuel_state`, 0 if different, 0.5 if the user chose "any" |
| Gravity | 0.10 | 1 if same g, 0.5 if both are below 1 g (for example lunar vs microgravity), else 0 |

If a run lacks a field, drop that factor and rescale the remaining weights so they sum to 1, and show "based on N of 5 factors". Score = 100 x sum.

## The five cases

| # | Target (O2 %, psi, cm/s, fuel, g) | Run | Factor closeness (O2, psi, airflow, fuel, gravity) | Score |
|---|---|---|---|---|
| R1 | 34, 10.2, 12, gas, 0 | PH-05-R01 (34, 10.2, 12, gas, 0) | 1, 1, 1, 1, 1 | **100.0** |
| R2 | 21, 14.7, 0, solid, 0 | PH-08-R01 (40, 14.7, 0, liquid, 0) | 0, 1, 1, 0, 1 | **50.0** |
| R3 | 21, 14.7, 10, solid, 0 | PH-02-R03 (25, 14.7, airflow missing, solid, 0) | 0.789, 1, missing, 1, 1 | **90.8** (4 of 5 factors) |
| R4 | 30, 10.2, 12, solid, 0 | PH-05-R02 (30, 10.2, 12, gas, 0) | 1, 1, 1, 0, 1 | **85.0** |
| R5 | 34, 10.2, 10, solid, 0.16 | PH-04-R01 (26, 10.2, 5, solid, 0) | 0.579, 1, 0.75, 1, 0.5 | **75.3** |

## Worked arithmetic

- **R2:** 0.35 x 0 + 0.20 x 1 + 0.20 x 1 + 0.15 x 0 + 0.10 x 1 = 0.50 -> 50.0.
- **R3 (missing airflow):** O2 closeness = 1 - 4/19 = 0.789. Used weights: 0.35 + 0.20 + 0.15 + 0.10 = 0.80. Sum = 0.35 x 0.789 + 0.20 + 0.15 + 0.10 = 0.7263. Rescaled: 0.7263 / 0.80 = 0.9079 -> 90.8.
- **R4:** every factor 1 except fuel 0 -> 1 - 0.15 = 0.85 -> 85.0.
- **R5:** O2 = 1 - 8/19 = 0.579; airflow = 1 - 5/20 = 0.75; gravity 0.5. Sum = 0.35 x 0.579 + 0.20 + 0.20 x 0.75 + 0.15 + 0.10 x 0.5 = 0.2026 + 0.20 + 0.15 + 0.15 + 0.05 = 0.7526 -> 75.3.

Another person recomputes R3 and R5 before these become tests (done when they match).
