# 研究阶段总结：从掌纹网络到失效闭环

最后更新：2026-08-27。本页是当前最短的决策摘要；证据细节见 [`05-evidence-ledger.md`](05-evidence-ledger.md)，阅读过程见 [`../log/35-research-reflection-round2-log.md`](../log/35-research-reflection-round2-log.md)、[`../log/38-research-first-candidates-log.md`](../log/38-research-first-candidates-log.md) 和 [`../log/42-sensor-state-action-audit.md`](../log/42-sensor-state-action-audit.md)。传感器故障闭环已由泛称的“demo 候选”收紧为状态分离与动作代价的 protocol 问题；当前研究优先集合以 [`16-research-first-direction-set.md`](16-research-first-direction-set.md) 为准。

## 我实际读到了什么

- 掌纹：近期深度学习综述、ROI/质量、跨设备/跨光谱、移动端、PAD、模板与隐私边界。
- Bob Zhang / PAMI：手部生物识别、缺失多视图、质量/不确定性、去噪复原、异常检测、开放世界和医疗多模态路线。
- 非掌纹近邻：缺失模态综述（354 篇）、CVPR 2025 传感器失败 benchmark、CAFuser/MoME、工业异常 EfficientAD/Real-IAD、连续 TTA 的 CMF/恢复/IST/BoTTA/OD-TTA/ELaTTA，以及 2026 CTTA survey。

证据账本目前有 113 个会改变选题、协议或边界的条目；其中约 117 个关键原始/官方资料被查看，2 篇综述做了逐段精读。这里的“查看”包括全文关键章节、官方摘要、代码 README 或数据卡；并不把摘要阅读写成完整复现。第二轮审计发现 2026-08 的 GBU-Palm 已覆盖掌纹多环境 RGB-NIR 视频 PAD 的大部分原先切口，故 P 已改为条件性系统协议；第三轮反证将复原 R 降为备用，将 S 恢复为首个非掌纹候选。

## 读完后可以排除什么

1. “树莓派 + RGB/NIR/ToF + 轻量网络”不是研究问题本身。
2. RGB/NIR fusion、quality score、missing-modality completion、condition-aware router、轻量 anomaly、TTA rollback、SAM 移植都已有直接或近直接先例。
3. 掌纹闭集 benchmark 很强，但 open-set、cross-device、攻击材料留出、采集失败和端到端资源仍存在 protocol gap；不能据此宣称行业已完全解决，也不能据此宣称我们的基本系统新颖。
4. 澳门市场价值和具体付费场景仍是待访谈问题，不由论文或个人体感自动推出。

掌纹也不是默认前提。PAMI 的公开研究线还包括 incomplete multi-view、图像复原、工业/医疗 anomaly 和计算生物学；补充精读表明，前两者和 anomaly 可以转成 edge reliability 问题，临床/Cell Painting 则受数据、算力和伦理限制。详见 [`../log/36-professor-other-directions-deep-read-log.md`](../log/36-professor-other-directions-deep-read-log.md)。

## 当前真正可防守的研究交集

> 当视觉传感器不完整、质量下降或发生分布漂移时，edge 系统能否估计可信度，并选择继续融合、固定降级、重采、适应、冻结或拒答；这些动作是否降低最终任务风险，同时满足延迟、内存、能耗和人工交互预算？

这是一个闭环，而不是一个网络名称：

```text
sensor/event log -> quality/uncertainty -> action policy -> task risk + recovery/resource cost
```

要称为研究贡献，至少需要：真实或可解释的相关故障机制、最终任务而非中间分数的收益、未见设备/环境/故障留出、Pi/CPU 实测，以及公开的故障日志和冻结协议。

## 四个候选的最终位置

| 方向 | 结论 | 启动实验 |
| --- | --- | --- |
| 掌纹 P | 保留为双轴开放世界 PAD：未见 PAIS material 与未见 capture device 下控制系统级 IAPMR。 | 冻结 matcher；按 material/device 双轴留出；主报 IAPMR budget 与 coverage。 |
| 状态-动作 S | 非掌纹首选；分离 sensor health、场景可观测性、task confidence 与 residual observability，再按风险/成本选择动作。 | 记录 raw telemetry 与 partial physical fault；按 action cost 比较 always-fuse、fallback、router 与 state-separated policy。 |
| 时序 T | 第二；将 RGB/NIR/ToF 的时间偏移 posterior 传播为 calibrated selective risk。 | 记录 LED/frame/ToF timing；留出未知 offset、运动与掉帧，比较同步与风险感知融合。 |
| 异常 O | 第三；区分正常性漂移与未知缺陷，输出 normal/recalibrate/defect 三态。 | normal-only 训练，另留正常 shift 与 defect，按 action cost 测 false alarm/false pass。 |

## 下一步不是继续堆论文

在老师选择一个方向前，先完成三个事实核验：

1. 实验室硬件能否导出原始 RGB/NIR、实际灯状态、ToF、时间戳、掉帧和功耗。
2. 一个具体低频内部工作流是否真的有“授权 claim 与到场者绑定、弱网 fallback、审计或重试成本”。
3. 被选方向是否经同任务、同输入、同评估的 direct-neighbor novelty gate 仍有空隙。

若硬件不能观测真实 telemetry 和 partial physical event，S/T 不成立；若访谈没有明确痛点，不写澳门 ROI 故事；若复杂策略不改善风险-成本 Pareto，保留简单 baseline 并报告负结果。
