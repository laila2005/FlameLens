# Beyond PSI: NASA sources for solids at Moon/Mars atmospheres, partial gravity, SoFIE/FLARE/FM2

Gathered 14 Nov 2026 (hour 20) by a research subagent; Olson & Ferkul 2012 Table I re-checked in the PDF. The rows used in the app are in `data/curated/beyond_psi_limits.csv`.

# FlameLens gap research: non-PSI NASA sources (2026-11-14)

All values below were read in the source text or in a rendered image of the source table. Nothing is inferred unless a row says "derived". Conversions: 1 kPa = 0.1450377 psi, 1 atm = 14.6959 psi. "Quiescent" means no forced flow (the test chamber is still air; buoyancy only), so flow is recorded as 0 (quiescent).

Definitions used by the sources:
- **MOC** (maximum oxygen concentration): the highest O2 % at which every sample (at least 3 or 5, see the source) self-extinguished within the NASA-STD-6001 Test 1 burn-length rule (less than 15.2 cm / 6 in). Above the MOC, at least one sample burned past 15.2 cm.
- **ULOI** (upward limiting oxygen index): the O2 % at which a sample passes about half the time.
- **MOC\*/ULOI\*** (reduced-gravity, Olson & Ferkul 2012): MOC\* = highest O2 % where the flame self-extinguished during the 5.18 s drop; ULOI\* = lowest O2 % where the flame survived the whole drop. These are NOT the same criteria as the 1 g MOC (the paper says so).
- **MTP** (maximum total pressure): the highest pressure in 99.8 % O2 at which all samples self-extinguished.

All NASA-STD-6001 Test 1 rows are **upward burning, quiescent, 1 g, ground test chamber (WSTF 1400 L)** unless noted.

---

## Gap 1: solids at raised O2 and/or reduced pressure

| id | material | o2_pct | pressure (source units) | pressure_psi | flow_cm_s | gravity | platform | outcome | source (citation + exact table/page) | url | quote |
|---|---|---|---|---|---|---|---|---|---|---|---|
| HIRSCH2007-NOMEX-J1 | Nomex HT90-40 fabric, single layer, J configuration | 30 | 70.1 kPa | 10.167 | 0 (quiescent) | 1 g | ground, WSTF | Burned at least 15.2 cm in 30 % O2 (fail); ULOI < 30, MOC < 30 | Hirsch, Williams, Harper, Beeson, Pedley, "Oxygen Concentration Flammability Thresholds of Selected Aerospace Materials Considered for the Constellation Program", 2nd IAASS Conf., 2007; Table 2 + Sec. 3 text, p. 2-3 | https://ntrs.nasa.gov/api/citations/20070018178/downloads/20070018178.pdf | "Nomex (an aramid) failed in 30 % oxygen in J-configuration in both single and double layers" |
| HIRSCH2007-NOMEX-J2 | Nomex HT90-40 fabric, double layer, J configuration | 30 | 70.1 kPa | 10.167 | 0 (quiescent) | 1 g | ground, WSTF | Fail at 30 % (ULOI < 30, MOC < 30) | same, Table 2 | same | "Nomex HT90-40 double layer (See Notes 3 and 4) < 30 < 30" |
| HIRSCH2007-NOMEX-15 | Nomex HT90-40 fabric, double layer, 15 deg from vertical | MOC 36 (ULOI 37.1) | 70.1 kPa | 10.167 | 0 (quiescent) | 1 g | ground, WSTF | Self-extinguished up to 36 % O2 | same, Table 2 + text p. 3 | same | "The double-layer Nomex installed at 15 degrees from vertical had an MOC of 36." |
| HIRSCH2007-LEXAN | Lexan 6006 polycarbonate, 1.6 mm | 30 | 70.1 kPa | 10.167 | 0 (quiescent) | 1 g | ground, WSTF | Fail at 30 % (ULOI < 30, MOC < 30); flame jets, melting, burning material falling | same, Table 2 | same | "Lexan® 6006 < 30 < 30 flame jets, melting, burning material falling" |
| HIRSCH2007-KYDEX | Kydex 100 PVC/PMMA alloy, 1.5 mm | MOC 33 (ULOI 34.4) | 70.1 kPa | 10.167 | 0 (quiescent) | 1 g | ground, WSTF | Self-extinguished up to 33 % O2; flame jets | same, Table 2 | same | "Kydex® 100 34.4 33 flame jets" |
| HIRSCH2007-SOLIMIDE | Solimide AC-530 polyimide foam | MOC 33 (ULOI 35.3) | 70.1 kPa | 10.167 | 0 (quiescent) | 1 g | ground, WSTF | Self-extinguished up to 33 % O2 | same, Table 2 | same | "Solimide® AC-530 (See Note 3) 35.3 33 None" |
| HIRSCH2007-ARMALON | Armalon TG4060 fluorocarbon/fiberglass fabric | > 40 (passed at 40) | 70.1 kPa | 10.167 | 0 (quiescent) | 1 g | ground, WSTF | Passed 15.2 cm criterion on 5 samples at 40 % O2 | same, Table 2, note 7 | same | "Armalon TG4060 > 40 > 40* none" |
| HIRSCH2007-CTD528 | CTD-528 graphite/epoxy laminate | 30 | 70.1 kPa | 10.167 | 0 (quiescent) | 1 g | ground, WSTF | Fail at 30 % (ULOI < 30, MOC < 30); flame jets | same, Table 2 | same | "CTD-528 (See Note 2) < 30 < 30 flame jets" |
| HIRSCH2010-NOMEX | Nomex HT90-40 fabric, 0.013 in., hemmed | MOC 25 (ULOI 28.5) at 10.2 psia; MTP 0.5 psia (ULPI 0.6) in 99.8 % O2 | 10.2 psia; 99.8 % O2 tests in psia | 10.2; 0.5 | 0 (quiescent) | 1 g | ground, WSTF | In 99.8 % O2, all samples self-extinguished only at or below 0.5 psia | Hirsch, Williams, Harper, Beeson, Ruff, Pedley, "Pressure Flammability Thresholds of Selected Aerospace Materials", ICES 2010; Table 2 (last page) | https://ntrs.nasa.gov/api/citations/20100015582/downloads/20100015582.pdf | "ULPIs and MTPs have units of psia and were determined in 99.8% oxygen" |
| HIRSCH2010-MELINEX | Melinex 515 PET film, 0.005 in. | MOC 20 (ULOI 21.2) at 10.2 psia; MTP 0.4 psia in 99.8 % O2 | 10.2 psia; psia | 10.2; 0.4 | 0 (quiescent) | 1 g | ground, WSTF | Lowest MOC and lowest MTP of the 7 materials | same, Table 2 + Sec. IV | same | "The material with the lowest MOC at 10.2 psia (Melinex 515) also had the lowest MTP." |
| HIRSCH2010-ALL7 | 7 materials (epoxy/glass, Udel P1700, Kydex 100, Solimide TA-301, Melinex 515, Nomex HT90-40, Ultem 1000) | 99.8 | 0.4 to 0.9 psia (MTP range) | 0.4-0.9 | 0 (quiescent) | 1 g | ground, WSTF | Flammable in near-pure O2 above 0.4-0.9 psia. Derived comparison (not tested at 4.3 psia): every MTP is below the 4.3 psi suit pressure | same, Abstract + Table 2 | same | "the non-metallic materials become flammable in oxygen between 0.4 and 0.9 psia" |
| HIRSCH2006-SILICONE-7 | Silicone rubber, ~1.5 mm | MOC 28 | 48.2 kPa (7 psia) | 6.991 (source: 7) | 0 (quiescent) | 1 g | ground, WSTF | Self-extinguished up to 28 % O2 at 7 psia (21 % at 14.7 psia) | Hirsch, Williams, Beeson, "Pressure Effects on Oxygen Concentration Flammability Thresholds of Materials for Aerospace Applications", J. Testing & Evaluation, 2006; Table 2 | https://ntrs.nasa.gov/api/citations/20070005041/downloads/20070005041.pdf | "Silicone 28 2.0 23 2.8 21 3.1" |
| HIRSCH2006-ZYTEL-7 | Zytel 42 nylon 6,6 | MOC 25 | 48.2 kPa (7 psia) | 6.991 (source: 7) | 0 (quiescent) | 1 g | ground, WSTF | Self-extinguished up to 25 % O2 at 7 psia | same, Table 2 | same | "Zytel 42 25 1.8 23 2.8 23 3.4" |
| HIRSCH2006-VITON-7 | Viton A fluoroelastomer | MOC 29 | 48.2 kPa (7 psia) | 6.991 (source: 7) | 0 (quiescent) | 1 g | ground, WSTF | Self-extinguished up to 29 % O2 at 7 psia | same, Table 2 | same | "Viton A 29 2.0 21 2.6 21 3.1" |
| HIRSCH2006-PTFE-7 | PTFE (Teflon TFE) | MOC 53 | 48.2 kPa (7 psia) | 6.991 (source: 7) | 0 (quiescent) | 1 g | ground, WSTF | Self-extinguished up to 53 % O2 at 7 psia | same, Table 2 | same | "PTFE 53 3.7 46 5.7 42 6.2" |
| HIRSCH2006-DELRIN-7 | Delrin polyoxymethylene | MOC 13 | 48.2 kPa (7 psia) | 6.991 (source: 7) | 0 (quiescent) | 1 g | ground, WSTF | Self-extinguished only up to 13 % O2 (burns in air) | same, Table 2 | same | "Delrin 13 0.9 12 1.5 11 1.6" |
| HARPER2017-NOMEX-H | Nomex HT90-40 hemmed, 20 cm sample | MOC 25.0 (ULOI 29.8) | 10.2 psia | 10.2 | 0 (quiescent) | 1 g | ground, WSTF | Self-extinguished up to 25 % O2 | Harper, Juarez?, Woods, Beeson, "NASA-STD-6001B Test 1 Upward Flame Propagation; Sample Length Impact on MOC Investigation", ICES-2017-509; Table 2, p. 3 (author list: check record) | https://ntrs.nasa.gov/api/citations/20170004702/downloads/20170004702.pdf | "Nomex HT 90-40 (Hemmed) ... 20 8 10.2 29.8 25.0" |
| HARPER2017-ULTEM | Ultem, 30 cm sample | MOC 23.0 (ULOI 24.5) | 10.2 psia | 10.2 | 0 (quiescent) | 1 g | ground, WSTF | Self-extinguished up to 23 % O2 | same, Table 2 | same | "Ultem ... 30 12 10.2 24.5 23.0" |
| ICES2026-PTFE | PTFE woven fabric, alone | 36 | 8.2 psia | 8.2 | 0 (quiescent) | 1 g | ground (Test 1) | Pass (less than 6 in char, no drip or melt) | Aly, Gao, Shaw, Walker, "Fire-resistant Textile Development for Exploration Vehicles with Enriched-Oxygen Cabin Environments", ICES-2026-301; Sec. II text + Fig. 1a, p. 3 | https://ntrs.nasa.gov/api/citations/20260003042/downloads/301-ICES_Paper_2026-FR-Textiles_Final_04-13-2026.pdf | "a Polytetrafluoroethylene (PTFE) woven fabric was tested at 36% O2 and passed the test" |
| ICES2026-PTFE-COTTON | PTFE woven fabric layered on cotton fabric | 36 (figure labels also show 34 and 32 Fail) | 8.2 psia | 8.2 | 0 (quiescent) | 1 g | ground (Test 1) | Fail; both layers burned through. The 34 % and 32 % Fail labels come from Fig. 1 panel labels: medium confidence on which panel is which | same, Fig. 1b + text p. 3 | same | "failed in a layup configuration with a cotton fabric as seen in Figure 1" |
| ICES2026-ARAMID | Commercial para-aramid / meta-aramid / antistatic blend fabric (crew outer garments) | 37 | 8.2 psia | 8.2 | 0 (quiescent) | 1 g | ground (Test 1) | Pass, alone and with meta-aramid zipper + PTFE thread | same, Sec. III.A.1 + Fig. 2, p. 4 | same | "the fabric passed NASA-STD-6001B Test 1 at 37% O2 individually" |
| ICES2026-PBI | 100 % PBI knit fabric (1x1 rib, next-to-skin shirt) | 48 | 8.2 psia | 8.2 | 0 (quiescent) | 1 g | ground (MOC test) | Passed MOC testing at 48 % O2 | same, Sec. III.B.4 + Fig. 4, p. 6 | same | "has passed MOC testing at 48% O2 and 8.2 psia" |
| ICES2026-PATCH | Polyester (Pellon) + polyurethane patches with fire-resistant topical treatment | 37 | 8.2 psia | 8.2 | 0 (quiescent) | 1 g | ground (Test 1) | Fail | same, Sec. III.B.5, p. 6 | same | "A fire-resistant topical treatment was applied to the existing patches; however, it did not pass Test 1" |

Notes for gap 1:
- Hirsch 2007 Table 2 says all MOCs were measured "at 70.1 kPa Total Pressures". The paper says Shuttle EVA prebreathe is "30 % oxygen at 70.1 kPa", so 70.1 kPa is the 10.2 psia condition.
- Hirsch 2006 Table 2 also has 12.4 psia and 14.7 psia columns for 11 materials (not copied here).
- Hirsch et al. 2011 (NTRS 20110008636, p. 2) adds a useful warning, not a data row: "a material with an MOC of 30% oxygen at 10.2 psia would fail NASA-STD-(I)-6001B Test 1 at 25.9% oxygen and 14.7 psia" (for at least one material).
- No source read here gives a NASA-STD-6001 result at exactly 34 % O2 / 8.2 psia for a named material. The ICES-2026 rows are at 32, 34 (layup only), 36, 37 and 48 % at 8.2 psia. SoFIE slides (NTRS 20200000361, p. 5) say: "Thin fuel sheets: few materials rated even in 1g at 34% O2, 8.2 psia".

---

## Gap 2: partial gravity (lunar, Mars) solid flammability

| id | material | o2_pct | pressure (source units) | pressure_psi | flow_cm_s | gravity | platform | outcome | source (citation + exact table/page) | url | quote |
|---|---|---|---|---|---|---|---|---|---|---|---|
| OLSON2012-MYLAR-MARS | Mylar G PET film, 5 mil, 5 cm x 15 cm, upward (concurrent buoyant) | MOC\* 17.0, ULOI\* 18.0 | 10.2 psia | 10.2 | 0 forced (buoyant only) | Mars 0.38 g | drop tower (5.18 s) + centrifuge, NASA GRC Zero-G Facility | Flame survived the drop at 18 %, went out at 17 % | Olson & Ferkul, "Evaluating Material Flammability in Microgravity and Martian Gravity Compared to the NASA Standard Normal Gravity Test", ICES 2012 (AIAA); Table I, p. 6 + text p. 4 | https://ntrs.nasa.gov/api/citations/20130010991/downloads/20130010991.pdf | "Mylar burning at the Martian-g ULOI* condition (18% O2 at 10.2 psi)" |
| OLSON2012-MYLAR-LUNAR | Mylar G PET film | MOC\* 14.1, ULOI\* 15.6 | 10.2 psia | 10.2 | 0 forced (buoyant only) | lunar (Table I; lunar data from Ferkul & Olson 2011) | drop tower + centrifuge, NASA GRC | Burned to 5.75 points lower O2 than in 1 g (1 g: ULOI 21.2, MOC 20.0) | same, Table I | same | "Lunar ULOI* 15.6 ... Lunar MOC* 14.1" (Mylar column) |
| OLSON2012-ULTEM-MARS | Ultem 1000 PEI film, 10 mil | MOC\* 21.1, ULOI\* 22.0 | 10.2 psia | 10.2 | 0 forced | Mars 0.38 g | drop tower + centrifuge | 1.7 points lower than 1 g (1 g: ULOI 23.5, MOC 23.0) | same, Table I | same | "Martian ULOI* 22.0 ... Martian MOC* 21.1" (Ultem column) |
| OLSON2012-ULTEM-LUNAR | Ultem 1000 PEI film | MOC\* 19.9, ULOI\* 21.0 | 10.2 psia | 10.2 | 0 forced | lunar | drop tower + centrifuge | 2.8 points lower than 1 g | same, Table I | same | "Lunar ΔO2 % ... -2.8" (Ultem column) |
| OLSON2012-NOMEX-MARS | Nomex HT90-40 fabric, 12 mil | MOC\* 19.0, ULOI\* 19.9 | 14.7 psia | 14.7 | 0 forced | Mars 0.38 g | drop tower + centrifuge | 3.35 points lower than 1 g (1 g: ULOI 23.5, MOC 22.1) | same, Table I | same | "Martian ΔO2 % ... -3.35" (Nomex column) |
| OLSON2012-NOMEX-LUNAR | Nomex HT90-40 fabric | MOC\* 19.9, ULOI\* 21.0 | 14.7 psia | 14.7 | 0 forced | lunar | drop tower + centrifuge | 2.35 points lower than 1 g | same, Table I | same | "Lunar ΔO2 % ... -2.35" (Nomex column) |
| OLSON2012-MYLAR-0G | Mylar G PET film | MOC\* 16.0, ULOI\* 17.0 | 10.2 psia | 10.2 | 30 (concurrent forced) | 0 g | reduced-gravity test at NASA GRC (facility not named in the text read) | 4.1 points lower than 1 g | same, Table I + Sec. III, p. 4 | same | "0g (with a concurrent flow of 30 cm/s, which is a reasonable maximum local spacecraft ventilation velocity" |
| FERKUL2026-SIBAL-AIRCRAFT | SIBAL fabric, 5 cm wide, downward (opposed) spread | 21 | 1 atm | 14.6959 | 0 forced (buoyant only) | lunar 0.165 g | parabolic flight aircraft | Steady downward spread for the whole 20 s; flame base spread rate 0.086 cm/s | Ferkul, Kralik, Liao, Johnston, "Material Flammability at Lunar and Martian Gravity", LPSC 2026 slides; p. 20-21 | https://ntrs.nasa.gov/api/citations/20260001966/downloads/Ferkul-Lunar%20and%20Planetary%20Science%20Conf%202026%20v2.pdf | "Lunar gravity: Steady, downward spread occurs for the entire 20-sec test time." |
| FERKUL2026-SIBAL-DROP | SIBAL fabric, downward | 21 (air) | 1 atm (air) | 14.6959 | 0 forced | lunar | drop tower + centrifuge | Flame base spread rate 0.11 cm/s | same, p. 21 | same | "SIBAL Lunar-g downward burning drop test with centrifuge ... Flame base spread rate in air: 0.11 cm/s" |
| FEIER2001-KIMWIPE-MARS | Kimwipes cellulose tissue, 2 cm wide, upward | 21 (air) | 0.27 atm (4.0 psia) | 3.97 (source: 4.0) | 0 forced (buoyant only) | Mars 0.38 g | NASA KC-135 aircraft | Upward flame spread observed (Fig. 3). Spread rates exist only as plots (Figs. 8-10): not copied | Feier, Shih, Sacksteder, T'ien, "Upward Flame Spread Over Thin Solids in Partial Gravity", AIAA 2001-0466; Fig. 3 caption, p. 4 | https://ntrs.nasa.gov/api/citations/20010059376/downloads/20010059376.pdf | "Martian gravity (0.38 G) 2-cm flame spread at 0.27 atm (4.0 psia)" |

Notes for gap 2:
- Olson & Ferkul 2012 say the reduced-gravity limits are conservative because flames were "becoming quite dim and shrinking at the end of the drop", and that the low-g criteria "are not the same as 1g due to time constraints in drop testing". Label these as short-duration limits.
- Feier 2001 also tested 0.10 g and 0.16 g (lunar) at 0.2 to 0.4 atm air, with 1, 2 and 4 cm samples. The flammability boundary (Fig. 6, 7) and spread rates are plots only (scanned PDF). If used, plot-read values must be low confidence.
- LPSC 2026 slide 24 states the planned exploration atmospheres: "100% O2, 4.3 psia" for suits and "8.2 psia / 34% O2, 66% N2" for HLS, lunar habitat and pressurized rover, with "Control bands are expected to allow up to 37% O2".

---

## Gap 3: SoFIE, FLARE, LUCI, FM2

| id | material | o2_pct | pressure (source units) | pressure_psi | flow_cm_s | gravity | platform | outcome | source (citation + exact table/page) | url | quote |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SOFIE-GEL-1409B | PMMA sphere, 4 cm diameter | 14.21 (at extinction) | 1.04 atm | 15.28 | 4.83 | 0 g | ISS, CIR, SoFIE insert | Extinction by quenching (inside duct) | Li, T'ien, Ferkul, Olson, Johnston, "Extinction of solid diffusion flame in microgravity: details of quenching and blowoff processes" (SoFIE-GEL); Table 1, p. 3 | https://ntrs.nasa.gov/api/citations/20240007628/downloads/GELsymposiumfinalRev1.pdf | "1 1409B quenching inside duct 4.83 128.8 3.63 14.21 1.04 0.36" |
| SOFIE-GEL-1408A | PMMA sphere, 4 cm | 14.99 | 1.06 atm | 15.58 | 34.28 | 0 g | ISS, CIR | Extinction by blowoff | same, Table 1 | same | "2 1408A blowoff inside duct 34.28 914.1 25.71 14.99 1.06 0.95" |
| SOFIE-GEL-1402C | PMMA sphere, 4 cm | 13.54 | 1.07 atm | 15.72 | 11.50 | 0 g | ISS, CIR | Extinction, intermediate mode (lowest O2 of the 5 cases) | same, Table 1 | same | "3 1402C intermediate Inside duct 11.50 306.7 8.63 13.54 1.07 0.37" |
| SOFIE-GEL-1409C | PMMA sphere, 4 cm | 20.77 | 1.03 atm | 15.14 | 0.44 | 0 g | ISS, CIR | Extinction by quenching at very low flow; flame pulsed ~15 min from 26.25 % O2 | same, Table 1 + Sec. 3.4 | same | "4 1409C quenching duct exit 0.44 11.7 0.33 20.77 1.03 0.17" |
| SOFIE-GEL-1410C | PMMA sphere, 4 cm | 14.37 | 1.07 atm | 15.72 | 49.68 | 0 g | ISS, CIR | Extinction by blowoff | same, Table 1 | same | "5 1410C blowoff duct exit 49.68 1324.8 37.26 14.37 1.07 not recorded" |
| FM2-PLAN | Synergy Pro "Navy" fabric, 2 cm x 20 cm, upward | 37, 33, 29, 25 (one test each) | 8.2 psia (+/- 0.3) | 8.2 | 0 (quiescent) | lunar (on the Moon) | CLPS lander (planned, launch late 2026) | PLANNED, no results. Expected lunar LOC 24-26 % (an expectation, not a result) | Ferkul et al., LPSC 2026 slides; p. 4 and p. 9 | https://ntrs.nasa.gov/api/citations/20260001966/downloads/Ferkul-Lunar%20and%20Planetary%20Science%20Conf%202026%20v2.pdf | "Test 1: 8.2 psia (+/- 0.3 psi), 37% O2 , balance nitrogen)" |

Notes for gap 3:
- SoFIE-GEL ISS tests used 0.2 to 80 cm/s flow and 13 to 28 % O2 at one atmosphere (abstract). Extinction values above are O2 at the moment of extinction while O2 slowly depleted. Do not treat them as "tested at a fixed atmosphere".
- SoFIE has five sub-experiments (NTRS 20200000361, p. 4): MIST (Fernandez-Pello, PMMA cylinders), SMRF (Olson, PMMA cylinders and engineering-material sheets), NCA (Miller), RTDFS (Bhattacharjee), GEL (T'ien). The same deck, p. 5 (SMRF), says "PMMA rods: NOMS = 1.4% O2" (negative oxygen margin of safety in reduced gravity) and "In reduced gravity (0g, Lunar g, Martian g), a flame can be sustained at lower O2". No MIST or SMRF numeric tables were found.
- FLARE (JAXA, Kibo SCEM): the JAXA leaflet says SCEM runs at atmospheric and low pressure with O2 "up to 45%", flow below 30 cm/s, with filter paper, PMMA, NOMEX and insulated wires. The 2018 AMS slides show MLOC vs flow curves for PMMA and NOMEX HT90-40 only as plots (parabolic flight + model). No flight numbers found.
- LUCI: no public source found under this name.
- FM2 has not flown, so it has no results yet.

---

## Best 5 rows for FlameLens

1. **OLSON2012-MYLAR-LUNAR and -MARS** (PET film, 10.2 psia, lunar and 0.38 g, drop tower + centrifuge): measured limits at 10.2 psia in partial gravity, 3.1 to 5.75 O2 points lower than 1 g. Best direct evidence for the "partial gravity is not safer than 1 g" claim.
2. **OLSON2012-ULTEM-LUNAR** (PEI, 10.2 psia, lunar): MOC\* 19.9 vs 1 g MOC 23.0 at the same pressure.
3. **HIRSCH2007-NOMEX-J1/J2** (Nomex fabric, 30 % O2, 70.1 kPa = 10.17 psi, 1 g): the cabin fabric NASA uses on ISS burned in the Moon/rover atmosphere. The 15-degree double layer self-extinguished up to 36 %.
4. **ICES2026-PTFE-COTTON vs ICES2026-ARAMID** (8.2 psia, 36-37 % O2, 1 g): closest to the 34 % / 8.2 psia exploration atmosphere. Layered fabrics failed where the single fabric passed. Aramid blend passed at 37 %.
5. **HIRSCH2010-ALL7 + HIRSCH2010-NOMEX** (99.8 % O2): all 7 cabin materials stay self-extinguishing only below 0.4 to 0.9 psia, far below the 4.3 psi suit pressure. This is the only measured link to the spacesuit row. The 4.3 psi comparison is derived, so label it.

Runner-up: HIRSCH2007-KYDEX (MOC 33 % at 10.17 psi) for a hard plastic that sits just under the 34 % mark.

---

## Leads not opened or not accessible

- Ferkul & Olson, "Zero-Gravity Centrifuge Used for the Evaluation of Material Flammability in Lunar Gravity", J. Thermophysics & Heat Transfer 25(3), 2011: paywalled. This is the original source of the lunar rows in Olson & Ferkul 2012 Table I.
- Olson, Neumann, Valletta, Ogorzaly, Owens, "Partial gravity flammability of cast PMMA rods in concurrent axial stagnation flow", Fire Safety Journal 150 (2024) 104267: paywalled; no NTRS copy found. Centrifuge drop-test extinction boundary for PMMA rods.
- James et al., SoFIE-GEL, Combustion and Flame 277 (2025) 114244: paywalled. The search summary says it covers 13 to 34 % O2 and 0.15 to 1.1 atm on ISS. That would be the SoFIE source for raised O2 and low pressure, but it was not read.
- Hirsch et al., "Pressure Effects on the Self-Extinguishment Limits of Aerospace Materials", ICES 2009, SAE 2009-01-2490 (NTRS 20090012334): MOC vs pressure, including the 17.3 psia result. Full text not opened.
- Harper et al., "Oxygen Partial Pressure and Oxygen Concentration Flammability: Can They Be Correlated?" (NTRS 20160004937): the MOC tables over 0.4 to 17.3 psia are images in the slides and could not be read.
- Sacksteder & T'ien, "Buoyant downward diffusion flame spread and extinction in partial-gravity accelerations", 25th Symp. (Int.) on Combustion, 1994: paywalled (KC-135, 0.05 to 1.0 g).
- Zhao et al., Proc. Combust. Inst. 36 (2017), SIBAL quenching boundary from ISS: paywalled.
- Takahashi et al., "Prediction of Limiting Oxygen Concentration of Thin Materials in Microgravity", Trans. JSASS 16(1): FLARE ground and parabolic-flight MLOC. The values exist only as plots in the 2018 AMS slides (https://iss.jaxa.jp/kiboexp/news/images/2018ams_flare.pdf).
- JAXA FLARE on-orbit (Kibo) results: no publication found.
- HLS/NESC "Phase 3" material flammability matrix at 8.2 psia, and the Hacopian memo ES-24-030 (July 2024): internal, not public.
- MIST (Fernandez-Pello/Gollner) ISS results: no numeric paper found. A Fire Science Show podcast discusses them only qualitatively.
- Hirsch et al. 2011 (NTRS 20110008636) Table 2: PET and PEI were tested at 10.2 psia in a GRC fixture with a hot wire. The text-extracted table is jumbled, so the rows were not copied. The page image was not checked.
