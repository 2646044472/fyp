# 正式掌纹综述精读日志：从“高准确率”回到可部署证据

最后更新：2026-08-21。本文记录对 Gao et al. *Deep Learning in Palmprint Recognition: A Comprehensive Survey* 的精读如何改变本项目判断。它不是该文的逐段摘要，也不以综述替代对关键原始论文、数据和工件的核验。

## 1. 版本与阅读边界

- 正式版：Gao et al., *IEEE Transactions on Systems, Man, and Cybernetics: Systems*, 56(3), 2143--2162, 2026-03, DOI [10.1109/TSMC.2025.3649416](https://doi.org/10.1109/TSMC.2025.3649416)。发表状态和书目信息由 [Yonsei University record](https://yonsei.elsevierpure.com/en/publications/deep-learning-in-palmprint-recognition-a-comprehensive-survey/) 核对。
- 可逐段阅读版本：[arXiv:2501.01166v2](https://arxiv.org/html/2501.01166)，2025-10-21。其目录覆盖 ROI、质量、closed/open-set、security/privacy、cross-domain、multi-modality、lightweight、datasets、evaluation 和 outlook。
- 因没有取得 IEEE 最终 PDF，下面关于段落、表和措辞的结论均指 arXiv v2；正式版只用于确认论文已经同行评审发表。两版的细微差异尚未逐页比对。

证据等级：`E1`（正式书目信息 + 可访问 v2 的相关原文）；不是“最终版每一个数字都已核实”。

## 2. 读到的关键结论

### 2.1 ROI 与采集质量是系统的一部分

综述把 acquisition、ROI extraction、quality enhancement、feature extraction 和 matching 写成连续流程，而非把 ROI 当作可忽略的前处理。无接触条件下，姿态、距离、照度、背景和 ROI 对应关系会改变后续特征。

**对 FYP 的推理：** B0 必须记录 ROI success/failure、quality reject、retry 和跨 session 变化；只报告 matcher accuracy 会掩盖真正的端侧失败来源。ToF 在未证实攻击区分力前，优先作为受限几何/quality gate，而非 "liveness sensor"。

### 2.2 闭集结果不能替代现场泛化

综述区分 closed-set 和 open-set；并将 lighting、resolution、device 和 environment 造成的 domain shift 视为 cross-domain recognition 的核心。其 outlook 认为 open-set/cross-domain generalization 仍是关键挑战，并要求 cross-dataset consistency、domain adaptability 和 user-independent evaluation。

**对 FYP 的推理：**

- B0 的公开测试不能采用同 session 的随机 image split 作为主结果；至少留出 identity 与 session。
- 自采传感实验必须让 session、距离、illumination、camera/firmware configuration 和操作人员可追溯；否则不能说明设备变化下的稳定性。
- 若使用 DAPANet 类的 target-domain adaptation，必须另设实验 arm 并披露 unlabeled target exposure；这不能与 blind PAIS/session holdout 混写。

### 2.3 数据规模、metadata 与公平性是实验设计问题

综述指出 palmprint benchmark 的规模/多样性相对成熟 biometric modality 仍有限，且许多数据缺少 metadata；demographic、environment、sensor、pose 和 temporal variation 都会影响 generalization。

**对 FYP 的推理：** 小型实验室数据不适合估计极低 error rate，也不应以少量参与者宣称人群公平性。我们要发布的是字段完备的 protocol 和材料/会话分层结果：参与者层 split、日期、距离 bin、light state、sensor setting、ROI/retry、攻击材料与 output/capture chain。未经同意，绝不发布原始掌纹。

### 2.4 轻量模型是路线，不是 edge 证据

综述单列 lightweight palmprint recognition，指出大模型在 mobile/edge 有 computation/resource cost，并列举 MobileNet 系轻量网络和 lightweight ROI 的工作。

**对 FYP 的推理：** “用了 MobileNet/PPNet/量化”最多是候选工程路线。论文必须在实际 Raspberry Pi 上测 `T_capture`、`T_ROI`、`T_embedding`、`T_match`、p95 interaction time、peak RAM、模型/模板大小和输入端能耗；不能从论文的 mobile/GPU 数字推导 Pi 可用性。

### 2.5 安全与隐私存在独立攻击面

综述将 spoofing、template correlation/reconstruction 和 adversarial perturbation 分开；outlook 同时讨论 template protection、cancelable biometrics、encryption 和 anti-spoofing。也就是说，提升 recognition accuracy、把 raw frame 留在本地、或加入 NIR，均不自动解决另一个攻击面。

**对 FYP 的推理：**

- 将 final decision 分为 matcher threshold、PAD/risk gate 和 authorization claim 三层，分别记录失败与指标。
- PAD 使用 APCER/BPCER，并用固定 matcher threshold 上的 IAPMR 验证“攻击是否真的通过”；不以 pooled classification accuracy 代表开门安全。
- edge 的唯一可验证说法是本地 capture/inference 减少 raw-frame transmission；模板可撤销、不可关联、不可逆、抗重建及整个门禁安全都不作声明。

## 3. 综述没有替我们证明的事情

1. 它不证明实验室的 RGB/NIR/ToF 组合对打印、屏幕、贴片或 relay 有效。
2. 它不证明短随机 RGB/NIR 序列形成了 challenge-response；必须预定义并验证 response relation，并相对静态 B2 测试。
3. 它不提供本项目可直接拿来跑的 Pi model、weight、license、data split、camera pipeline 或能耗数值。
4. 它不提供澳门特定的需求、可接受性、ROI 或合规结论。
5. 它的 high closed-set accuracy 汇总不能成为本项目的目标阈值，也不能替代低 FAR、未知 PAIS、cross-session 的评估。

## 4. 本次阅读后的研究主张收紧

原来的直觉是“edge 设备跑起来 + 多传感，就有创新”。综述和已读原始工作共同否定了这个说法：ROI、轻量网络、多模态、跨域、PAD 和 privacy 都已有独立研究线。

现在可检验的主张保持为：在**受限几何**的 Pi 级采集盒上，是否能以可审计的 capture metadata 和预冻结的 `1:1` threshold，测量 B0/B1/B2/M 在 identity/session/PAIS holdout 下的安全--可用性--资源 trade-off。只有 M 的 verifier 真正检查随机 challenge 的 response relation，且在未见 PAIS/session 相对 B2 降低 IAPMR 而不造成不可接受 BPCER/retry/p95/energy 时，才可讨论主动风险门控的附加价值。

这也保留了有价值的负结果：若 edge 的资源或多传感损耗大于收益，或收益只发生在已见攻击材料，结论应是该硬件等级不值得承担额外复杂度，而不是改写成“掌纹已经安全”。

## 5. 由此冻结的后续阅读与实验优先级

1. **Gate 0：** 核对实际 sensor driver、IR-cut、LED control、distance accuracy、frame order 和 power path；这是对综述所列 capture/ROI 问题的本机回答。
2. **B0：** 先以许可清楚的输入做工程 smoke test；正式 benchmark 只在数据条款、identity/session split 与 capture metadata 被核对后建立。
3. **Gate 1：** 在获批的物理攻击范围内，按 PAIS/material/output-capture chain/session 留出，先量静态 B0/B2 的 IAPMR。
4. **M：** 仅在 B2 稳定后实现；把 target adaptation、已见材料调参和 blind holdout 分开报告。
5. **场景：** 仍需访谈验证受控低频维护核验是否有真实流程、人工与网络故障成本；澳门只是访谈/数据治理环境，绝不是市场空白证据。
