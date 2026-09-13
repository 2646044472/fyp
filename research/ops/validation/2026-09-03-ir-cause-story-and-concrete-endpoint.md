# Validation Audit: 2026-09-03 IR-CAUSE story and concrete endpoint

## Decision investigated

Whether the current `IR-CAUSE` direction fits the user's stated factory,
temporary-site, mobile-maintenance and weak-network reality, and whether a
more concrete non-personal edge decision survives direct-neighbor, baseline,
identification and feasibility checks. This packet does not modify
`research/active/`, `research/archive/` or `.research/`.

## Claim under test

The current claim is: after an ambiguous RGB capture, one controlled IR-on
capture improves a `retain / reacquire / unknown` decision for a printed marker
under held-out low-light versus transparent-cover cells, at matched capture,
latency and energy cost.

The user's actual story is different: a worker in a factory, temporary site or
mobile-repair setting needs weak-network/offline palm authentication, without
uploading raw biometric data, and needs to distinguish an authorised person
from a fake or attack. The meeting note also mentions payment systems and
proving that someone is an illegal worker. Those are identity, presentation-
attack, legal-status and security endpoints, not optical maintenance-record
endpoints.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| Component collision | Active intervention, adaptive acquisition and screen/confirm/escalate policies are already covered by Han et al. (2025), Lens (ICLR 2025), AdaptiveAE (ICCV 2025) and Bian et al. (2026). Passive optical health monitoring is covered by Ma et al. (2026). | A finite IR-on experiment on a purchased RGB/NoIR pair with an exact printed-payload oracle is narrower than those methods. This is a protocol endpoint distinction, not a new sensing mechanism. | High for broad claims; medium for the finite endpoint. |
| Exact-claim collision | `IR-CAUSE` as causal diagnosis, camera-health monitoring, generic modality selection or energy-aware adaptive sensing is directly occupied. A Raspberry Pi deployment does not change the endpoint. | The exact finite question, “does IR-on change action risk for two pre-labelled physical cells?”, was not found in the inspected sources. It remains an empirical boundary study. | High collision risk; medium remaining distinction. |
| Boundary / impossibility | Clean low-light and transparent-cover scenes can be arranged to have the same passive RGB/luma/blur/metadata while requiring different actions. Passive observations therefore cannot identify the hidden condition in general. | Identifiability is possible only for a declared fixture, independently assigned cells, frozen controls and held-out repetitions. If the worlds overlap, the correct result is non-identifiability/null, not a larger model. | High for the warning; effect size remains [GAP]. |

## Assumption and identification audit

1. **Story mismatch [KILL].** The current prospectus explicitly says “lab
   maintainer”, “non-personal printed indicator” and “maintenance log”. It has no
   worker, job-site, offline credential, payment, access-control or repair
   workflow. Rebranding the marker as a worker credential would introduce
   biometric/security requirements that the experiment does not measure.
2. **Legal-status mismatch [KILL].** A palm matcher can at most test a claimed
   identity against an enrolled template. It cannot establish immigration or
   employment legality. That status requires an authorised document/status
   verification workflow; it is not identifiable from a palm image.
3. **Cause ambiguity [GAP].** Cover state must be assigned before capture by an
   independent fixture log. Lux, luma, IR ratio, decoder confidence and image
   quality are observations, not labels for the hidden physical cause.
4. **Truth [K].** Generate the printed payload before capture and verify it with
   an independent exact-payload oracle. Decoder confidence cannot be ground
   truth.
5. **Optical confounding [K].** Camera Module 3 standard has an IR-cut filter
   while NoIR omits it; RGB/NoIR is a spectral-path change, not a generic
   camera-device transfer. Raspberry Pi Camera Module 3 product brief, p. 3.
6. **Weak-network relevance [GAP].** The current experiment has no network
   outage, local credential cache, replay threat, synchronization protocol or
   delayed cloud decision. Therefore it does not test the reason edge matters
   in the user's story.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| Han et al., *A Counterfactual Reasoning Framework for Fault Diagnosis in Robot Perception Systems*, arXiv v1, 2025-09-22, https://arxiv.org/abs/2509.18460 | Passive perception plus selected interventions | Counterfactual fault diagnosis; abstract and Sec. 1 | Active intervention for hidden perception causes | Kills causal-diagnosis framing; leaves only the finite optical test. |
| Bian et al., *Resource-Aware Safety-First Active Sensor Acquisition with Few-Shot Commissioning for Edge Fault Warning*, Sensors 26(16):5065, 2026-08-10, https://doi.org/10.3390/s26165065 | Cheap screen, confirmation capture, uncertainty/OOD escalation | Fault warning under activation/latency cost; Secs. 1, 3.1, 5.1, 6, 8 | Same screen/confirm/escalate action family | Kills generic adaptive IR acquisition; fixed two-shot is mandatory. |
| Ma, Yan & Wu, *Clean-Reference Streaming Detection of Lens Occlusion and Photometric Transitions*, arXiv v1, 2026-07-16, https://arxiv.org/abs/2607.14760 | Clean reference, luminance/gradient statistics, state machine | Optical health and camera-disjoint transfer; Secs. I-VIII, X-XIII, Supplementary XII | Passive camera-health/occlusion diagnosis | Kills passive `OPT-WIT`; active IR increment remains unverified. |
| Oleksiyuk et al., *Authentication of Copy Detection Patterns via Cross-Camera Dual-Synthetic Referencing*, arXiv v1, 2026-05-29, https://arxiv.org/abs/2605.31292 | Digital template, enrolled physical capture, cross-camera translation | Printed-pattern authentication on heterogeneous cameras; Secs. 1-6 | Printed authentication / low-end camera endpoint | Kills turning the marker experiment into a new authentication thesis; leaves it as a maintenance-record control. |
| Liu et al., *mmCooper*, ICCV 2025, https://openaccess.thecvf.com/content/ICCV2025/html/Liu_mmCooper_A_Multi-agent_Multi-stage_Communication-efficient_and_Collaboration-robust_Cooperative_Perception_Framework_ICCV_2025_paper.html | Multi-agent views and communication actions | Communication-efficient cooperative perception under calibration errors; paper pp. 28396-28406 | `COOP-MARK` two-view communication/fusion | Kills a new cooperative-perception mechanism; a finite marker action audit remains possible. |
| Xia et al., *Theoretical Insights in Model Inversion Robustness...*, CVPR 2025, https://openaccess.thecvf.com/content/CVPR2025/html/Xia_Theoretical_Insights_in_Model_Inversion_Robustness_and_Conditional_Entropy_Maximization_CVPR_2025_paper.html | Intermediate features and collaborative inference | Reconstruction risk/lower bound; pp. 8753-8763, Secs. 1-4 | `SPLIT-LEAK-AUDIT` privacy endpoint | Kills a new split-inference privacy guarantee; finite leakage measurement remains an appendix. |

## Strongest simple baseline

For IR-CAUSE, the adversarial baseline is fixed `RGB -> NoIR+IR` two-shot,
plus always-RGB, always-NoIR+IR, always-reacquire, IR-ratio, brightness/blur/
decoder-quality routing and one-extra-capture escalation. Charge capture,
latency and joules. If fixed two-shot or a scalar rule is Pareto-optimal, the
adaptive intervention is unnecessary.

For a real weak-network identity story, the minimum baseline would be a local
matcher with encrypted/enrolled templates, offline allow/deny/unknown policy,
replay-resistant freshness state and a manual fallback. A Pi demo without
presentation-attack labels, an attacker model and offline state transitions
would not test the claimed security endpoint.

## Contrarian result

`IR-CAUSE` does not fit the user's real story as currently written. Its only
credible surviving endpoint is a non-personal maintenance-record decision:
“retain this printed asset/indicator reading, reacquire once, or mark unknown.”
That endpoint can support a bounded physical pilot and a useful null result,
but it is not palm authentication, worker authorisation, payment security or
weak-network mobile maintenance.

The more concrete alternatives do not currently become thesis mechanisms:
`COOP-MARK` is a finite two-view action audit; `SPLIT-LEAK-AUDIT` is a bounded
privacy measurement; `LINK-OUTAGE-REPLAY` is protocol hygiene likely matched
by TCP plus a local journal; `FCL-PI-NB` is an explicit negative/replication
benchmark. A non-personal asset-tag decision is the only coherent endpoint,
and it survives only as `HOLD/PIVOT` pending field-story confirmation and a
pilot that beats fixed controls.

## Feasibility audit

- Existing Pi 5B, RGB/NoIR cameras, IR illuminator, printed targets and inert
  covers are sufficient for a static bench pilot.
- The user's mobile/site story needs a real credential/asset workflow,
  offline state, attack/replay test, independent labels and permission. None is
  currently confirmed.
- A “3D box” or purchased sensor adds apparatus, not a CS contribution. A new
  sensor is justified only if it creates an independent observation or
  controlled intervention and changes the measured decision frontier.
- Do not use personal palm data, worker-status claims, payment decisions or
  safety actuation without an authorised dataset, threat model and ethics
  approval. The current printed-marker setup avoids those dependencies.
- RAW-JPEG-GATE remains only a capability preflight: actual RAW mode, pairing,
  storage, timing and energy are still [GAP].

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| IR-CAUSE is not a general causal-diagnosis contribution. | [KILL] | Han et al., arXiv:2509.18460v1, 2025-09-22, https://arxiv.org/abs/2509.18460 | Abstract; Sec. 1 | Framework-level collision; not the exact Pi endpoint. |
| Screen/confirm/escalate under edge cost is established. | [KILL] | Bian et al., Sensors 26(16):5065, 2026-08-10, https://doi.org/10.3390/s26165065 | Secs. 1, 3.1, 5.1, 6, 8 | Different sensor stack; same action family. |
| Passive optical-health monitoring is established. | [KILL] | Ma et al., arXiv:2607.14760v1, 2026-07-16, https://arxiv.org/abs/2607.14760 | Secs. I-VIII, X-XIII; Supplementary XII | Does not test the active IR increment. |
| Printed-pattern authentication is already a direct endpoint. | [KILL] | Oleksiyuk et al., arXiv:2605.31292v1, 2026-05-29, https://arxiv.org/abs/2605.31292 | Secs. 1-6 | Does not validate the maintenance-record endpoint. |
| RGB/NoIR are different optical paths. | [K] | Raspberry Pi Camera Module 3 product brief, 2025-10-06, https://pip-assets.raspberrypi.com/categories/786-raspberry-pi-camera-module-3/documents/RP-008151-DS/camera-module-3-product-brief | p. 3 | Nominal product specification; purchased unit still needs checking. |
| A finite non-personal retain/reacquire/unknown endpoint remains testable. | [C] | Local `research/active/14-ir-cause-working-prospectus.md` and `13-raw-jpeg-gate-preflight.md` | “Research question”, “Formal decision object”, “Policies and controls” | Requires independent labels, exact payload oracle and held-out cells. |
| The current endpoint explains weak-network mobile maintenance. | [KILL] | Local prospectus versus `minutes/08-17.md` | Prospectus “Real problem”; meeting note full text | No network, credential, replay or field-maintenance variable is measured. |

## Queries and failed searches

Queries already reviewed in the current evidence round:

- `active illumination counterfactual fault diagnosis robot perception intervention information 2025`
- `adaptive camera sensor exposure modality selection edge capture cost 2024 2025`
- `transparent cover low light infrared illumination camera marker diagnosis exact code`
- `Raspberry Pi cooperative perception benchmark`
- `split inference intermediate feature reconstruction attack 2025`

No inspected source jointly evaluates the exact Pi 5 RGB/NoIR, pre-labelled
cover/low-light cells, printed-payload action loss and matched joules. This is
an endpoint retrieval gap, not evidence of novelty. No authorised palm,
worker-status, payment or mobile-repair dataset is confirmed. Exact camera
revision, illuminator safety, power instrument, field workflow, attacker model
and ethics/permission remain unresolved.

## Decision

`IR-CAUSE`: **KILL** as the user's factory/site/mobile weak-network palm or
worker-authorisation story. **PIVOT** only to the bounded non-personal printed
maintenance-record experiment, with fixed two-shot and simple scalar controls.

`COOP-MARK`, `SPLIT-LEAK-AUDIT`, `FCL-PI-NB` and `LINK-OUTAGE-REPLAY`: **HOLD**
only as negative/replication audits, not thesis mechanisms. No more sensor
purchases or 3D-box construction should be treated as research progress before
the concrete decision, independent truth source and field workflow are fixed.

Overall: **HOLD**

