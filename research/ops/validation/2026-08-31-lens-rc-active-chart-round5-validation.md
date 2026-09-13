# Validation Audit: 2026-08-31 LENS-RC active-chart camera-health claim

## Decision investigated

Whether `LENS-RC` can support an undergraduate FYP claim: a low-cost local RGB
camera, under fixed pose/exposure/illumination, chooses `retain health`,
`capture a fixed chart`, or `unknown`; the chart-triggered policy is claimed to
improve a named camera-health false-clear/frontier at the same chart-use cost.

This audit deliberately separates that narrow claim from the rejected statement
that a chart establishes the truth of a scene-derived count or record. It tests
only image-path health: lens, focus, camera response and the declared optical
configuration. It does not test the correctness of objects or events in the
scene.

## Claim under test

Let `Y` be the normal scene image, `P(Y)` passive features, and `C` an image of
a known chart taken after a physical chart action. The residual claim is:

> With a fixed camera configuration and a finite chart-action budget, a local
> policy using `P(Y)` to decide whether to acquire `C` gives a lower
> camera-health false-clear rate at matched `unknown` and chart-use budgets than
> passive clean-reference monitoring, fixed-period chart tests, and charting
> every episode.

This is not a claim about a new chart, a new sharpness/soiling estimator, or a
new camera calibration procedure. Those are direct collisions.

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |
| 1. Component collision | ISO 12233:2024 specifies chart capture and SFR measurement under controlled illumination, framing, focus, camera-setting and white-balance conditions. IEEE 1858-2023 likewise standardizes camera-image-quality metrics. Pandey et al. 2026 use slanted-edge SFR/blur information for in-field automotive-camera state monitoring. The German 3-D-camera patent describes a reference-target capture, comparison against expected readings, and pass/fail functional monitoring. | The exact hardware here would be a cheap RGB camera with an external fixed chart, not a purpose-built internal ToF target or an automotive camera. That is an implementation boundary, not a new component family. | High for component collision. |
| 2. Exact-claim collision | Ma et al. 2026 formulate a low-cost, bounded-state camera-health signal with a clean-only reference, false-alarm constrained evaluation and explicit out-of-scope cases. Heuillet et al. 2024 formulate the general costly-observation versus prediction-error decision as cost-sensitive partial monitoring. Together they occupy passive health monitoring and the `pay for observation / act / abstain` decision family. | No inspected 2024-2026 primary paper exactly combined a commanded ISO-style external chart capture, a three-action local router, a chart-count budget and a false-clear health frontier. This absence is [GAP], not evidence of novelty. | Medium: exact combination not found; generic policy and measurement components are already occupied. |
| 3. Boundary / impossibility | ISO 12233 warns that even constrained camera files can produce chart-dependent SFR because of non-linear image processing; a chart is not a context-free measurement. Pandey et al. only estimate localized blur around suitable edges and state that a single kernel cannot cover the full image. Ma et al. report that subtle partial covers, mean-preserving defocus and geometric displacement lie outside their predicates; their thresholds also fail to transfer reliably between cameras. | A deliberately full-field chart can be an independent witness for the specific degradation and optical path it covers. It cannot identify scene truth, untested field regions, camera movement, or an application error with no chart-visible optical signature. | High for the broad-record impossibility; medium for any named health class until measured. |

## Assumption and identification audit

### What a chart pass can and cannot mean

[KILL] A chart image `C` supplies information about the camera path only under
the exact configuration in which it was captured. It contains no independent
observation of the scene state. If two scene states have different record truth
but yield the same `Y` and the chart yields the same `C`, every router based on
`(P(Y), C)` must make the same decision in both worlds. Therefore no result can
be described as certifying a scene count, object condition, or general record
truth.

[K] ISO 12233:2024 defines resolution/SFR test conditions precisely because
illumination, framing, focus, camera settings, white balance, colour/luminance
and gamma affect the measurement. Its Introduction 0.3 further says that
consumer-camera processing may make SFR depend on the test-chart feature and
can overstate an edge-based result under clipping. A casual printed chart under
automatic exposure is therefore not a calibrated external truth source.

[K] The image-path claim is also spatially bounded. Pandey et al. 2026 state
that blur kernels are estimated in localized edge ROIs, require suitable
geometry/contrast, and cannot represent a full spatially variant image with a
single kernel. Kim et al. 2025 show that droplets can have strong optical and
detector effects, but their controlled degradation measurement used a dedicated
cover-glass/droplet protocol rather than an ordinary scene. A chart should thus
be pre-registered as a witness for, for example, full-field contrast loss or
declared central defocus, not for all contamination or all task failures.

### Equally-informed active-router boundary

[KILL] Once the only new observation is a standard chart-health vector `C`, the
remaining decision is ordinary costly observation. For the same passive state
`P(Y)`, chart cost, health-label definition, data split and action set, an
equally informed cost-sensitive policy can be written directly as

`chart` iff expected reduction in false-clear loss from `C` exceeds chart cost;
otherwise choose `retain` or `unknown` according to the same loss table.

This is the partial-monitoring/active-acquisition problem studied by Heuillet,
Ahmad and Durand. A learned neural router, a confidence score, or an edge-board
deployment does not by itself distinguish LENS-RC. To claim a physical
contribution, the project would need to show that the **specific chart action**
has measurable value beyond all equally informed passive/fixed-chart policies;
to claim an algorithmic contribution, it would need a new decision guarantee
or observation constraint not presently specified.

### Required health label and failure model

[GAP] `health` is currently underspecified. A binary label such as “any lens
condition changed” is invalid because chart visibility and downstream harm are
not identical. The label must name an observable defect class and a predeclared
decision threshold, for example, “the full-field e-SFR/contrast test has crossed
the specified value in this fixed configuration.” If the label is instead
derived from the same chart score the policy consumes, evaluation leaks the
answer. Intervention logs can label deliberately imposed optical conditions,
but a separate retained test measurement is then required for the chart’s
detector score.

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |
| ISO 12233:2024, *Digital cameras - Resolution and spatial frequency responses* | Captures a suitable chart; specifies illumination, framing/focal setting, focus, camera settings, white balance, colour/luminance and gamma conditions; computes visual resolution/e-SFR/s-SFR. | Camera resolution and SFR measurement/presentation. | Fixed-chart image-path measurement and the need for frozen acquisition settings. | [KILL] A chart-based quality/self-test is established metrology. Leaves no chart-method claim, only a narrow costed routing comparison. |
| IEEE Std 1858-2023, *Camera Phone Image Quality* | Standard camera-quality metrics/procedures including SFR, colour uniformity, distortion, texture blur and visual noise. | Quantification of camera-equipped mobile-device performance. | The proposed camera-health measurements are standard quality metrics rather than novel sensing. | [KILL] Generic “measure camera health with a chart” contribution. Does not specify a conditional chart-action policy. |
| Moravec and Sara 2024, *High-recall calibration monitoring for stereo cameras* | Single-frame statistical verification of a reference calibration; emits calibrated/decalibrated/unconfirmed. | Online calibration validity and data loss, using synthetic and two real-world datasets. | Health/validity status, abstention-like `unconfirmed`, frozen-threshold evaluation and downstream failure rationale. | [KILL] Generic local camera-health status output. Different sensor setup and targetless cue leave the external-chart physical test untested. |
| Kim et al. 2025, *Effect of Droplet Contamination on Camera Lens Surfaces* | Controlled cover-glass droplet interventions; slanted-edge target/MTF and object-detection evaluation. | Quantified optical degradation under a physical lens condition. | Controlled condition map linking chart/image quality to camera degradation. | [KILL] A simple droplet/MTF mapping or degradation dataset. Leaves only a policy-comparison question. |
| Pandey et al. 2026, *Quantitative Kernel estimation from traffic signs using slanted-edge SFR* | SFR/PSF/blur-kernel estimation around naturally occurring known edge structures. | In-field sharpness/state monitoring; localized blur validation. | Low-cost non-invasive camera state monitoring with SFR; explicit spatial coverage limits. | [KILL] A new chart-SFR/blur health estimator. It strengthens the need for a full-field/declared-ROI boundary. |
| Ma, Yan and Wu 2026, *Clean-Reference Streaming Detection of Lens Occlusion and Photometric Transitions for Camera Tamper Monitoring* | Current-frame luminance/gradient/grid statistics, clean-only reference, bounded state and alarm suppression. | Low-false-alarm sensor-health/tamper signal, controlled and public diagnostics. | The fair passive baseline, health-gate output, false-alarm budget and explicit boundary reporting. | [KILL] Comparing only against generic blur/quality scores. Leaves chart action only if it beats this and a cost-matched periodic-chart control. |
| Heuillet, Ahmad and Durand 2024, *Neural Active Learning Meets the Partial Monitoring Framework* | Online costly information acquisition versus prediction-error cost. | Cost-sensitive partial-monitoring decisions across classification tasks. | The abstract action semantics of `retain / buy chart / unknown`. | [KILL] Rebranding ordinary cost-sensitive active acquisition as an edge mechanism. Leaves only an experimentally demonstrated physical information gain from the declared chart. |
| DE102021117818B4, *Camera for capturing three-dimensional image data and methods for checking the functionality of a camera* | Camera captures a reference target, compares expected and observed response, issues functional status. | Sensor self-test/fault monitoring; external target explicitly contemplated. | Commanded reference-target functional test and thresholded health conclusion. | [KILL] Reference-target self-test as a general camera-health idea. Different ToF/moving-scanner architecture means it is a component collision, not an RGB exact-endpoint collision. |

## Strongest simple baseline

The strongest fair control is an **equally informed, cost-calibrated
health router**, not a generic image-quality threshold:

1. Freeze the same passive features available to LENS-RC: clean-reference
   difference, sampled luminance/gradient, saturation/clipping indicators and
   time since last known-good chart.
2. On development blocks only, fit a monotone expected-loss lookup or logistic
   model for the three actions using exactly the declared false-clear, `unknown`
   and chart-action costs. It may not use online condition labels.
3. Compare four policies on blocked held-out episodes: passive-only
   `retain/unknown`; fixed-period chart; the cost-sensitive active router; and
   chart every episode. Each uses the same chart score, capture time, energy and
   action budget when charted.
4. Report a full Pareto curve: false-clear per independently labelled health
   episode, false alarm/unknown, chart actions, onset-to-alarm latency, and
   energy/blocked-record time. A single F1 or mean accuracy cannot establish the
   budgeted claim.

If LENS-RC's proposed method is merely another threshold or small model over
the same passive state, this baseline subsumes it. If it needs condition labels
or test-chart scores to decide *whether* to capture the chart, the protocol has
information leakage.

## Contrarian result

[KILL] The broad “reference-chart capture validates a retained record” story is
false by non-identifiability: a chart measures the imaging path but not scene
truth. The strongest narrower adversarial result is that chart self-testing,
SFR image-quality metrology, local camera-health monitoring and costly
observation routing all already exist. The present claim supplies neither a new
camera-path observation nor a new decision-theoretic boundary; a successful
chart-trigger experiment would initially be an application/condition map of
known tools.

The only defensible residual is a narrowly labelled physical preflight: on a
specific inexpensive camera and fixed optical configuration, does a chart
meaningfully improve *named* health-condition detection at a measured chart-use
cost over the equally informed passive and fixed-period controls? That is not
sufficient to lock a thesis direction before a positive result and a new
exact-claim audit.

## Feasibility audit

### Minimum physical preflight (not an FYP implementation commitment)

| Item | Must be frozen or independently recorded | Why it is required | Kill criterion |
| --- | --- | --- | --- |
| Camera path | One named low-cost camera model/firmware, manual exposure/gain/white-balance/focus if available, fixed lens distance and rigid mount. | ISO 12233 lists these acquisition factors; automatic control makes a chart score an ambiguous mixture. | Repeat clean captures cannot establish a stable reference distribution before degradation trials. |
| Reference | A chart with known geometry and a documented production/print source; chart position covers the declared field/ROI; clean repeat images acquired before each randomized block. | Home printing, chart angle, illumination and clipping can alter SFR/contrast. | Chart metric varies at the same order as the smallest intended health effect, or only detects a tiny central ROI. |
| Conditions | Pre-register no more than a few reversible, named optical interventions whose labels are set outside the online policy: for example full-field low-contrast film and a fixed manual-defocus setting. Keep localized peripheral occlusion as an explicit expected failure class, not a positive label. | Prevents post-hoc expansion from a detected case to “camera health.” | No condition has a repeatable effect on an independently retained chart measurement, or scene/passive features already separate every condition. |
| Truth split | Randomize condition order; block by day/illumination session; keep scenes and cameras out of the policy-tuning split. Preserve intervention logs; do not use online chart score as its own label. | Ma et al. show threshold transfer and real physical-event labels are serious limitations. | Health labels are inferred from the same frame/chart score used for routing, or camera/scene leakage makes holdout non-independent. |
| Comparators/endpoints | Passive Ma-style monitor, fixed-period chart and always-chart; matched chart actions/unknown rate; paired held-out decisions. | The residual claim is a resource frontier, not raw classifier accuracy. | Active chart policy does not improve the preregistered frontier, or any advantage vanishes once costs and blocked splits are matched. |

Hardware itself is inexpensive in principle, but exact model, chart source,
lighting stability, actuation mechanism, power meter and budget remain [GAP].
The bench must stay non-personal and non-production: no faces, surveillance
claims, safety actuation or consequential inspection decision.

### Exact value of a negative result

An honest null result would be:

> For camera model `X`, firmware/configuration `Y`, the stated chart geometry,
> and the pre-registered full-field optical conditions, chart-conditioned
> routing did not improve the held-out health false-clear/unknown/chart-use
> Pareto frontier over the equally informed passive router or fixed-period chart
> capture.

That result is only a scoped engineering boundary: it rules out the assumed
value of an active chart for this configuration and exposes which named
conditions are invisible to the chart/passive cues. It is useful as an appendix
or as a decision gate, but does not by itself become a broad camera-reliability
research contribution.

## Evidence ledger

| Claim | Label | Primary or official source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| Chart capture/SFR measurement and its controlled acquisition conditions are standardized; chart-dependent non-linear camera processing can change measured SFR even in laboratory conditions. | [KILL] | ISO 12233:2024(en), *Digital cameras - Resolution and spatial frequency responses*, 5th ed., 2024, https://www.iso.org/obp/ui?_escaped_fragment_=iso:std:iso:12233:ed-5:v1:en | Introduction 0.1-0.3; Clauses 4.1-4.7, 5.2, 6.1-6.2, 7 and 8. Official HTML lines 89-108. | Applies to camera resolution/SFR, not all camera faults; it establishes that a standard chart is a controlled metrology instrument, not scene truth. |
| Camera quality metrics including SFR, colour uniformity, distortion, texture blur and visual noise are already standardized. | [K] | IEEE Std 1858-2023, published 2023-08-04, https://standards.ieee.org/ieee/1858/6931/ | Official scope/metrics page, entirety. | Camera phones rather than every webcam; used only to establish component maturity. |
| Low-cost camera-health monitor has bounded state, clean-only reference, explicit scope and false-alarm-constrained protocol; physical-event/continuous labels and cross-camera threshold transfer remain limitations. | [KILL] | Ma, Yan and Wu, arXiv:2607.14760v1, 2026-07-16, https://arxiv.org/html/2607.14760v1 | Abstract; Sec. I lines 76-99; Sec. II-A-D lines 101-117; Sec. V-A and V-G lines 200-261; Sec. VI lines 255-272; Supplement Sec. XII lines 508-516. | Preprint and passive observation only; it is the required fair baseline, not proof that an external chart has zero value. |
| Controlled droplet contamination degrades MTF and object detection; optical degradation depends on contamination geometry/material rather than a generic label. | [K] | Kim et al., *Applied Sciences* 15(5):2690, 2025, https://doi.org/10.3390/app15052690 | Sec. 2.4, Fig. 5-8 and Secs. 3-4, official article HTML. | Automotive cover glass and droplets; it supports named-condition, independent intervention labels, not a chart-router method. |
| SFR/blur-kernel estimation is proposed for in-field camera state monitoring but is localized, needs suitable high-contrast edges and does not cover full spatially varying blur. | [KILL] | Pandey et al., *Scientific Reports* 16:7387, 2026-02-19, https://doi.org/10.1038/s41598-026-40556-w | Introduction, Sec. 1; Sec. 4, esp. pp. / HTML lines 307-328. | Automotive traffic signs, not an active chart. It blocks a new SFR/blur estimator and documents coverage limits. |
| Online camera calibration verification can emit calibrated/decalibrated/unconfirmed, report data loss, and requires an experimental evaluation of its choice of verification measure. | [K] | Moravec and Sara, *Pattern Analysis and Applications* 27:41, version of record 2024-04-13, https://doi.org/10.1007/s10044-024-01264-1 | Secs. 2-3.2, esp. Eq. (16); Sec. 4, lines 239-268; Conclusion. | Stereo calibration, targetless and automotive/robotics; it occupies health-status/unknown semantics, not the chart action. |
| Costly acquisition versus prediction error is a formal partial-monitoring problem; the cited 2024 work evaluates cost-sensitive actions. | [KILL] | Heuillet, Ahmad and Durand, *UAI 2024*, PMLR 244:1621-1639, https://proceedings.mlr.press/v244/heuillet24a.html | Abstract; official proceedings page lines 8-35; PDF Secs. 1-3. | General classification rather than physical chart health. It kills an abstract router innovation claim, not a measured physical information effect. |
| A reference-target capture compared with expected sensor readings is an established camera functional-test pattern; the patent explicitly permits external targets. | [K] | DE102021117818B4, published patent record accessed 2026-08-31, https://patents.google.com/patent/DE102021117818B4/en | Description paras. / HTML lines 139-148, 166-178 and 259-264; claims lines 278-280. | ToF/moving scanner and patent rather than RGB empirical paper; component collision only. |

## Queries and failed searches

Queries run on 2026-08-31:

- `"camera health" "reference chart" monitoring 2024 paper`
- `"camera self-test" calibration target industrial vision 2025 paper`
- `"lens soiling" "test chart" camera monitoring paper`
- `active camera calibration target online quality monitoring industrial vision paper`
- `"camera health monitoring" 2024 "lens" "calibration"`
- `"reference target" camera "self-test" vision sensor paper`
- `"test pattern" "camera health" monitoring image sensor`
- `2024 "active feature acquisition" selective sensing "cost" camera`
- `2025 "value of information" active sensing camera monitoring sensor health`
- `ISO 12233 2024 chart camera resolution measurement official`
- `camera module in-field image quality monitoring calibration chart 2024 paper`

Failed or unresolved retrievals:

- No inspected 2024-2026 primary work exactly matched an external RGB chart,
  action-selected chart capture, a local `retain/chart/unknown` output, and a
  matched chart-budget false-clear evaluation. This is [GAP], not an originality
  conclusion.
- The full 2025 Kim HTML was only partially available through search retrieval;
  its DOI, title, Section 2.4 and reported controlled protocol were verified,
  but a page-numbered PDF audit is [GAP].
- No current hardware purchase, chart spectral/reflectance certificate,
  controllable light source, servo/actuation design, power meter, or multiple
  camera units has been confirmed. Camera-disjoint assessment may therefore be
  infeasible under the actual budget.
- No named Bob Zhang paper was found that creates a non-superficial overlap with
  this chart-health router. Advisor fit remains [GAP], not a contribution.

## Decision

**KILL as a primary FYP direction; PIVOT only as a short physical gate.**

The earlier broad record-validity claim is invalid. The narrower camera-path
claim collides at the component level with standard chart metrology and
reference-target self-test, at the policy level with cost-sensitive active
acquisition, and at the evaluation level with Ma-style camera-health baselines.
It has no verified distinct guarantee, new observation model or endpoint. Do
not promote it to Amber based on a Raspberry Pi/webcam demonstration.

Run the minimum preflight only if it is useful for deciding whether to discard
the bench apparatus. A positive result shows a configuration-specific physical
value-of-information effect and must undergo a new exact-claim/citation audit;
a null gives the scoped boundary stated above. Neither outcome currently
justifies reserving the FYP research slot.

**KILL.**
