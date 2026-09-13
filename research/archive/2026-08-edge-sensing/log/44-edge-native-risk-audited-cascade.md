# Edge 强约束候选：风险审计式分级感知

日期：2026-08-27。本页专门问一个更严格的问题：是否存在一个问题，**不把 edge 当作部署结尾，而是 edge 的能量、算力、持续运行与本地数据约束本身使研究问题出现**？

结论：`risk-audited cascade sensing` 是目前最值得做可行性审计的候选。它尚未通过完整 novelty gate，不能写成“无人研究”；但比掌纹、普通 multi-modal fusion、普通 edge profiling 更有明确的 edge 因果链。

## 1. 题目与核心问题

> **风险审计式分级感知：在严格 sensing/compute budget 下，如何量化并控制低功耗触发器漏掉的安全事件？**

许多 edge 系统不会一直让相机和视觉模型全速运行：一个低功耗 sentinel（例如 ToF / PIR / very-low-rate distance reading）常开，只有它判断“可能有事件”时才唤醒 RGB/NIR 和较重的模型。这是合理的产品架构，但它产生一个通常被 accuracy/FPS 表掩盖的问题：

```text
low-power sentinel says "no event"
    -> high-fidelity camera/model never runs
    -> system has no normal operating log to证明这次真的没有危险
    -> missed events are censored by the trigger itself
```

也就是说，触发器决定了哪些样本进入第二级模型与训练/维护日志。这不是普通 class imbalance，而是 action-dependent / missing-not-at-random observation。只在“已唤醒”的帧上测 camera accuracy，无法估计系统真正的 missed-danger risk。

## 1.1 先答三问：故事、创新、baseline

### 故事：为什么这个系统必须是 edge

考虑一个无云、低成本、常开但不宜持续录像的近距离安全监测节点，例如实验室工位、轻型自动设备或机柜防夹区域。它需要在毫秒到秒级作出 `wake-and-verify / stop / clear` 决定；持续运行 RGB/NIR + model 会带来能耗、热、存储和隐私成本，购买 LiDAR/工业安全相机又会改变成本级别。于是系统采用 cheap sentinel + expensive verifier 的级联。

真正的风险不是第二级模型把已经看到的画面分类错，而是第一级漏掉事件、导致第二级从未观察到该事件。设备会以“没有发生任何事”的状态继续运行。这是为什么不能把本项目说成普通门禁或普通 motion-trigger demo；它研究的是**为了在 edge 预算内省下观察，系统是否还能知道自己漏掉了什么**。

原型只能是 safety-assist / simulated stop，不可宣称取代经认证的机械安全联锁。经济价值也不是“卖一个 Pi”，而是为已有低风险设备提供一直开机但不一直看/不一直存的本地附加监测层；真实购买意愿和法规仍须访谈/核对。

### 创新：边界在哪里

已有 work 已覆盖 low-power trigger、adaptive trigger threshold、selective high-cost inference、事件相机与 generic active sensing。因此这些都不是贡献。

本题唯一可能成立的创新假设是：**trigger policy 同时造成 observation policy**。若只在 trigger 后运行 verifier，`no-wake` population 的事件率不可见，因而普通 triggered-subset accuracy 不能支撑 safety claim。用具有已知 inclusion probability 的稀疏审计 capture，并按该概率校正估计，是否能在固定预算下更准确估计和降低 `no-wake` missed-risk？

这需要在以下四个要素的交集上成立：

1. low-power trigger 真正控制 high-fidelity observation；
2. no-wake safety event 是主风险，而非普通 false alarm；
3. audit sampling 为未观察总体提供可计算的风险估计，而非只收集更多 hard examples；
4. 在 Pi 级连续运行条件下，报告 risk 与 energy/latency 的 Pareto，而非离线 accuracy。

截至本轮检索没有找到同时具备四项的 direct neighbor；但这只是待复核的 gap，不可宣称“首次”。若引用链找到它，或审计只提高模型 accuracy 而不能改善 no-wake risk estimate，创新主张即失败。

### Baseline：什么结果会让我们输

| baseline | 它代表什么 | 若它赢，意味着什么 |
| --- | --- | --- |
| `B0` always-on RGB/NIR verifier | 用能耗换完整观测；安全/观测上界。 | 若同预算或实际成本可接受，cascade 没必要。 |
| `B1` fixed sentinel threshold | 最自然、最便宜的工程方案。 | 若它在相同 energy/latency 下达到相同 full-population missed-risk，审计无价值。 |
| `B2` adaptive threshold trigger | 现有 event-trigger / SHM 思路。 | 若仅调 threshold 已覆盖盲区，不能声称 observation-bias 贡献。 |
| `B3` random periodic wake | 简单地给 no-wake population 抽样。 | 若 uniform audit 在相同预算下已同样准确/安全，复杂 telemetry stratification 不值得。 |
| `B4` hard-example replay / self-training | 常见在线维护路径。 | 若它不做概率校正却同样估准 no-wake risk，选择偏差论点要重新审计。 |

主结果不是“B4 accuracy 更高”，而是：在预冻结的 wake/energy/latency budget 下，B4 对完整 episode population 的 `missed intrusion` 更低，或对 `P(intrusion | no-wake)` 的风险估计更准，且不把收益换成几乎 always-on 的 camera duty cycle。反例必须如实保留。

## 2. 推荐任务

以近距离 safety envelope 为最小任务，但不必连接真实危险机器：

- 状态：受保护区域 `clear` 或 `intrusion`；
- 动作：`sleep / wake-and-verify / stop / uncertain`；
- sentinel：低速 ToF 或距离阈值；
- verifier：RGB/NIR 的轻量 intrusion/hand/object detector；
- ground truth：滑轨、固定距离板、外部相机或预定义轨迹，仅用于实验标注；
- 真实安全动作：原型只亮灯/模拟 stop，不宣称 safety-certified interlock。

这可以先形成非常简单的 demo：ToF 有风险时唤醒 camera，camera 确认后 stop。研究版要回答的不是“能否唤醒”，而是**没有唤醒时是否仍可能漏掉危险，以及用多少额外预算才能知道这一点**。

## 3. 可能的研究机制

### 固定触发器的问题

`distance < threshold -> wake` 假设 ToF 对所有材质、角度、光照、运动都足以覆盖危险。黑色/透明/反光物体、边缘角度、快速掠过或 no-return 会让这个假设失效；最严重的 false negative 不会送到第二级，因此也不会在普通 online log 中被发现。

### 风险审计式 cascade

系统预留一个很小且可量化的 audit budget：即使 sentinel 没触发，也以受控概率唤醒 verifier，或在可疑 telemetry strata（near threshold、ToF variance/no-return、温度/照明变化）增加审计概率。

审计样本不是为了提高高层模型的平均准确率，而是为了估计：

`P(intrusion | sentinel did not wake, device/context stratum)`

以该估计决定是否提高 sentinel 灵敏度、扩大 wake region、临时输出 `uncertain`，或维持当前 budget。随机审计至少给未唤醒的时段一个已知的观察概率；若加入 context-aware sampling，评估时必须以 propensity / inclusion probability 校正，不能只报告被选中的样本。

一个最小控制器可以是轻量 lookup table、logistic model 或 calibrated risk bound；不需要 RL、VLM 或大融合网络。

## 4. Edge 为什么是不可替代的条件

| 约束 | 如何改变研究问题 |
| --- | --- |
| sensing/compute/energy budget | 不能 always-on RGB/NIR + heavy inference，必须在“安全覆盖”与“唤醒成本”之间分配有限预算。 |
| local latency | 云端无法作为安全事件的实时 verifier；wake-to-stop delay 是主终点之一。 |
| limited storage/privacy | 不应默认保存全量影像来离线找漏检；审计策略决定本地保留何种最小证据。 |
| sustained runtime | 触发频率、模型时间和温度/功耗会改变可用预算，必须报告连续运行而非 cold-start FPS。 |

如果最终设备是一台始终满功耗运行的 Pi、RGB/NIR 从不真正关闭、也不测增量能耗/compute budget，本题的 edge 主张会变弱。这是硬件 Gate 0，不可回避。

## 5. 与已有工作的边界

| 已有工作 | 已覆盖内容 | 因此不能主张 |
| --- | --- | --- |
| [event-triggered sensing in SHM](https://www.sciencedirect.com/science/article/pii/S0888327025012385) | low-power sentinel 唤醒 high-fidelity sensor，并动态调整 threshold 以减少 false trigger/miss。 | 不能把 hierarchical wake-up、adaptive threshold 或 energy-efficient sensing 当创新。 |
| 现有 PIR/GPIO wake camera 产品与 always-on vision hardware | deep sleep、motion/IO trigger、wake sequence 是成熟工程。 | 不能做“距离传感器唤醒相机”的产品 demo 后称研究。 |
| [risk-adaptive edge-cloud vision](https://arxiv.org/abs/2608.14991) | 以风险触发更强模型/云 reasoning。 | 不能把 selective higher-cost inference 本身当创新。 |
| active sensing / acquisition 文献 | budgeted modality choice、information gain 与 scheduling 已是成熟问题。 | 不能以任意 acquisition policy、RL scheduler 或某个 trigger rule 自称首创。 |

截至本轮检索，**未找到**同时以低功耗 trigger 导致的选择性不可观测性为中心、用带已知 inclusion probability 的稀疏 audit 来估计 `no-wake` safety risk、并在真实 Pi 级 camera/ToF safety task 上报告 risk-energy-latency 的直接邻居。该句只是范围限定的检索观察，后续必须以 citation chain、ACM/IEEE/Google Scholar 检索和具体应用关键词再核对。

## 6. 可证伪实验

### 条件

按 distance、material、angle、illumination、motion 和 ToF status 创建 episode；训练/开发/测试须按 material/environment family 留出，而不是随机分帧。

### 比较

1. `B0` always-on verifier：安全表现上界、资源成本上界；
2. `B1` fixed threshold trigger：现实产品 baseline；
3. `B2` adaptive trigger：已有 SHM 类方法；
4. `B3` uniform periodic audit + trigger；
5. `B4` proposed telemetry-stratified, propensity-corrected audit + risk controller。

### 终点

- 系统级 missed intrusion / false permit（包括没有 wake 的事件）；
- 估计的 no-wake risk 与外部完整 ground truth 的误差；
- audit 后发现的 trigger blind-spot time；
- joules per hour、joules per detected intrusion、wake-to-stop p95、duty cycle、RAM、temperature；
- camera 不应只测 triggered subset；必须报告完整 episode population。

### 推翻条件

1. B1/B2 在同等 budget 下已经达到同一 missed-risk，审计没有价值；
2. audit sampling 的能耗/延迟使 B0 更划算；
3. 无法实现或测得 verifier 的实际关闭/唤醒/增量 compute，则只可研究 compute duty cycle，不可声称 low-power system；
4. 找到同一 observation-bias + audit-risk + edge safety 交集的直接工作。

## 7. 当前相对排序

| 候选 | 研究风险 | FYP 可做性 | Edge 是否为问题根源 |
| --- | --- | --- | --- |
| P：掌纹 PAD | 新颖性低 | 中 | 弱 |
| S-H：共因虚假一致 | 高 | 低 | 中强 |
| T：异步 fusion | 新颖性低 | 低 | 中 |
| O：normal/shift/defect | 新颖性低 | 高 | 弱 |
| **E：风险审计式分级感知** | 中高 | **中高** | **强** |

E 的价值在于它把 edge 的资源约束转成可测、可反驳的统计问题：为了省下相机/模型运行，系统放弃观察了哪些事件？用多小的审计预算，才能发现这个盲区并把安全风险控制在目标范围内？
