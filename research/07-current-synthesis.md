# 当前综合结论：2026-08-21

这是目前给老师讨论的版本，不是最终论文摘要。它把已读文献、澳门事实、设备条件和仍未验证的假设分开。

## 1. 研究领域真正正在推进什么

2023--2026 的掌纹研究并不只是在换 backbone：

1. **采集不受控与跨域。** 研究将手机、相机、姿态、照度、session 变化视为独立问题，常做 cross-sensor/cross-dataset，而不是随机切分。[BEST](https://web.comp.polyu.edu.hk/csajaykr/myhome/papers/PR2023.pdf) 与 [smartphone CycleGAN work](https://doi.org/10.1109/TIFS.2023.3301729) 是明确例子。
2. **大规模与极低 FAR。** RegPalm/WebPalm 等将 1:1/1:N open-set 及极低 FAR 带入目标，但这类数据和算力规模不是 Pi FYP 可直接竞争的对象。
3. **合成与隐私。** GenPalm、Diff-Palm、FedPalm、去标识化等工作表示数据规模、跨客户端训练和资料保护都在快速发展；2025 的 EMPalm 又提示图像采集链路可存在 EM 侧信道。因此本项目只能说 edge 减少网络传输和集中原始帧留存，不能把 local inference 错误升级为完整隐私/安全保护。
4. **PAD 从分类走向未知域与物理呈现。** ICIP 2023、XJTU-PalmReplay 上的 2025 工作、CAAP 与 2026 HiChrom-MAE 表明 palmprint PAD 已是活跃方向。未知 display/camera/material，才是有效协议的一部分。
5. **传感器与采集控制不是免费信息，也不是空白。** 2010 年已有低成本可见光/NIR 四谱掌纹系统，2020 已有无接触 NIR+UV 同次 palm verification，2022 已有 dual-camera + 单点 ToF 的距离对齐，2025 又有距离/旋转/video registration 的完整 sensing 研究；`sweet` 和 HDC-Net 也表明 RGB/NIR/深度/掌静脉融合早有研究。故固定多谱、ToF 对齐或智能采集本身都不是贡献；同步、标定、光学质量、对齐、数据需求和资源成本仍是必须实测的系统组成部分。
6. **更强的活体路径已存在。** 同步双波长的 palm biometrics 已尝试用脉搏/SpO2 等动态信号提高 anti-spoofing。它提示我们把 `2--3` 帧主动短序列如实定位为低开销 risk gate，而非生理活体证明。

完整的反例与不可宣称事项见 [08-counterevidence-and-boundaries.md](08-counterevidence-and-boundaries.md)。

本轮覆盖、证据深度与尚未精读的资料见 [09-reading-coverage-audit.md](09-reading-coverage-audit.md)。

## 2. 因此不应做什么

- 只做单帧 RGB recognition，然后以高 accuracy 宣称创新；
- 把 RGB+NIR fusion 或 Raspberry Pi 部署本身作为新颖点；
- 把 RGB/IR、距离提示、QR 与掌纹/掌静脉的一体终端当成新产品类别；已有商用模组公开这类组合，且供应商数字必须独立验证；
- 用随机切分和 pooled attack accuracy 宣称 liveness/PAD；
- 以“澳门没有掌纹”“非法劳工”或没有来源的 ROI 金额作为动机；
- 把本地推理写成模板不可逆、不可关联或全面安全。

## 3. 仍然合理的研究缺口

不是声称文献完全没有做过，而是一个可检验的交集：

> 在低成本、受限几何的 RGB/NIR/ToF 采集盒中，claim 后生成的 illumination challenge 与质量风险 gate 是否在固定 `1:1` 匹配阈值下，相对**静态多谱 RGB/NIR**降低**未见**物理呈现攻击的最终通过率，同时不以过高的正常误拒、重采、Pi 延迟或输入端能耗为代价？

这个命题的贡献可以是正结果，也可以是可靠的负结果。后者同样能回答：在这个硬件等级和攻击范围里，第二模态或主动序列是否值得其复杂度。

**当前最大风险：** 2010 年已存在低成本静态可见光/NIR 多谱、<1 秒采集和纸张 anti-spoof 先例。因而在没有 `M > B2` 的未见 PAIS 结果前，项目不应使用“主动多传感掌纹防伪”作为创新摘要；老师讨论时应先展示这项反例及新的退出条件。

**第二个风险：** ToF 距离对齐（2022）和距离/旋转/video registration（2025）同样已有直接先例。因此即使 `M` 失败，项目也不能退回去把“ToF 引导采集”重命名为创新；可成立的成果将是已冻结硬件上的端到端 trade-off 测量，或一个被数据推翻的工程假设。

## 4. 最可信的应用故事

把系统定位为一个**受控、低频、有明确授权和人工 fallback 的内部核验器**：例如设施维护进入受限机房或领取关键工具时，工单/QR 先提出一个身份 claim，掌纹只做本地 `1:1` 确认。最小审计事件仅关联匿名人员 ID、工单/工具 ID、时间、结果和设备状态。ASIS 的非代表性行业调查可作为外部动机：705 个设施受访者中 38.30% 报告 credential sharing；但 tailgating 和 propped doors 更常见，因而本项目只能针对原本能逐人通过的单人核验点，不能声称解决一般物理门禁或尾随。

它的价值机制不是“掌纹比一切都先进”，而是待验证的三项运营假设：

| 假设 | 可量化量 | 推翻它的访谈/数据 |
| --- | --- | --- |
| 人与凭证可能不一致，人工确认造成时间/争议成本 | 例外次数、人工分钟、事后无法关联的事件数 | 现场能可靠处理且极少发生，或卡/PIN 已足够 |
| 设备须在网络异常时继续执行有限核验 | 断网成功率、恢复后的审计补齐率、人工 fallback 时延 | 现场网络稳定，且离线决策违反运营/合规规则 |
| 最小化原始图像传输/留存值得付出集成成本 | 原始帧上传数、保存期、负责人可接受的资料边界 | 组织不接受生物识别，或云端现有流程更合适 |

澳门的正确位置是**约束与访谈地点**，不是未经证明的市场空白：已有澳门银河掌纹支付先例；一份 2020 biometric 处理授权也在其特定处理情景中写入用户主动发起、原则同意及权限结束后的删除做法。这不是本项目的法律意见，却支持采用用途受限、低频、可退出的设计。密码学 access-control 文献也区分敏感工作区（身份披露可被需要）与公共通行/消费（可关联性不应交给 verifier）。因而 demo 不做支付、全员考勤、执法或劳动资格判断，更不声称 privacy-preserving/non-transferable credential。

## 5. 论文主线的决策树

```text
先实现 B0：RGB 1:1 + ROI + Pi 测量
  |
  +-- RGB/NIR/ToF 无法稳定测量 -> 只做 RGB/ToF 采集质量与 edge trade-off
  |
  +-- 低成本 PAIS 无法通过 B0 -> 不主张 PAD，收敛为质量/稳定性研究
  |
  +-- M 不优于 B2 静态多谱，或只在已见材料有效，或高 BPCER 换来低 APCER -> 负结果，停止主动安全主张
  |
  +-- M 在未见 PAIS/session 上有净收益 -> 完成主动采集风险门控研究
```

## 6. 现在最该做的事

1. 用 [06-evaluation-and-data-plan.md](06-evaluation-and-data-plan.md) 的字段核对实验室硬件，完成 Gate 0。
2. 下载或申请两 session contactless 数据，先跑 RGB B0；[PPNet 原作者代码](https://github.com/xuliangcs/ppnet) 可借用其 score/ROC 流程，但其 Pi guide 是 2021 年 32 位 Buster/预发布 PyTorch 环境，不能照抄为当前部署。先审计实际 Pi runtime，再设计经同意的小样本自采表。
3. 在老师批准的范围内做 print/screen Gate 1，并冻结 B0 阈值。
4. 完成 5--10 个面向设施/物业/承办商的半结构访谈，询问手套、污渍、伤口、重采和 fallback 是否影响流程；若故事不成立，及时把项目写成 biometric measurement benchmark，而不是硬凑经济价值。
