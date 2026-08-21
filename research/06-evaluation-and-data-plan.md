# 评测与数据计划：从可复现 baseline 到传感器主张

最后更新：2026-08-21。这里不是结果报告，而是在收集数据/挑阈值前写下的 protocol。任何偏离都要在实验日志中说明原因，避免看见测试结果后再改变标准。

## 1. 两个数据层，回答不同问题

| 层 | 数据 | 能回答 | 不能回答 | 通过条件 |
| --- | --- | --- | --- | --- |
| P：公开 protocol 层 | PolyU-IITD v3 或 Tongji 这类两 session contactless RGB 数据 | B0 识别 pipeline 是否实现正确；session shift 是否被报告；与公开方法是否同量级 | Pi 的真实速度、NIR/ToF 增益、物理攻击和本采集盒泛化 | 开源或经许可数据上的 1:1 ROC/DET、FMR/FNMR、ROI failure 与复现脚本 |
| S：自采传感层 | 经同意的 RGB、NIR、ToF、光照顺序、距离、session metadata | 主动采集是否改善本设备的 ROI/正常核验/攻击风险；Pi 的 p50/p95 和 memory | 全人群性能、澳门市场需求、生产级低 FAR 认证 | 预注册切分下的 B0/B1/B2/M 对比及不确定性说明 |

公开数据的事实依据：IEEE 数据库目录列出 PolyU-IITD contactless v3 为 600+ subject、12,000+ 图像、两 session；IITD v2 为单 session。IAPR TC4 目录也列出 Tongji 的两 session、12,000 图像。资料入口见 [IEEE Biometrics Council](https://ieee-biometrics.org/resources/biometric-databases/contactless-palmprint/) 和 [IAPR TC4](https://iapr-tc4.org/palmprint-datasets/)。许可、申请和是否允许发布例图应在下载前再次核对。

## 2. 系统定义

应用为带 claim 的 `1:1 verification`：二维码/工单/卡片先指向一个已注册模板；系统只判断 probe 是否匹配该模板，不进行 1:N 人群搜索。

| 版本 | 输入与决策 | 目的 |
| --- | --- | --- |
| B0 | 单帧 RGB -> ROI -> embedding -> fixed match threshold | 最小识别 baseline |
| B1 | B0 + ToF/几何/ROI quality gate | 测量距离控制是否改善正常采集 |
| B2 | 对齐 RGB + NIR 单次采集，采用固定的轻量 score/quality fusion | 测量第二光谱在不加时序挑战下的增益 |
| M | 按设备随机指令顺序获得 2--3 帧 RGB/NIR，加 quality/risk gate 后再核验 | 主候选：测量主动短序列的净收益 |

先在 development split 设定 match threshold 与 gate 规则，之后冻结。所有版本尽可能共享同一 ROI/identity matcher；否则无法区分“采集策略”与“换模型”的影响。

## 3. 自采数据卡草案

### 必须记录的每次呈现字段

`subject pseudonym`、左右手、session id、日期/时间、设备与软件版本、相机型号、镜头、RGB/NIR 模态、NIR 波长/电流、ToF 距离及方差、曝光/增益、光照顺序、环境光条件、手掌距离/角度、ROI success/failure、quality score、操作者、attack class/PAIS、攻击材料与制作条件、是否用于 train/dev/test。

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
| 数字注入、模板库篡改、强迫呈现 | 不在此实验 | 光学 gate 无法保护的攻击面 | 单列为系统安全范围外 |

纸张/屏幕二次拍摄不是凭空设想：[2022 palmprint presentation attack study](https://www.jmis.org/archive/view_article_pubreader?pid=jmis-9-2-103) 的方法确实重新拍摄 monitor/paper，并发现显示屏 moire、打印清晰度与纸张弯曲会改变结果。因此本项目不能只保存最终 cropped ROI，必须保存这些 capture metadata。

## 5. 指标与报告表

| 类别 | 指标 | 报告方式 | 解释陷阱 |
| --- | --- | --- | --- |
| 身份核验 | FMR/FNMR、TAR@fixed FAR、ROC/DET | B0--M 在同一个固定 threshold 或清楚标注各自 operating point | 只报 accuracy 会被大量 impostor pair 误导 |
| PAD | APCER、BPCER | 每一 PAIS/材料各自报告；不要只给 pooled average | 已见材料上低 APCER 不是未知攻击泛化 |
| 系统风险 | IAPMR | 攻击同时通过 gate/PAD 与目标 matcher 的比例；固定 matcher threshold | APCER 不等于门被打开 |
| 采集 | ROI failure、重采次数、quality reject | 按距离、模态、session 和 bonafide/attack 分层 | 以高拒绝率换取“安全”不可接受 |
| edge | interaction p50/p95、每阶段耗时、peak RSS、模型/模板大小、功耗或能耗代理 | 在同一 Pi、相同热状态和固定运行模式测量 | 手机/GPU延迟不能代替 Pi 测量 |

ISO/IEC 30107-3 的范围是采集处 PAD，不覆盖整体系统安全；NIST SOFA 明确区分 APCER 与 IAPMR。故结论要写成“在本设备、这些 PAIS、该阈值和该测试集下”，不写成“证明活体”或“系统全面安全”。

## 6. 结果的继续/退出条件

进入 M 的条件：B0 先完成且 P/S 层均能稳定取 ROI；NIR/ToF 输出在 session 内有可解释、可重复的 metadata。

继续主线的条件：M 在至少一个未见 PAIS 或 session 中，较 B0/B1 降低 IAPMR 或 APCER，同时 BPCER、ROI failure 与 p95 interaction time 不超过在实验前确定的预算。

退出主线的条件：增益只来自已见材料、只靠增加 bona fide 重采得到，或硬件不能同步/稳定提供所宣称的模态。退出并非失败：结果应收敛为 Pi 上的采集质量与部署 trade-off 报告。
