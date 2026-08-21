# 2022 Edge Computing 掌纹系统阅读日志

最后更新：2026-08-21。本文核对 Liu、Zhong、Shao、Liu 的《基于边缘计算的紧致化掌纹识别系统》（英文题名 *Design of a compact palmprint recognition system based on edge computing*）。由于出版社 PDF 入口在本次访问中被 WAF 拦截，以下只把官方检索到的摘要、引言片段和书目信息作为已核验内容，不把全文实验细节补写出来。

## 1. 原始资料与可读范围

- [Scientia Sinica Technologica DOI/PDF 入口](https://doi.org/10.1360/SST-2021-0223)，2022，52(5):704--712；官方检索片段显示收稿 2021-05-29、接受 2021-11-04、网络版 2022-03-30。
- [出版社 PDF 检索结果](https://www.sciengine.com/doi/pdf/DF22037D58944CCEB5ED13226AE7134D) 提供中文摘要、关键词和部分引言；直接抓取 PDF 返回 WAF 拦截，ResearchGate 也只提供 request-full-text 页面。

## 2. 系统架构（摘要明确写出的部分）

论文把系统分为三层：

1. **终端设备层**：采集图像，使用 Tiny YOLO-v3 目标检测和 MobileNetV2 关键点定位，预处理并提取掌纹 ROI，然后发起识别请求。
2. **边缘服务器层**：接收 ROI，使用基于对抗度量学习的 GoogLeNet 做特征提取和匹配，返回识别结果并同步数据。
3. **云层**：记录识别任务到数据库，并定期训练/更新终端与边缘设备模型，以增强跨域识别。

因此这里的 `edge computing` 是终端向附近边缘服务器卸载识别任务的三层体系，不等于所有推理都在 Raspberry Pi 本地完成，也不等于离线系统。

## 3. 对本项目最重要的反证

- “把掌纹识别放到 edge/embedded 系统”不是空白；2022 年已有中文核心期刊论文明确以 edge computing 为题，并描述了完整终端--边缘--云工作流。
- Tiny YOLOv3、MobileNetV2、GoogLeNet 和模型定期更新已经是该先例的一部分；不能把“轻量 ROI + 端侧请求 + 边缘匹配”直接写成方法创新。
- 该架构的动机是多设备实时处理、带宽/云负载和跨域模型更新，和本项目假定的低频、断网、人工 fallback 的内部核验器并不相同。两者不要混称为同一个部署模型。

## 4. 本次没有核验到的内容

摘要/可见片段没有给出可迁移的具体硬件型号、CPU/GPU/NPU、模型参数量、端到端 p50/p95、网络往返、峰值 RAM、温度、功耗、相机曝光/光源状态、身份/会话划分、PAIS/PAD、`IAPMR` 或人工 fallback 协议。故不能引用它的“实时、高效、完整可行、市场前景”作为 Raspberry Pi 实测结论或安全结论。

## 5. 对题目的收窄

若本项目坚持 `palmprint + edge`，标题第一次出现时应明确是 **edge device / local capture-to-decision**，并说明和该论文的 edge-server offloading 区别。可验证的贡献只能来自：

- 同一 Raspberry Pi、相机/IR/NIR/ToF 硬件上的真实采集到放行闭环；
- 在无网络或受限网络下，过期授权、撤销、重采和人工 fallback 的可审计行为；
- 以 session/device/illumination/PAIS 留出验证 ROI、质量门、PAD gate 与身份匹配，而非只报识别准确率；
- 冻结 runtime、线程、输入分辨率和模型后报告 p95、RAM、thermal、input energy。

## 6. 禁止外推的句子

- `2022 年还没有 edge palmprint system。`
- `这篇论文证明 Raspberry Pi 可以离线完成掌纹识别。`
- `Tiny YOLOv3 + MobileNetV2 + GoogLeNet 在我们的硬件上就是实时的。`
- `edge computing 架构自动提供隐私、活体或门禁安全。`

