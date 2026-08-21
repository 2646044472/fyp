# 采集质量与 ToF 近邻的可复现性日志

最后更新：2026-08-21。本日志复核 [Fan et al., *Smart touchless palm sensing via palm adjustment and dynamic registration*](https://www.nature.com/articles/s41467-025-58213-7) 的实验边界与两个作者公开工件：[ERAlign](https://github.com/zoe-abu/ERAlign) 和 [Simulation-of-the-Sensing-Model](https://github.com/zoe-abu/Simulation-of-the-Sensing-Model)。目的是判断它能否成为 B0/B1 的依赖，而不是仅凭论文标题判断“已有代码”。

## 1. 论文真正解决的问题

该工作把距离、亮度/清晰度、旋转、ROI alignment 与 video-based registration 视为同一个 sensing chain。它以多距离 samples 讨论 registration trade-off，并提出 edge-aware rotation-invariant ROI alignment (ERAlign)。其 CUHKSZ collection 是桌上、从下向上、无 enclosure 的 NIR/visible acquisition，距离 6--14 cm；论文还承认 palm curling 和多个手掌的复杂背景会失败。

这直接否定两种写法：

- “距离引导、视频注册或稳定 ROI 是本项目创新”；
- “距离 sensor 天然是 liveness/PAD sensor”。

从该论文可借用的只是问题拆分：距离和姿态会改变 ROI/quality，因此 B1 应独立测这些变化及重采成本。它不评估 ToF 对 PAIS 的判别、主动 illumination relation、Pi end-to-end latency/energy、IAPMR 或澳门采用。

## 2. 工件审计

| 工件 | 已核对到的内容 | 当前可用范围 | 关键缺口 |
| --- | --- | --- | --- |
| [ERAlign](https://github.com/zoe-abu/ERAlign) | CC-BY-NC 4.0；5 commits；`run_roi.py`、传统 Gabor/ROI 脚本，依赖 OpenCV, NumPy, Shapely, scikit-image, NetworkX；README 只要求修改本地 dataset path 后运行。 | 可读的 ROI/rotation 对照候选；只有在许可与输入格式被核对后，才可用于开发机算法比较。 | 无相机/ToF/LED service、无数据、无 model weight、无 ROI ground-truth manifest、无 ARM/Pi/runtime/latency/RSS/energy recipe。 |
| [sensing-model simulator](https://github.com/zoe-abu/Simulation-of-the-Sensing-Model) | C/C++ OpenGL project；README 指向 MinGW、CMake、GLUT/GLEW/GLFW/GLAD/SOIL/GLM，含 v1.0 release。 | 用于理解作者的 optical/distance simulation 假设。 | Windows-oriented graphical simulation，不读实验室 raw frame，不控制 ToF/LED/camera，也不构成 edge deployment artifact。 |
| CUHKSZ data | 论文的 data availability 说明：原始 data 在 2027 confidentiality period 后，才可为 non-commercial use request。 | 当前只能阅读 protocol。 | 现在不可下载、hash、审计 identity/session/split 或复现论文图表；不能纳入 P0/P/S。 |

## 3. 对 Gate 0/B1 的可执行影响

1. 先测**本机** `ToF distance -> ROI success/overlap -> sharpness/quality -> retry -> identity score` 的关系；不要直接搬用 6--14 cm 或注册样本数。
2. 每个 capture record 保存 ToF raw/filtered value、distance bin、camera exposure/gain、actual illumination、ROI box/keypoints、ROI overlap/alignment residual、rotation proxy、quality result、drop/timeout 与时间戳。
3. 质量 gate 的报告要同时有 accept/retry 分布、bona-fide BPCER、ROI failure 和 `T_interaction`。只挑选成功 ROI 来比较 EER 会掩盖真实交互失败。
4. ERAlign 若被运行，只能作为 `image-only ROI baseline`；其输入、commit hash、license、环境和失败样本必须被固定，且不能把开发机 ROI result 称为 Pi sensing result。

## 4. 本次反思

这篇高质量系统论文并没有消灭我们的 FYP 问题，反而迫使问题更小：不是“是否能发明 smart palm sensing”，而是**在已有实验室硬件上，ToF/quality control 的净收益是否大于它的采集摩擦和 edge 成本**。即使结果为否，也应成为主结论的一部分，而不是改名为“智能采集”继续宣称创新。
