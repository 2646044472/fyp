# 2023--2026 掌纹研究图谱：最近的人在做什么

最后更新：2026-08-21。范围是无接触掌纹、掌纹/掌静脉近邻问题及与本 FYP 有关的 PAD/边缘部署。不是系统性综述：本轮优先检索了同行评审期刊/会议、arXiv 和作者页面；未读全文的资料明确标为 `E2`，不拿其数字作为设计结论。

## 1. 一页结论

近三年的方向可以概括为六条：

1. **从受控数据集走向未知域。** 研究者正处理跨手机、跨传感器、跨光谱、未知目标数据集和标签噪声。
2. **从小型真实数据转向合成数据。** 2024--2025 出现多篇 diffusion 生成工作，目标是得到身份一致、类内变化真实的训练数据。
3. **从 closed-set accuracy 转向开放集和极低 FAR。** 大型身份库与 `TAR@FAR=1e-6` / `1e-9` 正成为更接近真实部署的压力测试。
4. **从集中训练转向隐私与联邦学习。** 目标是用跨客户端数据训练，同时不集中上传生物图像。
5. **从单纯识别转向鲁棒性和攻击。** 新工作处理几何/纹理退化、物理对抗贴片及专门的 palmprint PAD。
6. **从算法脱离采集到传感器协同。** 开放采集平台、RGB/NIR、立体/深度、ROI 交互控制不断出现，但多传感不等于自动更安全。

对本项目最重要的判断：主流已经在规模、生成、纯识别和通用 PAD 模型上竞争。FYP 的合理位置是第 5 和第 6 条的交集，即以现有低成本传感器研究**采集策略如何改变最终攻击放行、正常误拒与端侧资源的关系**。

## 2. 主题一：跨设备、跨域和不受控采集

| 工作 | 年份/来源 | 阅读 | 做的是什么 | 对 FYP 的含义 |
| --- | --- | --- | --- | --- |
| [Zhu et al., Self-Paced CycleGAN Across Smartphones](https://doi.org/10.1109/TIFS.2023.3301729) | TIFS 2023 | `E1` 摘要 | 用自注意力 CycleGAN 补齐跨手机缺失数据，并用 self-paced learning 应对设备域差。 | 不同相机/设备会显著改变问题；注册与验证跨设备时，不能只报告同设备随机切分。 |
| [Shao et al., PDFG for unseen-target CDPR](https://doi.org/10.1109/TIFS.2024.3371257) | TIFS 2024 | `E2` 摘要 | 在没有目标域样本时，以 Fourier 增广和特征损失学习适应未知数据集。 | 最终采集盒必须至少做跨 session；若有两种相机，应加跨设备测试。 |
| [SYEnet](https://doi.org/10.1016/j.ins.2024.120518) | Information Sciences 2024 | `E2` 摘要 | 轻量网络和专用 ROI 网络，面向姿态、低照度、背景和角度变化的无约束移动采集。 | ROI 与采集质量不是前处理细节，而是核心误差来源。 |
| [Shao et al., noisy-label selection/correction](https://doi.org/10.1109/TIP.2025.3588040) | TIP 2025 | `E1` 摘要 | 以自监督、Fourier 和 prototype 机制分阶段选择/修正噪声标签。 | 自采数据的身份标注、左右手、session metadata 要从一开始受控，否则模型结果难以解释。 |
| [RegPalm](https://doi.org/10.1109/TIFS.2025.3593352) / [WebPalm](https://zhongyy.github.io/WebPalm/) / [code](https://github.com/zhongyy/RegPalm) | TIFS 2025 | `E2` 论文摘要 + `E1` data/code audit | WebPalm 页面称有 83,145 张、83,145 个 identity 的互联网 contactless palm 图片，申请后用于 non-commercial research；RegPalm code 能计算 `FPR=1e-4` 至 `1e-9`，但仓库没有权重、license 或 dependency lock，训练过程硬编码 CUDA。 | 它说明超低 FAR 需要巨大的 impostor comparison bank，而非小样本“零误放行”；但每 identity 一图，不能代替 cross-session `1:1` bona fide/genuine 测试，也不代表 Pi、NIR/ToF 或 PAIS。FYP 只能报告实际比较次数/区间，不伪称 `FAR=1e-9`。 |
| [PalmBridge](https://arxiv.org/abs/2601.20351) | arXiv 2026 | `E2` 书目信息 | 2026 仍在研究 open-set palmprint verification 的特征对齐。 | 开放集/域适应仍是活跃缺口，但超出当前 demo 数据规模。 |
| [X-Palm](https://arxiv.org/abs/2606.08437) / [data and code](https://github.com/X-Palm/X-Palm-2026) | arXiv/code 2026 | `E1` 论文、data card、protocol、code audit | 6,006 图、103 位/206 手；受控 scanner 的六谱 enrollment 与 80+ 手机、远近、姿态、flash、湿手、文字/遮挡等 smartphone probe 配对。repo 有固定 seed 的 cross-dataset/closed-set/open-set split 和 12 个 baseline scripts；原图需签 non-commercial EULA，作者训练用 RTX A6000。 | 将 distance、surface condition 和 domain shift 视为正式压力变量；经批准后可作 B0 的 RGB cross-domain protocol，但不拿它证明 Pi、同步 RGB/NIR challenge、ToF 或 PAIS，也不把其训练环境当部署方案。 |
| [MPW-180 / PalmWildNet](https://doi.org/10.3390/app152111368) | Applied Sciences 2025 | `E1` 论文数据/伦理/availability + IAPR/GitHub 核验 | 论文描述 180 人、180 台手机、720 个自由手视频和 flash/ambient 条件；但 IAPR 指向的 GitHub 暂无数据 DOI、代码或下载，且显示 under review。 | 视频自由手/照明 protocol 很适合自采参考；在实际 archive/metadata 可获取前，不把它列为可运行的公开 B0 benchmark，也不引用其 5 ms 或识别数字作 Pi 依据。 |

**反思：** 把距离传感器只解释成“活体检测”太窄。更基础也更可信的贡献，是让设备主动控制几何，从而降低 ROI 和跨 session 变化；这与近期对未约束采集和 pattern variance 的关注一致。

## 3. 主题二：生成式数据与数据规模

| 工作 | 年份/来源 | 阅读 | 做的是什么 | 对 FYP 的含义 |
| --- | --- | --- | --- | --- |
| [GenPalm](https://arxiv.org/abs/2406.00287) | arXiv 2024 | `E1` 方法/数据/实验 | Stable Diffusion + ControlNet 生成身份与类内变化；用约 7,873 个真实身份训练，报告合成数据可改善跨库/时间分离测试。 | 公开数据少是现实瓶颈；合成数据适合 recognition 预训练，不可直接替代真实攻击或 NIR/ToF 数据。 |
| [Diff-Palm](https://openaccess.thecvf.com/content/CVPR2025/papers/Jin_Diff-Palm_Realistic_Palmprint_Generation_with_Polynomial_Creases_and_Intra-Class_Variation_CVPR_2025_paper.pdf) / [code](https://github.com/Ukuer/Diff-Palm) | CVPR 2025 | `E1` 全文 + artifact audit | 多项式掌纹线与可控 diffusion 处理“身份一致 vs 类内变化”；生成器训练用 48,000 张匿名互联网 RGB 图，识别测试在七个公开 RGB 数据集作 identity-disjoint open-set split。官方 Apache-2.0 code 有生成权重下载入口和 1,000-step diffusion script，但训练仍需自备真 ROI；作者训练用四张 V100 GPU。 | 合成 RGB 可作为未来的离线 pre-training/augmentation 对照，但不代表 Pi inference、NIR/ToF、跨 session 采集或物理 PAIS；不可把 synthetic identity 当作真实生物资料或隐私问题的解决方案。 |
| [Palmprint de-identification via diffusion](https://arxiv.org/abs/2504.08272) | arXiv 2025 | `E2` 书目信息 | 用 diffusion 做掌纹去标识化，服务数据共享/隐私。 | 与其承诺完整可撤销模板，不如在项目里先落实原始帧不出设备、最小日志和删除策略。 |
| [PD-GAN](https://doi.org/10.1109/TCE.2025.3620834) | TCE 2025 | `E2` 摘要 | 以 GAN 去除可识别掌纹信息，同时保留某些效用。 | 说明“发布掌纹数据”本身已经成为隐私研究主题；演示数据不能随意公开。 |

**反思：** 新工作正在把训练数据扩至几千或上万身份，通常使用 GPU 大规模训练。对于 Pi 项目，合理策略是采用已训练/公开 baseline，或只用合成数据做离线增广对照；不要把训练成本误写成 edge 部署能力。若以后启用合成数据，必须把它固定为一个独立的 offline training arm，并以真实、未参与生成器训练的 session/PAIS 测试；不让合成帧进入最终攻击或 edge 能耗结论。

## 4. 主题三：鲁棒表征与增强

| 工作 | 年份/来源 | 阅读 | 做的是什么 | 对 FYP 的含义 |
| --- | --- | --- | --- | --- |
| [UAA: Unified Adversarial Augmentation](https://openaccess.thecvf.com/content/ICCV2025/papers/Jin_Unified_Adversarial_Augmentation_for_Improving_Palmprint_Recognition_ICCV_2025_paper.pdf) | ICCV 2025 | `E1` 摘要/补充实验说明 | 将几何变形和纹理退化进行 identity-preserving adversarial augmentation，以改善挑战性数据上的识别。 | 拍摄距离、姿态、照度/反射都会造成真实退化；FYP 需先测这些退化，而不是假设 NIR 可以消除一切。 |
| [AMCOA ROI extraction](https://doi.org/10.1109/TIM.2025.3560751) | TIM 2025 | `E1` 摘要 | 以可控运动/障碍规避改进无接触 palm ROI 采集，使用 IR 与可见光协同。 | 近期工作仍把“怎样稳定取 ROI”作为研究问题，支持把 ToF 质量门控列为 baseline。 |
| [Single-source domain generalization for palm biometrics](https://doi.org/10.1016/j.patcog.2025.111629) | Pattern Recognition 2025 | `E2` 摘要 | 只用单一源域学习未见域鲁棒性，并讨论多源数据的隐私风险。 | 实验室若只能采一个小数据源，应该避免在同一背景/光照随机切分后声称 generalization。 |

**反思：** “反射、纹理和几何变化”是近年识别鲁棒性的正式研究方向，和 PAD 使用的是部分相同信号。因此识别质量 gate 与 PAD 不能各自独立训练后简单相乘，应该研究它们会否互相误伤，例如把低光真人误判为攻击。

## 5. 主题四：隐私、联邦与去中心化

| 工作 | 年份/来源 | 阅读 | 做的是什么 | 对 FYP 的含义 |
| --- | --- | --- | --- | --- |
| [Federated metric learning for palmprint](https://ieeexplore.ieee.org/document/10295483/) | 2023 | `E2` 书目信息 | 用联邦度量学习处理掌纹识别中的集中资料风险。 | “edge + 掌纹”已有隐私路线；若不做联邦，必须清楚限定为 local inference/data minimization，而不是泛称 privacy-preserving。 |
| [FedPalm](https://arxiv.org/abs/2503.04837) | arXiv 2025 | `E1` 摘要 | 给 closed- 和 open-set palm verification 建 FL benchmark，以个性化/共享 texture experts 处理客户端异质性。 | 可撤销模板 + 跨设备 + 联邦一起做会远超 FYP；本项目只记录模板生命周期和本地存储边界。 |
| [DPFed-Palm](https://doi.org/10.1109/TIP.2025.3590524) | TIP 2025 | `E2` 书目信息 | 动态个性化联邦学习处理 cross-spectral palmprint 的 non-IID 与资料隐私。 | RGB/NIR 多光谱还伴随 non-IID 训练问题；不要先承诺一套模型自然适配所有设备。 |

**反思：** 端侧推理不是完整隐私方案。它减少原始帧传输，却不自动给模板带来可撤销、不可关联或抗模型反演性质。论文中必须诚实地把“local-only raw capture”写成系统设计，而不是密码学证明。

## 6. 主题五：攻击、PAD 与系统安全

| 工作 | 年份/来源 | 阅读 | 做的是什么 | 对 FYP 的含义 |
| --- | --- | --- | --- | --- |
| [CAAP](https://arxiv.org/abs/2604.06987) / [official repository](https://github.com/ryliu68/CAAP) | arXiv 2026 | `E1` 论文范围 + 代码工件审计 | 针对深度掌纹模型的 capture-aware、可重用物理对抗贴片；代码公开，但默认脚本依赖作者机器上的绝对路径数据、未随仓库提供的 classifier checkpoint，以及 CUDA 12.4 Linux 环境。 | 它是高级白盒威胁的研究参照，不是 Pi 可跑 baseline 或本项目默认攻击；任何复现均须先获伦理批准、独立取得数据/权重并明确隔离环境。 |
| [Wang et al., Anti-spoofing study on palm biometric features](https://doi.org/10.1016/j.eswa.2023.119546) | ESWA 2023 | `E2` 摘要/方法片段 | 同步双波长采集 palmprint/palm-vein，并从较长的动态影像估计 pulse/SpO2；作者制作多种人工 palmprint/palm-vein 材料，提出三层 anti-spoofing。 | 这是生理动态 liveness 的更高要求参照，不是 2--3 帧 RGB/NIR 的证据；没有实测帧率、光学稳定性和 signal pipeline 时，本项目不可借此声称测到 pulse/SpO2。 |
| [Yao et al., domain-adversarial palmprint anti-spoofing](https://dblp.org/rec/conf/icip/YaoSZ23) | ICIP 2023 | `E2` 书目信息/作者摘要 | 已提出大型攻击数据与 domain generalization；说明掌纹 anti-spoofing 并非空白。 | FYP 不能以“首次跨域 PAD”表述；需具体限定为传感协议、主动采集或 edge trade-off。 |
| [DAPANet](https://doi.org/10.1016/j.displa.2024.102871) | Displays 2025 | `E1` 摘要/方法/协议 | 用 XJTU-PalmReplay 的 5 个 display-capture domain，做多源到多目标的 anti-spoofing domain adaptation。 | 留出攻击设备/domain 是已有最低标准；RGB/NIR/ToF 的结果也须把材料/设备完整留出。 |
| [HFSRA](https://doi.org/10.1049/ipr2.70029) | IET Image Processing 2025 | `E1` 数据/协议 | 也使用 XJTU-PalmReplay；按 display-capture domain 做 cross-domain test。作者认为平面 palm 特征下 depth signal 较弱，这是其 RGB 资料的设计判断。 | 不把“ToF 对掌纹无用”当作结论；只把它视作必须在真实贴片和受限几何上验证的反例。 |
| [HiChrom-MAE](https://dblp.org/rec/conf/mir/XiongHCLF26) | ICMR 2026 | `E2` 书目信息 | 专门的 palmprint PAD，基于 frequency/chromaticity masked autoencoding。 | palmprint PAD 已成最近方向；FYP 需要强调主动采集、传感器约束、未知攻击协议或 edge cost 中至少一项。 |
| [ISO/IEC 30107-3](https://www.iso.org/standard/79520.html) | 标准 2023 | `E1` 范围 | 规定 PAD 的评测/报告与已知攻击分类。 | 以 APCER/BPCER，另加系统级 IAPMR，避免以 binary accuracy 代替安全评估。 |

**反思：** 最近研究已经不再只问“模型能否从图像辨认攻击”，而是问攻击是否可物理实现、能否迁移、在未知条件能否泛化。项目的演示视频只能是证据之一，不能替代材料留出、session 留出和攻击成功率统计。

## 7. 主题六：端侧与采集系统

| 工作 | 年份/来源 | 阅读 | 做的是什么 | 对 FYP 的含义 |
| --- | --- | --- | --- | --- |
| [Palm-ID](https://arxiv.org/abs/2401.08111) / [MSU PalmDB](https://biometrics.cse.msu.edu/Publications/Databases/MSU_PalmDB/) | TIFS 2024 | `E1` 方法/效率 + artifact audit | 手机端完整无接触掌纹 pipeline，含 ROI、质量、压缩 embedding 和端侧应用；相关数据须签协议后向作者申请。 | 最重要 conceptual baseline，但作者公开页面未见对应源码/模型下载；Pi 不能直接照搬其手机或服务器数字，必须设备实测。 |
| [sweet sensor platform](https://arxiv.org/abs/2404.09376) | arXiv 2024 | `E1` 传感平台 | RGB、multi-NIR、stereo、photometric stereo 的模块化无接触手部平台；反射式 NIR 对环境敏感。 | 采集盒的首要任务是可控光学与重复采集；先验证 NIR 信噪和同步，再写 fusion。 |
| [MobileFaceNet + Circle loss](https://doi.org/10.1016/j.displa.2022.102214) | Displays 2022 | `E2` 摘要 | 早期轻量移动端识别基线。 | 边缘轻量化已有长线工作，FYP 应报告真正 Pi 上的真实 latency/内存，而非仅参数量。 |

## 8. 对 FYP 的最终收敛

### 不值得作为主贡献的部分

- 单帧 RGB 掌纹识别；
- RGB/NIR 融合本身；
- 训练一个随机切分下高 accuracy 的 PAD；
- 宣称掌纹资料只要不上传云端就“完全隐私”；
- 做支付/大规模开放集搜索。

### 仍值得验证的候选贡献

> 为 Pi 级、受限几何的 RGB/NIR/ToF 无接触掌纹 `1:1` 核验建立一个**主动采集风险门控协议**：在 claim 后产生挑战，并检验预定义 response relation；用固定的真实身份阈值，在材料和 session 留出的物理攻击条件下，量化该策略对 `IAPMR / APCER / BPCER / ROI failure / p95 interaction time / memory` 的影响。

这不是预先声称方法有效。它的研究价值来自严格的负结果也有信息量：若多传感策略只提高误拒或仅适用于已见材料，便说明该低成本 edge 设定不值得部署复杂 PAD。

## 9. 仍未覆盖、下一轮应读的资料

- HiChrom-MAE 全文与附录；
- 获取 RegPalm 正文，补齐其 `1:1`/`1:3` open-set split、weight release 和 WebPalm 的实际下载/metadata；当前已确认其数据/代码入口与限制；
- DPFed-Palm 与 FedPalm 的 threat model，避免误用“federated = safe”；
- 只有老师决定把 synthetic augmentation 纳入 scope 时，才申请 GenPalm 并审计其 agreement、生成器训练源与 exact split；当前 Diff-Palm/GenPalm 都不进入 B0/P0/S；
- 掌纹 PAD 的公开 benchmark 和实际攻击采集流程，确认是否可在学校伦理范围内复现。
