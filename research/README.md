# Edge Palm FYP Research Notebook

本目录是研究笔记，不是最终论文，也不替代 `minutes/` 的会议记录。目标是在先做最小 demo 的同时，逐步收窄一个可验证、可部署、且不过度宣称的 FYP 创新点。

## 文件导航

| 文件 | 内容 | 更新时机 |
| --- | --- | --- |
| [00-research-method.md](00-research-method.md) | 研究问题、检索方法、AI 的使用边界和推理日志 | 每次改变方向时 |
| [01-literature-map.md](01-literature-map.md) | 阅读过的综述/论文、可复现信息和证据等级 | 每读一篇就追加 |
| [02-story-and-innovation-options.md](02-story-and-innovation-options.md) | 澳门场景、经济价值、候选创新点和否决条件 | 与老师/用户访谈后更新 |
| [03-research-reflection.md](03-research-reflection.md) | 已被否定的直觉、当前最小研究主张和继续/停止门槛 | 每个阶段实验后更新 |
| [04-recent-research-landscape.md](04-recent-research-landscape.md) | 2023--2026 近期论文主题图谱，以及对 FYP 的含义 | 每轮文献扩展后更新 |
| [05-evidence-ledger.md](05-evidence-ledger.md) | 精读论文、标准与系统资料的可审计证据账本 | 每次精读或改变研究决策后更新 |
| [06-evaluation-and-data-plan.md](06-evaluation-and-data-plan.md) | 公开数据、自采数据、切分和指标的实验协议草案 | 实验开始前冻结，变更需记录原因 |
| [07-current-synthesis.md](07-current-synthesis.md) | 近期文献、场景、反思与当前决策树的汇总 | 与老师讨论前更新 |
| [08-counterevidence-and-boundaries.md](08-counterevidence-and-boundaries.md) | 主候选方向的反例检索、竞争路线与不可宣称事项 | 每次定位方法时更新 |
| [09-reading-coverage-audit.md](09-reading-coverage-audit.md) | 本轮读到的范围、精读深度和后续阅读优先级 | 每轮研究结束时更新 |
| [10-story-validation-plan.md](10-story-validation-plan.md) | 将必要性、经济价值和采用条件写成可否定的访谈/流程验证计划 | 场地访谈前与完成后更新 |
| [11-ai-assisted-research-protocol.md](11-ai-assisted-research-protocol.md) | AI 辅助检索、阅读、反证和写作的可审计流程 | 每次变更检索或证据规则时更新 |
| [12-pad-protocol-reading-log.md](12-pad-protocol-reading-log.md) | DAPANet/HFSRA 精读、推理变化与 PAD 到最终放行风险的协议边界 | 每轮深读攻击协议后更新 |
| [13-b0-reproducibility-log.md](13-b0-reproducibility-log.md) | Tongji、PalmMatchDB、PPNet 工件审计与最小 B0 的三阶段落地路径 | 每次选择数据或运行时后更新 |
| [14-formal-survey-reading-log.md](14-formal-survey-reading-log.md) | 2026 正式掌纹深度学习综述精读，以及它如何收紧 edge/PAD 研究主张 | 每次完成综述或研究边界复核后更新 |
| [15-vis-nir-boundary-log.md](15-vis-nir-boundary-log.md) | VIS-NIR 异构掌纹匹配的精读边界，防止将跨光谱识别误写为 PAD | 每次研究多光谱/主动采集时更新 |
| [16-dynamic-terms-boundary-log.md](16-dynamic-terms-boundary-log.md) | 审计文献中 "dynamic" 与 "sequence" 的真实含义，防止将生成配对或空间 token 误写成物理时序/活体 | 每次研究主动采集或序列模型时更新 |
| [17-active-illumination-neighbor-log.md](17-active-illumination-neighbor-log.md) | 精读配对 flash/non-flash 指纹近邻工作，界定主动光照在掌纹项目中的可借鉴与不可外推之处 | 每次设计 illumination protocol 或 PAD 对照时更新 |
| [18-maintenance-story-evidence-log.md](18-maintenance-story-evidence-log.md) | 审计临时维护访问、工单和身份核验的证据，避免将参考架构写成澳门市场事实 | 每次更新应用故事、访谈或经济假设时更新 |
| [19-sensing-reproducibility-log.md](19-sensing-reproducibility-log.md) | 审计 2025 smart palm sensing 的代码、数据与硬件边界，防止将 ROI 工件误当作 Pi 采集系统 | 每次选择 ToF/ROI/video baseline 时更新 |
| [20-random-order-boundary-log.md](20-random-order-boundary-log.md) | 精读 2020 NIR/UV 随机灯序与跨帧差异检查，界定它为何不能成为本项目的创新点 | 每次定义 M 的 challenge 或 response relation 时更新 |

## 当前工作结论

1. 最小 demo 先完成无接触 RGB 掌纹 `1:1 verification`、ROI、阈值和端侧测量；它是仪表盘，不是论文贡献。
2. 条件性候选主线是：`ToF 固定几何 + claim 后实际状态可观测的 RGB/NIR command + 预冻结 response verifier + 风险门控`。随机顺序和帧差已有直接掌部先例；只有 relation 相对静态多谱 B2 在未见 PAIS 与 edge 成本上证明额外价值时，才保留该候选。没有 relation 时它只是动态采集，候选安全主张停止。
3. 澳门只作为访谈与数据治理约束地点，不作为“没有掌纹”的市场空白；已有局部掌纹/掌静脉支付先例。应验证受控工作现场是否存在尚未被合理满足的离线、隐私和抗伪造需求。
4. 当前不把“识别非法劳工”作为应用宣称。系统只能确认某人是否匹配授权名册；法律身份和劳动资格仍须由有权系统和人工流程判定。
5. `edge` 只表示本地 capture/inference 与更小的数据流，不等于完整隐私、模板保护或侧信道安全。

## 接下来最有价值的证据

- 实验室设备能否独立输出并控制 RGB、NIR、距离和补光；
- 5--10 位现场角色的访谈，验证卡片转借、人工核验、网络故障和资料留存是否真是痛点；
- 相同人跨日期、跨距离、跨光照的自采数据；
- 打印、屏幕重放和普通纹理贴片在现有原型上的基线攻击表现。
