# 最小 B0 可复现性日志：先跑通，再不夸大

最后更新：2026-08-21。本日志回答“最简单 demo 明天到底从哪里开始”。它区分三个不同目标：跑通处理链、在公开 protocol 上检查识别流程、在实验室硬件上得出端侧结论。

## 1. 结论先行

首周可交付的 B0 不应叫“复现 PPNet on Pi”。应叫：

> 在已记录版本的 RGB ROI 输入上，完成 `ROI -> embedding/descriptor -> enrollment template -> 1:1 score -> frozen threshold -> accept/retry` 的可测处理链，并保存 capture-to-decision 时间戳、失败原因和环境信息。

这里的模型可先是一个当前 ARM runtime 可维护的 frozen RGB encoder，也可在尚未取得模型权重前暂用可解释 descriptor 做管线 smoke test。无论哪种，只有实机测量的数值才能写成 Pi performance。

## 2. 数据与代码分别审计

| 工件 | 实际已核对到的内容 | 可用于什么 | 仍缺什么，因此不能说什么 |
| --- | --- | --- | --- |
| [Tongji Contactless Palmprint](https://cslinzhang.github.io/ContactlessPalm/) | 官方页提供原图/ROI 下载入口；600 palms、两 session、每 session 每 palm 10 图，平均相隔约 61 天；同名文件跨 session 表示同一 palm。 | 经下载条款核对后，可作为 P 层的 `session1 gallery/dev -> session2 probe` 1:1 protocol 参照；文件名也允许脚本可审计地建立 pair。 | 当前页面没有明确可读的 license/redistribution/figure-publication 条款。下载入口存在不等于授权已满足；它也不是实验室 RGB/NIR/ToF、PAD 或 Pi 数据。 |
| [PalmMatchDB](https://huggingface.co/datasets/aspmirlab/PalmMatchDB) | Apache-2.0、可直接下载、10,528 rows/1.27 GB，但公开 card 只有 `train` split。 | P0：安装、预处理、embedding、模板、分数和日志的工程 smoke test。 | 缺 session/identity/camera/attack metadata，不能靠随机重切分写泛化、cross-device 或 PAD 结论。 |
| [PPNet code](https://github.com/xuliangcs/ppnet) | CC-BY-NC 4.0；源码可读，输入为 128 灰度 ROI、nonzero ROI normalization、输出 512-D feature，使用 L2 distance；repo 可生成 Tongji session1/session2 file list 和 EER/ROC score files。inference 脚本在 CUDA 不可用时选择 CPU。 | B0 的数据字段、灰度 ROI 预处理和 score-script 参照；可在**实际权重可取得且环境可重建**时做一个独立对照。 | 预训练 weights 只链接外部网盘，GitHub release 没有模型资产；`torch.load` 未指定 CPU `map_location`；README 的 Pi guide 是旧 Buster/ARMv7/Python 3.7/pre-release PyTorch 环境。源码默认可训练/评测，不含相机、ROI online capture、端到端时延、memory 或能耗测试。故不能说它是当前可直接部署的 Pi recipe 或当前可复现权重。 |

## 3. 为什么 PPNet 不是默认部署依赖

它不是没有价值，而是研究工件的边界很清楚：`test.py` 在 session gallery/probe 间枚举距离并用 score files 计算 EER，适合检查 `1:1` 评分；但这不是一个现场交互服务。`inference.py` 只读取既存的 `test.txt`，按数据集硬编码 `num_classes`，并加载本地 `net_params.pth`。没有冻结权重 hash、下载入口完整性、现代 ARM runtime 或 capture chain 时，不应把“repo 能打开”改写成“demo 可复现”。

此外，该网络的第一个全连接层是 `43264 -> 512`；仅这层就约 22.15M 个 weight（不含 bias）。因此“lightweight”是作者方法命名，不能在未实测前等同低 RAM、低 latency 或低能耗。

## 4. 三阶段最小路径

| 阶段 | 输入 | 通过证据 | 禁止的表述 |
| --- | --- | --- | --- |
| P0 smoke test | PalmMatchDB 或获同意的非生产测试图 | dependency lock、input/model hash、至少一个 genuine/impostor score、异常/ROI failure 日志 | “识别准确率”“跨设备”“PAD” |
| P protocol check | 获许可的 Tongji ROI，session1/session2 按官方命名规则 | 明确下载/条款记录、gallery/probe manifest、development 冻结 threshold、FMR/FNMR/ROC 和比较次数 | “本采集盒性能”“Pi 速度”“对攻击安全” |
| S hardware demo | 实验室 RGB capture，随后才加入 Gate 0 合格的 NIR/ToF | camera/driver/config log、consented enrollment/probe、`T_interaction`、ROI/retry、template lifecycle 与 fallback | “公开 benchmark 的数字”“liveness”“澳门需求已证明” |

这三层都不要求先训练一个新网络。先让 B0 的输入边界和日志正确，才能判断 NIR、ToF 或主动序列是否真的值得加入。

## 5. 开始前的可执行清单

1. 向实验室确认 Pi 型号/RAM、OS/architecture、相机驱动、RGB/NIR 模组与供电方式；按 Gate 0 建表。
2. 先在开发机下载 PalmMatchDB，记录 revision/hash；完成一个不输出生物帧的 `score + log` smoke test。
3. 单独核对 Tongji 下载条款；未明确前不下载、不再发布图像，也不将它当正式 P 层输入。
4. 选定当前 ARM 可维护的 runtime 后，冻结 model file/hash、预处理、线程数与 CPU governor；不要先安装 PPNet 的 2021 Pi guide。
5. 在 Pi 上以真实 capture 测 `T_model`、`T_pipeline`、`T_interaction`，并保留 thermal/throttle、camera timeout 与 ROI failure。任何一个为空，B0 仍只是开发机脚本。

## 6. 仍未解决

- 实验室真实硬件型号和能否取得 raw RGB/NIR frame；
- 目标 Pi 是 ARMv7 还是 aarch64，及当前可维护 runtime；
- Tongji 的明确使用条款；
- PPNet 外部权重是否仍能下载、适配 CPU，并有可核验 hash；
- 目标工作流是否接受生物特征及 fallback。

这些未知量不应被“先做 demo”跳过。它们决定 demo 是可信的测量起点，还是不可交代的演示。

## 7. 再审计一个“轻量”路线：EEPNet 与 runtime 不是同一件事

综述提到的 [EEPNet](https://doi.org/10.1016/j.patrec.2022.05.015) 是 2022 年 Pattern Recognition Letters 的 MobileNetV3-based palmprint network。论文摘要称它以压缩层数、较大卷积核和若干训练策略追求效率，并在七个掌纹库比较 precision、speed、parameter count 与 FLOPs。

这说明轻量 backbone 已是已有研究路线，却没有给当前 B0 一个可直接部署的 artifact：本轮按完整题名、作者和 GitHub 检索，未找到作者发布的 official code、weight、ONNX/TFLite export、licence 或 Pi benchmark。未找到公开工件不等于作者从未提供；但在能核对出处前，它不能成为本项目的 default dependency，也不能以论文里的效率比较代替 Pi 数字。

相对地，[ONNX Runtime 的官方 Python 文档](https://onnxruntime.ai/docs/get-started/with-python.html) 明确把 CPU package 列为 Arm CPU 路线，并有 [Raspberry Pi camera-to-inference tutorial](https://onnxruntime.ai/docs/tutorials/iot-edge/rasp-pi-cv.html)。这只支持把 ONNX Runtime 放入 **candidate runtime**，不代表任意 palm model 都能在任意 Pi 上安装或跑得足够快。

因此 B0 的 runtime gate 是：

1. 在 Pi 上记录 `uname -m`、OS release、Python version、RAM、camera driver 和 CPU governor；不可用开发机推测。
2. 对已获合法权重的 frozen model，在目标架构创建干净环境，记录 `pip`/wheel version、provider、threads 和 model SHA-256；先跑 deterministic test input，再接 camera。
3. 若 `aarch64` 的 CPU runtime 可安装，测试 ONNX Runtime；若为 ARM32 或 wheel/算子不兼容，则记录失败原因并在**同一已冻结模型**上改走可维护 runtime 或 descriptor P0，不编造跨 runtime 可比性。
4. runtime 能启动并不通过 Gate 0：仍须实测 `T_capture`、`T_ROI`、`T_embedding`、`T_match`、p95 interaction、RSS/peak memory、thermal/throttle 和 input energy。

结论：B0 的第一项贡献是可复现实验链和失败日志，不是指定 EEPNet、PPNet 或 ONNX Runtime 为“最终系统”。
