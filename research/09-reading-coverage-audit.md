# 阅读覆盖审计：读了多少，读到什么程度

最后更新：2026-08-21。目标不是制造“已读很多”的印象，而是如实说明本轮阅读的边界，并让下一轮能从最重要的缺口继续。

## 1. 当前覆盖

| 项目 | 数量 | 含义 |
| --- | ---: | --- |
| 文献图谱和近期图谱的带链接条目 | 47 | 覆盖 2023--2026 趋势、较早基础工作、标准、数据集目录与澳门资料；包含 `E1`--`E3`，不能一律等价看待。 |
| 证据账本条目 | 38 | 只收入会改变题目、协议、指标或范围的资料，并说明不可外推之处。 |
| 已查看关键章节的原始/官方资料 | 约 28 | Palm-ID、2010 multispectral system、2020 smartphone liveness、2020 NIR/UV verification、2025 smart palm sensing、EMPalm、ASIS access-control survey、privacy-preserving physical access control、PalmMatchDB card、sweet、CAAP、BEST、2022 presentation attack、DAPANet/HFSRA 的数据与跨域 protocol、X-Palm、FedPalm、GenPalm、NIST、ISO、澳门官方资料与 biometric authorization、MLPerf 规则、adaptive-biometric review 与 workplace-privacy study 等。部分为预印本。 |
| 已精读的综述 | 1 | 2025 palmprint DL survey 的任务、security/privacy、cross-domain 和 outlook 章节；其版本状态在正式论文中需再核。 |

“查看关键章节”不是从头到尾逐字阅读，也不意味着可复现论文；它足以判断研究问题和评测边界。每项技术声称仍需回到相应原文和代码/数据许可复核。

## 2. 已解决的研究问题

| 问题 | 当前证据状态 | 当前答案 |
| --- | --- | --- |
| 单帧 RGB + edge 是否本身新颖 | 足够 | 否。已有完整 mobile pipeline；必须测量 Pi 约束而非移植数字。 |
| RGB/NIR/深度/掌静脉 fusion 是否本身新颖 | 足够 | 否。已有多模态传感器与 fusion 网络。 |
| palmprint PAD 是否是空白 | 足够 | 否。已有 display/paper、跨域 anti-spoofing、对抗贴片与近期 PAD 工作。 |
| 低成本多传感主动短序列是否在本设备有效 | 未解决，需实验 | 这是可测试候选，不可由已有论文替代。 |
| 随机短序列是否比静态多谱新/有效 | 技术新颖性未成立，效果未解决 | 2010 已有低成本静态多谱和纸张 liveness 线索；M 仅是相对 B2 的条件性假设，必须在未见 PAIS/session 中实测。 |
| 双光照同步采集或纸张/屏幕纹理 PAD 是否新 | 足够否定 | 否。2020 已有 NIR+UV simultaneous verification，也有 smartphone print/display liveness；关键是跨设备/材料留出和 M 相对 B2 的增益。 |
| ToF 距离对齐/引导采集是否本身新颖 | 足够否定 | 否。2022 已做 dual-camera + 单点 ToF 对齐，2025 已做 distance/rotation/video sensing；只剩下本硬件真实端到端 trade-off 能构成测量问题。 |
| 澳门是否没有掌纹 | 足够否定 | 不能这样说；有局部、较新的掌纹/掌静脉支付部署。 |
| 澳门受控现场是否有明确付费痛点 | 未解决，需访谈 | 目前只是合理场景假设。 |
| 凭证与实际到场者不一致是否可作为全球动机 | 有限支持，澳门未解决 | ASIS 的非代表性设施调查记录 credential sharing，但更多报告尾随/撑门；只支持单人核验点的假设，必须用本地流程验证。 |
| Pi 上端侧方案是否实际可用 | 未解决，需设备测量 | 不能用模型推理时间代替端到端交互或能耗；已预先写下测量 protocol。 |
| edge 是否自动保障 biometric privacy | 足够否定 | 否。local inference 只缩小网络/集中留存数据流；template protection 与 EM 侧信道属于不同问题。 |
| 本项目是否能称 non-transferable / privacy-preserving credential | 足够否定 | 否。真正的 biometric-bound credential 需独立的密码学机制；本项目只测受限场景的 credential-person binding。 |
| RGB baseline 是否需跨域压力测试 | 已有可用候选，尚未实际运行 | X-Palm 的 identity-disjoint scanner/mobile protocol 比同 session 随机切分更有说服力，但不回答本设备 ToF/NIR/PAD。 |
| 能否立刻跑通一个许可明确的公开 B0 输入 | 可行，但只限工程 smoke test | PalmMatchDB 可直接下载且许可明确；其公开 card 缺正式切分/条件 metadata，不能拿来写泛化或 PAD 结果。 |
| 是否已有可立即下载、可复现的 palmprint 屏幕 PAD benchmark | 尚未确认 | XJTU-PalmReplay 有明确五域 protocol，但本轮未找到官方下载、许可或代码入口。它只能约束我们的切分；纸张/贴片/主动 RGB-NIR 的 S 层数据仍需经同意自采或另获许可。 |
| 受控现场是否愿意采用 biometric | 未解决，需访谈 | 不能由“更安全/方便”推断；目的限制、可见性、问责感、资料泄露担忧与公平 fallback 都是应收集的条件。 |

## 3. 仍需优先精读/核对

1. **HiChrom-MAE 全文与补充材料。** 目前只有书目信息；需确认数据、PAIS、protocol、资源和是否真正重叠。
2. **Diff-Palm 与 GenPalm 的代码、数据 licence 和 training details。** 只在决定用合成数据时才投入时间；当前不是主线。
3. **RegPalm/WebPalm 的数据与低 FAR protocol。** 用来确定开集、低 FAR 的表述边界，避免不必要地复刻大规模任务。
4. **template protection 的原始 security analysis。** 只有在放弃 PAD、转向可撤销模板时才升级为主读。
5. **实验室实际 hardware manual/driver。** 这是最优先的非文献资料：NIR 是否原始可控、IR-cut、ToF 精度、同步、帧率和耗电将决定研究能否成立。

## 4. 本轮的研究纪律

- 预印本用于提出实验，不作生产性能或安全保证。
- 澳门供应商发布用于证实一个部署先例，不推断市场规模。
- 标准/NIST 文本用于定义指标范围，不声明获得认证。
- 论文中的准确率、延迟和攻击成功率只在其设备、数据和阈值中成立。
- 对本项目最重要的未知量，通过设备测量、预冻结的 protocol 和访谈收集，而不是继续用搜索结果填充。
