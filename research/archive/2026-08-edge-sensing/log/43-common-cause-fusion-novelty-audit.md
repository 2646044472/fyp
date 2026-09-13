# 共因退化、虚假一致与多模态安全：第四轮新颖性审计

日期：2026-08-27。此日志回应一个更高的标准：不是寻找一个能做的 edge demo，而是寻找一个有实际安全意义、且尽量未被同类工作直接覆盖的研究问题。结论首先写在前面：**不能把“相关性感知融合”“缺模态校准”或“主动根因诊断”再称为创新。**它们已有直接邻居。唯一仍值得深入审计的交集，是低成本异质视觉传感器在**部分、物理、共因退化**下产生的“虚假一致”与高置信自动接受。

这里的“未找到 direct neighbor”只表示截至本轮检索日，没有发现同时满足相同传感器级别、部分真实物理退化、共因机制、独立证据量化和 action-level risk 的公开论文；它不是全球不存在证明。

## 1. 问题为什么重要

多传感器不等于多个独立证人。强光、距离、反射材质、姿态、污染、共同电源/时钟或共同 ISP 设置，都可能令 RGB、NIR 和 ToF 同时失去辨识能力；此时“两个流都同意”反而会让朴素融合产生更高置信度。

[UL 4600 的 sensing guidance](https://users.ece.cmu.edu/~koopman/pubs/191002_UL4600_draft.pdf) 明确把 correlated/common-cause degradation 列为多传感器安全论证的陷阱，并要求分析 sensor degradation 的类型和幅度。近期的[系统综述](https://www.mdpi.com/1424-8220/26/16/5316)也要求未来 benchmark 将物理退化、环境状态、感知输出和 operational response 同步记录。这说明问题不是“多做一组噪声测试”，而是可信冗余是否真的存在的问题。

## 2. 已有工作已经覆盖什么

| 已有方向 | 直接证据 | 对本题的影响 |
| --- | --- | --- |
| 相关/依赖 sensor fusion | [distributed fusion under unknown correlation](https://pmc.ncbi.nlm.nih.gov/articles/PMC5713506/) 与大量 covariance/evidence-fusion 文献已讨论相关观测和 double counting。 | 不能把“考虑 correlation”当算法创新。 |
| 相关性放入学习式 fusion | 近期 [ACIFNet](https://www.mdpi.com/2077-1312/14/13/1252) 在定位中加入 cross-correlation/common disturbance；[ModTrack](https://arxiv.org/abs/2603.15812) 显式分解 shared common-mode covariance。 | 不能只提出一个 correlation-aware weight 或 covariance head。 |
| 模态缺失下的不确定性/coverage | [MCCF](https://arxiv.org/abs/2608.07183) 以 modality-presence mask 做 group-conditional conformal coverage；另一近期医疗预印本也以相同思路处理整路缺失。 | 不能以“缺一路也校准”或 Mondrian CP 自称新。它们处理 presence mask，不是 partial physical common cause。 |
| 主动诊断、反事实测试 | Murphy 的 sensing-failure recovery 早已用主动测试排除故障原因；[counterfactual robot perception diagnosis](https://arxiv.org/abs/2509.18460) 已将 active/passive FDI 与干预式测试直接用于 robot perception。 | 不把 causality、主动 probe 或 root-cause diagnosis 单独作为贡献。 |
| degradation benchmark | [M3DGR](https://arxiv.org/abs/2507.08364) 已为 RGB-D/LiDAR/GNSS/IMU SLAM 加入可控退化；多传感器 robustness benchmark 也早已存在。 | 不能仅以“我们也有 degradation dataset”自称新。 |

## 3. 还可能成立的窄问题

### 暂定题目

> **虚假一致风险：低成本多模态 edge 视觉在部分共因退化下，何时拥有独立佐证，何时必须拒绝自动动作？**

### 推荐的具体承载任务：安全边界（safety envelope）放行

不要再把“掌纹/门锁”当作问题本体。把现有 Pi + RGB/NIR + 距离模块改造成一个**近距离危险区域监测器**：它只回答一个有动作后果的问题，`permit / stop / uncertain`。

- `permit`：受保护区域内没有人手、工具或其他目标，或目标离危险平面仍有足够安全距离；
- `stop`：检测到侵入或安全距离不足；
- `uncertain`：现有证据不足以安全放行，要求重采、减速或人工确认。

实验时不连接真实危险机器，只用小型滑轨、光幕/外部参考或预定义物体轨迹产生 ground truth。第一版 demo 可以是“手或物体进入桌面安全区即停止”；研究版的任务是：在不同距离、运动、照明、反光/吸光材质、局部遮挡、NIR illumination drift、ToF no-return 等**真实物理事件**下，是否仍会错误给出 `permit`。

它比 generic object detection 更适合做研究，因为任务风险是可定义的：**false permit**（区域实际不安全却放行）通常比 false stop 更严重，可以在协议中预先规定其预算。RGB 提供轮廓和语义、NIR 提供低光可见性、ToF 提供几何距离；它们有互补性，也有机会被同一个物理原因同时误导。这个“互补与共因同时存在”的张力正是研究对象。

经济/应用叙事可以是“给实验室工位、教学设备、小型协作机器人或既有机柜作低成本本地 safety retrofit”，但在访谈目标用户、核对法规和责任边界以前，不能声称某行业一定会购买，也不能把 demo 接到真实安全联锁上。

### 可证伪假设

在三路设备中，若第二模态对任务输出的额外信息在给定可测 shared-cause state（例如距离、照明、运动、反射/遮挡、温度和时序状态）后消失，则它不应获得“独立佐证”带来的风险下降。一个 controller 若在这种情形撤回自动 accept，而不是仅根据多模态 confidence 加权，能否在**留出的共因事件族**上降低 accepted-task error / false pass，并保持指定 coverage、latency、energy 与人工复核预算？

这个命题刻意不承诺在任意未知分布上有理论保证。conformal 的有限样本保证要求定义清楚的 exchangeable calibration/test group；对未见共因机制，最多能报告 held-out-cause transfer，不能声称 distribution-free safety guarantee。

### 贡献必须同时具备的四件事

1. **物理因果设计，而不是独立随机噪声。**每个 event 至少记录一个共享物理因素及其强度，并分别记录每路 sensor 的原始健康/quality 指标。
2. **独立佐证的可操作定义。**不能把 attention、Shapley 或 feature correlation 直接叫作 evidence independence；必须事先冻结一个可检验判据，例如在 shared-cause strata 内，额外模态是否显著降低 out-of-sample task loss / error risk。
3. **虚假一致终点。**主指标不只是 accuracy/ECE，而是 `false-consensus lift`：在各流预测一致且 fusion 高置信的样本中，实际错误率相对 clean 或 marginal-calibrated reference 增加多少；另报 accepted-task risk、coverage 和每类拒绝的成本。
4. **外推边界。**训练、验证与测试必须按 common-cause family 留出，例如只在训练见过 glare/distance，测试另一个未见的 reflection-plus-motion 或 timing-plus-illumination 组合。若只随机分帧，不能论证共因泛化。

### 基线与反例

- `B0` 单 RGB / 单 NIR / 单 ToF。
- `B1` ordinary late/feature fusion。
- `B2` per-modality quality-aware router。
- `B3` modality-presence calibration（MCCF 类），用于表明“整路缺失的校准”不能解决 partial shared failure。
- `B4` correlation-aware fusion / covariance baseline。
- `B5` proposed independent-evidence gate + abstain/reacquire action。

主张只有在 B5 在冻结 protocol 下减少 `false-consensus lift` 和 accepted risk，且不是以几乎零 coverage 换来的，才成立。若 B2 或 B4 已达到同一 risk-cost Pareto，结论应是该窄机制不需要。

## 4. 这仍不是确定方向的原因

它的研究意义高于普通“fusion accuracy”：它针对 safety case 中最危险的冗余错觉，也能迁移到机器人、工业检测和近距离生物核验。但创新风险仍高：

- 现有相关性 fusion、evidence theory、conditional calibration 和 FDI 文献很宽，后续引用链可能发现更直接的工作；
- 若实验室只能做整路关闭或数字噪声，问题立即退化为已有 missing-modality/robustness benchmark；
- 三路设备未必有真正互补的信息。若 RGB/NIR 来自高度耦合的同一成像链，结论可能是硬件设计问题，而非可学的 controller；
- 要声称“独立佐证”，必须有足够多的 per-cause episode。小样本下只能做 pilot，不能做可靠风险论断。

因此它现在应标为 **H（high-significance, high-risk）候选**，而不是给老师承诺的最终 FYP。下一步 novelty gate 必须检索 `common-mode/common-cause + selective prediction/abstention + multimodal perception` 的引用链，并先检查硬件能否获取 shared-cause telemetry。

## 5. 对原 S/T/O 的更新

| 候选 | 当前判断 |
| --- | --- |
| S：状态分离 + 动作 | 有意义，但其主动诊断部分已有直接工作；保留作 protocol 父问题。 |
| S-H：虚假一致 / 共因退化 | 这是 S 内唯一具有较强研究问题感的窄版本；尚未通过 novelty gate。 |
| T：时间不确定性 | 异步对齐、uncertainty 与 risk coverage 的组合已有强近邻；只可作为 S-H 的一个共因事件，不单独立项。 |
| O：normal/shift/defect | 三态和 shift-aware anomaly 已有近邻；不作为首选。 |

## 6. 当前结论

若要求“研究意义大且尽量新”，我不会继续推荐原本宽泛的 S/T/O。唯一值得投入下一轮深读的是 **S-H：部分共因退化下的虚假一致风险**。它不是“做一个多传感器 demo”，而是检验一个能被推翻的安全命题：多一路传感器是否真的降低了可接受风险，还是只重复了同一个物理盲点。
