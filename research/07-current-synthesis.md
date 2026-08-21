# 当前综合结论：2026-08-21

这是目前给老师讨论的版本，不是最终论文摘要。它把已读文献、澳门事实、设备条件和仍未验证的假设分开。

## 1. 研究领域真正正在推进什么

2023--2026 的掌纹研究并不只是在换 backbone：

1. **采集不受控与跨域。** 研究将手机、相机、姿态、照度、session 变化视为独立问题，常做 cross-sensor/cross-dataset，而不是随机切分。[BEST](https://web.comp.polyu.edu.hk/csajaykr/myhome/papers/PR2023.pdf) 与 [smartphone CycleGAN work](https://doi.org/10.1109/TIFS.2023.3301729) 是明确例子。
2. **大规模与极低 FAR。** RegPalm/WebPalm 等将 1:1/1:N open-set 及极低 FAR 带入目标，但这类数据和算力规模不是 Pi FYP 可直接竞争的对象。
3. **合成与隐私。** GenPalm、Diff-Palm、FedPalm、去标识化等工作表示数据规模、跨客户端训练和资料保护都在快速发展；本项目不应把“edge inference”错误升级为完整隐私保护。
4. **PAD 从分类走向未知域与物理呈现。** ICIP 2023、XJTU-PalmReplay 上的 2025 工作、CAAP 与 2026 HiChrom-MAE 表明 palmprint PAD 已是活跃方向。未知 display/camera/material，才是有效协议的一部分。
5. **传感器不是免费信息。** `sweet` 和 HDC-Net 表明 RGB/NIR/深度/掌静脉融合早有研究；它们也表明同步、标定、光学质量、对齐、数据需求和资源成本是系统组成部分。
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

> 在低成本、受限几何的 RGB/NIR/ToF 采集盒中，主动短序列与质量风险 gate 是否在固定 `1:1` 匹配阈值下，降低**未见**物理呈现攻击的最终通过率，同时不以过高的正常误拒、重采或 Pi 延迟为代价？

这个命题的贡献可以是正结果，也可以是可靠的负结果。后者同样能回答：在这个硬件等级和攻击范围里，第二模态或主动序列是否值得其复杂度。

## 4. 最可信的应用故事

把系统定位为一个**受控、低频、有明确授权和人工 fallback 的内部核验器**：例如设施维护进入受限机房或领取关键工具时，工单/QR 先提出一个身份 claim，掌纹只做本地 `1:1` 确认。最小审计事件仅关联匿名人员 ID、工单/工具 ID、时间、结果和设备状态。

它的价值机制不是“掌纹比一切都先进”，而是待验证的三项运营假设：

| 假设 | 可量化量 | 推翻它的访谈/数据 |
| --- | --- | --- |
| 人与凭证可能不一致，人工确认造成时间/争议成本 | 例外次数、人工分钟、事后无法关联的事件数 | 现场能可靠处理且极少发生，或卡/PIN 已足够 |
| 设备须在网络异常时继续执行有限核验 | 断网成功率、恢复后的审计补齐率、人工 fallback 时延 | 现场网络稳定，且离线决策违反运营/合规规则 |
| 最小化原始图像传输/留存值得付出集成成本 | 原始帧上传数、保存期、负责人可接受的资料边界 | 组织不接受生物识别，或云端现有流程更合适 |

澳门的正确位置是**约束与访谈地点**，不是未经证明的市场空白：已有澳门银河掌纹支付先例，同时澳门个人资料指引要求考虑用途、比例性、替代方案和留存。因而 demo 不做支付、全员考勤、执法或劳动资格判断。

## 5. 论文主线的决策树

```text
先实现 B0：RGB 1:1 + ROI + Pi 测量
  |
  +-- RGB/NIR/ToF 无法稳定测量 -> 只做 RGB/ToF 采集质量与 edge trade-off
  |
  +-- 低成本 PAIS 无法通过 B0 -> 不主张 PAD，收敛为质量/稳定性研究
  |
  +-- B1/B2/M 只在已见材料有效，或高 BPCER 换来低 APCER -> 负结果，停止安全主张
  |
  +-- M 在未见 PAIS/session 上有净收益 -> 完成主动采集风险门控研究
```

## 6. 现在最该做的事

1. 用 [06-evaluation-and-data-plan.md](06-evaluation-and-data-plan.md) 的字段核对实验室硬件，完成 Gate 0。
2. 下载或申请两 session contactless 数据，先跑 RGB B0；同时设计经同意的小样本自采表。
3. 在老师批准的范围内做 print/screen Gate 1，并冻结 B0 阈值。
4. 完成 5--10 个面向设施/物业/承办商的半结构访谈，询问手套、污渍、伤口、重采和 fallback 是否影响流程；若故事不成立，及时把项目写成 biometric measurement benchmark，而不是硬凑经济价值。
