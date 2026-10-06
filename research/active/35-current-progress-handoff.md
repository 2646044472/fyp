# Current Progress Handoff — 2026-09-17

## Decision investigated

What is the latest project state, and what work should continue next after the
2026-09-13 reset?

## Executive state

The project has two deliberately separate tracks:

1. **Immediate execution:** build the user-confirmed Raspberry Pi 5 Palm
   Payment Phase 1 MVP: local/offline visible-light capture, 1:N Fast-CC
   identification, unknown-user rejection, simulated MOP balance/payment, and
   a transaction record.
2. **Research identity:** remain gated. No thesis contribution is locked. The
   latest active research record still retains `PRF-TR` as a conditional,
   bounded physical-versus-digital action-rank evaluation (`PIVOT (Amber)`),
   while the 2026-09-13 roadmap makes the palm-payment MVP the immediate
   implementation priority. The MVP is engineering groundwork and must not be
   presented as a novel biometric, payment-security, PAD, palm-vein, or
   edge-systems contribution.

This is the authoritative handoff for continuing work: implement Phase 1 first;
preserve the older research audits as constraints; do not reopen broad
literature search or begin NIR/fusion/attack/PAD work before the Phase 1 gate.

## Evidence checked

- `research/active/README.md`, `00-project-charter.md`,
  `01-candidate-register.md`, `02-decision-log.md`, and
  `03-evidence-ledger.md`.
- `research/active/30-round-22-prf-tr-reconciliation.md` through
  `34-prf-tr-advisor-one-pager-cn.md`.
- `minutes/09-13-palm-payment-roadmap-update.md`.
- `docs/superpowers/plans/09-13-palm-payment-phase1.md`.
- The latest 2026-09-13 divergence and validation packets.
- The independent 2026-09-17 packets: [post-reset divergence](../ops/divergence/2026-09-17-palm-payment-post-reset-divergence.md)
  and [MVP/research-boundary validation](../ops/validation/2026-09-17-palm-payment-mvp-and-research-boundary-validation.md).
- `code/palm_demo/` source, README, requirements, and repository status.
- Git history through commit `08e7e6a` and working-tree status on 2026-09-17.

## What is complete

### Research and decisions

- [K] A substantial direct-neighbor audit has killed or bounded the earlier
  generic edge candidates: adaptive sensing, generic uncertainty/routing,
  storage/power recovery, transfer guarantees, RF/magnetic/mmWave/gas
  diagnosis, palm biometric fusion/attribution, generic RAW claims, marker
  decoding, and related mechanisms.
- [K] The palm/biometric branch has no surviving standalone research candidate.
  Fast-CC remains a practical engineering baseline only.
- [K] `PRF-TR` has a complete protocol, schema, prospectus, implementation
  helpers, and explicit kill path, but is only a finite evaluation/negative
  result candidate. No physical PRF-TR dataset, acquisition log, or energy log
  is present in the workspace.
- [K] The 2026-09-13 user-confirmed roadmap is a staged project: Phase 1 demo
  first, then optional NIR, fusion, physical attacks, and PAD only after later
  feasibility and direct-neighbor gates.
- [K] The independent 2026-09-17 divergence packet keeps `RING-CELL`/
  `PALM-ROBUST-ACT`, `IR-INCREMENT`, and guided-retry as conditional hypotheses
  only, with `NULL-AUDIT` as the safest fallback. The independent validation
  audit concludes `PIVOT`: retain Phase 1 as gated engineering groundwork and
  kill generic NIR/fusion/PAD/attack novelty claims until the evidence gates
  pass.

### Existing implementation

- [K] `code/palm_demo/palm_demo.py` provides a local fixed-stand **1:1**
  Fast-CC verifier, fractional fixed crop, contrast/sharpness checks, local
  template files, JSONL logging, and RGB/NoIR profile metadata.
- [K] `code/palm_demo/debug_ui.py` provides an in-memory MJPEG debug UI with
  fixed ROI preview and explicit local consent checkbox.
- [K] Pi bring-up, offline-install, safety, USB-C, and camera preflight
  documentation/scripts exist.
- [E] The two current Python files pass `python -m py_compile` on 2026-09-17.

## Working-tree changes not made by this reconciliation

The live tree also contains pending connection-document changes that were
already present during the final inspection: `code/palm_demo/README.md` and
`make_deploy_bundle.ps1` are modified, `CONNECT_GUIDE.md` is untracked, and
`SSH_REMOTE.md`/`USB_C_DIRECT_SETUP.md` are marked deleted. These changes were
preserved and not reviewed or folded into the Phase 1 implementation. The
current README and new connection guide still contain the same plaintext Pi
password, so the security gate remains open.

## What is specified but not implemented

The untracked plan
`docs/superpowers/plans/09-13-palm-payment-phase1.md` specifies the full
critical path, but repository inspection found none of the new modules or test
suite. The following are still absent:

- characterization tests and `pytest` setup;
- extracted `camera.py`, `biometric.py`, and `templates.py` services;
- `models.py` result types;
- 1:N `gallery.py` and a frozen system-level identification policy;
- SQLite `payment.py` ledger with idempotent request IDs;
- `workflow.py` connecting ROI → feature → gallery → simulated payment;
- `palm_payment_ui.py` and separate `/admin` surface;
- automatic ROI with explicit `RETRY` outcomes;
- atomic enrollment/deletion across templates and accounts;
- stage-level timing logs;
- Pi acceptance evidence for enrolled, unknown, bad-capture, insufficient-
  balance, restart, and deletion cases.

The current `requirements-dev.txt` contains NumPy, SciPy, and Pillow only; it
does not yet include `pytest`.

## Open blockers and uncertainties

- [KILL/BLOCKER] `code/palm_demo/README.md` still contains a plaintext Pi SSH
  password. The Pi password must be rotated on the device, the secret removed
  from the README, and the history exposure treated as compromised if the
  repository is public. This is Task 0 of the plan and must precede normal
  feature work.
- [GAP] No evidence shows that the Pi 5 Palm Payment MVP has been run end to
  end. Hardware presence and documentation are not transaction evidence.
- [GAP] The provisional `0.28` threshold is not frozen for 1:N use. It may be
  used only as an explicitly provisional development value until authorized
  development captures determine a system-level policy.
- [GAP] Automatic ROI has no physical capture validation. Fixed ROI should
  remain the first vertical-slice path and a debug fallback.
- [GAP] Dataset/collection permissions and ethics approval for any personal
  palm data remain unresolved. Do not treat supplied archive filenames or
  hashes as permission.
- [GAP] NIR visibility, palm-vein validity, attack apparatus feasibility, and
  PAD value are all untested; the roadmap explicitly forbids assuming them.

## Current status by track

| Track | Status | Honest interpretation | Next gate |
| --- | --- | --- | --- |
| Literature/candidate search | `HOLD` | Broad mechanism search has reached diminishing returns and many kill results | Reopen only with a qualifying workflow, independent truth, or distinct intervention |
| PRF-TR | `PIVOT (Amber)` | Complete bounded protocol/research fallback; no physical data | Pi/camera bring-up and fixed baseline matrix, if this track is later resumed |
| Palm Payment Phase 1 architecture | `SPECIFIED` | Detailed staged plan exists; no implementation yet | Close Task 0, then characterization tests |
| Existing palm demo | `ENGINEERING BASELINE` | Local 1:1 fixed-ROI verifier/debug UI | Preserve behavior while refactoring |
| Palm Payment MVP | `NOT STARTED` | No 1:N checkout or payment ledger exists | First successful fixed-ROI simulated transaction |
| NIR/fusion/attacks/PAD | `DEFERRED` | Future gated phases, not current work | Phase 1 definition of done plus new audits |

## Authoritative next work order

1. **Security gate:** rotate the Pi credential and remove the plaintext secret
   from documentation/history handling.
2. **Characterize existing behavior:** add pytest and tests for crop parsing,
   normalization, sanitization, and invalid images.
3. **Refactor without behavior change:** extract camera, biometric, and
   template services; keep CLI 1:1 verification working.
4. **Build the first vertical slice using fixed ROI:** add 1:N gallery with
   explicit `UNKNOWN`, then SQLite simulated payment, then checkout workflow.
5. **Replace the debug surface:** add the payment UI and separate admin route;
   keep user payment free of account-ID input.
6. **Harden the demo:** automatic ROI with `RETRY`, atomic enrollment/deletion,
   detailed timing logs, and a frozen threshold selected on development data.
7. **Run the Pi acceptance matrix:** two or more enrolled users, one unknown
   person, poor capture, insufficient balance, restart, and deletion.
8. **Only after Phase 1 passes:** decide whether a later NIR/attack/PAD branch
   has a real observation, endpoint, and direct-neighbor-surviving claim.

## Do not infer from this handoff

- A working Fast-CC verifier is not a working palm-payment system.
- A nearest enrolled template is not an accepted identity; open-set rejection
  and a frozen system policy are required.
- A NoIR camera plus IR illumination is not automatically palm-vein sensing.
- A payment-like UI is not a production payment or security system.
- Lack of an exact literature collision is not proof of novelty.
- The PRF-TR protocol does not authorize promoting it over the newer
  user-confirmed MVP priority.

## Decision

**HOLD implementation claims; proceed with Phase 1 engineering from Task 0.**
Keep research novelty and all later biometric/security claims gated until the
MVP and its evidence gates are complete.
