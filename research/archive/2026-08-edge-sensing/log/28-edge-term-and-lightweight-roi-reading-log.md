# Edge 术语与轻量 ROI 阅读日志

最后更新：2026-08-21。本日志专门处理项目标题中“掌纹 + edge”的歧义：文献里的 edge-aware / Canny edge 多数是图像边缘、ROI 或生成条件；它们不是 edge computing。另精读一篇 2024 年轻量 ROI 原始论文，用来判断真正的端侧缺口在哪里。

## 1. 术语拆分

| 词 | 文献含义 | 对本项目的结论 |
| --- | --- | --- |
| `edge-aware regression` | PKLNet 用手部区域、掌边界和指缝边缘帮助关键点定位；edge 是视觉结构线索。 | 不能把题目里的 edge 写成技术创新，除非明确改为 edge computing 并测 Pi。 |
| `Canny edge` | Canny2Palm 从掌纹纹理提取边缘，作为 Pix2Pix 生成条件，生成合成 identity。 | 与传感器部署无关；不能把 Canny/边缘图当成 edge AI。 |
| `edge device / edge computing` | 在采集端或本地设备上完成 capture、ROI、embedding、matching，减少上传和端到云延迟。 | 这是系统部署位置，必须以本机 p95、峰值 RAM、热、能耗、掉线行为证明；“放在 Raspberry Pi”本身不是方法创新。 |

## 2. 原始论文阅读

### PKLNet, IEEE JSTSP 2023

[论文记录与摘要](https://scholarship.miami.edu/esploro/outputs/journalArticle/PKLNet-Keypoint-Localization-Neural-Network-for/991032796168702976) 将任务定义为无接触场景下的 ROI 关键点定位。PKLNet 是两阶段网络：先利用手部区域/掌边界进行分割和全局关系建模，再回归关键点；作者还用 image-synthesis 训练策略减少手工标注。跨数据集测试报告 82.1% success rate 和 7.7-pixel median localization error。

重要限制：这是 ROI localizer，不是 verifier、PAD 或 Pi resource benchmark；摘要没有给出模型大小、真实端侧延迟、RAM、能耗或传感器同步。它直接否定“掌纹 edge-aware ROI 还没人做”，同时说明 ROI 失败会在 matcher 前决定系统可用性。

### Lin et al., PLOS ONE 2024: lightweight ROI

这篇开放全文的核心问题很贴近 edge：作者明确指出传统/深度 ROI 方法常在 PC 上运行，忽略 embedded device 的计算成本。方法由 YOLOv5-lite 做手掌初定位，再由改进的轻量 U-Net 做两个指缝关键点定位；输入降到 `64x64`，使用深度可分离卷积、残差下采样，以及 heatmap + direct coordinate 的联合损失。

原文可核对的实验边界：

- 自建 SCAUPD：89 人、178 hands、2,274 images；智能手机采集，含自然/闪光照明、背景、姿态和角度变化。
- 另混合 BMPD、REST、MPD、IITD，合计 739 人、24,462 images；MPD 包含两 session、两手机设备。
- mixed database 以 1:1 随机图像划分 train/test，再做旋转和增强；这不等于 identity-disjoint、cross-session 或 cross-device deployment test。
- 论文报告 keypoint accuracy 98.3%、GPU detection 28 ms、model size 831k；open-set success 93.4%、GPU 5.95 ms。
- 训练环境是 Windows 10 + i7-10700F + 7 GB RAM + Quadro RTX 5000。论文没有给 Raspberry Pi/ARM、CPU-only、端到端 capture-to-decision、峰值 RAM、热或 energy 结果。
- SCAUPD 在文章发表时未提供下载；作者称可联系通讯作者取得，故不能把它当现成公开 benchmark。

这里最重要的不是 28 ms 数字，而是报告边界：`GPU ms` 只是 ROI 子模块，不是终端交互时间；1:1 随机图像 split 也不能支撑真实跨 session 泛化。该论文的“embedded feasibility”动机与我们的 Gate 0 一致，但没有替我们完成 Pi 测量。

### Canny2Palm, arXiv 2025

[开放全文](https://arxiv.org/abs/2505.04922) 用 Canny 提取掌纹纹理，重组不同 identity 的 texture patches，作为 Pix2Pix 条件生成可控的新掌纹。作者报告在 open-set benchmark 上最高提升 7.2%，并观察到 synthetic IDs 增至 10,000 时仍有收益。

这篇工作的价值是说明 `edge` 也可能指生成数据的视觉条件；它不是 edge deployment。它的目标是缓解掌纹数据稀缺、做离线预训练，不处理真实相机、NIR/ToF、session、PAIS 或 Pi。当前 arXiv 页面没有关联的官方 code/data link；不能把“可生成 10,000 synthetic IDs”写成项目可用数据或隐私保证。

## 3. 对本项目的可迁移结论

1. 若题目保留 `edge`，中文和英文首次出现必须写成 **edge computing / edge device**，另在术语表注明不是 edge-aware image regression。
2. ROI 是最现实的 edge 优化入口。可以把轻量 ROI、quality reject 和 matcher 组成模块化 B0，但不能将轻量 ROI 的 GPU 数字移植为 Pi 数字。
3. 自采表必须分开记录 `ROI success/failure`、`T_ROI`、`T_embedding` 和 `T_interaction`；否则即使 matcher 很准，用户仍可能因定位失败/重采而无法使用。
4. 对照组应包含一个简单、可解释的 ROI baseline 和一个轻量 learned ROI；如果 learned ROI 只在随机 mixed split 提升，不应声称跨设备或 edge 泛化。
5. synthetic Canny/augmentation 只能是离线训练分支，且必须在 identity/session-disjoint 的真实测试上验证；不进入最小 demo 的现场推理闭环。

## 4. Wording

建议：`edge computing` 指本地 capture-to-decision pipeline；`edge-aware ROI` 指文献中的视觉边缘线索，二者不要混写。

禁止：`Canny edge = edge AI`、`GPU 5.95 ms = Pi 端到端实时`、`轻量 ROI = 已解决边缘部署`、`synthetic IDs = 可替代真人/攻击数据`。

