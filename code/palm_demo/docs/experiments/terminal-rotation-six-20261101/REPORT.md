# Terminal rotation-consensus pilot: implementation ready, image run blocked

2026-11-01. Windows CPU, previously seen device/public development data. No Pi
timing, independent generalization or stranger FAR qualification.

The candidate and fixed six-query paired protocol were prepared. The formal
startup check observed **11.132935 GiB available RAM**, below the frozen **12 GiB**
requirement, and raised `MemoryError: Frozen available-memory/RSS limit`.
**Zero image queries, zero model inference and zero gallery initializations were
attempted.** This is an operational block, not candidate success or failure.
No full168 regression was started. SMPD remains paused at1239/3217 with STOP.

## Evidence and mechanism

The preceding device experiment retained166 correct and2 wrong out of168 on both
arms, with exactly matching ROI, scores/routes and34 five-frame template groups.
All169 device primary ROIs were geometry-valid, so the existing OOB half-turn
policy did not trigger. The two remaining errors both have conflicting localizer
heads, but21 correct device queries do too. Conflict alone cannot justify rejection.

Earlier per-frame logs reproduce the new baseline's complete ordinary/RF score
vectors for both errors. Their winning incorrect frame scores came from fixed
pose comparisons, with full receptive-field support. One alternate localization
ranked the true identity first under CompNet but failed the unchanged confidence
gates. These observations motivate an identity-independent localization test;
they do not establish its success or justify lowering acceptance thresholds.

The new opt-in wrapper first calls the unchanged scorer. Only an original
terminal-RF query with a valid primary ROI and conflicting localizer heads may
enter the new mechanism. It reuses the original0-degree localization and observes
90/180/270-degree views once each. Coordinates are mapped back to the original
image. A unique largest clique of at least3 distinct views must have pairwise
IoU>=.5. The selected ROI is the actual geometric medoid, with ascending rotation
as a deterministic tie break. No identity, label, filename or matching score
selects the ROI. Ambiguity or insufficient agreement preserves the primary.

Polygon hull ordering is used for overlap comparisons only. Original detector
corner semantics are retained when sampling original pixels; sorting sampling
corners would introduce an unrelated texture rotation. A changed ROI causes one
fresh query extraction and complete-gallery rescore using the existing pipeline,
five-frame best2 rule and gates. The saved original scorer prevents recursion;
new and old score vectors are never combined or selected by better identity score.
The wrapper is installed only by the isolated pilot, not the service.

## Frozen panel and evaluation rules

|Private role label|Selection rule|Stored baseline outcome|New observations|
|---|---|---|---|
|D1,D2|Both remaining device errors, sorted by original case/query key|2 wrong|0|
|D3|First correct terminal query with conflicting heads in that case|correct|0|
|D4|First correct early-exit query with conflicting heads in that case|correct|0|
|P1|First eligible completed development F/frontal query, enrolled truth, wrong terminal route, conflicting heads|wrong|0|
|P2|First eligible completed development query with correct early exit|correct|0|

Public selection excludes the previous eight-image pilot and the prospectively
reserved subjects before reading query-result payloads. F/frontal selection avoids
making the previously identified side-on, unusable-valley example the repair
target. It does not certify finger-valley visibility or anatomical ROI correctness.
There is no substitution after seeing new results. This authorized panel differs
from the draft's six-device-then-public sequence: it fixes **four device plus two
public** queries in one panel before any new inference.

Both arms retain all11 device-case identities or all86 public identities and each
identity's five original enrollment frames. Templates may be hash-verified and
byte-copied to isolated writable runtimes because the candidate is query-only.
The report must describe initialization/gallery-ready time separately, with
**zero fresh enrollment attempts**, rather than calling copied loading enrollment.
Full168, if later authorized after passing, requires the original fresh enrollment
protocol and all166 previously correct per-query guards.

The intended12 HTTP observations are six baseline and six candidate requests.
Baseline full-gallery vectors/decisions/routes/primary localization must match
stored references. Candidate original scoring is a shadow control and must match
the stored full vector, route and primary localization. Pass requires complete
coverage, at least one wrong-to-correct transition, zero lost correct controls
and no new error acceptance, rejection, tie or processing failure. A retry/reject
never counts as correct identification. No real correction or any control loss
eliminates the candidate; it must not proceed to168. Any pass here is only bounded
seen-development evidence, not proof of public generalization.

Models, thresholds, labels, original bytes, galleries and five-frame selection
are frozen. Every issued token must be canceled, all balances preserved and zero
transactions recorded. This does not test positive payment confirmation.

## Resource and protocol limits

Single CPU worker; startup>=12 GiB free, running>=2 GiB free and RSS<=14 GiB.
No app termination or lowering memory gates. The one-shot startup receipt failed
the first gate. No retry or automatic resumption was scheduled. The local
`RUN_STARTED.json` marker does not exist because inference never began.

The source-bound protocol fingerprint is
`73ebec4ba28743bbeadf3eef48a72f42c70b2e83aaa96c1bcf6b46b3ad768214`.
The private protocol, fixed role bindings and startup receipt remain local.
If the already fixed pilot is explicitly continued later, it must recheck the
same source/model/template hashes and12 GiB gate; sample/parameter reselection
is not an operational continuation.

The prior device168 logical evaluation used a reviewed **8 GiB** startup gate for
the final55 candidate queries after the original **12 GiB** gate stopped the first
epoch. This historical difference is preserved; it was not an all-epochs pass
under12 GiB. Its159 vs153 timely-correct observations have epoch/host-load
confounding and do not establish algorithmic acceleration.

Old error requests took approximately5.6–5.8 seconds on Windows; adding three
localizations and possibly a second full score pass may increase that cost.
Public difficult queries can take over a minute. The pilot freezes a30-minute
wall budget checked at completed boundaries and a600-second HTTP timeout; neither
is a completion guarantee or Pi speed estimate. No new timing result exists.

## Validation and model evidence

**15 synthetic tests passed**. They check non-square image coordinate inverses
against every pixel under PIL right-angle transforms, unique/ambiguous/insufficient
geometric quorums, medoid selection, original-pixel sampling and anatomical corner
order, unchanged early/invalid/agreed paths, single rescoring without score-based
selection, fixed control roles, rejection accounting, correct losses, duplicate
queries, incomplete coverage and shadow-parity failures.

The developer-supplied current model identifier is `gpt-6.1-sol`. There is no
independent tool-returned runtime-model receipt. The preceding planning text was
written by the current assistant, not a verified Astra run; an incoming task's
description of it as an Astra result is not execution evidence.

Only code, synthetic tests and this sanitized report are intended for Git. Private
role bindings, image paths, identities, ROI coordinates/pixels, templates, raw
results and historical failures remain local. No GPU dependency, driver, download,
network/security change, deployment, production change or PPT edit occurred.
