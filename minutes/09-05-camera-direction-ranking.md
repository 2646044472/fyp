# Edge + Camera Direction Ranking

**Date:** 2026-09-05  
**Decision status:** No thesis is locked. This memo ranks the remaining
camera candidates after direct-neighbor correction; it does not promote a
paper claim.

## Decision investigated

Which remaining edge-camera problem has the strongest combination of a real
decision story, auditable distinction, undergraduate feasibility and useful
failure path?

## Rank 1: PRF-TR / physical-versus-digital action-risk audit

**Question.** For a fixed non-personal visual record, do digital brightness,
blur, noise, masking and missing-frame tests preserve the cost-risk ordering
of `retain`, `reacquire` and `unknown/review` on held-out physical optical
conditions?

**Why it ranks first.** It remains the most coherent finite evaluation object:
an independent exact-payload oracle, preregistered physical cells, actual
capture costs and a valid null result. It has a credible maintenance/inspection
record story, although that story is motivation rather than a claimed local
deployment.

**Why it is still only Amber, now weaker.** Generic synthetic-versus-real
corruption, quality-aware inspection and acquire/abstain actions have direct
neighbors. Krumstroh et al. (VR/AR 2025) additionally compare ArUco tracking
in a physical rig and Blender digital twin across cameras, so a marker
physical-versus-simulation comparison is already a demonstrated evaluation
pattern. The residual can justify a bounded FYP only if a blocked physical
session changes the risk--cost frontier after fixed-two-shot, standard
IQA/scalar and always-review baselines. It should not be sold as a likely
publication before that effect exists.

**Feasibility.** High: inert printed target, existing RGB/NoIR pair, cheap
fixture, no personal data, no partner or training data required.

## Rank 2: RAW-JPEG evidence sufficiency

**Question.** Does a same-exposure RAW scalar reduce exact-record false-retain
beyond JPEG quality/decoder evidence when RAW unpacking, bytes, time and energy
are charged?

**Why it is second.** It has a cleaner systems observation boundary than an
ordinary image-quality score and could yield a specific negative result: JPEG
is enough for the stated task. It is not an edge RAW detector or a general
RAW-robustness claim.

**Why it cannot lead yet.** RAW detection, robust RAW vision and RAW-domain
uncertainty are direct method-family collisions. The camera/API must also
produce a stable same-exposure RAW/JPEG pair; otherwise the comparison is
confounded before research begins. Its real-world story is weaker than Rank 1.

**Feasibility.** Medium: depends on unverified raw capture path and accurate
cost accounting.

## Rank 3: IR or polarization value of information

**Question.** For one named physical optical ambiguity, does one fixed IR-on
or polarizer observation reduce false retain at equal capture cost relative to
fixed RGB, fixed filter, fixed two-shot and scalar-quality controls?

**Why it is third.** The demo is visually intuitive and uses the owned NoIR
path. It has an independent fixture label and a clear decision cost.

**Why it is not a primary FYP.** Active illumination, adaptive acquisition,
transparent-material inspection and polarization-based glare handling have
strong direct neighbors. With a fixed action and one surface family, it is more
likely to become a configuration characterization than an independent CS
contribution.

**Feasibility.** Medium-high: low hardware cost, but extra optical controls
and careful exposure logging are mandatory.

## Rejected framing

"Photo quality admission" is not an independent candidate. Dong, Lu and Chen,
*Image Quality Assessment for Construction E-inspection: A Case Study* (2023,
DOI 10.1007/978-981-99-3626-7_10) is a strong direct neighbor for a generic
e-inspection IQA story. The full non-open chapter has not yet been read, so its
exact action policy is [GAP], but ordinary edge IQA remains a required baseline
rather than a contribution.

## Recommended next research gate

Keep the story of Rank 1, but make no novelty claim yet. Before any thesis lock,
freeze a one-page pilot with:

1. one non-personal record object and independently generated payload oracle;
2. four named physical optical cells;
3. fixed RGB, fixed NoIR+IR, fixed two-shot, standard IQA/scalar and
   always-review controls;
4. source/held-out session split and measured false-retain, latency, bytes and
   energy;
5. a predeclared outcome rule: promote only for repeatable held-out action-rank
   difference; otherwise report a bounded null and choose another topic.

PROMOTE only conditionally for Rank 1; HOLD Rank 2 and Rank 3; KILL generic
photo-IQA-as-topic.
