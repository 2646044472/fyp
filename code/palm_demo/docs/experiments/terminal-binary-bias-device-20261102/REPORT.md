# Terminal RF binary-bias screen: blocked before first query

2026-11-02, Windows CPU, four previously exposed device-development queries.
The one allowed run loaded the complete 11-identity, five-frame gallery, then
stopped on `PermissionError: [WinError 10013]` in the first HTTP client's
`socket.connect()`. **Zero identification queries completed, zero scoring
callbacks ran, and zero A/B/C image results exist.** This is an environment
block, not a passed or rejected recognition mechanism. No accuracy or speed
gain has been established.

The denied action was the first baseline `POST /api/demo/identify` connection
to `127.0.0.1` at the HTTP server's OS-assigned ephemeral TCP port. The server
bind had succeeded; the port number was not persisted by the inherited harness
and is unknown. The stack identifies `HTTPConnection.request -> connect ->
socket.create_connection -> sock.connect`. No HTTP response was received and
there is no evidence of a handler invocation. This was an actual command/OS
permission error, not an automatic approval-review rejection. The tool reported
exit code 1. No retry, alternate port/transport, in-process query workaround,
escalation, firewall/ACL change or permission repair was attempted.

## Frozen hypothesis and implementation

Existing terminal RF Hamming counts exclude the known filter-border responses
but do not center each code's binary marginal. A skewed zero/one fraction can
contribute similarity without establishing corresponding palm structure. That
is a mathematical motivation for a screen; real-query marginal bias has not
been observed in this run. Earlier errors' winning frames already shared one
pose, and valid support did not prove anatomical correspondence.

All three arms use identical original code pairs, 81 shifts, the 28x28 RF mask,
per-frame minima and mean of the best two original enrollment frames. For each
overlap, `n` is the valid count, `a,b` the one counts and `c` their intersection:

- A: `(a + b - 2*c) / n`, the original RF distance.
- B: `A + .5*(2*a/n - 1)*(2*b/n - 1)`, a mean-centering diagnostic only.
- C: `.5*(1 - (n*c-a*b)/sqrt(a*(n-a)*b*(n-b)))`, the sole candidate.

C is Pearson correlation mapped to a distance. The centered-correlation formula
and constant-input limitation are documented by
[SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html).
An exactly zero variance maps to worst distance 1; there is no fitted epsilon,
margin, mixture weight or imbalance threshold. Float64 count arithmetic checks
the feasible contingency table and correlation bounds. Only final numerical
roundoff within 1e-12 may be clipped to the mathematical correlation range.
No independence/p-value claim is made for spatially correlated code locations.

Only the original terminal RF branch could change. Confident paths retain their
original full vectors and decisions. ROI, template bytes, all identities, five
frames, poses, shifts, aggregation and acceptance thresholds remain fixed.
The candidate has no image-name, identity, truth-label or score-based ROI rule.
Evaluation consults truth only after producing all identity scores. Ties and
constant comparisons remain visible and cannot count as correct recognition.

`terminal_rf_evidence.install` gained an optional immutable pair observer; its
default has the original numerical path. The private observer captures packed
actual comparisons once, without adding features or changing the original
scorer's accumulators. Source/model/dependency/image/template hashes and the
CPU backend participate in a per-role versioned capture cache key. No cache was
populated in this attempt. Raw codes and full role bindings belong only under
ignored runtime, never this report or Git.

## Fixed denominator and promotion gates

The inherited role bindings were frozen before the run:

| Role | Stored reference | This attempt |
| --- | --- | --- |
| D1 | Remaining device error | First HTTP connection denied; no result |
| D2 | Remaining device error | Not attempted |
| D3 | Correct terminal control | Not attempted |
| D4 | Correct fast control | Not attempted |

The denominator stays **four**. Observed outcome counts are unavailable, not
zero accuracy. No role was replaced. All 11 identities and all 55 original
enrollment frames were present in preparation; copied loading is not fresh
registration.

The frozen order requires all four real baseline full vectors, ROI coordinates,
details, sampled-ROI pixel hashes, decoded-input hashes, routes and decisions to
match their stored references before any offline candidate calculation. A must
then reproduce all terminal identity scores exactly from captured codes. Neither
real parity gate was reached.

The mechanism gate compares the signed-mean penalty on original winning cells
for the wrong and true identities. All tied cells and tied best-two frame
selections are retained; the wrong minimum penalty must exceed the true maximum
for at least one error. If neither error supports that explanation, stop it.
C must additionally correct at least one error, preserve both correct controls,
and introduce no failure, rejection or tie. B cannot substitute for C. A failed
formula or panel cannot be adjusted or resampled. The run is non-resumable.
Even a future pass would only qualify further investigation on seen development
data, not an independent evaluation, public generalization or deployment.

No public query, full168 replay, new registration, GPU installation/inference,
retired SIFT/rotation/common-pose experiment or push ran. The prospectively
discussed public three-query panel was not executed or added to this device run.

## Actual execution and resources

Protocol fingerprint, frozen before model loading:
`acf2c7173ae655353d2267f4fbf88b9a5f9daf60652e156af2f2757eebe709a4`.
It locks 389 source files, 3,518 dependency files, model files, four original
inputs and 11 template containers. The executed driver byte-matches its archive.
Private artifacts are under `runtime/terminal-binary-bias-device-20261102-r1`.

| Observation | Actual value |
| --- | ---: |
| Initial available RAM | 12.6406 GiB |
| Protocol verification/import boundary | 9.636 s elapsed; RSS 0.1008 GiB |
| Model initialization and complete gallery-ready | 15.917 s |
| CompNet embedding calls | 55, all CPU provider |
| Gallery load calls | 22, including normal repeated cache access |
| Completed identify HTTP / candidate HTTP | 0 / 0 |
| Fresh enrollment attempts / offline metric records | 0 / 0 |
| One-second telemetry samples | 27 |
| Minimum sampled host available RAM | 11.8380 GiB |
| Maximum sampled worker RSS | 0.88184 GiB |
| Process peak working set at last resource observation | 0.88232 GiB |
| Post-epoch RSS at last resource observation | 0.48758 GiB |
| CPU time at that observation | 22.25 s |
| Whole run wall time, including final integrity checks | 30.844 s |

Startup available RAM >=12 GiB, running >=2 GiB and worker RSS <=14 GiB stayed
fixed. No sampled violation occurred; the minimum running sample need not meet
the separate next-start gate. Sampling is not continuous-limit proof.
The final resource observation preceded the final read-only integrity hashes.
Gallery-ready and wall times are not recognition latency or an acceleration.

Post-return GC collected zero objects on this exceptional path; residual RSS
remained about .488 GiB at the saved observation. This does not reproduce or
extend the earlier successful normal-lifecycle release result. The worker then
exited. At 08:19:41 UTC a read-only process check found no related worker and
12.5244 GiB available; no other application was terminated.

The D1 `inflight.json` remains as a historical failed-attempt marker. It does
not mean a worker or request is currently active. The original SMPD status
remains `paused_STOP`, 1239/3217, with STOP present and no original inflight.
The after-run full frozen-file verification passed: source/dependency/model
hashes, original template and input hashes, protocol and pause metadata match.

## Tests and outstanding evidence

**48 tests passed**, zero failures/errors/skips, before freezing. They cover
integer overlap counts against a separate direct-pixel implementation, all A/B/C
formulas, exact A equivalence to the existing RF kernel, constants, nearly
constant arrays, malformed tables, symmetry, input immutability, frozen Gallery
decision parity, tie accounting, diagnostic-B exclusion, four-role promotion
gates, original RF paths and the existing resource/registration diagnostics.
An initial test's overlap-order expectation was reversed; that reference was
corrected before the passing tests and before protocol preparation. No image
experiment preceded the passing test gate.

The missing evidence is still the real-query bit marginals, four exact baseline
reproductions, A reconstruction, B/C paired outcomes and any candidate HTTP/Pi
end-to-end or public results. The numerical implementation is tested; the
recognition mechanism is unmeasured. The local TCP-connect denial must have
material repair evidence before a separately authorized new attempt. Existing
GPU temporary-wheel and external-publication blockers were not retried.

There is no independent runtime-model identity receipt; no Astra execution or
model-setting change is claimed. No remote state was changed by this work.
