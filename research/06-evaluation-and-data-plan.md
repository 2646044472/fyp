# 评测与数据计划：从可复现 baseline 到传感器主张

最后更新：2026-08-21。这里不是结果报告，而是在收集数据/挑阈值前写下的 protocol。任何偏离都要在实验日志中说明原因，避免看见测试结果后再改变标准。

## 1. 两个数据层，回答不同问题

| 层 | 数据 | 能回答 | 不能回答 | 通过条件 |
| --- | --- | --- | --- | --- |
| P0：公开工程 smoke-test | [PalmMatchDB](https://huggingface.co/datasets/aspmirlab/PalmMatchDB) 这类可直接下载、许可明确的单 split 数据 | 下载、预处理、ROI、embedding、score、模板和 Pi runtime 是否能跑通 | identity-disjoint、session/cross-device shift、PAD 或可发布的识别性能结论 | 版本化下载 hash、最小运行脚本和不作泛化宣称的 smoke-test 日志 |
| P：公开 protocol 层 | PolyU-IITD v3、Tongji，或经许可的 X-Palm 这类 contactless RGB 数据 | B0 识别 pipeline 是否实现正确；session/cross-domain shift 是否被报告；与公开方法是否同量级 | Pi 的真实速度、NIR/ToF 增益、物理攻击和本采集盒泛化 | 开源或经许可数据上的 1:1 ROC/DET、FMR/FNMR、ROI failure 与复现脚本 |
| S：自采传感层 | 经同意的 RGB、NIR、ToF、光照顺序、距离、session metadata | 主动采集是否改善本设备的 ROI/正常核验/攻击风险；Pi 的 p50/p95 和 memory | 全人群性能、澳门市场需求、生产级低 FAR 认证 | 预注册切分下的 B0/B1/B2/M 对比及不确定性说明 |

公开数据的事实依据：IEEE 数据库目录列出 PolyU-IITD contactless v3 为 600+ subject、12,000+ 图像、两 session；IITD v2 为单 session。IAPR TC4 目录也列出 Tongji 的两 session、12,000 图像。资料入口见 [IEEE Biometrics Council](https://ieee-biometrics.org/resources/biometric-databases/contactless-palmprint/) 和 [IAPR TC4](https://iapr-tc4.org/palmprint-datasets/)。许可、申请和是否允许发布例图应在下载前再次核对。

[X-Palm (2026)](https://github.com/X-Palm/X-Palm-2026) 是更贴近“controlled enrollment -> unconstrained mobile probe”的补充候选：其 6,006 图、103 人/206 手的公开数据卡列出远近、姿态、flash、湿手与表面文字等条件，并提供 identity-disjoint 的 cross-domain split 与 code。数据需签 academic EULA；它没有 PAIS、ToF 或同步 RGB/NIR，因此只用于 B0/domain-shift 对照，不可代替 S 层传感/攻击实验。

P0 的 [PalmMatchDB](https://huggingface.co/datasets/aspmirlab/PalmMatchDB) 标为 Apache-2.0、10,528 rows / 1.27 GB，但公开 card 只有一个 `train` split 和极少采集 metadata。它可以让第一周 demo 有可重复的下载与输入，却**不能**被随机重切分后冒充 session/cross-device/PAD benchmark；其论文的 identities、split 和采集条件要在决定引用任何识别数字前再精读。

[Palm-ID 的 MSU PalmDB](https://biometrics.cse.msu.edu/Publications/Databases/MSU_PalmDB/) 是现代 mobile RGB 的 `P?` 候选，而非直接依赖：官方页要求签署数据协议并经作者批准才给下载链接；所见页面也没有 Palm-ID 的公开模型或代码链接。获批后它可以帮助检查 RGB baseline 的跨时间 protocol，但不能把 paper 的手机/服务器延迟转成 Pi 数据，更不能替代 S 层的 RGB/NIR/ToF/PAIS。

### 公开 PAD 资料的边界

[XJTU-PalmReplay](https://doi.org/10.1049/ipr2.70029) 是当前读到的最贴近掌纹屏幕重放的 protocol 参照：400 个手掌、五个 display-capture domain、总计 96,000 张图，并有 identity-disjoint 和留一 domain 的测试方式。但截至本次检索，未找到官方数据下载、许可或代码入口。因此它不是 `P` 层可立即运行的数据集，只能提供两项设计约束：

1. 屏幕攻击的 train/test 不能随机混合同一 display-capture 链；至少留一输出端或相机组合。
2. 该集只覆盖 RGB 屏幕重放。纸张、覆贴材料、NIR/ToF 和 session-random challenge 必须由经同意、文档化的 `S` 层自采补齐，不能被它替代。

若以后获得作者明确许可，仍须保存获准日期、原始文件 hash、每个 domain 的设备表和 exact split；否则不把其数字写入结果比较。这个限制也避免项目在“数据很大”与“可以复现”之间作错误等同。

### 新近 mobile 数据的可得性检查：MPW-180

[MPW-180](https://doi.org/10.3390/app152111368) 的论文很有价值：180 人、180 台手机、720 段视频，按左右手与 flash/ambient 分成四种条件，且刻意记录自由手距离、姿态、焦点和背景变化。它适合作为我们的 `S` 层采集卡参考，也本应是 B0 跨照明/ROI 的 `P` 候选。

但可运行性未获证实。IAPR TC4 目录目前把它链接至 [PalmWildNet GitHub](https://github.com/bingolo/PalmWildNet)，而该仓库现只有 README、图和 license；README 的 `Dataset DOI / Link` 为空，并称研究仍在 review。论文说数据位于 Aperta，但本轮不能找到可核验的 Aperta record。因此在拿到实际文件、明确许可、完整 identity/condition metadata 和作者 split 前，**不得下载或引用 MPW-180 的性能数字，也不得列为本项目可复现实验的数据来源**。

这不是否定该论文，而是采纳它提出的两条设计纪律：视频相邻帧高度相关，不能被随机拆入 train/test；ROI quality exclusion、motion blur 和 illumination artefact 必须记录为结果，而非在汇总前无痕删除。

## 2. 系统定义

应用为带 claim 的 `1:1 verification`：二维码/工单/卡片先指向一个已注册模板；系统只判断 probe 是否匹配该模板，不进行 1:N 人群搜索。

**授权边界先于 biometric。** 工单/授权服务是唯一的 allow source of truth；Pi 不能由历史成功记录自行推导新权限。若测试离线连续性，Pi 只可使用事前同步的 authorization record，并记录其版本、人员 pseudonym、受限资源、开始/结束时间和 expiry。record 未过期才可本地作 `claim -> palm` 比对；过期、版本冲突、需要即时撤销或无法读取 record 时，决策为 retry/人工 fallback，而不是离线放行。这个模式借鉴 [NIST SP 1800-2b 的能源维护 use case](https://www.nccoe.nist.gov/publication/1800-2/VolB/index.html)，不是对目标场所网络或业务规则的假定。

### B0 不是复制旧 Pi 环境

PPNet 的代码与 metrics 可帮助定义 B0，但其公开 Pi guide 基于 Raspberry Pi 4B 的 32 位 Buster、Python 3.7 和预发布 ARMv7 PyTorch wheels。它不能作为今天的默认安装方案，也不应因“能跑”而成为长期部署依赖。先执行 Gate 0 的设备/OS/runtime 清点，再选择当前硬件能维护的 inference runtime；B0 的不变量只有：固定版本的 RGB ROI、embedding、注册模板、`1:1` score 和 development-set 冻结阈值。

因此最小 demo 的通过条件应是可重复地保存：设备/OS/architecture、runtime/model hash、enrollment 与 probe 的匿名 ID、score、阈值、accept/reject、ROI failure 及 capture-to-decision timestamp。它不以迁移某个旧 PyTorch wheel 或复现作者机器上的数字为通过条件。

| 版本 | 输入与决策 | 目的 |
| --- | --- | --- |
| B0 | 单帧 RGB -> ROI -> embedding -> fixed match threshold | 最小识别 baseline |
| B1 | B0 + ToF/几何/ROI quality gate | 测量距离控制是否改善正常采集 |
| B2 | 对齐 RGB + NIR 的固定序列，采用固定的轻量 score/quality fusion | 静态多光谱强对照；复核第二光谱在本硬件的增益，不将其称为新颖 |
| M | 在身份 claim 后由设备即时选择、记录的 2--3 帧 RGB/NIR illumination challenge；加 quality/risk gate 后再核验 | **条件性候选**：只测其相对 B2 的额外 freshness/risk 收益，而非“多光谱 PAD”本身 |
| MA | 先取得 ToF + 一帧 RGB；只在预冻结的 quality/score uncertainty rule 触发时才进入 M | 次级 edge 对照：测量按需 NIR 是否保留风险收益而减少等待/能耗 |

先在 development split 设定 match threshold、B2 的固定序列与 M 的 challenge space/随机生成规则，之后冻结。M 的 challenge 必须在 claim 后生成，并把 `challenge id/seed`、模态/光照帧顺序和每帧时间戳写入不可改写的实验日志。更重要的是，verifier 须预先定义并检验“所选 illumination 与本次跨帧观测的 response relation”（例如受控曝光下的反射/quality consistency）；若只把随机序列的帧送进普通 fusion/matcher，M 只是动态采集，**不能称 freshness 或 replay-resistant**。攻击样本需要按确实面对的 challenge 分层，不能把同一静态多谱样本冒充为应答。所有版本尽可能共享同一 ROI/identity matcher；否则无法区分“采集策略”与“换模型”的影响。

`MA` 不是新的 fusion 声称。它的测量需加：escalation rate（按 bonafide、impostor、每 PAIS、session 分层）、未升级但最终放行的攻击比例、每 interaction 的 NIR 时间/能耗和 fallback。若 `MA` 以错过攻击为代价换来较低平均成本，则不得称为 edge 优化。

## 3. 自采数据卡草案

### 必须记录的每次呈现字段

`subject pseudonym`、左右手、session id、日期/时间、设备与软件版本、相机型号、镜头、RGB/NIR 模态、NIR 波长/电流、ToF 距离及方差、曝光/增益、光照顺序、环境光条件、手掌距离/角度、ROI success/failure、quality score、操作者、attack class/PAIS、攻击材料与制作条件、是否用于 train/dev/test。另标记可见的 glove/污渍/水分/贴布或伤口、遮挡和无法完成标准姿势的情况；不记录不必要的健康诊断。

这些 condition tag 不是要把手套/污渍/湿手预设为“系统支持的功能”。它们是公平性与可用性的失败分层：若样本被拒绝、无法取 ROI 或需要 fallback，仍应被计入结果。对于必须戴手套的角色，先由访谈确认是否可在进入前脱下并完成单人核验；若不可以，场景本身不适合裸掌掌纹，不能靠排除该角色来维持指标。

原始帧只用于获同意的研究目的；默认只在加密的研究设备/受控存储中保存。需要保存的最小结果日志为：匿名 session id、版本、成功/失败、quality/gating reason、延迟。不要把真实人名、工单或门禁记录混入研究集。

### 最小切分

1. **身份层：** 同一人的 registration 与 probe 可以构成 genuine pair；不同人形成 zero-effort impostor pair。
2. **时间层：** 至少两次不同日期/重新摆放设备的 session；development 和 test 不共享同一 session 条件。
3. **攻击层：** 至少一种 PAIS/材料完全不进入 development；测试时按 PAIS 分开报告，而不是把帧随机混合。
4. **人员层：** 负责制作某一攻击样本或调整装置的人，其攻击捕获条件也尽量与 development 分开。
5. **相机层（可选但优先）：** 若可获得第二种 RGB 相机或更换镜头，在未参与开发的相机上再测 B0/B1。若没有，不声称 cross-device generalization。

小样本无法支持 `FAR=1e-6` 一类生产声称。应报告比较次数、误差计数和区间，使用“在此样本内观察到”而非“系统 FAR 为零”。

这一区分有直接文献依据：[BEST](https://web.comp.polyu.edu.hk/csajaykr/myhome/papers/PR2023.pdf) 将 within-database、cross-database、cross-sensor 分开，并在其两 session、跨手机 MPD 上报告低 FAR 指标。项目若只在同一 session 随机切分，最多只能称为受控条件下的 baseline。

## 4. 攻击范围与安全边界

| PAIS/攻击 | 是否先做 | 所测问题 | 记录的额外变量 |
| --- | --- | --- | --- |
| 纸质 print（只在获授权的测试目标上） | 是 | 二维纹理和打印/重拍是否能通过 B0 | 打印机、纸张、分辨率、尺寸、平面/弯曲、距离 |
| 屏幕 replay | 是 | 显示屏纹理/闪烁/深度与随机采集顺序 | 屏幕型号、刷新率、亮度、显示比例、距离、角度 |
| 非对抗性纹理贴片 | 需老师/伦理批准 | 真实手掌几何下的局部材料变化 | 材料、面积、位置、是否覆盖真实 ROI |
| 白盒优化贴片（CAAP 风格） | 后置且需批准 | 高资源攻击的敏感性，不做生产风险估计 | 代码版本、攻击知识、训练材料、打印/捕获参数 |
| 实时驱动 screen/relay replay | 不在最小 demo；仅在批准后作为高能力 attack | 攻击者能否针对本次 illumination sequence 产生响应 | attacker latency、challenge knowledge、display/sensor path；没有实测不得说 M 抗此类攻击 |
| 数字注入、模板库篡改、强迫呈现 | 不在此实验 | 光学 gate 无法保护的攻击面 | 单列为系统安全范围外 |

纸张/屏幕二次拍摄不是凭空设想：[2022 palmprint presentation attack study](https://www.jmis.org/archive/view_article_pubreader?pid=jmis-9-2-103) 的方法确实重新拍摄 monitor/paper，并发现显示屏 moire、打印清晰度与纸张弯曲会改变结果。因此本项目不能只保存最终 cropped ROI，必须保存这些 capture metadata。

### CAAP 不是当前的可运行攻击任务

[CAAP 的公开仓库](https://github.com/ryliu68/CAAP) 可以审计其研究设定，但不构成即插即用的 benchmark：默认训练脚本读取作者机器的绝对数据路径，引用仓库外的分类器 checkpoint，并锁定 CUDA 12.4 的 Linux 环境。它也只处理预处理后的灰度 palm ROI，并不代表本采集盒的 RGB/NIR/ToF 或即时随机 challenge。

因此本项目的最小 demo 和 S 层评测不得下载、执行或改写 CAAP 来生成攻击材料。CAAP 只用于建立**高资源白盒攻击存在**这一 threat boundary。任何日后的复现必须先同时满足：老师明确同意、学校伦理/安全要求许可、合法取得其数据与权重、隔离的 GPU 环境、冻结的代码 commit 和只针对获授权测试目标的处置方案。即使全部满足，仍只能作为后置、单列的 stress test；不能用来取代 print/screen PAIS 的黑盒实测，也不能把结果表述为真实世界风险率。

## 5. 指标与报告表

| 类别 | 指标 | 报告方式 | 解释陷阱 |
| --- | --- | --- | --- |
| 身份核验 | FMR/FNMR、TAR@fixed FAR、ROC/DET | B0--M 在同一个固定 threshold 或清楚标注各自 operating point | 只报 accuracy 会被大量 impostor pair 误导 |
| PAD | APCER、BPCER | 每一 PAIS/材料各自报告；不要只给 pooled average | 已见材料上低 APCER 不是未知攻击泛化 |
| 系统风险 | IAPMR | 攻击同时通过 gate/PAD 与目标 matcher 的比例；固定 matcher threshold | APCER 不等于门被打开 |
| 采集 | ROI failure、重采次数、quality reject | 按距离、模态、session 和 bonafide/attack 分层 | 以高拒绝率换取“安全”不可接受 |
| edge | interaction p50/p95、每阶段耗时、peak RSS、模型/模板大小、功耗或能耗代理 | 在同一 Pi、相同热状态和固定运行模式测量 | 手机/GPU延迟不能代替 Pi 测量 |

ISO/IEC 30107-3 的范围是采集处 PAD，不覆盖整体系统安全；NIST SOFA 明确区分 APCER 与 IAPMR。故结论要写成“在本设备、这些 PAIS、该阈值和该测试集下”，不写成“证明活体”或“系统全面安全”。

质量 gate 需要透明处理。HGAIQA 在其协议中显示手部几何、平坦度、亮度和清晰度会影响 contactless palmprint performance；但本项目不能通过事后丢弃失败样本来提高数字。任何 quality reject 都是用户可见结果，须纳入重采次数、BPCER 和 interaction time。

### 5.1 Edge 测量 protocol：不要把模型推理当成完整开门交互

本项目不宣称符合 MLPerf。这里借用其可复现原则：在同一质量/同一版本下分开报告 accuracy、latency 与 energy；完整硬件和软件栈必须可辨认；性能模式不能换成一套不同于准确率实验的代码。见 [MLPerf Tiny rules](https://github.com/mlcommons/tiny/blob/master/benchmark/MLPerfTiny_Rules.adoc) 与 [MLPerf Tiny 测量说明](https://mlcommons.org/2026/07/mlperf-tiny-v1-4-results/)。

| 测量 | 起止点 | 样本与报告 | 它回答什么 | 不可替代为 |
| --- | --- | --- | --- | --- |
| `T_model` | 已载入 model 后，embedding runtime 调用前后 | warm-up 后，对同一 frozen ROI 重复至少 100 次；p50/p95/min/max | matcher 的纯 runtime 成本 | 真实用户等待时间 |
| `T_pipeline` | 收到已存在的 RGB/NIR/ToF frame 到产生 decision | 以同一组真实 capture 对 B0/B1/B2/M 重放；每阶段 monotonic timestamp | pre-process、ROI、gate、matcher 的软件成本 | 相机、光源、ToF 的等待 |
| `T_interaction` | 设备发出“请呈现”指令到给出 success/failure/retry | bona fide 成功、quality reject、match reject 和每一 PAIS 都分层；报告 p50/p95、重采次数及分位数置信区间 | 人真正等待的端到端时间 | 只有 model 的 FPS |
| `T_startup` | 进程/服务启动到可接受首次呈现 | 冷启动至少重复 10 次，单列报告 | 断电恢复或 watchdog 后的体验 | steady-state interaction latency |

**一次实验前固定和公开的环境。** 记录 Pi 型号/RAM、OS image/kernel、CPU governor、GPU/NPU delegate、runtime 与版本、线程数、模型 hash/精度、相机/ToF driver、RGB/NIR resolution/fps/exposure/gain、NIR 波长/电流、IR-cut 状态、供电器、散热器/风扇、室温与设备温度。每轮先 warm-up；轮次随机交错 B0--M，而不是把较重版本总放在最后。开始/结束时记录 CPU 温度与 throttling 标志。遇到 thermal throttle、掉帧、sensor timeout 或重启，保留为失败记录，不从分位数样本中静默删除。

**时间和内存。** 同一程序在准确率与性能测量中运行；日志使用 monotonic clock，至少写出 `capture request`、各模态 ready、ROI、gate、embedding、matching、decision、UI/relay signal 的 timestamp。分别报告 stage latency 与 `T_interaction`，并说明 capture 是否同步。peak RSS 测主进程及其子进程的峰值，而不只看 Python/TFLite 的一段；另列模型文件、加载后常驻 RAM 与一人模板大小。若需要关闭磁盘 debug log 才能稳定运行，应报告该 operational mode，不能同时宣称它是 production audit configuration。

**能耗。** 有外接、校准或说明精度的 5 V 输入端功率计时，先量至少 5 分钟 idle，再对每个版本连续运行固定数量 `N` 次、至少三批，并记录总能量 `E_batch` 与时长 `T_batch`。在同一 idle 配置下计算：

`E_incremental_per_interaction = (E_batch - P_idle * T_batch) / N`

同时报告 idle W、batch average W、总输入能量/interaction 和上述增量值，明确这是**整机输入端**能量，不是模型的“J/inference”。批处理可以降低廉价仪表的分辨率误差，但不能消除相机、NIR、ToF、风扇和 UI 的真实成本。没有外接仪表时，只报告 time、temperature 和 memory；CPU utilization 或额定功耗不可改名为能耗结果。DeepEdgeBench 也将 idle power 与持续 inference 的能量分开，因此不同工作负载下的“更省电”不能只由 model latency 推断。见 [DeepEdgeBench](https://arxiv.org/abs/2108.09457)。

**最低可复现实验包。** 保存版本锁定文件、模型 hash、每轮原始 timestamp CSV、sensor configuration、功率计型号/照片/采样率、失败记录、生成汇总表的脚本和不包含生物帧的 example log。绝不在日志中出现真实姓名、掌纹图、模板或门禁记录。

## 6. 结果的继续/退出条件

进入 M 的条件：B0/B2 先完成且 P/S 层均能稳定取 ROI；NIR/ToF 输出在 session 内有可解释、可重复的 metadata；并可证明 M 的随机 challenge 与 B2 固定序列是不同的 capture protocol，而非同一组帧的重新排序。

继续 M 的条件：M 在至少一个未见 PAIS 或 session 中，相对 **B2 静态多光谱** 进一步降低 IAPMR 或 APCER，同时 BPCER、ROI failure、p95 interaction time 与输入端能量不超过在实验前确定的预算。只胜过 B0/B1 而不胜过 B2，不足以支撑主动 challenge 的论文主张。

退出主线的条件：增益只来自已见材料、只靠增加 bona fide 重采得到，或硬件不能同步/稳定提供所宣称的模态。退出并非失败：结果应收敛为 Pi 上的采集质量与部署 trade-off 报告。
