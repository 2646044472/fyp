# 阅读覆盖审计：读了多少，读到什么程度

最后更新：2026-08-21。目标不是制造“已读很多”的印象，而是如实说明本轮阅读的边界，并让下一轮能从最重要的缺口继续。

## 1. 当前覆盖

| 项目 | 数量 | 含义 |
| --- | ---: | --- |
| 文献图谱和近期图谱的带链接条目 | 59 | 覆盖 2023--2026 趋势、较早基础工作、标准、数据集目录与澳门资料；包含 `E1`--`E3`，不能一律等价看待。 |
| 证据账本条目 | 59 | 只收入会改变题目、协议、指标或范围的资料，并说明不可外推之处。 |
| 已查看关键章节的原始/官方资料 | 约 51 | Palm-ID 论文/MSU PalmDB、RegPalm/WebPalm code and data terms、Diff-Palm paper/code、MSU GenPalm terms、X-Palm paper/code/EULA、FedPalm paper/code、ICIP 2023 PAD record/artifact search、HiChrom-MAE ACM metadata/abstract、challenge-response formalism、2010 multispectral system、2018 PALMspoof、2020 smartphone liveness、2020 NIR/UV verification、2025 smart palm sensing、EMPalm、ASIS access-control survey、privacy-preserving physical access control、PalmMatchDB card、Tongji data page、PPNet code/releases、EEPNet publication/artifact search、FFLNet VIS-NIR metadata/abstract/artifact search、Beyond Static Features metadata/abstract、SF2Net paper/code/license、IWBF 2026 flash/non-flash fingerprint paper/code、NIST SP 800-171r3 maintenance/physical-access original text、ONNX Runtime ARM/Pi docs、MPW-180 paper/repository、CAAP repository、sweet 与 CandyFV 的硬件/PAI/access records、BEST、2022 presentation attack、DAPANet/HFSRA 的 data/protocol（含 target-adaptation 与 cross-domain 区别）、Gao et al. 2026 formal survey 的 publication record + 可访问 v2、PVASD 2026 paper/repository/data terms、NIST OT/manufacturing and utility IdAM, ISO、澳门官方资料与 biometric authorization、MLPerf 规则、adaptive-biometric review 与 workplace-privacy study 等。部分为预印本。 |
| 已精读的综述 | 1 | Gao et al. 的正式版已核对书目信息（IEEE TSMC-S 2026）；实际逐段阅读的是 arXiv v2 的任务、security/privacy、cross-domain、lightweight、datasets 和 outlook。未把它误写成逐页取得 IEEE 最终 PDF。 |

“查看关键章节”不是从头到尾逐字阅读，也不意味着可复现论文；它足以判断研究问题和评测边界。每项技术声称仍需回到相应原文和代码/数据许可复核。

## 2. 已解决的研究问题

| 问题 | 当前证据状态 | 当前答案 |
| --- | --- | --- |
| 单帧 RGB + edge 是否本身新颖 | 足够 | 否。已有完整 mobile pipeline；必须测量 Pi 约束而非移植数字。 |
| RGB/NIR/深度/掌静脉 fusion 是否本身新颖 | 足够 | 否。已有多模态传感器与 fusion 网络。 |
| palmprint PAD 是否是空白 | 足够 | 否。已有 display/paper、跨域 anti-spoofing、对抗贴片与近期 PAD 工作。 |
| 低成本多传感主动短序列是否在本设备有效 | 未解决，需实验 | 这是可测试候选，不可由已有论文替代。 |
| 随机短序列或跨帧差异是否比静态多谱新/有效 | 技术新颖性足够否定，效果未解决 | 2010 已有低成本静态多谱和纸张 liveness 线索；2020 Stanuch 已有掌部随机 NIR/UV 顺序与跨帧差异检查。M 只剩下 actual-state-verified response relation 相对 B2 的条件性假设，必须在未见 PAIS/session 中实测。 |
| 双光照同步采集或纸张/屏幕纹理 PAD 是否新 | 足够否定 | 否。2020 已有 NIR+UV verification、随机顺序与差异检查，也有 smartphone print/display liveness；关键是跨设备/材料留出和 M 相对 B2 的增益。 |
| ToF 距离对齐/引导采集是否本身新颖 | 足够否定 | 否。2022 已做 dual-camera + 单点 ToF 对齐，2025 已做 distance/rotation/video sensing；只剩下本硬件真实端到端 trade-off 能构成测量问题。 |
| 澳门是否没有掌纹 | 足够否定 | 不能这样说；有局部、较新的掌纹/掌静脉支付部署。 |
| 澳门受控现场是否有明确付费痛点 | 未解决，需访谈 | 目前只是合理场景假设。 |
| 凭证与实际到场者不一致是否可作为全球动机 | 有限支持，澳门未解决 | ASIS 的非代表性设施调查记录 credential sharing，但更多报告尾随/撑门；只支持单人核验点的假设，必须用本地流程验证。 |
| Pi 上端侧方案是否实际可用 | 未解决，需设备测量 | 不能用模型推理时间代替端到端交互或能耗；已预先写下测量 protocol。 |
| edge 是否自动保障 biometric privacy | 足够否定 | 否。local inference 只缩小网络/集中留存数据流；template protection 与 EM 侧信道属于不同问题。 |
| 本项目是否能称 non-transferable / privacy-preserving credential | 足够否定 | 否。真正的 biometric-bound credential 需独立的密码学机制；本项目只测受限场景的 credential-person binding。 |
| RGB baseline 是否需跨域压力测试 | 已有可用候选，尚未实际运行 | X-Palm 的 identity-disjoint scanner/mobile protocol 比同 session 随机切分更有说服力，但不回答本设备 ToF/NIR/PAD。 |
| 能否立刻跑通一个许可明确的公开 B0 输入 | 可行，但只限工程 smoke test | PalmMatchDB 可直接下载且许可明确；其公开 card 缺正式切分/条件 metadata，不能拿来写泛化或 PAD 结果。 |
| Tongji/PPNet 能否直接构成当前 Pi demo | 暂不可以，但可分别作为 P 层 protocol 和 score-script 参照 | Tongji 有两 session/filename/download 边界但未见明确 license；PPNet code 可读/有 CPU path，却缺发布权重、现代 ARM runtime 和端到端测量。须先核对条款/工件并实测自己的 Pi。 |
| EEPNet 或 ONNX Runtime 能否直接解决 Pi B0 | 足够否定 | EEPNet 是轻量论文但本轮未找到公开 code/weight/export/licence/Pi benchmark；ONNX Runtime 有 Arm CPU/Pi 官方路线，却取决于具体 arch、OS、Python、wheel、算子与合法 frozen model。它们只能组成 runtime gate，不能替代本机实测。 |
| VIS-NIR matching 能否当作 RGB/NIR PAD 或 freshness 依据 | 足够否定 | FFLNet 的问题是跨光谱 identity matching，而非 PAIS 分类或随机 response verification；即使 B2 提高 cross-spectral recognition，也必须另测 attack IAPMR 和 actual illumination/frame relation。 |
| 是否已有可立即下载、可复现的 palmprint 屏幕 PAD benchmark | 尚未确认 | XJTU-PalmReplay 有明确五域 protocol，但本轮未找到官方下载、许可或代码入口。它只能约束我们的切分；纸张/贴片/主动 RGB-NIR 的 S 层数据仍需经同意自采或另获许可。 |
| ICIP 2023 的 large-scale palm attack dataset 是否可用 | 暂不可以 | 官方摘要只确认存在并做 unseen-domain study；未找到 author/institution dataset page、license、download、code、weights 或 split。它不能作为 P0/P/S 输入或数值比较，只能支持“跨域 PAD 已有先例”。 |
| MPW-180 能否作为公开 mobile B0 benchmark | 暂不可以 | 论文、IAPR 目录和 GitHub 互相指向，但 GitHub 的 DOI/link/代码/数据均缺，Aperta 无可核验 record。它是高质量自采 protocol 参考，不是当前可复现输入。 |
| CAAP 能否作为当前可运行的高级 PAIS benchmark | 暂不可以，也不应作为最小 demo 范围 | 源码为 MIT，但需作者绝对路径数据、仓库外 classifier checkpoint 与 CUDA Linux；它是白盒 GPU research 工件，且任何攻击复现还需独立伦理/安全批准。 |
| Palm-ID/MSU PalmDB 能否作为明天可复跑的 B0 | 暂不可以 | 数据要协议申请，所见官方资料没有对应源码/模型链接；它适合设定 B0 的 protocol 上限，不能把论文的 mobile/server 数字或实现直接搬到 Pi。 |
| RegPalm/WebPalm 能否作为 B0 或 `FAR=1e-9` 依据 | 足够否定 | 数据/代码入口存在，但 WebPalm 每 identity 一图、仅经申请使用、来源权利由使用者承担，且代码无 weights/环境 lock、训练硬编码 CUDA；它是 low-FAR impostor-bank 参照，不是本项目的 session `1:1` 或 Pi benchmark。 |
| Diff-Palm/GenPalm 能否解决本项目的小样本、隐私或传感问题 | 足够否定 | Diff-Palm 的 RGB generator 仍训练于 48,000 张互联网图、用 4 V100，公开 code 缺原训练资料和完整评测；GenPalm 是须签 agreement 申请的合成集。两者没有本设备 NIR/ToF、session、PAIS 或 Pi 证据，只能是日后独立的离线增广 arm。 |
| X-Palm 能否作为可立即运行的 Pi/B2/M benchmark | 足够否定，但可申请为 P 层 B0 压力测试 | 数据、EULA、condition metadata、fixed split 与 code 边界完整，仍需批准下载；作者训练环境是 CUDA/RTX A6000，且数据没有 PAIS/ToF/synchronized challenge。它回答 RGB cross-domain，不回答本设备的传感、主动 gate 或 edge trade-off。 |
| FedPalm 是否让项目可称 privacy-preserving / federated edge | 足够否定 | 其 scope 是 GPU multi-client training；公开 repo 无 data/weights/license，且未见 secure aggregation、DP、update leakage/poisoning 或 transport/client-security implementation。FL 减少 raw training-data flow，不保证 template、model update 或现场认证安全。 |
| M 的随机光序列、两帧差异是否自动代表 challenge-response | 足够否定 | 不代表，且两者都有 2020 掌部近邻先例。没有预定义、actual-state-verified 的 challenge-response relation，它只是动态/多帧采集；即使实现 relation，也尚未对实时 display、真人贴片或 relay 证明安全。 |
| 文献中的 "dynamic" / "sequence" 能否直接证明设备时序或 active capture 新颖 | 足够否定 | Beyond Static Features 的 dynamic 是特征空间配对生成；SF2Net 的 sequence 是单帧内部空间 token。两者均不是相机连续帧或对命令作出可验证响应的证据，不能支持 M 的 physical freshness 表述。 |
| 配对主动 illumination 是否可直接写成掌纹创新或 Pi PAD 证据 | 足够否定 | 2026 IWBF 已有 flash/non-flash contactless fingerprint 近邻；它不是掌纹，数据私有，且没有 Pi/随机 challenge/response relation/IAPMR 证据。它使 capture/quality 对照更具体，却不能替代本项目实测。 |
| PVASD 是否可作为本项目当前的 NIR/Pi/掌纹 PAD benchmark | 足够否定，但可作静脉 PAD 阅读参照 | 它是 2026 的 palm-vein 大规模 PA 数据与 code artifact，公开下载仍受 academic/non-commercial rules 与超大规模约束；其 recipe 锁 CUDA 12.1，任务是 PAD 二分类/ACER，不含 palmprint `1:1`、IAPMR、RGB/NIR/ToF actual state 或 Pi capture-to-decision。不可直接迁移其数字或作为 P0/P/S。 |
| 限时维护访问是否足以证明澳门市场、掌纹必要性或离线放行 | 足够否定 | NIST r3/1800-2b 只支持临时维护授权与 local authorization 的参考模式；它们不是澳门数据，也不指定 biometric。目标现场仍需确认授权/撤销责任、弱网规则、例外成本和可接受 fallback。 |
| 近期 cross-domain PAD 数字是否可直接说明本项目对未知攻击有效 | 足够否定 | DAPANet 的 target adaptation 可见未标注目标域，HFSRA 是 RGB display-capture 分类 protocol；均不等于我们的 blind PAIS/session holdout 或 target-match IAPMR。 |
| 受控维护的“工单 + 本地执行”是否只是空想 | 有具体系统先例，本地价值未解决 | NIST SP 1800-2b 的能源 scenario 用中央授权、时限工单和预置 PACS 在通信故障下继续工作；它证明 architecture pattern，不证明澳门/学校/其他机房的网络或经济需求，更不要求 palm。 |
| 受控现场是否愿意采用 biometric | 未解决，需访谈 | 不能由“更安全/方便”推断；目的限制、可见性、问责感、资料泄露担忧与公平 fallback 都是应收集的条件。 |

## 3. 仍需优先精读/核对

1. **HiChrom-MAE 全文与补充材料。** 已核对 ACM metadata/abstract（七 domain、frequency/chromaticity 表征），仍需确认数据、PAIS、protocol、资源和是否真正重叠。
2. **只在老师选择 synthetic augmentation 时才升级合成数据审计。** Diff-Palm/GenPalm 的论文、代码/申请边界和不适用范围已核验；仍需在获批后取得实际 artifact、准确 licence/协议和冻结 generator version，才可能运行。
3. **RegPalm 正文与实际下载 metadata。** 当前已核验 dataset/code 边界；如未来需要比较其数值，仍须拿到正文 split、预训练权重和获批数据，而不是只依赖 README。
4. **template protection 的原始 security analysis。** 只有在放弃 PAD、转向可撤销模板时才升级为主读。
5. **实验室实际 hardware manual/driver。** 这是最优先的非文献资料：NIR 是否原始可控、IR-cut、ToF 精度、同步、帧率和耗电将决定研究能否成立。

## 4. 本轮的研究纪律

- 预印本用于提出实验，不作生产性能或安全保证。
- 澳门供应商发布用于证实一个部署先例，不推断市场规模。
- 标准/NIST 文本用于定义指标范围，不声明获得认证。
- 论文中的准确率、延迟和攻击成功率只在其设备、数据和阈值中成立。
- 对本项目最重要的未知量，通过设备测量、预冻结的 protocol 和访谈收集，而不是继续用搜索结果填充。
