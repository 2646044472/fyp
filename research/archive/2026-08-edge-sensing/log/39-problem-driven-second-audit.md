# 问题驱动的第二轮研究审计

日期：2026-08-27。目的：主动提出会推翻候选的问题，再用近年论文、协议和 artifact 检查，而不是为既有题目寻找支持性措辞。

## 审计规则

对每个候选连续问四件事：

1. 这个“机制”是否已经在别的模态或任务里出现？
2. 是否已有同任务的 protocol，而我们只是换设备或数据？
3. 能否定义一个 baseline 可以推翻的主要终点？
4. 最小数据和硬件是否能真的观测该终点？

## P：掌纹 PAD

**跨域 PAD 是否已经有人做？** 是。2023 IEEE 论文已做 palmprint anti-spoofing 的 domain generalization 和 unseen target domain；2025 PalmRSS 又把 single-source unseen-domain generalization 带入 palm biometrics。因此“未知设备/跨域”不能单独构成题目。

**系统级安全指标是否只是换名字？** 是。FIDO/NIST 已定义 IAPMR，PALMspoof 已报告 display/print attack。PAD accuracy、APCER 或换成 IAPMR 都不自动带来方法新颖性。

**剩余问题：** 是否存在同时留出 PAIS material 和 capture device、冻结 matcher threshold、以 calibrated IAPMR budget 和 bona-fide coverage 为主要终点的 palmprint 实验？这仍是一个需要数据库和引用链复核的窄问题。若找不到多设备与多材料数据，P 应降为 benchmark，不应假装做出新 PAD 网络。

## R：跨模态复原证据

**缺模态工业检测是否空白？** 否。CMDIAD、RADAR、MISDD-MM 和 2025 modality-resilient IAD 都已经研究 RGB/3D 缺失、distillation/prompt 和动态模态可用性。

**跨模态 hallucination/uncertainty 是否空白？** 否。HalluciDet 将 privileged RGB 信息用于 IR detection；ReCoFuse 做 restorative multimodal diffusion；UMFNet 在未对齐 RGB-T 中输出 pixel-wise uncertainty 并门控融合；HalluGen/sFRC 还覆盖 restoration hallucination 生成与检测。

**剩余问题：** 能否把“第二个原始模态支持某一复原细节”定义成可审计 certificate，并在证据冲突时 veto downstream inspection，而非继续优化重建或融合？这是比原题窄得多的决策研究；其风险是最终仍会被已有 cross-modal consistency 论文覆盖。

## T：时间不确定性

**异步对齐 + uncertainty + risk coverage 是否已经组合？** 基本是。2026 UAMF-Net 已在金融多模态风险预警中联合 asynchronous alignment、modality reliability、predictive uncertainty、calibration 和 risk-coverage；安全监控工作也把 temporal multimodal uncertainty 用于预测。

**换成 RGB/NIR/ToF 是否足够？** 不足。只有实际 exposure/LED/ToF-return timestamp 可观测，且 offset posterior 会改变最终 selective decision，才不是简单移植。

**剩余问题：** Pi 级硬件是否能取得真实时序 ground truth？若不能，T 只能是模拟延迟实验，研究主张不成立。

## O：normality shift 与未知 defect

**shift-aware anomaly 和 conformal reject 是否已有？** 是。ICCV 2023、工业 stream failure/domain-shift、conformal industrial anomaly、unseen video anomaly uncertainty 都是直接近邻；三态 decision 与 conformal 的理论关系也早已有。

**三态标签是否自然存在？** 不自然。必须在采集时独立定义“正常但条件改变”和“真实 defect”，否则模型只能学习人为命名的 anomaly score。

**剩余问题：** 在 normal-only 训练、未见 shift、未见 defect 的同一现场协议中，三态 action 是否降低 false alarm、false pass 和人工成本？如果只用 MVTec 随机切分，O 退化为普通 anomaly detection，应放弃。

## 结论变化

1. 四个方向都不能再以宽泛关键词宣称首创。
2. P 仍是最合适的掌纹方向，但本质是“安全评测协议 + 风险校准假设”，不是新 backbone。
3. 原 R/T/O 均降级为条件候选：R 需要 certificate-veto，T 需要真实 timing，O 需要真实三态标签和 action cost。
4. 若老师要求“必须有方法创新且能在 FYP 内完成”，目前最诚实的选择是先做 P 的 novelty gate；若双轴数据不可取得，就不要继续包装掌纹 PAD。

## 下一轮必须回答的问题

- P：是否有公开或可合法自采的至少两个 capture device、至少三种 PAIS material，并能对同一 target 做 fixed-threshold IAPMR？
- R：已有 CMDIAD/RADAR/MISDD 的 loss、输入缺失方式和输出是否已经包含 evidence veto？需要全文逐段核对。
- T：实验室相机是否能输出 hardware timestamp，LED 控制是否有 GPIO trace，ToF 是否有 return validity/time-of-flight 字段？
- O：谁来标注 shift 与 defect 的边界，三态错误的成本如何获得，而不是事后任意设定？
