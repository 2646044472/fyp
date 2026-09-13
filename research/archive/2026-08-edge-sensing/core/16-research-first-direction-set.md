# 四个研究优先的 FYP 方向

最后更新：2026-08-27。此页取代“先有一个可用设备，再找应用”的思路。每个方向先有一个可证伪的研究假设，demo 只是验证它的工具。第二轮问题驱动审计见 [`../log/39-problem-driven-second-audit.md`](../log/39-problem-driven-second-audit.md)，本轮的 candidate replacement 见 [`../log/41-capture-provenance-and-restoration-audit.md`](../log/41-capture-provenance-and-restoration-audit.md) 和 [`../log/42-sensor-state-action-audit.md`](../log/42-sensor-state-action-audit.md)。这里的“未找到直接工作”均指截至本轮检索日的范围限定结论，不是全球不存在证明。

## 什么才算研究，而不是 demo

| Demo 问题 | 研究问题 |
| --- | --- |
| 能不能在 Pi 上跑？ | 某个可定义的机制是否在未见条件下改善一个风险/泛化界限？ |
| 多模态是否比单模态准确？ | 为什么某种信息应被信任，何时不应被信任，且该规则能否跨设备/攻击/环境成立？ |
| 做一个门锁/检测器。 | 在预先冻结的 protocol 下，提出的假设能否被 baseline 推翻？ |

## 每个候选必须先过的三问

以后不再只因“edge 可以部署”保留方向。任何候选都必须在选题前用下面三项写成一页；任一项空泛就停止。

| 问题 | 必须回答什么 | 不能接受的回答 |
| --- | --- | --- |
| **故事** | 谁在什么真实约束下作什么决定；错一次的后果是什么；为什么 cloud/always-on/昂贵硬件不能直接解决？ | “AI 很方便”“edge 更快”“可以用在很多地方”。 |
| **创新** | 精确指出现有最接近工作已解决什么，以及本题在任务、观测、约束、假设或评价终点中哪一个**可证伪**的交集不同。 | “用了 RGB+NIR+ToF”“部署到 Pi”“模型更轻”。 |
| **baseline** | 最强、最自然的既有方案是什么；它若同样好，本题的主张如何被推翻？ | 只和一个弱 CNN 或单模态 accuracy 比。 |

“没有找到相关论文”不是创新论证；创新只能由一个清楚的 direct-neighbor exclusion 表和会失败的 baseline 支撑。

## P：掌纹方向

### 题目

> **双轴开放世界掌纹 PAD：在未见攻击材料和未见采集设备下控制系统级 IAPMR**

### 研究假设

传统 PAD 在“训练/测试 attack material 与 device 相近”的二元分类中表现好，但安全失败真正发生在攻击既是未见材料、又经新采集设备呈现时。若从 bona-fide acquisition distribution 建模，并把 device condition 与 attack nonconformity 分开校准，能否在两轴都留出的测试中控制**系统级**攻击接受率（IAPMR），而不仅是 PAD 的 ACER/APCER？

### 最接近工作与尚未找到的交集

- PALMspoof/2018 已报告 palmprint verification 的 display/print attack 及 IAPMR；FIDO/NIST 也明确 IAPMR 是 PAD 加 matcher 后的系统指标。
- DAPANet（2025）已做 multi-source 到 unlabeled target 的 palmprint PAD domain adaptation；2023 也已有 palmprint anti-spoofing domain generalization，故“跨域”本身不能作为新颖性。
- GBU-Palm（2026-08-14 预印本）已经把原生多模态视频、六环境、攻击 lineage、跨环境、光谱/时序干预放进掌纹 PAD benchmark；因此这些内容不能再作为 P 的贡献。
- 尚未在 GBU-Palm 的公开正文中看到将 PAD 输出接到冻结的 1:1 palm matcher、按攻击材料和采集设备计算系统级 IAPMR，并同时报告 Pi capture-to-decision/energy 的协议。这个交集仍未确认，而且 GBU 数据尚未正式可下载。

### 可做的贡献

不是再造 PAD backbone，而是把 PAD 与冻结 matcher、攻击 lineage 和端侧成本连接起来，提出 `device-conditioned bona-fide nonconformity + risk-controlling accept/reject rule`。若 GBU-Palm 后续版本或其他工作已覆盖这个系统级协议，P 应放弃方法主张，只保留复现实验或测量报告。

### 风险

需要合法的攻击材料、受试者同意和至少两个采集链；没有 cross-device/PAIS 留出时，不能保留该题。

## S：非掌纹方向一

### 题目

> **从传感器状态到安全动作：低成本多模态 edge 视觉中的残余可观测性协议**

### 研究假设

系统的低置信度既可能来自故障/同步/标定问题，也可能来自传感器健康但场景或目标本身不可观测。若显式分离 `sensor health`、`environment/target observability`、`task confidence` 和 `residual observability`，再选择继续、固定 fallback、重采、重标定或 abstain，能否在固定 latency/energy/human-retry budget 下，降低最终任务的 false pass/高风险自动动作？

### 最接近工作与尚未找到的交集

- sensor health monitor、fault recovery、missing-modality fusion 与 active perception 已有长期研究；不能把 root-cause diagnosis、重采或 graceful degradation 单独作为创新。
- MAMMOTH（2026）已在真实机器人上融合 RGB/thermal/point cloud，按整路 modality dropout 训练端到端 navigation policy，并报告 collision、success 和 manual takeover。因此“真实多模态 action policy 抗缺失”不是空白。
- 最新自动驾驶系统综述明确区分 sensor health、task confidence 和 residual observability；其 65 项 primary studies 仅少数连接到 operational response，并指出联合 physical degradation、environment state、perception output、response 的开放 benchmark 仍缺。尚未找到将这些联合标签、**partial real fault** 和 risk/action-cost 放在低成本 RGB/NIR/ToF edge 设备上的 direct neighbor。

### 可做的贡献

不是提出一个新 fusion backbone，而是定义可复现 episode：raw sensor/timing telemetry、physical fault、healthy-but-unobservable scene、task outcome、chosen action 和 cost 同步记录。比较 `always fuse`、`fixed fallback`、quality/router 与 state-separated action policy；关键终点是 accepted-task risk、false warning、detection delay、recovery success、coverage 和 edge cost。

### 风险

需要实验室硬件导出 actual illumination、frame/timestamp、ToF status、温度和功耗，且能制造并独立标注 partial physical faults 与 healthy-but-unobservable hard negatives。若只有随机 mask 或无法记录 telemetry，S 退化成已有 missing-modality demo；若 B1/B2 已有相同 risk-cost，则复杂策略应报告负结果。

## T：非掌纹方向二

### 题目

> **时间不确定性感知的多模态 edge fusion：把异步采集误差传播为可校准的任务风险，而不是假设同步**

### 研究假设

低成本 RGB、NIR 和 ToF 的 frame timestamp 不代表真实曝光/回波时刻；把它们强行当作同步输入，会制造高 confidence 的错误融合。若对每模态学习/估计 time-offset posterior，并将它传播到 prediction set 或 abstention，是否能在未知 offset、运动和掉帧下控制 task risk？

### 最接近工作与尚未找到的交集

- 2026 TSP 已研究异步 sensor network 的未知 temporal misalignment，并估计 offset 做目标跟踪；UAMF-Net 还联合 asynchronous alignment、uncertainty、calibration 和 risk-coverage。
- 近期 multimodal tracking/robotics 文献已承认 temporal missingness、同步和 action latency 问题。
- T 只能保留为硬件条件式问题：Pi 设备必须能观测 actual exposure/LED/ToF-return timing，并把 offset posterior 传播到视觉任务的 calibrated reject；否则只是已有异步融合方法的设备替换。

### 可做的贡献

把时间偏移当作随机变量而非 preprocessing error；设计 interval-correspondence encoder 和 offset-conditioned conformal reject rule。实验按真实/受控延时、目标运动和掉帧三轴留出，比较 naive sync、fixed offset、learned alignment、risk-aware fusion。

### 风险

若硬件没有任何可验证 timestamp/LED state/运动参考，offset 没有 ground truth，研究不可答。

## O：非掌纹方向三

### 题目

> **正常性漂移还是未知缺陷：面向工业视觉的三态 normal/shift/defect 风险控制**

### 研究假设

正常批次的光照、视角、纹理或相机 ISP 改变常被 one-class detector 当作 defect；反过来，把异常全视为 domain shift 又会漏检真实缺陷。若显式学习 normality shift 与 defect 的可分证据，并输出 `accept normal / recalibrate / defect` 三态，而非一个 anomaly score，是否能降低未见现场的 false alarm 和 false pass？

### 最接近工作与尚未找到的交集

- ICCV 2023 已研究 anomaly detection under distribution shift；2026 工业 stream 工作已区分 failure 与 healthy domain shift；conformal industrial anomaly 也已有。
- 相关 shift-aware、conformal、unseen-anomaly 和三态谨慎决策已有近邻；O 只能保留为同一现场协议下的 normal-only、未见 shift、未见 defect 和 action-cost 联合评测。没有独立采集标签时应放弃。

### 可做的贡献

以 normal prototype + shift evidence + defect evidence 做三态 decision，并用 split-conformal 或 risk-controlling calibration 固定 false alarm/false pass 预算。数据可用 MVTec/VisA/Real-IAD 加上独立采集的 illumination/view/ISP shift；重点不是最高 AUROC，而是 shift 被错误报 defect 的比例和真正未知 defect 的漏检。

### 风险

“shift”与“defect”标签的定义必须由采集过程固定；若只在 MVTec 随机切分上跑，不能声称现场泛化或新颖。

## 当前建议

若必须掌纹，仍只把 **P** 作为条件性候选：先确认 GBU-Palm 数据/协议是否已覆盖系统级 matcher 与端侧成本；不能确认前，不把它写成新方法。若可不做掌纹，原本宽泛的 S/T/O 都有强近邻，不能再以“研究创新”推荐。S 内新提出的高意义、高风险窄问题是「部分共因退化下的虚假一致风险」：详见 [`../log/43-common-cause-fusion-novelty-audit.md`](../log/43-common-cause-fusion-novelty-audit.md)。它尚未通过 direct-neighbor novelty gate，不能承诺首创；T/O 暂降为其中的事件或对照，而非独立首选。被淘汰的 R（复原幻觉/证据 certificate）保留在日志中，不应为了“有四个方向”硬留在主短名单。

在该窄问题下，推荐把第一个具体任务设为**安全边界放行**，而不是掌纹：设备输出 `permit / stop / uncertain`，研究终点是 physical common-cause event 下的 false permit、coverage 和成本。这样 edge device 是研究载体，RGB/NIR/ToF 是证据来源，掌纹只在日后有明确需求时才是可替换的 application task。

## 新增的 edge-native 候选

原有 P/S/T/O 都把 edge 的限制主要当作部署成本。新候选 **E：风险审计式分级感知** 则把有限 sensing/compute budget 作为问题的起点：低功耗 sentinel 决定何时唤醒 RGB/NIR verifier，而这个选择会使未被唤醒事件在日志中不可见。研究问题变为如何以很小、可校正的 audit budget 估计并控制 `no-wake` 的安全风险。它目前在可做性与 edge 相关性上优于 S-H，完整定义、已知近邻、主指标和硬件 Gate 见 [`../log/44-edge-native-risk-audited-cascade.md`](../log/44-edge-native-risk-audited-cascade.md)。它仍须完成 direct-neighbor novelty gate，不能提前声称首创。

选定一个后，下一轮只围绕该题跑完整 novelty gate：Boolean queries、近五年引用链、代码/数据审计、按“是否同任务/同输入/同评估”的排除表，而不是同时推进四个。
