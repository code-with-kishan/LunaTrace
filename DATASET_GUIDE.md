# LunaTrace Dataset Guide

This is the exact dataset checklist needed to move LunaTrace from demo mode to a mentor-aligned hackathon submission.

## What We Need From You

### 1. Chandrayaan-2 DFSAR L-band full-pol data

Source:
- ISSDC PRADAN portal

What to download:
- L-band metadata XML
- The raster payloads referenced by that XML
- The four polarimetric channels for the same acquisition where available:
  - `HH`
  - `HV`
  - `VH`
  - `VV`
- Incidence-angle or geometry raster if supplied with the product

Minimum acceptable folder contents:

```text
data/raw/dfsar/l_band/
  <product>.xml
  <product>_hh.tif
  <product>_hv.tif
  <product>_vh.tif
  <product>_vv.tif
  <product>_incidence.tif
```

### 2. Chandrayaan-2 DFSAR S-band full-pol data

Source:
- ISSDC PRADAN portal

Why it matters:
- The mentor guidance makes it clear that DFSAR is the primary dataset for subsurface-ice detection.
- The dual-band part matters because the workflow is expected to demonstrate CPR and DOP usage on real processed DFSAR data.

What to download:
- Matching S-band metadata XML
- Matching S-band raster payloads for the same scene or same crater study area
- The same channel set where available:
  - `HH`
  - `HV`
  - `VH`
  - `VV`

### 3. MIDAS processing outputs

This is the most important workflow requirement because the mentor explicitly said the judges want to see DFSAR usage and MIDAS processing in the submission.

Required workflow:
1. Open MIDAS from VEDAS
2. Load the Chandrayaan-2 DFSAR product
3. Extract/import the product
4. Convert to a C2 matrix
5. Run the relevant decomposition or processing flow
6. Export or retain the outputs needed for CPR and DOP inspection

What I need saved from MIDAS:
- `cpr.bin`
- `dop.bin`
- C2 matrix or any intermediate files you use to derive CPR/DOP
- Any screenshots or notes proving the processing chain if you want stronger presentation material

Minimum acceptable folder contents:

```text
data/raw/dfsar/midas_outputs/
  cpr.bin
  dop.bin
  c2/
  notes/
```

### 4. Chandrayaan-2 OHRC imagery

Why it matters:
- crater morphology
- landing-site selection
- local hazard assessment

What to download:
- georeferenced OHRC image products for the chosen south-polar crater
- coverage of the crater and nearby landing terrain

Preferred formats:
- `.tif`
- `.img`
- other raster products with usable metadata

### 5. NASA ShadowCam imagery

Why it matters:
- doubly shadowed crater assessment
- visual support inside deep shadow zones where ordinary context is weak

What to download:
- one or more ShadowCam images covering the target crater or equivalent south-polar practice site

Preferred formats:
- georeferenced raster if available
- otherwise the highest-quality image plus metadata

### 6. LOLA DEM, ideally 5 m/pixel

Why it matters:
- slope and terrain safety
- landing-site assessment
- rover-path simulation
- crater and boulder hazard interpretation

What to download:
- LOLA DEM or equivalent lunar DEM raster
- 5 m/pixel if available for the selected study area

Preferred formats:
- GeoTIFF
- other DEM raster with clear metadata

### 7. Illumination / PSR / solar-geometry layers

Why it matters:
- PSR mapping
- doubly shadowed crater logic
- solar-power and survivability constraints for rover traversal

What to download if available:
- PSR masks
- shadow persistence rasters
- illumination maps
- sun-angle or solar-geometry layers

If you do not have these yet:
- we can derive a weaker proxy later, but this is not ideal for a final submission

## Folder Structure To Use

Please place the datasets like this:

```text
data/raw/
  dfsar/
    l_band/
    s_band/
    midas_outputs/
  ohrc/
  shadowcam/
  dem/
  illumination/
```

## What I Need You To Send Me Next

Please send one of these:

### Best option
- a folder tree of everything you downloaded

Use:

```bash
find data/raw -maxdepth 4 -type f | sort
```

### Also useful
- screenshots of the dataset folders
- the exact filenames
- whether each file is raster, XML, BIN, or label/metadata

## Minimum Package Needed To Start Real Integration

If you want me to start implementing the real-data pipeline immediately, I need at least:

1. DFSAR L-band real files
2. DFSAR S-band real files
3. MIDAS `cpr.bin` and `dop.bin`
4. one OHRC image
5. one ShadowCam image
6. one DEM raster

## What I Will Implement Once You Drop The Data In

After you provide the files, I can do the next step in the repo:

1. build loaders for PRADAN DFSAR products
2. ingest MIDAS CPR/DOP outputs into the pipeline
3. replace demo detection logic with data-backed CPR/DOP feature maps
4. ingest OHRC and ShadowCam for morphology and landing assessment
5. ingest LOLA DEM for slope and path planning
6. rework the landing and rover planning stages on real terrain

## Important Judge-Expectation Note

Per the mentor guidance, the final site may change during the hackathon.

That means the project should be built to:
- practice on any south-polar crater now
- switch to the announced crater later with minimal code changes

So right now, I do not need the final hackathon crater.
I need a practice site dataset package from the lunar south pole region so we can wire the workflow correctly.
