# VIS-NIR 掌纹阅读日志：跨光谱匹配不等于活体检测

最后更新：2026-08-21。本文精读的是 Fei et al. [*Learning Frequency-Aware Common Feature for VIS-NIR Heterogeneous Palmprint Recognition*](https://doi.org/10.1109/TIFS.2024.3441945) 的正式书目信息与可访问摘要。全文、数据、代码、权重和部署工件尚未取得，因此不复述实验数字或具体 split。

## 1. 它实际回答的问题

作者将问题定义为：gallery 和 probe 分别在 visible light (VIS) 与 near-infrared (NIR) 下采集、存在较大 modality gap 时，如何做 identity matching。其 FFLNet 先提取多尺度浅层特征，再以 Fourier transform 得到 frequency-specific representations，利用共通与 modality-specific 信息，最后回到 spatial domain 学习 identity-invariant representation。摘要称其在三个 heterogeneous palmprint databases 上评估。

这是**异构/跨光谱识别**：回答“同一人不同光谱的两张掌纹能否相配”。它不是：

- print/screen/patch/replay 是否会被拒绝的 PAD；
- 随机 illumination command 与接收到的 frame 是否存在 response relation 的 freshness 验证；
- 同步 RGB/NIR capture 是否可靠；
- Pi 的延迟、RAM、能耗或相机 pipeline；
- 本地模板是否可撤销/不可逆，或澳门用户是否接受系统。

## 2. 对 B0/B2/M 的具体影响

| 路线 | 这篇工作可支持 | 不能借用的结论 |
| --- | --- | --- |
| B0 RGB | 单一 spectrum baseline 不能自动外推到异构 query。 | FFLNet 的结果不能证明我们的 RGB matcher 或 Pi。 |
| B2 static RGB/NIR | 若 enrollment/probe 真的跨光谱，cross-spectral matching 是正式已有问题，可作独立 recognition arm。 | RGB/NIR fusion 或 Fourier feature 不是新颖点，也不是 PAD。 |
| M challenge | 多帧响应可能要面对 VIS/NIR representation gap。 | 不能把匹配到共通特征解释为“真实呈现”或 challenge-response 成功。 |

## 3. 由此增加的协议约束

1. 在数据 manifest 写明每一个 enrollment/probe/template 的 spectrum、sensor、IR-cut state、illumination command 与实际 frame state；不把 VIS/NIR 样本悄悄混入一个 pooled recognition score。
2. 若比较 RGB-only、static RGB/NIR 和 cross-spectral matcher，所有路线使用相同 identity/session holdout，threshold 只由 development set 冻结。
3. PAD 主结果仍按 PAIS/material/output-capture chain/session 给 APCER/BPCER 与固定 matcher threshold 下 IAPMR；cross-spectral TAR 只能作为 recognition 维度。
4. 在未拿到代码、weight、license 与目标 Pi profile 前，不实现 FFLNet，也不引用其效率/准确率作为 B0/B2 预期。

## 4. 研究判断的变化

此前“RGB/NIR 为何有价值”的表述仍过于笼统。现在应拆成三个可彼此失败的假设：

1. **Recognition:** 两个光谱的掌纹信息能否补足/稳定 identity score？
2. **Capture quality:** 受限几何、IR-cut 与已验证的 illumination state 能否提高 ROI/retry 稳定性？
3. **Attack risk:** 静态或主动多光谱是否会在未见 PAIS 上降低 IAPMR，并维持 bona-fide usability？

只有第三项对应风险门控；第一项成功不会推出第三项成功。这个拆分也避免把一个更复杂的 RGB/NIR matcher 命名为 liveness。
