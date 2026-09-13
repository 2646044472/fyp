---
topic: macau-open-data-visual-asset-audit
created: 2026-09-05
last_verified: 2026-09-05
status: superseded
depth: medium
sources:
  - url: https://data.gov.mo/DownLoad
    fetched: 2026-09-05
  - url: https://api.data.gov.mo/datadir/search/download
    fetched: 2026-09-05
---

# Macao Open-Data Visual Research Asset Audit

## Decision investigated

Could Macao's government open-data platform provide a permission-clear,
repeated visual dataset with independent outcomes that would support a new
edge-camera FYP without a field partner?

## Retrieval

The public catalogue download endpoint returned a 1,377-row dataset catalogue
on 2026-09-05. The catalogue includes open structured data for real-time
weather, UV, tropical-cyclone signals, water-quality results, ecological-zone
species, waste and facilities locations, among other government statistics and
geospatial tables.

A keyword audit over titles and descriptions for `image`, `photo`, `camera`,
`webcam`, `video`, `CCTV` and Chinese equivalents returned one item only:
the list of businesses participating in the One Account "My Photos" service.
It is a JSON business list, not image data. No catalogue row provided a public
continuous image stream, CCTV frames, field-photo collection or image/outcome
pair.

## Result

- [K] Macao open data supplies useful contextual or auxiliary numerical data.
- [KILL] It does not currently supply the visual episodes and independent
  outcomes required to anchor a camera reliability/detection paper.
- [KILL] Weather or water-quality tables cannot be paired post hoc with an
  unrelated camera stream and called image-level ground truth.

## Disposition

**KILL as a standalone research asset.** Do not claim a Macao camera dataset
or use the open-data platform to manufacture an image-label task. Reopen only
if an official catalogue update provides permission-clear repeated imagery
linked to a declared outcome.
