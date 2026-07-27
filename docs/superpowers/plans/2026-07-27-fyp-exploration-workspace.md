# FYP Exploration Workspace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a minimal Git-based workspace that helps two teammates complete and document a two-week exploration of edge AI for palmprint recognition.

**Architecture:** The repository uses a deliverable-oriented `README.md` and `TRACKER.md`, three focused append-only research logs under `notes/`, and intentionally neutral `code/` and `data/` areas. Git ignore rules keep local environments, large datasets, model artifacts, and generated experiment output outside version control.

**Tech Stack:** Markdown, Git, Git ignore patterns, PowerShell validation commands

## Global Constraints

- Preserve the approved minimal top-level structure: `README.md`, `TRACKER.md`, `notes/`, `code/`, `data/`, and `.gitignore`.
- Support exactly the current two-person collaboration need without adding external project-management or experiment-tracking services.
- Do not prescribe a framework, package layout, dataset, model, evaluation protocol, or edge platform before the exploration produces evidence.
- Do not commit datasets, model weights, generated outputs, local environments, secrets, or editor metadata.
- Keep `data/README.md` and lightweight data manifests trackable.
- Incorporate the exploration brief into `README.md`, then remove the existing empty `brief.md`.

---

## File Map

- `README.md`: project direction, motivation, scope, two-week outcomes, setup, repository map, and collaboration workflow.
- `TRACKER.md`: shared task board for the five initial exploration workstreams.
- `notes/literature.md`: evidence tables for papers, datasets, baselines, tools, bottlenecks, and candidate questions.
- `notes/meetings.md`: reusable chronological meeting and decision record.
- `notes/experiments.md`: reusable experiment record with deployment-relevant metrics.
- `code/README.md`: neutral guidance for future source code and acquisition/deployment utilities.
- `data/README.md`: dataset handling, provenance, checksum, and manifest guidance.
- `.gitignore`: exclusions for local, generated, sensitive, and heavyweight artifacts.
- `brief.md`: delete after its content is represented in `README.md`.

### Task 1: Create the Project Entry Point and Shared Tracker

**Files:**
- Create: `README.md`
- Create: `TRACKER.md`
- Delete: `brief.md`

**Interfaces:**
- Consumes: The project direction, motivation, scope, deliverables, uncertainties, and supervisor questions in the approved design and original exploration brief.
- Produces: Stable links to `TRACKER.md`, `notes/literature.md`, `notes/meetings.md`, and `notes/experiments.md`; the initial workstream names used by the research notes.

- [ ] **Step 1: Verify the starting state**

Run:

```powershell
@('README.md', 'TRACKER.md') | ForEach-Object { "$_ exists: $(Test-Path $_)" }
Get-Item 'brief.md' | Select-Object Name, Length
```

Expected: `README.md` and `TRACKER.md` report `False`; `brief.md` exists and has length `0`.

- [ ] **Step 2: Write `README.md`**

Create a concise project entry point containing:

```markdown
# Edge AI Palmprint Recognition — FYP Exploration

> Status: exploratory; the final research question, dataset, baseline model,
> and target edge platform have not been selected.

## Direction

Explore how palmprint recognition models can be deployed and optimized on
smartphones, Jetson platforms, or Raspberry Pi-class devices.

## Motivation

- Reduce inference latency and network dependency.
- Improve privacy and suitability for real-time authentication.
- Study trade-offs among accuracy, memory, power, robustness, and device limits.

## Two-Week Outcomes

1. Literature and technology map.
2. Shortlist of suitable datasets and evaluation protocols.
3. One baseline palmprint recognition model.
4. One target deployment platform.
5. Preliminary bottlenecks and measurable research questions.

## Exploration Scope

- Palmprint recognition pipelines, datasets, and baseline models.
- ONNX, TensorFlow Lite, Core ML, and TensorRT deployment options.
- Quantization, pruning, and knowledge distillation.
- Accuracy, latency, memory, power, and model-size measurements.

## Getting Started

1. Read and update [the tracker](TRACKER.md).
2. Record sources and comparisons in [the literature notes](notes/literature.md).
3. Record decisions in [the meeting notes](notes/meetings.md).
4. Record reproducible trials in [the experiment log](notes/experiments.md).
5. Keep source code in `code/`; keep only data instructions and small
   manifests in `data/`.

## Repository Map

| Path | Purpose |
| --- | --- |
| `TRACKER.md` | Shared responsibilities, progress, and next actions |
| `notes/literature.md` | Papers, datasets, baselines, tools, and research ideas |
| `notes/meetings.md` | Meeting notes, decisions, and action items |
| `notes/experiments.md` | Experiment configurations, results, and conclusions |
| `code/` | Source code and data/deployment utilities |
| `data/` | Acquisition guidance, metadata, checksums, and small manifests |

## Collaboration

- Assign every active task to one owner.
- Update the tracker in the same commit as material research notes.
- Record decisions with rationale so they can be revisited.
- Commit small, reviewable changes with descriptive messages.

## Questions for Supervisor Discussion

1. Does this direction fit the expected FYP scope?
2. Which sub-area best aligns with the lab's current work?
3. Which lab datasets, models, repositories, or devices can the team reuse?
4. What deliverable is expected for the next meeting?
5. When should the exploration narrow into a formal research question?
```

- [ ] **Step 3: Write `TRACKER.md`**

Create the initial tracker:

```markdown
# FYP Tracker

## Status Key

- `Not started`
- `In progress`
- `Blocked`
- `In review`
- `Done`

Replace `Member 1` and `Member 2` with the teammates' names when work is
assigned. Use ISO dates (`YYYY-MM-DD`) for due dates.

## Current Work

| Task | Owner | Priority | Status | Due date | Next action |
| --- | --- | --- | --- | --- | --- |
| Build literature and technology map | Member 1 | High | Not started | 2026-08-10 | Define search keywords and inclusion criteria |
| Shortlist datasets and evaluation protocols | Member 2 | High | Not started | 2026-08-10 | Compare access, size, capture conditions, and protocols |
| Select a baseline model | Unassigned | High | Not started | 2026-08-10 | Identify reproducible open-source candidates |
| Select a target deployment platform | Unassigned | High | Not started | 2026-08-10 | Inventory available hardware and toolchain constraints |
| Draft bottlenecks and research questions | Both | High | Not started | 2026-08-10 | Convert evidence into measurable trade-off questions |

## Blockers

| Blocker | Owner | Needed from | Next review |
| --- | --- | --- | --- |

## Recently Completed

| Task | Owner | Completion date | Evidence |
| --- | --- | --- | --- |
```

- [ ] **Step 4: Remove the superseded empty brief**

Delete `brief.md` only after checking that `README.md` includes the direction,
motivation, scope, outcomes, uncertainties, and supervisor discussion prompts.

- [ ] **Step 5: Validate links and required content**

Run:

```powershell
$required = @(
  'README.md',
  'TRACKER.md',
  'notes/literature.md',
  'notes/meetings.md',
  'notes/experiments.md'
)
$required | ForEach-Object { "$_ referenced or planned: $((Get-Content -Raw 'README.md').Contains($_))" }
Select-String -Path 'TRACKER.md' -Pattern 'literature and technology map|datasets and evaluation protocols|baseline model|deployment platform|research questions'
Test-Path 'brief.md'
```

Expected: every required path is referenced or planned as `True`; five tracker
matches are printed; `brief.md` reports `False`.

- [ ] **Step 6: Commit the entry point and tracker**

```powershell
git -c safe.directory="E:/Steph's repos/fyp" add README.md TRACKER.md brief.md
git -c safe.directory="E:/Steph's repos/fyp" commit -m "docs: add FYP overview and tracker"
```

Expected: one commit containing the overview, tracker, and deletion of the
empty brief.

### Task 2: Create the Three Research Logs

**Files:**
- Create: `notes/literature.md`
- Create: `notes/meetings.md`
- Create: `notes/experiments.md`

**Interfaces:**
- Consumes: Workstream names and internal links established in Task 1.
- Produces: Stable Markdown templates linked by `README.md` and used as evidence from `TRACKER.md`.

- [ ] **Step 1: Verify that note files do not exist**

Run:

```powershell
@(
  'notes/literature.md',
  'notes/meetings.md',
  'notes/experiments.md'
) | ForEach-Object { "$_ exists: $(Test-Path $_)" }
```

Expected: all three paths report `False`.

- [ ] **Step 2: Write `notes/literature.md`**

Include a search-log table with query, source, filters, date, and result count;
a paper table with citation/link, task, dataset, method, metrics, edge
relevance, and follow-up; and comparison tables for datasets, baseline models,
deployment tools, and edge platforms. End with structured sections for
technical bottlenecks, candidate research questions, and unresolved questions.
Each table must include one instructional example row clearly marked
`Example — replace`.

- [ ] **Step 3: Write `notes/meetings.md`**

Start with the instruction `Add the newest meeting directly below this line.`
Then provide this reusable entry:

```markdown
## YYYY-MM-DD — Meeting title

**Attendees:** Member 1, Member 2  
**Purpose:** State the decision or outcome needed from this meeting.

### Agenda

1. Agenda item

### Discussion

- Topic:
  - Evidence:
  - Concerns:

### Decisions

| Decision | Rationale | Evidence/link |
| --- | --- | --- |

### Action Items

| Action | Owner | Due date | Tracker link/status |
| --- | --- | --- | --- |

### Questions for Supervisor

- Question:

### Next Meeting

- Proposed date:
- Required preparation:
```

- [ ] **Step 4: Write `notes/experiments.md`**

Start with metric conventions: use milliseconds for latency, MiB for memory,
watts or joules per inference for energy, megabytes for model size, and
`Not measured` when a metric is unavailable. Then include:

```markdown
## EXP-001 — Short descriptive title

**Date:** YYYY-MM-DD  
**Owner:** Member 1 or Member 2  
**Status:** Planned / Running / Complete / Invalid

### Question or Hypothesis

State one falsifiable question or expected trade-off.

### Configuration

| Field | Value |
| --- | --- |
| Code revision | Git commit hash |
| Dataset and split | Name and exact protocol |
| Preprocessing | Input size, normalization, ROI handling |
| Model | Architecture and checkpoint identifier |
| Optimization | None / quantization / pruning / distillation |
| Runtime | Framework, version, and execution provider |
| Hardware | Device, accelerator, CPU/GPU mode |
| Measurement method | Warm-up, run count, batch size, power tool |

### Results

| Metric | Result |
| --- | --- |
| Recognition metric | Not measured |
| Latency | Not measured |
| Peak memory | Not measured |
| Power or energy | Not measured |
| Model size | Not measured |

### Observations

- Observation:

### Conclusion

- Was the hypothesis supported?
- What decision does this result inform?
- What is the next action?

### Artifacts

- Code:
- Configuration:
- Raw output:
```

- [ ] **Step 5: Validate the templates**

Run:

```powershell
Select-String -Path 'notes/literature.md' -Pattern 'Papers|Datasets|Baseline Models|Deployment Tools|Edge Platforms|Technical Bottlenecks|Candidate Research Questions|Unresolved Questions'
Select-String -Path 'notes/meetings.md' -Pattern 'Agenda|Discussion|Decisions|Action Items|Questions for Supervisor|Next Meeting'
Select-String -Path 'notes/experiments.md' -Pattern 'Question or Hypothesis|Configuration|Results|Recognition metric|Latency|Peak memory|Power or energy|Model size|Conclusion|Artifacts'
```

Expected: every named section or metric produces a match.

- [ ] **Step 6: Commit the research logs**

```powershell
git -c safe.directory="E:/Steph's repos/fyp" add notes
git -c safe.directory="E:/Steph's repos/fyp" commit -m "docs: add research note templates"
```

Expected: one commit containing the three note files.

### Task 3: Add Code, Data, and Ignore Guidance

**Files:**
- Create: `code/README.md`
- Create: `data/README.md`
- Create: `.gitignore`

**Interfaces:**
- Consumes: The neutral code/data boundaries documented in `README.md`.
- Produces: Trackable directory guidance and enforceable exclusions for heavyweight or local artifacts.

- [ ] **Step 1: Verify that scaffold paths do not exist**

Run:

```powershell
@('code/README.md', 'data/README.md', '.gitignore') |
  ForEach-Object { "$_ exists: $(Test-Path $_)" }
```

Expected: all three paths report `False`.

- [ ] **Step 2: Write `code/README.md`**

Explain that this directory will contain source code, dataset acquisition
scripts, preprocessing, training/evaluation code, export utilities, deployment
benchmarks, and small configuration files. State that the team will choose a
package layout and dependency manager only after selecting the baseline and
target platform. Require commands and environment assumptions to be documented
next to runnable code.

- [ ] **Step 3: Write `data/README.md`**

Explain that raw and processed datasets must not be committed. Define the
trackable contents as download instructions, source URLs, license/access notes,
checksums, split definitions, and small CSV/JSON/YAML manifests. Require each
dataset record to include version, provenance, expected directory structure,
and preparation commands.

- [ ] **Step 4: Write `.gitignore`**

Use explicit sections covering:

```gitignore
# Operating system and editors
.DS_Store
Thumbs.db
.idea/
.vscode/
*.swp

# Secrets and local configuration
.env
.env.*
!.env.example

# Python
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/
.venv/
venv/
env/

# Jupyter
.ipynb_checkpoints/

# Local datasets (retain guidance and lightweight manifests)
data/*
!data/README.md
!data/**/*.csv
!data/**/*.json
!data/**/*.yaml
!data/**/*.yml

# Model checkpoints and exports
*.ckpt
*.pth
*.pt
*.onnx
*.tflite
*.mlmodel
*.mlpackage/
*.engine
*.plan

# Generated experiment artifacts
outputs/
results/
runs/
logs/
profiles/
*.log
```

- [ ] **Step 5: Test representative ignore behavior**

Create temporary representative paths under the repository, query Git's ignore
rules, and remove only those exact temporary paths:

```powershell
$testPaths = @(
  'data/raw/sample.bin',
  'data/manifest.csv',
  'model.onnx',
  '.venv/pyvenv.cfg',
  'outputs/result.json'
)
foreach ($path in $testPaths) {
  $parent = Split-Path $path
  if ($parent) { New-Item -ItemType Directory -Force $parent | Out-Null }
  New-Item -ItemType File -Force $path | Out-Null
}
git -c safe.directory="E:/Steph's repos/fyp" check-ignore -v @testPaths
git -c safe.directory="E:/Steph's repos/fyp" check-ignore 'data/README.md'
```

Expected: raw data, ONNX model, virtual environment file, and generated result
are ignored; `data/manifest.csv` and `data/README.md` are not ignored.

After verifying that every resolved path is inside
`E:\Steph's repos\fyp`, remove only:

```text
E:\Steph's repos\fyp\data\raw\sample.bin
E:\Steph's repos\fyp\data\manifest.csv
E:\Steph's repos\fyp\model.onnx
E:\Steph's repos\fyp\.venv\pyvenv.cfg
E:\Steph's repos\fyp\outputs\result.json
```

Remove any now-empty test-only directories `.venv/`, `outputs/`, and
`data/raw/`; do not remove `data/`.

- [ ] **Step 6: Commit code/data guidance and exclusions**

```powershell
git -c safe.directory="E:/Steph's repos/fyp" add code/README.md data/README.md .gitignore
git -c safe.directory="E:/Steph's repos/fyp" commit -m "chore: add code data and ignore guidance"
```

Expected: one commit containing both guidance files and `.gitignore`.

### Task 4: Verify the Completed Workspace

**Files:**
- Verify: `README.md`
- Verify: `TRACKER.md`
- Verify: `notes/literature.md`
- Verify: `notes/meetings.md`
- Verify: `notes/experiments.md`
- Verify: `code/README.md`
- Verify: `data/README.md`
- Verify: `.gitignore`

**Interfaces:**
- Consumes: All deliverables from Tasks 1–3.
- Produces: Evidence that the workspace matches the approved design and is ready for two-person Git collaboration.

- [ ] **Step 1: Verify the exact user-facing structure**

Run:

```powershell
Get-ChildItem -Force |
  Where-Object Name -NotIn @('.git', 'docs') |
  Select-Object Name, Mode
Get-ChildItem -File notes, code, data | Select-Object FullName
```

Expected top-level user-facing entries: `.gitignore`, `README.md`,
`TRACKER.md`, `notes`, `code`, and `data`. Expected nested files: the three
note files and the two directory README files.

- [ ] **Step 2: Verify all local Markdown links**

Extract the relative Markdown targets from `README.md`, resolve them against
the repository root, and assert that each target exists:

```powershell
$content = Get-Content -Raw 'README.md'
$links = [regex]::Matches($content, '\[[^\]]+\]\(([^)]+)\)') |
  ForEach-Object { $_.Groups[1].Value }
$links | ForEach-Object {
  if (-not (Test-Path $_)) { throw "Broken local link: $_" }
  "OK: $_"
}
```

Expected: every link prints `OK` and the command exits successfully.

- [ ] **Step 3: Verify the worktree and recent commits**

Run:

```powershell
git -c safe.directory="E:/Steph's repos/fyp" status --short
git -c safe.directory="E:/Steph's repos/fyp" log --oneline --decorate -5
```

Expected: no unintended working-tree changes; the log shows the design, plan,
overview/tracker, note-template, and code/data guidance commits.

- [ ] **Step 4: Record completion**

If plan checkbox updates are being tracked during execution, mark all completed
steps and commit only the plan update:

```powershell
git -c safe.directory="E:/Steph's repos/fyp" add docs/superpowers/plans/2026-07-27-fyp-exploration-workspace.md
git -c safe.directory="E:/Steph's repos/fyp" commit -m "docs: record workspace setup completion"
```

Expected: the implementation plan reflects actual execution without unrelated
changes.
