# 嵌入式掌纹系统先例阅读日志

最后更新：2026-08-21。本文精读 Shen et al. 的 2012 嵌入式掌纹系统，纠正一个容易出现的误判：edge palm recognition 不是因为 Raspberry Pi 才成为新方向；其研究价值必须来自现代硬件上的可验证问题，而不是“能跑在嵌入式设备上”这个事实。

## 1. 原始资料

- [Shen et al., *Embedded Palmprint Recognition System Using OMAP 3530*, Sensors 2012](https://doi.org/10.3390/s120201482)，开放全文，CC BY 3.0。
- [PubMed/PMC 记录](https://pmc.ncbi.nlm.nih.gov/articles/PMC3304123/)确认 DOI、版本和开放全文。

## 2. 系统实际做了什么

装置包含 blue LED、CMOS 广角相机、灯光/相机控制板、OMAP 3530 和触屏。CPU 为 600 MHz ARM Cortex-A8，另有 412 MHz TMS320C64x+ DSP。ARM 负责 capture、UI 和 peripheral control；DSP 做 Gabor-wavelet + LBP 的 `G-LBP` feature extraction，Hamming distance 做 matching。两侧用 Codec Engine/shared DDR memory 传递图像/特征。

它不是只在离线图像上跑模型：论文描述实物机、相机、照明、UI、采集到板上识别的分工。它也不是自由手场景：箱体上有三根定位柱，用户须把手放在固定位置，使旋转和平移较小。

## 3. 可核对的结果与边界

- PolyU 上的 image-level identification 比较：G-LBP `96.82%`，PalmCode `88.93%`；不是本项目需要的跨 session `1:1` FMR/FNMR 阈值，也没有 PAIS。
- 板上 DSP 的 feature extraction 为 `60 ms`，单对 matching 为 `3.9 ms`；100-palm identification 小于半秒。
- 数字只对应固定点 C/DSP、该 G-LBP、该尺寸输入、受限手位和 2012 的系统。论文没有 Raspberry Pi、RGB/NIR/ToF、ROI detector、深度网络、ARM-only、峰值 RAM、温度、输入 energy、现代 runtime 或 capture-to-decision p95。
- 论文没有 PAD、IAPMR、APCER/BPCER、攻击材料分层、相机注入、relay 或模板保护评估。因此“real time and robust”是作者当时的工程描述，不是本 FYP 的安全证明。

## 4. 与 2025 RDRLA 的对照

| 先例 | 已经证明 | 留给本项目的问题 |
| --- | --- | --- |
| OMAP 2012 | 受控手位下，照明、相机、ARM/DSP pipeline 和本地 matching 能组成实际嵌入式终端。 | 不受控距离/姿态、现代 Pi runtime、多光谱/ToF、PAD、全链资源和安全 release。 |
| RDRLA 2025 | 无 FVP 的 adaptive ROI 能处理复杂背景/手势，且有公开 PyTorch implementation。 | 它在 GV100 GPU 测试，未给 edge resource/capture measurement，且不测 PAD。 |

这两项证据合起来排除了两个相反但同样错误的叙事：既不能说“嵌入式掌纹还没人做”，也不能说“ROI 论文已证明 Pi 端侧可用”。可研究的交集是指定装置上从 raw capture 到 local decision 的失败率、时延、资源、重采和攻击边界。

## 5. 对最小 demo 的动作

1. 将受限几何写成显式设计变量：记录距离、角度、ROI failure、quality reject 和 retry，而不是在固定手位取得高分后暗示自然交互。
2. 分段测量 `T_capture`、`T_ROI`、`T_embedding`、`T_match`、`T_decision` 与 `T_interaction`。不得将某个 matcher/DSP inference 数字称为整机速度。
3. B0 可采用传统、可解释 ROI/matcher 作工程比较，但不能借 OMAP 的 accuracy/latency 作 Pi benchmark；Pi 的模型、runtime、线程、温度和真实输入须冻结后独立测量。
4. 每个“authentication/security”结论仍须报告 FMR/FNMR、IAPMR/APCER/BPCER、PAIS/session holdout 和 fallback；本地设备本身不增加这些证据。

## 6. 禁止写法

- `首次将掌纹识别部署到 edge/Raspberry Pi 类设备`。
- `60 ms 说明 Pi 的整个掌纹锁会实时`。
- `定位柱下的识别准确率说明自由手掌可用`。
- `板上处理或本地模板说明 PAD、隐私或门锁系统安全已经解决`。

