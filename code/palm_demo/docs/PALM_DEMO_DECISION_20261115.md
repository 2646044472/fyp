# 掌纹演示候选与数据集结果（2026-11-15）

## 决定

**目前不批准任何方案在树莓派上作真实身份确认演示。** 现有数据没有同时证明可用的自动 ROI、可靠识别、合理陌生人拒识及 Pi 端实时表现。这里给出每个队列当前最有信息量的离线臂，供选择后续验证顺序；“最佳”只指该数据集/协议内的实验结果，不是部署推荐。

如果必须在 Pi 到位前准备展示素材，可展示采集界面、ROI 质量门和拒绝/重试流程；识别标签须明确标为实验，不得作为身份确认。这是演示呈现边界，不是算法验收。

## 当前数据集结果与限制

| 数据集/协议 | 最有信息量的 ROI + 识别器臂 | Rank-1 | EER（genuine / impostor） | ROI/评分分母与开集结果 | 决策 |
|---|---|---:|---:|---|---|
| PalmSet b16d，已暴露 | 作者公式 reference ROI + SF2e20 | 700/700（reference arm）；PKLNet-v5 自动 ROI 配对公共支持 325/374 | reference .00157（700/29,300）；PKLNet-v5 .09893（374/12,078） | PKLNet-v5 ROI 1,514/1,600，图库 12/20 手完整；758 unknown 只在11手共同子图库算EER，不能报完整开集FA | reference 不可作为现场自动定位；PKLNet-v5落后且大量图库缺失。身份、手侧为未核验文件名代理，并与训练图像严重重叠。 |
| 11KHands development20，已暴露 | D127 21-point + SF2e20 | 185/185 | .04324（185/9,615） | ROI 590/590、图库20/20；冻结迁移阈值下 unknown FA 62/305 | 闭集结果高，但陌生人误接受不可接受；没有该数据集专属冻结阈值，不能部署。 |
| X-Palm dev/test，已暴露 | 官方 reference ROI + PB170（同一参考输入上 Rank-1较高） | dev 122/140；test 117/136 | dev .08760（140/4,840）；test .10294（136/4,884） | reference ROI 813/813；test 冻结门 unknown 1 FA/114 reject。自动 D127 在 test 388/406 成功，但只有8/20图库完整，Rank-1 PB 39/136（55可排） | reference 是测试上界而非运行时 detector；D127 无完整图库开集结果。数据曾暴露。 |
| Axon，已暴露 | D127 21-point + SF2e20 | 53/60（59可排） | .11864（59/1,121） | ROI 118/120；只有1/6 fold的10陌生query有完整图库且均拒绝，其余49不可评分、1 ROI失败 | 无 reference ROI；小支持不足以作拒识/FAR结论。 |
| 自采已记录队列，已暴露 | PKLNet-v5 ROI + SF2e20 | 63/94 | 此臂未报告 | ROI 196/196；固定迁移阈值下 unknown FA 0/48（PB 1/48）；另有 RTM/D127 严格共同支持 SF2 Rank-1 46/59、51/59，EER .22034/.11864（各59/590） | 11个身份/手标签仍是记录代理，unknown仅48张；0/48不能支持低FAR。无独立身份、设备和完整现场拒识依据。 |
| TCD/Tongji 固定 PKL ROI | 固定 PKL ROI + SF2e20 | 5,800/6,000（5,877可排） | .016305（28,914/17,261,220） | 新增RTM自动ROI共11,993/12,000成功，但协议只有gallery/known/supplemental，无stranger；身份/手/设备映射不足 | 只能作组件/闭集描述；不能声称开集或自动ROI端到端验证。 |
| BJTU_PalmV2 预裁剪 development | 作者预裁ROI + SF2e20 | 380/400 | .08000（1,000/39,000） | 固定源开发阈值下 unknown FA 0/200；预裁图，20人验证队列已暴露；F/S是采集phase而非已核实设备 | 仅识别器筛查；没有原图/自动ROI对照，且队列已曝光。 |

完整计划分母、PB/SF2双臂和状态见总台账 D149、D150 与 D166–D168 addendum。各 EER 的支持范围并不总相同，不应跨表直接排名；上表只在同数据/同输入臂内部解释。冻结阈值来自既有 source development 数据；未知角色仅当完整计划图库可用时才计入接受/拒绝。

## 建议的验证顺序

1. **ROI先过人工可用性检查。** 使用 D167 盲审包核对自动 ROI 是否覆盖可见掌区。审阅包含失败与成功对照，尚未人工阅览；不能把它当作标签核实或模型评分结果。
2. **Pi通电后先按原交接流程做小规模端到端验收。** 备份当前 Pi 配置，保留回滚；只用明确登记者和一名陌生参与者，记录所有质量拒绝、重试、失败、误认/拒识及 camera→decision 延迟。Pi 未连接前不改变已部署 runtime，也不报告 X 的离线计时为 Pi 速度。
3. **新的独立数据必须先有可信 person/hand/device 分组与完整图库，再冻结阈值与计划分母。** 当前本机可用队列都已暴露，或缺 raw、reference ROI、可靠标签或 stranger protocol。不要在这些目标上重新拟合阈值。

## 可复现入口

以下为现存X运行工件；复现时使用各目录冻结的 protocol/manifest、checkpoint SHA 和 score summary，不要从当前源码默认参数猜测历史设置。

- 统一 reference vs D127：`runtime/palm-fixed-D127-PB170-SF2e20-unified-D149-X-20261115-001/REPORT.md`、`protocol.json`。
- ROI × recognizer 因子对照：`runtime/palm-2x2-factorization-D150-X-20261115-001/run-006/APPENDIX.md`；CPU cached scorer `runtime/palm-2x2-factorization-D150-X-20261115-001/run-006/`。
- TCD RTM 与 PalmSet三ROI：`runtime/palm-full-evaluation-ledger-X-20261115-001/ADDENDUM-D166-D167-FULL-PALMSET-20261115.md`；逐图记录、runner、协议和score位于 D166/D167 目录。
- PalmSet共同支持重聚合：`runtime/reconcile-palmset-D167-3roi-paired.py`；输入仅是 D164/D165/D167冻结向量与 b16d manifest，不需要重跑推理。
- D167 ROI盲审：`runtime/palmset-D167-blind-roi-review-20261115-001/README.md`；映射seal单独存放，不进入Git。
- Pi演示边界及供电/回滚流程：`runtime/palm-fixed-D127-PB170-SF2e20-unified-D149-X-20261115-001/DEMO-HANDOFF.md`。

## 结论状态

已完成的内容：已有数据可形成的主要 ROI/识别器离线对照、全计划失败分母记录、跨数据集固定候选评估、缓存配对分解和本地演示交接材料。尚未完成：D167人工盲审、任何未暴露身份级验证、可靠物理设备迁移验证、Pi部署/速度/真人体验验收。故当前没有可被证据支持的 live identity-demo winner。


### X-Palm D144 on the exposed test partition (added 2026-11-15)

D144 recovered 5/406 ROIs (3 gallery, 1 registered, 1 unknown), had zero regressions among 388 D127 successes, and increased complete gallery support from 8/20 to 11/20. Native rankable Rank-1 was PB 39/55→51/76 and SF2 33/55→46/76; EER changed .14545→.16974 (55/385→76/760) and .25455→.26316 (55/385→76/760). On identical support (8 hands, 55 probes, 55 genuine/1,265 impostor scores), rank and EER were unchanged for both models. The 21 newly rankable probes were a support gain, not an equal-support recognition improvement. All 115 stranger rows remain unscorable against a complete gallery. This partition was previously exposed; D144 is not promoted. Full report and scripts: `runtime/xpalm-pose-geometry-detector-fallback-D144-test-X-20261115-001/REPORT.md`.


### TCD D168 strict common support (added 2026-11-15)

The cached-vector three-ROI comparison used the same 5,539 queries and 562 complete filename-proxy galleries. PB170 Rank-1 was fixed PKLNet 4,988/5,539 (EER 2.0401%), D127 4,158/5,539 (10.2546%), RTM 4,165/5,539 (7.3298%). SF2e20 was 5,472/5,539 (.6138%), 4,137/5,539 (15.8332%), and 3,442/5,539 (15.6346%). 461/6,000 planned queries were outside paired support. TCD has no unknown queries, so this does not establish stranger rejection; identity groups are filename proxies and data are exposed. This cached comparison does not change the Pi decision. Details: `runtime/tcd-three-roi-common-support-D168-X-20261115-001/REPORT.md`.
