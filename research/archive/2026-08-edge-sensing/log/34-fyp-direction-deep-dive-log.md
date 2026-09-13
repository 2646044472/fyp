# FYP 四方向深研日志

日期：2026-08-27

## 目标

用户要求保留一个掌纹方向，并提出三个非掌纹候选。这里把候选限制为：有 Bob Zhang/PAMI 研究连接、有可获得的公开数据或可控硬件、能在 FYP 时间内形成可证伪实验。

## 本轮查阅

### 数据和 benchmark

- [MVTec AD 官方页](https://www.mvtec.com/research-teaching/datasets/mvtec-ad)：15 个物体/纹理类别、超过 5,000 张高分辨率图、正常训练图、缺陷测试图和像素级标注；许可是 CC BY-NC-SA 4.0，禁止商业用途。
- [AWS Open Data registry 的 VisA 条目](https://github.com/awslabs/open-data-registry/blob/main/datasets/visa.yaml)：12 类、3 个 domain、10,821 张图（9,621 normal、1,200 anomaly），图像和像素级标注，条目标注为 CC BY 4.0，并链接 Amazon 的 [SPot-the-Difference repository](https://github.com/amazon-science/spot-diff)。许可证仍应在下载时复核。
- [TUM RGB-D 官方页](https://cvg.cit.tum.de/data/datasets/rgbd-dataset)：RGB-D SLAM 场景，适合先做 RGB/深度缺失和同步故障脚本；它不是工业缺陷或生物识别数据。
- [NYU Depth V2 官方页](https://cs.nyu.edu/~fergus/datasets/)：464 个室内场景、407,024 个未标注帧、1,449 个密集标注帧；适合小规模 RGB-D 可行性验证，不应把它宣传成真实 ToF 故障数据。
- [OpenOOD 官方仓库](https://github.com/Jingkang50/OpenOOD)：统一 OOD/开放集/异常检测评测，支持多个 benchmark 和方法；它是评测框架，不解决 Pi 采集、缺失模态或长期漂移。

### Bob Zhang / PAMI 线索

- [PAMI 完整发表列表](https://pamigroup.github.io/publications.html)确认了 incomplete multi-view、质量/不确定性、去噪复原、异常检测、测试时适应和多种手部生物识别并存。
- [OFTTA](https://arxiv.org/abs/2310.18562) 与 [官方代码](https://github.com/Claydon-Wang/OFTTA)给出了无梯度、低资源 TTA 的可复现入口，但任务是跨人传感器 HAR。
- [ODS-SAM](https://www.ijcai.org/proceedings/2025/129) 与 [UPformer 摘要](https://pubmed.ncbi.nlm.nih.gov/38593560/)支持异常检测和不确定性方向；不能把医疗/工业 benchmark 的结果外推到 Pi。
- [掌纹 complete ROI](https://pubmed.ncbi.nlm.nih.gov/38837937/) 和 [HGAIQA](https://doi.org/10.1109/TIM.2024.3485454)说明掌纹 ROI 与质量评估已有较强先例，因此掌纹题目的变量必须上移到条件式采集、拒答和资源-风险联合协议。

## 推理链

1. “换一个应用”不等于新问题。每个候选必须写出故障机制、动作选择和失败成本。
2. “缺失模态”最贴近 PAMI 的共同核心，但随机 mask 过于理想化；研究价值取决于相关缺失、留出设备和真实资源测量。
3. “TTA”已有方法和代码，缺口在长期流中的污染、最坏窗口和回滚；否则只是跨域复现。
4. “异常检测”容易得到公开数据和可视化结果，但 SAM 迁移本身不够新；未知缺陷留出、校准拒答和 Pi budget 才是研究变量。
5. 掌纹系统最容易被硬件 demo 吸引，却最容易落入已有商业/论文先例。保留它的理由应是实验室已有设备和可测的故障闭环，不是“掌纹还没人做”。

## 最小选择实验

先实现 A 的四个 baseline：完整 RGB-D、固定 RGB fallback、质量加权、拒答/重采。故障注入分为随机缺失、相关缺失、过曝/低照、深度空洞和时序掉帧；以设备/场景留出做测试。若策略没有 risk-coverage 或资源 Pareto 改善，不继续堆网络，转 T 或 O。

## 重要边界

- MVTec AD 的非商业许可不能支持产品商业化叙事。
- 公开 RGB-D 数据不能证明实验室 RGB/NIR/ToF 的物理故障分布。
- Bob Zhang 论文的结果不能直接迁移到 Raspberry Pi；每项都要重新测 p95、RAM、温度和能耗。
- 掌纹识别、PAD、模板安全、设备安全和法律身份是不同层；不能用一个 demo 的 accuracy 覆盖它们。

## 当前决策

当前建议顺序为 A > P > T > O（按“研究贡献与可控性”的综合平衡；若必须掌纹则 P 置顶）。完整题目、问题、基线和停止条件见 [`../core/13-fyp-direction-shortlist.md`](../core/13-fyp-direction-shortlist.md)。
