# 研究优先候选的近邻核查日志

日期：2026-08-27。此日志记录为什么旧的“传感器失效闭环”被降级为系统 demo 候选，及四个新候选为何仍有可检验的研究切口。

## P：开放世界掌纹 PAD

- [PALMspoof / Bhilare et al. 2018](https://dspace.iiti.ac.in/handle/123456789/5829) 已构造 104 subject、三类 artefact 数据，并报告 display/print 对 palmprint verifier 的攻击；不能声称 palm PAD/IAPMR 新。
- [DAPANet](https://www.sciencedirect.com/science/article/pii/S014193822400235X) 已做 multi-source domain adaptive palmprint PAD；不能声称 cross-domain PAD 新。
- [FIDO PAD criteria](https://fidoalliance.org/specs/biometric/requirements/Biometrics-Requirements-v1.1-fd-20190606.html) 与 [NIST SOFA](https://github.com/usnistgov/SOFA/blob/nist-pages/FMR_and_PADER.md?plain=1) 明确系统级 IAPMR 的定义，故不能改造指标后冒充方法。
- 本轮未找到将未见 PAIS 和 capture-device **同时**留出、将 matcher threshold 固定、并以 calibrated IAPMR budget + coverage 为主要研究终点的 palmprint 方法。若后续找到，应放弃 P 的新颖性主张。

## R：证据约束复原

- [UniRestore](https://unirestore.github.io/)（CVPR 2025）已同时面向 perceptual/task-oriented restoration；[OPIR](https://arxiv.org/abs/2601.10192) 已在 all-in-one restoration 内输出 uncertainty；不能声称 task-aware/uncertainty-aware restoration 新。
- [HalluGen](https://openaccess.thecvf.com/content/CVPR2026/papers/Kim_HalluGen_Synthesizing_Realistic_and_Controllable_Hallucinations_for_Evaluating_Image_Restoration_CVPR_2026_paper.pdf) 和 [sFRC](https://arxiv.org/abs/2603.04673) 已证明 hallucination evaluation/detection 本身是活跃领域，特别是医疗重建。
- 本轮未找到以 RGB/NIR/ToF 或 RGB-D 的**原始 companion modality** 为恢复输出提供 support certificate，并以证据 gate 控制 edge inspection 下游决策的直接工作。该结论须在选题后以 `cross-modal/physical consistency/restoration hallucination/industrial inspection` 的引用链再查一次。

## T：时间不确定性

- [Li et al. 2026](https://flore.unifi.it/handle/2158/1469153) 已解决 asynchronous sensor network target tracking 的未知 time offset estimation；不能将“估计 offset”作为独立创新。
- 缺失模态综述与 VLA/robotics 综述都把 temporal misalignment 视为部署问题；不能把“时间不同步”包装为新发现。
- 未找到将 actual LED state、frame timing、ToF return 形成 time-offset posterior，并最终给 edge visual task 的 calibrated selective risk 的直接工作。硬件 Gate 0 前只是研究假设。

## O：normality shift vs defect

- [ICCV 2023 anomaly under distribution shift](https://openaccess.thecvf.com/content/ICCV2023/papers/Cao_Anomaly_Detection_Under_Distribution_Shift_ICCV_2023_paper.pdf) 已处理 shift；[2026 industrial stream work](https://www.catalyzex.com/paper/towards-differentiating-between-failures-and) 已区分 failure/domain shift；[2026 conformal industrial anomaly](https://www.sciencedirect.com/science/article/abs/pii/S0951832026002334) 已把 conformal reliability 引入工业场景。
- 这些都排除“shift-aware / conformal anomaly”作为新词。当前候选只保留 visual normal-only、unseen normality shift 与 unseen defect 三态动作的联合协议；若找到同样的 visual protocol，就转向 R 或 T。
