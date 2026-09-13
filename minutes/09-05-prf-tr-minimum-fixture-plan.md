# PRF-TR Minimum Fixture Plan

**Date:** 2026-09-05  
**Purpose:** Establish whether the conditional PRF-TR direction can generate
repeatable physical cells with the existing Pi/camera inventory and inexpensive
non-specialist hardware. This is a feasibility plan, not an experiment result
or a purchase requirement.

## Constraint

The useful hardware budget is below the user's stated `1k` threshold. Exact
currency, suppliers, and prices are intentionally not assumed. Each proposed
item must either create a controlled physical intervention or make the episode
cost/fixture state observable. No extra camera, larger model, or generic
sensor is required for the first gate.

## Bench layout

Use a fixed optical path:

```text
camera mount  ->  transparent-cover holder  ->  printed target plane
                     ^
                     |
              controlled visible lamp
```

The camera, cover, target, and lamp must have fixed reference marks. A black,
matte surround removes changing background reflections. The target remains
static; the first gate makes no multi-camera synchronization or motion claim.

## Minimum components

| Component | Role in the study | Requirement | Not a contribution |
| --- | --- | --- | --- |
| Rigid camera/phone mount or small tripod | Holds camera geometry fixed and permits documented remounts | Height and angle can be marked/repeated | The mount itself |
| Flat target holder | Holds printed marker at a fixed plane | Supports target lots and exact target distance | A QR/AprilTag reader |
| Transparent-sheet holder | Applies a labelled physical optical condition | Can swap cover material, angle, and distance reproducibly | A generic glare-removal technique |
| Clear acrylic/PET sheets and one removable protective film | Physical cover/reflection cells | Label each material/lot; do not call it a universal cover family | Material classification |
| Dimmable visible LED panel or stable lamp plus diffuser | High/low-light and glare geometry cells | Fixed output settings are logged; do not use auto exposure as a label | Adaptive exposure |
| Matte black board/cloth | Limits uncontrolled background reflection | Remains in the fixture log | Image-quality improvement |
| Printed non-personal marker registry | Independent exact payload truth | Generate expected payloads before capture | New marker decoding |
| Optional inline USB power meter | Charges energy only if measurement is repeatable enough | Use as a covariate/secondary cost until validated | Power-aware vision method |
| Optional inexpensive lux meter | Records visible-light covariate only | Never treat equal lux as equal spectrum or scene truth | A light-based router |

The existing Pi, Camera NoIR v2, and any optional IR illumination may be
included as named capture paths after individual static-capture bring-up. The
first gate uses the confirmed NoIR path; it can compare physical and digital
conditions without any additional camera.

## First four physical cells

The cells must be assigned by the fixture log before data collection. They are
not labels inferred from the image.

| ID | Intervention | What changes physically | Digital analogue to test later |
| --- | --- | --- | --- |
| `C0_clean_bright` | No cover; stable high visible light | Baseline optical path | None; source captures |
| `C1_clean_low_light` | Fixed lower visible-light output | Photon count / sensor noise regime | Brightness reduction plus sensor-like noise |
| `C2_cover_glare` | Clear sheet at a marked angle with off-axis lamp | Reflection, local saturation, transmission path | Brightness/blur/masking alone, then declared digital glare proxy |
| `C3_held_out` | New lamp posture, remount, cover lot, or fixed cover distance | A blocked physical configuration not used for thresholds | No tuning after observing it |

Do not include water droplets, dirt, arbitrary camera defocus, dynamic targets,
or real field weather in the first gate. Those multiply confounders without
improving the central physical-versus-digital comparison.

## One-week feasibility sequence

1. Assemble the dry fixture with `C0_clean_bright`; record camera path,
   manual/locked exposure and white-balance state, distance, lamp output, and
   target registry.
2. Repeat ten static captures after a full remount. If clean exact-payload
   truth is not stable, stop before introducing faults.
3. Stage `C1_clean_low_light` and `C2_cover_glare`; photograph the fixture
   state and keep the physical labels outside policy inputs.
4. Freeze one `C3_held_out` choice before looking at scored results.
5. Run the fixed baseline actions from the PRF-TR schema. Do not train a model
   or tune transformations in this week.
6. Pass only if the four states can be recreated from the log and the registry,
   capture manifest, and cost ledger remain separate from the deployable policy.

## Immediate stop rules

- Clean control decoding varies under a supposedly fixed mount/light state.
- Auto exposure, white balance, or target geometry cannot be logged or held
  stable enough to explain capture changes.
- The cover/glare state cannot be reproduced independently of image output.
- The confirmed NoIR path cannot produce usable captures under a controlled
  visible-light setup; stop rather than adding an unverified camera comparison.
- Added equipment supplies only another image-quality proxy rather than a
  controlled physical factor or independent record of the fixture/cost.

## Gate outcome

Passing this plan proves only that PRF-TR has a repeatable benchtop apparatus.
It does not establish a digital-to-physical rank inversion, a field workflow,
or a paper contribution. Failure is still useful: it means the project should
not claim a physical-condition evaluation before the fixture problem is solved.
