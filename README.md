<div align="center">

<!-- HEADER BANNER -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:1a1f35,100:0d2452&height=220&section=header&text=LunaTrace&fontSize=80&fontColor=c8d6f0&fontAlignY=40&desc=Lunar%20Subsurface%20Ice%20Detection%20%7C%20South%20Polar%20Region&descAlignY=60&descSize=20&animation=fadeIn" width="100%"/>

<!-- BADGES ROW 1 -->
<p>
  <img src="https://img.shields.io/badge/Mission-Lunar%20South%20Pole-1a1f35?style=for-the-badge&logo=nasa&logoColor=c8d6f0"/>
  <img src="https://img.shields.io/badge/Primary%20Data-Chandrayaan--2%20DFSAR-FF6B35?style=for-the-badge&logo=satellite&logoColor=white"/>
  <img src="https://img.shields.io/badge/Sensor-L%20%26%20S%20Band%20Full--Pol-00BFFF?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Status-Active%20Research-brightgreen?style=for-the-badge"/>
</p>

<!-- BADGES ROW 2 -->
<p>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/MIDAS-DFSAR%20Processing-FF6B35?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/QGIS-Landing%20Site%20Assessment-589632?style=for-the-badge&logo=qgis&logoColor=white"/>
  <img src="https://img.shields.io/badge/LOLA%20DEM-5%20m%2Fpx%20Topography-blueviolet?style=for-the-badge"/>
</p>

<!-- BADGES ROW 3 -->
<p>
  <img src="https://img.shields.io/badge/OHRC-Morphology%20%26%20Hazard-orange?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/ShadowCam-Doubly%20Shadowed%20Craters-darkblue?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Ice%20Extraction-O₂%20%7C%20H₂O%20%7C%20Fuel-00BFFF?style=for-the-badge"/>
</p>

---

<!-- ANIMATED TYPING EFFECT -->
<a href="https://git.io/typing-svg">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=17&pause=1200&color=00BFFF&center=true&vCenter=true&multiline=true&repeat=true&width=800&height=100&lines=DFSAR+%E2%86%92+MIDAS+%E2%86%92+CPR+%2B+DOP+%E2%86%92+Bayesian+Ice+Map+%E2%86%92+Mission+Go%2FNo-Go;Ice+Detection+%7C+Landing+Site+Assessment+%7C+Rover+Path+Planning;Faustini+F2+Practice+Site+%7C+Switches+to+Final+Crater+on+Announcement" alt="Typing SVG" />
</a>

</div>

---

## Table of Contents

- [Overview](#-overview)
- [Three Equal Pillars](#-three-equal-pillars)
- [How We Are Doing This — End to End](#-how-we-are-doing-this--end-to-end)
  - [Pillar 1 — Ice Detection via DFSAR + MIDAS](#pillar-1--ice-detection-via-dfsar--midas)
  - [Pillar 2 — Landing Site Assessment via OHRC + ShadowCam + QGIS](#pillar-2--landing-site-assessment-via-ohrc--shadowcam--qgis)
  - [Pillar 3 — Rover Path Planning via LOLA DEM](#pillar-3--rover-path-planning-via-lola-dem)
- [Scientific Architecture (Deep)](#-scientific-architecture-deep)
- [Innovative Experiments — Ice Confirmation, Extraction & Utilisation](#-innovative-experiments--ice-confirmation-extraction--utilisation)
- [Datasets](#-datasets)
- [MIDAS Processing — Step by Step](#-midas-processing--step-by-step)
- [QGIS Workflow](#-qgis-workflow)
- [Detection Pipeline](#-detection-pipeline)
- [Landing Site Scoring](#-landing-site-scoring)
- [Rover Traverse Planning](#-rover-traverse-planning)
- [Output Artifacts](#-output-artifacts)
- [Repository Structure](#-repository-structure)
- [Tech Stack](#-tech-stack)
- [Installation & Usage](#-installation--usage)
- [Assumptions & Uncertainty](#-assumptions--uncertainty)
- [Future Scope](#-future-scope)
- [Relevance to LUPEX](#-relevance-to-lupex)
- [References](#-references)

---

## 🌑 Overview

**LunaTrace** is a full-stack geophysical inference system for detecting, quantifying, and characterising subsurface water-ice within doubly shadowed craters at the lunar south pole. The current practice site is **Faustini F2**, selected based on anomalous CPR/DOP signatures identified in the published PRL study of nine candidate south-polar craters. The pipeline is designed to switch to any announced crater with minimal code change — the site is a parameter, not hardwired.

This system does not simply threshold a radar number against the published CPR > 1, DOP < 0.13 rule and call it ice. It builds a **forward scattering model** that first predicts what the radar *should* look like given assumed physics, inverts that model against real dual-band **Chandrayaan-2 DFSAR** measurements processed through **MIDAS**, and produces a **Bayesian posterior probability of ice** per pixel — separating ice from roughness, porosity, and grain-size effects that produce identical naive signatures.

It then uses that ice map to drive **landing site assessment** from OHRC + ShadowCam loaded in QGIS, **topographic rover path planning** from LOLA DEM, and closes with a **falsifiable single-sentence mission recommendation**.

> **On site ice detection:** The methodology and correct adopted steps are what matter scientifically. A south-polar crater that does not meet the high-CPR / low-DOP threshold is itself a valid, documented result — the pipeline reports and interprets that outcome rather than treating it as a failure.

---

## ⚖️ Three Equal Pillars

LunaTrace treats ice detection, landing site assessment, and rover path planning with **equal analytical weight**. Each pillar has its own dedicated dataset, dedicated software, dedicated outputs, and dedicated section of the final presentation.

```
┌───────────────────────┬───────────────────────┬───────────────────────┐
│   ICE DETECTION       │  LANDING SITE ASSESS. │  ROVER PATH PLANNING  │
│                       │                       │                       │
│  Chandrayaan-2 DFSAR  │  OHRC + ShadowCam     │  LOLA DEM 5 m/pixel   │
│  L-band + S-band      │  loaded in QGIS       │  + OHRC hazard layer  │
│  Full-Pol             │                       │                       │
│                       │  Slope, boulder,      │  A* path over DEM     │
│  Processed in MIDAS   │  illumination,        │  4-term cost:         │
│  → C2 Matrix          │  shadow extent,       │  slope + boulders +   │
│  → m-Delta / m-Chi    │  PSR proximity        │  thermal + comms      │
│  → cpr.bin + dop.bin  │                       │                       │
│                       │  Weighted score per   │  Explicit infeasibility│
│  CPR > 1 + DOP < 0.13 │  candidate site       │  report if no safe    │
│  + Bayesian posterior │  committed primary    │  path exists          │
└───────────────────────┴───────────────────────┴───────────────────────┘
```

---

## 🔧 How We Are Doing This — End to End

### Pillar 1 — Ice Detection via DFSAR + MIDAS

**What DFSAR is and why it is the primary dataset**

The Dual Frequency Synthetic Aperture Radar (DFSAR) aboard Chandrayaan-2 is the only spaceborne instrument currently providing full-polarimetric radar coverage of the lunar south pole at two wavelengths simultaneously — L-band (~24 cm wavelength) and S-band (~12 cm wavelength). Radar penetrates regolith to a depth that optical imaging cannot reach. Ice buried beneath a dry regolith layer produces a characteristic **volume scattering signature** — it scatters energy back across multiple polarisation channels in a pattern that differs from bare rock or rough terrain. The two key derived products that capture this are:

- **CPR (Circular Polarisation Ratio):** Ratio of same-sense to opposite-sense circular polarisation backscatter. Ice-bearing volumes produce CPR > 1 because subsurface volume scattering depolarises the signal. Rough bare rock can also produce elevated CPR, which is why CPR alone is insufficient.
- **DOP (Degree of Polarisation):** Measures how polarised the returning signal is. Subsurface scattering reduces polarisation coherence — ice candidates show DOP < 0.13 alongside elevated CPR.

Using both together, and across two bands that penetrate to different depths, provides a genuine physical argument for *buried* ice rather than *surface* roughness.

**How the data flows**

```
ISSDC PRADAN portal
  → Download DFSAR product (L-band + S-band full-pol .zip)
  → Extract: HH / HV / VH / VV .tif + incidence-angle raster + metadata .xml

MIDAS software (from VEDAS)
  → Import product → Extract → Convert to C2 Matrix (CP/DP mode)
  → PROCESS → Decomposition → m-Delta / m-Chi (CP)
  → Window Size = 3 → Execute
  → Outputs: cpr.bin, dop.bin (loaded in MIDAS left panel)
  → Inspect pixel values: high CPR + low DOP = ice candidate zone

Python pipeline (this repo)
  → Ingest cpr.bin + dop.bin as rasters
  → Apply forward scattering model (IEM/SPM grid)
  → Apply Bayesian posterior framework
  → Output: ice-probability map (0–100%, continuous)
```

**Why both L-band and S-band matter**

L-band penetrates significantly deeper into regolith than S-band under typical lunar dielectric loss assumptions. If L-band CPR is elevated but S-band CPR is not, the scattering source is likely *below* the S-band penetration depth — a buried scatterer, consistent with subsurface ice rather than surface frost or rough rock. This dual-band depth argument is the strongest discriminant in the entire detection chain.

---

### Pillar 2 — Landing Site Assessment via OHRC + ShadowCam + QGIS

**What OHRC contributes**

The Orbiter High Resolution Camera (OHRC) on Chandrayaan-2 provides panchromatic imagery at approximately 25 cm/pixel resolution — sufficient to resolve metre-scale boulders, crater rims, and surface texture anomalies. In LunaTrace it is used for:

- **Morphology corroboration:** Lobate rim structures and crater-floor texture anomalies consistent with ice-influenced ejecta (matching the PRL paper's F2 figures) are detected and cross-checked against a control region with similar boulder density but no PSR status. This gives the morphology layer a stated false-positive rate rather than an assumed one.
- **Boulder density mapping:** Object detection on OHRC provides the boulder hazard layer fed into both the landing site score and the rover cost raster.
- **Landing candidate delineation:** Flat, low-slope, low-boulder zones adjacent to the PSR are identified as candidate landing ellipses.

**What ShadowCam contributes**

NASA's ShadowCam (aboard Korea Pathfinder Lunar Orbiter, KPLO) is the only camera with sufficient sensitivity to image inside permanently shadowed regions — using scattered and reflected light from crater walls and the broader terrain. In LunaTrace it is used to:

- Visually confirm the extent and character of the doubly shadowed zone inside Faustini F2
- Assess albedo variations within the PSR that may indicate surface frost or compositional heterogeneity
- Provide a sanity check on the PSR boundary derived from the LOLA DEM illumination model

**How QGIS is used**

All georeferenced raster products — OHRC, ShadowCam, LOLA DEM, CPR/DOP rasters from MIDAS, PSR masks, and illumination layers — are co-registered and visualised in **QGIS** (open-source geospatial software, qgis.org). QGIS loads all these formats natively without pre-conversion. The workflow:

```
QGIS layers loaded:
  1. LOLA DEM (slope shading + contours)
  2. OHRC imagery (boulder + morphology overlay)
  3. ShadowCam (PSR interior)
  4. CPR raster (from MIDAS output, georeferenced)
  5. DOP raster (from MIDAS output, georeferenced)
  6. PSR mask (derived from DEM)
  7. Illumination map

Outputs from QGIS:
  → Candidate landing ellipses (manual + automated)
  → Boulder density polygons
  → Hazard-excluded zones
  → Slope safety layer (< 15° threshold)
  → Final landing site decision figure
```

---

### Pillar 3 — Rover Path Planning via LOLA DEM

**What the LOLA DEM provides**

The Lunar Orbiter Laser Altimeter (LOLA) aboard the Lunar Reconnaissance Orbiter provides global lunar topography. At **5 m/pixel** resolution, the DEM resolves individual craters, boulder clusters, and slope changes relevant to rover mobility. In LunaTrace it is used to:

- Derive a slope raster (first spatial derivative) — hard constraint: slopes > 15° excluded
- Simulate terrain energy cost for rover climbing
- Compute line-of-sight visibility from lander to rover along candidate paths
- Derive illumination geometry for PSR boundary and solar-charging zone mapping
- Provide the terrain grid over which the A* path search runs

**How the rover path is simulated**

The rover path is a **simulated traverse**, not a mission-executed path. It is computed by A* search over a cost raster derived from the LOLA DEM and OHRC hazard layers, subject to four simultaneous constraints:

```
Cost = w_slope  × (elevation-gain energy per segment)
     + w_boulder × (boulder obstruction probability)
     + w_thermal × (time in PSR vs. minimum operating temperature)
     + w_comms   × (out-of-LOS-to-lander penalty)
```

The rover navigates **safely around craters and boulders** rather than across them. If no path satisfies all constraints, the planner reports which constraint is binding — it does not silently return a violating path.

---

## 🔬 Scientific Architecture (Deep)

### Forward Radar Model — Inference Before Inversion

The naive pipeline goes: raw backscatter → CPR/DOP threshold → ice verdict. The problem is that **high CPR does not uniquely mean high ice fraction** — surface roughness, regolith porosity, and grain size all push CPR in the same direction independently.

LunaTrace reverses the order. Using a **small-perturbation / Integral Equation Method (IEM)-style** surface scattering formulation:

```
CPR_predicted = f(ice_fraction, roughness, incidence_angle, dielectric_contrast)
DOP_predicted = g(ice_fraction, roughness, incidence_angle, dielectric_contrast)
```

A lookup grid is swept across plausible `(roughness, ice_fraction)` combinations. Each observed pixel is matched against the **family of parameter combinations** that could produce it, not a single threshold. The second frequency band and morphology layer narrow that family — the grid point where L-band, S-band, and morphology evidence all converge becomes the posterior ice-fraction estimate for that pixel.

### Dual-Frequency Depth Discrimination

| Signal Pattern | Physical Interpretation |
|---|---|
| L-band CPR elevated, S-band CPR not elevated | Buried scatterer below S-band penetration depth → subsurface ice candidate |
| Both L-band and S-band CPR elevated | Near-surface or surface-level roughness / scattering |
| S-band only elevated | Shallow thin scattering layer → lower confidence for substantial deposit |
| Neither elevated | Consistent with dry, smooth regolith at this site |

Penetration depth per band is computed from the regolith loss tangent sourced from Apollo and LCROSS literature — not asserted generically.

### Bayesian Ice-Probability Framework

The published ISRO/PRL baseline (CPR > 1, DOP < 0.13) is the **starting prior**, not the final answer:

```
P(ice | CPR, DOP, entropy, dual-band ratio, morphology)
  ∝ P(CPR, DOP, entropy, dual-band ratio, morphology | ice) × P(ice)
```

Each feature contributes a quantified likelihood term. The entropy term's **information value is demonstrated**, not assumed — if entropy does not shift the posterior, that null result is reported as a legitimate scientific finding.

### End-to-End Uncertainty Propagation

```
Radar measurement noise (calibration + speckle residual)
  ↓  Monte Carlo resampling
CPR / DOP / entropy uncertainty
  ↓  forward-model grid lookup uncertainty
Ice-fraction uncertainty (per pixel)
  ↓  depth assumption + dielectric constant uncertainty
Ice-volume uncertainty  →  low / expected / high range
  ↓
Water-yield uncertainty
```

The **dominant uncertainty contributor** is identified by name in every run: for example *"the volume range is dominated by dielectric-constant uncertainty, not radar noise."*

---

## 🧪 Innovative Experiments — Ice Confirmation, Extraction & Utilisation

Beyond detection and site selection, LunaTrace proposes a staged experimental programme for **confirming** subsurface ice in-situ, **extracting** it, and **converting** it into mission-critical resources.

### Stage 1 — In-Situ Confirmation Experiments

| Experiment | Instrument / Method | What It Confirms |
|---|---|---|
| **Neutron Spectrometry** | Epithermal neutron flux suppression (LPNS analog) | Hydrogen abundance consistent with H₂O-ice at depth |
| **Ground Penetrating Radar (GPR)** | Rover-mounted GPR traverse over high-CPR zones | Subsurface dielectric interface at predicted ice-layer depth |
| **Drill + Sample Return** | Rotary-percussive drill to 1–2 m | Direct physical sample; sublimation rate in vacuum confirms ice vs. hydrated mineral |
| **TIR Thermometry** | Thermal infrared sensor on rover arm | Temperature at drilled depth vs. expected frost-point — ice present if T < 110 K at ~1 m |
| **Mass Spectrometry on sublimate** | Heated chamber + residual gas analyser | Confirms H₂O vapour vs. CO₂ vs. other volatiles in the sublimate |

Each proposed experiment is cross-referenced against the detection pipeline: the drill target coordinates are sourced from the Bayesian posterior map's highest-confidence zone, not selected arbitrarily.

### Stage 2 — Ice Extraction Concepts

```
Confirmed ice zone (from Stage 1)
        │
        ▼
┌───────────────────────────────────────────┐
│  THERMAL EXTRACTION                       │
│  Resistive or microwave heating of        │
│  regolith at depth → sublimation of H₂O  │
│  vapour → cold-trap condensation in an   │
│  adjacent collection vessel               │
└────────────────┬──────────────────────────┘
                 │
        ┌────────▼────────┐
        │  COLLECTED H₂O  │
        └────────┬────────┘
                 │
    ┌────────────┼─────────────┐
    │            │             │
    ▼            ▼             ▼
 Potable     Electrolysis   Cryogenic
 water for   → H₂ + O₂     storage
 crew use    (fuel cell /   for propellant
             life support)  production
```

### Stage 3 — Resource Utilisation Pathways

| Resource | Process | Application |
|---|---|---|
| **Water (H₂O)** | Direct collection from cold trap | Crew hydration, radiation shielding, soil processing |
| **Oxygen (O₂)** | Water electrolysis (H₂O → H₂ + O₂) | Life support breathable atmosphere; oxidiser for propellant |
| **Hydrogen (H₂)** | Water electrolysis | Fuel cell energy storage; potential rocket propellant component |
| **Rocket Propellant** | Liquefied H₂ + O₂ cryo storage | In-situ propellant production for lunar ascent / deep-space stages |
| **Thermal Regulation** | Ice as passive thermal mass | Crater-rim habitat thermal buffer |

**Yield estimate framework:**

The LunaTrace volume inversion (low / expected / high range) feeds directly into a yield calculation:

```
Water yield (kg) = ice_volume (m³) × ice_density (917 kg/m³) × extraction_efficiency (%)
O₂ yield (kg)    = water_yield × (32/18)   [from electrolysis stoichiometry]
H₂ yield (kg)    = water_yield × (4/18)
Propellant mass  = f(mission ΔV requirement, engine Isp)
```

Extraction efficiency is stated as an assumption (30–70% range for thermal extraction in vacuum, sourced from ISRO/NASA ISRU literature) rather than asserted as a fixed number.

---

## 📡 Datasets

| Dataset | Source Portal | Role |
|---|---|---|
| **Chandrayaan-2 DFSAR L-band Full-Pol** | [ISSDC PRADAN](https://pradan.issdc.gov.in/) | Primary ice detection — CPR, DOP, entropy |
| **Chandrayaan-2 DFSAR S-band Full-Pol** | [ISSDC PRADAN](https://pradan.issdc.gov.in/) | Dual-frequency depth discrimination |
| **Chandrayaan-2 OHRC** | [ISSDC PRADAN](https://pradan.issdc.gov.in/) | Morphology, boulder hazard, landing candidate |
| **NASA ShadowCam (KPLO)** | [LROC ShadowCam Archive](https://www.lroc.asu.edu/shadowcam) | PSR interior visual, albedo, shadow extent |
| **LOLA DEM 5 m/pixel** | [NASA PDS / LROC QuickMap](https://quickmap.lroc.asu.edu/) | Slope, topography, rover path, volume geometry |

### DFSAR Folder Structure After Download

```
data/raw/
├── dfsar/
│   ├── l_band/
│   │   ├── <product>.xml
│   │   ├── <product>_hh.tif
│   │   ├── <product>_hv.tif
│   │   ├── <product>_vh.tif
│   │   ├── <product>_vv.tif
│   │   └── <product>_incidence.tif
│   ├── s_band/
│   │   ├── <product>.xml
│   │   ├── <product>_hh.tif
│   │   ├── <product>_hv.tif
│   │   ├── <product>_vh.tif
│   │   └── <product>_vv.tif
│   └── midas_outputs/
│       ├── cpr.bin
│       ├── dop.bin
│       └── c2/
├── ohrc/
├── shadowcam/
├── dem/
└── illumination/
```

---

## ⚙️ MIDAS Processing — Step by Step

**MIDAS** (Multi-temporal Imagery Data Analysis System) is the official SAC/ISRO software for Chandrayaan-2 DFSAR data analysis, distributed via [VEDAS](https://vedas.sac.gov.in/).

```
Step 1 ─ Setup
  Download MIDAS from VEDAS portal
  Launch midas.bat

Step 2 ─ Load Data
  Download Chandrayaan-2 DFSAR product from PRADAN portal
  Import into MIDAS → File → Open Product

Step 3 ─ Extract & Convert
  Extract the product in MIDAS
  Convert to C2 Matrix  →  CP/DP mode

Step 4 ─ Decompose
  PROCESS → Decomposition → m-Delta / m-Chi (CP)
  Select the C2 Matrix as input
  Set Window Size = 3
  Execute

Step 5 ─ Outputs
  MIDAS generates:  cpr.bin   dop.bin
  Open both from the left panel

Step 6 ─ Inspect
  Review pixel values spatially
  High CPR (> 1) + Low DOP (< 0.13) → ice candidate zone
  Note: site may or may not meet this criterion — the methodology is what matters

Step 7 ─ Export
  Export cpr.bin and dop.bin as georeferenced rasters
  Feed into Python pipeline for Bayesian analysis
```

**Key MIDAS reference papers (findable via Google Scholar):**
- *A software tool to process & analyse Chandrayaan-2 polarimetric dual frequency SAR data*
- *Chandrayaan-2 DFSAR data processing using MIDAS software*

---

## 🗺️ QGIS Workflow

QGIS (free, open-source — [qgis.org](https://qgis.org)) is used for all geospatial visualisation and landing site assessment. All product types from PRADAN, LROC, and PDS load natively.

```
Layer stack in QGIS (bottom to top):
  1. LOLA DEM             → slope shading, contour overlay
  2. OHRC orthorectified  → high-res surface texture
  3. ShadowCam            → PSR interior imagery
  4. CPR raster           → georeferenced MIDAS output
  5. DOP raster           → georeferenced MIDAS output
  6. PSR mask             → derived from DEM illumination
  7. Illumination map     → solar geometry layer
  8. Ice-probability map  → from Python Bayesian pipeline

Analysis done in QGIS:
  → Candidate landing ellipse delineation
  → Slope safety filter (< 15°)
  → Boulder exclusion zones
  → PSR proximity measurement to candidate sites
  → Cross-overlay of CPR anomaly with morphology features
  → Final annotated landing-site map export
```

---

## 🧊 Detection Pipeline

```
┌────────────────────────────────────────────────────────────────────┐
│                          RAW INPUT                                 │
│   DFSAR L-band (HH/HV/VH/VV) + S-band (HH/HV/VH/VV)             │
│   + Incidence-angle raster from PRADAN product                    │
└──────────────────────────┬─────────────────────────────────────────┘
                           │
                   ┌───────▼────────┐
                   │  Calibration   │
                   │  Speckle Filter│ ← Refined Lee, 5×5 window
                   └───────┬────────┘
                           │
             ┌─────────────┴─────────────┐
             │                           │
     ┌───────▼───────┐           ┌───────▼───────┐
     │  L-band        │           │  S-band        │
     │  Polarimetry   │           │  Polarimetry   │
     │  CPR / DOP /   │           │  CPR / DOP /   │
     │  Entropy / α   │           │  Entropy / α   │
     └───────┬───────┘           └───────┬───────┘
             │                           │
             └─────────────┬─────────────┘
                           │
             ┌─────────────▼─────────────┐
             │   FORWARD SCATTERING MODEL │
             │   IEM/SPM parameter grid   │
             │   roughness × ice-fraction │
             └─────────────┬─────────────┘
                           │
             ┌─────────────▼─────────────┐
             │  DUAL-BAND DEPTH MAP       │
             │  L-only / Both / S-only    │
             │  elevated CPR regions      │
             └─────────────┬─────────────┘
                           │
             ┌─────────────▼─────────────┐
             │  BAYESIAN POSTERIOR        │
             │  P(ice | CPR, DOP,         │
             │    entropy, dual-band,     │
             │    morphology)             │
             └─────────────┬─────────────┘
                           │
             ┌─────────────▼─────────────┐
             │  OHRC MORPHOLOGY CHECK     │
             │  Lobate-rim detection      │
             │  Control-region false-pos  │
             │  rate stated explicitly    │
             └─────────────┬─────────────┘
                           │
             ┌─────────────▼─────────────┐
             │  ICE VOLUME INVERSION      │
             │  low / expected / high     │
             │  + dominant uncertainty    │
             │  source named              │
             └─────────────┬─────────────┘
                           │
                    ┌──────▼──────┐
                    │  POSTERIOR  │
                    │  ICE MAP    │
                    │ + BASELINE  │
                    │ COMPARISON  │
                    └─────────────┘
```

---

## 🛬 Landing Site Scoring

Candidate sites are scored using a **disclosed weighted sum**:

```
Score = w₁·(illumination_safety) + w₂·(slope_safety)
      + w₃·(boulder_safety)      + w₄·(ice_proximity)
```

**Weight rationale:** Terrain safety (w₁ + w₂ + w₃) is weighted above ice proximity (w₄) because a mission that cannot land safely never reaches the ice. Exact weight values are in `assumptions.md` with one-paragraph justification.

| Input | Source |
|---|---|
| Slope raster | LOLA DEM 5 m/pixel (first-derivative) |
| Boulder density | OHRC object detection |
| Illumination suitability | Solar geometry + PSR mask from DEM |
| Ice confidence proximity | Bayesian posterior ice-probability map |
| Shadow zone extent | ShadowCam albedo + LOLA illumination |

One site is **committed to** as the primary recommendation. Alternates are shown only as sensitivity notes — how much weight would need to shift to change the ranking.

---

## 🤖 Rover Traverse Planning

### Four-Term Cost A* Search

| Cost Term | Source Data | Constraint Type |
|---|---|---|
| **Slope / Energy** | LOLA DEM slope raster | Soft — elevation gain scaled by rover mass + motor efficiency |
| **Boulder Hazard** | OHRC boulder density | Soft — probability of obstruction per segment |
| **Thermal / Darkness Dwell** | PSR mask + thermal model | **Hard** — time in shadow vs. min. operating temperature |
| **Communication Visibility** | LOLA DEM line-of-sight to lander | **Hard** — blind segments flagged as non-traversable unless relay present |

### Rover navigates around hazards

The simulated rover path goes **around** craters and boulder clusters, not across them. The OHRC hazard map and LOLA DEM crater polygons are combined into a traversability mask. Cells with slope > 15° or boulder density above threshold are excluded from the search graph entirely.

### Explicit Failure Reporting

```
If A* finds no path satisfying all constraints simultaneously:

  REPORT: "No feasible path exists.
           Binding constraint: [thermal / battery / comms / slope]
           Closest path exceeds thermal limit by N minutes.
           Proposed mitigation: staged traverse with sunlit
           rest stop at [coordinates] before entering PSR."
```

This is the most scientifically honest output the planner can produce — it distinguishes *ice not present* from *ice present but operationally unreachable under current rover assumptions*.

---

## 📦 Output Artifacts

| # | Artifact | Description |
|---|---|---|
| 1 | **Forward-Model Grid** | Roughness/ice-fraction prediction grid with observed pixels overlaid |
| 2 | **Dual-Band Depth Map** | L-only / both / S-only elevated CPR — the depth dimension of the ice candidate |
| 3 | **Bayesian Posterior Ice Map** | 0–100% continuous probability map alongside naive-threshold baseline |
| 4 | **Morphology + Hazard Map** | OHRC lobate-rim detection + control-region false-positive rate |
| 5 | **Landing Site Decision Figure** | Disclosed weights, committed site, sensitivity notes on alternates |
| 6 | **Rover Traverse Map** | All four cost terms, explicit infeasibility report if any constraint violated |

**Closing statement format:**

> *"Given an estimated ice volume of X–Y m³ at Z% posterior confidence, dominated by [dielectric constant / radar noise / grain-size] uncertainty, and a round-trip traverse cost of W Wh against a dwell/thermal limit of T minutes, with [thermal / comms / slope] binding rather than ice scarcity, a follow-up sampling mission to this site is [justified / marginal / not justified]."*

---

## 🗂️ Repository Structure

```
lunatrace/
│
├── data/
│   ├── raw/
│   │   ├── dfsar/
│   │   │   ├── l_band/          # HH HV VH VV + incidence .tif
│   │   │   ├── s_band/          # HH HV VH VV .tif
│   │   │   └── midas_outputs/   # cpr.bin  dop.bin  c2/
│   │   ├── ohrc/                # Georeferenced OHRC rasters
│   │   ├── shadowcam/           # ShadowCam imagery
│   │   ├── dem/                 # LOLA 5 m/pixel DEM
│   │   └── illumination/        # PSR masks, shadow persistence
│   └── processed/               # Calibrated, filtered outputs
│
├── src/
│   ├── radar/
│   │   ├── calibration.py
│   │   ├── speckle_filter.py
│   │   └── polarimetry.py       # CPR, DOP, entropy — per band
│   ├── forward_model/
│   │   ├── scattering_model.py  # IEM/SPM parameter grid
│   │   └── depth_penetration.py # L vs S penetration depth calc
│   ├── detection/
│   │   ├── bayesian_posterior.py    # P(ice | features)
│   │   ├── feature_value_check.py  # entropy information-value test
│   │   └── baseline_comparison.py  # naive threshold vs full map
│   ├── terrain/
│   │   ├── hazard_map.py
│   │   └── morphology.py        # + control-region false-pos check
│   ├── resource/
│   │   ├── volume_inversion.py  # forward-model-grid-based
│   │   ├── uncertainty_chain.py # end-to-end Monte Carlo
│   │   └── isru_yield.py        # H₂O / O₂ / H₂ yield estimates
│   ├── planning/
│   │   ├── landing_site.py      # disclosed weighted scoring
│   │   └── rover_traverse.py   # 4-term A*, failure reporting
│   └── dashboard/
│       └── app.py               # Streamlit viewer over figures
│
├── scripts/
│   ├── run_phase1.py   # Gate + config validation
│   ├── run_phase2.py   # Calibration + per-band polarimetry
│   ├── run_phase3.py   # Forward model + dual-band depth map
│   ├── run_phase4.py   # Bayesian posterior ice map
│   ├── run_phase5.py   # OHRC morphology + hazard map
│   ├── run_phase6.py   # Volume inversion + uncertainty chain
│   ├── run_phase7.py   # Landing site scoring
│   ├── run_phase8.py   # Rover traverse A* + failure report
│   └── run_all_phases.py
│
├── config/
│   ├── project.toml         # Pipeline mode flags
│   └── assumptions.toml     # All sourced science constants
│
├── outputs/                 # Six final artifacts
├── assumptions.md           # Every placeholder resolved with source
├── DATASET_GUIDE.md         # Exact download checklist
├── requirements.txt
└── README.md
```

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Tools |
|---|---|
| **SAR Processing** | MIDAS (VEDAS) → cpr.bin / dop.bin |
| **Geospatial Visualisation** | QGIS (open-source) |
| **Raster I/O** | GDAL, rasterio |
| **Forward Scattering Model** | Custom IEM/SPM (NumPy, SciPy) |
| **Bayesian Framework** | scikit-learn (naive Bayes / logistic likelihood) |
| **Traverse Planning** | NetworkX A\* / custom 4-term cost raster |
| **Uncertainty Propagation** | Monte Carlo (NumPy, SciPy) |
| **ISRU Yield Model** | Custom (NumPy) |
| **Visualisation** | Matplotlib, Plotly |
| **Dashboard** | Streamlit |
| **Numerical Core** | NumPy, SciPy, Pandas |

</div>

---

## 🚀 Installation & Usage

```bash
# Clone the repository
git clone https://github.com/your-org/lunatrace.git
cd lunatrace

# Install Python dependencies
pip install -r requirements.txt
```

```bash
# Run individual phases
python3 scripts/run_phase1.py   # Repository gate + config validation
python3 scripts/run_phase2.py   # Radar calibration + per-band polarimetry
python3 scripts/run_phase3.py   # Forward model grid + dual-band depth map
python3 scripts/run_phase4.py   # Bayesian posterior ice-probability map
python3 scripts/run_phase5.py   # OHRC morphology + terrain hazard map
python3 scripts/run_phase6.py   # Volume inversion + uncertainty chain
python3 scripts/run_phase7.py   # Landing site weighted scoring
python3 scripts/run_phase8.py   # Rover traverse A* + failure report

# Run the full pipeline end-to-end
python3 scripts/run_all_phases.py

# Launch the results dashboard
streamlit run src/dashboard/app.py
```

> **Site switching:** The practice site is Faustini F2. When the final crater is announced, update `config/project.toml → study_site` and re-run `run_all_phases.py`. No code changes are required — the pipeline is parameterised, not hardwired.

---

## 📐 Assumptions & Uncertainty

All physical constants are in `config/assumptions.toml` and cross-referenced in `assumptions.md`. Every value carries its bibliographic source — none is presented as derived when it was assumed.

| Constant | Source |
|---|---|
| Regolith dielectric constant | Olhoeft & Strangway (1975); Carrier et al. (1991) |
| Regolith loss tangent | Apollo/LCROSS regolith literature |
| Grain size for mixing model | Regolith simulant characterisation literature |
| DFSAR NESZ / radiometric noise | DFSAR instrument paper / ISSDC documentation |
| Rover mass & motor efficiency | Pragyan-class analog reference |
| Rover battery & power draw | Stated reference class |
| Minimum safe operating temperature | Stated electronics specification |
| Maximum safe darkness dwell time | Derived from thermal model |
| Extraction efficiency (ISRU) | ISRO/NASA ISRU literature, 30–70% range |
| Landing site scoring weights | Team-chosen; justified in `assumptions.md` |

---

## 🔭 Future Scope

- **ML backscatter regressor:** Trained model for backscatter-to-dielectric-property mapping once larger labelled datasets exist — mirroring MLP-based approaches from related Faustini Rim A research
- **Full volumetric radiative transfer:** Replacing the single-scattering forward model with complete volumetric RT
- **Regional comparative mapping:** Full pipeline generalised across all nine doubly-shadowed PRL candidates
- **GPR integration:** Ground-penetrating-radar equivalent data from future surface missions
- **3D digital twin:** Visualisation sequenced after science validation, not before
- **ISRU pilot plant design:** Engineering design for thermal extraction apparatus sized from the LunaTrace ice-volume estimate

---

## 🚀 Relevance to LUPEX

LUPEX's core objective — detecting and quantifying water-ice using PRATHIMA (soil composition) and a dedicated GPR for in-situ confirmation — is methodologically identical to what LunaTrace rehearses:

- **Detection + corroboration + depth discrimination** from orbital radar mirrors the orbital-to-surface inference chain LUPEX must close between Chandrayaan-2 data and its rover instruments
- **Landing-site selection near Shackleton crater** remains open for the JAXA/ISRO team; a framework tying site choice to a disclosed, weighted resource-confidence score addresses this directly
- **Energy / thermal / slip-aware traverse planning** directly rehearses the tradeoff LUPEX will face: passive insulating mechanism (no active heating) + 25° slope capability sets the same survival-margin boundary LunaTrace models
- **ISRU yield framework** maps directly onto LUPEX's mission justification — the economic and life-support case for a follow-up extraction mission

---

## 📚 References

- Singh et al. — *Detection of subsurface water ice in permanently shadowed craters on the Moon using Chandrayaan-2 DFSAR data* (PRL study — primary reference for Faustini F2)
- Olhoeft & Strangway (1975) — *Dielectric properties of the first 100 metres of the Moon*
- Carrier, Olhoeft & Mendell (1991) — *Physical properties of the lunar surface*, in Lunar Sourcebook
- Spudis et al. — *Evidence for water ice on the Moon: results for anomalous polar craters from the LRO Mini-RF imaging radar*
- SAC/ISRO — *Chandrayaan-2 DFSAR instrument technical documentation*
- SAC/ISRO — *A software tool to process & analyse Chandrayaan-2 polarimetric dual frequency SAR data*
- SAC/ISRO — *Chandrayaan-2 DFSAR data processing using MIDAS software*
- Nozette et al. — *The Clementine bistatic radar experiment*
- NASA/GSFC — *LOLA instrument description and data products*, LRO mission documentation

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d2452,50:1a1f35,100:0d1117&height=130&section=footer&animation=fadeIn" width="100%"/>

<p>
  <img src="https://img.shields.io/badge/Practice%20Site-Faustini%20F2%20%7C%2087.2°S-1a1f35?style=flat-square"/>
  <img src="https://img.shields.io/badge/PSR%20Status-Doubly%20Shadowed-FF6B35?style=flat-square"/>
  <img src="https://img.shields.io/badge/Primary%20Instrument-DFSAR%20L%2FS%20Full--Pol-00BFFF?style=flat-square"/>
  <img src="https://img.shields.io/badge/Site%20Switch-On%20Announcement-brightgreen?style=flat-square"/>
</p>

*Chandrayaan-2 DFSAR · MIDAS · OHRC · ShadowCam · LOLA DEM · QGIS*

</div>
