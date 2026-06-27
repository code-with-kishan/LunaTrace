# LunaTrace Assumptions

This file tracks the assumptions used by the current LunaTrace hackathon MVP.

## Status

- Mode: `demo`
- Source of truth for workflow: `Lunatrace_All_Details.pdf`
- Source of truth for science values: `config/assumptions.toml`

## Demo Assumptions In Use

- S-band DFSAR is currently represented by a synthetic proxy derived from available L-band metadata.
- OHRC imagery is currently represented by morphology and texture surrogates derived from the radar and synthetic DEM layers.
- DEM coverage is currently represented by a crater-shaped synthetic elevation field.
- Illumination and PSR support are currently represented by a synthetic rim-biased illumination model.
- Rover energy, dwell, and thermal limits are demo assumptions and must be replaced with mission-specific values later.
- The forward-scattering and Bayesian stages are MVP-grade approximations designed for a strong hackathon demo, not a final mission science product.

## Required Replacements Before Real-Data Submission

- Real DFSAR S-band products
- Real OHRC imagery
- Real DEM raster
- Real illumination or solar-geometry inputs
- Sourced dielectric, loss tangent, grain size, and instrument noise values
- Sourced rover power, thermal, and mobility values

## Why This Is Acceptable For The MVP

The current objective is to demonstrate the full end-to-end system architecture from the PDF, with all modules, artifacts, reports, and decision layers functioning coherently in a live demo. The present assumptions make that possible while keeping every substitution explicit and easy to replace later.
