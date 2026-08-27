# 新颖性检索日志：不是证明无人研究，而是排除直接近邻

日期：2026-08-27。关键词检索覆盖 `active sensing / sensor failure / edge vision / abstention / reacquisition`、`quality-aware acquisition`、`sensor self-diagnosis / RGB-D / multimodal perception`、`sensor health / task confidence / biometrics`，并回看缺失模态、自动驾驶融合、on-device TTA、掌纹和 PAMI 代表论文。

## 检索结果如何改变题目

### 已有且必须承认

- 医疗成像和人脸已有 image quality -> recapture/reject；因此“quality score 后重采”不是创新。
- CVPRW 2025 的 missing/noisy modality benchmark、CAFuser 和 MoME 已覆盖模态失效/quality router；因此“检测缺失后调整 fusion”不是创新。
- Zhiwei（Sensors 2026）已在 Raspberry Pi 5 上实现 reference-free 多传感器自诊断和 offline fallback；因此“Pi 自诊断/离线 rule engine”不是创新。
- GSHI/DRIVE-C 方向已做单相机 health score、synthetic corruption 和 early warning；因此“一个 camera health index”不是创新。

### 没有找到的直接交集

未找到一篇同时具备以下全部要素的公开原始工作：

1. Pi 级 RGB/NIR/ToF 或同等低成本小型视觉采集；
2. 可核验的 physical/timing fault event，而非仅 image corruption 或随机 mask；
3. 将 **sensor health**、**environment/target limitation**、**task confidence**、**residual observability** 分开标注或评估；
4. 用继续/fallback/reacquire/recalibrate/abstain 等动作改变最终风险，并报告 recovery/energy/latency。

### 新增近邻：不能忽略“已有动作闭环”

检索又找到 [Sensing the Action](https://www.mdpi.com/1424-8220/26/11/3541)（2026）：该综述已经从 sensor-to-action 角度讨论 RGB-D 反射、同步、缺失、可靠性加权、延迟和安全评测；更早的 [Liu et al. 2017](https://arxiv.org/abs/1705.10422) 已在 TORCS 仿真里用 sensor dropout 和 policy switching 处理部分故障。它们排除了“传感器坏了就切换策略”这种泛泛表述。

但两者都没有同时提供：低成本 RGB/NIR/ToF 真实采集事件、物理/同步故障的可核验根因、健康但任务不可观测的 hard-negative、Pi 端风险与恢复成本。因此候选题目必须使用这些限定词；否则应降级为已有 sensor-failure policy 的应用复现。

这不是“没有任何相关研究”的证明。它只是截至 2026-08-27、按上述关键词和直接近邻论文反向检查得到的范围限定结论。

## 关键反证与为何仍保留

[2026 autonomous-vehicle systematic review](https://www.mdpi.com/1424-8220/26/16/5316) 是最接近的反证：它已经把 sensor health、task confidence 和 residual observability 区分开，并建议开放 benchmark 应标注 physical degradation、environmental state、perception output 和 vehicle response。它表明问题不是凭空的，也使我们不能把概念本身称为原创；但它同时明确这是未来 benchmark 建议，且其范围是车载 camera/LiDAR/radar，不是低成本 RGB/NIR/ToF 采集和小任务 action policy。

[Zhiwei](https://pmc.ncbi.nlm.nih.gov/articles/PMC13418726/) 又是第二近的反证：它有真实 30 天、Pi 5、reference-free self-diagnosis 和 offline fallback。它的物理一致性 reasoning 可借鉴，但气体/颗粒传感与视觉几何、同步、目标可见性不同；不能宣称我们第一个 on-device self-diagnosis。

## 下一步必须做的三个检查

1. 对每个候选故障造一个可复查 trigger：LED current/state、camera frame id、ToF return/variance、timestamp skew、遮挡/光照/距离测量。
2. 在冻结的下游任务上收集“healthy but insufficient”例子，否则 root cause label 会退化成普通 quality classification。
3. 在正式 proposal 前以同一 Boolean query 复查 Google Scholar、IEEE Xplore、ACM DL、arXiv 和引用链；把检索日、query、候选命中与排除理由附在附录。
