# Working Story: Edge Visual Record Binding for Monitoring Points

**Date:** 2026-09-05  
**Status:** Story selected for the PRF-TR bench proxy only. It is not proof of
an adopted Macao deployment, a technical contribution, or a thesis lock.

## The real-world situation

A facilities or heritage-monitoring technician makes repeated visits to a
declared **monitoring point**: for example, a non-personal equipment location,
an environmental-observation point, or a fixed condition-photo position. Each
point carries a printed identifier. Before the technician's local observation
is appended to the visit log, the edge client must bind the capture to the
correct point identifier.

The first capture is sometimes degraded by low light, transparent protective
covers, glare, water or a changed optical path. The client must decide one of:

1. `retain`: append a record for the decoded monitoring point;
2. `reacquire`: make one fixed additional capture;
3. `unknown/review`: do not append an automatically bound record.

## Concrete harm, without exaggeration

A false `retain` does **not** prove that the wrong physical condition was
observed or that maintenance was completed. It attaches an observation to the
wrong monitoring-point history. This can invalidate a later trend comparison,
force a manual audit, or require another visit. A needless `reacquire` costs
capture time and local energy; needless review consumes an operator's time.

The object of truth in the FYP is only exact identifier binding. Any claim about
heritage damage, moisture, equipment health, work completion, safety or legal
compliance is out of scope.

## Why this is a legitimate Macao-motivated story

- [K] The Macao World Heritage Monitoring Centre publicly describes systematic
  collection of site changes and environmental information, including the use
  of mobile applications and a long-term monitoring record.
- [K] Local asset-management marketing and an independently published
  property-management workflow show that non-personal facilities can carry
  unique QR identifiers that staff scan to retrieve or update maintenance data.
- [C] Together, these sources make a monitoring-point/asset-record binding
  workflow plausible. They do not demonstrate a partner, offline operation,
  optical-fault incidence, or demand for this Pi prototype.

## Research question that remains after the story

The study does not ask whether the client can decode a tag or assess photo
quality. It asks whether source-fitted **digital** fault tests preserve the
cost-risk ordering of `retain`, `reacquire` and `unknown/review` under held-out
**physical** optical conditions.

The tag is deliberately a truth oracle and a record-binding object. It is not
the claimed computer-vision innovation.

## Required wording for an advisor meeting

> We are not building a Macao heritage-monitoring system or a QR scanner. We
> use a monitoring-point record as a realistic bench proxy to ask whether
> digital camera-fault tests make the right local record-admission decision
> under physical optical failures.

## Evidence and limitations

- Macao Cultural Affairs Bureau World Heritage Monitoring Centre news release,
  2022-11-16: https://www.macauculture.gov.mo/en/News/detail/20784
- iN Systems (Macao) asset-management product page: https://insys.com.mo/en/application-services/asset-management-system-with-rfid.html
- HKEX property-management listing document, pp. 193-194: https://www1.hkexnews.hk/listedco/listconews/sehk/2021/0525/sehk21011301063.pdf
- The e-inspection IQA chapter by Dong, Lu and Chen (2023) is a strong generic
  neighbor. Standard IQA/re-capture must be a baseline. Its full non-open text
  still needs a task/action/limitation audit before it is used as a
  load-bearing collision.

## Decision

Use **monitoring-point record binding** as the first advisor-facing story for
Rank 1. Do not name a particular employer or claim field deployment. If an
advisor requires a partner-validated application rather than a bench proxy,
this story is insufficient and the project must seek a documented workflow
before locking the thesis.

PIVOT.
