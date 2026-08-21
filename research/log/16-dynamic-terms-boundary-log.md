# "Dynamic" / "Sequence" 掌纹术语边界日志

最后更新：2026-08-21。本日志处理一个论文检索中很容易造成误判的问题：标题出现 `dynamic` 或 `sequence`，不代表研究对象是设备采集到的连续帧，也不代表它处理了主动 challenge、活体或 PAD。

## 1. 先冻结术语

| 术语 | 本项目中必须满足的最低含义 | 不能仅凭什么成立 |
| --- | --- | --- |
| 物理时序采集 | 相机在一次呈现中记录两个或更多有时间顺序的原始 frame，且日志能还原实际 frame order。 | 模型内的 token sequence、batch、pair 或数据增强。 |
| 主动 illumination challenge | claim 后，由设备随机选择并记录 illumination command；传感链实际观察到对应状态。 | 仅让 RGB/NIR 轮流拍摄，或只记录软件 command。 |
| response relation | verifier 预先定义并检查 command、实际 illumination/frame order、可测响应之间的关系。 | 随机序列本身、多个 frame 的拼接，或一个普通 PAD classifier。 |
| freshness 假设 | 在上述 relation 已实现后，对写明的 replay/PAIS 威胁提出、并以留出测试检验的有限假设。 | "dynamic"、"multi-frame" 或 "liveness" 的营销式命名。 |

因此，B0/B1/B2 只回答识别和采集质量。M 即使完成，也只能在实际 relation、未见 PAIS/session 和 target-match IAPMR 都测完后，讨论有限的 freshness 证据；不能宣称一般性活体检测。

## 2. 反例一："dynamic" 是特征空间的动态配对

[Yang et al., *Beyond Static Features: Dynamic Pair Construction for Palmprint Verification* (IEEE Signal Processing Letters, 2025)](https://doi.org/10.1109/LSP.2025.3611328) 的可访问书目信息及摘要/索引描述，把 dynamic 放在 class-aware pair synthesis、classifier-guided regularization 和 matching representation 上。这里的动态对象是用于训练/匹配的 feature pair，不是从掌纹传感器获得的时间帧。

本轮没有取得全文、代码、数据、权重或采集协议。因此只能作如下保守判断：它是一个必须避免混淆的 `dynamic` 术语先例，**不是**主动 RGB/NIR 采集、frame synchronization、challenge-response、PAD 或 Pi 运行的证据。不能从它推出数据集、攻击模型、性能数字或物理安全结论。

## 3. 反例二："sequence feature fusion" 是单帧的空间 token

[Liu et al., *SF2Net: Sequence Feature Fusion Network for Efficient Palmprint Recognition* (IEEE TIFS, 2025)](https://doi.org/10.1109/TIFS.2025.3611692) 的官方 [repository](https://github.com/20201422/SF2Net) 提供 MIT 代码。其 [model](https://raw.githubusercontent.com/20201422/SF2Net/master/model/sf2net.py) 注释明确输入为 `batch_size x 1 x 128 x 128`；[inference](https://raw.githubusercontent.com/20201422/SF2Net/master/inference.py) 分别读取两张灰度 ROI、提取各自 feature 后计算 score。网络把局部、一阶和二阶空间 feature 送入 ViT 并融合，这解释了题名中的 sequence，但没有视频/帧序列输入。

这给出较强的工程结论：SF2Net 是 palmprint recognition architecture 的研究参照，不是 physical sequence capture 的反例或同类方案。它不测 illumination command、实际 frame order、response relation、PAIS 或 IAPMR，因此不能证明 M 的安全目标已被覆盖。

可复现性也不能被过度解读。repo 为 MIT，inference 有 CPU device fallback；但其 [requirements](https://raw.githubusercontent.com/20201422/SF2Net/master/requirements.txt) 以 CUDA 12.1/PyTorch 2.4.1 为主，本轮未见可下载 dataset、release asset 或预训练 weight。CPU path 不等于可在具体 Pi 安装、也不等于有足够延迟/RAM/温度/能耗表现。B0 不以它为默认依赖。

## 4. 对题目和实验的实际影响

1. 不使用“first dynamic palmprint”“sequence-based liveness”“dynamic palmprint security”作为项目创新语句。这些名称无法区分 feature-space、spatial token 和 physical temporal capture。
2. 若 Gate 0 证实硬件能控制并观察 RGB/NIR 状态，M 的准确名称是：**post-claim active illumination acquisition with a verifier-checked response relation**。这仍是候选实验机制，而非已证明贡献。
3. 日志必须保存 command timestamp、actual frame timestamp/order、drop/timeout、LED/IR-cut state、ROI/quality 和 challenge ID。只保存 command 不足以证明实际 challenge。
4. 评测必须先冻结 B0/B1/B2 及 matcher threshold，再在 identity/session/PAIS 留出下比较 M 的 bona-fide retry/BPCER、APCER 和 target-match IAPMR。若 M 没有相对 B2 的增益，或 relation 无法稳定验证，停止安全叙事。

## 5. 这次阅读改变了什么

它没有证明主动采集是新的，也没有证明主动采集无价值。它消除了一个更基础的写作风险：将论文标题中的 `dynamic` 和 `sequence` 误当成自身的物理时序创新。当前可辩护的空白仍是条件性的系统问题：在具体低成本 RGB/NIR/ToF 硬件上，能否可靠记录并核验主动采集关系，并在预冻结、未见攻击/时段的评测中，相对静态多谱 B2 显示净收益。这个问题必须由 Gate 0 与实测回答。
