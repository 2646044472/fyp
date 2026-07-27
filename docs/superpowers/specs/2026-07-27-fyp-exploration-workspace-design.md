# FYP Exploration Workspace Design

## Objective

Create a minimal Git-based workspace for two teammates conducting a two-week
exploration of edge AI for palmprint recognition. The workspace should keep
research evidence, team responsibilities, meeting decisions, and experiment
results organized without imposing a premature software architecture.

## Design Principles

- Start with the smallest structure that supports two-person collaboration.
- Keep planning and research records in Markdown so they are easy to review in
  Git.
- Keep datasets, model weights, generated artifacts, and local environments out
  of version control.
- Add new files or split existing notes only when their size or use justifies it.
- Keep the code and data areas intentionally neutral until the team selects a
  baseline model, dataset, and deployment platform.

## Repository Structure

```text
fyp/
├── README.md
├── TRACKER.md
├── notes/
│   ├── literature.md
│   ├── meetings.md
│   └── experiments.md
├── code/
│   └── README.md
├── data/
│   └── README.md
└── .gitignore
```

The existing empty `brief.md` will be removed after its intended content has
been incorporated into `README.md`.

## File Responsibilities

### `README.md`

The repository entry point will contain:

- the tentative project direction and motivation;
- the boundaries of the initial exploration;
- the five expected two-week outputs;
- basic collaboration and setup instructions;
- a map of the repository;
- links to the tracker and three note files.

It will explicitly state that the research question, dataset, baseline, and
edge platform have not yet been finalized.

### `TRACKER.md`

The shared tracker will use a compact task table with:

- task;
- owner;
- priority;
- status;
- due date;
- next action.

It will contain the five exploration deliverables as the initial workstreams
and define a small set of consistent status values. Teammates will replace the
generic member labels with their names when assigning work.

### `notes/literature.md`

This file will consolidate early research notes under sections for:

- search strategy and keywords;
- papers;
- datasets and evaluation protocols;
- baseline models and repositories;
- deployment tools and edge platforms;
- technical bottlenecks;
- candidate research questions;
- unresolved questions.

Tables will encourage links, evidence, relevance notes, and follow-up actions
instead of unstructured paper summaries.

### `notes/meetings.md`

This file will include a reusable meeting-entry format covering:

- date and attendees;
- agenda;
- discussion notes;
- decisions and rationale;
- action items with owners and due dates;
- questions for the supervisor;
- next meeting.

The newest meeting entry will be placed first.

### `notes/experiments.md`

This file will define an experiment-entry format containing:

- experiment identifier and date;
- owner and status;
- question or hypothesis;
- dataset and evaluation protocol;
- model and configuration;
- hardware and software environment;
- accuracy, latency, memory, power, and model-size metrics where applicable;
- results;
- conclusion and next action;
- links to code and generated artifacts.

Missing metrics will be marked as not measured rather than silently omitted.

### `code/README.md`

This file will explain that source code, download scripts, training code, and
deployment utilities belong in `code/`. It will avoid prescribing a Python
package layout before a baseline is selected.

### `data/README.md`

This file will document the rule that datasets are not committed to Git. It
will reserve the directory for acquisition instructions, checksums, metadata,
and small manifests, while raw and processed data remain ignored.

### `.gitignore`

The ignore rules will cover:

- operating-system and editor metadata;
- Python caches, test caches, and virtual environments;
- notebook checkpoints;
- secrets and local environment files;
- raw and processed dataset directories;
- model checkpoints and common exported-model formats;
- generated experiment outputs, logs, and profiling traces.

README files and lightweight manifests inside `data/` will remain trackable.

## Collaboration Workflow

1. A teammate selects or creates a task in `TRACKER.md`.
2. The owner records evidence in the relevant note file while working.
3. Decisions made in meetings are recorded with their rationale.
4. Reproducible trials receive an entry in `notes/experiments.md`.
5. Code and data-acquisition instructions are linked from the relevant entry.
6. Changes are committed in small, descriptive Git commits.

No external issue tracker, project board, database, or experiment-tracking
service is required during the initial two-week exploration.

## Validation

The setup is complete when:

- every path in the repository structure exists;
- all Markdown links resolve to tracked files;
- the five two-week deliverables appear in the tracker;
- each note file contains a usable entry or table template;
- ignore rules exclude a representative dataset file, model checkpoint,
  virtual environment file, and generated result while retaining
  `data/README.md`;
- Git reports no unintended files after the initial setup commit.

## Deferred Decisions

The following decisions are intentionally outside this setup:

- final FYP research question;
- dataset and evaluation protocol;
- baseline model and framework;
- target edge platform;
- dependency manager and Python package structure;
- experiment-tracking platform;
- division of work between the two teammates.

These will be decided using evidence gathered during the exploration.
