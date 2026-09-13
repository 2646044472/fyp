# Divergence Packet: 2026-08-28 one-year low-cost edge reliability

## Decision investigated

在 `2026-08-28` 到 `2027-06` 的一年 FYP 中，且必须在 `2026-12` 前做出可运行 demo、之后用于扩展实验和优化的约束下，是否存在一个**不是**“换模型/传感器/开发板”的低成本 edge sensing / reliability 方向，值得进入下一道精确主张与可行性 gate？

本 packet 独立发散，不把当前 C3 当默认答案。结论只是一组可被杀死的假设；任何未完成 component collision、exact-claim collision、boundary/impossibility 三轮审计的创新主张均为 **Amber**。

## Search boundary

- 日期与范围：2026-08-28；2024--2026 原始论文优先，并保留 BLE RSS 的 2022 基础测量论文，因为它给出可复现的物理反例边界。
- 机制覆盖：时间/新鲜度语义、间歇供电状态持久化、无线物理测距、资源压力下服务失效、无线模块瞬态故障。
- 检索并阅读的 primary/official sources 包含 Kopetz & Steiner (arXiv 2024), Williams et al. (USENIX ATC 2024), Alharbi & Jhumka (PRDC 2024, metadata), Pourreza & Narasimhan (UCC 2025, existing audited packet), Khademi et al. (2025), 以及 Flueratoru et al. (IEEE Sensors Journal 2022)。出版商全文受限处明确标为 [GAP]，不以摘要支撑精确差异。
- 与现有 archive 的 RGB/NIR/ToF、wake cascade、自测试和 generic anomaly-model 路线重叠的候选未重新包装为新方向。

## Recent-paper limitation map

| Primary work | 读到的任务与假设 | 限制 / failure case | 对本轮的含义 |
| --- | --- | --- | --- |
| Kopetz & Steiner, 2024 | 讨论传感值获取与执行之间的 temporal inconsistency；其解法要求 time-triggered operation、已知 interaction instants 和足够精确的 fault-tolerant global time。 | 该工作不是低成本、断网/重启边缘节点上“是否可相信一个带时间戳样本”的实测决策协议。它也说明没有全局时间时不能把 timestamp 当作无条件真值。 | 可研究的是严格有限的 `accept / defer / time-indeterminate` 证据边界，而不是发明 AoI 或同步算法。 |
| Williams et al., 2024 (CAMEL) | 在 intermittent computing 中以任务、非易失状态和恢复语义确保跨掉电的 forward progress。 | 系统需 task decomposition、编译器分析和特定 state model；应用级“传感记录是否完整”的 claim 很容易被成熟 checkpoint/journal 机制吸收。 | generic brownout/checkpoint FYP 不应晋级；只有无法被 durable journal 消除的观测边界才可能保留。 |
| Alharbi & Jhumka, 2024 (CheckIn) | 标题已直接覆盖 intermittent sensor-IoT checkpointing。 | 全文此轮不可得，故 exact claim 未核实；但标题/正式 proceedings 已足以成为强 component-collision lead。 | 任何“更高效 sensor checkpoint”主张先视为 [KILL]，不能因为使用 ESP32 或新的 fault schedule 而继续。 |
| Pourreza & Narasimhan, 2025 | Pi 4B/Jetson Nano 上 static timeout 在资源压力下会脆弱；工作属于 timeout failure characterization。 | 已有直接 failure-detector 邻居和后续 EdgeStressBench lead；简单 percentile/one-signal baseline 可以消掉多信号故事。 | C3 应只作为 transfer-boundary study 复核，不应被本轮默认维护。 |
| Khademi et al., 2025 | NB-IoT 电源扰动会出现 packet drop 和 packet generation / silent corruption，论文用重传窗口 `k` 做 reliability--overhead trade-off。 | 使用 NB-IoT、PSD circuit 和 server receiver；其 active retransmission 直击“低成本模块掉电后重传改善可靠性”。 | generic transient-fault / retransmission 方向有强 direct neighbor，除非动作或 observation model 真正不同。 |
| Flueratoru et al., 2022 | BLE RSS 在 LOS/NLOS、方向、干扰和 advertising channel 下具有高 snapshot variability；聚合帮助，但 proximity 应用常只看短窗口。 | 论文的难例表明 RSS trace 本身可由不同物理世界产生；后续 RSS+IMU reliability filtering 已存在。 | 低成本 BLE 距离不该做“更准分类器”；最多做有限设备/姿态 panel 的 abstention/no-transfer 边界。 |

## Candidate matrix

| ID | Story and harm | Exact candidate claim | Closest known work | Falsification / kill test | Feasibility |
| --- | --- | --- | --- | --- | --- |
| **T1: edge timestamp-trust boundary** | 在非危险的实验室环境监测 demo 中，维护员必须决定 `accept / defer-resample / time-indeterminate` 一条阈值相关样本是否还能用于告警记录。把断网或重启后的旧样本当新样本会造成错误检查；把所有延迟样本丢弃会制造记录空洞与不必要人工复核。edge 约束是 source 在 WAN 不可用时仍须本地决定，且没有可信云时钟。 | 对预注册的两节点、Wi-Fi delay/loss、sender reboot/clock reset、sleep/wake 有限族，记录 `(monotonic sequence, boot epoch, local clock-quality bound, receiver-arrival time)` 的三动作策略，能否在同等告警延迟下，相比 arrival-only、sender-timestamp-only、timestamp+NTP-offset 和 `any gap => defer`，降低 reference-labelled **false-fresh accept** 且不增加 defer rate。只主张该有限 transfer map，不主张新的同步协议。 | Kopetz & Steiner 2024 提出 temporal-consistency 对 global time / interaction instant 的要求；AoI/edge freshness 论文通常假定 timestamp/generation time 可用。 | **KILL**：普通持久化 epoch+sequence 与 NTP offset 在每个留出 cell 达到相同 false-fresh/defer frontier，或时钟品质 bounds 在 reboot 后不能校准。 | 两块 ESP32/Pi-class board、廉价 RTC 可选、局域 AP、可控软件网络延迟/断电、独立 reference capture node。到 2026-12 可完成 runner、日志和 2--3 个单故障 demo；2027-01--06 做 leave-one-cell-out、重复与 power measurement。无个人数据，无真实控制器。 |
| **B1: BLE proximity abstention boundary** | 实验室资产盘点员决定一台 tag 是否在指定采集区内，动作是 `record present / manual check / no-record`，不是门锁或安全互锁。错误 record 造成盘点追溯错误和人工补录；原始位置 trace 不应上传云端。edge 设备须仅用本地广播收包及时决策。 | 在预注册的 device-pair, pose, LOS/NLOS, channel-interference 物理格上，判定是否存在只基于 RSS window / packet count 的三动作规则，能在留出 pose/obstacle cell 上达到指定 false-record cap 且保留非零自动记录率；比较 RSS threshold/median、status+threshold、和已知 RSS+IMU filtering。不是定位模型。 | Flueratoru et al. 2022 测量并归因 RSS 波动；Filus et al. 2022 已将 RSS 与 IMU 用于 reliability filtering。 | **KILL**：RSS median+abstain 或已发表 RSS+IMU filtering 匹配整个 frontier；或相同 RSS window 同时对应区内/区外，迫使所有满足 cap 的规则近乎全 abstain。 | 3--5 个 ESP32/手机、打印位置格、遮挡板，所有轨迹由研究者操作。年底可有小板 demo；2027 上半年才够做随机化 pose/device blocks 与盲标签。无人体受试者要求，但必须避免把结果描述为 access/safety guarantee。 |
| **I1: intermittent sensing-record completeness** | 维护员读到一个间歇供电节点的温度/振动记录，想判定 `complete / known gap / indeterminate`，而不是估计环境数值。将 last-value 当完整会掩盖未采样，所有重启皆认定失败则过度维护。 | 一个 source state `(epoch, next-sequence, sampled/read-failed/persisted/delivery-unknown)` 是否可在预注册 fault replay 中降低 false-complete rate，相对 MQTT QoS1、persistent sequence、以及 append-only journal，在相同 bytes/energy 下成立。 | CheckIn 2024 和 CAMEL 2024 是直接 checkpoint / recovery 邻居；MQTT durable semantics 也是简单基线。 | **KILL (预期很强)**：persistent epoch+sequence+append-only journal 已可区分所有状态，或 QoS1+重放覆盖 metrics。 | 硬件/数据最容易，且可在年底完成 demo；但 contribution 很可能只是标准日志工程。保留其作为 T1 的 instrumentation，不作为独立 FYP。 |
| **R1: resource-failure transfer boundary (C3 comparator)** | 边缘维护员决定是否对本地 sensing/inference service `continue / observe / fail over`；误 failover 会中断记录，晚 failover 延长真实 outage。 | 在预注册 held-out device/workload/fault cell 上，测 local telemetry 是否能超越 phi-accrual、Lifeguard（拓扑允许时）、percentile timeout 和 one-signal rule 的 false-failover/detection-delay/overhead frontier。 | Pourreza & Narasimhan UCC 2025；EdgeStressBench 2026 lead；Lifeguard baseline family。 | **KILL**：任一强 baseline 匹配 frontier，或 resource signals 不能从调参板迁移到留出 cell。 | 两块 Linux edge board 和容器/服务注入已经足以在 2026-12 demo；2027 上半年适合完成 holdout matrix。无个人数据。它不是本轮首选，只是较成熟的 comparator。 |
| **N1: NB-IoT/LPWAN transient-fault retransmission** | 网络维护员决定 packet 是否可信、是否请求 replay；silent packet generation 会污染记录，过多 retransmit 消耗能量和 airtime。 | 在低成本 radio module 中，local supply/packet metadata 能否选择 retransmission window 优于固定 `k`。 | Khademi et al. 2025 直接做 PSD fault injection、packet drop/generation 和 adaptive retransmission window。 | **KILL**：该论文的 ART 或固定 `k` 已匹配；若换 LoRa/NB-IoT/ESP32 只是硬件替换则不构成研究。 | 需商用 LPWAN/SIM、PSD rig 和无线合规/网络条件；在一年与年底 demo 门槛下不值得承担这些外部依赖。 |

**Pareto reading, not a score:** T1 有最清晰的“决定是否可把一条数据当新鲜证据”的观测/动作差异，也能在安全 bench 完成；但 simple epoch/journal/NTP baseline 有很高 kill power。B1 的物理故事与负结果最直接，但已有 RSS+IMU component collision，而且其正向作用域只能是冻结的 device/pose panel。I1 和 N1 的实现可行性不等于论文可防守性，它们被成熟 checkpoint/retransmit 邻居显著压制。R1 的实验 protocol 最成熟，但 literature collision 的暴露面最大。

Bob Zhang adjacency 只限于 imperfect observation / trustworthy decision 的一般主题；本轮没有复用其公开模型，也不把 advisor fit 当 novelty evidence。

## Top two formalizations

### T1: edge timestamp-trust boundary

- **[D]** 第 `i` 个 source record 为 `o_i=(q_i,e_i,s_i,u_i,r_i)`: monotonic sequence `q_i`、boot epoch `e_i`、sender timestamp `s_i`、本地估计 clock-uncertainty bound `u_i` 和 receiver-arrival `r_i`。参考 capture node 离线记录真实 acquisition order / wall time `g_i`，只用于评分。`d_i in {accept, defer, indeterminate}`。
- **[A]** source 的 `q,e` 可在其 flash/FRAM 持久化；对每个预注册 physical cell，clock bound `u` 可由重同步 probe 校准。该假设对未测的 oscillator、温度和长断电时间**不成立或未知**。[GAP]
- **[T]** 在 source device、network fault 和 reboot pattern 的 leave-one-cell-out split 上，T1 policy 可在不高于 `alpha` 的 `P(false-fresh accept)` 下，严格降低 `P(defer or indeterminate)`，相对四个 named baselines；`alpha`、deadline、所有 cells 和决策门槛均须预注册。
- **Observable outcome:** false-fresh accept、unnecessary defer、样本到 action delay、重启后收敛时间、bytes、monitor CPU/energy；按 device/fault cell 报告，不汇总成单一 accuracy。
- **Counterexample:** 在 reboot 后，只要两个世界给出相同 `(q,e,s,u,r)`，一个 world 的 acquisition 在 freshness deadline 内、另一个在 deadline 外，则任何只看这些 observables 的 policy 必须作相同决定，不能对二者同时保证正确。结论是需额外可信时间/保守 indeterminate，而不是训练更多模型。
- **Negative-result value:** 若 persistent epoch+sequence 或 `any gap => defer` 支配 T1，则得到实际 board/network family 中“timestamp augmentation 没有额外决策信息”的 boundary；若某些 reset cells 始终不可识别，也能给出硬件/同步要求的可审计下界。

### B1: BLE proximity abstention boundary

- **[D]** 一个 RSS observation window `x_t=(RSS_{1:k}, packet-count, channel metadata)`；真值 `y_t in {inside, outside}` 由地面标记位置定义；动作 `d_t in {record-present, manual-check, no-record}`。留出的 physical condition `c` 由 tx/rx device pair、姿态、LOS/NLOS、干扰和距离格组成。
- **[A]** 标签位置、距离边界、采样窗口和环境布置在采集前冻结；测试集的 pose/obstacle cell 对规则调参不可见。静态有限 panel 之外不作外推。[A]
- **[T]** 仅在一个公开冻结的 physical condition panel 内，某规则在完全留出的 `c` 上能否令 `P(record-present | outside) <= beta` 同时 `P(record-present | inside) > 0`，并优于 RSS median abstention。这个命题可为真或假；没有“所有室内 BLE”保证。
- **Observable outcome:** false record、automatic-record coverage、manual-check rate、per-cell calibration/receiver operating curves、local latency/energy。
- **Counterexample:** 两个 `inside/outside` 物理状态产生同一 RSS window distribution 时，任意只用 RSS 的规则有同一输出分布；把阈值调得更复杂不能消除混淆。需要额外可观测量（例如 IMU/第二无线机制）或 abstention。
- **Negative-result value:** 量化达到 false-record cap 所必需的 manual-check 下限，或证实 simple median+abstain 已经充分。这比声称一个未验证的“安全距离 classifier”更诚实且可复用。

## Evidence ledger

| Claim | Label | Primary source and version | Exact section/page read | Scope/caveat |
| --- | --- | --- | --- | --- |
| temporal inconsistency arises when a sensor acquisition and later action are separated; proposed dependable solution requires global time, precise interaction instants and time-triggered operation. | [K] | Kopetz & Steiner, “Temporal Consistency of Data and Information in Cyber-Physical Systems,” arXiv:2409.19309v1, 28 Sep 2024, https://arxiv.org/pdf/2409.19309 | Abstract and Sec. I, PDF p. 1; Sec. V, pp. 6--7; Sec. VII, p. 8; conclusion, p. 9. | Preprint / general CPS design work, not an empirical low-cost edge protocol. It supports the time assumption and counterexample, not T1 novelty. |
| CAMEL treats intermittent execution as task-based forward progress across unpredictable power cycles and discusses peripheral-operation recovery; its conclusion targets checkpoint performance/lifetime. | [K] | Williams, Ahmad & Hicks, “A Difference World: High-performance, NVM-invariant, Software-only Intermittent Computation,” USENIX ATC 2024, pp. 1223--1238, official PDF https://www.usenix.org/system/files/atc24-williams.pdf | Sec. 1, printed pp. 1223--1224; Sec. 2, pp. 1224--1225; Sec. 3.1, p. 1226; Sec. 7, p. 1236. | Direct component collision for I1; not evidence about MQTT receiver semantics. |
| CheckIn is a 2024 PRDC paper explicitly on efficient checkpointing of intermittent sensor-based IoT networks. | [K] bibliographic / [GAP] exact content | Alharbi & Jhumka, “CheckIn: Efficiently Checkpointing Intermittent Sensor-Based Internet of Things (IoT) Networks,” PRDC 2024, DOI https://doi.org/10.1109/PRDC63035.2024.00016 ; official proceedings TOC https://www.proceedings.com/content/078/078722webtoc.pdf | Official proceedings TOC, p. v; DOI metadata only. | Full primary text was unavailable in this round. Do not assert an exact collision until it is read. |
| Static timeout behavior under edge resource stress has a direct UCC 2025 neighbor, so a generic telemetry detector is not a defensible claim. | [K] | Pourreza & Narasimhan, “When Timeouts Fail: Revisiting Fault Detection under Resource Stress in Edge Computing,” UCC 2025, DOI https://doi.org/10.1145/3773274.3774280 | Existing audited coordinator packet reports Secs. 2--3, printed pp. 2--4, and Sec. 6, p. 9; this divergence round did not independently obtain the ACM PDF. | Use only as a direct-neighbor lead pending full text / split audit. |
| NB-IoT PSD injection can manifest packet drops and packet generation / silent corruption; the paper proposes retransmitting last `k` packets as reliability-overhead trade-off. | [K] | Khademi et al., “A reliability framework for NB-IoT devices: Addressing transient faults and silent data corruptions,” *Computers and Electrical Engineering* 124, 110405 (May 2025), https://doi.org/10.1016/j.compeleceng.2025.110405 | Official HTML abstract; Sec. I introduction/contributions; stated Secs. III--V organization, publisher record accessed 2026-08-28. | Full PDF page mapping is [GAP]. Enough to make N1 a direct-neighbor warning, not to prove all LPWAN overlap. |
| BLE RSS snapshots vary with LOS/NLOS, orientation, interference and advertising channel; the paper says such snapshots can make proximity accuracy unreliable. | [K] | Flueratoru, Shubina, Niculescu & Lohan, “On the High Fluctuations of Received Signal Strength Measurements With BLE Signals for Contact Tracing and Proximity Detection,” *IEEE Sensors Journal* 22(6), pp. 5086--5100, published online 8 Jul 2021 / issue 15 Mar 2022, https://doi.org/10.1109/JSEN.2021.3095710 ; author repository https://trepo.tuni.fi/handle/10024/220480 | Abstract, printed p. 5086; conclusion/future-work pages require re-open of the paper before B1 promotion [GAP]. | Foundational measurement evidence, not a claim about a particular 2026 device panel. |
| RSS+IMU reliability filtering is already a low-cost proximity component combination. | [K] | Filus et al., “Cost-effective filtering of unreliable proximity detection results based on BLE RSSI and IMU readings using smartphones,” *Scientific Reports* 12, 2440, 14 Feb 2022, official full text https://www.nature.com/articles/s41598-022-06201-y | Abstract; “Proximity and reliability estimation” section, Eqs. (6)--(8), HTML accessed 2026-08-28. | Direct component collision; B1 must include it as a baseline or restrict its claim to RSS-only boundary measurement. |
| T1/B1 exact claims are distinct from all direct literature. | [C] | Bounded sources/queries in this packet. | Three novelty audits incomplete. | **Amber only**; validation can kill either claim. |

## Queries and failed searches

- `2024 intermittent computing sensor data consistency checkpoint paper conference`
- `2025 low power IoT power failure data integrity sensor logging paper`
- `2024 MQTT edge sensor outage data loss durable logging study paper`
- `2025 BLE RSS proximity low cost edge decision reliability paper`
- `"Temporal Consistency of Data and Information" cyber physical systems 2024 pdf`
- `2025 edge IoT timestamp freshness sensor data reliability paper`
- `2024 networked control sensor data age edge computing freshness decision paper`
- `2025 edge sensor data provenance gap outage reliability paper`
- `"CheckIn: Efficiently Checkpointing" PDF`
- `"A reliability framework for NB-IoT devices" PDF`
- `"On the High Fluctuations of Received Signal Strength" pdf`

Failed/limited retrievals:

- ACM UCC 2025 and IEEE PRDC 2024 full PDFs were not accessible through the publisher in this round. Their exact algorithms, fault splits, and evaluation scope remain [GAP].
- No verified 2024--2026 primary work was found that exactly performs T1's `false-fresh accept` versus defer protocol on low-cost rebooting nodes. This is **not** evidence of absence and is the first exact-claim search for validation.
- No verified source establishes that an NTP offset plus persistent epoch/sequence cannot subsume T1; this is its strongest simple-baseline kill risk.
- No verified source establishes RSS-only B1 has a positive transfer region beyond the known device/pose limitations; a result can properly be negative.

## Decision

**PROMOTE (Amber) T1 only to a component-collision, exact-claim, and clock-bound calibration gate. HOLD (Amber) B1 only as a finite physical-boundary alternative. PIVOT R1 to its already narrowed transfer-boundary protocol. KILL I1 and N1 as standalone FYP directions unless validation finds a task/observation/action distinction that survives durable-journal and ART baselines.**

PROMOTE
