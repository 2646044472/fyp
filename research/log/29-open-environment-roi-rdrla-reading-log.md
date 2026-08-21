# RDRLA 开放环境 ROI 阅读日志

最后更新：2026-08-21。本文记录 Chai et al. 的 2025 IEEE TIFS 论文，作为 PKLNet、轻量 ROI 之后的开放环境 ROI 强基线；重点是它解决了什么，以及它没有替我们解决什么。

## 1. 原始资料

- [论文开放 PDF](https://liru0126.github.io/collections/2025_tifs/chai_tifs2025.pdf)，IEEE TIFS 20 (2025), pp. 421--435, DOI `10.1109/TIFS.2024.3516539`。
- [作者代码仓库](https://github.com/godfatherwang2/RDRLA)：公开 FFARD、CHSST、adaptive PROIE、RLANN 等 PyTorch 目录和 requirements；README 还列出 HIT-NIST-V1 与 BJTU PalmV2 的 ROI 数据链接及非商业使用限制。

## 2. 论文问题与方法

论文把开放环境掌纹识别拆成 PROIE、feature extraction、matching 三段，指出传统 ROI 依赖 finger valley points (FVPs)，而在手指未充分伸展、复杂背景、光照变化和自由姿态下，FVP 可能不可见。其 RDRLA 包含：

1. `CHSST`：跨数据集的 hand-shape semantic transfer，用分割网络从复杂背景提取手部。
2. `FFARD`：用手掌内接圆搜索做自适应 ROI，摆脱手工标注/显式 FVP 定位。
3. `RLANN` + `ACPLoss`：用 recurrent layer aggregation 和 angular center proximity loss 提取并约束识别特征。

论文明确把 FFARD 当成可组合的 ROI 模块，而不是必须与 RLANN 绑定的硬件方案；这对我们的 B0/B1 模块化设计有参考价值。

## 3. 实验边界

- PROIE 训练使用七个较受控数据集；识别使用 HIT-NIST-V1、MPD、BJTU PalmV2 和 IITD。作者把后三个开放环境数据集用于复杂背景、光照和姿态测试。
- close-set 对有两 session 的数据使用第一 session 训练、第二 session 测试；single-session 数据按 class/image 顺序切分。open-set 将 class 分为训练与测试，避免把类别当成同一个身份的随机 image split。
- 论文报告 FFARD+RLANN 的 close-set Rank-1/EER，以及 open-set Rank-1/EER；open-set 例子包括 HIT-NIST-V1 `94.29% / 8.43% EER`、IITD `99.15% / 1.53%`、MPD `99.62% / 6.13%`，但这些是作者数据集、训练策略和识别模型下的结果，不是 Pi 或我们设备的预期性能。
- 训练机为 Intel i7-9700K、16 GB RAM、NVIDIA Quadro GV100 32 GB；代码是 PyTorch。论文的“computational complexity”比较仍是模型间比较，没有 Raspberry Pi/ARM、CPU-only、峰值 RAM、thermal、energy 或端到端 capture-to-decision 结果。
- 代码仓库公开实现，但仓库声明的 ROI 数据有非商业限制；README 未提供一个冻结的 ARM inference artifact、release weight/benchmark 或完整 raw-capture protocol。

## 4. 对本项目的结论

1. “自由手姿态导致 ROI 失败”是有原始论文支持的现实问题；如果现有实验室装置要求用户把手放到固定框内，最可测的创新可以是降低姿态/距离容错下的 ROI failure 和重采次数。
2. FVP-free/adaptive ROI 已经是 2025 的明确研究方向，不能把“自动 ROI”或“edge-aware ROI”写成空白。我们真正尚未回答的是：在指定 RGB/NIR/ToF 硬件和 Pi 上，ROI、质量门、embedding、matching 的总延迟与失败率如何。
3. RDRLA 的 open-set/class split 比随机图像 split 更接近泛化，但仍不是我们的 session、device、illumination、PAIS protocol；不能把其 EER 当作 authentication release threshold。
4. RDRLA 代码可以作为离线 ROI 对照阅读，不应直接成为最小 demo 依赖。先用可解释 baseline 测 `ROI success`、`T_ROI` 和端到端 p95，再决定是否移植轻量模型。

## 5. 不能写的句子

- `RDRLA 已经证明 Raspberry Pi 可实时运行`：论文没有 ARM/Pi 测量。
- `FVP-free ROI 已解决开放环境`：作者结果仍依赖数据集、训练/测试划分和受控采集假设，且论文结论自己把更轻量结构列为 future work。
- `RDRLA 的 EER 就是掌纹锁的安全性`：EER 是识别验证指标，不包含 PAD、相机注入、模板保护、relay 或门锁控制安全。

