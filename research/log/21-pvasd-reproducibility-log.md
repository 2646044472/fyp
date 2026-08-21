# PVASD 掌静脉 PAD 阅读与可复现性日志

最后更新：2026-08-21。本日志精读 [Yan et al., *A Comprehensive Framework for Palm Vein Anti-Spoofing With Preprocessing Pipeline, Dataset, and Benchmark* (TIFS 2026)](https://doi.org/10.1109/TIFS.2025.3650391) 的公开全文关键章节，并审计 [official PVASD repository](https://github.com/valhongli/PVASD) 的当前 `main` branch、README、dataset card、requirements、训练/测试入口与 license。它是**掌静脉** PAD 的重要近邻，不是本项目掌纹 edge demo 的即插即用答案。

## 1. 论文和工件实际提供什么

论文称 PVASD 覆盖 5,515 subject、1,187,519 图，其中 880,241 为 live、307,278 为 spoof；攻击包括 16 种 2D/3D PA（打印物、手套、假体等），在室内/户外和五种 resolution 下采集。另有 20,000 个 AI-generated spoof 样本。其 task 是将 presented palm vein 图像分为 live/spoof，并以 APCER、BPCER、ACER 作评测。

当前 repository 可以核对到以下内容：

| 项目 | 可确认内容 |
| --- | --- |
| 代码许可 | 根目录 `LICENSE` 为 MIT。 |
| 数据入口 | `dataset.md` 列出 train/validation/test 三个 Google Drive 分卷和 deepfake 分卷；README 的数据规则限 academic research、禁止 commercial use、再分发与未获准展示图片。 |
| 方法/指标 | 训练和测试代码会先在 validation 找 EER threshold，再在 test 写 APCER/BPCER/ACER；README 列出 MobileNetV3Large、BiFPNFAS 等模型及 checkpoint links。 |
| 运行环境 | `requirements.txt` 锁定 `torch==2.2.0+cu121`、`torchvision==0.17.0+cu121`；`main.py` 的训练例子采用 CUDA-first 环境和很大的 data-loader batch。 |

因此，先前“仓库尚未发布”的网页抓取是错误的：浏览器抓取返回 404，但 Git remote 与 GitHub API 均确认当前 repository 存在。研究笔记保留这一修正，而不将一时的网页失败写成 artifact 缺失。

## 2. 为什么它不能直接变成我们的 baseline

| PVASD 的问题 | 本项目的问题 | 不可直接外推之处 |
| --- | --- | --- |
| NIR palm-vein 的 live/spoof 二分类 | RGB/NIR/ToF contactless palmprint 的 claim-based `1:1` verification | PAD classifier 的 ACER 不等于攻击者是否与目标 template 匹配的 IAPMR。 |
| 多种 2D/3D PA、不同 resolution 和环境 | 本实验室具体相机、LED、距离、同步与经批准的 material | 传感器、光谱、ROI 和 artefact 成像链不同；大数据数字不能迁移。 |
| 离线训练/testing code | Raspberry Pi capture-to-decision interaction | CUDA 12.1 和训练 batch 不证明 ARM wheel、CPU latency、RSS、热量、输入能耗或 camera service。 |
| 静态 PAD | B2 vs M 的 actual-state illumination-response 比较 | 无 post-claim command、frame-state verification、response relation 或 adaptive screen/relay protocol。 |

论文的 “palm vein” 不能被简写成“掌纹”。实验室若最终硬件输出的是可识别静脉而非掌纹，需要重新定义 biometric modality、registration、伦理与研究问题，不能悄悄将两个任务拼接。

## 3. 对本项目有用的部分

PVASD 可借鉴三件事：

1. 攻击样本至少按 2D/3D、材料和 capture condition 记录，而不是统称 `spoof`。
2. PAD threshold 应从 validation 冻结，再单列 test APCER/BPCER；不能在 test attack 后再挑 threshold。
3. 数据入口、许可、split、checkpoint 和环境都是 benchmark 的一部分，不能只读论文表格。

它不改变当前 P0/P/S 决策：不下载约百万图数据，不运行其 CUDA training，不把静脉 PAD 结果和掌纹 B0--M 放在同一张性能表。

## 4. 若未来转向掌静脉的前置门槛

1. 老师明确确认研究对象改为或增加 palm vein，并核对实验室 NIR wavelength、IR-cut、raw frame、ROI 与注册能力。
2. 在下载前确认学校伦理/数据处理批准、academic-only 条款、存储容量、访问人和删除安排；不得再分发原数据。
3. 固定 repo commit、分卷 hash、data manifest 与 checkpoint hash；Google Drive link 存在不等于每次下载内容可重复。
4. 先在开发机隔离复现一个小规模 data-loader/metric smoke test；ARM/Pi 只在合法 frozen model 上单独做 export、兼容性与端到端测量。
5. 若应用仍是授权进入/工具领取，补上真正的 claim-to-template `1:1` matcher，按 PAIS/session 报 IAPMR；单独的 live/spoof ACER 不足以回答是否会错误放行。

## 5. 当前结论

PVASD 使文献图谱更完整，也把候选创新进一步压缩：不能以“首次 NIR palm PAD dataset/benchmark”或“轻量 PAD model”命名项目。对现有 Raspberry Pi + RGB/NIR + 距离原型，最有价值的下一步仍是 Gate 0 实机观测与 B0 `1:1` baseline；只有证明确实获得稳定的静脉输入，才应重新评估是否扩大到 PVASD 这条路线。
