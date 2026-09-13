# 更广 Edge Sensing 扫描：为什么暂不保留第三主方向

日期：2026-08-27。本轮问题是：在 E1 风险审计式 cascade 与 E3 共因独立证据之外，是否还有一个更强、且能在现有硬件条件下被防守的 edge-sensing FYP？答案目前是没有。以下不是“这些方向没有价值”，而是它们的直接近邻已足够强，或需要超过本项目范围的新硬件/数据。

| 候选 | 为什么看似有价值 | 近邻/障碍 | 当前决定 |
| --- | --- | --- | --- |
| privacy-aware cloud escalation | 只在本地不足时上传少量证据，降低原始影像暴露 | CoSense-LLM 已将 uncertainty/cost/privacy 纳入 edge-cloud routing；还引入网络、身份/数据治理与云端信任边界 | 不单独立题；最多是 E1 的 `uncertain` action |
| pipelined partial evidence | 边采集边编码，早期 confidence 足够则跳过慢模态 | MMEdge 已做 fine-grained sensing/encoding、cross-modal speculative skipping 和 edge testbed | 不单独立题 |
| event-camera / learned sensor threshold | change-driven sensing 可减少帧与功耗 | NeuroViG、task-specific event camera、event edge detection 已覆盖实际触发与专用硬件 | 需要新硬件；不能用普通 Pi camera 重命名 |
| information freshness / stale state | 不重采会让决策依赖过期证据 | AoI scheduling、asynchronous/latency-robust fusion 已是成熟线 | 只作为 E1/E3 的时序压力变量 |
| online health/calibration maintenance | 镜头污染、LED 老化、姿态 drift 影响长期可靠性 | sensor monitoring、online calibration、cross-modal matching、MoME 等已有强近邻 | 只保留在 S 的真实 telemetry + action-cost protocol 内 |
| capture provenance / witness sensing | 第二 sensor 证明第一 sensor 来自真实物理世界 | IAD 标准、visual challenge、virtual-camera detection 已淘汰原 capture-provenance 题；witness sensing 也已有近期 proof-of-concept | 不与当前 FYP 合并 |

## 结论

当前不应为了“多一个 edge 方向”而继续保留这些宽泛题。可防守的研究主线仍是：

1. **E1：风险审计式 cascade sensing**，把不唤醒造成的不可观测风险变成统计/控制问题；
2. **E3：共因退化下的独立证据 acquisition**，检验多传感冗余是否真的降低安全风险。

E2 时间有效性、online health、cloud escalation 可以作为两个主线的 action 或事件轴，不能写成额外独立贡献。若后续获得 event camera、独立 MCU trust root、长期漂移数据或真实工业合作，才重新开启相应的 novelty gate。
