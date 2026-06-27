# Phase 1 Report

**Status:** PASS WITH WARNINGS
**Source of truth:** `Lunatrace_All_Details.pdf`

## Mission gate

Phase 1 verifies the repository scaffold and checks the workspace against the mandatory inputs in Section 14 of the PDF before any scientific implementation continues. In hackathon MVP mode, missing datasets are reported but do not stop the synthetic demo pipeline.

## Dataset verification summary

- Required DFSAR dual-band full polarimetry: incomplete
- Required MIDAS DFSAR processing outputs: missing
- Required OHRC imagery: missing
- Required ShadowCam imagery: missing
- Required DEM: missing
- Required illumination/sun-angle geometry: missing

## Evidence

- XML metadata products: 6
- L-band DFSAR metadata products: 3
- S-band DFSAR metadata products: 0
- MIDAS-derived processing outputs: 0
- Existing metadata-referenced payload files: 2
- Missing metadata-referenced payload files: 18
- OHRC imagery products: 0
- ShadowCam imagery products: 0
- DEM raster candidates: 0
- Illumination or PSR products: 0
- LOLA count-map labels: 2

### Missing metadata-referenced payloads

- `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_gri_xx_fp_hh_d18.tif` referenced by `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_gri_xx_fp_xx_d18.xml`
- `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_gri_xx_fp_hv_d18.tif` referenced by `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_gri_xx_fp_xx_d18.xml`
- `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_gri_xx_fp_vh_d18.tif` referenced by `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_gri_xx_fp_xx_d18.xml`
- `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_gri_xx_fp_vv_d18.tif` referenced by `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_gri_xx_fp_xx_d18.xml`
- `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_gri_in_fp_xx_d18.tif` referenced by `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_gri_xx_fp_xx_d18.xml`
- `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_sli_xx_fp_hh_d18.tif` referenced by `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_sli_xx_fp_xx_d18.xml`
- `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_sli_xx_fp_hv_d18.tif` referenced by `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_sli_xx_fp_xx_d18.xml`
- `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_sli_xx_fp_vh_d18.tif` referenced by `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_sli_xx_fp_xx_d18.xml`
- `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_sli_xx_fp_vv_d18.tif` referenced by `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_sli_xx_fp_xx_d18.xml`
- `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_sri_xx_fp_hh_d18.tif` referenced by `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_sri_xx_fp_xx_d18.xml`
- `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_sri_ma_fp_xx_d18.tif` referenced by `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_sri_xx_fp_xx_d18.xml`
- `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_sri_xx_fp_hv_d18.tif` referenced by `data/dataset/calibrated/20210424/ch2_sar_ncxl_20210424t153316757_d_sri_xx_fp_xx_d18.xml`

## Completed modules list

- Repository scaffolding aligned to the PDF target structure.
- Phase 1 dataset-verification entrypoint at `scripts/run_phase1.py`.
- Configured project and assumption manifests under `config/`.
- Markdown reporting outputs under `reports/phase_1/`.

## Pending tasks

- Supply the missing DFSAR payload files referenced by the existing L-band metadata.
- Supply a matching S-band DFSAR full-polarimetric acquisition for the same crater.
- Process the DFSAR acquisition in MIDAS and save the derived outputs needed for CPR and DOP analysis.
- Supply Chandrayaan-2 OHRC imagery for the crater and surrounding control terrain.
- Supply NASA ShadowCam imagery for doubly shadowed crater assessment.
- Supply a usable DEM raster, not only LOLA count-map labels.
- Supply illumination/sun-angle geometry or enough source data to derive it reproducibly.
- Replace all placeholder physical, instrument, rover, and scoring assumptions in `config/assumptions.toml` with sourced values.

## Blockers

- 18 metadata-referenced payload files are missing from disk.
- No DFSAR S-band metadata products were found.
- No MIDAS-generated DFSAR processing outputs were found (for example CPR/DOP or C2 products).
- No OHRC imagery products were found.
- No ShadowCam imagery products were found.
- No DEM raster products were found.
- No illumination, solar-geometry, or PSR-boundary products were found.

## Stop decision

Per the original mission rule, work would stop here. MVP demo mode is enabled, so later phases may continue with explicit synthetic assumptions and warnings.
