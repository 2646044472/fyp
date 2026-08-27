# Bob Zhang / PAMI 研究线与非掌纹 FYP 决策

最后更新：2026-08-27。详细发表目录和阅读边界见 [`../log/33-bob-zhang-pami-lab-audit-log.md`](../log/33-bob-zhang-pami-lab-audit-log.md)。

## 结论先行

Bob Zhang 在澳门大学 PAMI 组的工作并不是只有掌纹：它形成了四个相互连接的能力层：

1. **手部生物识别**：掌纹、掌/指静脉、指关节纹、跨光谱、移动端、模板保护和攻击。
2. **非侵入式医疗感知**：舌象、脸部、声音、视网膜、CT、病理图像和多视图缺失。
3. **稳健表示学习**：LDA、稀疏/协同表示、低秩、图学习、缺失多视图、质量和不确定性。
4. **视觉系统工程**：去噪/复原、超分辨率、异常检测、开放世界、测试时适应和 edge 资源约束。

官方 [PAMI 发表列表](https://pamigroup.github.io/publications.html) 是完整目录，[PAMI 主页](https://pamigroup.github.io/) 是研究线的官方归纳。[澳门大学主页](https://www.fst.um.edu.mo/personal/bobzhang/) 确认研究兴趣包括 biometrics、pattern recognition、image processing、medical image analysis。

## 研究线的可迁移核心

跨论文重复出现的不是某个具体网络，而是四个系统问题：

- 输入会缺失、变质或跨域：missing view、照明/设备变化、噪声、遮挡和开放环境；
- 表示要压缩、可泛化并适合资源受限设备；
- 系统要知道何时不确定、拒答或请求重采；
- 算法结果要落到真实采集、资源、隐私和安全边界。

这给 FYP 的启发是：可以把掌纹换掉，仍然研究“**传感器不完美时，edge AI 如何可靠地融合、适应和降级**”。

## 推荐方向排序（第二轮精读后解释）

| 排名 | 方向 | 为什么值得做 | 主要风险 |
| ---: | --- | --- | --- |
| 1 | **传感器故障溯源、剩余可观测性与安全降级** | 直接继承 PAMI 的 incomplete multi-view、quality-aware fusion 和 edge 系统问题；可用公开 RGB-D/多视图数据，之后再接实验室 RGB/NIR/ToF 设备。 | 2025 已有 sensor-failure benchmark、CAFuser 和 MoME；置零一个模态或再做 router 不够新，必须分离 sensor fault/healthy-but-insufficient、测动作选择、拒答/重采、恢复和能耗。 |
| 2 | **无标签测试时适应 + 安全回滚** | OFTTA、BoTTA、OD-TTA 和 ELaTTA 已覆盖 edge 适应、周期性/按需触发、Pi 资源和无梯度单实例方法；剩余问题是具体视觉传感器流中的污染监控、最坏时间窗口、冻结/回滚和恢复成本。 | 适应可能越适应越错；需要严格 streaming protocol 和事件时间戳。 |
| 3 | **任务感知的低照度/噪声复原** | 能利用 QFormer/频域/自监督去噪线，把“图像变漂亮”改成“下游任务是否更可靠且成本可接受”。 | 去噪算法竞争拥挤；若只报 PSNR，研究问题太弱。 |
| 4 | **开放世界异常检测与不确定性拒答** | ODS-SAM、evidential/prototype anomaly 线提供强方法背景；工业公开数据可避免生物隐私。 | SAM/VLM 太重；需做轻量化和可解释评估。 |
| 5 | **生物识别模型后门/投毒审计** | 团队已有 palmprint GAN poisoning 论文，安全问题明确。 | 攻击复现、数据许可和安全伦理需要老师批准；不是简单加 trigger。 |
| 6 | **舌象/声音隐私保护筛查** | 团队有 TongueNet、Voice-AttentionNet、隐私年龄估计。 | 医疗标签、伦理和临床责任使 FYP 风险高；不能宣称诊断。 |

## 首选题目（暂定）

> **面向低成本多传感器设备的缺失模态感知视觉推理与安全降级**

白话是：当 RGB、NIR、ToF 某一路掉帧、过曝、距离异常或完全不可用时，系统能否自己判断哪一路可信，选择继续推理、降级到单模态、请求重采，或者拒答；同时速度、内存、温度和能耗是否仍可接受。

最小研究问题：

> 在固定模型和阈值下，quality-aware fusion/拒答策略能否相对于始终融合和简单 fallback，降低缺失/退化输入下的 selective risk，并以可接受的 coverage、p95 latency、RAM 和 energy 工作？

建议对照：

```text
F0  始终使用完整模态
F1  模态缺失时固定 fallback
F2  质量感知加权融合
F3  质量低时拒答/请求重采，并记录代价
```

必须报告：coverage、selective risk、各缺失机制下的错误率、拒答/重采率、最坏时间窗口、p50/p95、RAM、温度、能耗和模态开启次数。若 F2/F3 没有 Pareto 改善，负结果也是结论。

## 为什么不是直接复现 Bob 的方法

`OFTTA`、`QFormer`、`ODS-SAM`、missing-view completion 都已经有论文；直接换数据或把网络移植到 Pi 不是新颖性。新颖性只能来自一个明确且可证伪的交集，例如：

- 真实 RGB/NIR/ToF 设备的相关缺失和采集质量，而不是随机置零；
- 无标签 streaming 中适应污染和回滚，而不是离线 target accuracy；
- 下游安全/识别任务与恢复质量、延迟、能耗的联合评测，而不是单一 PSNR/accuracy；
- 未见设备/照度/故障模式的留出协议和可复现实验工件。

## 选择门槛

1. **范围门：** 老师确认可以转向一般 edge vision；若必须保留生物识别，使用同一问题但以 palmprint 作为 case study。
2. **硬件门：** 确认 RGB/NIR/ToF 原始输入、控制接口、掉帧和功耗可记录；否则先用公开 RGB-D 数据，不声称真实多传感实验。
3. **数据门：** 先用许可清楚的公开数据完成 baseline 和故障脚本；不要把未获批的医疗/掌纹数据作为依赖。
4. **创新门：** 通过关键词、引用和 artifact 检索，确认主变量不是已有论文的直接重命名。
5. **停止门：** 如果质量感知策略不改善风险-成本 Pareto，停止复杂化，报告简单 fallback 的边界。
