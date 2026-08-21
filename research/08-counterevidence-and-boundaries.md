# 反例检索与边界：为什么当前主张必须很小

最后更新：2026-08-21。这个文件专门记录会削弱我们候选创新点的资料。目的是防止“先有方案、再找支持”的确认偏误。

## 1. 检索的问题

本轮反向检索包括：`palmprint liveness active challenge response RGB NIR ToF`、`palmprint ToF depth anti-spoofing`、`Raspberry Pi RGB NIR ToF palmprint recognition liveness`、`palmprint presentation attack challenge response active illumination`，并延伸到动态 palm biometrics 和 contactless fingerprint PAD。

## 2. 已找到的直接反例

| 可能的自我宣传 | 反例证据 | 对项目的后果 |
| --- | --- | --- |
| “掌纹 PAD 还是空白” | 2018 的 PALMspoof 已涵盖 104 人、三类 artefact，且测试 print/display、same-device/cross-device；ICIP 2023、DAPANet/HFSRA 2025、CAAP 2026 和 HiChrom-MAE 2026 继续推进。 | 不做“第一个 PAD”；问题只能是特定采集策略、威胁 protocol 与 edge trade-off。 |
| “屏幕/打印攻击只是理论” | [2022 研究](https://www.jmis.org/archive/view_article_pubreader?pid=jmis-9-2-103) 实际重拍 monitor/paper，并在其识别器与条件下发现泄露原图攻击风险。 | Gate 1 从最简单的 PAIS 开始，但完整记录屏幕、打印、距离、角度和光照。 |
| “随机 RGB/NIR 2--3 帧等于 liveness” | [challenge-response formalism](https://doi.org/10.1186/s13635-022-00131-y) 只说明 challenge 可带来 freshness；攻击者可用能跟随挑战的高级 artefact。更强的 palm 研究会测脉搏/SpO2。 | 只写 `active quality/risk gate` 或 `freshness check`；不写活体证明。 |
| “可见光 + NIR 多谱和纸张 anti-spoof 是新的 palm 主张” | [Zhang et al. 2010](https://www4.comp.polyu.edu.hk/~cslzhang/paper/TIM_10_Feb.pdf) 已做低成本四谱在线系统、<1 s 采集和一张 Blue palmprint 纸张攻击；其谱间反射关系被作者提为 liveness 线索。 | B2 必须是静态多谱对照。只有 session-random challenge 能在未见 PAIS 上额外优于 B2，且其随机性真的发生在攻击采集前，才保留主动策略假设。 |
| “多谱同步采集且没有额外交互是新的” | [Stanuch et al. 2020](https://doi.org/10.3390/s20195695) 已做 contact-free NIR + UV 同次 palm verification；2020 也已有 smartphone palmprint print/display liveness 工作。 | M 的唯一待测差异应是 claim 后的随机 challenge 及其相对静态 B2 的净收益；不能把 two-light capture 或重拍纹理 PAD 命名为贡献。 |
| “ToF 一定能拆穿假掌纹” | XJTU-PalmReplay 的 2025 RGB anti-spoofing 研究认为平面 palm 场景中 depth 可能不是主要线索；真实手掌上贴片又可能具有正常深度。 | ToF 首先是距离/几何/ROI 控制；只有未见 PAIS 的结果证明后，才称为 attack signal。 |
| “RGB+NIR 多传感已足够新” | `sweet`、HDC-Net、双波长脉搏/SpO2 palm studies 都有多模态/多波长方案。 | 多传感只能作为控制变量，不能作为贡献名称。 |
| “RGB/IR + 距离 + QR 的掌纹终端还没有产品” | GRGIntech 的 PRM-001 规格已公开列出 RGB+IR camera、5--12 cm distance sensor、QR、补光、palm print/vein 和 ARM/NPU。 | 不把硬件堆叠或掌纹锁 demo 写成创新；供应商数字未经独立验证，但足以否定“首个一体终端”。 |
| “Pi 本地推理就等于隐私保护” | 2024--2025 palmprint template protection 研究已处理可撤销、不可关联、不可逆与密文匹配；这些性质不会由本地推理自动产生。 | 只承诺 raw frame local-only、最小日志、删除期和加密存储；不声称 cryptographic template protection。 |
| “ToF 距离对齐/智能采集是新的” | 2022 已有 dual-camera + 单点 ToF 的 bimodal alignment；2025 已有 distance/rotation/video registration 的完整 touchless palm sensing 系统。 | 不将 ToF guidance 或 smart sensing 命名为创新；只评估在本硬件、固定协议下它是否值得其重采、延迟和能耗成本。 |
| “图像不上传云端就不存在采集端隐私风险” | [EMPalm](https://arxiv.org/html/2510.07533) 在其预印本实验中研究 Pi、Jetson、相机与商用 palm device 的 EM leakage，并重建 palm image；这是物理侧信道而不是云端泄露。 | 本 FYP 不复现/防御该攻击，但不将 edge 写成完整隐私或系统安全保证；raw frame local-only 只是较小的数据流承诺。 |
| “二维码/卡 + 本地掌纹就成为隐私保护、不可转借凭证” | [Garcia-Rodriguez et al. 2024](https://doi.org/10.1016/j.cose.2023.103566) 的真正 privacy-preserving biometric-bound credential 使用属性凭证、加密与零知识机制，并且其适用性受场景限制。 | 当前 FYP 只能做 reader-local `1:1` match 与最小日志。它可测 credential-person binding，不具备 unlinkability、cryptographic non-transferability 或正式 template protection。 |

## 3. 未找到的同型工作，及其正确含义

在本轮公开检索中，尚未找到一篇同时满足以下全部条件的论文：

- Raspberry Pi 级终端；
- 无接触 palmprint 的 RGB + NIR + ToF；
- session-random active short sequence；
- `1:1` 核验中的 print/screen/贴片 PAIS 留出测试；
- 同时报 `IAPMR`、`BPCER`、ROI failure 和端侧 p95 latency/memory。

这只是一个 **E3 检索观察**，不等于世界上不存在，也不能转换成论文的“first” claim。它只能帮助我们制定一个较小而清晰的实验证据组合。

## 4. 哪些结果会真正否定主候选

1. B0 已对获批准的 print/screen PAIS 有很低 IAPMR：没有可改善的安全问题。
2. B1/B2/M 的低 APCER 只来自对 bona fide 的高拒绝：是阈值惩罚，不是防御。
3. 只在已见屏幕/纸张有效：模型学到装置痕迹，不能称 unknown-attack improvement。
4. 设备同步或 NIR 信噪不稳定：不能研究模态融合/主动序列，应退回 RGB/ToF 质量研究。
5. `M` 的时间、重采或内存无法被场景接受：即便攻击数值变好，部署价值也不成立。
6. 访谈显示卡/PIN/人工已经足够，或不能接受生物识别：应用故事无效，应只保留为测量 benchmark。

## 5. 当前可防守的一句话

> 本项目不发明“掌纹活体检测”。它在一个明确、低成本的 edge 采集设定中，测试主动采集的风险门控是否值得其复杂度，并把失败条件预先写清。

这句话比任何“首创”更容易用数据支撑。
