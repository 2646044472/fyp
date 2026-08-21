# 掌纹 PAD 协议精读日志：从“分类效果”到“最终放行风险”

最后更新：2026-08-21。本日志保留这轮阅读中发生的推理变化，方便老师追问“为什么不直接复现一篇近期 PAD 网络”。它不是隐藏推理记录：每个判断都附来源、可复述范围和仍未知道的部分。

## 1. 这轮问题

不是“最近有没有一个更高 accuracy 的掌纹 PAD 网络”，而是：

1. 近期工作把什么算作 unknown-domain 测试？
2. 它们的攻击是哪个 physical/capture chain，是否可迁移到 RGB/NIR/ToF Pi 盒？
3. 结果是 PAD classifier error，还是攻击最终匹配到目标模板的风险？
4. 论文、数据和代码是否足以成为可运行 baseline？

先读 [DAPANet](https://doi.org/10.1016/j.displa.2024.102871) 的方法/协议说明和 [HFSRA](https://doi.org/10.1049/ipr2.70029) 的全文协议段，再回查 XJTU-PalmReplay 在二者中被怎样使用。并检索作者/题名/数据集的公开 artifact；本轮未找到可核验的 XJTU-PalmReplay 下载、license、dataset card、code 或 weights。这个“未找到”不证明作者不提供，只表示它不能进入当前的可运行数据清单。

## 2. 两篇近期工作的可复述内容

| 资料 | 真正测试的内容 | 对我们有用的内容 | 不能转用的内容 |
| --- | --- | --- | --- |
| DAPANet, *Displays* 2025 | 在 XJTU-PalmReplay 的五个 display-capture domain 上，作 multi-source 到 multi-target 的 domain adaptation；目标域是 unlabeled adaptation input。 | 不能把同一 display/capture domain 的帧随机打散到 train/test；至少要按输出设备、重拍设备或材料整体留出。 | 使用未标注 target data 的 transductive adaptation 与本项目“完全不碰 test PAIS/session”的测试不是同一任务；其 PAD 数字不等于 target-match IAPMR，也不等于 Pi、NIR、ToF 或真实贴片表现。 |
| HFSRA, *IET Image Processing* 2025 | 聚焦 secondary-capture 造成的 detail loss、moire 与稀疏/密集高频纹理；给出 closed/open/cross-domain 三类 protocol。其 cross-domain protocol 从一个 domain 取 train/validation、另一个 domain 作 test，列出 20 个 train--test combination。 | 已见 output/capture artefact 很容易成为捷径特征；cross-domain 必须按 domain 单列，而不只给 pooled ACER。论文也提醒平面 RGB replay 下 depth 未必是强信号。 | 它的分析针对其 RGB display-recapture 数据；不等于 ToF 无用，也未评估有真实几何的贴片、主动光照、身份核验、交互时延或 Pi 能耗。 |

两者都报告 PAD 侧的 `APCER/BPCER/ACER` 或类似分类结果，均没有替代以下系统问题：一个攻击是否同时通过 PAD **并**匹配到被 claim 的目标模板。因此它们是 *PAD protocol* 的反例和参考，而不是我们 B0--M 的端到端结果 baseline。

## 3. 本轮如何改变研究设计

### 3.1 把“未见攻击”拆成可检查的三层

不能只写“unknown attack”。每个测试结果需明确留下哪一层：

| 留出层 | 例子 | 解释时可说什么 | 不能说什么 |
| --- | --- | --- | --- |
| PAIS/material | 未在 development 出现的纸张、屏幕或贴片材料 | 对该未知材料的 black-box 泛化 | 对所有攻击材料都泛化 |
| output/capture chain | 新打印机、屏幕型号/刷新率或相机/光照 session | 对该重拍链的泛化 | 攻击的生理/3D 属性已经被理解 |
| session | 不同日期、重新摆放设备、环境光改变 | 对当前设备随时间的稳定性 | cross-device 或 cross-site generalization |

小型 FYP 不可能覆盖所有组合。因此最小做法是：至少一个 PAIS/material 完全不进入 development，且另一个 capture session 不参与阈值、response-relation 或 quality rule 的设定；若只更换 screen 而纸张、攻击制作和相机都相同，就如实称为 output-device holdout。

### 3.2 目标域适配必须与盲测分开

DAPANet 的论文价值在于证明 cross-domain 是正式问题，不在于授权我们使用 test domain 调参。当前 FYP 的主要 M 测试固定为 **blind holdout**：目标 PAIS/session 的 raw frames、标签、quality distribution 和设备 metadata 都不参与训练、阈值、response-relation 或 escalation rule。

若日后做一个“设备到场后收集无标签帧再校正”的 adaptation arm，必须和 blind holdout 表分开，并逐项报告：可看到哪些 target frames/metadata、是否含攻击帧、何时冻结、对 bona fide 与每个 PAIS 的影响。它不能再被称为 zero-data unknown-PAIS test。

### 3.3 PAD classifier 和开门决策必须同时记录

对于每个 attack presentation，保留四个元素：`claim target`、identity match score、PAD/gate score、最终 allow/retry/fallback。报告：

`IAPMR = count(PAD/gate pass AND target match) / count(targeted attack presentations)`

并与 APCER/BPCER 分开。若一个方法以大量 bona fide quality reject 换取低 APCER，它的 IAPMR、BPCER、ROI failure、retry 和 `T_interaction` 会共同暴露这个 trade-off。这样才能回答“这台锁是否变得更难被打开”，而不是只回答“图像分类器是否识别某些重拍纹理”。

## 4. 对 ToF 与主动光照的反思

HFSRA 中平面 replay 的 depth 反例使 ToF 的默认角色更保守：先固定工作距离、减少 ROI drift、记录几何质量。真实手掌上贴片可能带有正常深度，平面纸张/屏幕也可能被距离门拦住；两种情况都不能由该论文预先断言。

同理，DAPANet/HFSRA 的强项是从已有 capture artefact 找 domain-invariant feature，不是验证 session-random light challenge。我们的 M 只有在 Gate 0 已证明“每一帧的实际 illumination state 与时序”后才成立；即便如此，也只声称对预先定义攻击集的 possible freshness/risk gate，而非对实时 display、真人贴片、relay 或数字注入的 liveness/security guarantee。

## 5. 这轮未解决的事项与下一步

| 未解决项 | 为什么还不能下结论 | 下一步证据 |
| --- | --- | --- |
| XJTU-PalmReplay 能否作为 benchmark | 未获得可下载 files、license、identity/split/PAIS metadata 或 code/weights。 | 仅在取得作者/机构明确入口、许可和完整 metadata 后再做 artifact audit。 |
| HiChrom-MAE 的真实 protocol | 已取得 ACM metadata/abstract：其称 seven-domain cross-medium PAD、high-frequency residual reconstruction 与 chromaticity alignment；仍未得到正文。 | 取得正式全文后核对 domain/PAIS、split、APCER/BPCER、资源和 artifact；不从 abstract 推断其对 Pi/M 的效果。 |
| 主动 M 是否胜过 B2 | 文献不能代替本设备的实际光学、攻击和 edge 测量。 | 完成 Gate 0，再以冻结 B0/B2/M 和 PAIS/session holdout 测 IAPMR/APCER/BPCER/ROI/p95/energy。 |
| 目标工作流是否值得采用 biometrics | PAD 文献不提供澳门运营成本或接受度。 | 按 [10-story-validation-plan.md](10-story-validation-plan.md) 完成访谈与流程计时；需求闸门失败则不讲经济故事。 |

## 6. 当前一句话结论

近期 palmprint PAD 已经将 display-capture domain generalization 作为问题；本 FYP 不竞争“又一个 PAD 分类器”。它要么用完整的 claim-to-decision protocol 测量主动采集是否降低 held-out attack 的 IAPMR，要么诚实收敛为 Pi 级无接触掌纹采集质量与 edge trade-off 报告。
