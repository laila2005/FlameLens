# Official challenge: Flame in Freefall

Source: https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/ , copied by the team on 13 Nov 2026 (hackathon day). The full text is below, followed by what it means for FlameLens.

## What it asks, in short

Build an **interactive, super intelligence (SI) powered, web-based dashboard** that **summarizes, ranks and interprets** NASA's microgravity combustion investigations (PSI) to deliver **fire safety insights for human space exploration**. Users may be able to:

1. Identify the investigations most relevant to fire safety in habitable crew environments: spacecraft, space stations, lunar and Martian bases, **pressurized rovers**.
2. **Extract data** that supports predictive modeling of flammability and fire scenarios.
3. Highlight research that informs next-generation fire safety controls and equipment.
4. Optionally: applications to fire safety on Earth (fine-water-mist extinguishers, smoke detection, firefighter clothing and air tanks).

Audience: professors, graduate and undergraduate students, aerospace researchers and engineers.

## Facts given in the challenge (citable)

| Fact | Value |
|---|---|
| Spacesuit atmosphere | 100 % oxygen at 4.3 psi |
| Earth sea level | 14.7 psi |
| **Moon Base and pressurized rovers** | **30 % oxygen or greater, at 10.2 psi or less** (more than 40 % more oxygen than Earth air, making materials much more flammable) |
| Highest-oxygen microgravity tests | ACME CFI-G: oxygen-nitrogen flow up to **85 % oxygen** from a spherical burner (inside-out flame) |
| Partial gravity | **No partial-gravity combustion data in PSI yet** (future: LUCI, FM2). E-FIELD Flames mimicked partial gravity with an electric field. Microgravity and normal-gravity results could **bound** intermediate gravity |
| Pillars | Prevention (ignition sources, material selection, flammability limits), detection, suppression |
| Prevention studies | BASS, BASS-II, Saffire-I, -II, -III (solid materials: fabrics, plastics) |
| Detection | SAME, SAME-R. One SAME instrument was used for dust in DAFT and DAFT-2 |
| Suppression | FLEX: dilution with carbon dioxide and helium |
| ACME BRE | Burned gaseous fuels to study materials flammability in still atmospheres |
| Hardware groups | ACME (6 experiments): gaseous flames, same modular hardware in the Combustion Integrated Rack (CIR). FLEX, FLEX-2, CFI: burning liquid droplets, Multi-user Droplet Combustion Apparatus (MDCA) in the CIR. BASS, BASS-II, SPICE, SLICE: solid and gaseous fuels, Microgravity Science Glovebox (MSG) with the SPICE fan-driven flow duct |
| Out of scope | Rockets and propellants |
| Story hooks | Artemis II smoke alarm (commander quote), Apollo 13 oxygen tank explosion, Mir oxygen generator fire, Apollo 1 oxygen-filled spacecraft fire |

Suggested attributes to display: experimental objectives; fuels, sample or burner shape and size; test conditions such as oxygen and airflow; variables (how tests in one investigation differ and how they are the same); sensors or measurement types; similarities and differences between investigations.

## What this changes in FlameLens

| Challenge point | FlameLens answer | Status |
|---|---|---|
| "SI-powered" | The AI explanation is now **Must ship** (cached, verified text; Dai) | to build |
| Rank investigations for crew environments | Ranker + Evidence case per habitat | done |
| Moon Base / pressurized rover: ≥30 % O₂, ≤10.2 psi | Presets now **sourced** from this text: Moon base 30 % at 10.2 psi, spacesuit 100 % at 4.3 psi | done in this update |
| No partial-gravity data; 0 g and 1 g bound it | Gravity condition now says "bounded by microgravity data, no partial-gravity data in PSI" instead of a bare "No evidence" | done in this update |
| Summarize and compare investigations (objectives, fuels, hardware, conditions, variables, sensors) | New **Investigations** explorer with profiles and side-by-side compare | to build |
| Extract data for predictive modeling | **Download** the curated run table (CSV) with sources | to build |
| Next-generation controls and equipment | Early-detection simulator (sensor fusion), safer options, run-this-next | done |
| Earth applications | Spin-off panel: smoke detector (smoke vs dust), firefighter clothing and air tanks, water mist | to build |

## Full text

> For decades, NASA has studied how flames and fire behave in microgravity, gathering a trove of experimental data along the way. That knowledge matters more than ever as humans gear up to return to the Moon and press on to Mars, yet the volume of results makes them hard to find, compare, and understand. Your challenge is to create an interactive, super intelligence (SI) powered dashboard that summarizes, ranks, and interprets those findings to deliver fire safety insights for human space exploration.

**Background.** Fire hazards are extremely dangerous in space exploration! In describing a smoke alarm that went off during the recent Artemis II mission, the commander commented, "[If] you want to get somebody's attention really quick, make the fire alarm go off in your spacecraft when you're still about 80,000 miles from home." Decades earlier, the Apollo 13 crew endured the life-threatening results of an oxygen tank explosion on their way to the Moon. Similarly, a multinational crew survived a fire aboard the Mir space station caused by an oxygen generator failure. In 1967, the Apollo 1 crew died in a pre-launch test when fire erupted in their oxygen-filled spacecraft.

Compared to Earth, flames in free fall (i.e., in microgravity) are often dramatically different because of the absence of buoyancy and thus rising hot gases. Instead of a flickering teardrop, a candle flame becomes a ghostly blue sphere reliant on diffusion for its oxygen.

NASA's spacecraft fire safety work is focused on prevention, detection, and suppression. Prevention is achieved by controlling ignition sources and through material selection, which depends on understanding flammability limits. To facilitate spacesuit use, an atmosphere with increased oxygen and reduced pressure compared to Earth's is expected within the planned Moon Base and pressurized rovers. Flammability is highly dependent on oxygen concentration, and air flow is also important in microgravity. Flammability studies focus on solid materials such as fabrics and plastics, as studied in the Burning and Suppression of Solids (BASS and BASS-II) and Spacecraft Fire Safety Demonstration (Saffire-I, -II, and -III) investigations.

Fire detection was tested in microgravity through the Smoke and Aerosol Measurement Experiment studies (SAME and SAME-R). Suppression was studied in the Flame Extinguishment Experiment (FLEX) through dilution of the chamber atmosphere with carbon dioxide and helium, both of which suppress fire.

**Objectives.** Results from low-gravity combustion experiments, conducted for example on the International Space Station (ISS), are being made publicly available through NASA's Physical Science Informatics (PSI) database, but the amount of data can be overwhelming. It can be hard to find, harder to compare, and harder yet to interpret.

Your challenge is to build an SI-powered, web-based dashboard that summarizes, ranks, and interprets combustion science investigations to deliver critical foundational insights for fire safety. You may consider enabling users to:

- Identify investigations most relevant to the fire safety needs of habitable crew environments, including spacecraft, space stations, bases on the lunar and Martian surfaces, and pressurized rovers.*
- Extract data that supports predictive modeling of flammability and fire scenarios in space exploration.
- Highlight research that informs the development of next-generation fire safety controls and equipment.

In this challenge, you'll help turn complex data into clear answers and make the next giant leap a safer one.

Your dashboard could also address potential applications of the PSI data to fire safety on Earth. Fine-water-mist extinguishers developed for use on the ISS have practical applications here on Earth, and NASA technology has similarly led to improvements in terrestrial smoke detection and firefighter gear, including protective clothing and air tanks.

\*Fire safety involving rockets and propellants is generally beyond the scope of the research available in the PSI database. The high velocities within rocket engines render the combustion effectively independent of gravity — although a rocket's launch is of course strongly dependent on gravity.

**Potential considerations.** You may (but are not required to) consider the following:

- Your target audience can include professors, graduate students, undergraduate students, aerospace researchers, and aerospace engineers.
- Consider how you might summarize and display attributes such as: experimental objectives; fuels, including shape and size of the samples or burners; other test conditions, such as oxygen concentration and airflow speed; variables: how did tests from the same investigation differ and how were they the same?; sensors or types of measurements.
- Consider how to summarize and display similarities and differences between different investigations.
- Other investigations in PSI: One of the instruments used for smoke detection in the SAME and SAME-R studies was instead used to detect dust in the Dust and Aerosol Measurement Feasibility Test (DAFT and DAFT-2) studies. While it burned gaseous fuels, the Burning Rate Emulator (BRE) experiment of the Advanced Combustion via Microgravity Experiments (ACME) project was a study of materials flammability in still atmospheres as a function of material properties. Other combustion investigations within the PSI database (but not explicitly referenced above) are still relevant to fire safety, just not as strongly or directly.
- Hardware: The six experiments in the ACME project featured flames of gaseous fuels and were all conducted with the same modular set of ACME hardware in the Combustion Integrated Rack (CIR). FLEX, FLEX-2, and the Cool Flames Investigation (CFI) each featured burning droplets of liquid fuel and were conducted with the Multi-user Droplet Combustion Apparatus (MDCA) in the CIR. BASS, BASS-II, the Smoke Point In Co-flow Experiment (SPICE), and the Structure & Liftoff In Combustion Experiment (SLICE) collectively featured both solid and gaseous fuels. Each of these investigations was conducted within the Microgravity Science Glovebox (MSG) using the modular fan-driven flow duct built for SPICE.
- Spacesuits and oxygen concentration: To enable flexibility, spacesuits are filled with 100% oxygen to only 4.3 psi (pounds per square inch), where the Earth's pressure at sea level is 14.7 psi. To avoid the bends (decompression sickness), the astronauts pre-breathe 100% oxygen to expel absorbed nitrogen. To reduce the pre-breathing duration and thus facilitate lunar excursions, it is expected that the Moon Base and pressurized rover(s) will be at a pressure and oxygen concentration between those in a spacesuit and the Earth's atmosphere. The intermediate oxygen concentration used on the Moon will likely be 30% or greater, with a corresponding pressure of 10.2 psi or less. Compared to Earth's atmosphere, that's more than a 40% increase in the oxygen concentration making materials much more flammable. Microgravity tests with the highest oxygen concentrations were conducted as part of the ACME's Cool Flames Investigation with Gases (CFI-G). In those tests, the combustion chamber was filled with a mixture of nitrogen and a flammable gas (e.g., propane), while an oxygen-nitrogen mixture of up to 85% oxygen flowed from the spherical burner creating an inside-out flame.
- Partial-gravity data: Although NASA is heavily focused on the return of astronauts to the Moon's surface and the establishment of a Moon Base in preparation for the future human exploration of Mars, there is currently no partial-gravity combustion data available in PSI. We expect such data will be added in the future, for example from the Lunar-g Combustion Investigation (LUCI) and the Flammability of Materials on the Moon (FM2) experiment. Partial gravity was mimicked in ACME's Electric-Field Effects on Laminar Diffusion Flames (E-FIELD Flames) experiment through the effect of the electric field on the ions that naturally occur in flames. Microgravity and normal-gravity results could bound what occurs at intermediate gravity levels.

For data and resources related to this challenge, refer to the Resources tab at the top of the page.
