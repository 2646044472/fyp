# Palm Payment Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:subagent-driven-development` or `superpowers:executing-plans` to implement this task-by-task. Do not begin Phase 2 NIR, attack, fusion or PAD work while this plan is incomplete.

**Goal:** Convert the existing Raspberry Pi 5 1:1 palm verifier into a stable local 1:N palm-payment demo with unknown-user rejection, simulated balances, transaction records, explicit retry paths, automatic ROI and complete timing logs.

**Architecture:** Preserve the existing Fast-CC recognition baseline and Pi camera code. Refactor reusable biometric functions out of `palm_demo.py`, add a 1:N gallery layer, add a small SQLite payment subsystem, then connect them through one checkout workflow. Build the first complete payment transaction using the existing fixed guide ROI before replacing it with automatic ROI, so ROI development cannot block the vertical slice.

**Tech Stack:** Python 3, Picamera2, NumPy, SciPy, Pillow, SQLite, Fast-CC, built-in HTTP server, pytest.

**Spec:** `minutes/09-13-palm-payment-roadmap-update.md`

## Global Constraints

* Raspberry Pi 5 is the deployment target.
* Identification is 1:N; users do not enter an account identifier during payment.
* Fast-CC remains the Phase 1 matcher.
* System works locally/offline.
* Payment is simulated only.
* Unknown users must not be mapped to the nearest enrolled user automatically.
* Recognition policy must use one frozen system-level threshold, not a different threshold per user.
* ROI/acquisition failure must return `RETRY`, not a guessed identity.
* Raw camera frames remain unsaved by default.
* Existing consent/authorization guard remains.
* RGB and NoIR capture profiles must not be mixed.
* Templates remain local.
* A user's biometric templates and simulated account must be deterministically deletable.
* Log capture, ROI, feature extraction, 1:N search, payment and total transaction latency separately.
* Phase 1 makes no PAD, liveness, production payment, palm-vein or commercial-security claim.
* NIR, fusion, attack evaluation and PAD are explicitly outside this implementation plan.

---

# Target Phase 1 Flow

```text
camera preview
      │
      ▼
capture palm
      │
      ▼
ROI extraction
      │
      ├── invalid ───────► RETRY
      │
      ▼
Fast-CC feature
      │
      ▼
1:N gallery search
      │
      ├── score > threshold ─► UNKNOWN USER
      │
      ▼
identified user
      │
      ▼
simulated payment
      │
      ├── insufficient balance ─► FAILURE
      │
      ▼
transaction committed
      │
      ▼
SUCCESS
```

---

# Target Repository Structure

Do not reorganize the whole repository.

Extend only `code/palm_demo/`:

```text
code/palm_demo/
├── palm_demo.py
├── debug_ui.py
├── palm_payment_ui.py          NEW
│
├── models.py                   NEW
├── camera.py                   NEW
├── roi.py                      NEW
├── biometric.py                NEW
├── templates.py                NEW
├── gallery.py                  NEW
├── payment.py                  NEW
├── workflow.py                 NEW
│
├── tests/                      NEW
│   ├── conftest.py
│   ├── test_roi.py
│   ├── test_templates.py
│   ├── test_gallery.py
│   ├── test_payment.py
│   ├── test_workflow.py
│   └── test_deletion.py
│
├── runtime/
│   ├── templates/
│   ├── logs/
│   ├── palm_payment.sqlite3
│   └── identification_policy.json
│
├── tools/
├── install_pi.sh
├── requirements-dev.txt
└── ...
```

`palm_demo.py` remains the CLI entry point.

`debug_ui.py` remains useful as a diagnostic interface.

`palm_payment_ui.py` becomes the actual Phase 1 demonstration surface.

---

# Core Data Types

### `models.py`

Define explicit result objects so UI code does not need to understand recognition internals.

```python
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class ROIResult:
    status: Literal["OK", "RETRY"]
    roi: object | None
    reason: str | None
    quality: dict[str, float]
    elapsed_ms: float


@dataclass(frozen=True)
class IdentificationResult:
    status: Literal["MATCH", "UNKNOWN", "RETRY"]
    user_id: str | None
    score: float | None
    second_score: float | None
    search_ms: float
    reason: str | None = None


@dataclass(frozen=True)
class PaymentResult:
    status: Literal[
        "SUCCESS",
        "INSUFFICIENT_BALANCE",
        "ERROR",
    ]
    transaction_id: str | None
    balance_cents: int | None


@dataclass(frozen=True)
class CheckoutResult:
    status: Literal[
        "SUCCESS",
        "RETRY",
        "UNKNOWN_USER",
        "INSUFFICIENT_BALANCE",
        "FAILURE",
    ]
    user_id: str | None
    transaction_id: str | None
    score: float | None
    balance_cents: int | None
    reason: str | None
    timings: dict[str, float]
```

Money is always stored as integer minor units.

Example:

```text
MOP 20.00 = 2000
```

Never use floating-point money values.

---

# Task 0 — Repository Safety Before Feature Work

**Files:**

* Modify: `code/palm_demo/README.md`
* Review: repository history containing the exposed SSH credential

The current public repository contains a plaintext device password. Fix this before continuing normal development.

* [ ] Change the Pi account password locally:

```bash
passwd
```

* [ ] Remove the password from `README.md`.

Keep only:

```text
Host: <local Pi address>
Username: fyp
Authentication: local credentials configured on device
```

* [ ] Do not commit another device password, API key or secret.

* [ ] If the repository is intended to remain public, purge the old secret from Git history or treat it permanently as compromised.

Commit:

```bash
git add code/palm_demo/README.md
git commit -m "security: remove device credentials from documentation"
```

---

# Task 1 — Establish Automated Tests Before Refactoring

**Files:**

* Modify: `code/palm_demo/requirements-dev.txt`
* Create: `code/palm_demo/tests/conftest.py`
* Create: `code/palm_demo/tests/test_existing_pipeline.py`

Add:

```text
pytest>=8.0
```

to `requirements-dev.txt`.

### Characterization tests

Before moving code, preserve important current behaviour.

Test:

```python
def test_parse_crop_accepts_valid_fractional_box():
    assert palm_demo.parse_crop("0.1,0.2,0.8,0.9") == (
        0.1, 0.2, 0.8, 0.9
    )
```

Test deterministic normalization using a generated image:

```python
def test_crop_and_normalize_returns_128_square():
    image = make_test_image()

    roi, quality = palm_demo.crop_and_normalize(
        image,
        palm_demo.DEFAULT_CROP,
    )

    assert roi.shape == (128, 128)
    assert roi.dtype.name == "uint8"
    assert "contrast" in quality
    assert "sharpness" in quality
```

Test template filename sanitization.

Test that invalid zero-range images are rejected.

Run:

```bash
cd code/palm_demo
pytest -q
```

Expected:

```text
all tests pass
```

Commit:

```bash
git add requirements-dev.txt tests/
git commit -m "test: characterize existing palm demo pipeline"
```

---

# Task 2 — Extract Existing Biometric Code Without Changing Behaviour

This task is a refactor only.

Do not implement 1:N yet.

## 2.1 `camera.py`

Move camera acquisition from `palm_demo.py` and reusable live-feed code from `debug_ui.py`.

Provide:

```python
def capture_image(
    camera_index: int,
    width: int,
    height: int,
    warmup: float,
):
    ...
```

and:

```python
class CameraFeed:
    def frame(self):
        ...

    def jpeg_frame(self) -> bytes:
        ...

    def close(self) -> None:
        ...
```

Both `debug_ui.py` and later `palm_payment_ui.py` must use this implementation.

## 2.2 `biometric.py`

Move Fast-CC loading/extraction/scoring here.

Provide:

```python
def load_fastcc(baseline_path):
    ...
```

```python
def extract_feature(algorithm, roi):
    ...
```

```python
def score_probe(algorithm, probe, enrolled_features) -> float:
    scores = [
        float(algorithm.match(probe, candidate))
        for candidate in enrolled_features
    ]
    return float(np.median(scores))
```

This preserves the existing median-of-enrollment-samples behaviour.

## 2.3 `templates.py`

Move template-path and file persistence logic here.

Provide:

```python
class TemplateStore:
    def save(...):
        ...

    def load(...):
        ...

    def list_users(...):
        ...

    def delete(...):
        ...
```

A stored identity still consists of:

```text
<user>.npz
<user>.json
```

Do not migrate biometric features into SQLite.

### Acceptance test

The existing CLI commands must still work:

```bash
python palm_demo.py users
```

and existing 1:1 verification behaviour must remain unchanged.

Run:

```bash
pytest -q
```

Commit:

```bash
git add palm_demo.py debug_ui.py camera.py biometric.py templates.py tests/
git commit -m "refactor: extract reusable palm recognition services"
```

---

# Task 3 — Build the First 1:N Gallery Search

**Files:**

* Create: `gallery.py`
* Create: `tests/test_gallery.py`
* Create: `runtime/identification_policy.json` only at runtime
* Modify: `palm_demo.py`

This is the biggest functional change.

## Identification policy

Use one system-level policy:

```json
{
  "algorithm": "FastCC",
  "capture_profile": "rgb",
  "threshold": 0.28,
  "min_margin": 0.0,
  "frozen": false
}
```

`0.28` remains explicitly provisional until a development-session threshold is frozen.

Do not read thresholds from individual users during 1:N search.

## Interface

```python
class Gallery:
    def identify(
        self,
        probe_feature,
        capture_profile: str,
    ) -> IdentificationResult:
        ...
```

Algorithm:

```text
for every enrolled user with same capture profile:
    load enrollment features
    calculate median Fast-CC distance

sort ascending

best = smallest distance
second = second-smallest distance

if no users:
    UNKNOWN

if best > threshold:
    UNKNOWN

if min_margin > 0
and second - best < min_margin:
    RETRY

otherwise:
    MATCH(best_user)
```

Remember:

> Lower Fast-CC distance is better.

### Required tests

#### Correct person wins

```python
result = gallery.identify(probe)

assert result.status == "MATCH"
assert result.user_id == "stephen"
```

#### Unknown user stays unknown

```python
result = gallery.identify(unknown_probe)

assert result.status == "UNKNOWN"
assert result.user_id is None
```

#### Nearest identity is not automatically accepted

Construct:

```text
Stephen 0.34
Bankey  0.42
threshold = 0.28
```

Expected:

```text
UNKNOWN
```

not:

```text
Stephen
```

#### Profile isolation

An RGB probe must not search `noir-ir` templates.

Run:

```bash
pytest tests/test_gallery.py -v
```

Commit:

```bash
git add gallery.py tests/test_gallery.py palm_demo.py
git commit -m "feat: add open-set 1-to-N palm identification"
```

---

# Task 4 — Get the First End-to-End Transaction Working

Before building automatic ROI, complete the first vertical slice using the existing fixed ROI.

This proves the architecture.

## 4.1 Create SQLite payment storage

**Files:**

* Create: `payment.py`
* Create: `tests/test_payment.py`

Database:

```text
runtime/palm_payment.sqlite3
```

Schema:

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE accounts (
    user_id TEXT PRIMARY KEY,
    balance_cents INTEGER NOT NULL CHECK(balance_cents >= 0),
    FOREIGN KEY(user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);

CREATE TABLE transactions (
    transaction_id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL UNIQUE,
    user_id TEXT NOT NULL,
    amount_cents INTEGER NOT NULL CHECK(amount_cents > 0),
    balance_before_cents INTEGER NOT NULL,
    balance_after_cents INTEGER NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(user_id)
        REFERENCES users(user_id)
);
```

## Payment API

```python
class PaymentService:
    def create_account(
        self,
        user_id: str,
        display_name: str,
        initial_balance_cents: int,
    ) -> None:
        ...
```

```python
def pay(
    self,
    user_id: str,
    amount_cents: int,
    request_id: str,
) -> PaymentResult:
    ...
```

Payment must execute within one SQLite transaction.

Required behaviour:

```text
balance = 10000
payment = 2000

→ balance_after = 8000
```

Insufficient balance:

```text
balance = 1000
payment = 2000

→ no deduction
→ INSUFFICIENT_BALANCE
```

Repeated `request_id` must not deduct twice.

Run:

```bash
pytest tests/test_payment.py -v
```

Commit:

```bash
git add payment.py tests/test_payment.py
git commit -m "feat: add simulated palm payment ledger"
```

---

# Task 5 — Connect Recognition to Payment

**Files:**

* Create: `workflow.py`
* Create: `tests/test_workflow.py`

Provide:

```python
class PalmPaymentWorkflow:
    def checkout(
        self,
        image,
        amount_cents: int,
        request_id: str,
    ) -> CheckoutResult:
        ...
```

Workflow:

```text
image
 ↓
ROI
 ↓
Fast-CC feature
 ↓
Gallery.identify()
 ↓
MATCH?
 ├── no / RETRY   → RETRY
 ├── no / UNKNOWN → UNKNOWN_USER
 │
 yes
 ↓
PaymentService.pay()
 ↓
SUCCESS / INSUFFICIENT_BALANCE
```

The payment service must never receive a user ID until identification succeeds.

### Required integration tests

Successful flow:

```python
result = workflow.checkout(...)

assert result.status == "SUCCESS"
assert result.user_id == "stephen"
assert result.transaction_id is not None
```

Unknown flow:

```python
result = workflow.checkout(unknown_image, ...)

assert result.status == "UNKNOWN_USER"
assert transaction_count() == 0
```

ROI failure:

```python
result = workflow.checkout(bad_image, ...)

assert result.status == "RETRY"
assert transaction_count() == 0
```

Insufficient funds:

```python
assert result.status == "INSUFFICIENT_BALANCE"
```

Run:

```bash
pytest tests/test_workflow.py -v
```

Commit:

```bash
git add workflow.py tests/test_workflow.py
git commit -m "feat: connect palm identification to simulated checkout"
```

At this point the project has its first complete transaction.

Do not begin NIR work.

---

# Task 6 — Turn the Browser Demo into Palm Payment

Keep `debug_ui.py` for engineering diagnostics.

Create:

```text
palm_payment_ui.py
```

## Normal payment screen

It should contain only:

```text
PALM PAYMENT

[ live camera ]

Place your palm inside the guide

Item: Demo Purchase
Amount: MOP 20.00

[ PAY WITH PALM ]
```

No:

```text
username
user ID
account number
identity dropdown
```

## UI states

### READY

```text
Place your palm
```

### SCANNING

```text
Identifying...
```

### SUCCESS

```text
Payment successful

Welcome, Stephen
MOP 20.00 paid
Balance: MOP 80.00
```

### UNKNOWN

```text
Palm not recognised
No payment was made
```

### RETRY

```text
Unable to read palm
Please reposition your hand and try again
```

### INSUFFICIENT BALANCE

```text
Payment declined
Insufficient simulated balance
```

## Admin route

Provide a separate:

```text
/admin
```

for:

```text
enroll user
set display name
set/top-up simulated balance
view users
view transaction history
delete user
```

The administrator may enter user IDs.

The payment user may not.

### API routes

Suggested minimum:

```text
POST /api/checkout
POST /api/admin/enroll
POST /api/admin/topup
DELETE /api/admin/users/<id>
GET  /api/admin/users
GET  /api/admin/transactions
```

Commit:

```bash
git add palm_payment_ui.py
git commit -m "feat: add local palm payment web interface"
```

---

# Task 7 — Replace Fixed Crop With Explicit Automatic ROI

Only start this after Task 5 has produced a complete transaction.

The existing fixed crop remains available as:

```text
--roi-mode fixed
```

for debugging.

The normal demo becomes:

```text
--roi-mode auto
```

## `roi.py`

Define:

```python
class FixedGuideROI:
    def extract(self, image) -> ROIResult:
        ...
```

and:

```python
class AutomaticPalmROI:
    def extract(self, image) -> ROIResult:
        ...
```

## First automatic implementation

Do not introduce a neural ROI model.

Use the constrained physical demo setup.

Process:

```text
current frame
   │
   ▼
compare with calibrated empty background
   │
   ▼
foreground hand mask
   │
   ▼
largest connected component
   │
   ▼
validate hand area / borders
   │
   ▼
canonical orientation
   │
   ▼
estimate central palm area
   │
   ▼
128 × 128 normalized ROI
```

SciPy already provides:

```python
scipy.ndimage.label
scipy.ndimage.binary_opening
scipy.ndimage.binary_closing
scipy.ndimage.distance_transform_edt
```

so no new computer-vision dependency is required initially.

## Failure conditions

Return `RETRY` when:

```text
no foreground object
multiple similarly large objects
hand too small
hand clipped by frame border
palm centre cannot be determined
ROI falls outside image
contrast below minimum
sharpness below minimum
```

Never silently switch to a guessed crop.

## Tests

Use generated masks/images for:

```text
centred hand-like foreground
empty frame
object too small
object touching image edge
blurred crop
low contrast
```

Run:

```bash
pytest tests/test_roi.py -v
```

Then compare on actual Pi captures:

```text
fixed ROI
vs
automatic ROI
```

Before making automatic ROI default.

Commit:

```bash
git add roi.py tests/test_roi.py
git commit -m "feat: add automatic palm ROI with retry states"
```

---

# Task 8 — Complete Enrollment and Deterministic Deletion

Enrollment must create both:

```text
biometric template
simulated account
```

but keep their storage technically separate.

Provide a workflow:

```python
def enroll_user(
    user_id: str,
    display_name: str,
    captures,
    initial_balance_cents: int,
):
    ...
```

Required sequence:

```text
capture several samples
→ validate every ROI
→ extract templates
→ write template files
→ create user/account
→ success
```

If enrollment fails before completion:

```text
do not leave a half-created account
```

## Deletion

Provide:

```python
def delete_user(user_id: str) -> None:
    ...
```

It must remove:

```text
runtime/templates/<user>.npz
runtime/templates/<user>.json
users row
accounts row
```

For transaction history, use one documented rule.

Recommended for the FYP demo:

> deletion removes biometric/account information while historical simulated transactions are deleted as well, because there is no financial/audit requirement to retain them.

Test:

```python
delete_user("stephen")

assert not template_store.exists("stephen")
assert not payment_service.user_exists("stephen")
assert not payment_service.account_exists("stephen")
assert payment_service.transactions_for("stephen") == []
```

Commit:

```bash
git add workflow.py templates.py payment.py tests/test_deletion.py
git commit -m "feat: add atomic enrollment and user deletion"
```

---

# Task 9 — Stage-Level Timing and Attempt Logs

The existing single `pipeline_ms` value is no longer sufficient.

Each checkout should measure:

```text
capture_ms
roi_ms
feature_ms
search_ms
payment_ms
total_ms
```

Example JSONL:

```json
{
  "event": "checkout",
  "attempt_id": "...",
  "result": "SUCCESS",
  "user_id": "stephen",
  "score": 0.184,
  "gallery_size": 12,
  "capture_profile": "rgb",
  "capture_ms": 73.4,
  "roi_ms": 18.1,
  "feature_ms": 21.7,
  "search_ms": 15.6,
  "payment_ms": 3.1,
  "total_ms": 139.8
}
```

For unknown users:

```json
{
  "result": "UNKNOWN_USER",
  "user_id": null
}
```

For ROI failure:

```json
{
  "result": "RETRY",
  "retry_reason": "HAND_CLIPPED"
}
```

Do not calculate energy from CPU utilization.

Energy remains unavailable unless measured directly in a later phase.

Commit:

```bash
git add workflow.py palm_demo.py tests/
git commit -m "feat: add stage-level palm payment timing logs"
```

---

# Task 10 — Freeze the 1:N Decision Rule

Before presenting the final Phase 1 demo, stop treating `0.28` as a magic constant.

Collect authorized development captures separately from final evaluation/demo captures.

Construct:

```text
mated scores
non-mated scores
```

for the actual Pi VIS capture setup.

Choose the policy using development data.

Write:

```json
{
  "algorithm": "FastCC",
  "capture_profile": "rgb",
  "threshold": 0.XX,
  "min_margin": 0.XX,
  "frozen": true,
  "frozen_at": "2026-XX-XX",
  "notes": "Selected using development identities/sessions only"
}
```

The final demonstration and evaluation must load this file and must not tune it further.

Important distinction:

```text
best user
```

does not mean:

```text
accepted user
```

Acceptance is always:

```text
best score
+
frozen acceptance rule
```

---

# Task 11 — Raspberry Pi 5 Phase 1 Acceptance Test

Test on the physical Pi.

Use at least:

```text
2+ enrolled users
1 unenrolled person
bad placement
insufficient balance
deleted user
restart
```

## Case A — Correct enrolled user

```text
Place palm
→ ROI succeeds
→ 1:N identifies correct account
→ MOP 20 simulated payment
→ balance decreases once
→ transaction stored
→ SUCCESS
```

## Case B — Different enrolled user

Must identify their account without the operator selecting their name.

## Case C — Unknown participant

```text
palm
→ gallery search
→ below acceptance rule
→ UNKNOWN USER
→ zero transactions created
```

## Case D — Bad capture

```text
bad position / clipped hand
→ RETRY
→ no gallery acceptance
→ no payment
```

## Case E — Insufficient balance

```text
identity accepted
→ payment rejected
→ balance unchanged
→ INSUFFICIENT BALANCE
```

## Case F — Restart

After reboot:

```text
users remain
templates remain
balances remain
transactions remain
identification still works
```

## Case G — Deletion

After deleting a user:

```text
template gone
account gone
person no longer authenticates as that user
```

---

# Phase 1 Definition of Done

Phase 1 is complete only when this works on Raspberry Pi 5:

```text
Enrolled participant
      │
      ▼
shows palm
      │
      ▼
automatic ROI
      │
      ▼
1:N search
      │
      ▼
identity accepted
      │
      ▼
MOP 20 simulated payment
      │
      ▼
balance updated
      │
      ▼
transaction logged
      │
      ▼
SUCCESS
```

and independently:

```text
Unenrolled participant
      │
      ▼
shows palm
      │
      ▼
1:N search
      │
      ▼
UNKNOWN USER
      │
      ▼
no payment
```

and:

```text
Poor capture
      │
      ▼
ROI/acquisition gate
      │
      ▼
RETRY
      │
      ▼
no payment
```

---

# Explicitly Do Not Implement Yet

Until the Phase 1 acceptance test passes, do not spend implementation time on:

```text
850 nm NIR
palm vein recognition
RGB/NIR fusion
PAD
liveness
print attacks
screen/replay attacks
adversarial patches
learned fusion
PPNet migration
new recognition networks
cross-device work
cloud backend
real payment APIs
template protection
```

Those belong after the Palm Payment MVP.

---

# Recommended Commit Sequence

```text
security: remove device credentials from documentation

test: characterize existing palm demo pipeline

refactor: extract reusable palm recognition services

feat: add open-set 1-to-N palm identification

feat: add simulated palm payment ledger

feat: connect palm identification to simulated checkout

feat: add local palm payment web interface

feat: add automatic palm ROI with retry states

feat: add atomic enrollment and user deletion

feat: add stage-level palm payment timing logs

docs: document Phase 1 demo protocol
```

Each commit should leave the repository runnable.

---

# Critical Path

The shortest route from today's repo to the FYP demo is:

```text
existing 1:1 verifier
        ↓
refactor reusable matcher
        ↓
1:N gallery + UNKNOWN
        ↓
SQLite balance
        ↓
checkout workflow
        ↓
Palm Payment UI
        ↓
──────── FIRST COMPLETE TRANSACTION ────────
        ↓
automatic ROI
        ↓
deletion + detailed logs
        ↓
freeze threshold
        ↓
Pi 5 acceptance test
        ↓
PHASE 1 COMPLETE
```

The project-management rule is:

> **Get the first complete payment transaction working before improving ROI or touching research extensions.**

That first vertical slice is the highest-priority engineering milestone.
