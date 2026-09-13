# 传感器状态、任务状态与动作：第三轮候选重审

日期：2026-08-27。这个日志回答一个会改变题目排序的问题：原先的“真实传感器失效闭环”会不会只是一个较大的 demo？本轮不先设计模型，而是找能够覆盖相同输入、相同状态标签、相同动作后果的直接邻居。

## 1. 重新定义问题

“模型置信度低”不能说明系统为什么不可靠，也不能自然推出应采取什么动作。对于一个多传感器 edge 任务，应至少分开四层变量：

```text
physical / timing sensor state
    -> environment / target observability state
    -> task confidence and residual observability
    -> action (continue / single-sensor fallback / re-acquire / calibrate / abstain)
    -> task loss + recovery / latency / energy cost
```

例子：RGB 过曝可能是 camera exposure 异常，也可能是传感器完全健康而场景没有可用纹理；ToF 的无回波可能是 sensor fault、距离/材质造成的物理限制，或目标超出任务范围。把这些都压成一个 fusion weight，系统无法说明为什么继续、重采或拒答。

研究问题改为：

> 在低成本 RGB/NIR/ToF edge 设备的受控真实事件中，显式分离 sensor state、environmental/target observability 与 task state，是否比 `always fuse`、`fixed fallback` 和 quality-aware router 更能在固定人工重试、延迟和能耗预算下减少高风险自动接受？

这里的贡献单位是**可证伪的事件标签与动作协议**，不是一个新的 fusion backbone。

## 2. 直接邻居一：古典主动诊断已经存在

[Murphy 与 Hershberger 的 sensing-failure recovery](https://publications.ri.cmu.edu/storage/publications/pub_files/pub4/murphy_robin_1999_1/murphy_robin_1999_1.pdf) 早已提出：机器人用 active perception 对 sensing-failure cause 生成假设、安排测试以消除混淆，并将 recovery method 连接到 cause。它还强调 “sensing failure” 可来自硬件、软件或环境，而不只是坏传感器。

这排除了“按根因诊断并重试”作为概念创新；任何新工作必须说明：为什么现代视觉、异质互补传感器、真实 telemetry 与 calibrated task-risk 让问题有不同、可验证的结论。

## 3. 直接邻居二：现代端到端缺模态策略已存在，但测试过于粗糙

[MAMMOTH (2026)](https://academ.us/article/2607.12965/) 是很强的近邻：真实越野机器人融合 RGB、thermal、3D point cloud 和 velocity，以 modality dropout 训练稀疏 MoE/diffusion navigation policy，并在五个真实环境运行；它报告 collision、goal success 和 manual takeover。该工作已覆盖：

- 多模态端到端 action；
- 真实机器人部署；
- 低光环境；
- 单路传感器消失后的 task-level 后果。

但其 missing-modality ablation 的定义是**完全关闭一整路 sensor**，并以 `mask-and-ignore` 处理；它没有独立标注 sensor health、环境可观测性、校准/时间状态或“剩余模态是否足以完成当前动作”。它也不根据根因在 `reacquire / recalibrate / abstain` 中选择。这不是小差别：整路黑屏是最容易检测的失效形式，不能代表 partial blur、saturation、IR illumination drift、ToF high variance、single-sector loss 或 time offset。

## 4. 最新综合证据：问题重要，但不能越界宣称首创

[2026 autonomous-vehicle systematic review](https://www.mdpi.com/1424-8220/26/16/5316) 给出最有用的外部审计：

- 将 sensor degradation、sensor failure 与 downstream perception failure 固定为不同定义；
- 明确区分 **sensor health**、**task confidence** 和 **residual observability**；
- 在其 65 个 primary studies 中，只有 5 项到 operational/system response；
- 指出未来 open benchmark 应联合包含 physically measured degradation、environmental state、perception output 和 vehicle response，且应测 detection delay、false warning、severity at detection 与 selected-response 的 downstream risk。

这不是“没有人研究”的证明，反而证明这个领域已有相当多的 fusion/health work；但它是一个强的、近期的依据，说明现有公开证据仍常把物理失效、环境 shift、感知错误和行动后果断开。

## 5. 与原 R 的比较及排序更新

| 判断维度 | R：复原证据约束 | S：状态分离 + 动作协议 |
| --- | --- | --- |
| 直接成熟先例 | tomography hallucination 定义、measurement consistency、FDA assessment tool、data-consistent diffusion | health monitoring / fault recovery / missing-modality policy 很多，但同一联合标签与 action-cost protocol 仍未见 direct neighbor |
| 对实验室现有 RGB/NIR/distance 硬件的匹配 | 要求 pixel-level alignment、ground truth detail 和 paired task labels，门槛高 | 要求 telemetry、可控事件与一个真实下游任务，现有硬件更接近 |
| 最容易退化成 | “复原图更好看”或普通 uncertainty map | “关掉某一路看看 accuracy” |
| 如何避免退化 | 必须实现 independent raw support -> hard veto | 必须记录 partial physical faults，并区分 health、observability、task risk 与 action cost |
| 当前决定 | 记录为高风险 reserve，不列入三项主候选 | 恢复为首个非掌纹 live candidate |

## 6. S 的最小研究协议与失败标准

### 事件设计

在可控采集场景中，每个 episode 记录 raw RGB/NIR/ToF、frame/timing/illumination metadata、功耗和温度。物理事件须区分：

1. sensor/timing: drop, exposure/illumination drift, ToF high variance/no-return, calibration/time offset；
2. healthy sensor but hard scene: target distance/pose, low texture, reflective/absorbing material, occlusion；
3. task ambiguity: remaining modalities 的信息不足以完成该 action。

“随机 mask”“单帧置零”只能作为压力测试，不得替代真实事件。

### 对照与终点

- `B0` always fuse；`B1` fixed RGB (或单模态) fallback；`B2` quality/router；`B3` state-separated action policy。
- 状态层：root-cause macro-F1、health false alarm、detection delay、severity-at-detection。
- 任务层：accepted-task error / false pass、coverage、每类 action 的 recovery success。
- 系统层：p50/p95 capture-to-decision、energy、RAM、thermal state、人工重试次数。

主假设只在 `B3` 在预冻结 budget 下改善 risk-cost Pareto 时成立。若 `B1` 或 `B2` 同样好，结果应如实写成“复杂 state separation 不值得”。

### 立即推翻条件

1. 找到同等价 sensor、真实 partial fault、四层同步标签、动作成本和下游 risk 的公开工作；
2. 实验室硬件无法取得 actual LED/frame/ToF/timing/energy telemetry，无法区分故障和 scene；
3. 只有整路 mask，没有 physical/scene hard negatives；
4. 没有任务决定的真实代价，只有分类准确率。

## 7. 结论

S 不是“再造一个门锁”的理由，也不是 `sensor health score` 的创新。它是一个关于**信息何时足以支持哪种动作**的可反驳假设。相对 R，它与现有硬件的 observables 更匹配，且研究空隙能被近期综合审计表述得更清楚。因此当前非掌纹三候选排序应为：`S`（首选）、`T`（异步时间不确定性）、`O`（normal/shift/defect 三态）；R 保留为被否定后的备用问题，而非主候选。

## 8. 与 Bob Zhang / PAMI 的关系：继承问题，不复制算法

这一方向与实验室的关联是可解释的，但不能夸大：[TIMVC-IGC](https://ojs.aaai.org/index.php/AAAI/article/view/26340) 处理离线 incomplete multi-view clustering；[FADNet](https://ojs.aaai.org/index.php/AAAI/article/view/20088) 处理相机/ISP real-noise 的 input-conditioned denoising；[OFTTA](https://arxiv.org/abs/2310.18562) 则在跨人传感器 HAR 中处理资源受限的无标签 test-time adaptation。这三条线共同说明 PAMI 长期关心“输入不完整、失真或漂移时，表示如何仍可用”。

它们**没有**提供 S 的主张：TIMVC-IGC 没有实时采集和动作；FADNet 以 reconstruction fidelity 为终点；OFTTA 没有 RGB/NIR/ToF 的物理故障、scene observability、重采或 action cost。故 S 不应把任一网络直接搬到 Pi 后称为实验室延续，而应以它们作为方法对照/设计灵感，贡献放在可复现的事件协议和被 baseline 推翻的 risk-cost 结果上。更早的团队审计与原文边界见 [`36-professor-other-directions-deep-read-log.md`](36-professor-other-directions-deep-read-log.md) 与 [`33-bob-zhang-pami-lab-audit-log.md`](33-bob-zhang-pami-lab-audit-log.md)。
