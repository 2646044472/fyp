# 研究反思：什么没有新，什么值得继续

最后更新：2026-08-21。本文件不是宣传稿，而是用来阻止项目沿着看似合理、其实已被文献或现实否定的方向投入时间。

## 1. 三个被研究否定的直觉

### 直觉一：把掌纹放到 edge 就是创新

不成立。Palm-ID 已把 ROI、质量、匹配、紧凑模板和端上应用组合成完整移动系统；`sweet` 也已公开了比现有原型更丰富的 RGB/NIR/立体/光度立体手部采集研究平台。Raspberry Pi 版的复现有工程价值，却不自动构成方法创新。

**因此：** `edge` 在本项目中必须成为一个可测约束，而不是标题装饰。至少应报告端到端 p50/p95、模型/模板大小、CPU/RAM、采集失败、断网决策和功耗或能耗代理指标。

### 直觉二：RGB + NIR / 3D 盒子就是创新

不成立。多光谱掌纹、NIR 可见静脉以及快速多光谱采集已有长期研究；`sweet` 也表明多模态手部采集可行。同时该文明确提示：反射式无接触 NIR 信号较弱、对环境敏感。简单堆传感器会使模型、对齐和故障模式更多，却未必提高真实系统安全性。

**因此：** 盒子只在它变成实验控制器时有研究价值：固定手掌工作距离、记录几何、遮蔽环境光、同步 RGB/NIR 光源和相机，并允许公平比较不同采集策略。它不是要展示一台“更复杂的锁”。

### 直觉三：做一个掌纹 PAD 网络就够新

不成立。ICIP 2023 已研究掌纹 anti-spoofing 的跨域泛化，2025 的 DAPANet/HFSRA 又以 XJTU-PalmReplay 的 display-capture domain 测未知域；CAAP 则将可复用、print-and-capture 的对抗贴片作为攻击问题，2026 ICMR 还有专门的 palmprint PAD 论文。更广的 PAD 文献也一直把未知材料、未知传感器和未知环境的泛化作为难点。

**因此：** 若最终只训练一个 `bonafide / attack` 分类器并在随机切分上报 accuracy，应视为失败的研究定位。更重要的是，2010 年的 online multispectral palmprint system 已用 visible/NIR 固定多谱采集和纸张攻击讨论 antispoof/liveness；2020 年 Stanuch et al. 又已有掌部 NIR/UV 随机采集顺序、跨帧差异检查和重复采集建议。故“RGB/NIR 短序列能挡打印”“随机 challenge”或“两帧不同”都不能作为本项目的创新。真正要证明的是，一个预冻结、实际可观测的 illumination-response verifier 是否相对**静态多谱 B2**在未知攻击条件下进一步降低最终放行风险，并且代价可接受。

### 直觉四：找到维护或钥匙管理场景，就已经找到经济价值

不成立。NIST 的维护场景只说明时限授权、预同步和事后撤销是一种真实的 access-control workflow pattern，不指定 palm，也不提供澳门现场的频率、采购价格或人工成本。Chin et al. 的实地研究反而说明：当存在高峰人流时，biometric 的姿态调整和重采成本可能使它输给 RFID/QR。Yamasaki et al. 的形式化模型则提醒，比较不同凭证时成本不只是一次开门/匹配，而包括授权、撤销、发放、收回等权限变更操作。

**因此：** 机房维护或关键工具领取只能作为可被推翻的访谈假设。若现场没有足够的临时授权/交接、现有 QR/card/人工已能低成本处理、或无法提供公平 fallback，结论应是“不部署 biometric”。在获得流程数据前，不写 ROI 金额，也不把“离线”或“少传原始帧”当作客户已确认愿付费的价值。具体的访谈字段和停止条件见 [`10-story-validation-plan.md`](10-story-validation-plan.md) 与 [`18-maintenance-story-evidence-log.md`](../log/18-maintenance-story-evidence-log.md)。

## 2. 当前可 defend 的最小研究主张

不是：

> RGB/NIR/ToF 能“证明活体”或“解决掌纹伪造”。

而是：

> 在由 Raspberry Pi 级采集盒约束几何的无接触掌纹 `1:1` 核验中，一个轻量的、claim 后实际状态可记录的 RGB/NIR illumination command、预冻结 response verifier 与质量风险 gate，是否能相较**固定 RGB/NIR 多谱采集**，降低指定攻击族在**最终核验通过**中的成功率；这种增益是否仍能在未见材料/未见采集 session 中保留，并且不造成不可接受的真人误拒、时延与能耗？

这里“随机化”只指每次采集所要求的光照/帧次序由设备在 claim 后即时选择并记录，它本身不构成新颖或 freshness。只有 verifier 预先定义并检查“该次 illumination 与观测到的跨帧反射/quality response 的关系”时，它才可能对**预先录制的静态/固定序列重放**加入可测的 freshness 假设；单纯随机取帧、比较差异或再 fusion 都不是充分的 challenge-response。即使关系检验成立，攻击者若使用真实手、能随光照变化的高级假体或能实时驱动显示的攻击装置，仍可能通过。故它是一个**可测风险控制**，不是密码学保证，也不是普遍 liveness proof。

还要避免把它与生理活体混同：已有 palm biometrics 工作通过同步双波长和较长的动态信号提取脉搏/SpO2 来提升 anti-spoofing。若现有设备没有足够帧率、光学稳定性和经验证的 signal pipeline，`2--3` 帧短序列只能研究 freshness/quality，不可声称检测生命体征。

### 不把“自适应开启 NIR”误写成新的 fusion 理论

质量感知、成本敏感的多模态 fusion 早已有研究，因此“先看质量、再开更多传感器”不是独立创新。它可以是一个有价值的**edge 对照策略**：先取得 ToF 和一帧 RGB；仅当 development split 冻结的质量/匹配不确定区间触发时，才要求 RGB/NIR 主动短序列。该策略必须同时和“始终 RGB”及“始终短序列”比较，并报告每次核验的 NIR 开启率、输入端增量能量、p95 interaction time、IAPMR、BPCER 和 retry。

若策略只是把容易通过的样本直接 accept，导致攻击也不进入 NIR，则它会降低成本却提高最终风险。因此它不能只按 accuracy 或平均 latency 选择，且 escalation rule、阈值和训练数据必须在 PAIS/session test 前冻结。若没有总风险与成本的 Pareto 改善，保留固定短序列，或彻底舍弃该变体。

## 3. 威胁模型必须分层

| 攻击族 | 低成本实验样本 | ToF / RGB-NIR 短序列可能检查什么 | 不能保证什么 | 最终指标 |
| --- | --- | --- | --- | --- |
| 二维打印 | 目标掌纹打印在纸张/薄片上 | 平面距离、表面反射、随机光序列是否一致 | 高质量打印或覆盖真实手掌的材质也可能模仿部分响应 | APCER、IAPMR |
| 屏幕重放 | 手机/平板显示图或视频 | 屏幕闪烁/色彩、深度、对随机光挑战的同步响应 | 实时渲染/注入型攻击不在传感器 PAD 范围 | APCER、IAPMR |
| 普通纹理贴片 | 非对抗性印刷/纹理材料贴在真人手掌上 | 局部谱反射、帧间一致性、ROI 质量 | 贴片可能具有真实 3D 距离，ToF 不能单独发现 | APCER、IAPMR |
| CAAP 风格对抗贴片 | 经批准后按公开代码/规范制造 | 作为高成本、白盒风险基线 | 预印本的相机、攻击知识和模板流程不等于本系统 | attack success rate、IAPMR |
| 数字注入/模板篡改 | 不做为本 FYP 的传感实验 | 不适用 | 光学 PAD 无法保护被攻破的 OS、通信或模板库 | 单独的系统安全范围 |

`APCER` 衡量攻击被 PAD 错判为真人；它不足以说明门是否被打开。`IAPMR` 衡量攻击同时绕过 PAD 且被匹配为目标身份，才接近本 demo 的真实安全失败。ISO/IEC 30107-3 的范围是采集处的 presentation attack；不要把实验结果说成整个门禁系统安全。

## 4. 研究问题的真正风险

| 风险 | 可能发生的结果 | 正确反应 |
| --- | --- | --- |
| NIR 传感器质量不足 | 无法看出稳定、可重复的跨光谱信息 | 先缩回 `RGB + ToF quality`，不要硬训多模态网络；必要时购置有原始帧/独立曝光控制的模块。 |
| 攻击基线本身不能骗过 B0 | 没有可改善的安全问题 | 不要继续宣传 PAD；转为采集质量/边缘测量，或提高攻击真实性后再判断。 |
| 攻击能骗过 B0，B1/B2 均无改善 | 短序列并非有效信号 | 诚实报告负结果；转向可撤销模板或设备安全。 |
| 只在已见材料有效 | 分类器学到材料或采集背景 | 必须在未知材料/session 下重测；不能把随机切分数字当贡献。 |
| 安全提升伴随真人频繁重采 | 用户会绕过设备或人工放行 | 调整为低摩擦质量引导；同时报告 BPCER 和 interaction time。 |
| 访谈没有现场需求 | 故事不成立 | 保留为 biometric measurement demo，不硬绑澳门经济叙事。 |

## 5. 继续、暂停或换方向的决策门槛

### Gate 0：设备是否值得做多传感研究

在写 PAD 模型前，必须记录：相机型号与 raw pixel format/bit-depth、NIR LED 波长及电流/PWM、是否存在 IR-cut filter、曝光/增益能否锁定、ToF 量程/方差、遮光条件和每种采集的时间戳。`sweet` 的经验尤其重要：受控多光源、多相机仍需把相机触发、LED 实际状态、标定和掉帧当作测量对象；“程序请求某个灯序”不等于该帧真的在该光照下被拍到。

Gate 0 的最小验收不是买更多传感器，而是留下以下可复查记录：

| 验收项 | 最小记录/测试 | 失败后的含义 |
| --- | --- | --- |
| 光谱输入 | RGB 是否为可见光、NIR 是否有原始稳定帧；波长、IR-cut、曝光/增益、LED current/PWM 及暗帧/饱和帧样本 | 不能解释 RGB/NIR 差异，停止 B2/M，只保留 RGB/ToF。 |
| 实际灯序与帧序 | 对固定 target 连续执行已知 RGB/NIR 序列，记录 command、相机 frame id/monotonic timestamp、曝光和实际 illumination state；检查掉帧、重排、超时和 LED 切换延迟 | 不把“随机序列”称作 challenge，也不合成跨帧 response relation。 |
| 几何与对齐 | 在工作距离/角度范围内记录 ToF、ROI 成功率；若融合 RGB/NIR，使用明确的 calibration target 或可重复对应点记录 ROI drift | 不将模态差异归因于皮肤/攻击材料；B2 退回各模态独立质量对照。 |
| 重复性 | 同一静态 target、同一呈现者与重新摆放后的 session 都重复采集，保留环境光、warm-up、sensor timeout 和 blank-frame 记录 | 不能把单次演示的好图或模型分数当作稳定信号。 |

这是从 `sweet` 的工程细节得到的研究纪律，不是照抄其硬件：该平台使用全局快门 NIR 相机、可编程多光源和专用 trigger controller，仍报告了同步脉冲缺失，并以采集开头/结尾的视觉标记校正序列。我们的 Pi 原型若没有同等级触发能力，应诚实将 sequential capture 的不确定性计入实验，而不是暗示硬件同步。

**停止条件：** 无法独立取到稳定 NIR 原始帧，或无法证明每帧对应的实际 illumination/几何状态。此时只做 RGB/ToF baseline，或者更换传感器；不要把软件请求序列包装成主动安全机制。

### Gate 1：是否有值得防护的物理攻击

冻结 B0 的身份阈值后，在未参与阈值设定的攻击集上测试打印、屏幕和普通贴片。记录每类攻击的 IAPMR，而不是只拍一次成功视频。

**停止条件：** 所有低成本攻击在 B0 上都几乎无法通过，且没有可信、合规的方法构造更强攻击。此时 PAD 不是当前设备的核心问题。

### Gate 2：主动采集是否提供真实增益

比较 `B0 RGB 单帧`、`B1 RGB + ToF quality gate`、`B2 RGB/NIR 单次`、`M RGB/NIR 随机 2--3 帧 gate`。阈值只在 development set 固定；测试按攻击材料和 session 留出。

**继续条件：** M 相对 **B2 静态 RGB/NIR 多谱** 在至少一个未见攻击设定中降低 IAPMR 或 APCER，且 BPCER、ROI failure、p95 interaction time 与输入端能耗保持在预先同意的预算内。仅优于 B0/B1 不足以支持主动安全主张。

**暂停条件：** 增益只来自已见攻击材料、靠提高 BPCER 换取，或 Pi 的端到端交互时延不可用。

### Gate 3：澳门故事是否成立

访谈至少覆盖设施/机房运营、承办商或维修管理、安全/物业三类角色。记录现行核验步骤、断网 fallback、凭证与人不一致的处理、人工时延、资料顾虑和愿意尝试的替代方式。

**继续条件：** 至少一个具体工作流确认“人-工单/工具-时间”的核验与离线审计确有成本；研究题目围绕该工作流收紧。

**暂停条件：** 只有泛泛“安全可能有用”的反馈；此时不要声称经济价值，只作为 edge biometric benchmark。

## 6. 目前的研究结论

1. 澳门确实不是“没有掌纹”：2024 年澳门银河已有微信掌纹+掌静脉支付部署，第一阶段覆盖 60 多个零售点。但这并未反驳本地居民很少遇到的体感，因为它很新、局部且服务已开通相关钱包功能的用户。
2. 正因为支付已有银行、商户、风控和大厂硬件生态，FYP 不应竞争支付。一个小型 edge device 的合理边界是小规模、`1:1`、可离线、可人工 fallback 的内部核验。
3. 当前最有研究价值的不是“我们拥有更多传感器”，而是“在受限硬件与未知攻击下，怎样量化安全、可用性和成本的 trade-off”。
4. 这仍只是**候选研究问题**。Gate 0--3 任一失败，都应缩小或改变问题，而不是用更复杂模型遮掩负结果。

## 7. 下一批必须精读的资料

- HiChrom-MAE 全文：确认数据集、传感器、攻击材料、训练/test protocol、是否覆盖未知攻击和运行资源；
- CAAP 的公开代码与数据可用性：仅在伦理与老师批准后考虑复现；
- `sweet` 的硬件 BOM、同步方式和对齐流程：作为评估自制采集盒的参考，不照搬其昂贵组件；
- ISO/IEC 30107-3 正文或学校可访问版本：正式论文的 PAD 实验须对齐其定义与报告结构。

## 参考资料

- [Palm-ID (2024)](https://arxiv.org/abs/2401.08111)
- [sweet: modular contactless hand sensor platform (2024)](https://arxiv.org/abs/2404.09376)
- [CAAP: physical palmprint adversarial patches (2026 preprint)](https://arxiv.org/abs/2604.06987)
- [ISO/IEC 30107-3:2023 PAD testing and reporting](https://www.iso.org/standard/79520.html)
- [NIST SOFA biometrics draft](https://pages.nist.gov/SOFA/SOFA.html)
- [Challenge-response formalism (2022)](https://doi.org/10.1186/s13635-022-00131-y)
- [Tencent: Weixin Palm Pay Macao deployment (2024)](https://www.tencent.net.cn/weixin-palm-pay-achieves-first-application-outside-the-chinese-mainland-with-launch-in-macao/)
