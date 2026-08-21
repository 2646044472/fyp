# 证据账本：读到的事实如何改变项目

最后更新：2026-08-21。本文件故意不追求“引用越多越好”。它只记录足以改变 FYP 设计、测量或论述边界的证据。每个条目分开写出作者研究了什么、我们能合理借用什么、以及不能外推什么。

## 1. 阅读与证据规则

`E1` 表示已经查看原始全文的相关方法、实验或标准正文/官方页面；`E2` 表示只核对摘要、索引或二手描述；`E3` 表示预印本、供应商资料或研究推断。`E1` 不表示该论文结论在我们的设备上已成立，只表示可以准确复述其限定条件。

| ID | 来源与阅读位置 | 可复述的事实 | 不可外推的部分 | 本项目动作 | 证据 |
| --- | --- | --- | --- | --- | --- |
| E-01 | [Palm-ID (2024)](https://arxiv.org/abs/2401.08111)，方法、数据、效率、失败分析 | 系统将 9 个手掌边界关键点用于 ROI；ROI 输入为 224x224；融合 ViT 与 ResNet50；压缩后模板为 516 bytes。论文保留测试数据集，报告 time-separated 数据性能下降，并以 embedding norm 做质量分数。 | 其 76.04M 参数模型和 18ms template extraction / 0.33ms 1:10k comparison 是作者的系统配置，不能外推到 Raspberry Pi；它并未验证 RGB/NIR/ToF 的 PAD。 | 把 ROI failure、质量拒绝和 session 留出作为 B0 必测项；Pi 必须实测 latency/RAM。 | `E1`，预印本 |
| E-02 | [sweet (2024)](https://arxiv.org/abs/2404.09376)，硬件、采集、限制、实验 | 该平台明确区分 RGB 表面纹理与 NIR 浅层血管信息；使用 850/950 nm、RGB、双 NIR 相机和 3D/光度立体处理。它的装置约 21 cm 立方，使用 120 位受试者的数据，并承认其主要结果是 finger-vein，不是 palmprint PAD。 | 多模态采集可行不等于多模态对我们攻击材料有效；其 Jetson、多相机、可编程照明不是 Pi 原型的资源上限。 | 先建硬件测量表：波长、IR-cut、曝光、同步、距离方差、环境光。未满足时不做 fusion 结论。 | `E1`，预印本 |
| E-03 | [CAAP (2026)](https://arxiv.org/abs/2604.06987)，威胁模型、方法、物理实验、消融 | 该工作研究可复用、capture-aware 的掌纹对抗贴片；训练时假设可访问受害模型的架构、logits 和梯度，另测跨模型/跨数据集迁移，并进行 print-and-capture。 | 这是白盒、预印本且以其 ROI/相机流程得到的攻击结果；不能把其 ASR 说成我们 Pi 的风险概率，也不能把它当成普通用户威胁。 | 将其作为 Gate 1 的上界/高级威胁参考；先做普通打印、屏幕重放与非对抗性贴片。只有获得批准才尝试其代码。 | `E1`，预印本 |
| E-04 | [ISO/IEC 30107-3:2023](https://www.iso.org/standard/79520.html)，范围说明 | 标准规定 PAD 的性能评估、测试结果报告和已知攻击分类；它只覆盖采集设备处的 presentation attack，明确不覆盖总体系统安全。 | 不能用 ISO 名称暗示整个门锁、网络、模板数据库或 OS 已安全。 | 所有 PAD 图表按攻击材料/PAIS 报告，并把数字注入、模板盗取排除在本实验安全结论之外。 | `E1`，标准官方页 |
| E-05 | [NIST SOFA biometrics draft](https://pages.nist.gov/SOFA/SOFA.html)，认证流程与 PAD 测量章节 | 对 1:1 authentication，匹配阶段的 FMR/FNMR 与 PAD 均是强度因素；APCER 是 PAD 层的攻击误放行，IAPMR 是攻击绕过 PAD 后又匹配目标模板的系统级失败。未知 PAIS 与代表性采集条件会影响测试可信度。 | 这是 draft framework，不是本项目可取得“认证强度”的依据；样本量很小的 FYP 不能得出精确低 error-rate。 | 固定 B0 的 verification threshold，再测 IAPMR；按材料与 session 留出；加清楚的置信区间/样本数说明。 | `E1`，NIST 草案 |
| E-06 | [UAA, ICCV 2025](https://openaccess.thecvf.com/content/ICCV2025/papers/Jin_Unified_Adversarial_Augmentation_for_Improving_Palmprint_Recognition_ICCV_2025_paper.pdf)，摘要、补充实验 | 近期高水平工作把几何变形和纹理退化都视为 palmprint recognition 的核心鲁棒性问题，而非前处理噪声。 | 训练该大型增强方法不一定适合小数据或 Pi，也不能证明它提供 liveness。 | capture protocol 要系统改变距离、姿态、照度与 session；多传感 gate 需同时报告真人误拒。 | `E1`，同行评审 |
| E-07 | [Diff-Palm, CVPR 2025](https://doi.org/10.1109/CVPR52734.2025.02455)，摘要与实验表 | 可控 diffusion 正在解决“身份一致性与类内变化”的合成掌纹数据问题，说明合成数据已是主流研究方向。 | 其合成识别数据不等于真实的 NIR、ToF、攻击材料或长期模板风险；结果仅在作者协议中成立。 | 不将“生成更多掌纹数据”作为核心创新；若使用，只作为离线 augmentation 对照且与真实攻击集分开。 | `E1`，同行评审 |
| E-08 | [HDC-Net (2026)](https://doi.org/10.3390/sym18071155)，方法、数据表、实验页 | 近期工作已用异构双支路、对比学习与 cross-modal attention 融合 contactless palmprint 和 palm vein，并在 Tongji、CASIA-MS、SCAU-PM 等数据上测试。 | 该融合网络的准确率或参数量不代表低成本 RGB/NIR 模组，也没有处理主动随机光序列、ToF 或物理 PAD。 | 明确排除“RGB/NIR fusion 本身”作为创新。若做 B2，仅用轻量 score/quality fusion 做受限对照。 | `E1`，同行评审 |
| E-09 | [HiChrom-MAE, ICMR 2026](https://dblp.org/rec/conf/mir/XiongHCLF26) | 2026 已有标题明确针对 palmprint PAD 的会议论文。 | 尚未获得全文，不能描述数据、攻击材料、结果或新颖点。 | 仅用来否定“第一个 palmprint PAD”措辞；列入待全文精读，不能作技术结论。 | `E2` |
| E-10 | [微信掌纹支付澳门上线公告](https://www.tencent.net.cn/weixin-palm-pay-achieves-first-application-outside-the-chinese-mainland-with-launch-in-macao/) | 2024 年微信掌纹支付在澳门银河上线，公告称首期覆盖 60 多个零售点，采用掌纹与掌静脉。 | 这是供应商发布，不能给出覆盖率、采用率、用户满意度、经济回报或全澳门部署情况。 | 不以“澳门没有掌纹”写故事；若本地化，只把它作为“有局部先例、非普遍体验”的背景。 | `E3`，供应商一手发布 |
| E-11 | [IEEE Biometrics Council contactless database index](https://ieee-biometrics.org/resources/biometric-databases/contactless-palmprint/) 与 [IAPR TC4 dataset index](https://iapr-tc4.org/palmprint-datasets/)，条目与数据说明 | PolyU-IITD v3 是 600+ subject、12,000+ 图像的两 session contactless 数据；IITD v2 是 230 subject 的单 session 数据；Tongji 也有两 session、12,000 图像。 | 这些公开数据不是本实验室相机，也没有 RGB/NIR/ToF 同步或攻击材料；不能验证我们的传感器、边缘性能或 PAD。 | 用两 session 数据验证 B0 的 protocol、ROI 和 threshold；不把它混入传感/PAD 的最终结论。 | `E1`，专业机构目录 |
| E-12 | [Presentation Attacks in Palmprint Recognition Systems (2022)](https://www.jmis.org/archive/view_article_pubreader?pid=jmis-9-2-103)，摘要、方法、实验与结论 | 该工作把泄露的掌纹图经 monitor 或 paper 重新拍摄，显示原始图泄露型攻击可能保持较高成功率；屏幕再拍会有 moire，纸张清晰度/弯曲会改变攻击表现。 | 其 iPhone XS、屏幕、打印机、ROI、识别器和测试数据不代表我们的装置；其 reported accuracy 不能当成 IAPMR。 | Gate 1 要记录 display/printer、距离、角度、照度与相机，按材料留出，并以固定 matcher threshold 直接计算 IAPMR。 | `E1`，同行评审 |
| E-13 | [DAPANet (Displays 2025)](https://doi.org/10.1016/j.displa.2024.102871)，摘要、方法/协议说明 | 此工作以 XJTU-PalmReplay 的五种 display-capture domain 做多源到多目标 palmprint anti-spoofing；问题已从随机切分转向未知 domain。 | 作者的 domain、手机与 RGB feature 不代表我们的 ToF/NIR；没有给我们的硬件带来已验证 liveness 结论。 | 测试集必须留出至少一个攻击材料/显示-相机条件；不以 pooled accuracy 作为主结果。 | `E1`，同行评审 |
| E-14 | [HFSRA (IET Image Processing 2025)](https://doi.org/10.1049/ipr2.70029)，数据/协议段落 | XJTU-PalmReplay 有五种 display-capture 条件；其 cross-domain protocol 将训练/验证与未见 domain test 分离。作者针对平面掌纹的 RGB acquisition 认为 depth 的直接判别力有限。 | 这不是“depth 无用”的普适结论，未覆盖我们真实手+贴片、ToF 精度和主动序列；也不能拿其 data volume 比较小型 FYP。 | ToF 的角色首先设为几何/质量控制，只有在未见 PAIS 测试提升时才称为抗攻击信号。 | `E1`，同行评审 |
| E-15 | [BEST (Pattern Recognition 2023)](https://web.comp.polyu.edu.hk/csajaykr/myhome/papers/PR2023.pdf)，全文的成像变化、cross-sensor protocol 与结果表 | Contactless capture 带来 6-DoF、环境光和局部 ROI 不对应问题；作者将 cross-database/cross-sensor 单独评估。其 MPD cross-sensor protocol 是两 session、手机采集的 16,000 张图/200 subject，并在 `FAR=1e-4` 下报告 GAR，说明低 FAR 与跨传感是独立压力测试。 | 该工作优化的是其 match framework，使用的相机/数据和量级不等于实验室设备；不能把其 GAR 或速度作为 Pi 指标。 | 自采必须至少 session 留出；若使用第二相机，再加 cross-camera holdout。题目只能说“受控几何下的稳定性”，不可说“解决跨设备泛化”。 | `E1`，同行评审 |
| E-16 | [澳门 GPDP 考勤身份核验生物资料豁免文件（英文译本）](https://www.dspdp.gov.mo/file/Service%20Applications/Exemption%20of%20notification/2.%20%E7%82%BA%E7%A2%BA%E8%AA%8D%E8%BA%AB%E4%BB%BD%E4%BD%9C%E8%80%83%E5%8B%A4%E7%94%A8%E9%80%94%E8%80%8C%E9%80%B2%E8%A1%8C%E6%B6%89%E5%8F%8A%E7%94%9F%E7%89%A9%E7%89%A9%E7%89%B9%E5%BE%B5%E8%B3%87%E6%96%99%E7%9A%84%E8%99%95%E7%90%86-ENG.pdf)，文件节选 | 文件提及考勤目的的生物识别资料处理、非生物替代方案，以及关系结束后 30 天内删除生物资料。 | 这是旧文件/非正式英文译本，不能作为现行法律意见、自动适用于非考勤场景，或替代部署前的法律审查。 | 学校 demo 默认有 card/PIN/manual fallback、明确删除期和最小日志；避免把日常考勤作为唯一故事。 | `E1`，官方文件，法律适用 `Q` |
| E-17 | [Anti-spoofing study on palm biometric features (ESWA 2023)](https://doi.org/10.1016/j.eswa.2023.119546)，摘要 | 作者提出同步双波长采集，并从 palmprint/palm-vein 图像提取静态特征和脉搏/SpO2 动态信号；它是“真正生理 liveness”的更高资源参照。 | 摘要没有证明现有 Pi 的 RGB/NIR 模组能稳定恢复脉搏或 SpO2；也不表示 2--3 帧光照随机序列具备同等活体强度。 | 当前项目只称短序列为主动 quality/risk gate；若转向 pulse/SpO2，需独立做帧率、曝光、时长、伦理和攻击评估。 | `E2`，同行评审摘要 |
| E-18 | [Deep Secure PalmNet (Computers & Security 2024)](https://doi.org/10.1016/j.cose.2024.103863) 与 [PalmSecMatch (Displays 2024)](https://doi.org/10.1016/j.displa.2024.102771)，摘要 | palmprint template protection 已有 cancelable/hashing 和 ciphertext-domain matching 的专门路线，处理 revocability、unlinkability、irreversibility 与性能的权衡。 | 作者的安全论证、密钥管理、数据和计算成本必须逐篇审计；local inference 本身不等于这些性质。 | 将 template protection 保留为替代论文路线；当前主线只落实加密存储、最小日志、删除期，不声称 cryptographic template protection。 | `E2`，同行评审摘要 |
| E-19 | [Deep Learning in Palmprint Recognition: A Comprehensive Survey (2025 preprint / 2026 journal listing)](https://www.qeios.com/read/YZ5TFY/pdf)，任务分类、security/privacy、cross-domain、outlook 章节 | 综述将 ROI、表征、open/cross-domain、跨光谱/多模态、轻量系统与安全/隐私放入同一研究版图。其 outlook 指出公开数据的规模、样本多样性及设备/照度/姿态/时间 metadata 不足，并把 spoofing、模板泄露、open/cross-domain 视为持续挑战。 | 综述的分类不能代替各原始论文的 protocol；版本/出版状态须在正式引用前核对。 | 保留 hardware/capture metadata、session/PAIS 留出，并以原始论文支撑关键技术结论。 | `E1`，综述全文，出版状态 `E2` |
| E-20 | [FedPalm (2025)](https://arxiv.org/abs/2503.04837)，benchmark、方法、deployment、实验章节 | FedPalm 区分 closed-set 与 open-set 的 federated palmprint verification，客户端可有个性化模型并参与全局模型训练；其实验使用公开数据和 ROC/EER。 | FL 不自动保证模板保护、抗模型反演或 Pi 可部署；该预印本的训练/通信规模远超单台离线终端。 | edge 主张严格限定为 local capture/inference；若未来做多点训练，另立 FL threat model、通信和隐私评测。 | `E1`，预印本 |
| E-21 | [HGAIQA (IEEE TIM 2024)](https://doi.org/10.1109/TIM.2024.3485454)，摘要/实验概述 | 真实场景中复杂背景、手姿差异会使 contactless palmprint quality assessment 成为问题；该工作使用整手几何、平坦度、亮度和清晰度，而非只看 ROI。在其 COEP 协议中，去掉最低 10% 质量图可降低 EER。 | 该质量筛选结果不能外推为我们应拒绝 10% 用户；丢弃低质量样本会损害可用性，模型也不是 Pi 上的 baseline。 | 报告 quality rejection、重采次数、BPCER 和身份表现；对 glove/污渍/遮挡/异常手姿做标记而不把它们偷偷从测试集中删除。 | `E1`，同行评审摘要 |
| E-22 | [MLPerf Tiny rules](https://github.com/mlcommons/tiny/blob/master/benchmark/MLPerfTiny_Rules.adoc) 与 [MLPerf Tiny 2026 measurement explainer](https://mlcommons.org/2026/07/mlperf-tiny-v1-4-results/)，规则和官方说明 | 可比的 edge benchmark 固定任务/质量目标，并将 accuracy、latency、energy 分开；须标识决定性能的硬件和软件栈；官方能耗结果使用校准测量。 | 这不是 palmprint benchmark，也不意味着 Pi 项目符合 MLPerf 或可同其他设备横比；其 microcontroller workload 不能代替真实 capture interaction。 | 在同版本/同质量下分开量 `T_model`、`T_pipeline`、`T_interaction`、idle 与输入端 batch energy；保存硬件/软件和 thermal 状态。 | `E1`，基准组织官方资料 |
| E-23 | [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html)，biometrics、PAD 与 usability sections | 该数字身份指南将 biometric comparison 视为有 FMR/FNMR 和主动冒充风险的概率性比较；强调 alternative non-biometric method、敏感资料保护、fixed threshold、PAD/endpoint integrity 与 usability/fallback。 | 这是美国网络身份认证指导，不是澳门实体门禁法规或本项目的合规认证；其特定 AAL 数字/因素要求不可直接套用到 Pi demo。 | 将 card/受控 QR claim + palm `1:1`、人工/card/PIN fallback、fixed threshold、retries 和数据最小化作为设计/访谈检查项，而不把 palm-only 或 local inference 写成全面保证。 | `E1`，NIST 官方指南 |
| E-24 | [BioSecure cost-sensitive fusion study (Pattern Recognition 2010)](https://doi.org/10.1016/j.patcog.2009.09.011) 与 [adaptive biometric systems review (ICT Express 2023)](https://doi.org/10.1016/j.icte.2023.04.003)，摘要 | quality-dependent/cost-sensitive multimodal fusion 早已将额外采集/处理的时间等成本纳入决策；综述把自适应采样/识别视为既有领域，同时指出移动或 wearable 场景仍需研究。 | face/fingerprint/iris 或一般自适应认证的结果不能证明 RGB/NIR/ToF 掌纹的策略有效；“尚需研究”不等于本项目第一个。 | 若做按不确定度升级 NIR 的策略，只作为 energy/latency 对照，冻结 escalation rule 后报告 escalation rate、IAPMR、BPCER 和 `T_interaction`；不单独宣传 adaptive fusion 新颖。 | `E1`，同行评审摘要/综述 |
| E-25 | [X-Palm 2026 paper](https://arxiv.org/abs/2606.08437) 与 [code/data README](https://github.com/X-Palm/X-Palm-2026)，数据卡、protocol、code 和结果摘要 | 预印本给出 6,006 图、103 人/206 手的 paired controlled-multispectral 与 unconstrained-smartphone 数据；手机端覆盖 80+ 型号、10+ 品牌，以及距离、姿态、flash、湿手、文字/遮挡等条件。其 code 定义 cross-dataset、closed/open-set cross-domain 及 leave-one-dataset-out protocol；在其设定下，scanner--smartphone 与 held-out X-Palm 都导致显著 EER 下降。 | 这是作者的预印本和受 EULA 限制的数据；其 112x112 ROI、RTX A6000 训练、相机和无 PAIS 任务都不能代表 Pi、ToF/NIR 或物理攻击。不能把其“first”复述为本项目主张。 | 若获许可，以其 smartphone domain 只测 B0 的 cross-domain/quality baseline；自采至少标记同类条件（近/远、姿态、湿/遮挡），但不借用其结果作为本设备性能。 | `E1`，预印本 + 开放 code/data 指引 |
| E-26 | [GRGIntech PRM-001 palm print/vein module](https://www.grgintech.com/product/prm-001-palm-print-and-vein-recognition-module/)，产品规格页 | 供应商公开宣称一个 ARM/NPU 模组已组合 RGB+IR camera、内置距离检测、QR、补光与 palm print/vein recognition，面向门禁/考勤等场景。 | 供应商给出的 FAR/FRR、抗伪造、速度、环境与适用性未见独立评测；它不证明市场采用或项目硬件完全相同。 | 不以 RGB/IR/distance/QR 一体化或“做掌纹锁”作为创新；与商用品的差别只能是透明可复现实验、明确 PAIS/边界与低成本硬件 trade-off。 | `E3`，供应商资料 |

## 2. 跨论文综合，而不是拼接结论

### 2.1 已有共识

1. ROI、采集质量、距离/姿态变化及 session shift 会影响无接触掌纹表现。Palm-ID、UAA 与近期 ROI 研究都把它们作为主要问题。`E1`
2. 多光谱/掌纹-掌静脉融合早已是研究主题；采集平台可做到多光源、多相机及 3D 控制。`E1`
3. 物理攻击评估必须按攻击材料与采集条件测试，单个二元分类 accuracy 不是最终门禁风险。`E1`
4. 多模态与边缘部署会增加同步、光学、对齐和资源成本，不能只报 accuracy。`E1`

### 2.2 仍是空白或只是假设

1. 本轮没有找到一个公开 benchmark 同时包含低成本 Pi 级 RGB/NIR/ToF、随机主动采集、掌纹 `1:1` 核验和未见物理攻击。这个观察是检索结果，不是“绝对不存在”的证明。`E3`
2. 低成本反射式 NIR 加 ToF 是否能识别打印、屏幕或贴片，必须取决于实际模块的光谱响应、几何和攻击制作，不能从血管识别或 RGB 融合论文推断。`Q`
3. 澳门哪个现场为此付费、离线是否为痛点、现有卡/QR/人工流程造成多少损失，现有资料没有证明。`Q`

## 3. 项目级研究问题与不可答问题

**可答：** 在我们写清楚的设备、受试者、攻击材料与 session 切分中，主动采集 gate 相对 RGB baseline 是否降低 IAPMR/APCER，且保持预先设定的 BPCER、ROI failure、p95 latency 和 memory 预算。

**不可答：** 掌纹是否在一般意义上“更安全”、系统是否足以证明某人的法律身份、澳门是否需要全面推广掌纹、或者 edge 是否天然保护模板隐私。

## 4. 下一批精读优先级

1. 获取 HiChrom-MAE 正文，补齐 PAIS、切分、PAD 指标与资源信息。
2. 深读 2024/2025 palmprint survey 的数据集与 evaluation 章节，建立可用公开 baseline/许可清单。
3. 读 cross-device/cross-sensor 原始论文的 protocol，避免把 cross-session 与 cross-device 混为一谈。
4. 拿到实验室硬件型号后，对照 sweet 的采集字段完成 Gate 0；这比新增一个网络更优先。
