# Macau Edge-Camera Story Red Team (2026-09-04)

## User constraints reaffirmed

- The research object remains an edge node plus camera. Raspberry Pi and Camera NoIR v2 are available; inexpensive extra sensing or fixture parts are permitted only when they supply independent truth or a controlled intervention.
- The user asks for an actual problem/story, not another generic detector, camera demo, model swap, or a superficial Macao label.
- No personal-data workflow, legal-status inference, production safety actuation, or automatic public enforcement is in scope.

## Local stories with verified motivation

- [K] Macao's public-works authority reports that, during the 2026 rainy/typhoon season, it prioritises inspection and clearance of sewers, catch pits, open channels and pumping facilities in low-lying/flood-prone areas; post-typhoon clearance is a concrete operational workflow. Source: Macao DSOP, 2026-07-02, https://www.gov.mo/zh-hans/news/919586/.
- [K] Macao's World Heritage Monitoring Centre describes a workflow that collects site changes together with temperature, humidity, meteorology and other environmental information; humidity and rain are also documented conservation concerns in Macao. Sources: Cultural Affairs Bureau, 2022-11-16, https://www.macauculture.gov.mo/en/News/detail/20784 ; ICM restoration knowledge, https://www.icm.gov.mo/mhd10/e/RepairKnowledge .
- [K] Macao's food-waste-recycling pilot includes participating restaurants and a requirement to sort food waste and clean collection bins after collection. Source: Environmental Protection Bureau, retrieved 2026-09-04, https://www.dspa.gov.mo/richtext_foodwasterecycling.aspx?a_id=1528441021 .

## Direct-neighbour findings

### DRAIN-DETECT [KILL as a detector/system thesis]

- [K] Rowlatt et al., *Operational uncertainty in machine learning based debris block detection in urban waterways*, Cambridge Prisms: Water, 2026, analyse 1,089 real CCTV images of a Cardiff trash screen labelled `low risk / high risk / unknown risk`; fixed daily, water-level-triggered and manual captures occur under varying light and season. Logistic regression is broadly comparable with more complex vision models, with leading models over 80% accuracy. https://doi.org/10.1017/wat.2026.10018
- [K] Lorilla et al. (2026) already demonstrate a Raspberry Pi/webcam system with ultrasonic and water-level sensors classifying `clear / partially blocked / fully blocked`. https://ideas.repec.org/a/bjc/journl/v13y2026i5p3156-3167.html
- [K] Vandaele et al., *Automating Visual Blockage Classification of Culverts with Deep Learning*, Applied Sciences 2021, has an explicit visual blockage-classification endpoint. https://doi.org/10.3390/app11167561
- [KILL] A Macao story, a Pi, NoIR imagery, a water sensor, a dashboard, an `unknown` label, or another YOLO variant does not create a thesis distinction.

### WET-VIEW-IDENT [KILL as a primary direction]

**Candidate decision:** A drainage inspector seeing an apparent blockage in a post-rain image must choose `record possible scene obstruction`, `perform one declared independent check`, or `manual review`. The scientific object is not debris classification: can a physical optical-path condition (water/dirt on a protective window) and a real scene obstruction create matched visual evidence that reverses the action choice, and does one independently logged hydraulic witness repair that ambiguity?

- [K] Real droplet contamination substantially alters camera image quality and object-detection performance; Kim et al. (Applied Sciences 2025) report MTF50 loss varying with droplet amount/surface and major small-object degradation. https://doi.org/10.3390/app15052690
- [K] Camera-lens droplet detection/removal, depth-aware multi-view rain removal, and automatic lens-contamination cleaning are established direct families. Relevant direct works include You et al. (CVPR 2013), Jiang et al. (ICCV 2019), Kim et al. (Information 2024), and the 2026 light-field raindrop-removal work. A focus sweep, active cleaning routine, de-raindrop model, new droplet detector, or generic camera-health score is not an eligible positive contribution.
- [K] Iqbal et al., *Artificial Intelligence of Things (AIoT)-oriented framework for blockage assessment at cross-drainage hydraulic structures*, 2023, already combines camera visual blockage status with hydraulic inputs including water level, inlet discharge and surface velocity, and evaluates visual-only, hydraulic-only and hybrid hydraulic-blockage prediction. https://doi.org/10.1080/13241583.2023.2292608
- [K] Rowlatt et al. (2026) already combine the operational `low risk / high risk / unknown risk` vocabulary with fixed, water-level-triggered and manually requested camera captures in a real trash-screen workflow. https://doi.org/10.1017/wat.2026.10018.pr5
- [KILL] The proposed hydraulic “independent witness” is therefore an established hybrid blockage observation, while the optical-path branch is established camera-health/decontamination work. The exact wording of a scene/path ambiguity is not enough to make the combination a new contribution. Retain a paired obstruction-versus-window-contamination cell only as a nuisance-control lesson in another finite evidence study.

### HERITAGE-WET-CHANGE [KILL as ordinary vision thesis]

- [K] Recent work already targets heritage/facade moisture and deterioration with visible/infrared fusion, deep-learning segmentation, meteorology/microclimate inputs, and even Raspberry Pi 5 deployment. Examples include Wang et al., Journal of Building Engineering 2024 (IR-visible facade deterioration) https://doi.org/10.1016/j.jobe.2024.110122 and Wang et al., npj Heritage Science 2025 (Pi 5 heritage wall damage). https://doi.org/10.1038/s40494-025-01725-8
- [KILL] Do not frame an FYP as “use Pi/camera to detect Macao heritage dampness, cracks, salts or surface damage.” A new model or small local image collection would be a direct continuation.
- [PIVOT] The only remotely plausible residual is an evaluation boundary: whether a short-term wet/dry illumination cycle can be distinguished from permanent surface change with a declared follow-up action and independent materials truth. This needs heritage access and conservator-defined labels, so it is not currently feasible.

### OVI-ZERO [KILL as a primary direction]

**Candidate decision:** A vector-monitoring technician must decide whether a night-time trap observation is admissibly `empty`, requires a second controlled capture, or requires manual count. The target is false-empty release rather than insect detection/counting.

- [K] Smart camera traps, infrared insect monitoring, detection and counting are established method families; a conventional on-device insect detector is not eligible. The 2026 AIMS mosquito sentinel already performs local event triggering, standardized imaging, field deployment and hierarchical recognition under rain/humidity/salt exposure. https://doi.org/10.1038/s44172-026-00685-6
- [K] Image-quality/adequacy gating is also direct: Simoes et al., *AI-Powered Mobile Image Acquisition of Vineyard Insect Traps with Automatic Quality and Adequacy Assessment*, Agronomy 2021, evaluates focus, shadows/reflections, whole-trap coverage and automatic reacquisition on a 516-image field-plus-lab dataset. https://doi.org/10.3390/agronomy11040731
- [K] A trap's zero catch is not a population-absence observation. A 2026 ecology perspective formalises catch as abundance times movement, motivation, detection, retention and sampling geometry, and explicitly warns that zero catch can arise from low detection probability or unfavourable conditions. https://doi.org/10.3389/fevo.2026.1839762
- [KILL] The intended `empty / second capture / manual count` endpoint is simultaneously blocked by existing image-adequacy systems and by the biological non-identification of zero catch. A proxy target would also weaken the public-health story. Do not pursue it as a primary FYP.

### CLEAN-RECORD-NULL [KILL as a primary direction]

**Candidate decision:** A facilities or food-waste-bin operator wants to retain a `visually clean` post-cleaning record, request reclean/reimage, or send it to swab/manual review. A cheap independent contamination/readiness measure would be the truth channel.

- [K] Visual cleaning inspection is a subjective check, while ATP bioluminescence measures ATP from both organic material and microorganisms; the university-canteen study treats visual inspection, ATP and microbiological analysis as distinct evidence channels. https://pmc.ncbi.nlm.nih.gov/articles/PMC4211008/
- [K] ATP is not a universal hygiene/microbial ground truth: its instrument readings can be affected by chemistry and may have poor association with plate counts in some settings. https://pmc.ncbi.nlm.nih.gov/articles/PMC4062432/ ; https://pmc.ncbi.nlm.nih.gov/articles/PMC11034431/
- [KILL] A camera-to-ATP predictor would compare one context-dependent proxy with another. It cannot truthfully support cleaning, hygiene or sanitation release, and a non-health tabletop version is an ordinary material/appearance classifier with weak CS identity.

## Current ranking after this red team

1. **WET-VIEW-IDENT** -- credible Macao story, now killed as a primary direction by camera-plus-hydraulic blockage assessment and camera-contamination direct neighbours.
2. **OVI-ZERO** -- convincing local motivation but now killed by direct image-adequacy work and the zero-catch identification failure.
3. **CLEAN-RECORD-NULL** -- killed because visual and ATP measurements are both incomplete proxies, not an independent operational truth channel.
4. **HERITAGE-WET-CHANGE** -- attractive Macao narrative but technically crowded and access-gated; do not lead with it.

No Macao-specific candidate from this short list remains eligible as a primary FYP. The next search must begin from a distinct recurring workflow and an independently measurable decision endpoint, rather than from a local camera application.

## Positive workflow grounding for the retained record story

- [K] iN Systems (Macao) publicly describes an asset-management product for lifecycle tracking, mobile/RFID stock-taking and maintenance records for equipment, vehicles and machines; its page labels the asset-management application “Macau Government.” This is vendor marketing, not evidence of a verified government deployment. https://insys.com.mo/en/application-services/asset-management-system-with-rfid.html
- [K] An independently published property-management system description gives the concrete non-personal workflow: equipment receives a unique QR code; staff scan it using a mobile staff app; serial number, status and maintenance record are retrieved; staff then add/edit data. https://www1.hkexnews.hk/listedco/listconews/sehk/2021/0525/sehk21011301063.pdf (pp. 193-194)
- [C] This supports the *story* for a benchtop `record / reacquire / review` study around tagged physical assets. It does not prove a named Macao deployment, a weak-network requirement, an optical-fault rate, or any research gap.

`PRF-TR` remains the most technically executable bounded benchmark from the earlier audit, but it is not promoted by this note and does not become a Macao field-deployment claim.
