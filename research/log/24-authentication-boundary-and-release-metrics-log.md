# Authentication Boundary and Release-Metric Reading Log

Last updated: 2026-08-21. This log audits NIST SP 800-63B-4, ISO/IEC 30107-3:2023, and NIST SP 800-116r1 to stop the project from confusing a local biometric comparison, an authorization claim, a possession factor, and an end-to-end secure physical-access system.

## Question

The candidate workflow says that a work order, QR code, or card presents an identity claim and the Pi confirms the claimed palm locally. What does that actually prove, what does PAD cover, and what must remain outside the FYP claim?

## Primary material inspected

| Source | What was read | Directly usable conclusion | What it does not establish for this FYP |
| --- | --- | --- | --- |
| [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html), biometric section | Current normative guidance around biometric accuracy, PAD, endpoint integrity, local comparison, alternatives, and data handling | A biometric match is probabilistic and does not itself cover active impersonation. NIST treats biometrics as an activation factor inside a multi-factor authenticator with a physical authenticator, requires a non-biometric alternative, requires a fixed threshold, distinguishes FMR/FNMR from attack acceptance, and says local comparison is preferable where central comparison creates a larger-scale attack surface. It also says verifier trust in the sensor/endpoint matters for injection attacks. | It is a digital-identity guideline, not Macau law, a certification of this prototype, a palmprint-specific performance target, or a mandate that the work-order workflow be labelled MFA. |
| [ISO/IEC 30107-3:2023](https://www.iso.org/standard/79520.html) public abstract | Current standard scope and reporting boundary | PAD testing/reporting concerns presentation attacks at the biometric capture device; it does not standardize a particular countermeasure or assess whole-system security. | ISO scope does not cover a compromised Pi, camera injection, template-store compromise, relay, QR/work-order authorization, tailgating, or organizational access policy. |
| [NIST SP 800-116r1](https://csrc.nist.gov/pubs/sp/800/116/r1/final) publication record/abstract | Facility-access scope and risk-based selection framing | A facility access control system is a risk-based combination of PIV credential mechanisms, PACS, validation, and organizational controls; biometrics and smart cards are separate technologies in that system. | It is a US federal PIV guide, not a proof that a low-cost palm reader should replace a card, guard, or QR procedure. |

## Reasoning change

1. **A work-order QR is not automatically a possession factor.** In this project it is an already-authorized, pseudonymous claim lookup. Unless a future implementation gives it a protected, non-transferable secret and authenticates its issuance/presentation path, do not write “two-factor authentication” or “MFA.” The defensible phrase is **claim-bound local `1:1` biometric confirmation**.
2. **PAD is one release gate, not the security claim.** PAD covers the physical presentation layer. The measured system-level outcome should be `IAPMR`: an attack passes both the capture gate/PAD and the claimed-template matcher at a frozen threshold. That is still not a result for software injection, sensor emulation, relay, tampering, or tailgating.
3. **The edge claim needs an endpoint boundary.** Local inference may reduce raw biometric traffic and centralized matching exposure, but a Raspberry Pi prototype without sensor authentication, signed metadata/attestation, protected boot/storage, and tamper analysis cannot claim endpoint integrity or injection resistance.
4. **Fallback is not an afterthought.** NIST requires a non-biometric alternative in its own digital context. For this project, a clearly documented human/manual fallback and its timing are a mandatory story/evaluation field, not an optional recovery flow.
5. **No borrowed deployment target.** NIST's reported FMR, FNMR, and IAPAR figures are deployment guidance for its scope, not performance pass thresholds for an undergraduate palm prototype. This project reports estimates and intervals under its own small, explicit protocol; it does not claim conformance.

## Resulting wording

Use:

> An authorized work-order record supplies a time-bounded identity claim. The device performs a local `1:1` palm comparison and optional capture-side PAD/risk gate. A successful result is only a prototype-level confirmation under the recorded hardware, attack, and threshold conditions; authorization remains the upstream system's responsibility, and a human fallback remains available.

Do not use:

- “MFA” or “two-factor” for QR/work order plus palm;
- “secure access control system,” “anti-injection,” “relay resistant,” or “full liveness”;
- a NIST/ISO reference as a claim of conformance or a Macau requirement;
- `APCER` alone as the probability that the door/tool workflow would release an attack.

## Concrete protocol additions

For every release decision, record separately:

| Layer | Required field | FYP status |
| --- | --- | --- |
| Authorization | signed/versioned claim record, resource, start/end, expiry, sync status | In scope as a prototype workflow boundary |
| Capture/PAD | PAIS/specimen/material/output/capture/session, gate decision, actual illumination state | In scope for approved sensor-side PA experiments |
| Matcher | claimed template version, score, frozen threshold, match decision | In scope |
| Final workflow | release/retry/manual fallback and end-to-end interaction time | In scope |
| Endpoint/system attacks | camera injection, sensor emulation, relay, OS compromise, template extraction, tailgating | Explicitly out of scope; describe as residual risk |

## Open evidence

- Whether a target facility can legally and operationally issue a signed, time-bounded claim record to a local device is a field-interview/system-design question, not answered by NIST.
- Whether the laboratory Pi exposes device identity, secure boot, hardware-backed storage, or sensor attestation must be checked against the actual hardware. Do not infer it from using edge inference.
- Palmprint-specific PAD targets and required attack species must be decided from the agreed threat model and available approved samples; the standards do not choose them.
