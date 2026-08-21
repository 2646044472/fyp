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

## 当前工作结论

1. 最小 demo 先完成无接触 RGB 掌纹 `1:1 verification`、ROI、阈值和端侧测量；它是仪表盘，不是论文贡献。
2. 条件性候选主线是：`ToF 固定几何 + claim 后随机 RGB/NIR illumination challenge + verifier 检验的 response relation + 风险门控`。它必须相对静态多谱 B2 在未见 PAIS 与 edge 成本上证明额外价值；没有 response relation 时它只是动态采集，候选安全主张停止。
3. 澳门只作为访谈与数据治理约束地点，不作为“没有掌纹”的市场空白；已有局部掌纹/掌静脉支付先例。应验证受控工作现场是否存在尚未被合理满足的离线、隐私和抗伪造需求。
4. 当前不把“识别非法劳工”作为应用宣称。系统只能确认某人是否匹配授权名册；法律身份和劳动资格仍须由有权系统和人工流程判定。
5. `edge` 只表示本地 capture/inference 与更小的数据流，不等于完整隐私、模板保护或侧信道安全。

## 接下来最有价值的证据

- 实验室设备能否独立输出并控制 RGB、NIR、距离和补光；
- 5--10 位现场角色的访谈，验证卡片转借、人工核验、网络故障和资料留存是否真是痛点；
- 相同人跨日期、跨距离、跨光照的自采数据；
- 打印、屏幕重放和普通纹理贴片在现有原型上的基线攻击表现。
