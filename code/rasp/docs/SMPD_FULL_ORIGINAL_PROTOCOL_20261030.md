# SMPD public-release full original-image evaluation — 2026-10-30

Purpose: test the current palm demo's full localization/feature/staged-matching pipeline on a larger, pose-challenging public original-image dataset, using Windows instead of the Pi. This is evaluation only; no threshold fitting, algorithm/model training, enrollment replacement, failure deletion or production deployment.

## Data selection and actual release size

Source is the dataset author's [public SMPD upload](https://www.kaggle.com/datasets/mahdieizadpanah/sapienza-university-mobile-palmprint-databasesmpd). The cited paper is Izadpanahkakhk et al., *Novel mobile palmprint databases for biometric authentication*, 2019, DOI [10.1504/IJGUC.2019.102016](https://doi.org/10.1504/IJGUC.2019.102016).

The author describes right palms of 110 participants, with ten captures per view: frontal (F), rotated frontal (RF), perspective (P), and rotated perspective (RP). These are phone originals rather than supplied ROI patches. The description says distance was adjusted for best quality; dark background and pose variation do not establish a general uncontrolled-scene or deliberately low-quality benchmark.

The actual published ZIP, inventoried completely before inference, contains **3,677 original JPEGs / 92 right-palm identities**, comprising F=920, RF=920, P=920, RP=917. There are 89 identities with 40 files and three with 39. Compared with the nominal 110 x 40 paper collection, 18 people are not present and three further frames are absent among the present people: **723 nominal files unavailable**, not merely three. The initial private protocol's `missing_nominal_members=3` denotes that latter within-release shortage; it must not be presented as the total nominal-publication shortage.

Archive compressed size is **6,365,761,274 bytes**, uncompressed **6,397,326,499 bytes**. The platform file-list API has two path aliases per basename and misleadingly lists 7,354 entries. Actual ZIP membership controls this experiment. Content hashes/duplicate metrics will further distinguish files from independent captures. Do not count aliases or repeat bytes as extra evidence.

The advertised Axon 24K alternative exposes only 360 images / 30 people in its actual public sample, so it was not substituted for a large evaluation. NTU-PI and X-Palm access requires signed agreements/application; no applications or messages were sent on the user's behalf. SMPD's public version is larger than BMPD's nominal 1,640 and the project's 169 own-device images. It is not claimed to be the unavailable full 110-person release.

## Frozen input and scoring protocol

- Inventory **every** archive image and retain its original member path, size, CRC and content SHA. Extract to opaque unique local names, preserving original bytes and avoiding Windows case/path collisions. Validate member CRC and the complete ZIP; do not use partial or broken downloads as completed data.
- Decode every photo identically with PIL and metadata-driven EXIF transpose, then RGB. This is standard orientation handling, not trying rotations and selecting a winner. All other localization preprocessing remains unchanged.
- Fixed enrollment: **F0..F4 of each of the 92 people**, 460 originals. Query every other published image: **3,217 queries**. No replacement if one of the five fails. A person lacking a complete five-frame template remains unregistered and its query failures remain in the primary end-to-end denominator.
- Use the staged `FastCCCompNetAlternateROI-v26-experimental` pipeline plus the already verified retained-FastCC-evidence repair. CompNet, weighted quality and ordinary FastCC metrics remain separate. All early .32/.08 gates, final distance=1.0/margin=0, poses, feature definitions, candidate search and best-two-of-five aggregation remain fixed. No runtime rejection file is enabled.
- Keep all successfully registered identities in **one simultaneous gallery**; do not split people into easier recognition subsets. Store and report every unsuccessful registration and every query result, including ROI errors, feature errors, wrong identities, ties/rejections and timings.
- The project code/model hashes, exact label split and decoder policy are locked before inference. No results from this public cohort may return to tuning in this experiment. Original localizer pretraining exposure is not fully established; do not claim a blind or fully independent subject-holdout result merely because the download is new to the project.

## Windows execution and scope

Windows uses the unchanged original OpenCV BF reference for descriptor correspondences; the Pi's ARM64 NEON shared library cannot load on this host. RootSIFT, ratio/mutual checks and geometric scoring logic are preserved, but this is not a claim of bit-identical ARM arithmetic or Pi latency.

The PC's memory allowance is explicitly larger: the descriptor-index guard is raised from 256MiB to 2GiB and prepared-gallery cache allowance from 256MiB to 6GiB in the isolated evaluation process. Only resource guards/cache capacity differ; all descriptors, index construction parameters, candidate lists, scores and gates are unchanged. A test constructs both indexes and verifies identical mapping, labels and KNN results below the original capacity. These allowances do not establish that the Pi can hold 92 palms or its planned roughly 40 people. Insufficient host memory stops the run rather than silently reducing the gallery.

The local export environment uses ONNX Runtime CPU, OpenCV=1 thread, PKLNet=3 threads, and the same exact PKLNet/CompNet ONNX binaries. During raw-image preparation, independent person groups are assigned to three worker processes with unchanged per-image model settings. All completed records from the initial sequential prefix, including its failures, are preserved; only remaining raw preparations are partitioned. Recognition is a single process with one complete gallery and fresh original read/decode/ROI/features for every query. No query feature/answer cache is used.

The preparatory ROI audit records **programmatic geometric validity**, not anatomical ROI correctness; there are no supplied anatomical ROI labels. Five selected enrollment captures also use the real demo feature path and their displayed ROI bytes are checked against the independent same-model audit. Per-frame features are stored privately for atomic five-frame bulk enrollment, with gallery preparation measured once separately after all registrations. This avoids repeatedly rebuilding the full gallery while offline registrations are staged; it does not count data preparation as live acquisition or claim each staged identity was immediately ready.

Recognition uses the actual local demo HTTP handler. Its client timeout is enlarged to 1,800 seconds for this evaluation, without shortening or replacing a slow algorithm path. Measured query time includes original read/hash, JPEG/EXIF handling, ROI, feature extraction, matching and loopback HTTP, excluding camera capture and external upload. Cold model/gallery ready time is reported separately. Pending simulated-payment tokens are canceled; no query is charged. Windows and parallel-preparation timings are never relabeled as Pi demo speed.

## Completeness and reporting requirements

Require 3,677 processed originals, all 460 fixed enrollment attempts and all 3,217 query outcomes before calling the run complete. Report overall and per-view correct, wrong accepted, rejected, processing failures, enrollment coverage and time distributions. Distinguish the strict unique-correct decision used by the existing evaluator from any correct-ID tie. Report duplicate counts and query/enrollment content overlap separately; repeated files are not independent generalization evidence. Capture failures remain failures, not successful rejection or correct identification.

Source code is in `tools/evaluate_raw_smpd.py`, `tools/parallel_smpd_prepare.py`, `tools/run_locked_smpd.py`; download/inventory utilities are `tools/inventory_kaggle_public.py`, `tools/inspect_public_zip.py`, and `tools/download_public_archive.py`. Private runtime is `runtime/smpd-full-20261030/`. Original photos, packed features, templates, model binaries and local example images stay outside Git. Only owned code/tests, scalar diagnostics and result documentation may be pushed.
