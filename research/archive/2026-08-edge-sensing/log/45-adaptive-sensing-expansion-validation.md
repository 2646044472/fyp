# Adaptive Sensing：问题发散与验证结果

日期：2026-08-27。本页把“先 RGB，必要时再开 NIR/thermal”拆成可检验的研究问题，并用近期 primary work 做第一轮 direct-neighbor 排除。结论不是 Adaptive Sensing 已经新颖，而是普通 acquisition policy 已有强先例；目前只保留一个风险/观测协议候选。

## 1. 问题空间

| 候选 | 核心问题 | 研究终点 | 当前判断 |
| --- | --- | --- | --- |
| A1：不确定性驱动 modality acquisition | uncertainty 高时是否值得开启第二模态？ | accuracy、cost、latency | 已有 active sensing、selective inference、dynamic fusion；不能单独立题 |
| A2：任务驱动 keep/drop | 哪一路输入对当前 task 真的必要？ | task quality vs data/compute reduction | FusionSense、DynaFuse 等已有直接近邻 |
| A3：质量/故障驱动 fallback | 传感器坏了还是场景不可观测？应融合、重采还是拒答？ | accepted-task risk、recovery、资源 | repo 的 S；可做性取决于真实 telemetry 和 partial fault |
| A4：共因退化下的虚假一致 | 多个 sensor 同意是否只是同一个物理盲点？ | false-consensus lift、false permit | 研究意义高，但硬件/数据风险高 |
| A5：trigger-induced observation bias | sentinel 不唤醒时系统如何知道自己漏了事件？ | full-population no-wake risk、audit efficiency | 当前最值得继续验证的 edge-native 候选 |

这里的关键分界是：A1/A2 在问“如何少采一些仍保持任务质量”；A5 在问“少采以后，未被观察的总体风险是否仍可估计和控制”。后者不是普通 class imbalance，因为 observation 本身由系统动作决定。

## 2. 第一轮文献验证

已核对的 direct/near neighbors：

1. **FusionSense (2026)**：在 RGB+Depth/LiDAR edge 系统中，以 fused task 学习 near-sensor keep/drop 决策，明确优化数据减少、计算和能耗。因此“按任务动态启用模态”不能作为贡献。
2. **Energy-Proportional Vision IoT Node (2026)**：用 always-on event imager 触发高功耗 RGB，展示 wake-on-motion、低功耗持续运行和 sense-to-report 成本。因此“sentinel 唤醒相机”是已有系统模式。
3. **Energy-Efficient Adaptive 3D Sensing (CVPR 2023)**：按 ROI 和深度需求自适应投光，联合优化 range、power 和 eye-safety。因此“只在需要时取得昂贵深度证据”已有硬件/算法先例。
4. **MoME (CVPR 2025)**：在 sensor failure 下按 feature quality 选择 camera、LiDAR 或 fusion expert。因此 quality-aware routing、失效下选择模态不能单独主张新颖。
5. **Active sensing / POMDP / selective prediction**：长期已有 resource-constrained sensor selection、主动观测和 reject option；RL、uncertainty threshold 或 cost-sensitive reward 不是空白。

这些工作没有同时验证：低功耗触发器造成的选择性不可观测、no-wake 安全风险、带已知 inclusion probability 的稀疏 audit，以及 Pi 级端到端 risk-energy-latency。这个交集仍是范围限定的待验证假设，不是首创声明。

## 3. 收敛后的研究问题

> 在固定 sensing/compute/energy budget 下，低功耗 sentinel 控制昂贵 verifier 的开启；若 sentinel 未触发，系统如何用很小的审计采样估计并控制 `P(event | no-wake, context)`，而不是只在 triggered subset 上报告准确率？

建议题目：

> **Risk-audited adaptive sensing for edge vision under trigger-induced selective observation**

最小系统：ToF/PIR sentinel 常开，RGB/NIR detector 只在 sentinel 触发时运行；一小部分 no-wake episode 以预先冻结的概率 audit。控制器可先是 lookup table 或 logistic risk bound，不需要 RL。

## 4. 最小验证协议

### 4.1 数据与事件

- 每个 episode 都由外部参考产生完整 ground truth，不能只保存 wake 后影像；
- 条件按 distance、material、angle、illumination、motion、ToF status 分层；
- 训练/验证/测试按 material 或 environment family 留出；
- 记录 sentinel output、wake decision、audit probability、RGB/NIR readiness、frame/timestamp、energy 和 temperature；
- 必须包含 sentinel 盲区：黑色/透明/反光物体、no-return、快速掠过和边缘角度。

### 4.2 Baseline

`B0` always-on RGB/NIR verifier；`B1` fixed threshold sentinel；`B2` adaptive threshold；`B3` uniform periodic audit；`B4` telemetry-stratified audit + propensity/inclusion-probability correction。

### 4.3 主指标

- 完整 episode population 的 missed event / false permit，而非 triggered subset accuracy；
- `P(event | no-wake)` 的估计误差和置信区间覆盖；
- audit 发现的 blind-spot time；
- joules/hour、joules/event、camera duty cycle、wake-to-stop p95、RAM、temperature；
- coverage、人工 retry 和 false stop 作为可用性约束。

## 5. 会推翻题目的结果

1. `B1`/`B2` 在相同 energy、latency、coverage 下达到相同 no-wake risk；
2. uniform audit 与 telemetry-stratified audit 没有显著差异；
3. audit 成本使 always-on `B0` 更划算；
4. 无法真正关闭/唤醒相机或测增量能耗，只能声称 duty-cycle 优化；
5. 外部 ground truth 不完整，无法知道 no-wake 时是否漏事件；
6. citation chain 找到同样的 observation-bias + audit-risk + edge safety 交集。

## 6. 对掌纹版本的限制

Palm 可以是 verifier task：RGB 先做 ROI/quality，低质量时启动 NIR，再选择 accept、reacquire 或 abstain。但 palm 版本会增加 identity/session、PAD、攻击材料、matcher threshold 和伦理负担；若没有双轴留出和系统级 IAPMR，就只能是 adaptive capture demo，不能声称 biometric security contribution。

当前建议先用可完全标注的近距离 intrusion/safety-envelope task 做方法验证，再把相同 sensing policy 迁移到掌纹作为 case study。
