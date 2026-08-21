# 文献地图：掌纹、边缘与安全

最后更新：2026-08-21。这里记录“读到了什么”和“它不能证明什么”，避免把不同数据集、设备和威胁模型的数字直接比较。

## A. 与 baseline 直接相关

| 文献 | 阅读深度 | 证据 | 核心内容 | 对本项目的影响 |
| --- | --- | --- | --- | --- |
| [Grosz, Godbole, Jain, Palm-ID, 2024](https://arxiv.org/abs/2401.08111) | 方法、数据、效率、失败分析 | `E1`，预印本 | 手机端完整 pipeline：ROI keypoints、增强、CNN + ViT、质量估计和紧凑 embedding；512-byte 模板在其协议中保持接近原表示的 TAR；部署于 Galaxy S22。 | v0 baseline 采用其问题分解与指标，而非声称新识别网络。Pi 的 latency 不可从其手机/服务器数字外推。 |
| [Liu et al., BEST, Pattern Recognition, 2023](https://doi.org/10.1016/j.patcog.2023.109422) | 摘要/方法定位 | `E2` | 做了 within-, cross-database 和 cross-sensor 的无接触掌纹评测。 | 证明跨传感器必须单独测；本项目不应只随机分割同一采集 session。 |
| [Amrouni & Benzaoui, 2024 survey](https://doi.org/10.3390/app14010153) | 摘要、数据集段落 | `E2` | 综述接触/无接触数据集、特征类别和评估问题；列出 PolyU-MS 等多光谱数据。 | 为公开 baseline 数据集筛选提供地图，最终仍需核对许可与 protocol。 |
| [Gao et al., DL Palmprint Survey, IEEE TSMC-S 2026](https://doi.org/10.1109/TSMC.2025.3649416) / [arXiv v2](https://arxiv.org/html/2501.01166) | 正式 metadata；v2 的任务、security/privacy、cross-domain、lightweight、datasets 与 outlook | `E1`，正式书目信息 + 可访问 preprint；最终 PDF 未逐页核对 | 将 ROI、open/cross-domain、跨光谱/多模态、轻量部署、数据与安全/隐私放入同一系统图；强调数据 metadata 和跨域泛化挑战。 | 支持把 capture/ROI、identity/session/PAIS holdout 与实测 Pi resource 作为系统证据；不从综述推出本设备 liveness、部署价值或任何性能数字。 |
| [Seyedmohammadi et al., X-Palm, 2026](https://github.com/X-Palm/X-Palm-2026) | 数据卡、split、code、results README | `E1`，预印本 | paired controlled-multispectral 与 unconstrained smartphone 的 6,006 图/103 人数据；code 已写出 closed/open cross-domain split。 | 是 B0 的高价值 domain-shift protocol 候选；数据签 EULA，且不包含 PAIS、ToF 或本相机。 |
| [Alausa et al., PalmMatchDB, ICPECA 2023](https://huggingface.co/datasets/aspmirlab/PalmMatchDB) | dataset card/API | `E1`，数据卡 | Apache-2.0、10,528 rows 的 on-device contactless corpus；公开 card 只见一个 `train` split。 | 可立即用于 B0 工程 smoke test；没有公开 session/identity/camera/PAIS metadata 时，不可用作正式性能或泛化协议。 |
| [Jia et al., EEPNet, PRL 2022](https://doi.org/10.1016/j.patrec.2022.05.015) | 出版 metadata/abstract；作者/题名/GitHub 工件检索 | `E2` | MobileNetV3-based lightweight palmprint route；摘要称在七个库比较 precision、speed、parameter count 与 FLOPs。未找到作者公开 code、weight、export、licence 或 Pi benchmark。 | “lightweight”不等于当前可部署。只作 architecture reading reference；B0 不依赖它，直到公开工件、数据条款和目标 Pi runtime 可被逐项核对。 |
| [Fei et al., FFLNet VIS-NIR, TIFS 2024](https://doi.org/10.1109/TIFS.2024.3441945) | 正式 metadata/abstract；artifact search | `E2` | 以 Fourier feature learning 缩小 VIS/NIR heterogeneous palmprint matching 的 modality gap；摘要称在三个 heterogeneous database 评估。未找到可核验 code、weight、data/license、export 或 Pi artifact。 | 跨光谱 recognition 是已有路线，和 PAD/freshness 是不同任务。B2/M 必须把 spectrum metadata、cross-spectral matching 与 PAIS/IAPMR 分开报告。 |
| [Yang et al., Beyond Static Features, IEEE SPL 2025](https://doi.org/10.1109/LSP.2025.3611328) | 正式 metadata；可访问摘要/索引描述 | `E2` | 可访问描述将其 "dynamic" 定义为在特征空间生成 class-aware pairs 并做匹配正则化，不是由传感器采集的连续掌纹帧。 | 不能把 M 写成首个 "dynamic palmprint"；更不能拿该方法支持 physical freshness 或 PAD。 |
| [Liu et al., SF2Net, TIFS 2025](https://doi.org/10.1109/TIFS.2025.3611692) / [official code](https://github.com/20201422/SF2Net) | 正式 metadata/abstract；README、requirements、inference 与 model code、license | `E1`，原始代码/正式书目信息 | 模型每次接收单张 `1x128x128` grayscale ROI；标题中的 sequence 指内部局部/空间 feature token 的融合，而非物理连续帧。MIT code 有 CPU fallback，但训练依赖 CUDA PyTorch；没有 release weight、dataset 或 edge benchmark。 | 是识别架构阅读参照，不是 B0 默认依赖，也不是主动光照 challenge、PAD 或 freshness 的先例。 |
| [Sahoo & Namboodiri, flash/non-flash fingerprint PAD, IWBF 2026](https://arxiv.org/abs/2603.17679) / [official code](https://github.com/clspooffnf/CLSpoofFNF) | 论文全文、私有数据/限制段、code/weight README | `E1`，IWBF 2026 camera-ready preprint + code；无公开 data/license | 手机连续 flash/non-flash 指纹 pair 用光度差异分析 print/display 样本；论文明确是 preliminary、私有小数据，且其限制含 pose/distance/temporal misalignment/high-fidelity 3D spoof。repo 有 notebooks 和一个 fingerprint-tuned ResNet weight，但要求自备数据、无显式 code license、GPU/MPS 推荐。 | 主动照明是已有 biometric sensing pattern，不是空白；它是掌纹 M 的 protocol/quality 近邻，不证明本设备、NIR、ToF、随机 challenge、掌纹 PAIS 或 Pi 效果。 |

## B. 多光谱、NIR 与测量

| 文献 | 阅读深度 | 证据 | 核心内容 | 对本项目的影响 |
| --- | --- | --- | --- | --- |
| [Aberni et al., Multispectral Palmprint Review, 2017](https://doi.org/10.1109/TSP.2017.8076097) | 摘要/全文片段 | `E2` | 多光谱掌纹中，NIR 可显现静脉等与可见光互补的信息。 | 不能声称 RGB+NIR fusion 新颖；新意必须在主动采集、安全与边缘测量。 |
| [Amrouni & Benzaoui, 2024](https://doi.org/10.3390/app14010153) | 数据集段落 | `E2` | PolyU-MS 为 250 位受试者、红绿蓝/NIR、多 session 的受控多光谱数据。 | 可作为光谱 baseline 候选，但其固定采集装置不等于真实 Pi 采集盒。 |
| [Zhang et al., online multispectral verification, IEEE TIM 2010](https://www4.comp.polyu.edu.hk/~cslzhang/paper/TIM_10_Feb.pdf) | 硬件、采集、anti-spoof、速度和结论全文 | `E1` | 低成本 visible/NIR 四谱系统用 470/525/660/880 nm LED、单色 CCD 和 controller 在 <1 s 采集；用纸张打印攻击，提出 Blue--NIR reflectance difference 为 liveness 线索。 | 固定多谱、低成本采集、纸张 anti-spoof 都不是新；M 必须相对静态 B2、未见 PAIS 与 Pi 成本证明随机 challenge 的额外价值。 |
| [GRGIntech PRM-001](https://www.grgintech.com/product/prm-001-palm-print-and-vein-recognition-module/) | 产品规格 | `E3` | 商用模组已公开组合 RGB+IR、距离、QR、补光与 palm print/vein。 | 不能将相同硬件组件/掌纹锁 demo 写成首创；产品性能声明需独立验证。 |

## C. 物理攻击与 PAD

| 文献 | 阅读深度 | 证据 | 核心内容 | 对本项目的影响 |
| --- | --- | --- | --- | --- |
| [Liu et al., CAAP, 2026](https://arxiv.org/abs/2604.06987) | 威胁模型、物理攻击、消融、结论 | `E1`，预印本 | 提出考虑打印和采集变化的可复用、十字形物理对抗贴片；在 Tongji、IITD、AISEC 和多个识别器上测白盒攻击、迁移与 print-and-capture。 | 最接近的攻击动机与高级攻击基线。先复现低风险物理攻击；不要直接套用其 ASR 或宣称 NIR 可防御。 |
| [Shaheed et al., PAD systematic review, 2024](https://doi.org/10.1016/j.engappai.2023.107569) | 摘要 | `E2` | 总结深度 PAD，强调跨攻击、材料、传感器的泛化困难。 | PAD 必须报告 APCER/BPCER 与未知攻击条件，不能只报 accuracy。 |
| [Li & Ramachandra, fingerprint PAD survey, 2023](https://arxiv.org/abs/2305.17522) | 摘要 | `E2`，预印本综述 | 总结接触、无接触、手机指纹 PAD 的攻击材料、数据和方法。 | 用来学习 PAD protocol，不用于把指纹数字外推到掌纹。 |
| [Xiong et al., HiChrom-MAE, ICMR 2026](https://doi.org/10.1145/3805622.3810599) | 正式 metadata/abstract | `E2` | 摘要称在七个 domain 上以 high-frequency residual 与 chromaticity alignment 做 cross-medium palmprint PAD；正文/工件仍待取得。 | “做一个 frequency/chromaticity PAD 分类器”本身也不新；需要在传感、协议、威胁模型或边缘测量上区分。 |
| [Geissbuhler et al., sweet, 2024](https://arxiv.org/abs/2404.09376) | 传感与限制段落 | `E1`，预印本 | 开放模块化无接触手部平台覆盖 multi-NIR、RGB、立体视觉和 photometric stereo；反射式 NIR 可无接触但信号较弱、环境敏感。 | 3D 盒子/RGB+NIR 的存在不是贡献；先确认本实验室 NIR 的光学质量与同步方式。 |
| [Garcia et al., challenge-response formalism, 2022](https://doi.org/10.1186/s13635-022-00131-y) | PAD、challenge-response 形式化段落 | `E1` | 把“是不是某人”与“是否为真实呈现”统一为阈值决策；challenge-response 给生物呈现加入 freshness。 | 主动短序列可以有明确安全动机，但并不自动证明某种掌纹 challenge 有效。 |
| [ISO/IEC 30107-3:2023](https://www.iso.org/standard/79520.html) | 范围与评测/报告要求 | `E1`，标准元数据 | 定义 PAD 性能评估和已知攻击分类，范围限于采集装置处的 presentation attack。 | 项目需把 sensor-level PAD 与模板库、通信、门锁控制等其他攻击面分开。 |
| [NIST SOFA biometrics draft](https://pages.nist.gov/SOFA/SOFA.html) | PAD 与 system-level 指标段落 | `E1`，草案 | 区分 PAD 的 APCER 与最终“攻击呈现被匹配为目标用户”的 IAPMR。 | 最终 demo 不能只报 PAD accuracy，要报告攻击是否真的获得通过。 |

## D. 隐私、模板与端侧部署

| 结论 | 依据 | 证据 | 对项目的意义 |
| --- | --- | --- | --- |
| 端侧无接触掌纹识别已经可实现，模板可被压缩，质量拒绝可提高使用可靠性。 | Palm-ID | `E1` | “edge” 不能只等于离线 inference；要报告端到端延迟、ROI、模板/日志和断网行为。 |
| 生物模板保护通常要求可撤销、不可关联、不可逆与性能同时成立。 | [Jain et al., template protection review](https://doi.org/10.1109/TIFS.2015.2481158) | `E2` | 这是强论文方向，但单个 FYP 同时做跨设备与安全证明风险高；保留为备选。 |

## E. 读文献后形成的空白，而非“领域从未做过”

| 观察 | 支持它的资料 | 必须避免的过度结论 |
| --- | --- | --- |
| 识别、跨传感器泛化、质量估计和移动部署已有大量工作。 | Palm-ID、BEST、两份综述 | 不能称“第一个移动/边缘掌纹识别”。 |
| 多光谱/NIR 掌纹已研究多年。 | 多光谱综述、PolyU 系统 | 不能称“第一个 RGB+NIR 掌纹”。 |
| 新近 CAAP 将物理可复用贴片带入掌纹识别威胁讨论。 | CAAP | 不能称“第一个掌纹贴片攻击”或假定在本设备上有效。 |
| 本轮没有找到一个公开标准数据集，同时覆盖低成本 RGB/NIR/ToF、主动短序列、掌纹身份核验和未知物理攻击。 | 检索结果，`E3` | 这只是待进一步系统检索和自采实验验证的 gap，不能写为绝对不存在。 |
| 2026 已有专门的掌纹 PAD 论文。 | HiChrom-MAE 书目信息，`E2` | 不能声称“第一个掌纹 PAD”；获得全文后需检查其传感器、数据和协议是否与本项目重叠。 |

## F. 澳门部署事实更新

| 资料 | 证据 | 可支持的说法 | 不可支持的说法 |
| --- | --- | --- | --- |
| [腾讯：微信掌纹支付在澳门银河上线，2024-09](https://www.tencent.net.cn/weixin-palm-pay-achieves-first-application-outside-the-chinese-mainland-with-launch-in-macao/) | `E1`，供应商一手发布 | 这是微信掌纹支付在中国内地以外的首个应用；其描述使用掌纹与掌静脉，服务澳门银河购物/支付。 | 不能从单一上线项目估计全澳门普及率、用户采用率、经济效果或系统架构细节。 |
| [澳门 GPDP：指纹/掌形考勤设备指引](https://www.dspdp.gov.mo/file/Guideline/%E4%BD%BF%E7%94%A8%E6%8C%87%E7%B4%8B%E6%8E%8C%E5%BD%A2%E8%80%83%E5%8B%A4%E8%A8%AD%E5%82%99%E7%9A%84%E5%95%8F%E9%A1%8C_TC.pdf) | `E1`，官方资料 | 澳门曾明确处理指纹/掌形考勤设备的个人资料问题。 | 掌形（hand geometry）不等于掌纹；不能把此指引当作掌纹门禁普及证据。 |

这个更新解释了“在澳门住了 18 年仍没遇到”的合理现象：不是完全不存在，而是公开能查到的掌纹支付部署较新且局部。下一步要问的不是“有没有”，而是“为什么没有成为一般商户/工作现场的默认交互”。
