# 其他 Edge Sensing 方向：故事、创新与淘汰审计

日期：2026-08-27。本页只保留把 edge 约束变成研究问题的候选。所有候选都按“真实故事、与直接近邻的差异、可证伪指标、硬件 Gate”审计；不是“可以在 Pi 跑”的功能清单。

## 1. 已淘汰的宽泛方向

| 宽泛想法 | 直接近邻 | 淘汰原因 |
| --- | --- | --- |
| 不确定时开启第二模态 | sequential cost-sensitive acquisition、A2MT、FusionSense | acquisition policy、RL、cost-accuracy trade-off 已是成熟问题 |
| 低功耗 sensor 唤醒 RGB | NeuroViG、energy-proportional IoT node、event-triggered sensing | wake-up/duty cycling 已有真实 edge 系统 |
| quality-aware fusion/router | MoME、CAFuser、EAU | 输入已采集时的质量加权/专家选择已有强近邻 |
| 为 edge 量化一个 fusion model | Q-TempFusion 等 | 量化/硬件 profiling 不是新的 sensing 问题 |
| 传感器故障后 fallback | active fault diagnosis、MAMMOTH | 故障诊断、缺模态 action policy 已有长期和近期先例 |

## 2. 仍值得验证的两个主方向与一个条件性事件

### E1：风险审计式 cascade sensing

**故事。** 常开节点必须节省电力、热、存储和连续视频的隐私成本，于是低功耗 sentinel 决定是否启动 RGB/NIR verifier。最危险的错误不是 verifier 看错，而是 sentinel 漏掉后 verifier 从未看见事件。

**待验证创新。** 把 trigger 视为 observation policy；对 no-wake population 以已知 inclusion probability 做少量 audit，以估计/控制完整 episode 的 missed-event risk。不是发明 trigger、RL 或更好的 router。

**研究价值。** 给“不开相机”这一产品选择一个可审计的风险度量，直接连接 safety、edge energy 与统计选择偏差。

**验证/推翻。** 外部 ground truth 覆盖所有 episode；比较 always-on、fixed/adaptive trigger、uniform audit 与 telemetry-stratified audit。若简单 trigger 或 uniform audit 的 risk-energy Pareto 同样好，或 audit 令 always-on 更划算，即失败。

### E2：wake-induced temporal evidence validity（条件性事件，不单独立题）

**故事。** 昂贵传感器不是瞬时可用：power-on、auto-exposure、LED settling、first-valid-frame 都会滞后。移动中的手/物体可能使 RGB 触发时的状态和 NIR/ToF verifier 实际看到的状态不同，系统却错误把两者视为“第二份证据”。

**边界。** acquisition action 自身确实可能造成 evidence-time mismatch，系统可选择 `wake / wait / re-acquire / abstain` 并按实际 readiness/exposure timestamp 限制自动决策。然而 asynchronous fusion、latency compensation 和 Age-of-Information 已有广泛近邻，不能把 timestamp-aware fusion 或 freshness scheduling 本身称为创新。

**保留条件。** 只有实际 wake/readiness/LED delay 可测，且它在移动 target 上造成 action-level false permit，并且 validity gate 优于 async-fusion/freshness baseline，才将其作为 E1/E3 的压力事件；否则不单独立题。

**验证/推翻。** 以滑轨/摆动目标控制运动，记录 trigger command、first-valid frame、exposure、LED/ToF timing；比较 always-on sync、naive wake fusion、timestamp-aware validity gate。若 wake latency 远小于状态变化时间，或 naive fusion 无风险损失，题目失败。

### E3：共因退化下的独立证据 acquisition

**故事。** 强光、反光材质、遮挡、距离、共享时钟/供电会同时影响 RGB/NIR/ToF；多个 sensor 的同意可能是虚假一致。系统不应只因多一路高 confidence 就自动放行。

**待验证创新。** 在 shared-cause strata 内检验第二模态是否真正降低 held-out task risk；若没有独立增益，controller 选择主动 probe、re-acquire 或 abstain。不是普通 correlation-aware fusion、uncertainty weighting 或 modality dropout。

**研究价值。** 对多模态安全论证中的“冗余是否真的独立”给出物理、可复现实证；可迁移到工业、机器人和生物核验。

**验证/推翻。** 物理记录 glare、reflectivity、distance、motion、occlusion、ToF no-return 等 cause；按 cause family 留出，主报 false-consensus lift、accepted-task risk、coverage 和 cost。若 quality-aware router 已给出相同 Pareto，或没有真实共因事件，题目失败。

## 3. 现阶段排序

| 候选 | 研究价值 | 新颖性风险 | FYP 可行性 | 硬件 Gate |
| --- | --- | --- | --- | --- |
| E1 风险审计 cascade | 高 | 中 | 中高 | 真正关/开 verifier、测增量能耗、全体 ground truth |
| E2 时序证据有效性 | 中 | 高 | 低 | actual readiness/LED/exposure timestamp、受控运动；只作 E1/E3 事件 |
| E3 共因独立证据 | 很高 | 高 | 中低 | 真实相关退化、独立模态、足够 episode |

E1 是第一个应该做的，因为它有最清楚的 edge 因果链和否证条件；E2 是 E1/E3 的硬件压力事件，不再单列为主方向；E3 应作为高风险的第二阶段，不能在没有真实共因采集前承诺。
