# 随机灯序与跨帧差异阅读日志：已有掌部先例，不是本项目创新

最后更新：2026-08-21。本日志精读 [Stanuch, Wodzinski & Skalski, *Contact-Free Multispectral Identity Verification System Using Palm Veins and Deep Neural Network* (Sensors, 2020)](https://doi.org/10.3390/s20195695) 的全文。它是最直接的反证之一：本项目不能把随机 RGB/NIR 灯序、两模态无接触采集、跨帧差异，或“无需用户额外动作”包装为掌部 edge 创新。

## 1. 原文实际实现的机制

该系统以 CCD、NIR 与 UV 灯板、偏振片采集无接触手掌。每次 examination 取一张 NIR 与一张 UV 图，顺序随机；系统知道顺序，用户不知道。作者明确说明，这让攻击者需猜测顺序或模仿不同照明下图像的变化，并建议在一次 verification 中重复该过程。

它不只将两张图送进两个 recognition pipeline：作者还比较 NIR 与 UV 图，写明若图像没有足够差异，就按 presentation attack 处理并拒绝。这个方法与本项目最初设想的“随机 illumination 加跨帧 relation”有实质重叠，不能在论文中略去。

## 2. 它证明了什么，没证明什么

| 可从原文确认 | 不能从原文推出 |
| --- | --- |
| 掌部 biometric 已有随机双光照顺序、跨帧差异检查和可重复短采集的设计。 | 这种机制在本项目 RGB/NIR/ToF、Raspberry Pi、实际相机同步与弱光条件下有效。 |
| 论文做了 `1:1` verification；515 人、10,160 图；其 combined TPR 在作者的 EER threshold/随机图像切分下为 99.5%。 | 该数字是未知 PAIS、跨材料、跨日 session 或 target-match attack 的防护效果。 |
| 作者把随机顺序/差异检查作为减少 presentation attack 的设计动机。 | 已验证 APCER、BPCER、IAPMR、attack diversity、攻击者是否预知顺序，或高级 screen/relay/真实手贴片下的风险。 |

论文的数据将同一手的图像随机分入 train/validation/test；这对于其 recognition 任务可以报告结果，却不能成为本项目的 blind PAIS/session 协议。也不能从作者的“fraud 更困难”用语导出绝对 liveness 或 replay-resistance 结论。

## 3. 对 M 的直接收缩

M 不再定义为“随机 RGB/NIR challenge”。该表述既没有说明可验证的 response，也会掩盖已有文献。

仅在以下条件都满足时，M 才保留为一个条件性实验臂：

1. claim 后生成 command，并记录实际 illumination、frame order、曝光、掉帧、延迟与 ROI alignment，而不是只记录 seed 或软件命令。
2. development data 上预先冻结一个明确的 response relation 和阈值；例如受控曝光下与 command 对应的反射/质量一致性。它必须比“帧不同”更具体，并在测试前不可修改。
3. B0/B1/B2 与 M 共享 ROI、identity matcher、identity threshold 和攻击者知识假设；M 的唯一变化是该 verifier。
4. test 至少按 PAIS/material、capture/output chain 与 session 留出，并在最终流程报告 APCER、BPCER、IAPMR、ROI/retry、p95 interaction time 与输入端能耗。

即使满足这些条件，正确问题仍是“是否有净收益”，不是“是否首次实现随机主动光照”。若 B2 已足够、M 只靠提高 BPCER 获得低 IAPMR、或未见 PAIS 不保留增益，M 应被淘汰或降为工程测量的负结果。

## 4. 写作用语

可写：`post-claim, actual-state-logged illumination-response gate evaluated against a static multispectral baseline`。

不可写：`first randomized illumination palm liveness`、`random sequence proves liveness`、`two-frame difference prevents replay`，或把 2020 recognition TPR 写成自身系统的 PAD/edge 性能。

## 5. 这次阅读如何改变研究决策

这篇 2020 全文使“主动采集”候选更窄，但没有把项目归零。它把可研究的部分从器件/随机化移动到可审计的实验组合：在已知硬件约束下，真实 command-state、ROI/几何、attack holdout 和 edge cost 是否一起支持某个小型 gate。这个问题仍需要 Gate 0 实机测量和合规自采数据回答，不能由文献代答。
