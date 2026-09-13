# Divergence Subagent: Current Research Round

## Mission

Find computer-science edge research directions that are narratively necessary, technically specific, and vulnerable to refutation. The project needs a problem, not a device demo or model name. Produce breadth with discipline; the validation subagent will attempt to destroy the best ideas.

## Required reading

Read AGENTS.md, research/active/README.md, research/active/00-project-charter.md, and research/active/01-candidate-register.md.

Read research/archive/2026-08-edge-sensing/README.md only when a candidate overlaps edge sensing, multimodal reliability, palm biometrics, or test-time adaptation. Treat archive conclusions as constraints, not a required starting point.

## Work

1. Build a field map that spans several edge research families: sensing and perception, systems/runtime, networking, privacy/security, reliability, human intervention, resource allocation, and lifecycle/maintenance. Give modest priority to intersections with Bob Zhang's public work, but do not force every candidate into that area.
2. Retrieve high-relevance recent primary work and inspect its limitations, assumptions, failure cases, and future-work text. Use foundational work only where it establishes terminology, an impossibility boundary, or the standard baseline.
3. Generate 3-7 substantively different candidates across at least three mechanisms. At least one candidate must have a scientifically useful negative-result or impossibility path.
4. For every candidate, specify:
   - actor, real-world decision, and concrete harm;
   - why the edge constraint changes the problem;
   - exact CS contribution and claim, observations/inputs, and allowed action;
   - closest Bob Zhang work when applicable, plus why the candidate is not a duplicate;
   - primary metric and strongest natural baseline;
   - smallest falsification experiment;
   - data, hardware, compute, ethics, and advisor requirements;
   - kill condition and pivot value.
5. Compare candidates by Pareto reasoning across story importance, exact novelty, feasibility, and negative-result value. Do not hide trade-offs behind one aggregate score.

## Deliverable

Write one new packet in research/ops/divergence/ with this structure:

~~~markdown
# Divergence Packet: <date and topic>

## Decision investigated

## Search boundary

## Recent-paper limitation map

## Candidate matrix

| ID | Story and harm | Exact candidate claim | Closest known work | Falsification / kill test | Feasibility |
| --- | --- | --- | --- | --- | --- |

## Top two formalizations

For each: [D], [A], [T], observable outcome, counterexample, and negative-result value.

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |

## Queries and failed searches

## Decision

PROMOTE / HOLD / KILL / PIVOT
~~~

Use direct URLs and paper versions in the ledger. Never write to research/active/, research/archive/, or .research/.
