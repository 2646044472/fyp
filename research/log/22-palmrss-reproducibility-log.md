# PalmRSS 阅读与复现性日志：跨域问题不等于可部署基线

最后更新：2026-08-21。本文只记录对 [Jia et al., *Single source domain generalization for palm biometrics*](https://doi.org/10.1016/j.patcog.2025.111620) 的正式摘要和作者仓库所作核验；本轮无法取得 Pattern Recognition 正文，因此不补写摘要未报告的数值、split 或模型细节。

## 1. 它实际提出的问题

正式摘要将 palmprint 的 device difference 和 environmental variation 视为 domain shift，并把只拥有一个 source dataset 的情形写成 single-source domain generalization（SSDG）。作者称 PalmRSS 在 source 内部划分 subsets，以 Fourier low-frequency exchange 与 histogram matching 对齐低层分布，再加入 domain-adversarial 与 feature-similarity loss，在 cross-dataset setup 评测。

这直接反驳了一个常见偷换：在同一相机、同一背景、同一 session 的随机 train/test split 上获得高 recognition score，不等于在本实验室不同相机、光照、重新摆放或新 session 上仍可靠。它也没有证明任何一个特定 Raspberry Pi、RGB/NIR/ToF 盒子已经跨设备泛化。

## 2. 当前仓库工件审计

2026-08-21 核对的 [作者仓库](https://github.com/yocii/PalmRSS) `main` remote ref 为 `6415ae9faaa0405ba2292a2fad002f9b97d043e4`。仓库包含 PyTorch model/training/test/inference scripts 和多份 `data/*.txt` path list；递归 tree 中没有图像档、`.pth`/`.pt` weight 或 `LICENSE`。根 README 仅提供联系邮箱，`data/readme.md` 没有使用说明；requirements 列出辅助库但没有 pin PyTorch、CUDA、Python 或 OS。

`train.py`、`test_cross_performance.py` 中的主要 training/testing route 直接调用 `.cuda()`，默认 batch 为 512 或 1024，并含作者机器的 `/media/Storage1/...` data/output paths。`inference.py` 有 `cuda` 不可用时选 CPU 的 device expression，但它期待本地 `net_params.pth`，其 model import 与其他脚本不一致。没有 compatible published weight、数据、license 或环境说明时，这不是 Pi CPU/ARM 可复现工件，更没有 camera capture、ARM export、latency、memory、energy 或 interactive retry 的报告。

## 3. 对本项目的正确使用

| 可借用 | 不可借用 |
| --- | --- |
| B0--M 应预先按 session、sensor 或 capture-condition 留出，而不是只做随机 split。 | PalmRSS 的声称效果、cross-dataset 数字、模型大小和算力需求；正文未得。 |
| 将 RGB/NIR、IR-cut、距离、环境光、相机和 session metadata 写入 manifest，便于定位 shift。 | 其 repo 作为可运行 Pi baseline；data/weight/license/ARM runtime 均未确认。 |
| recognition 的 cross-domain 结果与 PAD 的 PAIS holdout 分开解释。 | 将 recognition domain generalization 改写为 PAIS detection、active illumination freshness 或 `1:1` final IAPMR。 |

因此 PalmRSS 提高的是本项目对外部有效性的门槛：B0 若不先跨 session/condition 压测，之后 B2/M 即使在同一装置上看似提升，也不能解释为可部署的安全收益。它不是可以替代硬件 Gate 0 或 blind PAIS/session test 的算法答案。
