# Edge Palm FYP Research

This is the research workspace for the edge palm-recognition FYP. It is not the final thesis and it does not replace the meeting record in [`../minutes/`](../minutes/).

## Start here

An agent should read these files in this order before adding a claim or proposing an experiment:

1. [`core/07-current-synthesis.md`](core/07-current-synthesis.md): the current conclusion, candidate claim, and stop conditions.
2. [`core/09-reading-coverage-audit.md`](core/09-reading-coverage-audit.md): what has actually been read, the remaining gaps, and the evidence strength.
3. [`core/02-story-and-innovation-options.md`](core/02-story-and-innovation-options.md): the application story and its testable economic assumptions.
4. [`core/06-evaluation-and-data-plan.md`](core/06-evaluation-and-data-plan.md): the proposed experiment, split rules, and metrics.
5. [`core/05-evidence-ledger.md`](core/05-evidence-ledger.md): the source-level boundary before relying on a technical or market claim.

The short rule is: **`core/` states what the project may currently claim; `log/` records how that conclusion was reached.** A detailed log alone is not sufficient evidence for a new project claim.

## Directory map

| Directory | Purpose | Read when |
| --- | --- | --- |
| [`core/`](core/README.md) | Canonical research state: question, source ledger, narrative, limits, evaluation plan, and current synthesis | Starting work, making a decision, writing a proposal, or changing the experiment |
| [`log/`](log/README.md) | Append-oriented deep-reading notes, reproducibility audits, protocol analysis, and discarded paths | A core claim needs its reasoning trail, or a source needs intensive reading |

## Working loop

1. Start with the five files above and state the decision being investigated.
2. Search for primary sources, then classify each source as `E1` (full primary paper/data/code), `E2` (partial primary material), `E3` (publisher/vendor/secondary material), or `Q` (question to verify).
3. Add a source-level row to [`core/05-evidence-ledger.md`](core/05-evidence-ledger.md). Update the map or landscape only when it changes the decision.
4. Create or extend a file in [`log/`](log/README.md) for an intensive paper reading, artifact audit, or protocol argument. Record what was inspected, what was not accessible, and exactly what cannot be inferred.
5. Reconcile changed conclusions into the relevant `core/` files, especially `07-current-synthesis.md`, `08-counterevidence-and-boundaries.md`, and `06-evaluation-and-data-plan.md`.

## Non-negotiable boundaries

- Do not use “Macau has no palm-recognition system” as a story. The local deployment landscape is not an established absence claim.
- Do not frame the system as detecting illegal workers. Biometric matching only supports an authorization workflow; legal status requires an authorized system and human process.
- Do not call RGB/NIR/ToF hardware, Raspberry Pi deployment, random light order, or frame differences novel without a directly comparable baseline and evidence.
- Do not call a short multi-frame capture physiological liveness, replay-resistant, or privacy-preserving without the corresponding verifier, threat model, and measurement.

## Current direction in one paragraph

The minimum demo is contactless RGB palm `1:1` verification with ROI, thresholds, and edge measurements. The only retained research candidate is conditional: a low-frequency, user-initiated, time-bounded internal maintenance workflow, where a work-order claim is already authorized and the device verifies a locally enrolled palm. The technical candidate is `ToF`-constrained geometry plus an observable RGB/NIR command-response relation and risk gate. It survives only if it improves the frozen B2 static multispectral baseline on a blind, PAIS-aware evaluation while keeping retries, latency, energy, and operator burden acceptable.
