# 新颖性审计：传感器故障溯源与剩余可观测性

最后更新：2026-08-27。这里的目标不是写“世界上没有人研究过”，那是无法由有限检索证明的绝对命题；目标是把候选收窄为一个**截至本轮系统检索未找到直接可比工作**的交集，并预先写下什么证据会推翻它。此方向现保留为历史的系统优先候选：用户指出它仍像 demo 后，当前研究优先集合以 [`16-research-first-direction-set.md`](16-research-first-direction-set.md) 为准。

## 候选题目

> **低成本 RGB/NIR/ToF edge 设备的传感器故障溯源、剩余可观测性与安全降级评测**

白话：当系统输出不可信时，不能只给一个低 confidence。它要区分：

1. 传感器/同步/标定是否真的坏了；
2. 传感器健康但环境或目标使当前任务不可观测；
3. 剩余模态是否足够完成这个具体任务；
4. 因此应继续、固定 fallback、重采、重新标定还是拒答。

最终任务可以是掌纹 `1:1`、物件核验或一个小型视觉质检任务；题目的贡献不依赖掌纹，掌纹只是在现有硬件可用时的 case study。

## 为什么这是比“fusion”更窄的新交集

| 已有工作 | 已解决的部分 | 仍不等于本候选 |
| --- | --- | --- |
| [CVPRW 2025 MMSS sensor-failure benchmark](https://openaccess.thecvf.com/content/CVPR2025W/TMM-OpenWorld/html/Liao_Benchmarking_Multi-modal_Semantic_Segmentation_under_Sensor_Failures_Missing_and_Noisy_CVPRW_2025_paper.html) | 整体缺失、随机缺失、噪声下的 segmentation robustness。 | 不给低成本真实采集事件、根因标签、任务可观测性、重采/拒答策略或 Pi cost。 |
| [CAFuser](https://arxiv.org/abs/2410.10791) / [MoME](https://openaccess.thecvf.com/content/CVPR2025/html/Park_Resilient_Sensor_Fusion_Under_Adverse_Sensor_Failures_via_Multi-Modal_Expert_CVPR_2025_paper.html) | condition/quality-aware fusion、router。 | 仍以改善自动驾驶最终任务为主，未区分“坏传感器”与“健康但当前看不见”，不评估小设备的 action/recovery cost。 |
| [Zhiwei](https://pmc.ncbi.nlm.nih.gov/articles/PMC13418726/) | Pi 上 reference-free 多污染物传感器自诊断、离线 fallback。 | 是环境数值传感器而非 RGB/NIR/ToF 视觉；没有视觉几何/同步、下游视觉任务或剩余可观测性评测。 |
| [GSHI camera monitor](https://arxiv.org/abs/2605.05439) | 单 RGB 相机、12 类退化、health index 和早期预警。 | 不是多模态、没有跨模态 root-cause isolation/动作闭环；为 KITTI-derived corruption 预印本。 |
| [2026 autonomous-vehicle systematic review](https://www.mdpi.com/1424-8220/26/16/5316) | 明确区分 sensor health、task confidence、residual observability；建议未来开放 benchmark 同时标注物理退化、环境状态、perception 输出和响应。 | 是对自动驾驶文献的综合与议程，不是 RGB/NIR/ToF/Pi 实证；它支持问题重要性，不自动证明本项目首创。 |
| [Sensing the Action VLA perspective](https://www.mdpi.com/1424-8220/26/11/3541) / [2017 multimodal sensor policy](https://arxiv.org/abs/1705.10422) | 已讨论 RGB-D 反射/同步/缺失、可靠性加权、sensor-to-action latency，以及仿真中 sensor dropout 后的 policy switching。 | 不是低成本 RGB/NIR/ToF 真实采集、故障根因/健康但不可观测区分，也没有本项目的 Pi 风险-恢复协议。 |

因此可防守的最小主张是：**本轮检索未找到将这四层同时固定的直接工作：低成本 RGB/NIR/ToF 真实事件日志、根因/环境/任务可观测性分离、动作策略、edge 风险和恢复成本。** 这不是“故障切换”或“多模态闭环”的首创声明，而是一个设备/标签/协议范围声明。

## 最小可证伪协议

### 状态标签

每个短采集 episode 都记录并标注：

```text
hardware/timing state -> environmental/target state -> per-modality health
                         -> task confidence -> residual observability -> action -> outcome/cost
```

至少包含：RGB 过曝/低照、NIR LED 或相机掉帧、ToF 无回波/高方差、跨模态时间错位、遮挡/目标距离异常，以及“传感器正常但任务仍不可观测”的 hard-negative。

### 对照与结果

- `B0`：永远融合；`B1`：固定 RGB fallback；`B2`：quality/router；`B3`：溯源 + action policy。
- 报根因分类的 macro-F1、误报警率、检测延迟、accepted-task risk、coverage、重采成功率、恢复时间、p50/p95、RAM、温度、能耗。
- 主要终点不是 B3 的 accuracy，而是它是否在相同 coverage 或相同延迟/能耗预算下减少高风险接受；若没有，结论是 root-cause 层不值得其复杂度。

## 新颖性推翻条件

以下任一项成立，即不能再称该交集新颖，应降为复现/扩展：

1. 找到公开工作同时具有 RGB/NIR/ToF 或等价低成本视觉传感、真实或物理测得故障事件、root-cause label、task confidence/residual observability 和 action-cost evaluation。
2. 实验室硬件不能可靠记录 actual illumination、frame id/timestamp、ToF 状态和功耗；此时不能作“故障溯源”主张，只能模拟 corruption。
3. B3 不优于 B1/B2 的 risk-cost Pareto；此时研究结论应是简单 fallback 足够。

## 目前的优先级

这成为第一候选，而不是原先泛称的“missing modality fusion”。第二候选仍是开放世界工业异常 + calibrated abstention；掌纹改为可选 case study。它比“没有人做过掌纹 edge”更可检验，也更接近 PAMI 的 incomplete multi-view、quality/uncertainty 和 edge reliability 交集。
