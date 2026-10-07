# FYP_Minutes_PalmRecog_2026-09-04.md

**Group:** Biometric: Palm Recognition
**Supervisor:** Bob Zhang
**Date:** September 4, 2026
**Attendee:** Stephen, Bankey

---

#### 1. Ruled-Out Research Directions
The following areas were identified as not viable for the current scope of work and have been excluded:
- **Cross-Device Compatibility:** This includes all variations of cross-device scenarios, such as differing cameras and hardware boards.
- **End-to-End Attacks:** Due to the difficulty of achieving a sufficiently accurate printer for physical attacks, this direction is deprioritized. Existing work in this area focuses on software-based modification of palmprints to cause misidentification, which is outside our current scope.


#### 2. Recommended Path for FYP Demo
Upon discussion, the following strategic priorities have been set:
- **Prioritize Portability:** The primary goal is to create a portable system that surpasses the standalone WeChat Pay machines in terms of *convenience* and *deployment*.
- **Increase Model Accuracy:** Focus on improving the precision of the palm recognition algorithm to ensure reliable identification.
- **Enhance Model Robustness:** The system must perform reliably outside of controlled lab environments. This involves training the model to handle disturbances (e.g., the presence of rings) and adapting to various environmental settings.
- **Incorporate Multi-Modality Early:** Use the IR illumination not just for palmprint, but to also capture palm vein patterns. Consider if additional modalities (e.g., finger length ratios or dorsal hand features) can be extracted from the same camera feed without extra hardware.

#### 3. Potential Future Paths
Several avenues for future research and development were discussed:
- **Dorsal Hand Detection:** Exploring the use of hand-back (dorsal) detection for additional biometric data.
- **Edge Computing Integration:** Pivoting to leverage cameras and edge computing to improve processing speed and on-device AI capabilities.
- **Security & Attacks:** Investigating both physical attack vectors (e.g., spoofing) and algorithmic vulnerabilities to strengthen the system's security.
- **Human-Computer Interaction (HCI) Improvement:** Enhancing the user interface and overall user experience to make the system more intuitive.

#### 4. Next Stage Action Items
The immediate next steps to progress the project are:
- **Hardware Development:** Begin construction of the IR illumination system to enable a functional, demoable prototype.
- **Literature Review:** Conduct a comprehensive search and review of existing literature to identify specific research gaps and refine the problem statement for the next phase.