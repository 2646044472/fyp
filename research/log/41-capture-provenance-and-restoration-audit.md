# 采集来源与复原幻觉：反证式研究审计

日期：2026-08-27。此日志记录一次刻意的“提出候选，再寻找足以否定它的直接工作”的循环。目的不是把已有安全功能或视觉效果换名后作为 FYP 创新，而是留下可复查的淘汰理由。

## 1. 提出的问题：PAD 之外，能否证明图像真的来自眼前的相机？

掌纹 PAD 处理的是攻击物被呈现在 capture device 前的情况。一个自然延伸是：攻击者绕过相机，向 Pi/应用注入旧帧、合成帧或 virtual camera，是否可通过随机 NIR/RGB 光照、帧签名或一个外置 MCU 来证明“此帧由真实传感器刚刚拍到”？

这个问题有现实意义，但有意义不等于新颖。首先要分开三层攻击者：

| 攻击者位置 | 例子 | 仅由应用层签名或 LED nonce 能否处理？ |
| --- | --- | --- |
| 应用/API 层 | virtual camera、替换 OpenCV/V4L frame | 可能，取决于相机枚举、metadata、host 是否仍可信 |
| host/OS 层 | hook driver、伪造 GPIO state、替换 camera service | 不能证明；host 持有或能调用的密钥/状态可被伪造 |
| 总线/传感器层 | emulated camera、物理替换、relay | 不能证明；需要独立且被保护的信任根，且仍要说明其覆盖边界 |

若没有先写清攻击者层级，把“签过名的帧”叫做“真实采集证明”是错误的安全主张。

## 2. 反证阅读：这是已有标准化问题

[CEN/TS 18099:2024](https://standards.iteh.ai/catalog/standards/cen/43336798-87a4-49d1-9a0b-4e74c73345a7/cen-ts-18099-2024) 将 injection 定义为修改 data flow 的 data source 或覆盖数据；其范围明确是 capture subsystem **之后**替换 biometric sample。它列出 virtual sensor detection、system-change detection、secure channel/device authentication、challenge-response 和 artefact detection，并要求 IAD 评价覆盖 bona-fide 与 attack samples。这直接说明：

1. 注入攻击不是 PAD 的小补充，而是有独立术语、攻击样本和评价框架的问题；
2. “检测 virtual camera”“加密/签名 channel”“随机 challenge-response”都已经是标准列举的防护类别，不能单独称为新机制；
3. 该标准也承认 application 收到的数据无法天然保证来自 trusted capture device，因此方法防御通常依赖 cryptographic security，而仪器防御才可利用 challenge-response 或 artefact。

[Virtual camera detection: Catching video injection attacks in remote biometric systems](https://arxiv.org/abs/2512.10653)（2025 preprint）又给出了近期直接邻居：其 browser authentication 采集 30,000+ session 的 capability/configuration-response 和性能 metadata，区分 real camera、static/synthetic virtual camera 和 real-time face-swap virtual camera。它报告固定 attack-acceptance 点的 BPCER trade-off。这否定“用相机 reconfigure timing / metadata 识别 virtual camera”作为独立的 FYP 方法。

更关键的反证来自 [Valente 与 Cardenas, ACSAC 2015](https://juniavalente.com/valente15acsac.pdf)：系统把随机文字或 QR visual challenge 显示在 camera 视野内，再验证 frame 内是否出现该 challenge，以证明 camera footage 的 freshness/integrity。随后 [2019 扩展工作](https://juniavalente.com/valente19tcps.pdf) 已使用连续变化的可见光、IR light，并讨论攻击者把正确 challenge copy-paste 回伪造 frame 的强攻击者。因此“随机 IR LED 序列是否能证明新鲜采集”不是一个未研究的起点。

### 结论 A：淘汰为独立方向

**不保留**“低成本 physical-capture provenance / 注入检测”为第五个 FYP 方向。它可以成为任何真实 biometric device 的工程安全清单，但下列题目均不足以形成研究贡献：

- 给 Pi camera 的 frame 加 hash/signature；
- 用随机 LED/NIR nonce 检查 frame 响应；
- 基于 camera metadata 或 timing 区分 virtual camera；
- 把 PAD 和注入检测拼到同一个门锁 demo。

未来只有在存在一个真正独立的 trust boundary、明确不同于上述标准机制的攻击模型、完整 IAD attack species 和对手可复现的结果时，才可重新立题；即便如此也必须比较标准方案，而不是只演示“挡住自己写的攻击”。

## 3. 继续追问：复原生成的细节能否被证据约束？

排除 capture provenance 后，回到 R：若一个低成本相机出现强噪声、过曝、模糊或其中一路缺失，复原/融合网络可能让图像更漂亮，却把本来没有的纹理放进下游检测器。问题不是 PSNR，而是：**下游是否有权使用一个没有来自实际测量的支持的细节？**

这是一个可证伪的问题，因为可将每个细节区域分为：

- measured-supported：可由原始 companion measurement、已标定投影或时间邻帧支持；
- unsupported-generated：只由 restoration prior 产生，找不到独立原始证据；
- unresolved：因遮挡、registration error 或 companion modality 本身失效而无法判定。

但这一定义本身尚不等于新颖。

## 4. 反证阅读：复原幻觉与不确定性已有深厚先例

[Bhadra et al. 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8673588/) 已在线性 tomography 中把 hallucination 形式化为不能从 measurements 产生、而由 learned prior 造成的错误结构，并分析 null-space hallucination。其要点与 R 完全一致：漂亮的 reconstruction 并不保证对真实测量忠实。

[FDA 的 sFRC 工具](https://www.origin-cdrh-rst.fda.gov/sfrc-detecting-hallucinations-medical-image-restoration) 可标出 AI restoration 增添或删除的结构，也明确限制是需要 matched reference，不能无参考在线判断。这是一个有用的**负结果**：没有可信测量或 reference，就不能把“模型不确定”误写成“证据证书”。

[DynamicDPS (2025)](https://arxiv.org/abs/2503.01075) 已将 conditional/unconditional diffusion 与 data consistency 用于减少 medical reconstruction hallucination，并以真实/合成 MRI 和下游 volume 估计验证。它否定“data-consistent restoration + downstream task”这个总想法的空白性。

## 5. R 只剩下的、仍未确认的窄问题

以下问题**暂时不称为创新**，而是下一轮检索应优先试图否定的假设：

> 对已标定且时间对齐的低成本 RGB + NIR/ToF 采集，能否从没有经过生成网络的 companion raw measurement 构造区域级 `support certificate`，让一个下游视觉模型只在证据支持区域采取自动动作，其余区域固定 fallback 或 abstain？该 rule 是否会在未见退化中降低 task-level false pass/false defect，而不是只提高 image metric？

它与医疗先例的差异不是“也有 cross-modal consistency”，而是四个必须同时存在的边界：

| 需要证明的差异 | 若不存在，R 的结论 |
| --- | --- |
| companion 是独立、原始、可标定的 sensor measurement，而非 restoration 输出或同一 encoder feature | 退化为普通 self-consistency，放弃 |
| certificate 对应的是下游实际使用的局部细节，并可触发 hard veto/abstain | 退化为 uncertainty heatmap，放弃 |
| 测试按未见 degradation / sensor failure 留出，且测 false pass、false defect、coverage、latency/energy | 退化为图像质量或 in-domain 分类，放弃 |
| registration error 与 companion failure 被单独标注和报告 | “不一致”无法区分为传感器误差还是模型幻觉，放弃 |

这已比最初的“做一个 multimodal restoration”更研究化，但仍有数据与评价风险。下一步不是设计网络，而是找同一输入、同一 certificate action、同一 endpoint 的 direct neighbor；一旦找到，R 也应淘汰或只保留复现。

## 6. 本轮方法反思

这次循环的顺序是：提出机制 -> 写出可攻击它的 threat model/失败模式 -> 搜同任务标准和原文 -> 写出会迫使我们放弃的证据。这样做带来两个实际收益：

1. 把“技术上能做”与“研究上值得做”分开；
2. 不会把对 Pi 有吸引力的 feature（LED、签名、fusion、uncertainty）误当成贡献单位。

下一轮优先验证 R 的 narrow question 与“真实传感器失效的 action selection”是否已有 direct neighbor。若没有，才值得将其收敛为数据集、protocol 和 baseline；若有，则应继续回到 PAMI 的其它问题，而不是硬保留四方向。
