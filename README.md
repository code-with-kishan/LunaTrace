<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:1a1f35,100:0d2452&height=220&section=header&text=LunaTrace&fontSize=80&fontColor=c8d6f0&fontAlignY=40&desc=Subsurface%20Ice%20Detection%20%7C%20Lunar%20South%20Polar%20Region&descAlignY=60&descSize=20&animation=fadeIn" width="100%"/>

<p>
  <img src="https://img.shields.io/badge/Mission-Lunar%20South%20Pole-1a1f35?style=for-the-badge&logo=nasa&logoColor=c8d6f0"/>
  <img src="https://img.shields.io/badge/Primary%20Data-Chandrayaan--2%20DFSAR-FF6B35?style=for-the-badge&logo=satellite&logoColor=white"/>
  <img src="https://img.shields.io/badge/Sensor-L%20%26%20S%20Band%20Full--Pol-00BFFF?style=for-the-badge"/>
</p>
<p>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/MIDAS-DFSAR%20Processing-FF6B35?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/QGIS-Geospatial%20Analysis-589632?style=for-the-badge&logo=qgis&logoColor=white"/>
  <img src="https://img.shields.io/badge/LOLA%20DEM-5%20m%2Fpx-blueviolet?style=for-the-badge"/>
</p>
<p>
  <img src="https://img.shields.io/badge/OHRC-Morphology%20%26%20Hazard-orange?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/ShadowCam-PSR%20Interior-darkblue?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/ISRU-O₂%20%7C%20H₂O%20%7C%20Fuel-00BFFF?style=for-the-badge"/>
</p>

<a href="https://git.io/typing-svg">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=16&pause=1200&color=00BFFF&center=true&vCenter=true&multiline=true&repeat=true&width=820&height=80&lines=DFSAR+%E2%86%92+MIDAS+%E2%86%92+Bayesian+Ice+Map+%E2%86%92+Mission+Go%2FNo-Go;Ice+Detection+%7C+Landing+Site+%7C+Rover+Path+%7C+ISRU+Yield" alt="Typing SVG"/>
</a>

</div>

---

## What We Built

**LunaTrace** is an end-to-end geophysical pipeline that takes raw Chandrayaan-2 DFSAR radar data and produces three mission-ready outputs — a subsurface ice probability map, a scored landing site recommendation, and a simulated rover traverse — closing with a single falsifiable mission verdict backed by quantified uncertainty.

It covers the full chain from orbital radar to resource yield estimate. Every number has a source. Every result has an error bar. Every decision has a stated weight.

---

## What Makes It Different

Most approaches stop at flagging pixels where CPR > 1 and DOP < 0.13 and calling it ice. That is necessary but not sufficient — surface roughness, regolith porosity, and grain size can produce identical signatures with no ice present.

LunaTrace goes further on three fronts:

**1 — Physics before thresholds**
We build a forward scattering model first. It predicts what CPR and DOP *should* look like for a given combination of ice fraction, roughness, and incidence angle. We then invert that model against actual MIDAS outputs to produce a **Bayesian posterior probability of ice per pixel** — not a binary flag, a continuous 0–100% confidence surface.

**2 — Depth discrimination from two frequencies**
L-band (24 cm) penetrates deeper than S-band (12 cm). If L-band CPR is elevated but S-band is not, the scatterer is *below* S-band penetration depth — buried, not surface roughness. This dual-band depth argument is the strongest physical discriminant in the pipeline and is something single-frequency approaches cannot make.

**3 — The pipeline knows what it doesn't know**
Every output carries a Monte Carlo uncertainty chain. The final volume estimate comes as low / expected / high, and the dominant uncertainty source — dielectric constant, radar noise, or grain size — is named explicitly. A pipeline that reports its own confidence limits is more trustworthy than one that doesn't.

---

## Three Pillars, Equal Weight

```
┌─────────────────────┬─────────────────────┬─────────────────────┐
│   ICE DETECTION     │   LANDING SITE      │   ROVER TRAVERSE    │
│                     │                     │                     │
│  Chandrayaan-2      │  OHRC + ShadowCam   │  LOLA DEM 5 m/px   │
│  DFSAR L + S band   │  loaded in QGIS     │                     │
│  Full-Pol           │                     │  A* over 4-term     │
│                     │  Slope · Boulder    │  cost raster:       │
│  MIDAS → C2 Matrix  │  Illumination ·     │  slope + boulders   │
│  m-Delta / m-Chi    │  PSR proximity      │  thermal + comms    │
│  cpr.bin + dop.bin  │                     │                     │
│                     │  Weighted score →   │  Navigates AROUND   │
│  Bayesian posterior │  committed primary  │  hazards, not over  │
│  ice-prob map       │  site + alternates  │  them               │
└─────────────────────┴─────────────────────┴─────────────────────┘
```

---

## Pipeline at a Glance

```
ISSDC PRADAN
  └─ DFSAR L+S Full-Pol
        │
        ▼
     MIDAS
  └─ C2 Matrix → m-Delta/m-Chi
  └─ cpr.bin  dop.bin
        │
        ▼
  Forward Scattering Model (IEM/SPM grid)
  └─ roughness × ice-fraction sweep
        │
   ┌────┴────┐
   │         │
L-band    S-band
CPR/DOP   CPR/DOP
   │         │
   └────┬────┘
        │
   Dual-Band Depth Map
   (buried vs surface scatterer)
        │
        ▼
   Bayesian Posterior
   P(ice | CPR, DOP, entropy, dual-band, morphology)
        │
   ┌────┴───────────────┐
   │                    │
Ice Map            Ice Volume
(0–100% per px)    low / mid / high
                   + ISRU yield (H₂O · O₂ · H₂)
        │
   ┌────┴───────────────────────────┐
   │                                │
Landing Site Score            Rover Traverse
(OHRC + ShadowCam + QGIS)    A* on LOLA DEM
slope · boulders ·            4-term cost
illumination · ice proximity   explicit failure report
        │                          │
        └──────────┬───────────────┘
                   │
         Mission Recommendation
         Go / No-Go · stated uncertainty
         dominant constraint named
```

---

## Our Unique Innovations

### Bayesian Ice Mapping vs Naive Thresholding

| Approach | What it does | Limitation |
|---|---|---|
| Naive (CPR > 1, DOP < 0.13) | Binary ice/no-ice flag | Roughness mimics ice — false positives |
| **LunaTrace** | Continuous posterior probability per pixel | Separates ice from roughness, porosity, grain size |

### Dual-Band Depth Discrimination

| L-band CPR | S-band CPR | Interpretation |
|---|---|---|
| Elevated | Not elevated | Buried scatterer → subsurface ice candidate |
| Both elevated | Both elevated | Surface-level roughness / near-surface scattering |
| Neither elevated | Neither elevated | Dry, smooth regolith |

### 4-Term Rover Cost Function

The simulated rover does not pick the shortest path. It picks the safest one.

```
Cost = w_slope  × elevation-gain energy
     + w_boulder× obstruction probability (OHRC)
     + w_thermal× time in shadow vs min. operating temp
     + w_comms  × out-of-line-of-sight-to-lander penalty
```

If no path satisfies all four constraints, the planner reports *which* constraint is binding and proposes a staged mitigation — it does not silently return a violating path.

### End-to-End Ice-to-Resource Chain

From a radar measurement to a resource quantity:

```
Bayesian ice-fraction estimate (per pixel)
  → ice volume (m³)  low / expected / high
  → water yield (kg) = volume × 917 kg/m³ × extraction efficiency
  → O₂ yield  (kg)  = water × (32/18)
  → H₂ yield  (kg)  = water × (4/18)
  → propellant mass  = f(mission ΔV, engine Isp)
```

### In-Situ Confirmation Experiments (Beyond Detection)

Rather than stopping at orbital inference, we propose a staged verification programme:

| Stage | Experiment | What it confirms |
|---|---|---|
| 1 | Neutron spectrometry | Hydrogen abundance at depth (LPNS analog) |
| 1 | Rover-mounted GPR traverse | Subsurface dielectric interface at ice-layer depth |
| 2 | Rotary-percussive drill to 1–2 m | Physical sample — sublimation rate confirms ice vs hydrated mineral |
| 2 | TIR thermometry at drill depth | T < 110 K at ~1 m → ice present |
| 3 | Mass spectrometry on sublimate | H₂O vs CO₂ vs other volatiles — confirms water specifically |

Drill coordinates are sourced from the highest-confidence zone of the Bayesian posterior map, not selected arbitrarily.

---

## Datasets

| Dataset | Portal | Role in Pipeline |
|---|---|---|
| Chandrayaan-2 DFSAR L-band Full-Pol | [ISSDC PRADAN](https://pradan.issdc.gov.in/) | Primary ice detection — CPR, DOP, depth |
| Chandrayaan-2 DFSAR S-band Full-Pol | [ISSDC PRADAN](https://pradan.issdc.gov.in/) | Dual-frequency depth discrimination |
| Chandrayaan-2 OHRC | [ISSDC PRADAN](https://pradan.issdc.gov.in/) | Morphology, boulder density, landing candidates |
| NASA ShadowCam (KPLO) | [LROC Archive](https://www.lroc.asu.edu/shadowcam) | PSR interior imagery, albedo, shadow extent |
| LOLA DEM 5 m/pixel | [LROC QuickMap / PDS](https://quickmap.lroc.asu.edu/) | Slope, topography, rover cost raster, volume geometry |

---

## Outputs

| # | Output | Description |
|---|---|---|
| 1 | Forward-model grid | Roughness × ice-fraction prediction vs observed pixels |
| 2 | Dual-band depth map | L-only / both / neither elevated CPR — depth of ice candidate |
| 3 | Bayesian ice-probability map | 0–100% continuous, shown alongside naive-threshold baseline |
| 4 | Morphology + hazard map | OHRC lobate-rim detection, boulder density, control-region false-positive rate |
| 5 | Landing site decision | Disclosed weights, committed primary site, sensitivity on alternates |
| 6 | Rover traverse map | All four cost terms, explicit infeasibility report if any constraint violated |

**Final output format:**
> *"Given an estimated ice volume of X–Y m³ at Z% posterior confidence, dominated by [dielectric constant / radar noise / grain-size] uncertainty, with [thermal / comms / slope] as the binding traverse constraint rather than ice scarcity, a follow-up sampling mission to this site is [justified / marginal / not justified]."*

---

## Tech Stack

| Layer | Tools |
|---|---|
| SAR Processing | MIDAS (VEDAS) → cpr.bin / dop.bin |
| Geospatial | QGIS, GDAL, rasterio |
| Forward Scattering Model | Custom IEM/SPM — NumPy, SciPy |
| Bayesian Framework | scikit-learn likelihood + custom posterior |
| Traverse Planning | NetworkX A\* · 4-term cost raster |
| Uncertainty | Monte Carlo — NumPy, SciPy |
| ISRU Yield | Custom NumPy model |
| Visualisation | Matplotlib, Plotly, Streamlit dashboard |

---

## Repository Structure

```
lunatrace/
├── data/
│   ├── raw/
│   │   ├── dfsar/            # L+S band HH/HV/VH/VV + midas_outputs/
│   │   ├── ohrc/             # Georeferenced OHRC rasters
│   │   ├── shadowcam/        # PSR interior imagery
│   │   ├── dem/              # LOLA 5 m/px DEM
│   │   └── illumination/     # PSR masks, shadow persistence
│   └── processed/
│
├── src/
│   ├── radar/                # Calibration · speckle filter · polarimetry
│   ├── forward_model/        # IEM/SPM grid · depth penetration
│   ├── detection/            # Bayesian posterior · entropy check · baseline
│   ├── terrain/              # Hazard map · morphology · control-region check
│   ├── resource/             # Volume inversion · Monte Carlo · ISRU yield
│   ├── planning/             # Landing site scoring · rover A* traverse
│   └── dashboard/            # Streamlit viewer
│
├── scripts/
│   ├── run_phase1.py         # Config validation
│   ├── run_phase2.py         # Calibration + per-band polarimetry
│   ├── run_phase3.py         # Forward model + dual-band depth map
│   ├── run_phase4.py         # Bayesian posterior ice map
│   ├── run_phase5.py         # OHRC morphology + hazard map
│   ├── run_phase6.py         # Volume inversion + uncertainty
│   ├── run_phase7.py         # Landing site scoring
│   ├── run_phase8.py         # Rover traverse + failure report
│   └── run_all_phases.py
│
├── config/
│   ├── project.toml          # Site parameter (switch crater here)
│   └── assumptions.toml      # All constants with bibliographic sources
│
├── outputs/                  # Six final artifacts
├── assumptions.md
├── DATASET_GUIDE.md
├── requirements.txt
└── README.md
```

---

## Run It

```bash
git clone https://github.com/your-org/lunatrace.git
cd lunatrace
pip install -r requirements.txt

# Full pipeline
python3 scripts/run_all_phases.py

# Individual phases
python3 scripts/run_phase2.py   # Radar calibration + polarimetry
python3 scripts/run_phase4.py   # Bayesian ice map
python3 scripts/run_phase7.py   # Landing site scoring
python3 scripts/run_phase8.py   # Rover traverse

# Dashboard
streamlit run src/dashboard/app.py
```

> **Switching sites:** Update `config/project.toml → study_site`. Re-run `run_all_phases.py`. No code changes needed — the site is a parameter, not hardwired.

---

## Relevance to Future Missions

Everything LunaTrace does maps directly onto what LUPEX (ISRO + JAXA) needs to solve before it lands:

- **Orbital radar → in-situ inference** mirrors the chain LUPEX must close between Chandrayaan-2 data and its rover instruments (PRATHIMA soil sensor + onboard GPR)
- **Landing site selection near Shackleton** is still open — our resource-confidence-weighted scoring framework addresses it with disclosed, reproducible weights
- **Thermal and slope-aware traverse planning** rehearses the exact survival-margin tradeoff LUPEX faces: no active heating, 25° slope limit, battery-constrained darkness dwell
- **ISRU yield framework** provides the quantitative economic case for a follow-up extraction mission — the number LUPEX stakeholders need

---

## References

- Singh et al. — *Detection of subsurface water ice in permanently shadowed craters on the Moon using Chandrayaan-2 DFSAR data* (PRL — primary reference for Faustini F2)
- SAC/ISRO — *A software tool to process & analyse Chandrayaan-2 polarimetric dual frequency SAR data*
- SAC/ISRO — *Chandrayaan-2 DFSAR data processing using MIDAS software*
- Olhoeft & Strangway (1975) — *Dielectric properties of the first 100 metres of the Moon*
- Carrier, Olhoeft & Mendell (1991) — *Physical properties of the lunar surface*, Lunar Sourcebook
- Spudis et al. — *Evidence for water ice on the Moon: results for anomalous polar craters from LRO Mini-RF*
- NASA/GSFC — *LOLA instrument description and data products*, LRO mission documentation

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d2452,50:1a1f35,100:0d1117&height=130&section=footer&animation=fadeIn" width="100%"/>

<p>
  <img src="https://img.shields.io/badge/Practice%20Site-Faustini%20F2%20%7C%2087.2°S-1a1f35?style=flat-square"/>
  <img src="https://img.shields.io/badge/PSR-Doubly%20Shadowed-FF6B35?style=flat-square"/>
  <img src="https://img.shields.io/badge/Primary%20Instrument-DFSAR%20L%2FS%20Full--Pol-00BFFF?style=flat-square"/>
  <img src="https://img.shields.io/badge/Site%20Switch-One%20Config%20Change-brightgreen?style=flat-square"/>
</p>

*Chandrayaan-2 DFSAR · MIDAS · OHRC · ShadowCam · LOLA DEM · QGIS*

</div>
