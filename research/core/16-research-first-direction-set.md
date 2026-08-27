# 四个研究优先的 FYP 方向

最后更新：2026-08-27。此页取代“先有一个可用设备，再找应用”的思路。每个方向先有一个可证伪的研究假设，demo 只是验证它的工具。这里的“未找到直接工作”均指截至本轮检索日的范围限定结论，不是全球不存在证明。

## 什么才算研究，而不是 demo

| Demo 问题 | 研究问题 |
| --- | --- |
| 能不能在 Pi 上跑？ | 某个可定义的机制是否在未见条件下改善一个风险/泛化界限？ |
| 多模态是否比单模态准确？ | 为什么某种信息应被信任，何时不应被信任，且该规则能否跨设备/攻击/环境成立？ |
| 做一个门锁/检测器。 | 在预先冻结的 protocol 下，提出的假设能否被 baseline 推翻？ |

## P：掌纹方向

### 题目

> **双轴开放世界掌纹 PAD：在未见攻击材料和未见采集设备下控制系统级 IAPMR**

### 研究假设

传统 PAD 在“训练/测试 attack material 与 device 相近”的二元分类中表现好，但安全失败真正发生在攻击既是未见材料、又经新采集设备呈现时。若从 bona-fide acquisition distribution 建模，并把 device condition 与 attack nonconformity 分开校准，能否在两轴都留出的测试中控制**系统级**攻击接受率（IAPMR），而不仅是 PAD 的 ACER/APCER？

### 最接近工作与尚未找到的交集

- PALMspoof/2018 已报告 palmprint verification 的 display/print attack 及 IAPMR；FIDO/NIST 也明确 IAPMR 是 PAD 加 matcher 后的系统指标。
- DAPANet（2025）已做 multi-source 到 unlabeled target 的 palmprint PAD domain adaptation。
- 未找到一项 palmprint 研究同时冻结 matcher、按 attack material 和 capture device 做双轴 leave-one-out、以 calibration 后的 IAPMR budget 为主要终点，并明确拒答覆盖率。

### 可做的贡献

不是再造 PAD backbone，而是提出 `device-conditioned bona-fide nonconformity + risk-controlling accept/reject rule`，并给出双轴开放集协议。若该规则在未见 PAIS/device 上不能优于 DAPANet-style/one-class/energy baselines，结论就是它不成立。

### 风险

需要合法的攻击材料、受试者同意和至少两个采集链；没有 cross-device/PAIS 留出时，不能保留该题。

## R：非掌纹方向一

### 题目

> **证据约束的跨模态图像复原：阻止 restoration 在 edge 视觉质检中伪造或抹除任务关键细节**

### 研究假设

未知退化下的复原模型可产生视觉可信但事实错误的细节。若 RGB 的复原高频结构没有 NIR/ToF/raw-frame 的对应支持，系统应将该区域标为 unsupported，而不是交给下游 defect/recognition 模型。跨模态物理一致性能否比单图 uncertainty 更可靠地定位这种 hallucination，并降低 downstream false pass/false defect？

### 最接近工作与尚未找到的交集

- UniRestore、OPIR 等已经做 task-aware/uncertainty-aware all-in-one restoration；QFormer/FADNet 是 PAMI 的复原基础。
- HalluGen（CVPR 2026）和 sFRC 已将 medical restoration hallucination 的生成/评价推进很远。
- 未找到将**第二个原始物理传感模态**当作 restoration evidence certificate，并用它控制低成本 edge 视觉质检最终决策的直接工作。

### 可做的贡献

提出 support map/certificate：只有被跨模态对应、几何或时序约束支持的重建细节可影响下游模型；其余区域触发原图 fallback 或 abstain。关键终点是未见退化下的 false pass、false defect、hallucination localization 和 edge cost，不是 PSNR。

### 风险

需要良好对齐的 RGB/NIR/ToF 或 RGB-D 数据及真实缺陷/目标；若各模态不可对齐，只能研究普通 restoration，题目失去关键新意。

## T：非掌纹方向二

### 题目

> **时间不确定性感知的多模态 edge fusion：把异步采集误差传播为可校准的任务风险，而不是假设同步**

### 研究假设

低成本 RGB、NIR 和 ToF 的 frame timestamp 不代表真实曝光/回波时刻；把它们强行当作同步输入，会制造高 confidence 的错误融合。若对每模态学习/估计 time-offset posterior，并将它传播到 prediction set 或 abstention，是否能在未知 offset、运动和掉帧下控制 task risk？

### 最接近工作与尚未找到的交集

- 2026 TSP 已研究异步 sensor network 的未知 temporal misalignment，并估计 offset 做目标跟踪。
- 近期 multimodal tracking/robotics 文献已承认 temporal missingness、同步和 action latency 问题。
- 未找到针对 Pi 级 RGB/NIR/ToF 小型视觉设备，把 actual illumination/frame timing uncertainty、跨模态 correspondence 和 selective task risk 联合评估的直接工作。

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
- 未找到以**视觉 normal-only training**、未见缺陷、未见正常性漂移和三态动作成本为同一协议的直接工业 edge 研究。

### 可做的贡献

以 normal prototype + shift evidence + defect evidence 做三态 decision，并用 split-conformal 或 risk-controlling calibration 固定 false alarm/false pass 预算。数据可用 MVTec/VisA/Real-IAD 加上独立采集的 illumination/view/ISP shift；重点不是最高 AUROC，而是 shift 被错误报 defect 的比例和真正未知 defect 的漏检。

### 风险

“shift”与“defect”标签的定义必须由采集过程固定；若只在 MVTec 随机切分上跑，不能声称现场泛化或新颖。

## 当前建议

若必须掌纹，选 **P**，因为它把成熟识别领域转成仍未被充分解决的开放世界安全评估/校准问题。若可不做掌纹，优先约谈 **R**：它继承 PAMI 的复原线，但问题是“何时不应相信复原结果”，比再提高 PSNR 或在 Pi 跑模型更像研究。**T** 的理论味最强但严重依赖硬件时序；**O** 的公开数据最容易获得，但必须做出三态 normal/shift/defect 才不落回普通 anomaly detection。

选定一个后，下一轮只围绕该题跑完整 novelty gate：Boolean queries、近五年引用链、代码/数据审计、按“是否同任务/同输入/同评估”的排除表，而不是同时推进四个。
