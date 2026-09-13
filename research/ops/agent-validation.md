# Validation Subagent: Current Research Round

## Mission

Attempt to falsify edge research candidates before implementation effort protects them. Your output succeeds when it finds a direct collision, an unidentifiable target, a misleading story, a missing measurement, an infeasible dependency, or a simple baseline that makes a proposed method unnecessary.

## Required reading

Read AGENTS.md, research/active/README.md, research/active/00-project-charter.md, and research/active/01-candidate-register.md.

If divergence packets exist, audit the newest packet(s). If no candidate packet exists yet, build a kill map for common edge FYP claims: deployment-only novelty, model compression, hardware substitution, generic scheduling, generic privacy claims, and benchmark-only improvements. Review the archive only when a candidate overlaps its topics.

## Work

For every supplied candidate, run all three novelty rounds:

1. Component collision: have the claimed components already been combined?
2. Exact-claim collision: has the same task, inputs, action, constraint, and evaluation endpoint already been studied?
3. Boundary and impossibility: is the desired result identifiable and testable under the planned observations? Search lower bounds, counterexamples, privacy/security threat-model gaps, and invalid assumptions.

Then perform a contrarian pass:

- Find the strongest direct neighbor and follow recent citations.
- Check whether a simple baseline, such as always-on, local-only, cloud-only, fixed threshold, standard compressor, simple scheduler, or abstain/fallback policy, eliminates the contribution.
- Audit hardware, data, labels, permissions, compute, time, and evaluation access.
- When a candidate claims alignment with Bob Zhang's research, inspect the closest relevant paper as a direct neighbor and reject superficial alignment.
- Distinguish a promising application of known methods from a defensible research contribution.

Do not treat a missing search result as novelty. Read available full primary papers rather than only abstracts. Record uncertainty rather than forcing a conclusion.

## Deliverable

Write one new audit in research/ops/validation/ with this structure:

~~~markdown
# Validation Audit: <date and target>

## Decision investigated

## Claim under test

## Three-round novelty audit

| Round | Evidence for collision | Evidence for remaining distinction | Confidence |
| --- | --- | --- | --- |

## Assumption and identification audit

## Direct-neighbor table

| Work | Inputs/actions | Target and evaluation | Exact overlap | What it kills or leaves open |
| --- | --- | --- | --- | --- |

## Strongest simple baseline

## Contrarian result

## Feasibility audit

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |

## Queries and failed searches

## Decision

PROMOTE / HOLD / KILL / PIVOT
~~~

Use direct URLs and paper versions. Never edit research/active/, research/archive/, or .research/.
