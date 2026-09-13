# Edge-Camera Story Shortlist (2026-09-04)

## Decision

Choose a default real-world story for an `edge + camera` FYP before selecting
RAW, NoIR, IR, polarization, a decoder, or a model.

## Candidate stories

| Story | Actor and local decision | Concrete error consequence | Independent truth | Feasibility | Status |
| --- | --- | --- | --- | --- | --- |
| Field maintenance record release | Technician captures a non-personal asset/check marker and chooses `retain`, `reacquire`, or `unknown/review`. | Wrong asset, part, or work-order record; later rework and audit delay. | Pre-generated marker payload and independent decoder/registry. | High: static fixture can emulate low light, cover glare, remount and material changes. | Default working story. |
| Refurbishment serial-number intake | Repair-centre operator binds a returned device to a serial/return label before diagnosis. | Diagnostic result or warranty history is attached to the wrong device. | Pre-registered serial/marker registry. | High, but use synthetic/non-production labels only. | Strong alternative. |
| Laboratory sample-label intake | Technician records a non-personal sample identifier from a bag, vial, or test coupon. | Measurement result is associated with the wrong sample; retest or recollection is required. | Pre-registered sample-label registry. | Medium: packaging, condensation and handling fixture are required. | Alternative if laboratory access exists. |
| Asset handover | Lab or school staff records a non-personal asset tag during issue/return. | Handover and maintenance history are attached to the wrong asset. | Pre-registered asset-tag registry. | High, but lower operational impact than maintenance/return. | Demo-friendly fallback. |

## Recommended default

Use **field-maintenance record release**. It has the cleanest edge decision:

```text
Capture a non-personal identifier locally
-> retain the record / reacquire once / mark unknown for review
```

The study verifies only exact identifier reading. It does not prove that a
repair occurred, a part was installed, a person is authorised, or a safety
condition is satisfied.

## Research problem carried by the story

Laboratory teams often evaluate a camera policy with digital brightness, blur,
noise, masking, and frame-loss transformations. The research question is
whether those cheap digital tests safely choose the local release action under
held-out physical optical conditions such as low light, reflection, transparent
covers, and remount/path changes.

## Reality grounding

Official field-service documentation is used only to establish that offline
field work, asset/barcode lookup, local task handling, and later
synchronization are real workflow components:

- SAP Asset Manager scanning and offline work-order features are recorded in
  `research/active/33-prf-tr-research-prospectus.md`.
- Salesforce Field Service Mobile and ServiceNow Field Service offline mobile
  documentation are recorded in the same prospectus.

Those sources do not establish a research gap, deployment approval, or a claim
that a bench proxy proves repair completion.

## Screening rule

Reject any future story that cannot name all four items:

1. the local actor;
2. the `retain / reacquire / unknown` decision;
3. the real cost of a wrong retain; and
4. an independent truth source unavailable to the policy at decision time.
