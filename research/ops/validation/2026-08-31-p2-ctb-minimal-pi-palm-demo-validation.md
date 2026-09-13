# Validation Audit: 2026-08-31 P2-CTB minimal Raspberry Pi palm demo

## Decision investigated

Whether the newly available Raspberry Pi 5 (8 GB RAM, 64 GB card), official camera module, and the three archives in `code/data/` can support a **minimal local, offline palm enrollment/verification demonstration** without breaching P2-CTB's public-data/offline threat boundary or making an unsupported biometric-security claim.

## Claim under test

The proposed demo is admissible only as a benchtop interaction prototype: capture one RGB palm image locally, assess capture quality, derive a local template, compare it with a locally enrolled template, and show `match / no match / capture unsuitable`. It must neither represent a real access-control service nor assert liveness, presentation-attack resistance, cross-device robustness, identity accuracy, irreversibility, or privacy protection. P2-CTB's actual research endpoint remains offline acceptance of reconstructed presentations at a target's frozen FAR, not whether a Raspberry Pi can execute a matcher.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | The supplied Python repository is explicitly a personal study/comparison reimplementation of classic coding matchers, and already provides pairwise genuine/impostor scoring and a PolyU `P_F` benchmark. Raspberry Pi officially supports camera capture through `rpicam-*`/Picamera2. | Joining a camera capture loop to a classic matcher is normal integration work. It is useful only as an instrumented demo and P2 target-runtime measurement surface. | High collision |
| Exact-claim collision | A local register-and-match UI changes neither P2's leaked-template observation, its source-to-target device/sensor/model matrix, nor its frozen-FAR attack-acceptance endpoint. The current candidate register already marks a deployment-only edge claim as insufficient. | It can supply a clearly labelled local RGB target matcher for latency/RAM measurement after the offline protocol is frozen. | High collision |
| Boundary and impossibility | The included CASIA archive is multispectral: six wavelengths plus white; the official Camera Module 3 standard variant has an IR-cut filter and RAW10 output, not CASIA's controlled multispectral acquisition. Capture mismatch, palm pose, crop/ROI, illumination, focus and threshold calibration can dominate a result. | A capture-quality rejection state and a fixed camera/illumination/ROI protocol can make the demo honest, but cannot establish cross-sensor transfer or presentation-attack resistance. | High confidence in limitation |

## Assumption and identification audit

- [K] P2-CTB permits an optional Pi matcher demonstration only for target latency, RAM and template storage; training and attack evaluation are offline. Its public-data/offline boundary prohibits a live service.
- [KILL] A successful own-palm re-capture after enrollment establishes only that this particular camera, pose, preprocessing, user and threshold can sometimes produce a score above threshold. It does not estimate FAR, FNMR/EER, generalisation, identity accuracy, or cross-device transfer. With one enrolled identity, an apparent `match` is not a biometric-performance result.
- [KILL] Standard RGB capture is not proof of liveness or spoof resistance. ISO/IEC 30107-1:2023 defines PAD terminology but explicitly does not standardize PAD algorithms/countermeasures or provide an overall system security/vulnerability assessment. No PAD protocol, attack instruments, APCER/BPCER, or capture-device attack evaluation has been supplied.
- [KILL] Do not call a feature vector a "protected template", a hash, encrypted data, or irreversible simply because raw frames are deleted. P2's protection comparison requires a published transform plus separate linkability/reissuance and attack tests.
- [C] The exact supplied camera variant is unspecified. The official standard Camera Module 3 page documents a visible-light IMX708 with integrated IR-cut filter; if the purchased module is Camera Module 2 or a NoIR variant, capture controls and the exact observation model must be recorded before any result is compared.
- [GAP] The in-scope user may demonstrate their own palm locally only if their institution approves that collection/retention; the current charter says no personal data and requires public, de-identified data. Until the coordinator obtains explicit ethics/consent direction, the safest initial Pi demonstration is camera/ROI/quality plumbing with no persistent biometric enrollment, plus the supplied licensed public data for offline baseline work.
- [GAP] No archive contains a manifest, licence, original acquisition agreement, checksum manifest, or provenance record. Possession of an archive is not evidence of authorization to process, redistribute, publish sample images, or use it for a demo.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Li-ChengYan, `palmprint-recognition-python`, main branch inspected 2026-08-31 | A folder of already cropped/labelled images; classic coding extraction; all pairwise scores | Offline ROC/EER and deterministic PolyU `P_F` benchmark | Directly supplies an offline baseline, but no camera acquisition, palm detection, ROI localisation, enrollment store, liveness/PAD, or ARM benchmark | Kills any claim that an offline classic matcher is new; leaves a controlled Pi integration task |
| Raspberry Pi Camera software documentation, current page inspected 2026-08-31 | Supported camera modules; `rpicam-*`/libcamera; Picamera2 Python API | Camera capture integration on Raspberry Pi OS Bookworm | Capture stack only | Leaves matcher, ROI protocol and security evaluation to the project |
| Raspberry Pi Camera Module 3 product page/product brief, current page inspected 2026-08-31 | IMX708 RGB/NoIR variants, autofocus, HDR, RAW10 | Device specification | Defines the real Pi observation model | Kills treating visible-light capture as six-band CASIA imaging |
| CASIA Multi-Spectral Palmprint V1 official description, 2016 page inspected 2026-08-31 | 7,200 images, 100 people, self-designed multispectral device; local archive filename encodes left/right, 460/630/700/850/940/WHT and six repeats | Controlled multispectral benchmark; not Pi RGB live capture | Data-format/domain mismatch | Leaves it as offline multispectral baseline only, subject to access terms |
| ISO/IEC 30107-1:2023 official abstract, edition 2 | Presentation attacks at the capture device | PAD framework/terminology, not a method or system-security certification | Governs what a PAD claim would mean | Kills untested "anti-spoof" or "secure door" language |

## Strongest simple baseline

The strongest honest demo baseline is a **non-biometric camera preflight**: show live preview, fixed capture distance/lighting guide, focus lock, palm-in-frame/blur/exposure checks, and save no biometric output. For an authorised offline biometric demo, compare the selected local matcher against (1) a fixed, pre-enrolled reference image from the same approved source and (2) a clearly labelled unsuitable-capture rejection. Do not use a hand-tuned threshold from the same two images to claim verification performance. Before P2 work, the supplied repository's documented PolyU `P_F` benchmark is the minimal reproducibility baseline; it is not a live-camera baseline.

## Contrarian result

The proposed "basic palm demo" is feasible as engineering, but it is dangerous as a research or security demonstration: it could look like a door/access system while its RGB camera, one-user threshold and non-PAD matcher say nothing about an attacker using a printed/displayed/reconstructed palm. The most useful first deliverable is therefore an offline, local-only, visibly non-production prototype with an explicit `capture unsuitable` outcome and audit logs, while keeping public database experiments separate from camera images.

## Feasibility audit

### Resource inventory and data use

| Resource | Observed format/use | Licence/provenance status | Deployment admissibility |
| --- | --- | --- | --- |
| `PalmBigDataBase.zip` | 129,762,638 bytes; 7,754 archive entries. It contains `PalmBigDataBase/P_F_<identity>_<sample>.bmp`, matching the supplied Python repository's PolyU `P_F` filename parser. No licence/README/COPYING entry was found in its archive listing. | [GAP] Likely a PolyU-derived `P_F` subset, but its archive has no licence or source record. The public PolyU multispectral terms require academic/non-commercial use, agreement and acknowledgement; they do not prove this specific archive's provenance or terms. | HOLD until the provider supplies original dataset URL/agreement and intended-use confirmation. It is suitable in principle for the repo's offline benchmark, not for a live RGB Pi claim. |
| `CASIA-Multi-Spectral-PalmprintV1.rar` | 122,878,043 bytes; 7,202 archive entries (7,200 images plus directory/`Thumbs.db`). Filename sampling shows `images/<id>_<l/r>_<460/630/700/850/940/WHT>_<01..06>.jpg`. | [GAP] The archive structure matches CASIA-MS-PalmprintV1's official 7,200-image description, but the archive contains no licence/manifests. CASIA's official page identifies the database but the retrieved page did not provide a redistributable-use licence. | Use only as offline, permission-confirmed data. Do not input its NIR bands or combine its scores with Pi RGB results as the same sensor condition. |
| `palmprint-device-intro.zip` | 354,806,789 bytes; 13 entries: Word manual, PNG images and MP4 demonstrations. No source code, model files, install manifest or licence is present. | [GAP] Filename corruption in archive listing prevents even the product name from being reliably read; vendor/device rights are unknown. | Reference-only until the lab identifies the device/vendor and confirms demo reuse rights. Do not reverse-engineer or deploy it. |
| Li-ChengYan Python repository | MIT licence; Python 3.11+, NumPy, SciPy, Pillow, Matplotlib; folder-based batch score generation and benchmark. | [K] Code licence is MIT, but the README says it is a personal reimplementation and directs users to obtain dataset access from official dataset pages. Model/data authorisation remains separate. | Reasonable offline baseline candidate. It must be extended with camera capture, ROI localisation, enrolment persistence, quality gate, logging, and tests; no dependency manifest/ARM CI or Pi benchmark was found. |
| Pi 5 + official camera | Hardware is adequate for capture and classic CPU matching in principle, but board OS, camera model, cooling/power, storage headroom and exact package versions have not been observed. | [GAP] Hardware presence alone is not a passed deployment test. | Begin only with official Raspberry Pi OS Bookworm, `rpicam-hello` preflight, then Picamera2 capture. Record OS/package versions and actual latency/RAM. |

### Deployment gates

1. **Data gate:** obtain the original download/agreement URL or written confirmation from the doctoral student for each archive; record SHA-256, source, permitted use and citation. Do not redistribute or post images/videos.
2. **Ethics gate:** coordinator confirms whether a volunteer's own palm may be captured and whether template/image retention is permitted. Without it, persist no Pi palm images/templates.
3. **Camera gate:** record board revision, exact camera module/standard versus NoIR, Raspberry Pi OS release, `rpicam-hello` result, fixed distance/background/light, autofocus behaviour and image format. The standard Camera Module 3's visible-light observation model is the default assumption only.
4. **ROI/quality gate:** prove deterministic palm/ROI extraction on a small, authorised capture set; reject out-of-frame, blurred, over/underexposed or badly cropped frames. Save numeric quality diagnostics and only an allowed local sample/derived template.
5. **Matcher gate:** freeze extractor, normalisation, template serialization, comparison metric and threshold before a test session. Separate the development references from probes; report raw scores, not a security or recognition-rate claim.
6. **Scope gate:** UI must say `local offline prototype` and `not an access-control or anti-spoofing system`. Keep target Pi inference/resource measurements separate from P2's desktop/offline attack evaluation.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Pi OS Bookworm uses `rpicam-*`; Picamera2 is the supported Python interface | [K] | Raspberry Pi Documentation, "Camera software", current page, https://www.raspberrypi.com/documentation/computers/camera_software.html | "rpicam-apps" and "Use libcamera from Python with Picamera2" sections | Software-stack support, not matcher support/performance |
| Current Camera Module 3 standard hardware is 11.9 MP IMX708, 4608 x 2592, RAW10, 75-degree FoV, with integrated IR-cut filter; NoIR is a distinct variant | [K] | Raspberry Pi, "Camera Module 3" product page and product brief, current page, https://www.raspberrypi.com/products/camera-module-3/; product brief PDF, https://datasheets.raspberrypi.com/camera/camera-module-3-product-brief.pdf | "Specification" section; product-brief pp. 1-2 | Applies to Module 3; purchased variant has not been identified |
| CASIA-MS-Palmprint V1 describes 7,200 images from 100 people with a custom multispectral device | [K] | CASIA Institute of Automation, "Multispectral Palm", 2016-11-01, https://english.ia.cas.cn/db/201611/t20161101_169937.html | "1. Introduction" and "2. Brief Descriptions of the Database" | Archive structure is consistent, but not an access licence |
| CASIA data has six spectra and acquisition is contactless/unrestricted in pose | [K] | Zhang et al., "Palmprint Translation Network for Cross-Spectral Palmprint Recognition", *Electronics* 11(5):736, 2022, https://doi.org/10.3390/electronics11050736 | Sec. 2.3, "Multispectral Palmprint Dataset" | Secondary paper confirms observation mismatch; not a licence source |
| PolyU multispectral database terms reserve rights, restrict to academic/non-commercial research, require agreement and acknowledgement | [K] | PolyU Palmprint Database archived official terms, https://archive.ph/3ka1f | "The Announcement of the Copyright" and "Downloading Steps" | Specific supplied `P_F` archive provenance remains unverified |
| Supplied Python repository is a personal study/comparison reimplementation, supports folder-based baseline and `P_F` benchmark, and is MIT licensed | [K] | Li-ChengYan repository main branch, README and LICENSE, https://github.com/Li-ChengYan/palmprint-recognition-python; https://github.com/Li-ChengYan/palmprint-recognition-python/blob/main/LICENSE | README: opening notice, Requirements, Baseline, Benchmark; `baseline.py`: `compute_genuine_imposter`; `run.py`: commands | Repository was inspected 2026-08-31; it contains no camera/liveness/enrollment UI module |
| PAD terminology does not certify a method or whole-system security | [KILL] | ISO/IEC 30107-1:2023 official abstract, https://www.iso.org/standard/83828.html | Abstract, exclusions list | Standard framework; a demo needs separate PAD design/test to make such claims |
| P2's PI role is target matcher resource measurement, while its research endpoint is frozen-FAR cross-cell attack acceptance | [K] | Local project, `research/active/06-p2-ctb-prospectus.md`, current 2026-08-31 version | "Exact research question", "Minimum experiment", "Data, compute, ethics" | Governing project boundary; coordinator owns any change |

## Queries and failed searches

Queries run on 2026-08-31: `site:raspberrypi.com documentation camera software Picamera2 Raspberry Pi OS Bookworm libcamera 2026`; `site:raspberrypi.com products camera module 3 autofocus HDR Raspberry Pi official specifications`; `CASIA Multi-Spectral Palmprint Image Database Version 1 license terms official`; `Palm Big Data Base palmprint dataset license official`; `palmprint presentation attack detection RGB camera liveness limitation ISO 30107 official`; `PolyU Palmprint Database P_F license official`.

Failed/unresolved: no original source, EULA, contact or licence text was located inside either data archive; no downloadable code/model was included with the device-demo archive; no evidence identifies the purchased camera variant; no ARM64/Pi 5 benchmark, camera ROI pipeline, liveness/PAD protocol, or calibrated target FAR exists in the supplied resources. These are [GAP] findings, not evidence that the components are unavailable.

## Decision

**HOLD.** Permit only a narrowly labelled local/offline engineering prototype after the data and ethics gates. Do not let it count as P2-CTB validation, biometric security, liveness/PAD, or production authentication evidence. Advance to a persistent enrollment/verification demo only when the coordinator has recorded data permission, collection approval (if any), camera variant and a deterministic ROI/quality preflight; retain the offline public-data benchmark as the separate P2 research path.
