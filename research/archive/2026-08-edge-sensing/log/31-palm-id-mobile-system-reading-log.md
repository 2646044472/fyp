# Palm-ID 移动端系统阅读日志

最后更新：2026-08-21。本文精读 Grosz、Godbole、Jain 的 Palm-ID 原始论文 HTML，重点核对“mobile/端侧”到底测了什么，以及哪些结果可以作为本项目 B0 的 protocol 参照。

## 1. 原始资料

- [arXiv HTML 全文](https://arxiv.org/html/2401.08111)，题名 *Mobile Contactless Palmprint Recognition: Use of Multiscale, Multimodel Embeddings*，v1 2024-01-16；页面给出 DOI `10.48550/arXiv.2401.08111`。
- [arXiv 记录与摘要](https://arxiv.org/abs/2401.08111)。论文同时有 IEEE TIFS 版本 DOI `10.1109/TIFS.2024.3413631`，但本次逐段阅读以开放 HTML 为准。

## 2. 实际系统

Palm-ID 是一个 Android app，使用 Samsung Galaxy S22、Qualcomm Snapdragon 8 Gen 1、8 GB RAM。app 明确有三种模式：enrollment、输入 ID 后的 `1:1 authentication`、以及带阈值的 `1:N search`；模板保存在设备上，论文把 image capture、ROI、feature extraction、template generation、matching 都放在手机内。

pipeline 是九个掌边 keypoint 的 ROI（ResNet-50，使用 Armatura COTS SDK 产生的 keypoint 作为训练目标），homography/TPS 对齐，SqueezeUNet enhancement，ViT + ResNet50 embedding，DeepMDS++ 降维，再把 32-bit float 压成 uint8 template。最终模板为 516 bytes；模型参数总量约 `76.04M`。

## 3. 论文真正测量的内容

- 论文的 efficiency table 报告 template extraction `18.0 ms`、10,000 gallery search `0.33 ms`，但摘要和表格把 search 运行环境写成 **AMD EPYC 7543 32-Core CPU、128 threads**；不能将这些数字称为 Galaxy S22 或 Raspberry Pi latency。
- 手机 app 被实现为可实时 enrollment/search 的实际工件，但公开论文没有给 Galaxy S22 的 capture-to-decision p50/p95、峰值 RAM、温度、功耗、帧丢失、相机曝光/光照状态或 Android pipeline profiling。
- 识别测试严格把 test database 与 train/validation identities 分开；MSU 数据含 Galaxy S22 的 5--13 个月 time-separated sessions，另外使用 CASIA、IITD、NTU 等公开数据。论文报告 0.01% FAR 下的 TAR，以及 open-set `FPIR/FNIR`；这些是 recognition 结果，不含 PAIS/PAD。
- MSU 的新数据在论文中承诺发表后开放，但本次未找到可验证的作者下载入口、license 或完整 app/model artifact；不能当作当前可直接运行数据。
- ROI keypoint 的 ground truth 来自 Armatura COTS SDK，而非完全独立的人手标注；这会影响“自研 ROI”与商业 SDK 的比较解释。

## 4. 对本项目的意义

### 已经被文献覆盖的部分

1. smartphone/contactless palmprint 的完整本地 pipeline 已有强先例。
2. on-device template、质量拒绝、time-separated session 和 cross-database protocol 已有可借鉴设计。
3. template 压缩和 1:N search efficiency 已被系统性讨论，不能把“在 Pi 存 embedding”写成创新。

### 仍然没有被这篇论文回答的部分

1. Raspberry Pi/ARM CPU 的真实 capture-to-decision 资源和热/能耗。
2. RGB/NIR/ToF 同步、实际 illumination state 与距离质量门。
3. print/display/贴片等 PAIS，以及 `IAPMR = PAD pass AND target match` 的最终放行风险。
4. 小规模、低频、断网预同步授权工作流中的重采、人工 fallback 和运营成本。

## 5. 实验协议可迁移点

- B0 可以借用其 `1:1` authentication 语义、time-separated session、identity-disjoint test、quality reject 和 embedding-size ablation 的结构。
- 不能借用其 TAR/FAR 数字当本机目标；应在 Pi 上报告 FMR/FNMR、阈值冻结方式、ROI failure、retry、`T_capture/T_ROI/T_embedding/T_match/T_interaction`、RAM、thermal 和 input energy。
- Palm-ID 的 76M 参数和 ViT/ResNet50 组合不适合作为最小 Pi 依赖。可把它作为上界/移动端参考，实际 demo 先选可解释的小模型或传统 matcher，再做量化/移植 gate。
- 其质量分数是 embedding L2 norm 的 surrogate，不是独立安全或活体信号；本项目要把 quality reject、PAD/risk gate、identity match 分开报告。

## 6. 不能写的句子

- `Palm-ID 证明了掌纹识别可以在 Raspberry Pi 上实时运行`。
- `18 ms 是手机端到端延迟`。
- `on-device template 等于隐私保护/不可逆模板`。
- `Palm-ID 的高 TAR 证明了掌纹锁可抵抗 print/display/relay`。

