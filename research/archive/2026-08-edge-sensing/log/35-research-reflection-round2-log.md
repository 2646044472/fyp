# 第二轮研究与反思日志

日期：2026-08-27

## 研究问题

本轮不再问“哪个关键词看起来最新”，而问：在已有大量论文之后，FYP 还能贡献哪一个可证伪、可复现、可在边缘设备测量的变量？阅读范围覆盖掌纹综述、缺失模态综述、传感器失败 benchmark、轻量/条件式融合、工业异常检测、连续 TTA 和 Bob Zhang/PAMI 研究地图。

## 读到的关键原文

### 1. 掌纹：成熟的是闭集分数，脆弱的是开放集和资料协议

[Deep Learning in Palmprint Recognition](https://arxiv.org/html/2501.01166) 的综述明确把 ROI、特征、open-set、security/privacy 和数据集放在一条 pipeline 中。它汇总的表格中，CCNet 等方法在多个数据集闭集准确率接近 100%，但跨数据集/开放集 EER 明显变差；综述的 outlook 直接把跨域、用户独立、元数据、人口/环境/时间偏差以及模板重建、对抗攻击列为未解决问题。

这改变了“掌纹已经完全解决”的说法：识别算法在标准数据上的 benchmark 很成熟，但从实验室图像到真实设备仍有 protocol gap。另一方面，这也否定了“再训练一个轻量掌纹网络就创新”。本项目应研究**测量和决策协议**，而不是与闭集 accuracy 竞争。

### 2. 缺失模态：领域活跃，但真实流式和效率仍是公开缺口

[Deep Multimodal Learning with Missing Modality: A Survey](https://arxiv.org/html/2409.07825) 的 2026 v4 汇总了 2012--2025.8 的 354 篇重要论文，按 modality imputation、representation、architecture 和 model combination 分类。它指出两点对 FYP 很关键：大部分方法仍很重，不适合受限设备；只有少量工作处理 multimodal streaming/temporal missingness，异步掉帧会同时造成空间缺口和时间错位，真实 IoT/wearable/mobile sensing 的整体评估仍零散。

所以“缺失模态”本身不是空白；可辩护的切口是**真实采集链的异步失效 + 端侧动作选择 + 资源/风险评测**。

### 3. 传感器失败：已有 benchmark，不能再声称“首次研究失效”

[Liao et al., CVPR Workshop 2025](https://openaccess.thecvf.com/content/CVPR2025W/TMM-OpenWorld/html/Liao_Benchmarking_Multi-modal_Semantic_Segmentation_under_Sensor_Failures_Missing_and_Noisy_CVPRW_2025_paper.html) 建立 EMM、RMM、NM 三种失效场景，并用均匀损坏组合和独立 Bernoulli 失效定义指标；代码公开。其仓库还列出了 MAGIC、Any2Seg、CAFuser、MemorySAM、RMMSS 等已经面向失效或质量的模型。

[CAFuser](https://arxiv.org/abs/2410.10791) 从 RGB 生成 condition token 来动态调整 lidar/radar/event 融合；[MoME](https://openaccess.thecvf.com/content/CVPR2025/html/Park_Resilient_Sensor_Fusion_Under_Adverse_Sensor_Failures_via_Multi-Modal_Expert_CVPR_2025_paper.html) 用 camera、LiDAR、camera-LiDAR 三个 expert 和 quality-based router 应对 camera drop、LiDAR drop、beam reduction 和遮挡。

这三篇一起说明：quality-aware fusion、condition-aware fusion、mixture-of-experts 不能直接写成 FYP 创新；公开 benchmark 多数仍是自动驾驶/语义分割，和 Pi 级 RGB/NIR/ToF 小型采集盒的真实掉帧、同步和功耗不同。FYP 的新变量应是 capture-side event log、相关失效分布、主动重采策略或拒答成本，而非又一个 router。

### 4. 异常检测：性能和速度已有强基线，未知和现场协议更重要

[EfficientAD](https://arxiv.org/html/2303.14535) 用轻量 feature extractor、student-teacher 和逻辑异常 autoencoder，在论文硬件上报告约 2 ms/600 images per second；官方实现是 Apache-2.0 的非官方复现，README 给出 MVTec/VisA 结果和 GPU timing。它直接否定“把轻量模型放 Pi”作为单独创新。

[Real-IAD](https://arxiv.org/html/2403.12580) 指出 MVTec 等公开数据已经出现性能饱和，与真实应用有差距；它提供约 150K 图、30 类物体、5 个视角和 sample-level evaluation，并提出 FUIAD（带正常/异常噪声的 fully unsupervised setting）。这使异常方向的研究重点从“再提高 AUROC”转向未知缺陷、样本级决策、噪声训练和端侧拒答。

### 5. TTA：回滚/恢复已经是主流问题，不是空白

[OFTTA](https://arxiv.org/abs/2310.18562) 已为跨人传感器 HAR 提出无梯度 EDTN + prototype/support set，并验证 edge 可行；它没有解决视觉传感器和长期安全策略。

[Continual Momentum Filtering](https://proceedings.iclr.cc/paper_files/paper/2024/hash/eb03488d2a00e50419cbba761da87e93-Abstract-Conference.html) 用 Kalman-style parameter filtering 处理在线适应的 catastrophic forgetting；[Effective Restoration of Source Knowledge](https://arxiv.org/html/2311.04991) 用 running-statistics peak detection 检测 domain change 并恢复 source model；[IST](https://openaccess.thecvf.com/content/CVPR2024/html/Ma_Improved_Self-Training_for_Test-Time_Adaptation_CVPR_2024_paper.html) 用 pseudo-label correction 和 parameter moving average 稳定 TTA。

因此“加一个 rollback”也不足够。TTA 候选只有在明确视觉设备漂移、污染注入、风险监控和最坏时间窗口后才有研究价值；否则是把已有方法换数据集。

### 6. 最新 edge TTA 证据让边界更具体

[BoTTA](https://arxiv.org/abs/2504.10149) 把 on-device TTA 的现实限制做成 benchmark：少量 adaptation 样本、类别暴露不足、多个重叠 shift，并要求报告真实设备资源。它还在 Raspberry Pi 上报告峰值内存变化，说明“在 Pi 上部署”不能只引用桌面 GPU 的推理时间。更重要的是，BoTTA 主张周期性适应，而不是每一批数据都更新；这与低频授权/采集设备的工作节奏更接近。

[OD-TTA](https://arxiv.org/abs/2505.00986) 已经提出 shift detector、source-domain selection 和 decoupled BN 的 on-demand adaptation。[ELaTTA](https://arxiv.org/abs/2510.11068) 的 2026 v3 则进一步把单实例、无梯度、低维 latent search 和 ZYNQ-7020 部署做成方法。由此可以排除“按需触发”“forward-only”“低内存适应”作为单独创新。

2026 的 [CTTA survey](https://arxiv.org/abs/2607.08164) 将领域共识整理为 optimization、parameter-efficient 和 architecture 三族，同时指出长期非平稳流、开放世界/黑盒设置、资源预算和多模态扩展仍需要更真实的 benchmark。这里的“需要”是研究议程，不是我们已经拥有空白的证据；FYP 必须把它改写成一个小而可测的设备协议。

因此 T 的最小新问题改为：**在视觉传感器的可观测漂移/故障事件上，什么时候适应会降低风险，什么时候应冻结或回滚；策略的最坏窗口、恢复时间、峰值内存和能耗是否优于固定模型？** 若没有连续流和事件时间戳，T 不成立。

## 研究判断的变化

### 从“算法方向”改为“失效闭环”

早期的候选排序把缺失模态、TTA 和 anomaly 看成三个算法方向。读完上述原文后，它们更像同一个系统问题的不同动作：

```text
observe sensor state -> estimate quality/uncertainty -> choose fuse/degrade/reacquire/adapt/abstain -> log cost and outcome
```

掌纹只是一个有现成采集硬件的 case study；RGB-D、工业相机或其他视觉任务都可使用同一闭环。

### 从“创新性高”改为“新颖性可防守”

“高”不能再只依据论文数量少。现在用四个问题检查每个候选：

1. 失效是不是现实采集链能产生的，而不是随机 mask？
2. 动作是否改变最终风险或资源，而不只是中间 feature？
3. 是否有未见设备/环境/故障模式的留出？
4. 是否能在 Pi 或明确的 CPU 预算上测量，而不是只引用 GPU 数字？

按这个标准，公开数据上的 A（缺失模态）仍是最容易启动，但其算法新颖性只有中等；P（掌纹条件式采集）硬件依赖高，却有实验室设备优势；T 需要长期流式协议；O 需要把轻量化和未知缺陷留出做实。

## 负结果也有价值，但必须预先定义

- 如果真实 RGB/NIR/ToF 故障下质量 gate 不比固定 fallback 好，结论是复杂融合不值得其成本。
- 如果 TTA 在漂移后改善平均准确率，却出现严重最坏窗口或无法恢复，结论是不能部署，而不是只报均值。
- 如果异常模型在 MVTec 很好、Real-IAD/真实小样本未知缺陷很差，结论是 benchmark saturation 与现场差距。
- 如果掌纹主动短序列只降低真人通过率，或只对已见攻击材料有效，应停止 PAD 主张。

## 当前综合结论

最稳妥的研究主线是：

> **低成本视觉设备在传感器不完整、不确定或发生分布漂移时，如何用可解释的质量估计选择继续推理、降级、重采、适应或拒答，并以任务风险、恢复时间和端侧资源共同评价。**

若必须掌纹，将掌纹 1:1 验证作为此主线的实例；若允许换题，先以公开 RGB-D 或工业图像做小规模 proof-of-concept，再决定是否接实验室硬件。这个表述比“掌纹 + edge”更接近 Bob Zhang/PAMI 多条研究线的交集，也明确承认已有工作的边界。
