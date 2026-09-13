# Bob Zhang / 澳门大学 PAMI Research Group 研究审计日志

最后更新：2026-08-27。本日志回答两个问题：Bob Zhang（张一博）及其 PAMI Research Group 到底长期做了哪些研究线；如果掌纹识别已经成熟，哪些机制可以转成一年制 FYP。这里的“读过”只表示我查看了相应原始论文、官方摘要/HTML、作者代码或出版物页面中的可访问部分；没有把每一篇几十页论文都假装成逐字精读。

## 1. 身份和资料边界

- [澳门大学教师主页](https://www.fst.um.edu.mo/personal/bobzhang/)：Bob Zhang 是澳门大学计算机与信息科学系副教授，研究兴趣为 biometrics、pattern recognition、image processing、medical image analysis。
- [PAMI Research Group 主页](https://pamigroup.github.io/)：研究组成立于 2013 年，公开定位为 pattern recognition、biometrics、image processing、AI。
- [PAMI 公开发表列表](https://pamigroup.github.io/publications.html)：按专著、期刊、会议和书章列出完整清单；本次以它作为“全量目录”，再对代表作逐篇核查。
- [教师/课题组公开 CV](https://www.macaoyouthscholars.org/cv/doc_278_2024-01-04-08-36-33747.pdf)：补充早期项目、医疗视觉和生物识别工作，但日期早于最新网页列表，不能替代当前 publication page。

注意：网络上还有香港理工大学 David Zhang、PolyU Visual Computing Lab 等同名/近名页面；本日志只讨论澳门大学的 Yibo Bob Zhang 和 PAMI 组。

## 2. 全量发表目录的结构化阅读

官方 publication page 的完整标题仍是唯一全量索引。为了便于后续 agent 读取，这里按研究问题而不是按年份重排：

### A. 手部生物识别（最成熟、最密集）

掌纹、掌静脉、指静脉、指关节纹和多模态手部识别构成团队的主线。代表性工作包括：

- Palmprint：Deep Discriminative Representation（Pattern Recognition 2020）、coordinate-aware/competitive methods、CO3Net（TIM 2023）、`Complete region of interest for unconstrained palmprint recognition`（TIP 2024）、VIS-NIR frequency-aware common feature（TIFS 2024）、mobile multi-view hierarchical graph learning（TIFS 2025）、PalmMamba denoising（TMM 2025）、dynamic generative verification（SPL 2025）、SF2Net sequence feature fusion（TIFS 2025）、deep hashing/controllable inter-class distance（TMM 2026）。
- Security/privacy：cross-database/template reconstruction attacks（2023）、dual-level cancelable framework and hack-proof storage（TIFS 2024）、physics-driven spectrum-consistent federated learning（IJCV 2024）、GAN data-poisoning backdoor attack（ICME 2025）、FedPalm / dynamic personalized federated learning（2025--2026）。
- Other hand traits：robust sparse least-squares recognition for finger vein and finger-knuckle print（TIFS 2024）、generative finger-knuckle recognition（ICPR 2024）、hyperspectral dorsal-hand/palmprint fusion（2018--2021）。
- Surveys/monographs：*Advanced Palmprint Authentication*（2025）、*Advanced Hand-based Biometrics*（2026）、*Hand-based Multimodal Biometric Fusion: A Review*（2024）、deep-learning palmprint survey（2025）。

**判断：**掌纹识别、移动掌纹、跨光谱、ROI、哈希、联邦和模板保护都已经有连续论文链。FYP 不应把“换网络、加 NIR/ToF、部署 Pi、做一个识别 demo”当作新问题。

### B. 医疗/非侵入式视觉和声学（应用价值高，但标签和伦理更难）

- Tongue/facial biometrics：TongueNet tongue localization/segmentation（IEEE Access 2019）、tongue geometry/color/texture、face color blocks for diabetes and diabetic retinopathy、tongue/sub-lingual vein/facial multi-view diagnosis、tongue-based privacy-sensitive age estimation with LLM/LISA（IJCB 2025）。
- Medical image detection/segmentation：retinal microaneurysm/vessel/optic-disc detection（2009--2010）、COVID CT、renal-cancer histopathology、fatty-liver missing-view completion（Computers in Biology and Medicine 2022）、diabetic-retinopathy local/long-range model（2024）、unsupervised nuclei segmentation（2024）、chest X-ray anomaly detection（TMI 2025）。
- Voice/other sensing：Voice-AttentionNet for multi-disease detection（AI 2025）、breath sample fatty-liver features（BIBM 2022）、antimicrobial-peptide MIC prediction（mSystems 2023）。

**判断：**团队核心问题是把便宜、非侵入、易采集的视觉/声学输入转成可量化筛查，而不是直接替代医生。FYP 可以研究 acquisition quality、domain shift、uncertainty 或 privacy，但不能未经临床合作宣称诊断。

### C. 缺失多视图、图/矩阵与稳健表示（最适合迁移到新传感器问题）

这条线从 LDA、稀疏/协同表示、低秩矩阵，到 incomplete multi-view clustering/classification：DIMC-net（ACM MM 2020）、unified tensor framework and missing-view inferring（AAAI 2021）、tensorized graph completion（AAAI 2023）、incomplete multi-view multi-label transformers（AAAI 2023）、uncertainty-aware pseudo labels/dual graph（ACM MM 2024）、reliable representation for missing views/labels（TPAMI 2025）。

我逐段核对了 [fatty-liver missing-view paper](https://pubmed.ncbi.nlm.nih.gov/36244304/)：其数据有 face、tongue、sublingual-vein 三个视图，随机移除 tongue/vein view（10--30%），用跨视图/视图内信息完成缺失视图，再评估健康/脂肪肝分类。它证明“设备故障/采集不完整”是实问题，但数据是医疗私有收集，不应直接拿来做 FYP 数据。

**判断：**最值得迁移的是“模态缺失时，系统是否知道自己不确定、是否应该降级或拒答”，而不是“如何把掌纹特征再提高 0.2%”。

### D. 图像复原、去噪和超分辨率（有 edge 连接，但算法已拥挤）

代表线包括 PID-guided attention（TNNLS 2021）、generative adaptive convolutions（AAAI 2022）、wavelet multi-stage denoising（PR 2023）、few-shot denoising（TCSVT 2023）、QFormer quaternion transformer（IJCAI 2024）、frequency-domain attention（TIP 2024）、self-supervised denoising/watermark removal（Neural Networks 2024）、implicit multi-scale Swin denoising（TCE 2025）、Cosine Network/Tree-guided CNN super-resolution（TIP/TCE 2025）。

我核对了 [QFormer 官方页面](https://www.ijcai.org/proceedings/2024/468)：动机是彩色通道关系和 Transformer 成本，方法是 quaternion transformation + sequential block，论文声称兼顾去噪效果和效率，但页面没有给 Raspberry Pi 端到端功耗结论。

**判断：**“再做一个去噪网络”不适合 FYP。可迁移的问题是**任务感知的 edge restoration**：图像 PSNR 变好是否真的提升识别/检测、拒答率和交互延迟；如果去噪让攻击图像也更容易通过，甚至应报告负面结果。

### E. 异常检测、开放世界和不确定性（适合非生物识别 FYP）

- [Uncertainty-aware prototypical learning for anomaly detection in medical images](https://pubmed.ncbi.nlm.nih.gov/38593560/)（Neural Networks 2024）：prototype 表示异常多样性，Bayesian uncertainty quantizer 表示像素级边界不确定性。
- [ODS-SAM](https://www.ijcai.org/proceedings/2025/129)（IJCAI 2025）：用 omni-dimensional state-space residual module 自动生成多尺度 SAM prompts，针对工业/医疗像素异常检测。
- Multimodal evidential learning for open-world weakly-supervised video anomaly detection（TMM 2025）：CLIP 视觉-语言关联、多尺度时序和证据收集器，目标是已见/未见异常。
- Prototype-guided dynamic-aware video anomaly、VLM-based explainable industrial anomaly、SAM-based pixel anomaly（2025 conference/journal list）。

**判断：**研究问题已从“分类准确率”移到“未见异常、弱标签、开放世界、置信度和像素定位”。这比做一个固定类别的门锁更容易构造公开数据和可审计指标。

### F. 跨域/测试时适应、活动和多模态系统

我核对了 [OFTTA 原文](https://arxiv.org/abs/2310.18562) 和 [官方代码](https://github.com/Claydon-Wang/OFTTA)：它针对跨人传感器 HAR 的分布漂移，以不做梯度优化的 EDTN 和固定大小 support set/prototype 做 test-time adaptation；论文明确讨论资源受限 edge device，代码提供 checkpoint 和 `adapt.sh` 复现实验。

此外，团队公开列表包含 open-vocabulary CLIP calibration、cross-person activity recognition、UAV multimodal detection、person re-identification、remote-sensing super-resolution、electronic-nose sensor drift compensation 等交叉合作。

**判断：**“测试时适应 + 安全拒答 + 资源预算”可以迁移到摄像头/传感器漂移，但直接把 OFTTA 改名成掌纹并不新；新问题应是具体的传感器、无标签漂移、错误累积和 reset/rollback 协议。

### G. 计算生物学和数据/工具平台（高价值，但不宜作为没有生物合作的独立 FYP）

[PhenoProfiler](https://www.nature.com/articles/s41467-025-67479-w)（Nature Communications 2026 issue / online 2025）把多通道 Cell Painting 图像直接编码为低维表型表示，组合 gradient encoder、Transformer 和 classification/regression/contrastive multi-objective learning，并在约 40 万高内容图像、约 842 万单细胞图像上做 leave-plate/dataset/out-of-distribution 评价。

**判断：**它提供“端到端表型表示 + OOD 评价 + 可解释的处理效应”范式，但需要细胞成像、药物标签和生物合作，不是把公开自然图像换进来就能复现的轻量 FYP。

## 3. 逐篇核对后的共同方法论

Bob Zhang 团队不同论文表面上横跨掌纹、舌象、矩阵学习、图像去噪、医疗和异常检测，但重复出现四个问题：

1. **真实输入不完整或不稳定**：视图缺失、跨手机/跨人、噪声、遮挡、低质量、开放环境。
2. **表示要可压缩且可泛化**：稀疏/低秩/哈希/轻量模型/紧凑模板。
3. **模型要知道不确定性**：质量评分、prototype、evidence、uncertainty、拒答。
4. **需要从算法走向系统**：医疗采集设备、手机、边缘设备、数据/模型更新和安全攻击。

因此新的 FYP 不一定要继续用掌纹；可以把实验室的方法论抽象为：

> **在真实传感器会失效、分布会变化、标签不完整和算力受限时，系统能否可靠地融合信息、知道何时不可信，并以可审计的方式降级？**

## 4. 候选 FYP 方向筛选

评分是研究判断，不是文献证明；`5` 表示更好。新颖性仍需在正式检索后确认。

| 候选方向 | 核心问题 | 新颖潜力 | FYP 可行性 | 数据/伦理风险 | 与现有设备/实验室匹配 | 结论 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 1. 传感器缺失/质量感知的多模态 edge vision | RGB/NIR/ToF 某一路失效或质量下降时，模型是否自动降级、拒答并控制能耗？ | 4 | 5 | 低--中 | 5 | **首选** |
| 2. 无标签测试时适应 + 安全回滚 | 摄像头、照明、用户/环境改变后，模型能否在 edge 上适应而不被错误伪标签污染？ | 4 | 4 | 中 | 4 | 强候选 |
| 3. 任务感知低照度复原 | 去噪/增强是否改善下游识别，而不是只改善 PSNR？ | 3 | 5 | 低 | 5 | 稳妥候选 |
| 4. 开放世界异常检测 + 不确定性拒答 | 只用正常样本/弱标签发现未见异常，并输出可解释 mask/置信度？ | 4 | 4 | 低 | 3 | 非掌纹首选 |
| 5. 生物识别模型后门/数据投毒审计 | 攻击能否植入，检测/清除后性能和误报如何？ | 4 | 3 | 中--高 | 3 | 安全方向，需老师批准 |
| 6. 舌象/声音隐私保护的非侵入筛查 | 用舌头或声音做年龄/健康筛查，同时做隐私、质量和跨设备评测？ | 4 | 2 | 高 | 3 | 需要临床/伦理合作 |
| 7. Cell Painting/虚拟细胞表型 | 表型表示、OOD 和处理效应解释 | 5 | 1 | 高 | 1 | 不适合当前 FYP |

## 5. 最推荐的新方向

### 首选：缺失模态和质量感知的 edge vision

暂定题目：

> **面向低成本多传感器设备的缺失模态感知视觉推理与安全降级**

最小实验不是训练一个巨型 Transformer，而是：

```text
RGB / NIR / ToF（或公开 RGB-D 数据）
    ↓ 人为模拟或真实制造：掉帧、遮挡、过曝、距离异常、模态缺失
质量估计 + uncertainty
    ↓
始终融合 / 质量感知融合 / 拒答或请求重采
    ↓
准确率、错误率、拒答率、p95、RAM、能耗、模态开启次数
```

它直接吸收了团队的 missing-view、quality-aware fusion、医疗多视图和 edge 经验，但研究对象从掌纹身份换成更一般的“传感器不完美时如何可靠工作”。可以先在公开 RGB-D/多视图数据上完成算法，再用实验室 RGB/NIR/ToF 设备验证采集故障和资源曲线。

**必须防止的伪创新：** 不能只把一个模态置零后报 accuracy；要区分 MCAR（随机缺失）、传感器相关缺失、质量退化和攻击性遮挡，冻结触发规则，报告 selective risk/coverage、误拒、恢复时间和能耗。若质量感知融合不优于简单 fallback，负结果也应保留。

### 强候选：无标签测试时适应，但加入安全回滚

OFTTA 已经解决了一个 HAR 版本，故不能直接宣称 TTA 新颖。可以把问题改为：

> **在低算力视觉设备上，如何在无标签环境漂移下适应，同时防止伪标签污染、性能崩溃和长期累积错误？**

实验可使用公开跨设备/跨照度数据，比较 frozen model、BN-only、OFTTA-style prototype、带置信度门的适应和 reset/rollback。核心指标是 target accuracy、worst-window accuracy、adaptation memory、更新次数、错误累积和恢复时间，而不是平均准确率。

### 稳妥候选：任务感知低照度/噪声复原

用 QFormer 等论文的思想做小模型对照，但问题限定为：

> **图像质量改善是否真的改善下游任务，并且没有增加 edge 交互延迟或放大伪造输入？**

可用公开真实噪声数据 + 实验室相机采集；必须同时报 PSNR/SSIM、下游任务分数、质量拒绝、攻击/伪影、Pi p95、RAM 和温度。不要再写成“提出新的去噪网络”，除非确实有算法贡献。

## 6. 不推荐的转向

- 继续做一个更深的掌纹识别 backbone：与团队现有掌纹论文链和商业成熟度相比，FYP 很难证明问题新。
- 直接做临床疾病诊断：标签、伦理、样本偏差和责任边界超过一年制 FYP；可改做数据质量/不确定性 benchmark，不做诊断结论。
- 直接复现 PhenoProfiler：需要 Cell Painting 数据、GPU 和生物解释，不适合当前硬件条件。
- 直接套 OFTTA、QFormer 或 ODS-SAM：已有论文和代码的“换数据集/换设备”不足以构成新方法；必须提出具体故障、预算、风险或可复现协议。

## 7. 下一步验证顺序

1. 先问老师：FYP 是否允许从掌纹转成一般 edge vision，还是必须保留生物识别应用。
2. 对现有盒子做一次硬件盘点：RGB/NIR 原始帧、ToF、可控光源、掉帧/曝光/能耗和可编程接口。
3. 选择一个公开可下载数据集，先实现 frozen baseline 和模态缺失/质量退化脚本。
4. 只保留一个主研究变量（quality-aware fusion、TTA rollback 或 task-aware restoration），其余作为对照。
5. 在写题目之前，做一次关键词检索和 artifact audit，确认不是已有论文的直接重命名。

