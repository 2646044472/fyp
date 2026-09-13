# Edge FYP Research Agent Guide

This workspace is for finding one defensible computer-science undergraduate FYP direction in edge computing. It is a research workspace, not an implementation repository. Preserve the distinction between sourced evidence, hypotheses, and decisions.

## Workspace map

| Path | Role | Write policy |
| --- | --- | --- |
| research/active/ | Current project charter, candidates, decisions, and evidence | Coordinator only after checking both subagent outputs |
| research/archive/2026-08-edge-sensing/ | Historical palm and edge-sensing investigation | Read-only; do not promote an archived claim by default |
| research/ops/divergence/ | Candidate packets from the divergence subagent | Divergence subagent only |
| research/ops/validation/ | Falsification and direct-neighbor audits | Validation subagent only |
| research/inbox/ | Archived unstructured notes | Read-only historical input; not evidence |
| .research/ | Persistent synthesis store managed by the research skill | Coordinator only |
| minutes/ | Meeting notes and user constraints | User/coordinator only |

Do not edit a file outside the role directory assigned in the prompt, except when explicitly acting as the coordinator. Never erase or rewrite another agent's file. The worktree contains user-owned changes; preserve them.

## Shared evidence standard

- Read research/active/README.md and research/active/00-project-charter.md before proposing a conclusion.
- Use research/archive/2026-08-edge-sensing/ only when the new idea overlaps its prior topics. It records real negative evidence and baselines, but it is not the current direction.
- Search primary papers and official author, conference, journal, dataset, or code versions first. A search snippet, abstract, survey, or model-generated summary may generate a lead but cannot establish a central claim.
- Inspect the task, inputs, assumptions, baselines, evaluation target, limitations, and future-work text of every load-bearing paper. Do not treat an author's future-work sentence as proof of an open problem; check later work and citation chains.
- Label claims as [K] known with source, [C] conjecture, [GAP] unresolved, [KILL] a result that defeats a candidate, and [E] an empirical finding.
- No statement of global novelty. Permitted novelty wording is limited to the databases, queries, dates, and source chains actually inspected.
- A candidate is not research merely because it uses edge hardware, on-device AI, model compression, federated learning, a new neural network, or a new dataset. It must differ from direct work in a falsifiable task, observation model, decision/action, guarantee, constraint, or evaluation endpoint.
- The project may be modestly adjacent to Bob Zhang's public research, including biometrics, incomplete multi-view learning, restoration, anomaly detection, uncertainty, or trustworthy vision. Treat that adjacency as advisor fit, not proof of novelty; inspect the professor's closest work as a direct-neighbor check.
- Preserve both arguments for every candidate: the story explains the real decision and concrete harm, while the innovation claim states the exact technical difference that a direct baseline or paper could refute.

## Parallel roles

Choose exactly one role for a subagent. The roles deliberately disagree in incentives.

### Role: divergence

Read research/ops/agent-divergence.md and write only to research/ops/divergence/.

Goal: use recent and foundational literature to generate 3-7 sharply different edge candidates with a coherent real-world story plus a claim that could fail. Do not defend an existing candidate by default.

### Role: validation

Read research/ops/agent-validation.md and write only to research/ops/validation/.

Goal: try to kill active or supplied candidates using direct-neighbor research, citation chains, benchmarks, lower bounds, identification checks, feasibility failures, and simple baselines. A strong negative result is useful output.

### Role: coordinator

The main agent launches the divergence and validation subagents in parallel, reads their packets, reports evidence and conflicts directly to the user, and asks a question only when the answer changes the next research gate. The coordinator does not call a direction novel merely because neither subagent found a collision.

## Required handoff

Every subagent output must begin with the decision it investigated and end with PROMOTE, HOLD, KILL, or PIVOT. Include exact URLs, paper version/date, sections or pages read, search queries, and unresolved uncertainties. Do not modify research/active/ until the coordinator has checked both sides.
