# Bob Zhang / PAMI 非掌纹方向补充精读日志

日期：2026-08-27。目的不是证明“教授什么都能做”，而是避免实验室已有掌纹盒子把 FYP 锁死在掌纹。官方 [PAMI 主页](https://pamigroup.github.io/) 把研究组织为 hand biometrics、medical biometrics、robust representation、image restoration 和 computational biology 五线；本日志抽取各线的代表原文，判断其可迁移的**问题**，而非复制网络。

## 1. 缺失多视图：方法根源强，但原论文不是 edge 系统

[TIMVC-IGC](https://ojs.aaai.org/index.php/AAAI/article/view/26340)（AAAI 2023，Bob Zhang 合著）针对 incomplete multi-view clustering：用低秩结构推断缺失 instance、构建各 view 的 complete graph，再做跨 view consistency 和 tensor constraint。它解释了 PAMI 为什么持续研究“缺失 view”，但任务是离线 clustering，不包含相机时间戳、实际传感器故障、动作选择、端侧时延或能耗。

**可迁移：** 不应把“不完整输入”当作异常样本丢掉，系统要建模它。

**不可迁移：** 不能把 tensor graph completion 换成 RGB-D 并称为 edge innovation。
**FYP 结论：** 用这条理论线支撑“可靠降级/拒答”的问题背景，但实验必须由真实或可解释故障事件、任务风险和资源测量构成。

## 2. 图像复原：教授组已有网络，但可转成 task-aware 评测

[Generative Adaptive Convolutions / FADNet](https://ojs.aaai.org/index.php/AAAI/article/view/20088)（AAAI 2022）把跨相机/ISP 的真实噪声差异作为问题，以 input-conditioned dynamic filters 适应特定噪声；[QFormer](https://www.ijcai.org/proceedings/2024/0468.pdf)（IJCAI 2024）以 quaternion colour relation 和顺序 Transformer block 降低 attention 的计算。两者的原始目标都是 denoising reconstruction，而不是 edge 传感器的最终决策安全。

QFormer 论文的实验训练使用 A100、SAM 类 ODS-SAM 使用 ViT-H/A100，均不能拿来证明 Pi 可行。更根本的是，PSNR/SSIM 的改善不自动代表下游识别、检测或用户交互风险改善。

**可迁移：** 将复原视为可被系统选择的一种动作，并问它是否让下游任务的 risk-coverage Pareto 更好。

**不建议作为主题：** “提出轻量去噪网络”或“在 Pi 跑 QFormer”，因为两者都不足以构成问题新颖性。

## 3. 开放世界 anomaly：问题适合 FYP，ODS-SAM 不适合端侧复现

[ODS-SAM](https://www.ijcai.org/proceedings/2025/0129.pdf)（IJCAI 2025，Bob Zhang 合著）将 SAM 用于工业/医疗的 pixel-level anomaly，使用自动 prompt encoder、multi-scale feature 和 state-space module；原文以 MVTec AD 与多份医疗数据评估，训练设定为 A100、SAM ViT-H、最多 200 epoch。它清楚说明直接应用 SAM 并不能解决 anomaly，但也说明“自动 prompt + SAM”已有直接先例。

**可迁移：** 未见缺陷、像素/样本级不确定性、检测失败的可解释性。

**不可迁移：** SAM/ODS-SAM 模型与 A100 数字，或医疗诊断结论。
**FYP 结论：** 可把 O 做成轻量正常样本基线 + 未见缺陷留出 + calibrated abstention + Pi 资源测量；重点不是追赶 ODS-SAM 的 MVTec 分数。

## 4. 医疗与计算生物学：研究价值高，但当前不应选为独立 FYP

[PhenoProfiler](https://www.nature.com/articles/s41467-025-67479-w) 使用多通道 Cell Painting、约 40 万高内容图像和约 842 万单细胞图像，面向药物扰动/表型表示；PAMI 主页将其归为计算生物学和虚拟细胞方向。该工作对 OOD、leave-plate/dataset split 和表型解释有方法论价值，但需要大型生物数据、GPU、药物/细胞领域解释，不能用普通相机图像替代后仍声称解决同一问题。

Tongue/face/voice 的医疗感知工作同理：可借鉴非侵入采集、quality control 和 uncertainty，却没有临床合作、同意、标签治理与合适 sample size 时，不能写成疾病诊断 FYP。

## 5. 选题后果

掌纹不再是默认方向，只是我们已有硬件时的一个可能 case study。按当前条件排序：

1. **真实传感器失效下的多模态 edge vision 闭环**：承接 incomplete multi-view，公开数据和硬件都可逐步接入。
2. **开放世界工业异常 + 校准拒答**：承接 ODS-SAM/uncertainty，但用轻量模型和公开数据，不用 SAM 作为主干。
3. **task-aware restoration**：承接 FADNet/QFormer，但必须证明修复动作改善下游风险/资源，不能只报图像分数。
4. **掌纹条件式采集**：只在老师希望用已有设备或 Gate 0 确认硬件可观测故障时保留。

医疗诊断、Cell Painting 和后门攻击不删除，但在没有相应数据、伦理/安全批准和算力合作前，不进当前短名单。
