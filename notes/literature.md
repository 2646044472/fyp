# Literature and Technology Map

Use this file for concise comparisons and decision-relevant evidence. Link to
the original source and distinguish reported results from our interpretation.

## Search Log

| Query | Source | Filters | Search date | Results reviewed | Notes |
| --- | --- | --- | --- | --- | --- |
| Example — replace: `palmprint recognition edge quantization` | Google Scholar | Since 2021 | YYYY-MM-DD | 0 | Refine terms after first pass |

## Papers

| Citation/link | Task | Dataset/protocol | Method | Reported metrics | Edge relevance | Follow-up |
| --- | --- | --- | --- | --- | --- | --- |
| Example — replace | Verification | Dataset and split | Architecture | EER / accuracy | Parameters or measured latency | Reproduce or exclude |

## Datasets

| Dataset/link | Access/license | Subjects/samples | Capture conditions | Contactless? | Published protocol | Main risks | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Example — replace | Public/restricted | Record counts | Controlled/uncontrolled | Yes/No | Split and metric | Domain shift, size, access | Investigate |

### Dataset Selection Criteria

- A documented and reproducible train/validation/test or verification protocol.
- Legal and practical access within the project schedule.
- Capture conditions relevant to the intended edge-device scenario.
- Enough identities and samples for meaningful recognition evaluation.
- Comparability with published baselines.

## Baseline Models

| Model/repository | Framework/license | Task | Input/ROI assumptions | Parameters/size | Reproducible checkpoint? | Reported result | Deployment risk | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Example — replace | PyTorch / license | Identification or verification | Input description | Unknown | Yes/No | Metric and protocol | Unsupported operators | Investigate |

## Deployment Tools

| Tool | Target devices | Quantization support | Profiling support | Likely constraints | Evidence/link |
| --- | --- | --- | --- | --- | --- |
| Example — replace: ONNX Runtime | CPU/GPU/mobile | Dynamic/static | Runtime profiling | Operator compatibility | Official documentation |

## Edge Platforms

| Platform | Availability | Compute/runtime | Memory | Power measurement | Relevance | Constraints | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Example — replace: smartphone | Confirm access | CPU/GPU/NPU and runtime | Record capacity | Tool or method | Authentication scenario | OS/toolchain limits | Investigate |

## Technical Bottlenecks

| Bottleneck | Evidence | Affected metric | Possible intervention | How to measure |
| --- | --- | --- | --- | --- |
| Example — replace: unsupported export operator | Export log or documentation | Deployability/latency | Replace operator | Successful export and device benchmark |

## Candidate Research Questions

A useful question names an intervention, target platform, workload, and
measurable trade-off.

| Candidate question | Independent variable | Outcomes | Dataset/protocol | Platform | Novelty/evidence gap | Feasibility |
| --- | --- | --- | --- | --- | --- | --- |
| Example — replace: How does post-training quantization affect verification performance and latency? | Precision/quantization method | EER, latency, size | Select after comparison | Select after inventory | State literature gap | High/medium/low with reason |

## Unresolved Questions

| Question | Why it matters | Who/what can answer it | Next action |
| --- | --- | --- | --- |
| Example — replace: Which devices can the lab provide? | Determines runtime and measurement tools | Supervisor/lab inventory | Ask at next meeting |
