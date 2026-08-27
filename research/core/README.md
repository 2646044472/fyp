# Core Research State

`core/` is the concise, canonical state of the research. It is the first place to read and the only place from which an agent should take a project-level conclusion. Detailed inspection trails live in [`../log/`](../log/README.md).

## Reading order

| File | Authority |
| --- | --- |
| [`00-research-method.md`](00-research-method.md) | Research question, source rules, and AI-assisted research method |
| [`01-literature-map.md`](01-literature-map.md) | Fast map of the literature and what each source is usable for |
| [`02-story-and-innovation-options.md`](02-story-and-innovation-options.md) | Candidate story, user value, and falsifiable assumptions |
| [`03-research-reflection.md`](03-research-reflection.md) | Rejected intuitions, changed beliefs, and stop/go criteria |
| [`04-recent-research-landscape.md`](04-recent-research-landscape.md) | Recent technical landscape and direct implications |
| [`05-evidence-ledger.md`](05-evidence-ledger.md) | Source-level evidence, accessibility, and inference limits |
| [`06-evaluation-and-data-plan.md`](06-evaluation-and-data-plan.md) | Dataset, split, metrics, baselines, and frozen protocol |
| [`07-current-synthesis.md`](07-current-synthesis.md) | Current project claim and next decision |
| [`08-counterevidence-and-boundaries.md`](08-counterevidence-and-boundaries.md) | Competing explanations, negative evidence, and prohibited claims |
| [`09-reading-coverage-audit.md`](09-reading-coverage-audit.md) | Reading depth, coverage, and the next evidence to acquire |
| [`10-story-validation-plan.md`](10-story-validation-plan.md) | Interviews and observations needed to validate the story |
| [`11-ai-assisted-research-protocol.md`](11-ai-assisted-research-protocol.md) | Auditable AI research workflow and citation discipline |
| [`12-bob-zhang-lab-audit.md`](12-bob-zhang-lab-audit.md) | Bob Zhang/PAMI publication map and non-palmprint FYP direction decision |

## Update rules

- New source: add it to [`05-evidence-ledger.md`](05-evidence-ledger.md) before using it in a conclusion.
- Decision changes: revise [`07-current-synthesis.md`](07-current-synthesis.md) and, where relevant, the story, evaluation plan, or boundaries document.
- Intensive reading, artifact inspection, or protocol reasoning: write the detail in [`../log/`](../log/README.md), then link or cite it from the ledger.
- A source may be useful without being transferable. Preserve modality, protocol, hardware, dataset, and deployment limits explicitly.
