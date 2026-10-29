# Pi capture samples

This active collection contains 110 full-resolution palm images from 11 capture sessions
recorded on October 12–13, 2026. The directory is dated October 15, 2026, when the
local collection was saved. It includes six subject labels and eleven sessions of ten samples.
At the user's request, one of syr's two right-hand sessions was removed from the active
collection; syr now has one right-hand session, and the collection contains eleven
subject/hand labels. The removed ZIP is preserved in a separate recoverable runtime folder.

Each original ZIP is named after its session ID and contains:

- `<session_id>/manifest.json`
- `<session_id>/sample_001/full.jpg` and `metadata.json`, through `sample_010`

`sessions.json` is the session index, including subject labels, hand, capture time,
and sample counts. Preserve the archives as the source data; extract working copies
outside this directory for analysis. `SHA256SUMS.txt` records SHA-256 checksums for
the archives and session index.

These captures are explicitly versioned at the repository owner's request. Other
local capture directories remain subject to the repository's existing ignore rules.

## Confirmed label correction (2026-10-29)

All ten images in session `20261013T111838871161Z-df3d072b` were mislabeled
`syr:left`; their corrected label is `syr:right`. See `label-corrections.json`.
This corrected session was subsequently removed from the active collection at the
user's request. Its correction record and a recoverable copy are retained as history.
Existing frozen evaluation outputs retain the data and labels used at evaluation time.
